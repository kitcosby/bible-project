# Five-verse YLT variant sequence materialization — 2026-11-06

## Result

Five additional verse sequences were committed to the isolated shadow database `bible_greek_bridge_test_20261106.ylt_profile_shadow` after a dry run and strict precondition checks.

| Verse | Robinson group | YLT selection | Sequence effect |
|---|---:|---|---|
| John 8:6 | 43:6 | A | Empty branch; YLT does not render the additional branch-B participial phrase. |
| Acts 3:3 | 44:3 | A | `λαβεῖν` already occurs in the base sequence; no insertion required. |
| Romans 16:27 | 45:7 | A | `ᾧ` already occurs in the base sequence; no insertion required. |
| Ephesians 6:24 | 49:3 | A | `ἀμήν` already occurs in the base sequence; no insertion required. |
| 1 John 2:23 | 62:3 | B | Adds the eight-token bracketed confession clause present in YLT: `ὁ ὁμολογῶν τὸν υἱὸν καὶ τὸν πατέρα ἔχει`. |

The 1 John insertion is marked `proposed_ylt_branch`, with null base positions and explicit dependency `62:3`. It is not represented as an inherited Robinson base token. The bracketed English text is preserved in the YLT token stream; bracketed Robinson subscription/paratext is excluded from verse sequences.

## Added shadow records

- 95 YLT tokens.
- 77 Greek sequence words.
- 45 new YLT token-review rows with status `pending_review`.
- 30 new Greek token-review rows with status `pending_review`.
- 30 corresponding unaligned-Greek alignment placeholders.

## Initial shadow totals immediately after materialization (before contextual review)

| Table | Rows |
|---|---:|
| Profiles | 4 |
| Textual variant groups | 261 |
| Textual variant branches | 522 |
| Profile variant selections | 783 |
| YLT-profile Greek sequence words | 2,444 |
| YLT tokens | 3,171 |
| YLT–Greek alignment rows | 582 |
| YLT token-review rows | 3,171 |
| Greek token-review rows | 565 |

Review status counts:

| Review layer | Status | Rows |
|---|---|---:|
| Greek token | Proposed | 479 |
| Greek token | Legacy overlap review | 25 |
| Greek token | Pending review | 61 |
| YLT token | Proposed | 473 |
| YLT token | Legacy overlap review | 37 |
| YLT token | Legacy only | 2,114 |
| YLT token | Pending review | 547 |
| Alignment | Proposed | 521 |
| Alignment | Not expressed | 20 |
| Alignment | Unresolved | 11 |
| Alignment | Pending review | 30 |

At this intermediate checkpoint, before contextual alignment review, the Greek pending queue was 61 rows (31 original plus 30 new) and the YLT pending queue was 547 (502 original plus 45 new). These are historical materialization-stage counts; the final current counts after contextual review are 32 Greek pending and 505 YLT pending, as reported below.

## Variant-selection status

Across the 261 YLT-profile variant groups:
- 224 inherited provisional selections.
- 17 reviewed against the stored YLT text.
- 14 not applicable to verse alignment (subscription/colophon groups).
- 5 explicit proposed YLT overrides (Mark 8:24, 2 Corinthians 7:12, 2 Corinthians 11:10).
- 1 unresolved verse-text group (Revelation 7:3).

The five newly reviewed groups above are materialized in the YLT sequence. Revelation 7:3 remains deliberately unmaterialized: its two branches differ in verbal mood, and no YLT-specific selection has been established. Do not infer a choice from the inherited KJV candidate sequence.

## Validation and isolation

The materialization script required exact pre-materialization table counts, checked YLT verse-text SHA-256 hashes, verified inherited words against production `public.gnt_words` by surface/Strong's/morphology at each source position, and required contiguous one-based token positions. Post-insert checks compared the complete inserted sequences and token rows against the dry-run manifest.

The final shadow validator passed:
- Exact expected table totals and review-status counts.
- Exact branch selections and sequence dependencies.
- The eight-token 1 John 2:23 branch-B insertion.
- All five new verse sequence/token counts and pending-row counts.
- No bracketed paratext in the verse sequence.
- No missing alignment targets, incomplete proposed endpoints, or orphan alignment groups.

Production read-only counts remained:
- `gnt_words`: 141,009
- `gnt_ylt_renderings`: 143,227
- `ylt_verses`: 31,102
- `ylt_verses_embedding_store`: 31,102
- Non-null stored embeddings: 31,102

No production rows, API behavior, embedding vectors, or vectorizer configuration were changed. This is an isolated research/shadow update only.


## Follow-up contextual alignment review

The five materialized verses were reviewed against their complete stored YLT wording, profile-specific Greek sequence, and existing legacy position associations. The review now records **46 contextual alignment rows**:

- 42 shadow alignment proposals.
- Three legacy-overlap rows retained for separate adjudication.
- One Greek article classified as not separately expressed (no YLT token assigned).
- Fourteen phrase groups preserve one-to-many, many-to-one, and grammatical phrase relationships.

### Phrase and token decisions

