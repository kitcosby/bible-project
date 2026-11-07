# Greek Token Alignment Disposition Audit — 2026-11-07

## Result

The 20 remaining cases whose alignment rows were already marked not_expressed but still had unresolved confidence have now been reviewed against their full YLT verse and the exact YLT-profile Greek sequence.

- 18 cases: high-confidence not_expressed.
- 2 cases: moderate-confidence not_expressed because the Greek function contributes to a recast clause or attributive phrase rather than a separately rendered English token.
- The two genuinely unresolved cases remain Acts 15:32 δέ and Acts 21:8 περί.

Combined current disposition for the 31 Greek-token rows still marked pending_review in the token-review table:

| Alignment-level disposition | Confidence | Count |
|---|---|---:|
| not_expressed | high | 24 |
| not_expressed | moderate | 5 |
| unresolved | unresolved | 2 |

The complete row-level export is [GREEK_TOKEN_ALIGNMENT_DISPOSITION_QUEUE_20261107.csv](GREEK_TOKEN_ALIGNMENT_DISPOSITION_QUEUE_20261107.csv). It deliberately includes both status layers.

## Why 31 token rows remain pending

The gnt_token_review table does not have a not_expressed status. Its pending_review value therefore remains for rows that have no YLT token target, even when the separate alignment row records a contextually reviewed not_expressed disposition. Do not interpret all 31 token-table pending rows as undecided alignments.

The two remaining open cases are:

- **Acts 15:32, δέ:** δὲ καί has joint discourse/connective force. Assigning YLT “also” to δέ alone would overstate a one-to-one relationship; the interaction with καί remains unresolved.
- **Acts 21:8, περί:** οἱ περὶ τὸν Παῦλον is an idiomatic group expression rendered “Paul and his company”. No separate YLT preposition token can be isolated with sufficient confidence.

## Scope and safeguards

The 20 confidence updates affected only existing rows in ylt_profile_shadow.ylt_greek_alignment and corresponding explanatory reason fields in ylt_profile_shadow.gnt_token_review. No Greek sequence positions, YLT token positions, alignment endpoints, legacy associations, raw Robinson branches, production tables, embeddings, vectorizer, API, or deployment were changed.

The full validator passed after these updates. Production read-only counts remain unchanged:

- gnt_words: 141,009
- gnt_ylt_renderings: 143,227
- ylt_verses: 31,102
- ylt_verses_embedding_store: 31,102
- non-null embedding vectors: 31,102

The dispositions are evidence-based shadow annotations, not production approvals or claims that a Greek word has no semantic contribution. not_expressed means no independent English token is warranted in this YLT rendering; grammatical and phrase-level contribution may still be present.
