#!/usr/bin/env python3
"""LXX crosswalk realignment, round 2 (LXX-REALIGN-R2, 2026-11-22).

Round 1 (`build_lxx_realign.py`, basis 'content-v1') paired 551 of the
numbering-v1 orphans in Psalms/Jeremiah/Proverbs and documented the
residual: Ps 381 mt_only / 386 lxx_only, Jer 206/138, Prov 56/32 verses
staying unpaired. This script is the second content pass over exactly
that residual.

Evidence function: IMPORTED VERBATIM from build_lxx_realign.py (same
module: toks/stem/shared_weight/accepted/BookData, same per-book gloss
recipes, same IDF over the book's full orphan pool), so every score
here is directly comparable to the round-1 scores. Nothing about the
scorer changes; only candidate generation and adjudication differ.

Candidate classes:
  * residual proposals -- mutual-best pairs INSIDE the residual pool
    (numbering-v1 orphans minus content-v1 paired ids) passing a
    LOWERED proposal gate (score >= 0.08 and effective shared >= 2).
    The lowered gate only GENERATES proposals; it never accepts.
    Every proposal is hand-read against the Hebrew pointed text and
    the Greek text (the gate); only text-verified pairs are applied,
    and every rejected proposal is recorded in
    `lxx_realign_exclusions.json` with its text-read reason.
  * consumed-counterpart candidates -- a residual MT orphan whose
    best-scoring LXX verse in the whole book is already consumed by a
    numbering-v1 'same' row (or a content-v1 row), scoring >= 0.16 and
    beating its best residual candidate by > 0.03. These are REPORTED
    ONLY (see --consumed PATH): numbering-v1 rows are never modified,
    and no content-v2 row may point at a consumed verse (the apply
    verification requires both ids to be residual orphans).

Writes: INSERT-only into `lxx_crosswalk`, relation 'same', basis
'content-v2', driven by an explicit hand-adjudication gate file
(--gate: {"accepted": [{"osis","mt_ref","lxx_ref"}, ...]}). Every
accepted pair must be a generated proposal, must pass a mechanical
re-check against the evidence function (score > 0), must not be
banned, and both ids must be residual orphans of the same book.
Idempotent: refuses to run on a DB that already carries content-v2
rows.

Usage:
  python3 build_lxx_realign_r2.py --db DB --propose \
      --dossier proposals.tsv --consumed consumed.tsv
  python3 build_lxx_realign_r2.py --db DB --gate gate.json [--dry-run]

Public-domain / permissive sources only (KJV, Strong's, Rahlfs LXX
via CenterBLC) -- no copyrighted lexicons.
"""
import argparse
import json
import os
import re
import sqlite3
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_lxx_realign as R1  # evidence function, verbatim

PROPOSE_MIN_SCORE = 0.08
PROPOSE_MIN_EFF = 2.0
CONSUMED_MIN_SCORE = 0.16
CONSUMED_MARGIN = 0.03


def residual_pools(db, bd, osis):
    """(residual mt index list, residual lx index list) into bd's
    orphan sequences: numbering-v1 orphans not paired by content-v1."""
    paired_mt = {r[0] for r in db.execute(
        "SELECT mt_verse_id FROM lxx_crosswalk WHERE osis=? "
        "AND basis='content-v1'", (osis,))}
    paired_lx = {r[0] for r in db.execute(
        "SELECT lxx_verse_id FROM lxx_crosswalk WHERE osis=? "
        "AND basis='content-v1'", (osis,))}
    res_mt = [i for i, (_, _, v) in enumerate(bd.mt) if v not in paired_mt]
    res_lx = [j for j, (_, _, v) in enumerate(bd.lx) if v not in paired_lx]
    return res_mt, res_lx


def propose_pairs(bd, res_mt, res_lx):
    """Mutual-best pairs inside the residual pool at the lowered
    proposal gate. Returns [(i, j, score, eff, shared_names)]."""
    best_for_mt = {}
    best_for_lx = {}
    for i in res_mt:
        for j in res_lx:
            if (i, j) in bd.banned:
                continue
            s, eff, _ = bd.score(i, j)
            if s <= 0:
                continue
            if s > best_for_mt.get(i, (0, None))[0]:
                best_for_mt[i] = (s, j)
            if s > best_for_lx.get(j, (0, None))[0]:
                best_for_lx[j] = (s, i)
    out = []
    for i, (s, j) in best_for_mt.items():
        if j is None or best_for_lx.get(j, (0, None))[1] != i:
            continue
        sc, eff, names = bd.score(i, j)
        if sc >= PROPOSE_MIN_SCORE and eff >= PROPOSE_MIN_EFF:
            out.append((i, j, sc, eff, names))
    return sorted(out)


