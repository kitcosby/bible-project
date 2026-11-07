# Hebrew vowel-only variant audit — source-code review

**Date:** 2026-11-07  
**Scope:** Read-only review of repository builders, OSHB parser, schema, and variant methodology.  
**Status:** Code-level findings established; corpus-wide candidate inventory not yet run. No database or source changes.

## 1. User rule

Hebrew word forms whose consonantal sequence is identical and whose only differences are vowel points (niqqud) must be linked as variants. Preserve the exact pointed forms as separate readings. A variant link must not merge their lemma, morphology, semantic gloss, Strong's number, or translation alignment.

This is a relationship between forms, not an instruction to normalize away vowels or merge lexical entries.

## 2. Existing pipeline findings

### OSHB parser

worker-out/oshb/parse_oshb.py preserves the source <w> text in pointed, including slash morpheme separators. Its unpointed() function retains only codepoints U+05D0–U+05EA. Thus the unpointed export removes vowel points, cantillation, and other non-letter marks together; it is useful as a consonantal surface key but cannot classify which marks differ.

The parser emits ketiv and nested qere as separate rows in document order. This is intentional and already feeds the dedicated qere apparatus.

### Existing word_variants builders

build_variants.py currently builds variant_kind='spelling' rows for the v1-medial versus academic-final consonant conventions and documented surface anomaly alternatives. It does not compare pointed forms or create niqqud-only relationships.

build_variants_kq.py creates variant_kind='textual', witness='MT', variant_type='qere' rows. It compares consonantal skeletons to align ketiv and qere, and stores the qere pointed form in variant_text. This is a distinct Masoretic reading apparatus, not a general vowel-only variant linker.

The schema's word_variants primary key is (word_id, variant_seq). It attaches a reading to one corpus occurrence. It has no explicit group identifier or membership relation connecting multiple distinct word_id records that share a consonantal skeleton. Therefore it cannot, by itself, express the requested cross-occurrence linking cleanly.

### Existing root/vowel grouping

build_roots3.py creates root_vowel rows by grouping each exact pointed string beneath a (root_id, root_form_seq) pair. Distinct pointed strings therefore already receive distinct vowel_seq values within a root/form, and words with the same pointed string share that root_vowel identity.

This is a useful existing structural relationship, but it is **not yet a vowel-only variant apparatus**:
- grouping is scoped to an existing root/form assignment, not globally to an exact consonantal surface signature;
- the builder groups distinct pointed strings without determining whether the difference is only vowel points, cantillation, dagesh, or another mark;
- it does not preserve a pairwise/group-level explanation that a specific pair differs only in niqqud;
- it is a lexical numbering tier, not a textual-variant provenance record.

The audit must inspect root_vowel membership before proposing any new table, so it can reuse or reference existing IDs and avoid duplicating work already represented structurally.

### Other consonantal normalization

assemble_bible.py's cons_key() retains Hebrew letters and folds final forms (ךםןףץ → כמנפצ). That is appropriate for its OSHB crosswalk, but must not be reused as the strict vowel-only variant key: the user's rule requires identical consonantal spelling, and final-form differences are not vowel differences.

## 3. Recommended data model

Do not overload the existing qere rows or the spelling-convention rows. Add a distinct, explicit form-variant grouping relation after the read-only inventory establishes its scope.

Suggested normalized model:

- hebrew_form_variant_group: one row per exact consonantal spelling and comparison convention, with source/provenance and a documented grouping rule.
- hebrew_form_variant_member: links a group to each distinct pointed form (and, where appropriate, its corpus word_id occurrences), preserving exact pointed text and source identity.

Alternative: a nullable variant_group_id on a dedicated form-variant entity, not on words directly, if multiple corpus occurrences share one pointed form. Avoid putting a single group ID on a lexical entry: one consonantal spelling can have several distinct vocalizations and each form may have its own morphology/lemma.

Keep existing word_variants for occurrence-specific spelling/textual readings, including qere, unless a later schema review demonstrates a safe normalized integration. The new group should link to, not replace, those records.

## 4. Deterministic candidate rule

