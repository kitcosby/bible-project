# Follow-up review of eleven pending Greek function-word cases — 2026-11-06

## Outcome

A contextual pass rechecked the eleven rows whose alignment records still had `review_status=unresolved` in the original 39-case function-word set. It used the complete YLT verse, the complete YLT-profile Greek sequence, and the existing legacy token associations.

- Eight cases now have context-supported `not_expressed` alignment dispositions, with high or moderate confidence.
- One case (Philippians 4:2, τὸ) is now a legacy-overlap review case because its candidate YLT target “the” has a conflicting legacy Greek position.
- Two cases remain unresolved: Acts 15:32 δέ and Acts 21:8 περί.
- No production data or legacy associations were overwritten.

## Case dispositions

| Reference | Greek | Disposition | Reason |
|---|---|---|---|
| Matthew 4:13, position 3 | τήν | Not separately expressed; high | εἰς τὴν Ναζαρέτ → “to Nazareth”; no separate English article. |
| Luke 4:16, position 4 | τήν | Not separately expressed; high | Same place-name construction: “to Nazareth”. |
| Acts 19:27, position 7 | τό | Not separately expressed; high | τὸ μέρος τοῦτο → “this department”; the demonstrative renders the phrase without a separate article. |
| Acts 22:25, position 14 | εἰ | Not separately expressed; moderate | Conditional εἰ introduces a direct-question construction; YLT uses “A man, a Roman, uncondemned — is it lawful…” without “if”. |
| Acts 22:25, position 17 | καί | Not separately expressed; moderate | Greek coordinates “Roman and uncondemned”; YLT compresses the description into an appositional list with punctuation. |
| Colossians 4:10, position 4 | ὁ | Not separately expressed; high | ὁ σύναιχμάλωτός μου → “my fellow-captive”; the article is absorbed into the possessive phrase. |
| James 4:15, position 2 | τοῦ | Not separately expressed; high | Articular infinitive ἀντὶ τοῦ λέγειν → “instead of your saying”; no standalone article. |
| Revelation 7:2, position 22 | αὐτοῖς | Not separately expressed; high | Redundant dative after οἷς; YLT expresses the recipient once as “to whom”. |
| Philippians 4:2, position 6 | τό | Legacy overlap; unresolved | Candidate τὸ → YLT “the” (token 11) in “the same”. But token 11 has legacy Greek position 8, φρονεῖν. A phrase group `PHP-4:2-the-same` records τὸ αὐτό → “the same” without overwriting the legacy association. |
| Acts 15:32, position 2 | δέ | Unresolved | δὲ καί has joint discourse/additive force in “Judas also and Silas”; assigning “also” to δέ alone would be speculative. |
| Acts 21:8, position 6 | περί | Unresolved | οἱ περὶ τὸν Παῦλον → “Paul and his company” is an idiomatic phrase. No distinct YLT preposition token is safely isolated. |

The machine-readable [11-case disposition ledger](ELEVEN_FUNCTION_WORD_CASE_DISPOSITIONS_20261106.csv) records the exact Greek positions, any candidate YLT target, review status, confidence, legacy positions, and rationale.

## Token-review versus alignment status

The Greek token-review table has no `not_expressed` status. Therefore, the eight new not-expressed alignment dispositions remain `pending_review` in `gnt_token_review`, with the reason field explicitly stating the contextual disposition. This is a schema limitation, not evidence that the linguistic assessment remains unresolved.

Philippians 4:2 is different: both the Greek token and YLT token are moved to `legacy_overlap_review`, preserving the candidate relationship and the old association. The two unresolved cases remain pending in token review and unresolved in alignment.

## Updated shadow totals

| Layer | Status | Rows |
|---|---|---:|
| Alignment | Proposed | 563 |
| Alignment | Not expressed | 29 |
| Alignment | Legacy overlap review | 4 |
| Alignment | Unresolved | 2 |
| Greek token review | Proposed | 510 |
| Greek token review | Legacy overlap review | 29 |
| Greek token review | Pending review | 31 |
| YLT token review | Proposed | 514 |
| YLT token review | Legacy overlap review | 41 |
| YLT token review | Pending review | 505 |
| YLT token review | Legacy only | 2,111 |

The original 39-case set now has eight proposed token-review rows, one legacy-overlap row (Philippians 4:2), and 30 pending rows. The current all-verse Greek pending queue is 31 because it also includes the Romans 16:27 article added during the five-verse sequence materialization. The current YLT pending queue is 505.

There are 29 alignment rows classified not_expressed, but 20 of those older rows still carry `confidence=unresolved`. The eight dispositions in this pass have high or moderate confidence; the one Romans 16:27 article also has moderate confidence. Those twenty older rows should be revisited rather than treated as settled.

## Validation and isolation

The full shadow validator passed after these changes:
- 2,444 YLT-profile Greek sequence words.
- 3,171 YLT tokens.
- 31 alignment groups.
- 598 YLT–Greek alignment rows.
- 3,171 YLT token-review rows.
- 570 Greek token-review rows.
- Only two alignment rows remain unresolved: Acts 15:32 δέ and Acts 21:8 περί.

Production read-only counts remained unchanged: 141,009 Greek words, 143,227 legacy rendering rows, 31,102 YLT verses, 31,102 embedding-store rows, and 31,102 non-null embeddings. All dispositions remain in the isolated shadow database; no production rows, API behavior, or embedding vectors were changed.
