# YLT Lexicon Validation Change Log

## 2026-11-06 — Initial read-only discovery and documentation setup

- Inspected the live PostgreSQL `bible` database using READ ONLY transactions.
- Recorded database version, approximate size, selected table sizes and baseline row counts in `LEXICON_INVENTORY.md`.
- Inspected the repository's Greek and Hebrew computation scripts and the deployed Flask/PWA integration.
- Recorded confirmed Greek positional mapping examples and the SBL lemma representation mismatch in `DEBUGGING_REPORT.md`.
- Added representative OT/NT validation specifications in `VALIDATION_DATASET.md`.
- Added proposed issue classifications and repair gates.
- Created branch `ylt-lexicon-validation` from `master`.
- No production database, source code, generation scripts or computed lexicon rows were changed.
- No recomputation was run.
- No verified PostgreSQL backup was located during the initial check; backup verification remains a blocking item.

This log records project documentation changes only. GitHub issue creation and subsequent evidence will be appended as separate dated entries.

## 2026-11-06 — Validation branch and issue tracking

- Created branch `ylt-lexicon-validation` from `master`.
- Added the seven initial validation records under `lexicon-validation/`.
- Opened GitHub issues #1–#4 for the confirmed positional bridge defect, SBL lemma/gloss lookup defect, PWA provenance gap and Byzantine bridge integrity risk.
- A duplicate submission (#5) was immediately closed with reason `duplicate`; issue #4 is the canonical tracking item for the Byzantine bridge.
- No source code, production data or computed lexicon content changed.

## 2026-11-06 — First executable read-only validation run

- Added `eval/validate_ylt_lexicon_postgres.py`, a parameterized read-only PostgreSQL validation script.
- Executed it against the live `bible` database in a READ ONLY transaction.
- Result: 3 TR out-of-range alignment rows; 3 TR orphan YLT rendering rows; 0 Hebrew orphan renderings; 0 Byzantine out-of-range/orphan mappings; 0 duplicate keys in the tested TR/Byzantine mapping tables; 5 TR G0 occurrences; 0 SBL rows with an exact LXX lemma/gloss match.
- Confirmed the orphan YLT words: John 9:21 `shall` and `speak`; Colossians 4:10 `him`.
- Confirmed no PostgreSQL backup was identified in inspected locations. The existing `bible.db` and `bible_v2.db` files are SQLite artifacts, not PostgreSQL backups. Backup/restore verification remains blocking.
- No database rows, live application files or generation scripts were modified.

## 2026-11-06 — PostgreSQL backup and restore test

- Located a full custom-format backup, separate globals export and backup manifest under /var/backups/bible-postgres-20261106T171837Z/.
- Verified file existence and metadata sizes: bible.dump 195,708,631 bytes; globals.sql 1,088 bytes; archive-list.txt 22,018 bytes.
- Read the archive catalogue; PostgreSQL reports 324 TOC entries. The manifest records SHA-256 hashes, but those hashes were not independently recomputed in this phase.
- Verified the OneDrive-path copy exists at 195,708,448 bytes. The OneDrive process was running; cloud sync completion remains unconfirmed.
- Restored the OneDrive-path archive into isolated database bible_restore_verify_20261106; pg_restore --exit-on-error completed successfully.
- Independent row counts matched production for eleven key tables. The backup manifest also records a 47-table comparison and extension/index checks; those additional checks have not yet been independently repeated in this phase.
- The restore used --no-owner --no-acl; global roles and ownership/ACL recovery were not exercised.
- No production data or application files were changed by the restore test.

## 2026-11-06 — Backup/restore and TR parser root-cause investigation

- Installed PostgreSQL 16 client tools (pg_dump 16.15) on Lampy; no production database configuration or rows were changed by the package installation.
- Created custom-format database dump in the local OneDrive sync folder: 91,500,544 bytes; SHA-256 `7e41a2abc13a9b558c16d209611868d7ac36ff15847a1f5147892be61f2e4377`.
- `pg_restore -l` read the archive and `pg_restore --exit-on-error` restored it into isolated database `bible_restore_verify_20261106` with exit code 0.
- Independent counts matched production for 11 key tables. The dump used `--no-owner --no-acl`; global roles were not included. OneDrive cloud replication was not independently confirmed.
- Downloaded and inspected the pinned CrossWire KJV 3.1 module and Robinson TR source files. The root cause is now traced to `build_nt.py` `parse_tr()` skipping pipe-delimited variant/morphology records, omitting `autou` in John 9:21 and `barnaba` in Colossians 4:10. Issue #1 was updated with source pins and a corrected repair plan.
- A validator run against the restored database returned zero for several Greek/rendering tables despite the independent count check showing matching nonzero counts. This inconsistency is unresolved and is explicitly recorded; do not trust that restored-snapshot validator result until reconciled.
- No production data, deployed code, or computed lexicon rows were changed.
