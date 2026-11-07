# YLT Token Review Queue — Triage Notes and Corner Cases

**Prepared:** 2026-11-07  
**Environment:** Isolated database bible_greek_bridge_test_20261106, schema ylt_profile_shadow.  
**Scope:** Historical pre-Revelation-9:20 snapshot of YLT-profile token rows with ylt_token_review.review_status = pending_review.

## Historical queue snapshot before Revelation 9:20 phrase review

This pre-Revelation snapshot contained **499 YLT tokens** across 23 New Testament books and 116 verses. The review-reason field divides them as follows:

| Reason | Count | Interpretation |
|---|---:|---|
| No direct proposal identified in this review set. | 495 | No candidate was recorded by the current review workflow. This does not mean the token was examined and proved to have no Greek counterpart. |
| Bracketed supplied copula; no Greek finite verb is present. | 1 | Romans 16:27, “be”. |
| English article added before “only wise God”; no Greek article occurs in this sequence. | 1 | Romans 16:27, “the”. |
| English subject pronoun supplied with third-person ἔχει; no independent Greek pronoun occurs. | 1 | 1 John 2:23, “he” in “neither hath he the Father”. |
| YLT “also” token depends on unresolved source-branch particle (A τε / B δέ). | 1 | Acts 15:32, “also” (token 2). |

The 495 generic rows remain a candidate-discovery queue. They should not be automatically classified as unexpressed, nor should their count be presented as 500 unresolved alignments: many may already have legacy relationships or may require phrase-level treatment.

## Annotated pending corner cases

### Romans 16:27 — supplied “the”

- YLT token: “the” before “only wise God”.
- Greek sequence begins μονῷ σοφῷ θεῷ; there is no Greek article in this sequence.
- The English determiner is supplied by English syntax and should not be forced onto a Greek token.
- **Interpretation:** no independent Greek token corresponds to this English “the”.
- **Workflow status:** remains pending_review in the YLT token-review table because that table has no not_expressed status. The reason field records the grammatical finding; it is not a production approval.

### Romans 16:27 — bracketed “be”

- YLT token: “[be]” in “to him [be] the glory”.
- The Greek sequence has the relative pronoun ᾧ, the article ἡ, and the noun δόξα, but no finite copula corresponding to English “be”.
- The Greek article ἡ is already separately classified at alignment level as not_expressed; it is not the source of the English copula.
- **Interpretation:** “be” is a supplied English copula, not a Greek lexical token.
- **Workflow status:** remains pending_review in the YLT token-review table for the same status-vocabulary limitation.

### 1 John 2:23 — supplied subject “he”

- YLT phrase: “neither hath he the Father”.
- Greek phrase: οὐδὲ τὸν πατέρα ἔχει.
- The finite verb ἔχει is third-person singular; its subject is implicit. There is no independent Greek pronoun corresponding to the English “he”.
- Do not confuse this first “he” (YLT token 10) with the later “he who is confessing” (YLT token 13 onward). The latter is expressed by the substantival article + participle ὁ ὁμολογῶν and already has a phrase-group proposal.
- **Interpretation:** the first “he” is a supplied English subject pronoun, not a separate Greek lexical token.
- **Workflow status:** remains pending_review in the YLT token-review table; no Greek token should be fabricated to support it.

### Acts 15:32 — branch-dependent “also”

- YLT phrase: “Judas also and Silas”.
- Robinson variant group 44:19 has branch A τε and branch B δέ. The Robinson source is unselected; CrossWire/KJV selected B algorithmically, and the YLT candidate inherited B provisionally. This is not a YLT editorial decision.
- The stable καί at Greek position 3 is proposed to YLT “and” (token 3). The position-2 particle and YLT “also” (token 2) remain unresolved because the YLT source reading has not been established independently.
- **Interpretation:** do not force “also” to δέ on the basis of the inherited KJV candidate. The YLT wording is compatible with both branches.
- **Workflow status:** remains pending_review in the YLT token-review table and unresolved at alignment level. See the [Acts 15:32 variant review](ACTS_15_32_DE_KAI_VARIANT_ALIGNMENT_REVIEW_20261107.md).



