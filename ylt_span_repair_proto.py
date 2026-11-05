#!/usr/bin/env python3
"""Span-boundary repair prototype — YLT alignment repair ROUND 2.

Trial only — read-only against bible_v2.db, scored on the EXPANDED gold
set eval/ylt_gold.tsv (42 verses: the round-1 30 plus Ex 20:2, Ex 20:3,
Ex 3:14, Deut 6:4, Deut 6:5, Prov 3:5, Prov 3:6, Eccl 1:2, Song 8:6,
Amos 5:24, Hab 2:4, Mic 6:8, hand-aligned 2026-11-05). Takes the SHIPPED
assignments (ylt_renderings, already carrying the round-1 R2+R1g+R1s
grammar repair) and applies span-boundary rules driven by the corpus's
own OSHB morphology (morph_patterns), reusing the round-1 prototype's
machinery (ylt_grammar_repair_proto: parse_morph / stem / STOP / score).

Discipline (identical to round 1):
  * insert-only — a rule may claim only a token position held by NO
    word; it never steals a held position;
  * H3068 guard (R1g-style) — no rule ever claims for an H3068 word;
  * blank-Strong's words are never claimed for (the documented
    unbridgeable remainder is not guessed at);
  * evidence — a claim must be supported by a stem match against a
    rendering the lemma is known to take (lexicon_ylt_rendering or the
    word's own KJV phrase), except for the closed auxiliary/function
    classes of SB2/SB4, which are ablated separately.

Rules (each ablated):
  SB1 span extension, content tokens: a word WITH a span claims an
      unheld content token immediately adjacent to its span (inside its
      positional gap) when the token stem-matches its lemma evidence.
  SB2 span extension, function tokens: a word WITH a span claims an
      unheld function (stop/auxiliary) token immediately adjacent to
      its span when the run of such tokens is at most 3 and the span
      itself holds a content token.
  SB3 gap claiming v2 (unrendered words): a content word (V/N/A/R/D)
      with NO span claims the maximal contiguous unheld run inside its
      positional gap (length <= 6) when the run contains a token that
      stem-matches its lemma evidence. (Round-1 R1 required the run to
      fill the whole gap, V/N/A only, length <= 4.)
  SB3s strict SB3: run length <= 4 and the evidence token must be a
      content token. (The looser SB3 failed the precision gate; SB3s
      passed — see NOTATION_LEDGER S10, YLT-REPAIR-R2.)
  SB4 verb auxiliary capture: a verb (rendered or not) claims unheld
      auxiliary tokens (hath/doth/is/are/was/be/there/it/...) inside its
      positional gap that are adjacent to its span or to a token it
      claims under SB3 in the same pass.

Gate (round-2, recorded in NOTATION_LEDGER S10): on the round-1
30-verse subset the shipped operating point must be preserved —
precision >= 0.7984, recall strictly above 0.5039, H3068 drift 0 — AND
on the full expanded gold precision must not fall below the shipped
expanded baseline (0.7873) with recall strictly above it (0.5116) and
H3068 drift 0. A rule set failing either half is dropped.
"""
import sys
from collections import defaultdict

sys.path.insert(0, '/home/hatch/workspace/bible-project')
import ylt_grammar_repair_proto as base

AUX = set('hath doth does did shall will is are was were be been there it '
          'let lo'.split())
OLD30 = ({(1, 1, c) for c in range(1, 13)} |
         {(19, 23, c) for c in range(1, 7)} |
         {(23, 53, c) for c in range(1, 13)})


def score_subset(gold, data, predmap, keys):
    sub_gold = {w: gold[w] for k in keys for w in
                [x['word_id'] for x in data[k]['words']]}
    sub_data = {k: data[k] for k in keys}
    return base.score(sub_gold, sub_data, {k: predmap[k] for k in keys})


def evidence_stems(d, w):
    lex, kjv_phrase = d['lex']
    ev = set()
    for rend in lex.get((w['root_id'], w['root_form_seq'],
                         w['root_vowel_seq']), []):
        ev.add(base.stem(rend))
    for t in kjv_phrase.get(w['word_id'], []):
        ev.add(base.stem(t))
    return ev


