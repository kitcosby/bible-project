# Hebrew/Aramaic vowel-only variants — cross-root member review

**Date:** 2026-11-08  
**Status:** Member-level inspection is complete for all 372 cross-root candidate groups: three three-root cases plus batches 1–24 (15 groups each) and final batch 25 (9 groups). Zero groups remain pending. Batches 8–25 have individual reports linked in §17; the isolated shadow build is documented in §10.
**Parent evidence:** [Live inventory results](HEBREW_VOWEL_VARIANT_INVENTORY_RESULTS_20261107.md), [schema proposal](HEBREW_VOWEL_VARIANT_SCHEMA_PROPOSAL_20261107.md).

## 1. Scope and safeguards

The original corpus inventory and early member-level passes used read-only queries against Lampy's live PostgreSQL `bible` database. After the isolated shadow snapshot was built and independently validated (§10), batches 6–25 were reviewed with explicitly read-only transactions against `bible_hebrew_variant_shadow_20261107`. The 2026-11-08 reconciliation queried only that shadow database; the production `bible` database was not accessed in this run. No production or shadow writes were made during this reconciliation.

The review joined candidate members to:

- `root_entry` for the existing root label;
- `root_form` for prefix/suffix analysis;
- `root_vowel` for the exact pointed pattern;
- `words` for occurrence counts, Strong's values, morphology pattern IDs, and verse references;
- `morph_patterns` for stored morphology codes.

No source data, lexical rows, alignments, embeddings, vectorizer, or schema were changed. This was a member-level database review, not a complete contextual exegesis of every occurrence.

## 2. Three-root groups: all individually inspected

All three groups spanning three root/form parents were inspected at member level.

### Signature `לבנ֖י` — 11 occurrences

| Existing member | Root | Stored analysis | Occurrences | Strong's |
|---|---|---|---:|---|
| `לְבָנַ֖י` — `6105.28.1` | `בנ` | `HR/Ncmpc/Sp1cs` | 1 | H1121 |
| `לִבְנִ֖י` — `17764.1.1` | `לבני` | `HNp` | 1 | H3845 |
| `לִבְנִ֖י` — `6105.28.3` | `בנ` | `HR/Ncmsc/Sp1cs` | 3 | H1121 |
| `לִבְנֵ֖י` — `6627.44.1` | `בני` | `HR/Ncmpc` | 6 | H1121 |

The same pointed form `לִבְנִ֖י` exists under two different root-vowel keys and analyses. This demonstrates why the member relation must reference the existing root-vowel key, not just the pointed string.

### Signature `לבנ֥י` — 56 occurrences

| Existing member | Root | Stored analysis | Occurrences | Strong's |
|---|---|---|---:|---|
| `לִבְנִ֥י` — `17764.1.2` | `לבני` | `HNp` | 4 | H3845 |
| `לִבְנִ֥י` — `6105.28.5` | `בנ` | `HR/Ncmsc/Sp1cs` | 1 | H1121 |
| `לִבְנֵ֥י` — `6627.44.4` | `בני` | `HR/Ncmpc` | 51 | H1121 |

Again, one pointed form occurs under more than one lexical/root analysis.

### Signature `לכ֔ה` — 4 occurrences

| Existing member | Root | Stored analysis | Occurrences | Strong's |
|---|---|---|---:|---|
| `לְכָ֔ה` — `14608.6.1` | `כה` | `HR/Sp2ms` | 1 | null |
| `לְכָ֔ה` — `17908.2.1` | `לכ` | `HVqv2ms/Sh` | 2 | H3212 |
| `לֵכָ֔ה` — `17918.1.1` | `לכה` | `HNp` | 1 | H3922 |

The exact form `לְכָ֔ה` is assigned to both a prepositional/pronominal analysis and a verb analysis. The similar `לֵכָ֔ה` is a proper-name analysis. These should remain distinct members of one orthographic candidate group.

## 3. Fifteen highest-occurrence cross-root groups

The following groups were queried against existing root, affix, Strong's, morphology, and occurrence data.

| Signature | Occurrences | Distinct pointed forms | Key observed divergence |
|---|---:|---:|---|
| `בּנ֣י` | 396 | 4 | Root `בנ` with suffix, root `בני` forms, and proper name Bani; five root-vowel member keys because one pointed form has two analyses. |
| `אדנ֣י` | 217 | 4 | `אדנ` vs `אדני`; Strong's H113, H136, H134 and differing number/suffix analyses. |
| `לפנ֣י` | 216 | 2 | `פנ` with first-person suffix vs `פני` without that suffix; same Strong's H6440, different morphology. |
| `בּנ֥י` | 206 | 2 | Singular construct with first-person suffix vs plural construct; H1121 and H1145 occur in the latter member's occurrences. |
| `אלה֣י` | 179 | 2 | `אלהי` construct form vs `אלה` with first-person suffix; both H430, morphology differs. |
| `לפנ֥י` | 167 | 2 | Same broad distinction as `לפנ֣י`: suffix-bearing `פנ` vs `פני`. |
| `אדנ֥י` | 108 | 4 | Same broad lexical split as `אדנ֣י`; H113, H136, H134 represented. |
| `אל֔י` | 89 | 2 | Mainly `אֵלַ֔י` under root `אל`; one occurrence of the same pointed form under root `אלי`, plus `אֵלָ֔י`. |
| `אלה֥י` | 86 | 2 | `אלהי` construct vs `אלה` with first-person suffix; both H430, morphology differs. |
| `דּבר֥י` | 85 | 3 | Noun `דבר` forms vs participial `דברי` from verbal root `דבר`; H1697 vs H1696. |
| `לפנ֖י` | 84 | 2 | Suffix-bearing `פנ` vs `פני`; same H6440, distinct morphology. |
| `וּבנ֣י` | 69 | 2 | Conjunction + suffix-bearing singular vs conjunction + plural construct; H1121/H1123 in the latter member's occurrences. |
| `לֽך׃` | 67 | 2 | Verb `לֵֽךְ׃` (H3212) vs prepositional `לָֽךְ׃`; different morphology and lexical function. |
| `לך֙` | 66 | 3 | Two pronominal/prepositional gender analyses vs verb `לֵךְ֙` (H3212). |
| `מע֣ל` | 65 | 2 | Preposition `מֵעַ֣ל` (H5921) vs verb `מָעַ֣ל` (H4603). |

