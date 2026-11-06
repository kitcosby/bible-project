# YLT Lexicon Inventory

**Status:** Initial inventory; production baseline measured 2026-11-06  
**Scope:** Existing computed Young's Literal Translation (YLT) alignments and the Hebrew/Greek data used to serve them.  
**Safety:** Discovery only. No production rows, source files, scripts, or generated artifacts were changed.

## Authority and environment

- Live serving database: PostgreSQL database `bible` on Lampy (WSL2), PostgreSQL 16.10.
- Live database size at discovery: 1,174 MB.
- The old SQLite file `/opt/bible/bible_v2.db` is not authoritative for the current production corpus. It predates the current Greek extension and later live repairs.
- The canonical source repository is `kitcosby/bible-project`, default branch `master`. The source checkout was not present at the documented Lampy workspace path during discovery.
- Serving application: `/opt/bible/website/app_v2.py`; PWA: `/var/www/html/byot/index.html`.
- Current application API routes include `/bible/api/verse/<book>/<chapter>/<verse>` and `/bible/api/word/<strongs>`.

## Live PostgreSQL baseline

Measurements obtained using a PostgreSQL transaction explicitly started READ ONLY.

| Table | Approximate on-disk size | Notes |
|---|---:|---|
| `words` | 64 MB | Hebrew/Aramaic token records |
| `ylt_renderings` | 73 MB | Computed Hebrew-token to YLT-word renderings |
| `lexicon_ylt_rendering` | 50 MB | Aggregated Hebrew lexicon YLT rendering data |
| `gnt_words` | 13 MB | Robinson TR Greek token records; 141,009 rows |
| `gnt_alignment` | 15 MB | KJV-to-TR positional bridge; 3 out-of-range rows detected |
| `gnt_ylt_renderings` | 13 MB | TR-token to YLT-word renderings; 143,227 rows, 3 orphan renderings detected |
| `gntb_words` | 12 MB | Byzantine Greek token records; 140,149 rows |
| `gntb_ylt_renderings` | 9 MB | Byzantine-token to YLT-word renderings; 141,902 rows |
| `gnts_words` | 15 MB | SBL Greek token records; 137,554 rows |
| `lxx_words` | 90 MB | LXX Greek token/lemma/gloss source data; 623,693 rows |

Additional counts measured:

- `words`: 264,217 rows.
- `ylt_renderings`: 358,391 rows.
- `lexicon_ylt_rendering`: 234,091 rows.
- `gnt_words`: 141,009 rows; `gnt_ylt_renderings`: 143,227 rows.
- `gntb_words`: 140,149 rows; `gntb_ylt_renderings`: 141,902 rows.
- `gnts_words`: 137,554 rows; `lxx_words`: 623,693 rows.

These are point-in-time production measurements, not a recoverable backup or cryptographic content manifest. Table sizes are approximate PostgreSQL total relation sizes.

## Source and computation inventory

### Hebrew Old Testament

| Layer | Source/artifact | Role |
|---|---|---|
| Hebrew text and morphology | OSHB / morphhb source family | Hebrew/Aramaic tokens, morphology and Strong's crosswalk |
| English alignment anchor | CrossWire KJV with Strong's | Word-level English anchor |
| Translation text | ebible.org YLT USFM | YLT verse text and token stream |
| Alignment builder | `build_ylt_align.py` | KJV/YLT token alignment and Hebrew association |
| Grammar repair | R2, R1g and R1s rules documented in the project ledger | Adds morphology-informed YLT associations |
| Lexicon aggregation | `build_lexicon.py` and normalized-v2 builders | Aggregates word renderings and contexts by root/form/vowel |

Important semantic constraint: YLT source text is verse-level. A computed per-word association is an alignment hypothesis, not a publisher-supplied YLT word-by-word gloss. Preserve that distinction in labels and documentation.

### Greek New Testament

