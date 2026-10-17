#!/usr/bin/env python3
"""Load Samaritan Pentateuch variants (witness='SP') into word_variants.

Kit 2026-10-14: full traditions campaign, leg 2 (Samaritan). Source:
DT-UCPH/sp Text-Fabric 7.2.4 — the Samaritan Pentateuch in Stefan
Schorch's editio maior transcription (MS Dublin Chester Beatty 751,
Gen 1-Deut 32:36; MS Garizim 1, Deut 32:36b-end), CC BY-NC 4.0,
staged under sources/sp. Torah only, as the SP itself is.

Input is the graphic-word extraction (worker-out/sp/sp_words.tsv,
built by extract_sp.py): the dataset's analytic word nodes are joined
into manuscript graphic words on the ETCBC trailer feature, shin/sin
presentation forms normalized to ש, final forms preserved in `raw`,
folded in `folded`.

Alignment is per verse against the MT corpus (words table, books 1-5),
on folded consonant skeletons ('-' maqqef joins removed), via
difflib.SequenceMatcher. Rules (fixed from measured dry runs,
2026-10-16; pass1/pass2 reports in worker-out/sp/):
  equal            -> no row, EXCEPT pairs whose RAW forms differ
                      while the folded forms match (final-form-only
                      readings): Kit ruled 2026-10-17 that these are
                      MARKED as 'orthographic' rows carrying the
                      FF_SUFFIX basis flag (they were dropped under
                      the sofit-fold rule in the first build; 2 such
                      pairs in the Torah: Gen 19:38, Gen 35:18). The
                      same marking applies to final-form-only diffs
                      found inside equal-length replace pairs, paired
                      remainders of complex blocks, and word-division
                      blocks whose joined raw consonants differ.
  replace, equal length -> per-word substitution rows.
  insert           -> one 'addition' row on the preceding MT word
                      (first MT word if verse-initial).
  delete           -> one 'omission' row per MT word.
  replace, unequal length:
    joined folded equal        -> word-division only, no row.
    joined matres-stripped equal -> one 'orthographic' block row on
                      the block's first MT word.
    else -> fragment-merge pass (concatenations of 2-3 words on
      either side that exactly equal one word on the other side are
      word-division matches, no rows), then greedy best-ratio pairing
      (ratio >= 0.6) -> substitution rows; leftover MT words ->
      omission rows; leftover SP words -> one addition row on the
      block's first MT word. If nothing pairs and both sides have
      leftovers -> one 'substantive' block row over the leftovers.

Classification of a substitution: folded skeletons differing only by
matres lectionis (אהוי insertion/deletion, i.e. equal after stripping
אהוי from both) = 'orthographic' (plene/defective spelling); anything
else = 'substantive'.

Known source facts the counts must show (not special-cased):
- SP places the incense-altar pericope (MT Exod 30:1-10) after
  Exod 26:35; the dataset groups it into the Exod 26:35 verse node, so
  MT Exod 30:1-10 have no same-reference SP counterpart (counted as
  mt_verse_no_sp) and Exod 26:35 yields one large addition row.
- Dataset additions after Gen 30:36 are grouped under verse 36
  (not 36a/36b/36c) -> they surface as additions in Gen 30:36.
- Deut 34:2-3 have no SP verse node in this dataset (counted).

variant_text = SP reading as attested (consonants, final forms kept;
the dataset carries no Samaritan vocalization). unpointed/letters =
folded consonants (corpus convention). Omissions: variant_text NULL,
unpointed/letters ''.

Idempotent: existing variant_kind='textual' AND witness='SP' rows are
deleted first. Supports --dry-run (full accounting, no writes).
"""
import collections
import difflib
import json
import os
import sqlite3
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
TSV = os.path.join(BASE, 'worker-out', 'sp', 'sp_words.tsv')
DRY = '--dry-run' in sys.argv
_args = [a for a in sys.argv[1:] if not a.startswith('--')]
DB = _args[0] if _args else os.path.join(BASE, 'bible_v2.db')
FINALS = {'ך': 'כ', 'ם': 'מ', 'ן': 'נ', 'ף': 'פ', 'ץ': 'צ'}
MATRES = set('אהוי')
BASIS = ('Samaritan Pentateuch (Schorch editio maior), DT-UCPH/sp '
         'Text-Fabric 7.2.4, CC BY-NC 4.0; per-verse consonantal '
         'alignment vs MT (WLC); matres-only difference = orthographic')
