# YLT–Greek Alignment Field Guide

**Status:** Working research guide; not all alignments are finalized.  
**Prepared:** 2026-11-06  
**Scope:** YLT token ↔ Greek token alignment review in the isolated Robinson/YLT profile shadow.

## Purpose

This guide records recurring alignment problems that are easy to misread when a translation is compared with a Greek token sequence. It is intended to accompany the YLT lexicon/database and make future review reproducible.

**A Greek token can contribute to an English phrase without having a separate English token as its direct equivalent.** Conversely, two English tokens may express one Greek form, one English token may represent a multi-token Greek phrase, and a grammatical marker may be represented by English syntax rather than a literal word.

The database should preserve token-level evidence and, where needed, phrase-level relationships. It should not flatten these into a false one-to-one mapping.

## Evidence labels

- **Direct token correspondence:** a clear English token equivalent in this verse.
- **Phrase contribution:** contributes to an English phrase, but is not a one-token gloss.
- **Grammatical contribution:** article, case, infinitive, participial, or clause structure expressed by English syntax rather than a separate lexical item.
- **Sequence/occurrence issue:** repeated forms or variant-dependent sequence changes make position alone unsafe.
- **Legacy positional defect candidate:** the stored legacy position appears to point to a different Greek occurrence or word. Preserve the legacy row; record a shadow proposal and rationale.
- **Unexpressed / not independently rendered:** no distinct English token should be forced.
- **Unresolved:** evidence is insufficient to decide.

These are semantic classifications, not database status values. Keep the underlying review status and provenance fields intact.

## Core review procedure

1. Identify the exact YLT verse and token position. Read the full verse, not only a short token window.
2. Identify the Greek profile and exact profile-specific sequence. Do not substitute a KJV/CrossWire sequence for the YLT sequence.
3. Inspect Robinson source branches and provenance where the verse depends on a variant group.
4. Read the Greek construction, including nearby articles, prepositions, conjunctions, pronouns, participles, and infinitives.
5. Check every occurrence of a repeated form. Strong's + morphology is useful evidence, but not a unique occurrence identifier.
6. Classify the relationship before proposing a position: direct, phrase, grammatical, sequence, unexpressed, or unresolved.
7. Preserve the legacy association. Record a shadow-only correction only when contextual evidence identifies the intended occurrence.
8. Validate that the proposed target exists in the exact sequence profile and that no target or group is orphaned.
9. Record reasoning and uncertainty. Do not convert a plausible phrase contribution into a proven lexical gloss.

## Recurring corner cases

### 1. Greek articles

Greek articles are frequent and highly inflected. English may render them as “the”, omit them, use a possessive, or absorb their contribution into an idiomatic phrase.

- **Matthew 4:13 — τὴν παραθαλασσιάν.** YLT “by the sea” renders article + adjective as a phrase. The article is not an independently obvious token.
- **Matthew 10:10 — τῆς τροφῆς.** YLT “his nourishment” uses a possessive where Greek has article + noun.
- **Luke 2:4 — διὰ τὸ εἶναι.** An articular infinitive, rendered “because of his being”. The article belongs to the construction, not an isolated “the”.
- **Luke 4:16 — ἐν τῇ ἡμέρᾳ τῶν σαββάτων.** YLT “on the sabbath-day” compresses a Greek phrase.
- **Colossians 4:14 — ὁ ἰατρὸς ὁ ἀγαπητός.** Two articles occur in one noun phrase; the second introduces the attributive adjective.

**Rule:** an article is not automatically an English “the”. Check whether English uses a possessive, idiom, compound, relative construction, or no separate article.

### 2. Articular infinitives

The article can nominalize or mark an infinitive. English often expresses the construction with “to”, “because of”, “when”, or a gerund-like phrase.

- **Acts 26:18 — τοῦ ἐπιστρέψαι:** YLT “to turn”. The article participates in the articular infinitive.
- **Luke 2:4 — διὰ τὸ εἶναι:** YLT “because of his being”.
- **James 4:15 — ἀντὶ τοῦ λέγειν:** YLT “instead of your saying”.

