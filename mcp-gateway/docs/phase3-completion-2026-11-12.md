# ChatGPT Remote MCP Access to Lampy — Phase 3 Completion Report

Date: 2026-11-12. Authorization: Kit, 2026-11-12 ~06:42 PST ("On to phase
three"). Scope: remote connectivity (Funnel) + the OAuth authorization
server. No write tools; no production data changed; the laptop node's
Funnel configuration was not touched at any point.

## Exposure — Route A, as designed

- **Funnel on the `lampy` node**: `https://lampy.taila7a335.ts.net`
  (HTTPS 443) → proxy `http://127.0.0.1:8765` (the gateway). Public DNS
  resolves the name to the Tailscale Funnel ingress pair
  208.111.35.209 / 208.111.34.11 (verified via Google DoH).
- The node's pre-existing **Serve :22 SSH mapping is intact** (status
  shown identical before/after; fresh SSH sessions verified). The laptop
  node's handlers (/bible, /byot, /api-stage, …) are on a different node
  and were **not modified** — AT-12 satisfied by construction.
- Gateway transport security now allows the public hostname (bare +
  wildcard forms — see the defect note below). PostgreSQL and SSH gained
  no new exposure: the only public surface is the gateway itself.

## OAuth authorization server (`oauth_as.py`, mounted on the gateway)

Implements the MCP authorization profile ChatGPT expects:

- `GET /.well-known/oauth-protected-resource` (and the `/mcp`-suffixed
  variant) — resource `https://lampy.taila7a335.ts.net/mcp`, scopes
  `read` + `offline_access`.
- `GET /.well-known/oauth-authorization-server` — full AS metadata.
- `POST /oauth/register` — dynamic client registration; https redirect
  URIs only (localhost excepted); client secrets stored hashed.
- `GET /oauth/authorize` — validates client, redirect URI, scope, and
  **PKCE S256 (mandatory)**, then creates a *pending* request and shows
  its short request ID. **Consent is out of band**: the owner approves
  with `gw_admin.py approve <id>` (or `deny`) over the existing
  authenticated Lampy channel. There is deliberately **no password
  database** in this design.
- `GET /oauth/authorize/complete` — after approval, mints a single-use
  10-minute authorization code (stored hashed) and 302s to the client.
- `POST /oauth/token` — authorization-code exchange with client
  authentication (Basic or post) and PKCE verification; issues a 1-hour
  access token into the gateway's existing token store (the Phase 2
  verifier is unchanged) plus a **rotating refresh token** when
  `offline_access` was granted; refresh reuse is rejected.
- Unauthenticated `/mcp` requests return 401 with
  `WWW-Authenticate: Bearer resource_metadata="…"` for AS discovery.

## Verification

- **OAuth dance battery 16/16** (`oauth_test.py`, simulating ChatGPT):
  DCR 201; http redirect refused; pending page carries a request ID;
  completion before approval yields no code; unregistered redirect and
  missing PKCE → 400; owner approval works; 302 carries code + state;
  wrong verifier → invalid_grant; wrong client secret → 401; exchange →
  access + refresh; code reuse → invalid_grant; the OAuth access token
  lists 11 tools and answers a live query; refresh rotates; old refresh
  reuse → invalid_grant; refreshed token works.
- **Phase 2 battery still 23/23** after all Phase 3 changes.
- **External, over the genuine public path** (this VM → Funnel ingress IP
  → TLS to lampy.taila7a335.ts.net): well-known metadata 200; `/mcp`
  without a token → **401**; with a dedicated probe token: initialize →
  valid MCP result, tools/list → all 11 tools, tools/call `pg_query`
  → live answer (words = 264,217). Probe token revoked afterward.
- **No collateral change**: all 16 pre-existing Supervisor programs still
  run under their original pids (diffed against the pre-Phase-2 record).

## Defect found and fixed during external verification

First public initialize returned `Invalid Host header`. Root cause,
reproduced locally: the MCP SDK's host check treats the pattern
`lampy.taila7a335.ts.net:*` as requiring the literal colon — a portless
Host (what the Funnel delivers) fails, while `:443` passes. Fix: the bare
hostname was added to the allowed-hosts list alongside the wildcard form.
Re-verified end to end afterward (above).

## What remains — Phase 4 (registration) and Phase 5 (writes)

Phase 4 is now purely a ChatGPT-side ceremony; nothing is left to build:

1. Kit, on ChatGPT **web**, with a plan that can register custom MCP
   servers (current official docs: Pro = read/fetch connections, which
   covers everything built; Business = full incl. writes).
2. Plugins → **Add custom MCP server** → URL
   `https://lampy.taila7a335.ts.net/mcp`, authentication OAuth.
3. ChatGPT opens the gateway's authorize page, which shows a request ID.
   Kit relays the ID (or just says it's waiting); Muse approves it from
   Lampy with `gw_admin.py approve <id>`; Kit clicks "Check approval &
   continue" — ChatGPT exchanges the code and the tools appear.
4. First real conversation test = the requirements doc's AT-13 and the
   project's Definition of Done.

Rollback for Phase 3: `tailscale funnel --https=443 off` on the lampy
node closes the public surface instantly (gateway keeps running
locally); the OAuth state files live in `/home/mcpgw/secrets/` and can be
deleted without affecting the Phase 2 token path.
