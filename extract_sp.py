#!/usr/bin/env python3
"""Extract Samaritan Pentateuch graphic words from the DT-UCPH/sp
Text-Fabric dataset (v7.2.4) into a flat TSV:
  book_num, chapter, verse, word_pos, raw, folded

The dataset's word nodes are ANALYTIC (proclitics like ב, ה, ו are
separate nodes). Graphic (manuscript) words are rebuilt by joining
nodes while the ETCBC `trailer` feature is '' (no space follows);
a ' ' trailer ends the graphic word. (Dataset trailers are only ''
and ' ' — verified 2026-10-16; no maqqef trailer is encoded.)

Normalization (documented, consonants only):
- g_cons_utf8 uses presentation forms for shin/sin: U+FB2A (שׁ) and
  U+FB2B (שׂ) both map to ש (U+05E9) — consonantally identical.
- stray spaces inside a word's g_cons_utf8 (95 words) are removed.
- raw keeps final letterforms as attested; folded maps ךםןףץ -> כמנפצ
  (the corpus convention) for alignment keys.

Source of truth: sources/sp (staged copy of the TF download,
DT-UCPH/sp 7.2.4, Schorch editio maior, CC BY-NC 4.0). TF itself loads
from ~/text-fabric-data; the loader asserts the loaded version.
Run with the project venv: tf-venv/bin/python extract_sp.py
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                'tf-venv', 'lib'))
from tf.app import use  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   'worker-out', 'sp', 'sp_words.tsv')
BOOKMAP = {'Genesis': 1, 'Exodus': 2, 'Leviticus': 3, 'Numbers': 4,
           'Deuteronomy': 5}
FINALS = {'ך': 'כ', 'ם': 'מ', 'ן': 'נ', 'ף': 'פ', 'ץ': 'צ'}
EXPECTED_VERSION = '7.2.4'


def fold(s):
    return ''.join(FINALS.get(c, c) for c in (s or ''))


def norm(text):
    t = (text or '').replace(' ', '')
    t = t.replace('\ufb2a', 'ש').replace('\ufb2b', 'ש')
    return t


def main():
    A = use('DT-UCPH/sp', silent=True)
    api = A.api
    F, L = api.F, api.L
    prov = A.appProvenance() if hasattr(A, 'appProvenance') else {}
    version = None
    try:
        version = A.settings['version']
    except Exception:
        pass
    print('provenance:', prov, 'version:', version, file=sys.stderr)
    rows = []
    seen_keys = {}
    for vnode in F.otype.s('verse'):
        bnode = L.u(vnode, otype='book')[0]
        cnode = L.u(vnode, otype='chapter')[0]
        book = BOOKMAP[F.book.v(bnode)]
        ch = F.chapter.v(cnode)
        vs = F.verse.v(vnode)
        key = (book, ch, vs)
        seen_keys[key] = seen_keys.get(key, 0) + 1
        # graphic words: join analytic words while trailer == ''
        graphic = []
        cur = ''
        for w in L.d(vnode, otype='word'):
            cur += norm(F.g_cons_utf8.v(w))
            if F.trailer.v(w) != '':
                graphic.append(cur)
                cur = ''
        if cur:
            graphic.append(cur)
        for i, g in enumerate(graphic, 1):
            rows.append((book, ch, vs, i, g, fold(g)))
    dupes = {k: n for k, n in seen_keys.items() if n > 1}
    print(f'verses: {len(seen_keys)}, dup verse keys: {len(dupes)}, '
          f'graphic words: {len(rows)}', file=sys.stderr)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write('book_num\tchapter\tverse\tword_pos\traw\tfolded\n')
        for r in rows:
            f.write('\t'.join(str(x) for x in r) + '\n')
    print('wrote', OUT, file=sys.stderr)


if __name__ == '__main__':
    main()
