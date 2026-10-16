#!/usr/bin/env python3
"""STRONGS-BLANK-6008 repair (Strong's fill only): apply the diagnosis fills.

Consumes diagnose_strongs_blank.py's JSON verbatim — this script contains
no alignment logic of its own and can never fill a word the diagnosis did
not bucket (i)/(ii)/(iii). For each fill:

  UPDATE words SET strongs=?, strongs_source_id=? WHERE word_id=? AND strongs IS NULL

strongs_source is the strongs_sources entity ('oshb' for buckets i/iii,
'oshb-split' for bucket ii), exactly the assembler's own source labels.
No existing Strong's value is ever modified: the UPDATE is guarded by
`strongs IS NULL`, and a fill whose word no longer reads NULL (or whose
word_id is unknown) aborts the run. If a fill's Strong's is missing from
the `strongs` entity table it is inserted (language 'H') so
PRAGMA foreign_key_check stays clean — in the measured diagnosis all
fills' Strong's already exist there.

KJV conversion is a separate step: convert_strongs_fill_kjv.py.
Lexicon rebuild is a separate step: repair_strongs_fill_lexicon.py.

Usage: repair_strongs_blank.py --db PATH --diagnosis JSON [--limit N] [--dry-run]
"""
import argparse, json, sqlite3, sys

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--db', required=True)
    ap.add_argument('--diagnosis', required=True)
    ap.add_argument('--limit', type=int, default=None)
    ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()

    diag = json.load(open(a.diagnosis, encoding='utf-8'))
    fills = diag['fills']
    if a.limit:
        fills = fills[:a.limit]
        print(f'slice: first {len(fills)} fills')
    print(f'planned fills: {len(fills)}')

    con = sqlite3.connect(a.db)
    cur = con.cursor()
    src_ids = {r[1]: r[0] for r in cur.execute('SELECT source_id, source FROM strongs_sources')}
    updates, inserted_entities = [], 0
    for f in fills:
        row = cur.execute('SELECT strongs FROM words WHERE word_id=?', (f['word_id'],)).fetchone()
        if row is None:
            sys.exit(f"refusing: word_id {f['word_id']} not in words")
        if row[0] is not None:
            sys.exit(f"refusing: word_id {f['word_id']} already has strongs {row[0]} "
                     '(diagnosis is stale or DB already repaired)')
        if not cur.execute('SELECT 1 FROM strongs WHERE strongs=?', (f['strongs'],)).fetchone():
            if not a.dry_run:
                cur.execute("INSERT INTO strongs(strongs, language) VALUES (?, 'H')", (f['strongs'],))
            inserted_entities += 1
        updates.append((f['strongs'], src_ids[f['strongs_source']], f['word_id']))

    print(f'strongs entities to insert: {inserted_entities}')
    if a.dry_run:
        print('dry-run: wrote nothing; sample updates:')
        for u in updates[:20]:
            print(' ', u)
    else:
        cur.executemany('UPDATE words SET strongs=?, strongs_source_id=? '
                       'WHERE word_id=? AND strongs IS NULL', updates)
        changed = cur.execute('SELECT changes()').fetchone()[0]
        con.commit()
        print(f'updated {len(updates)} words (last-statement changes(): {changed})')
        left = cur.execute('SELECT COUNT(*) FROM words WHERE strongs IS NULL').fetchone()[0]
        print(f'blank strongs remaining in db: {left}')
    con.close()

if __name__ == '__main__':
    main()
