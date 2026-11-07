# Acts 26:20 — Dense Phrase and YLT-Specific Variant Proposal

**Prepared:** 2026-11-07  
**Status:** Shadow phrase proposals inserted; YLT-specific branch B proposed; full validator passed.  
**Environment:** `bible_greek_bridge_test_20261106.ylt_profile_shadow`  
**YLT alignment profile:** profile 4 over sequence profile 3.

## Primary text

YLT (database text, preserving punctuation):

> but to those in Damascus first, and to those in Jerusalem, and to all the region also of Judea, and to the nations, I was preaching to reform, and to turn back unto God, doing works worthy of reformation;

The 11 YLT tokens pending before this review were: **to** (2), **to** (8), **those** (9), **in** (10), **region** (15), **I** (23), **was** (24), **to** (26), **to** (29), **back** (31), and **of** (37).

The Robinson-derived sequence has 33 Greek positions. Robinson group `44:36` changes one token at Greek position 18; the two alternatives have the same sequence length, so selecting the other branch does not shift downstream positions.

## Variant group 44:36 — participle versus imperfect indicative

Robinson source alternatives:

| Branch | Payload | Greek reading | Strong’s | Morphology | Parse |
|---|---|---|---|---|---|
| A | `apaggellwn 518 5723 {V-PAP-NSM}` | ἀπαγγέλλων | G518 | V-PAP-NSM | present active participle, nominative singular masculine |
| B | `aphggellon 518 5707 {V-IAI-1S}` | ἀπήγγελλον | G518 | V-IAI-1S | imperfect active indicative, first-person singular |

