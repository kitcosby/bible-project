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
| `gnt_words` | 13 MB | Robinson TR Greek token records |
| `gnt_alignment` | 15 MB | KJV-to-TR positional bridge |
| `gnt_ylt_renderings` | 13 MB | TR-token to YLT-word renderings |
| `gntb_words` | 12 MB | Byzantine Greek token records |
| `gntb_ylt_renderings` | 9 MB | Byzantine-token to YLT-word renderings |
| `gnts_words` | 15 MB | SBL Greek token records |
| `lxx_words` | 90 MB | LXX Greek token/lemma/gloss source data |

Additional counts measured:

- `words`: 264,217 rows.
- `ylt_renderings`: 358,391 rows.
- `lexicon_ylt_rendering`: 234,091 rows.

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

**Unverified / blocking before repair.** Existing historical application-code backups were found under `/opt/bible/website`, but the read-only discovery did not establish a verified backup of the current PostgreSQL `bible` database. Do not infer that an application-code backup protects database contents. Before any production repair, take a fresh, independently verifiable PostgreSQL backup and record its path, size, checksum, timestamp, restore test and database identity. No such backup was created in this discovery phase.

## Next inventory work

- Record exact source commit hashes and source archive checksums for every loaded NT dataset.
- Record exact row counts and schema/constraint inventory for every lexicon bridge table.
- Establish an encrypted/off-host backup and perform a restore test before any data mutation.
- Capture reproducible table-level fingerprints for the relevant production tables.