- **John 8:6:** the two occurrences of δέ are distinguished and linked to the two English “and” tokens; πειράζοντες → “trying”; ἔγραφεν → “he was writing”. A supplemental phrase group links κυψας to “having stooped”, retaining the legacy “stooped” link. Another group links τῷ to “the” in “with the finger”, retaining the existing legacy links to “with” and “finger”.
- **Acts 3:3:** ἰδών → “having seen”; ἠρώτα → “was begging”; ἐλεημοσύνην → “a kindness”; λαβεῖν → “to receive”. These are phrase-level proposals where English uses auxiliaries or an expanded infinitive.
- **Romans 16:27:** ᾧ → “to him” is a candidate phrase link; δόξα → “glory”; εἰς → “to”; τούς → “the”; αἰῶνας → “ages”. A supplemental phrase group links θεῷ to “God”, preserving the existing legacy link to “to”. The article ἡ before δόξα is not separately expressed in YLT “to him [be] glory”.
- **Ephesians 6:24:** τῶν ἀγαπώντων → “those loving”; ἐν ἀφθαρσίᾳ → “undecayingly”; and, in a supplemental phrase group, ἡ → “The” in “The grace”, while preserving the existing legacy link to “grace”.
- **1 John 2:23:** the new branch-B clause is linked phrase by phrase: ὁ ὁμολογῶν → “he who is confessing”; τὸν υἱόν → “the Son”; καί → “also”; τὸν πατέρα → “the Father”; ἔχει → “hath”. The first-clause links already supported by legacy positions were retained without duplicate shadow links.

### Legacy overlaps deliberately retained

Three overlap rows arise from two legacy-position problems in Romans 16:27:

1. YLT “to” (token 9) has legacy Greek position 13, ἀμήν, although the contextual candidate for “to him” is ᾧ at YLT tokens 9–10.
2. The reverse side of that same mismatch is Greek ἀμήν (position 13): its candidate YLT target is “Amen” (token 16), but its legacy target is token 9, “to”. The candidate “Amen” link is therefore also marked `legacy_overlap_review`, not used to overwrite the legacy association.
3. YLT “the” (token 14) has legacy positions 22 and 25, διακόνου and Κεγχρεαῖς in the subscription; the contextual candidate is τούς at Greek sequence position 11 (“to the ages”).

All three candidate rows are marked `legacy_overlap_review` in the alignment layer. Neither legacy association was overwritten. The 1 John 2:23 first-clause links at YLT positions 6, 7, 9, 11, and 12 were independently checked against Greek positions [4,5], [4,5], [9], [7,8], and [7,8] respectively and retained as legacy-only rather than duplicated.

### Remaining deliberately unlinked YLT tokens

Three YLT tokens in the five new verses remain pending rather than being forced into a Greek link:

- Romans 16:27 “the” before “only wise God”: English article supplied without a Greek article.
- Romans 16:27 “[be]”: bracketed supplied copula; no Greek finite verb occurs.
- 1 John 2:23 “he” in “neither hath he the Father”: English subject supplied with third-person ἔχει; no independent Greek pronoun occurs.

The Greek article ἡ before δόξα remains `not_expressed` in the alignment layer and pending in the Greek token-review layer because that token-review table does not support a `not_expressed` status.

### Final queue counts after contextual review

| Review layer | Status | Rows |
|---|---|---:|
| Greek token | Proposed | 510 |
| Greek token | Legacy overlap review | 28 |
| Greek token | Pending review | 32 |
| YLT token | Proposed | 514 |
| YLT token | Legacy overlap review | 40 |
| YLT token | Pending review | 505 |
| YLT token | Legacy only | 2,112 |
| Alignment | Proposed | 563 |
| Alignment | Legacy overlap review | 3 |
| Alignment | Not expressed | 21 |
| Alignment | Unresolved | 11 |

Of the 45 YLT tokens initially queued as pending in the five new verses, 41 now have proposed links, one has a candidate link retained as a legacy-overlap case, and three remain pending. The current all-verse queues are [32 pending Greek positions](GREEK_TOKEN_REVIEW_QUEUE_PENDING_20261106.csv) and [505 pending YLT tokens](YLT_TOKEN_REVIEW_QUEUE_CURRENT_20261106.csv). The [45-row initial YLT queue snapshot](YLT_TOKEN_REVIEW_QUEUE_FIVE_NEW_VERSES_20261106.csv) is historical; the [three-row remaining queue for the five new verses](YLT_TOKEN_REVIEW_QUEUE_FIVE_NEW_VERSES_PENDING_20261106.csv) is current.

The machine-readable [46-row contextual alignment ledger](FIVE_VERSE_CONTEXTUAL_ALIGNMENT_PROPOSALS_20261106.csv) records all proposals, overlaps, and the not-expressed article. The [14 phrase-group definitions](FIVE_VERSE_CONTEXTUAL_ALIGNMENT_GROUPS_20261106.csv) preserve phrase-level evidence. The final validator is available at [eval/validate_ylt_profile_shadow_context_review_20261106.py](../eval/validate_ylt_profile_shadow_context_review_20261106.py), with its [successful output](FINAL_VALIDATION_AFTER_CONTEXT_REVIEW_20261106.txt).

### Final validation after contextual review

The updated full validator passed with:
- 2,444 YLT-profile Greek sequence words.
- 3,171 YLT tokens.
- 30 alignment groups.
- 598 YLT–Greek alignment rows.
- 3,171 YLT token-review rows.
- 570 Greek token-review rows.
- All endpoints and alignment-group references resolving.
- Five selected YLT verse-text branches materialized; Revelation 7:3 still unmaterialized and unresolved.

Production counts remained unchanged, including all 31,102 non-null stored embeddings. The contextual proposals and overlap decisions remain shadow-only research data, not production approvals.
