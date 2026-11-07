# YLT Pending Token Queue — Stratification and Review Plan (2026-11-07)

## Current queue state after Revelation 9:20 review

The YLT-side token-review table now has **484 pending YLT tokens across 116 verses and 23 New Testament books**.

Current status totals:
- **536** proposed
- **484** pending_review
- **42** legacy_overlap_review
- **2,109** legacy_only

The 484 pending rows divide by recorded reason:
- **479** generic rows: “No direct proposal identified in this review set.”
- **5** annotated corner cases: one each in Acts 15:32, 1 John 2:23, Romans 16:27 (“the” and “[be]”), and Revelation 9:20 (“are”).

The 479 generic rows remain a candidate-discovery queue. They are not proven unexpressed cases. The five annotated rows retain their actual grammatical or textual disposition; pending_review is the token-table status, not a claim that every case is undecided.

## Four earlier proposal-status reconciliations

A previous reconciliation found four YLT tokens whose alignment rows were already marked proposed while their YLT token-review rows still said pending. Those statuses were synchronized without creating new alignment rows:

| YLT reference | YLT token | Greek target | Confidence | Disposition |
|---|---|---|---|---|
| 1 Corinthians 13:2 | “the” (token 9) | τὰ (position 7) | high | Proposed |
| Acts 5:12 | “through” (token 2) | διά (position 1) | high | Proposed |
| Acts 26:20 | “those” (token 3) | τοῖς (position 2) | high | Proposed |
| Matthew 2:23 | “that” (token 15) | τό (position 10) | moderate | Proposed phrase member |

## Five annotated pending cases

| Reference | YLT token | Disposition |
|---|---|---|
| 1 John 2:23 | “he” (token 10) | Supplied English subject pronoun with third-person ἔχει; no independent Greek pronoun. |
| Acts 15:32 | “also” (token 2) | Branch-sensitive: Robinson group 44:19 has A=τε and B=δέ; YLT-specific source reading is not established. The stable καί at Greek position 3 → “and” is proposed separately. |
| Romans 16:27 | “the” (token 2) | English article before “only wise God”; no Greek article occurs in the selected sequence. |
| Romans 16:27 | “[be]” (token 11) | Bracketed supplied copula; no Greek finite verb is present. |
| Revelation 9:20 | “are” (token 52) | Supplied English copula; recorded as alignment-level unaligned_ylt/not_expressed. The token-review table has no not_expressed status, so it remains pending_review there. |

See the focused [Acts 15:32 variant review](ACTS_15_32_DE_KAI_VARIANT_ALIGNMENT_REVIEW_20261107.md), [Romans 16:27/1 John 2:23 grammatical-supply notes](YLT_TOKEN_REVIEW_QUEUE_TRIAGE_20261107.md), and [Revelation 9:20 phrase case](REVELATION_9_20_DENSE_PHRASE_ALIGNMENT_CASE_20261107.md).

## Most frequent pending YLT surfaces

| Surface | Count |
|---|---:|
| to | 51 |
| the | 33 |
| may | 22 |
| did | 20 |
| was | 18 |
| having | 15 |
| is | 15 |
| of | 15 |
| a | 14 |
| who | 13 |
| in | 12 |
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
| those | 5 |
| do | 4 |
| were | 4 |
| and | 3 |
| back | 3 |
| before | 3 |
| didst | 3 |
| for | 3 |
| it | 3 |

Frequencies prioritize review batches; they do not establish that repeated English words share the same Greek source. “To” may represent a preposition, an infinitive marker, a purpose construction, or English syntax without a one-to-one Greek token.

## Pending rows by book

| Book | Pending YLT tokens |
|---|---:|
| Acts | 101 |
| Luke | 54 |
| Matthew | 49 |
| Revelation | 34 |
| Colossians | 33 |
| Mark | 30 |
| John | 25 |
| 1 Corinthians | 21 |
| Romans | 20 |
| 2 Corinthians | 17 |
| Hebrews | 16 |
| 1 Timothy | 15 |
| Philippians | 12 |
| 1 Thessalonians | 12 |
| 2 Peter | 10 |
| James | 8 |
| Jude | 6 |
| 1 Peter | 5 |
| 1 John | 4 |
| 2 John | 4 |
| 2 Timothy | 3 |
| Titus | 3 |
| Philemon | 2 |

## Largest remaining verse clusters

| Reference | Pending YLT tokens |
|---|---:|
| Acts 19:27 | 13 |
| 1 Corinthians 5:11 | 12 |
| Acts 26:20 | 11 |
| Revelation 7:2 | 11 |
| Acts 4:32 | 10 |
| Acts 21:8 | 10 |
| Acts 22:25 | 9 |
| 2 Corinthians 6:15 | 8 |
| 2 Corinthians 7:12 | 8 |
| Colossians 4:16 | 8 |
| Luke 8:29 | 8 |
| Luke 12:20 | 8 |
| Mark 13:14 | 8 |
| Matthew 2:11 | 8 |
| Philippians 4:12 | 8 |
| Romans 1:27 | 8 |
| 1 Thessalonians 2:15 | 7 |
| 1 Timothy 3:2 | 7 |
| Acts 7:26 | 7 |
| Acts 26:18 | 7 |

Revelation 9:20 is no longer the largest pending cluster: 15 tokens now have proposed phrase-member endpoints and “are” has an alignment-level not_expressed disposition.

## Recommended next review batches

1. Review the 51 remaining “to” occurrences by full verse and Greek construction, distinguishing prepositions from infinitive markers and supplied English syntax.
2. Review the 33 “the” occurrences, especially repeated Greek articles, articular infinitives, and articles introduced or omitted in English.
3. Review auxiliaries and participial expansions (“may”, “did”, “was”, “having”, “is”) as constructions before proposing individual Greek tokens.
4. Keep the five annotated cases above separate from the 479 generic pending rows.
5. Preserve legacy links; contextual alternatives should remain overlap candidates until occurrence identity is established.

The current row-level queue is [YLT_TOKEN_REVIEW_QUEUE_CURRENT_20261107.csv](YLT_TOKEN_REVIEW_QUEUE_CURRENT_20261107.csv). It contains exactly 484 rows.

No production tables, legacy associations, embeddings, vectorizer, API, or deployment were changed.