**Rule:** record grammatical contribution separately from lexical equivalence. The infinitive carries the core lexical meaning while the article marks the construction.

### 3. Article + noun/adjective/participle phrases

A YLT word such as “the”, “who”, or “same” can correspond to a Greek article or pronoun that is one component of a larger phrase.

- **Matthew 21:11 — οἱ ὄχλοι:** “the multitudes”; article and noun form the phrase.
- **1 Corinthians 5:7 — τὴν παλαιὰν ζύμην:** “the old leaven”; article and adjective are separate Greek tokens.
- **Colossians 4:11 — οἱ ὄντες ἐκ περιτομῆς:** “who are of the circumcision”; the article introduces a substantival participial expression.
- **Acts 22:25 — τὸν ἑστῶτα ἑκατοντάρχην:** “the centurion who was standing”; article, participle, and noun jointly express the phrase.

**Rule:** preserve both token-level and phrase-level facts. A legacy mapping to the head noun may be complementary rather than contradictory.

### 4. Repeated forms and occurrence identity

A verse may contain multiple occurrences of the same article, preposition, or conjunction. Strong's and morphology can match more than one position.

- **Luke 1:26:** two occurrences of τῷ appear in “in the sixth month”. The first belongs with μηνί; the second with ἕκτῳ.
- **Colossians 4:14:** ὁ ἰατρός ὁ ἀγαπητός contains two articles.
- **Acts 21:8:** two εἰς occurrences appear in the verse. “Into the house” maps to the second, not the earlier “to Caesarea”.

**Rule:** never resolve a repeated-form ambiguity using Strong's + morphology alone. Use whole-verse syntax and the exact variant-specific sequence.

### 5. Conjunctions and particles

Greek conjunctions can be paired, layered, or rendered idiomatically.

- **Acts 19:27:** δὲ καί is represented by “and also”. Treating one conjunction as the whole phrase loses the contribution of the other.
- **James 4:13:** καὶ before a verb corresponds to “and”; the following verb is part of the coordinated predicate.
- **Luke 2:4:** δὲ καί around Joseph's movement is not necessarily a word-for-word “but also” sequence in YLT.

**Rule:** distinguish local gloss from connective function. Do not force a separate English token where syntax absorbs the conjunction.

### 6. Prepositions and phrase boundaries

- **Acts 10:38:** ὑπὸ τοῦ διαβόλου = “by the devil”; article and noun are separate components of the prepositional phrase.
- **Acts 21:8:** εἰς τὸν οἶκον = “into the house”; distinguish preposition, article, and noun.
- **2 Peter 2:9:** εἰς ἡμέραν = “to a day”; distinguish this preposition from the later infinitive τηρεῖν, “to keep”.
- **Romans 16:20:** ἐν τάχει is the idiom “quickly”. The preposition ἐν and noun τάχει jointly express one English adverb; the shadow review now proposes a phrase-member link from ἐν to the same YLT token already linked to τάχει.
- **Luke 2:39:** ἅπαντα τὰ κατὰ τὸν νόμον κυρίου is rendered “all things, according to the Law of the Lord”. The article τὰ substantivizes the following phrase; YLT “things” is a phrase-level rendering, not a lexical gloss for the article alone.

**Rule:** inspect the complete phrase. Do not let a nearby repeated preposition or later infinitive capture the wrong English token.

### 7. Genuine positional defects

Not every discrepancy is explained by phrase granularity.

- **Romans 1:27:** YLT “their” is directly supported by αὐτῶν. Legacy positions point to the preceding article+noun phrase. Strong candidate for a genuine positional defect.
- **2 Peter 2:9:** “to a day” corresponds to εἰς ἡμέραν; the legacy position points to τηρεῖν (“to keep”) later in the verse. Strong candidate for a genuine positional defect.
- **1 Timothy 3:2:** proposed τόν begins τὸν ἐπίσκοπον (“the overseer”); legacy position points to οὖν. Likely positional error, but verify exact production sequence provenance before any migration proposal.

**Rule:** even a strong defect candidate remains a proposal until exact production sequence and variant provenance are reconciled. Never repair production by simply shifting positions after a gap.

## Variant-aware alignment

