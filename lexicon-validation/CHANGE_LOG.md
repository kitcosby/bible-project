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
