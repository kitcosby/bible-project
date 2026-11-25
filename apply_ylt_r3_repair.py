#!/usr/bin/env python3
"""Apply the YLT round-3 repair pass (D1s + J3068b) corpus-wide.

Round 3 of the YLT alignment repair (see NOTATION_LEDGER S10,
YLT-REPAIR-R3). The prototype ylt_r3_repair_proto.py measured the
combo on the expanded gold set eval/ylt_gold.tsv (42 verses /
438 words / 991 pairs):
  D1s   strict displaced claim — an unrendered word (blank Strong's
        and H3068 excluded) claims an unheld CONTENT token anywhere
        in its verse whose stem matches a rendering the lemma is
        known to take (lexicon_ylt_rendering or the word's own KJV
        phrase), only when no other unrendered eligible word in the
        verse evidence-matches that token;
  J3068b divine-name token claim — an unrendered H3068 word claims
        the token 'Jehovah' when it is the verse's only unrendered
        H3068 word, the token is unheld and unique, and it does not
        lie within 1 position of another H3068 word's span.
This script imports the prototype's rule code verbatim
(ylt_r3_repair_proto.apply_rules) so the applied pass is the measured
pass. It runs over every verse in ylt_verses, starting from the
ylt_renderings table as shipped. Both rules only ever claim token
positions that are currently unheld, so the write is insert-only:
rows are added where a word gains a token; no row is removed or
retargeted. Blank-Strong's words are never claimed for; the H3068
guard is retained for every rule except J3068b's 'Jehovah'-only
claim, which never touches any other token.

Gate (round-3, re-checked on the CURRENT table before any write):
  expanded gold: precision >= 0.7979 AND recall strictly above
    0.5378, H3068 drift 0;
  round-1 30-verse subset: precision >= 0.8055 AND recall strictly
    above 0.5325, H3068 drift 0.
The shipped baselines are measured live from the target DB at run
time and the after-scores must also preserve the measured baseline
precision on both halves. If the gate fails, the script writes
nothing and exits 2.

Usage:
  python3 apply_ylt_r3_repair.py --db PATH [--write]
Without --write it computes and reports only. With --write it inserts
the new rows in one transaction, then re-verifies from the written
table (gold scores read back, counts, insert-only delta).
"""
import argparse, csv, sqlite3, sys
from collections import defaultdict

sys.path.insert(0, '/home/hatch/workspace/bible-project')
import ylt_grammar_repair_proto as base
import ylt_span_repair_proto as span
import ylt_r3_repair_proto as r3

ROOT = '/home/hatch/workspace/bible-project'
RULES = {'D1s', 'J3068b'}
# Round-3 gate floors (the 2026-11-19 shipped operating point,
# NOTATION_LEDGER S10 YLT-REPAIR-R2 application).
HIST_EXP_P, HIST_EXP_R = 0.7979, 0.5378
HIST_OLD_P, HIST_OLD_R = 0.8055, 0.5325


def load_corpus(db):
    """(data, predmap) for every verse in ylt_verses, proto formats."""
    lex = {}
    for r in db.execute('''SELECT root_id, root_form_seq, vowel_seq, rendering
        FROM lexicon_ylt_rendering ORDER BY seq'''):
        lex.setdefault((r['root_id'], r['root_form_seq'], r['vowel_seq']),
                       []).append(r['rendering'])
    kjv_all = defaultdict(list)
    for r in db.execute('''SELECT word_id, kjv_word FROM kjv_renderings
        ORDER BY word_id, rendering_id'''):
        kjv_all[r['word_id']].append(r['kjv_word'])
    words_by_verse = defaultdict(list)
    for r in db.execute('''SELECT w.word_id, w.word_pos, w.strongs,
            m.pattern AS morph, w.root_id, w.root_form_seq,
            w.root_vowel_seq, w.verse_id
        FROM words w
        JOIN ylt_verses yv ON yv.verse_id = w.verse_id
        LEFT JOIN morph_patterns m ON m.pattern_id = w.morph_pattern_id
        ORDER BY w.verse_id, w.word_pos'''):
        words_by_verse[r['verse_id']].append(dict(r))
    pred_by_verse = defaultdict(lambda: defaultdict(set))
    for r in db.execute('''SELECT y.word_id, y.ylt_word_pos, w.verse_id
        FROM ylt_renderings y JOIN words w ON w.word_id = y.word_id'''):
        pred_by_verse[r['verse_id']][r['word_id']].add(r['ylt_word_pos'])
    data, predmap = {}, {}
    for r in db.execute('SELECT verse_id, text FROM ylt_verses'):
        vid = r['verse_id']
        words = words_by_verse.get(vid, [])
        kjv_phrase = {w['word_id']: kjv_all.get(w['word_id'], [])
                      for w in words}
        data[vid] = {'toks': base.tokenize(r['text']), 'words': words,
                     'lex': (lex, kjv_phrase)}
        predmap[vid] = dict(pred_by_verse.get(vid, {}))
    return data, predmap


