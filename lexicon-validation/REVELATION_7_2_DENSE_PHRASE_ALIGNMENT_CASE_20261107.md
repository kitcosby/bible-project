# Revelation 7:2 — dense phrase alignment and variant review

**Date:** 2026-11-07  
**Environment:** Isolated database `bible_greek_bridge_test_20261106`, schema `ylt_profile_shadow`.  
**Status:** Shadow-only phrase proposals; YLT branch B is proposed, not final. No production approval.

## 1. Text and variant

YLT Revelation 7:2 reads:

> “and I saw another messenger going up from the rising of the sun, having a seal of the living God, and he did cry with a great voice to the four messengers, to whom it was given to injure the land and the sea, saying,”

Robinson source group **66:8** affects the participle translated “going up”:

| Branch | Greek | Strong’s | Morphology | Parse |
|---|---|---|---|---|
| A | ἀναβάντα | G305 | V-2AAP-ASM | Aorist active participle, accusative masculine singular |
| B | ἀναβαίνοντα | G305 | V-PAP-ASM | Present active participle, accusative masculine singular |

The YLT profile now **proposes branch B** because the present participle directly corresponds to Young’s “going up”. The existing “going” content-word link is retained and the new phrase-member link adds “up”. Both rows directly depend on group 66:8.

This is a translation-profile proposal, not a definitive reconstruction of Young’s Greek exemplar. The English phrase is compatible with the action described by either participle, although it is a more transparent rendering of the present participle.

## 2. Textual evidence and the Received Text caveat

The editions do not agree uniformly:

| Edition / text | Reading |
|---|---|
| Stephanus 1550 | ἀναβάντα (A) |
| Beza 1598 | ἀναβάντα (A) |
| Scrivener 1894 | ἀναβαίνοντα (B) |
| RP Byzantine 2005 | ἀναβαίνοντα (B) |
| Greek Orthodox 1904 | ἀναβαίνοντα (B) |
| SBL GNT / Nestle 1904 / Westcott–Hort 1881 | ἀναβαίνοντα (B) |

