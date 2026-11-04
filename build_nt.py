#!/usr/bin/env python3
"""Extend the corpus to the New Testament (Kit's order, 2026-11-03):
KJV, Young's (YLT), and Greek — Greek primary text = Textus Receptus
(Kit's ruling: the Greek text behind the KJV and Young's).

Sources (all verified on disk; see NT section of NOTATION_LEDGER):
  Greek : byztxt/greektext-textus-receptus — Robinson's parsed TR,
          PUBLIC DOMAIN ("Copy freely"). Beta-code surfaces
          (unaccented), Strong's numbers, Robinson morphology codes.
          Beta is converted to (unaccented) Greek script for `surface`;
          the beta string itself is kept in `beta`.
  KJV   : CrossWire SWORD KJV module 3.1 (worker-out/kjv zip), the NT
          testament decoded with the same zText/OSIS logic as the OT
          builder (worker-out/kjv/build_kjv_words.py, GPL module text).
  YLT   : ebible.org engylt USFM (public domain), NT files parsed with
          the same rules as worker-out/ylt/parse_ylt.py.

Build (idempotent for the NT range; OT rows are never touched):
  1. books 40..66 inserted if absent (name_he carries the Greek title).
  2. verses: NT verse rows created for the UNION of refs seen in the
     KJV parse, the YLT parse, and the TR parse (each source's own
     grid is preserved in its tables; grid differences are reported).
  3. kjv_words: NT rows replaced wholesale (delete by NT verse_id,
     reinsert).
  4. ylt_verses: NT rows replaced wholesale.
  5. gnt_books / gnt_verses / gnt_words rebuilt from the TR files;
     gnt_verses.corpus_verse_id links to `verses` where the ref exists.
"""
import glob
import os
import re
import sqlite3
import struct
import zipfile
import zlib
from collections import Counter
from html import unescape

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, 'bible_v2.db')
KJV_ZIP = os.path.join(HERE, 'worker-out', 'kjv', 'KJV-crosswire-3.1.zip')
YLT_DIR = os.path.join(HERE, 'worker-out', 'ylt', 'usfm')
TR_DIR = os.path.join(HERE, 'sources', 'gnt-tr', 'parsed')

# book_id -> (name_en, greek title, KJV OSIS id, YLT USFM code, TR file code)
NT_BOOKS = [
    (40, 'Matthew', 'Ματθαῖος', 'Matt', 'MAT', 'MT'),
    (41, 'Mark', 'Μάρκος', 'Mark', 'MRK', 'MR'),
    (42, 'Luke', 'Λουκᾶς', 'Luke', 'LUK', 'LU'),
    (43, 'John', 'Ἰωάννης', 'John', 'JHN', 'JOH'),
    (44, 'Acts', 'Πράξεις', 'Acts', 'ACT', 'AC'),
    (45, 'Romans', 'Ῥωμαίους', 'Rom', 'ROM', 'RO'),
    (46, '1 Corinthians', 'Κορινθίους Α', '1Cor', '1CO', '1CO'),
    (47, '2 Corinthians', 'Κορινθίους Β', '2Cor', '2CO', '2CO'),
    (48, 'Galatians', 'Γαλάτας', 'Gal', 'GAL', 'GA'),
    (49, 'Ephesians', 'Ἐφεσίους', 'Eph', 'EPH', 'EPH'),
    (50, 'Philippians', 'Φιλιππησίους', 'Phil', 'PHP', 'PHP'),
    (51, 'Colossians', 'Κολοσσαεῖς', 'Col', 'COL', 'COL'),
    (52, '1 Thessalonians', 'Θεσσαλονικεῖς Α', '1Thess', '1TH', '1TH'),
    (53, '2 Thessalonians', 'Θεσσαλονικεῖς Β', '2Thess', '2TH', '2TH'),
    (54, '1 Timothy', 'Τιμόθεον Α', '1Tim', '1TI', '1TI'),
    (55, '2 Timothy', 'Τιμόθεον Β', '2Tim', '2TI', '2TI'),
    (56, 'Titus', 'Τίτον', 'Titus', 'TIT', 'TIT'),
    (57, 'Philemon', 'Φιλήμονα', 'Phlm', 'PHM', 'PHM'),
    (58, 'Hebrews', 'Ἑβραίους', 'Heb', 'HEB', 'HEB'),
    (59, 'James', 'Ἰάκωβος', 'Jas', 'JAS', 'JAS'),
    (60, '1 Peter', 'Πέτρος Α', '1Pet', '1PE', '1PE'),
    (61, '2 Peter', 'Πέτρος Β', '2Pet', '2PE', '2PE'),
    (62, '1 John', 'Ἰωάννης Α', '1John', '1JN', '1JO'),
    (63, '2 John', 'Ἰωάννης Β', '2John', '2JN', '2JO'),
    (64, '3 John', 'Ἰωάννης Γ', '3John', '3JN', '3JO'),
    (65, 'Jude', 'Ἰούδας', 'Jude', 'JUD', 'JUDE'),
    (66, 'Revelation', 'Ἀποκάλυψις', 'Rev', 'REV', 'RE'),
]
OSIS2ID = {b[3]: b[0] for b in NT_BOOKS}
USFM2ID = {b[4]: b[0] for b in NT_BOOKS}
TR2ID = {b[5]: b[0] for b in NT_BOOKS}

