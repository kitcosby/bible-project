# Hebrew vowel-variant shadow validation — 2026-11-07

**Result:** PASS  
**Validator:** `lexicon-validation/scripts/validate_hebrew_variant_shadow.py`  
**Execution environment:** Lampy WSL, Python 3 / psycopg2  
**Source database:** `bible`  
**Shadow database:** `bible_hebrew_variant_shadow_20261107`  
**Source snapshot:** `sha256:2ea0a1b12a4335d11393c1baddd1d0e0327f67f70059973f82f52c9bb557a540`  
**Algorithm:** `nfc-remove-u05b0-u05bb-u05c7-v1`

## New invariant added

The validator now independently checks the **actual shadow membership**, not only the source-derived candidate set, and requires every group to contain at least two distinct NFC pointed forms.

It also runs two in-memory regression fixtures:
- Negative: two member entries with the same NFC pointed form must be rejected.
- Positive: the two Ezekiel 27:32 pointed forms must remain distinct.

The validator reports the number of groups checked, minimum/maximum distinct forms, and whether the negative fixture passed.

## Execution result

The updated validator completed with exit code 0 and returned:

| Assertion / count | Result |
|---|---:|
| Validation passed | true |
| Source rows scanned | 264,217 |
| Candidate groups | 3,349 |
| Language-scoped members | 7,148 |
| Unique root-vowel keys | 7,145 |
| Candidate occurrences | 32,676 |
| Cross-root groups | 372 |
| Qere MT rows kept separate | 1,204 |
| Candidate-status groups | 3,349 |
| Groups with at least two distinct NFC forms | 3,349 |
| Minimum distinct forms per group | 2 |
| Maximum distinct forms per group | 6 |
| Negative distinct-form fixture passed | true |
| Member-language mismatches | 0 |
| All members have root_vowel parents | true |
| All members have lexicon rows | true |
| Source-table counts match clone | true |
| Database modified | false |
| Production database modified | false |

Source-table row counts matched the shadow clone:
- `words`: 264,217
- `root_vowel`: 126,966
- `lexicon`: 126,966
- `root_form`: 57,816
- `root_entry`: 30,149
- `word_variants`: 542,553
- `books`: 66
- `verses`: 31,311
- `morph_patterns`: 3,438

The existing independent checks also passed: exact source-derived group/member reconstruction; algorithm and snapshot match; cross-language membership handling; qere separation; lexical-parent resolution; and source-table row-count equality.

## Reproducibility and preservation

- Validator source SHA-256 after change: `08437eaa1c9b1f4876720d924fefb9722321180c214a8277f3c533c42d9820ac`.
- A byte-identical pre-change backup was retained on Lampy at `C:\Temp\validate_hebrew_variant_shadow.py.pre-distinct-form-20261107`.
- The validator uses read-only database sessions. It ran against `bible` and the isolated shadow clone; it performed no DDL/DML.
- This is a snapshot-specific validator. Expected inventory counts and the source snapshot hash must be deliberately revised for a new corpus snapshot; do not silently reuse this result for later data.
- The test fixtures verify the invariant function. The live shadow query verifies all current groups. These checks do not replace a future API integration test or least-privilege role test.

## Scope boundary

This validates the isolated research shadow only. No production schema/data, lexical records, source text, YLT text/alignment, API code, database roles/grants, or running services were changed. The read-only API remains a draft contract; no endpoint has been implemented or deployed.
