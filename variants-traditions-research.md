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

### 3. Samaritan Pentateuch — open data exists, Torah only
- DT-UCPH `sp` Text-Fabric dataset (Zenodo 10.5281/zenodo.7734632,
  **CC BY-NC 4.0** — non-commercial use, attribution required).
- Text: Schorch editio maior transcription (MS Dublin Chester Beatty
  751 + MS Garizim 1). Word features mirror BHSA → word-level alignment
  against MT Torah feasible. ~6,000 SP-vs-MT differences expected
  (standard scholarly count; most orthographic).

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
  renders witness/source/basis columns; sofit-folding still applies
  (orthographic-only differences that fold away are marked, not dropped,
  when they carry a tradition label — Kit to confirm).
- Order of work by readiness: Kethiv/Qere → SP → DSS → (LXX notes).
