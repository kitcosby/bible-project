#!/usr/bin/env python3
"""Load Kethiv/Qere variants (Masoretic tradition) into word_variants.

Kit 2026-10-14: full traditions campaign. The OSHB (morphhb, WLC) XML marks
ketiv words with type="x-ketiv" and the qere reading in a following
<rdg type="x-qere"> group. Each pair becomes one word_variants row on the
ketiv's corpus word:
  variant_kind='textual', witness='MT', variant_type='qere',
  variant_text = qere pointed reading ('/' morpheme separators stripped,
  matching corpus convention), unpointed/letters = qere consonants with
  final letterforms folded to medial (corpus convention).

Alignment: per verse, main (non-qere) OSHB tokens are aligned to corpus
words by position, with a difflib fallback on folded consonant skeletons
when counts differ. Every skip is counted and reported; nothing is forced.

Idempotent: existing witness='MT' AND variant_type='qere' rows are deleted
first. Source: /tmp/morphhb-check/wlc (morphhb @ 3d15126, WLC public
domain, OSHB apparatus CC BY).
"""
import difflib
import json
import os
import re
import sqlite3
import sys
import xml.etree.ElementTree as ET

SRC = sys.argv[1] if len(sys.argv) > 1 else '/tmp/morphhb-check/wlc'
DB = sys.argv[2] if len(sys.argv) > 2 else os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'bible_v2.db')
NS = '{http://www.bibletechnologies.net/2003/OSIS/namespace}'
BOOKMAP = {'Gen': 1, 'Exod': 2, 'Lev': 3, 'Num': 4, 'Deut': 5, 'Josh': 6,
           'Judg': 7, 'Ruth': 8, '1Sam': 9, '2Sam': 10, '1Kgs': 11,
           '2Kgs': 12, '1Chr': 13, '2Chr': 14, 'Ezra': 15, 'Neh': 16,
           'Esth': 17, 'Job': 18, 'Ps': 19, 'Prov': 20, 'Eccl': 21,
           'Song': 22, 'Isa': 23, 'Jer': 24, 'Lam': 25, 'Ezek': 26,
           'Dan': 27, 'Hos': 28, 'Joel': 29, 'Amos': 30, 'Obad': 31,
           'Jonah': 32, 'Mic': 33, 'Nah': 34, 'Hab': 35, 'Zeph': 36,
           'Hag': 37, 'Zech': 38, 'Mal': 39}
FINALS = {'ך': 'כ', 'ם': 'מ', 'ן': 'נ', 'ף': 'פ', 'ץ': 'צ'}
BASIS = ('Kethiv/Qere apparatus of the Westminster Leningrad Codex '
         '(OSHB morphhb@3d15126); qere = Masoretic reading tradition')


def fold(s):
    return ''.join(FINALS.get(c, c) for c in (s or ''))


def consonants(text):
    return ''.join(c for c in (text or '') if 'א' <= c <= 'ת')


def clean_pointed(text):
    return (text or '').replace('/', '').strip()


def extract_pairs(path):
    """Yield (book, chapter, verse, tokens) where tokens is a list of
    dicts: {pointed, ketiv: bool, qere: [pointed, ...] or None}."""
    tree = ET.parse(path)
    root = tree.getroot()
    for chapter_el in root.iter(NS + 'chapter'):
        for verse_el in chapter_el.iter(NS + 'verse'):
            osis = verse_el.get('osisID')
            if not osis:
                continue
            parts = osis.split('.')
            book = BOOKMAP[parts[0]]
            ch, vs = int(parts[1]), int(parts[2])
            tokens = []
            for child in verse_el:
                if child.tag == NS + 'w':
                    tokens.append({
                        'pointed': ''.join(child.itertext()),
                        'ketiv': child.get('type') == 'x-ketiv',
                        'qere': None})
                elif child.tag == NS + 'rdg' and child.get('type') == 'x-qere':
                    qwords = [''.join(w.itertext())
                              for w in child.iter(NS + 'w')]
                    if tokens:
                        tokens[-1]['qere'] = qwords
                    else:
                        tokens.append({'pointed': '', 'ketiv': False,
                                       'qere': qwords, 'orphan': True})
                else:
                    # nested structures: walk descendants in doc order
                    for el in child.iter():
                        if el.tag == NS + 'w':
                            tokens.append({
                                'pointed': ''.join(el.itertext()),
                                'ketiv': el.get('type') == 'x-ketiv',
                                'qere': None})
            yield book, ch, vs, tokens


