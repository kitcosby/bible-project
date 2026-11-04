# Variant alignment bridges — commissioned 2026-11-03 (Kit)

Kit's ruling: "The variants need their own translations" → after specimens
and options, Kit chose **the full alignment bridges per tradition**
(deeper, slower) over the Strong's-copy shortcut and over gloss chains.

## What a bridge is here
For each non-base tradition, per-word English phrases in two flavors
(KJV and computed Young's), built the way the TR bridge was built:
anchor on what is known, align the whole verse, inherit/assign phrases,
label everything COMPUTED. The app then renders a variant verse's
sentence from ITS OWN tradition's phrases, following the reader's
KJV/Young's base toggle.

## Method (mirrors build_nt_align.py's two-step philosophy)
1. **Greek↔Greek alignment** of the tradition's words to the TR words
   of the same verse (Needleman-Wunsch):
   - Byzantine: scorer = Strong's equality (2.0), form equality (1.5).
   - SBLGNT: scorer = accent-stripped form equality (2.0), then
     lemma/gloss-token overlap (1.0). (SBL carries no Strong's.)
2. **Inheritance**: an aligned tradition word takes the TR word's KJV
   phrase (CrossWire alignment) and computed-Young's phrase
   (gnt_ylt_renderings) wholesale.
3. **Residue pass**: tradition words with no TR pair (additions,
   substitutions) are aligned to the verse's leftover English tokens
   (tokens not consumed by any inherited phrase) with a gloss-token
   scorer; still-unmatched words get NO phrase (honest gap, gloss
   shows in the frame).
4. Verses where the tradition is absent produce no rows (the absence
   itself is the data, already in gnt_variants).

## Tables (new; TR tables untouched)
- `gntb_alignment` (corpus_verse_id, kjv_pos, gntb_position) — KJV links
- `gntb_ylt_renderings` (gntb_verse_id, gntb_position, ylt_word,
  ylt_word_pos, label 'ylt-bridge-byz')
- `gnts_alignment`, `gnts_ylt_renderings` — same shapes for SBL.

## Evaluation (the gate discipline, adapted from the OT bridge)
- **Self-consistency**: on verses gnt_variants calls 'same', the bridge
  must reproduce the TR phrases ~exactly (target: ≥ 99% of words with
  identical phrase assignment; deviations investigated, not waved).
- **Silver standard** (Byz): occurrence-ordered Strong's phrase-copy —
  the bridge must agree with it wherever the silver is unambiguous,
  and its disagreements are sampled and hand-read.
- **Hand gold**: ~8 variant verses read by hand against the Greek
  (1 John 5:7–8, Matt 17:21, John 5:4, Acts 8:37 [absence], Mark
  16:19–20, Rom 14:24–26 [Byz extra], Luke 23:34?, Rev 22:19) —
  content words must carry the right phrase.
- Precision floor: the OT bridge's standing standard, **≥ 0.7923**,
  measured the same way (exact 2 / stem 1.5 / fuzzy 1 scoring against
  the silver+gold references); a tradition that misses the floor does
  not ship.

## Sequence
1. Byzantine bridge (this plan's first build) + evaluation.
2. SBL bridge + evaluation.
3. OT scope decision: Samaritan is a full Hebrew text in the SP
   Text-Fabric data — a bridge needs the SP loaded as verses (new
   load) aligned to MT words; DSS bridges only the 4,202 fully
   attested verses (Kit's standing scope). Kit rules after NT lands.
4. API + app: verse payloads gain per-tradition phrase maps; Study
   sentence under a variant default renders from the tradition's own
   phrases (base toggle picks the flavor); frames show the tradition's
   own KJV/Young's in the Translation select.

## Status
- 2026-11-03: commissioned; plan written.
- 2026-11-03: **Byzantine bridge BUILT and WRITTEN** (build_gntb_bridge.py;
  backup bible_v2.db.bak-gntb-bridge-pre; PG synced, counts equal).
  gntb_alignment 200,422 rows; gntb_ylt_renderings 141,902 rows.
  Gates: same-verse self-consistency 7,560/7,560 = 100% (sampled every
  15th 'same' verse); silver agreement on variant verses
  15,033/15,264 = 98.49% (floor 0.7923). Coverage: KJV phrases for
  132,755/140,149 Byzantine words (94.7%); computed-Young's for
  106,433 (75.9% -- bounded by the TR bridge's own 76.2% ceiling).
  Hand-read disagreement sample: silver occurrence ambiguity (Matt
  7:2), word-order swaps a monotone aligner cannot cross -> honest
  gaps (Matt 15:5, 21:14), article-folding near-misses. No systematic
  garbage found. Known thin spot: YLT flavor at Comma-type verses
  (1 John 5:7 gets only 'are') -- inherited from the TR bridge's own
  sparse mapping there, not a Byzantine-side defect.
- 2026-11-04: **SBLGNT bridge BUILT and WRITTEN** (build_gnts_bridge.py;
  backup bible_v2.db.bak-gnts-bridge-pre; trial run on a DB copy
  first, live output identical). gnts_alignment 191,378 rows;
  gnts_ylt_renderings 135,971 rows (label 'ylt-bridge-sbl'). Scorer
  per this plan: accent-stripped form equality 2.0, then lemma /
  gloss-token overlap 1.0 (no Strong's scorer reused; gloss tokens
  from lxx_words by Greek form for SBL, by Strong's for TR). Gates:
  same-verse self-consistency 41,441/41,441 = 100% over ALL 2,718
  SBL 'same' verses (target >=99%); silver agreement on variant
  verses 71,125/71,972 = 98.82% (silver = occurrence-unambiguous
  form copy; floor 0.7923). Coverage: KJV phrases for
  126,556/137,554 SBL words (92.0%); computed-Young's for 101,981
  (74.1%) — cf. Byz 94.7% / 75.9%. Hand gold read against the Greek:
  1 John 5:7-8 correct (Comma absent), Matt 17:21 / John 5:4 /
  Acts 8:37 absent -> zero rows, Mark 16:19-20 correct, Rev 22:19
  'tree' (xylou) honestly unphrased rather than inheriting 'book'.
  FK check: 176,042 violations before and after, all pre-existing
  in kjv_words (NT G-Strong's absent from the H-only strongs
  table); the bridge tables add 0. TR/Byz/OT tables hash-identical.
  Sync: export route extended + loaders written, CSV counts ==
  SQLite; the PG load itself is the laptop ship step (Kit's
  authorization), not yet run.
- Next: API + app surfacing; PG load of both bridge pairs at the
  next authorized laptop ship.
