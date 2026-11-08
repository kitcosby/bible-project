# Hebrew vowel-only variants — read-only BibleApp API contract

**Date:** 2026-11-07  
**Status:** Draft contract for review; no API code, database grants, schema, or deployment changes made.  
**Scope:** Read-only exposure of the independently validated Hebrew/Aramaic vowel-only candidate groups in `bible_hebrew_variant_shadow_20261107`.

## 1. Decision and integration boundary

The first integration should be a read-only, token-protected API over the isolated shadow database. It must not query or modify the production `bible` database and must not reuse the existing BibleApp translation-authoring connection.

The current Lampy checkout is `/opt/bible-app-api`, branch `feat/bible-app-legacy-db-adapter`, HEAD `62cd51e39973011d1d1a0201250a48cf21bbc8a0`. Its existing API adapter uses the `bible_app` database for translation-authoring tables. Its `DATABASE_URL` and role `bible_app_api` are not the connection for the corpus or the variant shadow database.

The public default branch of `kitcosby/BibleApp` is a separate scaffold: its OpenAPI file currently describes only `GET /healthz`, and its Drizzle schema package is a stub. The deployed Lampy branch has additional `/api/bible/*` routes, while its checked-in OpenAPI file does not describe those routes. Therefore, implementation must target the actual deployed branch and reconcile its API specification before generating clients. Do not assume the public default-branch architecture document describes the deployed API.

**Proposed isolation:**
- Add a distinct read-only PostgreSQL connection for the variant shadow database, using a new environment variable such as `HEBREW_VARIANT_DATABASE_URL`.
- Use a dedicated login role with only the minimum `CONNECT`, schema `USAGE`, and table `SELECT` privileges required by the reviewed queries. No writes, sequences, temporary objects, migrations, or superuser connection.
- Keep PostgreSQL bound to localhost. Keep the API localhost-bound and behind the existing trusted ingress.
- Apply the sandbox-token middleware explicitly to every new lexicon route. The current router-level middleware protects `/api/bible/*`; a route outside that prefix must not be assumed protected.
- Do not change the existing `bible_app_api` role, its database, or existing translation routes.

This is a proposed deployment architecture, not an assertion that the new role, connection, routes, or grants already exist.

## 2. Resource naming and semantics

Proposed base path:

`/api/lexicon/hebrew-vowel-variants`

Use the term **related pointed forms** in user-facing UI. The relation is a strict orthographic comparison, not a claim of shared lexeme, synonymy, semantic equivalence, identical morphology, Strong's identity, or translation equivalence.

