#!/usr/bin/env python3
"""SBLGNT alignment bridge (VARIANT_BRIDGES_PLAN_2026-11-03, step 2).

Mirror of build_gntb_bridge.py for the SBL tradition. Per SBL verse:
(1) NW-align SBL Greek words to the TR words of the same verse with
the SBL scorer from the plan -- SBL carries no Strong's, so the
Byzantine Strong's scorer is NOT reused:
  - accent-stripped form equality ............ 2.0
  - lemma / gloss-token overlap .............. 1.0
    (lemma: the SBL word's stored normalized form, accent-stripped
    and movable-nu parentheses removed, equals the TR form; gloss:
    the SBL word's English gloss tokens share a token with the TR
    word's gloss tokens. Gloss tokens come only from public-domain
    in-DB sources: lxx_words glosses, keyed by Strong's for TR words
    and by accent-stripped Greek form for SBL words -- the form map
    is built from lxx_words surfaces, extended with TR form ->
    Strong's-gloss pairs for forms the LXX does not attest.)
(2) an aligned word inherits the TR word's KJV phrase (CrossWire
gnt_alignment) and computed-Young's phrase (gnt_ylt_renderings)
wholesale; (3) residue pass: unaligned SBL words are NW-aligned to
the verse's leftover English tokens with the gloss-token scorer;
still-unmatched words get no phrase (honest gap).
Verses where SBL is absent produce no rows; SBL-only verses (no
corpus reference, no TR counterpart) produce no rows either.

Outputs (with --write): gnts_alignment (KJV links, mirroring
gntb_alignment) and gnts_ylt_renderings (mirroring
gntb_ylt_renderings, label 'ylt-bridge-sbl'). TR and Byzantine
tables are never written. Without --write it only evaluates:
'same'-verse self-consistency over ALL SBL 'same' verses, silver
agreement on variant verses (silver = occurrence-unambiguous
accent-stripped-form copy, the SBL analogue of the Byzantine
Strong's silver), graded precision the OT-bridge way, and printed
specimens for the hand-gold verses.
"""
import difflib
import sqlite3
import sys
import unicodedata
from collections import Counter, defaultdict
from functools import lru_cache

DB = 'bible_v2.db'
if '--db' in sys.argv:
    DB = sys.argv[sys.argv.index('--db') + 1]
STRIP = ".,;:!?\"'()[]—-«»"
WRITE = '--write' in sys.argv


def norm_form(s):
    s = ''.join(c for c in unicodedata.normalize('NFD', s)
                if unicodedata.category(c) != 'Mn').lower()
    return s.replace('ς', 'σ').strip(',.;·:!?⸀⸂⸃[]()')


