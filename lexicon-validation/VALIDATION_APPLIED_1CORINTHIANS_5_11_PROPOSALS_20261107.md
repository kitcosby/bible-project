# Validation of Applied 1 Corinthians 5:11 Phrase Proposals

**Date:** 2026-11-07  
**Target:** `bible_greek_bridge_test_20261106.ylt_profile_shadow`  
**YLT alignment profile:** 4  
**Greek sequence profile:** 3  
**Result:** Applied shadow proposals validated; production unchanged.

## Executive result

The 1 Corinthians 5:11 phrase/variant work passes an independent endpoint audit:

- **11 proposed alignment rows** are present exactly once: ten `phrase_member` rows and one existing `content_word` row for “named”.
- **Two supplied English tokens** remain alignment-level `not_expressed`: bracketed “[him]” (high confidence) and the article “a” in “such a one” (moderate confidence).
- Robinson group `46:2` is proposed as branch B in the YLT profile; branch B supplies ᾖ (G1510, V-PAS-3S), while the CrossWire/KJV profile remains branch A (ἤ, “or”).
- The one direct variant-dependent alignment is Greek position 11 → YLT “may” (token 21). The legacy “be” association at the same Greek position is preserved.
- All 36 production legacy rendering rows for this verse remain untouched.

## Proposed endpoints

| Greek position | Greek form | YLT position | YLT token | Alignment kind | Group |
|---:|---|---:|---|---|---|
| 3 | ἔγραψα | 4 | did | phrase_member | 1CO-5:11-i-did-write |
| 3 | ἔγραψα | 5 | write | phrase_member | 1CO-5:11-i-did-write |
| 4 | ὑμῖν | 6 | to | phrase_member | 1CO-5:11-to-you |
| 6 | συναναμίγνυσθαι | 12 | with | phrase_member | 1CO-5:11-keep-company-with |
| 8 | τις | 16 | one | phrase_member | 1CO-5:11-if-any-one |
| 10 | ὀνομαζόμενος | 17 | being | phrase_member | 1CO-5:11-being-named |
| 10 | ὀνομαζόμενος | 18 | named | content_word | 1CO-5:11-being-named |
| 11 | ᾖ | 21 | may | phrase_member | 1CO-5:11-may-be-whoremonger |
| 12 | πόρνος | 24 | whoremonger | phrase_member | 1CO-5:11-may-be-whoremonger |
| 25 | μηδέ | 44 | even | phrase_member | 1CO-5:11-not-even |
| 26 | συνεσθίειν | 47 | together | phrase_member | 1CO-5:11-eat-together |

Each endpoint was queried against the current profile-3 sequence and profile-4 alignment table; every expected pair returned exactly one proposed row.

## Supplied English tokens

| YLT token | Text | Alignment disposition | Confidence | Reason |
|---:|---|---|---|---|
| 13 | [him] | unaligned_ylt / not_expressed | high | The bracketed object pronoun has no independent Greek pronoun; συναναμίγνυσθαι already expresses association with someone. |
| 41 | a | unaligned_ylt / not_expressed | moderate | The article in “such a one” is English grammatical supply; the Greek phrase τῷ τοιούτῳ is already represented by the phrase-member links. |

Both token-review rows remain `pending_review` because the YLT token-review table does not have a `not_expressed` status. This is a schema-layer distinction, not two undecided alignments.

## Phrase and legacy-overlap details

### One Greek verb, “did write”

The YLT phrase “I did write” is a periphrastic English realization of the single Greek aorist ἔγραψα. The new “did” and “write” phrase-member endpoints supplement the existing legacy “I” link; they do not replace it.

### One dative, “to you”

The dative pronoun ὑμῖν is expressed as “to you”. The proposal adds “to” while preserving the legacy “you” association.

### One compound verb, “keep company with”

συναναμίγνυσθαι expresses association/keeping company with someone. The legacy “to keep company” links remain; “with” is added as a phrase member. The bracketed “[him]” is not a separate Greek token.

### One pronoun, “any one”

τις at Greek position 8 is associated by legacy data with YLT “any” and by the new phrase proposal with “one”. This is a legitimate phrase-level one-to-many English realization, not a reason to discard the legacy link.

### One participle, “being named”

ὀνομαζόμενος is represented by the English phrase “being named”. Both English tokens map to the same Greek participle. The existing “named” content-word proposal is retained; “being” completes the phrase group.

### Variant-dependent “may be a whoremonger”

Robinson group `46:2`:
- A: ἤ (G2228), “or”.
- B: ᾖ (G1510, V-PAS-3S), present active subjunctive 3rd singular of εἰμί.

The YLT phrase “may be a whoremonger” supports branch B. The profile-3 selection is `proposed`; the KJV candidate remains branch A with its algorithmic status. The YLT “may” token is a proposed phrase member of ᾖ, while the legacy “be” association at Greek position 11 is retained. This is an intentional phrase-level overlap: English “may be” realizes the subjunctive verb; it is not evidence for two Greek verbs.

The noun πόρνος maps to “whoremonger”; the legacy “a” association with the noun is retained. The additional article “a” in “such a one” is a different token and is separately dispositioned as not_expressed.

### “Not even to eat together”

μηδέ is represented by the phrase “not even”; the legacy “not” link remains, and “even” is added. συνεσθίειν is rendered “to eat together”; the existing “to eat” legacy links remain, and “together” is added.

## Variant dependency audit

Only the “may” alignment row at Greek position 11 carries direct dependency group `46:2`. The other phrase endpoints are not directly variant-dependent on this group. The sequence profile as a whole remains provisional because it inherits other source variants; do not confuse global sequence status with direct token sensitivity.

## Validation and safeguards

- Proposed endpoints checked: 11; all exact and unique.
- Alignment-level not_expressed rows: 2.
- Direct group `46:2` alignment dependencies: 1, at Greek position 11 → YLT “may”.
- Legacy “be” association: retained at Greek position 11.
- Production legacy rendering rows in verse: 36, unchanged.
- Full v14 shadow validator passed: [FINAL_VALIDATION_AFTER_RE9_20_YLT_BRANCH_A_PROPOSAL_20261107.txt](FINAL_VALIDATION_AFTER_RE9_20_YLT_BRANCH_A_PROPOSAL_20261107.txt).
- Production counts unchanged: 141,009 Greek words; 143,227 legacy renderings; 31,102 YLT verses; 31,102 non-null embeddings.

No production DDL/DML, legacy update, embedding/vectorizer change, API change, or deployment occurred. All proposal and review statuses remain shadow-only.