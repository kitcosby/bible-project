# Prompt for CodeSnack — Hook the BYOT app up to the Lampy Bible database

Paste this whole file into CodeSnack as the task. It continues the PWA you
already built; it does not start over.

## Repos

- **Work in:** https://github.com/kitcosby/BibleApp-pwa (branch `main`) —
  the finished PWA (single `index.html` + `manifest.webmanifest` + `sw.js`
  + icons), currently running on baked-in sample data for Genesis 1:1–5.
- **Reference:** https://github.com/kitcosby/bible-project — the corpus
  project. In particular `website/app_v2.py` is the live server app whose
  JSON routes are listed below; the corpus schema is in `schema_v2.md`.

## The architecture (read first — do not redesign around it)

- The app is a **static PWA**. It cannot open a database connection, and it
  must never try. The Bible database (PostgreSQL on the owner's Lampy
  server) is reached **only over HTTPS, through a JSON API** served by the
  same host that serves the app.
- The API base URL must live in **one** clearly-marked constant,
  `API_BASE`, defaulting to the **relative** path `/bible` so the app
  works unchanged when served from the Lampy host. (The full tailnet
  address of that host is `https://laptop.taila7a335.ts.net`, so the live
  API is `https://laptop.taila7a335.ts.net/bible/api/...`. During
  development inside CodeSnack the API will usually be **unreachable** —
  that is expected; see the fallback rules.)
- The API is **read-only** for this task: GET requests only. Do not invent
  POST endpoints. The user's own rendering choices stay in `localStorage`
  exactly as they work today.

## The API contract

**Already live on the server** (navigation data):

- `GET /api/books` → `[{ "book_id": 1, "name_en": "Genesis" }, ...]` (all 39 books)
- `GET /api/chapters/<book_id>` → `[1, 2, 3, ...]`
- `GET /api/verses/<book_id>/<chapter>` → `[1, 2, 3, ...]`

**Being built server-side to this contract** — build the client against
these shapes now, with the mock/fallback below:

- `GET /api/verse/<book_id>/<chapter>/<verse>` → one verse for Study:
  ```json
  { "book_id": 1, "book_name": "Genesis", "chapter": 1, "verse": 1,
    "words": [ { "wid": 101, "hebrew": "בְּרֵאשִׁית", "xlit": "bereshit",
                 "strongs": "H7225", "gloss": "beginning",
                 "morph": "noun, construct",
                 "kjv": "In the beginning", "ylt": "In the beginning",
                 "supplied": false } ],
    "witnesses": [ { "witness": "Samaritan", "kind": "orthographic",
                     "note": "..." } ] }
  ```
  (`ylt` is a COMPUTED rendering and must keep its "computed" labeling in
  the UI, as today. `supplied` words render italic, as today.)
- `GET /api/chapter/<book_id>/<chapter>` → `{ "book_id": 1, "chapter": 1,
  "verses": [ <verse objects as above> ] }` for the Read page.
- `GET /api/word/<strongs>` (e.g. `/api/word/H430`) →
  `{ "strongs": "H430", "hebrew": "אֱלֹהִים", "xlit": "Elohim",
     "gloss": "God", "morph": "noun, masculine, plural",
     "occurrences": [ { "book_id": 1, "chapter": 1, "verse": 1,
                        "ref": "Genesis 1:1" } ] }`
- `GET /api/search?q=<text>` → ranked results from the server's verse
  embeddings: `[ { "book_id": 1, "chapter": 1, "verse": 3,
  "ref": "Genesis 1:3", "score": 0.83, "snippet": "..." } ]`
  (This is the SearchResult shape the app already uses — make it real.)

## What to build

1. **A data layer** inside the existing single-file app: functions
   `getBooks()`, `getChapters(b)`, `getVerses(b,c)`, `getVerse(b,c,v)`,
   `getChapter(b,c)`, `getWord(strongs)`, `search(q)` that fetch from
   `API_BASE` and return the shapes above. Replace the baked-in CORPUS
   lookups in Study, Read, the word page, and Search with these.
2. **Fallback, honestly labeled.** Keep the existing Genesis 1:1–5 sample
   embedded as the offline fallback. When the API is unreachable or a
   request fails, serve the sample where it covers the request and show a
   small, clear notice that the app is showing built-in sample data
   because the database is unreachable. Never fabricate verses, words, or
   search results beyond that labeled sample.
3. **Choices unchanged.** The user's rendering choices (including free-text
   "Custom…" entries) stay keyed by Strong's number in `localStorage` and
   apply on top of API data with the settled precedence — Study:
   choice → Young's computed → gloss; Read: choice → KJV → gloss.
4. **Caching.** Extend the service worker with a runtime cache for API
   GET responses (stale-while-revalidate is fine), and bump the cache
   version (e.g. `byot-v2`). A verse once viewed should re-open offline.
5. **Navigation from live data.** The Home table of contents and the
   Book/Chapter/Verse selectors must be driven by `/api/books`,
   `/api/chapters`, `/api/verses` when reachable (39 books from the
   server, not a hard-coded grid); with the API down, fall back to the
   sample's coverage.
6. **Loading and error states** for every view — a verse still loading or
   a failed fetch must never render as a blank page or an invented text.

## Keep unchanged

- All settled behavior and design from the original build: the two doors,
  the parchment/bronze/gold palette, Frank Ruhl Libre + Inter, hash
  routes, the word-card layout, "See also" occurrence lists, witnesses
  shown only where a verse/word actually has them, and the PWA layer
  itself (manifest, icons, installability).
- The license: this project is released under **The Unlicense** (LICENSE
  file in the repo). Keep it.

## Acceptance checklist

- With the API reachable, Study opens any verse (try Genesis 1:1,
  Psalm 23:1 — book_id 19, Isaiah 53:11 — book_id 23) with real Hebrew
  words, glosses, KJV and computed-Young's renderings from the server.
- Read renders a full live chapter; red-letter-style links on words open
  the matching word page; word-page occurrence lists come from the API.
- Search returns ranked server results with scores for a real query.
- With the API unreachable, the labeled sample fallback engages, the app
  still installs and opens, and previously viewed verses reopen from
  cache.
- Choices persist across reloads and apply to live data.
- Work in small commits. At the end, summarize what you changed and how
  the fallback behaves.
