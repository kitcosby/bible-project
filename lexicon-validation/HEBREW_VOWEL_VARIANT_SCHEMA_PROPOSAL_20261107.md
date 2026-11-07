# Hebrew vowel-only variant relation — schema and validation proposal

**Date:** 2026-11-07  
**Status:** Proposed only; not applied to any database.  
**Evidence base:** [Live inventory results](HEBREW_VOWEL_VARIANT_INVENTORY_RESULTS_20261107.md).

## 1. Design decision

Represent each strict vowel-only candidate as a group of existing vocalized form records. Do not merge `root_entry`, `root_form`, `root_vowel`, or `lexicon` rows.

The live scan found 3,349 candidate groups and 7,148 language-scoped member keys. All 7,148 have existing `lexicon` rows, and all 32,676 candidate occurrences match their referenced `root_vowel.vowel_pattern` after NFC normalization. This supports using `root_vowel` as the member target.

A group must be language-scoped (`is_aramaic`) because Hebrew and Aramaic must not be joined solely by surface spelling. The member key may occur in separate Hebrew and Aramaic groups if its underlying root-vowel record is used in both populations.

## 2. Proposed tables

Illustrative PostgreSQL DDL only:

```sql
CREATE TABLE public.hebrew_vowel_variant_group (
    variant_group_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    is_aramaic BOOLEAN NOT NULL,
    non_vowel_signature TEXT NOT NULL,
    normalization_form TEXT NOT NULL DEFAULT 'NFC'
        CHECK (normalization_form = 'NFC'),
    algorithm_version TEXT NOT NULL,
    source_relation TEXT NOT NULL DEFAULT 'public.words.pointed',
    review_status TEXT NOT NULL DEFAULT 'candidate'
        CHECK (review_status IN ('candidate', 'reviewed', 'rejected', 'superseded')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (is_aramaic, non_vowel_signature, algorithm_version)
);

CREATE TABLE public.hebrew_vowel_variant_member (
    variant_group_id BIGINT NOT NULL
        REFERENCES public.hebrew_vowel_variant_group(variant_group_id),
    root_id BIGINT NOT NULL,
    root_form_seq BIGINT NOT NULL,
    vowel_seq BIGINT NOT NULL,
    PRIMARY KEY (variant_group_id, root_id, root_form_seq, vowel_seq),
    FOREIGN KEY (root_id, root_form_seq, vowel_seq)
        REFERENCES public.root_vowel(root_id, root_form_seq, vowel_seq)
);
```

The stored `non_vowel_signature` is the NFC form after removing only U+05B0–U+05BB and U+05C7. It deliberately retains all other codepoints, including cantillation and dagesh. The algorithm version records the exact codepoint policy used to create the group.

No pointed form needs to be duplicated in the member table: it is already stored verbatim in `root_vowel.vowel_pattern`. Occurrences and verse references remain available through `words`.

## 3. Build procedure

1. Build signatures from `words.pointed` using Unicode NFC and the reviewed vowel-point set.
2. Partition by `is_aramaic` and signature.
3. Retain only groups with at least two distinct normalized pointed forms.
4. Resolve each member to distinct `(root_id, root_form_seq, root_vowel_seq)` keys.
5. Insert group rows and member rows into an isolated shadow database only.
6. Preserve all existing root, form, vowel, lexicon, Strong's, morphology, and alignment rows.
7. Keep `word_variants` qere/ketiv records out of this builder. A later apparatus crosswalk can reference them separately without converting them into canonical word members.

Expected inventory-level assertions for the current corpus snapshot:

- 3,349 groups: 3,323 Hebrew and 26 Aramaic.
- 7,148 language-scoped member keys.
- 32,676 candidate word occurrences.
- 2,977 groups within one root/form; 372 across multiple root/forms.
- 0 member keys missing a `lexicon` row.
- 0 candidate occurrences whose pointed form disagrees with `root_vowel.vowel_pattern` after NFC.

These are regression expectations for the captured snapshot, not permanent constants for future corpus revisions.

## 4. Required validator assertions

- Every group has at least two distinct member keys.
- All member `root_vowel.vowel_pattern` values produce the stored non-vowel signature.
- All occurrences reached through a member have the group's language flag.
- Every member has its `root_vowel` and `lexicon` parent.
- No member joins two groups with the same language, signature, and algorithm version.
- Forms differing in dagesh/mapiq, meteg, shin/sin dot, cantillation, consonants, matres, final forms, or separators do not share a group.
- Qere/ketiv rows are absent from canonical membership.
- All original `words`, `root_vowel`, and `lexicon` row counts and values remain unchanged.
- The candidate group/member counts match the read-only inventory for the same source snapshot.

## 5. Open decisions before implementation

1. Whether the persistent relation should be a regular table or a materialized view refreshed from the source corpus. A regular table preserves review status and provenance; a view avoids stale derived data but is more expensive and cannot hold manual review state.
2. Whether rejected candidates should remain in the table with `review_status='rejected'` or be excluded from the persistent relation and retained only in the audit export.
3. How to version the source corpus snapshot and parser version alongside `algorithm_version`.
4. Whether qere readings should later receive a parallel member type or a separate apparatus group, preserving the distinction between canonical vocalization variants and Masoretic reading alternatives.

## 6. Change boundary

This proposal has **not** been executed. No production or shadow DDL/DML, table creation, row insertion, or data update was performed. The next implementation must be a reversible isolated-shadow prototype with a verified backup and post-build validator. Production remains untouched.