For each pointed Hebrew token from one explicitly identified source:

1. Preserve the raw source string byte-for-byte and record its source, verse/token reference, and parser version.
2. Normalize to Unicode NFC for comparison while retaining the raw string. Do not silently strip or reorder characters in stored values.
3. Parse Hebrew combining marks explicitly. Remove only the recognized vowel-point code points to form the strict comparison signature. The initial vowel-point set is U+05B0–U+05BB plus U+05C7 (sheva, hataf vowels, hiriq, tsere, segol, patah, qamats, holam, holam haser, qubuts, qamats qatan).
4. Retain consonant letters exactly, including matres lectionis and final forms. Do not fold final forms, remove yod/vav/he, or collapse consonant sequences.
5. Retain dagesh/mapiq (U+05BC), meteg (U+05BD), shin/sin dots (U+05C1/U+05C2), cantillation (U+0591–U+05AF), maqaf, paseq, slash/morpheme separators, and any other non-vowel characters in the comparison signature. If these also differ, the pair is not a strict vowel-only match and must be classified separately.
6. Group only distinct pointed forms with exactly the same resulting signature and at least one difference among the recognized vowel points. Identical pointed strings are duplicates/occurrences, not variants.
7. Preserve every distinct vocalization as a separate member. Attach morphology and lemma at the appropriate occurrence/form level; never infer that same consonants imply same lemma or meaning.

The code-point set must be validated against the Unicode Hebrew block and the corpus's actual strings before production use. In particular, confirm the intended treatment of holam variants, qamats qatan, slash separators, and normalization ordering on real corpus specimens.

## 5. Required edge-case tests

- Same consonants, patah vs qamats: candidate vowel-only variant.
- Same consonants, sheva vs hiriq: candidate vowel-only variant.
- Same consonants and vowels, dagesh present vs absent: not vowel-only.
- Same consonants and vowels, shin dot vs sin dot: not vowel-only.
- Same letters except final kaf vs medial kaf: not vowel-only under the strict rule.
- Added/removed mater lectionis (ו/י/ה/א): not vowel-only.
- Different cantillation or meteg in addition to vowel differences: separate pointing/accents case, not auto-grouped as vowel-only.
- Qere/ketiv pair: retain its existing qere apparatus classification; do not relabel as vowel-only merely because consonants happen to match.
- OSHB slash morpheme boundaries or maqqef tokenization differences: do not erase separators to force a match.
- Unicode composed/decomposed input: NFC-equivalent forms compare consistently, while raw source strings remain recoverable.

## 6. Audit sequence before any write

1. Read-only inventory from the canonical words.pointed source and, separately, OSHB pointed; never mix source editions in one grouping pass.
2. Report distinct consonantal signatures, number of pointed forms per signature, candidate vowel-only pairs/groups, and excluded near-matches (dagesh, accents, sofit, matres, separators).
3. Cross-tab candidates by lemma, morphology, Strong's, root/form/vowel group, and verse occurrences. Flag same-consonant groups containing multiple lemmas or incompatible morphology for human review; do not discard them automatically.
4. Reconcile candidates with existing word_variants spelling and qere rows to prevent duplicate or misleading apparatus entries.
5. Run deterministic tests and a small hand-adjudicated gold set. Measure false-positive and false-negative examples before proposing schema migration.
6. Only then stage a new group/member schema on a database copy, with exact before/after row-multiset checks, foreign-key checks, and idempotence verification.

## 7. Findings and limits

**Established from source code:** the OSHB parser preserves pointed text but its unpointed projection removes all non-Hebrew-letter codepoints; the spelling builder does not create vowel-only links; qere is already represented separately; the current variant table has no cross-occurrence group key.

**Not established:** number of eligible vowel-only pairs in the corpus; how many are already co-located under the same root_vowel parent; how many strict vowel-only pairs cross existing root/form boundaries; or whether the live database has additional local changes not present in GitHub.

**No changes performed:** no database writes, schema changes, parser changes, corpus-wide query, embedding/vectorizer operation, production access, or deployment. This report is a code-level audit and implementation design only.