| Layer | Source/artifact | Role |
|---|---|---|
| Primary TR text | byztxt `greektext-textus-receptus`, Robinson parsed TR | Greek surface, beta-code, Strong's and Robinson morphology |
| KJV alignment source | CrossWire SWORD KJV 3.1 | English tokens and source-encoded Greek positional references |
| Translation text | ebible.org `engylt` USFM | YLT verse text |
| Builder | `build_nt.py` | Loads NT books, verses, KJV, YLT and TR |
| Alignment builder | `build_nt_align.py` | Transfers KJV source references to TR positions and aligns YLT |
| Alternative textual traditions | Byzantine and SBL source/build bridges | Separate Greek token streams; not interchangeable with TR |
| Derived lexical metadata | `lxx_words` | LXX-based lemma/gloss lookup; not a direct NT lexicon |

The Greek build header explicitly identifies the primary Greek text as the Textus Receptus and the stated rationale as the Greek text behind KJV and YLT. Treat TR, Byzantine and SBL as separate text witnesses.

## Consumer/integration path

1. PostgreSQL stores source word records, computed YLT mappings and lexicon aggregates.
2. Flask application `/opt/bible/website/app_v2.py` serves verse and Strong's-word API responses.
3. PWA `/var/www/html/byot/index.html` renders the YLT text and computed word associations.
4. The current separate Node API in `kitcosby/BibleApp` is not the serving source for these legacy lexicon routes.

The API exposes the Greek lexical provenance field in its underlying response, but the PWA word-page adapter currently drops that field. The Byzantine mapping tables exist in PostgreSQL but were not found in the current Flask API's Greek-variant serving path. SBL's lemma/gloss join currently fails because the LXX lemma and MorphGNT lemma representations use different scripts/transliteration conventions.

## Known data limitations

- Hebrew YLT alignment is computed and best-effort; it is not an authoritative interlinear.
- Greek YLT alignment inherits a KJV-to-Greek positional bridge.
- LXX-derived NT glosses are a convenience lookup, not a direct NT lexicon or contextual translation.
- Some Greek Strong's identifiers have no corresponding LXX gloss; absence of a gloss is not proof of a bad Strong's assignment.
- The older SQLite database and older README counts must not be used as the current production baseline.

## Backup and recovery status

**A logical backup exists and has been restored locally; off-host replication and full permission recovery remain open.**

The current backup report and manifest are recorded in BACKUP_REPORT.md. The files were independently located on Lampy and their metadata checked:

- Full local archive: /var/backups/bible-postgres-20261106T171837Z/bible.dump, 195,708,631 bytes.
- Separate globals export: /var/backups/bible-postgres-20261106T171837Z/globals.sql, 1,088 bytes.
- Archive catalogue: archive-list.txt, 22,018 bytes; PostgreSQL archive header reports 324 TOC entries.
- Portable OneDrive-path copy: C:\Users\kitco\OneDrive\BibleBackups\bible-20261106.dump, 195,708,448 bytes.
- The backup manifest records SHA-256 values; this phase verified file existence, sizes and archive-list readability, but did not independently recompute the manifest hashes.
- The OneDrive process was running, but cloud upload completion was not independently confirmed. This is not yet a verified off-host copy.
- The portable archive restored into isolated database bible_restore_verify_20261106 with pg_restore --exit-on-error completing successfully. Independent counts matched production for 11 key tables. A separate restored-snapshot validator run unexpectedly returned zero for several populated Greek/rendering tables; that discrepancy remains unresolved.
- The portable restore used --no-owner --no-acl. The separate globals export exists, but restoration of original roles, ownership and ACLs has not been exercised.
- An earlier 91.5 MB dump was superseded at the same OneDrive path by the current 195.7 MB archive; use the current manifest and file metadata, not the earlier hash.

Do not treat the local OneDrive path as a proven cloud backup until sync is confirmed from the client or another device. Before production repair, independently recompute checksums, verify the full local archive and globals export, complete an owner/ACL restore test in isolation, and confirm an off-host copy.

## Next inventory work

- Record exact source commit hashes and source archive checksums for every loaded NT dataset.
- Record exact row counts and schema/constraint inventory for every lexicon bridge table.
- Establish an encrypted/off-host backup and perform a restore test before any data mutation.
- Capture reproducible table-level fingerprints for the relevant production tables.
