#!/usr/bin/env python3
"""STRONGS-BLANK-6008 diagnosis: bucket every blank-Strong's word in bible_v2.db.

Verified state before this item: 264,217 words, 6,008 with strongs IS NULL
(258,209 = 97.7261% carry one). This script is READ-ONLY on the DB.

Method: re-run the OSHB crosswalk's own align_verse machinery (copied
verbatim from assemble_bible.py, 2026-09-24 crosswalk) over every verse
containing a blank word, using the CURRENT words.pointed/letters (the
2026-09-29 anomaly resolutions changed 128 words' letters after the
crosswalk ran, so a fresh alignment can pair words the original run could
not). Buckets:

  (i)   exact      non-split word paired by difflib ('1to1'/'replace') to an
                   OSHB row carrying a Strong's — the crosswalk missed it
                   (in practice: letters/pointed corrected after the build).
  (ii)  split      maqqef-split word whose paired OSHB components carry
                   EXACTLY ONE distinct Strong's; every other paired
                   component is a lemma-less pronominal-suffix fragment
                   (OSHB morph */Sp*, lemma 'l'/'b'/'m'/'k' — no Strong's
                   number exists for it). The sole numbered component is
                   the word's only possible OSHB Strong's.
  (iii) fallback   non-split word paired only via the crosswalk's Stage-2
                   exact-consonant fallback (unique unconsumed skeleton
                   match), or unmapped by align_verse but with exactly one
                   consonant-skeleton match in the verse carrying a Strong's.
  (iv)  remainder  NOT repairable, never guessed:
                   - paired_blank_lemma: paired OSHB row's lemma has no
                     digits (OSHB letter lemmas l/b/m/k for the standalone
                     prepositions with pronominal suffixes — OSHB assigns
                     them no Strong's number at all);
                   - split_multi_strongs: maqqef-split with >1 distinct
                     numbered components (ambiguous which one represents
                     the word — the assembler's last-component convention
                     cannot fire because the last component is lemma-less);
                   - unmapped: no OSHB counterpart (paseq tokens, merged
                     ketiv/qere artifact tokens, Esther 4:1 verse shift);
                   - no_oshb_verse: verse absent from OSHB (versification).

Output: JSON {summary, fills: [{word_id, strongs, strongs_source, bucket,
evidence}], remainder: [{word_id, reason}]} — repair_strongs_blank.py
consumes the fills list verbatim, so repair can never exceed the diagnosis.

Usage: diagnose_strongs_blank.py --db PATH [--oshb TSV] --out JSON
"""
import argparse, csv, difflib, json, re, sqlite3
from collections import Counter, defaultdict

# --- copied verbatim from assemble_bible.py (2026-09-24 crosswalk) ---
def norm_strongs(s):
    if not s: return None
    s = str(s).strip().upper().replace(' ', '')
    m = re.match(r'^H?0*(\d+)$', s)
    return f'H{int(m.group(1))}' if m else None

def multi_strongs(s):
    out = []
    for tok in re.split(r'[;,/|\s]+', str(s or '')):
        n = norm_strongs(tok)
        if n and n not in out: out.append(n)
    return out

VERSE_REMAP = {(19, 17, 17): (19, 17, 1), (23, 27, 22): (23, 27, 1),
               (24, 28, 23): (24, 28, 1), (25, 2, 23): (25, 2, 1)}
MAQQEF = '־'
SOFIT_FOLD = {'ך': 'כ', 'ם': 'מ', 'ן': 'נ', 'ף': 'פ', 'ץ': 'צ'}
def cons_key(s):
    return ''.join(SOFIT_FOLD.get(ch, ch) for ch in (s or '') if 'א' <= ch <= 'ת')
def find_unconsumed(key, owords, consumed, bkeys):
    if not key: return None
    for j, (used, bk) in enumerate(zip(consumed, bkeys)):
        if not used and bk == key: return j
    return None
