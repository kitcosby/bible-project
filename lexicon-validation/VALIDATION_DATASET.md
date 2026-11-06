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
| V-NT-003 | John 9:21 | TR Greek | Confirmed positional bridge mismatch | No reference exceeds verse token count; `λαλησει` does not inherit `himself`; `shall speak` association is reviewed against source text |
| V-NT-004 | Colossians 4:10 | TR Greek | Confirmed positional bridge mismatch | No reference exceeds verse token count; `αυτον` does not inherit `receive`; `him` association is reviewed against source text |
| V-NT-005 | 1 John 5:7-8 | TR / Byzantine | Textual tradition differences | Witnesses remain separate; absence/presence of text is not silently harmonized |
| V-NT-006 | Romans 8:1 | TR / Byzantine / SBL | Variant witness and serialization | Each witness returns its own tokens, lemma/morphology and mappings; no cross-witness positional join |
| V-NT-007 | Luke 1:1-4 | TR Greek | Punctuation, quotation and formatting | Punctuation is not emitted as lexical tokens unless source tokenization explicitly treats it so |
| V-NT-008 | Mark 1:1 | TR Greek | Words without direct English equivalents / textual variants | Unaligned words are represented as unaligned, not assigned to a neighboring word |

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

## Automated validator\n\nA read-only PostgreSQL validator is now available at `eval/validate_ylt_lexicon_postgres.py`. It requires `BIBLE_DATABASE_URL`, starts a read-only transaction, checks Hebrew/TR/Byzantine parent references, position bounds, duplicate bridge keys, Strong's G0 count and SBL/LXX exact lemma-match coverage, and emits focused records for John 9:21 and Colossians 4:10. It does not mutate the database.\n\nInitial live run (2026-11-06): Hebrew orphan mappings 0; TR out-of-range alignment rows 3; TR orphan YLT rendering rows 3; Byzantine out-of-range rows 0; Byzantine orphan rendering rows 0; duplicate keys in the checked bridge tables 0; TR G0 occurrences 5; SBL words with exact LXX lemma/gloss match 0. The validator returned a nonzero status because the TR positional/orphan checks fail, as intended.\n\n## Current readiness

The Hebrew gold set already includes 30 manually aligned verses (Genesis 1, Psalm 23 and Isaiah 53), with reported baseline precision 0.7984 and recall 0.5039 at the current operating point. The Greek cases above are currently a specification, not yet a machine-executable gold set. Independent manual annotation is required before treating all expected Greek word associations as gold truth.
