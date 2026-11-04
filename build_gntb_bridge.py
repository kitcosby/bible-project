#!/usr/bin/env python3
"""Byzantine alignment bridge (VARIANT_BRIDGES_PLAN_2026-11-03).

Per Byzantine verse: (1) NW-align Byzantine Greek words to the TR words
of the same verse (scorer: Strong's equality 2.0, accent-stripped form
equality 1.5); (2) an aligned word inherits the TR word's KJV phrase
(CrossWire gnt_alignment) and computed-Young's phrase
(gnt_ylt_renderings); (3) residue pass: unaligned Byzantine words are
NW-aligned to the verse's leftover English tokens with a gloss-token
scorer; still-unmatched words get no phrase (honest gap).

Outputs (with --write): gntb_alignment (KJV links, mirroring
gnt_alignment) and gntb_ylt_renderings (mirroring gnt_ylt_renderings,
label 'ylt-bridge-byz'). Without --write it only evaluates:
'same'-verse self-consistency on a sample, silver-standard agreement
on variant verses, and printed specimens.
"""
import difflib
import sqlite3
import sys
import unicodedata
from collections import Counter, defaultdict
from functools import lru_cache

DB = 'bible_v2.db'
STRIP = ".,;:!?\"'()[]—-«»"
WRITE = '--write' in sys.argv


def norm_form(s):
    s = ''.join(c for c in unicodedata.normalize('NFD', s)
                if unicodedata.category(c) != 'Mn').lower()
    return s.replace('ς', 'σ').strip(',.;·:!?⸀⸂⸃[]()')


def tokenize(text):
    return [t for raw in text.split()
            if (t := raw.strip(STRIP))]


def norm_word(w):
    return w.lower().strip(STRIP)


def stem(w):
    w = norm_word(w)
    for suf in ('ing', 'eth', 'est', 'es', 'ed', "'s", 's'):
        if len(w) > len(suf) + 2 and w.endswith(suf):
            return w[:-len(suf)]
    return w


@lru_cache(maxsize=None)
def sim(a, b):
    na, nb = norm_word(a), norm_word(b)
    if not na or not nb:
        return -1
    if na == nb:
        return 2.0
    if stem(a) == stem(b):
        return 1.5
    r = difflib.SequenceMatcher(None, na, nb).ratio()
    return 1.0 if r >= 0.85 else -1.0


