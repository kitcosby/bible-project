-- Bible database v2 — normalized schema.
-- Built by migrate_v2.py from bible.db (v1). Design rationale: schema_v2.md.
-- Every FK declared and enforced. Conventions:
--   * book_id 1..39 preserved from v1 book_num (stable natural key).
--   * strongs keeps its stable TEXT form ('H7225') as PK.
--   * word_id values preserved from v1 (translation choice files index by word_id).
--   * Pure derivations (root_code, book/chapter/verse on word rows) live in
--     views, not tables. unpointed/letters are preserved verbatim from v1
--     (the migration does not adjudicate legacy values).

PRAGMA foreign_keys=ON;

CREATE TABLE books(
  book_id   INTEGER PRIMARY KEY,   -- 1..39, was book_num
  name_en   TEXT NOT NULL,
  name_he   TEXT NOT NULL
);

CREATE TABLE verses(
  verse_id  INTEGER PRIMARY KEY,
  book_id   INTEGER NOT NULL REFERENCES books(book_id),
  chapter   INTEGER NOT NULL,
  verse     INTEGER NOT NULL,
  hidden    INTEGER NOT NULL DEFAULT 0,  -- 1 = retained in the grid but never rendered (2026-11-11, issue #23 shells)
  UNIQUE(book_id, chapter, verse)
);
-- verses = UNION of (book,chapter,verse) from words, ylt_verses, kjv_words,
-- so the 139 English-versification orphans (e.g. Gen 31:55 = Heb 32:1) resolve.

CREATE TABLE strongs(
  strongs   TEXT PRIMARY KEY,       -- 'H7225', or a composite 'H01,H015' verbatim
  language  TEXT NOT NULL           -- 'H' (all H in this corpus; schema allows 'A')
);

-- Relational decomposition of composite Strong's values ('H01,H015').
-- The exact original string (and component order) is preserved here;
-- strongs.strongs keeps the verbatim composite. Components are NOT a hard
-- FK to strongs: 155 components (e.g. 'H010') have no row of their own.
CREATE TABLE strongs_components(
  strongs   TEXT NOT NULL REFERENCES strongs(strongs),
  seq       INTEGER NOT NULL,        -- 0-based component order
  component TEXT NOT NULL,           -- e.g. 'H01', verbatim
  PRIMARY KEY(strongs, seq)
);

CREATE TABLE strongs_sources(
  source_id INTEGER PRIMARY KEY,
  source    TEXT NOT NULL UNIQUE    -- 'oshb', 'oshb-split', 'kit'
);

CREATE TABLE morph_patterns(
  pattern_id   INTEGER PRIMARY KEY,
  pattern      TEXT NOT NULL UNIQUE,  -- OSHB @morph verbatim, e.g. 'HR/Ncfsa'
  language     TEXT,                  -- 'H' / 'A' (first char)
  parse_status TEXT NOT NULL DEFAULT 'parsed',  -- 'parsed' | 'unparsed'
  parse_notes  TEXT
);
-- 79 words have no morph: their morph_pattern_id is NULL (documented, kept).

CREATE TABLE morph_segments(
  segment_id INTEGER PRIMARY KEY,
  pattern_id INTEGER NOT NULL REFERENCES morph_patterns(pattern_id),
  seq        INTEGER NOT NULL,       -- 0-based, '/' split order
  code       TEXT NOT NULL,          -- segment code verbatim, e.g. 'Ncfsa'
  pos        TEXT,                   -- A C D N P R S T V
  pos_name   TEXT,
  stem       TEXT,  stem_name TEXT,   -- verbs
  conj       TEXT,  conj_name TEXT,   -- verbs: conjugation
  type       TEXT,  type_name TEXT,   -- adjectives/nouns/pronouns/preps/suffixes/particles
  person     TEXT,                   -- 1/2/3/x
  person_name TEXT,
  gender     TEXT,                   -- b/c/f/m/x
  gender_name TEXT,
  number     TEXT,                   -- d/p/s/x
  number_name TEXT,
  state      TEXT,                   -- a/c/d
  state_name TEXT,
  UNIQUE(pattern_id, seq)
);
-- COMPUTED parse of OSHB morphology codes per the authoritative doc
-- (openscriptures.github.io/morphhb/parsing/HebrewMorphologyCodes.html,
-- fetched 2026-09-28; CC-BY-4.0). Any segment with a code letter outside the
-- documented sets flags its pattern parse_status='unparsed'.

CREATE TABLE words(
  word_id           INTEGER PRIMARY KEY,  -- stable from v1
  orig_word_id      TEXT,                -- import natural key; NOT unique in v1
                                       -- (3 source ids each map to 2 word rows:
                                       --  split/merged tokens 51399, 252785, 227963)
  verse_id          INTEGER NOT NULL REFERENCES verses(verse_id),
  word_pos          INTEGER NOT NULL,
  pointed           TEXT NOT NULL,        -- canonical surface form (source)
  unpointed         TEXT,                 -- PRESERVED VERBATIM from v1
                                         -- (candidate derivation in migrate_v2.py
                                         -- for review only; NOT applied)
  letters           TEXT,                 -- PRESERVED VERBATIM from v1 (same)
  strongs           TEXT REFERENCES strongs(strongs),  -- NULL: 6,008 words
  strongs_source_id INTEGER REFERENCES strongs_sources(source_id),  -- NULL iff strongs NULL
  morph_pattern_id  INTEGER REFERENCES morph_patterns(pattern_id),   -- NULL: 79 words
  is_aramaic        INTEGER NOT NULL DEFAULT 0,
  root_id           INTEGER NOT NULL REFERENCES root_entry(root_id),
  root_form_seq     INTEGER NOT NULL,
  root_vowel_seq    INTEGER NOT NULL,
  FOREIGN KEY(root_id, root_form_seq) REFERENCES root_form(root_id, form_seq),
  FOREIGN KEY(root_id, root_form_seq, root_vowel_seq)
    REFERENCES root_vowel(root_id, root_form_seq, vowel_seq),
  UNIQUE(verse_id, word_pos),
  CHECK((strongs IS NULL) = (strongs_source_id IS NULL))
);

CREATE TABLE root_entry(
  root_id    INTEGER PRIMARY KEY,
  root       TEXT NOT NULL UNIQUE,
  word_count INTEGER NOT NULL   -- build-maintained cached aggregate
);

CREATE TABLE root_form(
  root_id         INTEGER NOT NULL REFERENCES root_entry(root_id),
  form_seq        INTEGER NOT NULL,
  prefix1         TEXT, prefix2 TEXT, prefix3 TEXT,
  suffix1         TEXT, suffix2 TEXT,
  prefix1_disp    TEXT, prefix2_disp TEXT, prefix3_disp TEXT,  -- MOVED from words (FD-verified)
  suffix1_disp    TEXT, suffix2_disp TEXT,
  word_count      INTEGER NOT NULL,  -- build-maintained cached aggregate
  example_pointed TEXT,
  example_unpointed TEXT,
  PRIMARY KEY(root_id, form_seq)
);

CREATE TABLE root_vowel(
  root_id       INTEGER NOT NULL,
  root_form_seq INTEGER NOT NULL,
  vowel_seq     INTEGER NOT NULL,
  vowel_pattern TEXT NOT NULL,
  word_count    INTEGER NOT NULL,  -- build-maintained cached aggregate
  PRIMARY KEY(root_id, root_form_seq, vowel_seq),
  FOREIGN KEY(root_id, root_form_seq) REFERENCES root_form(root_id, form_seq)
);

-- Lexicon: header + normalized children (were 4 multi-value TEXT blobs).
CREATE TABLE lexicon(
  root_id       INTEGER NOT NULL,
  root_form_seq INTEGER NOT NULL,
  vowel_seq     INTEGER NOT NULL,
  PRIMARY KEY(root_id, root_form_seq, vowel_seq),
  FOREIGN KEY(root_id, root_form_seq, vowel_seq)
    REFERENCES root_vowel(root_id, root_form_seq, vowel_seq)
);
CREATE TABLE lexicon_kjv_rendering(
  root_id INTEGER NOT NULL, root_form_seq INTEGER NOT NULL, vowel_seq INTEGER NOT NULL,
  seq     INTEGER NOT NULL,          -- preserves the build's frequency order
  rendering TEXT NOT NULL,
  PRIMARY KEY(root_id, root_form_seq, vowel_seq, seq),
  FOREIGN KEY(root_id, root_form_seq, vowel_seq)
    REFERENCES lexicon(root_id, root_form_seq, vowel_seq)
);
CREATE TABLE lexicon_ylt_rendering(
  root_id INTEGER NOT NULL, root_form_seq INTEGER NOT NULL, vowel_seq INTEGER NOT NULL,
  seq     INTEGER NOT NULL,
  rendering TEXT NOT NULL,
  PRIMARY KEY(root_id, root_form_seq, vowel_seq, seq),
  FOREIGN KEY(root_id, root_form_seq, vowel_seq)
    REFERENCES lexicon(root_id, root_form_seq, vowel_seq)
);
CREATE TABLE lexicon_ylt_context(
  root_id INTEGER NOT NULL, root_form_seq INTEGER NOT NULL, vowel_seq INTEGER NOT NULL,
  seq      INTEGER NOT NULL,
  verse_id INTEGER NOT NULL REFERENCES verses(verse_id),
  context_text TEXT NOT NULL,         -- the YLT verse text for that verse
  PRIMARY KEY(root_id, root_form_seq, vowel_seq, seq),
  FOREIGN KEY(root_id, root_form_seq, vowel_seq)
    REFERENCES lexicon(root_id, root_form_seq, vowel_seq)
);
CREATE TABLE lexicon_found_verse(
  root_id INTEGER NOT NULL, root_form_seq INTEGER NOT NULL, vowel_seq INTEGER NOT NULL,
  verse_id INTEGER NOT NULL REFERENCES verses(verse_id),
  PRIMARY KEY(root_id, root_form_seq, vowel_seq, verse_id),
  FOREIGN KEY(root_id, root_form_seq, vowel_seq)
    REFERENCES lexicon(root_id, root_form_seq, vowel_seq)
);

CREATE TABLE glosses(
  strongs TEXT NOT NULL REFERENCES strongs(strongs),
  source  TEXT NOT NULL,              -- 'bdb' | 'strongs_he'
  gloss   TEXT NOT NULL,
  PRIMARY KEY(strongs, source)
);

CREATE TABLE kjv_words(
  kjv_word_id INTEGER PRIMARY KEY,
  verse_id    INTEGER NOT NULL REFERENCES verses(verse_id),
  kjv_pos     INTEGER NOT NULL,
  kjv_word    TEXT NOT NULL,
  strongs     TEXT REFERENCES strongs(strongs),  -- NULL: 40,741 rows
  UNIQUE(verse_id, kjv_pos)
);

CREATE TABLE kjv_renderings(
  rendering_id INTEGER PRIMARY KEY,
  word_id      INTEGER NOT NULL REFERENCES words(word_id),
  kjv_word     TEXT NOT NULL,
  kjv_strongs  TEXT REFERENCES strongs(strongs),
  method       TEXT NOT NULL          -- 'direct' | 'maqqef-component' | 'verse-remap'
);
CREATE INDEX idx_kjv_renderings_word ON kjv_renderings(word_id);

CREATE TABLE ylt_verses(
  verse_id INTEGER PRIMARY KEY REFERENCES verses(verse_id),
  text     TEXT NOT NULL
);

CREATE TABLE ylt_renderings(
  rendering_id INTEGER PRIMARY KEY,
  word_id      INTEGER NOT NULL REFERENCES words(word_id),
  ylt_word     TEXT NOT NULL,
  ylt_word_pos INTEGER NOT NULL,
  label        TEXT NOT NULL          -- 'bridged' (computed alignment)
);
CREATE INDEX idx_ylt_renderings_word ON ylt_renderings(word_id);
CREATE INDEX idx_words_orig ON words(orig_word_id);
CREATE INDEX idx_words_verse ON words(verse_id);
CREATE INDEX idx_words_strongs ON words(strongs);
CREATE INDEX idx_words_morph ON words(morph_pattern_id);
CREATE INDEX idx_words_root ON words(root_id, root_form_seq, root_vowel_seq);
CREATE INDEX idx_kjv_words_verse ON kjv_words(verse_id);

-- ============================================================================
-- DERIVED-DATA STAGE (built after migrate_v2.py; not part of the base migration).
-- Build order: migrate_v2.py -> build_alignment.py -> build_variants.py
-- These tables record analysis/variance; they never alter base tables.
-- ============================================================================

CREATE TABLE word_alignment(
  alignment_id   INTEGER PRIMARY KEY,
  verse_id       INTEGER NOT NULL REFERENCES verses(verse_id),
  seq            INTEGER NOT NULL,
  hebrew_word_id INTEGER REFERENCES words(word_id),
  kjv_word_id    INTEGER REFERENCES kjv_words(kjv_word_id),
  ylt_rendering_id INTEGER REFERENCES ylt_renderings(rendering_id),
  syntactic_role TEXT NOT NULL,
  role_basis     TEXT NOT NULL,
  UNIQUE(verse_id, seq)
);
CREATE INDEX idx_alignment_hebrew ON word_alignment(hebrew_word_id);
CREATE INDEX idx_alignment_verse ON word_alignment(verse_id, seq);

CREATE TABLE word_variants(
  word_id      INTEGER NOT NULL REFERENCES words(word_id),
  variant_seq  INTEGER NOT NULL,
  variant_kind TEXT NOT NULL CHECK (variant_kind IN ('spelling','textual')),
  unpointed    TEXT NOT NULL,
  letters      TEXT NOT NULL,
  variant_text TEXT,         -- textual kind: pointed variant reading (NULL for spelling)
  convention   TEXT,          -- spelling kind: 'v1-medial' | 'academic-final'
  source       TEXT,          -- spelling kind: 'v1-stored' | 'oshb-verbatim' |
                              --   'transduced-from-v1' | 'conjectural'
                              --   (NULL for textual: provenance is witness)
  witness      TEXT,          -- textual kind: manuscript siglum ('LXX','DSS','SP',...)
  variant_type TEXT,          -- textual kind: 'orthographic' | 'substantive' | ...
  basis        TEXT,          -- evidence note / rule citation
  created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY(word_id, variant_seq)
);
CREATE INDEX idx_variants_word ON word_variants(word_id);
CREATE INDEX idx_variants_kind ON word_variants(variant_kind);

-- Morphology variance apparatus (built by apply_morph_corrections.py).
-- Established corrections re-point words.morph_pattern_id; probable and
-- secondary readings are staged here, never assigned to words.
CREATE TABLE morph_variants(
  word_id     INTEGER NOT NULL REFERENCES words(word_id),
  variant_seq INTEGER NOT NULL,
  morph_code  TEXT NOT NULL,
  pattern_id  INTEGER REFERENCES morph_patterns(pattern_id),  -- NULL when the
                               -- code has no pattern row (secondary readings)
  confidence  TEXT NOT NULL,   -- legacy | established | probable | secondary
  source      TEXT NOT NULL,   -- v1-stored | morphology-research-2026-09-28
  basis       TEXT,
  PRIMARY KEY(word_id, variant_seq)
);
CREATE INDEX idx_morph_variants_word ON morph_variants(word_id);

-- =====================================================================
-- Greek / LXX extension + witness apparatus (added 2026-11-12, §14).
-- These 22 tables complete the corpus schema: with the 24 above,
-- schema_v2.sql now defines all 46 corpus tables. Derived from a dual
-- inventory of the SQLite build corpus (bible_v2.db, the store of truth
-- for these tables' DDL) and the PostgreSQL `bible` catalog
-- (information_schema / pg_indexes), cross-checked column-by-column.
-- Review notes (2026-11-12):
--   * Unlike the core schema above, the Greek/LXX families declare NO
--     foreign keys in the corpus; their references (corpus_verse_id ->
--     verses, gnt_verse_id, book_id, osis) hold by builder convention.
--     verse_notes and witness_verses are the exceptions (FK declared).
--   * PostgreSQL types map INTEGER -> integer, TEXT -> text,
--     TIMESTAMP -> timestamp without time zone; column names and
--     nullability agree across both stores for all 22 tables.
--   * PostgreSQL divergences (documented, NOT repaired here): the
--     secondary indexes marked (*) exist in the corpus but were not
--     carried into PostgreSQL, and the lxx_crosswalk primary key was
--     likewise not carried into PostgreSQL.
--   * gntb_alignment / gnts_alignment and the gntb_/gnts_ YLT rendering
--     tables carry no primary key in either store (gnt_ TR has one) —
--     an as-built asymmetry of the bridge builders, recorded as-is.
-- =====================================================================

-- Septuagint (built by build_lxx.py; Theodotion Daniel is primary,
-- the Old Greek rides as the alternate tradition).
CREATE TABLE lxx_books(
  osis       TEXT PRIMARY KEY,     -- OSIS book code
  lxx_order  INTEGER,
  name       TEXT,
  mt_book_id INTEGER,              -- -> books.book_id, by convention
  tradition  TEXT,
  note       TEXT
);

CREATE TABLE lxx_verses(
  verse_id INTEGER PRIMARY KEY,    -- LXX-side verse id space
  osis     TEXT,                   -- -> lxx_books.osis, by convention
  chapter  INTEGER,
  verse    INTEGER,
  text     TEXT
);
CREATE INDEX idx_lxx_verses_ref ON lxx_verses(osis, chapter, verse);  -- (*) PG lacks

CREATE TABLE lxx_words(
  verse_id  INTEGER NOT NULL,      -- -> lxx_verses.verse_id, by convention
  position  INTEGER NOT NULL,
  surface   TEXT,
  lemma     TEXT,
  strongs   TEXT,                  -- G-number where assigned (93.3% of words)
  gloss     TEXT,
  bol_gloss TEXT,
  translit  TEXT,
  sp        TEXT,                  -- speech part
  morph     TEXT,
  ps        TEXT,                  -- person
  gn        TEXT,                  -- gender
  nu        TEXT,                  -- number
  tense     TEXT,
  mood      TEXT,
  voice     TEXT,
  case_     TEXT,
  degree    TEXT,
  PRIMARY KEY(verse_id, position)
);
CREATE INDEX idx_lxx_words_strongs ON lxx_words(strongs);  -- (*) PG lacks
CREATE INDEX idx_lxx_words_lemma ON lxx_words(lemma);      -- (*) PG lacks

-- MT <-> LXX verse mapping (numbering-v1: same / mt_only / lxx_only).
CREATE TABLE lxx_crosswalk(
  mt_verse_id  INTEGER,            -- -> verses.verse_id, by convention
  lxx_verse_id INTEGER,            -- -> lxx_verses.verse_id, by convention
  osis         TEXT,
  relation     TEXT,
  basis        TEXT,
  PRIMARY KEY(osis, relation, mt_verse_id, lxx_verse_id)  -- not carried into PG
);

-- Greek NT, Textus Receptus (primary Greek text; built by build_nt.py,
-- bridge by build_nt_align.py). Robinson pipe-variant parsing caveat:
-- 261 variant groups in the source are not yet modeled here.
CREATE TABLE gnt_books(
  book_id INTEGER PRIMARY KEY,
  code    TEXT,
  name    TEXT,
  note    TEXT
);

CREATE TABLE gnt_verses(
  gnt_verse_id    INTEGER PRIMARY KEY,
  corpus_verse_id INTEGER,         -- -> verses.verse_id, by convention
  book_id         INTEGER,         -- -> gnt_books.book_id, by convention
  chapter         INTEGER,
  verse           INTEGER,
  text            TEXT
);
CREATE INDEX idx_gnt_verses_ref ON gnt_verses(book_id, chapter, verse);  -- (*) PG lacks

CREATE TABLE gnt_words(
  gnt_verse_id INTEGER NOT NULL,   -- -> gnt_verses.gnt_verse_id, by convention
  position     INTEGER NOT NULL,
  surface      TEXT,
  beta         TEXT,               -- beta-code form
  strongs      TEXT,
  strongs_aux  TEXT,
  morph        TEXT,               -- Robinson morphology code
  PRIMARY KEY(gnt_verse_id, position)
);
CREATE INDEX idx_gnt_words_strongs ON gnt_words(strongs);  -- (*) PG lacks

CREATE TABLE gnt_alignment(
  corpus_verse_id INTEGER NOT NULL,
  kjv_pos         INTEGER NOT NULL,
  gnt_position    INTEGER NOT NULL,
  PRIMARY KEY(corpus_verse_id, kjv_pos, gnt_position)
);

CREATE TABLE gnt_ylt_renderings(
  gnt_verse_id INTEGER NOT NULL,
  gnt_position INTEGER NOT NULL,
  ylt_word     TEXT,
  ylt_word_pos INTEGER NOT NULL,
  label        TEXT,
  PRIMARY KEY(gnt_verse_id, gnt_position, ylt_word_pos)
);

-- Per-verse tradition comparison summary vs TR (build_gnt_variants.py).
CREATE TABLE gnt_variants(
  corpus_verse_id INTEGER,
  tradition       TEXT,            -- byzantine | sblgnt
  status          TEXT,
  basis           TEXT,
  detail          TEXT
);
CREATE INDEX idx_gntvar ON gnt_variants(corpus_verse_id, tradition);  -- (*) PG lacks

-- Greek NT, Byzantine / Robinson-Pierpont (built by build_gnt_variants.py,
-- bridge by build_gntb_bridge.py). Mirrors the TR shape minus beta/aux.
CREATE TABLE gntb_books(
  book_id INTEGER PRIMARY KEY,
  code    TEXT,
  name    TEXT,
  note    TEXT
);

CREATE TABLE gntb_verses(
  gnt_verse_id    INTEGER PRIMARY KEY,
  corpus_verse_id INTEGER,
  book_id         INTEGER,
  chapter         INTEGER,
  verse           INTEGER,
  text            TEXT
);
CREATE INDEX idx_gntb_ref ON gntb_verses(book_id, chapter, verse);  -- (*) PG lacks

CREATE TABLE gntb_words(
  gnt_verse_id INTEGER NOT NULL,
  position     INTEGER NOT NULL,
  surface      TEXT,
  strongs      TEXT,
  morph        TEXT,
  PRIMARY KEY(gnt_verse_id, position)
);

CREATE TABLE gntb_alignment(      -- no PK in either store (see header)
  corpus_verse_id INTEGER,
  kjv_pos         INTEGER,
  gntb_position   INTEGER
);

CREATE TABLE gntb_ylt_renderings(  -- no PK in either store (see header)
  gntb_verse_id INTEGER,
  gntb_position INTEGER,
  ylt_word      TEXT,
  ylt_word_pos  INTEGER,
  label         TEXT
);

-- Greek NT, SBLGNT / MorphGNT (built by build_gnt_variants.py, bridge by
-- build_gnts_bridge.py). Words carry lemma + normalized form instead of
-- a Strong's number, per MorphGNT.
CREATE TABLE gnts_books(
  book_id INTEGER PRIMARY KEY,
  code    TEXT,
  name    TEXT,
  note    TEXT
);

CREATE TABLE gnts_verses(
  gnt_verse_id    INTEGER PRIMARY KEY,
  corpus_verse_id INTEGER,
  book_id         INTEGER,
  chapter         INTEGER,
  verse           INTEGER,
  text            TEXT
);
CREATE INDEX idx_gnts_ref ON gnts_verses(book_id, chapter, verse);  -- (*) PG lacks

CREATE TABLE gnts_words(
  gnt_verse_id INTEGER NOT NULL,
  position     INTEGER NOT NULL,
  surface      TEXT,
  norm         TEXT,
  lemma        TEXT,
  morph        TEXT,
  PRIMARY KEY(gnt_verse_id, position)
);

CREATE TABLE gnts_alignment(       -- no PK in either store (see header)
  corpus_verse_id INTEGER,
  kjv_pos         INTEGER,
  gnts_position   INTEGER
);

CREATE TABLE gnts_ylt_renderings(  -- no PK in either store (see header)
  gnts_verse_id INTEGER,
  gnts_position INTEGER,
  ylt_word      TEXT,
  ylt_word_pos  INTEGER,
  label         TEXT
);

-- Witness apparatus (Peshitta-first; built by build_notes_syr.py and the
-- witness loaders). Text columns are per-witness by convention: text_syr
-- holds the witness's text (Syriac for the Peshitta rows).
CREATE TABLE witness_verses(
  verse_id      INTEGER NOT NULL REFERENCES verses(verse_id),
  witness       TEXT NOT NULL,     -- peshitta | ...
  words         INTEGER NOT NULL,  -- word count of the witness text
  text_syr      TEXT,
  text_translit TEXT,
  PRIMARY KEY(verse_id, witness)
);

CREATE TABLE verse_notes(
  verse_id   INTEGER NOT NULL REFERENCES verses(verse_id),
  witness    TEXT NOT NULL,
  note_kind  TEXT NOT NULL,        -- e.g. no_counterpart
  note_text  TEXT NOT NULL,
  basis      TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY(verse_id, witness, note_kind)
);