def bulk_fill_tokens(db, bd, osis):
    """Pre-fill bd's per-verse token cache for EVERY verse of the book
    (same token recipes as BookData._mt_tokens/_lx_tokens) so the
    consumed-counterpart scan over the full book is tractable."""
    mt_book = R1.BOOKS[osis]
    vids = [v for (v,) in db.execute(
        "SELECT verse_id FROM verses WHERE book_id=?", (mt_book,))]
    tok = {v: set() for v in vids}
    marks = ",".join("?" * len(vids))
    for vid, s in db.execute(
            f"SELECT verse_id, strongs FROM words "
            f"WHERE verse_id IN ({marks})", vids):
        if s:
            for c in s.split(","):
                tok[vid].update(bd.she.get(c.strip(), set()))
    if osis != 'Ps':
        for vid, w in db.execute(
                f"SELECT verse_id, kjv_word FROM kjv_words "
                f"WHERE verse_id IN ({marks})", vids):
            tok[vid].update(R1.toks(w))
    for v, t in tok.items():
        bd._tok_by_vid[('m', v)] = t
    lvids = [v for (v,) in db.execute(
        "SELECT verse_id FROM lxx_verses WHERE osis=?", (osis,))]
    ltok = {v: set() for v in lvids}
    lmarks = ",".join("?" * len(lvids))
    for vid, g, b in db.execute(
            f"SELECT verse_id, gloss, bol_gloss FROM lxx_words "
            f"WHERE verse_id IN ({lmarks})", lvids):
        ltok[vid].update(R1.toks(g))
        if b:
            ltok[vid].update(R1.toks(re.split(r";", b)[0]))
    for v, t in ltok.items():
        bd._tok_by_vid[('l', v)] = t
    return lvids


def consumed_candidates(db, bd, osis, res_mt, res_lx_ids):
    """Residual MT orphans whose best LXX match in the whole book is a
    consumed verse. Report-only. Returns rows of
    (mt_ref, consumed_lxx_ref, score, consumed_by, best_residual_score)."""
    lvids = bulk_fill_tokens(db, bd, osis)
    ref_of = {vid: (ch, v) for vid, ch, v in db.execute(
        "SELECT verse_id, chapter, verse FROM lxx_verses WHERE osis=?",
        (osis,))}
    consumed_by = {}
    for lvid, basis in db.execute(
            "SELECT lxx_verse_id, basis FROM lxx_crosswalk "
            "WHERE osis=? AND relation='same'", (osis,)):
        consumed_by[lvid] = basis
    out = []
    for i in res_mt:
        mch, mv, mvid = bd.mt[i]
        best_all = (0.0, None)
        best_res = 0.0
        for lvid in lvids:
            s = bd.score_vids(mvid, lvid)
            if s > best_all[0]:
                best_all = (s, lvid)
            if lvid in res_lx_ids and s > best_res:
                best_res = s
        s, lvid = best_all
        if (lvid is not None and lvid not in res_lx_ids
                and s >= CONSUMED_MIN_SCORE
                and s > best_res + CONSUMED_MARGIN):
            lc, lv = ref_of[lvid]
            out.append((f"{mch}:{mv}", f"{lc}:{lv}", s,
                        consumed_by.get(lvid, '?'), best_res))
    return out