The service must preserve these distinctions:
1. Candidate orthographic group and its member forms.
2. Existing lexical assignments (root, root-form, Strong's, morphology, gloss).
3. Exact source-word occurrences and verse references.
4. Textual witnesses/apparatus readings.
5. YLT translation text and alignment.

Only items 1–3 are in this first API scope. Textual witnesses and YLT alignment are not ordinary group members and must not be folded into this response.

## 3. Proposed read-only operations

### 3.1 Resolve a source word to its candidate group

`GET /api/lexicon/hebrew-vowel-variants/by-word/{wordId}`

Purpose: allow BibleApp to ask whether the currently selected source-word occurrence belongs to a candidate group.

Response: `200 application/json`.

- If the word belongs to a candidate group, return the group identifier, language, and relation label.
- If it does not, return `{ "group": null }` rather than treating an ordinary word as an exceptional server error.
- The lookup must resolve the word's existing root-vowel key and language from source data; clients must not calculate signatures or infer membership from displayed strings.
- Validate `wordId` as a positive safe integer. Invalid input: `400`.

### 3.2 Read a group and its members

`GET /api/lexicon/hebrew-vowel-variants/{variantGroupId}`

Purpose: show the candidate's related pointed forms.

Return:
- Group identifier.
- Language as a stable enum: `hebrew` or `aramaic`.
- Relation label: `vowel-only-orthographic-variant`.
- Algorithm version, normalization form, and source snapshot identifier.
- Member list, each resolved from the existing `root_vowel`, `root_entry`, and `root_form` records.
- Exact pointed form from `root_vowel.vowel_pattern`; do not normalize the returned display value.
- Root and root-form identifiers/labels from `root_entry` and `root_form`.
- Occurrence count computed from matching `words` rows in the selected source snapshot.
- Strong's and morphology are occurrence-level data (`words.strongs` and `words.morph_pattern_id` joined to `morph_patterns.pattern`), not intrinsic member properties. If the UI summarizes them, label them as observed occurrence assignments and preserve per-occurrence detail. The `lexicon` table itself contains only the `(root_id, root_form_seq, vowel_seq)` membership key; no gloss column was found in it.
- An explicit statement that the relation does not adjudicate lexical identity or meaning.

Do not return the non-vowel signature as a replacement spelling or a user-facing form. It may be included in maintainer-only diagnostics, not the ordinary reader response.

### 3.3 Read occurrences for a member

`GET /api/lexicon/hebrew-vowel-variants/{variantGroupId}/members/{memberKey}/occurrences?limit=50&cursor=...`

Purpose: support drill-down without returning the full corpus in the group response.

Return paginated occurrence records containing:
- Stable source `wordId` (`words.word_id`).
- Book/chapter/verse reference via `words.verse_id` → `verses` → `books`.
- Exact raw source token from `words.pointed` (and optionally `words.unpointed`).
- `word_pos` for within-verse order.
- Occurrence-level Strong's (`words.strongs`) and morphology (`words.morph_pattern_id` → `morph_patterns.pattern`) where present.
- Language mapped explicitly from the source `words.is_aramaic` flag (`0` Hebrew, `1` Aramaic in the inspected snapshot); do not assume this legacy integer column has the same type as the shadow group's boolean flag.
- Any source-snapshot or corpus provenance required to trace the token.

The raw occurrence token must come from the source occurrence record, not be reconstructed from the normalized signature or copied from a representative member form. The cursor must be opaque and stable for the selected snapshot. Clamp `limit` to a documented maximum (proposed maximum: 100). Invalid cursor or limit: `400`.

The exact member-key URL encoding and occurrence join columns must be fixed only after the deployed source schema is inspected and the query is independently tested. Do not guess column names or construct the route around unverified assumptions.

## 4. Response contract sketch

Illustrative shape only; field names and identifier serialization must be reconciled with the actual source schema before OpenAPI implementation.

```json
{
  "group": {
    "id": 504,
    "language": "hebrew",
    "relation": "vowel-only-orthographic-variant",
    "dataset": {
      "algorithmVersion": "strict-hebrew-vowel-removal-v1",
      "normalizationForm": "NFC",
      "sourceSnapshotId": "sha256:...",
      "validation": "passed"
    },
    "members": [
      {
        "memberKey": {
          "rootId": 0,
          "rootFormSeq": 0,
          "vowelSeq": 0
        },
        "pointedForm": "exact stored pointed form",
        "root": "root label from root_entry",
        "rootForm": "form metadata from root_form",
        "occurrenceCount": 0
      }
    ],
    "interpretiveLimit": "Orthographic relation only; lexical identity and meaning are not adjudicated."
  }
}
```

The example is schematic. The numeric identifiers and placeholder values are not asserted as a production response. Do not use the illustrative `review_status='reviewed'` value as evidence of lexical or text-critical adjudication. The current group status field is too broad for that purpose. Until review-state semantics are separately defined and stored, omit adjudication status from the reader API. Member-level review, lexical adjudication, and textual-critical adjudication are distinct states.

## 5. Data and validation requirements

The API must read the shadow prototype as built and independently validated:
- 3,349 groups (3,323 Hebrew; 26 Aramaic).
- 7,148 language-scoped members.
- 32,676 source occurrences in candidate groups.
- 372 cross-root groups.
- All members resolve to existing `root_vowel` and lexicon records in the validated snapshot.
- Hebrew and Aramaic memberships remain separate.
- Qere/ketiv records remain outside canonical membership.
- Source tables and production records remain unchanged.

Before enabling any route, the release gate must include all of the following:
1. Re-run the independent read-only validator against the exact shadow snapshot used by the service.
2. Verify each group contains at least two **distinct NFC pointed forms**, not merely two member keys. This invariant is not enforced by the prototype DDL's primary key alone.
3. Verify every member's source pointed form reconstructs the stored strict signature.
4. Verify occurrence language, exact raw token, verse reference, and source provenance.
5. Verify qere/ketiv and external textual witnesses are excluded from canonical member responses.
6. Verify the source snapshot and algorithm version match the validated release manifest. If the manifest is missing, mismatched, or validation has failed, disable the feature or return `503`; do not silently serve stale groups.
7. Verify the database role cannot write, create objects, access unrelated databases, or read unrelated application/user tables.
8. Verify all endpoints are GET-only and that unauthorized requests receive `403`.
9. Verify no route performs DDL, DML, or writes to production tables.

## 6. Ezekiel 27:32 acceptance fixture

The API and UI must preserve the documented separation:
- MT source token `בְּנִיהֶם֙`, word_id 238432, H5204, remains the base-text occurrence.
- Alternative pointed form `בְּנֵיהֶם֙`, H1121, remains a distinct member/reading as represented in the validated candidate group.
- The LXX reading “their sons” is external witness evidence, not an MT member or qere row.
- YLT “their sons” and its current alignment anomaly remain translation/alignment evidence, not a canonical member.
- The UI must not label the forms synonyms or silently replace the MT form.

The operational BibleApp default remains MT for this verse. The underlying text-critical question remains open.

## 7. Error and operational behavior

- `400`: invalid path/query parameter or cursor.
- `403`: missing or invalid sandbox token.
- `404`: requested group or member does not exist.
- `503`: shadow database unavailable, validator state missing/failed, or snapshot freshness check fails.
- `500`: unexpected server failure; never expose SQL text, credentials, filesystem paths, or connection strings.
- Health checks must not disclose credentials or detailed database internals.
- Log request ID, route, status, and timing; do not log the sandbox token, database URL, or full sensitive headers.

## 8. Implementation sequence

1. Confirm the deployed branch, commit, working tree, and live service entrypoint before editing. The deployed checkout and public default branch are not interchangeable.
2. Inspect the exact shadow table definitions, source-table joins, occurrence fields, and current grants using read-only inspection. **The table/column and occurrence-join inspection is now complete; see §10.**
3. Finalize and independently execute the read-only query plan against the shadow DB; verify row-level language mapping and all join counts.
4. Define a dedicated read-only role and connection plan; review privileges before applying any grant.
5. Add OpenAPI operations to the deployed branch's contract, generate client schemas, and add GET-only handlers with explicit authorization.
6. Test against the isolated shadow database only. Include unauthorized, malformed input, absent membership, Hebrew, Aramaic, same-root, cross-root, and Ezekiel 27:32 fixtures.
7. Prove read-only behavior with database privilege tests and before/after source/shadow row-count and checksum comparisons.
8. Review the UI copy and source-provenance display.
9. Require separate explicit approval before merging, changing production database grants/schema, connecting to production corpus data, or deploying.

## 9. Current disposition

**Contract drafted for review; implementation not started.** No API files were changed. No database grants, schema, or data were changed. No service was restarted or deployed.

The schema and source occurrence joins have now been inspected read-only. The next blocker is to execute and independently validate the proposed read-only query set, then review the dedicated database role and privilege boundary. No role or grant has been created.

## 10. Read-only schema inspection completed on Lampy

Inspected the isolated database `bible_hebrew_variant_shadow_20261107` through PostgreSQL read-only catalog and SELECT queries. No DDL, DML, grants, or service changes were made.

Observed table shapes:
- `hebrew_vowel_variant_group`: `variant_group_id`, `is_aramaic` (boolean), `non_vowel_signature`, `normalization_form`, `algorithm_version`, `source_snapshot_id`, `source_relation`, `review_status`, `created_at`.
- `hebrew_vowel_variant_member`: `variant_group_id`, `is_aramaic`, `algorithm_version`, `source_snapshot_id`, `root_id`, `root_form_seq`, `vowel_seq`.
- `root_vowel`: member key plus `vowel_pattern` and `word_count`.
- `root_entry`: `root_id`, `root`, `word_count`.
- `root_form`: keyed by `root_id, form_seq` (the column is `form_seq`, not `root_form_seq`); contains affix/display metadata and example forms.
- `lexicon`: only the three-column member key `root_id, root_form_seq, vowel_seq`; it does not itself contain gloss, Strong's, or morphology fields.
- `words`: `word_id`, `orig_word_id`, `verse_id`, `word_pos`, `pointed`, `unpointed`, `letters`, `strongs`, `strongs_source_id`, `morph_pattern_id`, `is_aramaic`, `root_id`, `root_form_seq`, `root_vowel_seq`.
- `verses`: `verse_id`, `book_id`, `chapter`, `verse`; `books`: `book_id`, `name_en`, `name_he`.
- `morph_patterns`: `pattern_id`, `pattern`, `language`, `parse_status`, `parse_notes`.

The legacy `words.is_aramaic` column is `bigint`, not boolean. In the inspected source snapshot, value `0` occurs on 259,812 Hebrew words and value `1` on 4,405 Aramaic words. The shadow group/member language flag is boolean. The query layer must map this explicitly and verify unexpected values fail closed.

The occurrence join path was verified with a SELECT:
`words` joins `verses` on `verse_id`, then `books` on `book_id`; morphology joins `morph_patterns` on `pattern_id = words.morph_pattern_id`. Strong's is stored directly on each `words` occurrence as text. Therefore Strong's and morphology must be returned as occurrence-level observations, not asserted as one fixed attribute of a member.

**Ezekiel 27:32 fixture observed in group 504:**
- Member 1: root_id 6627, root `בני`, root_form_seq 4, vowel_seq 11, pointed form `בְּנֵיהֶם֙`, root_vowel word_count 2.
- Member 2: root_id 21384, root `ני`, root_form_seq 3, vowel_seq 1, pointed form `בְּנִיהֶם֙`, root_vowel word_count 1.
- Matching `words` query returns exactly three occurrences: H1121 in Jeremiah 11:22 and Jeremiah 17:2; H5204 at Ezekiel 27:32 (word_id 238432). Exact pointed forms and occurrence-level morphology were returned from source rows.
- Group 504 carries algorithm `nfc-remove-u05b0-u05bb-u05c7-v1` and source snapshot `sha256:2ea0a1b12a4335d11393c1baddd1d0e0327f67f70059973f82f52c9bb557a540`.

A catalog query returned no foreign-key constraints for the inspected legacy corpus tables (`words`, `lexicon`, `root_vowel`, `root_form`, `root_entry`, `verses`). The API must not rely on those legacy joins being database-enforced; query validation and integrity checks must explicitly verify them. This observation does not negate the declared foreign keys on the two new shadow variant tables.

**Implication for the contract:** member forms come from `root_vowel.vowel_pattern`; root labels come from `root_entry.root`; root-form metadata joins using `root_form.form_seq`; exact occurrences and Strong's/morphology come from `words`; verse display joins through `verses` and `books`. The current response sketch has been corrected accordingly.