# Revelation 9:20 — Three-Reading Apparatus Review

**Date:** 2026-11-07  
**Scope:** External textual evidence for the negative particle before μετενόησαν, and its implications for the YLT profile.

## Finding

The Robinson source parser's group `66:18` contains two source payloads:
- A: `oute 3777 {CONJ-N}` — οὔτε
- B: `ou 3756 {PRT-N}` — οὐ

That two-branch representation is **not an exhaustive textual apparatus**. Independent textual apparatuses record a third reading:
- C (external apparatus): `oude 3761` — οὐδέ

The third reading is not present in the current Robinson parser payload table and has **not** been inserted as a new branch in the shadow database. This report preserves it as external witness evidence rather than silently changing the source parser's record.

## Witness and edition evidence

### Robinson–Pierpont Text-Critical Greek New Testament (2025 PDF; Byzantine Textform 2018 base)

The Revelation apparatus at 9:20 reports:
- οὐ — 73.7%, listed with 𝔐A(16), C, K
- οὔτε — 18.4%, listed with 𝔐A(28), ECM†, ST
- οὐδέ — 4.6%, listed with NA, SBL, TH

This is the distribution in that edition's collation, not a universal census of all extant witnesses. The edition identifies itself as a Text-Critical Greek New Testament based on the Byzantine Textform 2018, compiled and arranged by Maurice A. Robinson and William G. Pierpont.

### Additional apparatus summary

Robert B. Waltz's *Encyclopedia of New Testament Textual Criticism* lists:
- οὐδέ μετενόησαν: P47, א, 046, 61, 69, 2053 (txt), 2344; cited with NEB, Tischendorf, UBS, Weiss, and WH marginal.
- οὔτε μετενόησαν: A, 1, 181, 1611, and additional witnesses; cited with HF marginal, Lachmann, Soden, Tregelles, Vogels, and WH marginal.
- οὐ μετενόησαν: C, Papud, 94, 206, 1006, 1841, 1854, 2351, and others (with 2329 reported as και οὐ μετενόησαν); cited with Bover, Griesbach, HF text, Merk, RV, and WH text.

The apparatus summary's manuscript sigla and abbreviated editorial labels should be checked against its own key before any machine-readable witness normalization. Do not import these strings as if they were fully resolved manuscript IDs.

### Historical commentary

Meyer's *Critical and Exegetical Commentary on the New Testament* (Revelation 9:20) prefers οὐ μετενόησαν, calling it the “only intelligible reading” and citing C, 4, 6, 16, other witnesses, Coptic, Andreas, and Arethas. It contrasts οὔτε, which it associates with the Vulgate, Primas, Cyprian, Elzevir, Bengel, and Lachmann, and notes that א reads οὐδέ.

This is Meyer's nineteenth-century critical judgment, not a substitute for contemporary witness evaluation.

### Printed text examples

- Stephanus Textus Receptus 1550: οὔτε μετενόησαν.
- Scrivener Textus Receptus 1894: οὐ μετενόησαν.
- SBL Greek New Testament: οὐδὲ μετενόησαν.
- Robinson–Pierpont Byzantine Majority Text 2005 / 2018: οὐ μετενόησαν.

This demonstrates that “Received Text” is not a perfectly uniform edition label for this reading. The 1894 Scrivener edition postdates Young's death and cannot, by itself, identify the precise edition behind Young's translation.

## YLT source basis and translation evidence

The preface to Young's Revised Edition states that “The Greek Text followed is that generally recognized as the ‘Received Text’” and says that the translator leaves textual criticism to others rather than silently changing the underlying Greek reading. The same preface is reproduced in a modern reprint of Young's translation; the publisher's note identifies an 1887 revised edition and a later 1898 publisher's revision.

YLT Revelation 9:20 reads: “neither did reform from the works of their hands”. That English “neither” is compatible with οὔτε and is also a possible idiomatic rendering of οὐ or οὐδέ in context. The wording alone cannot identify the exact Greek source edition.

The Received-Text statement makes the TR reading οὔτε a serious candidate for the YLT profile, particularly because Stephanus 1550 and Elzevir are reported with οὔτε. It does **not** prove that Young used that exact edition at Revelation 9:20. A source-edition-level identification remains open.

