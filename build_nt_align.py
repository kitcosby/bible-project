#!/usr/bin/env python3
"""NT alignment bridges (computed, best-effort -- NOT authoritative).

1. gnt_alignment: KJV word -> TR Greek word positions, extracted from
   the CrossWire KJV NT module's own markup: every <w> element carries
   `src=` (the Greek word positions, in TR order, that the English
   phrase translates) and `lemma.TR:` (the Greek forms themselves).
   Integrity: the (word, strongs) sequence re-derived here must equal
   the shipped kjv_words rows verse by verse, or the run aborts.
   Compatibility: each element's lemma.TR forms are checked against
   our Robinson TR surfaces at the claimed positions (accent-stripped,
   final-sigma normalized); the agreement rate is printed, not assumed.
   Self-closing <w/> stubs (Greek words with no English in the verse)
   create no rows; their positions are counted for coverage.

2. gnt_ylt_renderings: computed Young's per Greek word -- YLT tokens
   are aligned to KJV tokens per verse with the SAME Needleman-Wunsch
   scorer as the OT bridge (build_ylt_align.py: exact 2, stem 1.5,
   fuzzy>=0.85 -> 1, mismatch -1, gap -1), then bridged through
   gnt_alignment. Label 'ylt-bridge-nt'. Same status as the OT
   computed layer: best-effort, labeled, never authoritative.
"""
import difflib
import re
import sqlite3
import string
import unicodedata
from collections import Counter
from html import unescape

from build_nt import kjv_decode_records, NT_BOOKS

DB = 'bible_v2.db'
OSIS2ID = {b[3]: b[0] for b in NT_BOOKS}
STRIP_CHARS = " \t.,;:!?\"'()[]{}<>«»‹›—–-–‐‑“”‘’…*†‡¶§\u00a0"
STRIP = string.punctuation + '—–‘’“”'


# ---- part 1: src extraction (mirrors build_nt.kjv_verse_words) ----

def verse_words_src(text):
    """-> [(word, strongs, [greek positions])] in KJV order."""
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
    t = re.sub(r"<inscription>(.*?)</inscription>", r" \1 ", t,
               flags=re.S | re.I)
    t = re.sub(r"<foreign\b[^>]*>(.*?)</foreign>", r" \1 ", t,
               flags=re.S | re.I)
    t = re.sub(r"<div\b[^>]*/>", " ", t)
    # stubs first: record their positions, then remove
    stub_positions = []

    def stubsub(m):
        sm = re.search(r'src="([\d ,]+)"', m.group(0))
        if sm:
            stub_positions.extend(
                int(x) for x in re.split(r'[ ,]+', sm.group(1)) if x)
        return " "
    t = re.sub(r"<w\b[^>]*/>", stubsub, t)

    def wsub(m):
        attrs, inner = m.group(1), m.group(2)
        nums, srcs = [], []
        lm = re.search(r'lemma="([^"]*)"', attrs)
        if lm:
            for tok in lm.group(1).split():
                if tok.startswith("strong:"):
                    nums.append(tok[7:].upper())
        sm = re.search(r'src="([\d ,]+)"', attrs)
        if sm:
            srcs = [int(x) for x in re.split(r'[ ,]+', sm.group(1)) if x]
        inner = re.sub(r"<[^>]*>", "", inner)
        inner = unescape(inner)
        return " " + " ".join(
            f"\x01{','.join(nums)}|{','.join(map(str, srcs))}\x02{w}"
            for w in inner.split()) + " "
    t = re.sub(r"<w\b([^>]*)>(.*?)</w>", wsub, t, flags=re.S | re.I)

    def asub(m):
        inner = re.sub(r"<[^>]*>", "", m.group(1))
        inner = unescape(inner)
        return " " + " ".join(f"\x01|\x02{w}" for w in inner.split()) + " "
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
            meta, w = m.group(1), m.group(2)
            strongs, _, srcstr = meta.partition('|')
            srcs = [int(x) for x in srcstr.split(',')] if srcstr else []
        else:
            strongs, w, srcs = "", tok, []
        w = w.strip(STRIP_CHARS)
        if w:
            words.append((w, strongs, srcs))
    return words, stub_positions


