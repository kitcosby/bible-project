# Hebrew spelling-variant search QA — post-reboot rerun with tie-aware IVFFlat check

**Run date:** 2026-11-10, after the owner/QA-side reboot and staging restoration.  
**Runner:** `website/tests/run_hebrew_variant_qa.sh`; standalone PWA repeat: `node --test tests/*.test.mjs`.  
**Environment:** Lampy WSL; isolated QA workspace `/tmp/variant-search-qa`; Python 3; Node v24.22.1. Live target: staging Flask at `127.0.0.1:5058`, staging database, and Ollama at `127.0.0.1:11434`.  
**Backend branch:** `feat/hebrew-variant-embedding-search`; this update includes the tie-aware IVFFlat criterion change and the new Layer 2 transcript.  
**PWA branch:** `feat/hebrew-variant-embedding-search`, PR #5 head `6ccac910a72b1c5ba75647db1ee2d07062ff22bc`.  
**Integrity behavior:** staged `config.js` is deliberately staging-specific; it is checked for `/stage-bible` and `/api-stage` overrides rather than compared to branch-default hash. All other staged files retain exact-hash checks.

## Outcome by layer

| Layer | Actual runner output | Interpretation |
|---|---:|---|
| 1. Flask mock-based unit tests | **9 passed, 0 failed** | Passed |
| 2. Live API + staging index battery | **8 passed, 0 failed** | Passed on the tie-aware exact-distance boundary for both exact-form and fuzzy-form queries |
| 3. Ollama outage/restore | **BLOCKED** | Required explicit `OLLAMA_STOP_COMMAND` and `OLLAMA_START_COMMAND` not supplied; no service state changed |
| 4. PWA tests (runner) | **25 total: 24 passed, 0 failed, 1 TODO** | Functional tests passed; D11 remains a TODO |
| 5. Staging integrity | **6 passed, 0 failed, 0 blocked** | Hashes/config overrides and live route all passed |

**Evidence scope:** Layer 2 was rerun after the criterion change. Layers 1, 4, and 5 remain verified by the immediately preceding full post-reboot run; they were not rerun as part of this Layer 2-only follow-up. Layer 3 remains safely blocked. The earlier Layer 2 failure is superseded by the passing tie-aware rerun.  
**Standalone PWA rerun:** **25 tests, 24 pass, 0 fail, 1 TODO**, duration **213.162038 ms**.

## Hebrew search latency

**Prior full-run measurements:** first query **1.750 s**, repeat query **0.261 s**; no latency threshold flags. The first request was after reboot, but the model may have been pre-warmed by stack startup. Label it **first query after reboot / warm state unknown**, not a true cold start.

**Tie-aware Layer 2 rerun:** first query **1.059 s**, repeat query **0.182 s**; no latency threshold flags. The test harness still prints the legacy labels `cold` and `warm`; interpret the first as **first query during this post-reboot rerun / warm state unknown**, not a verified cold start.

**Owner's independent post-reboot spot check:** first Hebrew search returned HTTP 200 in **1.5 s**; warm repeat **0.12 s**. This is owner-reported spot-check evidence, separate from the suite's own 1.750/0.261 s measurements. It is also correctly labeled first-after-reboot, not pure cold.

## Layer 2 — tie-aware IVFFlat distance-boundary result

The original ordered-identity assertion was invalid for this corpus. Embeddings were generated from each variant's letters string alone, so rows with identical letters forms have bit-identical vectors and cosine distance zero to the same query vector. The QA-side database investigation measured 617 rows within 1e-6 of the אלהים query vector and 114 within 1e-6 of שלום. Within such large tie groups, top-ten row identity and order can vary by scan plan without indicating an ANN quality loss. The sequential scan's chosen ten identities are therefore not a valid gold standard for an ordered identity comparison.

The test now retains the important index-plan check at ivfflat.probes = 16, but compares each indexed result's distance against the exact sequential scan's rank-10 distance plus a 1e-6 tolerance. It also tests the genuine fuzzy query בראשיט under the same criterion. No returned IVFFlat row may be worse than the exact top-10 distance boundary. Both queries returned ten rows and passed.

Actual Layer 2 transcript:

```text
test_00_latency_cold_and_warm_record (__main__.LiveHebrewVariantApiTests) ... ok
test_01_pointed_unpointed_and_cantillation_normalize_to_same_exact_set (__main__.LiveHebrewVariantApiTests) ... ok
test_02_final_and_medial_mem_are_distinct_exact_conventions (__main__.LiveHebrewVariantApiTests) ... ok
test_03_exact_order_scores_and_duplicate_suppression (__main__.LiveHebrewVariantApiTests) ... ok
test_04_surrounding_whitespace_preserves_results (__main__.LiveHebrewVariantApiTests) ... ok
test_05_invalid_queries_have_standard_400_and_no_store (__main__.LiveHebrewVariantApiTests) ... ok
test_06_passage_search_is_unchanged (__main__.LiveHebrewVariantApiTests) ... ok
test_07_ivfflat_top_ten_is_within_exact_distance_boundary (__main__.LiveHebrewVariantApiTests) ... ok

----------------------------------------------------------------------
Ran 8 tests in 15.930s

OK
LATENCY cold=1.059s warm=0.182s flags=none
IVFFLAT query=בראשית probes=16 exact_rank10=0.000000000000 indexed_worst=0.000000000000 recall_boundary=PASS
IVFFLAT query=בראשיט probes=16 exact_rank10=0.026760801971 indexed_worst=0.026760801971 recall_boundary=PASS
```

The two latency values above are the first and repeat requests during this post-reboot rerun. Because stack startup may have pre-warmed the embedding model, the first is not asserted to be a true cold start. The earlier 1.750/0.261-second battery measurements and the owner's separate 1.5/0.12-second spot check remain recorded above as distinct observations.

The test intentionally does not assert ordered identity equality within tied distances. This is a correction to the QA criterion, not a relaxation of the search implementation's API ordering contract: API exact-result ordering and deduplication remain covered by the separate live API tests.

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