# Kit ruling 2026-10-17: final-form-only readings (consonants identical
# once finals fold, differing only in medial/final letterform placement)
# are MARKED as tradition-labeled rows, not dropped.
FF_SUFFIX = ('; final-form-only difference: consonants differ solely in '
             'medial/final letterform placement (e.g. \u05df vs \u05e0), '
             'identical once finals are folded; marked as a '
             'tradition-labeled row per Kit ruling 2026-10-17 (earlier '
             'builds dropped these under the fold rule)')


def fold(s):
    return ''.join(FINALS.get(c, c) for c in (s or ''))


def consonants(text):
    return ''.join(c for c in (text or '') if 'א' <= c <= 'ת')


def strip_matres(s):
    return ''.join(c for c in s if c not in MATRES)


def classify(a, b):
    if a == b:
        return None
    return 'orthographic' if strip_matres(a) == strip_matres(b) \
        else 'substantive'


def load_sp():
    sp = collections.defaultdict(list)
    with open(TSV, encoding='utf-8') as f:
        next(f)
        for line in f:
            b, c, v, pos, raw, folded = line.rstrip('\n').split('\t')
            sp[(int(b), int(c), int(v))].append((raw, folded))
    return sp


def fragment_merge(mt_seg, sp_seg):
    """Two-pointer scan consuming exact concatenation matches
    (word-division fragments). Returns (mt_rest_idx, sp_rest_idx,
    n_merges) as index lists into the segments, order preserved."""
    i = j = 0
    merges = 0
    consumed_i, consumed_j = set(), set()
    while i < len(mt_seg) and j < len(sp_seg):
        if mt_seg[i] == sp_seg[j]:
            consumed_i.add(i); consumed_j.add(j)
            i += 1; j += 1
            merges += 1
            continue
        hit = False
        for n in (2, 3):
            if j + n <= len(sp_seg) and \
                    ''.join(sp_seg[j:j + n]) == mt_seg[i]:
                consumed_i.add(i)
                consumed_j.update(range(j, j + n))
                i += 1; j += n; merges += 1; hit = True
                break
            if i + n <= len(mt_seg) and \
                    ''.join(mt_seg[i:i + n]) == sp_seg[j]:
                consumed_j.add(j)
                consumed_i.update(range(i, i + n))
                j += 1; i += n; merges += 1; hit = True
                break
        if not hit:
            break
    mt_rest = [k for k in range(len(mt_seg)) if k not in consumed_i]
    sp_rest = [k for k in range(len(sp_seg)) if k not in consumed_j]
    return mt_rest, sp_rest, merges