Counts are occurrence counts in the candidate inventory, not counts of distinct lexical senses. Strong's and morphology arrays are aggregated from existing word occurrences; a null value in the source remains null.

## 4. Findings and classification

### Established by database inspection

1. A strict vowel-only signature can span multiple existing root entries and root-form parents.
2. The same pointed string can map to more than one `root_vowel` key and more than one lexical/morphological analysis.
3. A shared Strong's value does not imply identical morphology (for example, `לפני` and `אלהי` groups).
4. Different Strong's values can occur within one candidate group (for example, `אדני`, `דברי`, and `מעל`).
5. Prefix/suffix analysis can differ even when the consonantal signature is identical.
6. The strict signature can group fundamentally different lexical functions, such as a verb and a preposition/pronoun construction.

### Interpretation — not a database fact

These examples are consistent with homography, distinct lemma/root analyses, affix segmentation differences, and differences in vocalization. The database's stored labels and morphology codes are evidence of the current data model, not independent proof that every analysis is linguistically correct. Verse-level review is still needed before making claims about the best Hebrew parsing or translation.

### Design consequence

Retain a group/member cross-reference only. Never merge or rewrite:

- root entries or root-form parents;
- root-vowel records;
- lexicon rows;
- Strong's associations;
- morphology patterns or segments;
- verse occurrences, YLT renderings, or alignment records.

The member must be the existing `(root_id, root_form_seq, vowel_seq)` key. A pointed string alone is not a sufficiently unique member identifier.

## 5. Algorithm boundary confirmed

The inventory's comparison rule removes only the designated vowel points after NFC normalization. Dagesh/mapiq, shin/sin dots, meteg, cantillation, maqaf, sof pasuq, and other non-vowel marks remain significant. This boundary matters: for example, the verb/preposition contrasts above are grouped only where the non-vowel codepoints match exactly.

This is an orthographic candidate relation, not a general Hebrew consonantal-root index. A broader consonantal search would be a separate feature with a different name, algorithm, and review process.

## 6. Outstanding review

- Review the remaining 309 cross-root groups, prioritizing multiple Strong's, multiple morphology, and groups with unusual affix/root segmentation.
- Review the complete verse context for high-impact lexical cases, especially divine-name and `אדני` forms.
- Inspect whether the source's root and affix segmentation is internally consistent across repeated occurrences.
- Build a separate Qere/Ketiv apparatus inventory; do not fold it into canonical `words.pointed` membership.
- Decide snapshot/version semantics before implementing persistent group rows. Algorithm version alone does not identify the source-corpus revision.

## 7. Change record

- Read-only PostgreSQL transactions only.
- No DDL/DML or production writes.
- No schema, lexical, morphology, Strong's, alignment, embedding, or vectorizer changes.
- No shadow database was created or modified in this review.


## 8. Language-scope audit and corrected cross-root index

A second read-only check tested whether one existing `root_vowel` key can occur in both language populations. Among the **830 distinct member keys** used by the 372 cross-root groups, **eight keys** have occurrences with both `is_aramaic=0` and `is_aramaic=1`. The pointed spelling is the same, but the occurrence populations are distinct.

This confirms an important implementation detail: group identity is language-scoped, while the same existing root-vowel key may be a member of a Hebrew group and a separate Aramaic group. Validators must compare each group's signature and member occurrences only within its `is_aramaic` population. They must not aggregate every occurrence attached to a root-vowel key without that filter.

A diagnostic that aggregated all occurrences by root-vowel key (without language filtering) temporarily produced 186 cross-root groups with multiple Strong's values. It incorrectly included an Aramaic occurrence (H1123) in the Hebrew `וּבנ֣י` group. Recomputing from the exact candidate occurrence word IDs, as in the original inventory-level grouping, restored the correct totals: **185** cross-root groups with multiple Strong's values and **370** with multiple morphology patterns. The initial 186 figure is rejected and is not used in the corrected index.

The complete language-scoped group index is [HEBREW_VOWEL_VARIANT_CROSS_ROOT_INDEX_20261107.csv](HEBREW_VOWEL_VARIANT_CROSS_ROOT_INDEX_20261107.csv). It contains all 372 groups, sorted by lexical/morphological divergence, with root labels, occurrence counts, Strong's values and counts, morphology pattern IDs and counts, affix-profile counts, and a flag for groups containing a member key also used in the other language population.

The corrected all-group totals are:
- 372 cross-root groups and 830 distinct root-vowel member keys.
- 185 groups with multiple Strong's values, computed from the group's exact occurrence IDs.
- 370 groups with multiple morphology pattern IDs, computed from the group's exact occurrence IDs.
- All 372 groups have more than one affix profile across their members.
- Eight groups contain a root-vowel key that is also used in the other language population.
- Root-count distribution: 369 groups span two roots; three span three roots.

This audit is still a database-level structural review, not a complete linguistic adjudication of all 372 groups.


## 9. Second high-priority batch: 15 further cross-root groups

A second member-level pass selected the next 15 groups from the language-scoped index, ordered by multiple Strong's values, multiple morphology patterns, root divergence, and occurrence count, excluding the first 15 high-occurrence cases and the three three-root groups already reviewed separately.

