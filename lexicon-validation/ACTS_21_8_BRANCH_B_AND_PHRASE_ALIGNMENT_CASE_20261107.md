# Acts 21:8 — YLT branch-B proposal and phrase-alignment review

**Date:** 2026-11-07  
**Status:** YLT-profile branch B proposed; six new phrase groups; seven new proposed endpoints; four alignment-level `not_expressed` dispositions. All work is isolated in the shadow database.

## 1. Primary YLT wording

The stored YLT text reads:

> “and on the morrow Paul and his company having gone forth, we came to Caesarea, and having entered into the house of Philip the evangelist — who is of the seven — we remained with him,”

This wording contains two important textual signals:

1. “Paul and his company” represents the traditional phrase οἱ περὶ τὸν Παῦλον.
2. “We came” is first-person plural and matches ἤλθομεν, not third-person plural ἦλθον.

## 2. Robinson group 44:26 — ἦλθον versus ἤλθομεν

The parser group contains a one-token person/number alternative:

| Branch | Greek form | Morphology | Sense |
|---|---|---|---|
| A | ἦλθον | V-2AAI-3P | they came |
| B | ἤλθομεν | V-2AAI-1P | we came |

The YLT’s “we came” directly supports branch B. The prior YLT sequence had inherited branch A, so its Greek sequence did not agree with the person expressed in Young’s English text.

### Edition comparison

| Edition | Phrase οἱ περὶ τὸν Παῦλον | Verb |
|---|---|---|
| Stephanus 1550 | Present | ἦλθον (A) |
| Beza 1598 | Present | ἦλθον (A) |
| Elzevir 1624 | Present | ἤλθομεν (B) |
| Scrivener 1894 | Present | ἤλθομεν (B) |
| SBL / NA / Tischendorf | Omitted | ἤλθομεν (B) |

