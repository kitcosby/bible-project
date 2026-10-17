#!/usr/bin/env python3
"""Build verse-level Syriac (Peshitta) apparatus notes (witness='Syr').

Kit 2026-10-16: Syriac leg, scope (b) — verse-level notes now (the
recommended option, chosen by Kit). Source: ETCBC/peshitta Text-Fabric
v0.5 (Leiden Peshitta main text; Brill apparatus NOT included), text
CC BY-NC 4.0, staged at sources/peshitta. Extraction:
worker-out/peshitta/syr_verses.tsv (extract_syr.py).

What this builds, and what it deliberately does NOT claim:
- witness_verses: the Syriac text of every verse that carries a
  corpus reference (23,006 of the 23,076 canon verses; the other 70
  — Jer 48/49 verse-0 headings, the Dan 3 Prayer-of-Azariah pluses —
  have no corpus verse to anchor to and are counted, not loaded).
- verse_notes, two kinds, both purely measured facts:
  * 'no_counterpart' (214): an MT verse with words has no Syriac
    verse under the same reference. Concentrated in Chronicles (118)
    and Psalms (74) — versification, in most cases the material
    standing under a neighboring reference; the note says exactly
    that and does NOT claim the text is missing from the tradition.
  * 'length_divergence': Syr/MT word-count ratio outside the central
    98% of the measured distribution (ratio < 0.71 or > 2.00;
    percentiles p1/p99 of 23,001 matched verses, median 1.167) with
    an absolute difference of at least 4 words. The note prints both
    counts and the ratio and carries the caveat that translation
    technique can expand or compress — it is a signal to inspect the
    Syriac text (in witness_verses), not a variant verdict.
- NO word-level rows and NO 'orthographic' claims: the Peshitta is a
  translation; Hebrew spelling variants are unrecoverable from it.
  Word-level Syr rows, if ever, will be a hand-adjudicated,
  retroversion-secure subset with per-row reasoning (research doc).

Idempotent: witness='Syr' rows in both tables are deleted first.
Supports --dry-run (full accounting, no writes). Creates the two
tables when absent (they are new with this leg; bible_v2.db had no
notes tables — verified 2026-10-16).
"""
import collections
import json
import os
import sqlite3
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
TSV = os.path.join(BASE, 'worker-out', 'peshitta', 'syr_verses.tsv')
DRY = '--dry-run' in sys.argv
_args = [a for a in sys.argv[1:] if not a.startswith('--')]
DB = _args[0] if _args else os.path.join(BASE, 'bible_v2.db')
LO, HI, MIN_DIFF = 0.71, 2.00, 4
CITATION = ('Peshitta (Leiden edition main text), ETCBC/peshitta '
            'Text-Fabric v0.5, text CC BY-NC 4.0')
BASIS_LEN = (CITATION + '; per-verse word-count ratio vs MT (WLC), '
             'thresholds = central 98% of the measured distribution '
             '(p1 0.714, p99 2.000, median 1.167, n=23,001) and '
             '|difference| >= 4 words')
BASIS_COV = (CITATION + '; reference join on (book, chapter, verse) '
             'against the corpus (BHSA-family versification)')


