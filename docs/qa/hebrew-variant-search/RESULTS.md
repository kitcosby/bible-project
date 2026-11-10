# Hebrew spelling-variant search QA — restored-staging rerun

**Run date:** 2026-11-10 (Lampy local time, after the QA-side staging recovery reported at approximately 06:30 PT).  
**Runner:** `website/tests/run_hebrew_variant_qa.sh`; standalone repeat: `node --test tests/*.test.mjs`.  
**Environment:** Lampy WSL; isolated QA copies under `/tmp/variant-search-qa`; Python 3; Node v24.22.1. Live target was staging Flask at `127.0.0.1:5058`, staging database, and Ollama at `127.0.0.1:11434`.  
**Backend application branch at run:** `f5441e2e406e830d984286dda221738b4d51d107` (PR #18). The staging-integrity expectation was changed in this rerun to exempt the deliberately customized staging `config.js` from branch-default hash comparison and validate its two staging overrides instead. That exact change is now committed as `fe6154de40dfc614ae167e0ab5a5f2709a93db47`.  
**PWA branch at run:** `6ccac910a72b1c5ba75647db1ee2d07062ff22bc` (PR #5).

## Outcome by layer

| Layer | Actual runner output | Interpretation |
|---|---:|---|
| 1. Flask mock-based unit tests | **9 passed, 0 failed** | Passed |
| 2. Live API + staging index battery | **8 tests: 7 passed, 1 failed** | API behavior checks passed; pgvector IVFFlat top-10 did not equal exact sequential-scan top-10 |
| 3. Ollama outage/restore | **BLOCKED** | Explicit `OLLAMA_STOP_COMMAND` and `OLLAMA_START_COMMAND` were not supplied. No service state was changed |
| 4. PWA tests (runner) | **25 total: 24 passed, 0 failed, 1 TODO** | Functional tests passed; D11 remains a TODO, not a passing UX result |
| 5. Staging integrity | **6 passed, 0 failed, 0 blocked** | All staged hashes required to match and the staging-only config overrides were verified; live staging route returned HTTP 200 |

**Runner exit:** **1**, due only to Layer 2's IVFFlat-vs-exact top-10 assertion failure. Layer 1, Layer 3's blocked-safe exit, Layer 4, and Layer 5 returned exit 0.

**Measured Hebrew-search latency:** the live battery measured **1.307 s first query** and **0.204 s repeat query**. The first request is explicitly **first/warm-ish**, not a true cold start: Ollama was already running after the QA-side restore. The second is the warm repeat. No latency threshold flags were emitted.

**Standalone PWA rerun:** `node --test tests/*.test.mjs` independently returned **25 tests, 24 pass, 0 fail, 1 TODO**, duration **243.089534 ms**. This corroborates the PWA result from Layer 4.

## Layer 2 failure — full diagnostic

Seven live tests passed:

- Pointed, unpointed, and cantillation forms normalized to the same exact result set.
- Final and medial mem remained distinct exact conventions.
- Exact results preceded semantic neighbors; Genesis 1:1 was first; exact scores were null; embedding scores numeric; duplicates suppressed.
- Surrounding whitespace preserved results.
- Invalid queries returned the expected 400 bodies and `Cache-Control: no-store`.
- Passage search regression returned HTTP 200.
- The latency measurement test passed.

The remaining test, `test_07_ivfflat_top_ten_matches_exact_sequential_scan`, **failed**. It verified that PostgreSQL selected an IVFFlat index scan, then compared the indexed top ten against a sequential exact scan. The two ordered result lists differed:

```text
FAIL: test_07_ivfflat_top_ten_matches_exact_sequential_scan (__main__.LiveHebrewVariantApiTests)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/tmp/variant-search-qa/backend/website/tests/hebrew_variant_live_qa.py", line 210, in test_07_ivfflat_top_ten_matches_exact_sequential_scan
    self.assertEqual(indexed, sequential, "IVFFlat top-10 differs from exact sequential-scan top-10")
AssertionError: Lists differ: [(217985, 1), (218340, 2), (218340, 1), (1, 1), (226403, 1), (226403, 2), (217985, 2), (218678, 2), (218678, 1), (1, 2)] != [(1, 1), (1, 2), (217985, 2), (217985, 1), (218678, 1), (218678, 2), (218340, 2), (218340, 1), (226403, 2), (226403, 1)]

First differing element 0:
(217985, 1)
(1, 1)

- [(217985, 1),
? ^

+ [(1, 1),
? ^

+  (1, 2),
+  (217985, 2),
  (217985, 1),
+  (218678, 1),
+  (218678, 2),
  (218340, 2),
  (218340, 1),
-  (1, 1),
-  (226403, 1),
  (226403, 2),
-  (217985, 2),
-  (218678, 2),
-  (218678, 1),
-  (1, 2)] : IVFFlat top-10 differs from exact sequential-scan top-10

----------------------------------------------------------------------
Ran 8 tests in 9.677s

FAILED (failures=1)
LATENCY cold=1.307s warm=0.204s flags=none
```

This is a substantive retrieval/index-quality discrepancy, not a service-availability failure. The test proves the IVFFlat index was selected but does **not** prove its approximate top ten equals the exact top ten at `ivfflat.probes = 16`. Do not weaken or remove this assertion merely to obtain a green suite. Investigate index lists/probes, recall requirements, and whether the expected behavior is exact top-k or acceptable approximate recall before changing implementation or test criteria.

## Layer 3 — blocked safely

The outage harness reported:

```text
BLOCKED Layer 3: OLLAMA_STOP_COMMAND and OLLAMA_START_COMMAND must be supplied; no service state changed
```

The staging API and Ollama were reachable, but the test deliberately refuses to stop Ollama unless both explicit service-manager commands are configured. No outage was induced and no restoration action was needed. A separate authorization/owner-provided command pair is required to exercise this layer.

## Layer 4 — PWA results and known issue

Runner and standalone Node invocations both returned:

```text
tests 25
pass 24
fail 0
cancelled 0
skipped 0
todo 1
```

The single TODO is D11:

`KNOWN-ISSUE D11: initial non-sample footer reports database connected before data status is known`

It remains documented behavior awaiting a separate footer-state fix. It is not counted as a pass or a test failure.

## Layer 5 — staging integrity

Actual output:

```text
PASS Flask app_v2.py SHA-256 matches branch head: ca35e1314c98832f4840ef1ee2d9cb77471ec9b449ed088ac5844c7382a24205
PASS PWA index.html SHA-256 matches branch head: 9da35996ca6a6db0c107bf43894829d8754732aa03b84c34a587e74d2cede7df
PASS PWA sw.js SHA-256 matches branch head: 8154f321893373633d219e1e57a703cde5a7a9a35eef65281acc30dcbbbd28ae
PASS service-worker cache version and Hebrew network-only bypass
PASS staging config targets /stage-bible and /api-stage
PASS running Flask process serves variant-search route: HTTP 200
STAGING INTEGRITY COUNTS passes=6 failures=0 blocked=0
```

Staging `config.js` intentionally remains a staging-specific variant (SHA-256 begins `c9126f16a3d8`). It was **not** overwritten and is no longer compared to the branch's default config hash. Its required `/stage-bible` and `/api-stage` overrides are asserted directly. The other three staged files retain exact-hash checks.

## Safety and deployment state

- QA ran against staging only. Production Flask, production database, and production Ollama were not used for these tests.
- No staging files or configuration were restaged or modified by the run.
- No services were stopped or restarted by the test run.
- The outage test did not execute because no explicit stop/start commands were supplied.
- No merge was performed; PR #18 and PWA PR #5 were not changed in state.
- No PWA branch source was changed during this rerun.
