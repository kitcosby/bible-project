# Hebrew/Aramaic vowel-only variants — cross-root member review

**Date:** 2026-11-07  
**Status:** Read-only member-level review completed for the three three-root cases and the 15 highest-occurrence cross-root groups. No database changes.  
**Parent evidence:** [Live inventory results](HEBREW_VOWEL_VARIANT_INVENTORY_RESULTS_20261107.md), [schema proposal](HEBREW_VOWEL_VARIANT_SCHEMA_PROPOSAL_20261107.md).

## 1. Scope and safeguards

The review resumed against Lampy's live PostgreSQL `bible` database through the ToE → WSL `lampy` execution path. Queries ran as the local PostgreSQL account against `127.0.0.1` and used explicitly read-only transactions. The existing inventory JSON in `/tmp/hebrew-vowel-variants-20261107.summary.json` was used to identify candidate member keys.

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

- Review the remaining 357 cross-root groups, prioritizing multiple Strong's, multiple morphology, and three-root groups already covered above.
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

A second member-level pass selected the next 15 groups from the language-scoped index, ordered by multiple Strong's values, multiple morphology patterns, root divergence, and occurrence count, excluding the first 15 high-occurrence cases already reviewed.

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

These 15 are still database-level member reviews with sample references, not exhaustive contextual lexical adjudications. Combined with the first batch, 30 of the 372 cross-root groups have now received member-level inspection; 342 remain.
