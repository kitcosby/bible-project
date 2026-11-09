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

## Existing account login hardening (staged)

The current Flask account system remains authoritative. The staged hardening change preserves `user_accounts.user_id`, usernames, and existing Werkzeug password hashes; it does not introduce a second account store or require existing users to reset passwords.

The staged login-flow changes:

- Keep Werkzeug `check_password_hash` for existing credentials.
- Require 12–1024 characters for newly registered passwords; this does not impose a new minimum on existing accounts at login.
- Add session-bound CSRF tokens to signup, login, and logout.
- Change logout from GET to POST.
- Clear session state at successful signup/login boundaries and issue a fresh CSRF token.
- Mark authenticated sessions permanent with a 12-hour lifetime and disable sliding refresh.
- Set session cookies HttpOnly and SameSite=Lax; enable Secure cookies with `BIBLEAPP_COOKIE_SECURE=1` when served over HTTPS.

**Important remaining work:** this is only the first authentication-hardening slice. Persistent login throttling, server-side session revocation, and account recovery/email verification remain outstanding. The staged translation-ownership slice below adds CSRF and owner checks to the legacy Flask authoring routes, but the separate Express API still uses a shared sandbox token and does not yet enforce per-user identity. Do not expose public authoring or treat these branches as production-ready until the Express identity boundary and full cross-service tests are complete.

## Translation ownership (staged)

The legacy Flask routes now enforce the existing `user_accounts.user_id` as the owner authority:

- Creating a translation requires an active authenticated Flask account and a valid CSRF token. The server writes `owner_id` from the authenticated session; browser-supplied owner identifiers are not used.
- Translation selection, the translation list, reading views, and exports expose private translations only to their owner. Other users and anonymous visitors receive not-found behavior for private translation IDs.
- `/choice` requires authentication, CSRF, and an owner match. It locks the translation row with `SELECT ... FOR UPDATE` and commits the word choice, optional Other option, lemma default, and updated timestamp in one transaction.
- Built-in translation ID 1 (`KJV`) and ID 2 (`Young's`) remain public and read-only. A read-only metadata inventory found only these two NULL-owner translation rows; it also found no `word_choice`, `other_option`, or `lemma_default` rows attached to either built-in.
- Any other NULL-owner translation is hidden and denied. No legacy row is automatically assigned to an account, deleted, or made editable.
- Saved reading positions are revalidated against the current account's translation access before being used.
- Non-API Flask responses use `Cache-Control: private, no-store`, preventing private translation pages, exports, and login/CSRF forms from being reused from browser cache after logout or account switching. Public read-only `/api/*` corpus responses retain their existing cache behavior for offline PWA reading.

The metadata inventory was read-only. It did not expose translation contents, credentials, or account details, and it made no database changes.

**Important boundary:** the separate Express API in `kitcosby/BibleApp` still gates its `/api/bible/*` routes with the server-side `BIBLE_APP_SANDBOX_TOKEN`. It does not yet receive or validate a per-user identity and therefore does not implement this owner policy. Keep that API bound to localhost and keep the token server-side. Do not expose its authoring routes publicly or treat Flask ownership enforcement alone as end-to-end API authorization.

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
2. The Flask translation UI's staged ownership checks protect its legacy routes, but the separate Express API still uses a shared sandbox token without per-user identity. Keep Express private until a verifiable per-user identity and owner checks are implemented there too.
3. New Flask signups in the staged authentication branch require 12–1024 characters; existing accounts continue to authenticate using their existing Werkzeug hashes. Persistent login throttling and account recovery remain outstanding.
4. The Flask service still serves both legacy HTML UI and read-only JSON API routes. The eventual portable deployment should keep the core API boundary explicit and may separate UI from API, but do not remove existing routes before parity is verified.
5. The application DB setup runs DDL at runtime, as noted above. Replace this with versioned migrations before treating a fresh-host bootstrap as production-ready.

## Migration safety

- Existing Lampy databases remain authoritative until a separate migration/cutover is approved.
- Do not point the current live service at remote databases by setting these variables in its production environment.
- Do not restart the live service as part of this configuration change.
- Validate portable staging with read-only corpus credentials, a separately provisioned application database, backups, restore tests, and browser/API acceptance tests before proposing cutover.
- Do not copy secrets into deployment notes or repository files.
