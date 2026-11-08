# Hebrew vowel-only variants: study guide and interpretation rules

**Date:** 2026-11-07  
**Status:** Research guide for the 3,349-group inventory; not a lexical merge proposal.

## 1. What the link means

A Hebrew or Aramaic form belongs to a vowel-only candidate group when its pointed form has the same strict non-vowel signature as at least one other distinct pointed form in the same language population.

For the current inventory, pointed forms are NFC-normalized **for comparison keys only**, then only U+05B0–U+05BB and U+05C7 are removed. Every other codepoint is retained. This includes consonants, matres lectionis, final forms, dagesh/mapiq, meteg, maqaf, paseq, shin/sin dots, rafe, cantillation, sof pasuq, separators, and slash morpheme delimiters. Hebrew and Aramaic groups remain separate. Qere/Ketiv records are not ordinary members.

**A match is an orthographic cross-reference, not a claim of shared lexical identity.** It does not prove synonymy, common root, identical morphology, common Strong's number, or identical translation. It must never trigger an automatic merge of roots, lexicon entries, morphology, Strong's assignments, alignments, or word occurrences.

## 2. Inventory scale and review state

The live source snapshot contains:

- 3,349 candidate groups: 3,323 Hebrew and 26 Aramaic.
- 7,148 language-scoped member keys.
- 32,676 word occurrences.
- 372 groups spanning more than one root/form parent.

All 372 cross-root groups have received member-level review. The 15-case adjudication register records the more difficult lexical, textual, and source-data questions. Fourteen of those cases now have a documented disposition or relationship classification; one textual-critical question remains open. Member-level review does not mean that every occurrence has received full contextual lexical adjudication.

Primary records:
- [Cross-root CSV index](HEBREW_VOWEL_VARIANT_CROSS_ROOT_INDEX_20261107.csv)
- [Adjudication register](HEBREW_VOWEL_VARIANT_ADJUDICATION_REGISTER_20261107.md)
- [Structured adjudication CSV](HEBREW_VOWEL_VARIANT_ADJUDICATION_REGISTER_20261107.csv)
- [Batch review reports 8–25](.)

## 3. Main categories found

### A. Inflectional and syntactic variants within one lexeme family

Many groups are useful morphology examples rather than lexical collisions:

- Construct forms versus possessive suffix forms: `פְּנֵי` (“face/surface of”) versus `פָּנַי` (“my face”); `יְדֵי` (“hands of”) versus `יָדִי` (“my hand”); `דִּבְרֵי` (“words of”) versus `דְּבָרַי` (“my words”).
- Number and suffix distinctions: “sons of” versus “my sons”; singular “my foot” versus plural “my feet”.
- Verbal person/number/object-suffix distinctions: forms that differ in person, number, or object suffix can share the same consonantal skeleton.
- These forms are related, but their clause-level syntax and translation still need to be determined from context.

### B. Same consonants, unrelated lexical or grammatical units

These are the most important warnings against treating a candidate as a synonym link:

- `לֵךְ` — imperative “go!” versus `לָךְ` — “to you”.
- `אֶל` — “to/toward” versus `אַל` — negative/prohibitive particle.
- `עִיר` — “city” versus other forms whose consonants happen to match after vowel removal.
- `אֶתָּם` / `אִתָּם` contrasts object/pronominal and prepositional analyses in context.
- Proper names can collide with common nouns or inflected forms. A candidate group is not evidence that the name and the common noun are the same lexeme.

For these groups, the UI should show separate lexical records and make the orthographic nature of the link explicit.

### C. Proper names versus common nouns or verbal forms

Two examples were reviewed in detail:

- **Lebo-Hamath:** the project uses HNp for the Numbers 13:21 and 34:8 forms. Other boundary passages use both proper-name and common-noun-construct analyses. UBS and other translation sources support “Lebo-Hamath,” while “entrance/pass of Hamath” remains a valid literal alternative. The source annotation is defensible; no data correction is proposed.
- **Lair/Lahir:** in 2 Kings 19:13 / Isaiah 37:13, `לָעִיר` can be read as “the city of Sepharvaim” or as the proper name Lair. Zadok's geographical/onomastic study, UBS, and NET support the Lair identification. The project's HNp analysis is defensible; retain the common-noun translation alternative in notes.

These are examples where morphology and geographical interpretation must be considered together. A Strong's number alone does not settle the proper-name/common-noun question.

### D. Textual witness differences must remain distinct from MT qere

**Ezekiel 27:32** is the most important unresolved case:

- MT: `בְּנִיהֶם֙`, parsed as “in their wailing” (H5204).
- Alternative: `בְּנֵיהֶם֙`, “their sons” (H1121).
- The LXX reads `οἱ υἱοὶ αὐτῶν` (“their sons”); BDB reports the “their sons” reading in eleven manuscripts, early editions, and ancient versions.
- The isolated shadow inventory places the two pointed forms in candidate group 504, with distinct roots and morphology. The “sons” member occurs in Jeremiah 11:22 and 17:2; the “wailing” member occurs in Ezekiel 27:32.