## Sequence and alignment consequences

All three readings are one Greek token at position 13:
- A οὔτε
- B οὐ
- C οὐδέ

A deterministic alternative-sequence comparison confirmed:
- Token-count delta for A, B, and C: **0**.
- Only changed position relative to the current B sequence: position 13.
- Positions 14–49 remain unchanged.
- All 15 applied phrase-member endpoints remain positionally stable under all three readings.

Thus the 15 phrase groups for “did reform”, “may bow before”, “those of [material]”, and “to see/hear/walk” do not need positional remapping for any of these three readings. The directly affected alignment remains YLT token 13 (“neither”) ↔ Greek position 13.

The current direct dependency metadata is correct: only the position-13 alignment carries dependency group `66:18`. The YLT sequence profile proposes A for this group, but remains provisional overall because other variant groups still inherit candidate readings. Do not confuse that global provisional status with direct sensitivity of every later token.

## Implications for the YLT profile

- **Established:** Young's revised-edition preface says that his Greek text followed the generally recognized Received Text.
- **Established:** the source parser's local A/B alternatives do not exhaust the external apparatus; οὐδέ is also attested.
- **Established:** the three readings are each one token and do not shift the 15 phrase endpoints.
- **Plausible but not proven:** YLT's “neither” may reflect a Received-Text οὔτε reading.
- **Not established:** the exact TR edition Young used for this verse, or that his English wording uniquely identifies οὔτε rather than οὐδέ/οὐ.
- **Database action:** none for the external οὐδέ reading. It remains an apparatus note; do not add a third source branch without a provenance-preserving design decision.

## Recommended next step

Inspect Young's 1862/1887 printed Greek-text source or his *Concise Critical Commentary* for Revelation 9:20, if recoverable. Until that source edition is identified, keep the YLT profile's branch selection provisional and preserve the external οὐδέ reading in the study guide. If a future schema supports external witness alternatives separately from Robinson parser branches, represent οὐδέ there rather than rewriting the raw Robinson branch payloads.

## Sources

1. Young's preface, Revised Edition, especially the statement of the Received Text basis: https://logosapostolic.org/bibles/youngs_literal_translation/youngs_preface.htm
2. Robinson–Pierpont, *The New Testament in Ancient Greek with critical text notes*, Revelation 9:20 apparatus; edition statement and Byzantine Textform 2018 basis: https://ebible.org/pdf/grctcgnt/grctcgnt_REV.pdf
3. Waltz, *The Encyclopedia of New Testament Textual Criticism*, Revelation 9:20 apparatus: https://mnheritagesongbook.net/wp-content/uploads/2013/07/encyclopedia_nt_tc_final.pdf
4. Meyer, *Critical and Exegetical Commentary on the New Testament*, Revelation 9:20: https://www.truthaccordingtoscripture.com/commentaries/hmc/revelation-9.php
5. SBLGNT Revelation 9:20: https://biblia.com/bible/sblgnt/revelation/9/20-21
6. Stephanus Textus Receptus 1550: https://biblia.com/bible/tr1550mr/revelation/9/20-21
7. Young's Literal Translation Revelation 9:20: https://biblia.com/bible/ylt/revelation/9/20-21

No production data was changed. The only database change in this audit series remains the shadow-only correction of direct variant-dependency metadata described in [REVELATION_9_20_VARIANT_DEPENDENCY_AUDIT_20261107.md](REVELATION_9_20_VARIANT_DEPENDENCY_AUDIT_20261107.md).

## Subsequent YLT-profile proposal (2026-11-07)

After reviewing Young's preface and pre-1888 Received-Text editions, the isolated YLT profile now proposes branch A (οὔτε) for group 66:18. Stephanus 1550 and Beza 1598 both read οὔτε at this point; the YLT reads “neither did reform”. This is a strong profile-specific proposal but not final because Young's exact printed edition is unknown and the wider apparatus also records οὐδέ. See [REVELATION_9_20_YLT_BRANCH_A_PROPOSAL_20261107.md](REVELATION_9_20_YLT_BRANCH_A_PROPOSAL_20261107.md) and [v14 validation](FINAL_VALIDATION_AFTER_RE9_20_YLT_BRANCH_A_PROPOSAL_20261107.txt).
