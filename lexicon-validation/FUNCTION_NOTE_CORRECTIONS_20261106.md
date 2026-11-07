# Corrections to six Greek function-token review rationales

**Date:** 2026-11-06  
**Environment:** Isolated PostgreSQL database bible_greek_bridge_test_20261106, schema ylt_profile_shadow.  
**Change type:** Shadow-only annotation correction. No alignment endpoint or review status changed.

## Why this correction was needed

A comparison of the stored alignment-row notes with the full YLT verse and exact YLT-profile Greek sequence found six misleading explanations. Some referred to the wrong occurrence or incorrectly described a construction as possessive. The token positions themselves were correct; the problem was the rationale attached to the unaligned Greek rows.

## Corrected notes

| Reference | Greek position | Form | Correct contextual note |
|---|---:|---|---|
| Luke 2:34 | 21 | τῷ | In ἐν τῷ Ἰσραήλ; YLT “in Israel” has no separate article. |
| Acts 26:20 | 26 | τῆς | In ἔργα ἄξια τῆς μετανοίας, “works worthy of reformation”; genitive noun phrase, not a possessive. |
| 2 Corinthians 7:12 | 16 | τοῦ | Articular infinitive ἕνεκεν τοῦ φανερωθῆναι; YLT “for … being manifested”. |
| 2 Corinthians 7:12 | 18 | τήν | In τὴν σπουδὴν ἡμῶν, “our diligence”; article belongs to that noun phrase. |
| 2 Corinthians 7:12 | 21 | τήν | In τὴν ὑπὲρ ὑμῶν, a qualifying phrase modifying σπουδήν (“our diligence on your behalf”). |
| 2 Corinthians 7:12 | 27 | τοῦ | In ἐνώπιον τοῦ θεοῦ, “before God”; article is not separately expressed with the proper noun. |

## What changed and what did not

For each of the six existing alignment rows, the notes JSON and matching gnt_token_review reason were corrected. The following were explicitly asserted unchanged:

- alignment row identity and Greek sequence position;
- alignment_kind = unaligned_greek;
- alignment review status = not_expressed;
- alignment confidence = unresolved;
- gnt_token_review status = pending_review;
- no YLT token endpoint or proposed alignment count.

These rows remain open. Correcting a misleading rationale does not establish that the non-expression decision is final.

## Validation context

The eight current proposals remain intact. The review queue remains 31 pending, 479 proposed, and 25 legacy-overlap review rows. The full shadow validator and read-only eight-proposal validator are the governing checks; production tables, embeddings, vectorizer, API, and deployment were not changed.
