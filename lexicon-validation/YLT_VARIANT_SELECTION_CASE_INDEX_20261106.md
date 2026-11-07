# YLT Variant-Selection Case Index — 19 Formerly Unresolved Groups

**Prepared:** 2026-11-06; updated 2026-11-07  
**Environment:** Isolated database bible_greek_bridge_test_20261106, schema ylt_profile_shadow.  
**Scope:** The 19 YLT-profile variant-selection rows that were unresolved at the start of this review.  
**Companion snapshot for these 19 groups:** [YLT_VARIANT_SELECTIONS_CURRENT_20261106.csv](YLT_VARIANT_SELECTIONS_CURRENT_20261106.csv)  
**Current full-profile ledger:** [YLT_PROFILE_VARIANT_SELECTIONS_CURRENT_20261107.csv](YLT_PROFILE_VARIANT_SELECTIONS_CURRENT_20261107.csv)

## Executive result

The 19 groups divide into three materially different classes:

- **Five verse-text groups** can be selected against the stored YLT wording. Their YLT-profile selection rows are now marked reviewed_against_translation.
- **Thirteen groups** contain epistle subscriptions/colophons, not verse text. Their raw source payloads are preserved, but their YLT-profile selection rows are now marked not_applicable_to_verse_alignment.
- **One verse-text group** remains unresolved because the YLT English rendering does not distinguish the Greek aspect forms.

This resolves the selection-ledger ambiguity without forcing a decision for Revelation 7:3. The five selected verse-text branches have since been materialized in the isolated YLT-profile candidate sequence and validated against the stored YLT text. Revelation 7:3 remains deliberately unmaterialized until independent Greek textual evidence resolves the aspect distinction.

## A. Verse-text groups reviewed against YLT

| Group | Reference | Branch | Source difference | YLT evidence | Disposition |
|---|---|---|---|---|---|
| 43:6 | John 8:6 | A | A is empty; B adds μη … προσποιούμενος, an additional participial phrase. | The stored YLT verse ends “with the finger he was writing on the ground,” and does not render the extra branch-B phrase. | Select A for the YLT profile. |
| 44:3 | Acts 3:3 | A | A supplies λαβεῖν; B is empty. | YLT reads “was begging to receive a kindness”. | Select A. |
| 45:7 | Romans 16:27 | A | A supplies ᾧ; B is empty. | YLT reads “to him [be] glory to the ages”. | Select A. |
| 49:3 | Ephesians 6:24 | A | A supplies ἀμήν; B is empty. | YLT ends the verse with “Amen”. | Select A. |
| 62:3 | 1 John 2:23 | B | B supplies ὁ ὁμολογῶν τὸν υἱὸν καὶ τὸν πατέρα ἔχει; A is empty. | YLT includes the bracketed clause “he who is confessing the Son hath the Father also.” | Select B. |

These decisions are **translation-profile decisions**: they identify the Robinson branch that matches the stored YLT verse. They are not claims that the selected branch is universally the earliest or best-attested Greek reading.

## B. Subscription/colophon groups excluded from verse alignment

The following 13 source payloads are subscription or colophon material, generally identifying where an epistle was written or who carried it. The YLT verse text stored in public.ylt_verses does not include these subscription payloads. They must remain preserved in the raw source-variant tables but should not be inserted into the YLT verse token sequence.

| Group | Reference | Source payload type | YLT-profile disposition |
|---|---|---|---|
| 45:8 | Romans 16:27 | Written-from/by subscription, including Corinth and Phoebe | not_applicable_to_verse_alignment |
| 46:7 | 1 Corinthians 16:24 | Written-from/by subscription, including Philippi and named messengers | not_applicable_to_verse_alignment |
| 47:10 | 2 Corinthians 13:14 | Written-from/by subscription, including Philippi and named messengers | not_applicable_to_verse_alignment |
| 48:2 | Galatians 6:18 | Written-from subscription, Rome | not_applicable_to_verse_alignment |
| 49:4 | Ephesians 6:24 | Written-from/by subscription, Rome and Tychicus | not_applicable_to_verse_alignment |
| 50:4 | Philippians 4:23 | Written-from/by subscription, Rome and Epaphroditus | not_applicable_to_verse_alignment |
| 52:5 | 1 Thessalonians 5:28 | Written-from subscription, Athens | not_applicable_to_verse_alignment |
| 53:3 | 2 Thessalonians 3:18 | Written-from subscription, Athens | not_applicable_to_verse_alignment |
| 54:5 | 1 Timothy 6:21 | Written-from/by subscription, Laodicea and named persons | not_applicable_to_verse_alignment |
| 55:3 | 2 Timothy 4:22 | Written-from/by subscription, Rome and named persons | not_applicable_to_verse_alignment |
| 56:2 | Titus 3:15 | Written-from/by subscription, Nicopolis and named persons | not_applicable_to_verse_alignment |
| 57:2 | Philemon 1:25 | Written-from/by subscription, Rome and Onesimus | not_applicable_to_verse_alignment |
| 58:9 | Hebrews 13:25 | Written-to/from subscription, Italy and Timothy | not_applicable_to_verse_alignment |

