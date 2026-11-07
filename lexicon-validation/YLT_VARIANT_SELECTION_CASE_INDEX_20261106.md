# YLT Variant-Selection Case Index — 19 Formerly Unresolved Groups

**Prepared:** 2026-11-06  
**Environment:** Isolated database bible_greek_bridge_test_20261106, schema ylt_profile_shadow.  
**Scope:** The 19 YLT-profile variant-selection rows that were unresolved at the start of this review.  
**Companion snapshot:** [YLT_VARIANT_SELECTIONS_CURRENT_20261106.csv](YLT_VARIANT_SELECTIONS_CURRENT_20261106.csv)

## Executive result

The 19 groups divide into three materially different classes:

- **Five verse-text groups** can be selected against the stored YLT wording. Their YLT-profile selection rows are now marked reviewed_against_translation.
- **Thirteen groups** contain epistle subscriptions/colophons, not verse text. Their raw source payloads are preserved, but their YLT-profile selection rows are now marked not_applicable_to_verse_alignment.
- **One verse-text group** remains unresolved because the YLT English rendering does not distinguish the Greek aspect forms.

This resolves the selection-ledger ambiguity without claiming that all six verse sequences have been rebuilt. The current YLT sequence table covers only the existing 116-verse review sample; none of the six verse-text references below currently has a materialized YLT-profile sequence row. The five decisions are recorded in the profile selection ledger, but their Greek sequences must still be materialized and validated before alignment work can use them.

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

## D. Updated YLT-profile selection counts

| Decision status | Count |
|---|---:|
| inherited_provisional | 224 |
| proposed | 5 |
| reviewed_against_translation | 17 |
| not_applicable_to_verse_alignment | 14 |
| unresolved | 1 |
| **Total** | **261** |

The five reviewed verse-text groups and thirteen not-applicable subscriptions account for 18 of the 19 formerly unresolved groups. Revelation 7:3 remains the sole unresolved YLT-profile group in this set.

## E. Sequence materialization boundary

The current ylt_profile_shadow.gnt_sequence_word table contains 2,367 rows across the existing review sample. It has no sequence rows for the six verse-text references in sections A and C:

- John 8:6
- Acts 3:3
- Romans 16:27
- Ephesians 6:24
- 1 John 2:23
- Revelation 7:3

This is an intentional coverage boundary, not evidence that the selected branches were already materialized. The five reviewed choices are stored in profile_variant_selection only. The Revelation 7:3 sequence remains excluded while its branch is unresolved. The next sequence-build milestone should add the five reviewed verses using the exact selected Robinson branches, then validate the resulting positions against the stored YLT verse text. Do not create alignment rows against an unmaterialized sequence.

## F. Provenance and change control

- Raw branch payloads and source/parser provenance remain in textual_variant_group and textual_variant_branch.
- Only the YLT profile's profile_variant_selection rows were updated for these 18 decisions.
- The Robinson raw-source profile and CrossWire/KJV candidate profile were not changed.
- No sequence words were inserted or deleted in this milestone.
- No YLT/Greek alignment endpoints, legacy associations, production tables, embeddings, vectorizer settings, API, merge, or deployment were changed.
- The current selection snapshot is [YLT_VARIANT_SELECTIONS_CURRENT_20261106.csv](YLT_VARIANT_SELECTIONS_CURRENT_20261106.csv).

The controlling principle is to separate verse text from subscription paratext, preserve every raw branch, and leave a translation-insensitive Greek distinction unresolved.
