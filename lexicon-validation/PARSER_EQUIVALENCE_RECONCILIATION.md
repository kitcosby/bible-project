# Parser equivalence count reconciliation

Date: 2026-11-06

## Corrected result

The two branch-mode runs are separate comparisons and should not be collapsed into one count.

| Mode | Common verse keys compared | Exact sequences | Different sequences | Key-set caveat |
|---|---:|---:|---:|---|
| First-variant mode | 7954 | 7954 | 0 | Luke 17:36 exists upstream as an empty verse key but is absent from the port; Revelation 17:7–8 excluded. |
| Second-variant mode | 7947 | 7947 | 0 | Revelation 17:7–8 excluded. |

## Why the earlier counts appeared inconsistent

- First-variant mode reported 7,955 “exact” comparisons because the original comparator used dict.get(ref, []). For Luke 17:36, the upstream parser emitted an empty verse object, while the port emitted no key. The comparator treated the missing port key as an empty sequence and counted it as exact.
- Corrected first-variant result: 7,954 common verse keys; all 7,954 sequences are identical. One additional upstream-only key, Luke 17:36, has zero words.
- Second-variant mode: 7,947 common verse keys; all 7,947 sequences are identical.
- Both runs exclude Revelation 17:7 and 17:8 from direct equality because upstream librobinson applies its documented OLB workaround to those references. The port deliberately preserves Revelation 17:8 separately.

## Luke 17:36 source condition

The UTR source line is an empty-first-branch alternative: 17:36 | | duo ... . In first-variant mode, upstream creates an explicit empty verse object. The port currently omits the verse key when the selected branch has no words. This is a structural key-preservation issue, not a differing non-empty Greek word sequence. Preserve the empty verse status explicitly in future parser output if verse-key equivalence is required.

## Classification

- Verified derivation: first variant mode has 7,954/7,954 exact common sequences, plus one upstream-only empty verse key.
- Verified derivation: second variant mode has 7,947/7,947 exact common sequences.
- Not verified: direct parser equivalence for Revelation 17:7–8; these remain a documented special case.
- No production changes: this was a read-only parser comparison; no production or candidate database writes were made.