def align_verse(cwords, owords):
    pseudo = []
    for w in cwords:
        pt = w['word_pointed'] or ''
        if MAQQEF in pt:
            comps = [cons_key(p) for p in pt.split(MAQQEF)]
            if len(comps) > 1 and all(comps):
                for ci, ck in enumerate(comps):
                    pseudo.append((w, ck, ci, len(comps)))
                continue
        pseudo.append((w, cons_key(w['letters']), 0, 1))
    a = [p[1] for p in pseudo]
    b = [cons_key(r['unpointed']) for r in owords]
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    out = []
    consumed = [False] * len(owords)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == 'equal':
            for i, j in zip(range(i1, i2), range(j1, j2)):
                consumed[j] = True
                out.append((pseudo[i], owords[j], '1to1'))
        elif tag == 'replace':
            ca = ''.join(a[i1:i2]); cb = ''.join(b[j1:j2])
            if ca == cb and ca:
                if (i2 - i1) == (j2 - j1):
                    for i, j in zip(range(i1, i2), range(j1, j2)):
                        consumed[j] = True
                        out.append((pseudo[i], owords[j], 'replace'))
                else:
                    for i in range(i1, i2):
                        best = max(range(j1, j2), key=lambda j: len(b[j]))
                        consumed[best] = True
                        out.append((pseudo[i], owords[best], 'replace'))
            else:
                for i in range(i1, i2):
                    j = find_unconsumed(a[i], owords, consumed, b)
                    if j is not None:
                        consumed[j] = True
                        out.append((pseudo[i], owords[j], 'fallback'))
                    else:
                        out.append((pseudo[i], None, 'unmapped'))
        elif tag == 'delete':
            for i in range(i1, i2):
                j = find_unconsumed(a[i], owords, consumed, b)
                if j is not None:
                    consumed[j] = True
                    out.append((pseudo[i], owords[j], 'fallback'))
                else:
                    out.append((pseudo[i], None, 'unmapped'))
    return out
