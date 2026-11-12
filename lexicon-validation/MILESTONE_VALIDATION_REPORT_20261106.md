# Robinson TR Greek Bridge — Validation Milestone
Date: 2026-11-06
Status: isolated candidate only; production unchanged

## Scope and safety
- Test database: `bible_greek_bridge_test_20261106`
- Candidate schema: `variant_rebuild_test`
- Source repository: `byztxt/greektext-textus-receptus` at `7fd4d02c3e5adebd379ebfbc824040820dde10fc`
- Parser repository: `byztxt/librobinson` at `9acac9fbea409a767e020ff7e39018e43b0f6470`
- KJV source: CrossWire KJV at `d490be7e34762deb2c76cb2c1306d4808e27890d`
- No writes to production `bible` tables, vectorizer configuration, embeddings, API, or frontend were performed.

## Parser equivalence
A Python 3 port of the upstream Robinson parser was compared against the upstream Python 2 parser in first-variant mode. The comparison checked surface, primary Strong's, primary morphology, alternate Strong's, and alternate morphology.
- 7,955 compared verse sequences matched exactly.
- Revelation 17:7–8 were excluded because upstream's documented OLB word-limit workaround suppresses the explicit 17:8 marker and merges its 48-word content into 17:7.
- The isolated candidate preserves the explicit source boundary: Revelation 17:7 has 30 words and 17:8 has 49. Both sequences match the existing stored corpus exactly. The candidate's 17:8 override is intentional and documented in the run metadata.
- One empty-verse key difference exists at Luke 17:36; both parser outputs contain no words for that reference, so there is no token-sequence difference.

## Confirmed repair of the two reported defects
- John 9:21: candidate has 24 Greek positions; YLT “shall” and “speak” map to `λαλησει` at position 24, while “himself” maps to `αυτου` at position 23.
- Colossians 4:10: candidate has 21 Greek positions; YLT “him” maps to `αυτον` at position 21.
- Candidate alignment has zero out-of-range rows and zero orphaned YLT renderings.

## Whole-corpus comparison
- 7,957 verse sequences compared.
- 205 verses changed: 189 associated with variant groups and 16 without variant groups.
- 164 verses have a different word count; 7,793 retain the same word count.
- 2,118 word positions changed: 1,865 positions are present in both sequences but differ, 251 are old-only, and 2 are candidate-only.
- All 16 no-variant differences were inspected. Fifteen are old-parser splits of alternate Strong's/morphology analyses into false extra word positions; the candidate retains them as alternate analyses on the same lexical token. The remaining case is Revelation 7:4, where the old data misread the Greek numeral `ρμδ` as a separate numeric token and lost part of its Strong's sequence. The candidate's representation agrees with the upstream parser comparison.
- These are parser/data-model corrections, not variant-selection decisions. Production schema/API compatibility for the alternate-analysis fields still needs review.

## Source-evidence comparison
Using CrossWire KJV `src` positions with `lemma.TR`, Strong's, and Robinson morphology:
| Metric | Existing | Candidate |
|---|---:|---:|
| Source pairs | 133,255 | 133,255 |
| In-range positions | 133,253 | 133,255 |
| Lemma matches | 131,396 | 133,255 |
| Strong's matches | 131,411 | 133,188 |
| Morphology matches | 131,097 | 132,852 |
| All available fields match | 130,932 | 132,786 |
| Out-of-range positions | 2 | 0 |

