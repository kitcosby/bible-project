#!/usr/bin/env python3
"""STRONGS-BLANK-6008 verification: exact checks of the repaired bible_v2.db
against its pre-repair backup. Read-only on both DBs.

Checks (all exact numerators/denominators):
  1. Strong's coverage before/after out of total words (both DBs counted live).
  2. KJV coverage before/after (distinct word_id in kjv_renderings) out of total.
  3. YLT computed coverage before/after (distinct word_id in ylt_renderings) —
     expected UNCHANGED: the YLT bridge was not re-run (see ledger entry).
  4. Every pre-existing (word_id, strongs) pair byte-identical; the set of
     words rows differing from backup is exactly the diagnosis fills set and
     differs only in (strongs, strongs_source_id).
  5. Every pre-existing kjv_renderings (word_id, kjv_word, kjv_strongs, method)
     row preserved (multiset); zero new 'strongs-fill' (word_id, kjv_word)
     pairs collide with pre-existing pairs.
  6. Every new 'strongs-fill' row mechanically re-checked for Strong's
     sharing: the word's (new) Strong's is in the normalized Strong's set of
     some kjv_words row in the same verse carrying that kjv_word.
  7. PRAGMA foreign_key_check = 0 rows.
  8. Lexicon: every affected group's lexicon_kjv_rendering rows equal a
     from-scratch recomputation (build_lexicon.py cell computation).
  9. Every filled word's Strong's has at least one glosses row.
 10. Spot-check: 15 filled words re-verified against the OSHB XML pointed
     text in sources/morphhb/wlc/ (the strongs-bearing evidence component's
     <w> text and @lemma digits must match).

Usage: verify_strongs_blank.py --db PATH --backup PATH --diagnosis JSON
Exit code 0 iff every check passes.
"""
import argparse, json, re, sqlite3, sys
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict

ROOT = '/home/hatch/workspace/bible-project'
NS = '{http://www.bibletechnologies.net/2003/OSIS/namespace}'
ABBR = {1:'Gen',2:'Exod',3:'Lev',4:'Num',5:'Deut',6:'Josh',7:'Judg',8:'Ruth',
        9:'1Sam',10:'2Sam',11:'1Kgs',12:'2Kgs',13:'1Chr',14:'2Chr',15:'Ezra',
        16:'Neh',17:'Esth',18:'Job',19:'Ps',20:'Prov',21:'Eccl',22:'Song',
        23:'Isa',24:'Jer',25:'Lam',26:'Ezek',27:'Dan',28:'Hos',29:'Joel',
        30:'Amos',31:'Obad',32:'Jonah',33:'Mic',34:'Nah',35:'Hab',36:'Zeph',
        37:'Hag',38:'Zech',39:'Mal'}

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

fails = []
def check(name, ok, detail=''):
    print(f"[{'PASS' if ok else 'FAIL'}] {name} {detail}")
    if not ok:
        fails.append(name)