### Revelation 9:20 — phrase-level English expansions (reviewed)

- Sixteen tokens were pending before review: “did”; “may”, “bow”, “before”; five instances of “those”; three middle “of” tokens; “are”; and three infinitive “to” markers.
- Fifteen tokens now have proposed phrase-member alignment rows across 10 phrase groups; the supplied copula “are” has an alignment-level `not_expressed` disposition and remains token-table pending because the token-review status vocabulary has no `not_expressed` value.
- Existing legacy links for “of gold”, “silver”, “brass”, “stone”, and “of wood” were preserved. New phrase members fill gaps; no legacy rendering rows were overwritten.
- Do not treat each English word as a separate Greek lexeme. See the [Revelation 9:20 case report](REVELATION_9_20_DENSE_PHRASE_ALIGNMENT_CASE_20261107.md).

## Largest pending clusters in the historical pre-review snapshot

These are useful review batches, not evidence that every token in a verse has the same problem.

| Reference | Pending YLT tokens |
|---|---:|
| Revelation 9:20 | 16 |
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

Acts 21:8 appears here because the YLT phrase “Paul and his company” is not a simple one-Greek-token/one-English-token mapping. Its phrase-level candidates and legacy conflict are documented separately in the Acts 21:8 phrase review.

## Queue concentration by book

| Book | Pending tokens |
|---|---:|
| Acts | 101 |
| Luke | 54 |
| Matthew | 49 |
| Revelation | 49 |
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

## Recommended review method

1. Start with dense verses, but inspect the whole verse and the complete YLT-profile Greek sequence.
2. Separate direct lexical correspondence, phrase-level correspondence, English grammatical supply, and no-expression cases.
3. Preserve existing legacy links. A contextual alternative should be recorded as an overlap until its occurrence identity is established.
4. Do not use Strong’s or morphology alone to choose among repeated Greek occurrences.
5. Keep the token-review status distinct from the alignment-row disposition. The current schema does not provide a YLT-token not_expressed status.
6. Do not infer that the 495 generic pending rows are all missing Greek equivalents; they have not yet been individually adjudicated by this review.

## Scope and safeguards

Four YLT token-review rows already had proposed alignment endpoints but still carried pending_review status; their token-review statuses were reconciled to proposed without creating new alignment rows. The remaining 499-row queue has no proposed alignment endpoints and no legacy Greek position spans. No legacy association, production table, embedding, vectorizer, API, or deployment was changed. See the [current row-level queue](YLT_TOKEN_REVIEW_QUEUE_CURRENT_20261107.csv) and [surface/queue stratification](YLT_TOKEN_PENDING_QUEUE_STRATIFICATION_20261107.md).

## Subsequent status update (2026-11-07)

The 499-row distribution above is a historical snapshot and should not be treated as the current pending queue. Revelation 9:20 was reviewed as a dense phrase case: 15 tokens received proposed phrase-member links, and “are” received an alignment-level not_expressed disposition while remaining token-table pending because the token-review schema has no not_expressed status. Current YLT-token counts are 536 proposed, 484 pending_review, 42 legacy_overlap_review, and 2,109 legacy_only. See the [Revelation 9:20 case report](REVELATION_9_20_DENSE_PHRASE_ALIGNMENT_CASE_20261107.md) and [v12 final validation](FINAL_VALIDATION_AFTER_REVELATION_9_20_20261107.txt).


## Historical queue status after Acts 19:27 (superseded by 1 Corinthians 5:11 review)

The current YLT-profile token-review queue contains **474 pending tokens across 116 verses**. Reason counts:

| Reason | Count |
|---|---:|
| No direct proposal identified in this review set | 466 |
| Branch-dependent “also” (Acts 15:32) | 1 |
| Supplied copula “be” (Romans 16:27) | 1 |
| Supplied English article “the” (Romans 16:27) | 1 |
| Supplied subject pronoun “he” (1 John 2:23) | 1 |
| Supplied copula “are” (Revelation 9:20; alignment-level not_expressed) | 1 |
| Supplied article “the” (Acts 19:27; alignment-level not_expressed) | 1 |
| Supplied copula “is” (Acts 19:27; alignment-level not_expressed) | 2 |

Current YLT-token status totals: **546 proposed, 474 pending_review, 43 legacy_overlap_review, 2,108 legacy_only**. Current pending counts by book: Acts 91; Luke 54; Matthew 49; Revelation 34; Colossians 33; Mark 30; John 25; 1 Corinthians 21; Romans 20; 2 Corinthians 17; Hebrews 16; 1 Timothy 15; 1 Thessalonians 12; Philippians 12; 2 Peter 10; James 8; Jude 6; 1 Peter 5; 1 John 4; 2 John 4; 2 Timothy 3; Titus 3; Philemon 2.

The largest remaining verse clusters are 1 Corinthians 5:11 (12), Acts 26:20 (11), Revelation 7:2 (11), Acts 4:32 (10), Acts 21:8 (10), and Acts 22:25 (9). Acts 19:27 now has three pending tokens at token-review level; these are supplied English article/copula cases with alignment-level not_expressed dispositions.

The 466 generic rows remain unadjudicated. “No direct proposal identified” is not a finding of `not_expressed` and must not be treated as one.

Full shadow validation passed after the Acts 19:27 update. See the [Acts 19:27 case report](ACTS_19_27_DENSE_PHRASE_ALIGNMENT_CASE_20261107.md), [latest full validation](FINAL_VALIDATION_AFTER_ACTS_19_27_20261107.txt), and refreshed [474-row pending-token export](YLT_TOKEN_REVIEW_QUEUE_CURRENT_20261107.csv).

Production tables, legacy renderings, embeddings, vectorizer, API, and deployment remain unchanged.


## Historical queue status after 1 Corinthians 5:11 (superseded by Acts 26:20 review)

The current YLT-profile token-review queue contains **464 pending tokens across 116 verses**. Reason counts:

| Reason | Count |
|---|---:|
| No direct proposal identified in this review set | 454 |
| Branch-dependent “also” (Acts 15:32) | 1 |
| Supplied copula “be” (Romans 16:27) | 1 |
| Supplied English article “the” (Romans 16:27) | 1 |
| Supplied subject pronoun “he” (1 John 2:23) | 1 |
| Supplied copula “are” (Revelation 9:20; alignment-level not_expressed) | 1 |
| Supplied article “the” (Acts 19:27; alignment-level not_expressed) | 1 |
| Supplied copula “is” (Acts 19:27; alignment-level not_expressed) | 2 |
| Bracketed supplied pronoun “[him]” (1 Corinthians 5:11; alignment-level not_expressed) | 1 |
| Supplied article “a” (1 Corinthians 5:11; alignment-level not_expressed) | 1 |

Current YLT-token status totals: **556 proposed, 464 pending_review, 43 legacy_overlap_review, 2,108 legacy_only**. Current pending counts by book: Acts 91; Luke 54; Matthew 49; Revelation 34; Colossians 33; Mark 30; John 25; Romans 20; 2 Corinthians 17; Hebrews 16; 1 Timothy 15; 1 Thessalonians 12; Philippians 12; 1 Corinthians 11; 2 Peter 10; James 8; Jude 6; 1 Peter 5; 1 John 4; 2 John 4; 2 Timothy 3; Titus 3; Philemon 2.