def load_gold_view(db):
    """(gold, data, predmap) over the gold verses, read fresh from db."""
    gold, verses = {}, {}
    with open(f'{ROOT}/eval/ylt_gold.tsv') as f:
        for row in csv.DictReader(f, delimiter='\t'):
            wid = int(row['word_id'])
            gold[wid] = {int(x) for x in row['ylt_pos'].split(',')
                         if x.strip()}
            verses.setdefault((int(row['book']), int(row['chapter']),
                               int(row['verse'])), []).append(wid)
    data, predmap = {}, {}
    for (b, c, v) in verses:
        vrow = db.execute('''SELECT verse_id FROM verses
            WHERE book_id=? AND chapter=? AND verse=?''',
                          (b, c, v)).fetchone()
        vid = vrow['verse_id']
        yt = db.execute('SELECT text FROM ylt_verses WHERE verse_id=?',
                        (vid,)).fetchone()
        words = [dict(r) for r in db.execute(
            '''SELECT w.word_id, w.word_pos, w.strongs, m.pattern AS morph,
                w.root_id, w.root_form_seq, w.root_vowel_seq
            FROM words w
            LEFT JOIN morph_patterns m ON m.pattern_id=w.morph_pattern_id
            WHERE w.verse_id=? ORDER BY w.word_pos''', (vid,))]
        pred = defaultdict(set)
        for r in db.execute('''SELECT word_id, ylt_word_pos
            FROM ylt_renderings
            WHERE word_id IN (SELECT word_id FROM words
                              WHERE verse_id=?)''', (vid,)):
            pred[r['word_id']].add(r['ylt_word_pos'])
        data[(b, c, v)] = {'toks': base.tokenize(yt['text']) if yt else [],
                           'words': words}
        predmap[(b, c, v)] = dict(pred)
    return gold, data, predmap


def gold_scores(db):
    gold, data, predmap = load_gold_view(db)
    exp = base.score(gold, data, predmap)
    old = span.score_subset(gold, data, predmap, span.OLD30)
    return exp, old


def counts(db):
    rows = db.execute('SELECT COUNT(*) FROM ylt_renderings').fetchone()[0]
    words_hit = db.execute(
        'SELECT COUNT(DISTINCT word_id) FROM ylt_renderings').fetchone()[0]
    covered = db.execute('''SELECT COUNT(*) FROM (
        SELECT DISTINCT w.verse_id, y.ylt_word_pos
        FROM ylt_renderings y JOIN words w ON w.word_id = y.word_id)'''
        ).fetchone()[0]
    # Denominators of record (round-1/2 ledgers): YLT tokens in the
    # OT (book_id<=39) verses present in ylt_verses = 602,067, and the
    # OT words in those verses = 262,136 (re-measured 2026-11-19).
    total_tokens = 0
    for r in db.execute('''SELECT y.text FROM ylt_verses y
        JOIN verses v ON v.verse_id = y.verse_id WHERE v.book_id <= 39'''):
        total_tokens += len(base.tokenize(r['text']))
    words_in_verses = db.execute('''SELECT COUNT(*) FROM words w
        JOIN verses v ON v.verse_id = w.verse_id
        JOIN ylt_verses yv ON yv.verse_id = w.verse_id
        WHERE v.book_id <= 39''').fetchone()[0]
    n_verses = db.execute('SELECT COUNT(*) FROM ylt_verses').fetchone()[0]
    return {'rows': rows, 'words_hit': words_hit, 'covered': covered,
            'total_tokens': total_tokens, 'words_in_verses': words_in_verses,
            'n_verses': n_verses}


