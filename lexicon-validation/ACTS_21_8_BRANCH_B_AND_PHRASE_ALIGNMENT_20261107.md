# Acts 21:8 — branch B and phrase alignment review

Date: 2026-11-07  
Scope: isolated YLT profile / shadow schema only  
Artifact key: `ACTS_21_8_BRANCH_B_AND_PHRASE_ALIGNMENT_20261107`

## Result

The current isolated YLT candidate profile selects branch B for Robinson variant group `44:26` at Acts 21:8:

- Branch A: `ἦλθον` — `V-2AAI-3P`, third-person plural (“they came”).
- Branch B: `ἤλθομεν` — `V-2AAI-1P`, first-person plural (“we came”).
- YLT: “we came”.

The YLT-specific branch B selection is **proposed**, not final. It is a direct person/number match to YLT. The CrossWire/KJV candidate remains branch A under its independent positional algorithm; the raw Robinson source selection remains unreviewed. This is a profile-specific decision, not a claim that all source witnesses agree.

## Textual evidence and uncertainty

The two Robinson branch payloads differ in the finite verb at Greek position 9. The YLT wording “we came” matches the first-person plural morphology of branch B. Branch A is third-person plural and does not directly match the YLT subject/person marking.

The edition comparison recorded in the shadow evidence is:
- Stephanus 1550: branch A `ἦλθον`.
- Beza 1598: branch A `ἦλθον`.
- Scrivener 1894: branch B `ἤλθομεν`.
- Elzevir 1624: branch B `ἤλθομεν`.

Young's preface says that he followed the generally recognized Received Text, but does not identify the exact printed edition. Therefore the wording is good evidence for the YLT-specific candidate sequence, but it does not establish which printed Greek exemplar Young consulted. This distinction is retained in the proposal rationale.

The phrase `οἱ περὶ τὸν Παῦλον` (“Paul and his company”) is independent of group `44:26`. It is not evidence for either finite-verb branch. YLT's retention of this phrase alongside “we came” is compatible with a mixed textual profile and should not be used to force a global witness-level reading.

## Phrase review

Seven phrase groups are now recorded for Acts 21:8, including the pre-existing Paul/company group:

1. `τῇ ἐπαύριον` → “on the morrow”. The temporal dative construction supports “on”; `ἐπαύριον` supplies “morrow”. Existing legacy “the” associations are retained.
2. `οἱ περὶ τὸν Παῦλον` → “Paul and his company”. `Παῦλον` corresponds to “Paul”; `οἱ περὶ` jointly contribute the collective “company” sense. Legacy links for “company” to positions 7–8 are preserved as an overlap, not silently rewritten. English “and” and “his” are recorded as alignment-level not-expressed expansions, not as separate Greek words.
3. `ἐξελθόντες` → “having gone forth”. Existing “gone” proposal is retained; “having” and “forth” are proposed phrase members.
4. `ἤλθομεν` → “we came”. The verb's first-person plural inflection carries “we”; no separate Greek subject pronoun is present. The “we” token is recorded as alignment-level not-expressed and both rows directly depend on group `44:26`.
5. `εἰσελθόντες` → “having entered”. Existing “entered” legacy association is retained; “having” is proposed as a phrase member.
6. `τοῦ ὄντος` → “who is”. The article within the articular participle contributes the YLT relative marker “who”; the participle supplies “is”. The earlier candidate from `τοῦ` to YLT “the” is retained as a legacy-overlap review because the legacy “the” is associated with Greek positions 18–19.
7. `ἐμείναμεν` → “we remained”. First-person plural verb morphology carries “we”; no separate Greek subject pronoun occurs. The existing “remained” proposal is retained.

The shadow artifact contains seven new proposed endpoints and four new alignment-level `not_expressed` rows. Existing phrase endpoints were associated with the relevant phrase groups without changing their original source record keys. Existing legacy overlaps were retained.

## Dependency correction

Group `44:26` changes only the finite verb at Greek position 9. The current alignment dependency audit identifies exactly two direct dependent rows:
- Greek position 9 → YLT “came” (position 13), proposed.
- No Greek position → YLT “we” (position 12), not expressed.

Other phrase rows in the verse are not marked as directly dependent on this variant. This prevents the person/number choice from being over-propagated across unrelated phrase alignments.

## Current shadow state and validation

The current full shadow validator is `final_validate_ylt_profile_shadow_v17.py`; its output is preserved at `FINAL_VALIDATION_AFTER_ACTS21_8_V17.txt`.

Validation passed:
- 261 Robinson variant groups; 522 branch payloads; 783 profile-selection rows.
- 2,445 Greek words in the YLT candidate sequence; 3,171 YLT tokens.
- 94 alignment groups; 695 alignment rows.
- Alignment rows: 635 proposed, 47 not-expressed, 12 legacy-overlap review, one unresolved.
- YLT token review: 590 proposed, 431 pending review, 47 legacy-overlap review, 2,103 legacy-only.
- Greek token review: 553 proposed, 32 pending review, 35 legacy-overlap review.
- Ten YLT profile variant selections are proposed across the currently reviewed references.
- Group `44:26`: YLT profile branch B proposed; KJV candidate branch A algorithmically selected; Robinson source profile unreviewed.
- Exactly two direct alignment dependencies on `44:26`.
- Production read-only counts unchanged: 141,009 Greek words; 143,227 legacy renderings; 31,102 YLT verses; 31,102 embedding-store rows; 31,102 non-null embeddings.

The full v17 validator also checks the previously reviewed cases and endpoint assertions. A passing validator establishes internal consistency against its assertions; it does not establish Young's exact exemplar or convert proposals into final textual-critical decisions.

## Backup and audit trail

A pre-Acts-21:8 custom-format backup was created and passed `pg_restore -l` validation:
- Path: `/var/backups/bible-postgres-20261106T171837Z/bible_greek_bridge_test_ylt_profile_shadow_20261107_pre_acts21_8.dump`
- SHA-256: `ef1ab04f7f909fc665f26e9472a4cd9dfad9affd49c5a989345432ef584e4aee`
- Size: 192 MB.

Inspection of that backup confirms it contains the prior state: YLT group `44:26` branch A / `inherited_provisional`, and sequence position 9 `ηλθον / V-2AAI-3P`. A subsequent read-only inspection of the live shadow database found the branch-B proposal and its associated phrase rows already present. The first attempted application script stopped at its initial baseline assertion before performing any writes; it did not create these rows. The available process evidence does not identify which earlier process made the intervening shadow changes, so this report records the observed before/after state without attributing authorship.

A post-state backup is being produced separately; its hash and archive validation will be appended when verified.

## Safeguards

- All changes described here are confined to `bible_greek_bridge_test_20261106`, schema `ylt_profile_shadow`.
- No production database DDL/DML or legacy rendering changes occurred.
- No embedding generation, vectorizer change, API change, merge, or deployment occurred.
- The branch selection and all phrase mappings remain proposals for review, not production approval.
