# Prompt for CodeSnack IDE — onboarding: Build Your Own Translation (BYOT)

Paste everything below the line into CodeSnack as the opening prompt for a
new session. It brings you up to speed on the project; it is not itself a
task. When you have read it, confirm your understanding and wait for the
owner's task before changing code.

---

You are working with Kit Cosby on **"Build Your Own Translation" (BYOT)** —
a Hebrew Bible study and reading PWA that lets a reader build their own
English rendering, word by word, from the Hebrew text, choosing per-word
renderings that are remembered and applied everywhere.

## Repositories — read carefully

- **Work in:** https://github.com/kitcosby/BibleApp-pwa — public, branch
  `main`, current commit `8226792`. This is the one canonical home of the
  app. Everything you build goes here.
- **Reference only:** https://github.com/kitcosby/bible-project — the
  corpus project: the PostgreSQL corpus, the server app
  (`website/app_v2.py`), the schema (`schema_v2.md`), and the design
  history under `round4-proto/`. Read it to understand data and contracts;
  do not commit app code there.
- **Do NOT touch:** https://github.com/kitcosby/BibleApp — an unrelated
  private Replit scaffold. Leave it entirely alone.
- The app is released under **The Unlicense** (LICENSE in the repo). Keep it.

## What the app is (current state, verified 2026-11-03)

- A **single-file static PWA**: `index.html` + `manifest.webmanifest` +
  `sw.js` + icons. No build step, no framework, no server code. Service
  worker cache is currently `byot-v5` — bump it on every shipped change.
- **Live in two places**, both auto-serving `main` of BibleApp-pwa:
  - Vercel: https://bibleapp-pwa.vercel.app
  - The owner's server (Lampy): https://laptop.taila7a335.ts.net/byot/
    (tailnet) and https://laptop.taila7a335.ts.net:8443/byot/ (public)
- **Views** (hash routes): `#/` Home, `#/interlinear` Study,
  `#/read` Read, `#/word/<Strongs>` Word card, `#/search` Search.

## Settled behavior — do not redesign any of this

- **Home** holds the two doors (Study / Read) AND the table of contents:
  the 39-book grid plus Book/Chapter/Verse selectors with a Go button.
- **Study** is the word-by-word builder: one verse per frame, Prev/Next
  navigation (with chapter rollover), Hebrew words in framed RTL boxes,
  each with a rendering control. The frame heading is the reference only.
  Rendering precedence: **the reader's saved choice → Young's (computed)
  → gloss**.
- **Read** is the clean reading page. For live verses it renders the
  verse's `kjv_sentence` in **English word order** (never chain the
  per-word phrases in Hebrew order — that bug was fixed in `c5f3db8`).
  Precedence: **saved choice → KJV**. Each word span links to its word
  card.
- **Word cards** carry navigation: word links include verse context as
  `#/word/<Strongs>/<book>/<chapter>/<verse>/<wordPos>`, and a card opened
  with context shows Prev word / Next word and a link back to that verse
  in Study. A bare `#/word/H430` (no context) renders the card plainly,
  exactly as before.
- **Choices** (including free-text "Custom…" entries) live in
  `localStorage`, keyed by Strong's number, and apply on top of any data
  source. Never move them server-side.
- **Design system:** Parchment #FFFCF0, Papyrus #E8D5A3, Bronze #B89B5E,
  Deep Gold #8C6D2F, Ink #2B2118, Witness Slate #5D6D7E. Fonts: Frank Ruhl
  Libre (Hebrew + reading text), Inter (UI).

## Data — the Lampy API (read-only, GET only)

The app never connects to a database. It reads JSON from the owner's
Lampy server, probing these bases in order and sticking with the first
that answers (session-sticky `API_BASES` in the code — keep that logic):

1. `https://laptop.taila7a335.ts.net:8443/bible` (public funnel)
2. `https://laptop.taila7a335.ts.net/bible` (tailnet)
3. `/bible` (same host, relative)

Endpoints:

- `GET /api/books`, `GET /api/chapters/<book_id>`,
  `GET /api/verses/<book_id>/<chapter>` — navigation data.
- `GET /api/verse/<book>/<chapter>/<verse>` — one verse for Study:
  `words[]` each with `hebrew`, `strongs`, `morph`, `gloss`, `kjv`,
  `ylt`, `supplied`, per-word `variants`, plus `witnesses[]`, and
  `kjv_sentence` — KJV tokens in English order; a token's `heb_pos` links
  it to the Hebrew word position it translates (null = supplied lead-in).
- `GET /api/chapter/<book>/<chapter>` — a whole chapter for Read
  (per-word `variants` omitted for size; everything else as above).
- `GET /api/word/<strongs>` — the word card: lemma data plus an
  occurrences list; occurrences link back to their verses.
- `GET /api/search?q=<text>` — semantic search (server-side embeddings);
  snippets are computed Young's text and carry `"source": "ylt-computed"`.

Contract realities you must code against:

- **`xlit` is null.** The corpus has no Hebrew transliteration. Never
  invent one; a null transliteration simply doesn't render.
- **There is no raw KJV text.** KJV exists only as the `kjv_sentence`
  token stream (punctuation was stripped at tokenization). Do not promise
  or fake punctuation-perfect KJV.
- **404 contract:** a JSON body `{"error": "not found", ...}` is an
  authoritative not-found — show not-found, never fall back to sample
  data for it. A network failure is different: that is "unreachable".
- **Young's is computed**, not authoritative — alignments built by the
  corpus project. It must stay labeled "Young's (computed)" everywhere
  it appears, including search snippets.

## Honesty rules (project-wide, non-negotiable)

- **Never invent biblical data** — no fabricated verses, words, glosses,
  transliterations, or search results. The only offline fallback is the
  embedded Genesis 1:1–5 sample, and when it is shown it must be labeled
  as sample data shown because the database is unreachable.
- Sources are public-domain / openly licensed only.
- Report status exactly: what you verified, what you could not verify,
  and what failed. Never round a result up.

## Known open item (context only — do not fix unless tasked)

- Ecclesiastes 1:2: the Study frame gloss for the plural form הֲבָלִים
  (H1892, morph HNcmpa) shows "vanity" where the sense is "vanities" —
  the gloss is lemma-level and number-blind. A number-aware gloss fix is
  planned separately.

## How we work

- Small commits with clear messages, straight to `main` of BibleApp-pwa.
- No new dependencies, no build step, keep the app a static single file
  (plus manifest, service worker, icons).
- Bump the service worker cache version on every change, and state in
  your summary what you verified (and how) before calling anything done.

## Your first reply

Confirm, in a short list: (1) which repo you will work in and which you
will not touch; (2) the three API bases and the fallback rule; (3) the
Study and Read precedence orders; (4) why Read must use `kjv_sentence`;
(5) the honesty rules. Then stop and wait for a task.
