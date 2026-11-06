# YLT Lexicon Debugging Report

**Status:** Initial findings, 2026-11-06  
**Evidence class:** Live read-only observations, source-code inspection and integration inspection.  
**No repairs applied.**

## Executive summary

The Hebrew and Greek paths must be evaluated separately. Hebrew already has a manually aligned gold sample and a measured precision/recall baseline. The Greek positional defects are traced to pipe-delimited variant records skipped by the Robinson TR parser before the KJV bridge is applied. The SBL Greek lemma/gloss lookup has a representation mismatch. Additional items require source verification and must not yet be called defects.

## Confirmed software/integration defects

### YLT-GNT-001 — TR parser drops pipe-delimited variant tokens before Greek alignment

**Severity:** High  
**Affected components:** `build_nt_align.py`, `gnt_alignment`, `gnt_ylt_renderings`, Flask API and PWA display.

The primary cause is upstream in build_nt.py parse_tr(): its token regex expects a Strong's number to be followed immediately by a morphology brace and does not implement the Robinson pipe-delimited first/second-variant syntax. It skips some selected variant readings and can mishandle other variant groups. build_nt_align.py then transfers CrossWire KJV src positions onto a parsed TR sequence with different token positions. The alignment builder counts in-range references but does not stop or reconcile the resulting out-of-range positions.

Live examples identified during discovery:

- **John 9:21:** Robinson TR has 23 Greek word positions; the KJV bridge references position 24. YLT tokens `shall` and `speak` were left orphaned. The Greek token `λαλησει` was associated with `himself` rather than the YLT phrase `shall speak`.
- **Colossians 4:10:** Robinson TR has 20 Greek word positions; the KJV bridge references position 21. YLT token `him` was left orphaned. The Greek token `αυτον` was associated with `receive` rather than `him`.

A new read-only validator run against the live PostgreSQL database confirmed **3 out-of-range bridge rows and 3 orphaned YLT rendering rows**: two out-of-range source references at John 9:21 (both target TR position 24, beyond the 23-word verse) and one at Colossians 4:10 (target position 21, beyond the 20-word verse). The orphan renderings are John 9:21 `shall` and `speak`, plus Colossians 4:10 `him`. The current stored mapping associates John 9:21 TR token `λαλησει` with `himself`; Colossians 4:10 token `αυτον` receives `receive`. Source-level evidence from the pinned Robinson TR repository confirms the parser mismatch:

- `parsed/COL.UTR`, Colossians 4:10 contains `barnaba 921 | {N-GSM} | {N-DSM} | peri ...`. The current parser regex skips `barnaba` because a pipe intervenes between Strong's and morphology. Source sequence: 21 tokens; stored sequence: 20.
- `parsed/JOH.UTR`, John 9:21 contains `... peri 4012 {PREP} | autou 848 | autou 846 | {P-GSM} lalhsei ...`. The current parser skips the `autou` token and its alternate analyses. Source sequence: 24 tokens; stored sequence: 23.

CrossWire KJV module markup carries the omitted forms in `lemma.TR` and references John 9:21 positions 23–24 and Colossians 4:10 positions 11–21. Thus the evidence supports a parser omission, not merely an unexplained edition mismatch. The parser must preserve a single token occurrence while retaining alternative Strong's/morphology analyses separately. These are not evidence that YLT's translation choices are wrong.

**Expected behavior:** Every source reference must resolve against the selected Greek witness and verse. Unresolved references must be reported and excluded from automatic word association, not silently attached to another token.

**Minimal correction direction:** Port or reproduce the relevant MIT-licensed librobinson normalization and first/second-variant selection rules in Python 3. Select the primary reading only after checking full-corpus CrossWire lemma.TR compatibility; preserve unselected readings separately if required. Rebuild and validate the TR token stream in a disposable database before regenerating any downstream bridge. Do not apply a blanket positional shift.

### YLT-GNT-002 — SBL normalized word forms are incorrectly treated as LXX lexical lemmas

**Severity:** High  
**Affected components:** `gnts_words`, `lxx_words`, Flask lexical lookup and PWA.

Observed representation:

- LXX lemma values are transliterated Latin forms (examples include `arkhe`, `poieo`, `theos`).
- SBL/MorphGNT lemmas are Greek-script forms (examples include `βίβλος`, `γενέσεως`, `Ἰησοῦ`).

The API attempts an exact lemma equality lookup. These different representations do not match, leaving the SBL word glosses empty. Discovery measured 137,554 SBL word occurrences without a derived gloss in the response path.

**Expected behavior:** The application must either use a Greek-script lemma source or an explicit, provenance-bearing crosswalk from the SBL lemma representation to the LXX representation. A transliteration guess or accent-stripping alone is insufficient.

