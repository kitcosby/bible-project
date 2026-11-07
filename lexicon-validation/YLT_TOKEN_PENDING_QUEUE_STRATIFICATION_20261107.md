# YLT Pending Token Queue — Stratification and Review Plan (2026-11-07)

## Current queue state

The YLT-side token-review table now has **499 pending YLT tokens across 116 verses**.

A reconciliation pass found four YLT tokens whose alignment rows were already marked proposed while their YLT token-review rows still said pending. Those four token statuses have been synchronized to proposed; no new alignment rows were created in that reconciliation.

The remaining 499 pending tokens have:

- **499/499 with no legacy Greek position span**.
- **0/499 with an existing proposed alignment endpoint**.
- **495** with the generic reason “No direct proposal identified in this review set.”
- **4** explicitly annotated corner cases listed below.

This is a clean pending queue: none of its rows should be silently promoted from a stale alignment proposal. Surface-frequency groupings below are triage aids only, not alignment evidence.

## Four proposals reconciled

| YLT reference | YLT token | Greek target | Confidence | Disposition |
|---|---|---|---|---|
| 1 Corinthians 13:2 | “the” (token 9) | τὰ (position 7) | high | Proposed |
| Acts 5:12 | “through” (token 2) | διά (position 1) | high | Proposed |
| Acts 26:20 | “those” (token 3) | τοῖς (position 2) | high | Proposed |
| Matthew 2:23 | “that” (token 15) | τό (position 10) | moderate | Proposed phrase member |

The corresponding alignment records already existed. Only the YLT token-review status and reason were reconciled.

## Four annotated cases that remain pending

| Reference | YLT token | Existing note | Why it remains pending |
|---|---|---|---|
| 1 John 2:23 | “he” (token 10) | English subject pronoun supplied with third-person ἔχει; no independent Greek pronoun occurs. | The YLT token is supplied by English syntax; no direct Greek pronoun target is warranted. |
| Acts 15:32 | “also” (token 2) | Possible source is the branch-specific particle at position 2 (A τε / B δέ); YLT-specific source reading is not established. | Variant group 44:19 has A=τε and B=δέ; YLT candidate B is inherited provisionally from the KJV candidate. |
| Romans 16:27 | “the” (token 2) | English article added before “only wise God”; no Greek article occurs in this sequence. | No independent Greek article target is present in the selected candidate sequence. |
| Romans 16:27 | “[be]” (token 11) | Bracketed supplied copula; no Greek finite verb is present. | English supplied copula; no Greek finite verb target is warranted. |

The YLT token-review schema has no not_expressed or unresolved status. These four remain pending in that table, but their reasons preserve the actual disposition. The Acts 15:32 case has a separate unresolved Greek-side row and focused variant report.

## Most frequent pending YLT surfaces

| Surface | Count |
|---|---:|
| to | 54 |
| the | 33 |
| may | 23 |
| did | 21 |
| of | 18 |
| was | 18 |
| having | 15 |
| is | 15 |
| a | 14 |
| who | 13 |
| in | 12 |
| those | 10 |
| have | 8 |
| he | 8 |
| they | 8 |
| are | 6 |
| be | 6 |
| one | 6 |
| that | 6 |
| been | 5 |
| being | 5 |
| doth | 5 |
| before | 4 |
| do | 4 |
| were | 4 |
| and | 3 |
| back | 3 |
| didst | 3 |
| for | 3 |
| it | 3 |

These frequencies prioritize review batches; they do not establish that repeated English words share the same Greek source. For example, “to” may represent εἰς/πρός, an infinitive marker, a purpose construction, or English syntax without a one-to-one Greek token.

## Pending rows by book (largest queues)

| Book | Pending YLT tokens |
|---|---:|
| AC | 101 |
| LU | 54 |
| MT | 49 |
| RE | 49 |
| COL | 33 |
| MR | 30 |
| JOH | 25 |
| 1CO | 21 |
| RO | 20 |
| 2CO | 17 |
| HEB | 16 |
| 1TI | 15 |
| 1TH | 12 |
| PHP | 12 |
| 2PE | 10 |
| JAS | 8 |
| JUDE | 6 |
| 1PE | 5 |
| 1JO | 4 |
| 2JO | 4 |

## Current YLT token-review totals

- 521 proposed
- 499 pending_review
- 42 legacy_overlap_review
- 2,109 legacy_only

The current row-level queue is [YLT_TOKEN_REVIEW_QUEUE_CURRENT_20261107.csv](YLT_TOKEN_REVIEW_QUEUE_CURRENT_20261107.csv).

## Recommended next review batches

1. Review the 54 “to” occurrences by full verse and Greek construction, distinguishing prepositions from infinitive markers and supplied English syntax.
2. Review the 33 “the” occurrences, especially repeated Greek articles, articular infinitives, and articles introduced or omitted in English.
3. Review auxiliaries and participial expansions (“may”, “did”, “was”, “having”, “is”) as constructions before proposing individual Greek tokens.
4. Keep the four annotated cases above separate from generic pending rows; do not treat their pending status as an absence of research.

No production tables, legacy associations, embeddings, vectorizer, API, or deployment were changed.