Per-verse comparison across 7,940 verses with source pairs: 197 improved, 7,743 unchanged, zero worsened. Net increase under deduplicated source-position comparison: 1,859 lemma matches and 1,854 all-available-field matches (primary Strong's and morphology). This is an in-sample source-evidence comparison, because the same KJV source evidence informed branch selection; it is strong consistency evidence, not an independent textual witness.

## Variant decision quality
- 261 raw variant groups were organized into 245 connected components.
- 228 components had a unique best deterministic source-evidence score.
- 17 exact ties remain unresolved. Their 360 Greek word positions are marked unresolved and excluded from automatic alignment/rendering; both alternatives remain stored in `variant_groups`.
- Runner-up metrics were recomputed. None of the 228 selected choices is worse than its runner-up on any measured dimension (lemma, Strong's, morphology, in-range coverage, or all-field matches).
- 107 components have a one-unit advantage in all-field matches; one has a one-unit in-range advantage. These are weaker margins and should remain flagged for review. The remaining 120 have larger score margins.
- Colossians 4:10–18 is the one context-sensitive component. The candidate selects branch A (151 all-field source matches versus 150 for the runner-up). It remains flagged for manual review because its branches have different verse-context endpoints.

## Preservation proof
Ordered logical-content SHA-256 fingerprints were computed over every `(verse_id, embedding::text)` row and every `(verse_id, text)` row:
- Embeddings: 31,102 rows; SHA-256 `9f18fa61f57a80a575df25125102feaa09e6f7e1b52638b41dd015c11ae039f1`.
- YLT source text: 31,102 rows; SHA-256 `6e0d147ec023c39d10a7d5371cb890141ebae25062ffd45e371a9dc25cdbfdf7`.
- Both fingerprints are identical between production `bible` and restored snapshot `bible_restore_verify_20261106`.
- Vectorizer configuration SHA-256 is `6f0e77ba7d64e6de7c0cfabeca95af810aedac125b27540e2d459d56780ffa5d` in both; model is `nomic-embed-text`, 768 dimensions.
- This verifies logical row content, not raw PostgreSQL page bytes. No embedding generation was invoked.

## Remaining gates
1. Review the 107 one-unit-margin decisions and the 17 unresolved ties; do not treat the entire decision set as human-verified.
2. Manually validate the Colossians 4:10–18 context-sensitive component and the Revelation 17:7–8 override against source provenance and CrossWire.
3. Do not retry Qwen/Gwen on Lampy until a bounded, low-resource inference path is available; the attempted batch was stopped and no model output was accepted.
4. Review how production schema/API will preserve alternate Strong's and morphology without losing existing data.
5. Produce a migration/rollback proposal only after these gates pass. Do not deploy or merge the candidate yet.

## API compatibility audit (read-only)
The live production `gnt_words` schema already has `strongs_aux`, but has no `alt_strongs` or `alt_morph` columns. The live `app_v2.py` currently:
- returns Greek word fields `position, surface, beta, strongs, morph` only, omitting even the existing `strongs_aux`;
- builds Strong's phrase summaries from `gnt_words.strongs` only;
- looks up Strong's occurrences using exact equality on `gnt_words.strongs` only.

A production bridge migration therefore needs an explicit compatibility design: preserve existing primary-field behavior while exposing `strongs_aux` and the new alternate-analysis fields (or a normalized analysis table), then update Strong's lookup behavior and tests. No API files or endpoints were changed.

Unresolved references (book/chapter:verse): John 8:6; Acts 3:3; Romans 16:27; 1 Corinthians 16:24; 2 Corinthians 13:14; Galatians 6:18; Ephesians 6:24; Philippians 4:23; 1 Thessalonians 5:28; 2 Thessalonians 3:18; 1 Timothy 6:21; 2 Timothy 4:22; Titus 3:15; Philemon 1:25; Hebrews 13:25; 1 John 2:23; Revelation 7:3.

## Second-branch parser check
The upstream-equivalence harness was also run in `read_second_variant_only` mode:
- 7,947 compared verse sequences matched exactly, excluding Revelation 17:7–8 for the same documented OLB workaround.
- Thus both first-branch and second-branch token parsing match upstream on their ordinary compared cases. This validates branch parsing separately from the deterministic choice of which branch best fits the KJV source references.

For Colossians 4:10–18, the combined component's best choice is A/A: 151/151 source pairs match lemma, Strong's, and morphology. The runner-up has the same 151 in-range and lemma/Strong's matches but only 150 morphology and all-field matches. The morphology-only branch for Barnabas is `N-GSM` versus `N-DSM`; the evidence favors `N-GSM`. The larger context-spanning group remains explicitly flagged for manual review.

## Qwen/Gwen classifier experiment
The controlled batch classifier test was stopped before completion. Qwen3:0.6b produced no usable output; the earlier Qwen test log was empty, and the new batch remained stuck on its first Qwen request while its local model worker consumed roughly four CPU cores. I stopped the Qwen client processes and the orphaned model worker to avoid leaving Lampy under sustained load; the Ollama service itself remains running. The batch did not reach Gwen. A prior Gwen probe was not reliable: it misclassified a morphology-only case. No LLM output was used to select or validate any reading. Deterministic source checks remain authoritative.

A paired auxiliary-aware audit counted `strongs` plus `strongs_aux` for both datasets and also checked candidate `alt_strongs`/`alt_morph`. It yields 131,413 versus 133,190 Strong's matches and 130,934 versus 132,788 all-field matches (existing versus candidate); the net gains remain 1,777 Strong's and 1,854 all-field matches. Candidate alternate-analysis fields did not add further CrossWire matches. The primary-only table above is retained for apples-to-apples comparison with the existing validator; auxiliary codes and alternate analyses remain preserved as source metadata, not used to inflate primary lexeme matches. 65 primary Strong's and 403 morphology mismatches remain for source-level review.

## Residual source-metadata disagreements
A deduplicated review of the remaining 65 Strong's and 403 morphology mismatches found repeated cross-source patterns, not parser token-boundary errors. Strong's differences are dominated by CrossWire `G4119` versus Robinson `G4183` (and smaller `G3063` versus `G3062` groups). Morphology differences are dominated by tags such as CrossWire `ADV` versus Robinson `PREP`, and `V-ADI` versus Robinson `V-AMI`. The candidate parser reproduces upstream Robinson tags exactly in both first- and second-variant tests. These discrepancies should be recorded as source metadata disagreements and investigated with a proper crosswalk; do not rewrite Robinson values merely to force equality with CrossWire.

A structural review found 19 raw unresolved groups across the 17 unresolved verse references. Fifteen groups are book-subscription/colophon material (typically “written from …” formulas) with no ordinary KJV verse-position evidence; they should remain separately preserved rather than forced into the verse bridge. Three are genuine verse-level presence/absence alternatives with an empty branch: John 8:6, Acts 3:3 (the optional `labein` after `elehmosunhn`), and 1 John 2:23. Revelation 7:3 is a distinct unresolved form/morphology alternative (`sfragizwmen` versus `sfragiswmen`). This supports retaining all 17 references as unresolved instead of guessing.

## Production migration design draft
Created `PRODUCTION_MIGRATION_DESIGN_DRAFT.md` in the audit workspace. It proposes an additive word-analysis child table plus a separate verse-level textual-variant table, backward-compatible API changes, and a staged shadow-validation/rollback sequence. This is a design only: no production DDL, API edits, or merge/deployment actions were performed.

Review artifacts:
- `one_unit_margin_review_packet.json`: all 108 low-margin components, including both alternatives, affected references, selected branch, and best/runner-up metrics (118 raw groups total).
- `unresolved_group_review.json`: all 19 raw unresolved groups with alternative previews, token counts, and context flags.

YLT alignment coverage in the validation report rises from 76.2141% in the existing bridge to 76.3433% in the candidate. The candidate retains 142,978 YLT rendering rows and has zero orphan renderings; this coverage improvement is modest and should be interpreted alongside the 17 unresolved references rather than as a standalone quality measure.


## Follow-up review addendum (2026-11-06)

### Low-margin accounting verified
The actual one_unit_margin_review_packet.json contains 108 components, 118 raw groups, and 116 listed affected-reference entries. Of the 108 components, 107 have a one-unit advantage in all-field matches and one has a one-unit advantage in in-range coverage. All remain flagged; alignment score is not independent textual-critical proof.

A word-record-aware triage of the 118 raw groups classifies 38 as surface-only, 69 as surface-plus-metadata, 7 as token-count differences, and 4 as metadata-only. The seven token-count cases include two Mark 8:24 omissions, two Acts split/compound alternatives (10:2 and 24:16), Romans 16:20 Amen insertion, Colossians 4:10–18 main-text-versus-subscription branch, and 2 Peter 1:1 pronoun insertion. This is triage only; it does not establish a textual reading verdict.

### Colossians 4:10–18 clarification
The component contains groups 5 and 6. Group 5 is barnaba with N-GSM versus N-DSM; the selected genitive is grammatically supported by the genitive apposition “cousin of Barnabas” and matches the CrossWire Robinson morphology tag. Group 6 spans 4:10–4:18: branch A contains the main-text continuation through 4:18, while branch B contains the epistolary subscription (“written from the Romans through Tychicus and Onesimus”). The branches have different endpoints, which explains the context-sensitive flag. This is a source-structure/paratext distinction, not a local lexical alternative. Keep the subscription as paratext and do not force it into verse words. The 151-versus-150 all-field score difference is attributable to the Barnabas morphology difference, not proof that the subscription belongs in the verse bridge.

### Revelation 17:7–8 boundary
The Robinson source explicitly contains 17:8 at parsed source line 2268. The upstream parser's OLB workaround suppresses the explicit 17:8 marker because of the legacy per-verse word limit. In the faithful decision data, variant group 32 selects branch B for 17:8; the candidate retains the 17:8 header and matches 50/50 CrossWire source-position pairs (lemma, Strong's, and morphology). This supports retaining the explicit 17:8 boundary in the bridge, while documenting that the result is a deliberate compatibility override rather than literal upstream parser behavior.

### Production key structure confirmed
Read-only production schema inspection confirms:
- gnt_words primary key is (gnt_verse_id, position).
- gnt_verses primary key is (gnt_verse_id).
- No foreign-key constraint is declared on gnt_words or gnt_alignment.
- gnt_alignment primary key is (corpus_verse_id, kjv_pos, gnt_position).
The migration design now specifies the confirmed composite key for the word-analysis child table. No production DDL or data changes were made.

### Parser equivalence counts reconciled
The two totals are from separate parser modes, not contradictory reruns:
- First-branch mode: 7,955 compared verse keys, all exact.
- Second-branch mode: 7,947 compared verse keys, all exact.
Both exclude Revelation 17:7–8 because upstream applies its documented OLB workaround while the candidate preserves the explicit 17:8 boundary. The compared-key counts differ because selected branches can leave different empty verse keys; first-branch mode has an upstream-only empty Luke 17:36 key, while second-branch mode has no such key. The candidate's only extra second-branch key is the intentionally preserved Revelation 17:8, which is excluded from direct equivalence. No content mismatches were found in either compared set.

### Updated review artifacts
- review_low_margin_summary.py — reproducible packet accounting and preliminary alternative-shape triage.
- inspect_col_decisions.py, query_col_groups.py — Colossians source-branch review.
- inspect_revelation17.py, inspect_revelation17_decisions.py — Revelation 17 boundary review.
- inspect_production_keys.py — read-only production key/constraint inventory.
- PRODUCTION_MIGRATION_DESIGN_DRAFT.md — updated with confirmed key and source-structure notes.


### Representative residual metadata patterns inspected
The source-metadata mismatch audit reproduces repeated, surface-consistent cross-source differences:
- Strong's: CrossWire commonly expects G4119 where the Robinson candidate stores G4183 on forms such as πλειον; a smaller repeated family expects G3063 where Robinson stores G3062 on λοιπον.
- Morphology: repeated CrossWire V-ADI-3S / V-ADI-3P versus Robinson V-AMI-3S / V-AMI-3P occurs on forms of αρχομαι such as ηρξατο / ηρξαντο. Another repeated family classifies forms such as απεναντι as ADV in CrossWire but PREP in Robinson.
These are systematic tagging/lexicalization disagreements between source conventions. The Robinson candidate reproduces upstream Robinson metadata in parser-equivalence tests. Do not globally rewrite Strong's or morphology to force equality; build a documented per-source crosswalk only if downstream consumers require one.

- low_margin_word_record_triage.json — 118 raw groups classified using lexical word-record parsing rather than whitespace token counts.


### Decision status must distinguish algorithmic selection from editorial review
The candidate's resolved label denotes a unique best deterministic score, not human textual-critical approval. This applies to all 228 selected components, not just the 108 low-margin components. The production model should store selected branch and review status separately (for example algorithmically_selected, human_reviewed, unresolved, not_applicable_to_verse_alignment), along with scoring method/version and reviewer provenance. No selected branch should be presented as editorially settled merely because its score is unique.


### Manual source-pair inspection of the seven token-count groups
The CrossWire OSIS mappings explain the candidate's alignment choices but do not independently establish the underlying textual readings:
- Mark 8:24 has two groups. The KJV maps “as” to the Greek source positions for oti and ws, and maps “I see” to blepw; it has no source position for the optional orw. The candidate therefore keeps oti and omits orw to preserve the KJV source-position sequence. This is an alignment-driven omission and needs an independent Greek witness before it can be treated as a textual decision; the English translation may omit a redundant Greek verb.
- Acts 10:2 and 24:16 map “alway/always” to one source position for diapantos. The candidate's compound form keeps the single Greek position; the split dia + pantos branch changes the token count. This supports bridge alignment, not independent textual criticism.
- Romans 16:20 maps the closing “Amen” to a distinct source position; the candidate includes the optional amhn.
- 2 Peter 1:1 already contains a common hmwn at Greek position 17, mapped to “our.” The optional branch would add a second hmwn; the candidate omits the duplicate.
- Colossians 4:10–18 is the main-text continuation versus epistolary subscription case described above; the subscription is paratext, not a verse-word alternative.

The candidate's branch choices are internally consistent with CrossWire source positions. That establishes compatibility with this bridge source, not an independent verdict on Robinson's textual alternatives. In particular, Mark 8:24 should remain flagged for external witness review.


### Mark 8:24 — external witness review identifies a correlated-reading risk
The candidate selects ὅτι present (group 12 A) and ὁρῶ absent (group 13 B), producing a hybrid combination. This combination maximizes the CrossWire KJV source-position score: KJV “as” maps to positions 7–8 (ὅτι, ὡς), “trees” to 9, and “walking” to 10; there is no source position for ὁρῶ.

However, the external apparatus consulted lists substantially overlapping witness groups for ὅτι and ὁρῶ: major witnesses attest both, while a prominent shorter group (including D and W) omits both. Cambridge commentary likewise reports major witnesses with both and D omitting both. The consulted sources do not document the candidate's hybrid among the principal witness groupings. This does not prove that no manuscript supports the hybrid, but it makes the automatic A/B choice textually unsafe. Keep the groups, flag the component algorithmically_selected / needs_review, and do not present the hybrid as a settled Robinson reading.

The source-selection algorithm already joins groups sharing a verse into one scoring component, but it does not constrain the combinations to attested witness bundles. This is a separate gap: joint optimization is not the same as preserving correlated manuscript readings. Add correlated-reading/witness-bundle provenance to the migration design. If the hybrid is needed only to reproduce the KJV source-position map, label it as a KJV-alignment profile.

Detailed review: MARK_8_24_VARIANT_REVIEW.md. External sources consulted: greeknewtestament.net Mark 8:24 apparatus; Cambridge Greek Testament commentary excerpt reproduced at Lemma; Meyer commentary. The apparatus sources are supporting secondary/online references; primary manuscript collation remains the next verification gate.


## YLT-specific branch validation — new critical findings

### Mark 8:24
The stored YLT text reads “I behold men, as I see trees, walking.” The candidate's current branch combination is group 12 A / group 13 B: it includes ὅτι but omits ὁρῶ. The candidate Greek sequence therefore lacks the second seeing verb that YLT explicitly translates, and its rendering table has no Greek-word rendering for that second “I see” phrase. The CrossWire KJV positional map has no source position for ὁρῶ, which explains the KJV-driven omission but does not justify it for YLT. The external apparatus consulted presents the principal witness clusters as both words present or both absent; the candidate hybrid is not represented in those principal groupings. Proposed YLT profile: A/A, pending full apparatus review.

### 2 Corinthians 7:12
The stored YLT text reads “our diligence in your behalf.” The candidate selects group 4 A / group 5 A, yielding σπουδὴν ὑμῶν ... ἡμῶν (“your ... us”). The candidate's YLT rendering table maps “our” to position 20, surface ὑμῶν, Strong's G4771 (second-person plural), while ἡμῶν (G1473, first-person plural) is not the Greek word assigned to “our.” This is a direct semantic alignment error.

The YLT wording corresponds to the alternate group 4 B / group 5 B: σπουδὴν ἡμῶν ... ὑμῶν (“our ... your”). The KJV English “our care for you” also corresponds to that reading. Scrivener's Textus Receptus 1894 prints ἡμῶν ... ὑμῶν, whereas Nestle, Westcott-Hort, RP Byzantine and Greek Orthodox 1904 print ὑμῶν ... ἡμῶν. The CrossWire KJV OSIS lemma.TR mapping follows the latter sequence even though its English KJV wording follows the former. This may reflect a different Greek base in the annotation layer; in either case, CrossWire lemma.TR cannot be treated as the authoritative Greek text behind the KJV English or the YLT.

Proposed YLT profile: B/B, retaining A/A as a distinct textual alternative. No database changes made.

### James 4:13 control
The stored YLT reads “To-day and to-morrow we will go ...”; the candidate selects και (“and”). KJV English reads “To day or to morrow,” while the CrossWire lemma.TR field maps και. The candidate choice is consistent with YLT but not the KJV English conjunction. This is a control example confirming that target-translation profiles must be distinct.

### Implication for the selection method
The deterministic selection method optimizes agreement with CrossWire KJV src/lemma.TR/Strong's/morphology. It does not independently determine which Greek reading the YLT translator followed. In at least Mark 8:24 and 2 Corinthians 7:12, the KJV-derived selection conflicts with the stored YLT wording. The branch decision must therefore be translation-profile-specific. Preserve all source alternatives and store separate YLT and KJV alignment profiles rather than one universal selected branch.

New artifacts:
- YLT_TRANSLATION_VARIANT_REVIEW.md — detailed source and translation comparison for Mark 8:24, 2 Corinthians 7:12, and James 4:13.
- YLT_TRANSLATION_OVERRIDE_PROPOSAL.json — proposed YLT-specific branch choices; not applied.
- low_margin_ylt_review_packet.json — all 108 low-margin components with YLT verse text, candidate Greek words, current YLT rendering rows, branch alternatives, and score metrics.


## YLT-specific variant profile review (2026-11-06)

Reviewed all 108 low-margin components / 118 raw variant groups across 116 YLT verse contexts. Added YLT_LOW_MARGIN_COVERAGE_AND_TRIAGE.md and YLT_TRANSLATION_OVERRIDE_PROPOSAL_REVIEWED.json; the original proposal file remains unchanged.

The current YLT rendering table is KJV-mediated (YLT token → KJV token → Greek positions), not independent YLT lexical evidence. Across the packet, 3,076 YLT tokens were counted; 2,101 (68.3%) have a Greek-position row, 975 do not, and 389 mapped YLT tokens link to multiple Greek positions. These are coverage diagnostics, not quality scores. Mark 8:24 and 2 Corinthians 7:12 are direct examples of omitted/misassociated YLT wording.

Mechanical branch-payload classification: 39 primary Strong’s changes, 38 surface-spelling changes, 34 morphology/auxiliary changes, 4 presence/absence alternatives, and 3 token-count changes. Classification is not a textual verdict.

The reviewed proposal records 13 YLT-profile changes as not applied, including Mark 8:24 A/A, 2 Corinthians 7:12 B/B, 1 Corinthians 15:31 B, 2 John 1:3 B, 2 Corinthians 11:10 B, Acts 21:8 B (witness-bundle caveat), Acts 26:20 B, Luke 8:31 A, Revelation 11:2 B, Revelation 16:5 B (translation alignment only; not textual priority), Luke 6:9 B, Revelation 7:2 B, and Acts 7:26 A. Two earlier hypotheses were retracted after closer syntax review: Acts 26:18 retains A, and 2 John 1:5 retains A. Acts 15:32 and 19:27 remain unresolved.

No production branch selection was applied. Candidate schema still has 261 variant groups (242 resolved, 19 unresolved). Production YLT source and embedding row counts remain 31,102 each; vectorizer fingerprint recomputed using the original full-config method remains 6f0e77ba7d64e6de7c0cfabeca95af810aedac125b27540e2d459d56780ffa5d. No API, embedding, vectorizer, production DDL, merge, or deployment changes were made.


## Parser equivalence reconciliation (2026-11-06)

A corrected comparison separated first-variant and second-variant modes and stopped treating missing verse keys as empty sequences. First-variant mode has 7,954 common verse keys with 7,954 exact sequences; one additional upstream-only key, Luke 17:36, is an explicit empty first-branch verse and is omitted as a key by the port. Second-variant mode has 7,947 common verse keys with 7,947 exact sequences. Both runs exclude Revelation 17:7–8 under the documented upstream OLB workaround. The earlier first-mode count of 7,955 exact was inflated by the comparator's missing-key default; there are zero differing common sequences in either mode. See PARSER_EQUIVALENCE_RECONCILIATION.md and parser_equivalence_corrected_summary.json.

## YLT shadow profile artifact (2026-11-06)

Created YLT_SHADOW_PROFILE_v0.1.json with raw alternatives and profile-specific status for all 118 low-margin groups: 15 proposed branch selections across 13 references, 2 prior hypotheses retracted, 2 held unresolved, and 99 not yet decided. No KJV candidate selection is inherited by default. The profile is a pure-JSON research artifact and is not applied to the candidate or production database.