| Signature | Occurrences | Existing roots | Strong's values | Main stored distinction |
|---|---:|---|---|---|
| `אל֖י` | 58 | `אל`, `אלי` | H410, H413 | `אֵלִ֖י` noun + first-person suffix (“my God” analysis); `אֵלַ֖י` preposition + first-person suffix (“to me”); one `אֵלַ֖י` under root `אלי` has no Strong's/morphology assignment. |
| `הר֖ע` | 49 | `הרע`, `רע` | H7489, H7451 | One verbal member `הֵרַ֖ע` (Exodus 5:23) vs article/adjective members `הָרַ֖ע` and `הָרָ֖ע`. |
| `את֔ם` | 47 | `את`, `אתמ` | H853, H864 | `אֹתָ֔ם` object pronoun “them” vs proper name `אֵתָ֔ם` (Numbers 33:8). |
| `וּבנ֥י` | 45 | `בנ`, `בני` | H1121, H1129, H1137 | “and my son”, “and sons”, proper name Bani, and participial “builders”; different morphology and lexical entries. |
| `אתּ֣ם` | 42 | `את`, `אתמ` | H854, H859 | `אִתָּ֣ם` “with them” vs `אַתֶּ֣ם` “you” (masculine plural). |
| `מא֣ת` | 42 | `את`, `מאת` | H3967, H854 | `מְאַ֣ת` “hundred” vs `מֵאֵ֣ת` “from”. |
| `על֣י` | 41 | `על`, `עלי` | H5921, H5941 | `עֲלֵ֣י` preposition, `עֵלִ֣י` proper name Eli, and `עָלַ֣י` preposition with first-person suffix. |
| `דּבר֣י` | 38 | `דבר`, `דברי` | H1696, H1697 | “my words”, “words of”, and a participial form “speakers” (Psalms 28:3). |
| `בּנ֖י` | 35 | `בנ`, `בני` | H1121, H1137 | Singular construct with first-person suffix, plural construct, proper name Bani, and plural construct with suffix. |
| `אב֣י` | 32 | `אב`, `אבי` | H1, H33 | `אָבִ֣י` “my father” vs `אֲבִ֣י` under a separate root entry with both H1/H33 and multiple morphology assignments. |
| `מע֖ל` | 31 | `מעל`, `על` | H4603, H5921 | Verb `מָעַ֖ל` vs preposition `מֵעַ֖ל` “from above”. |
| `אדנ֖י` | 29 | `אדנ`, `אדני` | H113, H136 | “my lord”/divine-title analyses; one exact member `אֲדֹנִ֖י` itself carries both H113 and H136 across occurrences. |
| `אתּם֙` | 29 | `את`, `אתמ` | H854, H859 | `אִתָּם֙` “with them” vs `אַתֶּם֙` “you” (masculine plural). |
| `ל֣ך` | 29 | `כ`, `לכ` | H1980, H3212 | `לֵ֣ךְ` imperative/verb member has both Strong's H1980 and H3212 while retaining the same stored verbal morphology; `לָ֣ךְ` is a separate prepositional/pronominal member. |
| `אתּ֖ם` | 27 | `את`, `אתמ` | H854, H859 | Same “with them” vs “you” distinction as other accent-specific groups. |

### Additional data-quality flags

Two cases deserve review beyond the vowel-only relation itself:

1. In `אדנ֖י`, the same pointed root-vowel member `אֲדֹנִ֖י` is associated with both H113 and H136 across occurrences. The distinction may be contextual/lexical, but it cannot be resolved by the pointed form or root-vowel key alone.
2. In `ל֣ך`, the same pointed verbal member `לֵ֣ךְ` carries both H1980 and H3212 while the stored morphology remains `HVqv2ms`. This is a Strong's assignment divergence within one member, not simply a difference between two vocalized members.

The `אב֣י` group also has multiple Strong's and morphology assignments within its `אֲבִ֣י` member. These cases should become explicit lexical-association review items rather than being “fixed” by the variant-group builder.

These 15 are still database-level member reviews with sample references, not exhaustive contextual lexical adjudications. At this stage, 33 of the 372 cross-root groups had received member-level inspection (the three three-root cases plus two batches of 15); 339 remained before the later batches in §§11–12.


## 10. Follow-on isolated shadow prototype

After the member-level review, a separate database `bible_hebrew_variant_shadow_20261107` was restored from a verified dump of the live `bible` database. The group/member schema was created and populated only in that new database. The independent validator passed all 3,349 group and 7,148 language-scoped member comparisons, 32,676 occurrence counts, root-vowel/lexicon parent checks, language-scope assertions, and Qere separation. Production and the existing Greek bridge test database were not modified.

The source and post-build backup hashes, table-count parity, ACL restriction, and reproducible scripts are documented in [HEBREW_VOWEL_VARIANT_SHADOW_BUILD_RESULTS_20261107.md](HEBREW_VOWEL_VARIANT_SHADOW_BUILD_RESULTS_20261107.md). All 3,349 groups remain candidate-only; the prototype does not imply linguistic approval.


## 11. Third high-priority batch: 15 further cross-root groups

The third batch continues down the corrected language-scoped index's risk ranking, excluding the first 33 reviewed groups (the three three-root groups plus two 15-group batches).

| Signature | Occurrences | Existing roots | Strong's values | Main stored distinction |
|---|---:|---|---|---|
| `מא֥ת` | 26 | `את`, `מאת` | H3967, H854 | `מְאַ֥ת` “hundred” vs `מֵאֵ֥ת` “from”. |
| `אל֛י` | 24 | `אל`, `אלי` | H194, H413 | `אֵלַ֛י` “to me” vs `אֻלַ֛י` “perhaps”. |
| `אב֥י` | 23 | `אב`, `אבי` | H1, H33 | “my father” vs a separate `אבי` root entry with multiple noun/genitive morphology patterns. |
| `אח֣י` | 23 | `אח`, `אחי` | H251, H278 | Singular/plural construct, “my brothers”, and proper name Echi; five member keys and several noun parses. |
| `על֖י` | 23 | `על`, `עלי` | H5921, H5941 | Preposition `עֲלֵ֖י`, proper name Eli `עֵלִ֖י`, and `עָלַ֖י` “upon me”. |
| `אתּ֑ם` | 22 | `את`, `אתמ` | H854, H859 | `אִתָּ֑ם` “with them” vs `אַתֶּ֑ם` “you” (masculine plural). |
| `הע֣יר` | 22 | `העיר`, `עיר` | H5782, H5892 | Verb `הֵעִ֣יר` “awaken” vs article + noun `הָעִ֣יר` “the city”. |
| `העיר֙` | 21 | `העיר`, `עיר` | H5782, H5892 | Same verb-versus-article+noun contrast in another cantillation context. |
| `עבד֣י` | 21 | `עבד`, `עבדי` | H5647, H5650 | “my servants” / “servants of” noun forms vs participial `עֹבְדֵ֣י` “those serving”. |
| `בּנ֨י` | 19 | `בנ`, `בני` | H1121, H1137 | “my son”, “sons”, and proper name Bani. |
| `מא֖ת` | 19 | `את`, `מאת` | H3967, H854 | “hundred” (two vocalizations) vs “from”. |
| `אב֖י` | 17 | `אב`, `אבי` | H1, H21 | “my father” vs a distinct `אבי` member with H1/H21 and noun/proper-name analyses. |
| `על֔ינוּ` | 17 | `עלי`, `עלינו` | H5921, H5927 | `עָלִ֔ינוּ` “we went up” (verb) vs `עָלֵ֔ינוּ` “upon us” (preposition + suffix). |
| `עלי֙` | 17 | `על`, `עלי` | H5921, H5941 | Proper name Eli `עֵלִי֙` vs `עָלַי֙` “upon me”. |
| `אתּ֔ם` | 16 | `את`, `אתמ` | H854, H859 | `אִתָּ֔ם` “with them” vs `אַתֶּ֔ם` “you” (masculine plural). |

