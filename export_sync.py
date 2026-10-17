#!/usr/bin/env python3
"""Export the variants-campaign data from local bible_v2.db for the
sync to the website's PostgreSQL `bible` DB (Kit 2026-10-17: 'add and
sync with website, both word and verse scale variations').
Writes worker-out/sync/*.csv in PG COPY CSV format (NULL as \\N)."""
import csv
import os
import sqlite3

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, 'worker-out', 'sync')
os.makedirs(OUT, exist_ok=True)
db = sqlite3.connect(os.path.join(BASE, 'bible_v2.db'))

JOBS = [
    ('word_variants_textual.csv',
     "SELECT word_id, variant_seq, variant_kind, unpointed, letters,"
     " variant_text, convention, source, witness, variant_type, basis,"
     " created_at FROM word_variants WHERE variant_kind='textual'"),
    ('witness_verses.csv',
     'SELECT verse_id, witness, words, text_syr, text_translit '
     'FROM witness_verses ORDER BY verse_id'),
    ('verse_notes.csv',
     'SELECT verse_id, witness, note_kind, note_text, basis, created_at '
     'FROM verse_notes ORDER BY verse_id'),
]
for fname, sql in JOBS:
    rows = db.execute(sql).fetchall()
    with open(os.path.join(OUT, fname), 'w', encoding='utf-8',
              newline='') as f:
        w = csv.writer(f)
        for r in rows:
            w.writerow(['\\N' if v is None else v for v in r])
    print(fname, len(rows))