def nw_pairs(xs, ys, score):
    """Generic NW; returns [(i, j)] with score > 0."""
    m, n = len(xs), len(ys)
    GAP = -1.0
    dp = [[0.0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        dp[i][0] = dp[i - 1][0] + GAP
    for j in range(1, n + 1):
        dp[0][j] = dp[0][j - 1] + GAP
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            dp[i][j] = max(dp[i - 1][j] + GAP, dp[i][j - 1] + GAP,
                           dp[i - 1][j - 1] + score(xs[i - 1], ys[j - 1]))
    pairs = []
    i, j = m, n
    while i > 0 and j > 0:
        s = score(xs[i - 1], ys[j - 1])
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
    db.row_factory = sqlite3.Row

    gloss_of = {}
    for r in db.execute(
            'SELECT strongs, gloss, COUNT(*) AS n FROM lxx_words '
            'WHERE strongs IS NOT NULL AND gloss IS NOT NULL '
            "AND gloss <> '' GROUP BY strongs, gloss"):
        if r['strongs'] not in gloss_of or r['n'] > gloss_of[r['strongs']][0]:
            gloss_of[r['strongs']] = (r['n'], r['gloss'])
    gloss_toks = {s: [norm_word(t) for t in g.replace(';', ' ').split()]
                  for s, (_n, g) in gloss_of.items()}

    # TR phrase maps per corpus verse
    tr_kjv = defaultdict(dict)    # vid -> tr_pos -> (phrase, [kjv_pos])
    for r in db.execute(
            'SELECT a.corpus_verse_id AS vid, a.gnt_position AS pos, '
            'a.kjv_pos AS kp, k.kjv_word AS w FROM gnt_alignment a '
            'JOIN kjv_words k ON k.verse_id=a.corpus_verse_id '
            'AND k.kjv_pos=a.kjv_pos ORDER BY a.corpus_verse_id, '
            'a.gnt_position, a.kjv_pos'):
        e = tr_kjv[r['vid']].setdefault(r['pos'], ([], []))
        e[0].append(r['w'])
        e[1].append(r['kp'])
    tr_kjv = {v: {p: (' '.join(ws), ks) for p, (ws, ks) in d.items()}
              for v, d in tr_kjv.items()}
    tr_ylt = defaultdict(dict)    # gnt_verse_id -> pos -> (phrase, [ylt_pos])
    for r in db.execute(
            'SELECT gnt_verse_id AS gid, gnt_position AS pos, '
            'ylt_word AS w, ylt_word_pos AS yp FROM gnt_ylt_renderings '
            'ORDER BY gnt_verse_id, gnt_position, ylt_word_pos'):
        e = tr_ylt[r['gid']].setdefault(r['pos'], ([], []))
        e[0].append(r['w'])
        e[1].append(r['yp'])
    tr_ylt = {v: {p: (' '.join(ws), ks) for p, (ws, ks) in d.items()}
              for v, d in tr_ylt.items()}

    tr_words = {}
    for r in db.execute(
            'SELECT gv.corpus_verse_id AS vid, w.position AS pos, '
            'w.surface AS surf, w.strongs AS s FROM gnt_words w '
            'JOIN gnt_verses gv ON gv.gnt_verse_id=w.gnt_verse_id '
            'ORDER BY vid, pos'):
        tr_words.setdefault(r['vid'], []).append(
            {'pos': r['pos'], 'form': norm_form(r['surf']), 's': r['s']})
    tr_gid = {r['corpus_verse_id']: r['gnt_verse_id'] for r in db.execute(
        'SELECT corpus_verse_id, gnt_verse_id FROM gnt_verses')}
    kjv_toks = defaultdict(list)
    for r in db.execute(
            'SELECT verse_id AS vid, kjv_pos AS kp, kjv_word AS w '
            'FROM kjv_words WHERE verse_id IN '
            '(SELECT verse_id FROM verses WHERE book_id >= 40) '
            'ORDER BY vid, kp'):
        kjv_toks[r['vid']].append((r['kp'], r['w']))
    ylt_text = {r['verse_id']: r['text'] for r in db.execute(
        'SELECT verse_id, text FROM ylt_verses WHERE verse_id IN '
        '(SELECT verse_id FROM verses WHERE book_id >= 40)')}
    status = {(r['corpus_verse_id'], r['tradition']): r['status']
              for r in db.execute(
                  'SELECT corpus_verse_id, tradition, status '
                  'FROM gnt_variants')}

    def greek_score(bw, tw):
        if bw['s'] and tw['s'] and bw['s'] == tw['s']:
            return 2.0
        if bw['form'] == tw['form']:
            return 1.5
        return -1.0

    out_align = []   # (vid, kjv_pos, byz_pos)
    out_ylt = []     # (byz_gid, byz_pos, ylt_word, ylt_word_pos)
    disagree = []
    stats = Counter()
    same_tot = same_ok = 0
    sil_tot = sil_ok = 0
    specimens = {}

    byz_verses = db.execute(
        'SELECT gnt_verse_id, corpus_verse_id FROM gntb_verses '
        'ORDER BY corpus_verse_id').fetchall()
    for bv in byz_verses:
        vid, bgid = bv['corpus_verse_id'], bv['gnt_verse_id']
        bws = [{'pos': r['position'], 'form': norm_form(r['surface']),
                's': r['strongs']} for r in db.execute(
                    'SELECT position, surface, strongs FROM gntb_words '
                    'WHERE gnt_verse_id=? ORDER BY position', (bgid,))]
        tws = tr_words.get(vid, [])
        pairs = nw_pairs(bws, tws, greek_score)
        pair_of = dict(pairs)          # byz idx -> tr idx
        st = status.get((vid, 'byz'))
        gid = tr_gid.get(vid)
        # silver: occurrence-ordered strongs copy (unambiguous only)
        tr_by_s = defaultdict(list)
        for ti, tw in enumerate(tws):
            tr_by_s[tw['s']].append(ti)
        seen_s = defaultdict(int)
        silver = {}
        for bi, bw in enumerate(bws):
            seen_s[bw['s']] += 1
            lst = tr_by_s.get(bw['s'], [])
            if len(lst) == 1:
                silver[bi] = lst[0]
        used_kjv_pos = set()
        used_ylt_pos = set()
        byz_kjv_phrase = {}
        byz_ylt_phrase = {}
        for bi, ti in pairs:
            tpos = tws[ti]['pos']
            kp = tr_kjv.get(vid, {}).get(tpos)
            if kp:
                byz_kjv_phrase[bi] = kp[0]
                for k in kp[1]:
                    out_align.append((vid, k, bws[bi]['pos']))
                    used_kjv_pos.add(k)
            yp = tr_ylt.get(gid, {}).get(tpos) if gid else None
            if yp:
                byz_ylt_phrase[bi] = yp[0]
                for j, wtok in enumerate(yp[0].split()):
                    out_ylt.append((bgid, bws[bi]['pos'], wtok,
                                    yp[1][j] if j < len(yp[1]) else None))
                used_ylt_pos.update(yp[1])
        # residue passes
        unmatched = [bi for bi in range(len(bws)) if bi not in pair_of]
        if unmatched:
            ktoks = [(kp, w) for kp, w in kjv_toks.get(vid, [])
                     if kp not in used_kjv_pos]
            if ktoks:
                def res_score(bw, kt, _gt=gloss_toks):
                    toks = _gt.get(bw['s'], [])
                    return max([sim(kt[1], g) for g in toks] + [-1.0])
                rp = nw_pairs([bws[bi] for bi in unmatched], ktoks,
                              res_score)
                for ui, ki in rp:
                    bi = unmatched[ui]
                    byz_kjv_phrase.setdefault(bi, ktoks[ki][1])
                    out_align.append((vid, ktoks[ki][0], bws[bi]['pos']))
            ytoks_all = tokenize(ylt_text.get(vid, ''))
            ytoks = [(i + 1, w) for i, w in enumerate(ytoks_all)
                     if (i + 1) not in used_ylt_pos]
            if ytoks:
                def res_score_y(bw, yt, _gt=gloss_toks):
                    toks = _gt.get(bw['s'], [])
                    return max([sim(yt[1], g) for g in toks] + [-1.0])
                rp = nw_pairs([bws[bi] for bi in unmatched
                               if bi not in byz_ylt_phrase],
                              ytoks, res_score_y)
                base_un = [bi for bi in unmatched
                           if bi not in byz_ylt_phrase]
                for ui, yi in rp:
                    bi = base_un[ui]
                    byz_ylt_phrase.setdefault(bi, ytoks[yi][1])
                    out_ylt.append((bgid, bws[bi]['pos'], ytoks[yi][1],
                                    ytoks[yi][0]))
        # evaluation
        if st == 'same':
            stats['same_verses'] += 1
            if stats['same_verses'] % 15 == 0:   # sample every 15th
                for bi, bw in enumerate(bws):
                    same_tot += 1
                    ti = pair_of.get(bi)
                    if ti is not None and ti == bi:
                        tpos = tws[ti]['pos']
                        want = tr_kjv.get(vid, {}).get(tpos, ('',))[0]
                        if byz_kjv_phrase.get(bi, '') == want:
                            same_ok += 1
        elif st == 'variant':
            stats['variant_verses'] += 1
            for bi, ti in silver.items():
                sil_tot += 1
                tpos = tws[ti]['pos']
                want = tr_kjv.get(vid, {}).get(tpos, ('',))[0]
                if byz_kjv_phrase.get(bi, '') == want:
                    sil_ok += 1
                elif len(disagree) < 8:
                    bref = db.execute(
                        'SELECT book_id, chapter, verse FROM verses '
                        'WHERE verse_id=?', (vid,)).fetchone()
                    disagree.append(
                        (f"{bref['book_id']}/{bref['chapter']}:"
                         f"{bref['verse']}", bws[bi]['s'],
                         byz_kjv_phrase.get(bi, ''), want))
        if vid in (31251,):   # placeholder; specimens chosen below
            pass
        stats['byz_words'] += len(bws)
        stats['byz_words_kjv'] += len(byz_kjv_phrase)
        stats['byz_words_ylt'] += len(byz_ylt_phrase)
        if vid == db.execute('SELECT verse_id FROM verses WHERE '
                             'book_id=62 AND chapter=5 AND verse=7'
                             ).fetchone()[0]:
            specimens['1Jo5:7'] = (byz_kjv_phrase, byz_ylt_phrase, bws)

    print('silver disagreements (sample):')
    for d in disagree:
        print('  ', d)
    print('stats:', dict(stats))
    print(f'same-verse consistency (sampled): {same_ok}/{same_tot} '
          f'= {same_ok / max(same_tot, 1):.4f}')
    print(f'silver agreement (variant verses): {sil_ok}/{sil_tot} '
          f'= {sil_ok / max(sil_tot, 1):.4f}')
    kjv_p, ylt_p, bws = specimens.get('1Jo5:7', ({}, {}, []))
    print('1 John 5:7 Byzantine bridge:')
    for bi, bw in enumerate(bws):
        print(f"  pos {bw['pos']} {bw['s']}: KJV {kjv_p.get(bi)!r} "
              f"| YLT {ylt_p.get(bi)!r}")
    if WRITE:
        db.execute('DROP TABLE IF EXISTS gntb_alignment')
        db.execute('DROP TABLE IF EXISTS gntb_ylt_renderings')
        db.execute('CREATE TABLE gntb_alignment (corpus_verse_id INTEGER,'
                   ' kjv_pos INTEGER, gntb_position INTEGER)')
        db.execute('CREATE TABLE gntb_ylt_renderings ('
                   'gntb_verse_id INTEGER, gntb_position INTEGER, '
                   'ylt_word TEXT, ylt_word_pos INTEGER, label TEXT)')
        db.executemany('INSERT INTO gntb_alignment VALUES (?,?,?)',
                       out_align)
        db.executemany('INSERT INTO gntb_ylt_renderings VALUES (?,?,?,?,?)',
                       [(g, p, w, yp, 'ylt-bridge-byz') for
                        g, p, w, yp in out_ylt])
        db.commit()
        print(f'WROTE gntb_alignment {len(out_align)} rows, '
              f'gntb_ylt_renderings {len(out_ylt)} rows')


if __name__ == '__main__':
    main()
