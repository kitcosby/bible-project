# CodeSnack brief — New Testament support in BibleApp-pwa

You already know this project (see ONBOARDING_PROMPT_CODESNACK.md —
everything there still holds). New workstream: **the corpus is being
extended to the New Testament**, and your share is the client side of
`kitcosby/BibleApp-pwa`. Muse (the other agent) owns the corpus,
the Lampy API, and this brief; Kit owns the decisions. Work in small
commits on `main`, no dependencies, no build step, bump the service
worker cache version on every user-visible change.

## What is happening on the server side (Muse's share, in progress)

- The Hebrew OT corpus (39 books) gains the 27 NT books
  (book_id 40–66, KJV order: Matthew … Revelation).
- KJV and Young's (YLT) are being extended to the NT from the same
  sources as the OT (CrossWire KJV module with Strong's; ebible.org
  YLT USFM) — both public domain.
- A Greek NT word layer is being loaded mirroring the LXX tables
  (verse text assembled from word surfaces; per-word lemma, Strong's
  G number, gloss, SBL transliteration, morphology). The primary
  Greek text is Kit's ruling (pending); treat the text basis as a
  labeled field, never hard-code an edition name into UI copy.
- The LXX Greek layer (57 books) is likewise being synced to the API.

## API contract you can build against (draft — Muse confirms on ship)

Same three bases, same probe order, same 404 rule
(`{"error": "not found"}` is authoritative) as the current app.

- `/api/books` will return 66 books; NT entries carry
  `"testament": "NT"` (OT entries gain `"testament": "OT"`).
- Verse/chapter payloads for NT books carry the same fields as OT
  (`kjv_sentence`, per-word `kjv` / `ylt` / `gloss`) **plus**, for the
  Greek track, a `greek_words` array mirroring the LXX word shape:
  `{position, surface, lemma, strongs ("G…"), gloss, translit,
  morphology fields}`. Greek is the original language of the NT — in
  Study view the Greek words are the primary frames for NT verses,
  with the same choice → Young's-computed → gloss precedence applying
  to English renderings of Greek words once the computed layer ships;
  until then, NT Study shows the Greek frames with their dictionary
  gloss and the KJV/Young's verse text below, honestly labeled.
- Word pages work for G numbers exactly as for H numbers
  (`#/word/G2316/…`); the existing context-navigation (prev/next word,
  return-to-verse strip) must work unchanged for NT verses.

## Your tasks (in order; stop after task 1 and report)

1. **Canon readiness.** Extend the book canon to 66 books: the Home
   table of contents and the Read splash list both testaments
   (OT 39 / NT 27, KJV order and names). NT books whose data the API
   does not yet serve must render the existing honest fallback
   (labeled sample / not-yet-loaded state) — never fabricated text.
2. **Greek-track Study view.** When a verse payload carries
   `greek_words`, render Study frames from the Greek words (Greek
   surface in the frame, transliteration under it, gloss as the
   default English line), reusing the existing frame machinery.
3. **G-number word cards.** Word pages for Strong's G numbers:
   same layout as H cards, occurrences list, context navigation.

## Hard rules (unchanged from onboarding)

- No invented biblical data. If the API 404s or is unreachable, the
  labeled sample fallback is the only substitute, exactly as today.
- Young's is always labeled **computed** wherever it appears.
- The Greek verse text is *assembled from word surfaces*; do not
  describe it in UI copy as a printed edition's text.
- Do not touch `kitcosby/BibleApp` (private scaffold) or
  `kitcosby/bible-project` (reference only).
- If the shipped API payload differs from this draft contract, follow
  the payload and flag the difference in your commit message.

## First reply

Confirm back: (a) the 66-book canon order you will use, (b) where
the testament split lives in the TOC/splash, (c) that NT books with
no API data yet will show the honest fallback. Then do task 1 only,
and wait.
