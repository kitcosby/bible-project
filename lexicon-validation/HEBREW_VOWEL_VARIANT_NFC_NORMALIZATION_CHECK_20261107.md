# Hebrew vowel-variant NFC normalization check

**Date:** 2026-11-07  
**Database:** read-only query of Lampy `bible`, `public.words`  
**Purpose:** test the current key-only NFC normalization rule against the upstream OSHB warning about Hebrew normalization.  
**Writes:** none. No database or corpus values were changed.

## 1. Upstream warning

The `openscriptures/morphhb` repository README explicitly warns that uses of OSHB should avoid NFC normalization, citing the SBL Hebrew User Manual's discussion of normalization. This warning is important because the corpus contains Hebrew combining marks in source-specific order. See the [OSHB repository README](https://github.com/openscriptures/morphhb#hebrew-normalization), especially its Hebrew Normalization section.

The project's existing rule uses NFC **only for comparison keys** and preserves raw source strings. This test checks whether normalization order changes the candidate inventory; it does not authorize normalizing stored text.

## 2. Live corpus measurement

A read-only export of `is_aramaic` and `pointed` from all 264,217 word rows was processed with Python's standard-library `unicodedata.normalize('NFC', ...)`.

| Measurement | Result |
|---|---:|
| Word rows | 264,217 |
| Distinct raw language-scoped pointed forms | 126,936 |
| Distinct NFC language-scoped pointed forms | 126,789 |
| Rows whose code-point sequence changes under NFC | 138,497 |
| Distinct raw forms whose sequence changes under NFC | 70,800 |
| Raw encodings collapsed into an already-existing NFC form | 147 |

Most inspected differences are canonical reordering of Hebrew combining marks, for example dagesh relative to a vowel point, or meteg relative to a vowel point. Raw source sequences must therefore remain recoverable and must not be overwritten by normalized strings.

Input export SHA-256: `c77f8bb747fe17cfe6ac5a7d12dd155c7df336d51f748c8925fe07dfcdfff4b5`.

## 3. Candidate inventory and order-of-operations test

A first raw-string grouping count is 3,486 groups / 7,408 raw pointed forms, because canonically equivalent raw encodings can be counted as distinct forms. Under the established NFC comparison convention the inventory is 3,349 groups / 7,124 distinct normalized pointed forms.

Crucially, two comparison pipelines were independently evaluated over the same live export:

1. NFC-normalize each pointed form, then remove only U+05B0–U+05BB and U+05C7 from the comparison key.
2. Remove only those vowel-point codepoints from the raw form, then NFC-normalize the remaining comparison key.

**Result:** both pipelines produce exactly 3,349 candidate groups, identical signature-key sets, and identical normalized member sets (zero member-set mismatches).

This establishes that, for the current corpus and the defined vowel-point removal set, the order of NFC normalization and vowel-point removal does not change candidate membership. It does not establish that all NFC use is universally safe for all Hebrew corpora or source encodings.

## 4. Disposition

- Retain the established 3,349-group NFC inventory for this source snapshot.
- Preserve every raw `words.pointed` source value unchanged.
- Continue to store/use normalized values only as comparison keys.
- Keep the normalization algorithm version and source snapshot with every group.
- Add regression tests for canonical-equivalent raw encodings, including meteg, dagesh/mapiq, cantillation, and vowel points.
- Do not treat the 3,486 raw-string count as a competing inventory: it overcounts canonical-equivalent encodings as distinct forms.
- Re-run this test whenever the source edition, parser, Unicode library, or normalization policy changes.

## 5. Limits

This is a corpus-specific computational check, not a Masoretic or textual-critical judgment. It tests only the live database snapshot and the specified code-point removal set. It does not prove that the upstream OSHB warning is irrelevant; it shows that the current comparison-only normalization rule is internally consistent for this dataset while raw source strings remain preserved.

No schema, database, lexical, morphology, Strong's, alignment, embedding, or vectorizer changes were made.
