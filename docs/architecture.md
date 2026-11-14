Living document — update these diagrams when adding features.

# bible-project — Architecture

**Relationship to Bible:** this repo is the current, live Bible Project. `kitcosby/Bible` is an earlier partial copy of the same project — its own repo description says so ("Earlier partial Bible-database copy; current work continues in the bible-project repository"). Do not treat them as two independent systems: bible-project is the continuation with the U-8 maqqef-component repair, the U-9 verse-remap repair, YLT word alignment, the Flask translation website, and the v2 normalization, none of which exist in the older Bible repo.

**v2 status (2026-09-28):** the corpus has been normalized to the v2 schema (`schema_v2.sql`, design rationale in `schema_v2.md`). `bible_v2.db` is built and verified, and the live website now serves it via `app_v2.py` — **live cutover DONE 2026-09-28 ~17:15 PDT** on Kit's authorization ("go live with it both on github and on the laptop"; schema approved by Kit: "the schema looks great"). The diagrams below describe v2, which is now the production schema.

**2026-11-07 changes (this revision):** the corpus became a 66-book, two-testament corpus with a Greek track. (1) **NT extension** (`build_nt.py`, 2026-11-04): Textus Receptus Greek (141,009 words, Robinson parsed, public domain), KJV NT (180,568 words), and YLT NT (7,957 verses) loaded on the same verse grid as the OT — books now 66. (2) **LXX witness layer** (`build_lxx.py`): the Septuagint loaded as a witness (57 books, 30,371 verses, 623,693 words) with a numbering-v1 crosswalk (`lxx_crosswalk`) from MT verses; Kit's rulings: full Greek canon, Theodotion Daniel primary, Old Greek as alternate. (3) **GNT variant traditions**: Byzantine (Robinson-Pierpont, 7,953 verses) and SBLGNT/MorphGNT (7,927 verses) loaded as witnesses (`build_gnt_variants.py`, summary table `gnt_variants` vs TR with method stamps). (4) **Three Greek alignment bridges**: the TR bridge (`build_nt_align.py` — CrossWire KJV→Greek alignment plus computed Young's renderings, PG-synced), the Byzantine bridge (`build_gntb_bridge.py` — built, gated at 100% same-verse consistency and 98.49% silver agreement, PG-synced), and the SBLGNT bridge (`build_gnts_bridge.py` — built and gated in SQLite, then **loaded into PostgreSQL 2026-11-06 on Kit's authorization**, counts verified PG == SQLite). Since 2026-11-07 the API serves each tradition's own bridge phrases per word (`greek_words_variants` byz/sbl arrays in the verse payload; TR payloads byte-identical). (5) **Phase 3 JSON API completed** on `app_v2.py`: `/api/verse`, `/api/chapter`, `/api/word/<strongs>`, and `/api/search` joined the earlier list endpoints; all API responses go through `_api_json` (CORS `Access-Control-Allow-Origin: *`), and 404 bodies are `{"error": "not found", "detail": ...}`, matching the BibleApp-pwa client's not-found check exactly. `/api/search` is semantic: the query is embedded by the local Ollama service (`nomic-embed-text`) and matched against the pgvector store `ylt_verses_embedding_store` (31,102 verse rows after the NT rows were auto-processed, 2026-11-04). (6) **Computed-Young's grammar repair applied corpus-wide** (`apply_ylt_grammar_repair.py`, Kit's ruling): `ylt_renderings` 339,153 → 358,391 rows, `lexicon_ylt_rendering` rebuilt; plus a number-aware API gloss (plural nouns inflect the lemma gloss; Eccl 1:2 "vanities"). The primary new client of the API is **BibleApp-pwa** (see its own `docs/architecture.md`); the website's own pages are unchanged in structure.

**2026-11-14 changes (this revision, diagram maintenance):** three subsystems landed 2026-11-08…12 that the diagrams below now model. (1) **MCP gateway** (`mcp-gateway/`, new top-level subsystem): a FastMCP server (`gateway.py`, Streamable HTTP on 127.0.0.1:8765, public only via Tailscale Funnel on the Lampy node) with a built-in OAuth 2.1 authorization server (`oauth_as.py` — dynamic client registration, authorization-code flow with mandatory PKCE S256, rotating refresh tokens, owner approval out of band via `gw_admin.py`). It gives an external MCP client (ChatGPT, via a plugin) tool access to the Lampy estate: 11 read-only tools at Phase 4 (`fs_list`/`fs_read`/`fs_search` over fixed roots, `git_status`/`git_log`/`git_branches`/`git_diff` over gateway-owned clones, `pg_databases`/`pg_schema`/`pg_query` as the SELECT-only `mcp_ro` PostgreSQL role, `svc_probe` fixed health probes), extended in Phase 5 (2026-11-12) by the write/execution tools `fs_write`, `fs_edit`, `exec_run` with a write scope and a setuid root helper (`root_helper.py`) — 14 tools total. Runtime state (hashed access tokens, OAuth client/code/refresh stores, the `mcp_ro` credential) lives only in the deployment's `/home/mcpgw/secrets/` (mode 0600), never in this repo. Phase 4 completed 2026-11-12 (ChatGPT client registration); PR #33 merged the Phase 5 source the same day. (2) **Flask identity services for the PWA/Express authoring flow** (`website/app_v2.py`, 2026-11-09): JSON auth endpoints for PWA sessions (`/api/auth/bootstrap`, login/signup/logout as JSON POSTs with session cookie, exact-Origin check and CSRF token), a Flask API identity-token issuer (short-lived HS256 bearer tokens, five-minute expiry, issued atop the existing `user_accounts` login) that the BibleApp Express API verifies, and translation-ownership enforcement in the Flask routes (owner-scoped translation visibility and writes). (3) **Word-ID phrase-options endpoint** (2026-11-09): `GET /api/word-options` returns the exact dropdown phrase groups by Hebrew word ID, marked `Cache-Control: no-store` (the stored choice byte is an index into this ordering, so it must never be served stale). The Hebrew spelling-variant search described in the dated sections at the end of this document was promoted to production 2026-11-12 (separate PostgreSQL database `bible_search_prod_20261111`, read-only role `bible_search_prod_ro`); a fifth estate for that search database is noted in the ERD notes.

**2026-11-11 changes (previous revision):** the DB QA applications (issues #20/#21/#23, Kit-approved) repaired the corpus in place and added one schema element. (1) **Verse-grid repair**: 92 words misfiled under wrong verses were refiled to their true verses (Esth 4:4, Ps 17:1, Isa 27:1, Jer 28:1, Lam 2:1 filled), with `word_alignment` and `lexicon_found_verse` repointed surgically (`build_alignment.py` output no longer matches the shipped table — never rebuild it wholesale). (2) **Hidden verse shells**: the 7 rows emptied by the repair are kept in the grid (each retains its Peshitta `no_counterpart` verse note) and flagged with the new `verses.hidden` column (`schema_v2.sql`; 1 = hidden), set on Ps 17:17, Isa 27:22, Jer 28:23, Lam 2:23, Josh 4:32, 2 Chr 36:32, and Ruth 8:18. `app_v2.py` honors the flag in the shared `_WORDS_EXIST` fragment, the HTML book/chapter listings, and the read-view navigation helpers (`_chapter_bounds`, `_last_chapter`): hidden verses return the standard 404 and never appear in chapter lists or navigation (verified live: Ruth offers chapters 1–4 only). (3) **Composite Strong's**: `split_multi_strongs` resolved as composite values in `words.strongs` (comma-joined in maqqef-chain order; components in `strongs_components`; source `oshb-split`; 135 words, 65 new `strongs` entities) — `/api/word/<strongs>` resolves them by exact match as single lemmas. (4) **PARALLEL-CONFLATE distribution** on `ylt_renderings` (358,391 → 357,574 rows; shared YLT positions 11,448 → 10,642; `lexicon_ylt_rendering` rebuilt at 234,131) and 1,534 U-10 Strong's fills plus 18 post-repair exact fills synced (blank Strong's 4,321). Local SQLite corpus and production PostgreSQL verified in full content-hash parity (words text + locations, YLT renderings, `word_alignment`, `lexicon_ylt_rendering`). No routes, processes, or data flows changed — the DFD and context diagram are unaffected; the ERD gains `VERSES.hidden` only.

**2026-10-24 changes (previous revision):** the website migrated from SQLite to PostgreSQL (Kit 2026-10-09) — corpus reads come from the PostgreSQL `bible` database and application data lives in the PostgreSQL `bible_app` database (`website/app_v2.py`, psycopg2), so both can be administered via the Lampy admin tool; per-word choices were normalized into the `word_choice` table (2026-10-09), replacing the `translation_<id>.choices` byte files; a `reading_position` table and the two-doors redesign added `/read` daily reading, `/books`, `/api/books|chapters|verses`, and `/interlinear` routes; the variants campaign (Oct 14–17) added Kethiv/Qere (`build_variants_kq.py`, witness `MT`), Samaritan Pentateuch (`build_variants_sp.py`, witness `SP`), and Dead Sea Scrolls (`build_variants_dss.py`, per-scroll sigla, fully attested verses only) rows to `word_variants`, plus the new verse-scale tables `witness_verses` and `verse_notes` from the Syriac (Peshitta) leg (`build_notes_syr.py`); `export_sync.py` syncs the textual `word_variants` rows and both verse-scale tables from the SQLite build file `bible_v2.db` to the website's PostgreSQL `bible` database; final-form-only readings are marked `orthographic` (Kit 2026-10-17); and the YLT bridge was re-run on v2 and accepted at the 0.7923 precision baseline (Kit 2026-10-17). This revision also restores the website-login content (`user_accounts`, `lemma_default`, `translation.owner_id`) whose 2026-10-10 docs commit (79f68214) was lost when the 2026-10-18 merge (18ef982a) took the local master lineage as precedence — the code for it is present in `app_v2.py` at HEAD.

**2026-09-30 changes:** `word_variants` merged into one table tagged by `variant_kind` (`'spelling'` | `'textual'`, CHECK-enforced — Kit's decision); new `word_notes` table (one-to-many word notes, Kit 2026-09-29); `/variants` explorer route added to `app_v2.py`; `database/` now carries a 4-part pg_dump of the live `bible_v2.db`; the 129 OSHB anomaly resolutions applied to `bible_v2`. The level-1 DFD below was also corrected: the previous revision still showed the website reading the v1 `bible.db` live, which the 9/28 cutover superseded — the live site reads `bible_v2.db` via `app_v2.py`.

## 1. Context diagram (level 0)

```mermaid
flowchart LR
    E1["Kit developer"]
    E2["Kit reader"]
    E3["Spreadsheet files"]
    E4["OSHB Hebrew text"]
    E5["KJV word data"]
    E6["YLT verse data"]
    E7["Lexicon sources"]
    E8["Text-Fabric variant sources"]
    E9["Lampy admin console"]
    E10["Greek NT sources (TR, KJV NT, YLT NT)"]
    E11["LXX source (CenterBLC/LXX)"]
    E12["GNT variant sources (Byzantine RP, SBLGNT/MorphGNT)"]
    E13["Ollama embedding service"]
    E14["BibleApp-pwa client"]
    E15["ChatGPT plugin client (MCP)"]
    E16["BibleApp Express API"]
    P0("Bible Project system")
    E1 -->|"runs build and migration scripts"| P0
    E2 -->|"browses verses, picks translations"| P0
    E3 -->|"Hebrew word lists"| P0
    E4 -->|"Hebrew text with Strongs and morphology"| P0
    E5 -->|"KJV words with Strongs tags (OT and NT)"| P0
    E6 -->|"verse-level translation (USFM, OT and NT)"| P0
    E7 -->|"dictionary glosses (BDB, Strongs Hebrew)"| P0
    E8 -->|"Samaritan, Dead Sea Scrolls, and Peshitta texts"| P0
    E10 -->|"TR Greek text, KJV NT words, YLT NT verses"| P0
    E11 -->|"LXX Greek books, verses, and words"| P0
    E12 -->|"Byzantine and SBLGNT Greek texts"| P0
    P0 -->|"database administration queries"| E9
    E9 -->|"database rows and administration results"| P0
    P0 -->|"search query text"| E13
    E13 -->|"query embedding vector (nomic-embed-text)"| P0
    E14 -->|"read-only JSON API requests (GET /api/...)"| P0
    P0 -->|"JSON verse, chapter, word, and search payloads"| E14
    E14 -->|"JSON auth requests (bootstrap, login, signup, logout)"| P0
    P0 -->|"session cookie and short-lived identity token"| E14
    P0 -->|"issued identity tokens for verification"| E16
    E15 -->|"MCP tool calls with OAuth bearer token (via Tailscale Funnel)"| P0
    P0 -->|"MCP tool results (corpus rows, project files, git data, service probes)"| E15
    E1 -->|"OAuth authorization approvals (gw_admin, out of band)"| P0
    P0 -->|"built corpora, DB dump parts (database/), and verification reports"| E1
    P0 -->|"verse reader with word dropdowns, /variants explorer, /read daily reading, and interlinear pages"| E2
```

## 2. Level-1 data flow diagram

```mermaid
flowchart LR
    E1["Kit developer"]
    E2["Kit reader"]
    E3["Source text providers"]
    E8["Text-Fabric variant sources"]
    E10["Greek NT sources (TR, KJV NT, YLT NT)"]
    E11["LXX source (CenterBLC/LXX)"]
    E12["GNT variant sources (Byzantine RP, SBLGNT/MorphGNT)"]
    E13["Ollama embedding service"]
    E14["BibleApp-pwa client"]
    E15["ChatGPT plugin client (MCP)"]
    E16["BibleApp Express API"]
    P1("1.0 Ingest canonical word list")
    P2("2.0 Crosswalk words to OSHB")
    P3("3.0 Load renderings and glosses")
    P4("4.0 Build root tiers and lexicon")
    P5("5.0 Align YLT words and run repairs")
    P6("6.0 Assemble v1 SQLite corpus")
    P7("7.0 Normalize to v2 schema")
    P8("8.0 Serve translation website and JSON API")
    P9("9.0 Load variant traditions")
    P10("10.0 Sync variants to website database")
    P11("11.0 Load Greek NT corpus")
    P12("12.0 Load LXX witness layer")
    P13("13.0 Load GNT variant traditions")
    P14("14.0 Build Greek alignment bridges")
    P15("15.0 Sync Greek corpus to website database")
    P16("16.0 Embed verses for semantic search")
    P17("17.0 Issue identity tokens and enforce translation ownership")
    P18("18.0 Serve MCP gateway tools and OAuth authorization")
    D1[("D1 staged input files")]
    D2[("D2 bible.db - v1 corpus")]
    D3[("D3 bible_v2.db - normalized build corpus")]
    D4[("D4 bible_app - PostgreSQL website data")]
    D6[("D6 database/ DB dump parts")]
    D7[("D7 bible - PostgreSQL corpus")]
    D8[("D8 Greek NT and variant tables (gnt_, gntb_, gnts_ sets, gnt_variants)")]
    D9[("D9 LXX witness tables (lxx_books, lxx_verses, lxx_words, lxx_crosswalk)")]
    D10[("D10 ylt_verses_embedding_store - pgvector verse embeddings")]
    D11[("D11 MCP gateway runtime stores - hashed tokens, OAuth clients, codes, refresh tokens (deployment secrets directory)")]
    D12[("D12 bible_search_prod_20261111 - PostgreSQL spelling-variant search database")]
    E1 -->|"runs scripts"| P1
    E3 -->|"spreadsheets, OSHB, KJV, YLT, lexicons"| P1
    P1 -->|"canonical words"| D1
    D1 -->|"canonical words"| P2
    D1 -->|"parsed source data"| P3
    P2 -->|"aligned words"| P6
    P3 -->|"renderings, glosses, verses"| P6
    D1 -->|"base words"| P4
    P4 -->|"root tiers, lexicon rows"| P6
    D1 -->|"KJV and YLT tokens"| P5
    P5 -->|"word alignments, repair fixes"| P6
    P6 -->|"v1 corpus"| D2
    P6 -->|"assembly reports"| E1
    D2 -->|"v1 tables"| P7
    P7 -->|"normalized corpus"| D3
    P7 -->|"migration verification report"| E1
    D3 -->|"derived tables (alignment, variants)"| P7
    D3 -->|"pg_dump snapshot published in repo (4 parts)"| D6
    D6 -->|"distributable corpus snapshot"| E1
    E8 -->|"Samaritan, DSS, and Peshitta extraction files"| P9
    D3 -->|"MT corpus words and verses"| P9
    P9 -->|"textual word_variants rows"| D3
    P9 -->|"witness_verses and verse_notes rows"| D3
    D3 -->|"textual variants and verse-scale rows as CSV"| P10
    P10 -->|"synced variant and witness rows"| D7
    E10 -->|"TR Greek, KJV NT, and YLT NT files"| P11
    D7 -->|"corpus verse grid (books, verses, kjv_words, ylt_verses)"| P11
    P11 -->|"gnt_verses and gnt_words rows"| D8
    E11 -->|"LXX books, verses, and words"| P12
    P12 -->|"lxx_books, lxx_verses, and lxx_words rows"| D9
    P12 -->|"numbering crosswalk rows (MT verse to LXX verse)"| D9
    E12 -->|"Byzantine and SBLGNT Greek texts"| P13
    D8 -->|"TR verses and words (comparison base)"| P13
    P13 -->|"gntb_ and gnts_ verse and word rows"| D8
    P13 -->|"gnt_variants summary rows (tradition, status, detail)"| D8
    D8 -->|"Greek words and KJV words"| P14
    P14 -->|"TR alignment and computed-YLT rendering rows (gnt_alignment, gnt_ylt_renderings)"| D8
    P14 -->|"Byzantine bridge rows (gntb_alignment, gntb_ylt_renderings)"| D8
    P14 -->|"SBLGNT bridge rows (gnts_alignment, gnts_ylt_renderings)"| D8
    P14 -->|"bridge gate reports (consistency and coverage)"| E1
    D8 -->|"Greek corpus and bridge rows"| P15
    D9 -->|"LXX witness and crosswalk rows"| P15
    P15 -->|"synced Greek and LXX rows"| D7
    D7 -->|"verse texts (YLT computed corpus)"| P16
    P16 -->|"verse embedding vectors and chunks"| D10
    E2 -->|"HTTP requests"| P8
    E14 -->|"JSON API requests (GET only)"| P8
    P8 -->|"reads corpus, variants, Greek, and LXX data"| D7
    P8 -->|"reads Greek tables for NT payloads"| D8
    P8 -->|"reads LXX witness via crosswalk"| D9
    P8 -->|"reads and writes user, translation, choice, and reading-position data"| D4
    P8 -->|"search query text"| E13
    E13 -->|"query embedding vector"| P8
    P8 -->|"nearest-neighbour verse lookup"| D10
    P8 -->|"reader pages, /variants explorer, /read pages, and interlinear pages"| E2
    P8 -->|"JSON payloads (books, chapters, verses, verse, chapter, word, search)"| E14
    E14 -->|"JSON auth requests with session cookie and CSRF token"| P17
    P17 -->|"reads and writes account and translation ownership data"| D4
    P17 -->|"five-minute HS256 identity token"| E14
    P17 -->|"identity token verification contract"| E16
    P8 -->|"word-ID phrase-option groups (no-store)"| E14
    P8 -->|"spelling-variant search reads"| D12
    E15 -->|"MCP tool calls with OAuth bearer token"| P18
    E1 -->|"OAuth approvals and token administration (gw_admin)"| P18
    P18 -->|"reads and writes OAuth and token stores"| D11
    P18 -->|"SELECT-only corpus queries as mcp_ro role"| D7
    P18 -->|"tool results (files, git data, query rows, probe status)"| E15
```

Process grounding: 1.0 `ingest_canonical.py`; 4.0 `build_roots*.py` + `build_lexicon.py`; 5.0 `build_ylt_align.py`, `repair_u8_maqqef_kjv.py`, `repair_u8_lexicon.py`, `repair_u9_verse_remap_kjv.py`, `repair_u9_lexicon.py`, and (2026-11-03) `apply_ylt_grammar_repair.py`; 6.0 `assemble_bible.py`; 7.0 `migrate_v2.py`, then the derived-data stage `build_alignment.py`, `build_variants.py`, `apply_morph_corrections.py`, the post-normalization fixes `apply_anomaly_resolutions.py` (129 OSHB-verified fixes, 2026-09-29) and `migrate_variants_merge.py` (word_variants variant_kind merge, 2026-09-30); 8.0 `website/app_v2.py` — the LIVE server since the 2026-09-28 ~17:15 PDT cutover, and since 2026-10-09 a PostgreSQL server: corpus reads from PostgreSQL database `bible` (default `BIBLE_DB=bible`), application data in PostgreSQL database `bible_app` (default `APP_DB=bible_app`), both via psycopg2 (`PG_HOST` default `/tmp`, `PG_USER` default `postgres`); supervisord `bible`, port 5057, Apache `/bible`→5057. 9.0 `build_variants_kq.py` (Kethiv/Qere, OSHB morphhb WLC), `extract_sp.py` + `build_variants_sp.py` (Samaritan, DT-UCPH/sp Text-Fabric), `extract_dss.py` + `build_variants_dss.py` (Dead Sea Scrolls, ETCBC/dss Text-Fabric, fully attested verses only), `extract_syr.py` + `build_notes_syr.py` (Syriac Peshitta, ETCBC/peshitta Text-Fabric, verse scale only) — all builders write the SQLite build file `bible_v2.db`. 10.0 `export_sync.py` (CSV in PG COPY format from `bible_v2.db` to the PostgreSQL `bible` database). 11.0 `build_nt.py` (TR Greek + KJV NT + YLT NT on the corpus verse grid). 12.0 `build_lxx.py` (LXX books/verses/words + `lxx_crosswalk`; source audit in `LXX_AUDIT_2026-11-03.md`). 13.0 `build_gnt_variants.py` (Byzantine RP and SBLGNT/MorphGNT verse/word sets + `gnt_variants` summary vs TR). 14.0 `build_nt_align.py` (TR bridge: CrossWire KJV→Greek alignment + computed Young's), `build_gntb_bridge.py` (Byzantine bridge), `build_gnts_bridge.py` (SBLGNT bridge); plan and gates in `VARIANT_BRIDGES_PLAN_2026-11-03.md`. 15.0 `export_sync_gnt.py` (Greek/LXX sync to PostgreSQL; the SBLGNT bridge's PG load was Kit-authorized and verified 2026-11-06). 16.0 the embedding vectorizer (auto-processes new verse rows; the store is read by `api_search` in `app_v2.py`). `website/app.py` (the v1 server) is retained in the repo but superseded; the pre-cutover `/bible-v2` staging copy on port 5058 was observed 2026-09-28 — its post-cutover role was not re-verified. Processes 17.0/18.0 (2026-11-09/12): 17.0 is in `website/app_v2.py` — JSON auth endpoints (`/api/auth/bootstrap`, JSON login/signup/logout with CSRF + exact-Origin checks; commits fcc016d5, 42a7396f), the HS256 identity-token issuer (1399e583, 46b5a35b) and Flask translation-ownership enforcement (d8d120df and follow-ons); the word-ID phrase-options endpoint `GET /api/word-options` (1ea4b2ef, `no-store` per 18cd612a) is served by 8.0. 18.0 is `mcp-gateway/` — `gateway.py` (FastMCP, 127.0.0.1:8765), `oauth_as.py` (OAuth 2.1 AS), `gw_admin.py` (owner admin CLI), `setup_mcp_ro.py` (SELECT-only `mcp_ro` role), `root_helper.py` (Phase 5 setuid helper); Phase 4 completion and Phase 5 write/exec tools landed 2026-11-12 (0140647d, a4485753; merged in PR #33, 9cb32306). Routes: `/signup`, `/login`, `/logout`, `/api/auth/bootstrap` and the JSON `/api/auth/*` session endpoints, `/` (two-doors Study/Read landing), `/books`, `/book`, `/chapter`, `/verse`, `/word`, `/choice`, `/translations`, `/reading`, `/read` (daily reading with per-user position), `/export`, `/variants`, `/interlinear`, `/api/books`, `/api/chapters`, `/api/verses`, `/api/verse`, `/api/chapter`, `/api/word/<strongs>`, `/api/search`, `/api/search/variants`, `/api/word-options`, `/papyrus-tile.png`.

## 3. Entity–relationship diagram (v2 schema + Greek/LXX extension)

```mermaid
erDiagram
    BOOKS {
        int book_id PK
        string name_en
        string name_he
    }
    VERSES {
        int verse_id PK
        int book_id FK
        int chapter
        int verse
        int hidden
    }
    WORDS {
        int word_id PK
        string orig_word_id
        int verse_id FK
        int word_pos
        string pointed
        string unpointed
        string letters
        string strongs FK
        int strongs_source_id FK
        int morph_pattern_id FK
        int is_aramaic
        int root_id FK
        int root_form_seq FK
        int root_vowel_seq FK
    }
    STRONGS {
        string strongs PK
        string language
    }
    STRONGS_COMPONENTS {
        string strongs FK
        int seq
        string component
    }
    STRONGS_SOURCES {
        int source_id PK
        string source
    }
    MORPH_PATTERNS {
        int pattern_id PK
        string pattern
        string language
        string parse_status
        string parse_notes
    }
    MORPH_SEGMENTS {
        int segment_id PK
        int pattern_id FK
        int seq
        string code
        string pos
        string stem
        string person
        string gender
        string number
        string state
    }
    ROOT_ENTRY {
        int root_id PK
        string root
        int word_count
    }
    ROOT_FORM {
        int root_id FK
        int form_seq
        string prefix1
        string suffix1
        int word_count
        string example_pointed
    }
    ROOT_VOWEL {
        int root_id FK
        int root_form_seq FK
        int vowel_seq
        string vowel_pattern
        int word_count
    }
    LEXICON {
        int root_id FK
        int root_form_seq FK
        int vowel_seq FK
    }
    LEXICON_KJV_RENDERING {
        int root_id FK
        int root_form_seq FK
        int vowel_seq FK
        int seq
        string rendering
    }
    LEXICON_YLT_RENDERING {
        int root_id FK
        int root_form_seq FK
        int vowel_seq FK
        int seq
        string rendering
    }
    LEXICON_YLT_CONTEXT {
        int root_id FK
        int root_form_seq FK
        int vowel_seq FK
        int seq
        int verse_id FK
        string context_text
    }
    LEXICON_FOUND_VERSE {
        int root_id FK
        int root_form_seq FK
        int vowel_seq FK
        int verse_id FK
    }
    GLOSSES {
        string strongs FK
        string source
        string gloss
    }
    KJV_WORDS {
        int kjv_word_id PK
        int verse_id FK
        int kjv_pos
        string kjv_word
        string strongs FK
    }
    KJV_RENDERINGS {
        int rendering_id PK
        int word_id FK
        string kjv_word
        string kjv_strongs FK
        string method
    }
    YLT_VERSES {
        int verse_id PK_FK
        string text
    }
    YLT_RENDERINGS {
        int rendering_id PK
        int word_id FK
        string ylt_word
        int ylt_word_pos
        string label
    }
    WORD_ALIGNMENT {
        int alignment_id PK
        int verse_id FK
        int seq
        int hebrew_word_id FK
        int kjv_word_id FK
        int ylt_rendering_id FK
        string syntactic_role
        string role_basis
    }
    WORD_VARIANTS {
        int word_id FK
        int variant_seq
        string variant_kind
        string unpointed
        string letters
        string variant_text
        string convention
        string source
        string witness
        string variant_type
        string basis
        string created_at
    }
    WORD_NOTES {
        int note_id PK
        int word_id FK
        string note_text
        string note_type
        string source
        string created_at
    }
    MORPH_VARIANTS {
        int word_id FK
        int variant_seq
        string morph_code
        int pattern_id FK
        string confidence
        string source
        string basis
    }
    USER_ACCOUNTS {
        int user_id PK
        string username UK
        string password_hash
        string email
        string display_name
        int is_active
        string created_at
        string last_login_at
    }
    LEMMA_DEFAULT {
        int translation_id FK
        string lemma PK
        string rendering
        int from_word_id
        int source
        int other_option_id
    }
    WORD_CHOICE {
        int translation_id FK
        int word_id FK
        int choice
    }
    READING_POSITION {
        int user_id PK_FK
        int book_id FK
        int chapter
        int translation_id FK
        string updated
    }
    WITNESS_VERSES {
        int verse_id FK
        string witness
        int words
        string text_syr
        string text_translit
    }
    VERSE_NOTES {
        int verse_id FK
        string witness
        string note_kind
        string note_text
        string basis
        string created_at
    }
    APP_USER {
        int user_id PK
        string name
        string created_at
    }
    TRANSLATION {
        int translation_id PK
        int user_id FK
        int owner_id FK
        string name
        string description
        string created_at
        string updated_at
    }
    OTHER_OPTION {
        int option_id PK
        int translation_id FK
        int idx
        string text
        string created_at
    }
    GNT_BOOKS {
        int book_id PK
        string code
        string name
        string note
    }
    GNT_VERSES {
        int gnt_verse_id PK
        int corpus_verse_id FK
        string text
    }
    GNT_WORDS {
        int gnt_verse_id FK
        int position
        string surface
        string beta
        string strongs FK
        string morph
    }
    GNT_ALIGNMENT {
        int corpus_verse_id FK
        int gnt_position
        int kjv_pos FK
    }
    GNT_YLT_RENDERINGS {
        int gnt_verse_id FK
        int gnt_position
        int ylt_word_pos
        string ylt_word
    }
    GNTB_BOOKS {
        int book_id PK
        string code
        string name
        string note
    }
    GNTB_VERSES {
        int gnt_verse_id PK
        int corpus_verse_id FK
        string text
    }
    GNTB_WORDS {
        int gnt_verse_id FK
        int position
        string surface
        string strongs FK
        string morph
    }
    GNTB_ALIGNMENT {
        int corpus_verse_id FK
        int gntb_position
        int kjv_pos FK
    }
    GNTB_YLT_RENDERINGS {
        int gntb_verse_id FK
        int gntb_position
        int ylt_word_pos
        string ylt_word
    }
    GNTS_BOOKS {
        int book_id PK
        string code
        string name
        string note
    }
    GNTS_VERSES {
        int gnt_verse_id PK
        int corpus_verse_id FK
        string text
    }
    GNTS_WORDS {
        int gnt_verse_id FK
        int position
        string surface
        string lemma
        string morph
    }
    GNTS_ALIGNMENT {
        int corpus_verse_id FK
        int gnts_position
        int kjv_pos FK
    }
    GNTS_YLT_RENDERINGS {
        int gnts_verse_id FK
        int gnts_position
        int ylt_word_pos
        string ylt_word
    }
    GNT_VARIANTS {
        int corpus_verse_id FK
        string tradition
        string status
        string detail
    }
    LXX_BOOKS {
        string osis PK
        string tradition
    }
    LXX_VERSES {
        int verse_id PK
        string text
    }
    LXX_WORDS {
        int verse_id FK
        int position
        string surface
        string strongs FK
    }
    LXX_CROSSWALK {
        int mt_verse_id FK
        int lxx_verse_id FK
        string osis FK
        string relation
    }
    YLT_VERSES_EMBEDDING_STORE {
        int verse_id PK_FK
        string chunk
        vector embedding
    }
    HEBREW_VERSES_EMBEDDING_STORE {
        int verse_id PK_FK
        string chunk
        vector embedding
    }
    GREEK_VERSES_EMBEDDING_STORE {
        int verse_id PK_FK
        string chunk
        vector embedding
    }
    HEBREW_VOWEL_VARIANT_GROUP {
        int group_id PK
    }
    HEBREW_VOWEL_VARIANT_MEMBER {
        int group_id FK
        int root_id
        int root_form_seq
        int vowel_seq
    }
    BOOKS ||--o{ VERSES : contains
    VERSES ||--o{ WORDS : contains
    VERSES ||--o{ KJV_WORDS : contains
    VERSES ||--|| YLT_VERSES : has_text
    VERSES ||--o{ WORD_ALIGNMENT : aligns
    WORDS }o--|o STRONGS : tagged_with
    WORDS }o--|o STRONGS_SOURCES : source_recorded_in
    WORDS }o--|o MORPH_PATTERNS : parsed_as
    STRONGS ||--o{ STRONGS_COMPONENTS : decomposes_to
    STRONGS ||--o{ GLOSSES : glossed_by
    MORPH_PATTERNS ||--o{ MORPH_SEGMENTS : splits_into
    ROOT_ENTRY ||--o{ ROOT_FORM : has
    ROOT_FORM ||--o{ ROOT_VOWEL : has
    ROOT_VOWEL ||--|| LEXICON : describes
    WORDS }o--|| ROOT_VOWEL : numbered_as
    LEXICON ||--o{ LEXICON_KJV_RENDERING : lists
    LEXICON ||--o{ LEXICON_YLT_RENDERING : lists
    LEXICON ||--o{ LEXICON_YLT_CONTEXT : cites
    LEXICON ||--o{ LEXICON_FOUND_VERSE : found_in
    LEXICON_YLT_CONTEXT }o--|| VERSES : quotes
    LEXICON_FOUND_VERSE }o--|| VERSES : locates
    KJV_WORDS }o--|o STRONGS : tagged_with
    WORDS ||--o{ KJV_RENDERINGS : rendered_as
    KJV_RENDERINGS }o--|o STRONGS : via_kjv_strongs
    WORDS ||--o{ YLT_RENDERINGS : rendered_as
    WORD_ALIGNMENT }o--|o WORDS : hebrew_side
    WORD_ALIGNMENT }o--|o KJV_WORDS : kjv_side
    WORD_ALIGNMENT }o--|o YLT_RENDERINGS : ylt_side
    WORDS ||--o{ WORD_VARIANTS : varies_as
    WORDS ||--o{ WORD_NOTES : noted_in
    WORDS ||--o{ MORPH_VARIANTS : morph_readings
    MORPH_VARIANTS }o--|o MORPH_PATTERNS : staged_as
    APP_USER ||--o{ TRANSLATION : owns
    USER_ACCOUNTS o|--o{ TRANSLATION : owns_as_owner
    TRANSLATION ||--o{ OTHER_OPTION : adds
    TRANSLATION ||--o{ WORD_CHOICE : selects
    WORD_CHOICE }o--|| WORDS : chooses_for
    TRANSLATION ||--o{ LEMMA_DEFAULT : defaults
    USER_ACCOUNTS ||--|| READING_POSITION : reads_at
    VERSES ||--o{ WITNESS_VERSES : witnessed_by
    VERSES ||--o{ VERSE_NOTES : noted_in
    TRANSLATION }o--o{ WORDS : targets
    VERSES ||--o| GNT_VERSES : has_tr_text
    GNT_VERSES ||--o{ GNT_WORDS : contains
    GNT_WORDS }o--|o STRONGS : tagged_with
    GNT_ALIGNMENT }o--|| VERSES : aligns_verse
    GNT_ALIGNMENT }o--o{ KJV_WORDS : kjv_side
    GNT_VERSES ||--o{ GNT_YLT_RENDERINGS : rendered_as
    VERSES ||--o| GNTB_VERSES : has_byzantine_text
    GNTB_VERSES ||--o{ GNTB_WORDS : contains
    GNTB_WORDS }o--|o STRONGS : tagged_with
    GNTB_ALIGNMENT }o--|| VERSES : aligns_verse
    GNTB_ALIGNMENT }o--o{ KJV_WORDS : kjv_side
    GNTB_VERSES ||--o{ GNTB_YLT_RENDERINGS : rendered_as
    VERSES ||--o| GNTS_VERSES : has_sblgnt_text
    GNTS_VERSES ||--o{ GNTS_WORDS : contains
    GNTS_ALIGNMENT }o--|| VERSES : aligns_verse
    GNTS_ALIGNMENT }o--o{ KJV_WORDS : kjv_side
    GNTS_VERSES ||--o{ GNTS_YLT_RENDERINGS : rendered_as
    VERSES ||--o{ GNT_VARIANTS : variant_status_in
    LXX_BOOKS ||--o{ LXX_CROSSWALK : mapped_in
    VERSES ||--o{ LXX_CROSSWALK : mt_side
    LXX_VERSES ||--o{ LXX_CROSSWALK : lxx_side
    LXX_VERSES ||--o{ LXX_WORDS : contains
    LXX_WORDS }o--|o STRONGS : tagged_with
    VERSES ||--|| YLT_VERSES_EMBEDDING_STORE : embedded_as
    VERSES ||--|| HEBREW_VERSES_EMBEDDING_STORE : embedded_as
    VERSES ||--|| GREEK_VERSES_EMBEDDING_STORE : embedded_as
    GNT_BOOKS ||--o{ GNT_VERSES : contains
    GNTB_BOOKS ||--o{ GNTB_VERSES : contains
    GNTS_BOOKS ||--o{ GNTS_VERSES : contains
    HEBREW_VOWEL_VARIANT_GROUP ||--o{ HEBREW_VOWEL_VARIANT_MEMBER : has_members
    WORDS ||--o{ WORD_VARIANT_EMBEDDINGS : embedded_as
    OAUTH_CLIENT ||--o{ OAUTH_CODE : authorized_by
    OAUTH_CLIENT ||--o{ MCP_ACCESS_TOKEN : issued_to
    OAUTH_CLIENT ||--o{ OAUTH_REFRESH_TOKEN : issued_to

    WORD_VARIANT_EMBEDDINGS {
        int word_id PK_FK
        int variant_seq PK
        vector embedding
        string model
    }
    OAUTH_CLIENT {
        string client_id PK
        string redirect_uri
        string client_name
    }
    OAUTH_CODE {
        string code_hash PK
        string client_id FK
        string pkce_challenge
        string expires_at
    }
    MCP_ACCESS_TOKEN {
        string token_hash PK
        string client_id FK
        string scope
    }
    OAUTH_REFRESH_TOKEN {
        string token_hash PK
        string client_id FK
        string rotated_from
    }
```

Notes on the ERD: composite primary keys (`ROOT_FORM`, `ROOT_VOWEL`, `LEXICON` and its children, `GLOSSES`, `WORD_VARIANTS`, `MORPH_VARIANTS`, `STRONGS_COMPONENTS`, `WORD_CHOICE` (translation_id, word_id), `LEMMA_DEFAULT` (translation_id, lemma), `WITNESS_VERSES`, `VERSE_NOTES`) are declared in `schema_v2.sql` or in the `app_v2.py` migration DDL quoted in the Grounding notes; the `PK`/`FK` marks above show membership, not single-column keys. `YLT_VERSES.verse_id` is both PK and FK to `VERSES`. `WORD_CHOICE.choice` is CHECK-constrained 1–255 and sparse: an absent row means choice 0 (2026-10-09, replacing the byte files). The `TRANSLATION }o--o{ WORDS : targets` link is logical, not a declared FK — since 2026-10-09 the corpus lives in the PostgreSQL `bible` database and website data in the PostgreSQL `bible_app` database; the SQLite file `bible_v2.db` remains the build corpus the variant builders write, synced to PostgreSQL by `export_sync.py`. The Greek extension tables (2026-11-04/07) key off the corpus grid: each tradition's verses carry both their own `gnt_verse_id` and the `corpus_verse_id` of the shared `VERSES` row, and each tradition's alignment/rendering tables mirror the TR shape (`gntb_` Byzantine, `gnts_` SBLGNT; SBLGNT words carry `lemma` instead of a Strong's number, per MorphGNT). `LXX_WORDS` attributes beyond the verse link are representative (see Grounding notes). The embedding store is a pgvector table in the PostgreSQL `bible` database, keyed by `verse_id`, written by the vectorizer and read only by `/api/search`.

**Estates (2026-11-12 census).** The diagram spans four estates with different synchronization domains; only the first is governed by `schema_v2.sql`. (1) *Corpus estate* — the 46 corpus tables (SQLite build corpus `bible_v2.db`, synced to the PostgreSQL `bible` database); as of 2026-11-12 `schema_v2.sql` defines all 46. (2) *Authoring estate* — `bible_app` (`APP_USER`, `TRANSLATION`, `WORD_CHOICE`, `OTHER_OPTION`, `LEMMA_DEFAULT`, `READING_POSITION`, `USER_ACCOUNTS`), documented with the BibleApp repository, deliberately outside corpus synchronization. (3) *Embedding estate* — the three pgvector verse stores in PostgreSQL `bible` (YLT written by the pgai vectorizer; the Hebrew and Greek stores written by the language-store builder, Ollama `nomic-embed-text`; provenance spot-test passed 2026-11-12, issue #26). (4) *Frozen shadow estate* — database `bible_hebrew_variant_shadow_20261107`, a 2026-11-07 snapshot whose `HEBREW_VOWEL_VARIANT_GROUP` / `HEBREW_VOWEL_VARIANT_MEMBER` tables back the variant API; its runtime invariants are calibrated to the snapshot, so it is excluded from synchronization by design. **Search estate (2026-11-12).** (5) *Spelling-variant search estate* — PostgreSQL database `bible_search_prod_20261111`: `WORD_VARIANT_EMBEDDINGS` (528,565 rows keyed `(word_id, variant_seq)`, 768-dim `nomic-embed-text` vectors, IVFFlat cosine index) plus search copies of `word_variants`/`words`/`verses`/`books`, read by the Flask app as `bible_search_prod_ro` (SELECT-only) via `BIBLE_VARIANT_SEARCH_DATABASE_URL`; a rollback snapshot `words_merge_rollback_20261112` is retained in the same database. **MCP gateway runtime stores:** the `OAUTH_CLIENT` / `OAUTH_CODE` / `MCP_ACCESS_TOKEN` / `OAUTH_REFRESH_TOKEN` entities above are the gateway's deployment-side runtime stores (file-backed in `/home/mcpgw/secrets/`, mode 0600, tokens stored SHA-256 hashed) — they are NOT corpus tables, are not governed by `schema_v2.sql`, and never enter this repo; their shapes are grounded in `mcp-gateway/README.md` and `mcp-gateway/oauth_as.py` (OBSERVED) with exact serialization INFERRED. **WORD_NOTES disposition:** `WORD_NOTES` appears in no store (corpus, PostgreSQL, or shadow) as of the 2026-11-12 census — it is a planned entity, retained in the diagram as such; the live note apparatus is `VERSE_NOTES` / `WITNESS_VERSES`.

## Grounding notes

- OBSERVED (`schema_v2.sql`, 24 tables): exact table/column names, PKs, FKs, UNIQUE and CHECK constraints quoted above; `words.strongs` nullable (6,008 words), `words.morph_pattern_id` nullable (79 words), `words.strongs_source_id` null iff strongs null (CHECK).
- OBSERVED (migration verification, 2026-09-28): `migrate_v2.py` completed in 66.9 s over 264,217 words; `v_words` 0 differing rows; 0 FK violations; lexicon round-trips 0 mismatches on 126,869 rows; `orig_word_id` not unique (51399, 252785, 227963 each map to 2 rows — split/merged tokens), so no UNIQUE constraint.
- OBSERVED: 1,865 composite Strong's values decomposed into 3,783 `strongs_components` rows (reconstruction assertion 1,865/1,865); 155 components (e.g. `H010`) have no row of their own, so components are NOT a hard FK to `strongs`.
- OBSERVED: `verses` = UNION of (book,chapter,verse) from words, ylt_verses, kjv_words — the 139 English-versification orphans (e.g. Genesis 31:55) resolve; 209 word-derived verses lack YLT.
- OBSERVED: 7,552 `morph_patterns`; `parse_status` parsed/unparsed per the OSHB Hebrew Morphology Codes document (openscriptures.github.io/morphhb/parsing/HebrewMorphologyCodes.html, fetched 2026-09-28, CC BY 4.0); `morph_variants` holds 28 staged readings over 12 words (confidence legacy/established/probable/secondary), never assigned to `words` until adjudicated.
- OBSERVED (`schema_v2.sql` diff, 2026-09-30): `word_variants` MERGED per Kit's decision — ONE table tagged by `variant_kind` CHECK (`'spelling'` | `'textual'`), gaining `variant_text`, `witness`, `variant_type`, `created_at`; `convention`/`source` now nullable (used only for spelling rows). Column discipline per `variants_method.md`: spelling rows use `unpointed`/`letters` + `convention` (`v1-medial` | `academic-final`) + `source` (`v1-stored` | `oshb-verbatim` | `transduced-from-v1` | `conjectural`); textual rows use `variant_text` (pointed reading) + `witness` (manuscript siglum: `LXX`, `DSS`, `SP`, …) + `variant_type` (`orthographic` | `substantive` | …). `variant_seq` continues per word across kinds (spelling rows first, textual appended).
- OBSERVED (`migrate_variants_merge.py`, 2026-09-30): upgraded existing databases in place — all 528,565 rows backfilled `'spelling'`, old-column values verified byte-identical via EXCEPT both ways, 0 FK violations. No textual rows populated yet; the textual apparatus is populated separately.
- OBSERVED (`schema_var_notes.sql`, 2026-09-29): defines the `word_notes` table (note_id PK, word_id FK, note_text, note_type, source, created_at) — one word, many notes, per Kit ("definitely a one to many relationship"); resolves U-4. The file's earlier standalone `word_variants` definition is marked superseded (kept as the column-origin record for the textual kind); the merged table in `schema_v2.sql` is authoritative.
- OBSERVED (`apply_anomaly_resolutions.py`, 2026-09-29): applies 129 OSHB-verified unpointed/letters fixes to `bible_v2`.
- OBSERVED (`website/app_v2.py` diff, commit 3635422d, 2026-09-30): new `/variants` explorer route serving variant readings; routes are now book/chapter/verse/word/choice/translations/reading/export plus `/variants`.
- OBSERVED (`database/bible_dump.sql.gz.part-aa`…`.part-ad`, merged 2026-09-30): pg_dump of the live `bible_v2.db`, 4 parts, published in the repo as a distributable corpus snapshot (commit 02032780).
- OBSERVED (`website/schema.sql`): `app_user`, `translation`, `other_option` verbatim; `website/app.py` (Flask) opens `bible.db` read-only, `app.db` read-write, `user_data/translation_<id>.choices` byte files.
- OBSERVED: **live cutover DONE 2026-09-28 ~17:15 PDT** on Kit's authorization ("go live with it both on github and on the laptop"): supervisord `bible` runs `app_v2.py` on 5057 with `BIBLE_DB=/opt/bible/bible_v2.db`; Apache `/bible`→5057 unchanged; `/bible` + direct 5057 verified 200; word/book/verse pages 200. The 2026-09-30 laptop re-ship (anomaly-corrected `bible_v2.db`) was verified live. The previous diagram revision still showed the website reading the v1 `bible.db` live — that contradiction is corrected in this revision (8.0 reads D3 only; D2 remains the migration input).
- OBSERVED (Kit 2026-10-01, implemented by 2026-10-10): the website's variant readings are the academic (textual) variants, not his manuscript variance — `export_sync.py` exports only `variant_kind='textual'` rows for the website sync.
- OBSERVED (`website/app_v2.py` at HEAD 18ef982a, 2026-10-18): PostgreSQL port — `import psycopg2`, `BIBLE_DB` default `bible`, `APP_DB` default `bible_app`, corpus connection documented "Read-only corpus database (PostgreSQL `bible`)" and app connection "Application database (PostgreSQL `bible_app`): user accounts, translations, lemma defaults, reading positions"; header comment: "the website now reads from PG instead of SQLite so it can be administered via the Lampy admin tool (Kit 2026-10-09)".
- OBSERVED (`website/app_v2.py` migration DDL): `user_accounts(user_id SERIAL PK, username UNIQUE, password_hash, email, display_name, is_active, created_at, last_login_at)` with werkzeug password hashes and Flask session logins (`/signup`, `/login`, `/logout`); `lemma_default(translation_id, lemma, rendering, from_word_id, PRIMARY KEY(translation_id, lemma))` plus `source` (1=KJV, 2=Young's, 3=user-defined) and `other_option_id` columns; `translation.owner_id REFERENCES user_accounts(user_id) ON DELETE SET NULL` (NULL = legacy/anonymous); `word_choice(translation_id, word_id, choice SMALLINT CHECK 1–255, PRIMARY KEY(translation_id, word_id))` — "normalized per-word translation choices; replaces the translation_<id>.choices flat files; sparse: only non-default choices are rows" (2026-10-09); `reading_position(user_id PK, book_id, chapter, translation_id, updated)` for the Read door (2026-10-08).
- OBSERVED (`website/app_v2.py` routes at HEAD): two-doors landing at `/` (Study door and Read door), `/books`, `/read` + `/read/<book>/<chapter>` with translation picker, prev/next, and per-user reading position, `/interlinear`, `/api/books`, `/api/chapters/<n>`, `/api/verses/<n>/<c>`, `/papyrus-tile.png`, in addition to the pre-existing book/chapter/verse/word/choice/translations/reading/export/variants routes.
- OBSERVED (`build_variants_kq.py`): Kethiv/Qere rows — `variant_kind='textual'`, `witness='MT'`, `variant_type='qere'`, from the OSHB morphhb WLC apparatus staged at `sources/morphhb/wlc`; the 2026-10-15 skeleton-search fallback recovered 91 previously skipped pairs.
- OBSERVED (`build_variants_sp.py`): Samaritan Pentateuch rows (`witness='SP'`), source DT-UCPH/sp Text-Fabric 7.2.4 (Schorch editio maior, CC BY-NC 4.0, staged at `sources/sp`), Torah only, per-verse folded-skeleton alignment against MT; matres-only differences are `orthographic`, others `substantive`; final-form-only differences are marked `orthographic` with the FF_SUFFIX basis flag (Kit 2026-10-17).
- OBSERVED (`build_variants_dss.py`): Dead Sea Scrolls rows (`witness` = the scroll's siglum, e.g. `1Qisaa`), source ETCBC/dss Text-Fabric 2.0.1 (Abegg transcriptions, CC BY-NC 4.0, staged at `sources/dss`), fully attested verses only, reusing the Samaritan alignment engine and the same final-form marking.
- OBSERVED (`build_notes_syr.py`): Syriac leg is verse-scale only — creates `witness_verses` (Syriac text per verse) and `verse_notes` (`no_counterpart` and `length_divergence` measured notes, witness `Syr`), source ETCBC/peshitta Text-Fabric v0.5 (Leiden Peshitta main text, CC BY-NC 4.0); it deliberately creates NO word-level Syriac rows. `website/app_v2.py` reads both tables for the verse-scale block (`verse_witness_rows`, `verse_note_rows`), tolerating their absence.
- OBSERVED (`export_sync.py`): exports `word_variants` textual rows, `witness_verses`, and `verse_notes` from the local SQLite `bible_v2.db` to `worker-out/sync/*.csv` in PG COPY format "for the sync to the website's PostgreSQL `bible` DB (Kit 2026-10-17: add and sync with website, both word and verse scale variations)".
- OBSERVED (`build_ylt_align.py` diff and commits df162a5e / 7f5dfe4c, 2026-10-17/18): the YLT bridge was ported to v2 and re-run; Kit accepted the 0.7923 precision v2 baseline and the bridge was applied. This is a data refresh, not a schema change.
- OBSERVED: v1 row counts from README — words 264,217; kjv_words 610,324; kjv_renderings 631,950; ylt_renderings 337,601; ylt_verses 23,145; glosses 17,347; books 39; root_entry 30,087; root_form 57,724; root_vowel 126,869; lexicon 126,869.
- OBSERVED: `worker-out/` subdirectories (canon, kjv, lexicons, oshb, ylt) — the basis for D1; repair scripts named in 5.0; U-8 maqqef-component and U-9 verse-remap repairs with before/after coverage figures in README.
- INFERRED: the numbered process boundaries 1.0–8.0 group scripts by their documented purpose; the repo documents each script's role but no explicit pipeline wiring, so boundaries are inferred.
- INFERRED: `KJV_RENDERINGS.method` values 'direct' | 'maqqef-component' | 'verse-remap' and `YLT_RENDERINGS.label` = 'bridged' are observed in schema comments as the design's vocabulary.
- OBSERVED (commit 097c7f11, 2026-11-04): NT extension loaded — TR Greek 141,009 words (Robinson parsed, public domain), KJV NT 180,568 words, YLT NT 7,957 verses; all three grids identical; books now 66. Builder `build_nt.py` is present at HEAD.
- OBSERVED (commits 350c1123 / ac68d110 / c171ccb7, 2026-11-04; `LXX_AUDIT_2026-11-03.md` at HEAD): LXX loaded as a witness layer — 57 books, 30,371 verses, 623,693 words, G-numbers on 93.3% of words; source CenterBLC/LXX (license chain MIT over CATSS/Wong, documented in the audit; Kit's ruling a5a09634 accepted the dataset on permissive terms, his own part remaining Unlicense); numbering-v1 crosswalk; Kit's rulings: full Greek canon, Theodotion Daniel primary (the Old Greek rides as the alternate). Builder `build_lxx.py` at HEAD.
- OBSERVED (`website/app_v2.py` at HEAD a3cd9e9d, `_api_lxx_field`): an OT verse payload carries its LXX witness via `lxx_crosswalk` (`mt_verse_id`, `lxx_verse_id`, `osis`, `relation='same'`) joined to `lxx_books` (`osis`, `tradition`) and `lxx_verses` (`verse_id`, `text`); for Daniel the DanTh row is primary and the other tradition is returned as `lxx_alt`.
- OBSERVED (commit fb6fd32d, 2026-11-04): GNT variants loaded as witnesses — Byzantine (RP, Unlicense) 7,953 verses and SBLGNT/MorphGNT 7,927 verses; `gnt_variants` summary vs TR with method stamps. Builder `build_gnt_variants.py` at HEAD.
- OBSERVED (`website/app_v2.py` at HEAD, `_api_verse_nt` and `_greek_phrases`): NT verse payloads are built from `gnt_verses` (`gnt_verse_id`, `corpus_verse_id`, `text`) and `gnt_words` (`gnt_verse_id`, `position`, `surface`, `beta`, `strongs`, `morph`); the KJV side comes from `gnt_alignment` (`corpus_verse_id`, `gnt_position`, `kjv_pos` → `kjv_words`), the computed-Young's side from `gnt_ylt_renderings` (`gnt_verse_id`, `gnt_position`, `ylt_word_pos`, `ylt_word`); variant texts come from `gntb_verses` / `gnts_verses` with per-verse status from `gnt_variants` (`corpus_verse_id`, `tradition`, `status`, `detail`); the payload's Greek lexicon is "derived from LXX word data (most frequent lemma/gloss per Strong's number)".
- OBSERVED (`website/app_v2.py` at HEAD, `_api_verse_nt` variant block; commit a3cd9e9d, 2026-11-07): each variant tradition's own words and phrases are served as `greek_words_variants` (`byz` / `sbl`) built from that tradition's bridge — `gntb_words` / `gnts_words` (SBLGNT words carry `lemma`, no Strong's), `{tradition}_alignment` → KJV words, `{tradition}_ylt_renderings` → computed Young's — mirroring the TR construction; TR payloads were byte-identical before and after the change.
- OBSERVED (commits e9ecb4af / 5b8d40c5 / a9ad64d3 / 9abd3bfa, 2026-11-04/06; `VARIANT_BRIDGES_PLAN_2026-11-03.md` at HEAD): the variant alignment bridges were commissioned by Kit with evaluation gates; the Byzantine bridge passed at 100% same-verse consistency and 98.49% silver agreement and was written + PG-synced; the SBLGNT bridge was built and gated in SQLite, then loaded into PostgreSQL on Kit's authorization (2026-11-06) with counts verified PG == SQLite (specimens: John 1:1 full, 1 John 5:7 sparse as expected). Builders `build_gntb_bridge.py`, `build_gnts_bridge.py`, and `export_sync_gnt.py` are present at HEAD.
- OBSERVED (`website/app_v2.py` at HEAD, route table): the JSON API is `/api/books`, `/api/chapters/<n>`, `/api/verses/<n>/<c>`, `/api/verse/<n>/<c>/<v>`, `/api/chapter/<n>/<c>`, `/api/word/<strongs>`, `/api/search` — Phase 3 (commit e35c20c7, 2026-11-03) added the verse/chapter/word/search endpoints; commit 9be8af4f routed the list endpoints through `_api_json` so all API responses carry CORS `Access-Control-Allow-Origin: *`; commit b02867ab set the 404 body contract (`error 'not found'` + `detail`).
- OBSERVED (`website/app_v2.py` at HEAD, `api_search`; commit 79cfaaba, 2026-11-04): `/api/search` embeds the query with the local Ollama service (`http://127.0.0.1:11434/api/embeddings`, model `nomic-embed-text`; 503 `embedding service unavailable` when down) and ranks rows of `ylt_verses_embedding_store` (`verse_id`, `chunk`, `embedding` pgvector) by cosine distance, returning ref, score, and snippet with source stamp `ylt-computed`; the vectorizer auto-processed the NT rows so the store holds 31,102 verses.
- OBSERVED (commits ef1ccec5 / 1b472919, 2026-11-03): computed-Young's grammar repair (R2 construct extension + guarded evidence-based claiming; R3 possessive capture failed its gate and was dropped) applied corpus-wide on Kit's ruling — gold precision 0.7923 → 0.7984, recall 0.4558 → 0.5039, drift 0; `ylt_renderings` 339,153 → 358,391 rows; `lexicon_ylt_rendering` rebuilt (98,090 groups / 234,091 rows); PG synced. Script `apply_ylt_grammar_repair.py` at HEAD. A follow-up (b4229600, 2026-11-05) expanded the gold set to 42 verses and gate-passed a span-boundary prototype on a copy — not yet applied to the corpus.
- OBSERVED (commit dbaa5b12, 2026-11-04): number-aware API gloss — plural nouns inflect the lemma gloss (allowlist + guards), live-verified at Eccl 1:2 ("vanities"); the Elohim-class resolution (form-keyed transliteration/singular sense for -ayim duals: mayim, Mitzrayim) is recorded in commit a08452de as a plan addendum — the form-keyed registry build is not in this week's commits, so no registry table is drawn.
- INFERRED: `LXX_WORDS` columns beyond `verse_id` (position, surface, strongs) are representative — the 623,693-word census and the "derived from LXX word data" lexicon note are observed, but this run did not read `build_lxx.py`'s DDL. Likewise process 16.0's vectorizer is named from the commit record ("vectorizer auto-processed NT rows"); its script name was not observed in this run.

- OBSERVED (2026-11-14 run, commits 2026-11-08…12 since the 2026-11-07 watermark 9440b3a4; 274 commits reviewed): the MCP gateway subsystem (`mcp-gateway/` directory at HEAD 9cb32306: `gateway.py` 25,303 B, `oauth_as.py` 21,543 B, `gw_admin.py`, `setup_mcp_ro.py`, `root_helper.py` + `root_helper_launcher.c`, `phase5_test.py`, batteries) and its README (11 read-only tools, OAuth 2.1 AS with PKCE S256, out-of-band owner approval, `mcp_ro` SELECT-only role, Tailscale Funnel exposure, secrets only in `/home/mcpgw/secrets/`); Phase 5 write/exec tools per commit a4485753 and PR #33 merge 9cb32306 (fs_write, fs_edit, exec_run, write scope, setuid root helper) — the README's tool table predates Phase 5, so the Phase 5 grounding is the commit record plus the file listing, not the README.
- OBSERVED (2026-11-14 run, `website/app_v2.py` commit series 2026-11-09): JSON auth endpoints for PWA sessions (fcc016d5; tests 42a7396f), Flask identity-token issuer atop ownership checks (1399e583, 46b5a35b; CSRF-header acceptance 7d218d99), translation-ownership enforcement in Flask routes (d8d120df, b1cddef2, ffef6730), and the word-ID phrase-options endpoint (1ea4b2ef; `no-store` marking 18cd612a, tests 9a24b3b7). Exact HS256/five-minute parameters are grounded in the sibling BibleApp/BibleApp-pwa architecture docs' OBSERVED notes for the same contract.
- OBSERVED (2026-11-14 run): schema governance commit 8f81ab85 (2026-11-12) extended `schema_v2.sql` to all 46 corpus tables and completed the ERD estate census already recorded above; hidden-verse commit 4adb70a8 (issue #23) is the same change recorded in the 2026-11-11 revision note. The remaining ~260 commits in the window are Hebrew vowel-variant adjudication records, QA batteries, and documentation — no further routes, stores, or flows.

## Hebrew spelling embedding search — 2026-11-09

The existing `GET /api/search` remains the YLT passage-semantic endpoint: it embeds the query with local Ollama `nomic-embed-text` and searches 31,102 verse vectors in `bible.ylt_verses_embedding_store`. This route and index are unchanged.

A separate `GET /api/search/variants?q=<Hebrew spelling>` endpoint adds Hebrew word-form retrieval. It uses a reconstructed dataset of 528,565 spelling-variant embeddings, keyed by `(word_id, variant_seq)`, with 768-dimensional `nomic-embed-text:latest` vectors. The SQLite recovery set was compared against the staging corpus's `variant_kind='spelling'` keys: 528,565 on each side, with no missing or extra keys and no duplicate embedding keys. Source blobs are 3,072 bytes each (768 float32 values).

The recorded embedding input is `letters`, falling back to `unpointed` and `variant_text`. Fourteen empty-field paseq rows were topped up from the corresponding pointed word form. Because those rows have no stored unpointed spelling, the current normalized exact-match predicate does not return them as exact matches; they remain represented in the vector corpus and may be found through semantic-neighbor retrieval. This is a reconstruction from the recovered corpus and metadata, not a claim of bit-for-bit reproduction of the lost original run.

The variant vectors live in a separate search database and are accessed through the optional server-side `BIBLE_VARIANT_SEARCH_DATABASE_URL` connection. The application uses a read-only role. The staging index uses pgvector cosine distance with an IVFFlat index; exact normalized spelling matches are placed first, followed by vector-nearest spelling forms. Hebrew combining marks are removed from query input to align pointed user input with the unpointed indexed representation. Exact SQL matches are evaluated before Ollama; if embedding generation or semantic retrieval is unavailable, exact results are still returned with the `X-Hebrew-Semantic-Search: unavailable` response header. All responses from the variant endpoint, including errors, carry `Cache-Control: no-store`; non-Hebrew-script queries are rejected.

The two indexes have different scopes: passage vectors retrieve YLT verses by meaning; variant vectors retrieve Hebrew spelling records by model proximity. Similarity is not proof of lexical identity, common morphology, or textual equivalence. Result payloads retain source and witness metadata.

## Hebrew spelling embedding search — production status (2026-11-12)

The 2026-11-09 staging-only statement above is historical and superseded by the production promotion recorded here. The separate Hebrew spelling-variant search database is now configured for the live Flask process through `BIBLE_VARIANT_SEARCH_DATABASE_URL`; the application uses the read-only PostgreSQL role `bible_search_prod_ro`. The live route is `GET /api/search/variants?q=<Hebrew spelling>`.

**Production target:** PostgreSQL database `bible_search_prod_20261111`. The canonical corpus remains PostgreSQL database `bible`; the search database is a separate retrieval store and does not replace or duplicate the verse-semantic embedding store `bible.ylt_verses_embedding_store`.

**Verified synchronization (2026-11-12):**
- `word_variant_embeddings`: 528,565 rows; ordered `(word_id, variant_seq)` keys and vector-content fingerprint match the recovery dataset and the compared search-store copies.
- Embeddings remain 768-dimensional `nomic-embed-text:latest` vectors. The 14 empty-text/paseq rows remain represented; no vectors were regenerated.
- The production search database's `word_variants`, `words`, `verses`, and `books` search fields were compared with `bible`. The three stale `words` metadata fields (`strongs`, `word_pos`, `verse_id`) were refreshed for 1,781 rows; the full 264,217-row target table then matched the source exactly.
- A persistent pre-update snapshot is retained as `public.words_merge_rollback_20261112` in `bible_search_prod_20261111` (264,217 rows; owner `postgres`). The update transaction committed only after exact full-table comparison. Its source and post-update SHA-256 are both `9c1b71b2feba53a0bc8a8724c00258fd3fdadb23cc19a69319b670c62ec086ae`.
- Post-update parity fingerprints matched for spelling-variant keys, spelling-variant content, word search fields, verse search fields, and book search fields.
- The production cosine IVFFlat index `word_variant_embeddings_cosine_ivfflat` remains present with `lists=512`; the primary-key index remains present.
- The live variant-search endpoint returned HTTP 200 with 10 JSON records after the update. The app role retained SELECT-only access to the search tables; no write privileges were granted.

**Scope and limitations:** no production corpus rows in `bible` were modified; no embedding vectors were regenerated; no application code, credentials, service configuration, or running services were changed or restarted. The separate reconciliation database `bible_reconcile_20261111` still lacks the IVFFlat cosine index; that database is not the live search target and no index was added there. The 2026-11-09 staging description above is retained as historical context, not current deployment status.
