# Validation of Applied Revelation 9:20 Phrase Proposals

**Date:** 2026-11-07  
**Target:** `bible_greek_bridge_test_20261106.ylt_profile_shadow`  
**YLT alignment profile:** 4  
**Greek sequence profile:** 3  
**Scope:** Validation of the applied Revelation 9:20 proposals, branch-A/branch-B sequence comparison, and shadow-only correction of variant-dependency metadata.

## Result

**Structural validation passed; textual approval remains conditional.**

All 15 intended phrase-member endpoints exist exactly once, with the expected Greek and YLT positions, phrase-group IDs, and `proposed` status. The supplied English copula “are” (YLT token 52) exists exactly once as an alignment-level `unaligned_ylt/not_expressed` record, with no Greek endpoint. The YLT token-review rows for the 15 phrase members are `proposed`; “are” remains `pending_review` in that table because the token-review schema has no `not_expressed` status.

The latest full v13 shadow validator passed after the branch-dependency metadata correction. It reports 73 alignment groups and 658 alignment rows. This validates the database invariants and counts; it does not establish the textual correctness of an inherited variant selection. See the [branch-dependency audit](REVELATION_9_20_VARIANT_DEPENDENCY_AUDIT_20261107.md) for the exact branch-A/B comparison.

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

A branch-A/branch-B sequence comparison showed that both alternatives contain one token, so the only changed Greek position is position 13 (οὐ ↔ οὔτε). The 15 phrase-member endpoints occur after that position and remain positionally identical under either branch. The directly affected alignment is Greek position 13 → YLT token 13 (“neither”).

The first metadata pass had attached `66:18` to the 15 later phrase rows and omitted it from the position-13 row. This was corrected in the shadow database: the 15 phrase rows now have no direct `66:18` dependency, and the position-13 row carries it. `sequence_dependency_status = provisional_candidate_sequence` remains on the rows because profile 3 itself still inherits branch B provisionally.

Consequently:
- The **15 phrase-level endpoints are structurally verified and positionally stable under either branch**.
- The **lexical choice for YLT “neither” at position 13 remains variant-dependent and unresolved**.
- The current branch-B selection is **not** a YLT-specific textual decision.
- No later positional remapping is required if branch A is selected; re-evaluate the lexical identity and gloss at position 13.

## Latest full validation

The full v13 validator after the Revelation 9:20 dependency correction reports:

- Alignment groups: 73.
- Alignment rows: 658 (610 proposed, 40 not_expressed, 7 legacy_overlap_review, 1 unresolved).
- YLT token review: 565 proposed, 455 pending_review, 43 legacy_overlap_review, 2,108 legacy_only.
- Greek token review: 537 proposed, 32 pending_review, 31 legacy_overlap_review.
- Direct `66:18` dependency rows: exactly one, at Greek position 13.
- Production counts unchanged: 141,009 `gnt_words`; 143,227 `gnt_ylt_renderings`; 31,102 YLT verses; 31,102 non-null stored embeddings.

See [latest full validator output](FINAL_VALIDATION_AFTER_RE9_20_DEPENDENCY_FIX_20261107.txt) and the [branch-dependency audit](REVELATION_9_20_VARIANT_DEPENDENCY_AUDIT_20261107.md).

## Classification

- **Verified structural facts:** endpoint uniqueness, expected group membership, proposal statuses, supplied-copula row, and successful full shadow validator.
- **Verified derivation:** the 15 phrase endpoints remain positionally stable under either one-token branch; only position 13 changes.
- **Provisional textual selection:** Robinson group 66:18 branch B is inherited from an algorithmic KJV candidate selection.
- **Not established:** that branch B is the YLT reading, or that Young’s translation independently resolves the A/B textual variant.
- **Production:** unchanged. No production DDL/DML, legacy-link update, embedding/vectorizer change, API change, merge, or deployment occurred during this audit.

## Recommended next step

The branch-A sequence comparison is complete. Next, review Robinson group 66:18 against independent Greek witnesses and the YLT wording to determine whether οὐ or οὔτε is the better-supported reading. Retain both branch-conditioned readings if the evidence does not establish one YLT-specific choice.