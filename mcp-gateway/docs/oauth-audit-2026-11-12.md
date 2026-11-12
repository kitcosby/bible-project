# MCP Gateway — Read-Only OAuth Implementation Audit (2026-11-12)

Requested by GPT (protocol/security reviewer) via Kit, 2026-11-12 ~07:27 PST.
Scope: audit only — **nothing was changed**. Evidence: (a) full source read of
`oauth_as.py` (18,464 bytes, the byte-identical copy deployed 2026-11-12 07:05
PST) plus the auth middleware in `gateway.py`; (b) live discovery documents
fetched over the public Funnel path at ~07:35 PST (quoted below); (c) Phase 3
battery results (OAuth dance 16/16, local battery 23/23); (d) GPT's independent
live metadata cross-check at ~07:18 PST. Note: the Lampy SSH route was in a
transport-failure window during this audit (3 failed attempts, same
tunnel-proxy class seen before); the public-path fetch succeeded and the
served documents match the source exactly, so no finding rests on the SSH
route.

## Live discovery documents (fetched 2026-11-12 ~07:35 PST, public path)

AS metadata — `GET /.well-known/oauth-authorization-server`:
```json
{"issuer":"https://lampy.taila7a335.ts.net","authorization_endpoint":"https://lampy.taila7a335.ts.net/oauth/authorize","token_endpoint":"https://lampy.taila7a335.ts.net/oauth/token","registration_endpoint":"https://lampy.taila7a335.ts.net/oauth/register","scopes_supported":["read","offline_access"],"response_types_supported":["code"],"grant_types_supported":["authorization_code","refresh_token"],"code_challenge_methods_supported":["S256"],"token_endpoint_auth_methods_supported":["client_secret_basic","client_secret_post"]}
```

PRM — `GET /.well-known/oauth-protected-resource`:
```json
{"resource":"https://lampy.taila7a335.ts.net/mcp","authorization_servers":["https://lampy.taila7a335.ts.net"],"scopes_supported":["read","offline_access"],"bearer_methods_supported":["header"]}
```
(Also served at the path-suffixed `/.well-known/oauth-protected-resource/mcp`.)

## Conforms

- **Protected-resource metadata (RFC 9728):** resource is the canonical
  `https://lampy.taila7a335.ts.net/mcp`; authorization_servers names the
  issuer; scopes and bearer method advertised. 401 responses from the gateway
  middleware carry `WWW-Authenticate: Bearer resource_metadata="…"` pointing
  at this document (gateway.py).
- **AS discovery (RFC 8414):** all endpoints under the issuer origin;
  response_types `["code"]`; grant types authorization_code + refresh_token;
  `code_challenge_methods_supported: ["S256"]` only; token endpoint auth
  methods basic + post, both actually implemented (constant-time secret
  comparison; secrets stored SHA-256 only).
- **PKCE:** S256 mandatory at authorize (missing challenge or non-S256 method
  → refusal); verifier checked at token exchange with constant-time compare.
  Battery-proved: wrong verifier → `invalid_grant`.
- **Authorization endpoint:** response_type=code enforced; client must be a
  registered client; redirect_uri must **exactly match** a registered URI (no
  prefix/pattern matching); requested scope must be a subset of
  {read, offline_access} (default `read`).
- **Consent:** out of band by design — authorize creates a pending request
  (30-min expiry); a code is minted only by `/oauth/authorize/complete` after
  owner approval via `gw_admin.py`; denied → 403; exactly one code per
  request (a completed request cannot mint a second).
- **Codes:** single-use (marked used under lock before issuance), 10-minute
  expiry, bound to client and redirect_uri; reuse → `invalid_grant`
  (battery-proved).
- **Tokens:** opaque, stored SHA-256 only, 1-hour expiry, revocable
  (gw_admin). Access tokens are **always** issued with scope `["read"]` in
  the token store regardless of the grant; `offline_access` only gates
  refresh-token issuance. Gateway middleware enforces `read` ∈ token scopes.
- **Refresh tokens:** rotating; the presented token is revoked on use; reuse
  of an old refresh token → `invalid_grant` (battery-proved); refresh is
  bound to the original client; scope carried from the original grant, and
  refreshed access tokens are still read-only (no widening path exists).
- **Dynamic client registration (RFC 7591):** redirect_uris mandatory;
  https-only (localhost excepted); 201 with full client metadata; client
  secret stored hashed. Registration is unauthenticated, which is the MCP
  norm — and registration alone grants nothing: authorization still requires
  the owner's out-of-band approval.

