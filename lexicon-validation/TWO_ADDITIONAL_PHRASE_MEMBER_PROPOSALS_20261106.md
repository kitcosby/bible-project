# Two additional phrase-member proposals

**Date:** 2026-11-06  
**Environment:** Isolated PostgreSQL database bible_greek_bridge_test_20261106, schema ylt_profile_shadow.  
**Production impact:** None. Both changes are shadow-only proposals.

## Summary

Two further full-verse reviews support phrase-member alignments. In both cases the Greek function word contributes to a larger English phrase rather than having a separate one-word gloss.

| Reference | Greek position | Greek | YLT token position | YLT | Kind | Confidence |
|---|---:|---|---:|---|---|---|
| Luke 2:39 | 5 | τά | 6 | things | phrase_member | moderate |
| Romans 16:20 | 13 | ἐν | 14 | quickly | phrase_member | moderate |

## Luke 2:39 — τά → “things”

The sequence is ἅπαντα τὰ κατὰ τὸν νόμον κυρίου. YLT renders this “all things, according to the Law of the Lord”. The pending article is not part of a phrase τὰ πάντα; that was an inaccurate initial cue. It follows ἅπαντα and substantivizes the following κατὰ phrase. YLT renders ἅπαντα as “all” and the nominalized phrase as “things according to the Law”. The article's contribution is therefore represented in the English word “things” at token position 6. This is a phrase-member proposal, not a lexical gloss for τά by itself.

## Romans 16:20 — ἐν → “quickly”

The phrase ἐν τάχει is an adverbial idiom rendered “quickly”. Greek τάχει at profile position 14 already has a high-confidence content-word proposal to YLT token 14, “quickly”. Greek ἐν at position 13 contributes to that same adverbial phrase. The existing Greek-only row was updated in place to a moderate-confidence phrase-member proposal to the same YLT token. This represents a multi-token Greek phrase to one English token; it is not a claim that ἐν alone means “quickly”.

## Shadow changes and validation

The two existing Greek-only alignment rows were updated in place, preserving their alignment IDs and source lineage. The corresponding gnt_token_review rows changed from pending_review / zero proposals to proposed / one proposal. Sequence dependency remains provisional_candidate_sequence.

After these two proposals:
- gnt_token_review: 479 proposed, 31 pending_review, 25 legacy_overlap_review.
- ylt_greek_alignment: 521 proposed, 20 not_expressed, 11 unresolved (552 total).
- Full shadow validator: VALIDATION PASSED.
- Legacy overlap validator: FINAL OVERLAP CHECK PASSED.
- No missing alignment targets, incomplete proposed endpoints, or orphan alignment groups.
- Production baselines unchanged: gnt_words 141,009; gnt_ylt_renderings 143,227.

The latest 39-row queue snapshot is [GREEK_TOKEN_REVIEW_QUEUE_POST_EIGHT_PROPOSALS_20261106.csv](GREEK_TOKEN_REVIEW_QUEUE_POST_EIGHT_PROPOSALS_20261106.csv): 31 pending rows and eight proposed rows. These remain proposals, not accepted production mappings.
