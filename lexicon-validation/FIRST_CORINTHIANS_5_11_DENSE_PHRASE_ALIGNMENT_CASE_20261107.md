# 1 Corinthians 5:11 — Dense Phrase and YLT-Specific Variant Proposal

**Prepared:** 2026-11-07  
**Status:** Shadow phrase proposals inserted; YLT-specific branch B proposed; full validator passed.  
**Environment:** `bible_greek_bridge_test_20261106.ylt_profile_shadow`  
**YLT alignment profile:** profile 4 over sequence profile 3.

## Primary text

YLT (database text, preserving punctuation and brackets):

> and now, I did write to you not to keep company with [him], if any one, being named a brother, may be a whoremonger, or covetous, or an idolater, or a railer, or a drunkard, or an extortioner — with such a one not even to eat together;

The 12 YLT tokens pending before this review were: **did, write, to, with, him, one, being, may, whoremonger, a, even, together**.

The Robinson-derived profile has 26 Greek positions. Variant group `46:2` affects Greek position 11, replacing one Greek token with another; no downstream positional shift occurs.

## Variant group 46:2 — A=ἤ versus B=ᾖ

Robinson source branch payloads:

| Branch | Payload | Greek reading | Strong’s | Morphology | Sense |
|---|---|---|---|---|---|
| A | `h 2228 {PRT}` | ἤ | G2228 | PRT | or |
| B | `h 1510 5725 {V-PAS-3S}` | ᾖ | G1510 | V-PAS-3S | present active subjunctive, 3rd singular: “may be” |

The normalized surface is `η` in both alternatives; surface-only comparison cannot distinguish the branch. Strong’s and morphology are decisive metadata.

The YLT reads “may be a whoremonger”. This phrase is directly compatible with branch B ᾖ, the present active subjunctive of εἰμί. It is not a direct rendering of branch A ἤ (“or”), which contains no finite verb at that point. The [SBL Greek New Testament text analysis](https://biblehub.com/text/1_corinthians/5-11.htm) identifies ᾖ as the verb at this location, and the [parallel Greek texts](https://cnbible.com/texts/1_corinthians/5-11.htm) show ᾖ in SBLGNT, Nestle, Westcott–Hort, Byzantine, and Greek Orthodox witnesses. [Scrivener’s 1894 Textus Receptus](https://mail.cnbible.com/tr94/1_corinthians/5.htm) also prints ᾖ.

**Decision:** The YLT profile selection for group 46:2 is changed from inherited provisional A to **proposed B**. This is a YLT-specific proposal, not a proven Young editorial reading. The CrossWire/KJV candidate profile remains on branch A with its algorithmic-selection status unchanged. The Robinson source branch records are unchanged.

The legacy association of YLT “be” (token 22) to Greek position 11 is retained. Under proposed branch B it is now contextually compatible with ᾖ; no duplicate candidate row was added for “be”. A new phrase proposal links ᾖ to YLT “may” (token 21).

## Phrase-level review

| Greek position(s) | Greek form(s) | YLT phrase | Existing legacy/proposal retained | New YLT member(s) |
|---:|---|---|---|---|
| 3 | ἔγραψα | “I did write” | “I” (token 3) | “did” (4), “write” (5) |
| 4 | ὑμῖν | “to you” | “you” (7) | “to” (6) |
| 6 | συναναμίγνυσθαι | “keep company with [him]” | “to keep company” (9–11) | “with” (12) |
| 7–8 | ἐάν τις | “if any one” | “if” (14), “any” (15) | “one” (16) |
| 10 | ὀνομαζόμενος | “being named” | “named” (18) | “being” (17) |
| 11–12 | ᾖ πόρνος (proposed branch B) | “may be a whoremonger” | “be” (22), “a” (23) | “may” (21), “whoremonger” (24) |
| 25 | μηδέ | “not even” | “not” (43) | “even” (44) |
| 26 | συνεσθίειν | “to eat together” | “to” (45), “eat” (46) | “together” (47) |

### Grammatical supply and unresolved English additions

- YLT token 13, bracketed **[him]**, has no independent Greek pronoun. It is recorded as alignment-level `not_expressed` (high confidence).
- YLT token 41, **a**, in “with such a one” has no independent Greek indefinite article. The Greek phrase is τῷ τοιούτῳ; the existing legacy links for “with”, “such”, and “one” remain intact. The added English article is recorded as alignment-level `not_expressed` (moderate confidence).
- The YLT token-review table has no `not_expressed` status. Both tokens therefore remain pending in that table while their alignment-level dispositions are recorded separately.

## Implemented shadow work

- Changed YLT profile selection for Robinson group 46:2 from inherited provisional A to proposed B.
- Changed the YLT-profile sequence metadata at Greek position 11 from G2228 / PRT (ἤ) to G1510 / V-PAS-3S (ᾖ). No sequence length or downstream positions changed.
- Added 10 phrase groups.
- Added 12 alignment rows: 10 proposed phrase members and two alignment-level not_expressed YLT tokens.
- Attached the existing “named” proposal to the “being named” phrase group; retained all existing legacy links.
- Added/updated Greek token-review endpoints for the affected positions.
- Preserved the CrossWire/KJV profile’s branch A selection and the Robinson source A/B records.

## Evidence classification

- **Directly observed:** YLT wording and brackets; Robinson group 46:2 branch payloads; profile-specific selection state; Greek token metadata; legacy YLT position associations.
- **Imported textual evidence:** SBLGNT, Nestle, Westcott–Hort, Byzantine, Greek Orthodox, and Scrivener 1894 texts include ᾖ at this point.
- **Strong contextual proposal:** YLT “may be” supports branch B ᾖ; the YLT profile now proposes B.
- **Strong phrase proposals:** “did write”, “to you”, “with”, “one”, “being”, “may”, “whoremonger”, “even”, and “together”.
- **Grammatical supply:** bracketed “him” and English article “a” are recorded not_expressed at alignment level.
- **Open/disputed:** whether Young’s underlying source definitely selected branch B. The translation strongly supports B but does not prove the editorial source reading.

## Post-update validation (2026-11-07)

- Alignment groups: 66.
- Alignment rows: 647 — 601 proposed, 38 not_expressed, seven legacy_overlap_review, one unresolved.
- YLT token review: 556 proposed, 464 pending_review, 43 legacy_overlap_review, 2,108 legacy_only.
- Greek token review: 533 proposed, 33 pending_review, 31 legacy_overlap_review.
- Full v12 validator passed: [final validation output](FINAL_VALIDATION_AFTER_1CO_5_11_20261107.txt).
- Production counts unchanged: 141,009 gnt_words; 143,227 gnt_ylt_renderings; 31,102 YLT verses; 31,102 non-null stored embeddings.
- Pre-update schema-only shadow backup: `/var/backups/bible-postgres-20261106T171837Z/bible_greek_bridge_test_ylt_profile_shadow_20261107_pre_1co5_11.dump`; SHA-256 `bafbe12a0294cc5b568b1ebb616fb7bc608e246e0aa2a4dc671d34b5d99d3eb3`.
- Post-update schema-only shadow backup: `/var/backups/bible-postgres-20261106T171837Z/bible_greek_bridge_test_ylt_profile_shadow_20261107_after_1co5_11.dump`; SHA-256 `8f26d682891482d9b067b2c7c88aea2f70d20db85b2c8eb585cc6057838a8ac6`.

No production DDL/DML, legacy rendering changes, embedding generation, vectorizer changes, API changes, merge, or deployment occurred.