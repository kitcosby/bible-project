# MCP Gateway — Lampy Bible Project

A read-only MCP (Model Context Protocol) server with a built-in OAuth 2.1
authorization server, giving an external client (target: ChatGPT, via a
plugin) owner-approved, read-only access to the Bible project's Lampy
estate: the PostgreSQL corpus, the project's git clones, project files,
and fixed service-health probes.

Built and verified 2026-11-12 in three phases (local gateway; public
exposure via Tailscale Funnel on the Lampy node; OAuth authorization
server). Phase 4 (client registration in ChatGPT) is gated on the client
product's plan entitlement, not on this code.

## Files

| File | Role |
| --- | --- |
| `gateway.py` | FastMCP server (Streamable HTTP, stateless) on 127.0.0.1:8765; bearer-token middleware; 11 read-only tools |
| `oauth_as.py` | OAuth 2.1 authorization server mounted into the gateway: PRM + AS metadata, dynamic client registration, authorization-code flow with mandatory PKCE S256, rotating refresh tokens, plus the A2A agent card / conduct-consent endpoints |
| `gw_admin.py` | Owner-side admin CLI: mint/list/revoke static tokens; list/approve/deny pending OAuth authorization requests |
| `setup_mcp_ro.py` | One-time setup of the `mcp_ro` PostgreSQL role (SELECT-only on six allowlisted databases, read-only transaction default, 30 s statement timeout). Generates the role credential at runtime and stores it only in the deployment's 0600 secrets file |
| `test_client.py` | Local battery for the gateway tools (23 checks) |
| `oauth_test.py` | Simulated-client OAuth battery: DCR → authorize → owner approval → token exchange → MCP call → refresh rotation → reuse negatives (16 checks) |
| `f3_negative_test.py` | Regression test for the F3 fix: `redirect_uri` is required at token exchange (RFC 6749 §4.1.3); omission and mismatch are rejected, the correct value succeeds (7 checks) |
| `remediation_test.py` | Regression battery for the PR #31 review remediation: F6 search/read boundary canaries, F7 git option-injection rejections, F8 client-name escaping, single-code completion under the atomic authorize_complete, state-echo encoding, parsed-loopback redirect validation, and repeated-parameter preservation (32 checks) |
| `docs/` | Phase 2, 3, and 4 completion reports and the 2026-11-12 OAuth audit with its review addenda |

## Tools (all read-only, annotated `readOnlyHint: true`)

`fs_list`, `fs_read`, `fs_search` (fixed roots, canonicalized paths,
secret-shaped names denied, 256 KB read cap) · `git_status`, `git_log`,
`git_branches`, `git_diff` (gateway-owned clones only) · `pg_databases`,
`pg_schema`, `pg_query` (explicit database parameter; single SELECT/WITH;
200-row cap; runs as the `mcp_ro` role) · `svc_probe` (fixed probes only).

## Security model

- Access tokens are opaque and stored SHA-256 hashed; the token store is
  private to the gateway host and tokens verify nowhere else.
- OAuth consent is **out of band**: `/oauth/authorize` creates a pending
  request; the owner approves it with `gw_admin.py approve <id>` over a
  separate authenticated channel. No password database exists by design.
- Access tokens are always issued with scope `read` only; `offline_access`
  gates refresh-token issuance, and refresh tokens rotate with reuse
  rejection.
- Authorization codes are single-use, 10-minute expiry, bound to client,
  redirect URI, and PKCE challenge.
- The gateway binds localhost only; public reachability is via Tailscale
  Funnel on the Lampy node (`https://lampy.taila7a335.ts.net/mcp`).
  PostgreSQL and SSH gained no public exposure.
- Known staged hardening item (**F2**, see `docs/` audit, review
  addendum): the OAuth `resource` parameter is recorded but not yet
  validated/bound (RFC 8707). It is the mandatory precondition for any
  future multi-resource or multi-authorization-server expansion.
- **No secrets in this repository.** Runtime state (token store, OAuth
  client/code/refresh stores, the `mcp_ro` credential) lives only in the
  deployment's `/home/mcpgw/secrets/` directory (mode 0600 files) and is
  never committed. Deployment paths in the code (`/home/mcpgw/...`) are
  the Lampy deployment's; public origin is env-configurable
  (`MCPGW_PUBLIC_ORIGIN`, `MCPGW_ALLOWED_HOSTS`).

## Tests

On the deployment host, as the gateway user:

```sh
python test_client.py        # 23/23 expected
python oauth_test.py         # 16/16 expected
python f3_negative_test.py   # 7/7 expected
python remediation_test.py   # 32/32 expected
```

All three batteries passed on the deployed code on 2026-11-12, including
after the F3 fix (deployed `oauth_as.py` SHA-256
`746ae9771395e5e3bf1cc5f08886cc8acff1a9ef9f9aac507a766a15d2e4f95e`).