The YLT phrase is **“I was preaching”**. Branch B directly accounts for the first-person imperfect finite construction; branch A is a participle with an implied subject. The [Cambridge Greek Testament commentary](https://www.truthaccordingtoscripture.com/commentaries/cgt/acts-26.php) reads ἀπήγγελλον (“I declared”) and comments on its literal sense. [OpenBible’s Greek text analysis](https://openbible.com/text/acts/26-20.htm) likewise gives ἀπήγγελλον as an imperfect active indicative, first-person singular. The [parallel Greek edition comparison](https://www.studylight.org/interlinear-study-bible/greek/acts/26-20.html) shows ἀπήγγελλον in SBL/WH/UBS and ἀπαγγέλλων in the TR/RP line.

**Decision:** The YLT profile selection for group 44:36 changes from inherited provisional A to **proposed B**. This is a YLT-specific proposal, not a proven Young editorial reading. The CrossWire/KJV candidate profile remains on branch A with its algorithmic-selection status unchanged.

The lexical sense of ἀπαγγέλλω is announce, report, or declare. YLT “preaching” is contextually plausible but broader than the core lexical sense, so the existing lexical alignment remains moderate confidence. The branch decision is supported primarily by the finite person/tense form, not by claiming “preaching” is an exact gloss.

## Other textual differences kept separate

Acts 26:20 also has textual differences elsewhere in the verse, including τε after πρῶτον and εἰς before πᾶσαν. The Cambridge commentary notes that the oldest authorities omit εἰς before πᾶσαν, while Byzantine witnesses supply it; the [edition comparison](https://www.studylight.org/interlinear-study-bible/greek/acts/26-20.html) likewise lists differences in τε and εἰς. These are **not** part of Robinson group 44:36 and were not changed in this review. The existing Robinson-profile εἰς and its YLT “to all the region” proposal remain as they were.

## Phrase-level review

| Greek position(s) | Greek form(s) | YLT phrase | Existing legacy/proposal retained | New YLT member(s) |
|---:|---|---|---|---|
| 2–4 | τοῖς ἐν Δαμασκῷ | “to those in Damascus” | “those”, “in”, “Damascus” (3–5) | “to” (2) |
| 7 | Ἱεροσολύμοις | “to those in Jerusalem” | “Jerusalem” (11) | “in” (10); “to” (8) and “those” (9) are supplied |
| 12 | χώραν | “region” (15) | — | “region” (15) |
| 18 | ἀπήγγελλον (proposed branch B) | “I was preaching” (23–25) | “preaching” (25), moderate confidence | “I” (23), “was” (24) |
| 19 | μετανοεῖν | “to reform” (26–27) | “reform” (27) | “to” (26) |
| 21 | ἐπιστρέφειν | “to turn back” (29–31) | “turn” (30) | “to” (29), “back” (31) |
| 26–27 | τῆς μετανοίας | “of reformation” (37–38) | “reformation” (38) | “of” (37) |

### Jerusalem phrase: “to those in Jerusalem”

The Greek has the dative plural proper noun Ἱεροσολύμοις, not a separate preposition plus article/pronoun. The Cambridge commentary renders the phrase “and at Jerusalem”. YLT expands it as “to those in Jerusalem”, likely preserving parallelism with the preceding τοῖς ἐν Δαμασκῷ (“to those in Damascus”).

- YLT “in” (token 10) is proposed as a phrase member of the locative dative Ἱεροσολύμοις.
- YLT “to” (token 8) is recorded as alignment-level `not_expressed`: no separate εἰς/πρός occurs here.
- YLT “those” (token 9) is recorded as alignment-level `not_expressed`: there is no separate article or pronoun in the Greek phrase.

The legacy “Jerusalem” endpoint (token 11) is retained.

### “I was preaching”

Under proposed branch B, ἀπήγγελλον is an imperfect active indicative, first-person singular. The YLT “I” and “was” are therefore phrase members of the same finite Greek verb; they are not treated as absent Greek tokens. The existing “preaching” endpoint is retained at moderate confidence because announce/declare is the more direct lexical sense.

### Infinitive and genitive phrases

- μετανοεῖν → “to reform”: the English “to” (26) is the infinitive marker; “reform” (27) remains.
- ἐπιστρέφειν → “to turn back”: “to” (29) is the infinitive marker, “turn” (30) remains legacy-linked, and “back” (31) completes the sense of turn/return.
- τῆς μετανοίας → “of reformation”: “of” (37) expresses the genitive relation of the article+noun phrase; “reformation” (38) remains. This is a moderate-confidence phrase-level proposal, not a standalone gloss for the article.

## Implemented shadow work

- Changed YLT profile selection for Robinson group 44:36 from inherited provisional A to proposed B.
- Changed the YLT-profile sequence metadata at Greek position 18 from G518 / V-PAP-NSM (ἀπαγγέλλων) to G518 / V-IAI-1S (ἀπήγγελλον). No sequence length or downstream positions changed.
- Added seven phrase groups.
- Added 11 alignment rows: nine proposed phrase members and two alignment-level not_expressed YLT tokens.
- Attached five existing proposals to their phrase groups, including the existing “preaching” proposal; marked the finite-verb phrase rows as dependent on group 44:36.
- Added/updated Greek token-review endpoints for the affected Greek positions.
- Preserved the CrossWire/KJV profile’s branch A selection and all production legacy renderings.

## Evidence classification

- **Directly observed:** exact YLT verse text and token positions; Robinson group 44:36 branch payloads; profile-specific selection state; legacy mappings.
- **Imported grammatical/textual evidence:** Cambridge commentary; OpenBible Greek text analysis; SBL/WH/UBS and TR/RP comparison.
- **Strong contextual proposal:** YLT “I was preaching” supports branch B ἀπήγγελλον, imperfect active indicative 1sg.
- **Moderate phrase proposals:** the locative “in” for Ἱεροσολύμοις and genitive “of” for τῆς.
- **Alignment-level not_expressed:** the expanded “to” and “those” in YLT “to those in Jerusalem”.
- **Open/disputed:** whether Young’s source definitely selected branch B. The translation and critical-text evidence support it, but do not prove the editorial source reading.

## Post-update validation (2026-11-07)

- Alignment groups: 73.
- Alignment rows: 658 — 610 proposed, 40 not_expressed, seven legacy_overlap_review, one unresolved.
- YLT token review: 565 proposed, 455 pending_review, 43 legacy_overlap_review, 2,108 legacy_only.
- Greek token review: 537 proposed, 32 pending_review, 31 legacy_overlap_review.
- Full v13 validator passed: [final validation output](FINAL_VALIDATION_AFTER_ACTS_26_20_20261107.txt).
- Production counts unchanged: 141,009 gnt_words; 143,227 gnt_ylt_renderings; 31,102 YLT verses; 31,102 non-null stored embeddings.
- Pre-update schema-only shadow backup: `/var/backups/bible-postgres-20261106T171837Z/bible_greek_bridge_test_ylt_profile_shadow_20261107_pre_acts26_20.dump`; SHA-256 `72d18948f5ce18a988ea1d8dc5211081f1e522f3187fd3495b299fd7c58cadde`.
- Post-update schema-only shadow backup: `/var/backups/bible-postgres-20261106T171837Z/bible_greek_bridge_test_ylt_profile_shadow_20261107_after_acts26_20.dump`; SHA-256 `f0519977a6dd3a462032d8f69ca22c99f0ba57f1d94cc390b95b7194aae4aed7`.

No production DDL/DML, legacy rendering changes, embedding generation, vectorizer changes, API changes, merge, or deployment occurred.