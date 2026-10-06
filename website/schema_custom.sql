-- ============================================================================
-- Bible project — user accounts + custom per-word translations (PROPOSAL)
-- File: website/schema_custom.sql
-- Status: DESIGN ONLY — do NOT apply to the live DB without Kit's approval.
-- The corpus DB (bible_v2.db) stays read-only; these tables live in the
-- app database (website/app.db), which already holds app_user, translation,
-- and other_option for the translation-builder.
-- ============================================================================

-- ----------------------------------------------------------------------------
-- user_accounts
-- Who can log in. Passwords are NEVER stored in cleartext: password_hash holds
-- a salted hash (bcrypt/argon2, e.g. via Python passlib) generated at signup.
-- Kept separate from the existing app_user table on purpose: app_user rows are
-- anonymous browser sessions today; user_accounts is for real logins. A future
-- migration can link app_user.session -> user_accounts.user_id.
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS user_accounts (
    user_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT NOT NULL UNIQUE,          -- login name, case-insensitive compare in app
    password_hash TEXT NOT NULL,                -- bcrypt/argon2 hash, never cleartext
    email         TEXT,                          -- optional; for password reset
    display_name  TEXT,                          -- shown in UI; defaults to username
    is_active     INTEGER NOT NULL DEFAULT 1,    -- 0 = disabled (soft delete)
    created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_user_accounts_username
    ON user_accounts(username);
CREATE INDEX IF NOT EXISTS idx_user_accounts_email
    ON user_accounts(email);

-- ----------------------------------------------------------------------------
-- custom_translations
-- One row per (user, word): the user's chosen variant + translation for that
-- Hebrew word. This is the persistent backing store for the two dropdowns in
-- the word-level UI wireframe (website/wireframe-word-ui.html).
--
-- Design decisions:
-- 1. Grain is (user_id, word_id) — one choice-set per word per user. A word's
--    full state (which variant, which translation source, custom text) lives
--    in ONE row so the UI can load/save it atomically.
-- 2. variant_seq is NULLABLE: NULL means "corpus default" (no variant chosen).
--    When set, it references word_variants(word_id, variant_seq). We do NOT
--    declare a formal FK to the corpus DB because word_variants lives in
--    bible_v2.db (read-only corpus) while this table lives in app.db — SQLite
--    cannot enforce cross-database FKs. The app validates on write.
-- 3. translation_source is a CHECK-constrained enum: 'kjv' | 'ylt' |
--    'computed' | 'custom'. The *_index columns record WHICH item inside the
--    chosen group (e.g. kjv item #2 of 3 for that word); custom_text holds the
--    user's free text and is required when source='custom'.
-- 4. updated_at bumps on every save (UPSERT) so "recently edited" views and
--    sync can order by recency.
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS custom_translations (
    user_id            INTEGER NOT NULL,
    word_id            INTEGER NOT NULL,          -- words.word_id in the corpus DB
    variant_seq        INTEGER,                   -- word_variants.variant_seq, NULL = corpus default
    translation_source TEXT NOT NULL
        CHECK (translation_source IN ('kjv', 'ylt', 'computed', 'custom')),
    source_index       INTEGER,                   -- item # within the chosen source group
    custom_text        TEXT,                      -- required when source='custom'
    updated_at         TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, word_id),
    FOREIGN KEY (user_id) REFERENCES user_accounts(user_id) ON DELETE CASCADE,
    CHECK (
        (translation_source = 'custom' AND custom_text IS NOT NULL AND length(custom_text) > 0)
        OR (translation_source != 'custom')
    )
);
CREATE INDEX IF NOT EXISTS idx_custom_translations_user
    ON custom_translations(user_id);
CREATE INDEX IF NOT EXISTS idx_custom_translations_word
    ON custom_translations(word_id);

-- ----------------------------------------------------------------------------
-- Companion view (optional): one row per user per verse with a completeness
-- count, useful for a "my progress" page. Uncomment if wanted.
-- ----------------------------------------------------------------------------
-- CREATE VIEW IF NOT EXISTS user_verse_progress AS
-- SELECT ct.user_id, w2.verse_id, COUNT(*) AS words_customized
-- FROM custom_translations ct
-- -- words lives in the corpus DB; this view only works if the corpus tables
-- -- are ATTACHed. Otherwise compute progress in the app.
-- GROUP BY ct.user_id, w2.verse_id;