### Additional data-quality observations

- The `אח֣י` family has multiple pointed forms and root assignments even where the Strong's value remains H251; one member is assigned H278 and proper-name morphology. A consonantal signature cannot decide between kinship noun and proper name.
- The `העיר` groups are clear verb-versus-definite-article+noun cases. This also demonstrates why retaining cantillation creates separate groups for distinct accentual contexts, even when the underlying lexical contrast is repeated.
- `עבד֣י` includes both noun and participial morphology under the same signature, with H5650 vs H5647.
- `על֔ינוּ` is a particularly clear morphology contrast: first-person plural verb vs preposition with first-person plural suffix.
- `מא֥ת` / `מא֖ת` and `אתּ֑ם` / `אתּ֔ם` show that accent-specific signatures may repeat the same lexical contrast across several separate groups. The group key is intentionally strict; a higher-level lemma-family index would be a separate layer.

The review now covers **48 of 372 cross-root groups** (three three-root cases plus three batches of 15); **324 remain**. These are still database-level member reviews with sample references, not exhaustive contextual lexical adjudications.


## 12. Fourth high-priority batch: 15 further cross-root groups

This batch continues down the corrected risk-sorted index after the 48 previously reviewed groups.

| Signature | Occurrences | Existing roots | Strong's values | Main stored distinction |
|---|---:|---|---|---|
| `אתּ֥ם` | 16 | `את`, `אתמ` | H854, H859 | `אִתָּ֥ם` “with them” vs `אַתֶּ֥ם` “you” (masculine plural). |
| `אח֥י` | 15 | `אח`, `אחי` | H251, H277 | Singular/plural kinship forms, “my brothers”, and a member with H251/H277 and noun/proper-name morphology. |
| `עבד֥י` | 15 | `עבד`, `עבדי` | H5647, H5650 | Noun forms “my servants” / “servants of” vs participial `עֹבְדֵ֥י` “those serving”. |
| `עמּ֑י` | 15 | `עמ`, `עמי` | H3818, H5971, H5973 | `עִמִּ֑י` preposition “with me”, `עַמִּ֑י` “my people”, and proper name Ammi. |
| `בּע֥ד` | 14 | `בעד`, `עד` | H1157, H5750 | Prepositional member `בְּעַ֥ד` vs member from root `עד` with a different stored grammatical analysis. |
| `על֛י` | 14 | `על`, `עלי` | H5921, H5941 | Proper name Eli vs preposition with first-person suffix (“upon me”). |
| `על֥י` | 13 | `על`, `עלי` | H5921, H5927, H5941 | Adds a verbal imperative `עֲלִ֥י` (“go up”, feminine singular) alongside Eli and “upon me”. |
| `בּמ֣ות` | 11 | `במות`, `מות` | H1116, H1120, H4191, H4194 | Construct/inflected noun `בָּמ֣וֹת` (high places) vs `בְּמ֣וֹת` “at/in the death of” with verbal/noun morphology. |
| `מאחר֣י` | 11 | `אחרי`, `מאחרי` | H309, H310 | Participle from `מאחרי` vs preposition `מֵאַחֲרֵ֣י` (“from behind/after”). |
| `מאת֙` | 11 | `את`, `מאת` | H3967, H854 | “hundred” vs “from”; another cantillation-specific signature. |
| `מה֥ר` | 11 | `הר`, `מהר` | H2022, H4116, H4118, H4122 | “from the mountain” vs forms associated with hurrying/haste and a proper-name assignment. |
| `מעלֽיו׃` | 11 | `מעלי`, `עלי` | H4608, H5921 | Prepositional `מֵעָלָֽיו` with third-person suffix vs noun `מַעֲלָֽיו` with suffix; different morphology. |
| `על֑י` | 11 | `על`, `עלי` | H5921, H5941 | Proper name Eli vs “upon me”; two vocalized prepositional members are also separately recorded. |
| `על֔י` | 11 | `על`, `עלי` | H5921, H5941 | Same Eli vs “upon me” distinction in a different accentual context. |
| `רגל֑י` | 11 | `רגל`, `רגלי` | H7272, H7273 | Noun “my foot/feet” member vs a separate `רגלי` member with adjective morphology. |

### Additional data-quality and interpretation flags

- `עמּ֑י` combines preposition “with me”, noun “my people”, and a proper name. This is a strong example of why the signature cannot determine lexical class.
- `בּמ֣ות` is a high-value morphology case: the same consonantal sequence occurs in a noun for high places and in a construction tied to death. The vowel difference aligns with different stored roots and morphology.
- `מה֥ר` contains several Strong's values and mixed noun, verb, and proper-name morphology. It needs full-context review before any lexical conclusion.
- The recurring `עלי` families (Eli vs “upon me” vs “go up”) occur across multiple accent-specific groups. These groups should remain separate under the strict signature algorithm; a higher-level cross-accent lexical-family index would be distinct functionality.
- `אח֥י`, `עבד֥י`, and `רגל֑י` include cases where a pointed member itself has multiple stored Strong's or morphology assignments. These are data-quality review targets, not problems to resolve by merging variant members.

The review now covers **63 of 372 cross-root groups** (three three-root cases plus four 15-group batches); **309 remain**. The evidence is still member-level and sample-reference based, not a complete contextual Hebrew lexical adjudication.


