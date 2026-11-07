# Hebrew vowel-only variant inventory — live corpus results

**Date:** 2026-11-07  
**Database:** Lampy PostgreSQL database `bible`  
**Scope:** Read-only scan of `public.words.pointed`; Hebrew and Aramaic populations separated.  
**Status:** Inventory executed; candidate groups identified. No database changes.

## 1. Method and safeguards

The committed `audit_hebrew_vowel_variants_postgres.py` was run as the local PostgreSQL account against the live `bible` database. It used a PostgreSQL read-only transaction and streamed all word rows through a server-side cursor.

For comparison only, each source form was normalized to Unicode NFC. The strict signature removes only these vowel-point codepoints:

- U+05B0 through U+05BB: sheva, hataf vowels, hiriq, tsere, segol, patah, qamats, holam, holam haser for vav, and qubuts.
- U+05C7: qamats qatan (included in the rule, but absent from this corpus).

Every other codepoint remains significant: consonants and matres, final forms, dagesh/mapiq, meteg, shin/sin dots, cantillation, rafe, maqaf, paseq, sof pasuq, and other marks/separators. Hebrew (`is_aramaic=0`) and Aramaic (`is_aramaic=1`) are never grouped together. Raw source strings are retained in the output.

A candidate group requires at least two distinct NFC pointed forms with the same strict signature. This is a mechanical orthographic criterion only; it does not assert common lemma, morphology, sense, Strong's number, or translation.

## 2. Corpus inventory

The scan processed **264,217** rows from `public.words`.

| Population | Word rows | Candidate groups | Distinct pointed forms | Occurrences in candidate groups | Groups within one root/form | Groups spanning root/forms |
|---|---:|---:|---:|---:|---:|---:|
| Hebrew | 259,812 | 3,323 | 7,070 | 32,552 | 2,953 | 370 |
| Aramaic | 4,405 | 26 | 54 | 124 | 24 | 2 |
| **Total** | **264,217** | **3,349** | **7,124** | **32,676** | **2,977** | **372** |

Every one of the **3,349** candidate groups maps to at least two existing `root_vowel` IDs; the observed range is two to six IDs per group.

Interpretation of the root hierarchy:

- **2,977 groups** sit entirely within one existing `(root_id, root_form_seq)`. Their distinct pointed forms are already represented as sibling `root_vowel` records under that parent.
- **372 groups** span multiple `root_form` parents. The existing root/form hierarchy does not itself link these readings together.
- The shared `root_form` parent is a structural grouping, not proof that all its vowel patterns have the same lemma or meaning.

## 3. Unicode mark validation against the corpus

A separate read-only codepoint inventory confirmed that all codepoints U+05B0–U+05BB occur in the corpus. U+05BA occurs 417 times. U+05C7 does not occur.

The corpus also contains marks that the strict algorithm must retain, including cantillation (U+0591–U+05AE), dagesh/mapiq (U+05BC; 170,884 occurrences), meteg (U+05BD; 41,347), maqaf (U+05BE; 42,737), rafe (U+05BF; 12), paseq (U+05C0; 2,287), shin/sin dots (U+05C1/U+05C2; 46,075/12,088), sof pasuq (U+05C3; 23,194), and U+05C4/U+05C5. These are not stripped by the committed Python algorithm.

**Validation correction recorded:** an early hand-written SQL prototype used incorrect decimal codepoint values (1424–1435), which would have removed cantillation marks rather than vowel points. That exploratory result was discarded. The final Python scan uses the explicit Unicode codepoints above; a corrected independent SQL aggregation using decimal values 1456–1467 and 1479 returned the same population counts as the Python scan. No incorrect preliminary counts are used in this report.

## 4. Representative candidate patterns

Examples below are orthographic candidates, not semantic equivalence claims.

### Within one root/form

- `root_form 11971.1`: several pointed patterns for the divine name occur as separate `root_vowel` rows. Depending on the cantillation context, the scan identifies groups of two to five pointed forms.
- `root_form 5882.1`: `בֵּ֣ית` and `בַּ֣יִת` (214 occurrences in the displayed group) share the same consonantal signature but remain separate vocalizations.
- `root_form 3533.1`: `אֲשֶׁ֥ר` and `אָשֵׁ֥ר` occur as a mechanical candidate pair (925 occurrences in the displayed group). This is precisely the kind of case where morphology and lexical identity must be checked rather than inferred from consonants.

### Across root/form boundaries

- `בְּנִ֣י`, `בְּנֵ֣י`, `בָּנִ֣י`, and `בָּנַ֣י` share a strict consonantal signature but occur under root/form IDs `6105.5` and `6627.1` (396 occurrences in the displayed group).
- `לְפָנַ֣י` and `לִפְנֵ֣י` share a strict consonantal signature and span two root/form parents (216 occurrences in the displayed group).

These cross-root examples show why a vowel-only relationship must not collapse root entries, morphology, or glosses.

## 5. Qere/ketiv and other apparatus rows

The inventory intentionally scanned `public.words.pointed` only. It did not mix in `word_variants`. The live `word_variants` table currently contains **1,204** rows with `variant_type='qere'` and `witness='MT'`. Those qere readings remain a separate apparatus population and require their own pointed-form inventory and provenance treatment. They must not be silently absorbed into the canonical-word vowel groups.

## 6. Data and change status

- Database rows scanned: 264,217.
- Transaction: read-only.
- Database modified: no.
- DDL/DML: none.
- Lexicon, root numbering, `root_vowel`, `word_variants`, alignments, embeddings, and vectorizer: unchanged.
- Output files were written only to Lampy's temporary directory:
  - `/tmp/hebrew-vowel-variants-20261107.csv` (7,124 member-form rows plus header; 2.1 MB)
  - `/tmp/hebrew-vowel-variants-20261107.summary.json` (6.2 MB)
