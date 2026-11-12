# Robinson Variant-Aware Greek Bridge Rebuild — Isolated Test

**Date:** 2026-11-06  
**Status:** Isolated rebuild validated for source-resolved verses. **Not approved for production.**

## 1. Scope and safety

The rebuild was performed only in the isolated PostgreSQL database `bible_greek_bridge_test_20261106`, cloned from the verified restore database `bible_restore_verify_20261106`.

All generated objects are in the new `variant_rebuild_test` schema:
- `robinson_source_text`
- `variant_groups`
- `gnt_words`
- `gnt_alignment`
- `gnt_ylt_renderings`
- `validation_issues`
- `run_metadata`

No production database rows, source files, API code, PWA code, or embedding vectors were changed. The live database and the test database retain the same public-table counts:
- `ylt_verses`: 31,102
- `ylt_verses_embedding_store`: 31,102
- `gnt_words`: 141,009
- `gnt_alignment`: 202,901
- `gnt_ylt_renderings`: 143,227

The existing `bible_ylt_verses` vectorizer configuration fingerprint is identical in the live, restore, and test databases (SHA-256 of the one-row config list: `6f0e77ba7d64e6de7c0cfabeca95af810aedac125b27540e2d459d56780ffa5d`). The embedding store still contains 31,102 non-null vectors of 768 dimensions; vectorizer status is `pending_items=0`, `disabled=false`. No embedding generation was run.

## 2. Source and parser provenance

Pinned source revisions used:

| Source | Revision |
|---|---|
| Robinson parsed Textus Receptus | `byztxt/greektext-textus-receptus` — `7fd4d02c3e5adebd379ebfbc824040820dde10fc` |
| Upstream Robinson parser | `byztxt/librobinson` — `9acac9fbea409a767e020ff7e39018e43b0f6470` |
| CrossWire KJV 3.1 OSIS source | `crosswire-bible-society/kjv` — `d490be7e34762deb2c76cb2c1306d4808e27890d` |

The upstream `librobinson` parser explicitly handles pipe-delimited first/second readings and normalizes three special variant encodings before word parsing. The current Bible project `build_nt.py` parser extracts word/Strong's/morphology records but does not preserve this variant state; it effectively flattens alternatives. That is the parser-level cause of the positional drift.

The CrossWire KJV 3.1 source supplies the independent mapping fields used for this bridge test: `src` Greek positions, `lemma.TR` forms, Strong's identifiers, and Robinson morphology. The selection objective was deterministic: maximize exact lemma/Strong's/morphology agreement and in-range source positions. A tied result is unresolved; it is not broken by a language model or an arbitrary default.

## 3. Variant inventory and decisions

- **261** pipe-delimited variant groups identified across the 27 NT books.
- These form **245** connected decision components.
- **228** components had a unique source-supported combination.
- **17** components tied and remain unresolved.
- At the individual-group level, **242 groups were resolved** and **19 groups remain unresolved**, affecting **17 verse references**.
- Both alternatives for every group are preserved in `variant_groups`; unresolved verses are flagged and excluded from the rebuilt active bridge.

Unresolved references:

- John 8:6
- Acts 3:3
- Romans 16:27
- 1 Corinthians 16:24
- 2 Corinthians 13:14
- Galatians 6:18
- Ephesians 6:24
- Philippians 4:23
- 1 Thessalonians 5:28
- 2 Thessalonians 3:18
- 1 Timothy 6:21
- 2 Timothy 4:22
- Titus 3:15
- Philemon 1:25
- Hebrews 13:25
- 1 John 2:23
- Revelation 7:3

A significant cross-verse group spans Colossians 4:10–18. The source evidence uniquely selected its first alternative together with the associated group choice: **151/151** available source checks agreed. This is why a per-group parser is necessary; choosing all first or all second readings globally was materially worse.

## 4. KJV source-text verification

The KJV 3.1 OSIS source was compared against the existing PostgreSQL `kjv_words` corpus using the same tokenization conventions as the bridge builder.

- 7,957 NT verse blocks examined.
- 7,943 matched the stored KJV word/Strong's sequence exactly.
- 14 were exact prefixes of the stored KJV sequence, with **186 additional stored suffix tokens**.
- No non-prefix word/Strong's mismatches were found.
- 6,358 source stub positions were recorded separately.

The extra suffix tokens occur in book-ending records and are consistent with appended subscription/colophon material outside the OSIS verse body. They were not silently treated as verse-body words. The source ingestion table preserves the raw Robinson verse text, source repository/commit, source-file SHA-256, and original line range.

## 5. Source compatibility results

For the resolved verses, 137,821 source lemma/position checks were evaluated:

