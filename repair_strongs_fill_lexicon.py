#!/usr/bin/env python3
"""STRONGS-BLANK-6008 step 3b: rebuild lexicon KJV cells for affected groups.

bible_v2 stores the lexicon KJV cell as ordered child rows in
lexicon_kjv_rendering(root_id, root_form_seq, vowel_seq, seq, rendering).
For every (root_id, root_form_seq, root_vowel_seq) group containing a word
that gained a method='strongs-fill' kjv_renderings row, this script
recomputes the group's rendering list with the exact cell computation of
build_lexicon.py (per-word Counter of kjv_renderings rows, summed over the
group's words; distinct KJV words most frequent first, ties alphabetical)
and rewrites ONLY that group's lexicon_kjv_rendering rows (DELETE + INSERT
with seq 0..n-1, the migrate_v2.py split order). All other lexicon tables
and groups are untouched.

Usage: repair_strongs_fill_lexicon.py --db PATH [--dry-run]
"""
import argparse, sqlite3
from collections import Counter, defaultdict

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--db', required=True)
    ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()
    con = sqlite3.connect(a.db)
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    repaired_wids = [r[0] for r in cur.execute(
        "SELECT DISTINCT word_id FROM kjv_renderings WHERE method='strongs-fill'")]
    print('strongs-fill repaired word_ids:', len(repaired_wids))

    groups = defaultdict(set)
    for r in cur.execute('SELECT word_id, root_id, root_form_seq, root_vowel_seq FROM words'):
        groups[(r['root_id'], r['root_form_seq'], r['root_vowel_seq'])].add(r['word_id'])
    rset = set(repaired_wids)
    affected = [g for g, wids in groups.items() if wids & rset]
    print('affected lexicon groups:', len(affected))

    kjv = defaultdict(Counter)
    for wid, kw in cur.execute('SELECT word_id, kjv_word FROM kjv_renderings'):
        kjv[wid][kw] += 1

    changed, empty_to_filled, rows_written = 0, 0, 0
    for g in affected:
        c = Counter()
        for wid in groups[g]:
            c.update(kjv.get(wid, ()))
        cell = [w for w, _ in sorted(c.items(), key=lambda kv: (-kv[1], kv[0]))]
        old = [r[0] for r in cur.execute(
            'SELECT rendering FROM lexicon_kjv_rendering '
            'WHERE root_id=? AND root_form_seq=? AND vowel_seq=? ORDER BY seq', g)]
        if old != cell:
            changed += 1
            if not old:
                empty_to_filled += 1
            if not a.dry_run:
                cur.execute('DELETE FROM lexicon_kjv_rendering '
                            'WHERE root_id=? AND root_form_seq=? AND vowel_seq=?', g)
                cur.executemany('INSERT INTO lexicon_kjv_rendering VALUES (?,?,?,?,?)',
                                [(g[0], g[1], g[2], i, w) for i, w in enumerate(cell)])
                rows_written += len(cell)
    print(f'groups needing update: {changed} (empty->filled: {empty_to_filled})')
    if a.dry_run:
        print('dry-run: wrote nothing')
    else:
        con.commit()
        print(f'rewrote {rows_written} lexicon_kjv_rendering rows across {changed} groups')
    con.close()

if __name__ == '__main__':
    main()
