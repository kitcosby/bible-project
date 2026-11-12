# Staging database snapshot — 2026-11-12

## Purpose

Checkpoint the consolidated Bible search/staging database before the next test round. This is a staging artifact, not a production database export.

## Source artifact on Lampy

- Path: `/tmp/bible_search_stage_20261109_20261112.dump`
- Format: PostgreSQL custom-format dump (created for `pg_restore`)
- Observed size: approximately 1.4 GB
- SHA-256: `501e87f49995e0bc5d13b6d9c98e918a3729f5620f32d988823ea2875e988c92`
- Captured/observed: 2026-11-12

The checksum above was computed against the source file on Lampy. Verify it again after transfer or download before restoring.

## Known state at checkpoint

- Staging spelling embeddings: 528,565 rows.
- Hebrew embeddings: 23,217 stored; reported complete.
- Greek embeddings: not started; 250 rows present against a target of 31,311.
- A separate reconciliation audit reported a 49-table structural match. That statement is not a claim that this dump contains exactly 49 tables.
- The staging import was separately confirmed by hash verification (recorded in the activity log).

## Important distinctions

- This artifact is the staging search database dump, not `/tmp/bible-2026-11-11.dump` (the separate, approximately 257 MB Bible database backup).
- Do not restore this artifact over production.
- Do not infer vector finiteness across every component from sampled checks. Dimensions, nulls, and key coverage were checked across the row set; finiteness checks were sample-based.
- The reconciliation database's IVFFlat index was absent at the last independent check. The staging search database's index state is a separate matter.

## GitHub storage

This repository commit records the snapshot identity and verification instructions. The 1.4 GB binary is intentionally not committed to Git history. It must be attached as a GitHub Release asset (or stored in another explicitly approved large-artifact store) and the uploaded asset re-hashed against the SHA-256 above.

**Release asset status: uploaded and verified (2026-11-12).**

- Release: https://github.com/kitcosby/bible-project/releases/tag/staging-snapshot-2026-11-12
- Tag: `staging-snapshot-2026-11-12`, targeting commit `0efec41a80b2e8f751734c47ce7d076badc6fa85`
- Asset: `bible_search_stage_20261109_20261112.dump` (asset id 739308886)
- Asset download URL: https://github.com/kitcosby/bible-project/releases/download/staging-snapshot-2026-11-12/bible_search_stage_20261109_20261112.dump
- Asset size: 1,489,597,846 bytes — exact match to the source file on Lampy.
- Verification: the GitHub API asset record reports digest `sha256:501e87f49995e0bc5d13b6d9c98e918a3729f5620f32d988823ea2875e988c92`, an exact match to the source SHA-256 recorded above. Upload completed 2026-11-12T12:32:47Z; the source dump on Lampy was not modified or deleted.
- Remaining limitations: this remains a staging snapshot, not a production export. Its Greek verse embeddings are incomplete (250 of 31,311 rows) and its Hebrew count and other known-state notes above stand as recorded at checkpoint time. The distinctions in the section above (including sample-based vector finiteness and the reconciliation database's separate IVFFlat matter) still apply.

## Restore verification

1. Obtain the release asset.
2. Run `sha256sum bible_search_stage_20261109_20261112.dump` and require the exact SHA-256 recorded above.
3. Inspect the archive with `pg_restore -l`.
4. Restore only into a newly created, isolated staging/reconciliation database.
5. Compare table counts and key coverage before using it for tests.
