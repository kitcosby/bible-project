#!/usr/bin/env python3
"""Extract fully attested Dead Sea Scrolls verses from the staged
ETCBC/dss Text-Fabric dataset (2.0.1; Abegg transcriptions, CACCHT;
dataset CC BY-NC 4.0) into worker-out/dss/dss_words.tsv:
  scroll, book, chapter, verse, pos, raw, folded

Kit 2026-10-17: DSS leg, scope = FULLY ATTESTED VERSES ONLY.
A (scroll, book, chapter, verse) cell qualifies iff:
  * it has at least one glyph word;
  * every glyph word's letters are physically attested — its `glyph`
    feature is non-empty and NONE of its signs carries a rec / unc /
    rem / alt flag (reconstructed, uncertain, removed, or alternative
    letters never produce data; `cor` signs are the scribe's own
    corrected text and count as attested; `vac` is blank space);
  * no glyph word is Greek (lang 'g' or greekcapital script) and no
    word carries a halfverse mark (partial-verse coverage);
  * book/chapter/verse join the corpus (BHSA book codes, integer
    chapter/verse).
Punctuation and other non-glyph word types are ignored (they carry no
letters). Graphic words are rebuilt from the analytic word nodes on
the `after` feature (absent = adjacent, join; ' ' = boundary). `raw`
keeps only consonant letters (the transcription's morpheme mark
U+05F3 and any other non-letter characters are stripped); `folded`
additionally folds final letterforms to medial.
Run with the project venv: tf-venv/bin/python extract_dss.py
"""
import os
import sys

from tf.app import use

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   'worker-out', 'dss', 'dss_words.tsv')
BOOKMAP = {'Gen': 1, 'Ex': 2, 'Lev': 3, 'Num': 4, 'Deut': 5, 'Josh': 6,
           'Judg': 7, 'Ruth': 8, '1Sam': 9, '2Sam': 10, '1Kgs': 11,
           '2Kgs': 12, '1Chr': 13, '2Chr': 14, 'Ezra': 15, 'Neh': 16,
           'Esth': 17, 'Job': 18, 'Ps': 19, 'Prov': 20, 'Eccl': 21,
           'Song': 22, 'Is': 23, 'Jer': 24, 'Lam': 25, 'Ezek': 26,
           'Dan': 27, 'Hos': 28, 'Joel': 29, 'Amos': 30, 'Obad': 31,
           'Jonah': 32, 'Mic': 33, 'Nah': 34, 'Hab': 35, 'Zeph': 36,
           'Hag': 37, 'Zech': 38, 'Mal': 39}
FINALS = {'ך': 'כ', 'ם': 'מ', 'ן': 'נ', 'ף': 'פ', 'ץ': 'צ'}
BADFLAGS = ('rec', 'unc', 'rem', 'alt')


def fold(s):
    return ''.join(FINALS.get(c, c) for c in (s or ''))


def consonants(text):
    return ''.join(c for c in (text or '') if 'א' <= c <= 'ת')


def main():
    A = use('ETCBC/dss', silent=True)
    F, L = A.api.F, A.api.L
    cells = {}
    stats = {'cells_seen': 0, 'cells_qualified': 0, 'words_out': 0}
    for w in F.otype.s('word'):
        if F.biblical.v(w) not in (1, 2):
            continue
        bk = F.book.v(w)
        if bk not in BOOKMAP:
            continue
        ch, vs = str(F.chapter.v(w)), str(F.verse.v(w))
        if not (ch.isdigit() and vs.isdigit()):
            continue
        fr = L.u(w, otype='fragment')
        if not fr:
            continue
        sc = F.scroll.v(fr[0])
        key = (sc, BOOKMAP[bk], int(ch), int(vs))
        cell = cells.setdefault(key, {'words': [], 'ok': True})
        if F.halfverse.v(w):
            cell['ok'] = False
        if F.type.v(w) != 'glyph':
            continue
        if F.lang.v(w) == 'g' or F.script.v(w) == 'greekcapital':
            cell['ok'] = False
            continue
        glyph = F.glyph.v(w)
        attested = bool(glyph) and not any(
            getattr(F, f).v(s) for s in L.d(w, otype='sign')
            for f in BADFLAGS)
        if not attested:
            cell['ok'] = False
        cell['words'].append((glyph or '', F.after.v(w), attested))
    rows = []
    for (sc, b, c, v), cell in sorted(cells.items()):
        stats['cells_seen'] += 1
        if not cell['ok'] or not cell['words']:
            continue
        stats['cells_qualified'] += 1
        graphic, cur = [], ''
        for glyph, after, _att in cell['words']:
            cur += consonants(glyph)
            if after is not None:
                if cur:
                    graphic.append(cur)
                cur = ''
        if cur:
            graphic.append(cur)
        for pos, raw in enumerate(graphic, 1):
            if raw:
                rows.append((sc, b, c, v, pos, raw, fold(raw)))
                stats['words_out'] += 1
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write('scroll\tbook\tchapter\tverse\tpos\traw\tfolded\n')
        for r in rows:
            f.write('\t'.join(str(x) for x in r) + '\n')
    print(f"cells seen {stats['cells_seen']}; qualified "
          f"{stats['cells_qualified']}; graphic words {stats['words_out']}",
          file=sys.stderr)
    print('wrote', OUT, file=sys.stderr)


if __name__ == '__main__':
    main()
