# Acts 4:32 — phrase-level alignment and textual-variant review

**Date:** 2026-11-07  
**Environment:** Isolated database `bible_greek_bridge_test_20261106`, schema `ylt_profile_shadow`.  
**Status:** Shadow-only proposals. The inherited YLT selection for Robinson group 44:4 is preserved; no new variant branch was selected.

## 1. Primary text and source comparison

The stored YLT wording is:

> “and of the multitude of those who did believe the heart and the soul was one, and not one was saying that anything of the things he had was his own, but all things were to them in common.”

The Robinson YLT-candidate sequence contains the following main clauses:

- Τοῦ δὲ πλήθους τῶν πιστευσάντων
- ἦν ἡ καρδία καὶ ἡ ψυχὴ μία
- καὶ οὐδὲ εἷς τι τῶν ὑπαρχόντων αὐτῷ ἔλεγεν ἴδιον εἶναι
- ἀλλ’ ἦν αὐτοῖς ἅπαντα κοινά

The edition comparison matters:

| Reading | Stephanus 1550 | Beza 1598 | Scrivener 1894 | Critical-text comparison |
|---|---|---|---|---|
| Articles ἡ before καρδία and ψυχή | Present | Present | Present | Omitted in Tischendorf 8 and WH/SBL witnesses |
| Particle before εἷς | οὐδέ | οὐδ’ | οὐδ’ | Often οὐδέ |
| “all things” | ἅπαντα | ἅπαντα | ἅπαντα | Some critical texts read πάντα |
| Possessor pronoun | αὐτῷ | αὐτῷ | αὐτῷ | Some Byzantine witnesses read αὐτῶν |
| “was saying” | ἔλεγεν | ἔλεγεν | ἔλεγεν | A minority reading ἔλεγον is reported |