# --- end copied crosswalk machinery ---

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--db', required=True)
    ap.add_argument('--oshb', default='/home/hatch/workspace/bible-project/worker-out/oshb/oshb_words.tsv')
    ap.add_argument('--out', required=True)
    a = ap.parse_args()

    con = sqlite3.connect('file:' + a.db + '?mode=ro', uri=True)
    con.row_factory = sqlite3.Row
    total = con.execute('SELECT COUNT(*) FROM words').fetchone()[0]
    blank_ids = {r[0] for r in con.execute('SELECT word_id FROM words WHERE strongs IS NULL')}
    print(f'words {total}, blank strongs {len(blank_ids)}')

    oshb = {}
    with open(a.oshb, encoding='utf-8') as f:
        for r in csv.DictReader(f, delimiter='\t'):
            oshb.setdefault((int(r['book_num']), int(r['chapter']), int(r['verse'])), []).append(r)
    for v in oshb.values():
        v.sort(key=lambda r: int(r['word_pos']))

    verses = defaultdict(list)
    for r in con.execute('''SELECT w.word_id, w.word_pos, w.pointed AS word_pointed,
            w.letters, v.book_id, v.chapter, v.verse
            FROM words w JOIN verses v ON v.verse_id = w.verse_id
            ORDER BY v.book_id, v.chapter, v.verse, w.word_pos'''):
        verses[(r['book_id'], r['chapter'], r['verse'])].append(dict(r))
    con.close()

    fills, remainder = [], []
    counts = Counter()
    for ckey, cwords in verses.items():
        if not any(w['word_id'] in blank_ids for w in cwords):
            continue
        ow = oshb.get(VERSE_REMAP.get(ckey, ckey))
        if not ow:
            for w in cwords:
                if w['word_id'] in blank_ids:
                    counts['iv_no_oshb_verse'] += 1
                    remainder.append({'word_id': w['word_id'], 'reason': 'no_oshb_verse'})
            continue
        agg = {}
        for (w, key, ci, nc), orow, how in align_verse(cwords, ow):
            agg.setdefault(w['word_id'], []).append((key, orow, how, ci, nc))
        for w in cwords:
            wid = w['word_id']
            if wid not in blank_ids:
                continue
            plist = agg.get(wid, [])
            mapped = [(k, o, h, ci) for (k, o, h, ci, nc) in plist if o is not None]
            nc = plist[0][4] if plist else 1
            if nc > 1:
                strs, ev = [], []
                for k, o, h, ci in sorted(mapped, key=lambda t: t[3]):
                    ms = multi_strongs(o['strongs'])
                    strs.append(ms[0] if ms else None)
                    ev.append({'comp_idx': ci, 'oshb_word_pos': int(o['word_pos']),
                               'oshb_pointed': o['pointed'], 'oshb_unpointed': o['unpointed'],
                               'oshb_strongs': ms[0] if ms else None, 'oshb_morph': o['morph'],
                               'how': h})
                distinct = [s for s in dict.fromkeys(strs) if s]
                if len(distinct) == 1:
                    counts['ii_split_unique'] += 1
                    fills.append({'word_id': wid, 'strongs': distinct[0],
                                  'strongs_source': 'oshb-split', 'bucket': 'ii_split_unique',
                                  'evidence': ev})
                elif len(distinct) == 0:
                    counts['iv_split_all_blank'] += 1
                    remainder.append({'word_id': wid, 'reason': 'split_all_blank_lemma'})
                else:
                    counts['iv_split_multi_strongs'] += 1
                    remainder.append({'word_id': wid, 'reason': 'split_multi_strongs',
                                      'detail': distinct})
                continue
            if mapped:
                k, o, h, ci = mapped[0]
                ms = multi_strongs(o['strongs'])
                if ms:
                    bucket = 'i_exact' if h in ('1to1', 'replace') else 'iii_fallback'
                    counts[bucket] += 1
                    fills.append({'word_id': wid, 'strongs': ms[0],
                                  'strongs_source': 'oshb', 'bucket': bucket,
                                  'evidence': [{'comp_idx': 0, 'oshb_word_pos': int(o['word_pos']),
                                                'oshb_pointed': o['pointed'],
                                                'oshb_unpointed': o['unpointed'],
                                                'oshb_strongs': ms[0], 'oshb_morph': o['morph'],
                                                'how': h}]})
                else:
                    counts['iv_paired_blank_lemma'] += 1
                    remainder.append({'word_id': wid, 'reason': 'paired_blank_lemma',
                                      'detail': o['morph']})
                continue
            # unmapped by align_verse: unique-in-verse skeleton match?
            key = cons_key(w['letters'])
            matches = [o for o in ow if key and cons_key(o['unpointed']) == key]
            with_s = [o for o in matches if multi_strongs(o['strongs'])]
            if len(matches) == 1 and len(with_s) == 1:
                o = with_s[0]; ms = multi_strongs(o['strongs'])
                counts['iii_unique_skeleton'] += 1
                fills.append({'word_id': wid, 'strongs': ms[0],
                              'strongs_source': 'oshb', 'bucket': 'iii_unique_skeleton',
                              'evidence': [{'comp_idx': 0, 'oshb_word_pos': int(o['word_pos']),
                                            'oshb_pointed': o['pointed'],
                                            'oshb_unpointed': o['unpointed'],
                                            'oshb_strongs': ms[0], 'oshb_morph': o['morph'],
                                            'how': 'unique-skeleton'}]})
            else:
                counts['iv_unmapped'] += 1
                remainder.append({'word_id': wid, 'reason': 'unmapped'})

    n_fill = len(fills)
    assert n_fill + len(remainder) == len(blank_ids), (n_fill, len(remainder), len(blank_ids))
    summary = {'total_words': total, 'blank_before': len(blank_ids),
               'buckets': dict(counts), 'fills': n_fill, 'remainder': len(remainder)}
    print(json.dumps(summary, indent=1))
    with open(a.out, 'w', encoding='utf-8') as f:
        json.dump({'summary': summary, 'fills': fills, 'remainder': remainder}, f,
                  ensure_ascii=False, indent=1)
    print('wrote', a.out)

if __name__ == '__main__':
    main()
