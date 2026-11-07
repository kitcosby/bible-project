# Five-verse YLT variant sequence materialization — 2026-11-06

## Result

Five additional verse sequences were committed to the isolated shadow database `bible_greek_bridge_test_20261106.ylt_profile_shadow` after a dry run and strict precondition checks.

| Verse | Robinson group | YLT selection | Sequence effect |
|---|---:|---|---|
| John 8:6 | 43:6 | A | Empty branch; YLT does not render the additional branch-B participial phrase. |
| Acts 3:3 | 44:3 | A | `λαβεῖν` already occurs in the base sequence; no insertion required. |
| Romans 16:27 | 45:7 | A | `ᾧ` already occurs in the base sequence; no insertion required. |
| Ephesians 6:24 | 49:3 | A | `ἀμήν` already occurs in the base sequence; no insertion required. |
| 1 John 2:23 | 62:3 | B | Adds the eight-token bracketed confession clause present in YLT: `ὁ ὁμολογῶν τὸν υἱὸν καὶ τὸν πατέρα ἔχει`. |

The 1 John insertion is marked `proposed_ylt_branch`, with null base positions and explicit dependency `62:3`. It is not represented as an inherited Robinson base token. The bracketed English text is preserved in the YLT token stream; bracketed Robinson subscription/paratext is excluded from verse sequences.

## Added shadow records

- 95 YLT tokens.
- 77 Greek sequence words.
- 45 new YLT token-review rows with status `pending_review`.
- 30 new Greek token-review rows with status `pending_review`.
- 30 corresponding unaligned-Greek alignment placeholders.

## Current shadow totals after materialization

| Table | Rows |
|---|---:|
| Profiles | 4 |
| Textual variant groups | 261 |
| Textual variant branches | 522 |
| Profile variant selections | 783 |
| YLT-profile Greek sequence words | 2,444 |
| YLT tokens | 3,171 |
| YLT–Greek alignment rows | 582 |
| YLT token-review rows | 3,171 |
| Greek token-review rows | 565 |

Review status counts:

| Review layer | Status | Rows |
|---|---|---:|
| Greek token | Proposed | 479 |
| Greek token | Legacy overlap review | 25 |
| Greek token | Pending review | 61 |
| YLT token | Proposed | 473 |
| YLT token | Legacy overlap review | 37 |
| YLT token | Legacy only | 2,114 |
| YLT token | Pending review | 547 |
| Alignment | Proposed | 521 |
| Alignment | Not expressed | 20 |
| Alignment | Unresolved | 11 |
| Alignment | Pending review | 30 |

The current Greek pending queue is now 61 rows: the original 31 pending rows from the 116-verse fixture plus 30 newly materialized Greek positions. The YLT pending count is 547: the prior 502 plus 45 newly materialized YLT tokens. These are current database queue counts, not the historical 39-case subset described in the original contextual review.

## Variant-selection status

Across the 261 YLT-profile variant groups:
- 224 inherited provisional selections.
- 17 reviewed against the stored YLT text.
- 14 not applicable to verse alignment (subscription/colophon groups).
- 5 explicit proposed YLT overrides (Mark 8:24, 2 Corinthians 7:12, 2 Corinthians 11:10).
- 1 unresolved verse-text group (Revelation 7:3).

The five newly reviewed groups above are materialized in the YLT sequence. Revelation 7:3 remains deliberately unmaterialized: its two branches differ in verbal mood, and no YLT-specific selection has been established. Do not infer a choice from the inherited KJV candidate sequence.

## Validation and isolation

The materialization script required exact pre-materialization table counts, checked YLT verse-text SHA-256 hashes, verified inherited words against production `public.gnt_words` by surface/Strong's/morphology at each source position, and required contiguous one-based token positions. Post-insert checks compared the complete inserted sequences and token rows against the dry-run manifest.

The final shadow validator passed:
- Exact expected table totals and review-status counts.
- Exact branch selections and sequence dependencies.
- The eight-token 1 John 2:23 branch-B insertion.
- All five new verse sequence/token counts and pending-row counts.
- No bracketed paratext in the verse sequence.
- No missing alignment targets, incomplete proposed endpoints, or orphan alignment groups.

Production read-only counts remained:
- `gnt_words`: 141,009
- `gnt_ylt_renderings`: 143,227
- `ylt_verses`: 31,102
- `ylt_verses_embedding_store`: 31,102
- Non-null stored embeddings: 31,102

No production rows, API behavior, embedding vectors, or vectorizer configuration were changed. This is an isolated research/shadow update only.
