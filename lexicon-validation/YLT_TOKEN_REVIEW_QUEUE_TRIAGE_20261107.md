# YLT Token Review Queue — Triage Notes and Corner Cases

**Prepared:** 2026-11-07  
**Environment:** Isolated database bible_greek_bridge_test_20261106, schema ylt_profile_shadow.  
**Scope:** Current YLT-profile token rows with ylt_token_review.review_status = pending_review.

## Current queue shape

The current queue contains **503 YLT tokens** across 23 New Testament books. The review-reason field divides them as follows:

| Reason | Count | Interpretation |
|---|---:|---|
| No direct proposal identified in this review set. | 500 | No candidate was recorded by the current review workflow. This does not mean the token was examined and proved to have no Greek counterpart. |
| Bracketed supplied copula; no Greek finite verb is present. | 1 | Romans 16:27, “be”. |
| English article added before “only wise God”; no Greek article occurs in this sequence. | 1 | Romans 16:27, “the”. |
| English subject pronoun supplied with third-person ἔχει; no independent Greek pronoun occurs. | 1 | 1 John 2:23, “he” in “neither hath he the Father”. |

The 500 generic rows remain a candidate-discovery queue. They should not be automatically classified as unexpressed, nor should their count be presented as 500 unresolved alignments: many may already have legacy relationships or may require phrase-level treatment.

## Three explicit grammatical corner cases

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

## Largest current pending clusters

These are useful review batches, not evidence that every token in a verse has the same problem.

| Reference | Pending YLT tokens |
|---|---:|
| Revelation 9:20 | 16 |
| Acts 19:27 | 13 |
| 1 Corinthians 5:11 | 12 |
| Acts 26:20 | 12 |
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
| Acts | 103 |
| Luke | 54 |
| Matthew | 50 |
| Revelation | 49 |
| Colossians | 33 |
| Mark | 30 |
| John | 25 |
| 1 Corinthians | 22 |
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
6. Do not infer that the 500 generic pending rows are all missing Greek equivalents; they have not yet been individually adjudicated by this review.

## Scope and safeguards

This is a read-only triage of existing shadow rows. No YLT token-review status, alignment endpoint, legacy association, production table, embedding, vectorizer, API, or deployment was changed. The exact 503-row pending queue is represented by the database status at export time; this report gives the reason distribution and review priorities, not a replacement for the row-level queue.