#!/usr/bin/env python3
"""Grammar repair pass prototype for the computed Young's renderings.

Trial only — read-only against bible_v2.db, scored on eval/ylt_gold.tsv.
Takes the SHIPPED anchored assignments (ylt_renderings) and applies
grammar-informed repairs driven by the corpus's own OSHB morphology
(morph_patterns), then re-scores. No DB writes.

Rules (each ablated):
  R3 suffix-possessive capture: a word with an /Sp.. pronominal suffix
     should own its possessive token (my/thy/his/her/our/your/their).
  R2 construct head extension: a construct-state noun (or prep+noun)
     whose span has no content token claims the next content token
     when it is unclaimed ("Of the" -> "Of the travail").
  R1 unrendered claiming: a content word (V/N/A) with no span claims a
     short run of unclaimed tokens in its positional gap when the run
     contains a content token.

Gate discipline (NOTATION_LEDGER S10): precision must stay >= 0.7923
and H3068 drift must stay 0 for a rule set to be worth shipping.
"""
import sqlite3, re, string, csv, sys
from collections import defaultdict

ROOT = '/home/hatch/workspace/bible-project'
STRIP = string.punctuation + '\u2014\u2013\u2018\u2019\u201c\u201d\u00ab\u00bb'

def tokenize(text):
    return [t for t in (raw.strip(STRIP) for raw in text.split()) if t]

STOP = set('''of the and in on to from by with for a an is are was were be been
he she it they them him his her my thy their our your its not nor or but as at
unto hath doth shall will do does did have has had let lo behold also when who
whom whose which that this these those there here into out up down over under
again more most other some any no than too very can could may might must'''.split())

POSS = {'1cs': 'my', '1cp': 'our', '2ms': 'thy', '2fs': 'thy',
        '2mp': 'your', '2fp': 'your', '3ms': 'his', '3fs': 'her',
        '3mp': 'their', '3fp': 'their'}

def norm(t):
    return t.lower().strip(STRIP)

def stem(w):
    w = norm(w)
    for suf in ('ing', 'eth', 'est', 'es', 'ed', "'s", 's'):
        if len(w) > len(suf) + 2 and w.endswith(suf):
            return w[:-len(suf)]
    return w

def parse_morph(pattern):
    """(main_pos, is_construct, suffix_code, has_prep_prefix)"""
    if not pattern:
        return None, False, None, False
    segs = pattern.split('/')
    main_pos, is_construct, suffix_code, has_prep = None, False, None, False
    for i, seg in enumerate(segs):
        s = seg[1:] if i == 0 and seg[:1] in ('H', 'A') else seg
        if not s:
            continue
        head = s[0]
        if head == 'S' and s[1:2] == 'p':
            suffix_code = s[2:]
        elif head in ('V', 'N', 'A') and main_pos is None:
            main_pos = head
            if head in ('N', 'A') and s[-1:] == 'c':
                is_construct = True
        elif head == 'R':
            has_prep = True
    return main_pos, is_construct, suffix_code, has_prep

