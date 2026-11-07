# Acts 19:27 — Dense Phrase, Legacy Conflict, and Variant-Sensitive Alignment

**Prepared:** 2026-11-07  
**Status:** Contextual shadow proposals inserted and validated; production unchanged.  
**Environment:** `bible_greek_bridge_test_20261106.ylt_profile_shadow`  
**YLT profile:** profile 4 alignment over sequence profile 3.

## Primary text

YLT (database text, preserving punctuation):

> and not only is this department in danger for us of coming into disregard, but also, that of the great goddess Artemis the temple is to be reckoned for nothing, and also her greatness is about to be brought down, whom all Asia and the world doth worship.

The Robinson-derived sequence in this profile has 37 Greek tokens. The verse contains 48 YLT tokens. Thirteen YLT tokens were pending before this review.

Greek sequence (accented display; positions refer to the Robinson-derived profile):

`οὐ μόνον δὲ τοῦτο κινδυνεύει ἡμῖν τὸ μέρος εἰς ἀπελεγμὸν ἐλθεῖν, ἀλλὰ καὶ τὸ τῆς μεγάλης θεᾶς Ἀρτέμιδος ἱερὸν εἰς οὐδὲν λογισθῆναι, μέλλειν δὲ καὶ καθαιρεῖσθαι τῆς μεγαλειότητος αὐτῆς, ἣν ὅλη ἡ Ἀσία καὶ ἡ οἰκουμένη σέβεται.`

## Textual and grammatical evidence

