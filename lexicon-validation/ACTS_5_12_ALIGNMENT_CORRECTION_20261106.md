# Acts 5:12 — direct preposition alignment correction

**Date:** 2026-11-06  
**Environment:** Isolated PostgreSQL database bible_greek_bridge_test_20261106, schema ylt_profile_shadow.  
**Production impact:** None. This change is shadow-only.

## Finding

The earlier function-word review record for Acts 5:12 described Greek διά at YLT-profile Greek position 1 as having “no distinct YLT preposition token safely isolated” and left it unresolved.

Full-verse inspection disproves that assessment.

- YLT: “And **through** the hands of the apostles came many signs and wonders…”
- YLT token position 2: **through**
- YLT-profile Greek sequence position 1: **διά** (G1223, PREP)
- Greek phrase: διὰ τῶν χειρῶν τῶν ἀποστόλων
- English phrase: “through the hands of the apostles”

The correspondence is direct and unambiguous at the preposition level. The article/noun sequence that follows does not make διά idiomatic or unexpressed.

## Shadow-only correction

The existing Greek-only alignment row was updated in place, preserving its alignment ID:

| Field | Before | After |
|---|---|---|
| alignment_id | 466 | 466 |
| YLT target | null | verse 27281, token position 2 |
| YLT surface | — | through |
| Greek target | verse 3927, position 1 | unchanged |
| Greek surface | διά | διά |
| alignment_kind | unaligned_greek | function_word |
| review_status | unresolved | proposed |
| confidence | unresolved | high |
| source_record_key | function:192:pending | function:192:ylt:2 |

The corresponding gnt_token_review row was updated from pending_review / 0 proposed alignments to proposed / 1 proposed alignment. The rationale records the exact verse-level correspondence.

This is a proposal, not an accepted production mapping. The YLT profile sequence dependency remains provisional_candidate_sequence.

## Validation

The transaction asserted before writing that:
- the exact Greek-only row existed and was unresolved;
- the target YLT token existed and had surface “through”;
- no prior alignment row already linked that YLT token;
- the exact profile IDs were alignment profile 4 and YLT sequence profile 3.

After the update, the script read back the exact pair and asserted:
- YLT token 2 = “through”;
- Greek sequence position 1 = διά;
- alignment_kind = function_word;
- review_status = proposed;
- confidence = high;
- gnt_token_review = proposed with proposed_alignment_count 1.

Both existing validation scripts passed after the change:
- final_validate_ylt_profile_shadow.py — VALIDATION PASSED.
- final_validate_legacy_overlap_review.py — FINAL OVERLAP CHECK PASSED.

Updated shadow counts:
- ylt_greek_alignment: 552 rows (unchanged); proposed 514, unresolved 16, not_expressed 22.
- gnt_token_review: proposed 472, pending_review 38, legacy_overlap_review 25.
- No missing alignment targets, incomplete proposed endpoints, or orphan alignment groups.

Production baseline remained unchanged: gnt_words 141,009; gnt_ylt_renderings 143,227. No production DDL/DML, embeddings, vectorizer, API, merge, or deployment changes were made.

## Follow-up

The current 39-row queue snapshot now records one proposed row and 38 still pending. The original raw and pre-correction reconciled snapshots are retained as historical exports. Continue reviewing the remaining 38 pending function-word rows in verse context; do not infer that the other earlier “not_expressed” classifications are final, since their confidence remains unresolved.