def load():
    db = sqlite3.connect(f'{ROOT}/bible_v2.db')
    db.row_factory = sqlite3.Row
    gold = {}
    verses = {}
    with open(f'{ROOT}/eval/ylt_gold.tsv') as f:
        for row in csv.DictReader(f, delimiter='\t'):
            wid = int(row['word_id'])
            gold[wid] = {int(x) for x in row['ylt_pos'].split(',') if x.strip()}
            verses.setdefault((int(row['book']), int(row['chapter']),
                               int(row['verse'])), []).append(wid)
    data = {}
    for (b, c, v), wids in verses.items():
        vrow = db.execute('SELECT verse_id FROM verses WHERE book_id=? AND chapter=? AND verse=?',
                          (b, c, v)).fetchone()
        vid = vrow['verse_id']
        yt = db.execute('SELECT text FROM ylt_verses WHERE verse_id=?', (vid,)).fetchone()
        toks = tokenize(yt['text']) if yt else []
        words = []
        for r in db.execute('''SELECT w.word_id, w.word_pos, w.strongs, m.pattern AS morph,
            w.root_id, w.root_form_seq, w.root_vowel_seq
            FROM words w LEFT JOIN morph_patterns m ON m.pattern_id=w.morph_pattern_id
            WHERE w.verse_id=? ORDER BY w.word_pos''', (vid,)):
            words.append(dict(r))
        lex = {}
        for r in db.execute('''SELECT root_id, root_form_seq, vowel_seq, rendering
            FROM lexicon_ylt_rendering ORDER BY seq'''):
            lex.setdefault((r['root_id'], r['root_form_seq'], r['vowel_seq']),
                           []).append(r['rendering'])
        kjv_phrase = {}
        for r in db.execute('''SELECT word_id, kjv_word FROM kjv_renderings
            WHERE word_id IN (SELECT word_id FROM words WHERE verse_id=?)
            ORDER BY word_id, rendering_id''', (vid,)):
            kjv_phrase.setdefault(r['word_id'], []).append(r['kjv_word'])
        data_lex = (lex, kjv_phrase)
        pred = defaultdict(set)
        for r in db.execute('''SELECT word_id, ylt_word_pos FROM ylt_renderings
            WHERE word_id IN (SELECT word_id FROM words WHERE verse_id=?)''', (vid,)):
            pred[r['word_id']].add(r['ylt_word_pos'])
        data[(b, c, v)] = {'toks': toks, 'words': words, 'pred': pred,
                           'lex': data_lex}
    return gold, data

def score(gold, data, predmap):
    tp = fp = fn = 0
    drift = 0
    for (b, c, v), d in data.items():
        strongs = {w['word_id']: w['strongs'] for w in d['words']}
        for wid, g in gold.items():
            if wid not in strongs:
                continue
            p = predmap.get((b, c, v), {}).get(wid, set())
            tp += len(g & p); fp += len(p - g); fn += len(g - p)
            if strongs[wid] == 'H3068':
                drift += len(p - g)
    P = tp / (tp + fp) if tp + fp else 0
    R = tp / (tp + fn) if tp + fn else 0
    return tp, fp, fn, P, R, drift

def clone_pred(data):
    return {k: {wid: set(s) for wid, s in d['pred'].items()} for k, d in data.items()}

def owner_map(pred):
    own = {}
    for wid, s in pred.items():
        for p in s:
            own[p] = wid
    return own

def content(tok):
    return norm(tok) not in STOP