Sources: [parallel Greek texts for Revelation 7:2](https://cnbible.com/texts/revelation/7-2.htm); [Beza 1598 Greek text](https://biblehub.com/beza/revelation/7.htm); [Young’s Literal Translation, Revelation](https://www.sacred-texts.com/bib/ylt/rev.htm).

Young’s preface says that he followed the generally recognized “Received Text”, but does not identify the exact printed edition. Since Stephanus and Beza support A while Scrivener and several other witnesses support B, the preface alone cannot settle this reading. The stored YLT “going up” supports B as a translation-profile candidate, but does not prove which Greek edition Young consulted. Keep branch B **proposed**.

The CrossWire/KJV candidate remains on branch A with its algorithmic status. That selection is not a textual-critical verdict and is not copied into the YLT profile.

## 3. Phrase groups and alignment decisions

Seven phrase groups were added for Revelation 7:2. They preserve phrase-level relationships and avoid forcing every English word into a one-to-one lexical gloss.

| Greek phrase | YLT phrase | Review |
|---|---|---|
| ἀναβαίνοντα | “going up” | Existing “going” content link retained; “up” proposed as a phrase member. Both depend on branch B, group 66:8. |
| ἀπὸ ἀνατολῆς ἡλίου | “from the rising of the sun” | “of” and “sun” proposed as phrase members of ἡλίου; “rising” is corrected to ἀνατολῆς. |
| ἔχοντα σφραγῖδα | “having a seal” | Existing “having” and “seal” associations retained; English “a” is supplied and marked not expressed. |
| ἔκραξεν | “he did cry” | Existing “he” association retained; “did” and “cry” proposed as phrase members of the one aorist verb. |
| φωνῇ μεγάλῃ | “with a great voice” | “great” proposed for μεγάλῃ; the legacy links for “with” and “a” to the adjective are retained as overlap conflicts, not overwritten. |
| ἀδικῆσαι τὴν γῆν | “to injure the land” | Existing “to” and “the” links retained; “injure” and “land” proposed. |
| λέγων (Rev 7:3) | “saying” (end of Rev 7:2) | A cross-verse alignment links the first Greek word of 7:3 to YLT token 45 at the end of 7:2. |

### Corrected positional association

The YLT word “rising” is associated with Greek ἀνατολῆς at position 7, not ἡλίου at position 8. The shadow alignment target was corrected from position 8 to position 7. “Sun” is represented by ἡλίου at position 8. The separate legacy association between “the” in “of the sun” and position 7 remains preserved and is flagged for review; no production rendering was altered.

### Review totals for this case

- **11 proposed alignment rows:** eight phrase-member rows, two existing content-word rows retained within the phrase groups, and one cross-verse row.
- **Two** supplied English articles are alignment-level `not_expressed`: “the” before “rising” and “a” before “seal”.
- **Three** legacy-overlap rows are preserved: “the” in “of the sun”, and “with/a” in “with a great voice”.
- The two direct dependencies on group 66:8 are exactly the “going” and “up” links to Greek position 5.

The read-only endpoint validator checks all 11 proposed endpoints for exactness and uniqueness, the two non-expression rows, the three retained overlaps, the branch dependency, and the cross-verse anchor.

## 4. Revelation 7:3 remains a separate unresolved case

Robinson group **66:9** has:

- A: σφραγίζωμεν — present active subjunctive, first-person plural.
- B: σφραγίσωμεν — aorist active subjunctive, first-person plural.

YLT reads “till we may seal the servants of our God upon their foreheads.” That English wording does not reliably distinguish the present from the aorist subjunctive. The exact Received Text edition Young used is still unknown. The YLT profile therefore remains **unresolved**, with no selected branch.

The profile-specific Greek sequence contains only the stable cross-verse anchor λέγων at Revelation 7:3 position 1. It does not materialize the rest of 7:3 while group 66:9 remains unresolved. The production Greek source has 24 rows for the verse; the shadow profile intentionally avoids turning the two variant forms into an unreviewed single sequence. This is a materialization boundary, not evidence of production corruption.

## 5. Current full shadow validation (v15)

The updated full validator passes:

| Table / status | Current count |
|---|---:|
| Greek sequence words in YLT candidate profile | 2,445 |
| Alignment groups | 80 |
| Alignment rows | 672 |
| Alignment proposed | 619 |
| Alignment not_expressed | 42 |
| Alignment legacy_overlap_review | 10 |
| Alignment unresolved | 1 |
| YLT token proposed | 574 |
| YLT token pending_review | 446 |
| YLT token legacy_overlap_review | 46 |
| YLT token legacy_only | 2,105 |
| Greek token proposed | 541 |
| Greek token pending_review | 32 |
| Greek token legacy_overlap_review | 34 |

YLT profile variant-selection statuses: 220 inherited provisional, nine proposed, 17 reviewed against translation, 14 not applicable to verse alignment, and one unresolved. The current 261-row selection ledger is included in this release.

Production read-only counts remain unchanged:

- `gnt_words`: 141,009
- `gnt_ylt_renderings`: 143,227
- `ylt_verses`: 31,102
- `ylt_verses_embedding_store`: 31,102
- Non-null stored embeddings: 31,102

Reproducible artifacts:
- [Full v15 validator](../eval/validate_ylt_profile_shadow_v15.py)
- [Revelation 7:2 endpoint validator](../eval/validate_revelation_7_2_v15_endpoints.py)
- [Full v15 validation output](FINAL_VALIDATION_AFTER_REVELATION_7_2_20261107.txt)

No production database DDL/DML, legacy rendering changes, embedding generation, vectorizer changes, API changes, merge, or deployment occurred. All selections and alignments described here remain shadow-only.
