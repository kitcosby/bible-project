#!/usr/bin/env python3
"""Add the scholarly and Byzantine Greek NT traditions as variant
witnesses alongside the primary Textus Receptus (Kit's order,
2026-11-03: "First add the scholarly and Byzantine variants").

Sources:
  Byzantine : Robinson-Pierpont Majority Text, csv-unicode with
              parsing (sources/gnt-byz/), released under the
              Unlicense / public domain (LICENSE.txt staged with it).
              Unicode Greek (unaccented), Strong's, Robinson morph.
  Scholarly : SBLGNT in MorphGNT's morphological tagging
              (sources/gnt-sbl/). SBLGNT text under the SBLGNT EULA;
              MorphGNT parsing + lemmatization CC BY-SA 3.0 (upstream
              README staged with the data). Accented forms + lemmas;
              no Strong's numbers in this source.

Tables (rebuilt each run; the TR tables from build_nt.py are the
primary text and are NOT touched):
  gntb_books / gntb_verses / gntb_words   Byzantine
  gnts_books / gnts_verses / gnts_words   SBLGNT (extra columns:
                                          lemma, norm form)
  gnt_variants  per corpus verse and tradition:
                status 'same' | 'variant' | 'absent', plus rows with
                corpus_verse_id NULL for tradition verses that have
                no corpus (KJV-grid) reference ('extra').
                Comparison basis is stamped per row:
                byz -- Strong's-number sequence vs TR (exact);
                sbl -- accent-stripped lowercase form sequence vs TR
                (MorphGNT carries no Strong's), with a difflib
                similarity ratio stored in `detail`.
"""
import csv
import difflib
import glob
import os
import re
import sqlite3
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, 'bible_v2.db')
BYZ_DIR = os.path.join(HERE, 'sources', 'gnt-byz')
SBL_DIR = os.path.join(HERE, 'sources', 'gnt-sbl')

# Byzantine CSV file stems, in canonical NT order (book_id 40..66)
CODES = ['MAT', 'MAR', 'LUK', 'JOH', 'ACT', 'ROM', '1CO', '2CO', 'GAL',
         'EPH', 'PHP', 'COL', '1TH', '2TH', '1TI', '2TI', 'TIT', 'PHM',
         'HEB', 'JAM', '1PE', '2PE', '1JO', '2JO', '3JO', 'JUD', 'REV']
CODE2ID = {c: 40 + i for i, c in enumerate(CODES)}
# MorphGNT file numbers 61..87 in canonical order
SBL_FILES = {61 + i: c for i, c in enumerate(
    ['Mt', 'Mk', 'Lk', 'Jn', 'Ac', 'Ro', '1Co', '2Co', 'Ga', 'Eph',
     'Php', 'Col', '1Th', '2Th', '1Ti', '2Ti', 'Tit', 'Phm', 'Heb',
     'Jas', '1Pe', '2Pe', '1Jn', '2Jn', '3Jn', 'Jud', 'Re'])}


def parse_byz():
    out = {}
    for code, bid in CODE2ID.items():
        path = os.path.join(BYZ_DIR, code + '.csv')
        with open(path, encoding='utf-8-sig', newline='') as f:
            for row in csv.DictReader(f):
                ch, v = int(row['chapter']), int(row['verse'])
                words = []
                for wm in re.finditer(r'(\S+)\s+(\d+)\s*\{([^}]*)\}',
                                      row['text']):
                    words.append((wm.group(1), 'G' + wm.group(2),
                                  wm.group(3)))
                assert words, f'{code} {ch}:{v} no words parsed'
                out[(bid, ch, v)] = words
    return out


