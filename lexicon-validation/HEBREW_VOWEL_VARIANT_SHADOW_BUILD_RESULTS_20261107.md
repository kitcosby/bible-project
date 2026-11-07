# Hebrew/Aramaic vowel-only variant shadow prototype — build and validation

**Date:** 2026-11-07  
**Status:** Built and validated in a dedicated isolated shadow database. Production remains unchanged.

## 1. Snapshot and isolation

The live PostgreSQL database `bible` was exported using a PostgreSQL custom-format dump. The dump was created read-only and restored into a newly created database named:

`bible_hebrew_variant_shadow_20261107`

The existing Greek bridge test database was not reused or modified.

Source dump:
- Path on Lampy: `/var/tmp/bible-hebrew-variant-source-20261107.dump`
- Format: PostgreSQL custom archive, compression level 6
- Size: 187 MB
- SHA-256: `2ea0a1b12a4335d11393c1baddd1d0e0327f67f70059973f82f52c9bb557a540`
- `pg_restore --list`: successful; 334 archive-list entries
- Restored shadow database size: 1,087 MB

Source database size at snapshot time: 1,174 MB. The restored clone's selected source-table counts match the live source counts exactly (see §4).

## 2. Implemented shadow relation

The prototype created only two new tables in the isolated shadow database:

- `public.hebrew_vowel_variant_group`
- `public.hebrew_vowel_variant_member`

The member table references existing `root_vowel(root_id, root_form_seq, vowel_seq)` keys. It also carries the group language, algorithm version, and source snapshot identifier, constrained by a composite foreign key to the parent group.

A unique member constraint enforces at most one group membership per root-vowel key, language population, algorithm version, and source snapshot. This still permits a root-vowel key to be a member in both Hebrew and Aramaic populations where the source occurrences require it.

Snapshot identifier:
`sha256:2ea0a1b12a4335d11393c1baddd1d0e0327f67f70059973f82f52c9bb557a540`

Algorithm version:
`nfc-remove-u05b0-u05bb-u05c7-v1`

No pointed forms are copied into the member table. Exact pointed patterns remain in `root_vowel.vowel_pattern`; occurrences and references remain in `words`.

## 3. Build results

The committed builder scanned the restored snapshot and inserted:

| Measure | Result |
|---|---:|
| Canonical word rows scanned | 264,217 |
| Variant groups | 3,349 |
| Language-scoped member rows | 7,148 |
| Unique root-vowel keys across those memberships | 7,145 |
| Candidate word occurrences | 32,676 |
| Groups spanning multiple root/form parents | 372 |

The difference between 7,148 language-scoped member rows and 7,145 unique root-vowel keys is three keys that are members in both Hebrew and Aramaic candidate populations. This is intentional and is why language is stored on each membership.

## 4. Independent validator results

The committed validator independently rescanned the live source database read-only, recomputed the candidate groups, and compared the expected group/member sets with the isolated shadow relation.

**Validation passed.**

| Assertion | Result |
|---|---:|
| Group set exactly matches recomputed inventory | Pass; 3,349 |
| Member sets exactly match recomputed inventory | Pass; 7,148 language-scoped memberships |
| Candidate occurrences | 32,676 |
| All member keys resolve to `root_vowel` | Pass |
| All member keys resolve to `lexicon` | Pass |
| Member/group language mismatches | 0 |
| Cross-root groups | 372 |
| Cross-root groups with multiple Strong's values | 185 |
| Cross-root groups with multiple morphology patterns | 370 |
| Cross-root keys with occurrences in both language populations | 8 |
| Root-vowel keys actually members in both candidate populations | 3 |
| MT Qere rows kept separate | 1,204 |
| Candidate-status group rows | 3,349 |

The validator also compared source-table row counts between live `bible` and the restored shadow clone:

| Source table | Live and shadow counts |
|---|---:|
| `words` | 264,217 |
| `root_vowel` | 126,966 |
| `lexicon` | 126,966 |
| `root_form` | 57,816 |
| `root_entry` | 30,149 |
| `word_variants` | 542,553 |
| `books` | 66 |
| `verses` | 31,311 |
| `morph_patterns` | 3,438 |

The 1,204 MT Qere rows remain in `word_variants`; the builder reads only canonical `words.pointed` and creates no Qere membership.

## 5. Safeguards and scope

- Production `bible` database: read-only access only; no DDL/DML.
- New database: `bible_hebrew_variant_shadow_20261107`.
- Existing `bible_greek_bridge_test_20261106`: not modified.
- Existing root, form, vowel, lexicon, Strong's, morphology, word, and apparatus records: not updated or merged.
- No API, deployment, alignment, embedding, or vectorizer changes.
- The only database writes were creation/population of the two new relation tables in the isolated Hebrew shadow database.

The prototype establishes that the proposed relation is technically viable against the captured snapshot. It does **not** adjudicate the linguistic correctness of each candidate. All 3,349 groups remain `candidate`; the remaining 357 cross-root groups still need member-level review, and Qere/Ketiv requires its own separate apparatus work.

## 6. Reproducible scripts

- [Shadow builder](build_hebrew_variant_shadow.py)
- [Independent read-only validator](validate_hebrew_variant_shadow.py)
- [Live inventory runner](audit_hebrew_vowel_variants_postgres.py)
- [All-group cross-root index](HEBREW_VOWEL_VARIANT_CROSS_ROOT_INDEX_20261107.csv)
- [Member-level cross-root review](HEBREW_VOWEL_VARIANT_CROSS_ROOT_REVIEW_20261107.md)
- [Schema proposal and constraints](HEBREW_VOWEL_VARIANT_SCHEMA_PROPOSAL_20261107.md)


## 7. Post-build backup and access restriction

After the validator passed, the completed shadow database was backed up again:

- Path on Lampy: `/var/tmp/bible-hebrew-variant-shadow-built-20261107.dump`
- Format: PostgreSQL custom archive, compression level 6
- Size: 187 MB
- SHA-256: `3cbb5efb19c7c11db7ea996458372a0835c3bb94f988767e08ae5d8136e869a0`
- `pg_restore --list`: successful; 349 archive-list entries

The shadow database's default PUBLIC connection and temporary-table privileges were revoked. Its database ACL now grants CONNECT/TEMP only to the owning `postgres` role. The restore and backup procedures are committed as [restore script](restore_hebrew_variant_shadow.sh) and [post-build backup script](backup_built_hebrew_shadow.sh).
