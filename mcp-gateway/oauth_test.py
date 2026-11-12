#!/usr/bin/env python3
"""OAuth dance battery: simulate ChatGPT's MCP registration flow against
the Lampy gateway AS on localhost (the transport is identical over the
Funnel; only the base URL differs).

Flow: DCR -> authorize (pending) -> owner approval via gw_admin ->
complete (302 + code) -> token exchange with PKCE -> MCP call with the
access token -> refresh rotation -> reuse negatives.
"""
import asyncio
import base64
import hashlib
import json
import re
import secrets
import subprocess
import sys
import urllib.request
import urllib.error
import urllib.parse

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

BASE = "http://127.0.0.1:8765"
REDIRECT = "https://chatgpt.com/connector_platform_oauth_redirect"
ADMIN = ["/home/mcpgw/gateway/.venv/bin/python", "/home/mcpgw/gateway/gw_admin.py"]
RESULTS = []


def record(name, ok, detail=""):
    RESULTS.append((name, ok))
    print(("PASS " if ok else "FAIL ") + name + (f"  [{detail}]" if detail else ""))


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


opener = urllib.request.build_opener(NoRedirect)


def req(method, url, data=None, headers=None, form=None):
    body = None
    hdrs = dict(headers or {})
    if form is not None:
        body = urllib.parse.urlencode(form).encode()
        hdrs["Content-Type"] = "application/x-www-form-urlencoded"
    elif data is not None:
        body = json.dumps(data).encode()
        hdrs["Content-Type"] = "application/json"
    r = urllib.request.Request(url, data=body, method=method, headers=hdrs)
    try:
        with opener.open(r, timeout=15) as resp:
            return resp.status, resp.headers, resp.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.headers, e.read().decode()


def b64url(raw):
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()


