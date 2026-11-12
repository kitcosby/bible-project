# BibleApp presentation and schema safety review — Hebrew vowel-only variants

**Status:** design review only; no production schema, API, UI, or data changes.  
**Reviewed artifacts:** `HEBREW_VOWEL_VARIANT_SCHEMA_PROPOSAL_20261107.md`, `HEBREW_VOWEL_VARIANT_STUDY_GUIDE_20261107.md`, the isolated-shadow validation results, and the Ezekiel 27:32 follow-up.  
**Decision:** the isolated shadow schema is a sound research prototype. Production adoption should remain gated on the controls and acceptance tests below.

## 1. What is already sound

1. **No lexical merge:** groups point to existing `root_vowel` records; they do not replace root, root-form, lexicon, Strong's, morphology, or occurrence records.
2. **Language isolation:** Hebrew and Aramaic are distinct populations, with language scope included in membership constraints.
3. **Reproducibility:** the group records an algorithm version, NFC comparison policy, and source-snapshot identifier.
4. **Raw-source preservation:** NFC is a comparison-key operation only. The original pointed source string remains authoritative and unchanged.
5. **Strict codepoint policy:** only U+05B0–U+05BB and U+05C7 are removed. Matres, dagesh/mapiq, meteg, cantillation, shin/sin dots, separators, and other marks remain significant.
6. **Apparatus separation:** qere/ketiv, external textual witnesses, and YLT translation/alignment are not canonical members of the orthographic group.
7. **Isolation:** the prototype was built and validated in a separate shadow database. Production has not been changed.

## 2. Schema-level gaps to close before production

These are not failures of the current shadow build; they are requirements for a production-grade interface and validator.

### A. Enforce distinct pointed forms, not merely distinct member keys

The DDL's primary key ensures distinct member keys, but it does not by itself enforce the candidate rule that a group contain at least two **distinct NFC pointed forms** after the specified vowel removal. Two member keys could, in principle, resolve to the same pointed form.

**Required control:** the independent builder/validator must count distinct normalized pointed forms per group and reject groups with fewer than two. Add a regression fixture where two different root-vowel keys carry the same pointed form; it must not qualify as a two-form group.

### B. Make review status semantically precise

The illustrative `review_status` values include `reviewed`. That label is too ambiguous for BibleApp: a group may have been checked at member level without receiving full contextual lexical adjudication, and adjudication does not imply semantic equivalence.

**Required control:** document status semantics explicitly or use separate fields for (1) candidate-generation state, (2) member-level review state, and (3) lexical/text-critical adjudication state. Never encode “synonym,” “same lexeme,” or “safe to merge” as an implication of orthographic review. The current 372/372 figure means member-level inspection only.

### C. Preserve provenance for every displayed occurrence

The member table points to `root_vowel`; occurrences are resolved through `words`. UI and API responses should carry the actual source token, verse reference, language, and source-snapshot context from the occurrence row, not synthesize a pointed form from the signature.

**Required control:** display the raw source spelling for each occurrence and keep the normalized signature hidden or explicitly technical. Never use the signature as replacement text.

### D. Make source freshness visible

A group inventory is valid for a particular source snapshot and algorithm version. A newer OSHB/source import must not silently display stale groups as current.

**Required control:** expose build metadata (source snapshot, algorithm version, build timestamp, validation status) to maintainers; make the UI/API fail closed or mark the inventory stale when the active source snapshot does not match. Do not automatically rebuild or publish on source import without independent validation.

### E. Keep apparatus and translation data in separate relations

Ezekiel 27:32 is the decisive test. The MT word `בְּנִיהֶם֙` (H5204) remains the base-text record; `בְּנֵיהֶם֙` (H1121) remains a separate lexical member; “their sons” in the Old Greek is external witness evidence; YLT's “their sons” is translation evidence with a separate alignment anomaly. These are related but not interchangeable data types.

**Required control:** an apparatus/witness object must identify witness class, named witness or edition, reading language and exact reading, locus/token scope, source citation, and confidence/verification state. An LXX reading must not be inserted as an MT pointed-form member or fabricated as an MT qere. A YLT gloss/alignment must not be used to infer a Hebrew source reading.

## 3. Recommended BibleApp interaction

Use a modest “Related pointed forms” section on a word detail page. Avoid a global synonym label, automatic replacement, or default collapsing of lexicon entries.

For each linked member, show:

- Exact pointed form as stored in the source.
- Language (Hebrew or Aramaic).
- Existing root, Strong's, morphology, and gloss as separate fields.
- Occurrence count and a drill-down to actual verse occurrences.
- A neutral explanation: “Linked by the project's vowel-only orthographic comparison; lexical identity and meaning are not implied.”
- A visible distinction between same-root/form-family links and cross-root links, without ranking one as more correct.

Keep textual witnesses in a separate “Textual notes” area with explicit witness labels and citations. Keep translation and alignment in their existing layer.

### Ezekiel 27:32 acceptance example

The page for the MT token should continue to display `בְּנִיהֶם֙`, H5204, and the existing source morphology. Its related-form link may expose `בְּנֵיהֶם֙`, H1121, but the two entries must remain separate. A separate textual note may say that the Old Greek reads “their sons” and that Hebrew manuscript support is reported but not yet fully collated. The project default is MT; text-critical priority remains open. The YLT rendering “their sons” must be labelled as translation, not as an MT correction.

## 4. Minimum release acceptance tests

1. **No source mutation:** compare production source-table row counts and checksums before/after any deployment; no `words.pointed`, root, lexicon, Strong's, morphology, or alignment update is part of this feature.
2. **Distinct-form invariant:** every published group has at least two distinct normalized pointed forms under the exact versioned codepoint policy.
3. **Retained-mark negative tests:** changing dagesh, mapiq, meteg, cantillation, shin/sin dot, maqaf, paseq, matres, final forms, or morpheme delimiters must prevent a match when the retained signature differs.
4. **Language isolation:** Hebrew and Aramaic never join in one group.
5. **Qere/ketiv isolation:** apparatus readings do not appear as canonical members.
6. **Snapshot check:** stale or unvalidated inventory cannot be presented as current.
7. **No semantic side effects:** no auto-merge, redirect, root substitution, Strong's replacement, morphology rewrite, alignment rewrite, or synonym assertion.
8. **Occurrence integrity:** every displayed occurrence resolves to the original `words` row and displays its original raw pointed string.
9. **Ezekiel 27:32 regression:** MT remains the default; H5204 and H1121 remain separate; LXX and YLT evidence remain separate; no qere is fabricated.
10. **Read-only default:** the first production-facing endpoint should be read-only and should return only validated, source-current groups.

## 5. Recommended implementation sequence

1. Keep the current shadow schema and its data unchanged as the reproducible research artifact.
2. Add the distinct-pointed-form assertion and precise review-state semantics to the validator/specification.
3. Define a read-only API response contract and test it against the isolated shadow database.
4. Add UI only after API fixtures cover ordinary same-root cases, cross-root collisions, Hebrew/Aramaic separation, and Ezekiel 27:32.
5. Run source-preservation and regression validation against a fresh isolated snapshot.
6. Obtain explicit approval before any production DDL, DML, endpoint exposure, or deployment.

## 6. Disposition

**Approved as a research prototype; not yet approved for production adoption.** The schema direction is conservative and preserves the lexical source of truth. The main pre-production work is to tighten the distinct-form invariant, review-state semantics, source-freshness behavior, and read-only API contract. No production changes were made during this review.