F. F. Bruce’s commentary on Acts 19:27 (3rd revised edition, 1990, p. 415) identifies a difficult accumulation of infinitives: ἐλθεῖν, λογισθῆναι, and μέλλειν depend on κινδυνεύει, while καθαιρεῖσθαι depends on μέλλειν. This is important for phrase mapping: the English auxiliaries and infinitive markers do not each represent separate Greek lexemes. Bruce also discusses εἰς οὐδέν as a predicative construction and notes μέρος can mean “line of business.” See [Bruce, *The Acts of the Apostles*, commentary on 19:27](https://www.thetbs.org/study-materials/wp-content/uploads/2023/03/The-Acts-of-the-Apostles_-The-Greek-Text-with-Introduction-and-Commentary-PDFDrive-.pdf).

The Greek text comparison at [CNBible, Acts 19:27](https://cnbible.com/texts/acts/19-27.htm) shows the relevant textual contrast: the Robinson source group has A = δέ and B = τε after μέλλειν; the Textus Receptus and other witnesses differ at this point. The Robinson group is `44:22`, beginning at Acts 19:27. The YLT sequence currently inherits branch A provisionally from the KJV positional candidate. YLT “and also” does not independently establish whether the underlying particle was δέ or τε. This remains a source-reading dependency, not a YLT editorial decision.

Bruce’s discussion of the Western (δ) text changes to λογισθῆναι, μέλλειν, and τῆς μεγαλειότητος is a separate textual issue; it must not be conflated with Robinson group 44:22’s δέ/τε alternative.

## Pending-token review

| YLT position | Token | Contextual disposition | Greek basis |
|---:|---|---|---|
| 4 | is | Proposed phrase member | κινδυνεύει → “is in danger” |
| 9 | for | Proposed phrase member | ἡμῖν → “for us” |
| 11 | of | Proposed phrase member | ἐλθεῖν → “of coming”; English constructional marker |
| 23 | the | Alignment-level not_expressed | English article before “temple”; τὸ at Greek position 14 is already rendered “that” at YLT position 17 |
| 25 | is | Alignment-level not_expressed | Supplied English copula in the infinitive rendering of λογισθῆναι |
| 29 | for | Proposed phrase member | εἰς οὐδέν → “for nothing” |
| 32 | also | Proposed phrase member | Stable καί at Greek position 25 |
| 35 | is | Alignment-level not_expressed | Supplied English finite auxiliary in “is about to be brought down” |
| 36 | about | Proposed phrase member | μέλλειν |
| 37 | to | Proposed phrase member | Infinitive marker for καθαιρεῖσθαι |
| 39 | brought | Proposed phrase member | καθαιρεῖσθαι |
| 40 | down | Proposed phrase member | καθαιρεῖσθαι |
| 47 | doth | Proposed phrase member | σέβεται → “doth worship” |

Ten pending tokens received proposed phrase-member links. Three received alignment-level `not_expressed` dispositions. The YLT token-review table has no `not_expressed` status, so those three tokens remain pending at that separate layer; this is intentional and documented.

## Phrase groups and evidence

### 1. κινδυνεύει — “is in danger”

- Greek position 5: κινδυνεύει, present active indicative, third-person singular.
- YLT positions 4, 7–8: “is … in danger”.
- Existing legacy associations from Greek position 5 to “in” and “danger” are retained.
- New proposal: position 5 → YLT “is” (position 4).

The English predicate spans non-contiguous YLT tokens because “this department” intervenes. A one-token/one-token model would miss the phrase.

### 2. ἡμῖν — “for us”

- Greek position 6: dative pronoun ἡμῖν.
- Existing proposal: position 6 → “us” (YLT position 10).
- New proposal: position 6 → “for” (YLT position 9).

The two English words form one phrase-level realization of the dative.

### 3. ἐλθεῖν — “of coming”

- Greek position 11: ἐλθεῖν, aorist active infinitive.
- Existing proposal: position 11 → “coming” (YLT position 12).
- New proposal: position 11 → “of” (YLT position 11).

“Of” is an English constructional marker in “in danger … of coming”; it is not a separate Greek preposition.

### 4. εἰς οὐδέν — “for nothing”

- Greek positions 20–21: εἰς οὐδέν.
- YLT positions 29–30: “for nothing”.
- The earlier shadow candidate linked εἰς (position 20) to YLT “to” (position 26). That was a contextual misassignment: “to” marks the infinitive phrase “to be reckoned”, while εἰς οὐδέν is the predicative “for/as nothing” phrase.
- Corrected shadow candidate: εἰς position 20 → YLT “for” position 29.
- Existing proposal οὐδέν position 21 → “nothing” position 30 is retained.

This correction changes only the isolated shadow proposal. No production or legacy rendering row was modified.

### 5. λογισθῆναι — “to be reckoned”

- Greek position 22: λογισθῆναι, aorist passive infinitive.
- YLT positions 26–28: “to be reckoned”.
- Existing direct proposal to “reckoned” (position 28) remains.
- New proposal to “to” (position 26) and contextual candidate to “be” (position 27).

**Legacy conflict:** the legacy bridge associates YLT “be” (position 27) with Greek μέλλειν at position 23. The new contextual candidate links that same English token to λογισθῆναι at position 22, where it belongs in the phrase “to be reckoned”. The old association is preserved; the new row is explicitly `legacy_overlap_review`. Do not resolve this by overwriting the legacy mapping.

### 6. δέ/τε καί — “and also”

- Greek position 24: Robinson variant group 44:22, branch A δέ / branch B τε.
- Greek position 25: stable καί.
- YLT positions 31–32: “and also”.
- Existing proposal: position 24 → “and” (position 31).
- Existing legacy association: position 25 → “and” (position 31).
- New proposal: position 25 → “also” (position 32).

The existing overlap on “and” remains. Both phrase members carry variant dependency `44:22`; the YLT candidate inherits A provisionally, and the YLT wording does not settle A versus B.

### 7. μέλλειν — “about”

- Greek position 23: μέλλειν, present active infinitive.
- New proposal: position 23 → YLT “about” (position 36).
- YLT “is” (position 35) is recorded as a supplied English finite auxiliary.
- The legacy association from μέλλειν to YLT “be” (position 27) remains preserved, but the contextual reading places “be” in the earlier “to be reckoned” phrase and associates μέλλειν with the later “about to” phrase.

### 8. καθαιρεῖσθαι — “to be brought down”

- Greek position 26: καθαιρεῖσθαι, present passive infinitive.
- YLT positions 37–40: “to be brought down”.
- New proposals: “to” (37), “brought” (39), and “down” (40).
- Existing legacy association from position 26 to “be” (38) is retained.

### 9. σέβεται — “doth worship”

- Greek position 37: σέβεται, present middle indicative, third-person singular.
- Existing proposal: position 37 → “worship” (YLT position 48).
- New proposal: position 37 → “doth” (YLT position 47), an English auxiliary in the verbal phrase.

## Implemented shadow work

- Added 12 phrase groups.
- Added 14 alignment rows: 10 proposed phrase members, one legacy-overlap candidate, and three alignment-level not_expressed YLT tokens.
- Updated two existing proposal records: corrected εἰς position 20 from YLT “to” (26) to “for” (29), and attached the existing δέ→“and” proposal to the variant-sensitive “and also” phrase group.
- Reconciled token-review states for the 10 newly proposed YLT tokens and the one legacy-overlap candidate.
- Updated/created Greek token-review counts for the affected Greek endpoints.
- Preserved all production legacy rendering rows and existing legacy links.

## Evidence classification

- **Directly observed:** exact YLT verse text, 48 YLT token positions, 37 Greek sequence positions, Robinson branch payloads, and existing legacy mappings.
- **Imported grammatical analysis:** F. F. Bruce’s account of the infinitive dependencies and predicative εἰς construction.
- **Strong contextual proposals:** “is in danger”, “for us”, “of coming”, “for nothing”, “to be reckoned”, “about”, “to be brought down”, and “doth worship”.
- **Moderate grammatical dispositions:** the two supplied copulas and the English article before “temple”; kept token-table pending because the schema lacks a not_expressed state.
- **Open/retained ambiguity:** the legacy “be” position conflict and the YLT source’s δέ/τε reading in Robinson group 44:22.
- **Not established:** the inherited YLT branch A selection is not evidence of Young’s editorial reading.

## Post-update validation (2026-11-07)

- Alignment groups: 56.
- Alignment rows: 635 — 591 proposed, 36 not_expressed, seven legacy_overlap_review, one unresolved.
- YLT token review: 546 proposed, 474 pending_review, 43 legacy_overlap_review, 2,108 legacy_only.
- Greek token review: 525 proposed, 33 pending_review, 31 legacy_overlap_review.
- Full v11 validator passed: [final validation output](FINAL_VALIDATION_AFTER_ACTS_19_27_20261107.txt).
- Production counts unchanged: 141,009 gnt_words; 143,227 gnt_ylt_renderings; 31,102 YLT verses; 31,102 non-null stored embeddings.
- Pre-update schema-only shadow backup: `/var/backups/bible-postgres-20261106T171837Z/bible_greek_bridge_test_ylt_profile_shadow_20261107_pre_acts19_27.dump`; SHA-256 `57f1d5accbaf3e609f3e812d237256895d94ffebe740b403254a69738e590958`.
- Post-update schema-only shadow backup: `/var/backups/bible-postgres-20261106T171837Z/bible_greek_bridge_test_ylt_profile_shadow_20261107_after_acts19_27.dump`; SHA-256 `3e39c4b4b51dc0d3173618c11c63986aa2626dcb3dea5919b2a5dac0c7d65d45`.

No production DDL/DML, embedding generation, vectorizer changes, API changes, merge, or deployment occurred.