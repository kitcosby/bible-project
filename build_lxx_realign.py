#!/usr/bin/env python3
"""Content-based realignment of the LXX crosswalk's divergent books
(LXX-REALIGN, 2026-11-21).

`build_lxx.py` built `lxx_crosswalk` by NUMBERING only (basis
'numbering-v1'): 24,273 rows = 21,468 same / 1,554 mt_only / 1,251
lxx_only. The orphans concentrate in the structurally divergent books
-- Psalms (787 mt_only / 792 lxx_only), Jeremiah (245/177), Proverbs
(162/138) -- where the Greek tradition merges/splits psalms, displaces
whole blocks (Prov MT 25-29 stands at LXX 32-36), and reorders the
oracles (Jer). The LXX-LOAD ledger entry named content-based
realignment of these books as the deferred next work; this script is
that work.

Method (content evidence ONLY; no numbering information is used to
score a pair):
  * Per-verse token sets. MT side: head tokens of the Hebrew
    glosses of each Hebrew word's Strong's number(s) -- the MT
    verse's Hebrew lemmas, as specified. The exact recipe differs
    by book because the gate adjudicated two configurations:
    Psalms uses 'strongs_he' + 'bdb' gloss heads (split at ';')
    and NO KJV tokens; Jeremiah/Proverbs use 'strongs_he' gloss
    heads only (split at ';'/',') PLUS the verse's `kjv_words`
    tokens. Why: in titled psalms the corpus's kjv_words follow
    KJV numbering -- title unnumbered -- while `words` follows
    Hebrew numbering -- title = verse 1 -- so each row's KJV
    tokens describe the NEXT Hebrew verse and systematically
    pulled Psalms pairings off by one (trial 6: MT 18:22 paired
    to the Greek verse carrying MT 18:23's text; Hebrew-only
    tokens fixed the whole psalm to the correct diagonal, trial
    7). In Jeremiah/Proverbs the numberings agree, and there the
    bdb-inclusive recipe measurably degraded the match (trial 8
    lost gate-verified pairs and re-proposed banned ones), so
    those books keep the trial-6 recipe under which their pairing
    lists were hand-adjudicated. LXX side: the `gloss` tokens of
    the verse's `lxx_words` plus the head segment of `bol_gloss`.
    Tokens are lowercased, stopword-filtered, and lightly stemmed.
  * Evidence score = IDF-weighted overlap coefficient: sum of IDF
    weights of shared tokens / min(MT weight, LXX weight), with IDF
    computed over the book's orphan verses on both sides.
  * Psalms / Proverbs preserve verse order (merges, splits, and
    re-chaptering are monotonic), so their orphan sequences are
    aligned with a banded Needleman-Wunsch DP (pair gain = score -
    PAIR_COST, gap = GAP_PENALTY).
  * Jeremiah's oracle blocks are REORDERED, so Jeremiah uses greedy
    mutual descending-score 1-to-1 matching instead of a monotonic
    alignment.
  * Proper-noun fuzzy matching: token pairs of length >= 5 that
    share a >= 5-character substring after stripping a leading 'h'
    (Hezekiah ~ Ezekias, Judah ~ Ioudaia class) count as shared at
    0.7 weight, each token used at most once.
  * Minimum-evidence threshold (never force a pairing): a pair is
    written only if effective shared >= 2 and score >= 0.16, or
    effective shared >= 3 and score >= 0.12, or effective shared
    >= 4 and score >= 0.10; AND the pair passes a mutual-best
    filter (for monotonic books: best for both sides within a
    +/-4-verse window of the alignment path). Everything else
    stays mt_only / lxx_only as the documented remainder (e.g.
    Ps 151, which has no MT counterpart, must remain unpaired).
    The first trial run's spot-check gate caught an off-by-one DP
    slip in Ps 18 and a false Ps 151 pairing under the original
    looser threshold; both filters above are the response, and
    the gate was re-run after tightening.
  * Jeremiah is stricter (its formulaic prophetic vocabulary
    produced false pairings at the general threshold in trial 1:
    e.g. Jer 2:1 matched a 'word of the LORD' formula verse in
    LXX 45): score >= 0.22, effective shared >= 3.5, word-count
    ratio (Hebrew words vs Greek words) >= 0.35, and mutual-best
    at 90% of each side's best candidate score. Every Jeremiah
    pairing that survives was additionally hand-read against the
    verse texts in the gate dossier before the live application.
  * Adjacent-verse guard (all books): a pair is rejected if any
    immediately adjacent verse on either side -- in the FULL
    verse sequence of the book, pool member or not -- scores
    strictly higher against the other side.
  * Gate adjudication (2026-11-21, U-9 pattern): every Jeremiah
    pairing and samples of Psalms/Proverbs pairings were hand-read
    against the Hebrew pointed text and the Greek text before the
    live application. Gate lessons, recorded honestly:
    (1) adjudication must read the HEBREW text, not the KJV column
    -- in titled psalms the two numberings diverge by one verse,
    so KJV-based reading both falsely condemned correct pairings
    (Ps 18:19, 18:37) and falsely acquitted wrong ones (the
    18:22-24 stretch, where the scorer's own KJV contamination
    was the cause; see the token-set note above);
    (2) nine proposed pairs were nonetheless genuinely false
    (formulaic-vocabulary captures and one parallel-verse
    attribution in Jer, one off-by-one in Prov; two more false
    re-pairings of the same Greek verses surfaced and were banned
    in trial 5) and are banned by name in
    `lxx_realign_exclusions.json`, each with its text-read
    reason -- the anomaly_resolutions.json precedent of a curated
    file consumed by the builder. Trial 5 also showed the ban
    working positively: freed from the wrong attribution, the
    parallel 'young men shall fall' verses resolved correctly to
    BOTH their blocks (MT 49:26 -> LXX 30:32 and MT 50:30 ->
    LXX 27:30, verified against the Hebrew).

Writes: INSERT-only into `lxx_crosswalk`, relation 'same', basis
'content-v1'. Existing 'numbering-v1' rows are never modified or
deleted (the mt_only/lxx_only rows stay as the numbering record; the
content-v1 rows add the content pairing beside them). Idempotent:
refuses to run on a DB that already carries content-v1 rows.

Usage: python3 build_lxx_realign.py [--db bible_v2.db] [--dry-run]
       [--dossier PATH]   (write a TSV spot-check dossier of all
                           proposed pairings, with verse texts)
Public-domain / permissive sources only (KJV, Strong's, Rahlfs LXX
via CenterBLC) -- no copyrighted lexicons.
"""
import argparse
import collections
import json
import math
import os
import re
import sqlite3
import sys