Sources: [GreekLab interlinear and edition comparison](https://www.greeklab.org/interlinear.php?book=Acts&cap=4&verse=32); [StudyLight interlinear comparison](https://www.studylight.org/interlinear-study-bible/hebrew/acts/4-32.html); [BibleGateway Greek text comparison](https://www.biblegateway.com/verse/grc/Acts%204%3A32); [BibleHub parallel Greek texts](https://biblehub.com/texts/acts/4-32.htm).

The YLT’s “the heart and the soul” is consistent with the articles present in the Received Text editions. Its “all things” does not distinguish ἅπαντα from πάντα. “He had” and “his own” are compatible with the singular dative αὐτῷ, but the English recasting is not a literal word-for-word rendering.

**Important parser boundary:** Robinson group 44:4 captures only the οὐδέ / οὐδ form difference. The external apparatus also reports other differences in this verse, including articles, ἅπαντα / πάντα, αὐτῷ / αὐτῶν, and ἔλεγεν / ἔλεγον. Those additional differences are not silently treated as branches of group 44:4.

## 2. Group 44:4 — οὐδέ versus οὐδ

The stored parser branches are:

- A: οὐδέ (G3761, CONJ-N)
- B: οὐδ (G3761, CONJ-N), an elided form before εἷς

The YLT renders the phrase “not one”. That wording does not distinguish the full form from the elided form. The current YLT profile selection remains **A / inherited_provisional**; it was not promoted to a new proposal. Beza 1598 and Scrivener 1894 show the elided form, while Stephanus 1550 shows οὐδέ. Young’s preface does not identify the exact Received Text edition he used.

## 3. Eight phrase groups

The shadow review adds eight phrase groups and ten proposed phrase-member endpoints.

| Greek phrase / form | YLT phrase | Decision |
|---|---|---|
| Τοῦ πλήθους | “of the multitude” | The genitive article+noun phrase contributes to English “of”; two phrase-member endpoints connect “of” to the article and noun. No Greek preposition is asserted. |
| τῶν πιστευσάντων | “those who did believe” | τῶν is proposed for “those”; the aorist participle is proposed for “did”. “Who” is supplied English relative syntax; no separate Greek relative pronoun occurs. |
| ἡ καρδία | “the heart” | The article ἡ is proposed for “the”; the existing article/noun-to-“heart” legacy link is retained. |
| ἡ ψυχή | “the soul” | The article ἡ is proposed for “the”; the existing article/noun-to-“soul” legacy link is retained. |
| ἔλεγεν | “was saying” | The imperfect active indicative is proposed for “was”; the existing “saying” endpoint remains. |
| τῶν ὑπαρχόντων αὐτῷ | “the things he had” | ὑπαρχόντων is proposed for “had”. The possible αὐτῷ→“he” rendering is recorded as a legacy overlap, not a proposal. |
| αὐτοῖς | “to them” | The dative pronoun is proposed for “to”; the existing “them” endpoint remains. |
| κοινά | “in common” | The adjective is proposed for the idiomatic phrase member “in”; the existing “common” endpoint remains. |

### Morphology and interpretation

- **τῶν πιστευσάντων**: article plus aorist active participle, genitive masculine plural. The participle is substantival (“those who believed”). English “who” is a supplied relative marker; “did” is an English auxiliary in the YLT rendering, not a separate Greek finite verb.
- **ἔλεγεν**: imperfect active indicative, third-person singular. “Was saying” is a phrase-level rendering of this one Greek verb.
- **ὑπαρχόντων**: present active participle, genitive neuter plural in context. With dative αὐτῷ it describes “the things belonging to him”; YLT recasts this as “the things he had”.
- **αὐτοῖς**: dative plural. English “to” expresses the dative relation; there is no separate Greek preposition.
- **κοινά**: adjective “common”. “In common” is an English idiom, not evidence for a Greek preposition.

### Preserved legacy overlap: “he”

The legacy rendering associates YLT “he” (token 27) with Greek positions 17–18. The phrase context also makes αὐτῷ (position 19) a possible source for the English subject “he” in “the things he had”. However, αὐτῷ is already associated in the legacy data with YLT “his” (token 30). The candidate position-19→token-27 link is therefore recorded as **legacy_overlap_review**, with the original associations preserved. It is not promoted to proposed.

## 4. Validation and current queue

The Acts 4:32 endpoint validator passes:

- Eight phrase groups.
- Ten proposed phrase-member endpoints, each exact and unique.
- One alignment-level `not_expressed` row for “who”.
- One preserved legacy-overlap candidate for “he” ← αὐτῷ.
- Group 44:4 remains A / inherited_provisional.

The updated full shadow validator **v16 passes**:

| Table / status | Current count |
|---|---:|
| Greek sequence words in YLT candidate profile | 2,445 |
| Alignment groups | 88 |
| Alignment rows | 684 |
| Alignment proposed | 629 |
| Alignment not_expressed | 43 |
| Alignment legacy_overlap_review | 11 |
| Alignment unresolved | 1 |
| YLT token proposed | 583 |
| YLT token pending_review | 437 |
| YLT token legacy_overlap_review | 47 |
| YLT token legacy_only | 2,104 |
| Greek token proposed | 549 |
| Greek token pending_review | 32 |
| Greek token legacy_overlap_review | 35 |

The current YLT pending queue contains 437 rows: 422 generic discovery rows and 15 annotated grammatical/variant cases. Acts 4:32 retains one token-table-pending row (“who”) because the token-review table has no `not_expressed` status; its alignment-level disposition is explicit.

Production read-only counts remain unchanged:

- `gnt_words`: 141,009
- `gnt_ylt_renderings`: 143,227
- `ylt_verses`: 31,102
- `ylt_verses_embedding_store`: 31,102
- Non-null stored embeddings: 31,102

Reproducible artifacts:
- [Full v16 validator](../eval/validate_ylt_profile_shadow_v16.py)
- [Acts 4:32 endpoint validator](../eval/validate_acts4_32_v16_endpoints.py)
- [Full v16 validation output](FINAL_VALIDATION_AFTER_ACTS_4_32_20261107.txt)

### Shadow database backup integrity

A full custom-format backup was taken immediately before the Acts 4:32 shadow transaction and another immediately after it. Both archives passed `pg_restore -l` validation.

- Pre-change: `/var/backups/bible-postgres-20261106T171837Z/bible_greek_bridge_test_ylt_profile_shadow_20261107_pre_acts4_32.dump`  
  SHA-256: `a6694606a1d4177b4603757d16243bdc9ad331b7e1b3c6f29777666a32d0fdb1`
- Post-change: `/var/backups/bible-postgres-20261106T171837Z/bible_greek_bridge_test_ylt_profile_shadow_20261107_after_acts4_32.dump`  
  SHA-256: `9c72f1fe6b5c51d1c5e7eb261f20e8e6c1313f0e3f6ed17fae2cb3fb5e4128af`

No production DDL/DML, legacy rendering changes, embedding generation, vectorizer changes, API changes, merge, or deployment occurred. All proposals remain isolated in the shadow schema.
