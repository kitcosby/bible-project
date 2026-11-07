# Revelation 9:20 — Dense YLT/Greek Phrase-Alignment Case

**Prepared:** 2026-11-07  
**Status:** Contextual analysis; shadow proposal not yet inserted.  
**Environment:** Isolated YLT-profile sequence in bible_greek_bridge_test_20261106.

## Textual observation

YLT:

> and the rest of men, who were not killed in these plagues, neither did reform from the works of their hands, that they may not bow before the demons, and idols, those of gold, and those of silver, and those of brass, and those of stone, and those of wood, that are neither able to see, nor to hear, nor to walk,

The YLT-profile Greek sequence contains 49 words. The YLT token table contains 62 tokens. Sixteen YLT tokens are currently marked pending_review in this verse. This is the largest pending-token cluster in the current queue.

The sixteen pending YLT tokens are:
- did (14)
- may (24)
- bow (26)
- before (27)
- those (32, 36, 40, 44, 48)
- of (37, 41, 45)
- are (52)
- to (55, 58, 61)

The other tokens in the same constructions are already legacy_only or proposed. This report does not replace those legacy associations.

## Contextual phrase analysis

### 1. “did reform” — Greek μετενόησαν

- Greek position 14: μετενόησαν, aorist active indicative, third-person plural.
- YLT tokens 14–15: “did reform”.
- “reform” (YLT token 15) already has a proposed direct content-word alignment to the Greek verb.
- “did” is an English auxiliary used to render the finite aorist verb with the YLT verbal construction; it is not a separate Greek word.

**Disposition:** phrase-level expansion of one Greek finite verb into “did reform”. Do not invent a second Greek token for “did”.

### 2. “may not bow before” — Greek ἵνα μὴ προσκυνήσωσιν

- Greek position 21: ἵνα; YLT “that” (token 22) already represents the conjunction.
- Greek position 22: μή; YLT “not” (token 25) already represents the negative particle.
- Greek position 23: προσκυνήσωσιν, aorist active subjunctive, third-person plural.
- YLT tokens 24, 26–27: “may … bow before”.
- “may” expresses the subjunctive construction in English.
- “bow before” is the YLT phrase rendering of the single verb προσκυνέω in this context.

**Disposition:** one Greek verb contributes to the English phrase “may bow before”. The three YLT words should be treated as a phrase-level rendering, not three independent Greek lexemes.

### 3. Five repeated “those of [material]” phrases

Greek positions and YLT phrase spans:

| Greek positions | Greek phrase | YLT positions | YLT phrase |
|---|---|---|---|
| 28–29 | τὰ χρυσά | 32–34 | those of gold |
| 31–32 | τὰ ἀργυρά | 36–38 | those of silver |
| 34–35 | τὰ χαλκά | 40–42 | those of brass |
| 37–38 | τὰ λίθινα | 44–46 | those of stone |
| 40–41 | τὰ ξύλινα | 48–50 | those of wood |

Each Greek pair consists of the neuter plural article τὰ plus an adjective describing the material. The article makes the adjective substantival (“the golden ones”, “the silver ones”, etc.). YLT renders this as “those of [material]”. The English “of” is part of the idiomatic phrase expansion; it is not an independent Greek preposition in any of these five phrases.

Pending YLT tokens in these phrases are “those” at positions 32, 36, 40, 44, and 48, and “of” at positions 37, 41, and 45. “Of” at positions 33 and 49 remains legacy_only. The material nouns (“gold”, “silver”, “brass”, “stone”, “wood”) also remain legacy_only.

**Disposition:** five distinct phrase groups are appropriate, each linking a Greek article + adjective pair to the complete three-token YLT phrase. Do not create five separate lexical glosses for “of”. Preserve legacy-only token statuses and associations.

### 4. “that are neither able to see…” — Greek ἃ οὔτε βλέπειν δύναται οὔτε ἀκούειν οὔτε περιπατεῖν

- Greek position 42: ἃ; already proposed to YLT “that” (token 51).
- Greek position 45: δύναται; already proposed to YLT “able” (token 54).
- Greek position 43 and following: οὔτε introduces the coordinated negative infinitive series.
- Greek positions 44, 47, 49: βλέπειν, ἀκούειν, περιπατεῖν (infinitives).
- YLT token 52 “are” is a supplied English copula; there is no independent Greek copula.
- YLT tokens 55, 58, 61 “to” are English infinitive markers. Greek infinitive morphology is expressed in the verb forms themselves; there is no separate Greek preposition or particle for these three “to” tokens.
- YLT “see”, “hear”, and “walk” remain legacy_only.

**Disposition:** “are” is an English grammatical supply, not a separate Greek lexical item. Each “to [verb]” should be documented as a phrase-level realization of one Greek infinitive, rather than inventing a Greek token for “to”.

## Classification of the sixteen pending tokens

| YLT token(s) | Count | Contextual category | Greek basis |
|---|---:|---|---|
| did | 1 | English auxiliary in finite-verb phrase | μετενόησαν |
| may, bow, before | 3 | Subjunctive + lexical verb phrase | προσκυνήσωσιν |
| those | 5 | Substantival article + material adjective phrase | τὰ + adjective |
| of | 3 | English phrase expansion in “those of…” | τὰ + adjective |
| are | 1 | Supplied English copula | No Greek copula |
| to | 3 | English infinitive markers | Infinitive verb forms |


## Existing legacy-rendering evidence

A read-only inspection of production gnt_ylt_renderings confirms that the existing bridge has partial phrase mappings in this verse. Relevant legacy rows include:

| Robinson Greek position(s) | Existing legacy YLT token(s) | Surface(s) |
|---|---|---|
| 28–29 | 33–34 | “of gold” |
| 31–32 | 38 | “silver” |
| 34–35 | 42 | “brass” |
| 37–38 | 46 | “stone” |
| 40–41 | 49–50 | “of wood” |

The five YLT “those” tokens (32, 36, 40, 44, 48) have no corresponding legacy-rendering row in this verse. The middle three “of” tokens (37, 41, 45) also have no legacy row; the first and last “of” tokens (33, 49) do have legacy rows. This explains why the review queue marks the former as pending and the latter as legacy_only.

This legacy evidence strengthens the phrase-level diagnosis but does not authorize replacing the stored associations. Any shadow additions should explicitly preserve the existing links and record only the missing phrase members or phrase-level relationship.

## Evidence classification and cautions

- **Established observation:** the YLT wording, token positions, and YLT-profile Greek sequence shown above.
- **Strong phrase analysis:** “did reform”, “may bow before”, the five “those of [material]” phrases, and “to see/hear/walk”.
- **Grammatical inference:** “are” is supplied by English syntax; Greek uses the relative pronoun plus δύναται and infinitive complements.
- **Not yet implemented:** no new alignment-group rows or token-review statuses were inserted during this analysis.
- **Legacy protection:** existing legacy_only and proposed relationships remain untouched. Any future shadow proposals must be additive, phrase-aware, and checked against the exact existing endpoints.

## Recommended shadow proposal work

1. Add a phrase group for μετενόησαν → “did reform”, preserving the existing direct link to “reform”.
2. Add a phrase group for προσκυνήσωσιν → “may bow before”, preserving the existing ἵνα → “that” and μή → “not” links.
3. Add five distinct material phrase groups for τὰ + adjective → “those of [material]”.
4. Record “are” as a supplied English copula with no independent Greek endpoint.
5. Add three phrase groups for each Greek infinitive → “to [verb]”.
6. Reconcile token-review counts only after every proposed endpoint is represented and validated.

No production data, legacy links, embeddings, vectorizer, API, or deployment were changed.