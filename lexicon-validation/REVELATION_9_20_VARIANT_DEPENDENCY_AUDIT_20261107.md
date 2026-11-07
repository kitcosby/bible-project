# Revelation 9:20 — Variant-Dependency Audit and Applied Proposal Validation

**Date:** 2026-11-07  
**Database:** `bible_greek_bridge_test_20261106` (isolated shadow database)  
**Alignment profile:** 4 (YLT)  
**Sequence profile:** 3 (YLT candidate, provisional inheritance)  
**Status:** Structural validation passed; textual choice at Robinson group 66:18 remains open.

## Executive result

The 15 phrase-member proposals already applied to Revelation 9:20 are structurally valid and remain positionally stable under either branch of Robinson group `66:18`. The two alternatives are both single-token readings:

- A: `oute 3777 {CONJ-N}` — οὔτε
- B: `ou 3756 {PRT-N}` — οὐ

The current YLT candidate sequence uses B, inherited provisionally from the KJV candidate. A branch-A simulation changes exactly one sequence token, at Greek position 13, and changes no token count or later position. All 15 phrase-member endpoints occur after that point and retain the same Greek surface, position, YLT target, and phrase group under either branch.

The directly affected alignment is Greek position 13 → YLT token 13 (“neither”). The database previously had the dependency metadata backwards: the 15 later phrase rows were tagged with `66:18`, while this directly affected position-13 row was not. This metadata has been corrected in the shadow database only.

## Branch A/B comparison

| Attribute | Branch A | Branch B |
|---|---|---|
| Normalized source | `oute 3777 {CONJ-N}` | `ou 3756 {PRT-N}` |
| Greek surface | οὔτε | οὐ |
| Strong’s | G3777 | G3756 |
| Morphology | CONJ-N | PRT-N |
| Token count | 1 | 1 |
| Sequence position | 13 | 13 |

Deterministic comparison against the profile-3 sequence:
- Token-count delta: **0**.
- Changed sequence positions: **one**, position 13 (οὐ → οὔτε).
- Later positions: unchanged.
- All 15 phrase-member proposal endpoints: unchanged.

This is a one-token substitution, not an insertion/deletion. No positional shift should be applied to the rest of the verse when testing branch A.

## Directly affected alignment

The current branch-B sequence has οὐ at position 13, aligned to YLT “neither” (token 13). Under branch A, the same position would contain οὔτε. This is the one alignment row whose Greek lexical identity changes when the branch changes.

The YLT wording “neither did reform” may be a natural English rendering under either reading, but it does not by itself decide the Greek variant. The lexical match between οὔτε and “neither” is more direct; οὐ can also participate in a negative construction rendered idiomatically as “neither did …”. The textual choice therefore remains unresolved pending independent witness and source review.

## The 15 phrase-member endpoints

All endpoints were rechecked after the dependency correction:

| Greek position | Greek form | YLT position | YLT token | Phrase group |
|---:|---|---:|---|---|
| 14 | μετενόησαν | 14 | did | RE-9:20-did-reform |
| 23 | προσκυνήσωσιν | 24 | may | RE-9:20-may-bow-before |
| 23 | προσκυνήσωσιν | 26 | bow | RE-9:20-may-bow-before |
| 23 | προσκυνήσωσιν | 27 | before | RE-9:20-may-bow-before |
| 28 | τὰ | 32 | those | RE-9:20-material-gold |
| 31 | τὰ | 36 | those | RE-9:20-material-silver |
| 32 | ἀργυρά | 37 | of | RE-9:20-material-silver |
| 34 | τὰ | 40 | those | RE-9:20-material-brass |
| 35 | χαλκά | 41 | of | RE-9:20-material-brass |
| 37 | τὰ | 44 | those | RE-9:20-material-stone |
| 38 | λίθινα | 45 | of | RE-9:20-material-stone |
| 40 | τὰ | 48 | those | RE-9:20-material-wood |
| 44 | βλέπειν | 55 | to | RE-9:20-to-see |
| 47 | ἀκούειν | 58 | to | RE-9:20-to-hear |
| 49 | περιπατεῖν | 61 | to | RE-9:20-to-walk |

