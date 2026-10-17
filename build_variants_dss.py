#!/usr/bin/env python3
"""Load Dead Sea Scrolls variants into word_variants (witness = the
scroll's siglum, e.g. '1Qisaa', '11Q5', '4Q51').

Kit 2026-10-17: variants campaign leg 5 (DSS), scope = FULLY ATTESTED
VERSES ONLY (Kit picked the recommended option). Source: ETCBC/dss
Text-Fabric 2.0.1 — Abegg's scroll transcriptions (CACCHT), dataset
CC BY-NC 4.0, staged under sources/dss. Input: worker-out/dss/
dss_words.tsv (extract_dss.py), which contains ONLY fully attested
verses: every letter physically present on the parchment — no
reconstructed (rec), uncertain (unc), removed (rem), or alternative
(alt) signs anywhere in the verse, no halfverse splits, no Greek
words. Partial verses are counted in the research doc, never loaded
here; their attested share (median 22%) is too low for trustworthy
alignment.

Alignment is per (scroll, verse) against the MT corpus, using the
Samaritan leg's engine unchanged (folded consonant skeletons,
difflib per-verse alignment, identical block rules, matres-only =
'orthographic', else 'substantive'; helpers imported from
build_variants_sp). Kit's 2026-10-17 final-form marking rule applies
identically (FF_SUFFIX rows). Tripwire: a cell whose DSS word count
exceeds 2.2x the MT verse's word count is skipped and counted
(suspect double attestation of one verse inside a single scroll,
e.g. a psalm copied twice in 11Q5) rather than aligned as one
sequence.

basis (per row): 'Dead Sea Scrolls, <siglum> (Abegg transcription),
ETCBC/dss Text-Fabric 2.0.1, CC BY-NC 4.0; fully attested verse only
(no reconstructed/uncertain letters); per-verse consonantal alignment
vs MT (WLC); matres-only difference = orthographic' (+ FF_SUFFIX
where applicable). variant_text = the scroll's reading as attested
(consonants, final forms kept; Qumran scribes also write medial
forms finally — the fold, not the data, absorbs that).

Idempotent: existing DSS rows (identified by the basis prefix) are
deleted first. Supports --dry-run (full accounting, no writes).
"""
import collections
import difflib
import json
import os
import sqlite3
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_variants_sp import FF_SUFFIX, classify, consonants, fold, \
    fragment_merge  # noqa: E402

BASE = os.path.dirname(os.path.abspath(__file__))
TSV = os.path.join(BASE, 'worker-out', 'dss', 'dss_words.tsv')
DRY = '--dry-run' in sys.argv
_args = [a for a in sys.argv[1:] if not a.startswith('--')]
DB = _args[0] if _args else os.path.join(BASE, 'bible_v2.db')
BASIS_T = ('Dead Sea Scrolls, {sig} (Abegg transcription), ETCBC/dss '
           'Text-Fabric 2.0.1, CC BY-NC 4.0; fully attested verse only '
           '(no reconstructed/uncertain letters); per-verse '
           'consonantal alignment vs MT (WLC); matres-only difference '
           '= orthographic')


def load_dss():
    cells = collections.defaultdict(list)
    with open(TSV, encoding='utf-8') as f:
        next(f)
        for line in f:
            sc, b, c, v, pos, raw, folded = line.rstrip('\n').split('\t')
            cells[(sc, int(b), int(c), int(v))].append((raw, folded))
    return cells


