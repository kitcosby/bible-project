# YLT–Greek Alignment Field Guide

**Status:** Working research guide; not all alignments are finalized.  
**Prepared:** 2026-11-06; updated 2026-11-07  
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
- **Acts 21:8:** εἰς τὸν οἶκον = “into the house”; distinguish preposition, article, and noun. The earlier phrase οἱ περὶ τὸν Παῦλον is rendered “Paul and his company”: οἱ περὶ jointly contribute to “company”, Παῦλον maps to “Paul”, and τὸν has no separate English article. The phrase-member candidates for οἱ and περί are retained in legacy-overlap review because the legacy “company” token points to positions [7,8] (τὸν Παῦλον); see the [Acts 21:8 phrase report](ACTS_21_8_PAUL_COMPANY_PHRASE_REVIEW_20261107.md).
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

The review queue and alignment table are separate status layers. A Greek token can have an unaligned_greek row in ylt_greek_alignment marked not_expressed or unresolved while its gnt_token_review row remains pending_review. The token-review schema has no not_expressed value, so pending_review may persist after the alignment-level disposition has been contextually reviewed. The current v16 state has 32 token-table pending rows: 31 alignment-level not_expressed dispositions (26 high confidence, five moderate) and one unresolved case, Acts 15:32 position-2 particle. The stable καί at position 3 is proposed to YLT “and”; the position-2 token remains unresolved because Robinson variant group 44:19 has A=τε and B=δέ, while the YLT candidate sequence inherits B provisionally from the KJV candidate. Acts 21:8 περί now has a phrase-member candidate within the larger οἱ περὶ τὸν Παῦλον → “Paul and his company” group; two phrase members remain in legacy-overlap review. The [2026-11-07 disposition audit](GREEK_TOKEN_ALIGNMENT_DISPOSITION_AUDIT_20261107.md) and [dual-status export](GREEK_TOKEN_ALIGNMENT_DISPOSITION_QUEUE_20261107.csv) record both layers. Do not interpret the token-table pending count as the count of unresolved alignments; likewise, do not infer finality from not_expressed when confidence remains unresolved.

## Latest disposition update (2026-11-07)

Twenty additional alignment rows that had provisional not_expressed status and unresolved confidence were reviewed in full context. Eighteen are now high-confidence and two moderate-confidence. A subsequent audit found four Greek token-review rows marked proposed without matching alignment endpoints; these were reconciled using full-verse context. Acts 21:8 gained a phrase group for οἱ περὶ τὸν Παῦλον → “Paul and his company”, with two legacy-overlap members; the first εἰς is aligned to “to” and the second to “into”. The subsequent Acts 15:32, Revelation 9:20, Acts 19:27, 1 Corinthians 5:11, and Acts 26:20 passes bring the current alignment set to 43 not_expressed dispositions (30 high, thirteen moderate) and one unresolved case. The Greek token-review table now reports 32 pending rows: 31 have alignment-level not_expressed dispositions and one (Acts 15:32 δέ) remains unresolved. The token table has no not_expressed status, so these are status-layer distinctions, not 32 undecided alignments. The YLT token-review queue is now 437 pending, with 422 generic discovery rows and fifteen annotated grammatical/variant cases. No production rows or embeddings were changed.

## Variant groups and paratext

The 19 YLT-profile variant groups initially marked unresolved have now been classified: five verse-text groups were selected against the stored YLT wording, thirteen epistle subscriptions/colophons were marked not applicable to verse alignment, and Revelation 7:3 remains unresolved because YLT does not distinguish the present from aorist subjunctive. The raw Robinson branch payloads remain preserved. The five selected verse-text groups have now been materialized in the shadow sequence for John 8:6, Acts 3:3, Romans 16:27, Ephesians 6:24, and 1 John 2:23. The 1 John 2:23 branch-B clause adds eight tokens; the other four selections are already present in the base sequence or select an empty branch. Revelation 7:3 remains unmaterialized pending a textual decision. See [YLT_VARIANT_SELECTION_CASE_INDEX_20261106.md](YLT_VARIANT_SELECTION_CASE_INDEX_20261106.md), [the machine-readable snapshot](YLT_VARIANT_SELECTIONS_CURRENT_20261106.csv), and [the materialization report](FIVE_VERSE_SEQUENCE_MATERIALIZATION_20261106.md).

## Variant-dependent particle case: Acts 15:32