The largest remaining verse clusters are Acts 26:20 (11), Revelation 7:2 (11), Acts 4:32 (10), Acts 21:8 (10), and Acts 22:25 (9). 1 Corinthians 5:11 now has two token-table pending cases, both with alignment-level not_expressed dispositions: bracketed “[him]” and supplied “a”. The same verse also has a proposed YLT-specific branch-B selection for Robinson group 46:2 (ᾖ, “may be”); the CrossWire/KJV profile remains branch A.

The 454 generic rows remain unadjudicated. “No direct proposal identified” is not a finding of `not_expressed` and must not be treated as one.

Full shadow validation passed after the 1 Corinthians 5:11 update. See the [1 Corinthians 5:11 case report](FIRST_CORINTHIANS_5_11_DENSE_PHRASE_ALIGNMENT_CASE_20261107.md), [latest full validation](FINAL_VALIDATION_AFTER_1CO_5_11_20261107.txt), and refreshed [464-row pending-token export](YLT_TOKEN_REVIEW_QUEUE_CURRENT_20261107.csv).

Production tables, legacy renderings, embeddings, vectorizer, API, and deployment remain unchanged.


## Current queue status after Acts 26:20 (2026-11-07)

The current YLT-profile token-review queue contains **455 pending tokens across 116 verses**. Reason counts:

| Reason | Count |
|---|---:|
| No direct proposal identified in this review set | 443 |
| Acts 15:32 branch-dependent “also” | 1 |
| Romans 16:27 supplied copula “be” | 1 |
| Romans 16:27 supplied English article “the” | 1 |
| 1 John 2:23 supplied subject pronoun “he” | 1 |
| Revelation 9:20 supplied copula “are” | 1 |
| Acts 19:27 supplied article “the” | 1 |
| Acts 19:27 supplied copula “is” | 2 |
| 1 Corinthians 5:11 bracketed supplied pronoun “[him]” | 1 |
| 1 Corinthians 5:11 supplied article “a” | 1 |
| Acts 26:20 supplied “to” in “to those in Jerusalem” | 1 |
| Acts 26:20 supplied “those” in “to those in Jerusalem” | 1 |

Current YLT-token status totals: **565 proposed, 455 pending_review, 43 legacy_overlap_review, 2,108 legacy_only**. Current pending counts by book: Acts 82; Luke 54; Matthew 49; Revelation 34; Colossians 33; Mark 30; John 25; Romans 20; 2 Corinthians 17; Hebrews 16; 1 Timothy 15; 1 Thessalonians 12; Philippians 12; 1 Corinthians 11; 2 Peter 10; James 8; Jude 6; 1 Peter 5; 1 John 4; 2 John 4; 2 Timothy 3; Titus 3; Philemon 2.

The largest remaining verse clusters are Revelation 7:2 (11), Acts 4:32 (10), Acts 21:8 (10), Acts 22:25 (9), and 2 Corinthians 6:15 (8). Acts 26:20 now has two token-table pending cases (“to” and “those” in the expanded Jerusalem phrase), both with alignment-level not_expressed dispositions. The verse also has a proposed YLT-specific branch-B selection for Robinson group 44:36 (ἀπήγγελλον, first-person imperfect), while the CrossWire/KJV profile remains branch A.

The 443 generic rows remain unadjudicated. “No direct proposal identified” is not a finding of `not_expressed` and must not be treated as one.

Full shadow validation passed after Acts 26:20 and the subsequent Revelation 9:20 variant-dependency metadata correction. See the [Acts 26:20 case report](ACTS_26_20_DENSE_PHRASE_ALIGNMENT_CASE_20261107.md), [latest full validation](FINAL_VALIDATION_AFTER_RE9_20_DEPENDENCY_FIX_20261107.txt), and refreshed [455-row pending-token export](YLT_TOKEN_REVIEW_QUEUE_CURRENT_20261107.csv).

Production tables, legacy renderings, embeddings, vectorizer, API, and deployment remain unchanged.
