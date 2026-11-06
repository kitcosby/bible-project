# YLT Lexicon Repair Plan

**Status:** Proposed; no repair authorized or applied.

## Gate 0 — Preserve the production baseline

**Partially complete; off-host and full ownership/ACL verification remain open.**

1. PostgreSQL 16.10 and live database identity confirmed.
2. Full custom-format logical dump and globals export created.
3. SHA-256 hashes and archive-list validation recorded.
4. Portable OneDrive-path copy restored into an isolated database; exact row counts for all 47 public tables matched, extension versions matched and invalid index count was zero.
5. Backup report records current table counts and hashes.
6. OneDrive cloud synchronization completion has not been independently confirmed; full owner/ACL restore has not yet been exercised.

Historical `app_v2.py.bak-*` files are application-code backups, not database backups. Current local dump: `C:\\Users\\kitco\\OneDrive\\BibleBackups\\bible-20261106.dump`; SHA-256 `7e41a2abc13a9b558c16d209611868d7ac36ff15847a1f5147892be61f2e4377`; 91,500,544 bytes. Restored to `bible_restore_verify_20261106` with `pg_restore --exit-on-error`; independent key-table row counts matched. A restored-snapshot validator run disagreed with the independent count check and needs investigation. No production mutation is permitted until the remaining backup checks are complete.

## Gate 1 — Reproduce defects outside production

- Build a read-only extraction harness for the eight initial validation passages.
- Capture source Greek tokens, KJV encoded source references, YLT USFM tokens, stored bridge rows and API JSON.
- Add invariants for in-range Greek positions, same-witness parent references, duplicate mappings, orphan mappings and token order.
- Reproduce John 9:21 and Colossians 4:10 from source files and database snapshot.
- Preserve current mappings verbatim in the test fixture as the before-state.

## Priority 1 — Greek positional bridge

Proposed minimal repair:

1. Compare CrossWire's embedded TR source references against the pinned Robinson TR token stream for each verse.
2. Resolve references by source token identity/surface and local context, not by an assumed global offset.
3. Reject unresolved/out-of-range references and emit an explicit diagnostic report.
4. Rebuild only the affected bridge rows in a disposable database.
5. Compare all other verses against the pre-repair baseline; require zero unexplained changes.
6. Run the expanded Greek gold set and manual review before proposing production migration.

Do not shift all positions by one or replace the existing Greek witness.

## Priority 2 — SBL lemma/gloss mapping

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
