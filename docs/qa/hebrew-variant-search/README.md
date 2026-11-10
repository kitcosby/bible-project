# Hebrew spelling-variant search — repeatable QA suite

This suite encodes the independent QA review dated 2026-11-09 and the regression checks for defects D1–D11. It is deliberately split between mock-only tests, live staging checks, a controlled Ollama outage test, PWA tests, and staging drift checks.

## Safety boundaries

- **Staging only.** Default API target is `http://127.0.0.1:5058`; default DB credentials are loaded in-process from `/root/bible_app_pwa_stage_20261109.env`.
- The live DB test opens a read-only transaction and issues SELECT/SET statements only.
- The outage test refuses to stop Ollama unless both `OLLAMA_STOP_COMMAND` and `OLLAMA_START_COMMAND` are supplied. It restores Ollama in a `finally` path and verifies that it is healthy before declaring completion.
- The staging-integrity test is strictly read-only. Hash mismatches are reported; it never copies files, restarts a process, or changes config.
- Never point `BIBLE_VARIANT_QA_API_BASE`, `BIBLE_VARIANT_QA_STAGE_ROOT`, or the database URL at production.

## Repository layout

- Backend unit tests: `website/tests/test_hebrew_variant_search.py`
- Live API + index sanity: `website/tests/hebrew_variant_live_qa.py`
- Ollama outage/restore: `website/tests/hebrew_variant_outage_qa.py`
- Staging file/process drift: `website/tests/hebrew_variant_staging_integrity.py`
- PWA unit tests: `BibleApp-pwa/tests/*.test.mjs`
- PWA runtime and service worker: `BibleApp-pwa/index.html`, `sw.js`

## Run on demand

Backend mock tests:

```bash
python3 -m unittest discover -s website/tests -p 'test_hebrew_variant_search.py' -v
```

PWA tests (canonical invocation):

```bash
node --test tests/*.test.mjs
```

Live API and index battery:

```bash
python3 website/tests/hebrew_variant_live_qa.py
```

Controlled Ollama outage test. Set the service-manager commands for this Lampy installation first; do not guess them:

```bash
export OLLAMA_STOP_COMMAND='your staging-only stop command'
export OLLAMA_START_COMMAND='your staging-only start command'
python3 website/tests/hebrew_variant_outage_qa.py
```

Staging integrity (read-only):

```bash
python3 website/tests/hebrew_variant_staging_integrity.py
```

The orchestration script is `website/tests/run_hebrew_variant_qa.sh`. Set `PWA_DIR` to a local checkout of `kitcosby/BibleApp-pwa` if the repositories are not siblings.

## Manual browser / iPhone checklist

Cloudflare Access requires an email code per path and automated browsers do not retain the session. Do not automate the public tunnel. On the owner's iPhone, open the current staging tunnel URL (the Quick Tunnel hostname is ephemeral and must be supplied at run time), then:

1. Sign in with the existing account.
2. Confirm the sample-data banner is absent.
3. Run a passage-meaning search for `light`; confirm results render.
4. Switch to Hebrew spelling and search `בראשית`.
5. Search `שלום`.
6. Confirm exact spelling and embedding-similarity labels are distinguishable.
7. Open a result and confirm it navigates to the corresponding verse / Study view.
8. Switch between the two search modes with text still in the box; confirm the query is retained and results refresh.
9. Repeat once after reloading the PWA to ensure the service-worker update is active.

Do not hardcode the public tunnel hostname in scripts or documentation; obtain the current URL from the staging operator when performing this manual pass.

## Known issue

D11 is intentionally represented as a Node test marked `TODO`: the current non-sample footer says “Connected to the Bible database.” before the app has established a successful data connection. The TODO is visible in runner output and is not counted as a passing UX fix.

## Evidence and release gates

- A live API check is not considered passed when the Flask process or Ollama is unreachable; each case is reported as BLOCKED.
- Latency is recorded as cold and warm values. Warm above 10 seconds or cold above 45 seconds is flagged, but is not a functional test failure.
- Browser-level and iPhone checks are manual only.
- No test in this suite authorizes production changes, merges, or PR state changes.
