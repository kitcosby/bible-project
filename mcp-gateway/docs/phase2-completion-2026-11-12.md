# ChatGPT Remote MCP Access to Lampy — Phase 2 Completion Report

Date: 2026-11-12. Authorization: Kit, 2026-11-12 ~06:33 PST ("let's do it
from our side"), following the Phase 1 feasibility report. Scope executed:
local gateway only — no Funnel change, no public exposure, no write tools,
no production data modified.

## What exists now (all verified live)

- **User**: `mcpgw` (uid 1000), home `/home/mcpgw`, password login locked.
- **Gateway**: `/home/mcpgw/gateway/gateway.py` — Python + official MCP SDK,
  Streamable HTTP, stateless, bound to **127.0.0.1:8765 only** (verified in
  `ss` output). Runs as Supervisor program `mcp-gateway` (autostart +
  autorestart; stanza appended to lampy.conf, backup at
  `lampy.conf.bak-20261112-mcpgw`). All 16 pre-existing programs' pids were
  diffed before/after: **unchanged**.
- **Authentication**: opaque bearer tokens `mcpgw1.<id>.<secret>`, stored
  as sha256 hashes in `/home/mcpgw/secrets/tokens.json` (0600), scoped
  (`read`), revocable. Admin CLI `gw_admin.py` (mint/list/revoke) — mint
  prints the token once; list shows no secret material. This store is the
  seam where the Phase 4 OAuth authorization server will issue tokens;
  the verifier does not change.
- **Audit**: `/home/mcpgw/logs/audit.jsonl` — gateway starts, auth rejects,
  and every tool call (tool, root/database, timestamp). Battery-verified
  to contain no token material.
- **PostgreSQL**: role `mcp_ro` — LOGIN, SELECT-only grants on the six
  allowlisted databases (bible, bible_app, bible_search_prod_20261111,
  bible_search_stage_20261109, bible_reconcile_20261111,
  bible_hebrew_variant_shadow_20261107), `default_transaction_read_only
  = on`, `statement_timeout = 30s`. Credential lives only in
  `/home/mcpgw/secrets/pg_mcp_ro.password` (0600). Setup verification:
  read of bible.words = 264,217; CREATE TABLE and UPDATE both refused by
  the read-only transaction.
- **Repo clones** (gateway-owned, public HTTPS, no credentials embedded):
  `/home/mcpgw/projects/bible-project` @ 7944b3c (current master) and
  `BibleApp` @ cbafdb4 (current main).

## Tools (11, all annotated read-only)

`fs_list`, `fs_read`, `fs_search` (roots: projects, bible-website,
bible-data; path canonicalization + secret-file denylist + 256 KB cap +
UTF-8 only) · `git_status`, `git_log`, `git_branches`, `git_diff`
(gateway clones only) · `pg_databases`, `pg_schema`, `pg_query` (explicit
database parameter; single SELECT/WITH; keyword filter as third layer
behind role grants and read-only transactions; 200-row cap) ·
`svc_probe` (fixed TCP/HTTP probes — Supervisor's socket is root-only by
design, so the tool probes rather than querying it).

## Test results — local battery 23/23 PASS

Battery: `/home/mcpgw/gateway/test_client.py` (real MCP client SDK over
HTTP, run as mcpgw). Covers: no/garbage/wrong-scheme token → 401; tool
discovery (11); README read; clone listing; git status/log against the
known head commits; all 6 databases reachable; `words` = 264,217 via the
gateway; shadow DB groups = 3,349 via its explicit name (no substitution);
service probes (Flask books 200, Express variant route 403 no-auth);
DELETE / two-statement / non-allowlisted-database queries refused;
path traversal refused (×2 shapes); `.env` read denied; binary read
refused; unknown repo refused; audit-log hygiene; mint→use→revoke→401.

First run was 21/23, both failures mine and both fixed before the green
run: (1) the battery expected 10 tools, the gateway correctly exposes 11;
(2) a **real denylist bug** — the env-file pattern only matched names
*starting* with `.env`, so `probe.env` (a dummy I planted to test exactly
this) was readable. Pattern widened to any `.env` component; retest green.

## Requirement status after Phase 2

- AT-01/02 (unauthenticated/invalid rejected): **verified locally**.
- AT-03/04/05/07 (discovery, file read, git, read-only SQL): **verified**.
- AT-06 (command execution): **partially** — v1 deliberately ships fixed
  probes instead of a general shell tool (see Phase 1 addendum: on
  ChatGPT's read tier a general execute tool would be classified as an
  action tool anyway). A bounded command tool remains a Phase 5 design.
- AT-08 (unauthorized SQL write rejected): **verified** (three layers).
- AT-09/10 (directory escape, secret withholding): **verified**.
- AT-11 (audit recorded, no secrets): **verified**.
- AT-12 (existing Funnel handlers preserved): **trivially true** — no
  Funnel configuration was touched in this phase.
- AT-13 (tools invoked from ChatGPT): **not yet** — Phase 4.
- AT-14 (revocation): **verified locally**.
- AT-15 (restart recovery): gateway restarts cleanly under Supervisor
  (demonstrated); full boot recovery rides the existing stack watchdog
  (config-level: autostart=true) but has not had a dedicated reboot drill
  for this program.

## Rollback

1. `supervisorctl -c /etc/supervisor/conf.d/lampy.conf remove mcp-gateway`
   and restore `lampy.conf.bak-20261112-mcpgw` (or delete the stanza), then
   `supervisorctl ... update`.
2. `DROP ROLE mcp_ro` (as postgres) after terminating its connections.
3. `userdel -r mcpgw` removes code, clones, secrets, and logs wholesale.
   Nothing outside these three footprints was created, except the
   python3.10-venv apt package.

## Next phases (not authorized by this report)

Phase 3 — exposure: Funnel on the lampy node (Route A) or the Apache
handler (Route B), plus the OAuth authorization server build (offline_
access refresh tokens, frozen tool list). Phase 4 — registration from
Kit's ChatGPT account (Pro = read/fetch tier suffices for everything
built here; Business only if Phase 5 write tools are wanted).