def walk_records():
    recs = kjv_decode_records()
    book_num = ch = v = None
    for e in recs:
        if not e.strip() or "x-importer" in e:
            continue
        book_m = None
        for m in re.finditer(r'<div\b[^>]*type="book"[^>]*>', e):
            if re.search(r"\ssID\s*=", m.group(0)):
                book_m = m
        if book_m is not None:
            om = re.search(r'osisID="([A-Za-z0-9]+)"', book_m.group(0))
            book_num = OSIS2ID[om.group(1)]
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
        v += 1
        yield (book_num, ch, v), e


def norm_form(s):
    s = ''.join(c for c in unicodedata.normalize('NFD', s)
                if unicodedata.category(c) != 'Mn').lower()
    return s.replace('ς', 'σ').strip(',.;·:!?⸀⸂⸃[]()')


# ---- part 2: YLT<->KJV alignment (scorer copied from build_ylt_align) ----

def tokenize(text):
    toks = []
    for raw in text.split():
        t = raw.strip(STRIP)
        if t:
            toks.append(t)
    return toks


def norm_word(w):
    return w.lower().strip(STRIP)


def stem(w):
    w = norm_word(w)
    for suf in ('ing', 'eth', 'est', 'es', 'ed', "'s", 's'):
        if len(w) > len(suf) + 2 and w.endswith(suf):
            return w[:-len(suf)]
    return w


from functools import lru_cache


@lru_cache(maxsize=None)
def sim(a, b):
    # Memoized: the DP calls sim() per cell, and the same token pairs
    # recur constantly -- without the cache the fuzzy ratio dominates
    # the runtime (the uncached OT-style run did not finish NT in
    # reasonable time). Scores are identical to build_ylt_align.sim.
    na, nb = norm_word(a), norm_word(b)
    if not na or not nb:
        return -1
    if na == nb:
        return 2.0
    if stem(a) == stem(b):
        return 1.5
    r = difflib.SequenceMatcher(None, na, nb).ratio()
    if r >= 0.85:
        return 1.0
    return -1.0