STRIP_CHARS = " \t.,;:!?\"'()[]{}<>«»‹›—–-–‐‑“”‘’…*†‡¶§\u00a0"

# ---------------- KJV (CrossWire zText, NT testament) ----------------
# Decoder + OSIS word parser mirror worker-out/kjv/build_kjv_words.py.


def kjv_decode_records():
    z = zipfile.ZipFile(KJV_ZIP)
    base = "modules/texts/ztext/kjv/nt"
    comp = z.read(base + ".bzv")
    idx = z.read(base + ".bzs")
    txt = z.read(base + ".bzz")
    blocks = []
    for b in range(len(idx) // 12):
        blockStart, blockSize, uncompSize = struct.unpack_from(
            "<III", idx, b * 12)
        data = zlib.decompress(txt[blockStart:blockStart + blockSize])
        assert len(data) == uncompSize
        blocks.append(data)
    recs = []
    for i in range(len(comp) // 10):
        blockNum, verseStart, verseSize = struct.unpack_from(
            "<IIH", comp, i * 10)
        if verseSize == 0:
            recs.append("")
        else:
            recs.append(blocks[blockNum][verseStart:verseStart + verseSize]
                        .decode("utf-8", errors="replace"))
    return recs


def kjv_verse_words(text, stats):
    t = text
    t = re.sub(r"<note\b.*?</note>", " ", t, flags=re.S | re.I)
    t = re.sub(r'<title\b[^>]*type="(main|chapter)"[^>]*>.*?</title>', " ",
               t, flags=re.S | re.I)
    t = re.sub(r"<divineName>(.*?)</divineName>",
               lambda m: unescape(m.group(1)).upper(), t, flags=re.S | re.I)
    t = re.sub(r"<milestone[^>]*/>", " ", t, flags=re.I)
    t = re.sub(r'<div\b[^>]*type="x-milestone"[^>]*/>', " ", t, flags=re.I)
    t = re.sub(r"<chapter\b[^>]*>", " ", t, flags=re.I)
    t = re.sub(r'<div\b[^>]*type="book"[^>]*>', " ", t, flags=re.I)
    t = re.sub(r'<title\b[^>]*type="psalm"[^>]*>(.*?)</title>', r" \1 ", t,
               flags=re.S | re.I)
    t = re.sub(r'<title\b[^>]*type="acrostic"[^>]*>(.*?)</title>', r" \1 ", t,
               flags=re.S | re.I)
    t = re.sub(r"<inscription>(.*?)</inscription>", r" \1 ", t,
               flags=re.S | re.I)
    t = re.sub(r"<foreign\b[^>]*>(.*?)</foreign>", r" \1 ", t,
               flags=re.S | re.I)
    t = re.sub(r"<div\b[^>]*/>", " ", t)

    def wsub(m):
        attrs, inner = m.group(1), m.group(2)
        nums = []
        lm = re.search(r'lemma="([^"]*)"', attrs)
        if lm:
            for tok in lm.group(1).split():
                if tok.startswith("strong:"):
                    nums.append(tok[7:].upper())
        inner = re.sub(r"<[^>]*>", "", inner)
        inner = unescape(inner)
        stats["keyed_words"] += len(inner.split())
        return " " + " ".join(
            f"\x01{','.join(nums)}\x02{w}" for w in inner.split()) + " "
    t = re.sub(r"<w\b([^>]*)>(.*?)</w>", wsub, t, flags=re.S | re.I)

    def asub(m):
        inner = re.sub(r"<[^>]*>", "", m.group(1))
        inner = unescape(inner)
        stats["added_words"] += len(inner.split())
        return " " + " ".join(f"\x01\x02{w}" for w in inner.split()) + " "
    t = re.sub(r'<transChange\b[^>]*type="added"[^>]*>(.*?)</transChange>',
               asub, t, flags=re.S | re.I)
    t = re.sub(r"<transChange\b[^>]*>(.*?)</transChange>", r" \1 ", t,
               flags=re.S | re.I)
    t = re.sub(r"<[^>]*>", " ", t)
    t = unescape(t)
    words = []
    for tok in t.split():
        m = re.match(r"\x01([^\x02]*)\x02(.*)$", tok, re.S)
        if m:
            strongs, w = m.group(1), m.group(2)
        else:
            strongs, w = "", tok
        w = w.strip(STRIP_CHARS)
        if w:
            words.append((w, strongs))
    return words


def parse_kjv():
    """-> {(book_id, ch, v): [(word, strongs), ...]} in KJV NT grid."""
    recs = kjv_decode_records()
    stats = Counter()
    out = {}
    book_num = ch = v = None
    # NT module records carry NO <verse> milestones: the record stream
    # itself is the versification walk -- a book record, a chapter
    # record, then one record per verse in order. Self-closing <w/>
    # stubs at a verse record's head are displaced Greek words whose
    # English sits later in the same record; the word parser skips
    # them (they have no </w> and no English content).
    for e in recs:
        if not e.strip() or "x-importer" in e:
            continue
        book_m = None
        for m in re.finditer(r'<div\b[^>]*type="book"[^>]*>', e):
            if re.search(r"\ssID\s*=", m.group(0)):
                book_m = m
        if book_m is not None:
            om = re.search(r'osisID="([A-Za-z0-9]+)"', book_m.group(0))
            abbr = om.group(1) if om else None
            assert abbr in OSIS2ID, f"unknown NT book {abbr}"
            book_num = OSIS2ID[abbr]
            ch, v = None, 0
            continue
        ch_m = None
        for m in re.finditer(r"<chapter\b[^>]*>", e):
            if re.search(r"\ssID\s*=", m.group(0)):
                ch_m = m
        if ch_m is not None:
            om = re.search(r'osisID="[A-Za-z0-9]+\.(\d+)"', ch_m.group(0))
            ch = int(om.group(1))
            v = 0
            continue
        assert book_num is not None and ch is not None, \
            f'verse record before any book/chapter: {e[:80]}'
        v += 1
        words = kjv_verse_words(e, stats)
        assert words, f'empty verse at {book_num} {ch}:{v}'
        out[(book_num, ch, v)] = words
    print(f'KJV NT: {len(out)} verses, '
          f'{sum(len(x) for x in out.values())} words, stats {dict(stats)}')
    return out


# ---------------- YLT (ebible USFM) ----------------

RE_CH = re.compile(r"^\\c\s+(\d+)\s*$")
RE_V = re.compile(r"^\\v\s+(\d+)\s?(.*)$")
RE_STRAY = re.compile(r"\\[a-zA-Z]+\d*\*?")


def parse_ylt():
    out = {}
    for path in sorted(glob.glob(os.path.join(YLT_DIR, '*.usfm'))):
        m = re.search(r'-([A-Z0-9]{3})engylt\.usfm$', path)
        if not m or m.group(1) not in USFM2ID:
            continue
        bid = USFM2ID[m.group(1)]
        ch = v = None
        buf = []
        def flush():
            if v is not None and buf:
                text = RE_STRAY.sub('', ' '.join(buf))
                text = re.sub(r'\s+', ' ', text).strip()
                if text:
                    out[(bid, ch, v)] = text
        with open(path, encoding='utf-8-sig') as f:
            for raw in f:
                line = raw.strip()
                mc = RE_CH.match(line)
                mv = RE_V.match(line)
                if mc:
                    flush()
                    ch, v, buf = int(mc.group(1)), None, []
                elif mv:
                    flush()
                    v = int(mv.group(1))
                    buf = [mv.group(2)]
                elif line.startswith('\\'):
                    continue
                elif v is not None:
                    buf.append(line)
        flush()
    print(f'YLT NT: {len(out)} verses')
    return out


# ---------------- TR Greek (Robinson parsed, beta code) ----------------

# Robinson transliteration -> Greek script. NOTE: Robinson's scheme
# swaps c/x against TLG beta code -- c = chi (cariv = charis,
# cristov = christos, ecw = echo) and x = xi (sarx, exousia, ex = hex).
# Verified against Strong's-keyed specimens before first load.
BETA = {'a': 'α', 'b': 'β', 'g': 'γ', 'd': 'δ', 'e': 'ε', 'z': 'ζ',
        'h': 'η', 'q': 'θ', 'i': 'ι', 'k': 'κ', 'l': 'λ', 'm': 'μ',
        'n': 'ν', 'c': 'χ', 'o': 'ο', 'p': 'π', 'r': 'ρ', 's': 'σ',
        'v': 'ς', 't': 'τ', 'u': 'υ', 'f': 'φ', 'x': 'ξ', 'y': 'ψ',
        'w': 'ω'}


def beta2greek(s):
    return ''.join(BETA.get(ch, ch) for ch in s)


def parse_tr():
    """-> {(book_id, ch, v): [(greek, beta, strongs, aux, morph), ...]}"""
    out = {}
    for code, bid in TR2ID.items():
        path = os.path.join(TR_DIR, code + '.UTR')
        with open(path, encoding='utf-8', errors='replace') as f:
            verse_strs = []
            cur = None
            for line in f:
                line = line.strip()
                if not line:
                    continue
                if re.match(r'^\d+:\d+\s', line):
                    if cur is not None:
                        verse_strs.append(cur)
                    cur = line
                else:
                    cur += ' ' + line  # wrapped verse, ~72-col lines
            if cur is not None:
                verse_strs.append(cur)
            for line in verse_strs:
                m = re.match(r'^(\d+):(\d+)\s+(.*)$', line, re.S)
                assert m, f'{code}: bad verse {line[:60]}'
                ch, v, rest = int(m.group(1)), int(m.group(2)), m.group(3)
                words = []
                for wm in re.finditer(
                        r'(\S+)\s+(\d+(?:\s+\d+)?)\s*\{([^}]*)\}', rest):
                    beta, nums, morph = wm.group(1), wm.group(2).split(), \
                        wm.group(3)
                    words.append((beta2greek(beta), beta,
                                  'G' + nums[0],
                                  nums[1] if len(nums) > 1 else None,
                                  morph))
                assert words, f'{code} {ch}:{v} parsed no words'
                out[(bid, ch, v)] = words
    print(f'TR NT: {len(out)} verses, '
          f'{sum(len(x) for x in out.values())} words')
    return out


# ---------------- build ----------------

def main():
    kjv = parse_kjv()
    ylt = parse_ylt()
    tr = parse_tr()

    db = sqlite3.connect(DB)
    for bid, name_en, name_gr, *_ in NT_BOOKS:
        db.execute("INSERT OR IGNORE INTO books VALUES (?,?,?)",
                   (bid, name_en, name_gr))

    refs = set(kjv) | set(ylt) | set(tr)
    have = {(b, c, v) for b, c, v in db.execute(
        "SELECT book_id, chapter, verse FROM verses")}
    nxt = db.execute("SELECT COALESCE(MAX(verse_id),0) FROM verses"
                     ).fetchone()[0]
    vmap = {(b, c, v): vid for vid, b, c, v in db.execute(
        "SELECT verse_id, book_id, chapter, verse FROM verses")}
    for ref in sorted(refs - have):
        nxt += 1
        db.execute("INSERT INTO verses VALUES (?,?,?,?)", (nxt, *ref))
        vmap[ref] = nxt
    print(f'verses: NT grid {len(refs)} refs')

    nt_vids = [vmap[r] for r in refs]
    q = ','.join('?' * len(nt_vids))
    db.execute(f"DELETE FROM kjv_words WHERE verse_id IN ({q})", nt_vids)
    db.execute(f"DELETE FROM ylt_verses WHERE verse_id IN ({q})", nt_vids)
    n_kjv = 0
    for ref, words in kjv.items():
        for pos, (w, s) in enumerate(words, 1):
            db.execute("INSERT INTO kjv_words (verse_id, kjv_pos, kjv_word,"
                       " strongs) VALUES (?,?,?,?)",
                       (vmap[ref], pos, w, s or None))
            n_kjv += 1
    for ref, text in ylt.items():
        db.execute("INSERT INTO ylt_verses VALUES (?,?)", (vmap[ref], text))
    print(f'kjv_words NT rows {n_kjv}; ylt_verses NT rows {len(ylt)}')

    db.executescript("""
    DROP TABLE IF EXISTS gnt_words;
    DROP TABLE IF EXISTS gnt_verses;
    DROP TABLE IF EXISTS gnt_books;
    CREATE TABLE gnt_books (
      book_id INTEGER PRIMARY KEY, code TEXT, name TEXT, note TEXT);
    CREATE TABLE gnt_verses (
      gnt_verse_id INTEGER PRIMARY KEY, corpus_verse_id INTEGER,
      book_id INTEGER, chapter INTEGER, verse INTEGER, text TEXT);
    CREATE INDEX idx_gnt_verses_ref ON gnt_verses(book_id, chapter, verse);
    CREATE TABLE gnt_words (
      gnt_verse_id INTEGER, position INTEGER, surface TEXT, beta TEXT,
      strongs TEXT, strongs_aux TEXT, morph TEXT,
      PRIMARY KEY (gnt_verse_id, position));
    CREATE INDEX idx_gnt_words_strongs ON gnt_words(strongs);
    """)
    for bid, name_en, _g, _o, _u, code in NT_BOOKS:
        db.execute("INSERT INTO gnt_books VALUES (?,?,?,?)",
                   (bid, code, name_en,
                    'Textus Receptus (Robinson parsed), public domain'))
    gid = 0
    n_gw = 0
    for ref in sorted(tr):
        gid += 1
        words = tr[ref]
        db.execute("INSERT INTO gnt_verses VALUES (?,?,?,?,?,?)",
                   (gid, vmap.get(ref), ref[0], ref[1], ref[2],
                    ' '.join(w[0] for w in words)))
        for pos, (greek, beta, strongs, aux, morph) in enumerate(words, 1):
            db.execute("INSERT INTO gnt_words VALUES (?,?,?,?,?,?,?)",
                       (gid, pos, greek, beta, strongs, aux, morph))
            n_gw += 1
    db.commit()
    print(f'gnt_verses {gid}; gnt_words {n_gw}')
    # grid differences, for the record
    for label, a, b in [('KJV vs TR', set(kjv), set(tr)),
                        ('KJV vs YLT', set(kjv), set(ylt))]:
        d1, d2 = sorted(a - b), sorted(b - a)
        print(f'{label}: only-first {len(d1)} {d1[:8]} | '
              f'only-second {len(d2)} {d2[:8]}')


if __name__ == '__main__':
    main()