def load_exclusions():
    """(osis, mt_verse_id, lxx_verse_id) pairs banned by the
    hand-adjudication gate; see lxx_realign_exclusions.json."""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        'lxx_realign_exclusions.json')
    if not os.path.exists(path):
        return set()
    with open(path, encoding='utf-8') as f:
        data = json.load(f)
    return {(e['osis'], e['mt_ref'], e['lxx_ref'])
            for e in data.get('exclusions', [])}

BOOKS = {'Ps': 19, 'Jer': 24, 'Prov': 20}
MONOTONIC = {'Ps', 'Prov'}   # Jer is reordered -> greedy matching
PAIR_COST = 0.12
GAP_PENALTY = -0.07
BAND = 120

STOP = set(
    "a an the of to in and or for with by from as at on is be he she it "
    "they thou thee thy thine his her its our your their my me him them "
    "us you i we not no nor but if when who whom which that this these "
    "those unto upon over under before after between against into out "
    "up down shall will hath hast art were was are am do doth did have "
    "has had".split())


def stem(w):
    for suf in ("est", "eth", "ing", "ed", "es", "s"):
        if len(w) > len(suf) + 2 and w.endswith(suf):
            return w[:-len(suf)]
    return w


def toks(s):
    out = set()
    for w in re.findall(r"[a-z]+", (s or "").lower()):
        if len(w) > 1 and w not in STOP:
            out.add(stem(w))
    return out


def accepted(score, shared):
    return ((shared >= 2 and score >= 0.16)
            or (shared >= 3 and score >= 0.12)
            or (shared >= 4 and score >= 0.10))


def _fuzzy_key(w):
    return w[1:] if w.startswith('h') and len(w) > 4 else w


def shared_weight(idf, a, b):
    """(weighted shared sum, effective shared count, shared token set).

    Exact token matches count at full IDF weight; fuzzy proper-noun
    matches (see module docstring) at 0.7 weight."""
    inter = a & b
    w = sum(idf[x] for x in inter)
    eff = float(len(inter))
    names = set(inter)
    rest_a = [x for x in a - inter if len(_fuzzy_key(x)) >= 5]
    rest_b = [y for y in b - inter if len(_fuzzy_key(y)) >= 5]
    used = set()
    for x in sorted(rest_a):
        kx = _fuzzy_key(x)
        for y in sorted(rest_b):
            if y in used:
                continue
            ky = _fuzzy_key(y)
            if kx in ky or ky in kx:
                used.add(y)
                w += 0.7 * min(idf[x], idf[y])
                eff += 0.7
                names.add(f"{x}~{y}")
                break
    return w, eff, names