def main():
    db = sqlite3.connect(DB)
    db.row_factory = sqlite3.Row
    stats = {'verses_seen': 0, 'ketiv_total': 0, 'pairs': 0, 'inserted': 0,
             'skipped_no_word': 0, 'skipped_identical': 0,
             'orphan_qere': 0, 'ketiv_no_qere': 0,
             'verses_count_mismatch': 0, 'pos_mismatch': 0}
    rows = []
    for abbr, bnum in sorted(BOOKMAP.items(), key=lambda kv: kv[1]):
        path = os.path.join(SRC, abbr + '.xml')
        if not os.path.exists(path):
            print(f'MISSING {path}', file=sys.stderr)
            continue
        for book, ch, vs, tokens in extract_pairs(path):
            stats['verses_seen'] += 1
            vrow = db.execute(
                'SELECT verse_id FROM verses WHERE book_id=? AND chapter=? '
                'AND verse=?', (book, ch, vs)).fetchone()
            if vrow is None:
                stats['skipped_no_word'] += sum(
                    1 for t in tokens if t['ketiv'])
                continue
            vid = vrow['verse_id']
            cwords = db.execute(
                'SELECT word_id, word_pos, unpointed FROM words '
                'WHERE verse_id=? ORDER BY word_pos', (vid,)).fetchall()
            main_tokens = [t for t in tokens if not t.get('orphan')]
            orphans = [t for t in tokens if t.get('orphan')]
            stats['orphan_qere'] += len(orphans)
            # alignment token-index -> word_id
            cmap = {}
            cskel = [fold(c['unpointed'] or '') for c in cwords]
            tskel = [fold(consonants(t['pointed'])) for t in main_tokens]
            if len(cwords) == len(main_tokens):
                for i, (c, t) in enumerate(zip(cwords, main_tokens)):
                    cmap[i] = c['word_id']
                    if cskel[i] != tskel[i]:
                        stats['pos_mismatch'] += 1
            else:
                stats['verses_count_mismatch'] += 1
                sm = difflib.SequenceMatcher(a=cskel, b=tskel,
                                              autojunk=False)
                for tag, i1, i2, j1, j2 in sm.get_opcodes():
                    if tag == 'equal':
                        for k in range(i2 - i1):
                            cmap[j1 + k] = cwords[i1 + k]['word_id']
                    elif tag == 'replace' and (i2 - i1) == (j2 - j1):
                        for k in range(i2 - i1):
                            cmap[j1 + k] = cwords[i1 + k]['word_id']
            for i, t in enumerate(main_tokens):
                if t['ketiv']:
                    stats['ketiv_total'] += 1
                    if not t['qere']:
                        stats['ketiv_no_qere'] += 1
                        continue
                    wid = cmap.get(i)
                    if wid is None:
                        stats['skipped_no_word'] += 1
                        continue
                    q_pointed = ' '.join(clean_pointed(q)
                                         for q in t['qere'])
                    q_cons = ' '.join(fold(consonants(q))
                                      for q in t['qere'])
                    k_cons = fold(consonants(t['pointed']))
                    if q_cons == k_cons and \
                            q_pointed == clean_pointed(t['pointed']):
                        stats['skipped_identical'] += 1
                        continue
                    stats['pairs'] += 1
                    rows.append((wid, q_cons, q_cons, q_pointed))
    db.execute("DELETE FROM word_variants WHERE variant_kind='textual' "
               "AND witness='MT' AND variant_type='qere'")
    seq_cache = {}
    for wid, q_cons, q_letters, q_pointed in rows:
        if wid not in seq_cache:
            r = db.execute('SELECT COALESCE(MAX(variant_seq),0) m FROM '
                           'word_variants WHERE word_id=?',
                           (wid,)).fetchone()
            seq_cache[wid] = r['m']
        seq_cache[wid] += 1
        db.execute(
            'INSERT INTO word_variants (word_id, variant_seq, variant_kind,'
            ' unpointed, letters, variant_text, convention, source,'
            ' witness, variant_type, basis) VALUES (?,?,?, ?,?,?, NULL,'
            ' NULL, ?,?, ?)',
            (wid, seq_cache[wid], 'textual', q_cons, q_letters, q_pointed,
             'MT', 'qere', BASIS))
        stats['inserted'] += 1
    db.commit()
    print(json.dumps(stats, indent=1))
    n = db.execute("SELECT COUNT(*) c FROM word_variants WHERE "
                   "variant_kind='textual'").fetchone()['c']
    print('textual rows now:', n)


if __name__ == '__main__':
    main()