def main():
    syr = {}
    with open(TSV, encoding='utf-8') as f:
        next(f)
        for line in f:
            p = line.rstrip('\n').split('\t')
            if int(p[0]) == 0:
                continue
            syr[(int(p[0]), int(p[2]), int(p[3]))] = (
                int(p[4]), p[5], p[6])
    db = sqlite3.connect(DB)
    db.row_factory = sqlite3.Row
    st = collections.Counter()
    st['syr_canon_verses'] = len(syr)
    wv_rows = []
    note_rows = []
    corpus_keys = set()
    for vr in db.execute(
            'SELECT verse_id, book_id, chapter, verse FROM verses '
            'ORDER BY book_id, chapter, verse').fetchall():
        key = (vr['book_id'], vr['chapter'], vr['verse'])
        corpus_keys.add(key)
        n_mt = db.execute('SELECT COUNT(*) c FROM words WHERE verse_id=?',
                          (vr['verse_id'],)).fetchone()['c']
        if key not in syr:
            if n_mt > 0:
                st['no_counterpart'] += 1
                note_rows.append((
                    vr['verse_id'], 'no_counterpart',
                    'No Syriac (Peshitta) verse carries this reference '
                    'in the Leiden text. In most such cases the material '
                    'stands under a neighboring reference (versification '
                    'differs, chiefly in Chronicles and Psalms); this '
                    'note records the reference mismatch only and does '
                    'not claim the text is absent from the Syriac '
                    'tradition.', BASIS_COV))
            continue
        n_syr, text_syr, text_tr = syr[key]
        wv_rows.append((vr['verse_id'], n_syr, text_syr, text_tr))
        if n_mt == 0:
            st['matched_empty_mt'] += 1
            continue
        st['matched'] += 1
        ratio = n_syr / n_mt
        if (ratio < LO or ratio > HI) and abs(n_syr - n_mt) >= MIN_DIFF:
            st['length_divergence'] += 1
            direction = 'longer' if ratio > 1 else 'shorter'
            note_rows.append((
                vr['verse_id'], 'length_divergence',
                f'The Syriac (Peshitta) verse runs {n_syr} words '
                f'against {n_mt} in the MT (ratio {ratio:.2f}) — '
                f'substantially {direction}, outside the central 98% '
                f'of verse ratios. That can witness a '
                f'{"plus" if ratio > 1 else "minus"} in the Hebrew '
                f'text behind the Syriac, but translation technique '
                f'also expands and compresses; weigh it with the '
                f'Syriac text itself before treating it as a textual '
                f'variant.', BASIS_LEN))
    st['syr_verses_no_corpus_anchor'] = sum(
        1 for k in syr if k not in corpus_keys)
    st['witness_verse_rows'] = len(wv_rows)
    st['note_rows'] = len(note_rows)
    if DRY:
        print(json.dumps(dict(st), indent=1, ensure_ascii=False))
        print('DRY RUN — no writes')
        return
    db.execute('''CREATE TABLE IF NOT EXISTS witness_verses(
        verse_id INTEGER NOT NULL REFERENCES verses(verse_id),
        witness TEXT NOT NULL,
        words INTEGER NOT NULL,
        text_syr TEXT,
        text_translit TEXT,
        PRIMARY KEY(verse_id, witness))''')
    db.execute('''CREATE TABLE IF NOT EXISTS verse_notes(
        verse_id INTEGER NOT NULL REFERENCES verses(verse_id),
        witness TEXT NOT NULL,
        note_kind TEXT NOT NULL,
        note_text TEXT NOT NULL,
        basis TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY(verse_id, witness, note_kind))''')
    db.execute("DELETE FROM witness_verses WHERE witness='Syr'")
    db.execute("DELETE FROM verse_notes WHERE witness='Syr'")
    db.executemany(
        'INSERT INTO witness_verses (verse_id, witness, words, text_syr,'
        ' text_translit) VALUES (?, ?, ?, ?, ?)',
        [(vid, 'Syr', n, ts, tt) for vid, n, ts, tt in wv_rows])
    db.executemany(
        'INSERT INTO verse_notes (verse_id, witness, note_kind, note_text,'
        ' basis) VALUES (?, ?, ?, ?, ?)',
        [(vid, 'Syr', kind, text, basis)
         for vid, kind, text, basis in note_rows])
    db.commit()
    st['wv_inserted'] = db.execute(
        "SELECT COUNT(*) c FROM witness_verses WHERE witness='Syr'"
    ).fetchone()['c']
    st['notes_inserted'] = db.execute(
        "SELECT COUNT(*) c FROM verse_notes WHERE witness='Syr'"
    ).fetchone()['c']
    print(json.dumps(dict(st), indent=1, ensure_ascii=False))


if __name__ == '__main__':
    main()