def main():
    sp = load_sp()
    db = sqlite3.connect(DB)
    db.row_factory = sqlite3.Row
    st = collections.Counter()
    st['sp_verses'] = len(sp)
    st['sp_words'] = sum(len(v) for v in sp.values())
    rows = []  # (word_id, unpointed, letters, variant_text, type, basis)

    def emit(wid, sp_raw_list, vtype, suffix=''):
        folded_joined = ' '.join(fold(x) for x in sp_raw_list)
        rows.append((wid, folded_joined, folded_joined,
                     ' '.join(sp_raw_list), vtype, BASIS + suffix))

    def emit_omission(wid):
        rows.append((wid, '', '', None, 'omission', BASIS))

    for vr in db.execute(
            'SELECT verse_id, book_id, chapter, verse FROM verses '
            'WHERE book_id<=5 ORDER BY book_id, chapter, verse').fetchall():
        key = (vr['book_id'], vr['chapter'], vr['verse'])
        cwords = db.execute(
            'SELECT word_id, word_pos, pointed, unpointed FROM words '
            'WHERE verse_id=? ORDER BY word_pos',
            (vr['verse_id'],)).fetchall()
        if key not in sp:
            if cwords:
                st['mt_verse_no_sp'] += 1
                st[f"mt_verse_no_sp_list"] = \
                    st.get('mt_verse_no_sp_list', [])
                st['mt_verse_no_sp_list'].append(
                    f"{key[0]}.{key[1]}.{key[2]}")
            continue
        if not cwords:
            st['corpus_verse_empty'] += 1
            continue
        st['verses_aligned'] += 1
        mt_key, mt_raw = [], []
        for c in cwords:
            if c['unpointed']:
                mt_key.append(fold(c['unpointed']).replace('-', ''))
            else:
                st['mt_unpointed_null_fallback'] += 1
                mt_key.append(fold(consonants(c['pointed'])))
            mt_raw.append(consonants(c['pointed']))
        spt = sp[key]
        sp_key = [folded for _, folded in spt]
        sm = difflib.SequenceMatcher(a=mt_key, b=sp_key, autojunk=False)
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag == 'equal':
                for k in range(i2 - i1):
                    if mt_raw[i1 + k] != spt[j1 + k][0] and \
                            fold(mt_raw[i1 + k]) == fold(spt[j1 + k][0]):
                        st['final_form_marked'] += 1
                        emit(cwords[i1 + k]['word_id'],
                             [spt[j1 + k][0]], 'orthographic', FF_SUFFIX)
                    else:
                        st['pair_equal'] += 1
            elif tag == 'replace' and (i2 - i1) == (j2 - j1):
                for k in range(i2 - i1):
                    cls = classify(mt_key[i1 + k], sp_key[j1 + k])
                    if cls:
                        st['sub_' + cls] += 1
                        emit(cwords[i1 + k]['word_id'],
                             [spt[j1 + k][0]], cls)
                    elif mt_raw[i1 + k] != spt[j1 + k][0]:
                        st['final_form_marked'] += 1
                        emit(cwords[i1 + k]['word_id'],
                             [spt[j1 + k][0]], 'orthographic', FF_SUFFIX)
                    else:
                        st['pair_equal'] += 1
            elif tag == 'insert':
                anchor = cwords[i1 - 1] if i1 > 0 else cwords[0]
                st['addition_rows'] += 1
                st['addition_words'] += (j2 - j1)
                emit(anchor['word_id'], [r for r, _ in spt[j1:j2]],
                     'addition',
                     '; verse-initial addition' if i1 == 0 else '')
            elif tag == 'delete':
                for k in range(i1, i2):
                    st['omission_rows'] += 1
                    emit_omission(cwords[k]['word_id'])
            else:  # replace, unequal length
                mt_seg = mt_key[i1:i2]
                sp_seg = sp_key[j1:j2]
                if ''.join(mt_seg) == ''.join(sp_seg):
                    mr_join = ''.join(mt_raw[i1:i2])
                    sr_join = ''.join(r for r, _ in spt[j1:j2])
                    ff_ok = len(mr_join) == len(sr_join) and all(
                        FINALS.get(a, a) == FINALS.get(b, b)
                        and (a in FINALS or b in FINALS)
                        for a, b in zip(mr_join, sr_join)
                        if a != b)
                    if mr_join != sr_join and ff_ok:
                        st['final_form_block_rows'] += 1
                        emit(cwords[i1]['word_id'],
                             [r for r, _ in spt[j1:j2]], 'orthographic',
                             FF_SUFFIX + f'; word-division block '
                             f'({len(mt_seg)} MT words vs {len(sp_seg)} '
                             f'SP graphic words; letters identical once '
                             f'finals fold)')
                    elif mr_join != sr_join:
                        # raw joins differ but NOT solely by final-form
                        # placement — not markable; count for audit
                        st['ff_block_rejected'] += 1
                        st['division_only_blocks'] += 1
                    else:
                        st['division_only_blocks'] += 1
                    continue
                if strip_matres(''.join(mt_seg)) == \
                        strip_matres(''.join(sp_seg)):
                    st['block_orthographic_rows'] += 1
                    emit(cwords[i1]['word_id'],
                         [r for r, _ in spt[j1:j2]], 'orthographic',
                         f'; block alignment ({len(mt_seg)} MT words vs '
                         f'{len(sp_seg)} SP graphic words: word division '
                         f'+ spelling)')
                    continue
                mt_rest, sp_rest, merges = fragment_merge(mt_seg, sp_seg)
                st['fragment_merges'] += merges
                # greedy best-ratio pairing on the remainders
                cand = []
                for a in mt_rest:
                    for b in sp_rest:
                        r = difflib.SequenceMatcher(
                            None, mt_seg[a], sp_seg[b]).ratio()
                        if r >= 0.6:
                            cand.append((-r, a, b))
                cand.sort()
                used_a, used_b, pairs = set(), set(), []
                for _, a, b in cand:
                    if a not in used_a and b not in used_b:
                        used_a.add(a); used_b.add(b); pairs.append((a, b))
                left_mt = [a for a in mt_rest if a not in used_a]
                left_sp = [b for b in sp_rest if b not in used_b]
                if pairs:
                    st['complex_blocks_paired'] += 1
                    for a, b in pairs:
                        cls = classify(mt_seg[a], sp_seg[b])
                        if cls:
                            st['sub_' + cls] += 1
                            emit(cwords[i1 + a]['word_id'],
                                 [spt[j1 + b][0]], cls)
                        elif mt_raw[i1 + a] != spt[j1 + b][0]:
                            st['final_form_marked'] += 1
                            emit(cwords[i1 + a]['word_id'],
                                 [spt[j1 + b][0]], 'orthographic',
                                 FF_SUFFIX)
                        else:
                            st['pair_equal'] += 1
                    for a in left_mt:
                        st['omission_rows'] += 1
                        emit_omission(cwords[i1 + a]['word_id'])
                    if left_sp:
                        st['addition_rows'] += 1
                        st['addition_words'] += len(left_sp)
                        emit(cwords[i1]['word_id'],
                             [spt[j1 + b][0] for b in left_sp], 'addition',
                             '; within a mixed-alignment block')
                elif left_mt and left_sp:
                    st['block_substantive_rows'] += 1
                    emit(cwords[i1 + left_mt[0]]['word_id'],
                         [spt[j1 + b][0] for b in left_sp], 'substantive',
                         f'; block alignment ({len(mt_seg)} MT words vs '
                         f'{len(sp_seg)} SP graphic words: no word-level '
                         f'pairing >= 0.6)')
                else:
                    for a in left_mt:
                        st['omission_rows'] += 1
                        emit_omission(cwords[i1 + a]['word_id'])
                    if left_sp:
                        st['addition_rows'] += 1
                        st['addition_words'] += len(left_sp)
                        emit(cwords[i1]['word_id'],
                             [spt[j1 + b][0] for b in left_sp], 'addition')
    st['rows_total'] = len(rows)
    out = {k: v for k, v in st.items() if k != 'mt_verse_no_sp_list'}
    out['mt_verse_no_sp_list'] = st.get('mt_verse_no_sp_list', [])
    if DRY:
        print(json.dumps(out, indent=1, ensure_ascii=False))
        print('DRY RUN — no writes')
        return
    db.execute("DELETE FROM word_variants WHERE variant_kind='textual' "
               "AND witness='SP'")
    seq_cache = {}
    for wid, unp, letters, vtext, vtype, basis in rows:
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
             'SP', vtype, basis))
    db.commit()
    out['inserted'] = db.execute(
        "SELECT COUNT(*) c FROM word_variants WHERE variant_kind='textual' "
        "AND witness='SP'").fetchone()['c']
    print(json.dumps(out, indent=1, ensure_ascii=False))


if __name__ == '__main__':
    main()
