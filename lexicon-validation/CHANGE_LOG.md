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
