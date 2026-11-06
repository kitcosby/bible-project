# YLT shadow profile v0.1

Status: research artifact only; no branch selections applied to any database.

## Profile purpose

This file separates YLT-specific proposed branch selections from the existing KJV-alignment candidate. It preserves raw A/B alternatives and provenance for all low-margin groups. It does not assert that a proposed YLT-aligned reading is the earliest or best-attested reading.

## Scope and counts

- Low-margin components: 108
- Verse contexts: 116
- Raw branch groups: 118
- Proposed branch selections: 15
- Prior proposals retracted: 2
- Held unresolved: 2
- Not yet decided: 99

## Status semantics

- proposed_not_applied: a YLT profile branch is proposed but not applied.
- held_unresolved: alternatives retained without selection.
- prior_proposal_retracted_pending_review: a prior proposed change was withdrawn after further grammatical or clause-level review.
- not_yet_decided_for_ylt_profile: do not inherit the KJV candidate branch.

## Important limitation

The legacy rendering rows were generated through YLT→KJV alignment and then KJV→Greek positions. They are not independent YLT lexical evidence. A future renderer must carry profile_id and explicit unaligned-token reasons.