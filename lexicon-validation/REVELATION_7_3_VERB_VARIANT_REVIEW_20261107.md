# Revelation 7:3 — verb-form variant review (Robinson 66:9)

**Date:** 2026-11-07  
**Environment:** Documentary research only; no database or sequence changes.  
**Status:** YLT profile selection remains unresolved. No production approval.

## 1. Scope and correction

The active Robinson case is **group 66:9**, which records a verb-form variant:

| Robinson branch | Greek form | Morphology | Strong's |
|---|---|---|---|
| A | σφραγίζωμεν | Present active subjunctive, first-person plural (V-PAS-1P) | G4972 |
| B | σφραγίσωμεν | Aorist active subjunctive, first-person plural (V-AAS-1P) | G4972 |

The distinction is **present vs. aorist aspect**, not indicative vs. subjunctive, and not person or number. Both readings are first-person plural subjunctives of σφραγίζω.

YLT reads: “till we may seal the servants of our God upon their foreheads.” That English wording does not independently identify either Greek form. The YLT-profile selection therefore remains null / unresolved. Do not infer a branch from the inherited KJV candidate.

This report also separates a second textual issue in the same clause: the connective expression ἄχρι / ἄχρις οὗ. That variation is visible in edition comparisons but is **not** the verb-form distinction represented by Robinson group 66:9. Do not merge the two apparatus questions.

## 2. Edition comparison

The following edition comparisons were checked:

| Edition | Connective | Verb | Robinson 66:9 correspondence |
|---|---|---|---|
| Stephanus 1550 | ἄχρις οὗ | σφραγίζωμεν | A |
| Beza 1598 | ἄχρις οὗ | σφραγίζωμεν | A |
| Elzevir 1624 | ἄχρις οὗ | σφραγίσωμεν | B |
| Scrivener 1894 | ἄχρις οὗ | σφραγίσωμεν | B |
| Nestle 1904 | ἄχρι | σφραγίσωμεν | B |
| Westcott–Hort 1881 | ἄχρι | σφραγίσωμεν | B |
| SBL GNT 2010 | ἄχρι | σφραγίσωμεν | B |
| RP Byzantine Majority 2005 | ἄχρι οὗ | σφραγίσωμεν | B |
| Greek Orthodox 1904 | ἄχρις οὗ | σφραγίσωμεν | B |

Sources:
- [Textus Receptus Bibles: edition-by-edition Revelation 7:3](https://www.textusreceptusbibles.com/Interlinear/66007003)
- [CNBible: parallel Greek texts, Revelation 7:3](https://cnbible.com/texts/revelation/7-3.htm)
- [BibleHub: parallel Greek texts, Revelation 7:3](https://biblehub.com/texts/revelation/7-3.htm)
- [OpenBible: Greek text comparison, Revelation 7:3](https://www.openbible.com/text/revelation/7-3.htm)

**Observation:** the printed Received Text editions are not uniform at this point. Stephanus and Beza support Robinson A; Elzevir and Scrivener support Robinson B. The critical editions listed above support B. Consequently, Young's general statement that he followed the “Received Text” does not identify the exact reading he used here.

Young's preface says that his Greek text was the one generally recognized as the Received Text, while explicitly distinguishing translation from textual criticism. It does not name a single printed edition: [YLT preface, CCEL](https://www.ccel.org/bible/ylt/ylt.htm).

## 3. Morphology and translation

The two forms share:
- Lemma: σφραγίζω
- Lexical sense in this context: seal / mark with a seal
- Mood: subjunctive
- Voice: active
- Person and number: first-person plural

They differ in grammatical aspect:
- Present subjunctive (A): imperfective aspect.
- Aorist subjunctive (B): perfective aspect.

The temporal clause is introduced by ἄχρι (or, in other editions, ἄχρις οὗ). A. T. Robertson's discussion of Revelation 7:3 specifically cautions against translating the aorist subjunctive as a future perfect (“shall have sealed”); his gloss is simply “till we seal.” This is important: an English rendering such as “till we may seal” is not a reliable diagnostic for the aorist reading, nor does it prove the present reading. See [Robertson, Word Pictures, Revelation 7:3](https://ccel.org/ccel/robertson_at/word/word.xxx.vii.html).

**Interpretive limit:** the aspect contrast is real at the Greek morphological level, but the verse's future temporal setting and the semantics of ἄχρι make a simplistic English contrast (“ongoing” versus “completed”) unsafe. Do not encode an English tense/aspect distinction that the YLT wording does not express.

## 4. Separate connective variation

Edition comparisons also show:
- Critical editions: ἄχρι.
- Stephanus / Beza / Scrivener: ἄχρις οὗ.
- RP Byzantine 2005: ἄχρι οὗ.
- Greek Orthodox 1904: ἄχρις οὗ.

This is a distinct phrase-level variation. It may matter for a future parser/source-family audit, but it is not the A/B verb payload in Robinson group 66:9. No new group, token, or alignment is proposed here. The repository should retain the raw source and parser provenance before deciding whether this difference is already represented elsewhere.

## 5. YLT-profile decision

| Question | Finding |
|---|---|
| Does YLT “may seal” select A or B? | No; English is non-discriminating here. |
| Does Young's preface identify the exact Received Text edition? | No. |
| Do printed Received Text editions agree? | No; Stephanus/Beza=A, Elzevir/Scrivener=B. |
| Do the cited critical editions support B? | Yes. |
| Is B therefore proven to be Young's exemplar? | No. |
| Should the shadow profile be changed now? | No; retain unresolved / null. |

**Decision:** retain group 66:9 as unresolved; do not materialize the remainder of Revelation 7:3 in the YLT-profile candidate sequence. Preserve the stable cross-verse λέγων anchor already documented. Do not alter the raw Robinson branches, CrossWire/KJV candidate, production Greek sequence, legacy renderings, embeddings, or vectorizer.

## 6. Evidence classification

- **Established from the repository:** Robinson group 66:9 has A=σφραγίζωμεν and B=σφραγίσωμεν; the YLT profile selection is null/unresolved.
- **Verified from edition comparisons:** Stephanus 1550 and Beza 1598 have the present form; Elzevir 1624 and Scrivener 1894 have the aorist form; Nestle 1904, Westcott–Hort, and SBL GNT have the aorist form.
- **Imported grammatical evidence:** Robertson identifies the clause as an indefinite-future temporal clause with the aorist subjunctive and rejects a future-perfect gloss.
- **Unresolved:** which printed Received Text edition, or exemplar within that family, Young used for Revelation 7:3.
- **Not investigated to completion:** whether the connective ἄχρι / ἄχρις οὗ has a corresponding distinct Robinson source group or parser representation.

No database writes, validator runs, production changes, or deployment occurred as part of this documentary review.