## Findings (for the joint review; no changes made)

- **F1 — CIMD not supported.** The authorize endpoint resolves `client_id`
  only against the DCR store; a URL-form client_id (Client ID Metadata
  Document, the mechanism the current MCP specification prefers) fails
  closed with "unknown client_id". DCR is retained and is what ChatGPT's
  documented custom-MCP flow uses, so this is a deviation from the newest
  spec *preference*, not from the actual client's behavior. CIMD support
  would be an addition (fetch + parse the client metadata document at
  authorize time), not a modification of the DCR path.
- **F2 — `resource` parameter recorded, never validated (RFC 8707).** The
  authorize handler stores the client's `resource` value in the pending
  record but never compares it to the canonical resource, does not propagate
  it into the code record, and the token endpoint ignores it. Access tokens
  are opaque (no `aud` claim exists); audience binding is by construction —
  the token store is private to this gateway and tokens verify nowhere else,
  so no cross-service audience confusion is possible in this deployment.
  Smallest strictness fix, if approved: reject authorize/token requests
  whose `resource` is present and ≠ `https://lampy.taila7a335.ts.net/mcp`
  (validate-if-present; requiring it outright could break clients that omit
  it).
- **F3 — `redirect_uri` not required at token exchange.** If presented it
  must match the code's recorded URI exactly; if omitted, the exchange
  proceeds. RFC 6749 §4.1.3 requires it when it was present in the authorize
  request (it always is here). ChatGPT presents it. Smallest fix: require
  equality unconditionally.
- **F4 — Authorize errors never redirect (intentional).** All authorize
  errors return a direct HTML 400 page rather than a redirect carrying error
  parameters. This is the OAuth 2.1 Security BCP-endorsed behavior for
  unvalidated clients/redirects (avoids an open-redirector); recorded so the
  joint review does not mistake it for an oversight.
- **F5 — Cosmetic.** Re-visiting `/oauth/authorize/complete` for an already
  completed request shows the "still awaiting owner approval" wording
  (status is `completed`, neither `approved` nor `denied`). Wording only;
  no second code can be minted.
- **Absent but optional/by design:** no revocation or introspection
  endpoints (revocation is owner-side via `gw_admin.py revoke`); no `iss`
  authorization-response parameter (RFC 9207) and the metadata does not
  advertise it.
- **Auth0 note:** nothing in this implementation depends on Auth0. If an
  Auth0 tenant is introduced later (e.g. as an external AS), the trust
  boundaries change wholesale and this audit does not carry over; GPT's
  flagged MCP `resource`-parameter compatibility setting on the Auth0 side
  would then be a real checklist item. For the current built-in AS, F2 is
  the corresponding item.

## Bottom line

The implementation conforms to the MCP authorization profile as ChatGPT
exercises it today (DCR + authorization-code + PKCE S256 + rotating
refresh), with three strictness findings (F1–F3), one intentional deviation
(F4), and one cosmetic item (F5). None of F1–F3 blocks Phase 4 as
evidenced; each has a named smallest fix if the joint review wants it.
No configuration or code was changed by this audit.

## Addendum — post-audit verification pass (2026-11-12 ~07:32–07:38 PST)