The YLT wording is “Judas also and Silas”. Robinson variant group 44:19 contains branch A τε and branch B δέ. The Robinson source is unselected; CrossWire/KJV selected B algorithmically, and the YLT candidate inherited B provisionally. This inherited sequence is not a YLT editorial decision. The καί at position 3 is stable in both branches and is proposed to YLT “and” (token 3). The particle at position 2 and YLT “also” (token 2) remain unresolved pending independent evidence of the YLT source reading. See the [Acts 15:32 variant review](ACTS_15_32_DE_KAI_VARIANT_ALIGNMENT_REVIEW_20261107.md).

## Proposed-alignment counts across status layers

The Greek token-review table’s proposed_alignment_count should agree with the number of proposed alignment endpoints for that Greek token; the latest validator checks this and found no remaining mismatches. Do not apply the same row-count assumption blindly to YLT tokens: a single YLT token may represent a multi-token Greek phrase. For example, YLT “quickly” in Romans 16:20 is represented by the two Greek phrase members ἐν and τάχει within one phrase group.

## YLT-side pending queue stratification

The current YLT token-review queue has 437 pending tokens across 116 verses. Of these, 443 retain the generic “No direct proposal identified” reason and fifteen have explicit corner-case notes: 1 John 2:23 “he”; Acts 15:32 “also”; Romans 16:27 “the”/“be”; Revelation 9:20 “are”; Acts 19:27 “the” and two instances of “is”; 1 Corinthians 5:11 “[him]” and “a”; and Acts 26:20 “to” and “those” in the expanded Jerusalem phrase. The YLT review schema has no not_expressed or unresolved status, so these twelve remain pending with their rationale preserved.

Four additional YLT token rows that already had proposed alignment endpoints were reconciled from pending_review to proposed: 1 Corinthians 13:2 “the” → τὰ; Acts 5:12 “through” → διά; Acts 26:20 “those” → τοῖς; Matthew 2:23 “that” → τό (moderate-confidence phrase member). No alignment rows were created in that status-only reconciliation.

The highest-frequency pending surfaces are “to” (46) and “the” (33), followed by “may” (21), “did” (18), “was” (17), “a” (14), “having” (15), “is” (14), and “of” (12). Review by surface is only a batching aid: “to” may be a preposition, infinitive marker, purpose construction, or English syntactic expansion. See the [YLT pending queue stratification](YLT_TOKEN_PENDING_QUEUE_STRATIFICATION_20261107.md) and [current 437-row CSV](YLT_TOKEN_REVIEW_QUEUE_CURRENT_20261107.csv).

## Database design recommendations

Keep these concepts distinct:

1. **Token alignment:** YLT token to one or more Greek sequence positions, with profile and occurrence identity.
2. **Phrase alignment:** YLT span to a Greek span where the relationship is phrase-level.
3. **Grammatical contribution:** optional annotation describing article, infinitive, participle, conjunction, or case contribution.
4. **Review status:** use the actual schema's proposed, accepted/reviewed, unresolved, not-expressed, or legacy-only statuses.
5. **Provenance:** source text, parser/source commit, profile, variant group/branch, and rationale.

Do not add a production schema merely to hold this guide. Current work remains a shadow validation exercise. Any production schema/API extension should be additive and backwards-compatible and follow a separate reviewed migration proposal.

## Related function-word review

The [267-position function-word review milestone](FUNCTION_WORD_ALIGNMENT_MILESTONE_20261106.md) and [complete review bundle index](FUNCTION_WORD_ALIGNMENT_COMPLETE_REVIEW_BUNDLE_20261106.md) document a separate review across 116 verse contexts. Its 228 links are proposals, not applied production mappings, and its 39 pending/non-expressed cases are not the same set as the 39-case shadow token-review queue.

## Current audit snapshot

As of 2026-11-07:

- 37 legacy-overlap cases were reconciled.
- 20 positional-divergence cases received contextual classification; no production or legacy rows were changed.
- Four shadow alignment proposals were corrected in the earlier overlap review (Matthew 10:25; Luke 1:26; Acts 21:8, two tokens).
- At the historical post-eight-proposal snapshot, the original 39-case Greek-token subset had 31 pending rows and eight proposed alignments (three high-confidence function-word proposals and five moderate-confidence phrase-member proposals). This is not the current all-verse queue.
- Historical shadow alignment counts at the milestone after the Acts 15:32 and initial Revelation 9:20 reviews: 581 proposed, 33 not_expressed (28 high confidence, five moderate), one unresolved, and six legacy_overlap_review rows; 521 proposed, 33 pending, and 31 legacy-overlap rows in the Greek-token review table. These counts were superseded by later case reviews and the v15 validation.
- YLT token review counts after Acts 26:20: 583 proposed, 437 pending, 47 legacy-overlap review, and 2,104 legacy-only.
- The 19 YLT-profile variant groups that were unresolved at the start of the review have been classified: five verse-text branches selected against the stored YLT and now materialized, 13 subscription/colophon groups marked not applicable to verse alignment, and one verse-text group (Revelation 7:3) remains unresolved and unmaterialized.
- The five new sequence materializations add 95 YLT tokens and 77 Greek words. Their 45 contextual pair candidates produced 42 proposals, three retained legacy-overlap cases, and one Greek article classified not separately expressed; fourteen phrase groups preserve the non-one-to-one relationships.
- Three YLT tokens and one Greek token remain pending in the five new verses. The earlier eleven-case follow-up classified eight Greek function words as not separately expressed and identified one further legacy overlap in Philippians 4:2. The subsequent 20-case confidence review raised the not_expressed set to 29 (24 high, five moderate). The later occurrence audit reconciled four proposed-status rows without endpoints and added the Acts 21:8 phrase group. Acts 15:32 now has a stable καί → “and” proposal while δέ remains unresolved. At that historical milestone, Revelation 9:20 added 11 phrase groups and 16 alignment rows (15 proposed, one not_expressed), bringing the total to 33 not_expressed (28 high, five moderate), one unresolved (Acts 15:32 δέ), and six legacy-overlap alignment rows. Subsequent cases raised the current v16 totals to 43 not_expressed, eleven legacy-overlap, and one unresolved. The current v15 shadow validator passed after the Revelation 7:2 review; see [latest validation](FINAL_VALIDATION_AFTER_ACTS_4_32_20261107.txt). Production counts and all 31,102 stored embeddings were unchanged.

See [the case index](GREEK_ALIGNMENT_CASE_INDEX.md) for the 20 reviewed cases, the original 39-case subset, the current 32-row Greek pending queue, the separate 267-position function-word review, and the [YLT variant-selection case index](YLT_VARIANT_SELECTION_CASE_INDEX_20261106.md).

## Non-goals and cautions

This guide is not a new lexicon or a replacement for the source text. It does not establish a preferred Greek textual reading, claim that every Greek token needs an English rendering, or authorize changes to production tables, embeddings, vectorizer, API, or deployment. It does not turn Strong's/morphology agreement into proof of occurrence identity.

The governing principle is conservative: preserve evidence, represent phrase and grammar relationships honestly, and leave genuine uncertainty visible.


## YLT-token review queue: phrase expansion examples (2026-11-07)

Historical queue snapshot after 1 Corinthians 5:11: 464 YLT tokens: 454 generic “no direct proposal identified” rows and ten annotated grammatical/variant cases (Acts 15:32 “also”; Romans 16:27 supplied “be” and “the”; 1 John 2:23 supplied “he”; Revelation 9:20 supplied “are”; Acts 19:27 supplied “the” and two instances of “is”; 1 Corinthians 5:11 bracketed “[him]” and supplied “a”). The generic rows remain unadjudicated; do not classify them as not_expressed merely because no proposal is recorded. The Revelation 9:20 “are” token has an alignment-level not_expressed disposition but remains pending in the token-review table because that table lacks this status.

Before its phrase review, Revelation 9:20 was the densest pending verse (16 tokens). Its case report illustrates one Greek finite verb rendered “did reform”; one subjunctive rendered “may bow before”; five Greek article-plus-adjective phrases rendered “those of [material]”; a supplied English copula “are”; and three English infinitive markers “to”. These require phrase-aware modeling, not fabricated Greek tokens or forced one-to-one glosses. The 2026-11-07 shadow implementation added 11 phrase groups and 16 alignment rows (15 proposed, one not_expressed); see the v10 final validator and Revelation 9:20 case report. The verse now has only one token still pending at token-review level (“are”). Acts 19:27 adds a second dense phrase case: “is in danger”, “for us”, “of coming”, “for nothing”, “to be reckoned”, “and also”, “about to be brought down”, and “doth worship” require phrase-aware mapping. The corrected εἰς→“for” candidate and retained “be” legacy overlap are documented in the [Acts 19:27 case report](ACTS_19_27_DENSE_PHRASE_ALIGNMENT_CASE_20261107.md).


