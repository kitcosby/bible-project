#!/usr/bin/env python3
"""STRONGS-BLANK-6008 step 3a: convert newly filled Strong's into KJV coverage.

For every word filled by repair_strongs_blank.py (diagnosis fills whose
words.strongs now equals the diagnosed value), add kjv_renderings rows
using the assembler's exact normalized Strong's-sharing logic from
assemble_bible.py:

    for w in words:
        if not w['strongs']: continue
        for kw, ks in kjv_by_verse.get((w['book'], w['chapter'], w['verse']), []):
            if w['strongs'] in ks:
                rend.append((w['word_id'], kw, ','.join(ks)))

adapted to bible_v2 (kjv_words keyed by verse_id). kjv_strongs is stored
as the normalized set comma-joined, sorted for determinism (U-9
precedent; the assembler joined the same set in arbitrary order). New
rows carry method='strongs-fill'. Existing kjv_renderings rows are NEVER
modified or deleted; any (word_id, kjv_word) pair already present (any
method) is skipped and counted. If a needed composite kjv_strongs string
is missing from the `strongs` entity table, it is inserted together with
its ordered `strongs_components` rows (the migrate_v2.py entity pattern)
so PRAGMA foreign_key_check stays clean.

Usage: convert_strongs_fill_kjv.py --db PATH --diagnosis JSON [--limit N] [--dry-run]
"""
import argparse, json, re, sqlite3, sys

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

    con = sqlite3.connect(a.db)
    cur = con.cursor()
    existing = set((r[0], r[1]) for r in
                   cur.execute('SELECT word_id, kjv_word FROM kjv_renderings'))

    # KJV words by verse_id: (kjv_word, normalized-strongs set)
    kjv_by_verse = {}
    for vid, kw, ks in cur.execute('SELECT verse_id, kjv_word, strongs FROM kjv_words'):
        kjv_by_verse.setdefault(vid, []).append((kw, set(multi_strongs(ks))))

    new_rows, seen_new, new_entities = [], set(), []
    stats = {'words_considered': 0, 'words_not_filled_yet': 0, 'words_repaired': 0,
             'words_no_match': 0, 'rows_added': 0, 'rows_skipped_existing': 0,
             'rows_skipped_intradup': 0}
    known_strongs = {r[0] for r in cur.execute('SELECT strongs FROM strongs')}
    for f in fills:
        row = cur.execute('SELECT verse_id, strongs FROM words WHERE word_id=?',
                          (f['word_id'],)).fetchone()
        if row is None or row[1] != f['strongs']:
            stats['words_not_filled_yet'] += 1
            continue
        stats['words_considered'] += 1
        vid, s = row
        added = 0
        for kw, ks in kjv_by_verse.get(vid, []):
            if s in ks:
                if (f['word_id'], kw) in existing:
                    stats['rows_skipped_existing'] += 1
                    continue
                if (f['word_id'], kw) in seen_new:
                    stats['rows_skipped_intradup'] += 1
                    continue
                kjv_strongs = ','.join(sorted(ks))
                if kjv_strongs not in known_strongs:
                    known_strongs.add(kjv_strongs)
                    new_entities.append(kjv_strongs)
                new_rows.append((f['word_id'], kw, kjv_strongs, 'strongs-fill'))
                seen_new.add((f['word_id'], kw))
                added += 1
        if added:
            stats['words_repaired'] += 1
            stats['rows_added'] += added
        else:
            stats['words_no_match'] += 1

    print('stats:', stats)
    print(f'new strongs entities needed: {len(new_entities)}')
    if a.dry_run:
        print('dry-run: wrote nothing; sample new rows:')
        for r in new_rows[:20]:
            print(' ', r)
    else:
        for comp in new_entities:
            cur.execute("INSERT INTO strongs(strongs, language) VALUES (?, 'H')", (comp,))
            parts = comp.split(',')
            if len(parts) > 1:
                cur.executemany('INSERT INTO strongs_components(strongs, seq, component) '
                                'VALUES (?,?,?)',
                                [(comp, i, p) for i, p in enumerate(parts)])
        cur.executemany('INSERT INTO kjv_renderings(word_id, kjv_word, kjv_strongs, method) '
                        'VALUES (?,?,?,?)', new_rows)
        con.commit()
        print(f'inserted {len(new_rows)} strongs-fill rows')
    con.close()

if __name__ == '__main__':
    main()
