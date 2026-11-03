# Prompt for CodeSnack IDE — turn the Bible prototype into an installable PWA

Paste everything below the line into CodeSnack IDE as the project prompt.

---

You are building in the GitHub repository **kitcosby/BibleApp**
(https://github.com/kitcosby/BibleApp). The starting point already exists in
another of my repositories: clone or fetch **kitcosby/bible-project**
(https://github.com/kitcosby/bible-project) and take the file
`round4-proto/index.html` — a complete, working, self-contained prototype of
"Build Your Own Translation", a Hebrew Bible study/reading app. Both
repositories are dedicated to the public domain under The Unlicense; keep the
LICENSE file as it is.

## Task

Turn that prototype into an **installable Progressive Web App (PWA)** for iOS
and Android, and commit the result to the BibleApp repository as a static site
(no build step, no framework, no server code — plain HTML/CSS/JS files that
any static host can serve, including from a subpath).

## What already exists — do not redesign it

`round4-proto/index.html` is finished and approved. Preserve, unchanged:

- The single-file app: one typed CORPUS data block (Word / Verse /
  WitnessNote / SearchResult shapes), a hash router (`#/`, `#/interlinear`,
  `#/read`, `#/word/<Strongs>`, `#/search`), and a localStorage choices store
  keyed by Strong's number.
- All behavior from its six design rounds: Home tab holds the two doors AND
  the table of contents (39-book grid + Book/Chapter/Verse Go); Study shows
  one verse per frame with Prev/Next navigation; Study defaults are
  custom choice → Young's (computed); Read defaults are custom choice → KJV;
  every word/phrase in Read links to its Hebrew word card; each word card has
  a "See also — where this word is also used" list.
- The design system: Parchment #FFFCF0 background, Papyrus #E8D5A3, Bronze
  #B89B5E, Deep Gold #8C6D2F, Ink #2B2118, Witness Slate #5D6D7E. Fonts:
  Frank Ruhl Libre (Hebrew + reading text), Inter (UI).
- The sample corpus is Genesis 1:1–5 only. Do NOT invent additional biblical
  data. Young's renderings are computed alignments and must stay labeled
  "Young's (computed)".

## What to add — the PWA layer

1. `manifest.webmanifest` — name "Build Your Own Translation", short_name
   "BYOT", display "standalone", orientation "portrait", start_url and scope
   set RELATIVE (".") so it works from any subpath, theme_color #2B2118,
   background_color #FFFCF0, and the icon set below.
2. Icons generated from a simple design: a parchment (#FFFCF0) rounded square,
   a bronze (#B89B5E) border, and the Hebrew letter ב (bet) centered in Deep
   Gold (#8C6D2F) in a serif face. Produce PNG icons at 180×180
   (apple-touch-icon), 192×192, and 512×512 (the 512 also as a maskable icon
   with safe padding).
3. iOS installability meta tags in the HTML head: apple-mobile-web-app-capable
   "yes", apple-mobile-web-app-status-bar-style "black-translucent",
   apple-mobile-web-app-title "BYOT", apple-touch-icon link, viewport-fit=cover.
4. A small service worker (`sw.js`) registered from the page: cache-first for
   the app shell (the HTML, manifest, and icons) so the installed app opens
   offline with the sample data; network-first for everything else; a versioned
   cache name (e.g. "byot-v1") with old-cache cleanup on activate. Keep it
   short and dependency-free.
5. Split nothing else out of the single HTML file except the manifest, icons,
   and service worker — the app must keep working as static files.

## Deliverables in the BibleApp repo

- `index.html` (the prototype, with the PWA head tags + SW registration added)
- `manifest.webmanifest`, `sw.js`, `icon-180.png`, `icon-192.png`,
  `icon-512.png`, `icon-maskable-512.png`
- A short `README.md` section: how to install on iPhone (open in Safari →
  Share → Add to Home Screen) and on Android (Chrome install prompt), and a
  note that live corpus data and semantic search arrive later via the Lampy
  API (the SearchResult shape in the code is the contract).

## Acceptance checklist (verify before finishing)

- The page passes the standard installability requirements: manifest linked
  and valid, icons present at the declared sizes, service worker registered
  and controlling the page, served over HTTPS or localhost assumptions noted.
- Opening the installed app shows: Home (doors + table of contents), Study
  (Genesis 1:1–3, one verse per frame), Read (Genesis 1:1–5, word links),
  word cards with See also, Search (sample results for "light").
- My saved rendering choices still persist (localStorage) after install.
- No visual or behavioral regression versus `round4-proto/index.html`.

Work in small commits with clear messages. When you finish, summarize what
you added and confirm each acceptance item.
