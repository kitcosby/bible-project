# Validation of Applied Revelation 9:20 Phrase Proposals

**Date:** 2026-11-07  
**Target:** `bible_greek_bridge_test_20261106.ylt_profile_shadow`  
**YLT alignment profile:** 4  
**Greek sequence profile:** 3  
**Scope:** Read-only validation of the Revelation 9:20 proposals already inserted in the isolated shadow database.

## Result

**Structural validation passed; textual approval remains conditional.**

All 15 intended phrase-member endpoints exist exactly once, with the expected Greek and YLT positions, phrase-group IDs, and `proposed` status. The supplied English copula “are” (YLT token 52) exists exactly once as an alignment-level `unaligned_ylt/not_expressed` record, with no Greek endpoint. The YLT token-review rows for the 15 phrase members are `proposed`; “are” remains `pending_review` in that table because the token-review schema has no `not_expressed` status.

The latest full v11 shadow validator, run after the subsequent Acts 19:27 work, passed. It reports 56 alignment groups and 635 alignment rows. This validates the database invariants and counts; it does not establish the textual correctness of an inherited variant selection.

## Endpoint audit

| Greek position | Greek form | YLT position | YLT token | Group | Result |
|---:|---|---:|---|---|---|
| 14 | μετενόησαν | 14 | did | RE-9:20-did-reform | Exactly one proposed row |
| 23 | προσκυνήσωσιν | 24 | may | RE-9:20-may-bow-before | Exactly one proposed row |
| 23 | προσκυνήσωσιν | 26 | bow | RE-9:20-may-bow-before | Exactly one proposed row |
| 23 | προσκυνήσωσιν | 27 | before | RE-9:20-may-bow-before | Exactly one proposed row |
| 28 | τὰ | 32 | those | RE-9:20-material-gold | Exactly one proposed row |
| 31 | τὰ | 36 | those | RE-9:20-material-silver | Exactly one proposed row |
| 32 | ἀργυρά | 37 | of | RE-9:20-material-silver | Exactly one proposed row |
| 34 | τὰ | 40 | those | RE-9:20-material-brass | Exactly one proposed row |
| 35 | χαλκά | 41 | of | RE-9:20-material-brass | Exactly one proposed row |
| 37 | τὰ | 44 | those | RE-9:20-material-stone | Exactly one proposed row |
| 38 | λίθινα | 45 | of | RE-9:20-material-stone | Exactly one proposed row |
| 40 | τὰ | 48 | those | RE-9:20-material-wood | Exactly one proposed row |
| 44 | βλέπειν | 55 | to | RE-9:20-to-see | Exactly one proposed row |
| 47 | ἀκούειν | 58 | to | RE-9:20-to-hear | Exactly one proposed row |
| 49 | περιπατεῖν | 61 | to | RE-9:20-to-walk | Exactly one proposed row |

The verse contains 11 phrase groups created for this case: ten phrase groups for the 15 proposed links and one group for the supplied copula disposition. The case contributes 16 alignment rows in total.

## Supplied copula

YLT token 52 (“are”) is recorded as:
- `alignment_kind = unaligned_ylt`
- `review_status = not_expressed`
- `confidence = high`
- `gnt_position = NULL`
- source record key `re9:20:y52:unaligned`

Its YLT token-review status remains `pending_review`, with a reason explaining the alignment-level disposition. This is an intentional two-layer distinction, not a failed update.

## Legacy preservation

A read-only comparison of the current production legacy rendering rows for Revelation 9:20 confirms that the legacy table remains available separately from the new shadow proposals. The applied proposal script only inserts shadow alignment/group rows and updates shadow review tables; it does not update `public.gnt_ylt_renderings`.

The current verse has 52 legacy rendering rows. The legacy Greek-position map was inspected for all 49 positions. Existing links to “reform”, “that”, “not”, the material words, “able”, and “see/hear/walk” remain represented in the legacy table. The new phrase-member rows supplement those legacy links; they do not replace them.

## Important textual dependency: Robinson group 66:18

The applied sequence is not independent of textual-variant selection.

Robinson group `66:18`, at Revelation 9:20, has:
- Branch A: `oute 3777 {CONJ-N}`
- Branch B: `ou 3756 {PRT-N}`

Profile 2 (the KJV candidate) selected B algorithmically. Profile 3 (the YLT candidate) inherited B with status `inherited_provisional`, explicitly described as a provisional fallback rather than a YLT editorial decision. The Robinson source profile (profile 1) remains `unreviewed`.

The 15 newly added phrase-member rows carry the `66:18` variant dependency where the endpoint is directly affected by the branch sequence. Their sequence dependency is `provisional_candidate_sequence`. Consequently:

- The **phrase-level mapping is structurally verified conditional on the current profile-3 B sequence**.
- It is **not yet a final YLT-specific textual decision**.
- The full verse sequence and all affected alignments must be re-evaluated if branch A is selected.
- The existing algorithmic B selection must not be described as proof that Young followed B.

This is the principal caveat discovered by the independent audit. The earlier case report should be read with this qualification.

## Latest full validation

The full validator run after Acts 19:27 reports:

- Alignment groups: 56.
- Alignment rows: 635 (591 proposed, 36 not_expressed, 7 legacy_overlap_review, 1 unresolved).
- YLT token review: 546 proposed, 474 pending_review, 43 legacy_overlap_review, 2,108 legacy_only.
- Greek token review: 525 proposed, 33 pending_review, 31 legacy_overlap_review.
- Production counts unchanged: 141,009 `gnt_words`; 143,227 `gnt_ylt_renderings`; 31,102 YLT verses; 31,102 non-null stored embeddings.

See [latest full validator output](FINAL_VALIDATION_AFTER_ACTS_19_27_20261107.txt).

## Classification

- **Verified structural facts:** endpoint uniqueness, expected group membership, proposal statuses, supplied-copula row, and successful full shadow validator.
- **Verified conditional derivation:** phrase mapping against the current profile-3 B sequence.
- **Provisional textual dependency:** Robinson group 66:18 branch B is inherited from an algorithmic KJV candidate selection.
- **Not established:** that branch B is the YLT reading, or that Young’s translation independently resolves the A/B textual variant.
- **Production:** unchanged. No production DDL/DML, legacy-link update, embedding/vectorizer change, API change, merge, or deployment occurred during this audit.

## Recommended next step

Before treating the Revelation 9:20 proposals as approved, review Robinson group 66:18 against the YLT wording and independent textual witnesses, then generate the alternative branch-A sequence and compare every affected Greek position. Retain both branch-conditioned alignments if the source evidence does not establish one reading.