class BookData:
    def __init__(self, db, osis, exclusions=()):
        self.osis = osis
        self._excl_refs = {(m, l) for (o, m, l) in exclusions if o == osis}
        self.she = {}
        if osis == 'Ps':
            gloss_sql = ("SELECT strongs, gloss FROM glosses "
                         "WHERE source IN ('strongs_he','bdb')")
            split_pat = r";"
        else:
            gloss_sql = ("SELECT strongs, gloss FROM glosses "
                         "WHERE source='strongs_he'")
            split_pat = r"[;,]"
        for strongs, gloss_text in db.execute(gloss_sql):
            self.she.setdefault(strongs, set()).update(
                toks(re.split(split_pat, gloss_text)[0]))
        self.mt = self._orphans(db, 'mt_only')
        self.lx = self._orphans(db, 'lxx_only')
        self.banned = set()
        for i, (ch, v, _) in enumerate(self.mt):
            for j, (lch, lv, _) in enumerate(self.lx):
                if (f"{ch}:{v}", f"{lch}:{lv}") in self._excl_refs:
                    self.banned.add((i, j))
        self.mt_tok = [self._mt_tokens(db, v) for _, _, v in self.mt]
        self.lx_tok = [self._lx_tokens(db, v) for _, _, v in self.lx]
        self.mt_wc = [db.execute(
            "SELECT COUNT(*) FROM words WHERE verse_id=?",
            (v,)).fetchone()[0] for _, _, v in self.mt]
        self.lx_wc = [db.execute(
            "SELECT COUNT(*) FROM lxx_words WHERE verse_id=?",
            (v,)).fetchone()[0] for _, _, v in self.lx]
        self._cache = {}
        df = collections.Counter()
        for t in self.mt_tok + self.lx_tok:
            for w in t:
                df[w] += 1
        n = len(self.mt_tok) + len(self.lx_tok)
        self._idf_max = math.log(n) + 0.5
        self.idf = collections.defaultdict(
            lambda: self._idf_max,
            {w: math.log(n / (1 + c)) + 0.5 for w, c in df.items()})
        # Full verse sequences of the book (adjacent-verse guard).
        mt_id = BOOKS[osis]
        self.mt_seq = [v for (v,) in db.execute(
            "SELECT verse_id FROM verses WHERE book_id=? "
            "ORDER BY chapter, verse", (mt_id,))]
        self.lx_seq = [v for (v,) in db.execute(
            "SELECT verse_id FROM lxx_verses WHERE osis=? "
            "ORDER BY chapter, verse", (osis,))]
        self.mt_pos = {v: k for k, v in enumerate(self.mt_seq)}
        self.lx_pos = {v: k for k, v in enumerate(self.lx_seq)}
        self._tok_by_vid = {}
        for (_, _, v), t in zip(self.mt, self.mt_tok):
            self._tok_by_vid[('m', v)] = t
        for (_, _, v), t in zip(self.lx, self.lx_tok):
            self._tok_by_vid[('l', v)] = t
        self._db = db

    def _tokens_of(self, side, vid):
        key = (side, vid)
        t = self._tok_by_vid.get(key)
        if t is None:
            t = (self._mt_tokens(self._db, vid) if side == 'm'
                 else self._lx_tokens(self._db, vid))
            self._tok_by_vid[key] = t
        return t

    def score_vids(self, mvid, lvid):
        a = self._tokens_of('m', mvid)
        b = self._tokens_of('l', lvid)
        if not a or not b:
            return 0.0
        w, eff, _ = shared_weight(self.idf, a, b)
        if eff == 0:
            return 0.0
        denom = min(sum(self.idf[x] for x in a),
                    sum(self.idf[x] for x in b))
        return w / denom if denom > 0 else 0.0

    def adjacent_guard(self, i, j):
        """False if an adjacent verse on either side (full book
        sequence) scores strictly higher against the other side."""
        mvid = self.mt[i][2]
        lvid = self.lx[j][2]
        s = self.score_vids(mvid, lvid)
        lp = self.lx_pos[lvid]
        for k in (lp - 1, lp + 1):
            if 0 <= k < len(self.lx_seq):
                if self.score_vids(mvid, self.lx_seq[k]) > s:
                    return False
        mp = self.mt_pos[mvid]
        for k in (mp - 1, mp + 1):
            if 0 <= k < len(self.mt_seq):
                if self.score_vids(self.mt_seq[k], lvid) > s:
                    return False
        return True

    def _orphans(self, db, relation):
        col = 'mt_verse_id' if relation == 'mt_only' else 'lxx_verse_id'
        tbl = 'verses' if relation == 'mt_only' else 'lxx_verses'
        out = []
        for (vid,) in db.execute(
                f"SELECT {col} FROM lxx_crosswalk WHERE osis=? "
                f"AND relation=? AND basis='numbering-v1'",
                (self.osis, relation)):
            ch, v = db.execute(
                f"SELECT chapter, verse FROM {tbl} WHERE verse_id=?",
                (vid,)).fetchone()
            out.append((ch, v, vid))
        return sorted(out)

    def _mt_tokens(self, db, vid):
        t = set()
        for (s,) in db.execute(
                "SELECT strongs FROM words WHERE verse_id=?", (vid,)):
            if s:
                for c in s.split(','):
                    t.update(self.she.get(c.strip(), set()))
        if self.osis != 'Ps':
            # KJV tokens sharpen Jer/Prov (numbering agrees there);
            # excluded for Psalms -- see module docstring.
            for (w,) in db.execute(
                    "SELECT kjv_word FROM kjv_words WHERE verse_id=?",
                    (vid,)):
                t.update(toks(w))
        return t

    def _lx_tokens(self, db, vid):
        t = set()
        for g, b in db.execute(
                "SELECT gloss, bol_gloss FROM lxx_words "
                "WHERE verse_id=?", (vid,)):
            t.update(toks(g))
            if b:
                t.update(toks(re.split(r";", b)[0]))
        return t

    def score(self, i, j):
        """Returns (score, effective_shared, shared_token_names)."""
        hit = self._cache.get((i, j))
        if hit is not None:
            return hit
        out = self._score(i, j)
        self._cache[(i, j)] = out
        return out

    def _score(self, i, j):
        a, b = self.mt_tok[i], self.lx_tok[j]
        if not a or not b:
            return 0.0, 0.0, set()
        w, eff, names = shared_weight(self.idf, a, b)
        if eff == 0:
            return 0.0, 0.0, set()
        denom = min(sum(self.idf[x] for x in a),
                    sum(self.idf[x] for x in b))
        return (w / denom if denom > 0 else 0.0), eff, names

    def mutual_best_window(self, i, j, half=4):
        """True if (i,j) is the best-scoring pair for both sides
        within +/- half verses of the candidate in sequence order."""
        s, _, _ = self.score(i, j)
        for jj in range(max(0, j - half), min(len(self.lx), j + half + 1)):
            if jj != j and self.score(i, jj)[0] > s:
                return False
        for ii in range(max(0, i - half), min(len(self.mt), i + half + 1)):
            if ii != i and self.score(ii, j)[0] > s:
                return False
        return True

    def mutual_best_global(self, i, j, frac=0.8):
        s, _, _ = self.score(i, j)
        best_i = max(self.score(i, jj)[0] for jj in range(len(self.lx)))
        best_j = max(self.score(ii, j)[0] for ii in range(len(self.mt)))
        return s >= frac * best_i and s >= frac * best_j


