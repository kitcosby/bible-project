#!/usr/bin/env python3
"""Apply the YLT grammar repair pass (R2 + R1g + R1s) corpus-wide.

Kit approved 2026-11-03 ("Apply R2+R1g+R1s corpus-wide") after the
prototype (ylt_grammar_repair_proto.py) measured the combo on the gold
set at P 0.7984 / R 0.5039, H3068 drift 0, vs the shipped anchored
baseline P 0.7923 / R 0.4558.

This script imports the prototype's rule code verbatim (tokenize,
parse_morph, apply_rules, score) so the applied pass is the measured
pass. It runs over every verse in ylt_verses, starting from the
ylt_renderings table as shipped. The combo only ever claims token
positions that are currently unheld, so the write is insert-only:
rows are added where a word gains a token; no row is removed or
retargeted. (The shipped table does hold 11,448 token positions under
more than one word — a property of the anchored bridge's gap-fill.
The rules never touch a held position, so those are left exactly as
shipped; every position the pass itself claims was unheld and goes to
exactly one word.)

Usage:
  python3 apply_ylt_grammar_repair.py --db PATH [--write]
Without --write it computes and reports only. With --write it inserts
the new rows in one transaction, then re-verifies from the written
table (gold score, specimen, counts).
"""
import argparse, csv, sqlite3, sys
from collections import defaultdict

sys.path.insert(0, '/home/hatch/workspace/bible-project')
import ylt_grammar_repair_proto as proto

ROOT = '/home/hatch/workspace/bible-project'
RULES = {'R2', 'R1g', 'R1s'}


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
        data[vid] = {'toks': proto.tokenize(r['text']), 'words': words,
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
        data[(b, c, v)] = {'toks': proto.tokenize(yt['text']) if yt else [],
                           'words': words}
        predmap[(b, c, v)] = dict(pred)
    return gold, data, predmap


def counts(db):
    rows = db.execute('SELECT COUNT(*) FROM ylt_renderings').fetchone()[0]
    words_hit = db.execute(
        'SELECT COUNT(DISTINCT word_id) FROM ylt_renderings').fetchone()[0]
    covered = db.execute('''SELECT COUNT(*) FROM (
        SELECT DISTINCT w.verse_id, y.ylt_word_pos
        FROM ylt_renderings y JOIN words w ON w.word_id = y.word_id)'''
        ).fetchone()[0]
    total_tokens = 0
    for r in db.execute('SELECT text FROM ylt_verses'):
        total_tokens += len(proto.tokenize(r['text']))
    words_in_verses = db.execute('''SELECT COUNT(*) FROM words w
        JOIN ylt_verses yv ON yv.verse_id = w.verse_id''').fetchone()[0]
    n_verses = db.execute('SELECT COUNT(*) FROM ylt_verses').fetchone()[0]
    return {'rows': rows, 'words_hit': words_hit, 'covered': covered,
            'total_tokens': total_tokens, 'words_in_verses': words_in_verses,
            'n_verses': n_verses}


def specimen(db):
    vrow = db.execute('''SELECT verse_id FROM verses
        WHERE book_id=23 AND chapter=53 AND verse=11''').fetchone()
    vid = vrow['verse_id']
    yt = db.execute('SELECT text FROM ylt_verses WHERE verse_id=?',
                    (vid,)).fetchone()
    toks = proto.tokenize(yt['text'])
    w1 = db.execute('''SELECT word_id, strongs FROM words
        WHERE verse_id=? AND word_pos=1''', (vid,)).fetchone()
    poss = [r['ylt_word_pos'] for r in db.execute(
        'SELECT ylt_word_pos FROM ylt_renderings WHERE word_id=? '
        'ORDER BY ylt_word_pos', (w1['word_id'],))]
    return w1['strongs'], ' '.join(toks[p - 1] for p in poss)


def gold_score(db):
    gold, data, predmap = load_gold_view(db)
    return proto.score(gold, data, predmap)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--db', required=True)
    ap.add_argument('--write', action='store_true')
    args = ap.parse_args()
    db = sqlite3.connect(args.db)
    db.row_factory = sqlite3.Row

    before = counts(db)
    print('BEFORE:', before)
    tp, fp, fn, P, R, drift = gold_score(db)
    print(f'GOLD BEFORE: tp={tp} fp={fp} fn={fn} P={P:.4f} R={R:.4f} drift={drift}')
    s_strongs, s_phrase = specimen(db)
    print(f'SPECIMEN BEFORE: Isa 53:11 w1 ({s_strongs}) = {s_phrase!r}')

    data, predmap = load_corpus(db)
    old_pairs = {(wid, p) for vid, pm in predmap.items()
                 for wid, ps in pm.items() for p in ps}
    fired = proto.apply_rules(data, predmap, set(RULES))
    new_pairs = {(wid, p) for vid, pm in predmap.items()
                 for wid, ps in pm.items() for p in ps}
    added = new_pairs - old_pairs
    removed = old_pairs - new_pairs
    print(f'RULES FIRED: {dict(fired)}')
    print(f'PAIR DELTA: +{len(added)} added, -{len(removed)} removed')
    if removed:
        print('ABORT: pass removed pairs — diverges from the prototyped '
              'combo (insert-only). No writes.')
        return 1
    if not args.write:
        print('DRY RUN (no --write): nothing written.')
        return 0

    # verse token lists for ylt_word strings of the new rows
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
    tp, fp, fn, P, R, drift = gold_score(db)
    print(f'GOLD AFTER: tp={tp} fp={fp} fn={fn} P={P:.4f} R={R:.4f} drift={drift}')
    gate = P >= 0.7923 and drift == 0
    print('GATE:', 'PASS' if gate else 'FAIL')
    s_strongs, s_phrase = specimen(db)
    print(f'SPECIMEN AFTER: Isa 53:11 w1 ({s_strongs}) = {s_phrase!r}')
    return 0 if gate else 2


if __name__ == '__main__':
    sys.exit(main())
