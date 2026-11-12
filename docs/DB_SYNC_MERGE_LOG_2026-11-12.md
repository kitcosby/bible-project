# Database sync and merge log — 2026-11-12

## Scope

Promote and verify the recovered Hebrew spelling-variant embedding search store for the live Flask application, then reconcile the production search database's word metadata with the canonical corpus. This was a data-only operation. No schema changes, service restarts, credential changes, application-code changes, or vector regeneration were performed.

## Databases

| Role | Database | Purpose |
|---|---|---|
| Canonical corpus | `bible` | Authoritative books, verses, words, and spelling variants |
| Live variant search | `bible_search_prod_20261111` | Separate search-side metadata and 528,565 Hebrew spelling embeddings |
| Search staging | `bible_search_stage_20261109` | Previously validated staging copy |
| Reconciliation staging | `bible_reconcile_20261111` | Recovery/import audit target; not the live application target |

The live Flask process was observed using `bible_search_prod_20261111` through `BIBLE_VARIANT_SEARCH_DATABASE_URL` and the read-only role `bible_search_prod_ro`.

## Pre-merge findings

- The production search database and canonical corpus had matching spelling-variant keys and content, but 1,781 of 264,217 `words` rows had stale values in one or more of `strongs`, `word_pos`, and `verse_id`.
- The other compared search-side fields (`pointed`, variant records, verses, and books) matched.
- The recovery SQLite source contained 528,565 embedding rows. The staging, production-search, and reconciliation stores had matching ordered embedding keys and vector-content fingerprints. The recovery source hash recorded in reconciliation metadata matched the current recovery SQLite file.
- Fourteen empty-text/paseq records were retained; they were not dropped or regenerated.

## Authorized operation

On 2026-11-12, refresh only these columns in `bible_search_prod_20261111.public.words` from `bible.public.words`:

- `strongs`
- `word_pos`
- `verse_id`

The operation used a transaction, checked exact row-count and key-set parity, and created a complete pre-update snapshot before changing target rows.

**Result: committed successfully.**

| Measure | Result |
|---|---:|
| Source rows | 264,217 |
| Target rows | 264,217 |
| Rows updated | 1,781 |
| Rollback snapshot | `public.words_merge_rollback_20261112` |
| Rollback rows | 264,217 |
| Source SHA-256 | `9c1b71b2feba53a0bc8a8724c00258fd3fdadb23cc19a69319b670c62ec086ae` |
| Target-after SHA-256 | `9c1b71b2feba53a0bc8a8724c00258fd3fdadb23cc19a69319b670c62ec086ae` |
| Exact full-table equality | `true` |

The transaction committed only after the complete ordered target dataset matched the source for all compared fields. The rollback table is owned by `postgres`; the app's read-only role can read it but cannot update or delete it. No privilege changes were made.

## Post-merge verification

All five parity groups matched between `bible` and `bible_search_prod_20261111`:

| Group | Rows | Fingerprint |
|---|---:|---|
| Spelling variant keys | 528,565 | `2842941d4858c8aa80c62a27b6d274dc` |
| Spelling variant content | 528,565 | `e0ece5a78b1ade542bf52b65dc5f6bd3` |
| Word search fields | 264,217 | `b9c6d8f26119bb233241cdd8879c6744` |
| Verse search fields | 31,311 | `a14309bb774f114d4db97d37d9882585` |
| Book search fields | 66 | `0fcc8b03089aeef17fc190c42e684582` |

Additional checks:
- `word_variant_embeddings` still contains 528,565 rows.
- `word_variant_embeddings_cosine_ivfflat` remains present, using `vector_cosine_ops` and `lists=512`.
- The embedding table primary-key index remains present.
- The production endpoint `/bible/api/search/variants?q=בראשית` returned HTTP 200 and 10 JSON records after the update.
- `bible_search_prod_ro` retained CONNECT and schema USAGE plus SELECT on required search tables; no write privileges were granted.

## Explicitly not done

- No rows in the canonical `bible` database were modified.
- No verse-semantic embeddings in `bible.ylt_verses_embedding_store` were modified.
- No embedding vectors were recomputed.
- No application code, environment variables, secrets, PostgreSQL configuration, Apache configuration, or service state was changed.
- No service restart or laptop reboot occurred.
- No IVFFlat index was created in `bible_reconcile_20261111`. That database lacks the cosine index, but its intended long-term role must be decided before adding one.

## Remaining reconciliation decisions

