# Acts 21:8 — “Paul and his company” phrase review

**Status:** Shadow phrase proposal; two phrase-member rows remain in legacy-overlap review. Not a production approval.

## Textual observation

The YLT renders the relevant phrase:

> Paul and his company

The YLT-profile Greek sequence is:

| Greek position | Greek token | Function |
|---:|---|---|
| 5 | οἱ | Substantival article, “the ones/those” |
| 6 | περί | Preposition, “around/about” |
| 7 | τόν | Accusative article before the proper name |
| 8 | Παῦλον | Paul |

The construction οἱ περὶ τὸν Παῦλον is a collective expression: “those around Paul”, idiomatically rendered “Paul and his company”.

## Proposed phrase structure

- Παῦλον (position 8) → YLT “Paul” (token 5): direct lexical head, proposed with high confidence.
- οἱ (position 5) and περί (position 6) jointly contribute to YLT “company” (token 8): phrase-member candidates.
- τόν (position 7) has no separate English article before “Paul”; classified not_expressed.
- YLT “and his” are part of the English phrase expansion and should not be forced into separate Greek token glosses.

The phrase group is AC-21:8-paul-company, with Greek positions [5,6,7,8] and YLT positions [5,6,7,8].

## Legacy conflict

The legacy YLT association for “company” stores Greek positions [7,8] (τόν Παῦλον). The contextual analysis instead places the collective “company” contribution in οἱ περὶ (positions 5–6), while Παῦλον (position 8) corresponds to “Paul”.

The shadow model therefore preserves the legacy positions and marks the two new phrase-member candidates (positions 5 and 6 → “company”) as legacy_overlap_review. It does not silently overwrite the old association.

## Related sequence distinction

The same verse contains two εἰς tokens:

- Position 10 → YLT “to” (token 14), “to Caesarea”.
- Position 14 → YLT “into” (token 19), “into the house”.

The two occurrences must not be conflated. Both contextual proposals are now represented separately in the shadow alignment table.

## Evidence classification

- **Established textual observation:** the YLT wording and Greek token sequence shown above.
- **Strong contextual proposal:** Παῦλον → “Paul”; first εἰς → “to”; second εἰς → “into”.
- **Phrase-level interpretation:** οἱ περὶ jointly express the collective “company” sense.
- **Unresolved legacy question:** whether the old “company” positions [7,8] should ultimately be superseded. They remain preserved pending review.

No production table, legacy association, embedding, vectorizer, API, or deployment was changed.