def apply_rules(data, predmap, rules):
    fired = defaultdict(int)
    for key, d in data.items():
        toks = d['toks']
        pred = predmap[key]
        own = base.owner_map(pred)
        info = {}
        wmap = {}
        for w in d['words']:
            info[w['word_id']] = base.parse_morph(w['morph'])
            wmap[w['word_id']] = w
        order = [w['word_id'] for w in d['words']]

        def claim(wid, pos):
            if pos in own:
                return False
            pred.setdefault(wid, set()).add(pos)
            own[pos] = wid
            return True

        def gap(wid):
            """Positional gap (lo, hi) between neighbouring spans."""
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
                return False            # R1g-style divine-name guard
            if not w['strongs']:
                return False            # blank-Strong's: never guessed
            return True

        if rules & {'SB1', 'SB2'}:
            for wid in order:
                if not eligible(wid):
                    continue
                span = pred.get(wid, set())
                if not span:
                    continue
                lo, hi = gap(wid)
                ev = evidence_stems(d, wmap[wid])
                # extend left, then right, one contiguous unheld run each
                for start, step in ((min(span) - 1, -1), (max(span) + 1, 1)):
                    run = []
                    p = start
                    while lo <= p <= hi and p not in own:
                        run.append(p)
                        p += step
                    for p in run:
                        tok = toks[p - 1]
                        if 'SB1' in rules and base.content(tok) \
                                and base.stem(tok) in ev:
                            if claim(wid, p):
                                fired['SB1'] += 1
                        elif 'SB2' in rules and not base.content(tok) \
                                and len(run) <= 3 and any(
                                    base.content(toks[q - 1])
                                    for q in pred[wid]):
                            if claim(wid, p):
                                fired['SB2'] += 1
                        else:
                            break
        if rules & {'SB3', 'SB3s'}:
            strict = 'SB3s' in rules
            for wid in order:
                if pred.get(wid) or not eligible(wid):
                    continue
                mp = info[wid][0]
                if mp not in ('V', 'N', 'A', 'R', 'D'):
                    continue
                lo, hi = gap(wid)
                ev = evidence_stems(d, wmap[wid])
                # maximal contiguous unheld runs inside the gap
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
                    if strict:
                        ok = 1 <= len(run) <= 4 and any(
                            base.content(toks[p - 1]) and
                            base.stem(toks[p - 1]) in ev for p in run)
                    else:
                        ok = 1 <= len(run) <= 6 and any(
                            base.stem(toks[p - 1]) in ev for p in run)
                    if ok:
                        for p in run:
                            if claim(wid, p):
                                fired['SB3s' if strict else 'SB3'] += 1
                        break
        if 'SB4' in rules:
            for wid in order:
                if not eligible(wid):
                    continue
                if info[wid][0] != 'V':
                    continue
                span = pred.get(wid, set())
                if not span:
                    continue
                lo, hi = gap(wid)
                for p in range(max(lo, min(span) - 2),
                               min(hi, max(span) + 2) + 1):
                    if p not in own and base.norm(toks[p - 1]) in AUX:
                        if claim(wid, p):
                            fired['SB4'] += 1
    return fired


def main():
    gold, data = base.load()
    base_pm = base.clone_pred(data)
    tp, fp, fn, P, R, drift = base.score(gold, data, base_pm)
    print(f'shipped baseline (expanded gold): tp={tp} fp={fp} fn={fn} '
          f'P={P:.4f} R={R:.4f} drift={drift}')
    tp, fp, fn, P, R, drift = score_subset(gold, data, base_pm, OLD30)
    print(f'shipped baseline (round-1 30):    tp={tp} fp={fp} fn={fn} '
          f'P={P:.4f} R={R:.4f} drift={drift}')
    combos = [('SB1',), ('SB2',), ('SB3',), ('SB3s',), ('SB4',),
              ('SB4', 'SB3s'), ('SB4', 'SB1'),
              ('SB1', 'SB2'), ('SB1', 'SB3'), ('SB2', 'SB3'),
              ('SB1', 'SB2', 'SB3'), ('SB1', 'SB3', 'SB4'),
              ('SB1', 'SB2', 'SB3', 'SB4')]
    for rules in combos:
        pm = base.clone_pred(data)
        fired = apply_rules(data, pm, set(rules))
        tp, fp, fn, P, R, dr = base.score(gold, data, pm)
        t2, f2, n2, P2, R2, dr2 = score_subset(gold, data, pm, OLD30)
        gate = (P2 >= 0.7984 and R2 > 0.5039 and dr2 == 0 and
                P >= 0.7873 and R > 0.5116 and dr == 0)
        print(f'{"+".join(rules):16s} fired={dict(fired)} '
              f'EXP tp={tp} fp={fp} fn={fn} P={P:.4f} R={R:.4f} drift={dr} | '
              f'OLD tp={t2} fp={f2} fn={n2} P={P2:.4f} R={R2:.4f} '
              f'drift={dr2} {"GATE-PASS" if gate else "gate-fail"}')


if __name__ == '__main__':
    main()
