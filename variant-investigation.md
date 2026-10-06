# Variant dropdown investigation

Date: 2026-10-01 ~05:22 PDT (12:22 UTC)
Issue: Kit reports the /variants page dropdown still contains words that have no variance,
even though app_v2.py has a filter (variant_word_ids()) meant to list only words with
>=2 distinct readings post medial/final fold. Code comment claims "128 in the corpus".

## 1. Table structure

```sql
CREATE TABLE word_variants(
  word_id INTEGER NOT NULL REFERENCES words(word_id),
  variant_seq INTEGER NOT NULL,
  variant_kind TEXT NOT NULL CHECK (variant_kind IN ('spelling','textual')),
  unpointed TEXT NOT NULL,
  letters TEXT NOT NULL,
  variant_text TEXT,
  convention TEXT,
  source TEXT,
  witness TEXT,
  variant_type TEXT,
  basis TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY(word_id, variant_seq)
);
```

## 2. Filter verification (local DB)

Replicated the exact SQL from variant_word_ids() with fold_finals registered:

- Total rows in word_variants: 528,565
- Distinct word_ids: 264,217
- Passing filter (>=2 distinct post-fold readings): **exactly 128**
- First 20: [51400, 71447, 84266, 84702, 86191, 86269, 86337, 86442, 86443, 94116, ...]

The filter works as designed. The "128 in the corpus" comment is accurate.

## 3. Live app verification

- Live /variants page (http://127.0.0.1:5058/variants on laptop): dropdown contains **exactly 128 `<option>` elements**
- The filter IS active in the deployed code
- supervisor bible-v2 uptime confirmed running current code (MD5-verified identical to local)

## 4. What the 128 words' "variance" actually is

ALL 528,565 rows are variant_kind='spelling'. There are ZERO 'textual' rows in the DB.

Sampled words (51400, 71447, 84266, 84702, 86191, 86269, 86337, 86442, 86443, 94116)
all follow the same 3-row pattern:

| seq | convention | source | basis |
|-----|-----------|--------|-------|
| 1 | v1-medial | v1-stored | v1 stored verbatim \| anomaly=truncation-at-maqaf OR anomaly=wrong-row-data |
| 2 | v1-medial | oshb-verbatim | OSHB <ref> tokens [...] |
| 3 | academic-final | oshb-verbatim | OSHB <ref> tokens [...] (same as seq2) |

After medial/final fold, seq2 and seq3 are identical. The "variance" is seq1 vs seq2:
- **truncation-at-maqaf**: v1 stored a truncated form (e.g. 'לכ' for 'לכלכהנא', 'אכרות' for 'אכרותאכרתלכ')
- **wrong-row-data**: v1 stored completely wrong data (e.g. 'ככ' for 'בני', 'ככ' for 'אלי', 'קק' for 'אמ')

These are **data quality artifacts** (v1 study-tool bugs), not manuscript variants.

## 5. Medial/final fold verification

Word 1 has 2 rows byte-identical in unpointed/letters (both 'בראשית'), differing only in
convention (v1-medial vs academic-final). The fold correctly collapses them to 1 distinct
reading, and word 1 is correctly EXCLUDED from the 128. The fold works.

## 6. Root cause assessment

The filter `variant_word_ids()` is **working correctly as coded**:
- It returns exactly 128 words
- The live dropdown shows exactly 128 options
- The medial/final fold correctly excludes letterform-only duplicates

However, the 128 words' "variance" consists entirely of **v1 data artifacts**
(truncation-at-maqaf, wrong-row-data) versus OSHB correct forms. There are no real
textual/manuscript variants in the database (all rows are kind='spelling').

**Likely root causes for Kit's complaint:**

A. **Definition mismatch**: Kit may not consider data-artifact differences (v1 bugs vs OSHB)
   as "real variance". The code treats any post-fold difference as variance. If Kit expects
   only genuine manuscript/textual variants, the dropdown should arguably be empty
   (since no 'textual' rows exist).

B. **Stale browser cache**: Kit may be seeing a cached version of the page from before
   the filter was deployed.

C. **Specific word not sampled**: There may be a specific word Kit looked at that behaves
   differently. The 10 sampled words all show 2 variants correctly.

## 7. Recommendation

Clarify with Kit what he means by "no variance":
- If he means the data-artifact differences shouldn't count, then the filter needs to
  also exclude rows where basis contains 'anomaly=' (or only include kind='textual').
- If he saw a specific word with 0/1 variants displayed, get the word_id to investigate.
- If it's a cache issue, a hard refresh would resolve it.

**Do NOT change code until Kit's definition of "variance" is clarified.**
