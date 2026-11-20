#!/usr/bin/env python3
"""Round-3 YLT alignment repair prototype — displaced + remaining
span-boundary false negatives.

Trial only — read-only against bible_v2.db, scored on the EXPANDED gold
set eval/ylt_gold.tsv (42 verses, 438 words, 991 pairs), with the
round-1 30-verse subset scored separately. Takes the SHIPPED
assignments (ylt_renderings, already carrying round-1 grammar repair
and round-2 SB4+SB3s) and applies candidate round-3 rules reusing the
round-1/round-2 machinery (ylt_grammar_repair_proto / ylt_span_repair_proto).

Round-3 re-census of the shipped table (census_r3.py, 2026-11-20):
expanded precision 0.7979 (tp 533 / pred 668) / recall 0.5378,
round-1 subset 0.8055 / 0.5325, H3068 drift 0. Of 458 missed gold
pairs: 337 held by no word (insert-only claimable), 121 held by
another word (unreachable without stealing). False-negative words
271: displaced 89 (171 pairs — gold tokens outside the word's
positional gap, incl. rendered words with no gold overlap and
unrendered words whose gap is collapsed/inverted by a neighbour's
displaced span), remaining span-boundary 179 (281 pairs), unbridgeable
(blank Strong's) 3 (6 pairs).

Discipline (identical to rounds 1-2):
  * insert-only — claim only token positions held by NO word;
  * H3068 guard — no rule claims for an H3068 word, EXCEPT J3068,
    which claims only the token 'Jehovah' itself (YLT's unique
    rendering of H3068), only when it is unheld, the word is
    unrendered, and it is the verse's only unrendered H3068 word;
  * blank-Strong's words are never claimed for;
  * evidence — claims (except the closed-class J3068 and the
    span-interior D2a ablation) require a stem match against a
    rendering the lemma is known to take (lexicon_ylt_rendering or
    the word's own KJV phrase), as in SB3s / R1s.

Candidate rules (each ablated; gate-failures dropped and recorded):
  D1   displaced evidence claim (unrendered words, any morph class):
       claim every unheld token in the verse whose stem matches the
       word's lemma evidence, regardless of positional gap.
  D1c  D1 restricted to content tokens.
  D2   span-interior evidence fill: a rendered word claims unheld
       evidence-matching tokens strictly inside its own span.
  D2a  span-interior fill without evidence (ablation).
  D3   rendered-word displaced claim: a rendered word claims unheld
       evidence-matching tokens anywhere in the verse.
  SB5  long strict gap claim: SB3s with run length <= 6 when the run
       holds >= 2 content evidence tokens.
  SB6  span extension through function tokens: a rendered word claims
       a whole contiguous unheld run (<= 4) adjacent to its span when
       the run contains a content evidence token.
  SB7  SB4 with the auxiliary window widened from 2 to 4.
  J3068 divine-name token claim (see discipline above). First form
       FAILED: on Isa 53:10 it claimed the verse-final 'Jehovah' for
       the verse-initial H3068 word, but gold assigns that token to
       the verse's other (rendered) H3068 word — drift 1, dropped.
  D1s  strict displaced claim: D1c plus a uniqueness condition — the
       token is claimed only when NO other unrendered eligible word
       in the verse evidence-matches it. (Earned from the D1c
       claim-by-claim audit: all 5 D1c false positives had an
       unrendered competitor for the token; the true positives'
       competitors were already-rendered words.)
  J3068b J3068 plus an adjacency guard: the 'Jehovah' token must not
       lie within 1 position of another H3068 word's span (the
       Isa 53:10 failure mode above).

Gate (round-3, per plan): expanded precision >= 0.7979 with recall
strictly above 0.5378, round-1 subset precision >= 0.8055 with recall
strictly above 0.5325, H3068 drift 0 on both.
"""
import sys
from collections import defaultdict

sys.path.insert(0, '/home/hatch/workspace/bible-project')
import ylt_grammar_repair_proto as base
import ylt_span_repair_proto as span

AUX = span.AUX
OLD30 = span.OLD30