The candidate link is verified, but the textual priority of the readings remains open. The consonantal sequence is the same; the contrast is chiefly vocalization and lexical analysis: MT בְּנִיהֶם, parsed as preposition + the rare/doubtful noun נִי (“wailing”), versus בְּנֵיהֶם, parsed as “their sons.” BDB calls נִי doubtful and the MT reading improbable; it records the sons reading in the LXX, Theodotion, Syriac, and eleven Hebrew codices. Gesenius additionally reports several early editions and Arabic evidence. BDB also reports Cornill's view that “their sons” is a gloss. However, [Gesenius-Kautzsch-Cowley, *Hebrew Grammar* §23](https://www.studylight.org/lexicons/eng/gesenius/23.html), proposes that the MT form may be contracted from בְּנְהִיהֶם (preposition + the established noun נְהִי, H5092, “wailing”) by syncope of ה. This is a plausible grammatical explanation for the MT form, not proof of its original vocalization. The exact pinned OSHB XML (commit `3d15126fb1ef74867fc1434be1942e837932691f`) has been checked: Ezek.27.32 uses `lemma="b/5204"`, `morph="HR/Ncmsc/Sp3mp"`, and segmented form `בְּ/נִי/הֶם֙` (OSHB word id `26F8P`). The project's H5204 assignment therefore matches its upstream source exactly; Gesenius's alternative does not establish a parser/import error or justify changing the source lemma. Keil and Delitzsch reject it contextually, while Werner Commentary offers a descendant-based defense. Thus neither the witness count nor the translation evidence alone settles priority. There is also a literary-context difference: MT includes the sailors' mourning at 27:31 and then continues with “in their wailing” at 27:32; the Old Greek omits 27:31 but retains “their sons” in 27:32, including in P967. The Greek reading may be part of a broader form of the passage rather than an isolated vowel substitution. It is evidence for an ancient Greek textual/interpretive tradition, not conclusive proof of the Hebrew pointing in its Vorlage.

YLT renders “their sons”; KJV and JPS 1917 render “in their wailing”; NET renders “as they wail.” The NET footnote about Dahood concerns the later word כְּדֻמָה, not this reading. Broader research on Ezekiel's text history cautions against assuming that the LXX is automatically earlier or that the MT is automatically later: Hector M. Patmore, [“The Shorter and Longer Texts of Ezekiel” (2007)](https://doi.org/10.1177/0309089207085885), argues that different forms of Ezekiel circulated concurrently and that priority cannot simply be assigned to either edition. That is a general text-historical caution, not a direct verdict on this verse. No directly relevant Qumran/Masada witness to Ezekiel 27:32 was identified in the sources checked. The alternative is not a local MT qere row. Do not invent a qere entry or overwrite the MT token. If BibleApp later exposes the evidence, use a separate external-witness/apparatus layer that records witness type, edition/manuscript, reading, and provenance.

### E. Translation alignment is not a textual witness

The YLT verse at Ezekiel 27:32 reads “their sons,” but the current YLT alignment has only 14 of 30 verse tokens mapped. The MT H5204 token is bridged to “And” and “lifted,” while the YLT words “their sons” are unaligned; the preceding Hebrew verb also has no alignment rows.

This is a likely U-1 alignment anomaly, not a reason to rewrite the Hebrew text or recompute the YLT alignment during this task. Preserve the existing YLT data and track alignment review separately.

## 4. Unicode and source-preservation caution

The OSHB repository warns against normalizing Hebrew source text. A live-corpus test found that NFC changes code-point order in 138,497 word rows and collapses 147 raw encodings into already-existing NFC forms. A corrected comparison test found that 137 raw-only candidate groups collapse to one NFC form. However, NFC-then-vowel-removal and vowel-removal-then-NFC produce identical 3,349 candidate groups and identical normalized member sets for this source snapshot.

Therefore:

- Keep every raw source form unchanged.
- Use NFC only for the versioned comparison key.
- Re-run the regression test after any source, parser, or Unicode-library change.
- Do not use normalized comparison strings as replacement source text.

See [NFC normalization check](HEBREW_VOWEL_VARIANT_NFC_NORMALIZATION_CHECK_20261107.md).

## 5. Safe BibleApp presentation

Recommended user-facing language:

> **Vowel-only orthographic variant** — this form shares the same consonants and retained marks with another pointed form. The link does not imply the same meaning or lexical entry.

For each candidate group, display:

1. The exact pointed forms, preserving their raw source spelling.
2. Separate root, lexicon, Strong's, and morphology records for each member.
3. Occurrence counts and verse references.
4. A neutral note when the group crosses root/form boundaries.
5. A textual-witness note only when a named witness and source are available.
6. Clear separation between MT text, qere/ketiv, external witnesses, and YLT translation/alignment.

Never label the members “synonyms” merely because they share a non-vowel signature. Do not automatically merge, redirect, or collapse their lexical entries.

## 6. Current implementation boundary

The candidate schema and data have been built and independently validated only in the isolated shadow database `bible_hebrew_variant_shadow_20261107`. Production `bible` schema and rows remain unchanged. No lexical merges, Strong's changes, morphology changes, YLT alignment changes, embedding/vectorizer changes, API changes, or deployment have been performed.

The related proposal is documented in [the schema proposal](HEBREW_VOWEL_VARIANT_SCHEMA_PROPOSAL_20261107.md). The work remains in draft PR [#11](https://github.com/kitcosby/bible-project/pull/11).