| Check | Matches | Rate |
|---|---:|---:|
| `lemma.TR` | 137,683 | 99.90% |
| Strong's | 137,625 | 99.86% |
| Robinson morphology | 137,256 | 99.59% |
| All available fields | 137,182 | 99.54% |
| Out-of-range positions | 0 | — |

On the 133,255 distinct source positions that are actually attached to KJV word mappings, the old and rebuilt sequences compare as follows:

| Measure | Existing sequence | Variant-aware sequence |
|---|---:|---:|
| `lemma.TR` matches | 131,396 (98.60%) | 133,117 (99.90%) |
| Strong's matches | 131,411 | 133,061 |
| Morphology matches | 131,097 | 132,722 |
| All available fields match | 130,932 | 132,650 |
| Out-of-range positions | 2 | 0 |

The old sequence's two unique out-of-range positions generated three alignment rows: John 9:21 position 24 (referenced twice) and Colossians 4:10 position 21. Both are in range in the variant-aware sequence.

## 6. Bridge comparison

Comparisons below are restricted to the 7,940 resolved verses, so unresolved references do not distort the row counts.

| Measure | Existing bridge, resolved refs | Shadow rebuild |
|---|---:|---:|
| KJV-to-Greek alignment rows | 202,414 | 202,404 |
| YLT rendering rows | 142,978 | 142,978 |
| Distinct Greek positions with YLT | 107,186 | 107,186 |
| Out-of-range alignment rows | 3 | 0 |
| Orphan YLT rendering rows | 3 | 0 |

The alignment edge-set comparison found **10 legacy-only edges and zero new-only edges**. All 10 legacy-only edges are in Colossians 4:18, KJV positions 17–26. The CrossWire OSIS verse body ends before the appended subscription/colophon material, so those legacy-only edges were excluded and recorded as a colophon exclusion. The YLT rendering edge sets are otherwise identical on resolved verses: **zero old-only and zero new-only rendering edges**.

This is an important distinction: the YLT rendering rows were already present. They were orphaned because the flattened Greek token sequence did not contain the Greek positions those rows referenced. Correcting the Greek sequence makes the existing YLT renderings valid; a separate YLT realignment is not indicated by this test.

### Known examples

- **John 9:21:** the rebuilt sequence contains Greek position 24, `λαλησει` (`G2980`, `V-FAI-3S`). YLT `shall` and `speak` now resolve to that position; `him` resolves to `auton` at position 19.
- **Colossians 4:10:** the rebuilt sequence contains Greek position 21, `auton` (`G846`). YLT `him` resolves to position 21 rather than remaining orphaned; `receive` remains associated with the relevant receive-form position(s).

The sequence comparison over resolved verses found:
- 7,754 verses unchanged; 186 changed.
- Existing sequence: 140,638 words.
- Rebuilt sequence: 140,414 words (224 fewer).
- 1,724 same-position surface differences, 226 existing-only tail positions, and 2 rebuilt-only tail positions.

The YLT coverage percentage is 76.3357% for the rebuilt resolved sequence versus 76.2141% for the existing resolved subset. The numerator is unchanged at 107,186 mapped Greek positions; the denominator is smaller by 224 words. This is not evidence of more YLT mappings—it reflects removal/selection of variant tokens.

## 7. Gwen/Qwen classification test

A local inference test was attempted with `gwen:latest` and `qwen3:0.6b`. The Gwen request timed out and its Ollama runner remained at 100% CPU in a `Stopping` state. The Qwen CLI request exceeded 90 seconds without returning usable output. This is an inconclusive runtime test, not evidence that the models cannot help. No model output was used to select a reading. The canonical sequence decisions above are entirely deterministic.

## 8. Validation and decision

Shadow integrity checks passed:
- Greek word positions contiguous within every stored verse.
- No duplicate alignment or rendering keys.
- No alignment position missing a Greek word.
- No YLT rendering position missing a Greek word.
- No source-text row missing its source hash or line provenance.
- No out-of-range positions in the rebuilt active bridge.

**Conclusion:** The variant-aware reconstruction is validated in isolation for source-resolved verses and corrects the known John 9:21 and Colossians 4:10 positional failures. It also identifies 10 legacy Colossians 4:18 colophon mappings that should not be treated as ordinary verse-body alignment.

**Not approved for production.** The 19 unresolved variant groups across 17 references remain preserved but unselected. The Colossians 4:18 colophon exclusion also needs explicit review. No production migration, source change, API change, or vectorizer change has been made.

The test harness scripts and decision JSON are retained on Lampy under `/var/lib/bible-validation/robinson-variant-audit/`, with a `README.md` and `MANIFEST.sha256`. The pinned source checkouts and raw KJV OSIS input remain under `/tmp/robinson-variant-audit/`; the scripts have not yet been packaged as repository scripts. The report and durable validation notes are committed on the `ylt-lexicon-validation` branch only.