def apply_rules(data, predmap, rules):
    fired = defaultdict(int)
    for key, d in data.items():
        toks = d['toks']
        pred = predmap[key]
        own = base.owner_map(pred)
        wmap = {w['word_id']: w for w in d['words']}
        info = {w['word_id']: base.parse_morph(w['morph'])
                for w in d['words']}
        order = [w['word_id'] for w in d['words']]

        def claim(wid, pos):
            if pos in own:
                return False
            pred.setdefault(wid, set()).add(pos)
            own[pos] = wid
            return True

        def gap(wid):
            i = order.index(wid)
            lo, hi = 1, len(toks)
            for j in range(i - 1, -1, -1):
                if pred.get(order[j]):
                    lo = max(pred[order[j]]) + 1
                    break
            for j in range(i + 1, len(order)):
                if pred.get(order[j]):
                    hi = min(pred[order[j]]) - 1
                    break
            return lo, hi

        def eligible(wid):
            w = wmap[wid]
            if w['strongs'] == 'H3068':
                return False
            if not w['strongs']:
                return False
            return True

        if 'J3068' in rules:
            unrend = [wid for wid in order
                      if wmap[wid]['strongs'] == 'H3068'
                      and not pred.get(wid)]
            if len(unrend) == 1:
                wid = unrend[0]
                cand = [p for p in range(1, len(toks) + 1)
                        if p not in own and base.norm(toks[p - 1]) == 'jehovah']
                if len(cand) == 1 and claim(wid, cand[0]):
                    fired['J3068'] += 1

        if 'J3068b' in rules:
            unrend = [wid for wid in order
                      if wmap[wid]['strongs'] == 'H3068'
                      and not pred.get(wid)]
            if len(unrend) == 1:
                wid = unrend[0]
                other_spans = [pred[o] for o in order
                               if o != wid
                               and wmap[o]['strongs'] == 'H3068'
                               and pred.get(o)]
                cand = [p for p in range(1, len(toks) + 1)
                        if p not in own and base.norm(toks[p - 1]) == 'jehovah'
                        and not any(abs(p - q) <= 1 for s in other_spans
                                    for q in s)]
                if len(cand) == 1 and claim(wid, cand[0]):
                    fired['J3068b'] += 1

        if 'D1s' in rules:
            unrend_ev = {}
            for wid in order:
                if not pred.get(wid) and eligible(wid):
                    unrend_ev[wid] = span.evidence_stems(d, wmap[wid])
            for wid in order:
                if wid not in unrend_ev:
                    continue
                ev = unrend_ev[wid]
                if not ev:
                    continue
                for p in range(1, len(toks) + 1):
                    if p in own or not base.content(toks[p - 1]):
                        continue
                    st = base.stem(toks[p - 1])
                    if st not in ev:
                        continue
                    if any(st in ev2 for w2, ev2 in unrend_ev.items()
                           if w2 != wid):
                        continue
                    if claim(wid, p):
                        fired['D1s'] += 1

        if rules & {'D1', 'D1c'}:
            for wid in order:
                if pred.get(wid) or not eligible(wid):
                    continue
                ev = span.evidence_stems(d, wmap[wid])
                if not ev:
                    continue
                for p in range(1, len(toks) + 1):
                    if p in own:
                        continue
                    if 'D1c' in rules and not base.content(toks[p - 1]):
                        continue
                    if base.stem(toks[p - 1]) in ev:
                        if claim(wid, p):
                            fired['D1c' if 'D1c' in rules else 'D1'] += 1

        if rules & {'D2', 'D2a'}:
            for wid in order:
                if not eligible(wid):
                    continue
                s = pred.get(wid, set())
                if len(s) < 2:
                    continue
                ev = span.evidence_stems(d, wmap[wid])
                for p in range(min(s) + 1, max(s)):
                    if p in own:
                        continue
                    if 'D2a' in rules or base.stem(toks[p - 1]) in ev:
                        if claim(wid, p):
                            fired['D2a' if 'D2a' in rules else 'D2'] += 1

        if 'D3' in rules:
            for wid in order:
                if not pred.get(wid) or not eligible(wid):
                    continue
                ev = span.evidence_stems(d, wmap[wid])
                if not ev:
                    continue
                for p in range(1, len(toks) + 1):
                    if p not in own and base.stem(toks[p - 1]) in ev:
                        if claim(wid, p):
                            fired['D3'] += 1

        if 'SB5' in rules:
            for wid in order:
                if pred.get(wid) or not eligible(wid):
                    continue
                if info[wid][0] not in ('V', 'N', 'A', 'R', 'D'):
                    continue
                lo, hi = gap(wid)
                if lo > hi:
                    continue
                ev = span.evidence_stems(d, wmap[wid])
                runs, cur = [], []
                for p in range(lo, hi + 1):
                    if p not in own:
                        cur.append(p)
                    else:
                        if cur:
                            runs.append(cur)
                        cur = []
                if cur:
                    runs.append(cur)
                for run in runs:
                    nev = sum(1 for p in run
                              if base.content(toks[p - 1])
                              and base.stem(toks[p - 1]) in ev)
                    if 5 <= len(run) <= 6 and nev >= 2:
                        for p in run:
                            if claim(wid, p):
                                fired['SB5'] += 1
                        break

        if 'SB6' in rules:
            for wid in order:
                if not eligible(wid):
                    continue
                s = pred.get(wid, set())
                if not s:
                    continue
                lo, hi = gap(wid)
                ev = span.evidence_stems(d, wmap[wid])
                for start, step in ((min(s) - 1, -1), (max(s) + 1, 1)):
                    run = []
                    p = start
                    while lo <= p <= hi and p not in own:
                        run.append(p)
                        p += step
                    if 1 <= len(run) <= 4 and any(
                            base.content(toks[q - 1])
                            and base.stem(toks[q - 1]) in ev for q in run):
                        for q in run:
                            if claim(wid, q):
                                fired['SB6'] += 1

        if 'SB7' in rules:
            for wid in order:
                if not eligible(wid):
                    continue
                if info[wid][0] != 'V':
                    continue
                s = pred.get(wid, set())
                if not s:
                    continue
                lo, hi = gap(wid)
                for p in range(max(lo, min(s) - 4),
                               min(hi, max(s) + 4) + 1):
                    if p not in own and base.norm(toks[p - 1]) in AUX:
                        if claim(wid, p):
                            fired['SB7'] += 1
    return fired


