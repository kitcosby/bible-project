# Hebrew spelling-variant search QA — post-reboot rerun

**Run date:** 2026-11-10, after the owner/QA-side reboot and staging restoration.  
**Runner:** `website/tests/run_hebrew_variant_qa.sh`; standalone PWA repeat: `node --test tests/*.test.mjs`.  
**Environment:** Lampy WSL; isolated QA workspace `/tmp/variant-search-qa`; Python 3; Node v24.22.1. Live target: staging Flask at `127.0.0.1:5058`, staging database, and Ollama at `127.0.0.1:11434`.  
**Backend branch:** `feat/hebrew-variant-embedding-search`; current PR #18 head at the start of this rerun included the staging-config integrity expectation fix.  
**PWA branch:** `feat/hebrew-variant-embedding-search`, PR #5 head `6ccac910a72b1c5ba75647db1ee2d07062ff22bc`.  
**Integrity behavior:** staged `config.js` is deliberately staging-specific; it is checked for `/stage-bible` and `/api-stage` overrides rather than compared to branch-default hash. All other staged files retain exact-hash checks.

## Outcome by layer

| Layer | Actual runner output | Interpretation |
|---|---:|---|
| 1. Flask mock-based unit tests | **9 passed, 0 failed** | Passed |
| 2. Live API + staging index battery | **8 tests: 7 passed, 1 failed** | Live API checks passed; IVFFlat top-10 still differs from exact sequential-scan top-10 |
| 3. Ollama outage/restore | **BLOCKED** | Required explicit `OLLAMA_STOP_COMMAND` and `OLLAMA_START_COMMAND` not supplied; no service state changed |
| 4. PWA tests (runner) | **25 total: 24 passed, 0 failed, 1 TODO** | Functional tests passed; D11 remains a TODO |
| 5. Staging integrity | **6 passed, 0 failed, 0 blocked** | Hashes/config overrides and live route all passed |

**Runner layer summary:** Layer 1 exit=0; Layer 2 exit=1; Layer 3 exit=0 (safe block); Layer 4 exit=0; Layer 5 exit=0. Layer 2 is the only failing layer.  
**Standalone PWA rerun:** **25 tests, 24 pass, 0 fail, 1 TODO**, duration **213.162038 ms**.

## Hebrew search latency

**Live battery measurements:** first query **1.750 s**, repeat query **0.261 s**; no latency threshold flags. The first battery request was after the stack reboot, but the model may have been pre-warmed by stack startup. Label it **first query after reboot / warm state unknown**, not a true cold start. The repeat is the warm repeat.

**Owner's independent post-reboot spot check:** first Hebrew search returned HTTP 200 in **1.5 s**; warm repeat **0.12 s**. This is owner-reported spot-check evidence, separate from the suite's own 1.750/0.261 s measurements. It is also correctly labeled first-after-reboot, not pure cold.

## Layer 2 failure — full diagnostic

The seven other live tests passed:

- Pointed, unpointed, and cantillation forms normalized to the same exact result set.
- Final and medial mem remained distinct exact conventions.
- Exact results preceded semantic neighbors; Genesis 1:1 was first; exact scores were null; embedding scores numeric; duplicates suppressed.
- Surrounding whitespace preserved results.
- Invalid queries returned expected 400 bodies and `Cache-Control: no-store`.
- Passage search regression returned HTTP 200.
- Latency recording completed.

The remaining test, `test_07_ivfflat_top_ten_matches_exact_sequential_scan`, **failed again**. It confirmed index use, then compared the ordered indexed top ten with the exact sequential-scan top ten at the configured probe count. Actual failure:

```text
FAIL: test_07_ivfflat_top_ten_matches_exact_sequential_scan (__main__.LiveHebrewVariantApiTests)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/tmp/variant-search-qa/backend/website/tests/hebrew_variant_live_qa.py", line 210, in test_07_ivfflat_top_ten_matches_exact_sequential_scan
    self.assertEqual(indexed, sequential, "IVFFlat top-10 differs from exact sequential-scan top-10")
AssertionError: Lists differ: [(217985, 1), (218340, 2), (218340, 1), (1,[72 chars], 2)] != [(1, 2), (218678, 1), (226403, 1), (218678,[72 chars], 2)]

First differing element 0:
(217985, 1)
(1, 2)

+ [(1, 2),
- [(217985, 1),
? ^    - -

+  (218678, 1),
? ^   ++

-  (218340, 2),
-  (218340, 1),
?    ^^^

+  (226403, 1),
?    ^^  +

+  (218678, 2),
   (1, 1),
-  (226403, 1),
   (226403, 2),
   (217985, 2),
-  (218678, 2),
-  (218678, 1),
?      ^^^

+  (217985, 1),
?     ++ ^

+  (218340, 1),
-  (1, 2)]
+  (218340, 2)]
?   + ++++
 : IVFFlat top-10 differs from exact sequential-scan top-10

----------------------------------------------------------------------
Ran 8 tests in 8.765s

FAILED (failures=1)
LATENCY cold=1.750s warm=0.261s flags=none
```

The test output's legacy labels `cold` and `warm` are not semantically accurate for this post-reboot run: the first measurement is reported here as first-after-reboot / warm state unknown. Do not interpret the index discrepancy as a service outage. It is a retrieval/index-quality issue. Do not weaken the exact comparison without first agreeing on the required recall/accuracy criterion.

## Layer 3 — blocked safely

Actual output:

```text
BLOCKED Layer 3: OLLAMA_STOP_COMMAND and OLLAMA_START_COMMAND must be supplied; no service state changed
```

The services were up, but the harness requires explicit approved commands for both stop and restore. No outage was induced. This avoids an unapproved service interruption and leaves the current running state intact.

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

The TODO is D11:

`KNOWN-ISSUE D11: initial non-sample footer reports database connected before data status is known`

It remains a documented UX issue, not a passing test and not a test failure.

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

Staging `config.js` intentionally retains the staging-only `/stage-bible` and `/api-stage` overrides. It was not overwritten. The other three staged files match their expected branch hashes.

## Reboot and stack lifecycle finding

Owner/QA-side verification: terminating the Lampy distro and waiting approximately 90 seconds left a fresh distro with no supervisor and all services down. Running the existing `LampyStackBoot` scheduled task restored the stack; production Flask (5057) and Ollama (11434) were verified answering. Staging Flask (5058) is not a supervisor program and had to be restarted manually. It will not survive a distro reboot under the current arrangement.

This is an operational finding, not a change made by this QA run. Recommend a separate hardening decision: decide whether the boot task itself should start the supervisor automatically and whether staging Flask should be managed as a supervisor program or another controlled service. No automation or service configuration was changed here.

## Safety and deployment state

- Suite executed against staging only; production was not queried or modified by the suite.
- No staging files/configuration were restaged or modified by the suite.
- No services were stopped or restarted by the suite.
- Layer 3 did not execute because explicit outage/restore commands were not supplied.
- No merge or PR state change was made.
- Both PRs remain open drafts; backend PR #18 still has the failing live index-quality test.
