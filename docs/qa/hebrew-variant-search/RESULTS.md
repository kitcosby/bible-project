# Hebrew spelling-variant search QA — first full run

**Run date:** 2026-11-10  
**Runner:** `website/tests/run_hebrew_variant_qa.sh`  
**Environment:** Lampy WSL staging host; isolated temporary test worktree at `/tmp/variant-search-qa`; Python 3 and Node v24.22.1.  
**Backend branch head at test:** `a6a2f695b2852be507d0cde179a94e075ac89d67` (PR #18, still draft).  
**PWA branch head at test:** `6ccac910a72b1c5ba75647db1ee2d07062ff22bc` (PR #5, still draft).

## Outcome by layer

| Layer | Runner output | Interpretation |
|---|---:|---|
| 1. Flask unit tests | **9 passed, 0 failed** | Passed |
| 2. Live API battery | **8 skipped / BLOCKED, 0 run** | Flask staging listener was not running at 127.0.0.1:5058; no live assertions were passed |
| 3. Ollama outage/restore | **BLOCKED** | Flask staging listener was not running; Ollama was also not listening on 127.0.0.1:11434. No stop/start or service-state change was attempted |
| 4. PWA tests | **25 total: 24 passed, 0 failed, 1 TODO** | Functional tests passed; D11 remains a visible known issue, not a UX pass |
| 5. Staging integrity | **4 passed, 2 failed, 1 BLOCKED** | Staging drift remains: PWA index and config hashes differ; live Flask endpoint unavailable |

**Latency:** cold = BLOCKED / not measured; warm = BLOCKED / not measured. The staging API and Ollama were unavailable, so no latency value is claimed.

## Layer 5 failure details

1. **PWA index hash mismatch.** Staged SHA-256: `e6bdbe2bb5a4674baa247555af59e4089280adb6ea8c86142af8ccaa51b04dee`; current feature-branch SHA-256: `9da35996ca6a6db0c107bf43894829d8754732aa03b84c34a587e74d2cede7df`. The staged file is not the current branch head.
2. **PWA config hash mismatch.** Staged SHA-256: `c9126f16a3d80f7c952fce8a1476ae284e1019ae723407108fb4fa8b1ba41c32`; current feature-branch SHA-256: `60024580af53583a48d611f624faac87122dd20697b3aa8765d144194142de04`. The staged config does contain the required staging-only `/stage-bible` and `/api-stage` overrides, but it is intentionally not byte-identical to the branch's default `config.js`. This is still a failure against the requested exact-hash criterion; the staging override is not to be overwritten.
3. **Running Flask process check — BLOCKED.** Connection to `127.0.0.1:5058` was refused. This is not a 404 or a successful file-on-disk check.

The other staging checks passed: Flask `app_v2.py` hash matched; `sw.js` hash matched; service-worker cache version and Hebrew network-only bypass were present; staging config contained both staging API overrides.

## D11 known issue

The PWA runner reports:

`KNOWN-ISSUE D11: initial non-sample footer reports database connected before data status is known`

It is marked TODO in Node's test output by design. Do not count it as a fix or as a passing user-experience expectation.

## Full raw runner output

```text
=== Layer 1: Flask mock-based unit tests ===
test_database_exception_does_not_leak_secret_or_internal_detail (test_hebrew_variant_search.HebrewVariantSearchTests) ... ok
test_error_responses_all_carry_no_store (test_hebrew_variant_search.HebrewVariantSearchTests) ... ok
test_exact_matches_precede_deduplicated_embedding_neighbors (test_hebrew_variant_search.HebrewVariantSearchTests) ... ok
test_exact_matches_survive_embedding_service_outage (test_hebrew_variant_search.HebrewVariantSearchTests) ... ok
test_limit_is_clamped_to_one_and_twenty_five_and_honors_two (test_hebrew_variant_search.HebrewVariantSearchTests) ... ok
test_missing_variant_database_configuration_fails_closed (test_hebrew_variant_search.HebrewVariantSearchTests) ... ok
test_non_hebrew_query_is_rejected_before_embedding (test_hebrew_variant_search.HebrewVariantSearchTests) ... ok
test_three_hundred_hebrew_characters_are_accepted (test_hebrew_variant_search.HebrewVariantSearchTests) ... ok
test_wrong_embedding_dimension_returns_generic_502 (test_hebrew_variant_search.HebrewVariantSearchTests) ... ok

----------------------------------------------------------------------
Ran 9 tests in 0.016s

OK
=== Layer 2: live API + staging index battery ===
test_00_latency_cold_and_warm_record (__main__.LiveHebrewVariantApiTests) ... skipped 'BLOCKED: staging Flask at http://127.0.0.1:5058 is unreachable'
test_01_pointed_unpointed_and_cantillation_normalize_to_same_exact_set (__main__.LiveHebrewVariantApiTests) ... skipped 'BLOCKED: staging Flask at http://127.0.0.1:5058 is unreachable'
test_02_final_and_medial_mem_are_distinct_exact_conventions (__main__.LiveHebrewVariantApiTests) ... skipped 'BLOCKED: staging Flask at http://127.0.0.1:5058 is unreachable'
test_03_exact_order_scores_and_duplicate_suppression (__main__.LiveHebrewVariantApiTests) ... skipped 'BLOCKED: staging Flask at http://127.0.0.1:5058 is unreachable'
test_04_surrounding_whitespace_preserves_results (__main__.LiveHebrewVariantApiTests) ... skipped 'BLOCKED: staging Flask at http://127.0.0.1:5058 is unreachable'
test_05_invalid_queries_have_standard_400_and_no_store (__main__.LiveHebrewVariantApiTests) ... skipped 'BLOCKED: staging Flask at http://127.0.0.1:5058 is unreachable'
test_06_passage_search_is_unchanged (__main__.LiveHebrewVariantApiTests) ... skipped 'BLOCKED: staging Flask at http://127.0.0.1:5058 is unreachable'
test_07_ivfflat_top_ten_matches_exact_sequential_scan (__main__.LiveHebrewVariantApiTests) ... skipped 'BLOCKED: staging Flask at http://127.0.0.1:5058 is unreachable'

----------------------------------------------------------------------
Ran 8 tests in 0.000s

OK (skipped=8)
=== Layer 3: Ollama outage / restore regression ===
BLOCKED Layer 3: staging Flask is not listening at http://127.0.0.1:5058
=== Layer 4: PWA tests (canonical glob invocation) ===
✔ per-occurrence phrase comes first in each legacy dropdown group (3.350962ms)
✔ a phrase absent from the top twelve is prepended and the group remains capped (0.841506ms)
✔ root-code lemma words use the same phrase option builder without a Strong's number (0.598338ms)
✔ a saved lemma default remains effective when absent from the current phrase shortlist (1.278924ms)
✔ an available lemma-default phrase selects its existing dropdown index (0.962375ms)
✔ same-origin defaults preserve the Lampy mount contract (3.035334ms)
✔ a separately hosted deployment can override all three service origins (0.848554ms)
✔ passage meaning continues to use the existing verse embedding endpoint (2.77135ms)
✔ Hebrew spelling uses the separate variant embedding endpoint (0.81787ms)
✔ Hebrew mode rejects non-Hebrew input before making a request (0.860143ms)
✔ exact Hebrew spelling results are distinguished from embedding neighbors (0.836597ms)
✔ passage result labels preserve the computed Young's provenance (0.762601ms)
✔ the search view exposes both modes and gates the Genesis sample to passage mode (0.239301ms)
✔ Hebrew variant requests use 45 seconds while passage requests keep 8 seconds (1.618015ms)
✔ Hebrew exact-only outage warning is shown while exact results remain rendered (1.104015ms)
✔ Hebrew search never invokes the Genesis sample fallback; passage mode may (1.948091ms)
✔ switching search modes preserves the typed query and re-renders the selected mode (1.049167ms)
✔ KNOWN-ISSUE D11: initial non-sample footer reports database connected before data status is known (0.782873ms) # D11 is documented behavior awaiting a separate footer-state fix; do not treat as passing UX.
✔ CSRF bootstrap GET bypasses the shared API cache (30.686129ms)
✔ bearer-authenticated translation GET bypasses the shared API cache (1.406407ms)
✔ public API no-store responses are not inserted into API cache (1.484128ms)
✔ a previously cached no-store response is deleted rather than served (1.924266ms)
✔ indexed word-option GET bypasses shared cache to preserve choice-byte order (1.731086ms)
✔ current service-worker shell version retains the Hebrew variant network-only rule (0.222207ms)
✔ Hebrew variant search bypasses shared cache because results are query-specific and no-store (1.232639ms)
ℹ tests 25
ℹ suites 0
ℹ pass 24
ℹ fail 0
ℹ cancelled 0
ℹ skipped 0
ℹ todo 1
ℹ duration_ms 131.370088
=== Layer 5: staging integrity / drift checks ===
PASS Flask app_v2.py SHA-256 matches branch head: ca35e1314c98832f4840ef1ee2d9cb77471ec9b449ed088ac5844c7382a24205
FAIL PWA index.html SHA-256 mismatch: staged=e6bdbe2bb5a4674baa247555af59e4089280adb6ea8c86142af8ccaa51b04dee expected=9da35996ca6a6db0c107bf43894829d8754732aa03b84c34a587e74d2cede7df
PASS PWA sw.js SHA-256 matches branch head: 8154f321893373633d219e1e57a703cde5a7a9a35eef65281acc30dcbbbd28ae
FAIL PWA config.js SHA-256 mismatch: staged=c9126f16a3d80f7c952fce8a1476ae284e1019ae723407108fb4fa8b1ba41c32 expected=60024580af53583a48d611f624faac87122dd20697b3aa8765d144194142de04
PASS service-worker cache version and Hebrew network-only bypass
PASS staging config targets /stage-bible and /api-stage
BLOCKED running Flask process serves variant-search route: staging listener unavailable: [Errno 111] Connection refused
STAGING INTEGRITY COUNTS passes=4 failures=2 blocked=1
=== Runner exit summary ===
Layer 1 exit=0; Layer 2 exit=0; Layer 3 exit=0; Layer 4 exit=0; Layer 5 exit=1
```

## Safety and deployment state

- No production service, database, file, or configuration was read for test execution or modified.
- No staging file was restaged; no staging service was restarted or stopped.
- The outage test did not attempt to stop or start Ollama because the Flask staging listener was already down.
- No merge was performed and neither PR's state was changed.
