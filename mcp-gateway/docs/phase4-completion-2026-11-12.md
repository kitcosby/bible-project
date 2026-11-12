# MCP Gateway — Phase 4 Completion Report (2026-11-12)

**Status: CONNECTED — FIRST TOOL INVOCATION PENDING (label adopted
2026-11-12 from GPT's PR #31 review; the connection itself is complete —
acceptance criterion 8 of 9, the first live tool call from a ChatGPT
conversation, remains open for the ChatGPT session itself — see below).**

Phase 4 = register the Lampy MCP gateway in ChatGPT as a plugin and
complete the OAuth connection. For most of 2026-11-12 this was believed
blocked by a ChatGPT plan gate, based on OpenAI's help article ("Pro
users can connect custom MCP servers with read/fetch permissions"; Free
and Plus not named). A live browser experiment (Kit: "can we use this to
finish setting up?") settled it empirically: **on Kit's actual account
the registration UI was present and the full flow completed with no plan
change and no purchase.** The documentation-based expectation is
superseded by this observed result for this account.

## The run (2026-11-12, all times PST)

- 08:02–08:07 — Cloud-browser task (harness-measured) signed in to
  chatgpt.com as **kit cosby, kitcosby@gmail.com, Personal account, plan
  Free** (verified in the profile menu; sign-in via Continue with Google
  after Kit saved the login through the Secure Vault card).
- Plugins page → "+" → **"Add custom MCP server" was present and
  enabled.** Name "Lampy", URL `https://lampy.taila7a335.ts.net/mcp`,
  Authentication OAuth, risk warning accepted, "Create as a plugin".
  Kit clicked "Connect Lampy" during a brief takeover.
- OAuth: the flow reached the gateway's authorize page — request
  **3FRAUN**, client_name "ChatGPT", redirect
  `https://chatgpt.com/connector/oauth/phzM3o9jmJIa`, scope
  `read offline_access`. The approval watch (cron
  `mcp-phase4-approval-watch`, created for exactly this) approved it:
  `request 3FRAUN -> approved` (gw_admin output verified; state marker
  written).
- "Check approval & continue" succeeded; the flow returned to ChatGPT;
  Lampy appears under Installed plugins.
- Gateway-side independent verification (Muse, from the token store):
  access token issued to ChatGPT at 08:06:57 — id `88570bc1`, label
  `oauth:ChatGPT`, active, scope `read`, 1-hour expiry, refresh token
  behind it (offline_access granted).
- Plugin page (ChatGPT): "Your cloud plugin", by kit cosby, v1.0.0;
  Connected accounts: "kit's Lampy account — Primary", connected
  Nov 12, 2026; Authorization supported/used: OAuth; Review status
  DEVELOPMENT; permission "Allow low-risk".
- **Tools discovered in ChatGPT (11, all under "Read"):** fs_list,
  fs_read, fs_search, git_branches, git_diff, git_log, git_status,
  pg_databases, pg_query, pg_schema, svc_probe — exactly the gateway's
  11 read-only tools.

## Acceptance criteria (GPT's nine, 2026-11-12)

| # | Criterion | Result |
| --- | --- | --- |
| 1 | Custom MCP server registration available | ✅ (Free account, live UI) |
| 2 | Lampy server successfully registered | ✅ plugin "Lampy" installed |
| 3 | OAuth authorization request received by gateway | ✅ 3FRAUN |
| 4 | Approval watch recognizes the ChatGPT client | ✅ auto-approved |
| 5 | Read-only authorization completed | ✅ scope read (+offline_access for refresh) |
| 6 | Access token validated | ✅ issued and held by ChatGPT |
| 7 | All 11 MCP tools discovered | ✅ listed by name in ChatGPT |
| 8 | At least one read-only tool successfully executed | ⏳ pending — first invocation from a ChatGPT conversation; Muse will confirm from the gateway audit log |
| 9 | No standing unauthenticated access introduced | ✅ nothing was opened; opportunistic scans of the public address (/.env.dev, /config) were 401'd during the same window |

## Notes

- The approval watch cron was retired after it fired (purpose fulfilled).
- Registered tool lists are a snapshot in ChatGPT: if the gateway's tool
  set ever changes, the plugin's tools must be refreshed in ChatGPT
  settings. The tool set is deliberately frozen at 11.
- The ChatGPT account used (kitcosby@gmail.com) is on the **Free** plan.
  Muse's subscription records show a ChatGPT Plus ($21.82/mo) from the
  October audit — that is evidently a different account or a lapsed
  subscription; flagged for reconciliation, immaterial to this result.
- Phase 5 (write tools / bounded command execution) remains
  **unauthorized** and unbuilt.

## Addendum — PR #31 review remediation round (2026-11-12)

GPT's independent review of PR #31 returned REQUEST CHANGES: three new
findings (F6–F8), a concurrency concern in `authorize_complete`, the
status label adopted above, and a request to inspect the approval watch.
Muse verified every claim against the deployed source before acting;
Kit approved the round ("Apply the remediation round now", ~08:18 PST).
All four code items are FIXED and deployed (detail in the OAuth audit,
addendum of the same date):

- **F6 (fs_search denylist bypass) — CONFIRMED, sharper than reported.**
  The old grep-based search excluded only `.git`, `*.env`, and
  `tokens.json`, while `/opt/bible/website/secret.key` (the Flask site's
  secret key file, deny-class for `fs_read`) sits under a searchable
  root. No exposure is known: `fs_search` had only ever been run by
  Muse's own batteries, and ChatGPT has not yet executed a tool. Fix:
  search now traverses with exactly the `fs_read` rule (denied
  components pruned, denied filenames skipped, no symlinks).
- **F7 (git_diff option injection) — CONFIRMED.** The ref regex allowed
  a leading `-`; the pair `ref_a=--output`, `ref_b=<path>` would have
  git write the diff to a file as the gateway user. Fix: leading-dash
  refs rejected and every ref resolved to a verified commit SHA via
  `git rev-parse` before any diff runs.
- **F8 (unescaped client_name) — CONFIRMED.** The registration-supplied
  client name was interpolated raw into the authorization page. Fix:
  `html.escape` at render; regression-tested with a `<script>` payload.
- **Concurrency — CONFIRMED (small).** `authorize_complete` checked the
  request status outside its lock on a stale snapshot; two concurrent
  completions could have minted two codes (both still client + PKCE +
  redirect bound, single-use). Fix: check-and-issue is now one critical
  section with an atomic approved→completed transition; a second
  completion returns an "already completed" page and no code (this also
  resolves the F5 wording nit).
- **Approval watch — GPT's premise corrected.** The watch never matched
  on client_name; its criteria were redirect_uri + scope, recorded
  verbatim in the OAuth audit addendum. It was one-shot and is deleted.

Disclosure: during deployment, Muse's first edit inserted the new
helper functions between two `@mcp.tool` decorators and their
functions, leaving `fs_search` and `git_diff` unregistered for a few
minutes (and two helpers registered in their place). The remediation
battery's positive controls caught it — the first run scored 16/20 with
several vacuous negative passes, which were rejected as evidence; the
decorators were corrected, a registry precondition was added to the
battery, and the re-run is clean. No external calls occurred in that
window (the audit log shows only the battery's own attempts).

Verification after the fix (gateway pid 134345, RUNNING):
`remediation_test.py` **21/21**; `test_client.py` **23/23**;
`oauth_test.py` **16/16**; `f3_negative_test.py` **7/7**. Deployed
SHA-256: `gateway.py` 1c271a2ca72745b1649e61fbf92f5fbf4ac401205ae2cc34716a132822ab9e40,
`oauth_as.py` 3e7499867df8da6309329f99e2a2230dd79627305a0459f17483a0d8f69ee0fc
(local and remote identical). Criterion 8 remains the one open item.
