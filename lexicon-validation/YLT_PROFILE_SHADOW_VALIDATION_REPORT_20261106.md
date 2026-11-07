# YLT Profile Shadow — Validation Snapshot

**Date:** 2026-11-06  
**Database:** bible_greek_bridge_test_20261106  
**Schema:** ylt_profile_shadow  
**Result:** Full shadow validation passed.

## Current schema counts

| Object | Rows |
|---|---:|
| Profiles | 4 |
| Textual variant groups | 261 |
| Textual variant branches | 522 |
| Profile variant selections | 783 |
| YLT sequence words | 2,367 |
| YLT tokens | 3,076 |
| Alignment groups | 16 |
| YLT–Greek alignment rows | 552 |
| YLT token review rows | 3,076 |
| Greek token review rows | 535 |

## YLT profile variant-selection status

| Status | Count |
|---|---:|
| inherited_provisional | 224 |
| proposed | 5 |
| reviewed_against_translation | 17 |
| not_applicable_to_verse_alignment | 14 |
| unresolved | 1 |
| **Total** | **261** |

The 19 groups formerly unresolved were reviewed: five verse-text choices selected against YLT, thirteen epistle subscriptions/colophons marked not applicable to verse alignment, and Revelation 7:3 retained as unresolved. See [YLT_VARIANT_SELECTION_CASE_INDEX_20261106.md](YLT_VARIANT_SELECTION_CASE_INDEX_20261106.md).

Important coverage boundary: the five newly reviewed verse-text selections are recorded in the profile selection ledger but their six affected verses (five selected verses plus Revelation 7:3) are not yet materialized in the current 116-verse sequence sample. No sequence rows were inserted for them. They must be built from the selected Robinson branches before any alignment is attempted.

## Alignment and token-review status

| Table | Status | Count |
|---|---|---:|
| ylt_greek_alignment | proposed | 521 |
| ylt_greek_alignment | not_expressed | 20 |
| ylt_greek_alignment | unresolved | 11 |
| ylt_token_review | proposed | 473 |
| ylt_token_review | pending_review | 502 |
| ylt_token_review | legacy_overlap_review | 37 |
| ylt_token_review | legacy_only | 2,064 |
| gnt_token_review | proposed | 479 |
| gnt_token_review | pending_review | 31 |
| gnt_token_review | legacy_overlap_review | 25 |

The original 39 Greek function-token queue now has eight proposals and 31 pending rows. The eight include three high-confidence direct function-word proposals and five moderate-confidence phrase-member proposals. The remaining 31 are not automatically treated as absent from YLT: their confidence remains unresolved. See [GREEK_ALIGNMENT_CASE_INDEX.md](GREEK_ALIGNMENT_CASE_INDEX.md) and the latest [queue snapshot](GREEK_TOKEN_REVIEW_QUEUE_POST_EIGHT_PROPOSALS_20261106.csv).

## Sequence coverage

- 2,367 YLT-profile Greek sequence words.
- 2,215 sequence words have explicit variant dependency keys.
- Those dependencies span 108 verses.
- 152 sequence words are in verses with no recorded variant group.
- Five proposed YLT branch words remain in the existing sequence sample (Mark 8:24 and 2 Corinthians 7:12).
- No sequence rows were added for the six newly reviewed variant references.

## Integrity checks

- Missing alignment targets: 0.
- Incomplete proposed endpoints: 0.
- Orphan alignment groups: 0.
- The four earlier legacy-overlap target corrections remain valid.
- The eight current function-token proposals pass the read-only endpoint validator.
- The 19-group variant-selection review passes the read-only branch/status validator.
- The legacy-overlap validator passes.

## Production preservation

Production counts remained unchanged:

| Table | Rows |
|---|---:|
| public.gnt_words | 141,009 |
| public.gnt_ylt_renderings | 143,227 |

No production DDL/DML, legacy association edits, embedding generation, vectorizer changes, API changes, merge, or deployment occurred. All work remains in the isolated shadow database and this validation branch.