def gate_ok(before_exp, before_old, after_exp, after_old):
    return (after_exp[3] >= before_exp[3] and after_exp[3] >= HIST_EXP_P
            and after_exp[4] > before_exp[4] and after_exp[4] > HIST_EXP_R
            and after_exp[5] == 0
            and after_old[3] >= before_old[3] and after_old[3] >= HIST_OLD_P
            and after_old[4] > before_old[4] and after_old[4] > HIST_OLD_R
            and after_old[5] == 0)


def fmt(label, s):
    tp, fp, fn, P, R, drift = s
    print(f'{label}: tp={tp} fp={fp} fn={fn} P={P:.4f} R={R:.4f} drift={drift}')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--db', required=True)
    ap.add_argument('--write', action='store_true')
    args = ap.parse_args()
    db = sqlite3.connect(args.db)
    db.row_factory = sqlite3.Row

    before = counts(db)
    print('BEFORE:', before)
    b_exp, b_old = gold_scores(db)
    fmt('GOLD EXPANDED BEFORE', b_exp)
    fmt('GOLD ROUND1-30 BEFORE', b_old)

    data, predmap = load_corpus(db)
    old_pairs = {(wid, p) for vid, pm in predmap.items()
                 for wid, ps in pm.items() for p in ps}
    fired = r3.apply_rules(data, predmap, set(RULES))
    new_pairs = {(wid, p) for vid, pm in predmap.items()
                 for wid, ps in pm.items() for p in ps}
    added = new_pairs - old_pairs
    removed = old_pairs - new_pairs
    print(f'RULES FIRED: {dict(fired)}')
    print(f'PAIR DELTA: +{len(added)} added, -{len(removed)} removed')
    if removed:
        print('ABORT: pass removed pairs - diverges from the prototyped '
              'combo (insert-only). No writes.')
        return 1

    gold, gdata, gpred = load_gold_view(db)
    for (b, c, v) in list(gdata.keys()):
        vid = db.execute('''SELECT verse_id FROM verses
            WHERE book_id=? AND chapter=? AND verse=?''',
                         (b, c, v)).fetchone()['verse_id']
        gpred[(b, c, v)] = {wid: set(ps) for wid, ps in
                            predmap.get(vid, {}).items()}
    a_exp = base.score(gold, gdata, gpred)
    a_old = span.score_subset(gold, gdata, gpred, span.OLD30)
    fmt('GOLD EXPANDED AFTER (in-memory)', a_exp)
    fmt('GOLD ROUND1-30 AFTER (in-memory)', a_old)
    ok = gate_ok(b_exp, b_old, a_exp, a_old)
    print('GATE:', 'PASS' if ok else 'FAIL')
    if not ok:
        print('ABORT: re-gate failed on current data. No writes.')
        return 2
    if not args.write:
        print('DRY RUN (no --write): nothing written.')
        return 0

    toks_by_word = {}
    for vid, d in data.items():
        for w in d['words']:
            toks_by_word[w['word_id']] = d['toks']
    rows = [(wid, toks_by_word[wid][p - 1], p, 'bridged')
            for wid, p in sorted(added)]
    with db:
        db.executemany('''INSERT INTO ylt_renderings
            (word_id, ylt_word, ylt_word_pos, label) VALUES (?,?,?,?)''',
                       rows)
    print(f'INSERTED {len(rows)} rows')

    after = counts(db)
    print('AFTER:', after)
    r_exp, r_old = gold_scores(db)
    fmt('GOLD EXPANDED READBACK', r_exp)
    fmt('GOLD ROUND1-30 READBACK', r_old)
    match = (r_exp == a_exp and r_old == a_old)
    print('READBACK MATCHES PROTOTYPE/APPLY PASS:', match)
    return 0 if match else 3


if __name__ == '__main__':
    sys.exit(main())