def align(ys, ks):
    m, n = len(ys), len(ks)
    GAP = -1.0
    dp = [[0.0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        dp[i][0] = dp[i - 1][0] + GAP
    for j in range(1, n + 1):
        dp[0][j] = dp[0][j - 1] + GAP
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            dp[i][j] = max(dp[i - 1][j] + GAP, dp[i][j - 1] + GAP,
                           dp[i - 1][j - 1] + sim(ys[i - 1], ks[j - 1]))
    pairs = []
    i, j = m, n
    while i > 0 and j > 0:
        s = sim(ys[i - 1], ks[j - 1])
        if dp[i][j] == dp[i - 1][j - 1] + s:
            if s > 0:
                pairs.append((i - 1, j - 1))
            i -= 1
            j -= 1
        elif dp[i][j] == dp[i - 1][j] + GAP:
            i -= 1
        else:
            j -= 1
    pairs.reverse()
    return pairs


def main():
    db = sqlite3.connect(DB)
    vmap = {(b, c, v): vid for vid, b, c, v in db.execute(
        "SELECT verse_id, book_id, chapter, verse FROM verses "
        "WHERE book_id >= 40")}
    kjv_rows = {}
    for vid, pos, w, s in db.execute(
            "SELECT k.verse_id, k.kjv_pos, k.kjv_word, k.strongs "
            "FROM kjv_words k JOIN verses v ON v.verse_id = k.verse_id "
            "WHERE v.book_id >= 40 ORDER BY k.verse_id, k.kjv_pos"):
        kjv_rows.setdefault(vid, []).append((w, s or ''))
    tr_words = {}
    for gv, pos, surf in db.execute(
            "SELECT gnt_verse_id, position, surface FROM gnt_words "
            "ORDER BY gnt_verse_id, position"):
        tr_words.setdefault(gv, []).append(surf)
    tr_gid = {(b, c, v): gv for gv, b, c, v in db.execute(
        "SELECT gnt_verse_id, book_id, chapter, verse FROM gnt_verses")}

    db.executescript("""
    DROP TABLE IF EXISTS gnt_alignment;
    DROP TABLE IF EXISTS gnt_ylt_renderings;
    CREATE TABLE gnt_alignment (corpus_verse_id INTEGER,
      kjv_pos INTEGER, gnt_position INTEGER,
      PRIMARY KEY (corpus_verse_id, kjv_pos, gnt_position));
    CREATE TABLE gnt_ylt_renderings (gnt_verse_id INTEGER,
      gnt_position INTEGER, ylt_word TEXT, ylt_word_pos INTEGER,
      label TEXT, PRIMARY KEY (gnt_verse_id, gnt_position, ylt_word_pos));
    """)

    stats = Counter()
    align_rows = []
    kjv2greek = {}   # (vid, kjv_pos) -> [gnt positions]
    for ref, raw in walk_records():
        vid = vmap[ref]
        words, stubs = verse_words_src(raw)
        shipped = kjv_rows[vid]
        assert len(words) == len(shipped), \
            f'{ref}: re-derived {len(words)} vs shipped {len(shipped)}'
        for (w, s, _srcs), (sw, ss) in zip(words, shipped):
            assert w == sw and s == ss, f'{ref}: word mismatch {w} vs {sw}'
        gv = tr_gid[ref]
        tw = tr_words[gv]
        for pos, (_w, _s, srcs) in enumerate(words, 1):
            for gp in srcs:
                align_rows.append((vid, pos, gp))
                kjv2greek.setdefault((vid, pos), []).append(gp)
                stats['align_pairs'] += 1
                if 1 <= gp <= len(tw):
                    stats['src_in_range'] += 1
        stats['stub_positions'] += len(set(stubs))
        covered = {gp for (_w, _s, ss2) in words for gp in ss2}
        stats['greek_covered'] += len(covered)
        stats['greek_total'] += len(tw)
        stats['greek_uncovered'] += len(set(range(1, len(tw) + 1)) - covered)
    db.executemany("INSERT INTO gnt_alignment VALUES (?,?,?)", align_rows)
    print('part 1 stats:', dict(stats))

    # lemma.TR compatibility: sample every 37th element is embedded in
    # part 1's assert path only for words; do a direct sample here.
    agree = total = 0
    for ref, raw in walk_records():
        gv = tr_gid[ref]
        tw = tr_words[gv]
        for m in re.finditer(r'<w\b([^>]*)>(.*?)</w>', raw, re.S):
            attrs = m.group(1)
            sm = re.search(r'src="([\d ]+)"', attrs)
            lm = re.search(r'lemma="([^"]*)"', attrs)
            if not sm or not lm:
                continue
            srcs = [int(x) for x in sm.group(1).split()]
            forms = [tok[9:] for tok in lm.group(1).split()
                     if tok.startswith('lemma.TR:')]
            if len(srcs) != len(forms):
                continue
            total += 1
            if all(1 <= p <= len(tw) and
                   norm_form(f) == norm_form(tw[p - 1])
                   for p, f in zip(srcs, forms)):
                agree += 1
        if total >= 4000:
            break
    print(f'lemma.TR vs Robinson TR positions: {agree}/{total} elements '
          f'agree exactly ({100.0 * agree / max(total,1):.1f}%)')

    # ---- part 2: YLT bridge ----
    ylt_text = {vid: t for vid, t in db.execute(
        "SELECT verse_id, text FROM ylt_verses WHERE verse_id IN "
        "(SELECT verse_id FROM verses WHERE book_id >= 40)")}
    rend = []
    cov = Counter()
    for ref, vid in sorted(vmap.items(), key=lambda kv: kv[1]):
        ys = tokenize(ylt_text[vid])
        ks = [w for (w, _s) in kjv_rows[vid]]
        gv = tr_gid[ref]
        hit_positions = set()
        for yi, ki in align(ys, ks):
            for gp in kjv2greek.get((vid, ki + 1), []):
                rend.append((gv, gp, ys[yi], yi + 1, 'ylt-bridge-nt'))
                hit_positions.add(gp)
        cov['greek_words_with_ylt'] += len(hit_positions)
        cov['greek_words_total'] += len(tr_words[gv])
    db.executemany(
        "INSERT OR IGNORE INTO gnt_ylt_renderings VALUES (?,?,?,?,?)", rend)
    db.commit()
    print(f'part 2: {len(rend)} rendering rows; Greek words with >=1 '
          f'YLT rendering: {cov["greek_words_with_ylt"]} / '
          f'{cov["greek_words_total"]}')


if __name__ == '__main__':
    main()
