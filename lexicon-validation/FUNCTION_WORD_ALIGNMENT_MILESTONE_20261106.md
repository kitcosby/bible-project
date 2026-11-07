# Function-word alignment review milestone — 2026-11-06

## Complete coverage

All 267 initially unrendered Greek function-word positions in the 116 low-margin verse contexts have an explicit review disposition. Each Greek source position is represented exactly once in the consolidated review bundle.

- 228 proposed direct or phrase-level alignments.
- 39 retained as unresolved, non-expressed, or context-dependent.
- Zero validation errors across Greek source positions and proposed YLT target positions/surfaces.
- 31 proposed YLT source tokens already have legacy production associations. These are preserved as possible overlaps, not automatically labelled errors.
- Two YLT source-token positions intentionally receive multiple Greek proposals as phrase groups: 2 Corinthians 3:1 εἰ μή → “except”, and Acts 7:26 ἵνα τί → “wherefore”.

## Category breakdown

| Category | Reviewed | Proposed | Pending |
|---|---:|---:|---:|
| Initial high-priority set | 53 | 49 | 4 |
| Remaining conjunctions | 46 | 44 | 2 |
| Remaining articles | 67 | 37 | 30 |
| Remaining prepositions | 72 | 69 | 3 |
| Remaining particles/conditionals | 17 | 17 | 0 |
| Remaining miscellaneous function words | 12 | 12 | 0 |
| **Total** | **267** | **228** | **39** |

## Interpretation and safeguards

The 228 proposals are not approved production alignments.

- Articles may be expressed as English articles, substantival “those/whoever”, or absorbed into possessives, demonstratives, and articular infinitives.
- Prepositions may be explicit, phrase-level, case-marked, or idiomatic.
- Conjunctions may be rendered by “and”, “but”, “also”, “because”, “then”, “therefore”, or a whole purpose/cause clause.
- Phrase groups may map multiple Greek tokens to one YLT token or one Greek token to multiple YLT tokens. Do not split these into false one-to-one links.
- A YLT token with an existing legacy association is not necessarily in conflict with the proposed candidate Greek token. The legacy table uses a different, variant-inclusive production sequence. Never compare legacy Greek position numbers to isolated candidate positions numerically.
- No legacy association is overwritten. The proposal bundle records the old association so later profile migration can preserve both provenance layers.

## Selected corrections made during review

- Matthew 21:7 distinguishes two occurrences of αὐτῶν: the earlier one modifies “garments” (“their”), while the final one means “upon them”. The final Greek token is proposed against YLT “them”, not “their”.
- Acts 9:35 οἵτινες is not linked to “those”; the YLT clause is recast and “those” belongs to an earlier article/participle phrase.
- 2 Peter 1:1 genitive ἡμῶν maps to “our”; the distinct dative form maps to “us”.
- 2 Corinthians 3:1 εἰ μή and Acts 7:26 ἵνα τί are recorded as shared phrase-level mappings.
- Existing YLT/legacy overlap is recorded, not assumed to be a source defect.

## Artifact scope

The complete review bundle is a separate proposal/research layer covering 267 positions. It must not be conflated with the 39-case shadow token-review set (31 pending, eight proposed), nor with the 20 legacy-overlap positional-divergence cases.

The original working artifacts include the consolidated JSON/Markdown bundle and category-level review files for high-priority cases, conjunctions, articles, prepositions, particles/conditionals, and miscellaneous function words. Their proposals remain review candidates, not production mappings.

No production DDL/DML, API changes, embedding/vectorizer changes, repository merges, or deployments were performed for this review.
