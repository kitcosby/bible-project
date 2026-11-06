# YLT Lexicon Final Validation Report

**Status:** NOT COMPLETE — Phase 2 baseline and source diagnosis underway  
**Report date:** 2026-11-06

## Readiness assessment

The computed YLT lexicon is **not yet validated for release as a fully correct word-level lexicon**.

- Hebrew alignment has an existing manual gold set and a measured baseline; it remains best-effort, not an authoritative interlinear.
- Greek TR alignment contains confirmed positional defects. The upstream cause is traced to build_nt.py parse_tr() failing to implement the pinned Robinson source's first/second pipe-variant syntax. The MIT-licensed librobinson parser provides the reference behavior; the intended primary variant policy still needs compatibility testing.
- SBL lemma/gloss lookup fails because Greek-script MorphGNT lemmas are compared directly with transliterated LXX lemmas.
- The PWA drops the API's LXX-derived Greek lexical provenance note.
- SBL and Byzantine bridge tables exist in PostgreSQL. Their row counts and structural integrity are now measured; the API serving coverage and reader-facing witness/provenance behavior still require review.

## Completed

- Created a dedicated ylt-lexicon-validation branch and seven initial validation records, plus a backup report.
- Added a read-only PostgreSQL validator and ran it against the live production database.
- Confirmed 3 out-of-range TR bridge rows and 3 orphan TR YLT rendering rows; Hebrew and Byzantine structural checks passed.
- Traced the John 9:21 and Colossians 4:10 defects to the current TR parser's failure to implement Robinson first/second pipe-variant selection. Surveyed all 27 UTR files: 431 physical lines contain pipe markers, with 41 matches to librobinson's three shorthand-normalization patterns.
- Created five actionable GitHub issues (#1–#4 and #6); duplicate issue #5 was closed.
- Located a full custom-format backup, globals export and manifest; verified file existence, sizes and archive catalogue readability.
- Restored the backup into isolated database bible_restore_verify_20261106; `pg_restore --exit-on-error` completed, all 47 public-table row counts matched, 68 catalog objects across public/ai had matching owner and ACL metadata, extensions/versions matched, and neither database had invalid indexes. This is a same-cluster restore test, not a separate-cluster disaster-recovery test.

## Remaining blockers

- Independently recompute the backup archive and manifest checksums; the restore and table/metadata comparisons have passed, but checksum verification remains distinct.
- Confirm OneDrive cloud sync or another off-host copy.
- Test restoration onto a separate PostgreSQL cluster and independently exercise globals/role recovery; the current restore test was same-cluster and roles already existed.
- Implement the Robinson pipe-variant parser correction in an isolated branch, add explicit second-reading tests, and expand the Greek gold set. The focused first-reading tests have now been executed and both reproduce the expected failures on master.
- Extend full-corpus schema, FK and semantic alignment checks beyond the current validator's covered invariants.
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


## 2026-11-06 — Isolated Robinson variant rebuild

A variant-aware TR sequence and shadow bridge were built and validated in `bible_greek_bridge_test_20261106`, not in production. The resolved subset achieved 99.90% `lemma.TR` agreement and zero out-of-range positions; John 9:21 and Colossians 4:10 are corrected in the shadow sequence. Shadow integrity checks found no non-contiguous token positions, duplicate bridge keys, missing Greek references, or orphan YLT renderings.

This does **not** complete production validation. Nineteen groups across 17 references remain unresolved, and ten legacy Colossians 4:18 edges are classified as colophon-only. The existing YLT rendering edge set is unchanged on resolved verses. The embedding vectorizer and public corpus remain unchanged. Production status remains **not approved** pending review of unresolved variants and the colophon exclusion. See [ROBINSON_VARIANT_REBUILD_REPORT.md](ROBINSON_VARIANT_REBUILD_REPORT.md).