def ro(path):
    c = sqlite3.connect('file:' + path + '?mode=ro', uri=True)
    c.row_factory = sqlite3.Row
    return c

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--db', required=True)
    ap.add_argument('--backup', required=True)
    ap.add_argument('--diagnosis', required=True)
    a = ap.parse_args()
    diag = json.load(open(a.diagnosis, encoding='utf-8'))
    fills = {f['word_id']: f for f in diag['fills']}

    new, old = ro(a.db), ro(a.backup)
    n_new = new.execute('SELECT COUNT(*) FROM words').fetchone()[0]
    n_old = old.execute('SELECT COUNT(*) FROM words').fetchone()[0]
    check('word count stable', n_new == n_old == diag['summary']['total_words'],
          f'{n_old} -> {n_new}')

    s_old = old.execute('SELECT COUNT(*) FROM words WHERE strongs IS NOT NULL').fetchone()[0]
    s_new = new.execute('SELECT COUNT(*) FROM words WHERE strongs IS NOT NULL').fetchone()[0]
    print(f"Strong's coverage: {s_old}/{n_old} = {100.0*s_old/n_old:.4f}% -> "
          f"{s_new}/{n_new} = {100.0*s_new/n_new:.4f}%")
    check("Strong's gain == fills", s_new - s_old == len(fills),
          f'gain {s_new - s_old}, fills {len(fills)}')

    k_old = old.execute('SELECT COUNT(DISTINCT word_id) FROM kjv_renderings').fetchone()[0]
    k_new = new.execute('SELECT COUNT(DISTINCT word_id) FROM kjv_renderings').fetchone()[0]
    print(f"KJV coverage: {k_old}/{n_old} = {100.0*k_old/n_old:.4f}% -> "
          f"{k_new}/{n_new} = {100.0*k_new/n_new:.4f}%")

    y_old = old.execute('SELECT COUNT(DISTINCT word_id) FROM ylt_renderings').fetchone()[0]
    y_new = new.execute('SELECT COUNT(DISTINCT word_id) FROM ylt_renderings').fetchone()[0]
    print(f"YLT computed coverage (bridge not re-run): {y_old} -> {y_new} distinct words")
    check('YLT rows untouched',
          old.execute('SELECT COUNT(*) FROM ylt_renderings').fetchone()[0] ==
          new.execute('SELECT COUNT(*) FROM ylt_renderings').fetchone()[0] and y_old == y_new)

    # 4. words diff
    old_words = {r['word_id']: dict(r) for r in old.execute('SELECT * FROM words')}
    diff_ids, bad_cols = set(), Counter()
    for r in new.execute('SELECT * FROM words'):
        o = old_words[r['word_id']]
        if dict(r) != o:
            diff_ids.add(r['word_id'])
            for k in o:
                if r[k] != o[k]:
                    bad_cols[k] += 1
    check('words differing == fills set', diff_ids == set(fills),
          f'differing {len(diff_ids)}, fills {len(fills)}')
    check('words differ only in strongs/strongs_source_id',
          set(bad_cols) <= {'strongs', 'strongs_source_id'}, f'cols {dict(bad_cols)}')
    pre_ok = all(old_words[w]['strongs'] is None or
                 new.execute('SELECT strongs FROM words WHERE word_id=?', (w,)).fetchone()[0]
                 == old_words[w]['strongs'] for w in old_words)
    check('every pre-existing (word_id, strongs) byte-identical', pre_ok)
    fill_ok = all(new.execute('SELECT strongs FROM words WHERE word_id=?', (w,)).fetchone()[0]
                  == f['strongs'] for w, f in fills.items())
    check('every fill carries its diagnosed Strong\'s', fill_ok)

    # 5. kjv_renderings preservation + collisions
    old_rows = Counter((r[0], r[1], r[2], r[3]) for r in old.execute(
        'SELECT word_id, kjv_word, kjv_strongs, method FROM kjv_renderings'))
    new_rows = Counter((r[0], r[1], r[2], r[3]) for r in new.execute(
        'SELECT word_id, kjv_word, kjv_strongs, method FROM kjv_renderings'))
    missing = sum((old_rows - new_rows).values())
    check('all pre-existing kjv_renderings preserved (multiset)', missing == 0,
          f'missing {missing} of {sum(old_rows.values())}')
    old_pairs = {(r[0], r[1]) for r in old.execute('SELECT word_id, kjv_word FROM kjv_renderings')}
    sf = [(r[0], r[1], r[2]) for r in new.execute(
        "SELECT word_id, kjv_word, kjv_strongs FROM kjv_renderings WHERE method='strongs-fill'")]
    coll = sum(1 for wid, kw, _ in sf if (wid, kw) in old_pairs)
    check("zero 'strongs-fill' collisions with existing pairs", coll == 0, f'collisions {coll}')
    print(f"strongs-fill rows: {len(sf)} covering "
          f"{len({w for w, _, _ in sf})} distinct words; KJV gain {k_new - k_old} words")

    # 6. Strong's-sharing re-check of every strongs-fill row
    kjv_by_verse = {}
    for vid, kw, ks in new.execute('SELECT verse_id, kjv_word, strongs FROM kjv_words'):
        kjv_by_verse.setdefault(vid, []).append((kw, set(multi_strongs(ks))))
    winfo = {r['word_id']: (r['verse_id'], r['strongs']) for r in new.execute(
        'SELECT word_id, verse_id, strongs FROM words')}
    bad = 0
    for wid, kw, ks_stored in sf:
        vid, s = winfo[wid]
        if not any(kw == k2 and s in ks2 for k2, ks2 in kjv_by_verse.get(vid, [])):
            bad += 1
        elif norm_strongs(ks_stored.split(',')[0]) is None:
            bad += 1
    check("every 'strongs-fill' row shares the word's Strong's with a same-verse KJV row",
          bad == 0, f'bad {bad} of {len(sf)}')

    # 7. FK check
    fk = new.execute('PRAGMA foreign_key_check').fetchall()
    check('PRAGMA foreign_key_check = 0 rows', len(fk) == 0, f'{len(fk)} rows')

    # 8. lexicon recomputation for affected groups
    groups = defaultdict(set)
    for r in new.execute('SELECT word_id, root_id, root_form_seq, root_vowel_seq FROM words'):
        groups[(r['root_id'], r['root_form_seq'], r['root_vowel_seq'])].add(r['word_id'])
    sf_wids = {w for w, _, _ in sf}
    affected = [g for g, wids in groups.items() if wids & sf_wids]
    kjv = defaultdict(Counter)
    for wid, kw in new.execute('SELECT word_id, kjv_word FROM kjv_renderings'):
        kjv[wid][kw] += 1
    mism = 0
    for g in affected:
        c = Counter()
        for wid in groups[g]:
            c.update(kjv.get(wid, ()))
        expect = [w for w, _ in sorted(c.items(), key=lambda kv: (-kv[1], kv[0]))]
        got = [r[0] for r in new.execute(
            'SELECT rendering FROM lexicon_kjv_rendering '
            'WHERE root_id=? AND root_form_seq=? AND vowel_seq=? ORDER BY seq', g)]
        if got != expect:
            mism += 1
    check('affected lexicon groups match from-scratch recomputation', mism == 0,
          f'{len(affected)} groups, {mism} mismatches')

    # 9. glosses
    nogloss = [f['strongs'] for f in fills.values()
               if not new.execute('SELECT 1 FROM glosses WHERE strongs=? LIMIT 1',
                                  (f['strongs'],)).fetchone()]
    check('every filled Strong\'s has >=1 gloss row', not nogloss, f'missing {nogloss[:5]}')

    # 10. spot-check 15 fills against OSHB XML pointed text
    sample = sorted(fills.values(), key=lambda f: f['word_id'])
    step = max(1, len(sample) // 15)
    sample = sample[::step][:15]
    wref = {r['word_id']: (r['book_id'], r['chapter'], r['verse']) for r in new.execute(
        'SELECT w.word_id, v.book_id, v.chapter, v.verse FROM words w '
        'JOIN verses v ON v.verse_id = w.verse_id')}
    trees = {}
    spot_ok, spot_n = 0, 0
    for f in sample:
        b, ch, v = wref[f['word_id']]
        ab = ABBR[b]
        if ab not in trees:
            trees[ab] = ET.parse(f'{ROOT}/sources/morphhb/wlc/{ab}.xml')
        verse_el = None
        for el in trees[ab].getroot().iter(NS + 'verse'):
            if el.get('osisID') == f'{ab}.{ch}.{v}':
                verse_el = el
                break
        if verse_el is None:
            print(f"  spot word {f['word_id']}: verse {ab}.{ch}.{v} not found in XML")
            continue
        xml_words = {''.join(w.itertext()): w.get('lemma') for w in verse_el.iter(NS + 'w')}
        for ev in f['evidence']:
            if not ev['oshb_strongs']:
                continue
            spot_n += 1
            lemma = xml_words.get(ev['oshb_pointed'])
            digits = re.findall(r'\d+', lemma or '')
            if digits and f'H{int(digits[0])}' == ev['oshb_strongs']:
                spot_ok += 1
            else:
                print(f"  spot word {f['word_id']}: XML lemma {lemma!r} for "
                      f"{ev['oshb_pointed']!r} != diagnosed {ev['oshb_strongs']}")
    check('spot-check fills against OSHB XML pointed text', spot_n > 0 and spot_ok == spot_n,
          f'{spot_ok}/{spot_n} components across {len(sample)} words')

    print()
    print('RESULT:', 'ALL PASS' if not fails else f'FAILURES: {fails}')
    sys.exit(1 if fails else 0)

if __name__ == '__main__':
    main()
