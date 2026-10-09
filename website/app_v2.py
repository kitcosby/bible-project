#!/usr/bin/env python3
"""Bible translation-builder website — v2 corpus port.

Faithful port of app.py (v1) to the normalized bible_v2.db corpus.
Behavior preserved exactly:
- bible_v2.db opened READ-ONLY (corpus).
- website/app.db holds app_user, translation, other_option (unchanged schema).
- Per-word choices: website/user_data/translation_<id>.choices, 264,217
  bytes, ONE BYTE PER WORD at offset (word_id - 1); the byte is the item
  number of the word's drop-down, rebuilt identically on every call as
  [KJV renderings | Young's-computed renderings | this translation's Other
  options]. word_id values are stable across the v1->v2 migration.
- Routes, forms, redirects, export format, and choice-file format unchanged.

What changed vs app.py:
- Queries read the normalized v2 tables (verses, root_form, morph_patterns/
  morph_segments, strongs_sources, lexicon_* child tables) instead of the
  v1 flat columns and ' | '/' ‖ ' blobs. Child-table row order preserves the
  v1 blob item order, so drop-downs render identically.
- Mount-prefix aware: every link/form/redirect goes through u(), driven by
  the WSGI SCRIPT_NAME (set by PrefixMiddleware from the X-Script-Name
  header Apache sends, or an explicit SCRIPT_NAME). This fixes the /bible
  "Books" link bug the v1 app has live.
- word detail additionally shows the parsed morphology segments and glosses,
  which only exist because of normalization; YLT contexts and found verses
  render from their child tables with resolved verse references.
"""
import html
import os
import psycopg2
import psycopg2.extras
import psycopg2.errors
from flask import Flask, request, redirect, render_template_string, Response, g, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash

BASE = os.path.dirname(os.path.abspath(__file__))
# PostgreSQL databases on the lampy distro (Kit 2026-10-09): the website
# now reads from PG instead of SQLite so it can be administered via the
# Lampy admin tool. BIBLE_DB/APP_DB env vars are kept for override.
PG_HOST = os.environ.get('PG_HOST', '/tmp')
PG_USER = os.environ.get('PG_USER', 'postgres')
BIBLE_DB = os.environ.get('BIBLE_DB', 'bible')
APP_DB = os.environ.get('APP_DB', 'bible_app')
SCHEMA = os.path.join(BASE, 'schema.sql')

app = Flask(__name__)


def _load_secret():
    """Flask session secret, generated once and kept next to app.db so
    logins survive restarts."""
    p = os.path.join(os.path.dirname(APP_DB), 'secret.key')
    if os.path.exists(p):
        with open(p, 'rb') as f:
            return f.read()
    key = os.urandom(32)
    try:
        with open(p, 'wb') as f:
            f.write(key)
    except OSError:
        pass
    return key


app.secret_key = _load_secret()

# ---------------------------------------------------------------- mount prefix
class PrefixMiddleware:
    """Honor the mount point Apache serves us under. Apache sets
    X-Script-Name (RequestHeader set X-Script-Name /bible); explicit
    SCRIPT_NAME env wins when set (local dev / staging)."""
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app
    def __call__(self, environ, start_response):
        prefix = (os.environ.get('SCRIPT_NAME')
                  or environ.get('HTTP_X_SCRIPT_NAME', ''))
        environ['SCRIPT_NAME'] = prefix.rstrip('/')
        return self.wsgi_app(environ, start_response)

app.wsgi_app = PrefixMiddleware(app.wsgi_app)

def u(path):
    """Prefix-aware URL: '/verse/1/1/1' -> '/bible/verse/1/1/1' under /bible."""
    root = (request.script_root or '').rstrip('/')
    return root + path

# ---------------------------------------------------------------- databases
class PGWrapper:
    """Thin wrapper around a psycopg2 connection mimicking the sqlite3
    connection API used throughout the app: .execute() returns a
    RealDictCursor, plus .commit(), .rollback(), .close()."""
    def __init__(self, con):
        self._con = con
    def execute(self, *a, **kw):
        cur = self._con.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(*a, **kw)
        return cur
    def commit(self):
        self._con.commit()
    def rollback(self):
        self._con.rollback()
    def close(self):
        self._con.close()

def bible():
    """Read-only corpus database (PostgreSQL `bible`). Uses RealDictCursor
    so row['col'] access works as before. Kit 2026-10-01's fold_finals is
    now a native PL/pgSQL function in the database."""
    if 'bible' not in g:
        con = psycopg2.connect(dbname=BIBLE_DB, host=PG_HOST, user=PG_USER)
        g.bible = PGWrapper(con)
    return g.bible

def appdb():
    """Application database (PostgreSQL `bible_app`): user accounts,
    translations, lemma defaults, reading positions."""
    if 'appdb' not in g:
        con = psycopg2.connect(dbname=APP_DB, host=PG_HOST, user=PG_USER)
        db = PGWrapper(con)
        # migration: lemma defaults for sticky choices (2026-09-30);
        # idempotent so existing databases pick it up.
        db.execute('''CREATE TABLE IF NOT EXISTS lemma_default(
            translation_id INTEGER NOT NULL, lemma TEXT NOT NULL,
            rendering TEXT NOT NULL, from_word_id INTEGER NOT NULL,
            PRIMARY KEY(translation_id, lemma))''')
        # migration (2026-09-30, Kit): user accounts + translation-source
        # tracking (1=KJV, 2=Young's, 3=user-defined) + translation owners.
        # PG: AUTOINCREMENT -> SERIAL; datetime('now') -> CURRENT_TIMESTAMP.
        db.execute('''CREATE TABLE IF NOT EXISTS user_accounts(
            user_id SERIAL PRIMARY KEY,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            email TEXT,
            display_name TEXT,
            is_active INTEGER NOT NULL DEFAULT 1,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            last_login_at TIMESTAMP)''')
        for ddl in (
            'ALTER TABLE lemma_default ADD COLUMN source INTEGER',
            'ALTER TABLE lemma_default ADD COLUMN other_option_id INTEGER',
            'ALTER TABLE translation ADD COLUMN owner_id INTEGER',
        ):
            try:
                db.execute(ddl)
            except psycopg2.Error:
                db.rollback()  # already migrated; clear the failed txn
        # migration (2026-10-08, Kit): per-user daily-reading position for
        # the Read door's "continue where you left off".
        db.execute('''CREATE TABLE IF NOT EXISTS reading_position(
            user_id INTEGER PRIMARY KEY,
            book_id INTEGER NOT NULL,
            chapter INTEGER NOT NULL,
            translation_id INTEGER NOT NULL,
            updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP)''')
        # base app tables from schema.sql if the database is fresh
        db.execute('''CREATE TABLE IF NOT EXISTS app_user(
            user_id SERIAL PRIMARY KEY, name TEXT NOT NULL)''')
        db.execute('''CREATE TABLE IF NOT EXISTS translation(
            translation_id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES app_user(user_id),
            name TEXT NOT NULL, description TEXT NOT NULL DEFAULT '',
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            owner_id INTEGER REFERENCES user_accounts(user_id) ON DELETE SET NULL)''')
        db.execute('''CREATE TABLE IF NOT EXISTS other_option(
            option_id SERIAL PRIMARY KEY,
            translation_id INTEGER NOT NULL REFERENCES translation(translation_id),
            idx INTEGER NOT NULL, text TEXT NOT NULL)''')
        db.commit()
        g.appdb = db
        _backfill_lemma_source(db)
    return g.appdb

@app.teardown_appcontext
def close_dbs(exc):
    for k in ('bible', 'appdb'):
        con = g.pop(k, None)
        if con is not None:
            con.close()

# ---------------------------------------------------------------- helpers
def book_name(n):
    r = bible().execute('SELECT name_en FROM books WHERE book_id=%s', (n,)).fetchone()
    return r['name_en'] if r else f'Book {n}'

def current_translation():
    tid = request.args.get('t')
    if tid and tid.isdigit():
        r = appdb().execute('SELECT * FROM translation WHERE translation_id=%s', (tid,)).fetchone()
        if r:
            return r
    return None


# ---------------------------------------------------------------- user accounts
def current_user():
    uid = session.get('user_id')
    if not uid:
        return None
    return appdb().execute(
        'SELECT * FROM user_accounts WHERE user_id=%s AND is_active=1',
        (uid,)).fetchone()


