# PostgreSQL Backup and Restore Verification

**Date:** 2026-11-06  
**Database:** `bible`  
**Server:** PostgreSQL 16.10  
**Result:** Database dump created; isolated restore completed and validated. Cloud synchronization of the OneDrive-path copy remains unconfirmed.

## Backup set A — Full local logical backup

Directory on Lampy:

`/var/backups/bible-postgres-20261106T171837Z/`

| File | Bytes | SHA-256 |
|---|---:|---|
| `bible.dump` | 195,708,631 | `c8001a92bd0f5acfd2c64760ad04eaca826b569a8e08e1e02a9f0a14c1f55073` |
| `globals.sql` | 1,088 | `9511336a405fd17ef1df2dabbb1145924152f8a258548567ae84d61fa4b1bacc` |
| `archive-list.txt` | 22,018 | `9d8c4ea0ec629c6b70e11655af2a5531a6ea0f70d1d1e227b7ff4d779b839d78` |
| `manifest.json` | — | Contains the file hashes and restore-test record |

- Database dump: PostgreSQL custom archive, compression level 6.
- Globals export: roles and other cluster-global definitions from `pg_dumpall --globals-only`.
- Archive readability: `pg_restore --list` completed successfully (319 archive entries).
- Local directory is owned by the PostgreSQL service account with mode 0700; backup files are mode 0600.
- This is a logical backup, not a physical/base backup. PostgreSQL configuration files and WAL are not included.

## Backup set B — OneDrive-path portable copy

Path on Windows:

`C:\Users\kitco\OneDrive\BibleBackups\bible-20261106.dump`

| Attribute | Value |
|---|---|
| Size | 195,708,448 bytes |
| SHA-256 | `f34e99854ee108f025db1fc1645a885fdefab5dafbd49852fcedc8f271292889` |
| Format | PostgreSQL custom archive |
| Archive readability | `pg_restore --list` succeeded; 319 entries |
| Restore options | `--no-owner --no-acl` |

The OneDrive client process was running and the file resides under the OneDrive directory. **Cloud upload/synchronization completion was not independently confirmed.** Do not rely on this copy as an off-host backup until the OneDrive client reports that synchronization is complete.

## Restore test

The OneDrive-path archive was restored with `pg_restore --exit-on-error` into a separate database:

`bible_restore_verify_20261106`

This did not overwrite or alter the production `bible` database.

Results:

- Restore command completed; no active restore sessions remained.
- Restored database size: approximately 1,086 MB.
- Production database size at validation: approximately 1,174 MB.
- Exact row counts compared for all 47 public tables: **zero differences**.
- Extensions matched: `plpgsql 1.0`, `vector 0.8.0`.
- Invalid indexes: 0 in production and 0 in restored database.
- Key lexicon counts matched, including Hebrew `words` (264,217), `ylt_renderings` (358,391), `lexicon_ylt_rendering` (234,091), TR `gnt_words` (141,009), `gnt_ylt_renderings` (143,227), Byzantine `gntb_words` (140,149), `gntb_ylt_renderings` (141,902), SBL `gnts_words` (137,554), and `lxx_words` (623,693).

The restore test used `--no-owner --no-acl`, so it validates schema/data restoration, not restoration of original object ownership and ACLs. The separate globals export and full local archive preserve those items, but an isolated full-owner/ACL restore test has not yet been run.

## Recovery limitations and next checks

1. Confirm OneDrive upload/sync completion from the Windows client.
2. Copy the backup to an independent off-host location or verify OneDrive cloud availability from another device/session.
3. Perform a separate isolated restore using the full local archive and globals export, validating owner/ACL recovery without replaying global role changes into production.
4. Record the restore procedure and required PostgreSQL/pgvector versions.

**Safety:** No production rows, schema, application files or computed lexicon entries were changed during backup or restore verification.
