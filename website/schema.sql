-- website/app.db schema -- user and translation data only.
-- bible.db (corpus) is opened READ-ONLY; all writes go here.
-- word_id is a logical cross-database reference to bible.db.words(word_id),
-- enforced by application code (SQLite cannot enforce cross-db FKs).

CREATE TABLE app_user(
  user_id    INTEGER PRIMARY KEY,
  name       TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE translation(
  translation_id INTEGER PRIMARY KEY,
  user_id        INTEGER NOT NULL REFERENCES app_user(user_id),
  name           TEXT NOT NULL,
  description    TEXT NOT NULL DEFAULT '',
  created_at     TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at     TEXT NOT NULL DEFAULT (datetime('now')),
  -- owner of the translation (2026-09-30): the logged-in user_accounts row
  -- that created it. NULL = legacy/anonymous translation (pre-accounts).
  owner_id       INTEGER REFERENCES user_accounts(user_id) ON DELETE SET NULL
);
CREATE INDEX idx_translation_user ON translation(user_id);

-- Per-word choices are NOT rows here. Each translation gets a flat file
-- website/user_data/translation_<id>.choices: 264,217 bytes, one byte per word,
-- byte at offset (word_id - 1). The byte is the item number of the word's
-- drop-down that was selected: 0 = default (no choice); the rest index into
-- the word's drop-down list built as [KJV renderings | Young's renderings |
-- this translation's Other options]. "Other" is multi-value: each custom
-- rendering the user adds becomes a row below and a new drop-down item.
CREATE TABLE other_option(
  option_id     INTEGER PRIMARY KEY,
  translation_id INTEGER NOT NULL REFERENCES translation(translation_id)
    ON DELETE CASCADE,
  idx           INTEGER NOT NULL,  -- 1-based creation order within the translation
  text          TEXT NOT NULL,
  created_at    TEXT NOT NULL DEFAULT (datetime('now')),
  UNIQUE(translation_id, idx)
);
CREATE INDEX idx_other_translation ON other_option(translation_id);

-- Sticky/propagating choices (2026-09-30): when a non-default choice is
-- saved for a word, the chosen rendering ALSO becomes the lemma default for
-- that word's lemma (keyed by Strong's number, falling back to the word's
-- root_code when Strong's is NULL) from that word_id FORWARD. When rendering
-- any later occurrence of the same lemma with no explicit per-word choice
-- (choices byte = 0), the lemma default's rendering is used if it appears in
-- that word's drop-down. An explicit per-word choice (byte != 0) always
-- wins; resetting one word to default (byte 0) does NOT clear the lemma
-- default — the word then follows the lemma default. Rendering TEXT is
-- stored (not the drop-down index) because drop-downs are built per
-- root_code and different inflections of one lemma have different lists.
CREATE TABLE lemma_default(
  translation_id INTEGER NOT NULL REFERENCES translation(translation_id)
    ON DELETE CASCADE,
  lemma          TEXT NOT NULL,  -- Strong's (e.g. 'H7225') or 'root:<root_code>'
  rendering      TEXT NOT NULL,  -- chosen rendering text
  from_word_id   INTEGER NOT NULL,  -- applies to word_id >= this
  -- Kit's translation-source integer (2026-09-30): 1=KJV, 2=Young's,
  -- 3=user-defined. For source=3 the rendering links to other_option:
  -- other_option_id points at the translation's Other row holding the text.
  source         INTEGER,       -- 1 | 2 | 3, NULL = default/unknown
  other_option_id INTEGER REFERENCES other_option(option_id) ON DELETE SET NULL,
  PRIMARY KEY(translation_id, lemma)
);

-- User accounts (2026-09-30): real logins. Kept separate from app_user on
-- purpose: app_user rows are anonymous browser sessions; user_accounts holds
-- salted password hashes (werkzeug/argon2-bcrypt via generate_password_hash,
-- NEVER cleartext). translation.owner_id links a translation to its owner;
-- translation.user_id keeps its legacy app_user meaning for old rows.
CREATE TABLE IF NOT EXISTS user_accounts(
  user_id       INTEGER PRIMARY KEY AUTOINCREMENT,
  username      TEXT NOT NULL UNIQUE,
  password_hash TEXT NOT NULL,
  email         TEXT,
  display_name  TEXT,
  is_active     INTEGER NOT NULL DEFAULT 1,
  created_at    TEXT NOT NULL DEFAULT (datetime('now')),
  last_login_at TEXT
);