def _auth_form(action, legend):
    return f'''<h2>{legend}</h2>
<form method="post" action="{u(action)}">
<label>Username: <input type="text" name="username"></label><br>
<label>Password: <input type="password" name="password"></label><br>
<button type="submit">{legend}</button></form>'''


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        db = appdb()
        if not username or not password:
            return render('Sign up',
                          '<p>Username and password are required.</p>'
                          + _auth_form('/signup', 'Sign up'))
        if len(password) < 4:
            return render('Sign up',
                          '<p>Password must be at least 4 characters.</p>'
                          + _auth_form('/signup', 'Sign up'))
        try:
            cur = db.execute(
                'INSERT INTO user_accounts(username, password_hash, display_name)'
                ' VALUES(%s,%s,%s) RETURNING user_id',
                (username, generate_password_hash(password), username))
            new_uid = cur.fetchone()['user_id']
            db.commit()
        except psycopg2.IntegrityError:
            db.rollback()
            return render('Sign up',
                          '<p>That username is taken.</p>'
                          + _auth_form('/signup', 'Sign up'))
        session['user_id'] = new_uid
        db.execute("UPDATE user_accounts SET last_login_at=now()"
                   ' WHERE user_id=%s', (new_uid,))
        db.commit()
        return redirect(u('/'))
    return render('Sign up', _auth_form('/signup', 'Sign up'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        db = appdb()
        row = db.execute(
            'SELECT * FROM user_accounts WHERE username=%s AND is_active=1',
            (username,)).fetchone()
        if not row or not check_password_hash(row['password_hash'], password):
            return render('Login',
                          '<p>Incorrect username or password.</p>'
                          + _auth_form('/login', 'Login'))
        session['user_id'] = row['user_id']
        db.execute("UPDATE user_accounts SET last_login_at=now()"
                   ' WHERE user_id=%s', (row['user_id'],))
        db.commit()
        return redirect(u('/'))
    return render('Login', _auth_form('/login', 'Login'))


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(u('/'))

# ---------------------------------------------------------------- choice index: 1 byte per word
# website/user_data/translation_<id>.choices: 264,217 bytes, byte at offset
# (word_id - 1). The byte is the item number of the word's drop-down that was
# selected: 0 = default (no choice); the rest index into dropdown_items(),
# rebuilt identically on every call as [KJV renderings | Young's-computed
# renderings | this translation's Other options].
N_WORDS = 264217
USER_DATA = os.environ.get('USER_DIR', os.path.join(BASE, 'user_data'))
MAX_ITEMS = 255    # must fit in one byte
MAX_OTHERS = 230   # headroom so KJV + Young's items always fit in the byte

def choices_path(tid):
    return os.path.join(USER_DATA, f'translation_{tid}.choices')

def read_choices(tid):
    """Whole choice file as a mutable bytearray (zeros = all default)."""
    p = choices_path(tid)
    if not os.path.exists(p):
        return bytearray(N_WORDS)
    with open(p, 'rb') as f:
        data = f.read()
    if len(data) < N_WORDS:
        data += b'\x00' * (N_WORDS - len(data))
    return bytearray(data[:N_WORDS])

def write_choice(tid, word_id, val):
    os.makedirs(USER_DATA, exist_ok=True)
    p = choices_path(tid)
    if not os.path.exists(p):
        with open(p, 'wb') as f:
            f.write(b'\x00' * N_WORDS)
    with open(p, 'r+b') as f:
        f.seek(word_id - 1)
        f.write(bytes([val & 0xFF]))

def other_options(tid):
    return appdb().execute(
        'SELECT * FROM other_option WHERE translation_id=%s ORDER BY idx', (tid,)).fetchall()

# ---------------------------------------------------------------- lexicon child tables (cached)
_LEX_CACHE = {}
def lex_renderings():
    """(kjv_map, ylt_map): (root_id, root_form_seq, vowel_seq) -> ordered
    rendering lists. Cached per corpus path; the corpus is read-only so the
    cache never goes stale. Row order matches the v1 blob item order."""
    if BIBLE_DB not in _LEX_CACHE:
        kjv, ylt = {}, {}
        db = bible()
        for rid, fs, vs, t in db.execute(
                'SELECT root_id, root_form_seq, vowel_seq, rendering'
                ' FROM lexicon_kjv_rendering'
                ' ORDER BY root_id, root_form_seq, vowel_seq, seq'):
            kjv.setdefault((rid, fs, vs), []).append(t)
        for rid, fs, vs, t in db.execute(
                'SELECT root_id, root_form_seq, vowel_seq, rendering'
                ' FROM lexicon_ylt_rendering'
                ' ORDER BY root_id, root_form_seq, vowel_seq, seq'):
            ylt.setdefault((rid, fs, vs), []).append(t)
        _LEX_CACHE[BIBLE_DB] = (kjv, ylt)
    return _LEX_CACHE[BIBLE_DB]

# ---------------------------------------------------------------- per-occurrence translation phrases
# Kit 2026-10-01: a Hebrew word's KJV/Young's translation is often a
# multi-word phrase ("In the beginning"), and one lemma can have several
# distinct phrases across verses. The drop-down must offer each FULL phrase
# as ONE choice — never split a phrase into separate one-word lines (the
# old lexicon-fragment lists did exactly that, and the single-byte choice
# could not hold a multi-word translation as a unit). Storage is unchanged:
# one byte per word indexing into dropdown_items().
N_PHRASES = 12   # per-group cap, as the old lexicon lists
_PHRASE_CACHE = {}

def lemma_phrases(db=None):
    """(kjv_map, ylt_map, kjv_word, ylt_word). kjv_map/ylt_map: lemma_key ->
    [distinct phrases, most frequent first], built from the per-occurrence
    kjv_renderings/ylt_renderings tables (each occurrence's English words
    joined in order). kjv_word/ylt_word: word_id -> this occurrence's
    phrase (or missing). Cached per corpus path; the corpus is read-only so
    the cache never goes stale. Pass an explicit db to avoid needing the
    Flask request context (used by the QA driver)."""
    if BIBLE_DB not in _PHRASE_CACHE:
        db = db or bible()
        _PHRASE_CACHE[BIBLE_DB] = (
            _build_phrase_map(db, 'kjv_renderings', 'kjv_word', 'rendering_id')
            + _build_phrase_map(db, 'ylt_renderings', 'ylt_word', 'ylt_word_pos'))
    return _PHRASE_CACHE[BIBLE_DB]


def _build_phrase_map(db, table, wcol, poscol):
    """(lemma_map, word_map) for one renderings table."""
    from collections import defaultdict
    freq = defaultdict(lambda: defaultdict(int))
    word_phrase = {}
    cur_wid, cur, cur_key = None, [], None
    q = (f'SELECT w.word_id, w.strongs,'
         f' (w.root_id || \'.\' || w.root_form_seq || \'.\' || w.root_vowel_seq),'
         f' r.{wcol} FROM words w JOIN {table} r ON r.word_id=w.word_id'
         f' ORDER BY w.word_id, r.{poscol}')
    for wid, strongs, rc, txt in db.execute(q):
        if wid != cur_wid:
            if cur_wid is not None:
                phrase = ' '.join(cur)
                word_phrase[cur_wid] = phrase
                freq[cur_key][phrase] += 1
            cur_wid, cur = wid, []
            cur_key = strongs or ('root:' + (rc or ''))
        cur.append(txt or '')
    if cur_wid is not None:
        phrase = ' '.join(cur)
        word_phrase[cur_wid] = phrase
        freq[cur_key][phrase] += 1
    lemma_map = {k: sorted(v, key=lambda p: -v[p]) for k, v in freq.items()}
    return lemma_map, word_phrase


def _phrase_options(phrases, here, prefix):
    """This occurrence's phrase first, then the lemma's other phrases by
    frequency, capped — each a single one-line option."""
    ordered = ([here] if here else []) + [p for p in phrases if p != here]
    return [(f'{prefix}: {p}', p) for p in ordered[:N_PHRASES]]


def dropdown_items(w, others):
    """The word's drop-down list, built identically on every call. The list
    index IS the byte value stored in the choices file (0 = default).
    KJV/Young's groups hold the lemma's full phrases — one option per
    phrase, this occurrence's phrase first. Kit 2026-10-01: the old
    lexicon-fragment fallback (which split phrases like "In the beginning"
    into separate one-word lines) is removed — lemmas with no per-occurrence
    phrase data offer no KJV/Young's options rather than broken fragments."""
    kjv_lp, kjv_wp, ylt_lp, ylt_wp = lemma_phrases()
    lk = lemma_key(w)
    items = [('— default —', None)]
    kp = kjv_lp.get(lk)
    if kp:
        items.extend(_phrase_options(kp, kjv_wp.get(w['word_id']), 'KJV'))
    yp = ylt_lp.get(lk)
    if yp:
        items.extend(_phrase_options(yp, ylt_wp.get(w['word_id']), "Young's"))
    for o in others:
        items.append((f"Other: {o['text']}", o['text']))
    return items[:MAX_ITEMS]

# ---------------------------------------------------------------- v2 word queries
# (v2 words has no affix/base columns; they come from root_form/root_entry)
WORD_COLS = '''w.word_id, w.word_pos, w.pointed, w.unpointed, w.letters,
    rf.prefix1, rf.prefix2, rf.prefix3, e.root AS base_word, rf.suffix1, rf.suffix2,
    rf.prefix1_disp, rf.prefix2_disp, rf.prefix3_disp,
    rf.suffix1_disp, rf.suffix2_disp,
    w.strongs, ss.source AS strongs_source,
    m.pattern AS morph, m.parse_status AS morph_status,
    w.is_aramaic, w.root_id, w.root_form_seq, w.root_vowel_seq,
    (w.root_id || '.' || w.root_form_seq || '.' || w.root_vowel_seq) AS root_code,
    v.book_id, v.chapter, v.verse'''
WORD_JOINS = '''FROM words w
    JOIN verses v ON v.verse_id=w.verse_id
    JOIN root_entry e ON e.root_id=w.root_id
    JOIN root_form rf ON rf.root_id=w.root_id AND rf.form_seq=w.root_form_seq
    LEFT JOIN strongs_sources ss ON ss.source_id=w.strongs_source_id
    LEFT JOIN morph_patterns m ON m.pattern_id=w.morph_pattern_id'''

def word_with_lex(wid):
    return bible().execute(
        f'SELECT {WORD_COLS} {WORD_JOINS} WHERE w.word_id=%s', (wid,)).fetchone()

def resolve_choice(w, others, byte):
    """Byte -> chosen rendering text, or None for default/stale."""
    items = dropdown_items(w, others)
    if 0 < byte < len(items):
        return items[byte][1]
    return None

def lemma_key(w):
    """Identity a choice propagates under: Strong's number, else the
    word's root_code. (Same Strong's, different inflections, have
    different drop-downs — matching is by rendering text.)"""
    return w['strongs'] or ('root:' + str(w['root_code'] or ''))

def effective_item(tid, w, others, byte):
    """Drop-down index in effect for this word: the explicit per-word byte
    when set, else the translation's lemma default for this word's lemma
    (matched by rendering text against this word's own drop-down) when the
    word is at/after the default's from_word_id, else 0 (default)."""
    items = dropdown_items(w, others)
    if 0 < byte < len(items):
        return byte
    if tid:
        r = appdb().execute(
            'SELECT rendering, from_word_id FROM lemma_default'
            ' WHERE translation_id=%s AND lemma=%s', (tid, lemma_key(w))).fetchone()
        if r and w['word_id'] >= r['from_word_id']:
            for i in range(1, len(items)):
                if items[i][1] == r['rendering']:
                    return i
    return 0

def resolve_effective(tid, w, others, byte):
    """Effective choice -> rendering text, or None for default/stale."""
    items = dropdown_items(w, others)
    idx = effective_item(tid, w, others, byte)
    if 0 < idx < len(items):
        return items[idx][1]
    return None

# Kit's translation-source integer (2026-09-30): 1=KJV, 2=Young's,
# 3=user-defined. Source 3 renderings link to other_option (the user's
# custom-renderings table): lemma_default.other_option_id points at the row.
SRC_KJV, SRC_YLT, SRC_USER = 1, 2, 3


def _source_of(w, others, rendering):
    """Classify a rendering into Kit's source integer from the word's own
    drop-down groups: 1=KJV, 2=Young's (computed), 3=user-defined (Other).
    Checks the per-occurrence phrase lists first, then the lexicon fragment
    lists (for choices saved before the 2026-10-01 phrase change)."""
    if rendering is None:
        return None
    kjv_lp, _, ylt_lp, _ = lemma_phrases()
    lk = lemma_key(w)
    if rendering in kjv_lp.get(lk, []):
        return SRC_KJV
    if rendering in ylt_lp.get(lk, []):
        return SRC_YLT
    kjv_map, ylt_map = lex_renderings()
    key = (w['root_id'], w['root_form_seq'], w['root_vowel_seq'])
    if rendering in kjv_map.get(key, []):
        return SRC_KJV
    if rendering in ylt_map.get(key, []):
        return SRC_YLT
    if any(o['text'] == rendering for o in others):
        return SRC_USER
    return None


def _backfill_lemma_source(db):
    """One-time: fill source for lemma defaults saved before source
    tracking existed. Best-effort — skips silently on any error."""
    try:
        rows = db.execute(
            'SELECT translation_id, lemma, rendering, from_word_id'
            ' FROM lemma_default WHERE source IS NULL').fetchall()
        for r in rows:
            w = word_with_lex(r['from_word_id'])
            if not w:
                continue
            others = other_options(r['translation_id'])
            src = _source_of(w, others, r['rendering'])
            db.execute(
                'UPDATE lemma_default SET source=%s'
                ' WHERE translation_id=%s AND lemma=%s',
                (src, r['translation_id'], r['lemma']))
        db.commit()
    except Exception:
        pass


def record_lemma_default(tid, w, others, item, source=None, other_option_id=None):
    """A non-default choice becomes the new lemma default (forward-only)
    for the rest of the text for that word's lemma. Records Kit's
    translation-source integer (1=KJV, 2=Young's, 3=user-defined)."""
    items = dropdown_items(w, others)
    if 0 < item < len(items) and items[item][1]:
        if source is None:
            source = _source_of(w, others, items[item][1])
        appdb().execute(
            '''INSERT INTO lemma_default(translation_id, lemma, rendering,
                   from_word_id, source, other_option_id)
               VALUES(%s,%s,%s,%s,%s,%s)
               ON CONFLICT(translation_id, lemma) DO UPDATE SET
                 rendering=excluded.rendering,
                 from_word_id=excluded.from_word_id,
                 source=excluded.source,
                 other_option_id=excluded.other_option_id''',
            (tid, lemma_key(w), items[item][1], w['word_id'],
             source, other_option_id))

def morph_segments_html(wid):
    rows = bible().execute('''SELECT s.seq, s.code, s.pos_name, s.stem_name, s.conj_name,
        s.type_name, s.person_name, s.gender_name, s.number_name, s.state_name,
        m.parse_status
        FROM words w
        JOIN morph_patterns m ON m.pattern_id=w.morph_pattern_id
        JOIN morph_segments s ON s.pattern_id=m.pattern_id
        WHERE w.word_id=%s ORDER BY s.seq''', (wid,)).fetchall()
    if not rows:
        return ''
    if rows[0]['parse_status'] != 'parsed':
        return '<i>morphology pattern not parsed (see raw pattern above)</i>'
    out = ['<ul>']
    for r in rows:
        feats = [x for x in (r['stem_name'], r['conj_name'], r['type_name'],
                             r['person_name'], r['gender_name'],
                             r['number_name'], r['state_name']) if x]
        out.append(f'<li><b>{html.escape(r["pos_name"])}</b> '
                   f'({html.escape(r["code"])}): {html.escape(", ".join(feats))}</li>')
    out.append('</ul>')
    return ''.join(out)

NAV = '''
<div class="navbar">
<a href="{{u0}}/">Books</a>
 | <a href="{{u0}}/interlinear">Interlinear</a>
 | <a href="{{u0}}/variants">Word variants</a>
 | <a href="{{u0}}/translations">My translations</a>
{% if user %} | logged in as <b>{{user['display_name'] or user['username']}}</b>
 (<a href="{{u0}}/logout">logout</a>)
{% else %} | <a href="{{u0}}/login">login</a> | <a href="{{u0}}/signup">sign up</a>{% endif %}
{% if trans %} | working on translation: <b>{{trans['name']}}</b>
  (<a href="{{u0}}/translations?t={{trans['translation_id']}}">switch</a>){% endif %}
</div>'''

PAGE = '''<!doctype html><html><head><meta charset="utf-8">
<title>{{title}}</title>
<style>
body{font-family:Georgia,serif;max-width:900px;margin:0 auto;padding:12px;line-height:1.5;color:#2a1f0d;background-color:#e8d5a3;background-image:url("{{tile}}");background-repeat:repeat}
.navbar{margin:10px 0;padding:8px 12px;background:rgba(238,238,255,.9);border:1px solid #b89b5e;border-radius:8px;box-shadow:0 2px 6px rgba(90,60,10,.15)}
.heb{direction:rtl;font-size:1.6em}
.wordbox{border:1px solid #b89b5e;margin:8px 0;padding:8px;background:rgba(255,252,240,.88);border-radius:8px;box-shadow:0 2px 6px rgba(90,60,10,.15)}
select,input[type=text]{font-size:1em;max-width:220px}
.saved{color:green;font-size:.9em}
table{border-collapse:collapse;background:rgba(255,252,240,.88)} td,th{border:1px solid #b89b5e;padding:4px 8px}
.dim{color:#777}
h1{color:#2a1f0d}
a{color:#5a3c0a}
</style></head><body>''' + NAV + '''
<h1>{{title}}</h1>
{{body|safe}}
</body></html>'''

def render(title, body, trans=None):
    return render_template_string(PAGE, title=title, body=body, trans=trans,
                                   user=current_user(),
                                   u0=request.script_root or '',
                                   tile=u('/papyrus-tile.png'))

# ---------------------------------------------------------------- routes
# ---------------------------------------------------------------- two doors
# Kit 2026-10-08: the Bible website opens with two doors — Study (the
# interlinear, brought forward) and Read (clean daily reading). The old
# book index moves to /books.

DOORS_CSS = '''
.doors{display:flex;gap:24px;flex-wrap:wrap;margin:32px 0}
.door{flex:1;min-width:260px;background:rgba(255,252,240,.92);border:2px solid #b89b5e;
border-radius:12px;padding:32px 24px;text-align:center;box-shadow:0 4px 12px rgba(90,60,10,.2);
text-decoration:none;color:#2a1f0d;display:block}
.door:hover{border-color:#5a3c0a;box-shadow:0 6px 18px rgba(90,60,10,.3)}
.door h2{margin:0 0 12px 0;font-size:1.8em;color:#5a3c0a}
.door p{margin:0;color:#5a4a2a;font-size:1.05em;line-height:1.6}
.door .heb{font-size:2em;display:block;margin-bottom:12px}
.continue{margin:24px 0;padding:16px;background:rgba(255,252,240,.92);border:1px solid #b89b5e;
border-radius:8px;text-align:center}
'''

def get_reading_position():
    """(book_id, chapter, translation_id) or None. Per-user in appdb;
    anonymous users get session storage."""
    u = current_user()
    if u:
        r = appdb().execute(
            'SELECT book_id, chapter, translation_id FROM reading_position WHERE user_id=%s',
            (u['user_id'],)).fetchone()
        if r:
            return (r['book_id'], r['chapter'], r['translation_id'])
    return tuple(session.get('reading_position', ())) or None

def save_reading_position(n, c, tid):
    u = current_user()
    if u:
        appdb().execute('''INSERT INTO reading_position (user_id, book_id, chapter, translation_id, updated)
            VALUES (%s,%s,%s,%s,now())
            ON CONFLICT(user_id) DO UPDATE SET book_id=excluded.book_id, chapter=excluded.chapter,
            translation_id=excluded.translation_id, updated=excluded.updated''',
            (u['user_id'], n, c, tid))
        appdb().commit()
    else:
        session['reading_position'] = [n, c, tid]

@app.route('/')
def index():
    pos = get_reading_position()
    cont = ''
    if pos:
        n, c, tid = pos
        cont = (f'<div class="continue">Continue reading: '
                f'<a href="{u("/read/" + str(n) + "/" + str(c) + "?t=" + str(tid))}">'
                f'{html.escape(book_name(n))} {c}</a></div>')
    body = f'''<style>{DOORS_CSS}</style>
{cont}
<div class="doors">
<a class="door" href="{u("/interlinear")}">
<span class="heb">למד</span>
<h2>Study</h2>
<p>The interlinear — every Hebrew word with its variants and translation
choices, word details, and cross-references. For deep digging.</p>
</a>
<a class="door" href="{u("/read")}">
<span class="heb">קרא</span>
<h2>Read</h2>
<p>Clean, quiet English for daily reading. Pick up where you left off,
chapter by chapter, nothing between you and the text.</p>
</a>
</div>
<p style="text-align:center"><a href="{u("/books")}">Browse all books</a> |
<a href="{u("/variants")}">Word variants</a> |
<a href="{u("/translations")}">My translations</a></p>'''
    return render('Hebrew Bible', body, current_translation())

@app.route('/books')
def books():
    books = bible().execute('SELECT book_id, name_en, name_he FROM books ORDER BY book_id').fetchall()
    items = ''.join(
        f'<li><a href="{u("/book/" + str(b["book_id"]))}">{html.escape(b["name_en"])}</a> '
        f'<span class="heb">{b["name_he"]}</span></li>'
        for b in books)
    body = (f'<ul>{items}</ul><p><a href="{u("/interlinear")}">Interlinear</a> | '
            f'<a href="{u("/variants")}">Word variants</a> | '
            f'<a href="{u("/translations")}">My translations</a></p>')
    return render('Hebrew Bible — books', body, current_translation())

@app.route('/book/<int:n>')
def book(n):
    trans = current_translation()
    chaps = bible().execute('''SELECT DISTINCT v.chapter FROM verses v
        WHERE v.book_id=%s AND EXISTS (SELECT 1 FROM words w WHERE w.verse_id=v.verse_id)
        ORDER BY v.chapter''', (n,)).fetchall()
    items = ''.join(f'<li><a href="{u("/chapter/" + str(n) + "/" + str(c["chapter"]) + tqs(trans))}">'
                    f'Chapter {c["chapter"]}</a></li>' for c in chaps)
    return render(f'{book_name(n)} — chapters', f'<ul>{items}</ul>', trans)

def tqs(trans):
    return '?t=' + str(trans['translation_id']) if trans else ''

@app.route('/chapter/<int:n>/<int:c>')
def chapter(n, c):
    trans = current_translation()
    verses = bible().execute('''SELECT v.verse FROM verses v
        WHERE v.book_id=%s AND v.chapter=%s AND EXISTS (SELECT 1 FROM words w WHERE w.verse_id=v.verse_id)
        ORDER BY v.verse''', (n, c)).fetchall()
    items = ''.join(
        f'<li><a href="{u("/verse/" + str(n) + "/" + str(c) + "/" + str(v["verse"]) + tqs(trans))}">Verse {v["verse"]}</a></li>'
        for v in verses)
    return render(f'{book_name(n)} {c} — verses', f'<ul>{items}</ul>', trans)

@app.route('/verse/<int:n>/<int:c>/<int:v>')
def verse(n, c, v):
    trans = current_translation()
    b = bible()
    words = b.execute(f'''SELECT {WORD_COLS} {WORD_JOINS}
        JOIN verses vv ON vv.verse_id=w.verse_id
        WHERE vv.book_id=%s AND vv.chapter=%s AND vv.verse=%s
        ORDER BY w.word_pos''', (n, c, v)).fetchall()
    tid = trans['translation_id'] if trans else None
    choice_bytes = read_choices(tid) if tid else None
    others = other_options(tid) if tid else []
    parts = []
    if not trans:
        parts.append(f'<p><b><a href="{u("/translations")}">Pick or create a translation</a></b> '
                     'to start choosing word renderings.</p>')
    for w in words:
        wid = w['word_id']
        items = dropdown_items(w, others)
        byte = choice_bytes[wid - 1] if choice_bytes is not None else 0
        cur = effective_item(tid, w, others, byte) if trans else 0
        opts = []
        for i, (label, _text) in enumerate(items):
            sel = ' selected' if i == cur else ''
            opts.append(f'<option value="{i}"{sel}>{html.escape(label)}</option>')
        ctl = ''
        if trans:
            ctl = f'''<form method="post" action="{u("/choice" + tqs(trans))}" style="display:inline">
<input type="hidden" name="word_id" value="{wid}">
<input type="hidden" name="next" value="/verse/{n}/{c}/{v}{tqs(trans)}">
<select name="item">{"".join(opts)}</select>
<input type="text" name="other_txt" placeholder="new Other rendering (optional)">
<button type="submit">save</button>
{"<span class='saved'>✓</span>" if cur else ""}
</form>'''
        parts.append(f'''<div class="wordbox"><span class="heb">{w["pointed"] or w["unpointed"]}</span>
 <a href="{u("/word/" + str(wid) + tqs(trans))}" style="font-size:.85em">detail</a><br>{ctl}</div>''')
    nav = ''
    if trans:
        nav = (f'<p><a href="{u("/reading/" + str(trans["translation_id"]) + "/" + str(n) + "/" + str(c) + "/" + str(v))}">reading view</a> | '
               f'<a href="{u("/export/" + str(trans["translation_id"]))}">export translation</a></p>')
    return render(f'{book_name(n)} {c}:{v}', nav + ''.join(parts), trans)

@app.route('/choice', methods=['POST'])
def choice():
    """Save one byte: the selected drop-down item number for the word.
    A non-empty other_txt adds a new multi-value Other option first.
    A non-default choice also becomes the new lemma default (forward-only)
    for the rest of the text for that word's lemma (see record_lemma_default)."""
    trans = current_translation()
    if not trans:
        return 'No translation selected', 400
    tid = trans['translation_id']
    wid = int(request.form['word_id'])
    db = appdb()
    new_other = request.form.get('other_txt', '').strip()
    others = other_options(tid)
    if new_other:
        match = next((o for o in others if o['text'] == new_other), None)
        if match is None:
            if len(others) >= MAX_OTHERS:
                return f'Other-option limit reached ({MAX_OTHERS})', 400
            idx = max([o['idx'] for o in others] + [0]) + 1
            db.execute('INSERT INTO other_option(translation_id, idx, text) VALUES (%s,%s,%s)',
                       (tid, idx, new_other))
            db.commit()
            others = other_options(tid)
    w = word_with_lex(wid)
    if not w:
        return 'Unknown word', 404
    items = dropdown_items(w, others)
    if new_other:
        item = next(i for i, (lab, txt) in enumerate(items)
                    if txt == new_other and lab.startswith('Other:'))
    else:
        try:
            item = int(request.form.get('item', '0'))
        except ValueError:
            item = 0
        if not 0 <= item < len(items):
            item = 0
    write_choice(tid, wid, item)
    # Kit's translation-source integer: 1=KJV, 2=Young's, 3=user-defined.
    # Source 3 links to other_option via other_option_id.
    src, ooid = None, None
    if 0 < item < len(items):
        label = items[item][0]
        if label.startswith('KJV:'):
            src = SRC_KJV
        elif label.startswith("Young's"):
            src = SRC_YLT
        elif label.startswith('Other:'):
            src = SRC_USER
            m = next((o for o in others if o['text'] == items[item][1]), None)
            ooid = m['option_id'] if m else None
    record_lemma_default(tid, w, others, item, source=src,
                         other_option_id=ooid)
    db.execute("UPDATE translation SET updated_at=now() WHERE translation_id=%s", (tid,))
    db.commit()
    return redirect(u(request.form.get('next', '/')))

@app.route('/translations', methods=['GET', 'POST'])
def translations():
    db = appdb()
    if request.method == 'POST':
        name = request.form.get('name', '').strip() or 'Untitled'
        desc = request.form.get('description', '').strip()
        urow = db.execute('SELECT user_id FROM app_user LIMIT 1').fetchone()
        if not urow:
            cur = db.execute("INSERT INTO app_user(name) VALUES('Kit') RETURNING user_id")
            uid = cur.fetchone()['user_id']
        else:
            uid = urow['user_id']
        owner = current_user()
        cur = db.execute(
            'INSERT INTO translation(user_id, name, description, owner_id)'
            ' VALUES(%s,%s,%s,%s) RETURNING translation_id',
            (uid, name, desc, owner['user_id'] if owner else None))
        new_tid = cur.fetchone()['translation_id']
        db.commit()
        return redirect(u(f'/translations?t={new_tid}'))
    trans = current_translation()
    rows = db.execute('''SELECT t.*, a.display_name AS owner_name
        FROM translation t LEFT JOIN user_accounts a
          ON a.user_id=t.owner_id
        ORDER BY t.updated_at DESC''').fetchall()
    items = []
    for r in rows:
        tid = r['translation_id']
        n_chosen = sum(1 for x in read_choices(tid) if x) if os.path.exists(choices_path(tid)) else 0
        n_other = db.execute('SELECT COUNT(*) c FROM other_option WHERE translation_id=%s', (tid,)).fetchone()['c']
        owner_txt = (f' by {html.escape(r["owner_name"])}'
                     if r['owner_name'] else '')
        items.append(
            f'<li><a href="{u("/verse/1/1/1?t=" + str(tid))}">{html.escape(r["name"])}</a>'
            f' <span style="color:#666">{html.escape(r["description"])}'
            f' (updated {r["updated_at"]}; {n_chosen} words chosen, {n_other} Other options)'
            f'{owner_txt}</span>'
            f' | <a href="{u("/export/" + str(tid))}">export</a></li>')
    body = f'''<ul>{"".join(items)}</ul>
<h2>New translation</h2>
<form method="post"><input type="text" name="name" placeholder="name">
<input type="text" name="description" placeholder="description">
<button type="submit">create</button></form>'''
    return render('My translations', body, trans)

# ---------------------------------------------------------------- clean reading
# Kit 2026-09-30: a page that is NOTHING but the English translation as it
# would appear in an exported text file — no interlinear, no drop-downs, no
# Hebrew spans, no navigation chrome. Just the readable text.
READING_CLEAN = '''<!doctype html><html><head><meta charset="utf-8">
<title>{{title}}</title>
<style>
body{font-family:Georgia,serif;max-width:700px;margin:2.5em auto;padding:0 1.2em;
line-height:1.9;font-size:1.3em;color:#1a1a1a;background:#fdfbf5}
.ref{color:#777;font-size:.72em;margin-bottom:1.2em}
</style></head><body>
<p class="ref">{{ref}}</p>
<p>{{text|safe}}</p>
</body></html>'''


@app.route('/reading/<int:tid>/<int:n>/<int:c>/<int:v>')
def reading(tid, n, c, v):
    trans = appdb().execute('SELECT * FROM translation WHERE translation_id=%s', (tid,)).fetchone()
    if not trans:
        return 'Unknown translation', 404
    choices = read_choices(tid)
    others = other_options(tid)
    words = bible().execute(f'''SELECT {WORD_COLS} {WORD_JOINS}
        WHERE v.book_id=%s AND v.chapter=%s AND v.verse=%s ORDER BY w.word_pos''',
        (n, c, v)).fetchall()
    if not words:
        return 'Unknown verse', 404
    out = []
    for w in words:
        txt = resolve_effective(tid, w, others, choices[w['word_id'] - 1])
        if txt:
            out.append(html.escape(txt))
        else:
            # as exported: unchosen words keep their Hebrew in brackets
            out.append(f'[{html.escape(w["pointed"] or w["unpointed"])}]')
    return render_template_string(
        READING_CLEAN,
        title=f'{trans["name"]} — {book_name(n)} {c}:{v}',
        ref=f'{book_name(n)} {c}:{v} — {html.escape(trans["name"])}',
        text=' '.join(out))

# ---------------------------------------------------------------- daily reading
# Kit 2026-10-08: the Read door — chapter-at-a-time clean English for daily
# reading, with translation picker, prev/next chapter, and per-user
# "continue where you left off".

READ_CSS = '''
.read-chapter{max-width:640px;margin:0 auto;font-size:1.25em;line-height:1.9;color:#2a1f0d}
.read-chapter .vnum{font-size:.7em;color:#8a6d3b;vertical-align:super;margin-right:6px}
.read-nav{display:flex;justify-content:space-between;margin:24px 0;max-width:640px;margin-left:auto;margin-right:auto}
.read-nav a{background:rgba(255,252,240,.92);border:1px solid #b89b5e;border-radius:8px;
padding:10px 20px;text-decoration:none;color:#5a3c0a}
.read-head{text-align:center;margin-bottom:8px}
.read-head h2{margin-bottom:4px}
.trans-picker{text-align:center;margin:16px 0}
.trans-picker select{font-size:1em}
'''

def _chapter_verses(n, c):
    return bible().execute('''SELECT v.verse FROM verses v
        WHERE v.book_id=%s AND v.chapter=%s AND EXISTS
        (SELECT 1 FROM words w WHERE w.verse_id=v.verse_id)
        ORDER BY v.verse''', (n, c)).fetchall()

def _chapter_bounds(n, c):
    """(prev, next) as (book_id, chapter) tuples or None."""
    books = [r['book_id'] for r in bible().execute(
        'SELECT book_id FROM books ORDER BY book_id').fetchall()]
    chaps = [r['chapter'] for r in bible().execute(
        'SELECT DISTINCT chapter FROM verses WHERE book_id=%s ORDER BY chapter', (n,)).fetchall()]
    bi, ci = books.index(n), chaps.index(c)
    prev = (books[bi - 1], _last_chapter(books[bi - 1])) if ci == 0 and bi > 0 else \
           (n, chaps[ci - 1]) if ci > 0 else None
    prev = None if (ci == 0 and bi == 0) else prev
    if ci == len(chaps) - 1:
        nxt = (books[bi + 1], 1) if bi < len(books) - 1 else None
    else:
        nxt = (n, chaps[ci + 1])
    # fix prev when at first chapter of a book
    if ci == 0 and bi > 0:
        prev = (books[bi - 1], _last_chapter(books[bi - 1]))
    elif ci == 0:
        prev = None
    return prev, nxt

def _last_chapter(n):
    r = bible().execute('SELECT MAX(chapter) AS mc FROM verses WHERE book_id=%s', (n,)).fetchone()
    return r['mc'] or 1

@app.route('/read')
def read_default():
    pos = get_reading_position()
    if pos:
        n, c, tid = pos
        return redirect(u(f'/read/{n}/{c}?t={tid}'))
    return redirect(u('/read/1/1'))

@app.route('/read/<int:n>/<int:c>')
def read_chapter(n, c):
    trans = current_translation()
    if not trans:
        # default to KJV (translation_id 1)
        trans = appdb().execute(
            'SELECT * FROM translation WHERE translation_id=1').fetchone()
    if not trans:
        return 'No translations available', 500
    tid = trans['translation_id']
    verses = _chapter_verses(n, c)
    if not verses:
        return 'Unknown chapter', 404
    save_reading_position(n, c, tid)
    choices = read_choices(tid)
    others = other_options(tid)
    paras = []
    for vr in verses:
        v = vr['verse']
        words = bible().execute(f'''SELECT {WORD_COLS} {WORD_JOINS}
            WHERE v.book_id=%s AND v.chapter=%s AND v.verse=%s ORDER BY w.word_pos''',
            (n, c, v)).fetchall()
        out = []
        for w in words:
            txt = resolve_effective(tid, w, others, choices[w['word_id'] - 1])
            out.append(html.escape(txt) if txt else
                       f'[{html.escape(w["pointed"] or w["unpointed"])}]')
        paras.append(f'<p><span class="vnum">{v}</span>{" ".join(out)}</p>')
    prev, nxt = _chapter_bounds(n, c)
    nav = '<div class="read-nav">'
    nav += (f'<a href="{u(f"/read/{prev[0]}/{prev[1]}?t={tid}")}">← {html.escape(book_name(prev[0]))} {prev[1]}</a>'
            if prev else '<span></span>')
    nav += (f'<a href="{u(f"/read/{nxt[0]}/{nxt[1]}?t={tid}")}">{html.escape(book_name(nxt[0]))} {nxt[1]} →</a>'
            if nxt else '<span></span>')
    nav += '</div>'
    # translation picker
    alltrans = appdb().execute('SELECT translation_id, name FROM translation ORDER BY translation_id').fetchall()
    opts = ''.join(f'<option value="{t["translation_id"]}"{" selected" if t["translation_id"] == tid else ""}>'
                   f'{html.escape(t["name"])}</option>' for t in alltrans)
    picker = (f'<div class="trans-picker"><label>Translation: '
              f'<select onchange="location.href=\'{u(f"/read/{n}/{c}")}?t=\'+this.value\">'
              f'{opts}</select></label></div>')
    # study this chapter link
    study = (f'<p style="text-align:center"><a href="{u(f"/interlinear/{n}/{c}/1")}">'
             f'Study this chapter in the interlinear →</a></p>')
    body = (f'<style>{READ_CSS}</style>{picker}'
            f'<div class="read-head"><h2>{html.escape(book_name(n))} {c}</h2>'
            f'<div class="dim">{html.escape(trans["name"])}</div></div>'
            f'<div class="read-chapter">{"".join(paras)}</div>{nav}{study}'
            f'<p style="text-align:center"><a href="{u("/")}">&larr; Study or Read</a></p>')
    return render(f'{book_name(n)} {c} — Read', body, trans)

@app.route('/export/<int:tid>')
def export(tid):
    trans = appdb().execute('SELECT * FROM translation WHERE translation_id=%s', (tid,)).fetchone()
    if not trans:
        return 'Unknown translation', 404
    choices = read_choices(tid)
    others = other_options(tid)
    b = bible()
    lines = [f'# {trans["name"]}', f'# {trans["description"]}']
    fmt = request.args.get('format')
    if fmt:
        # Kit 2026-09-28: an unrecognized format is not invalid (possibly a
        # highly archaic vowel structure) — never reject it. Flag it for
        # further research and keep rendering the full text, special
        # characters as-is.
        lines.append(f"# flagged for research: unrecognized export format {fmt!r}")
    lines.append('')
    verses = b.execute('''SELECT v.book_id, v.chapter, v.verse FROM verses v
        WHERE EXISTS (SELECT 1 FROM words w WHERE w.verse_id=v.verse_id)
        ORDER BY v.book_id, v.chapter, v.verse''').fetchall()
    for vr in verses:
        words = b.execute(f'''SELECT {WORD_COLS} {WORD_JOINS}
            WHERE v.book_id=%s AND v.chapter=%s AND v.verse=%s ORDER BY w.word_pos''',
            (vr['book_id'], vr['chapter'], vr['verse'])).fetchall()
        parts = []
        for w in words:
            txt = resolve_effective(tid, w, others, choices[w['word_id'] - 1])
            parts.append(txt if txt else f'[{w["pointed"] or w["unpointed"]}]')
        lines.append(f'{book_name(vr["book_id"])} {vr["chapter"]}:{vr["verse"]}\n{" ".join(parts)}\n')
    return Response('\n'.join(lines), mimetype='text/plain',
                    headers={'Content-Disposition': f'attachment; filename=translation_{tid}.txt'})

@app.route('/word/<int:wid>')
def word_detail(wid):
    trans = current_translation()
    b = bible()
    w = word_with_lex(wid)
    if not w:
        return 'Unknown word', 404
    letters = (w['letters'] or '').strip()
    letter_list = ' · '.join(letters.split()) if letters else '(no letter data)'
    affix_prefix = ' '.join((w[f'prefix{i}_disp'] or '').strip() for i in (1, 2, 3)).strip()
    affix_suffix = ' '.join((w[f'suffix{i}_disp'] or '').strip() for i in (1, 2)).strip()
    affix_parts = []
    if affix_prefix:
        affix_parts.append(f'prefix: {affix_prefix}')
    if affix_suffix:
        affix_parts.append(f'suffix: {affix_suffix}')
    affix_disp = f'<span class="heb">{" / ".join(affix_parts)}</span>' if affix_parts else '(none)'
    # lexicon children for this root vowel; re-aggregate in seq order to
    # reproduce the v1 blobs byte-for-byte (verified lossless in migration)
    kjv_map, ylt_map = lex_renderings()
    key = (w['root_id'], w['root_form_seq'], w['root_vowel_seq'])
    kjv_list = kjv_map.get(key, [])
    ylt_list = ylt_map.get(key, [])
    ctx_rows = b.execute('''SELECT vv.book_id, vv.chapter, vv.verse, c.context_text
        FROM lexicon_ylt_context c JOIN verses vv ON vv.verse_id=c.verse_id
        WHERE c.root_id=%s AND c.root_form_seq=%s AND c.vowel_seq=%s
        ORDER BY c.seq''', key).fetchall()
    ylt_contexts = ' \u2016 '.join(
        f'{book_name(r["book_id"])} {r["chapter"]}:{r["verse"]} \u2014 {r["context_text"]}'
        for r in ctx_rows)
    fv_rows = b.execute('''SELECT vv.book_id, vv.chapter, vv.verse
        FROM lexicon_found_verse f JOIN verses vv ON vv.verse_id=f.verse_id
        WHERE f.root_id=%s AND f.root_form_seq=%s AND f.vowel_seq=%s
        ORDER BY f.rowid''', key).fetchall()
    found_verses = '; '.join(
        f'{book_name(r["book_id"])} {r["chapter"]}:{r["verse"]}' for r in fv_rows)
    rows = [
        ('Pointed', w['pointed']),
        ('Unpointed', w['unpointed']),
        ('Letters', f'<span class="heb">{letter_list}</span>'),
        ('Affixes', affix_disp),
        ('Root code', w['root_code']),
        ('Strong\u2019s', f"{w['strongs'] or '(none)'} "
                          f"<span style='color:#666'>source: {w['strongs_source'] or '?'}</span>"),
        ('Morphology', w['morph'] or '(none)'),
        ('KJV renderings', '<br>'.join(kjv_list) if kjv_list else '(none)'),
        ('Young\u2019s renderings (computed)', '<br>'.join(ylt_list) if ylt_list else '(none)'),
        ('YLT verse contexts', (ylt_contexts or '(none)')[:2000]),
        ('Found verses', (found_verses or '(none)')[:1500]),
    ]
    body = '<table>' + ''.join(f'<tr><th>{k}</th><td>{v or "(none)"}</td></tr>' for k, v in rows) + '</table>'
    # bibliomancy: every verse using this word form, each linking to its verse page
    unp = w['unpointed']
    bib_cnt = b.execute('''SELECT COUNT(DISTINCT vv.verse_id)
        FROM words w2 JOIN verses vv ON vv.verse_id=w2.verse_id
        WHERE w2.unpointed=%s''', (unp,)).fetchone()[0]
    bib_rows = b.execute('''SELECT DISTINCT vv.book_id, vv.chapter, vv.verse
        FROM words w2 JOIN verses vv ON vv.verse_id=w2.verse_id
        WHERE w2.unpointed=%s
        ORDER BY vv.book_id, vv.chapter, vv.verse LIMIT 200''', (unp,)).fetchall()
    bib_items = ''.join(
        f'<li><a href="{u("/verse/" + str(r["book_id"]) + "/" + str(r["chapter"]) + "/" + str(r["verse"]) + tqs(trans))}">'
        f'{book_name(r["book_id"])} {r["chapter"]}:{r["verse"]}</a></li>'
        for r in bib_rows)
    body += (f'<h2>Bibliomancy — verses using this word</h2>'
             f'<p>{bib_cnt} verse(s) use <span class="heb">{html.escape(unp or "")}</span>'
             + (' (showing first 200)' if bib_cnt > 200 else '') + '</p>'
             f'<ul>{bib_items}</ul>')
    body += f'<p><a href="{u("/verse/" + str(w["book_id"]) + "/" + str(w["chapter"]) + "/" + str(w["verse"]) + tqs(trans))}">back to verse</a></p>'
    return render(f'Word {wid} — {w["pointed"] or w["unpointed"]}', body, trans)

@app.route('/variants')
def variants():
    """Hebrew word variants explorer: pick a word from the drop-down (optionally
    filtered by a Hebrew text search) and see all its variant readings."""
    trans = current_translation()
    b = bible()
    q = request.args.get('q', '').strip()
    sel = request.args.get('word_id', '').strip()
    sel_wid = int(sel) if sel.isdigit() else None
    # word list for the drop-down: only words that actually HAVE variance
    # (two or more distinct academic/textual readings post medial/final fold,
    # v1 data-artifact rows excluded — Kit 2026-10-01). Empty until real
    # textual-apparatus variants are loaded into the corpus.
    vids = variant_word_ids()
    in_list = ",".join(str(v) for v in vids) or "-1"
    if q:
        qq = q.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')
        words = b.execute(f'''SELECT word_id, pointed, unpointed FROM words
            WHERE (pointed LIKE %s ESCAPE '\\' OR unpointed LIKE %s ESCAPE '\\')
              AND word_id IN ({in_list})
            ORDER BY word_id LIMIT 500''', (f'%{qq}%', f'%{qq}%')).fetchall()
    else:
        words = b.execute(f'''SELECT word_id, pointed, unpointed FROM words
            WHERE word_id IN ({in_list}) ORDER BY word_id''').fetchall()
    # make sure the currently selected word is in the list even when it falls
    # outside the variant-word list (direct links still resolve)
    if sel_wid and not any(w['word_id'] == sel_wid for w in words):
        w0 = b.execute('SELECT word_id, pointed, unpointed FROM words WHERE word_id=%s',
                       (sel_wid,)).fetchone()
        if w0:
            words = [w0] + list(words)
    opts = []
    for w in words:
        s = ' selected' if sel_wid == w['word_id'] else ''
        disp = w['pointed'] or w['unpointed'] or f'word {w["word_id"]}'
        opts.append(f'<option value="{w["word_id"]}"{s}>'
                    f'{w["word_id"]}: {html.escape(disp)}</option>')
    search_form = f'''<form method="get" action="{u("/variants")}">
<input type="text" name="q" value="{html.escape(q)}" placeholder="search Hebrew text…"
       class="heb" style="font-size:1.1em">
<button type="submit">search</button>
</form>'''
    pick_form = f'''<form method="get" action="{u("/variants")}">
<label>Hebrew word:
<select name="word_id" class="heb" style="font-size:1.2em;max-width:340px">
{"".join(opts)}</select>
</label>
<button type="submit">show variants</button>
</form>'''
    body = search_form + pick_form
    if not vids and not sel_wid:
        body += ('<p><i>No manuscript variants are loaded in the corpus yet. '
                 'The v1 data-artifact rows are excluded by Kit\'s 2026-10-01 '
                 'direction; only academic/textual variants will appear here '
                 'once loaded.</i></p>')
    if sel_wid:
        w = b.execute('SELECT word_id, pointed, unpointed FROM words WHERE word_id=%s',
                      (sel_wid,)).fetchone()
        if not w:
            body += f'<p>Unknown word id {sel_wid}.</p>'
        else:
            rows_all = b.execute('''SELECT COUNT(*) FROM word_variants
                WHERE word_id=%s''', (sel_wid,)).fetchone()[0]
            rows = word_variant_rows(sel_wid)
            heb = w['pointed'] or w['unpointed'] or ''
            body += (f'<h2><span class="heb">{html.escape(heb)}</span> '
                     f'(word {sel_wid}) — {len(rows)} variant(s)</h2>')
            hidden = rows_all - len(rows)
            if hidden:
                body += (f'<p class="dim">{hidden} duplicate row(s) differing'
                         ' only by medial/final letterforms are folded away'
                         ' (study-tool artifacts, not real variance).</p>')
            if rows:
                hdr = ['seq', 'kind', 'unpointed', 'letters', 'variant text',
                       'convention', 'source', 'witness', 'variant type', 'basis']
                body += '<table><tr>' + ''.join(f'<th>{h}</th>' for h in hdr) + '</tr>'
                for r in rows:
                    cells = [r['variant_seq'], r['variant_kind'], r['unpointed'],
                             r['letters'], r['variant_text'], r['convention'],
                             r['source'], r['witness'], r['variant_type'], r['basis']]
                    tds = []
                    for i, c in enumerate(cells):
                        val = (html.escape(str(c)) if c is not None else '<i>—</i>')
                        if i in (2, 3, 4) and c is not None:
                            val = f'<span class="heb">{val}</span>'
                        tds.append(f'<td>{val}</td>')
                    body += '<tr>' + ''.join(tds) + '</tr>'
                body += '</table>'
            else:
                body += '<p>No variants recorded for this word.</p>'
    return render('Word variants', body, trans)

# ---------------------------------------------------------------- interlinear
# Word-level interlinear view (Kit 2026-09-30, from the approved wireframe):
# Hebrew words in Hebrew word order (RTL), each with its variant drop-down and
# translation drop-down; below, the English sentence in English word order from
# word_alignment/kjv_words, with KJV words lacking a Hebrew alignment italicized
# (KJV print convention for supplied words). Book/Chapter/Verse drop-downs are
# dynamic (chapter list depends on book, verse list on chapter) via /api/*.
# Prev/Next verse links roll over chapter and book boundaries.

INTER_PAGE = '''<!doctype html><html><head><meta charset="utf-8">
<title>{{title}}</title>
<style>
body{font-family:Georgia,serif;max-width:1200px;margin:0 auto;padding:12px;line-height:1.5;color:#2a1f0d;background-color:#e8d5a3;background-image:url("{{tile}}");background-repeat:repeat}
.heb{direction:rtl;unicode-bidi:embed}
.big{font-size:1.9em}
.wpos{color:#888;font-size:.85em}
.strongs{color:#666;font-size:.8em}
.dim{color:#999}
.interlinear{display:flex;flex-wrap:wrap;direction:rtl;gap:.6em;margin:1em 0;align-items:stretch}
.icol{flex:0 1 200px;min-width:150px;max-width:240px;border:1px solid #b89b5e;border-radius:8px;padding:.6em;background:rgba(255,252,240,.88);display:flex;flex-direction:column;gap:.35em;box-shadow:0 2px 6px rgba(90,60,10,.18)}
.iheb{text-align:center;padding:.2em 0}
.imeta{text-align:center}
.ilabel{display:block;font-size:.82em;color:#444}
.ilabel select{width:100%;margin-top:.15em;font-size:.95em}
.english{direction:ltr;text-align:left;background:rgba(247,247,247,.92);padding:1em 1.2em;border-radius:8px;margin:1.2em 0;font-size:1.35em;line-height:2;border:1px solid #b89b5e}
.enw{white-space:nowrap;margin-right:.15em}
.wnum{font-size:.55em;color:#888;margin-left:.1em}
.legend{font-size:.9em;color:#555;margin:.5em 0 1.5em}
.nbar{display:flex;flex-wrap:wrap;gap:.6em;align-items:center;background:rgba(238,238,255,.9);padding:.7em 1em;border-radius:8px;margin:1em 0;border:1px solid #b89b5e}
.nbar label{font-size:.9em}
.nbar select{font-size:1em;padding:.2em .4em}
.prevnext{margin-left:auto;display:flex;gap:.8em}
.saved{color:green;font-size:.9em}
table{border-collapse:collapse} td,th{border:1px solid #ccc;padding:4px 8px}
</style></head><body>''' + NAV + '''
<h1>{{title}}</h1>
{{body|safe}}
</body></html>'''

def render_interlinear(title, body, trans=None):
    return render_template_string(INTER_PAGE, title=title, body=body,
                                   trans=trans, user=current_user(),
                                   u0=request.script_root or '',
                                   tile=u('/papyrus-tile.png'))

@app.route('/papyrus-tile.png')
def papyrus_tile():
    p = os.path.join(BASE, 'papyrus-tile.png')
    if not os.path.exists(p):
        return 'Not found', 404
    with open(p, 'rb') as f:
        return Response(f.read(), mimetype='image/png')

_WORDS_EXIST = 'AND EXISTS (SELECT 1 FROM words w WHERE w.verse_id=vv.verse_id)'

def verse_row(n, c, v):
    return bible().execute(
        f'''SELECT verse_id FROM verses vv WHERE vv.book_id=%s AND vv.chapter=%s
            AND vv.verse=%s {_WORDS_EXIST}''', (n, c, v)).fetchone()

def adjacent_verse(n, c, v, d):
    """Prev/next verse with rollover: next chapter when the chapter's verses
    are exhausted, next book when its chapters are exhausted (and mirrored
    for prev). Only verses that have words. Returns (book, chapter, verse)
    or None at the ends of the corpus."""
    b = bible()
    if d > 0:
        r = b.execute(f'''SELECT MIN(vv.verse) m FROM verses vv
            WHERE vv.book_id=%s AND vv.chapter=%s AND vv.verse>%s {_WORDS_EXIST}''',
            (n, c, v)).fetchone()
        if r['m']:
            return (n, c, r['m'])
        r = b.execute(f'''SELECT MIN(vv.chapter) m FROM verses vv
            WHERE vv.book_id=%s AND vv.chapter>%s {_WORDS_EXIST}''', (n, c)).fetchone()
        if r['m']:
            nc = r['m']
            rv = b.execute(f'''SELECT MIN(vv.verse) m FROM verses vv
                WHERE vv.book_id=%s AND vv.chapter=%s {_WORDS_EXIST}''', (n, nc)).fetchone()
            return (n, nc, rv['m'])
        r = b.execute(f'''SELECT MIN(vv.book_id) m FROM verses vv
            WHERE vv.book_id>%s {_WORDS_EXIST}''', (n,)).fetchone()
        if r['m']:
            nb = r['m']
            rc = b.execute(f'''SELECT MIN(vv.chapter) m FROM verses vv
                WHERE vv.book_id=%s {_WORDS_EXIST}''', (nb,)).fetchone()
            nc = rc['m']
            rv = b.execute(f'''SELECT MIN(vv.verse) m FROM verses vv
                WHERE vv.book_id=%s AND vv.chapter=%s {_WORDS_EXIST}''', (nb, nc)).fetchone()
            return (nb, nc, rv['m'])
        return None
    r = b.execute(f'''SELECT MAX(vv.verse) m FROM verses vv
        WHERE vv.book_id=%s AND vv.chapter=%s AND vv.verse<%s {_WORDS_EXIST}''',
        (n, c, v)).fetchone()
    if r['m']:
        return (n, c, r['m'])
    r = b.execute(f'''SELECT MAX(vv.chapter) m FROM verses vv
        WHERE vv.book_id=%s AND vv.chapter<%s {_WORDS_EXIST}''', (n, c)).fetchone()
    if r['m']:
        nc = r['m']
        rv = b.execute(f'''SELECT MAX(vv.verse) m FROM verses vv
            WHERE vv.book_id=%s AND vv.chapter=%s {_WORDS_EXIST}''', (n, nc)).fetchone()
        return (n, nc, rv['m'])
    r = b.execute(f'''SELECT MAX(vv.book_id) m FROM verses vv
        WHERE vv.book_id<%s {_WORDS_EXIST}''', (n,)).fetchone()
    if r['m']:
        nb = r['m']
        rc = b.execute(f'''SELECT MAX(vv.chapter) m FROM verses vv
            WHERE vv.book_id=%s {_WORDS_EXIST}''', (nb,)).fetchone()
        nc = rc['m']
        rv = b.execute(f'''SELECT MAX(vv.verse) m FROM verses vv
            WHERE vv.book_id=%s AND vv.chapter=%s {_WORDS_EXIST}''', (nb, nc)).fetchone()
        return (nb, nc, rv['m'])
    return None

# Kit 2026-09-30: the v1-medial vs academic-final "variants" are NOT real
# manuscript variance — that's dirty data from the study tool, which ignored
# special characters when a letter appears at the end of the word (final
# letterforms ךםןףץ vs medial כמנפצ). Rows differing ONLY by medial/final
# letterforms are folded together here so they are never baked into the UI.
_FINALS_FOLD = str.maketrans('ךםןףץ', 'כמנפצ')


def fold_finals(s):
    """Fold Hebrew final letterforms to their medial equivalents."""
    return (s or '').translate(_FINALS_FOLD)


def word_variant_rows(wid, prefer_letters=None):
    """Variant rows for a word, de-duplicated: rows whose letters (and
    variant text) are identical after final-letterform folding are the same
    reading — keep one, preferring the row whose letters match the word's
    own corpus form, else the lowest variant_seq. Kit 2026-10-01: v1
    data-artifact rows (basis marking anomaly= or ARTIFACT) are excluded —
    only academic/textual manuscript variants are shown. Returns the
    survivors in variant_seq order."""
    rows = bible().execute('''SELECT variant_seq, variant_kind, unpointed,
        letters, variant_text, convention, source, witness, variant_type, basis
        FROM word_variants WHERE word_id=%s
          AND basis NOT LIKE '%%anomaly=%%'
          AND basis NOT LIKE '%%ARTIFACT%%'
        ORDER BY variant_seq''',
        (wid,)).fetchall()
    best = {}
    for r in rows:
        key = (r['variant_kind'], fold_finals(r['letters']),
               fold_finals(r['variant_text']))
        if key not in best:
            best[key] = r
        elif (prefer_letters and r['letters'] == prefer_letters
              and best[key]['letters'] != prefer_letters):
            best[key] = r
    return sorted(best.values(), key=lambda r: r['variant_seq'])

# Kit 2026-10-01: the /variants drop-down must list only words that actually
# HAVE variance — two or more distinct readings after the medial/final
# letterform fold. (Every word has >=2 raw rows; the fold is the real test.)
_VARIANT_WORD_IDS = {}

def variant_word_ids():
    """Sorted word_ids having >=2 distinct REAL variant readings (post
    medial/final fold, same de-dup rule as word_variant_rows). Kit 2026-10-01:
    v1 data-artifact rows (basis marking anomaly= or ARTIFACT) are excluded —
    only academic/textual manuscript variants count. Cached per corpus path;
    the corpus is read-only so the cache never goes stale."""
    if BIBLE_DB not in _VARIANT_WORD_IDS:
        rows = bible().execute('''SELECT word_id FROM word_variants
            WHERE basis NOT LIKE '%%anomaly=%%'
              AND basis NOT LIKE '%%ARTIFACT%%'
            GROUP BY word_id
            HAVING COUNT(DISTINCT
                COALESCE(variant_kind, '') || chr(31) ||
                fold_finals(letters) || chr(31) ||
                fold_finals(variant_text)) >= 2
            ORDER BY word_id''').fetchall()
        _VARIANT_WORD_IDS[BIBLE_DB] = [r['word_id'] for r in rows]
    return _VARIANT_WORD_IDS[BIBLE_DB]


def parse_variant_params():
    sel = {}
    for p in request.args.getlist('wv'):
        if ':' in p:
            wid, seq = p.split(':', 1)
            if wid.isdigit() and seq.isdigit():
                sel[int(wid)] = int(seq)
    return sel

def english_sentence_html(verse_id):
    """KJV words in KJV (English) word order. A KJV word with no Hebrew
    alignment in word_alignment is italicized (KJV print convention for
    supplied words); aligned words carry their Hebrew word position as a
    superscript. Hebrew words with no KJV alignment are listed after."""
    b = bible()
    kws = b.execute('''SELECT kjv_word_id, kjv_pos, kjv_word FROM kjv_words
        WHERE verse_id=%s ORDER BY kjv_pos''', (verse_id,)).fetchall()
    if not kws:
        return '<p><i>No KJV text for this verse.</i></p>'
    al = {r['kjv_word_id']: r['hebrew_word_id'] for r in b.execute(
        'SELECT kjv_word_id, hebrew_word_id FROM word_alignment '
        'WHERE verse_id=%s AND kjv_word_id IS NOT NULL', (verse_id,))}
    poss = {r['word_id']: r['word_pos'] for r in b.execute(
        'SELECT word_id, word_pos FROM words WHERE verse_id=%s', (verse_id,))}
    parts = []
    for k in kws:
        wtxt = html.escape(k['kjv_word'])
        hid = al.get(k['kjv_word_id'])
        if hid is None:
            parts.append(f'<span class="enw"><i>{wtxt}</i></span>')
        else:
            pos = poss.get(hid, '?')
            parts.append(
                f'<span class="enw">{wtxt}<sup class="wnum">{pos}</sup></span>')
    out = ['<h2>English (KJV word order)</h2>',
           '<p class="english">' + ' '.join(parts) + '</p>',
           '<p class="legend"><i>Italics</i> = KJV word with no Hebrew word '
           'aligned in word_alignment (supplied for English grammar, per KJV '
           'print convention). Superscript = Hebrew word position above.</p>']
    untr = b.execute('''SELECT w.word_pos, w.pointed, w.unpointed FROM words w
        WHERE w.verse_id=%s
        AND NOT EXISTS (SELECT 1 FROM word_alignment a
            WHERE a.verse_id=w.verse_id AND a.hebrew_word_id=w.word_id
            AND a.kjv_word_id IS NOT NULL)
        ORDER BY w.word_pos''', (verse_id,)).fetchall()
    if untr:
        ulist = ', '.join(
            f'<span class="heb">{html.escape(r["pointed"] or r["unpointed"])}</span>'
            f' (#{r["word_pos"]})' for r in untr)
        out.append(f'<p class="legend">Hebrew with no KJV alignment: {ulist}</p>')
    return ''.join(out)

@app.route('/api/books')
def api_books():
    rows = bible().execute(
        'SELECT book_id, name_en FROM books ORDER BY book_id').fetchall()
    return jsonify([{'book_id': r['book_id'], 'name_en': r['name_en']}
                    for r in rows])

@app.route('/api/chapters/<int:n>')
def api_chapters(n):
    rows = bible().execute(
        f'''SELECT DISTINCT vv.chapter FROM verses vv
            WHERE vv.book_id=%s {_WORDS_EXIST} ORDER BY vv.chapter''',
        (n,)).fetchall()
    return jsonify([r['chapter'] for r in rows])

@app.route('/api/verses/<int:n>/<int:c>')
def api_verses(n, c):
    rows = bible().execute(
        f'''SELECT vv.verse FROM verses vv
            WHERE vv.book_id=%s AND vv.chapter=%s {_WORDS_EXIST}
            ORDER BY vv.verse''', (n, c)).fetchall()
    return jsonify([r['verse'] for r in rows])

@app.route('/interlinear')
def interlinear_default():
    return redirect(u('/interlinear/1/1/1'))

@app.route('/interlinear/<int:n>/<int:c>/<int:v>')
def interlinear(n, c, v):
    trans = current_translation()
    b = bible()
    vrow = verse_row(n, c, v)
    if not vrow:
        return 'Unknown verse', 404
    verse_id = vrow['verse_id']
    words = b.execute(f'''SELECT {WORD_COLS} {WORD_JOINS}
        JOIN verses vv ON vv.verse_id=w.verse_id
        WHERE vv.book_id=%s AND vv.chapter=%s AND vv.verse=%s
        ORDER BY w.word_pos''', (n, c, v)).fetchall()
    tid = trans['translation_id'] if trans else None
    choice_bytes = read_choices(tid) if tid else None
    others = other_options(tid) if tid else []
    var_sel = parse_variant_params()
    # resolved display Hebrew for variant-selected words
    var_text = {}
    for wid, seq in var_sel.items():
        r = b.execute('''SELECT variant_text, unpointed FROM word_variants
            WHERE word_id=%s AND variant_seq=%s''', (wid, seq)).fetchone()
        if r:
            var_text[wid] = r['variant_text'] or r['unpointed']
    wv_qs = ''.join(f'&wv={wid}:{seq}' for wid, seq in sorted(var_sel.items()))
    t_qs = f'?t={tid}' if tid else ''
    # nav drop-downs (server-rendered; JS re-fills chapter/verse dynamically)
    books = b.execute('SELECT book_id, name_en FROM books ORDER BY book_id').fetchall()
    chaps = b.execute(f'''SELECT DISTINCT vv.chapter FROM verses vv
        WHERE vv.book_id=%s {_WORDS_EXIST} ORDER BY vv.chapter''', (n,)).fetchall()
    vss = b.execute(f'''SELECT vv.verse FROM verses vv
        WHERE vv.book_id=%s AND vv.chapter=%s {_WORDS_EXIST} ORDER BY vv.verse''',
        (n, c)).fetchall()
    bopts = ''.join(f'<option value="{r["book_id"]}"'
                    f'{" selected" if r["book_id"] == n else ""}>'
                    f'{html.escape(r["name_en"])}</option>' for r in books)
    copts = ''.join(f'<option value="{r["chapter"]}"'
                    f'{" selected" if r["chapter"] == c else ""}>'
                    f'{r["chapter"]}</option>' for r in chaps)
    vopts = ''.join(f'<option value="{r["verse"]}"'
                    f'{" selected" if r["verse"] == v else ""}>'
                    f'{r["verse"]}</option>' for r in vss)
    prev = adjacent_verse(n, c, v, -1)
    nxt = adjacent_verse(n, c, v, +1)
    prev_html = (f'<a id="prev-link" href="{u(f"/interlinear/{prev[0]}/{prev[1]}/{prev[2]}")}{t_qs}">'
                 f'&larr; Prev verse</a>' if prev
                 else '<span class="dim">&larr; Prev verse</span>')
    next_html = (f'<a id="next-link" href="{u(f"/interlinear/{nxt[0]}/{nxt[1]}/{nxt[2]}")}{t_qs}">'
                 f'Next verse &rarr;</a>' if nxt
                 else '<span class="dim">Next verse &rarr;</span>')
    nav = (f'<div class="nbar" data-root="{request.script_root or ""}">'
           f'<label>Book <select id="nav-book">{bopts}</select></label>'
           f'<label>Chapter <select id="nav-ch">{copts}</select></label>'
           f'<label>Verse <select id="nav-v">{vopts}</select></label>'
           f'<button id="nav-go">Go</button>'
           f'<span class="prevnext">{prev_html} {next_html}</span></div>')
    parts = [nav]
    if not trans:
        parts.append(f'<p><b><a href="{u("/translations")}">Pick or create a translation</a></b> '
                     'to save per-word rendering choices.</p>')
    parts.append('<h2>Interlinear (Hebrew word order, right &rarr; left)</h2>')
    parts.append('<div class="interlinear">')
    for w in words:
        wid = w['word_id']
        heb = var_text.get(wid) or w['pointed'] or w['unpointed']
        vrows = word_variant_rows(wid, w['letters'])
        if len(vrows) <= 1:
            # no real variance (the surviving row is the word itself):
            # indicate none instead of a pointless drop-down (Kit 2026-09-30)
            vctl = '<span class="dim">none</span>'
        else:
            vopts2 = ['<option value="">— default (corpus) —</option>']
            for vr in vrows:
                val = f'{wid}:{vr["variant_seq"]}'
                s = ' selected' if var_sel.get(wid) == vr['variant_seq'] else ''
                disp = (vr['unpointed'] or '') + ' [' + (vr['letters'] or '') + ']'
                vopts2.append(
                    f'<option value="{val}"{s}>{html.escape(disp)} — '
                    f'{html.escape(vr["convention"] or "")} '
                    f'({html.escape(vr["variant_kind"] or "")})</option>')
            vctl = (f'<select class="wv-sel" data-wid="{wid}">'
                    f'{"".join(vopts2)}</select>')
        items = dropdown_items(w, others)
        byte = choice_bytes[wid - 1] if choice_bytes is not None else 0
        cur = effective_item(tid, w, others, byte) if trans else 0
        topts = []
        for i, (label, text) in enumerate(items):
            s = ' selected' if i == cur else ''
            topts.append(f'<option value="{i}"{s}>{html.escape(label)}</option>')
        if trans:
            tctl = (f'''<form method="post" action="{u("/choice" + t_qs)}" style="display:inline">
<input type="hidden" name="word_id" value="{wid}">
<input type="hidden" name="next" value="/interlinear/{n}/{c}/{v}{t_qs}{wv_qs}">
<select name="item" class="tr-sel">{"".join(topts)}</select>
<button type="submit">save</button>
{"<span class='saved'>✓</span>" if cur else ""}
</form>''')
        else:
            tctl = (f'''<select class="tr-prev" data-wid="{wid}">{"".join(topts)}</select>
<span class="tr-pv" id="pv-{wid}" style="font-size:.85em;color:#444"></span>''')
        parts.append(
            f'''<div class="icol">
<div class="iheb"><span class="heb big">{html.escape(heb)}</span></div>
<div class="imeta"><span class="wpos">#{w["word_pos"]}</span>
 <span class="strongs">{html.escape(w["strongs"] or "")}</span>
 <a href="{u("/word/" + str(wid) + t_qs)}" class="details-link">details</a></div>
<label class="ilabel">Variant<br>{vctl}</label>
<label class="ilabel">Translation<br>{tctl}</label>
</div>''')
    parts.append('</div>')
    parts.append(english_sentence_html(verse_id))
    js = '''
var nbar = document.querySelector('.nbar');
var APIR = nbar ? nbar.dataset.root : '';
var bookSel = document.getElementById('nav-book');
var chSel = document.getElementById('nav-ch');
var vSel = document.getElementById('nav-v');
function fillSel(sel, vals, keep) {
  sel.innerHTML = vals.map(function(x){
    return '<option value="' + x + '"' + (x == keep ? ' selected' : '') + '>' + x + '</option>';
  }).join('');
}
async function loadChapters(keepCh, keepV) {
  var r = await fetch(APIR + '/api/chapters/' + bookSel.value);
  var chaps = await r.json();
  fillSel(chSel, chaps, keepCh);
  await loadVerses(keepV);
}
async function loadVerses(keepV) {
  var r = await fetch(APIR + '/api/verses/' + bookSel.value + '/' + chSel.value);
  var vss = await r.json();
  fillSel(vSel, vss, keepV);
}
if (bookSel) bookSel.addEventListener('change', function(){ loadChapters(); });
if (chSel) chSel.addEventListener('change', function(){ loadVerses(); });
var goBtn = document.getElementById('nav-go');
if (goBtn) goBtn.addEventListener('click', function(){
  window.location = APIR + '/interlinear/' + bookSel.value + '/' + chSel.value + '/' + vSel.value + window.location.search;
});
document.querySelectorAll('.wv-sel').forEach(function(sel){
  sel.addEventListener('change', function(){
    var wid = sel.dataset.wid;
    var params = new URLSearchParams(window.location.search);
    var kept = params.getAll('wv').filter(function(x){ return x.indexOf(wid + ':') !== 0; });
    params.delete('wv');
    kept.forEach(function(x){ params.append('wv', x); });
    if (sel.value) params.append('wv', sel.value);
    window.location.search = params.toString();
  });
});
document.querySelectorAll('.tr-prev').forEach(function(sel){
  sel.addEventListener('change', function(){
    var pv = document.getElementById('pv-' + sel.dataset.wid);
    if (pv) pv.textContent = sel.value ? sel.options[sel.selectedIndex].text : '';
  });
});
'''
    parts.append(f'<script>{js}</script>')
    return render_interlinear(f'{book_name(n)} {c}:{v} — interlinear',
                              ''.join(parts), trans)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', '5057'))
    app.run(host='127.0.0.1', port=port, debug=False)
