# YLT Lexicon Final Validation Report

**Status:** NOT COMPLETE — initial discovery only  
**Report date:** 2026-11-06

## Readiness assessment

The current computed YLT lexicon is **not yet validated for release as a fully correct word-level lexicon**. The Hebrew path has an existing manual gold baseline and substantial computed coverage, but remains best-effort. The Greek path has confirmed positional defects whose upstream cause is now traced to the TR parser dropping pipe-delimited variant records, plus the SBL lookup defect.

## Completed

- Created a PostgreSQL custom-format backup and separate globals export; checksums and archive readability verified.\n- Restored a portable copy into an isolated database; exact row counts matched across all 47 public tables, extension versions matched and no invalid indexes were found.\n- Added `BACKUP_REPORT.md` with paths, hashes and remaining recovery limitations.\n
- Identified live PostgreSQL as the current authoritative store.
- Recorded selected table sizes and baseline counts.
- Identified Hebrew and Greek source/build paths.
- Traced the PWA and legacy Flask API consumption path.
- Reproduced two Greek positional alignment anomalies.
- Identified the SBL lemma representation mismatch and lost PWA provenance.
- Specified an initial representative validation dataset and safe repair gates.

## Not completed

- Recovery-grade PostgreSQL backup preserving ownership/ACLs and global roles, off-host replication confirmation, and restore under intended application roles. (A local data/schema dump restored successfully and key table counts matched; remaining recovery metadata and off-host confirmation are incomplete.)
- Full table/constraint/FK inventory and data fingerprints.
- Full source archive checksum and exact source-version pinning. (Robinson source commit and two relevant source-file blob IDs are now pinned; broader corpus pinning remains.)
- Machine-executable Greek gold dataset and parser-specific tests for pipe-delimited variant records.
- Full OT/NT alignment coverage analysis.
- Independent linguistic review of proposed expected word mappings.
- Repair implementation and regression run.
- Full PWA/API end-to-end validation after correction.

## Known limitations

- Computed YLT word associations are hypotheses derived from alignment, not publisher-provided interlinear data.
- LXX-derived glosses are not direct NT lexical definitions.
- Greek textual witnesses must remain separate.
- Some source/edition and morphology questions remain unresolved.

## Release recommendation

**Not ready for validated release.** Preserve the current production data, complete backup/restore verification, build executable regression tests on a snapshot, then repair the Greek positional bridge and SBL lookup in isolation. Do not regenerate the lexicon or modify production data as part of this phase.
