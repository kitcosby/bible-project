# Five contextual function-token proposals

**Date:** 2026-11-06  
**Environment:** Isolated PostgreSQL database bible_greek_bridge_test_20261106, schema ylt_profile_shadow.  
**Production impact:** None. All five changes are shadow-only proposals.

## Summary

A full-verse review identified five cases where the existing Greek-only alignment row could be paired with a specific YLT token. These are not all simple lexical glosses: three are phrase-member/grammatical correspondences and two are direct function-word correspondences.

| Reference | Greek profile position | Greek | YLT token position | YLT | Kind | Confidence |
|---|---:|---|---:|---|---|---|
| Matthew 2:23 | 10 | τό | 15 | that | phrase_member | moderate |
| Acts 26:20 | 2 | τοῖς | 3 | those | function_word | high |
| 1 Corinthians 13:2 | 7 | τά | 9 | the | function_word | high |
| Jude 1:24 | 1 | τῷ | 3 | Him | phrase_member | moderate |
| Acts 26:18 | 29 | τῇ | 37 | that | phrase_member | moderate |

## Case reasoning

### Matthew 2:23 — τό → “that”

The Greek construction is τὸ ῥηθέν, a substantivized participle, rendered by YLT “that was spoken”. The article contributes to the nominal/relative head “that”; ῥηθέν supplies “was spoken”. This is a phrase-member proposal, not a claim that τό independently means the English relative pronoun in all contexts.

### Acts 26:20 — τοῖς → “those”

The construction τοῖς ἐν Δαμασκῷ is rendered “to those in Damascus”. The substantival article is represented by the English “those”. This is a high-confidence function-word correspondence.

### 1 Corinthians 13:2 — τά → “the”

The Greek phrase is τὰ μυστήρια πάντα. YLT has “all the secrets”: πάντα contributes “all”, μυστήρια contributes “secrets”, and τά corresponds to the explicit English article “the”. Greek and English word order differ, but the token correspondence is clear.

### Jude 1:24 — τῷ → “Him”

The construction τῷ δυναμένῳ is rendered “to Him who is able”. The article substantivizes the participle; YLT expresses that nominal head as “Him”, while the participle supplies “who is able”. This is a moderate-confidence phrase-member proposal.

### Acts 26:18 — τῇ → “that”

The phrase is πίστει τῇ εἰς ἐμέ, rendered “by faith that is toward me”. The article introduces the attributive prepositional phrase, and YLT expresses that function with “that”. This is a moderate-confidence phrase-member proposal.

## Shadow changes

The five existing Greek-only alignment rows were updated in place, preserving their alignment IDs and source artifact lineage. Their targets, kinds, review statuses, confidence values, notes, and source record keys were updated. Each corresponding gnt_token_review row was changed from pending_review / zero proposals to proposed / one proposal.

The sequence dependency remains provisional_candidate_sequence. These are proposals for review, not accepted production mappings.

## Validation

After the five proposals:
- Full shadow validator: VALIDATION PASSED.
- Legacy overlap validator: FINAL OVERLAP CHECK PASSED.
- ylt_greek_alignment: 552 rows; 519 proposed, 20 not_expressed, 13 unresolved.
- gnt_token_review: 477 proposed, 33 pending_review, 25 legacy_overlap_review.
- Missing alignment targets: 0.
- Incomplete proposed endpoints: 0.
- Orphan alignment groups: 0.
- Production gnt_words: 141,009.
- Production gnt_ylt_renderings: 143,227.

No production tables, legacy associations, embeddings, vectorizer settings, API, merge, or deployment were changed.

The latest 39-row export is [GREEK_TOKEN_REVIEW_QUEUE_POST_CONTEXT_PROPOSALS_20261106.csv](GREEK_TOKEN_REVIEW_QUEUE_POST_CONTEXT_PROPOSALS_20261106.csv). It records 33 pending rows and six proposals, including the earlier Acts 5:12 διά → “through” correction.