def apply_rules(data, predmap, rules):
    """Mutate predmap in place; return per-rule firing counts."""
    fired = defaultdict(int)
    for key, d in data.items():
        toks = d['toks']
        pred = predmap[key]
        own = owner_map(pred)
        info = {}
        for w in d['words']:
            mp, cons, suf, prep = parse_morph(w['morph'])
            info[w['word_id']] = (mp, cons, suf, prep)
        order = [w['word_id'] for w in d['words']]

        def claim(wid, pos):
            if pos in own and own[pos] != wid:
                pred[own[pos]].discard(pos)
            pred.setdefault(wid, set()).add(pos)
            own[pos] = wid

        if 'R3' in rules or 'R3u' in rules:  # suffix possessive capture
            steal_ok = 'R3' in rules
            for wid in order:
                mp, cons, suf, prep = info[wid]
                want = POSS.get(suf or '')
                if not want:
                    continue
                span = pred.get(wid, set())
                lo = (min(span) if span else None)
                hi = (max(span) if span else None)
                # search a small window around the span for the possessive
                cand = [p for p in range(1, len(toks) + 1)
                        if norm(toks[p - 1]) == want
                        and (lo is None or lo - 2 <= p <= hi + 2)]
                for p in cand:
                    if p in span:
                        break
                    holder = own.get(p)
                    if holder is None:
                        claim(wid, p); fired['R3'] += 1; break
                    # steal only if holder keeps another token and does
                    # not itself carry the same suffix expectation
                    h_suf = info.get(holder, (None,) * 4)[2]
                    if steal_ok and len(pred[holder]) > 1 and POSS.get(h_suf or '') != want:
                        claim(wid, p); fired['R3'] += 1; break
        if 'R2' in rules:  # construct head extension
            for wid in order:
                mp, cons, suf, prep = info[wid]
                if not ((cons and mp in ('N', 'A')) or (prep and mp == 'N')):
                    continue
                span = pred.get(wid, set())
                if not span:
                    continue
                if any(content(toks[p - 1]) for p in span):
                    continue
                nxt = max(span) + 1
                if nxt <= len(toks) and nxt not in own and content(toks[nxt - 1]):
                    claim(wid, nxt); fired['R2'] += 1
        if rules & {'R1', 'R1g', 'R1s'}:  # unrendered claiming
            lex, kjv_phrase = d['lex']
            wmap = {w['word_id']: w for w in d['words']}
            spans = {wid: pred.get(wid, set()) for wid in order}
            for i, wid in enumerate(order):
                if spans[wid]:
                    continue
                w = wmap[wid]
                if 'R1g' in rules and w['strongs'] == 'H3068':
                    continue  # divine name: never guess-claimed (drift guard)
                mp, cons, suf, prep = info[wid]
                if mp not in ('V', 'N', 'A'):
                    continue
                lo = 1
                for j in range(i - 1, -1, -1):
                    if spans[order[j]]:
                        lo = max(spans[order[j]]) + 1; break
                hi = len(toks)
                for j in range(i + 1, len(order)):
                    if spans[order[j]]:
                        hi = min(spans[order[j]]) - 1; break
                run = [p for p in range(lo, hi + 1) if p not in own]
                if not (1 <= len(run) <= 4
                        and run == list(range(lo, lo + len(run)))
                        and any(content(toks[p - 1]) for p in run)):
                    continue
                if 'R1s' in rules:
                    # evidence: a run token must stem-match a rendering
                    # this lemma is known to take (YLT lexicon or its own
                    # KJV phrase) — no match, no claim
                    ev = set()
                    for rend in lex.get((w['root_id'], w['root_form_seq'],
                                         w['root_vowel_seq']), []):
                        ev.add(stem(rend))
                    for t in kjv_phrase.get(wid, []):
                        ev.add(stem(t))
                    if not any(stem(toks[p - 1]) in ev for p in run):
                        continue
                for p in run:
                    claim(wid, p)
                spans[wid] = pred[wid]
                fired['R1'] += 1
    return fired

def main():
    gold, data = load()
    base = clone_pred(data)
    tp, fp, fn, P, R, drift = score(gold, data, base)
    print(f'baseline (shipped): tp={tp} fp={fp} fn={fn} P={P:.4f} R={R:.4f} drift={drift}')
    for rules in [('R1',), ('R2',), ('R3',), ('R3', 'R2'), ('R3', 'R2', 'R1'),
                  ('R1g',), ('R1s',), ('R1g', 'R1s'), ('R3u',),
                  ('R2', 'R1g'), ('R2', 'R1s'), ('R2', 'R1g', 'R1s'),
                  ('R2', 'R3u'), ('R2', 'R3u', 'R1s'), ('R2', 'R3u', 'R1g', 'R1s')]:
        pm = clone_pred(data)
        fired = apply_rules(data, pm, set(rules))
        tp, fp, fn, P, R, drift = score(gold, data, pm)
        gate = 'GATE-PASS' if (P >= 0.7923 and drift == 0) else 'gate-fail'
        print(f'{"+".join(rules):16s} fired={dict(fired)} tp={tp} fp={fp} fn={fn} '
              f'P={P:.4f} R={R:.4f} drift={drift} {gate}')
    # the specimen: Isaiah 53:11 word 1 under the passing combo
    pm = clone_pred(data)
    apply_rules(data, pm, {'R2'})
    key = (23, 53, 11)
    d = data[key]
    w1 = d['words'][0]['word_id']
    got = sorted(pm[key].get(w1, set()))
    print('specimen Isa 53:11 w1 (H5999) after R2:',
          ' '.join(d['toks'][p - 1] for p in got), '| gold:',
          ' '.join(d['toks'][p - 1] for p in sorted(gold[w1])))

if __name__ == '__main__':
    main()