def verse_texts(db, bd, mvid, lvid):
    heb = " ".join(r[0] for r in db.execute(
        "SELECT pointed FROM words WHERE verse_id=? ORDER BY word_pos",
        (mvid,)))
    kjv = " ".join(r[0] for r in db.execute(
        "SELECT kjv_word FROM kjv_words WHERE verse_id=? "
        "ORDER BY kjv_pos", (mvid,)))
    mt_gloss = " | ".join(
        (db.execute(
            "SELECT gloss FROM glosses WHERE strongs=? "
            "AND source='strongs_he'", (s.strip(),)).fetchone() or [""])[0]
        .split(";")[0].split(",")[0]
        for (s,) in db.execute(
            "SELECT strongs FROM words WHERE verse_id=? "
            "ORDER BY word_pos", (mvid,)) if s)
    ltext = db.execute(
        "SELECT text FROM lxx_verses WHERE verse_id=?",
        (lvid,)).fetchone()[0]
    lx_gloss = " | ".join(r[0] or "" for r in db.execute(
        "SELECT gloss FROM lxx_words WHERE verse_id=? ORDER BY position",
        (lvid,)))
    return heb, kjv, mt_gloss, ltext, lx_gloss


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--db', default='bible_v2.db')
    ap.add_argument('--propose', action='store_true')
    ap.add_argument('--dossier', default=None)
    ap.add_argument('--consumed', default=None)
    ap.add_argument('--gate', default=None)
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()

    db = sqlite3.connect(args.db)
    exclusions = R1.load_exclusions()
    books = {}
    proposals = {}  # osis -> {(mt_ref, lxx_ref): (mvid, lvid, score, eff)}
    for osis in ('Ps', 'Jer', 'Prov'):
        bd = R1.BookData(db, osis, exclusions)
        books[osis] = bd
        res_mt, res_lx = residual_pools(db, bd, osis)
        props = propose_pairs(bd, res_mt, res_lx)
        proposals[osis] = {}
        for i, j, s, eff, names in props:
            mch, mv, mvid = bd.mt[i]
            lch, lv, lvid = bd.lx[j]
            proposals[osis][(f"{mch}:{mv}", f"{lch}:{lv}")] = (
                mvid, lvid, s, eff, names)
        print(f"{osis}: residual mt={len(res_mt)} lx={len(res_lx)} "
              f"proposals={len(props)}")
        if args.propose and args.consumed:
            res_lx_ids = {bd.lx[j][2] for j in res_lx}
            cons = consumed_candidates(db, bd, osis, res_mt, res_lx_ids)
            with open(args.consumed, 'a', encoding='utf-8') as f:
                for mref, lref, s, by, bres in cons:
                    f.write(f"{osis}\t{mref}\t{lref}\t{s:.3f}\t{by}\t"
                            f"{bres:.3f}\n")
            print(f"{osis}: consumed-counterpart candidates={len(cons)}")

    if args.propose:
        if args.dossier:
            with open(args.dossier, 'w', encoding='utf-8') as f:
                f.write("osis\tmt_ref\tlxx_ref\tscore\teff\tshared\t"
                        "mt_hebrew\tmt_kjv\tmt_gloss\tlxx_text\t"
                        "lxx_gloss\n")
                for osis in ('Ps', 'Jer', 'Prov'):
                    bd = books[osis]
                    for (mref, lref), (mvid, lvid, s, eff, names) in \
                            sorted(proposals[osis].items()):
                        heb, kjv, mg, ltext, lg = verse_texts(
                            db, bd, mvid, lvid)
                        f.write(
                            f"{osis}\t{mref}\t{lref}\t{s:.3f}\t{eff:.1f}\t"
                            f"{','.join(sorted(names))}\t{heb}\t{kjv}\t"
                            f"{mg}\t{ltext}\t{lg}\n")
        print("propose mode: no DB writes")
        return 0

    if not args.gate:
        print("need --propose or --gate", file=sys.stderr)
        return 2

    existing = db.execute(
        "SELECT COUNT(*) FROM lxx_crosswalk WHERE basis='content-v2'"
    ).fetchone()[0]
    if existing:
        print(f"ABORT: {existing} content-v2 rows already present "
              f"(idempotence guard)", file=sys.stderr)
        return 1

    with open(args.gate, encoding='utf-8') as f:
        gate = json.load(f)
    accepted = gate.get('accepted', [])
    total = 0
    for entry in accepted:
        osis, mref, lref = entry['osis'], entry['mt_ref'], entry['lxx_ref']
        key = (mref, lref)
        if key not in proposals.get(osis, {}):
            print(f"ABORT: gate pair {osis} {mref}->{lref} is not a "
                  f"generated proposal", file=sys.stderr)
            return 1
        mvid, lvid, s, eff, _ = proposals[osis][key]
        if s <= 0:
            print(f"ABORT: gate pair {osis} {mref}->{lref} fails the "
                  f"mechanical evidence re-check", file=sys.stderr)
            return 1
        if not args.dry_run:
            db.execute(
                "INSERT INTO lxx_crosswalk VALUES (?,?,?,'same',"
                "'content-v2')", (mvid, lvid, osis))
        total += 1
    if not args.dry_run:
        db.commit()
    print(f"total content-v2 pairings: {total}"
          f"{' (dry run, not written)' if args.dry_run else ''}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
