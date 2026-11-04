# Two-prong plan — lexicon/grammar + Greek/Septuagint (scoping, 2026-11-03)

Kit's framing (2026-11-03): the remaining work is two-pronged —
(1) improve our lexicon and grammar, and (2) extend into Greek with the
Septuagint. This note scopes both prongs from the verified current state.
Nothing here is built yet; decisions marked KIT are his.

## Prong 1 — Lexicon and grammar (Hebrew side)

State after the 2026-11-03 grammar-repair application (all verified):

- Computed Young's gate: **P 0.7984 / R 0.5039**, H3068 drift 0 (gold =
  30 verses, 335 words, 770 pairs). YLT token coverage **57.47%**,
  distinct Hebrew words hit **67.34%** (176,470 / 262,062).
- `lexicon_ylt_rendering`: 98,090 groups / 234,091 rows.
- Gold false-negative census (pre-repair): 207 unrendered words,
  **184 span-boundary errors** (largest class), 28 displaced spans;
  false positives were mostly wrong spans, not stub phrases.

Work items, in dependency order:

1. **Morph-aware glossing (grammar → lexicon).** The frame/lemma gloss is
   number-blind: Eccl 1:2 shows "vanity" under the plural הֲבָלִים
   (H1892, HNcmpa) — the morphology already distinguishes number, state,
   gender. Make glosses agree with the word's own morph (plural →
   "vanities", construct/absolute forms) without breaking the
   lemma-gloss contract. Eccl 1:2 is the acceptance specimen.
2. **Alignment repair round 2.** Attack the span-boundary class (184 on
   gold) with the same discipline as round 1: prototype on a copy,
   gate = precision ≥ 0.7984 AND H3068 drift 0, application is Kit's
   ruling. First expand the gold set beyond 30 verses so round 2 is not
   tuned to the same verses round 1 was.
3. **Lexicon depth.** lemma_default quality pass; per-occurrence variant
   renderings; word-card grammar presentation (parse spelled out, not
   just the morph code). Feeds both the site and the app.

### Addendum (2026-11-03, Kit): resolve the Elohim class by form

Kit: "Waters and Egypt and the third dual pair use the transliteration
to resolve the Elohim plural." Reading (his confirmation pending on the
third item): the plural-form / singular-sense nouns — Elohim, mayim
(waters), Mitzrayim (Egypt), and a third -ayim dual (best reading:
shamayim, heavens; other candidate: Yerushalayim) — are to be resolved
by their transliterated **form** (the recognizable -im / -ayim shape),
not by the morphology number tag. Corpus evidence for why the tag
cannot do it (verified 2026-11-03): Elohim is tagged plural 2,577x;
mayim plural 562x; shamayim is split (dual 7x / plural 413x);
**Mitzrayim and Yerushalayim carry no noun number tag at all** (635 /
643 occurrences, number NULL). The form is uniform where the tag is
absent or inconsistent. Mechanism when built: a form-keyed registry of
sense-number (elohim/mayim/mitzrayim/shamayim -> singular sense) that
the gloss layer consults before morph number; true body-pair duals
(eynayim eyes 762, yadayim hands 249, raglayim feet 166 — the three
most frequent dual lemmas) resolve to ordinary English plurals.

## Prong 2 — Greek: the Septuagint (LXX)

No Greek data exists in the corpus yet (`sources/` holds dss, morphhb,
peshitta, sp only). The LXX is a *translation witness* to a Hebrew text
older than the MT — in product terms it can join SP/DSS/Syriac as a
witness, and/or stand as a full Greek interlinear track.

Source audit (web-checked 2026-11-03; license is step 1, per the
project's public-domain / openly-licensed-only rule):

- **CenterBLC/LXX (Text-Fabric)** — Rahlfs 1935 + morphology/features,
  built on Eliran Wong's RLXX1935 dataset. Same Text-Fabric pipeline
  family we already run for SP, DSS, and Peshitta (tf-venv) — the
  natural primary candidate. **License must be verified on the repo
  before any load** (Wong datasets are often CC BY-NC-SA; the SP corpus
  we loaded is CC BY-NC 4.0, so NC terms have precedent, but SA would
  be new — KIT decision if it comes to that).
- **CATSS / CCAT LXX** — the scholarly morphological standard, but
  **not freely licensed** (user-declaration gate). Excluded as a load
  source under our rule; its Hebrew–Greek parallel alignment is the
  reference design for our own MT↔LXX alignment, not a dataset we take.
- **Swete's edition** — public-domain text; an openly licensed
  morphologically tagged Swete is still "under development" elsewhere.
  Fallback = text only, no morphology.
- **Brenton's English LXX (1844)** — public domain. The natural English
  bridge for a Greek computed-rendering layer, playing the role KJV/YLT
  play for the Hebrew side.

Structural facts the build must absorb (not optional):

**Rulings (Kit, 2026-11-03):** canon scope = **the full Greek canon,
deuterocanon included**. Daniel: **whichever tradition matches the
role that was found** — Kit's gloss: the archaeological cylinder (the
Nabonidus cylinders, Ur 1854) found Belshazzar's role — eldest son,
co-regent, second in the kingdom — which is why Daniel was made
*third* ruler (Dan 5:29), exactly as his printed King James reads; the
discovery vindicated the KJV's Daniel. The Greek Daniel matching that
found, MT-shaped Daniel is **Theodotion (DanTh)** — primary; the Old
Greek (Dan) is carried as the alternate tradition.

- **Verse crosswalk.** LXX numbering differs from MT (Psalms are offset
  by one through most of the book; Jeremiah's chapters are reordered and
  shorter; Daniel carries additions). A verse-mapping table is a
  deliverable in its own right, before any display.
- **Canon scope — KIT.** LXX includes books with no MT counterpart
  (the deuterocanon). Options: (a) MT-canon books only, aligned to our
  verses; (b) full LXX including deuterocanon as Greek-only books.
- **Product role — KIT.** (a) Witness layer: LXX rows in
  `witness_verses` / `word_variants` beside SP/DSS/Syriac (verse-level
  first, like Syriac). (b) Full Greek track: Greek words table, G-number
  lexicon, Greek interlinear view parallel to the Hebrew one. (a) is a
  campaign like the variants campaign; (b) is a second corpus.
- **Greek lexicon.** Strong's Greek (G) numbers + a public-domain/open
  lexicon source, audited the same way; Greek morphology codes differ
  from the Hebrew OSHB codes and need their own presentation mapping.

## Suggested sequence

1. Prong 1 item 1 (morph-aware gloss) — small, already scoped, fixes a
   bug Kit has seen in the app.
2. LXX source/license audit in earnest (fetch CenterBLC/LXX, read its
   license + feature list, census books/verses/words) → report, then
   Kit rules on canon scope and product role.
3. Prong 1 items 2–3 (gold expansion, repair round 2, lexicon depth)
   in parallel with the LXX witness build once 2 is ruled.