async def mcp_probe(access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    async with streamablehttp_client(BASE + "/mcp", headers=headers) as (rd, wr, _):
        async with ClientSession(rd, wr) as session:
            await session.initialize()
            tools = await session.list_tools()
            res = await session.call_tool(
                "pg_query",
                {"database": "bible", "sql": "SELECT count(*) AS n FROM verses"},
            )
            text = res.content[0].text if res.content else ""
            return len(tools.tools), text


def main():
    # 1. Dynamic client registration
    status, _, body = req("POST", BASE + "/oauth/register", data={
        "client_name": "Battery Simulated ChatGPT",
        "redirect_uris": [REDIRECT],
        "grant_types": ["authorization_code", "refresh_token"],
        "response_types": ["code"],
    })
    reg = json.loads(body) if status == 201 else {}
    record("DCR register -> 201 with client credentials",
           status == 201 and reg.get("client_id") and reg.get("client_secret"),
           f"status={status}")
    cid, csec = reg.get("client_id", ""), reg.get("client_secret", "")

    status, _, _ = req("POST", BASE + "/oauth/register", data={
        "client_name": "bad", "redirect_uris": ["http://evil.example.com/cb"]})
    record("DCR http redirect_uri refused", status == 400)

    # 2. Authorize -> pending page with a request id
    verifier = secrets.token_urlsafe(48)
    challenge = b64url(hashlib.sha256(verifier.encode()).digest())
    q = urllib.parse.urlencode({
        "response_type": "code", "client_id": cid, "redirect_uri": REDIRECT,
        "scope": "read offline_access", "state": "battery-state",
        "code_challenge": challenge, "code_challenge_method": "S256",
        "resource": "https://lampy.taila7a335.ts.net/mcp",
    })
    status, _, body = req("GET", BASE + "/oauth/authorize?" + q)
    m = re.search(r"Request ID: <b[^>]*>([A-Z2-9]{6})</b>", body)
    record("authorize -> pending page with request id",
           status == 200 and bool(m), f"status={status}")
    req_id = m.group(1) if m else ""

    status, _, body = req(
        "GET", BASE + f"/oauth/authorize/complete?req={req_id}")
    record("complete before approval -> still pending, no code",
           status == 200 and "still awaiting" in body)

    # authorize negatives
    qbad = urllib.parse.urlencode({
        "response_type": "code", "client_id": cid,
        "redirect_uri": "https://chatgpt.com/not-registered",
        "code_challenge": challenge, "code_challenge_method": "S256"})
    status, _, _ = req("GET", BASE + "/oauth/authorize?" + qbad)
    record("authorize unregistered redirect_uri -> 400", status == 400)
    qbad2 = urllib.parse.urlencode({
        "response_type": "code", "client_id": cid, "redirect_uri": REDIRECT})
    status, _, _ = req("GET", BASE + "/oauth/authorize?" + qbad2)
    record("authorize without PKCE -> 400", status == 400)

    # 3. Owner approval out of band, then complete -> 302 with code
    out = subprocess.run(ADMIN + ["approve", req_id],
                         capture_output=True, text=True).stdout
    record("gw_admin approve works", "approved" in out, out.strip())
    status, headers, _ = req(
        "GET", BASE + f"/oauth/authorize/complete?req={req_id}")
    loc = headers.get("Location", "")
    code = urllib.parse.parse_qs(
        urllib.parse.urlparse(loc).query).get("code", [""])[0]
    state = urllib.parse.parse_qs(
        urllib.parse.urlparse(loc).query).get("state", [""])[0]
    record("complete after approval -> 302 code + state",
           status == 302 and bool(code) and state == "battery-state")

    basic = "Basic " + base64.b64encode(f"{cid}:{csec}".encode()).decode()

    # 4. Token exchange: wrong verifier, wrong secret, then success
    status, _, body = req("POST", BASE + "/oauth/token", form={
        "grant_type": "authorization_code", "code": code,
        "redirect_uri": REDIRECT, "code_verifier": "wrong-verifier-value"},
        headers={"Authorization": basic})
    record("token exchange wrong PKCE verifier -> invalid_grant",
           status == 400 and "invalid_grant" in body)
    badbasic = "Basic " + base64.b64encode(f"{cid}:nope".encode()).decode()
    status, _, body = req("POST", BASE + "/oauth/token", form={
        "grant_type": "authorization_code", "code": code,
        "redirect_uri": REDIRECT, "code_verifier": verifier},
        headers={"Authorization": badbasic})
    record("token exchange wrong client secret -> 401",
           status == 401 and "invalid_client" in body)
    status, _, body = req("POST", BASE + "/oauth/token", form={
        "grant_type": "authorization_code", "code": code,
        "redirect_uri": REDIRECT, "code_verifier": verifier},
        headers={"Authorization": basic})
    tok = json.loads(body) if status == 200 else {}
    record("token exchange -> access + refresh (offline_access)",
           status == 200 and bool(tok.get("access_token"))
           and bool(tok.get("refresh_token")), f"status={status}")
    status, _, body = req("POST", BASE + "/oauth/token", form={
        "grant_type": "authorization_code", "code": code,
        "redirect_uri": REDIRECT, "code_verifier": verifier},
        headers={"Authorization": basic})
    record("authorization code reuse -> invalid_grant",
           status == 400 and "invalid_grant" in body)

    # 5. Access token actually works against the MCP endpoint
    try:
        n_tools, text = asyncio.run(mcp_probe(tok.get("access_token", "")))
        record("OAuth access token -> MCP tools + query",
               n_tools == 14 and "31311" in text,
               f"tools={n_tools} verses_row={text[:40]}")
    except Exception as e:  # noqa: BLE001
        record("OAuth access token -> MCP tools + query", False, str(e)[:120])

    # 6. Refresh rotation
    rt = tok.get("refresh_token", "")
    status, _, body = req("POST", BASE + "/oauth/token", form={
        "grant_type": "refresh_token", "refresh_token": rt},
        headers={"Authorization": basic})
    tok2 = json.loads(body) if status == 200 else {}
    record("refresh -> new access + rotated refresh",
           status == 200 and bool(tok2.get("access_token"))
           and tok2.get("refresh_token") not in ("", rt))
    status, _, body = req("POST", BASE + "/oauth/token", form={
        "grant_type": "refresh_token", "refresh_token": rt},
        headers={"Authorization": basic})
    record("old refresh token reuse -> invalid_grant",
           status == 400 and "invalid_grant" in body)
    try:
        n_tools, _ = asyncio.run(mcp_probe(tok2.get("access_token", "")))
        record("refreshed access token works", n_tools == 14)
    except Exception as e:  # noqa: BLE001
        record("refreshed access token works", False, str(e)[:120])

    failed = [n for n, ok in RESULTS if not ok]
    print(f"SUMMARY total={len(RESULTS)} pass={len(RESULTS) - len(failed)} "
          f"fail={len(failed)}")
    if failed:
        print("FAILED:", "; ".join(failed))
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