def align_monotonic(bd):
    """Banded Needleman-Wunsch over the orphan sequences."""
    n, m = len(bd.mt), len(bd.lx)
    NEG = float('-inf')
    # dp rows kept in full for traceback simplicity (n,m <= ~800)
    dp = [[NEG] * (m + 1) for _ in range(n + 1)]
    bt = [[None] * (m + 1) for _ in range(n + 1)]
    dp[0][0] = 0.0
    for i in range(n + 1):
        for j in range(m + 1):
            if abs(i - j) > BAND and not (i == 0 and j == 0):
                continue
            cur = dp[i][j]
            if cur == NEG:
                continue
            if i < n and j < m and abs((i + 1) - (j + 1)) <= BAND:
                s, _, _ = bd.score(i, j)
                if s > 0 and (i, j) not in bd.banned:
                    val = cur + s - PAIR_COST
                    if val > dp[i + 1][j + 1]:
                        dp[i + 1][j + 1] = val
                        bt[i + 1][j + 1] = ('P', i, j)
            if i < n and abs((i + 1) - j) <= BAND:
                val = cur + GAP_PENALTY
                if val > dp[i + 1][j]:
                    dp[i + 1][j] = val
                    bt[i + 1][j] = ('M', i, j)
            if j < m and abs(i - (j + 1)) <= BAND:
                val = cur + GAP_PENALTY
                if val > dp[i][j + 1]:
                    dp[i][j + 1] = val
                    bt[i][j + 1] = ('L', i, j)
    pairs = []
    i, j = n, m
    while (i, j) != (0, 0):
        step = bt[i][j]
        if step is None:
            break
        kind, pi, pj = step
        if kind == 'P':
            pairs.append((pi, pj))
        i, j = pi, pj
    return sorted(pairs)