def main():
    cells = load_dss()
    db = sqlite3.connect(DB)
    db.row_factory = sqlite3.Row
    st = collections.Counter()
    st['dss_cells'] = len(cells)
    rows = []  # (word_id, folded, folded, raw_text, type, basis, witness)

    def emit(wid, raw_list, vtype, basis, witness, suffix=''):
        folded_joined = ' '.join(fold(x) for x in raw_list)
        rows.append((wid, folded_joined, folded_joined,
                     ' '.join(raw_list), vtype, basis + suffix, witness))

    def emit_omission(wid, basis, witness):
        rows.append((wid, '', '', None, 'omission', basis, witness))

    verses_cache = {}
    for (sig, b, c, v), swords in sorted(cells.items()):
        basis = BASIS_T.format(sig=sig)
        vr = db.execute(
            'SELECT verse_id FROM verses WHERE book_id=? AND chapter=? '
            'AND verse=?', (b, c, v)).fetchone()
        if vr is None:
            st['cell_no_corpus_verse'] += 1
            continue
        vid = vr['verse_id']
        if vid not in verses_cache:
            verses_cache[vid] = db.execute(
                'SELECT word_id, word_pos, pointed, unpointed FROM words '
                'WHERE verse_id=? ORDER BY word_pos', (vid,)).fetchall()
        cwords = verses_cache[vid]
        if not cwords:
            st['corpus_verse_empty'] += 1
            continue
        if len(swords) > 2.2 * len(cwords):
            st['suspect_double_attestation'] += 1
            st.setdefault('suspect_list', []).append(
                f'{sig} {b}.{c}.{v} dss={len(swords)} mt={len(cwords)}')
            continue
        st['verses_aligned'] += 1
        st['scrolls_aligned_' + sig] += 1
        mt_key, mt_raw = [], []
        for cw in cwords:
            if cw['unpointed']:
                mt_key.append(fold(cw['unpointed']).replace('-', ''))
            else:
                mt_key.append(fold(consonants(cw['pointed'])))
            mt_raw.append(consonants(cw['pointed']))
        dss_key = [folded for _, folded in swords]
        sm = difflib.SequenceMatcher(a=mt_key, b=dss_key, autojunk=False)
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag == 'equal':
                for k in range(i2 - i1):
                    if mt_raw[i1 + k] != swords[j1 + k][0] and \
                            fold(mt_raw[i1 + k]) == fold(swords[j1 + k][0]):
                        st['final_form_marked'] += 1
                        emit(cwords[i1 + k]['word_id'],
                             [swords[j1 + k][0]], 'orthographic', basis,
                             sig, FF_SUFFIX)
                    else:
                        st['pair_equal'] += 1
            elif tag == 'replace' and (i2 - i1) == (j2 - j1):
                for k in range(i2 - i1):
                    cls = classify(mt_key[i1 + k], dss_key[j1 + k])
                    if cls:
                        st['sub_' + cls] += 1
                        emit(cwords[i1 + k]['word_id'],
                             [swords[j1 + k][0]], cls, basis, sig)
                    elif mt_raw[i1 + k] != swords[j1 + k][0]:
                        st['final_form_marked'] += 1
                        emit(cwords[i1 + k]['word_id'],
                             [swords[j1 + k][0]], 'orthographic', basis,
                             sig, FF_SUFFIX)
                    else:
                        st['pair_equal'] += 1
            elif tag == 'insert':
                anchor = cwords[i1 - 1] if i1 > 0 else cwords[0]
                st['addition_rows'] += 1
                st['addition_words'] += (j2 - j1)
                emit(anchor['word_id'], [r for r, _ in swords[j1:j2]],
                     'addition', basis, sig,
                     '; verse-initial addition' if i1 == 0 else '')
            elif tag == 'delete':
                for k in range(i1, i2):
                    st['omission_rows'] += 1
                    emit_omission(cwords[k]['word_id'], basis, sig)
            else:  # replace, unequal length
                mt_seg = mt_key[i1:i2]
                dss_seg = dss_key[j1:j2]
                if ''.join(mt_seg) == ''.join(dss_seg):
                    mr_join = ''.join(mt_raw[i1:i2])
                    sr_join = ''.join(r for r, _ in swords[j1:j2])
                    ff_ok = len(mr_join) == len(sr_join) and all(
                        fold(a) == fold(b) and (a in 'ךםןףץ' or b in 'ךםןףץ')
                        for a, b in zip(mr_join, sr_join) if a != b)
                    if mr_join != sr_join and ff_ok:
                        st['final_form_block_rows'] += 1
                        emit(cwords[i1]['word_id'],
                             [r for r, _ in swords[j1:j2]], 'orthographic',
                             basis, sig, FF_SUFFIX +
                             f'; word-division block ({len(mt_seg)} MT '
                             f'words vs {len(dss_seg)} DSS graphic words; '
                             f'letters identical once finals fold)')
                    else:
                        st['division_only_blocks'] += 1
                    continue
                if ''.join(c for c in ''.join(mt_seg)
                           if c not in 'אהוי') == \
                        ''.join(c for c in ''.join(dss_seg)
                                if c not in 'אהוי'):
                    st['block_orthographic_rows'] += 1
                    emit(cwords[i1]['word_id'],
                         [r for r, _ in swords[j1:j2]], 'orthographic',
                         basis, sig,
                         f'; block alignment ({len(mt_seg)} MT words vs '
                         f'{len(dss_seg)} DSS graphic words: word '
                         f'division + spelling)')
                    continue
                mt_rest, dss_rest, merges = fragment_merge(mt_seg, dss_seg)
                st['fragment_merges'] += merges
                cand = []
                for a in mt_rest:
                    for bb in dss_rest:
                        r = difflib.SequenceMatcher(
                            None, mt_seg[a], dss_seg[bb]).ratio()
                        if r >= 0.6:
                            cand.append((-r, a, bb))
                cand.sort()
                used_a, used_b, pairs = set(), set(), []
                for _, a, bb in cand:
                    if a not in used_a and bb not in used_b:
                        used_a.add(a)
                        used_b.add(bb)
                        pairs.append((a, bb))
                left_mt = [a for a in mt_rest if a not in used_a]
                left_dss = [bb for bb in dss_rest if bb not in used_b]
                if pairs:
                    st['complex_blocks_paired'] += 1
                    for a, bb in pairs:
                        cls = classify(mt_seg[a], dss_seg[bb])
                        if cls:
                            st['sub_' + cls] += 1
                            emit(cwords[i1 + a]['word_id'],
                                 [swords[j1 + bb][0]], cls, basis, sig)
                        elif mt_raw[i1 + a] != swords[j1 + bb][0]:
                            st['final_form_marked'] += 1
                            emit(cwords[i1 + a]['word_id'],
                                 [swords[j1 + bb][0]], 'orthographic',
                                 basis, sig, FF_SUFFIX)
                        else:
                            st['pair_equal'] += 1
                    for a in left_mt:
                        st['omission_rows'] += 1
                        emit_omission(cwords[i1 + a]['word_id'], basis, sig)
                    if left_dss:
                        st['addition_rows'] += 1
                        st['addition_words'] += len(left_dss)
                        emit(cwords[i1]['word_id'],
                             [swords[j1 + bb][0] for bb in left_dss],
                             'addition', basis, sig,
                             '; within a mixed-alignment block')
                elif left_mt and left_dss:
                    st['block_substantive_rows'] += 1
                    emit(cwords[i1 + left_mt[0]]['word_id'],
                         [swords[j1 + bb][0] for bb in left_dss],
                         'substantive', basis, sig,
                         f'; block alignment ({len(mt_seg)} MT words vs '
                         f'{len(dss_seg)} DSS graphic words: no '
                         f'word-level pairing >= 0.6)')
                else:
                    for a in left_mt:
                        st['omission_rows'] += 1
                        emit_omission(cwords[i1 + a]['word_id'], basis, sig)
                    if left_dss:
                        st['addition_rows'] += 1
                        st['addition_words'] += len(left_dss)
                        emit(cwords[i1]['word_id'],
                             [swords[j1 + bb][0] for bb in left_dss],
                             'addition', basis, sig)
    st['rows_total'] = len(rows)
    per_scroll = collections.Counter(r[6] for r in rows)
    out = {k: v for k, v in st.items()
           if not k.startswith('scrolls_aligned_')
           and k != 'suspect_list'}
    out['suspect_list'] = st.get('suspect_list', [])
    out['rows_by_scroll'] = dict(per_scroll.most_common())
    if DRY:
        print(json.dumps(out, indent=1, ensure_ascii=False))
        print('DRY RUN — no writes')
        return
    db.execute("DELETE FROM word_variants WHERE variant_kind='textual' "
               "AND basis LIKE 'Dead Sea Scrolls%'")
    seq_cache = {}
    for wid, unp, letters, vtext, vtype, basis, witness in rows:
        if wid not in seq_cache:
            r = db.execute('SELECT COALESCE(MAX(variant_seq),0) m FROM '
                           'word_variants WHERE word_id=?',
                           (wid,)).fetchone()
            seq_cache[wid] = r['m']
        seq_cache[wid] += 1
        db.execute(
            'INSERT INTO word_variants (word_id, variant_seq, variant_kind,'
            ' unpointed, letters, variant_text, convention, source,'
            ' witness, variant_type, basis) VALUES (?,?,?, ?,?,?, NULL,'
            ' NULL, ?,?, ?)',
            (wid, seq_cache[wid], 'textual', unp, letters, vtext,
             witness, vtype, basis))
    db.commit()
    out['inserted'] = db.execute(
        "SELECT COUNT(*) c FROM word_variants WHERE variant_kind='textual' "
        "AND basis LIKE 'Dead Sea Scrolls%'").fetchone()['c']
    print(json.dumps(out, indent=1, ensure_ascii=False))


if __name__ == '__main__':
    main()
