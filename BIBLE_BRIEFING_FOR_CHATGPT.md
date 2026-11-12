# Bible project — catch-up briefing (as of 2026-11-07, rev. 2)

For ChatGPT, from Muse (Kit's assistant), so you can work on this
project with current facts. Kit Cosby owns the project; his rulings
below are settled — don't relitigate them.

## What it is

"Build Your Own Translation": an interlinear Bible study app. Readers
see the Hebrew/Greek text word by word, with morphology, glosses, and
per-word renderings from the King James and from Young's Literal
Translation, and can substitute their own renderings, which persist
per Strong's number. Two views coexist by charter: **Study**
(interlinear, one verse's sentence rebuilt in English order) and
**Read** (clean chapter reading). Public-domain / openly licensed
sources ONLY (no NIV, no closed apparatus).

## Corpus (SQLite bible_v2.db == PostgreSQL `bible` on Lampy, row-for-row)

- 66 books, 31,311 verses. OT: Hebrew (OSHB morphology) + KJV token
  alignment + YLT verses. NT extended 2026-11-03 on Kit's order.
- LXX loaded in full (Rahlfs via CenterBLC Text-Fabric, MIT terms;
  57 books, 30,371 verses): Kit's part is The Unlicense. **Daniel:
  Theodotion (DanTh) is primary, Old Greek is the alternate.**
- Greek NT in three traditions: **Textus Receptus is primary**
  (Robinson, public domain); Byzantine (Robinson–Pierpont, Unlicense)
  and SBLGNT (MorphGNT CC BY-SA) as witnesses. gnt_variants marks
  same/variant/absent per verse (specimens: 1 John 5:7 TR 22 words vs
  Byz/SBL 5; Acts 8:37 absent in both).
- Variant layers (word_variants, ~542K rows): Kethiv/Qere 1,204;
  Samaritan Pentateuch 8,582 (witness siglum 'SP'); Dead Sea Scrolls
  4,202 fully-attested verses only (35 scroll sigla, e.g. 1Qisaa);
  Peshitta verse-level (witness_verses 23,006).
- Embeddings: all 31,102 YLT verses embedded (nomic-embed-text via
  Ollama on Lampy); semantic search live in the app.

## Translation bridges (the recent big work)

- OT: KJV alignment (CrossWire, source-encoded) and a computed
  Young's bridge (Needleman–Wunsch). Young's renderings are
  **COMPUTED best-effort, never authoritative** — labeled as such
  everywhere. Quality gate for bridge/repair work: gold-set precision
  >= 0.7923 AND zero drift on H3068 (the divine name). A grammar
  repair (construct-chain + gap-claiming rules) passed the gate and
  was applied 2026-11-03: precision 0.7923 -> 0.7984, +19,238 pairs.
- NT: TR alignment 202,901 pairs (CrossWire src= attributes); TR
  computed-Young's 143,227 rows.
- **Variant bridges (commissioned 2026-11-03, completed 2026-11-06):**
  Byzantine and SBLGNT each got their own full alignment bridges
  (Greek-to-Greek alignment to TR, then inherit phrases + a residue
  pass). Byzantine: 200,422 alignments, self-consistency 100%, KJV
  coverage 94.7%. SBLGNT: 191,378 alignments, self-consistency 100%,
  KJV coverage 92.0%, Young's 74.1%; Kit authorized its PostgreSQL
  load 2026-11-06. Both are now WIRED: verse payloads carry
  per-tradition phrases, and under a Byzantine/SBLGNT default the
  app's Study sentences build from that tradition's own phrases.

## Gloss layer (display rules, all Kit's rulings)

- Glosses are context-ranked against the verse's own KJV sentence and
  number-inflected for plural nouns via a curated allowlist (~200
  nouns; Eccl 1:2 position 2/6 read "vanities"). Elohim-class words
  (Elohim, mayim/waters, Mitzrayim/Egypt, shamayim) are protected:
  plural form, singular sense — a form-keyed registry was directed
  by Kit; the third member of his "dual pair" list is still
  unconfirmed, so the registry is NOT built yet.
- H853 (the object marker את) shows gloss "(object marker)" with its
  KJV phrase suppressed.

## The app (kitcosby/BibleApp-pwa, public, Unlicense; currently byot-v16)

- Single-file PWA + service worker; auto-deploys to Vercel from main:
  https://bibleapp-pwa.vercel.app ; also served on Lampy at /byot/.
- Data from the Lampy API (Flask app_v2.py on the laptop's WSL distro
  `lampy`, port 5057, proxied at /bible) via Tailscale Funnel :8443.
  PostgreSQL is NOT publicly exposed.
- Settled behavior: rendering precedence Study = reader's choice ->
  Young's (computed) -> gloss; Read = choice -> base version. Base
  toggle KJV/Young's sticky per view. Variant defaults sticky per
  testament with per-word overrides. Study sentence = the verse's
  actual YLT text with choices substituted (KJV base = KJV sentence
  spans); under a non-TR Greek default it chains that tradition's
  own phrases. Footer text follows the data state (Kit's ruling:
  fallback wording shows only while sample data is on screen).
- Division of labor so far: Muse did corpus + API + most client
  rounds; CodeSnack IDE (on Kit's phone) did the NT canon wiring and
  the 2026-11-03 phone-width design round (byot-v13); Kit pastes
  briefs and rules on everything. CodeSnack has ~50 of 500 tokens
  left — keep any briefs for it small and self-contained.

## Hard rules (do not break)

- Never present computed Young's as authoritative; keep labels.
- Public-domain / open-license sources only; SBLGNT text under its
  EULA, MorphGNT CC BY-SA; Kit's own work is The Unlicense.
- PostgreSQL loads of new corpus tables require Kit's explicit
  authorization (he gave it for the SBLGNT bridge; ask again for the
  next one).
- Report status precisely: proved / checked / computed / asserted /
  incomplete are different words here. Never round a status up.

## Validation program (2026-11-06/07 — read this before trusting the Greek data)

A separate validation lane (branches `ylt-lexicon-validation`,
`ylt-lexicon-validation-review-20261106`,
`ylt-greek-alignment-study-guide-docs-20261106`, and the
`lexicon-validation/` records) audited the shipped work and found
real defects. Production data is UNCHANGED by that lane; its standing
recommendation is: preserve production data, implement repairs in
isolation, no production migration without Kit's approval.

- **TR parser defect (root cause found):** `build_nt.py`'s parse_tr()
  does not implement the Robinson source's first/second pipe-variant
  syntax. 431 UTR lines carry pipe markers; 261 pipe-delimited
  variant groups form 245 decision components. Flattening them
  caused positional drift in the TR alignment (confirmed specimens:
  John 9:21, Colossians 4:10). An isolated rebuild in a test database
  (`bible_greek_bridge_test_20261106`, schema `variant_rebuild_test`,
  using the MIT-licensed librobinson parser as reference behavior)
  validated the correction approach for source-resolved verses.
  **Not approved for production.** Until Kit rules, treat TR Greek
  word positions — and everything aligned through them — as
  best-effort with known positional defects in pipe-variant verses.
- **Structural defects in production (small, confirmed):** 3
  out-of-range TR bridge rows and 3 orphan TR YLT rendering rows.
  Hebrew and Byzantine structural checks passed.
- **SBL gloss lookup root cause:** SBL word glosses are partial
  because Greek-script MorphGNT lemmas were compared directly with
  transliterated LXX lemmas. Fix designed, not applied.
- **PWA gap:** the app drops the API's Greek lexical-provenance note
  (`greek_lexicon`: glosses derived from LXX word data). The note is
  served; the client doesn't display it.
- **Backup/recovery:** a full backup was restored into an isolated
  database and all 47 public-table counts matched; checksum
  verification and an off-host copy are still open.
- **Study-guide / adjudication lane:** a deep Ezekiel 27:32 audit
  with an adjudication register (MT stands as the operational
  default); a read-only Hebrew variant API contract with a shadow
  validator (distinct pointed forms invariant verified); a BibleApp
  presentation/schema safety review; source-labelled gloss schema
  findings. These are documents and shadow tests — nothing in them
  is live in the app yet.
- The lexicon's own final validation verdict (2026-11-06):
  **not yet validated for release as a fully correct word-level
  lexicon.** The app remains live and useful; that verdict is about
  the lexicon's validated status, and it is the honest label.

## Open items (Kit's calls, in his time)

- TR parser correction: implement the pipe-variant fix in
  isolation, expand the Greek gold set, then Kit decides on any
  production regeneration. (From the validation lane; see above.)
- OT bridges: Samaritan full-text load + bridge; DSS bridge for the
  4,202 attested verses. Not yet ruled.
- Elohim-class registry: awaits Kit naming the third dual pair.
- Alignment repair round 2 (span-boundary class) under the standing
  gate; gold set expansion beyond 30 verses.
- LXX crosswalk is numbering-based v1; content-based realignment
  (Psalms/Jeremiah/Proverbs) is later work.

## Where things live

- Corpus + builders + ledger: github.com/kitcosby/bible-project
  (NOTATION_LEDGER.md section 10 is the dated record of every ruling
  and gate result).
- App: github.com/kitcosby/BibleApp-pwa.
- Server: /opt/bible/website/app_v2.py on the `lampy` WSL distro;
  supervisor program `bible`.