The YLT profile has its own sequence-word positions. They are not interchangeable with CrossWire/KJV positions or raw Robinson source positions. A branch selection can insert or remove a token and shift later positions.

The isolated shadow model therefore keeps separate:
- raw Robinson source branches and variant groups;
- CrossWire/KJV candidate sequence;
- YLT candidate sequence;
- YLT alignment targets referencing the YLT profile sequence.

A proposed alignment must target the correct profile-specific sequence. The 2 Corinthians 11:10 proposal (φραγήσεται, “shall be stopped”) is variant-sensitive and remains a YLT-profile proposal, not a universal textual claim.

## Review queue versus alignment-row status

The review queue and alignment table are separate status layers. A Greek token can have a corresponding unaligned_greek row in ylt_greek_alignment marked not_expressed or unresolved while its gnt_token_review row remains pending_review. In this audit, all 39 original queue entries had matching alignment rows, but their confidence was unresolved. That is a deliberate signal that the current non-link classification is provisional, not a settled decision. When a proposal is made, the alignment row and the corresponding token-review row should be updated together and validated. Do not infer finality from not_expressed when confidence remains unresolved.

## Variant groups and paratext

The 19 YLT-profile variant groups initially marked unresolved have now been classified: five verse-text groups were selected against the stored YLT wording, thirteen epistle subscriptions/colophons were marked not applicable to verse alignment, and Revelation 7:3 remains unresolved because YLT does not distinguish the present from aorist subjunctive. The raw Robinson branch payloads remain preserved. The five branch decisions are in the selection ledger, but their six affected verse references (the five selected verses plus Revelation 7:3) are not yet materialized in the current 116-verse sequence fixture. Do not align against them until the sequence is built and validated. See [YLT_VARIANT_SELECTION_CASE_INDEX_20261106.md](YLT_VARIANT_SELECTION_CASE_INDEX_20261106.md) and [the machine-readable snapshot](YLT_VARIANT_SELECTIONS_CURRENT_20261106.csv).

## Database design recommendations

Keep these concepts distinct:

1. **Token alignment:** YLT token to one or more Greek sequence positions, with profile and occurrence identity.
2. **Phrase alignment:** YLT span to a Greek span where the relationship is phrase-level.
3. **Grammatical contribution:** optional annotation describing article, infinitive, participle, conjunction, or case contribution.
4. **Review status:** use the actual schema's proposed, accepted/reviewed, unresolved, not-expressed, or legacy-only statuses.
5. **Provenance:** source text, parser/source commit, profile, variant group/branch, and rationale.

Do not add a production schema merely to hold this guide. Current work remains a shadow validation exercise. Any production schema/API extension should be additive and backwards-compatible and follow a separate reviewed migration proposal.

## Current audit snapshot

As of 2026-11-06:

- 37 legacy-overlap cases were reconciled.
- 20 positional-divergence cases received contextual classification; no production or legacy rows were changed.
- Four shadow alignment proposals were corrected in the earlier overlap review (Matthew 10:25; Luke 1:26; Acts 21:8, two tokens).
- The original 39-row Greek-token review set now has 31 pending rows and eight proposed alignments (three high-confidence function-word proposals and five moderate-confidence phrase-member proposals).
- Current shadow review counts: 521 proposed, 20 not_expressed, and 11 unresolved alignment rows; 479 proposed, 31 pending, and 25 legacy-overlap rows in the Greek-token review table.
- 19 Robinson variant groups remain unresolved.
- 502 YLT token review cases remain pending.
- The full shadow validator passed at the last recorded checkpoint; production counts and embeddings were unchanged.

See [the case index](GREEK_ALIGNMENT_CASE_INDEX.md) for the 20 reviewed cases and the corrected 31-row pending queue.

## Non-goals and cautions

This guide is not a new lexicon or a replacement for the source text. It does not establish a preferred Greek textual reading, claim that every Greek token needs an English rendering, or authorize changes to production tables, embeddings, vectorizer, API, or deployment. It does not turn Strong's/morphology agreement into proof of occurrence identity.

The governing principle is conservative: preserve evidence, represent phrase and grammar relationships honestly, and leave genuine uncertainty visible.
