# MCP Gateway — Phase 4 Completion Report (2026-11-12)

**Status: COMPLETE, with one acceptance item left for the ChatGPT session
itself (first live tool call — see below).**

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
