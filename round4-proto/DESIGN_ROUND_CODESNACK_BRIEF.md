# CodeSnack brief — design round (audit items 5–10), 2026-11-03

You audited the live Study page (Genesis 1:1, 430×932, service worker
off) and proposed fixing design items 5–10 in the app. Kit has given
the go. The data items from that audit (1, 3, 4) were Muse's and are
done; item 2 (Study sentence order) was Kit's call and is also done.
This brief is only the design round.

## Step 0 — sync first (do not skip)

Your audit baseline was `b16f0e3` (byot-v9). The repo has moved three
releases since. **Pull `main` to `97c55fe` (byot-v12) before touching
anything** and confirm the HEAD in your report. What changed since
your baseline — do not regress any of it:

- **byot-v10** — Study sentence rebuilt: the verse's actual Young's
  text with the reader's choices substituted at each word's own
  Young's phrase (`yltSubstHtml`); KJV spans and frame chain are
  fallbacks only.
- **byot-v11** — Base toggle KJV ⇄ Young's on Study and Read
  (`baseStore`, localStorage `byotBase`, `data-act="base"` select in
  the sentence caption and the Read header); KJV base substitutes
  choices on clean anchor runs only (`kjvBaseHtml`).
- **byot-v12** — Word-page Renderings panel is fed by API phrase lists
  (`kjv_phrases`/`ylt_phrases` on `/api/word`, carried as
  `kjvList`/`yltList`), session registry as supplement.

New controls exist since your audit (Base select, Default variant
select). They are in scope for the styling items below — the control
rows must end up consistent *including* them.

## The work (your audit items, restated)

5. **Rendering dropdowns are cut off** at phone width — "Young's
   (computed)" renders as "Young's (compute". Selects must show their
   full selected label at 430 px.
6. **Touch targets too small** — rendering dropdowns ≈19 px tall,
   Prev/Next buttons ≈30 px. Minimum target: **44 px** height for all
   interactive controls (selects, buttons, nav).
7. **Frame grid orphan** — a 7-word verse in 2 columns leaves the last
   frame alone on the right. Fix the grid so the final row doesn't
   strand a single frame awkwardly (your call how: column count,
   span, or centering — state what you chose).
8. **Three references on one screen** — "Study — Genesis 1:1"
   heading, the frame heading "1 Genesis 1:1", and the chapter
   selector all repeat the reference. Reduce to one clear reference;
   the verse frame heading is just the reference (settled: no
   descriptive text there).
9. **Top controls crowded and inconsistent** — four controls in two
   rows, and the Default variant dropdown styled differently from the
   others. One consistent control style (font, height, border,
   padding) across Book/Chapter/Verse selectors, Default variant,
   Base, and the per-card selects.
10. **Frame caption "Translation"** doesn't say which source is in use
    (reader's choice, Young's, or gloss fallback). The caption or the
    control should make the active source plain — without changing
    precedence behavior (Study: choice → Young's (computed) → gloss;
    Read: choice → base version).
11. **System fonts leak in** — some controls computed as Times New
    Roman / Arial. All controls should inherit the app font (Inter).

## Hard rules

- Single-file app (`index.html`) + `sw.js`; **bump the SW cache to
  byot-v13** in the same commit.
- Do not rename `data-act` values, store keys (`byotChoices`,
  `byotVariantDefaults`, `byotVariantWords`, `byotBase`), route
  shapes, or localStorage formats — behavior is settled and tested.
- Do not change precedence rules, the sentence constructions, or the
  variant logic. This round is presentation only.
- Young's is always labeled **computed**; assembled Greek text stays
  labeled assembled. No invented data, no placeholder text.
- No new dependencies, no build step.

## Verify and report

- Test at **430×932**: Genesis 1:1 Study, one NT Study verse
  (e.g. Matt 1:1), one word page, Read Genesis 1.
- Report: before/after measurements for control heights (must be
  ≥44 px), a statement that every select shows its full label, what
  you did for the orphan frame and the repeated references, and a
  regression pass: base toggle flips the sentence, Default variant
  still swaps DSS/Byzantine forms, word-page chips render, custom
  rendering entry still opens its text box.
- Commit to `main` and push; end your report with the commit hash.
  Kit relays reports; Muse verifies against the live deploy.