## 13. Fifth high-priority batch: 15 further cross-root groups

This pass reviews the next 15 pending groups in the risk-ranked index, after the 63 groups covered in §§1–12. The review used the isolated shadow snapshot and inspected each existing member's pointed form, root label, Strong's assignment, morphology pattern ID, occurrence count, and verse references. It remains a member-level database review, not a full contextual lexical adjudication.

| Signature | Occurrences | Existing roots | Stored member distinction |
|---|---:|---|---|
| `אדנ֨י` | 10 | `אדנ`, `אדני` | Members include `אֲדֹנִ֨י` (H113; 2 occurrences) and `אֲדֹנָ֨י` (H136; 6), plus `אֲדֹנֵ֨י` (H113; 1). Distinct pointed forms and Strong's assignments; do not collapse the divine-title and ordinary-lord analyses. |
| `בּנ֑י` | 10 | `בנ`, `בני` | `בְּנִ֑י` / `בָּנָ֑י` (H1121) alongside proper name `בָּנִ֑י` (H1137). |
| `וּמא֖ת` | 10 | `את`, `מאת` | `וּמֵאֵ֖ת` (H853; 1) vs `וּמְאַ֖ת` (H3967; 9): conjunction + “from” versus “hundred”. |
| `לב֔ן` | 10 | `בנ`, `לבנ` | `לְבֵ֔ן` (H1121; 2) vs `לָבָ֔ן` (H3836/H3837; 8), including “white” and Laban-related lexical assignments. |
| `מא֨ת` | 10 | `את`, `מאת` | `מֵאֵ֨ת` (H854; 8) vs `מְאַ֨ת` (H3967; 2): “from” vs “hundred”. |
| `מזּ֑ה` | 10 | `זה`, `מזה` | `מִזֶּ֑ה` (H2088; 9) vs `מִזָּ֑ה` (H4199; 1), with a distinct root/lexical assignment. |
| `אתּ֜ם` | 9 | `את`, `אתמ` | `אִתָּ֜ם` (H854; 1) “with them” vs `אַתֶּ֜ם` (H859; 8) “you”. |
| `העל֖ה` | 9 | `העלה`, `עלה` | `הֶעֱלָ֖ה` (H5927; 1) verbal form vs `הָעֹלָ֖ה` (H5930; 8) “the burnt offering”. |
| `לב֑ן` | 9 | `בנ`, `לבנ` | Same “to/for a son” vs “white/Laban” lexical contrast as `לב֔ן`, in a separate accent-specific group. |
| `כּלּ֖ה` | 8 | `כל`, `כלה` | `כֻּלֹּ֖ה` (H3605; 6) vs `כַּלָּ֖ה` (H3618; 2), “all of it” vs “bride”. |
| `על֤י` | 8 | `על`, `עלי` | `עָלַ֤י` (H5921; 4) “upon me” vs `עֲלִ֤י` (H5927; 4), feminine singular imperative “go up”. |
| `אתּֽם׃` | 7 | `את`, `אתמ` | `אִתָּֽם׃` (H854; 2) “with them” vs `אַתֶּֽם׃` (H859; 5) “you”. |
| `אתּי֙` | 7 | `את`, `אתי` | `אִתִּי֙` (H854; 6) “with me” vs `אִתַּי֙` (H863; 1), a proper-name/member assignment. |
| `בנ֔י` | 7 | `בנ`, `בני` | `בְנִ֔י` / `בָנַ֔י` (H1121) vs proper name `בָנִ֔י` (H1137). |
| `כּלּ֑ה` | 7 | `כל`, `כלה` | `כֻּלֹּ֑ה` (H3605), `כִּלָּ֑ה` (H3615), and `כַּלָּ֑ה` (H3618): “all of it”, verbal “finish/complete”, and “bride”. |

### Batch 5 observations and limits

- Several groups contain clear lexical contrasts: “from” vs “hundred” (`מאת`), “with them” vs “you” (`אתּם`), “upon me” vs “go up” (`עלי`), and “all of it” vs “bride” (`כלה`). These are evidence that the relation must remain a cross-reference, not a merge.
- The `לבנ` member family combines a word associated with “son” and forms associated with whiteness/the personal name Laban. The stored H3836 and H3837 assignments occur within one pointed-form grouping; retain this as a lexical-association review item rather than assuming the two Strong's labels are interchangeable.
- `אדנ֨י` includes both H113 and H136 assignments across distinct pointed members; the form is context-sensitive and should be reviewed against its verse context before any theological or lexical conclusion.
- The `אתּי֙` group includes H863 proper-name assignment `אִתַּי֙` (2 Samuel 23:29) alongside H854 “with me” forms. This is a proper-name/homograph case, not a semantic variant.
- `כּלּ֑ה` has three different Strong's values and three distinct pointed members. The same strict signature groups “all of it”, “finish/complete”, and “bride”; this is a particularly clear counterexample to treating vowel-only groups as synonym sets.
- Sample references include Genesis 22:8; Genesis 24:29; Genesis 36:17; Exodus 6:16; Exodus 16:31; Numbers 31:52; 1 Samuel 14:42; 2 Samuel 11:11; 2 Samuel 23:29; Isaiah 21:2; Ezekiel 11:15; and The Song of Solomon 4:11. The complete occurrence list remains in the shadow database and is not reproduced here.

The index now records **78 of 372 cross-root groups** as reviewed at the member level (three three-root cases plus five 15-group batches); **294 remain pending**. This batch did not alter the candidate relation, source tables, or production database. No member is linguistically approved merely by this review.


## 13. Batch 5 — 15 additional high-risk groups

Batch 5 inspected the next 15 pending groups against the isolated shadow database. The review retained every group as an orthographic candidate and did not infer shared lemma identity from the stripped-vowel signature.

