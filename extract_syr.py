#!/usr/bin/env python3
"""Extract Peshitta (Syriac) verses from the staged ETCBC/peshitta
Text-Fabric dataset (v0.5, TF data 0.2; text CC BY-NC 4.0) into
worker-out/peshitta/syr_verses.tsv:
  book_num, book_code, chapter, verse, n_words, text_syr, text_translit

book_num is the corpus (MT canon) number 1-39 for the 39 shared books,
0 for Apocrypha/other units (no MT counterpart; extracted for the
coverage audit, never joined). Graphic words are rebuilt from the
analytic word nodes on the ETCBC trailer feature ('' joins, anything
else ends the word — same convention as extract_sp.py).
Run with the project venv: tf-venv/bin/python extract_syr.py
"""
import os
import sys

from tf.app import use

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   'worker-out', 'peshitta', 'syr_verses.tsv')
# Syriac book code -> corpus book_id (MT canon order). Absent = no MT
# counterpart (Apocrypha / deuterocanonical units of the Peshitta).
BOOKMAP = {'Gn': 1, 'Ex': 2, 'Lv': 3, 'Nm': 4, 'Dt': 5, 'Jos': 6,
           'Jd': 7, 'Ru': 8, 'Sm1': 9, 'Sm2': 10, 'Rg1': 11, 'Rg2': 12,
           'Chr1': 13, 'Chr2': 14, 'Ezr': 15, 'Neh': 16, 'Est': 17,
           'Jb': 18, 'Ps': 19, 'Pr': 20, 'Ec': 21, 'Ct': 22, 'Is': 23,
           'Jr': 24, 'Thr': 25, 'Ez': 26, 'Dn': 27, 'Hs': 28, 'Jl': 29,
           'Am': 30, 'Ob': 31, 'Jon': 32, 'Mi': 33, 'Na': 34, 'Hb': 35,
           'Zf': 36, 'Hg': 37, 'Sa': 38, 'Ml': 39}


def main():
    A = use('ETCBC/peshitta', silent=True)
    F, L = A.api.F, A.api.L
    rows = []
    for vnode in F.otype.s('verse'):
        bnode = L.u(vnode, otype='book')[0]
        cnode = L.u(vnode, otype='chapter')[0]
        code = F.book.v(bnode)
        bnum = BOOKMAP.get(code, 0)
        ch = F.chapter.v(cnode)
        vs = F.verse.v(vnode)
        syr_words, tr_words = [], []
        cur_s, cur_t = '', ''
        for w in L.d(vnode, otype='word'):
            cur_s += F.word.v(w) or ''
            cur_t += F.word_etcbc.v(w) or ''
            if F.trailer.v(w) != '':
                syr_words.append(cur_s)
                tr_words.append(cur_t)
                cur_s, cur_t = '', ''
        if cur_s:
            syr_words.append(cur_s)
            tr_words.append(cur_t)
        rows.append((bnum, code, ch, vs, len(syr_words),
                     ' '.join(syr_words), ' '.join(tr_words)))
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write('book_num\tbook_code\tchapter\tverse\tn_words\t'
                'text_syr\ttext_translit\n')
        for r in rows:
            f.write('\t'.join(str(x) for x in r) + '\n')
    canon = [r for r in rows if r[0] > 0]
    print(f'verses total {len(rows)}; canon-39 verses {len(canon)}; '
          f'canon words {sum(r[4] for r in canon)}', file=sys.stderr)
    print('wrote', OUT, file=sys.stderr)


if __name__ == '__main__':
    main()
