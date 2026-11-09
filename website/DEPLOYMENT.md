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

- Preserve Werkzeug password verification for existing accounts.
- Require 12–1024 characters for newly registered passwords.
- Add session-bound CSRF validation to signup, login, logout, and translation-authoring mutations.
- Change logout from GET to POST.
- Rotate session and CSRF state at successful authentication boundaries.
- Use a fixed 12-hour session lifetime with HttpOnly and SameSite=Lax cookies by default; cross-site deployments require Secure cookies.

Translation ownership enforcement is included in the preceding section. The Flask-issued API identity-token exchange is documented below. Persistent login throttling, immediate server-side session revocation, and account recovery/email verification remain outstanding. This staged stack is not production-ready until the full cross-service flow is configured and tested.

## Translation ownership (staged)

The legacy Flask routes now enforce the existing `user_accounts.user_id` as the owner authority:

- Creating a translation requires an active authenticated Flask account and a valid CSRF token. The server writes `owner_id` from the authenticated session; browser-supplied owner identifiers are not used.
- Translation selection, the translation list, reading views, and exports expose private translations only to their owner. Other users and anonymous visitors receive not-found behavior for private translation IDs.
- `/choice` requires authentication, CSRF, and an owner match. It locks the translation row with `SELECT ... FOR UPDATE` and commits the word choice, optional Other option, lemma default, and updated timestamp in one transaction.
- Built-in translation ID 1 (`KJV`) and ID 2 (`Young's`) remain public and read-only. A read-only metadata inventory found only these two NULL-owner translation rows; it also found no `word_choice`, `other_option`, or `lemma_default` rows attached to either built-in.
- Any other NULL-owner translation is hidden and denied. No legacy row is automatically assigned to an account, deleted, or made editable.
- Saved reading positions are revalidated against the current account's translation access before being used.

The metadata inventory was read-only. It did not expose translation contents, credentials, or account details, and it made no database changes.

**Important boundary:** the separate Express API in `kitcosby/BibleApp` still gates its `/api/bible/*` routes with the server-side `BIBLE_APP_SANDBOX_TOKEN`. It does not yet receive or validate a per-user identity and therefore does not implement this owner policy. Keep that API bound to localhost and keep the token server-side. Do not expose its authoring routes publicly or treat Flask ownership enforcement alone as end-to-end API authorization.

## Flask-to-Express user identity token (staged)

The existing Flask account/session remains the only identity authority. After an authenticated Flask session is established, the browser may exchange that session for a short-lived API bearer token:

1. GET /api/auth/csrf returns the session-bound CSRF token for an active account.
2. POST /api/auth/token requires the same authenticated session, a matching X-CSRF-Token header, and an allowed browser Origin.
3. Flask signs an HS256 JWT with issuer bibleapp-flask, audience bibleapp-api, the existing user_accounts.user_id in sub, an issue time, a five-minute expiry, and a random token ID.
4. The browser sends this token as Authorization: Bearer ... to the Express /api/bible/* API. Keep it in memory only; never store it in localStorage/sessionStorage or put it in URLs or logs.
5. Express validates the HMAC signature in constant time and checks issuer, audience, account ID, issue/expiry times, and the maximum five-minute lifetime.

Required environment variables (configure out-of-band; never commit or display their values):

- BIBLEAPP_IDENTITY_TOKEN_SECRET: one independently generated random secret of at least 32 UTF-8 bytes, identical in Flask and Express. It must be distinct from BIBLEAPP_SESSION_SECRET and BIBLE_APP_SANDBOX_TOKEN.
- BIBLEAPP_ALLOWED_ORIGINS: comma-separated exact HTTPS origins, with no path or wildcard. Configure the frontend origin on both Flask and Express.
- BIBLEAPP_COOKIE_SAMESITE=None and BIBLEAPP_COOKIE_SECURE=1: required only when the frontend and Flask API are cross-site. Flask rejects SameSite=None unless Secure is enabled. Same-origin deployments retain the default Lax cookie.

The token endpoint returns Cache-Control: no-store and credentialed CORS only for the explicit origin allowlist. The Express API uses bearer authorization and non-credentialed CORS. A browser must first obtain the token from Flask with credentials: "include", then call Express with the bearer header and without ambient cookies.

**Revocation limitation:** a token already issued remains valid until its five-minute expiry, including immediately after logout or account deactivation. This is not server-side session revocation. Keep the token lifetime short and do not use this mechanism for high-risk operations requiring immediate revocation.

This is a staged cross-service contract. It does not expose the Express API publicly, configure production secrets, restart services, or alter production databases.

## PWA JSON authentication endpoints

The PWA may use the same Flask account store through these JSON routes. All responses are `Cache-Control: no-store`; browser requests must use `credentials: "include"` so the Flask session cookie is sent.

| Route | Method | Purpose |
|---|---|---|
| `/api/auth/bootstrap` | GET | Creates/returns a pre-authentication session-bound CSRF token. Also reports whether the session is already authenticated and, if so, the minimal user profile. |
| `/api/auth/login` | POST | Accepts JSON `username` and `password`; validates CSRF and Origin; verifies the existing Werkzeug password hash; clears the prior session and issues a new authenticated session and CSRF token. |
| `/api/auth/signup` | POST | Accepts JSON `username` and `password`; validates CSRF and Origin; applies the existing 12–1024-character password policy; creates a row in `user_accounts` and signs the new account in. |
| `/api/auth/logout` | POST | Validates CSRF and Origin, clears the authenticated session, and returns a fresh pre-authentication CSRF token. |
| `/api/auth/token` | POST | Exchanges the authenticated Flask session for the five-minute Express bearer token described above. |

The read-only corpus endpoint `GET /api/word-options?wordIds=...` accepts 1–100 Hebrew word IDs and returns each word's lemma key plus the exact KJV and Young's phrase groups used by the legacy dropdown. It supports the Strong's-number and root-code lemma keys. Its response is deliberately `Cache-Control: no-store`: the stored choice byte is positional, so a stale phrase ordering could silently select a different rendering. The PWA service worker must bypass its shared cache for this route.

For cross-origin frontend hosting, configure the exact frontend origin in `BIBLEAPP_ALLOWED_ORIGINS` and use `credentials: "include"`. If frontend and Flask are cross-site, configure `BIBLEAPP_COOKIE_SAMESITE=None` and `BIBLEAPP_COOKIE_SECURE=1`; modern browser third-party-cookie restrictions may still affect cross-site cookie delivery, so same-site hosting is preferable where practical.

Every mutating route requires the current session's token in `X-CSRF-Token`. Bootstrap is intentionally available before login; the token is rotated after successful login, signup, and logout. The PWA should keep the CSRF token in runtime memory and reacquire it through bootstrap after reload. It must not persist passwords, CSRF tokens, or bearer tokens in localStorage/sessionStorage.

These endpoints do not yet add persistent login throttling, email verification, account recovery, or immediate bearer-token revocation. The HTML login/signup/logout routes remain available for the existing web interface.

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