At GPT's request (relayed by Kit), the checks that had rested on the
public-path fetch were re-run over SSH once the route recovered, as short
independent commands. Results: SSH connectivity restored (2 s response);
remote `sha256sum /home/mcpgw/gateway/oauth_as.py` =
`26f44cb0d1d4eb4a3597ddc4726dbb8c4af15b7b719284c4a20884eb31dea3cb`,
identical to the audited local copy — the audited source is the deployed
file, now hash-proven. The discovery documents fetched from localhost on
Lampy are byte-identical to the public-path documents quoted above.
`mcp-gateway` RUNNING, pid 129257, continuous since the 07:06 deploy
restart (no restart during the audit window). No pending authorize
requests. The 07:28–07:31 SSH failures (4 attempts, "Connection closed by
UNKNOWN port 65535" / one mux timeout) are the documented tunnel-proxy
transport signature: the connection dies at the managed proxy's CONNECT
step and never reaches sshd. Lampy uptime 1d 8h40m (no reboot). Origin:
the VM↔tailnet transport leg — neither the gateway nor Lampy; the precise
hop is undetermined from this end, as in the 2026-11-11 stage-probe
forensics. No configuration was modified and no service restarted in this
pass.

## Review addendum — GPT qualifications + plugin-flow evidence (2026-11-12 ~07:40 PST)

GPT's review (relayed by Kit) qualified three findings; Muse accepts all
three regrades:

- **F1 regraded: compatibility question, client behavior unverified.** The
  audit's phrase "DCR is what ChatGPT's documented flow uses" was
  overclaimed. Kit's correction also applies: on the ChatGPT side the
  object being created is a **plugin** (Plugins page -> "Create as a
  plugin"); the MCP server is the plugin's backend. Evidence gathered from
  OpenAI's own Plugins authentication guide (developers.openai.com,
  crawled 2026-11-10): supported clients use CIMD, DCR, predefined OAuth
  clients, and PKCE; "ChatGPT prioritizes CIMD when it is available, but
  the plugin builder can choose DCR when both CIMD and DCR are available";
  CIMD is used when the AS advertises `client_id_metadata_document_supported:
  true`; on the DCR path "ChatGPT calls your authorization server's
  registration_endpoint once for the MCP server connection, receives a
  generated client_id, and reuses that client." Our AS metadata does NOT
  advertise CIMD support, so per OpenAI's documented client behavior the
  CIMD path is not offered against this server and the DCR path (or the
  builder's DCR choice) applies. This is documentation-grade evidence, not
  a live observation: the first real ChatGPT attempt remains the proof.
  Field corroboration: independent client-behavior research (measured
  against live ChatGPT connections, Aug 2026) likewise records "CIMD
  supported and preferred; DCR supported as fallback."
- **F2 regraded: security-hardening issue** (GPT's wording adopted).
  Assessment: the correct end-state is validate-at-authorize (reject a
  `resource` value that is present and != the canonical resource URI),
  propagate the resource into the code record, require match at token
  exchange when presented, and record the binding on the issued token with
  the gateway middleware asserting it. In the current single-resource,
  single-AS deployment every check would compare against the one canonical
  value, so the change buys conformance and future-proofing, not present
  protection. Recommendation: implement together with F3 if Kit wants one
  maintenance window, or stage it as the mandatory precondition for any
  multi-resource/multi-AS expansion. No silent risk either way.
- **F3 regraded: conformance defect.** RFC 6749 section 4.1.3 makes
  redirect_uri REQUIRED at token exchange when it was included in the
  authorization request, values identical. Our authorize flow always
  includes and stores it (the code record already persists it), so in this
  implementation the defect is unconditional, not conditional. Smallest
  fix (one line in the token handler): replace the conditional check
  `if form.get("redirect_uri") and form["redirect_uri"] != rec[...]`
  with an unconditional equality requirement
  `if form.get("redirect_uri") != rec["redirect_uri"]` (stored value is
  always non-empty, so an omitted value mismatches and fails with
  invalid_grant). Test plan: full OAuth battery re-run (16/16 expected;
  the battery's simulated client presents redirect_uri) plus one new
  negative case — exchange omitting redirect_uri must return
  invalid_grant. Prepared 2026-11-12; application awaits Kit's approval
  per change control.

## F3 fix applied (2026-11-12 ~07:42-07:46 PST, Kit approved via options widget + "Apply the F3 fix now")

One-line change in the token handler of oauth_as.py: the redirect_uri
check is now an unconditional equality requirement
(`if form.get("redirect_uri") != rec["redirect_uri"]`), so an omitted
value mismatches the code's stored (always non-empty) URI and fails with
invalid_grant, per RFC 6749 section 4.1.3. Deployed file SHA-256:
746ae9771395e5e3bf1cc5f08886cc8acff1a9ef9f9aac507a766a15d2e4f95e
(local and remote verified identical). Gateway restarted once for the
fix: mcp-gateway RUNNING, pid 129257 -> 131312. Verification:
- New regression test f3_negative_test.py: 7/7 PASS (exchange without
  redirect_uri -> 400 invalid_grant; wrong redirect_uri -> 400
  invalid_grant; correct redirect_uri -> token issued; the failed
  attempts did not consume the single-use code).
- OAuth dance battery re-run: 16/16 PASS (no regression).
- Phase 2 local battery re-run: 23/23 PASS.
F3 is CLOSED. F2 remains staged as the mandatory precondition for any
multi-resource/multi-AS expansion (assessment in the review addendum).

## Addendum 2026-11-12 (remediation) — PR #31 review findings F6–F8 and the authorize_complete race: all FIXED

GPT's independent review of PR #31 (GitHub source, not summaries)
returned REQUEST CHANGES with three new findings beyond F1–F5, a
concurrency concern, and an approval-watch inspection request. Muse
verified each against the deployed source; Kit approved the remediation
round on 2026-11-12 (~08:18 PST). All four code items are fixed,
deployed, and regression-tested. Verification (gateway pid 134345):
new `remediation_test.py` 21/21 PASS; regression `test_client.py`
23/23, `oauth_test.py` 16/16, `f3_negative_test.py` 7/7. Deployed
SHA-256: gateway.py
1c271a2ca72745b1649e61fbf92f5fbf4ac401205ae2cc34716a132822ab9e40,
oauth_as.py 3e7499867df8da6309329f99e2a2230dd79627305a0459f17483a0d8f69ee0fc
(local == remote for both).

- **F6 — fs_search bypassed the fs_read denylist (High, CONFIRMED).**
  fs_read enforces DENY_COMPONENT on every path component (env /
  secret / credential / .key / .pem / id_* / .password / .cred /
  tokens.json); the grep-based fs_search excluded only .git, *.env and
  tokens.json. Live consequence: /opt/bible/website/secret.key and
  /opt/bible/website-debug/secret.key (Flask secret key files) sit
  under searchable roots and would have been returned line-by-line to
  any token holder. No exposure is known (fs_search had only been run
  by Muse's batteries; ChatGPT has executed no tool yet). Fix:
  fs_search now walks in-process via _searchable_files(), applying the
  identical rule — denied directory components prune descent, denied
  filenames are skipped, symlinks are never followed, binary and
  >1 MiB files skipped; output format unchanged (path:line:text, 200
  lines). Regression: canary files (a secret.key name, a .env.local
  name, a file inside a secrets-named directory) planted in a gateway
  clone are invisible to search while a control file is found, and
  broad searches of both live website trees return no line sourced
  from either secret.key file.
- **F7 — git_diff option injection (High, CONFIRMED).** The ref
  validator's character class permitted a leading hyphen; git would
  parse such a "ref" as an option, and ref_a="--output" with
  ref_b=<path> writes the diff to that path as the gateway user — a
  write primitive in a read-only tool. Fix: refs beginning with "-" are
  rejected, and every ref (including both sides of ".." / "..."
  ranges) is resolved with `git rev-parse --verify <ref>^{commit}`
  before use; only verified 40-hex SHAs ever reach the diff command.
  Regression: both --output forms are rejected, no file is created,
  plain and range diffs still work.
- **F8 — unescaped client_name on the authorization page (High,
  CONFIRMED).** DCR accepts an arbitrary client_name (public
  registration), and the authorize handler interpolated it into HTML
  with no escaping anywhere in the file — a stored-XSS vector on the
  approval page (impact bounded: the origin holds no session or cookie,
  and consent is out-of-band, so the realistic harm is page spoofing).
  Fix: html.escape() on the client name at render. Regression: a client
  registered as `<script>alert(1)</script>` renders escaped
  (&lt;script&gt;...) and never raw.
- **authorize_complete TOCTOU (CONFIRMED, small).** The handler loaded
  the pending record under LOCK, released it, checked status on the
  stale snapshot, and only then minted a code and marked the request
  completed in a second critical section; two concurrent completions
  could each mint a code for one approved request (codes remain bound
  to the same client, PKCE challenge and redirect URI, and single-use,
  which bounds the impact). Fix: the whole read-check-transition-issue
  sequence now runs inside one LOCK section; status "completed" is
  terminal, and a repeat completion returns an "already completed"
  page with no code — which also resolves the F5 wording nit.
  Regression: double completion yields exactly one code, and that code
  exchanges normally.
- **Approval watch — inspection result.** GPT asked to inspect the
  Phase 4 approval automation, concerned it might identify ChatGPT by
  its self-supplied client_name. It did not. The one-shot cron
  `mcp-phase4-approval-watch` (created 2026-11-12 ~06:58 PST, deleted
  after it fired) approved a pending request ONLY when BOTH held:
  (1) redirect_uri starts with `https://chatgpt.com/`, and (2) the
  requested scope is a subset of {read, offline_access}. Unmatched
  pending requests were reported to the owner, never approved; two or
  more simultaneous matches meant approve none and report ambiguity.
  client_name played no part. Defense in depth, for the record:
  approval alone issues nothing — the code is delivered only to the
  client's registered redirect URI (exact match enforced at authorize),
  and redemption requires that client's secret, the PKCE verifier, and
  (since the F3 fix) the exact redirect_uri. The watch approved exactly
  one request (3FRAUN, ChatGPT's registration) and no longer exists;
  any future registration is approved manually via gw_admin.py.

Deployment disclosure: Muse's first remediation edit placed two
helper functions between @mcp.tool decorators and their functions,
leaving fs_search and git_diff unregistered for a few minutes. The new
battery's positive controls exposed it (first run 16/20; several
negative checks had passed vacuously against unknown-tool errors and
were rejected as evidence). The decorators were corrected, a registry
precondition (the tools must be listed) was added to the battery, and
the clean 21/21 above is the re-run. No external calls occurred in the
window.

## Addendum 2026-11-12 (final revision) — state encoding, localhost validation, and an audit limitation

GPT's re-review of the remediation commit accepted F6/F7/F8 and the
concurrency fix, accepted Phase 4 as complete (9/9) on the
audit-log-correlated criterion-8 evidence, and raised two smaller
items plus a documentation point. Muse verified both items against
the source (both confirmed), Kit approved the final revision, and both
are fixed and deployed. Verification (gateway pid 135555):
remediation_test.py extended to 29 checks, 29/29 PASS; oauth_test.py
16/16; f3_negative_test.py 7/7. test_client.py was not re-run this
round: gateway.py is byte-identical (the revision touches oauth_as.py
only). Deployed oauth_as.py SHA-256:
c16302e8d512b357c9879cfff80a77b57cd1484f9544ea217c2ff60bf245421d
(local == remote).

- **State parameter echoed without encoding (medium, FIXED).**
  authorize_complete built the callback by concatenating the stored,
  client-supplied state raw (`&state=` + state). A state containing &
  or = would inject extra parameters into the client's callback. The
  callback is now built with urlsplit/parse_qsl/urlencode, preserving
  any parameters already present in the registered redirect URI, so
  the state is echoed identically after parsing. Regression: a state
  of `x&code=FORGED y+z` round-trips exactly, and the callback carries
  exactly one code parameter — the real one.
- **Redirect registration accepted prefix-lookalike loopback hosts
  (low-medium, FIXED).** The validator used
  `uri.startswith("http://localhost")`, which also accepts
  http://localhost.evil.example and the userinfo form
  http://localhost@evil.example (whose host is evil.example).
  Registration now parses each URI: https for any host, http only when
  the parsed hostname is localhost, 127.0.0.1, or ::1. Regression:
  both lookalikes refused with 400; localhost:8765 and 127.0.0.1:9000
  accepted; plain http for non-loopback still refused. (The authorize
  step's exact-match against registered URIs already limited the
  practical risk; this closes the validator itself.)
- **Documentation consistency (FIXED).** The Phase 4 completion
  report's acceptance table row 8 now records criterion 8 as passed
  (executed 2026-11-12 08:28:03 PST, audit-log confirmed), matching
  its closing addendum.
- **AUDIT LIMITATION — approval-watch provenance.** The one-shot
  approval watch that approved ChatGPT's registration (3FRAUN) was a
  scheduled-job body; it was deleted after it fired, and its source is
  not preserved in this repository or elsewhere inspectable. Its
  matching criteria (redirect_uri prefix https://chatgpt.com/ AND
  scope subset of {read, offline_access}; unmatched requests reported,
  never approved; multiple matches = approve none) are recorded from
  the creation-turn record and the Phase 4 report, and cannot be
  independently re-verified from source. This is recorded as an audit
  limitation, not a vulnerability: the mechanism no longer exists.
  STANDING POLICY, stated at GPT's recommendation and already in
  effect: automatic approval is retired; every future registration is
  approved manually by the owner via gw_admin.py.

## Closing note 2026-11-12 — repeated-parameter edge case FIXED before merge

GPT's merge approval for PR #31 noted one non-blocking edge case: the
new callback builder converted the redirect URI's query pairs to a
dict, collapsing repeated parameters (tenant=a&tenant=b would keep
only one). Kit directed that it be fixed before merging ("Fix the edge
case first, then merge"). The builder now keeps the parse_qsl output
as a list of pairs, replaces only the code/state pairs, and urlencodes
the list, so repeated and unrelated parameters survive intact.
Regression: remediation_test.py RP checks (a registered redirect
carrying ?tenant=a&tenant=b&keep=1 completes with tenant=['a','b'],
keep=1, and exactly one fresh code) — battery now 32/32 PASS;
oauth_test.py 16/16 and f3_negative_test.py 7/7 unchanged. Deployed
oauth_as.py SHA-256:
32058a6fbc6704af187a0e9750a16cdaae7dbadb32155f5b52ebe4844ffa06ae
(gateway pid 136117). Filed as GitHub issue #32 and closed by this fix.
With this, PR #31 has no open findings of any severity.