def norm_lemma(s):
    # Stored SBL 'lemma' is MorphGNT's normalized word (e.g.
    # 'ἐγέννησε(ν)'); strip accents and movable-nu parentheses.
    s = norm_form(s or '')
    return s.replace('(', '').replace(')', '')


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

    # Strong's -> gloss tokens (TR side), as in the Byzantine bridge.
    gloss_of = {}
    for r in db.execute(
            'SELECT strongs, gloss, COUNT(*) AS n FROM lxx_words '
            'WHERE strongs IS NOT NULL AND gloss IS NOT NULL '
            "AND gloss <> '' GROUP BY strongs, gloss"):
        if r['strongs'] not in gloss_of or r['n'] > gloss_of[r['strongs']][0]:
            gloss_of[r['strongs']] = (r['n'], r['gloss'])
    gloss_toks_s = {s: [norm_word(t) for t in g.replace(';', ' ').split()]
                    for s, (_n, g) in gloss_of.items()}

    # Greek form -> gloss tokens (SBL side): most frequent lxx_words
    # gloss per accent-stripped surface form.
    form_best = {}
    for r in db.execute(
            'SELECT surface, gloss, COUNT(*) AS n FROM lxx_words '
            'WHERE gloss IS NOT NULL AND gloss <> \'\' '
            'GROUP BY surface, gloss'):
        f = norm_form(r['surface'])
        if f not in form_best or r['n'] > form_best[f][0]:
            form_best[f] = (r['n'], r['gloss'])
    form_gloss = {f: [norm_word(t) for t in g.replace(';', ' ').split()]
                  for f, (_n, g) in form_best.items()}

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
    # Extend the form->gloss map with TR forms the LXX never attests
    # (their Strong's gloss, corpus-wide, not verse-local).
    for ws in tr_words.values():
        for tw in ws:
            if tw['form'] not in form_gloss and tw['s'] in gloss_toks_s:
                form_gloss[tw['form']] = gloss_toks_s[tw['s']]
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
    ref_of = {r['verse_id']: (r['book_id'], r['chapter'], r['verse'])
              for r in db.execute(
                  'SELECT verse_id, book_id, chapter, verse FROM verses')}
    GOLD = {(62, 5, 7): '1Jo5:7', (62, 5, 8): '1Jo5:8',
            (41, 16, 19): 'Mk16:19', (41, 16, 20): 'Mk16:20',
            (66, 22, 19): 'Rev22:19'}

    def tr_gloss(tw):
        return gloss_toks_s.get(tw['s']) or form_gloss.get(tw['form'], [])

    def greek_score(sw, tw):
        if sw['form'] == tw['form']:
            return 2.0
        if sw['lemma'] and sw['lemma'] == tw['form']:
            return 1.0
        sg, tg = sw['gtoks'], tr_gloss(tw)
        if sg and tg and set(sg) & set(tg):
            return 1.0
        return -1.0

    out_align = []   # (vid, kjv_pos, sbl_pos)
    out_ylt = []     # (sbl_gid, sbl_pos, ylt_word, ylt_word_pos)
    disagree = []
    stats = Counter()
    same_tot = same_ok = 0
    sil_tot = sil_ok = 0
    sil_graded = 0.0
    specimens = {}

    sbl_verses = db.execute(
        'SELECT gnt_verse_id, corpus_verse_id FROM gnts_verses '
        'ORDER BY corpus_verse_id').fetchall()
    for sv in sbl_verses:
        vid, sgid = sv['corpus_verse_id'], sv['gnt_verse_id']
        if vid is None:
            stats['sbl_only_verses_skipped'] += 1
            continue
        sws = [{'pos': r['position'], 'form': norm_form(r['surface']),
                'lemma': norm_lemma(r['lemma']),
                'gtoks': form_gloss.get(norm_form(r['surface']), [])}
               for r in db.execute(
                    'SELECT position, surface, lemma FROM gnts_words '
                    'WHERE gnt_verse_id=? ORDER BY position', (sgid,))]
        tws = tr_words.get(vid, [])
        pairs = nw_pairs(sws, tws, greek_score)
        pair_of = dict(pairs)          # sbl idx -> tr idx
        st = status.get((vid, 'sbl'))
        gid = tr_gid.get(vid)
        # silver: occurrence-unambiguous form copy (a form occurring
        # exactly once on each side maps SBL word -> that TR word)
        tr_by_form = defaultdict(list)
        for ti, tw in enumerate(tws):
            tr_by_form[tw['form']].append(ti)
        sbl_form_n = Counter(sw['form'] for sw in sws)
        silver = {}
        for si, sw in enumerate(sws):
            lst = tr_by_form.get(sw['form'], [])
            if len(lst) == 1 and sbl_form_n[sw['form']] == 1:
                silver[si] = lst[0]
        used_kjv_pos = set()
        used_ylt_pos = set()
        sbl_kjv_phrase = {}
        sbl_ylt_phrase = {}
        for si, ti in pairs:
            tpos = tws[ti]['pos']
            kp = tr_kjv.get(vid, {}).get(tpos)
            if kp:
                sbl_kjv_phrase[si] = kp[0]
                for k in kp[1]:
                    out_align.append((vid, k, sws[si]['pos']))
                    used_kjv_pos.add(k)
            yp = tr_ylt.get(gid, {}).get(tpos) if gid else None
            if yp:
                sbl_ylt_phrase[si] = yp[0]
                for j, wtok in enumerate(yp[0].split()):
                    out_ylt.append((sgid, sws[si]['pos'], wtok,
                                    yp[1][j] if j < len(yp[1]) else None))
                used_ylt_pos.update(yp[1])
        # residue passes
        unmatched = [si for si in range(len(sws)) if si not in pair_of]
        if unmatched:
            ktoks = [(kp, w) for kp, w in kjv_toks.get(vid, [])
                     if kp not in used_kjv_pos]
            if ktoks:
                def res_score(sw, kt):
                    return max([sim(kt[1], g) for g in sw['gtoks']]
                               + [-1.0])
                rp = nw_pairs([sws[si] for si in unmatched], ktoks,
                              res_score)
                for ui, ki in rp:
                    si = unmatched[ui]
                    sbl_kjv_phrase.setdefault(si, ktoks[ki][1])
                    out_align.append((vid, ktoks[ki][0], sws[si]['pos']))
            ytoks_all = tokenize(ylt_text.get(vid, ''))
            ytoks = [(i + 1, w) for i, w in enumerate(ytoks_all)
                     if (i + 1) not in used_ylt_pos]
            if ytoks:
                def res_score_y(sw, yt):
                    return max([sim(yt[1], g) for g in sw['gtoks']]
                               + [-1.0])
                base_un = [si for si in unmatched
                           if si not in sbl_ylt_phrase]
                rp = nw_pairs([sws[si] for si in base_un],
                              ytoks, res_score_y)
                for ui, yi in rp:
                    si = base_un[ui]
                    sbl_ylt_phrase.setdefault(si, ytoks[yi][1])
                    out_ylt.append((sgid, sws[si]['pos'], ytoks[yi][1],
                                    ytoks[yi][0]))
        # evaluation
        if st == 'same':
            stats['same_verses'] += 1
            for si, sw in enumerate(sws):
                same_tot += 1
                ti = pair_of.get(si)
                if ti is not None and ti == si:
                    tpos = tws[ti]['pos']
                    want = tr_kjv.get(vid, {}).get(tpos, ('',))[0]
                    if sbl_kjv_phrase.get(si, '') == want:
                        same_ok += 1
        elif st == 'variant':
            stats['variant_verses'] += 1
            for si, ti in silver.items():
                sil_tot += 1
                tpos = tws[ti]['pos']
                want = tr_kjv.get(vid, {}).get(tpos, ('',))[0]
                got = sbl_kjv_phrase.get(si, '')
                if got == want:
                    sil_ok += 1
                if got and want:
                    sil_graded += max(
                        sim(g, w) for g in got.split()
                        for w in want.split())
                elif len(disagree) < 10:
                    bref = ref_of.get(vid)
                    disagree.append(
                        (f"{bref[0]}/{bref[1]}:{bref[2]}",
                         sws[si]['form'], got, want))
        stats['sbl_words'] += len(sws)
        stats['sbl_words_kjv'] += len(sbl_kjv_phrase)
        stats['sbl_words_ylt'] += len(sbl_ylt_phrase)
        key = GOLD.get(ref_of.get(vid, ()))
        if key:
            specimens[key] = (dict(sbl_kjv_phrase), dict(sbl_ylt_phrase),
                              [dict(sw) for sw in sws], vid)

    print('silver disagreements (sample):')
    for d in disagree:
        print('  ', d)
    print('stats:', dict(stats))
    print(f'same-verse consistency (ALL same verses): {same_ok}/{same_tot} '
          f'= {same_ok / max(same_tot, 1):.4f}')
    print(f'silver agreement (variant verses): {sil_ok}/{sil_tot} '
          f'= {sil_ok / max(sil_tot, 1):.4f}')
    print(f'silver graded score (exact2/stem1.5/fuzzy1, mean over '
          f'silver words with both phrases): {sil_graded:.1f} / '
          f'{2 * sil_tot} max')
    for key in ('1Jo5:7', '1Jo5:8', 'Mk16:19', 'Mk16:20', 'Rev22:19'):
        kjv_p, ylt_p, sws, vid = specimens.get(key, ({}, {}, [], None))
        print(f'{key} SBL bridge (corpus verse {vid}):')
        for si, sw in enumerate(sws):
            print(f"  pos {sw['pos']} {sw['form']}: "
                  f"KJV {kjv_p.get(si)!r} | YLT {ylt_p.get(si)!r}")
    if WRITE:
        db.execute('DROP TABLE IF EXISTS gnts_alignment')
        db.execute('DROP TABLE IF EXISTS gnts_ylt_renderings')
        db.execute('CREATE TABLE gnts_alignment (corpus_verse_id INTEGER,'
                   ' kjv_pos INTEGER, gnts_position INTEGER)')
        db.execute('CREATE TABLE gnts_ylt_renderings ('
                   'gnts_verse_id INTEGER, gnts_position INTEGER, '
                   'ylt_word TEXT, ylt_word_pos INTEGER, label TEXT)')
        db.executemany('INSERT INTO gnts_alignment VALUES (?,?,?)',
                       out_align)
        db.executemany('INSERT INTO gnts_ylt_renderings VALUES (?,?,?,?,?)',
                       [(g, p, w, yp, 'ylt-bridge-sbl') for
                        g, p, w, yp in out_ylt])
        db.commit()
        print(f'WROTE gnts_alignment {len(out_align)} rows, '
              f'gnts_ylt_renderings {len(out_ylt)} rows')


if __name__ == '__main__':
    main()