def align_greedy(bd):
    """Descending-score 1-to-1 matching (reordered books)."""
    cand = []
    for i in range(len(bd.mt)):
        for j in range(len(bd.lx)):
            if (i, j) in bd.banned:
                continue
            s, eff, _ = bd.score(i, j)
            if s > 0 and accepted(s, eff):
                cand.append((s, i, j))
    cand.sort(reverse=True)
    used_m, used_l, pairs = set(), set(), []
    for s, i, j in cand:
        if i not in used_m and j not in used_l:
            used_m.add(i)
            used_l.add(j)
            pairs.append((i, j))
    return sorted(pairs)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--db', default='bible_v2.db')
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--dossier', default=None)
    args = ap.parse_args()

    db = sqlite3.connect(args.db)
    existing = db.execute(
        "SELECT COUNT(*) FROM lxx_crosswalk WHERE basis='content-v1'"
    ).fetchone()[0]
    if existing:
        print(f"ABORT: {existing} content-v1 rows already present "
              f"(idempotence guard)", file=sys.stderr)
        return 1

    dossier = None
    if args.dossier:
        dossier = open(args.dossier, 'w', encoding='utf-8')
        dossier.write("osis\tmt_ref\tlxx_ref\tscore\tshared_tokens\t"
                      "mt_hebrew\tmt_kjv\tlxx_text\n")

    exclusions = load_exclusions()
    total = 0
    for osis in ('Ps', 'Jer', 'Prov'):
        bd = BookData(db, osis, exclusions)
        raw = (align_monotonic(bd) if osis in MONOTONIC
               else align_greedy(bd))
        kept = []
        for i, j in raw:
            if (i, j) in bd.banned:
                continue
            s, eff, inter = bd.score(i, j)
            if not accepted(s, eff):
                continue
            if not bd.adjacent_guard(i, j):
                continue
            if osis in MONOTONIC:
                if not bd.mutual_best_window(i, j):
                    continue
            else:
                # Jeremiah's stricter gate (see docstring).
                if s < 0.22 or eff < 3.5:
                    continue
                wc = min(bd.mt_wc[i], bd.lx_wc[j]) / max(
                    bd.mt_wc[i], bd.lx_wc[j])
                if wc < 0.35:
                    continue
                if not bd.mutual_best_global(i, j, frac=0.9):
                    continue
            kept.append((i, j, s, inter))
        print(f"{osis}: mt_only={len(bd.mt)} lxx_only={len(bd.lx)} "
              f"aligned_path={len(raw)} accepted={len(kept)}")
        for i, j, s, inter in kept:
            mch, mv, mvid = bd.mt[i]
            lch, lv, lvid = bd.lx[j]
            if dossier:
                heb = ' '.join(r[0] for r in db.execute(
                    "SELECT pointed FROM words WHERE verse_id=? "
                    "ORDER BY word_pos", (mvid,)))
                kjv = ' '.join(r[0] for r in db.execute(
                    "SELECT kjv_word FROM kjv_words WHERE verse_id=? "
                    "ORDER BY kjv_pos", (mvid,)))
                ltext = db.execute(
                    "SELECT text FROM lxx_verses WHERE verse_id=?",
                    (lvid,)).fetchone()[0]
                dossier.write(
                    f"{osis}\t{mch}:{mv}\t{lch}:{lv}\t{s:.3f}\t"
                    f"{','.join(sorted(inter))}\t{heb}\t{kjv}\t{ltext}\n")
            if not args.dry_run:
                db.execute(
                    "INSERT INTO lxx_crosswalk VALUES (?,?,?,'same',"
                    "'content-v1')", (mvid, lvid, osis))
            total += 1
    if dossier:
        dossier.close()
    if not args.dry_run:
        db.commit()
    print(f"total content-v1 pairings: {total}"
          f"{' (dry run, not written)' if args.dry_run else ''}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
