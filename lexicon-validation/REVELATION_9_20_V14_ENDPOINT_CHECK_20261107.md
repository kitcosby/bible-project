# Revelation 9:20 v14 endpoint check

Executed against the isolated shadow database `bible_greek_bridge_test_20261106` on 2026-11-07.

## Assertions passed

- All 15 phrase-member endpoints were found exactly once at their expected Greek/YLT positions.
- YLT profile 3 selects Robinson group `66:18` branch A with status `proposed`.
- Greek position 13 is `ουτε / oute / G3777 / CONJ-N` with sequence status `proposed_ylt_branch`.
- Exactly one alignment row directly depends on group `66:18`.
- The supplied-copula row remains `not_expressed`.

## Production row counts inspected

| Production table | Rows |
|---|---:|
| `gnt_words` | 141,009 |
| `gnt_ylt_renderings` | 143,227 |
| `ylt_verses` | 31,102 |
| `ylt_verses_embedding_store` | 31,102 |
| Non-null stored embeddings | 31,102 |

The Revelation 9:20 legacy rendering count inspected was 52. No production rows were modified by this read-only endpoint check.

## Scope

The script is a read-only assertion check for the Revelation 9:20 proposal. It is supplementary to the full v14 validator and does not replace it. The assertions verify endpoint identity, branch metadata, dependency scope, and production row-count invariants; they do not prove the proposed Greek reading is historically the exact edition Young used.
