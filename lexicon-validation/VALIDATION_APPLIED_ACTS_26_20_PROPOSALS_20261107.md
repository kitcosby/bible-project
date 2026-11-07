# Validation of Applied Acts 26:20 Phrase and Variant Proposals

**Date:** 2026-11-07  
**Target:** `bible_greek_bridge_test_20261106.ylt_profile_shadow`  
**YLT alignment profile:** 4  
**Greek sequence profile:** 3  
**Result:** Applied shadow proposals validated; production unchanged.

## Executive result

The Acts 26:20 proposals pass an independent endpoint audit:

- **Nine phrase-member endpoints** are present exactly once.
- **Two supplied English tokens** remain alignment-level `not_expressed` at moderate confidence: YLT “to” (token 8) and “those” (token 9) in “to those in Jerusalem”.
- Robinson group `44:36` is proposed as branch B in the YLT profile: ἀπήγγελλον (G518, imperfect active indicative, first-person singular). The CrossWire/KJV profile remains branch A by algorithmic selection.
- Exactly **three alignment rows** directly depend on group `44:36`: “I”, “was”, and “preaching”, all linked to Greek position 18.
- All 21 production legacy rendering rows for this verse remain unchanged.

## Phrase-member endpoint validation

| Greek position | Greek form | YLT position | YLT token | Phrase group |
|---:|---|---:|---|---|
| 2 | τοῖς | 2 | to | AC-26:20-to-those-damascus |
| 7 | Ἱεροσολύμοις | 10 | in | AC-26:20-jerusalem-dative |
| 12 | χώραν | 15 | region | AC-26:20-region |
| 18 | ἀπήγγελλον | 23 | I | AC-26:20-i-was-preaching |
| 18 | ἀπήγγελλον | 24 | was | AC-26:20-i-was-preaching |
| 19 | μετανοεῖν | 26 | to | AC-26:20-to-reform |
| 21 | ἐπιστρέφειν | 29 | to | AC-26:20-turn-back |
| 21 | ἐπιστρέφειν | 31 | back | AC-26:20-turn-back |
| 26 | μετανοίας | 37 | of | AC-26:20-of-reformation |

Each expected pair returned exactly one proposed `phrase_member` row.

Other retained content/function proposals include:
- τοῖς (position 2) → “those” (token 3)
- ἐν (position 3) → “in” (token 4)
- πρωτον (position 5) → “first” (token 6)
- εἰς (position 8) → “to” (token 12)
- τε (position 10) → “also” (token 16)
- ἔθνεσιν (position 17) → “nations” (token 22)
- μετανοεῖν (position 19) → “reform” (token 27)
- ἐπί (position 22) → “unto” (token 32)
- πράσσοντας (position 29) → “doing” (token 34)
- ἄξια (position 25) → “worthy” (token 36)
- μετανοίας (position 27) → “reformation” (token 38)

These are not counted as the nine new phrase-member rows above; existing content/function proposals remain separately classified.

## Supplied tokens in “to those in Jerusalem”

The Greek has the dative proper name Ἱεροσολύμοις (position 7), without a separate εἰς/πρός preposition or article/pronoun corresponding to “to those”. YLT expands the phrase by parallelism with the preceding “to those in Damascus”:

| YLT token | Surface | Disposition | Confidence | Explanation |
|---:|---|---|---|---|
| 8 | to | unaligned_ylt / not_expressed | moderate | Supplied in the expanded English parallel phrase; Greek has only the dative place-name. |
| 9 | those | unaligned_ylt / not_expressed | moderate | No separate Greek article/pronoun corresponds to “those” at this location. |

The Greek dative place-name is represented by the proposed “in” phrase member at token 10 and the existing legacy “Jerusalem” association at token 11. The two supplied tokens remain pending in the YLT token-review table because that table has no `not_expressed` status.

## Variant group 44:36 — “I was preaching”

Robinson group `44:36`:
- A: ἀπαγγέλλων — present active participle.
- B: ἀπήγγελλον — imperfect active indicative, first-person singular.

The YLT phrase “I was preaching” is grammatically compatible with B:
- “I” (token 23) expresses the first-person subject.
- “was” (token 24) expresses the imperfect aspect in English.
- “preaching” (token 25) is the existing content-word proposal, retained at moderate lexical confidence because ἀπαγγέλλω more directly means “announce/report/declare”.

The YLT profile selection remains `proposed`, not final. The KJV candidate's branch A algorithmic selection is not a textual-critical verdict and is not copied into the YLT profile.

Exactly three rows carry direct dependency group `44:36`, all at Greek position 18 → YLT tokens 23, 24, and 25. No other alignment rows in this verse are directly dependent on this group.

## Validation and safeguards

- Phrase-member endpoints checked: 9; all exact and unique.
- Supplied English tokens: 2, both alignment-level not_expressed at moderate confidence.
- Direct group `44:36` dependencies: exactly 3 rows, all at Greek position 18.
- YLT branch selection: B, status proposed.
- Production legacy rendering rows in verse: 21, unchanged.
- Full v14 shadow validator passed: [FINAL_VALIDATION_AFTER_RE9_20_YLT_BRANCH_A_PROPOSAL_20261107.txt](FINAL_VALIDATION_AFTER_RE9_20_YLT_BRANCH_A_PROPOSAL_20261107.txt).
- Production counts unchanged: 141,009 Greek words; 143,227 legacy renderings; 31,102 YLT verses; 31,102 non-null embeddings.

No production DDL/DML, legacy update, embedding/vectorizer change, API change, or deployment occurred. All proposals and review statuses remain shadow-only.