def parse_sbl():
    out = {}
    for fnum, stem in SBL_FILES.items():
        bid = fnum - 21
        path = os.path.join(SBL_DIR, f'{fnum}-{stem}-morphgnt.txt')
        with open(path, encoding='utf-8') as f:
            for line in f:
                parts = line.rstrip('\n').split(' ')
                if len(parts) < 7 or not parts[0].isdigit():
                    continue
                ref = parts[0]
                ch, v = int(ref[2:4]), int(ref[4:6])
                pos, parse = parts[1], parts[2]
                form, norm, lemma = parts[3], parts[4], parts[5]
                out.setdefault((bid, ch, v), []).append(
                    (form, norm, lemma, f'{pos} {parse}'))
    return out


def strip_accents(s):
    # Comparison form: accents/breathings stripped, lowercased, and
    # printed punctuation removed -- MorphGNT word forms carry the
    # edition's punctuation attached (e.g. 'logos,' / 'logos.'),
    # which otherwise poisons every verse comparison. Stored surfaces
    # keep the punctuation; only this comparison key strips it.
    s = ''.join(c for c in unicodedata.normalize('NFD', s)
                if unicodedata.category(c) != 'Mn').lower()
    return s.strip(',.;·:!?⸀⸂⸃[]()')


def main():
    byz = parse_byz()
    sbl = parse_sbl()
    print(f'Byz: {len(byz)} verses, '
          f'{sum(len(w) for w in byz.values())} words')
    print(f'SBL: {len(sbl)} verses, '
          f'{sum(len(w) for w in sbl.values())} words')

    db = sqlite3.connect(DB)
    vmap = {(b, c, v): vid for vid, b, c, v in db.execute(
        "SELECT verse_id, book_id, chapter, verse FROM verses")}
    tr = {}
    for gv, bid, ch, v in db.execute(
            "SELECT gnt_verse_id, book_id, chapter, verse FROM gnt_verses"):
        tr[(bid, ch, v)] = gv
    tr_strongs = {}
    tr_forms = {}
    for gv, pos, strongs, surface in db.execute(
            "SELECT gnt_verse_id, position, strongs, surface "
            "FROM gnt_words ORDER BY gnt_verse_id, position"):
        tr_strongs.setdefault(gv, []).append(strongs)
        tr_forms.setdefault(gv, []).append(strip_accents(surface))

    db.executescript("""
    DROP TABLE IF EXISTS gnt_variants;
    DROP TABLE IF EXISTS gntb_words; DROP TABLE IF EXISTS gntb_verses;
    DROP TABLE IF EXISTS gntb_books;
    DROP TABLE IF EXISTS gnts_words; DROP TABLE IF EXISTS gnts_verses;
    DROP TABLE IF EXISTS gnts_books;
    CREATE TABLE gntb_books (book_id INTEGER PRIMARY KEY, code TEXT,
      name TEXT, note TEXT);
    CREATE TABLE gntb_verses (gnt_verse_id INTEGER PRIMARY KEY,
      corpus_verse_id INTEGER, book_id INTEGER, chapter INTEGER,
      verse INTEGER, text TEXT);
    CREATE INDEX idx_gntb_ref ON gntb_verses(book_id, chapter, verse);
    CREATE TABLE gntb_words (gnt_verse_id INTEGER, position INTEGER,
      surface TEXT, strongs TEXT, morph TEXT,
      PRIMARY KEY (gnt_verse_id, position));
    CREATE TABLE gnts_books (book_id INTEGER PRIMARY KEY, code TEXT,
      name TEXT, note TEXT);
    CREATE TABLE gnts_verses (gnt_verse_id INTEGER PRIMARY KEY,
      corpus_verse_id INTEGER, book_id INTEGER, chapter INTEGER,
      verse INTEGER, text TEXT);
    CREATE INDEX idx_gnts_ref ON gnts_verses(book_id, chapter, verse);
    CREATE TABLE gnts_words (gnt_verse_id INTEGER, position INTEGER,
      surface TEXT, norm TEXT, lemma TEXT, morph TEXT,
      PRIMARY KEY (gnt_verse_id, position));
    CREATE TABLE gnt_variants (corpus_verse_id INTEGER,
      tradition TEXT, status TEXT, basis TEXT, detail TEXT);
    CREATE INDEX idx_gntvar ON gnt_variants(corpus_verse_id, tradition);
    """)
    names = {r[0]: r[1] for r in db.execute(
        "SELECT book_id, name FROM gnt_books")}
    for code, bid in CODE2ID.items():
        db.execute("INSERT INTO gntb_books VALUES (?,?,?,?)",
                   (bid, code, names[bid],
                    'Byzantine Majority Text (Robinson-Pierpont), '
                    'Unlicense/public domain'))
        db.execute("INSERT INTO gnts_books VALUES (?,?,?,?)",
                   (bid, code, names[bid],
                    'SBLGNT (SBLGNT EULA) + MorphGNT parsing '
                    '(CC BY-SA 3.0)'))

    gid = 0
    for ref in sorted(byz):
        gid += 1
        db.execute("INSERT INTO gntb_verses VALUES (?,?,?,?,?,?)",
                   (gid, vmap.get(ref), *ref,
                    ' '.join(w[0] for w in byz[ref])))
        for pos, (surf, strongs, morph) in enumerate(byz[ref], 1):
            db.execute("INSERT INTO gntb_words VALUES (?,?,?,?,?)",
                       (gid, pos, surf, strongs, morph))
    print(f'gntb_verses {gid}')
    gid = 0
    for ref in sorted(sbl):
        gid += 1
        db.execute("INSERT INTO gnts_verses VALUES (?,?,?,?,?,?)",
                   (gid, vmap.get(ref), *ref,
                    ' '.join(w[0] for w in sbl[ref])))
        for pos, (form, norm, lemma, morph) in enumerate(sbl[ref], 1):
            db.execute("INSERT INTO gnts_words VALUES (?,?,?,?,?,?)",
                       (gid, pos, form, norm, lemma, morph))
    print(f'gnts_verses {gid}')

    # Variant summary against the TR primary.
    counts = {}
    def add(vid, trad, status, basis, detail=''):
        db.execute("INSERT INTO gnt_variants VALUES (?,?,?,?,?)",
                   (vid, trad, status, basis, detail))
        counts[(trad, status)] = counts.get((trad, status), 0) + 1

    for ref, gv in tr.items():
        vid = vmap.get(ref)
        ts = tr_strongs[gv]
        tf = tr_forms[gv]
        if ref in byz:
            bs = [w[1] for w in byz[ref]]
            add(vid, 'byz', 'same' if bs == ts else 'variant',
                'strongs-sequence',
                '' if bs == ts else
                f'TR {len(ts)} words vs Byz {len(bs)} words')
        else:
            add(vid, 'byz', 'absent', 'strongs-sequence', '')
        if ref in sbl:
            sf = [strip_accents(w[0]) for w in sbl[ref]]
            if sf == tf:
                add(vid, 'sbl', 'same', 'form-sequence', '')
            else:
                ratio = difflib.SequenceMatcher(
                    None, tf, sf).ratio()
                add(vid, 'sbl', 'variant', 'form-sequence',
                    f'similarity {ratio:.3f}; TR {len(tf)} vs '
                    f'SBL {len(sf)} words')
        else:
            add(vid, 'sbl', 'absent', 'form-sequence', '')
    for ref in sorted(set(byz) - set(tr)):
        add(None, 'byz', 'extra', 'strongs-sequence',
            f'Byz-only ref book {ref[0]} {ref[1]}:{ref[2]}')
    for ref in sorted(set(sbl) - set(tr)):
        add(None, 'sbl', 'extra', 'form-sequence',
            f'SBL-only ref book {ref[0]} {ref[1]}:{ref[2]}')
    db.commit()
    for k in sorted(counts):
        print('variants', k, counts[k])


if __name__ == '__main__':
    main()
