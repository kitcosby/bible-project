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
- 2026-11-03: commissioned; plan written; Byzantine prototype in build.