Each endpoint exists exactly once as a proposed phrase-member row. The proposals remain phrase-level mappings: for example, the subjunctive προσκυνήσωσιν is expressed by “may bow before”, and the infinitives βλέπειν, ἀκούειν, and περιπατεῖν include the English infinitive marker “to”.

## Dependency metadata correction

In `ylt_profile_shadow.ylt_greek_alignment`:

- Removed the false-positive `66:18` dependency from the 15 phrase-member rows.
- Added `66:18` to the position-13 function-word alignment (Greek οὐ → YLT “neither”).
- Retained `sequence_dependency_status = provisional_candidate_sequence` for all these rows. This status describes the provisional nature of the selected sequence profile, not direct sensitivity of every token to this particular variant.

Post-update inspection confirms one direct alignment dependency on `66:18`, at position 13. The 15 phrase-member endpoints have empty direct variant-dependency arrays.

## Supplied copula and legacy preservation

The supplied English “are” remains an alignment-level `unaligned_ylt/not_expressed` record, with no Greek endpoint. Its token-review row remains pending because the token-review table does not support a `not_expressed` token status.

The 15 phrase proposals supplement rather than overwrite the existing legacy rendering rows. No production legacy association was modified.

## Latest full validation (v13)

The full v13 validator passed after the dependency metadata correction:

- 261 Robinson variant groups; 522 raw branch payloads; 783 profile selection rows.
- 2,444 profile-3 Greek sequence words; 3,171 YLT tokens.
- 73 alignment groups; 658 alignment rows.
- Alignment rows: 610 proposed, 40 not_expressed, 7 legacy_overlap_review, 1 unresolved.
- YLT token review: 565 proposed, 455 pending_review, 43 legacy_overlap_review, 2,108 legacy_only.
- Greek token review: 537 proposed, 32 pending_review, 31 legacy_overlap_review.
- The `66:18` dependency group now has exactly one directly dependent alignment row.
- Production counts unchanged: 141,009 `gnt_words`; 143,227 `gnt_ylt_renderings`; 31,102 YLT verses; 31,102 non-null embeddings.

Full output: [FINAL_VALIDATION_AFTER_RE9_20_DEPENDENCY_FIX_20261107.txt](FINAL_VALIDATION_AFTER_RE9_20_DEPENDENCY_FIX_20261107.txt).

## Backup and provenance

- Pre-correction shadow backup: `/var/backups/bible-postgres-20261106T171837Z/bible_greek_bridge_test_ylt_profile_shadow_20261107_pre_re9_20_dependency_fix.dump`
  - SHA-256: `fbb31cc03fa97214b0c266f9c4e7762dc7163bf06b11f503325b0e69df4e6281`
- Post-correction shadow backup: `/var/backups/bible-postgres-20261106T171837Z/bible_greek_bridge_test_ylt_profile_shadow_20261107_after_re9_20_dependency_fix.dump`
  - SHA-256: `5faf5fc812426e825e39aabe69c8f7cd1a2b1219376b3beb55063a554f9f7779`

## Evidence classification and next investigation

- **Verified structural result:** 15 unique phrase-member endpoints; one supplied-copula disposition; successful v13 full validator; unchanged production counts.
- **Verified sequence derivation:** branch A and B each contain one token; the only changed position is 13; later phrase endpoints are stable.
- **Provisional:** profile 3 currently inherits branch B from an algorithmically selected KJV candidate.
- **Open textual question:** whether the YLT should be represented with οὐ or οὔτε at position 13. The YLT English “neither” alone is insufficient to decide this.
- **Next:** inspect the Robinson source context and independent Greek witnesses for Revelation 9:20, document the textual evidence, and retain both branch-conditioned readings if the evidence does not establish a unique YLT choice.

No production DDL/DML, legacy rendering update, embedding generation, vectorizer change, API change, merge, or deployment occurred.