Key distinctions found:
- `אדנ֨י`: existing members include H113 and H136 assignments; the pointed forms and verse contexts remain distinct.
- `אתּ֜ם` and `אתּֽם׃`: `אִתָּם` (“with them”, H854) versus `אַתֶּם` (“you”, H859).
- `אתּי֙`: “with me” (H854) versus the proper name Ittai (H863).
- `בּנ֑י` and `בנ֔י`: son/sons forms versus the proper name Bani (H1137).
- `העל֖ה`: verbal “bring up/raise” (H5927) versus “the burnt offering” (H5930).
- `וּמא֖ת`: “and a hundred” (H3967) versus a conjunction/preposition combination involving H853.
- `כּלּ֑ה` and `כּלּ֖ה`: “all of it” (H3605), “finish/complete” (H3615), and “bride” (H3618).
- `לב֑ן` and `לב֔ן`: “son” (H1121) versus Laban/white (H3836/H3837).
- `מזּ֑ה`: “from this” (H2088) versus a proper-name assignment (H4199).
- `מא֨ת`: “from/with” (H854) versus “hundred” (H3967).
- `על֤י`: “upon me” (H5921) versus an imperative form of “go up” (H5927).

These are database member observations, not full contextual adjudications.

## 14. Batch 6 — 15 additional high-risk groups

Batch 6 was queried read-only from `bible_hebrew_variant_shadow_20261107`, not the production database. Member-level findings:

| Signature | Existing member distinction | Evidence / caution |
|---|---|---|
| `רגלֽי׃` | “my feet” (H7272) versus the proper name Ragli (H7273) | Root `רגל` with pronominal suffix versus separate proper-name root `רגלי`. |
| `רע֣י` | “my companion” (H7453), “companions” (H7453), “evil” (H7451), and shepherd forms (H7462/H7473) | Same stripped signature spans noun and verbal/participial analyses. |
| `א֭שׁרי` | “my steps” (H838) versus “blessed” (H835) | Different pointed forms, roots, and morphology. |
| `אתּ֛י` | “with me” (H854) versus Ittai (H863) | Preposition/pronominal suffix versus proper name. |
| `בּגד֣י` | “in my garment” (H1423) versus “garments” (H899) | Prefix preposition plus noun versus plural construct noun. |
| `בּז֔ה` | “in this” (H2088) versus “despised” (H959) | Demonstrative/preposition phrase versus verb. |
| `בּנֽי׃` and `בנ֖י` | “my son” (H1121) versus Bani (H1137) | Possessive noun form versus proper name. |
| `וּמא֣ת` | “and a hundred” (H3967) versus “and from” (H853) | Distinct prepositional/numeral analyses. |
| `כּל֖ב` | Caleb (H3612) versus “like the heart” (H3820) | Proper name versus prefix + noun. |
| `גּוי֙` | “my body” (H1460) versus “nation” (H1471) | Suffix-bearing noun versus independent noun. |
| `העל֣ים` | “he concealed” (H5956) versus “the ones going up” (H5927) | Verb versus article + participle. |
| `ועל֖י` | Eli (H5941), “upon me” (H5921), and “leaves” (H5929) | Three separate root/lexical analyses. |
| `כּלּ֥ה` | “finish/complete” (H3615) versus “all of it” (H3605) | Verbal and pronominal-noun analyses. |
| `מחל֥י` | sickness (H2483) versus Mahlai (H4249) | Common noun versus proper name. |

The member evidence was drawn from stored Strong's values, morphology codes, root/form assignments, and sample verse references in the shadow snapshot. The table is a review index, not a final lexical ruling; in particular, shared consonants and stripped-vowel signatures do not establish semantic equivalence.

### Updated review status

- 93 of 372 cross-root groups have member-level review notes (three three-root cases plus six batches of 15).
- 279 remain pending member review.
- All groups remain candidate-only; no group has been approved as a lexical equivalence.
- Production data and the existing embedding/vectorizer corpus were not modified.


## 15. Batch 7 — 15 additional high-risk groups

Batch 7 was queried in an explicitly read-only transaction against the isolated `bible_hebrew_variant_shadow_20261107` database. Member evidence includes exact pointed forms, root/form assignments, stored Strong's values, morphology codes, occurrence counts, and sample verse references.

| Signature | Existing member distinction | Sample references / caution |
|---|---|---|
| `על֑ה` | verbal “go up” (H5927), foliage/leaf (H5929), and burnt offering (H5930) | 2 Samuel 2:1; Isaiah 1:30; Leviticus 15:15, 15:30. |
| `רגל֖י` | “my feet” (H7272) versus proper name Ragli (H7273) | 2 Samuel 22:34; Isaiah 60:13; Judges 20:2; 1 Samuel 25:41. |
| `אחי֙` | “my brother” (H251) versus a proper-name/root assignment (H277) | 2 Samuel 1:26; Genesis 27:11; 1 Chronicles 5:15, 20:5. One member key itself carries both H251 and H277 across occurrences; retain as a data-quality flag. |
| `אתּם֮` | “with them” (H854) versus “you” (H859) | Daniel 1:19; Genesis 43:16; Jeremiah 26:15; Leviticus 20:24. |
| `בּע֖ד` | preposition “on behalf of/for” (H1157) versus prefixed “in/with/by” + “while” (H5704) | Genesis 26:8; Jeremiah 42:2; Proverbs 7:6; Psalms 39:2. |
| `הֽעל֔ה` | verbal “bring up” (H5927) versus “the burnt offering” (H5930) | Habakkuk 1:15; Leviticus 6:5; 2 Chronicles 20:34; Judges 6:28. |
| `הע֤יר` | “awaken/stir up” (H5782) versus “the city” (H5892) | Ezra 1:5; 2 Chronicles 6:34; Jeremiah 38:18; Zephaniah 2:15. |
| `העבר֖ים` | Hebrews (H5680/H5682) versus Abarim (H5863) | Exodus 5:3; Numbers 27:12; 33:44, 33:47. |
| `העל֛ה` | “bring up” (H5927) versus “the burnt offering” (H5930) | 1 Samuel 12:6; Jeremiah 16:14; 23:7; 1 Chronicles 16:40. |
| `והֽעלה֙` | “and he brought up” (H5927), “and the leaf” (H5929), and article + participial forms (H5927) | Exodus 25:37; Jeremiah 8:13; Jeremiah 48:44; Ezekiel 20:32. |
| `כּל֥ב` | Caleb (H3612) versus “like the heart” (H3820) | Joshua 14:6; 2 Samuel 17:10; Ezekiel 28:2, 28:6. |
| `כּלּ֣ה` | “finish/complete” (H3615) versus “all of it” (H3605) | Genesis 24:15, 27:30; Isaiah 16:7; Jeremiah 48:38. |
| `מא֧ת` | “hundred” (H3967) versus “from/with” (H854) | Exodus 38:27; Genesis 23:15; Deuteronomy 2:8; Jeremiah 52:34. |
| `מימ֣י` | “from the days of” (H3117) versus “waters of” (H4325) | Ezra 9:7; Jeremiah 36:2; 2 Kings 5:12; Exodus 8:2. |
| `מלּ֣א` | “fill/fulfil” (H4390) versus the place-name Millo (H3810) | Isaiah 33:5; Job 22:18; Psalms 83:17; 2 Samuel 17:27. |