def main():
    gold, data = base.load()
    base_pm = base.clone_pred(data)
    tp, fp, fn, P, R, drift = base.score(gold, data, base_pm)
    print(f'shipped baseline (expanded gold): tp={tp} fp={fp} fn={fn} '
          f'P={P:.4f} R={R:.4f} drift={drift}')
    tp, fp, fn, P, R, drift = span.score_subset(gold, data, base_pm, OLD30)
    print(f'shipped baseline (round-1 30):    tp={tp} fp={fp} fn={fn} '
          f'P={P:.4f} R={R:.4f} drift={drift}')
    combos = [('D1',), ('D1c',), ('D2',), ('D2a',), ('D3',), ('SB5',),
              ('SB6',), ('SB7',), ('J3068',),
              ('D1', 'D2'), ('D1c', 'D2'), ('D1', 'D3'), ('D1', 'D2', 'D3'),
              ('D1', 'SB6'), ('D1', 'J3068'), ('D1c', 'J3068'),
              ('D1', 'D2', 'J3068'), ('D1', 'D2', 'D3', 'J3068'),
              ('D1', 'D2', 'SB5'), ('D1', 'D2', 'SB6'),
              ('D1', 'D2', 'SB7'), ('D1', 'D2', 'SB5', 'SB6', 'SB7'),
              ('D1', 'D2', 'D3', 'SB5', 'SB6', 'SB7', 'J3068'),
              ('D1s',), ('J3068b',), ('D1s', 'J3068b'),
              ('D1s', 'D2'), ('D1s', 'SB6'), ('D1s', 'J3068')]
    for rules in combos:
        pm = base.clone_pred(data)
        fired = apply_rules(data, pm, set(rules))
        tp, fp, fn, P, R, dr = base.score(gold, data, pm)
        t2, f2, n2, P2, R2, dr2 = span.score_subset(gold, data, pm, OLD30)
        gate = (P >= 0.7979 and R > 0.5378 and dr == 0 and
                P2 >= 0.8055 and R2 > 0.5325 and dr2 == 0)
        print(f'{"+".join(rules):28s} fired={dict(fired)} '
              f'EXP tp={tp} fp={fp} fn={fn} P={P:.4f} R={R:.4f} drift={dr} | '
              f'OLD tp={t2} fp={f2} fn={n2} P={P2:.4f} R={R2:.4f} '
              f'drift={dr2} {"GATE-PASS" if gate else "gate-fail"}', flush=True)


if __name__ == '__main__':
    main()
