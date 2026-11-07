# Greek Token Alignment Disposition Audit — 2026-11-07

## Current result

The 20 remaining cases whose alignment rows were provisionally marked not_expressed but still had unresolved confidence have now been reviewed against their full YLT verse and exact YLT-profile Greek sequence:

- 18 cases were raised to high-confidence not_expressed.
- Two were classified moderate-confidence not_expressed because Greek function contributes to a recast clause or attributive phrase, rather than a separate English token.

A further context/consistency pass found four Greek token-review rows marked proposed with a proposed count of one but no corresponding alignment endpoint. These have now been reconciled rather than left as false approvals:

- **Acts 21:8, οἱ (position 5):** represented as a phrase-member candidate for YLT “company” within οἱ περὶ τὸν Παῦλον. Held in legacy-overlap review because the legacy “company” token points to Greek positions [7,8].
- **Acts 21:8, εἰς (position 10):** a direct proposal to YLT “to” (token 14), “to Caesarea”. The later εἰς (position 14) remains linked to “into” (token 19).
- **Luke 1:26, τῷ (position 5):** the second article in ἐν τῷ μηνὶ τῷ ἕκτῳ is not separately expressed; YLT has one “the”, already linked to the first τῷ (position 3).
- **Matthew 10:25, ὁ (position 7):** not independently expressed in “as his teacher”; διδάσκαλος maps to “teacher” and αὐτοῦ supplies “his”.

## Acts 21:8 phrase-level corner case

The Greek phrase **οἱ περὶ τὸν Παῦλον** is rendered by YLT as **“Paul and his company”**. It is not sound to force περί to a standalone English preposition. The contextual group records:

- Παῦλον → “Paul” as a direct phrase member.
- οἱ and περί jointly contribute to “company”.
- τὸν before the proper name has no separate English article.
- “and his” are English phrase expansions within the translation.

The legacy YLT “company” token carries Greek positions [7,8] (τὸν Παῦλον), which conflicts with the contextual analysis. Those two phrase-member candidates are therefore marked legacy_overlap_review, not approved. The legacy association is preserved.

## Current Greek pending queue: two distinct status layers

The current all-verse token-review queue contains **33 rows**. Their alignment-level dispositions are:

| Alignment-level disposition | Confidence | Count |
|---|---|---:|
| not_expressed | high | 27 |
| not_expressed | moderate | 5 |
| unresolved | unresolved | 1 |

The sole genuinely unresolved case is **Acts 15:32, δέ** in Ἰούδας δὲ καὶ Σιλᾶς → “Judas also and Silas”. The YLT has both “also” and “and”, but assigning the two particles to separate English tokens with confidence would require more than positional order; the phrase-level relation remains open.

The 33 token-table rows remain pending because gnt_token_review has no not_expressed status. The current queue export deliberately includes both token-review and alignment-review statuses. It must not be read as 33 undecided alignments.

## Final shadow counts

- Alignment groups: 32.
- Alignment rows: 604.
- Alignment statuses: 565 proposed, 32 not_expressed, six legacy_overlap_review, one unresolved.
- Greek token-review rows: 508 proposed, 33 pending_review, 31 legacy_overlap_review.
- YLT token-review rows: 516 proposed, 503 pending_review, 42 legacy_overlap_review, 2,110 legacy_only.
- All 508 Greek token-review rows marked proposed now have matching proposed alignment endpoints; the four mismatches discovered in this pass are reconciled.

The row-level export is [GREEK_TOKEN_ALIGNMENT_DISPOSITION_QUEUE_20261107.csv](GREEK_TOKEN_ALIGNMENT_DISPOSITION_QUEUE_20261107.csv). The current Greek pending-only queue is [GREEK_TOKEN_REVIEW_QUEUE_CURRENT_20261107.csv](GREEK_TOKEN_REVIEW_QUEUE_CURRENT_20261107.csv).

## Scope and safeguards

The changes affected only the isolated shadow schema ylt_profile_shadow. The full v9 validator passed. Production tables, legacy associations, embeddings, vectorizer, API, and deployment were not changed.

Production read-only counts remain unchanged:

- gnt_words: 141,009
- gnt_ylt_renderings: 143,227
- ylt_verses: 31,102
- ylt_verses_embedding_store: 31,102
- non-null embedding vectors: 31,102

These are evidence-based shadow annotations and proposals, not production approvals. not_expressed means no independent English token is warranted in this YLT rendering; grammatical and phrase-level contribution may still be present.