Sources: [StudyLight edition comparison](https://www.studylight.org/interlinear-study-bible/greek/acts/21-8.html); [Bible.by comparison of Stephanus, Scrivener, Elzevir, and Beza](https://bible.by/verse-tr/44/21/8/); [BibleHub Greek text analysis](https://www.biblehub.com/text/acts/21-8.htm); [BibleGateway SBL text and variant note](https://www.biblegateway.com/passage/?search=Acts+21%3A8); [Textus Receptus Bibles interlinear](https://www.textusreceptusbibles.com/Interlinear/44021008).

The YLT therefore has a mixed profile: it retains the traditional addition οἱ περὶ τὸν Παῦλον, while its “we came” matches the first-person plural reading found in Scrivener and Elzevir and in several critical editions. This is compatible with Scrivener/Elzevir, but not with the Stephanus 1550 or Beza 1598 verb reading. Young’s preface says he followed the generally recognized Received Text but does not identify the exact edition. The YLT-specific branch-B selection is consequently **proposed, not final**.

The Robinson parser group itself changes only the finite verb. The traditional phrase is part of the shared Robinson base sequence, not a second branch in group 44:26. Its omission in critical editions is an external apparatus difference, not a branch represented by this parser group.

### Shadow sequence decision

The YLT candidate profile now selects group 44:26 branch B, status `proposed`. Only the changed sequence word at Greek position 9 was materialized:

- Before: `ηλθον / hlqon / G2064 / V-2AAI-3P`
- After: `ηλθομεν / hlqomen / G2064 / V-2AAI-1P / proposed_ylt_branch`

The Robinson source remains unselected. The CrossWire/KJV candidate remains branch A / algorithmically selected. No source payload or other sequence positions were changed.

## 3. Phrase-level review

Six new phrase groups were added. The pre-existing `AC-21:8-paul-company` group was extended with two supplied-English dispositions.

| Greek form / phrase | YLT wording | Review |
|---|---|---|
| τῇ ἐπαύριον | “on the morrow” | “on” is a phrase member expressing the temporal dative; ἐπαύριον is proposed for “morrow”. Existing “the” legacy links are preserved. |
| ἐξελθόντες | “having gone forth” | “having” and “forth” are phrase members; the existing “gone” proposal is retained. |
| ἤλθομεν | “we came” | “came” is proposed for the verb; “we” is supplied by its first-person plural ending. |
| εἰσελθόντες | “having entered” | “having” is added as a phrase member; the existing “entered” legacy endpoint is preserved. |
| τοῦ ὄντος | “who is” | The article τοῦ is proposed for “who”; the existing “is” proposal to ὄντος is retained. |
| ἐμείναμεν | “we remained” | “we” is supplied by the first-person plural verb ending; the existing “remained” proposal is retained. |
| οἱ περὶ τὸν Παῦλον | “Paul and his company” | The phrase means “those around Paul”. English “and” and “his” are expansions, not separate Greek conjunction/possessive tokens. The existing “company” legacy overlap is preserved. |

### Morphological observations

- **τῇ** is a dative feminine singular article; **ἐπαύριον** is an adverb (“the next day”). English “on” makes the temporal relation explicit.
- **ἐξελθόντες** and **εἰσελθόντες** are aorist active participles, nominative masculine plural. Their English renderings use “having”.
- **ἤλθομεν** and **ἐμείναμεν** are aorist active indicative, first-person plural. The English subject “we” is already encoded in their inflection; no separate Greek pronoun appears.
- **τοῦ ὄντος** is an articular present participle, genitive masculine singular. The YLT renders the articular participial phrase as the relative clause “who is”. This alignment is a phrase-level proposal, not proof of Young’s exact exemplar.

### Preserved legacy overlap: “the evangelist”

The earlier candidate from Greek article position 20 to YLT “the” (token 24) is now classified as `legacy_overlap_review`. The existing legacy links from “the” to Greek positions 18–19 are preserved; those positions already represent the article and noun in “the evangelist”. Position 20 belongs to τοῦ ὄντος and is now proposed for “who”. The “is” endpoint to ὄντος remains proposed.

The possible YLT “company” overlap in οἱ περὶ τὸν Παῦλον also remains preserved. No legacy rendering was deleted or overwritten.

## 4. Variant dependency scope correction

The raw parser’s group 44:26 branch payload differs only at the finite verb. However, the sequence provenance tag `source_variant_groups=['44:26']` is attached broadly across the verse. That provenance tag must not be confused with an alignment’s direct dependency.

Before this review, five existing alignment rows carried group 44:26 as a direct dependency even though they did not target the changed verb: the Paul/company phrase rows, the article τὸν not expressed separately, and the “to Caesarea” endpoint. Those false direct dependencies have been cleared.

Exactly two direct alignment dependencies remain:

1. Greek position 9 → YLT “came” (token 13), proposed.
2. YLT “we” (token 12), alignment-level not_expressed because the proposed first-person plural verb already encodes the subject.

The raw Robinson group, branch payloads, and CrossWire/KJV candidate selection are unchanged.

## 5. Validation and current state

The independent Acts 21:8 endpoint validator passes:

- Seven proposed endpoints, exact and unique.
- Four alignment-level `not_expressed` rows: “and”, “his”, and the two instances of “we”.
- Branch 44:26 is B / proposed in the YLT profile; KJV remains A / algorithmically selected.
- Exactly two direct dependencies remain for group 44:26.
- The previous article-to-“the” candidate remains a legacy overlap.

The full v17 shadow validator passes:

| Metric | Current count |
|---|---:|
| Greek sequence words | 2,445 |
| Alignment groups | 94 |
| Alignment rows | 695 |
| Alignment proposed | 635 |
| Alignment not_expressed | 47 |
| Alignment legacy_overlap_review | 12 |
| Alignment unresolved | 1 |
| YLT token proposed | 590 |
| YLT token pending_review | 431 |
| YLT token legacy_overlap_review | 47 |
| YLT token legacy_only | 2,103 |
| Greek token proposed | 553 |
| Greek token pending_review | 32 |
| Greek token legacy_overlap_review | 35 |

The current YLT pending queue contains 431 rows: 412 generic discovery rows and 19 annotated grammatical/variant cases. The YLT profile-wide variant ledger has 10 proposed selections, 219 inherited provisional selections, 17 reviewed-against-translation selections, 14 not-applicable selections, and one unresolved selection.

Production read-only counts remain unchanged:

- `gnt_words`: 141,009
- `gnt_ylt_renderings`: 143,227
- `ylt_verses`: 31,102
- `ylt_verses_embedding_store`: 31,102
- Non-null stored embeddings: 31,102

Reproducible artifacts:
- [Full v17 validator](../eval/validate_ylt_profile_shadow_v17.py)
- [Acts 21:8 endpoint validator](../eval/validate_acts21_8_v17_endpoints.py)
- [Full v17 validation output](FINAL_VALIDATION_AFTER_ACTS_21_8_20261107.txt)
- [Acts 21:8 endpoint output](ACTS_21_8_ENDPOINT_CHECK_20261107.txt)

No production DDL/DML, legacy rendering changes, embedding generation, vectorizer changes, API changes, merge, or deployment occurred. All decisions remain shadow-only proposals.
