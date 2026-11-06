# YLT Lexicon Debugging Report

**Status:** Initial findings, 2026-11-06  
**Evidence class:** Live read-only observations, source-code inspection and integration inspection.  
**No repairs applied.**

## Executive summary

The Hebrew and Greek paths must be evaluated separately. Hebrew already has a manually aligned gold sample and a measured precision/recall baseline. The Greek pipeline inherits positional references from a KJV source module and contains confirmed verse-level mismatches. The SBL Greek lemma/gloss lookup has a representation mismatch. Additional items require source verification and must not yet be called defects.

## Confirmed software/integration defects

### YLT-GNT-001 — Greek positional bridge can assign source positions outside the TR verse

**Severity:** High  
**Affected components:** `build_nt_align.py`, `gnt_alignment`, `gnt_ylt_renderings`, Flask API and PWA display.

The alignment builder imports KJV source-encoded references to Greek positions and records them against the Robinson TR sequence. The source code counts in-range references but the observed logic does not reject or reconcile out-of-range references before mapping them.

Live examples identified during discovery:

- **John 9:21:** Robinson TR has 23 Greek word positions; the KJV bridge references position 24. YLT tokens `shall` and `speak` were left orphaned. The Greek token `λαλησει` was associated with `himself` rather than the YLT phrase `shall speak`.
- **Colossians 4:10:** Robinson TR has 20 Greek word positions; the KJV bridge references position 21. YLT token `him` was left orphaned. The Greek token `αυτον` was associated with `receive` rather than `him`.

These are positional/source-bridge defects, not evidence that YLT's translation choices are wrong. The exact upstream edition/versification cause remains to be isolated.

**Expected behavior:** Every source reference must resolve against the selected Greek witness and verse. Unresolved references must be reported and excluded from automatic word association, not silently attached to another token.

**Minimal correction direction:** Build a verse-local source-token reconciliation between CrossWire's encoded Greek references and the actual Robinson TR token stream. Reject unresolved references and retain an audit trail. Do not apply a blanket positional shift.

### YLT-GNT-002 — SBL lemma/gloss lookup uses incompatible lemma representations

**Severity:** High  
**Affected components:** `gnts_words`, `lxx_words`, Flask lexical lookup and PWA.

Observed representation:

- LXX lemma values are transliterated Latin forms (examples include `arkhe`, `poieo`, `theos`).
- SBL/MorphGNT lemmas are Greek-script forms (examples include `βίβλος`, `γενέσεως`, `Ἰησοῦ`).

The API attempts an exact lemma equality lookup. These different representations do not match, leaving the SBL word glosses empty. Discovery measured 137,554 SBL word occurrences without a derived gloss in the response path.

**Expected behavior:** The application must either use a Greek-script lemma source or an explicit, provenance-bearing crosswalk from the SBL lemma representation to the LXX representation. A transliteration guess or accent-stripping alone is insufficient.

**Minimal correction direction:** Identify a licensed, version-pinned Greek lemma crosswalk or use a direct Greek-script lexicon. Preserve source lemma and matched lemma separately, and expose lookup provenance and ambiguity.

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

### YLT-API-001 — Byzantine and SBL serving coverage

Byzantine YLT mapping rows exist in PostgreSQL but were not found in the Flask API's Greek variant response path. The SBL bridge is not synchronized into the equivalent YLT mapping table. Treat as integration coverage gaps; verify desired product behavior before implementing.

## Not a defect by itself

- YLT word choices that differ from KJV or other modern translations.
- Multiple English words aligned to one Greek/Hebrew token.
- A Greek Strong's value without an LXX gloss.
- Unaligned particles or function words where no defensible one-to-one English equivalent exists.
- A morphology pattern whose source grammar is genuinely ambiguous.

## Evidence and limitations

The initial discovery queried live PostgreSQL using a READ ONLY transaction, inspected current source files in `master`, and inspected the serving Flask/PWA implementation. The full raw query transcripts and exact source commit hashes still need to be attached to the issue evidence. No repair or recomputation has occurred.
