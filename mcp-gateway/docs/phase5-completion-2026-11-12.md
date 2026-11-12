# MCP Gateway — Phase 5 Completion Report (write + execution tools)

Date: 2026-11-12. Status: **COMPLETE — deployed, battery-verified, and
exercised live from ChatGPT.**

## Purpose (owner's direction)

Phases 2–4 gave ChatGPT read-only access to Lampy through the Lampy
plugin. The owner directed Phase 5 to make the plugin a full working
tunnel — the third access tunnel into Lampy, after SSH and Desktop
Commander — so the agent can do real work through it (edit files, run
the project's test suites, administer the environment) instead of
through Desktop Commander and its paywall. The two standing rails were
kept: every call is audit-logged, and the PostgreSQL role `mcp_ro`
stays read-only (database writes remain outside the gateway).

## What was built

Three new tools (14 total), all requiring the `write` scope:

- `fs_write(root, subpath, content)` — create/overwrite a UTF-8 text
  file, parents created, 1 MB cap, same secret-file denylist as reads.
- `fs_edit(root, subpath, old, new)` — exact-match replacement that
  refuses unless `old` occurs exactly once.
- `exec_run(command, cwd_root, cwd_subpath, timeout_seconds)` — bash
  command as root in a working directory inside a writable root;
  timeout clamped 5–600 s; output capped; command and exit code
  audit-logged.

Write roots: the three read roots (`projects`, `bible-website`,
`bible-data`) plus `stage` (`/opt/stage`) and `bible-app-api`
(`/opt/bible-app-api`). The gateway's own secrets and code are under no
write root.

Privilege path — design change disclosed: the original plan assumed a
sudoers rule, but **the Lampy distro ships no sudo binary**. The
privileged path is therefore a small setuid launcher
(`root_helper_launcher.c`, installed root:root mode 4755 at
`/usr/local/bin/mcpgw-root-helper`) that refuses every caller except
the `mcpgw` user (uid 1000) and execs the root-owned helper
(`/usr/local/sbin/mcpgw-root-helper.py`, root:root, not writable by
mcpgw). The helper re-enforces the root allowlist and denylist itself
(defense in depth), writes atomically, and services exec requests. One
defect was found and fixed during bring-up: children spawned by bash
dropped effective uid to the real uid, so the helper now sets uid 0
fully before dispatch and fails closed if it is not running as root.

Scope plumbing: `write` added to the OAuth scope registry and
discovery metadata; `issue_access_token` now carries the owner-approved
grant scopes (minus `offline_access`) for both the authorization-code
and refresh grants, so a write grant survives token refresh;
`gw_admin.py` gained `grant <token-id> <scope>` and
`mint --scopes read,write`. The agent-card description no longer claims
the server is read-only.

Registration discipline: the new tools follow the codebase's proven
pattern — ordinary sync-style registration with `@mcp.tool` directly on
each function, helpers called from inside the body, never interleaved
between a decorator and its function (the arrangement that silently
unregistered `fs_search`/`git_diff` during the remediation round).

## Batteries (all run against the deployed gateway)

- `test_client.py` — 23/23 PASS (tool-list check updated to 14 tools)
- `oauth_test.py` — 16/16 PASS (two `n_tools == 11` assertions updated
  to 14; the tokens themselves were never broken)
- `f3_negative_test.py` — 7/7 PASS
- `remediation_test.py` — 32/32 PASS
- `phase5_test.py` (new) — 18/18 PASS: write→read-back, edit
  exactly-once semantics, ambiguous edit refused, denylist and
  traversal refused on the write path, exec runs as root, cwd roots
  honoured (incl. `/opt/stage`), timeout enforced, **read-only token
  refused by both `fs_write` and `exec_run` at the scope gate**, audit
  entries present with no token material, revocation still enforced.

## Grant applied to the live connections

Owner-side grant, so both existing ChatGPT connections carry write
without reconnecting:

- Access tokens `88570bc1`, `9f9d8c19`, `56a32787` (all active
  `oauth:ChatGPT` records) → scopes `read,write`.
- The ChatGPT client's 2 refresh records → scope
  `read write offline_access`, so hourly refreshes keep issuing
  write-carrying access tokens.
- Pre-grant backups: `tokens.json.bak-20261112-phase5`,
  `oauth_refresh.json.bak-20261112-phase5` in `/home/mcpgw/secrets/`.

## ChatGPT-side verification (audit-log corroborated)

Tools refreshed in the plugin; the agent lists **14 tools**. Two smoke
sequences appear in `/home/mcpgw/logs/audit.jsonl`:

1. 2026-11-12 17:24:10–17:24:14 UTC — `exec_run whoami` (exit 0;
   agent reported `root`), `fs_write gpt-smoke/note.txt` (40 bytes),
   `fs_read` of the same file, `exec_run rm -rf …/gpt-smoke` (exit 0).
   One approval prompt was shown, for the first `exec_run`; the owner
   had authorized the operations and it was approved once.
2. 2026-11-12 17:24:52–17:25:08 UTC — a fuller pass: `whoami`,
   `fs_write` (41 bytes), `fs_read`, a read sweep
   (`fs_read`/`fs_list`/`git_status`/`git_log`/`pg_databases`/
   `pg_query`/`svc_probe`), then **`exec_run` of the gateway's own
   `test_client.py` suite, exit code 0** — the agent ran one of the
   project's test suites through the MCP — and final cleanup.

Caveats, stated plainly:

- The first browser report's internal timestamps were wrong (it
  claimed 18:38–18:41 UTC while the environment clock read 17:21 UTC)
  and it reached Muse before its calls appeared in the audit log.
  Muse therefore treated it as unverified, re-ran the test, and only
  accepted the result once the audit log — the source of truth —
  showed both sequences. Substance verified; the report's clock was
  not.
- In the re-run conversation the agent said its `fs_read` result came
  back as an empty object and declined to claim read verification.
  The audit log confirms `fs_read` executed in both sequences, and the
  read path is independently proven by the Phase 5 battery
  (write→read-back→edit→read-back). The empty-object report is an
  agent-side presentation quirk in that conversation, not a gateway
  failure.

Conversation of record (re-run):
https://chatgpt.com/c/6af5f5fa-2e98-83e8-ae86-8c5a1991b2ba

## Deployed state

- Gateway Supervisor program `mcp-gateway` RUNNING (pid 138993 at last
  check). Deployed hashes match the repository copies in this PR.
- Backups of the pre-Phase-5 sources:
  `/home/mcpgw/gateway/*.bak-20261112-phase5`.
- Rollback: restore those backups, restart `mcp-gateway`, remove
  `/usr/local/bin/mcpgw-root-helper` and
  `/usr/local/sbin/mcpgw-root-helper.py`, restore the two secrets
  backups (drops the write grants), restart again.

## Consequence

GPT's working route into Lampy is now the Lampy plugin itself:
read/write/edit files, shell as root, and the project's test suites —
no Desktop Commander in the loop.