1. Decide whether `bible_reconcile_20261111` is a retained audit/archive database or an intended query target. Only if it is intended for vector search should its missing IVFFlat index be considered.
2. Decide whether the rollback snapshot should remain accessible to the read-only application role. It is currently SELECT-readable but not writable/deletable by that role; no access change has been made.
3. Continue Git branch reconciliation separately. Several historical branches have diverged substantially from `master`; they must be reviewed by unique commits and file-level conflicts rather than merged wholesale.


## PostgreSQL dump reconciliation — search staging (2026-11-12)

### Dump validation

- Source archive: `/root/backups/2026-11-08-incident/bible-2026-11-11.dump`.
- Format: PostgreSQL custom archive; 257 MB; created 2026-11-11 22:10:53 PST; 508 TOC entries.
- SHA-256: `5c62529cecc10d67e1cc0eaa2be94be20bbd346c4fcfa372f915006e5e150547`.
- Restored successfully to isolated database `bible_dump_audit_20261112`; no live database was restored over or replaced.
- The dump contains 49 public base tables and 11 `ai` schema tables.
- All 49 public tables in the dump have identical full-content fingerprints and row counts to the live canonical `bible` database. No canonical `bible` table needed an update from this dump.

### Search-stage reconciliation

Target: `bible_search_stage_20261109`. The live application continues to use `bible_search_prod_20261111`; the production search database and canonical `bible` database were not modified by this operation.

The staging database had 47 of the dump's 49 public tables. The two absent tables are `greek_verses_embedding_store` and `hebrew_verses_embedding_store`; they were not added to the separate Hebrew spelling-variant search staging database. Four stage-specific tables were retained: `hebrew_vowel_variant_group`, `hebrew_vowel_variant_member`, `word_variant_embedding_meta`, and `word_variant_embeddings`.

Eight shared tables required reconciliation. A persistent pre-update snapshot was created in schema `pgdump_sync_rollback_20261112` before any change. The snapshot contains all eight original tables and their original row counts.

| Table | Dump rows | Stage before | Missing from stage | Changed common rows | Stage after |
|---|---:|---:|---:|---:|---:|
| `strongs` | 19,127 | 19,058 | 69 | 0 | 19,127 |
| `strongs_components` | 3,922 | 3,783 | 139 | 0 | 3,922 |
| `verses` | 31,311 | 31,311 | 0 | 7 hidden-flag values | 31,311 |
| `words` | 264,217 | 264,217 | 0 | 1,781 | 264,217 |
| `ylt_renderings` | 357,574 | 358,391 | 91 | 267 | 358,482 |
| `word_alignment` | 836,290 | 836,290 | 0 | 996 | 836,290 |
| `lexicon_found_verse` | 262,802 | 262,802 | 74 | 0 | 262,876 |
| `lexicon_ylt_rendering` | 234,131 | 234,091 | 40 | 440 | 234,131 |

**Merge semantics:** source rows were inserted or updated to match the dump; no stage-only rows were deleted. This deliberately retains 908 stage-only `ylt_renderings` rows and 74 stage-only `lexicon_found_verse` rows. The dump's `verses.hidden` column was added to staging as `integer NOT NULL DEFAULT 0`; seven verses have `hidden=1`.

### Post-sync verification

- All source rows in all eight reconciled tables now match the dump exactly, including schema and primary keys.
- The other 39 shared public tables were already content-identical to the dump. Thus all 47 public tables shared with staging now contain the complete dump data; the two documented stage-only supersets remain additive.
- Rollback snapshot counts were checked: `strongs` 19,058; `strongs_components` 3,783; `verses` 31,311; `words` 264,217; `ylt_renderings` 358,391; `word_alignment` 836,290; `lexicon_found_verse` 262,802; `lexicon_ylt_rendering` 234,091.
- Referential-integrity checks returned zero orphan references for `word_alignment.ylt_rendering_id`, `ylt_renderings.word_id`, and `words.verse_id`.
- Stage-specific Hebrew variant data remains present: 3,349 groups, 7,148 members, 528,565 embedding rows, and 14 metadata rows. The IVFFlat cosine index with `lists=512` remains present.
- All compared static `ai` metadata tables matched the dump, including `ai.vectorizer`, pgai migration/version metadata, and vectorizer progress. `ai.vectorizer_worker_process` differed (18 dump rows vs 13 staging rows) and was intentionally not synchronized because it represents runtime worker state, not canonical corpus data.

### Scope boundaries

- No rows or schema in canonical `bible` were changed.
- No rows or schema in live `bible_search_prod_20261111` were changed.
- No `bible_app` database or app-owned data was included.
- No stage-specific Hebrew variant groups, members, embeddings, or embedding metadata were overwritten or deleted.
- The isolated restore `bible_dump_audit_20261112` and rollback schema `pgdump_sync_rollback_20261112` are retained as audit/rollback evidence.
