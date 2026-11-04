#!/usr/bin/env python3
"""Export the Greek + NT sync bundle from bible_v2.db (companion to
export_sync.py): full-table CSVs in PG COPY format (NULL as \\N) for
worker-out/sync/, loaded on the laptop by load_sync_gnt.py.

Tables: core corpus tables extended by the NT build (books, verses,
kjv_words, ylt_verses -- full replace keeps PG identical to SQLite),
the LXX tables, the three GNT traditions, the variant summary, and
the NT alignment + computed-YLT bridge tables.
"""
import csv
import os
import sqlite3

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, 'worker-out', 'sync')
os.makedirs(OUT, exist_ok=True)
db = sqlite3.connect(os.path.join(BASE, 'bible_v2.db'))

TABLES = [
    'books', 'verses', 'kjv_words', 'ylt_verses',
    'lxx_books', 'lxx_verses', 'lxx_words', 'lxx_crosswalk',
    'gnt_books', 'gnt_verses', 'gnt_words',
    'gntb_books', 'gntb_verses', 'gntb_words',
    'gnts_books', 'gnts_verses', 'gnts_words',
    'gnt_variants', 'gnt_alignment', 'gnt_ylt_renderings',
    'gntb_alignment', 'gntb_ylt_renderings',
    'gnts_alignment', 'gnts_ylt_renderings',
]
for t in TABLES:
    cols = [r[1] for r in db.execute(f"PRAGMA table_info({t})")]
    rows = db.execute(f"SELECT {', '.join(cols)} FROM {t}").fetchall()
    path = os.path.join(OUT, f'gnt_{t}.csv')
    with open(path, 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f, lineterminator='\n')
        for r in rows:
            w.writerow(['\\N' if v is None else v for v in r])
    print(f'{t}: {len(rows)} rows -> gnt_{t}.csv '
          f'({os.path.getsize(path) / 1e6:.1f} MB)')