The selected_branch field remains null for these groups. No source payload was deleted or rewritten. The status means “outside this verse-alignment task”, not “textually rejected”.

## C. One unresolved verse-text group

### Revelation 7:3 — group 66:9

- Branch A: σφραγίζωμεν, present active subjunctive, first-person plural.
- Branch B: σφραγίσωμεν, aorist active subjunctive, first-person plural.
- YLT: “till we may seal the servants of our God upon their foreheads.”

The English rendering does not reliably distinguish the present from the aorist subjunctive here. Choosing a branch from this translation alone would overstate the evidence. The YLT profile selection remains unresolved and null. A separate Greek textual-evidence review is required.

## D. YLT-profile selection counts at the original 19-group review milestone

| Decision status | Count |
|---|---:|
| inherited_provisional | 224 |
| proposed | 5 |
| reviewed_against_translation | 17 |
| not_applicable_to_verse_alignment | 14 |
| unresolved | 1 |
| **Total** | **261** |

The five reviewed verse-text groups and thirteen not-applicable subscriptions account for 18 of the 19 formerly unresolved groups. Revelation 7:3 remains the sole unresolved YLT-profile group in this set. These counts are a historical milestone snapshot, not the current profile-wide totals.

## E. Sequence materialization boundary

The five reviewed choices have now been materialized in the YLT candidate sequence for John 8:6, Acts 3:3, Romans 16:27, Ephesians 6:24, and 1 John 2:23. The shadow sequence table now contains 2,444 Greek sequence-word rows and 3,171 YLT token rows, including the five new verse sequences. The stored YLT verse text was hash-checked and inherited Greek tokens were cross-checked against production positions. 1 John 2:23 branch B adds the eight-token bracketed confession clause.

Revelation 7:3 remains excluded while its branch is unresolved; do not infer a choice from the inherited KJV candidate sequence. The remaining materialization boundary is therefore one verse-text case, not six. See [the materialization and contextual review report](FIVE_VERSE_SEQUENCE_MATERIALIZATION_20261106.md) and the [2026-11-07 final shadow validation](FINAL_VALIDATION_AFTER_DISPOSITION_RECONCILIATION_20261107.txt).

## F. Provenance and change control

- Raw branch payloads and source/parser provenance remain in textual_variant_group and textual_variant_branch.
- Only the YLT profile's profile_variant_selection rows were updated for these 18 decisions.
- The Robinson raw-source profile and CrossWire/KJV candidate profile were not changed.
- The five selected YLT-profile verse sequences were materialized in a later shadow-only milestone. The Revelation 7:3 sequence remains unmaterialized pending independent textual review.
- No YLT/Greek alignment endpoints, legacy associations, production tables, embeddings, vectorizer settings, API, merge, or deployment were changed.
- The current selection snapshot is [YLT_VARIANT_SELECTIONS_CURRENT_20261106.csv](YLT_VARIANT_SELECTIONS_CURRENT_20261106.csv).

The controlling principle is to separate verse text from subscription paratext, preserve every raw branch, and leave a translation-insensitive Greek distinction unresolved.


## G. Current profile-wide YLT selection status (2026-11-07, v14)

The full YLT profile selection ledger now contains 261 rows:

| Decision status | Current count |
|---|---:|
| inherited_provisional | 221 |
| proposed | 8 |
| reviewed_against_translation | 17 |
| not_applicable_to_verse_alignment | 14 |
| unresolved | 1 |
| **Total** | **261** |

The eight proposed branch selections are:

| Reference | Group | Branch | Basis |
|---|---|---|---|
| Mark 8:24 | 41:12 | A | YLT “that” phrase / branch sequence |
| Mark 8:24 | 41:13 | B | YLT “I see” / walking sequence |
| Acts 26:20 | 44:36 | B | YLT “I was preaching” |
| 1 Corinthians 5:11 | 46:2 | B | YLT phrase and clause context |
| 2 Corinthians 7:12 | 47:4 | B | YLT “our” |
| 2 Corinthians 7:12 | 47:5 | B | YLT “your” |
| 2 Corinthians 11:10 | 47:7 | B | YLT “shall be stopped” |
| Revelation 9:20 | 66:18 | A | YLT “neither did reform”; Received-Text basis and Stephanus 1550 / Beza 1598 reading οὔτε; exact edition remains unconfirmed |

The Revelation 9:20 proposal is intentionally not described as a final textual decision. The Robinson source parser represents οὔτε/οὐ; external apparatus also records οὐδέ. The current 261-row export preserves all YLT profile selections, inherited statuses, rationale, and evidence: [YLT_PROFILE_VARIANT_SELECTIONS_CURRENT_20261107.csv](YLT_PROFILE_VARIANT_SELECTIONS_CURRENT_20261107.csv). The full shadow validation is [FINAL_VALIDATION_AFTER_RE9_20_YLT_BRANCH_A_PROPOSAL_20261107.txt](FINAL_VALIDATION_AFTER_RE9_20_YLT_BRANCH_A_PROPOSAL_20261107.txt). See the [Revelation 9:20 branch-A proposal report](REVELATION_9_20_YLT_BRANCH_A_PROPOSAL_20261107.md).
