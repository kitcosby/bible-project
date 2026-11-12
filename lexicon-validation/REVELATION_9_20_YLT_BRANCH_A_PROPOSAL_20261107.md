# Revelation 9:20 — YLT Branch-A Proposal

**Date:** 2026-11-07  
**Database:** `bible_greek_bridge_test_20261106` (isolated shadow database)  
**YLT alignment profile:** 4  
**YLT sequence profile:** 3  
**Status:** Branch A proposed; exact historical TR edition used by Young remains unidentified.

## Decision

The YLT candidate profile now proposes Robinson group `66:18` branch A:

- A: οὔτε — `G3777`, `CONJ-N`
- B: οὐ — `G3756`, `PRT-N`

This is a **YLT-specific proposal**, not a final textual-critical verdict. The selection was changed from inherited provisional B to proposed A in the isolated shadow database. The CrossWire/KJV candidate remains branch B with its existing algorithmic-selection status. The Robinson source profile remains unselected.

## Evidence for proposing A

1. **Young's own stated text basis.** The preface to Young's Revised Edition says: “The Greek Text followed is that generally recognized as the ‘Received Text’.” It also says that the translator did not intend to form a new Greek text and left textual criticism to others. The preface does not name a particular printed TR edition.
2. **Received-Text editions available before Young's death.** Stephanus 1550 and Beza 1598 both read `οὔτε μετενόησαν` at Revelation 9:20. Meyer also lists Elzevir among editions supporting οὔτε. These are direct examples of the Received-Text tradition available before the 1862 first edition and 1887 revision.
3. **YLT wording.** Young renders the clause “neither did reform”. Οὔτε is a direct negative conjunction naturally corresponding to “neither”; the choice is also consistent with Young's stated commitment to close rendering.
4. **External apparatus remains more complex.** The wider apparatus also records οὐ and οὐδέ. The third reading οὐδέ is absent from the two-branch Robinson parser payload and remains an external witness note, not a new parser branch.

The evidence makes A the best current YLT-profile candidate among the parser's two branches. It does not establish the exact TR edition used by Young or eliminate the external οὐδέ reading.

## Textual evidence and uncertainty

| Reading | Lexical / grammatical value | Witness / edition evidence |
|---|---|---|
| οὔτε | neither, nor; conjunction | Stephanus 1550; Beza 1598; Elzevir listed by Meyer |
| οὐ | not; negative particle | RP Byzantine Majority Text; Scrivener 1894; supported by C and other witnesses in apparatus |
| οὐδέ | nor, not even; conjunction | SBLGNT / NA family; listed with P47, א, 046 and other witnesses in apparatus |

The Robinson parser's A/B labels are local branch identifiers, not manuscript family labels. The external οὐδέ reading demonstrates that raw parser alternatives are not a complete critical apparatus. See [the three-reading apparatus review](REVELATION_9_20_THREE_READING_APPARATUS_REVIEW_20261107.md).

## Sequence and alignment effects

All three readings are one Greek token at position 13. Deterministic comparison confirms:
- A/B/C token-count delta: zero.
- The only lexical substitution is Greek position 13.
- Greek positions 14–49 do not shift.
- All 15 previously applied phrase-member endpoints remain unchanged under all three readings.

The YLT profile-3 sequence row at position 13 was updated in shadow only:
- surface: `ουτε`
- beta: `oute`
- Strong's: `G3777`
- morphology: `CONJ-N`
- sequence status: `proposed_ylt_branch`

The corresponding profile-3 selection is now branch A with status `proposed`. The alignment from Greek position 13 to YLT token 13 (“neither”) remains proposed at moderate confidence and retains direct dependency group `66:18`. Its notes record the textual evidence and caveat.

The 15 phrase-member rows are unchanged. Their direct `66:18` dependency arrays remain empty. Their sequence dependency status remains provisional because other inherited sequence choices still exist in profile 3.

## Validation v14

The full v14 validator passed after the branch-A proposal:

- 261 Robinson variant groups; 522 raw branch payloads; 783 profile-selection rows.
- YLT sequence profile: 2,444 Greek sequence words; 3,171 YLT tokens.
- 73 alignment groups; 658 alignment rows.
- Alignment rows: 610 proposed, 40 not_expressed, seven legacy_overlap_review, one unresolved.
- YLT token review: 565 proposed, 455 pending_review, 43 legacy_overlap_review, 2,108 legacy_only.
- Greek token review: 537 proposed, 32 pending_review, 31 legacy_overlap_review.
- Proposed YLT branch selections: eight, including Revelation 9:20 group 66:18 → A.
- Direct dependency rows for group 66:18: exactly one, at Greek position 13.
- Production counts unchanged: 141,009 `gnt_words`; 143,227 `gnt_ylt_renderings`; 31,102 YLT verses; 31,102 non-null embeddings.

See [FINAL_VALIDATION_AFTER_RE9_20_YLT_BRANCH_A_PROPOSAL_20261107.txt](FINAL_VALIDATION_AFTER_RE9_20_YLT_BRANCH_A_PROPOSAL_20261107.txt).

## Backup and provenance

- Pre-proposal shadow backup: `/var/backups/bible-postgres-20261106T171837Z/bible_greek_bridge_test_ylt_profile_shadow_20261107_pre_re9_20_ylt_branch_a_proposal.dump`
  - SHA-256: `3a006db505bac05f9acd175be982798fafeee8e021454851aa699ee9de334c1a`
- Post-proposal shadow backup: `/var/backups/bible-postgres-20261106T171837Z/bible_greek_bridge_test_ylt_profile_shadow_20261107_after_re9_20_ylt_branch_a_proposal.dump`
  - SHA-256: `d71dbdcab8ac322488fa693b10cbd19980bb9833aa30246a7883ce90bd770c93`

## Classification

- **Established:** Young's preface states a Received-Text basis; Stephanus 1550 and Beza 1598 read οὔτε; YLT renders “neither did reform”; all three variants are single-token alternatives; the v14 validator passes.
- **Proposed:** YLT profile branch A (οὔτε) is the best current candidate among the parser's two branches.
- **Unresolved:** exact printed Greek edition used by Young; how his “neither” relates to οὐδέ; whether the YLT's English wording uniquely identifies a specific Greek reading.
- **Not changed:** Robinson source payloads; CrossWire/KJV branch selection; production data, legacy renderings, embeddings, vectorizer, API, or deployment.

## Next investigation

Seek a primary copy of Young's 1862/1887 Greek source or his *Concise Critical Commentary* at Revelation 9:20. Until that is found, keep branch A proposed rather than final and retain οὐδέ as external apparatus evidence. If the exact source edition cannot be identified, preserve the unresolved textual caveat in the study guide.