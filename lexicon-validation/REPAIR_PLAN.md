# YLT Lexicon Repair Plan

**Status:** Proposed; no repair authorized or applied.

## Gate 0 — Preserve the production baseline (partly complete; blocking items remain)

- A full custom-format dump and a separate globals export are recorded in BACKUP_REPORT.md.
- The files exist on Lampy; metadata sizes were checked. The archive catalogue is readable.
- The OneDrive-path copy restored into isolated database bible_restore_verify_20261106 with pg_restore --exit-on-error completing successfully.
- Independent row counts matched production for eleven key tables.
- The manifest records checksums and a 47-table comparison; those checksum values and the full 47-table comparison have not yet been independently rerun in this phase.
- OneDrive cloud sync is unconfirmed. The restore used --no-owner --no-acl; ownership/ACL and globals restoration remain untested. The globals export contains SCRAM password hashes; restrict access and verify actual Linux file permissions (manifest says 0600, Windows/WSL metadata view reported 666).
- A restored-snapshot validator run returned zero for several Greek/rendering tables despite the independent count comparison showing those tables populated. Reconcile this before relying on the validator against snapshots.

No production data mutation is permitted until checksums, off-host replication, and a recovery-grade restore including the required roles/permissions have been verified.

## Gate 1 — Reproduce defects outside production

- Build a read-only extraction harness for the eight initial validation passages.
- Capture source Greek tokens, KJV encoded source references, YLT USFM tokens, stored bridge rows and API JSON.
- Add invariants for in-range Greek positions, same-witness parent references, duplicate mappings, orphan mappings and token order.
- Reproduce John 9:21 and Colossians 4:10 from source files and database snapshot.
- Preserve current mappings verbatim in the test fixture as the before-state.

## Priority 1 — Robinson TR parser and Greek positional bridge

**Confirmed upstream cause:** build_nt.py parse_tr() does not implement the Robinson file format's pipe-delimited first/second-variant syntax. A survey of all 27 UTR files found 431 physical lines containing pipe markers and 41 matches to librobinson's three shorthand-normalization patterns (39 surface alternatives, one morphology alternative, one Strong's alternative). The parser repair is therefore corpus-wide. The official MIT-licensed librobinson library normalizes these patterns and selects one reading explicitly. The current regex skips the selected token in these cases:
- Colossians 4:10: barnaba 921 | {N-GSM} | {N-DSM} | ... — first reading has one Barnabas token with N-GSM; second reading uses N-DSM.
- John 9:21: autou 848 | autou 846 | {P-GSM} ... — first and second readings differ in Strong's value.

The current stored TR verses have 20 instead of 21 first-reading tokens in Colossians 4:10, and 23 instead of 24 in John 9:21. CrossWire KJV lemma.TR references retain these positions, creating the observed out-of-range bridge rows and orphan YLT renderings.

Proposed minimal repair:

1. Extend the TR parser to recognize the pipe-delimited alternatives.
2. Preserve one occurrence per Greek token; keep alternative Strong's and morphology analyses as explicit metadata, not extra positions and not discarded data.
3. Rebuild the TR token stream only in a disposable database; compare every token against the pinned Robinson source.
4. Check every CrossWire lemma.TR reference against the parsed token identity, not only a small sample.
5. Only after source-to-token parity is proven, rebuild the KJV-to-TR and YLT bridge in the disposable database.
6. Require zero unexplained out-of-range references, orphan mappings or unrelated row changes; review all differences.

Do not shift all positions by one, merge Greek witnesses, or regenerate the Hebrew lexicon.

## Priority 2 — SBL lexical field semantics and gloss mapping

1. Determine exact lemma encodings and source versions in MorphGNT and LXX.
2. Prefer a direct Greek-script lexical source with documented licensing and lemma identifiers.
3. If a crosswalk is required, store canonical lemma, source lemma, target lemma, matching method and confidence separately.
4. Report ambiguous and missing matches rather than selecting an arbitrary gloss.
5. Add tests for accent, breathing, final sigma, Unicode normalization and genuinely different lemma conventions.

## Priority 3 — PWA provenance

Preserve the existing API value and render the provenance note in the PWA. This is a presentation-only correction and must not alter lexicon data.

## Priority 4 — G0 and morphology

- Inspect original source records for every G0 occurrence and document the upstream convention.
- Retain unresolved morphology verbatim; add a parse only with source grammar evidence and a test.

## Priority 5 — Byzantine/SBL integration and schema integrity

- Define product requirements for which witnesses expose YLT mappings.
- Confirm the intended key and uniqueness semantics before adding constraints.
- Test constraints and indexes on a disposable database first.
- Do not add foreign keys or uniqueness rules based solely on a presumed schema; inspect all existing data and bridge semantics.

## Production release gate

A production migration requires:

- A verified restorable backup.
- Reviewed migration SQL and rollback plan.
- Exact row-level before/after diff.
- Passing unit, integration and gold tests.
- Approval of linguistic ambiguities.
- Explicit user approval before production data changes.

## Recompute policy

No full lexicon recomputation is planned. Repairs should be limited to affected mapping rows or API presentation, preserving existing computed artifacts and provenance.
