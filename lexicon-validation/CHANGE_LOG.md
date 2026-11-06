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
- An initial 91,500,544-byte custom-format dump was created in the OneDrive folder and hashed. A later 195,708,448-byte archive replaced it at that same path; the current file is documented in BACKUP_REPORT.md.
- `pg_restore -l` read the archive and `pg_restore --exit-on-error` restored it into isolated database `bible_restore_verify_20261106` with exit code 0.
- Independent counts matched production for 11 key tables. The dump used `--no-owner --no-acl`; global roles were not included. OneDrive cloud replication was not independently confirmed.
- Downloaded and inspected the pinned CrossWire KJV 3.1 module and Robinson TR source files. The root cause is now traced to `build_nt.py` `parse_tr()` skipping pipe-delimited variant/morphology records, omitting `autou` in John 9:21 and `barnaba` in Colossians 4:10. Issue #1 was updated with source pins and a corrected repair plan.
- A validator run against the restored database returned zero for several Greek/rendering tables despite the independent count check showing matching nonzero counts. This inconsistency is unresolved and is explicitly recorded; do not trust that restored-snapshot validator result until reconciled.
- No production data, deployed code, or computed lexicon rows were changed.

## 2026-11-06 — Backup artifact reconciliation and security note

- A separate full backup set under `/var/backups/bible-postgres-20261106T171837Z/` and its manifest were discovered and verified to exist by file metadata. The manifest records a 195,708,631-byte database archive, 1,088-byte globals export and 22,018-byte archive catalogue.
- The portable OneDrive-path archive currently measures 195,708,448 bytes. This supersedes the earlier 91.5 MB file and its checksum.
- The globals export contains SCRAM password hashes. It is sensitive and must not be committed to GitHub or copied to an unencrypted cloud location. The manifest reports restrictive Linux permissions, but the Windows/WSL file metadata interface returned mode 666; actual WSL permissions still need direct verification before treating the file as protected.
- The backup manifest's checksums and 47-table comparison have not yet been independently recomputed in this phase. The restored-snapshot validator inconsistency remains open.

## 2026-11-06 — SBL bridge inventory correction

- The current PostgreSQL backup catalogue and pg_dump log show SBL-related tables including gnts_alignment and gnts_ylt_renderings. This contradicts the earlier unverified statement that the SBL bridge had not been synchronized to PostgreSQL.
- The SBL table row counts and mapping coverage have not yet been measured; the Flask API serving path still requires verification. The debugging report and issue log should treat this as an open integration/coverage question, not a confirmed missing-table defect.

## 2026-11-06 — SBL field-semantics review

- Inspected build_gnts_bridge.py and export_sync_gnt.py on master. The bridge builder explicitly describes the SBL/MorphGNT lemma field as a normalized word form (example ἐγέννησε(ν)), not a lexical dictionary lemma.
- Confirmed the repository export bundle includes gnts_alignment and gnts_ylt_renderings; the earlier statement that the SBL bridge was not synchronized is withdrawn. The PostgreSQL archive/catalogue also contains the SBL bridge table names.
- Updated issue #2: the API's exact match compares a normalized SBL word form with a transliterated LXX lexical lemma, which is a semantic as well as representation mismatch.
- Updated the inventory and validation dataset to measure SBL bridge row counts and API serving separately. No SBL data was changed.

## 2026-11-06 — Greek variant API tracking

- Created GitHub issue #6 to define and expose the existing Byzantine and SBL bridge tables through the API, while keeping witness positions separate.
- Updated ISSUE_LOG.md. The issue is an integration/design investigation; table counts and intended reader behavior still need verification.

## 2026-11-06 — TR parser regression reproducer

- Added `eval/test_nt_parser_variants.py` with focused John 9:21 and Colossians 4:10 source fixtures.
- The tests assert first-reading selection: John 9:21 uses the first Strong's alternative (G848), and Colossians 4:10 uses the first morphology alternative (N-GSM). The upstream librobinson reader also supports second-reading selection; explicit second-reading tests remain to be added.
- Tests are marked expected-failure against current master because the parser has not yet been fixed. They have not been executed in this phase.
- No parser implementation or production data was changed.

## 2026-11-06 — Upstream Robinson variant parser reference

- Inspected the MIT-licensed byztxt/librobinson parser. Its book.py normalizes three pipe-delimited variant patterns and selects either the first or second reading; verse.py assigns positions to the selected sequence; word.py has separate alternate Strong's and alternate morphology fields.
- Corrected issue #1 and the regression specification: pipe-delimited groups are alternative readings, not automatically one token with all alternatives attached or multiple sequential tokens. The primary TR reading policy must be explicit and checked against CrossWire lemma.TR compatibility.
- The focused parser tests now specify first-reading output. The second-reading path and corpus-wide pipe-pattern survey remain open.
- No builder code or production data has been changed.

## 2026-11-06 — Corpus-wide Robinson pipe-variant survey

- Surveyed all 27 pinned Robinson UTR book files. Found 431 physical source lines containing pipe markers; this is a line count, not a variant-group count.
- Applied librobinson's three documented shorthand regexes: 39 surface-alternative matches, one alternative-morphology match and one alternative-Strong's match (41 total).
- Found no M5:, M6:, VAR: or :END control markers in these 27 files.
- Confirmed the current builder's regex-only parser lacks librobinson's general first/second variant selection. The fix must use the upstream variant semantics across the whole corpus, not patch only John 9:21 and Colossians 4:10.
