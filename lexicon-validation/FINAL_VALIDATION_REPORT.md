# YLT Lexicon Final Validation Report

**Status:** NOT COMPLETE — Phase 2 baseline and source diagnosis underway  
**Report date:** 2026-11-06

## Readiness assessment

The computed YLT lexicon is **not yet validated for release as a fully correct word-level lexicon**.

- Hebrew alignment has an existing manual gold set and a measured baseline; it remains best-effort, not an authoritative interlinear.
- Greek TR alignment contains confirmed positional defects. The upstream cause is traced to build_nt.py parse_tr() failing to implement the pinned Robinson source's first/second pipe-variant syntax. The MIT-licensed librobinson parser provides the reference behavior; the intended primary variant policy still needs compatibility testing.
- SBL lemma/gloss lookup fails because Greek-script MorphGNT lemmas are compared directly with transliterated LXX lemmas.
- The PWA drops the API's LXX-derived Greek lexical provenance note.
- SBL and Byzantine bridge tables exist in PostgreSQL; their API serving coverage and SBL row counts remain to be measured.

## Completed

- Created a dedicated ylt-lexicon-validation branch and seven initial validation records, plus a backup report.
- Added a read-only PostgreSQL validator and ran it against the live production database.
- Confirmed 3 out-of-range TR bridge rows and 3 orphan TR YLT rendering rows; Hebrew and Byzantine structural checks passed.
- Traced the John 9:21 and Colossians 4:10 defects to the current TR parser's failure to implement Robinson first/second pipe-variant selection. Surveyed all 27 UTR files: 431 physical lines contain pipe markers, with 41 matches to librobinson's three shorthand-normalization patterns.
- Created five actionable GitHub issues (#1–#4 and #6); duplicate issue #5 was closed.
- Located a full custom-format backup, globals export and manifest; verified file existence, sizes and archive catalogue readability.
- Restored the OneDrive-path copy into isolated database bible_restore_verify_20261106; restore command completed successfully and independent row counts matched production for eleven key tables.

## Remaining blockers

- Independently recompute the backup manifest's checksums and repeat the full 47-table comparison recorded in the manifest.
- Confirm OneDrive cloud sync or another off-host copy.
- Test restoration of roles, ownership and ACLs using the globals export and full local archive.
- Reconcile the restored-snapshot validator output: it returned zero for several Greek/rendering tables although an independent count script found those tables populated.
- Execute the new expected-failure source-parser tests, implement the parser correction in an isolated branch, and expand the Greek gold set.
- Complete full-corpus schema, FK, duplicate, orphan and coverage checks.
- Independently review ambiguous lexical/morphological cases.
- Implement and regression-test repairs in isolation; no production migration has been approved.

## Known limitations

- Computed YLT word associations are hypotheses derived from alignment, not publisher-provided interlinear data.
- LXX-derived glosses are not direct NT lexical definitions.
- TR, Byzantine and SBL textual witnesses must remain separate.
- Some Strong's sentinel and morphology questions remain unresolved.

## Release recommendation

**Not ready for validated release.** Preserve the current production data. Finish backup recovery verification, reconcile the snapshot validator, implement the TR parser correction in isolation, and validate the SBL lookup/provenance fixes. Do not regenerate the full lexicon or modify production data as part of this phase.

## 2026-11-06 — Restored-snapshot full YLT token-position validation

The validator was downloaded from this branch and rerun read-only against `bible_restore_verify_20261106` (PostgreSQL 16.10; reported database size 1,086 MB). The run completed and emitted a JSON report.

- All four stored YLT rendering sets passed exact token-position comparison against their linked YLT verse text under the builder's whitespace-tokenization and punctuation-stripping convention:
  - Hebrew: 358,391 rows; 0 missing text, out-of-range positions or token mismatches.
  - TR: 143,227 rows; 0 in those three categories.
  - Byzantine: 141,902 rows; 0 in those three categories.
  - SBL: 135,971 rows; 0 in those three categories.
- All checked Hebrew/root/lexicon/KJV references passed (zero missing parent links).
- Byzantine and SBL alignment/rendering checks passed: zero missing verse links, out-of-range positions, orphan renderings or duplicate keys.
- TR checks still report exactly 3 out-of-range Greek positions and 3 orphan YLT rendering rows. The KJV positions themselves are in range; duplicate-key and missing-parent checks are zero. These are the known John 9:21 and Colossians 4:10 parser/bridge defects.
- Diagnostics remain: 5 TR G0 occurrences; 1 unparsed morphology pattern; Strong's dictionary contains Hebrew only (19,058 rows); 0 exact SBL normalized-form/LXX-lemma matches. These diagnostics are not automatically classified as corruption.
- Ran the focused parser regression tests against `master/build_nt.py`: both John 9:21 and Colossians 4:10 were reported as expected failures, confirming the reproducer still detects the parser defect. The tests are intentionally marked expected-failure; no parser code was changed.

Interpretation: the stored English rendering positions and token strings are internally consistent across all four witnesses. This does not prove that each Greek token has the correct English association; the three TR bridge defects remain. The validator's punctuation/token convention is a structural consistency test, not a semantic alignment gold standard. No production rows or application files were changed.