## Variant-sensitive phrase case (2026-11-07)

Acts 15:32 now has a stable proposal for Greek καί at position 3 → YLT “and” (token 3), because that καί is present in both Robinson branches. The branch-specific particle at position 2 (A=τε, B=δέ) remains unresolved; YLT “also” does not independently establish which branch Young used. See the [Acts 15:32 variant review](ACTS_15_32_DE_KAI_VARIANT_ALIGNMENT_REVIEW_20261107.md).


## Revelation 9:20 dense phrase case (2026-11-07)

The 16 YLT tokens that were pending in Revelation 9:20 are now dispositioned: 15 proposed phrase-member endpoints and one alignment-level not_expressed copula (“are”). The five substantival article-plus-adjective phrases “those of [material]” are modeled as phrase groups, with existing legacy links preserved. See the [case report](REVELATION_9_20_DENSE_PHRASE_ALIGNMENT_CASE_20261107.md) and the [latest v16 validation](FINAL_VALIDATION_AFTER_ACTS_4_32_20261107.txt).


## Acts 19:27: infinitive chain and phrase-level alignment (2026-11-07)

F. F. Bruce’s grammatical discussion (Acts, p. 415) parses ἐλθεῖν, λογισθῆναι, and μέλλειν as infinitives dependent on κινδυνεύει, with καθαιρεῖσθαι dependent on μέλλειν. This explains why YLT’s English auxiliaries and infinitive markers cannot be treated as independent Greek words. The case also exposes a shadow candidate error: εἰς οὐδέν is “for/as nothing”, not the English infinitive marker “to”. The candidate was corrected from YLT token 26 to token 29; the former now participates in “to be reckoned”.

A legacy association from μέλλειν to YLT “be” is retained as an overlap while a contextual proposal links that “be” to λογισθῆναι. Robinson variant group 44:22 (A=δέ, B=τε) affects the “and also” phrase; the YLT sequence inherits A provisionally, so the phrase remains variant-dependent. See the [Acts 19:27 case report](ACTS_19_27_DENSE_PHRASE_ALIGNMENT_CASE_20261107.md).


## 1 Corinthians 5:11: branch-sensitive subjunctive and phrase expansion (2026-11-07)

Robinson group 46:2 has A=ἤ (G2228, particle “or”) and B=ᾖ (G1510, present active subjunctive 3sg of εἰμί). The YLT phrase “may be a whoremonger” directly supports B; SBLGNT and Scrivener 1894 also include ᾖ. The YLT profile now proposes B while the CrossWire/KJV profile remains on A. This is not a proven Young source reading. The phrase report documents the evidence, the legacy “be” association, and the ten new phrase-member proposals. See [FIRST_CORINTHIANS_5_11_DENSE_PHRASE_ALIGNMENT_CASE_20261107.md](FIRST_CORINTHIANS_5_11_DENSE_PHRASE_ALIGNMENT_CASE_20261107.md). The independent post-application audit verified 11 unique proposed endpoints (ten phrase-member rows and one content-word row), plus two supplied English tokens ([him] and “a”) with alignment-level not_expressed dispositions. Only Greek position 11 → YLT “may” carries direct group 46:2 dependency; the legacy “be” link remains. See [VALIDATION_APPLIED_1CORINTHIANS_5_11_PROPOSALS_20261107.md](VALIDATION_APPLIED_1CORINTHIANS_5_11_PROPOSALS_20261107.md).


## Acts 26:20: finite-verb variant and expanded Jerusalem phrase (2026-11-07)

Robinson group 44:36 has A=ἀπαγγέλλων (present active participle) and B=ἀπήγγελλον (imperfect active indicative, first-person singular). YLT “I was preaching” strongly supports branch B; the Cambridge commentary and SBL/WH/UBS witnesses also read the finite form. The YLT profile now proposes B, while the KJV candidate profile remains A. The same case distinguishes the dative place-name Ἱεροσολύμοις (“at Jerusalem”) from YLT’s expanded “to those in Jerusalem”: “in” is a phrase member, while “to” and “those” are alignment-level not_expressed. See [ACTS_26_20_DENSE_PHRASE_ALIGNMENT_CASE_20261107.md](ACTS_26_20_DENSE_PHRASE_ALIGNMENT_CASE_20261107.md). The applied proposals were independently validated: nine phrase-member endpoints are unique, while YLT “to” and “those” in “to those in Jerusalem” are supplied English expansions over the dative place-name Ἱεροσολύμοις. Exactly three alignments at Greek position 18 depend on branch 44:36 (YLT “I was preaching”). See [VALIDATION_APPLIED_ACTS_26_20_PROPOSALS_20261107.md](VALIDATION_APPLIED_ACTS_26_20_PROPOSALS_20261107.md).


