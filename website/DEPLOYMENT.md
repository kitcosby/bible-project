# BibleApp v2 deployment configuration

This document describes the environment contract for `website/app_v2.py`. It is intended to make the core Flask service host-portable while preserving the current Lampy configuration as the default. It does not authorize a production cutover.

## Database connections

The service has two independent PostgreSQL connections:

| Variable | Purpose | Required privileges |
|---|---|---|
| `BIBLE_DATABASE_URL` | Canonical corpus database used for Bible text, morphology, alignments, lexicon, witnesses, variants, and current verse search | Read-only for the application |
| `BIBLE_APP_DATABASE_URL` | Application database used for user accounts, translations, word choices, options, lemma defaults, and reading positions | Current code performs reads/writes and idempotent schema setup/migrations |

When either URL is set, it takes precedence for that database. URLs are passed to psycopg2 in-process with a 10-second connection timeout and an explicit application name. Keep both URLs in the host's secret/environment configuration. Never place them in Git, browser configuration, static assets, or logs.

The URL variables are intentionally distinct from the Express API's `DATABASE_URL` and `HEBREW_VARIANT_DATABASE_URL`. Do not reuse those variables accidentally.

### Legacy local-PostgreSQL fallback

If the URL for a database is unset, the app retains the existing local connection settings:

- `PG_HOST` (default `/tmp`)
- `PG_USER` (default `postgres`)
- `BIBLE_DB` (default `bible`)
- `APP_DB` (default `bible_app`)

This preserves the current local peer-auth deployment behavior. These are database names/connection settings, not file paths.

**Important:** `appdb()` currently performs idempotent `CREATE TABLE IF NOT EXISTS` and `ALTER TABLE` operations during connection initialization. A portable deployment must account for those current DDL operations. A later hardening step should move schema changes into explicit versioned migrations and remove DDL from request-time connection setup.

## Session signing

Set `BIBLEAPP_SESSION_SECRET` to a stable, randomly generated value of at least 32 bytes on any portable/production host. It is read into the Flask process and is never returned to clients.

If unset, the app retains its existing local `_load_secret()` file-generation behavior for backward compatibility. That fallback is not the recommended deployment configuration: it depends on a persistent writable filesystem and a stable working directory. Do not rotate the secret casually; changing it invalidates existing signed sessions.

## Process and mount configuration

- `PORT`: Flask/Gunicorn listen port (default 5057).
- `SCRIPT_NAME`: optional explicit mount prefix; if unset, the app honors Apache's `X-Script-Name` header through `PrefixMiddleware`.
- `USER_DIR`: optional directory for user data (legacy choice-file compatibility); defaults to `website/user_data`.

Use a reverse proxy with TLS. Keep PostgreSQL private to the application host/network; never connect to it from browser code.

## Current portability blockers / deferred work

1. The current `/api/search` implementation still calls Ollama at the hard-coded `127.0.0.1:11434` endpoint using `nomic-embed-text` and searches the existing YLT verse embedding table. Kit has directed that search be retooled after the separate 528,565-row word-variant embedding rebuild completes and is validated. Do not treat the Ollama implementation as the final portable search design.
2. The legacy Flask translation UI uses a local signed session, but its translation selection and write handlers do not enforce translation ownership. Do not expose authoring publicly until a canonical identity/ownership policy and cross-user tests are implemented.
3. The current account password minimum is four characters. This legacy policy must not be carried into a new public signup flow without security review.
4. The Flask service still serves both legacy HTML UI and read-only JSON API routes. The eventual portable deployment should keep the core API boundary explicit and may separate UI from API, but do not remove existing routes before parity is verified.
5. The application DB setup runs DDL at runtime, as noted above. Replace this with versioned migrations before treating a fresh-host bootstrap as production-ready.

## Migration safety

- Existing Lampy databases remain authoritative until a separate migration/cutover is approved.
- Do not point the current live service at remote databases by setting these variables in its production environment.
- Do not restart the live service as part of this configuration change.
- Validate portable staging with read-only corpus credentials, a separately provisioned application database, backups, restore tests, and browser/API acceptance tests before proposing cutover.
- Do not copy secrets into deployment notes or repository files.
