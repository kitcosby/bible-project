# Academic variants by tradition — research extension (2026-10-14, Kit's order)

Goal: populate `word_variants` with genuine academic/textual variants, each
labeled by tradition via the existing `witness` column (schema already
supports this: variant_kind='textual', witness = siglum, variant_type,
variant_text = pointed reading, basis = evidence note). Current state:
528,565 rows, all variant_kind='spelling' (v1 artifacts), ZERO textual rows;
`/variants` intentionally empty until real apparatus data loads.

## Per-tradition source survey (verified 2026-10-14)

### 1. Masoretic — Kethiv/Qere — READY NOW, no external dependency
- OSHB (already the corpus base, CC BY) encodes ketiv (written) / qere
  (read) pairs. Local parse (`worker-out/oshb/parse_oshb.py`) counted
  **1,268 ketiv words / 1,278 qere words**; qere immediately follows its
  ketiv in document order → word-exact alignment.
- During assembly these were classed as OSHB-only "inserts"
  (assemble_bible.py) and never landed in `word_variants`.
- Label: witness='MT', variant_type='qere' (vs ketiv base). Ben Asher /
  ben Naphtali differences (~864, mostly vowels/accents) exist as a
  published list but no open machine-readable edition verified — deferred.

### 2. Dead Sea Scrolls — open data exists
- ETCBC `dss` Text-Fabric dataset: transcriptions of the biblical scrolls,
  verse-referenced, Hebrew. License to confirm at ingest.
- Alignment: word-diff per verse against MT; fragmentary coverage and
  differing word division are the known costs. Witness = scroll siglum
  (1QIsa-a, 4QDeut-j, …), tradition label DSS.

### 3. Samaritan Pentateuch — LOADED 2026-10-16 (8,574 rows)
- DT-UCPH `sp` Text-Fabric dataset **v7.2.4** (Zenodo 10.5281/zenodo.7734632,
  **CC BY-NC 4.0** — non-commercial use, attribution required), staged at
  `sources/sp` (untracked, like the morphhb fetch).
- Text: Schorch editio maior transcription (MS Dublin Chester Beatty
  751 + MS Garizim 1). Loader: `extract_sp.py` (analytic words joined
  to graphic words on the ETCBC trailer feature; shin/sin presentation
  forms normalized) → `build_variants_sp.py` (per-verse consonantal
  alignment vs MT; matres-only difference = orthographic).
- Result (verified by direct query of bible_v2.db): **8,574 rows**,
  witness='SP' — orthographic 5,357, substantive 1,721, addition 1,048
  (3,827 words), omission 448. All 5,841 SP verses aligned; 51,277 word
  pairs identical; 6,514 word-division-only blocks (no row).
- Accounting of non-loads: MT Exod 30:1–10 have no same-reference SP
  verse — SP places the incense-altar pericope after Exod 26:35 and
  the dataset groups it into that verse node, where it loads as one
  628-char addition row; Deut 34:2–3 have no SP verse node in this
  dataset. Dataset additions after Gen 30:36 are grouped under v36
  (not 36a/b/c) and surface as additions there (2 rows).
- Spot checks PASS: Gen 1:1 zero rows (identical); Gen 2:2 השביעי →
  הששי (substantive); Gen 4:8 addition נלכה השדה; Gen 5:20 chronology
  numbers (substantive). Loader idempotent.
- OPEN (flagged for Kit, 2026-10-16): exactly **2** word pairs in the
  Torah differ ONLY by final letterform (Gen 19:38, 35:18: בן־עמי /
  בן־אוני vs SP בנעמי / בנאוני — an ן/נ metathesis the fold masks).
  Under the standing sofit-fold rule they are dropped. Kit to confirm
  whether tradition-labeled final-form-only readings should instead
  be marked as rows.

### 4b. Syriac (Peshitta) — added by Kit 2026-10-16; source STAGED, scope = Kit's pick
- Survey complete 2026-10-16 (`worker-out/peshitta/FINDINGS.md`). One
  source passes the license gate: **ETCBC/peshitta** (Text-Fabric
  edition of the Leiden Peshitta main text; Brill apparatus expressly
  excluded, so "Syriac" = the single Leiden text, no intra-Syriac
  apparatus). Text data **CC BY-NC 4.0** per the repo's own
  docs/about.md (the MIT LICENSE covers only conversion code — GitHub's
  badge misleads here). Staged: `sources/peshitta` @ 9850f5a (v0.5,
  TF data 0.2) + PROVENANCE.md; verified load: 426,835 words, 31,341
  verses, 65 units (OT incl. Apocrypha), all 39 canon books.
- Rejected: CAL (no bulk access, no redistribution), SEDRA (NT-centric,
  no open license), STEPBible (no Syriac OT), PaTraCoSy alignment
  (Genesis only, no license), jcogitation (CAL-derived chain).
- Feasibility verdict: the Peshitta is a translation → Hebrew
  orthographic variants are unrecoverable in principle (this witness
  must never carry variant_type='orthographic'); no open scholarly
  MT↔Peshitta word alignment exists (the hand-built ones were never
  openly published; automatic ones are unlicensed/provisional).
  Recommended: **verse-level apparatus notes now** (witness label
  'Syr'); word-level rows later only for a hand-adjudicated,
  retroversion-secure subset (realistically tens to low hundreds,
  each with its retroversion reasoning in `basis`).


### 4. Septuagint — text open, Hebrew alignment NOT open
- Greek text: Swete (public domain); Rahlfs 1935 still in copyright.
- A Greek reading is not a Hebrew word-variant until retroverted. The
  scholarly MT↔LXX word alignment (Tov–Polak / CATSS) is not openly
  licensed → LXX enters, if at all, as verse-level apparatus notes
  ("LXX differs"), not word_variants rows. DEFERRED pending open alignment.

### 5. Printed apparatus (BHS / BHQ / HUBP) — NOT usable
- Deutsche Bibelgesellschaft / Hebrew University copyright; no open
  machine-readable apparatus. Excluded on licensing, same as NIV rule:
  public-domain / openly licensed sources only.

## Ingestion design (when Kit picks scope)
- One builder per tradition → rows into `word_variants` with
  variant_kind='textual', witness = tradition siglum, variant_type
  ('orthographic' | 'substantive' | 'qere' | 'addition' | 'omission'),
  basis = dataset + version citation. Existing display code already
  renders witness/source/basis columns; sofit-folding still applies.
  Final-form-only differences under a tradition label are currently
  DROPPED by the fold (SP leg: exactly 2 pairs) — whether they should
  be marked instead is flagged for Kit (see §3).
- Order of work by readiness: Kethiv/Qere → SP → DSS → (LXX notes).
