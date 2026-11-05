# YLT↔Hebrew alignment gold set (`ylt_gold.tsv`)

Hand-aligned evaluation set for U-1 (2026-09-24), expanded for YLT
alignment repair round 2 (2026-11-05). 42 verses, 438 Hebrew words, 991
expected `(word_id, ylt_word_pos)` pairs, validated against
`bible_v2.db` with 0 integrity errors (every row's verse, word_pos,
pointed form and Strong's match the DB; the 4 round-1 rows whose
Strong's was filled by the U-10 repair after the gold was written —
wids 116, 129, 206908, 206989 — had their `strongs` cells updated to
the current DB values; no `ylt_pos` changed):

- Genesis 1:1–12 — narrative
- Psalms 23:1–6 — poetry
- Isaiah 53:1–12 — prophecy
- Round-2 expansion (2026-11-05, 12 verses / 103 words / 221 pairs,
  8 further books): Exodus 20:2, 20:3, 3:14; Deuteronomy 6:4–5;
  Proverbs 3:5–6; Ecclesiastes 1:2; Song of Solomon 8:6; Amos 5:24;
  Habakkuk 2:4; Micah 6:8

Columns: `book, chapter, verse, word_id, word_pos, hebrew, strongs, ylt_pos, note`.
`ylt_pos` is a comma-separated list of 1-based YLT token positions, or empty
when the Hebrew word has no YLT token (4 such words in the set).

## Alignment policy (applied by hand, 2026-09-24)

1. A Hebrew word maps to the YLT token(s) that translate it.
2. English function words rendering Hebrew prefixes attach to that Hebrew
   word (e.g. the "in" of בראשׁית → בראשׁית).
3. H853 (את accusative marker) maps to nothing when untranslated.
4. Bracketed YLT editorial insertions (e.g. "[is]") are unmapped.
5. Construct-state "of" attaches to the genitive (following) word.
6. Unbracketed copulas ("is/are") attach to the predicate Hebrew word.
7. Restructured clauses map by sense, not by surface order.
8. Words YLT drops get an empty expected map, so any predicted token
   counts as a precision error.

## Scoring

`python3 build_ylt_align.py --eval` scores predicted
`(word_id, ylt_word_pos)` pairs against this set: precision = TP/predicted,
recall = TP/770. Predictions on the 4 empty-map words are false positives.
The H3068 (divine-name) words in the set are additionally checked for
drift: any predicted YLT token outside the gold map is a drift error.

Status note: this gold set measures the COMPUTED alignment only. The
alignment remains best-effort and NOT authoritative (NOTATION_LEDGER U-1).

## Measured results (2026-09-24, `build_ylt_align.py --eval`)

| method | precision | recall | predicted pairs | true positives |
|---|---|---|---|---|
| baseline | 0.6911 | 0.4766 | 531 | 367 |
| **anchored** (winner) | **0.7941** | 0.4506 | 437 | 347 |
| propagated | 0.7941 | 0.4506 | 437 | 347 |

The propagated variant produced zero propagated predictions on this set
(and zero propagated rows on the full 23,006-verse corpus), so the shipped
table is the anchored bridge. H3068 divine-name check: 0 drift pairs under
the anchored bridge (baseline: 1 wrong YLT token attached to an H3068 word);
H3068 misses remain — recall gaps, not mis-maps.

## Measured results (2026-11-05, expanded gold, SHIPPED `ylt_renderings`)

The shipped table (anchored bridge + round-1 grammar repair) scored on
this expanded set: precision 0.7873 (tp 507 / pred 644), recall 0.5116
(507 / 991), H3068 drift 0 (12 H3068 words in the set). On the round-1
30-verse subset it reproduces the recorded operating point exactly:
precision 0.7984 / recall 0.5039. The recomputed bridge methods
(`build_ylt_align.py --eval` on the expanded set) score lower, as
expected — they do not include the grammar repair: baseline 0.6689 /
0.4955, anchored 0.7810 / 0.4642, propagated 0.7810 / 0.4642. Round-2
span-boundary prototype results are recorded in `NOTATION_LEDGER.md`
§10 (YLT-REPAIR-R2).