These findings demonstrate lexical and morphological divergence under the strict vowel-stripped signature. They are member-level database observations, not exhaustive contextual adjudications or approval to merge roots, Strong's values, morphology, or lexicon records. The within-member H251/H277 variation under `אחי֙` is specifically retained as a source-data flag rather than “corrected” by this cross-reference project.

### Updated review status

- 108 of 372 cross-root groups have member-level review notes (three three-root cases plus seven batches of 15).
- 264 remain pending member review.
- All groups remain candidate-only; no group has been approved as a lexical equivalence.
- Batch 7 used the isolated shadow snapshot read-only; production data and the existing embedding/vectorizer corpus remain untouched.


## 16. Batch 8 — independently revalidated against the isolated shadow

The repository already contained a dedicated [Batch 8 report](HEBREW_VOWEL_VARIANT_CROSS_ROOT_BATCH8_REVIEW_20261107.md). Because the index and batch report already marked these groups complete, this run did not duplicate or reassign them. Instead, all 15 signatures were independently re-queried in an explicit read-only transaction against `bible_hebrew_variant_shadow_20261107`, joining group/member rows to `root_entry`, `root_form`, `root_vowel`, `lexicon`, `words`, `morph_patterns`, `verses`, and `books`.

**Independent check:** 15 groups, 33 language-scoped member rows, and 51 word occurrences; all 15 groups are Hebrew. Every `words.pointed` value matched its `root_vowel.vowel_pattern` (zero mismatches). Each member key had exactly one Strong's value; two member keys had more than one morphology ID: `בְּרִ֣יחַ` (H1280; IDs 1846/1849) and `הֲדֹ֣ם` (H1916; IDs 1846/1849). The Strong's differences below are across distinct member keys, not multiple Strong's values within one pointed member.

Member ledger (member key is `root_id.root_form_seq.vowel_seq`; `n` is the count of canonical `words` occurrences):

- `מעל֣ות` (4): `מַעֲל֣וֹת` — root `מעלות`, `19774.1.5`, H4609, morph 1795, n=2 (1 Kings 10:19; 2 Chronicles 9:18); `מֵעֲל֣וֹת` — root `עלות`, `24081.8.1`, H5927, morph 2180, n=2 (1 Kings 12:28; Nehemiah 4:15).
- `מעלֽות׃` (4): `מַעֲלֽוֹת׃` — root `מעלות`, `19774.1.6`, H4609, morph 1795, n=3 (2 Kings 20:9, 20:10, 20:11); `מֵעֹלֽוֹת׃` — root `עלות`, `24081.8.2`, H5930, morph 1982, n=1 (Hosea 6:6).
- `מצּב֔ה` (4): `מַצֵּבָ֔ה` — root `מצבה`, `19925.1.3`, H4676, morph 1807, n=3 (Genesis 28:22; Genesis 31:13; Exodus 24:4); `מִצֹּבָ֔ה` — root `צבה`, `25523.2.1`, H6678, morph 2038, n=1 (2 Samuel 23:36).
- `מרח֑ק` (4): `מֶרְחָ֑ק` — root `מרחק`, `20210.1.1`, H4801, morph 1846, n=1 (Jeremiah 6:20); `מֵרָחֹ֑ק` — root `רחק`, `26693.5.3`, H7350, morph 1904, n=3 (Genesis 37:18; Exodus 2:4; Exodus 20:21).
- `מרחֽק׃` (4): `מֶרְחָֽק׃` — root `מרחק`, `20210.1.3`, H4801, morph 1846, n=1 (Proverbs 25:25); `מֵרָחֹֽק׃` — root `רחק`, `26693.5.5`, H7350, morph 1904, n=3 (Genesis 22:4; Exodus 24:1; Jeremiah 23:23).
- `עיר֑ם` (4): `עִירָ֑ם` — root `עיר`, `23220.5.1`, H5892, morph 1820, n=1 (Genesis 34:20); `עֲיָרִ֑ם` — root `עירמ`, `23232.1.1`, H5895, morph 1833, n=1 (Judges 12:14); `עִירָ֑ם` — root `עירמ`, `23232.1.2`, H5902, morph 1869, n=2 (Genesis 36:43; 1 Chronicles 1:54). The exact pointed string `עִירָ֑ם` occurs under two root assignments: “their city” versus the proper name Iram.
- `אמר֖י` (3): `אֲמָרַ֖י` — root `אמר`, `2752.3.2`, H561, morph 1837, n=1 (Psalms 5:2); `אֱמֹרִ֖י` — root `אמרי`, `2764.1.1`, H567, morph 1867, n=1 (Numbers 21:29); `אִמְרִ֖י` — root `אמרי`, `2764.1.3`, H559, morph 3351, n=1 (Jeremiah 48:19).
- `אתּ֣י` (3): `אִתִּ֣י` — root `את`, `4060.6.7`, H854, morph 2080, n=2 (Jeremiah 40:4; Judges 1:3); `אִתַּ֣י` — root `אתי`, `5585.1.2`, H863, morph 1869, n=1 (2 Samuel 18:2). The latter is the proper name Ittai.
- `בּניהם֙` (3): `בְּנֵיהֶם֙` — root `בני`, `6627.4.11`, H1121, morph 1844, n=2 (Jeremiah 11:22; Jeremiah 17:2); `בְּנִיהֶם֙` — root `ני`, `21384.3.1`, H5204, morph 2034, n=1 (Ezekiel 27:32). Keep the H5204 assignment distinct; its precise gloss and the textual question remain open in the separate Ezekiel 27:32 case work.
- `בּר֣יח` (3): `בְּרִ֣יחַ` — root `בריח`, `6960.1.1`, H1280, morphs 1846/1849, n=2 (Amos 1:5; Job 38:10); `בְּרֵ֣יחַ` — root `ריח`, `26713.7.2`, H7381, morph 2026, n=1 (Ezekiel 20:41).
- `דּע֣י` (3): `דֵּעִ֣י` — root `דע`, `8153.4.3`, H1843, morph 1853, n=2 (Job 32:6; Job 32:10); `דְּעִ֣י` — root `דעי`, `8160.1.2`, H3045, morph 3351, n=1 (Jeremiah 3:13).
- `הד֣ם` (3): `הֲדַ֣ם` — root `דמ`, `8113.14.1`, H1818, morph 2416, n=1 (1 Chronicles 11:19); `הֲדֹ֣ם` — root `הדמ`, `8477.1.1`, H1916, morphs 1846/1849, n=2 (Isaiah 66:1; Psalms 110:1).
- `הזּ֥ה` (3): `הַזֵּ֥ה` — root `הזה`, `8707.1.1`, H5137, morph 2907, n=1 (Numbers 8:7); `הַזֶּ֥ה` — root `זה`, `10194.8.14`, H2088, morph 2331, n=2 (Genesis 31:48; Jeremiah 19:6).
- `העל֜ה` (3): `הֶעֱלָ֜ה` — root `העלה`, `9345.1.4`, H5927, morph 2871, n=1 (Jeremiah 16:15); `הָעֹלָ֜ה` — root `עלה`, `24069.4.11`, H5930, morph 2307, n=2 (Leviticus 6:18; 2 Chronicles 35:12).
- `העל֣ה` (3): `הֶעֱלָ֣ה` — root `העלה`, `9345.1.5`, H5927, morph 2871, n=1 (Ezra 1:11); `הֶעָלֶ֣ה` — root `עלה`, `24069.4.1`, H5929, morph 2415, n=1 (Job 13:25); `הָעֹלֶ֣ה` — root `עלה`, `24069.4.5`, H5927, morph 2381, n=1 (Joshua 12:7).