## Revelation 9:20: branch-conditioned dependency (2026-11-07)

Robinson group 66:18 offers οὔτε (A) versus οὐ (B). Both alternatives are one token, so the sequence changes only at Greek position 13 and no later positions shift. The 15 phrase-member proposals for “did reform”, “may bow before”, the five “those of [material]” phrases, and the three infinitive phrases remain positionally stable under either branch. Only the alignment of YLT “neither” at token 13 is directly variant-dependent.

An audit found that the initial dependency metadata had been assigned backwards: 15 later phrase rows carried 66:18 while the position-13 row did not. The shadow database was corrected; exactly one alignment row now carries direct dependency group 66:18. The YLT profile now proposes branch A (οὔτε) for group 66:18, replacing the inherited branch B. The overall sequence remains provisional because other variant groups still inherit candidate readings. Do not confuse this global provisional sequence status with direct token-level sensitivity. See the [variant-dependency audit](REVELATION_9_20_VARIANT_DEPENDENCY_AUDIT_20261107.md) and [latest v15 full validation](FINAL_VALIDATION_AFTER_ACTS_4_32_20261107.txt).


## Revelation 7:2 phrase and variant update (2026-11-07)

The YLT candidate profile now proposes branch B for Robinson group 66:8: ἀναβαίνοντα, present active participle, for YLT “going up”. Stephanus 1550 and Beza 1598 read branch A ἀναβάντα, while Scrivener 1894 and several other witnesses read branch B; Young’s preface does not identify the exact Received Text edition. Keep the YLT branch selection proposed, not final. Seven phrase groups and a cross-verse λέγων→“saying” anchor were added. The review includes 11 proposed rows, two supplied English articles marked alignment-level not_expressed, and three preserved legacy overlaps. See the [Revelation 7:2 case report](REVELATION_7_2_DENSE_PHRASE_ALIGNMENT_CASE_20261107.md).

Revelation 7:3 group 66:9 remains unresolved: σφραγίζωμεν (present subjunctive) versus σφραγίσωμεν (aorist subjunctive). YLT “till we may seal” does not discriminate reliably. The YLT candidate sequence contains only the stable cross-verse anchor at position 1; it does not materialize the remainder of 7:3 while the variant is unresolved.

The latest full v15 validator passes with 2,445 Greek sequence words, 80 alignment groups, and 672 alignment rows. Production counts and all 31,102 stored embeddings remain unchanged. See [v15 validation output](FINAL_VALIDATION_AFTER_ACTS_4_32_20261107.txt).


## Acts 4:32 phrase and variant update (2026-11-07)

The Acts 4:32 review added eight phrase groups and ten proposed phrase-member endpoints. It treats “of the multitude” as a genitive phrase, “those who did believe” as an articular aorist participle, the two explicit Greek articles ἡ as the source of YLT “the”, “was saying” as a phrase rendering of imperfect ἔλεγεν, “had” as a contextual rendering of ὑπαρχόντων, “to them” as the dative αὐτοῖς, and “in common” as an English idiom for κοινά. English “who” is supplied relative syntax and has an alignment-level not_expressed disposition. The possible αὐτῷ→“he” endpoint is recorded only as legacy_overlap_review; the original legacy links are preserved. See the [Acts 4:32 case report](ACTS_4_32_DENSE_PHRASE_ALIGNMENT_CASE_20261107.md).

Robinson group 44:4 retains branch A / inherited_provisional (οὐδέ versus elided οὐδ). The YLT “not one” wording does not distinguish them. External edition comparison also shows variants beyond group 44:4, including ἡ articles, ἅπαντα/πάντα, αὐτῷ/αὐτῶν, and ἔλεγεν/ἔλεγον; those are not silently treated as branches of this parser group.

The current v16 validator passes with 2,445 sequence words, 88 alignment groups, and 684 alignment rows. Current status totals are 629 proposed, 43 not_expressed (30 high, 13 moderate), 11 legacy_overlap_review, and one unresolved. Production counts and all 31,102 stored embeddings remain unchanged. See [v16 validation output](FINAL_VALIDATION_AFTER_ACTS_4_32_20261107.txt).