**Minimal correction direction:** Confirm the MorphGNT source schema, retain normalized form and morphology as such, and obtain a genuine lexical lemma from a version-pinned Greek lexicon/crosswalk. Preserve original form, canonical lemma, matching method and source provenance separately.

### YLT-GNT-003 — Greek lexical provenance is discarded by the PWA adapter

**Severity:** Medium  
**Affected components:** `app_v2.py` response and `/var/www/html/byot/index.html` word detail adapter.

The API provides a `greek_lexicon` provenance note explaining that the displayed Greek lemma/gloss is LXX-derived. The PWA adapter discards this field. Readers therefore see a gloss without the qualification that it is derived from LXX data and may not be a direct NT lexical definition.

**Expected behavior:** Display the provenance and the distinction between Strong's-based/LXX-derived lookup and contextual meaning.

**Minimal correction direction:** Preserve and render the existing provenance field. Do not change lexical values.

## Suspected / requires source verification

### YLT-GNT-004 — `G0` Strong's values

Five TR occurrences were observed with `G0`. The parser constructs Strong's identifiers by prefixing source numbers with `G`. Before changing them, inspect the original TR source records and its documented convention. These may represent untagged tokens, placeholders or a legitimate source-specific sentinel.

**Status:** Candidate anomaly; not yet a confirmed assignment defect.

### YLT-MORPH-001 — Unparsed morphology pattern

The `morph_patterns` table contains one pattern with `parse_status='unparsed'`. The ledger identifies an Aramaic pattern containing `AT`, where the bare `T` lacks a documented type. Do not invent a parse. Preserve the raw morphology and document the unresolved segment until a source grammar supports an interpretation.

**Status:** Confirmed unresolved metadata; not necessarily a software defect.

## Structural risks / integration gaps

### YLT-DB-001 — Byzantine bridge integrity constraints

The live `gntb_alignment` and `gntb_ylt_renderings` tables were found without primary-key constraints or indexes. Initial checks did not find duplicate mappings or orphaned references. This is a structural integrity risk, not proof of corrupt rows.

### YLT-API-001 — Greek variant API serving and SBL bridge coverage

Byzantine mapping tables exist in PostgreSQL but were not found in the Flask API's Greek variant response path. SBL tables (including gnts_alignment and gnts_ylt_renderings) also exist in the current database archive/catalogue; their row counts and actual mapping coverage have not yet been measured. The earlier statement that the SBL bridge was not synchronized is therefore unverified and is withdrawn. Inspect table contents and API usage before classifying this as a missing-data defect. Treat the API-serving gap as an integration question until the expected witness behavior is specified.

## Not a defect by itself

- YLT word choices that differ from KJV or other modern translations.
- Multiple English words aligned to one Greek/Hebrew token.
- A Greek Strong's value without an LXX gloss.
- Unaligned particles or function words where no defensible one-to-one English equivalent exists.
- A morphology pattern whose source grammar is genuinely ambiguous.

## Backup/restore evidence

A full custom-format backup and separate globals export are recorded in BACKUP_REPORT.md. File existence and sizes were checked; the archive catalogue was readable; the OneDrive-path copy restored into bible_restore_verify_20261106; and independent counts matched production for eleven key tables. The manifest SHA-256 values were not independently recomputed in this phase, OneDrive cloud sync remains unconfirmed, and ownership/ACL restore has not been tested. A restored-snapshot validator run returned zero counts for some tables that independent count checks showed as populated; this inconsistency remains open.

## Corpus-wide variant survey

A source survey of all 27 pinned Robinson UTR book files found 431 physical lines containing pipe markers. Applying the three shorthand-normalization regexes documented by librobinson to those files found 41 matches: 39 surface-alternative patterns, one alternative-morphology pattern, and one alternative-Strong's pattern. These are pattern matches, not a count of all variant groups; the remaining pipe markers are handled by librobinson's general first/second-variant selection logic. No M5:, M6:, VAR: or :END control markers were found in these 27 UTR files. The current build_nt.py parser does not implement the general variant selection stage.

## Upstream parser reference

The MIT-licensed byztxt/librobinson project explicitly supports Robinson's file format and variant handling. Its book.py normalizes three pipe-delimited variant patterns and chooses first or second readings; verse.py assigns one word position per selected reading; word.py preserves alternate Strong's and morphology fields. This is a better reference for the parser repair than inventing a new interpretation of pipe groups. The library is legacy Python 2 code, so direct import into the current Python 3 builder is not assumed; port the relevant behavior with tests.

## Evidence and limitations

The discovery queried live PostgreSQL using READ ONLY transactions, inspected source code and pinned Robinson/CrossWire source artifacts, and inspected the serving Flask/PWA implementation. The Robinson source repository commit and the JOH/COL source blob IDs are recorded in issue #1. No production repair or recomputation has occurred.