The main distinctions in the batch are proper-name/common-noun or proper-name/preposition collisions (`מצּב֔ה`, `עיר֑ם`, `אתּ֣י`), an ethnonym/noun/verb collision (`אמר֖י`), and clear lexical or grammatical contrasts under the same non-vowel signature. These examples show why identical consonants do not establish semantic equivalence. The `בְּנִיהֶם֙` member remains explicitly uncertain. No member in this batch has multiple Strong's values within one pointed member; the two multi-morphology members are retained as source observations, not corrected here.

## 17. Completion reconciliation — batches 8–25 and final index state

The branch already contains individual reports for every later batch: [Batch 8](HEBREW_VOWEL_VARIANT_CROSS_ROOT_BATCH8_REVIEW_20261107.md), [Batch 9](HEBREW_VOWEL_VARIANT_CROSS_ROOT_BATCH9_REVIEW_20261107.md), [Batch 10](HEBREW_VOWEL_VARIANT_CROSS_ROOT_BATCH10_REVIEW_20261107.md), [Batch 11](HEBREW_VOWEL_VARIANT_CROSS_ROOT_BATCH11_REVIEW_20261107.md), [Batch 12](HEBREW_VOWEL_VARIANT_CROSS_ROOT_BATCH12_REVIEW_20261107.md), [Batch 13](HEBREW_VOWEL_VARIANT_CROSS_ROOT_BATCH13_REVIEW_20261107.md), [Batch 14](HEBREW_VOWEL_VARIANT_CROSS_ROOT_BATCH14_REVIEW_20261107.md), [Batch 15](HEBREW_VOWEL_VARIANT_CROSS_ROOT_BATCH15_REVIEW_20261107.md), [Batch 16](HEBREW_VOWEL_VARIANT_CROSS_ROOT_BATCH16_REVIEW_20261107.md), [Batch 17](HEBREW_VOWEL_VARIANT_CROSS_ROOT_BATCH17_REVIEW_20261107.md), [Batch 18](HEBREW_VOWEL_VARIANT_CROSS_ROOT_BATCH18_REVIEW_20261107.md), [Batch 19](HEBREW_VOWEL_VARIANT_CROSS_ROOT_BATCH19_REVIEW_20261107.md), [Batch 20](HEBREW_VOWEL_VARIANT_CROSS_ROOT_BATCH20_REVIEW_20261107.md), [Batch 21](HEBREW_VOWEL_VARIANT_CROSS_ROOT_BATCH21_REVIEW_20261107.md), [Batch 22](HEBREW_VOWEL_VARIANT_CROSS_ROOT_BATCH22_REVIEW_20261107.md), [Batch 23](HEBREW_VOWEL_VARIANT_CROSS_ROOT_BATCH23_REVIEW_20261107.md), [Batch 24](HEBREW_VOWEL_VARIANT_CROSS_ROOT_BATCH24_REVIEW_20261107.md), and [Batch 25](HEBREW_VOWEL_VARIANT_CROSS_ROOT_BATCH25_REVIEW_20261107.md).

The 372-row CSV index was independently checked: 372 unique `(language, signature)` keys, 18 columns per row, no malformed rows or duplicate keys, and all 372 statuses set to `reviewed_member_level`. Batch assignment is complete and non-overlapping: three `three_root_cases`; batches 1–24 contain 15 groups each; batch 25 contains 9. The two Aramaic cross-root groups remain separate from Hebrew and appear one each in batches 10 and 21; all other cross-root rows are Hebrew. There are zero pending groups.

A read-only shadow query confirms all 3,349 group rows still have `review_status='candidate'`; member review is not linguistic approval. The separate apparatus relation still contains 1,204 MT Qere rows and remains outside canonical vowel-only membership. This run accessed only `bible_hebrew_variant_shadow_20261107`; production `bible` was not accessed or modified. No lexical, Strong's, morphology, alignment, embedding, vectorizer, API, or deployment changes were made.
