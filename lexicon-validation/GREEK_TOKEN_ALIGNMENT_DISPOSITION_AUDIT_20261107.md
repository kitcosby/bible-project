# Greek Token Alignment Disposition Audit — 2026-11-07

## Current result

The 20 remaining cases whose alignment rows were provisionally marked not_expressed but still had unresolved confidence have been reviewed against their full YLT verse and exact YLT-profile Greek sequence:

- 18 cases were raised to high-confidence not_expressed.
- Two were classified moderate-confidence not_expressed because Greek function contributes to a recast clause or attributive phrase, rather than a separate English token.

A further context/consistency pass found four Greek token-review rows marked proposed with a proposed count of one but no corresponding alignment endpoint. All four have been reconciled conservatively:

- **Acts 21:8, οἱ (position 5):** represented as a phrase-member candidate for YLT “company” within οἱ περὶ τὸν Παῦλον. Held in legacy-overlap review because the legacy “company” token points to Greek positions [7,8].
- **Acts 21:8, εἰς (position 10):** a direct proposal to YLT “to” (token 14), “to Caesarea”. The later εἰς (position 14) remains linked to “into” (token 19).
- **Luke 1:26, τῷ (position 5):** the second article in ἐν τῷ μηνὶ τῷ ἕκτῳ is not separately expressed; YLT has one “the”, already linked to the first τῷ (position 3).
- **Matthew 10:25, ὁ (position 7):** not independently expressed in “as his teacher”; διδάσκαλος maps to “teacher” and αὐτοῦ supplies “his”.

## Acts 21:8 phrase-level corner case

The Greek phrase **οἱ περὶ τὸν Παῦλον** is rendered by YLT as **“Paul and his company”**. Παῦλον (position 8) maps directly to “Paul”; οἱ and περί (positions 5–6) jointly contribute to “company”; τὸν (position 7) has no separate English article. “And his” are English phrase expansions within the whole expression.

The legacy YLT “company” token carries Greek positions [7,8] (τὸν Παῦλον), which conflicts with the contextual analysis. The two phrase-member candidates for positions 5 and 6 therefore remain in legacy_overlap_review; the legacy association is preserved. See [ACTS_21_8_PAUL_COMPANY_PHRASE_REVIEW_20261107.md](ACTS_21_8_PAUL_COMPANY_PHRASE_REVIEW_20261107.md).

## Acts 15:32: variant-dependent particle

The sole genuinely unresolved case is **δέ at Acts 15:32 position 2**. The YLT reads “Judas also and Silas”. Robinson variant group 44:19 has A=τε and B=δέ; Robinson source is unselected, the CrossWire/KJV candidate selected B algorithmically, and the YLT candidate inherited B provisionally. This is not a YLT editorial decision. The stable καί at position 3 is now proposed to YLT “and” (token 3), while the branch-dependent particle at position 2 and YLT “also” (token 2) remain unresolved. See [ACTS_15_32_DE_KAI_VARIANT_ALIGNMENT_REVIEW_20261107.md](ACTS_15_32_DE_KAI_VARIANT_ALIGNMENT_REVIEW_20261107.md).

## Current Greek pending queue: two distinct status layers

The current all-verse token-review queue contains **33 rows**. Their alignment-level dispositions are:

| Alignment-level disposition | Confidence | Count |
|---|---|---:|
| not_expressed | high | 27 |
| not_expressed | moderate | 5 |
| unresolved | unresolved | 1 |

The 33 token-table rows remain pending because gnt_token_review has no not_expressed status. The current queue export deliberately includes both token-review and alignment-review statuses. It must not be read as 33 undecided alignments.

## Final shadow counts

- Alignment groups: 33.
- Alignment rows: 605.
- Alignment statuses: 566 proposed, 32 not_expressed, six legacy_overlap_review, one unresolved.
- Greek token-review rows: 509 proposed, 33 pending_review, 31 legacy_overlap_review.
- YLT token-review rows: 517 proposed, 503 pending_review, 42 legacy_overlap_review, 2,109 legacy_only.
- All 509 Greek token-review rows marked proposed now have matching proposed alignment endpoints; the four mismatches discovered in this pass are reconciled.

The row-level export is [GREEK_TOKEN_ALIGNMENT_DISPOSITION_QUEUE_20261107.csv](GREEK_TOKEN_ALIGNMENT_DISPOSITION_QUEUE_20261107.csv). The current YLT pending queue is [YLT_TOKEN_REVIEW_QUEUE_CURRENT_20261107.csv](YLT_TOKEN_REVIEW_QUEUE_CURRENT_20261107.csv).

## Scope and safeguards

The full v10 shadow validator passed. Changes affected only the isolated shadow schema ylt_profile_shadow. Production tables, legacy associations, embeddings, vectorizer, API, and deployment were not changed.

Production read-only counts remain unchanged:

- gnt_words: 141,009
- gnt_ylt_renderings: 143,227
- ylt_verses: 31,102
- ylt_verses_embedding_store: 31,102
- non-null embedding vectors: 31,102

These are evidence-based shadow annotations and proposals, not production approvals. not_expressed means no independent English token is warranted in this YLT rendering; grammatical and phrase-level contribution may still be present.