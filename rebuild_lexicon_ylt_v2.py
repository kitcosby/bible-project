#!/usr/bin/env python3
"""Rebuild lexicon_ylt_rendering (v2 child table) from ylt_renderings,
applying the build_lexicon_ylt.py aggregation rule verbatim: distinct
YLT words per (root_id, root_form_seq, vowel_seq), ordered by
descending frequency, ties alphabetical (lowercased) — with first-seen
order (ylt_renderings rendering_id order) as the final tiebreak via
Python's stable sort, matching the v1 build's behavior.

Used 2026-10-17 to apply Kit's YLT-BRIDGE-RERUN-AFTER-U10 ruling
(0.7923 baseline accepted; anchored bridge re-run applied). Procedure
was proven beforehand: recomputing from the PRE-change ylt_renderings
reproduced the stored table on 95,961/95,963 groups exactly (2 groups
differed only in equal-frequency case-twin tie order).
Idempotent: the table is deleted and rebuilt in one transaction.
"""
import sqlite3
import sys
from collections import Counter, defaultdict

DB = sys.argv[1] if len(sys.argv) > 1 else \
    '/home/hatch/workspace/bible-project/bible_v2.db'
con = sqlite3.connect(DB)
cur = con.cursor()
agg = defaultdict(Counter)
for rid, fseq, vseq, yw in cur.execute(
        'SELECT w.root_id, w.root_form_seq, w.root_vowel_seq, y.ylt_word '
        'FROM ylt_renderings y JOIN words w ON w.word_id = y.word_id '
        'ORDER BY y.rendering_id'):
    agg[(rid, fseq, vseq)][yw] += 1
rows = []
for (rid, fseq, vseq), counter in agg.items():
    ordered = sorted(counter.items(), key=lambda kv: (-kv[1], kv[0].lower()))
    for i, (w, _n) in enumerate(ordered):
        rows.append((rid, fseq, vseq, i, w))
cur.execute('DELETE FROM lexicon_ylt_rendering')
cur.executemany(
    'INSERT INTO lexicon_ylt_rendering '
    '(root_id, root_form_seq, vowel_seq, seq, rendering) '
    'VALUES (?,?,?,?,?)', rows)
con.commit()
n = cur.execute('SELECT COUNT(*) FROM lexicon_ylt_rendering').fetchone()[0]
print(f'groups: {len(agg)}; rows inserted: {len(rows)}; table rows: {n}')
con.close()