- CSV SHA-256: `785213af65f4614bdee17e4e3daa3d2b8eb93fbca3431a7ad480618bacc712c1`
- JSON SHA-256: `419f52badf8c88862f36fc8e8fe3a3e7b1ec1d00f9bb6d3980e808c8c7644ef7`

The temporary exports are not yet committed to the repository. The committed PostgreSQL script is the reproducible inventory procedure.

## 7. Recommended next design

The current evidence supports a dedicated, explicit variant-group/member relation referencing existing `root_vowel` keys, without changing or merging the underlying lexical records:

- one group per `(is_aramaic, strict_consonantal_signature)`;
- members reference one or more `(root_id, root_form_seq, vowel_seq)` keys;
- preserve each exact `vowel_pattern`, source, and algorithm version;
- derive occurrence references through `words`;
- keep qere/ketiv in its existing apparatus and link it only through a separately reviewed cross-reference.

The group/member relation should cover all 3,349 candidate groups for explicit, uniform lookup, even though 2,977 groups are already siblings beneath one root/form parent. The 372 cross-root/form groups are the cases that cannot be linked by the existing root/form hierarchy alone.

Before any database write, review the full CSV in batches, especially groups with multiple root/form parents, and validate morphology/Strong's/lexicon associations. The next implementation step should be a reversible shadow-only prototype and validator, not a production migration.


The corpus contains one Hebrew row with an empty `pointed` value. It was included in the 264,217 rows-scanned total but excluded from signature formation.

Additional cross-root/form examples from the highest-occurrence groups:

| Shared pointed-form signature | Root/form IDs | Occurrences | Existing root entries |
|---|---|---:|---|
| `אֲדֹנִ֣י`, `אֲדֹנֵ֣י`, `אֲדֹנָ֣י`, `אַדְנֵ֣י` | `256.2`, `257.1` | 217 | `אדנ`, `אדני` |
| `אֱלֹהֵ֣י`, `אֱלֹהַ֣י` | `2051.6`, `2052.1` | 179 | `אלה`, `אלהי` |
| `בְּנִ֣י`, `בְּנֵ֣י`, `בָּנִ֣י`, `בָּנַ֣י` | `6105.5`, `6627.1` | 396 | `בנ`, `בני` |
| `לְפָנַ֣י`, `לִפְנֵ֣י` | `25056.11`, `25172.47` | 216 | `פנ`, `פני` |

The root-entry labels above are the database's existing root keys, not a linguistic adjudication. These cases demonstrate why the variant relation must point to existing form records rather than merge root entries: the same strict surface consonants can be parsed into different base/root structures.


## 8. Cross-check against existing lexicon records

A second read-only validation joined every candidate occurrence to `root_vowel` and `lexicon`:

- Candidate occurrence rows checked: **32,676**.
- `words.pointed` versus `root_vowel.vowel_pattern` after NFC: **32,676 matches; 0 mismatches**.
- Distinct candidate member keys at the `(root_id, root_form_seq, vowel_seq)` level: **7,148**.
- Candidate member keys with a corresponding `lexicon` row: **7,148; 0 missing**.

There are 7,124 distinct NFC pointed forms but 7,148 root-vowel keys because the same pointed form can occur under more than one root/form assignment. This confirms that a group/member relation can safely reference existing `root_vowel` keys while preserving each existing lexicon record; it does not justify merging those records.


### Cross-root group complexity

The 372 cross-root/form groups break down as follows:

- 367 Hebrew groups span exactly two root entries.
- 3 Hebrew groups span exactly three root entries.
- 2 Aramaic groups span exactly two root entries.
- No cross-root/form candidate in this inventory spans more than three root entries.

The three Hebrew groups spanning three root entries include:

| Pointed forms | Root/form IDs | Occurrences |
|---|---|---:|
| `לִבְנִ֥י`, `לִבְנֵ֥י` | `17764.1`, `6105.28`, `6627.44` | 56 |
| `לְבָנַ֖י`, `לִבְנִ֖י`, `לִבְנֵ֖י` | `17764.1`, `6105.28`, `6627.44` | 11 |
| `לְכָ֔ה`, `לֵכָ֔ה` | `14608.6`, `17908.2`, `17918.1` | 4 |

These are high-priority manual-review cases because one strict surface signature crosses several existing root entries. Preserve all existing root and lexicon records; the proposed relation is a cross-reference, not a normalization.


## 9. Lexical and morphology divergence check

I also grouped the candidate occurrences by strict signature and counted distinct existing Strong's values and morphology pattern IDs. These are occurrence-level differences, not claims that every member has a unique lexical analysis.

| Population | Candidate groups | Groups with multiple Strong's values | Groups with multiple morphology patterns | Groups with both |
|---|---:|---:|---:|---:|
| Hebrew | 3,323 | 1,223 | 2,932 | 1,115 |
| Aramaic | 26 | 3 | 23 | 3 |
| **Total** | **3,349** | **1,226** | **2,955** | **1,118** |

For the **372 cross-root/form groups**, 185 have multiple Strong's values and 370 have multiple morphology patterns; 185 have both. Thus, the shared consonantal signature is very often compatible with materially different existing morphological analyses, and in over a third of all groups with multiple Strong's values.

This is direct evidence against collapsing these records into a single lexical entry. The new relation must be a cross-reference between vocalized forms, with each member's root, morphology, Strong's association, glosses, and translation rendering left intact.
