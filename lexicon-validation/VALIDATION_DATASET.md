# YLT Lexicon Validation Dataset

**Status:** Initial test specification; expected outcomes are partly pending independent source review.  
**Rule:** Tests validate data provenance and alignment, not conformity to another Bible translation.

## Test case catalogue

| ID | Passage | Corpus | Test focus | Expected result / assertion |
|---|---|---|---|---|
| V-OT-001 | Genesis 1:1 | Hebrew OT | Basic Hebrew tokenization, Strong's and YLT association | Verse text matches pinned YLT USFM; each mapping references an existing Hebrew word and YLT token |
| V-OT-002 | Psalm 23:1-6 | Hebrew OT | Repeated lemmas, repeated surface forms, inflections | Repeated occurrences remain distinct word records; aggregate lexicon retains all contexts |
| V-OT-003 | Isaiah 53:11 | Hebrew OT | Grammar repair regression | Existing R2/R1g/R1s associations remain stable; no mapping is lost |
| V-OT-004 | Genesis 1:2 | Hebrew OT | Prefixes, particles and multiple morphemes | Do not force a one-to-one English token where YLT renders a Hebrew construction as a phrase |
| V-NT-001 | Matthew 1:1 | TR Greek | Genealogy terminology, repeated forms, Strong's and morphology | Source Greek witness, YLT text and KJV bridge are independently identified; no inferred gloss replaces YLT |
| V-NT-002 | John 1:1 | TR Greek | Article, copula, word order and lexical distinction | Preserve Greek token sequence and YLT phrase mapping; test multiple English words per Greek token |
| V-NT-003 | John 9:21 | TR Greek | Confirmed parser omission and positional bridge mismatch | Parser must retain the source token `autou` once, preserve its alternate Strong's/morphology analyses, and resolve downstream positions 23–24; `shall` and `speak` must not remain orphaned |
| V-NT-004 | Colossians 4:10 | TR Greek | Confirmed parser omission and positional bridge mismatch | Parser must retain the source token `barnaba` once, preserve both morphology alternatives, and resolve downstream positions 11–21; `him` must not remain orphaned |
| V-NT-005 | 1 John 5:7-8 | TR / Byzantine | Textual tradition differences | Witnesses remain separate; absence/presence of text is not silently harmonized |
| V-NT-006 | Romans 8:1 | TR / Byzantine / SBL | Variant witness and serialization | Each witness returns its own tokens, lemma/morphology and mappings; no cross-witness positional join |
| V-NT-007 | Luke 1:1-4 | TR Greek | Punctuation, quotation and formatting | Punctuation is not emitted as lexical tokens unless source tokenization explicitly treats it so |
| V-NT-008 | Mark 1:1 | TR Greek | Words without direct English equivalents / textual variants | Unaligned words are represented as unaligned, not assigned to a neighboring word |

## SBL and Greek-variant integration cases

- Verify gnts_alignment and gnts_ylt_renderings exist, record exact row counts, and check all parent references and verse-local positions.
- Compare SBL bridge output against the pinned MorphGNT normalized-form field; do not treat it as a dictionary lemma.
- Verify the Flask API exposes the intended TR, Byzantine and SBL witness data independently, or explicitly documents which witnesses are not served.
- Verify PWA rendering retains lexical source/provenance fields and does not present LXX-derived glosses as contextual NT definitions.

## Parser-specific regression cases

- `parsed/JOH.UTR` commit `7fd4d02c3e5adebd379ebfbc824040820dde10fc`, John 9:21: 24 source token occurrences; the current parser output stored 23. The pipe-delimited `autou` variant must be retained as one occurrence, with both Strong's alternatives preserved as metadata.
- `parsed/COL.UTR` same commit, Colossians 4:10: 21 source token occurrences; the current parser output stored 20. The pipe-delimited `barnaba` token must be retained once, with both morphology alternatives preserved as metadata.
- These tests must assert both token count and token sequence against the source, not only successful parsing or a final verse position.

## Automated invariants

1. Every mapping row resolves to an existing parent word in the same witness.
2. Every verse-local Greek position satisfies `1 <= position <= token_count`.
3. YLT word positions are unique within their intended tokenization scope and preserve source order.
4. No Greek witness is joined to another witness by positional number alone.
5. Every Strong's identifier is validated against the source convention; sentinel/unknown values remain explicit.
6. Every lemma/gloss response carries its source and matching method.
7. Repeated occurrences are never collapsed into a single occurrence-level record.
8. Aggregate lexicon contexts are reproducible from occurrence-level records.
9. Unicode normalization is tested without destroying Greek accents/breathings or Hebrew niqqud/cantillation needed by the source.
10. Punctuation stripping is tested against quotes, apostrophes, em-dashes, brackets and verse formatting.
11. All unaligned tokens are counted and inspectable; no automatic nearest-neighbor fallback is accepted without an explicit scoring/evidence record.
12. Read-only validation queries do not mutate production tables.

## Test evidence format

Each executable test result should record:

- Test ID and test version.
- Database snapshot identifier and timestamp.
- Source repository commit and source archive hashes.
- Witness and reference.
- Original token, Strong's, lemma and morphology values.
- Current mapping and expected mapping.
- Evidence source and confidence classification.
- Pass/fail/needs-review outcome.

## Automated validator

A read-only PostgreSQL validator is now available at `eval/validate_ylt_lexicon_postgres.py`. It requires `BIBLE_DATABASE_URL`, starts a read-only transaction, checks Hebrew/TR/Byzantine parent references, position bounds, duplicate bridge keys, Strong's G0 count and SBL/LXX exact lemma-match coverage, and emits focused records for John 9:21 and Colossians 4:10. It does not mutate the database.

Initial live run (2026-11-06): Hebrew orphan mappings 0; TR out-of-range alignment rows 3; TR orphan YLT rendering rows 3; Byzantine out-of-range rows 0; Byzantine orphan rendering rows 0; duplicate keys in the checked bridge tables 0; TR G0 occurrences 5; SBL words with exact LXX lemma/gloss match 0. The validator returned a nonzero status because the TR positional/orphan checks fail, as intended.

## Current readiness

The Hebrew gold set already includes 30 manually aligned verses (Genesis 1, Psalm 23 and Isaiah 53), with reported baseline precision 0.7984 and recall 0.5039 at the current operating point. The pipe-delimited TR parser cases now have an executable reproducer at `eval/test_nt_parser_variants.py`. Both tests are marked expected-failure against the current parser; they must become ordinary passing regressions after the parser correction. The remaining Greek alignment cases are specifications, not yet a machine-executable gold set. Independent manual annotation is required before treating all expected Greek word associations as gold truth.
