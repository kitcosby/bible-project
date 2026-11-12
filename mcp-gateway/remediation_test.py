#!/usr/bin/env python3
"""Remediation battery for the 2026-11-12 PR #31 review findings.

Covers:
- F6: fs_search must apply the same denylist as fs_read (canary files
  with deny-class names planted in a gateway clone must be invisible to
  search while a control file is found; the live secret.key under the
  bible-website root must never appear in search results).
- F7: git_diff must reject option-shaped refs (--output pair can no
  longer write a file); legitimate refs and ranges still resolve.
- F8: a client_name containing HTML/JavaScript must be escaped on the
  authorization page.
- Concurrency: completing an approved request twice must issue exactly
  one authorization code; the single code still exchanges normally.
- Final revision: a hostile OAuth state value (containing & and =)
  must be echoed identically after parsing, with exactly one code
  parameter in the callback; redirect registration must accept http
  only for parsed loopback hosts (localhost / 127.0.0.1), never for
  prefix lookalikes such as localhost.evil.example.

Runs on Lampy as mcpgw against http://127.0.0.1:8765.
"""
import asyncio
import base64
import hashlib
import json
import os
import re
import secrets
import subprocess
import sys
import urllib.request
import urllib.error
import urllib.parse
from pathlib import Path

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

BASE = "http://127.0.0.1:8765"
TOKEN = Path("/home/mcpgw/secrets/client-token.txt").read_text().strip()
REDIRECT = "https://chatgpt.com/connector_platform_oauth_redirect"
ADMIN = ["/home/mcpgw/gateway/.venv/bin/python",
         "/home/mcpgw/gateway/gw_admin.py"]
CLONE = Path("/home/mcpgw/projects/bible-project")
RESULTS = []


def record(name, ok, detail=""):
    RESULTS.append((name, ok))
    print(("PASS " if ok else "FAIL ") + name +
          (f"  [{detail}]" if detail else ""))


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
        with opener.open(r, timeout=20) as resp:
            return resp.status, resp.headers, resp.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.headers, e.read().decode()


def b64url(raw):
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()


async def call_tool(name, args):
    headers = {"Authorization": f"Bearer {TOKEN}"}
    async with streamablehttp_client(BASE + "/mcp", headers=headers) as (rd, wr, _):
        async with ClientSession(rd, wr) as session:
            await session.initialize()
            return await session.call_tool(name, args)


async def listed_tool_names():
    headers = {"Authorization": f"Bearer {TOKEN}"}
    async with streamablehttp_client(BASE + "/mcp", headers=headers) as (rd, wr, _):
        async with ClientSession(rd, wr) as session:
            await session.initialize()
            tools = await session.list_tools()
            return {t.name for t in tools.tools}


def tool_text(result):
    parts = []
    for item in (result.content or []):
        text = getattr(item, "text", None)
        if text:
            parts.append(text)
    return "\n".join(parts)


def register(client_name):
    status, _, body = req("POST", BASE + "/oauth/register", data={
        "client_name": client_name,
        "redirect_uris": [REDIRECT],
        "grant_types": ["authorization_code", "refresh_token"],
        "response_types": ["code"],
    })
    reg = json.loads(body) if status == 201 else {}
    return reg.get("client_id", ""), reg.get("client_secret", "")


def authorize(cid, verifier):
    challenge = b64url(hashlib.sha256(verifier.encode()).digest())
    q = urllib.parse.urlencode({
        "response_type": "code", "client_id": cid, "redirect_uri": REDIRECT,
        "scope": "read offline_access", "state": "remediation-state",
        "code_challenge": challenge, "code_challenge_method": "S256",
    })
    return req("GET", BASE + "/oauth/authorize?" + q)


async def mcp_checks():
    # ---- Registry precondition: negative checks below are meaningless
    # if the tool is not even registered (an unknown-tool error would
    # masquerade as a rejection). Assert the real tools exist first.
    names = await listed_tool_names()
    record("registry: fs_search and git_diff are listed tools",
           {"fs_search", "git_diff"} <= names,
           f"{len(names)} tools listed")

    # ---- F6: canary files in a gateway clone
    canaries = {
        "zz_f6_canary_secret.key": "F6CANARY-SECRET-9d3b",
        "zz_f6_canary.env.local": "F6CANARY-ENV-9d3b",
        "zz_f6_control.txt": "F6CANARY-CONTROL-9d3b",
    }
    secret_dir = CLONE / "zz_f6_secrets"
    try:
        for name, marker in canaries.items():
            (CLONE / name).write_text(marker + "\n")
        secret_dir.mkdir(exist_ok=True)
        (secret_dir / "inner.txt").write_text("F6CANARY-DIR-9d3b\n")

        res = await call_tool("fs_search", {
            "root": "projects", "subpath": "bible-project",
            "pattern": "F6CANARY"})
        text = "" if res.isError else tool_text(res)
        record("F6 control file is searchable",
               "F6CANARY-CONTROL-9d3b" in text)
        record("F6 secret.key canary invisible to fs_search",
               "F6CANARY-SECRET-9d3b" not in text)
        record("F6 .env.local canary invisible to fs_search",
               "F6CANARY-ENV-9d3b" not in text)
        record("F6 denied-directory canary invisible to fs_search",
               "F6CANARY-DIR-9d3b" not in text)

        res = await call_tool("fs_read", {
            "root": "projects", "subpath": "bible-project/zz_f6_control.txt"})
        record("F6 fs_read still reads a normal file",
               not res.isError and "F6CANARY-CONTROL-9d3b" in tool_text(res))
    finally:
        for name in canaries:
            (CLONE / name).unlink(missing_ok=True)
        (secret_dir / "inner.txt").unlink(missing_ok=True)
        try:
            secret_dir.rmdir()
        except OSError:
            pass

    # ---- F6: the live trees - the secret.key FILES must never be
    # searched. (Other files may legitimately mention the name in code;
    # the assertion is that no match line comes FROM a secret.key file.)
    res = await call_tool("fs_search", {"root": "bible-website",
                                        "pattern": "."})
    text = "" if res.isError else tool_text(res)
    record("F6 live bible-website search returns results", bool(text))
    record("F6 live website secret.key never searched",
           "/opt/bible/website/secret.key:" not in text)
    res = await call_tool("fs_search", {"root": "bible-data",
                                        "subpath": "website-debug",
                                        "pattern": "."})
    text = "" if res.isError else tool_text(res)
    record("F6 live website-debug secret.key never searched",
           "/opt/bible/website-debug/secret.key:" not in text)

    # ---- F7: git_diff option injection
    pwn = "/tmp/zz_f7_pwn"
    if os.path.exists(pwn):
        os.unlink(pwn)
    res = await call_tool("git_diff", {
        "repo": "bible-project", "ref_a": "--output", "ref_b": pwn})
    record("F7 ref_a=--output / ref_b=path rejected", bool(res.isError))
    record("F7 no file written by the rejected diff",
           not os.path.exists(pwn))
    res = await call_tool("git_diff", {
        "repo": "bible-project", "ref_a": "--output=/tmp/zz_f7_pwn2"})
    record("F7 ref_a=--output=<path> rejected", bool(res.isError))
    res = await call_tool("git_diff", {"repo": "bible-project",
                                       "ref_a": "HEAD"})
    record("F7 plain HEAD diff still works",
           not res.isError and "exit_code" in tool_text(res))
    res = await call_tool("git_diff", {"repo": "bible-project",
                                       "ref_a": "HEAD~1..HEAD"})
    record("F7 range HEAD~1..HEAD still works", not res.isError)


def oauth_checks():
    # ---- F8: client_name escaping
    payload = "<script>alert(1)</script>"
    cid, _ = register(payload)
    record("F8 payload client registered", bool(cid))
    verifier = secrets.token_urlsafe(48)
    status, _, body = authorize(cid, verifier)
    record("F8 authorize page escapes the client name",
           status == 200 and payload not in body
           and "&lt;script&gt;alert(1)&lt;/script&gt;" in body,
           f"status={status}")

    # ---- Concurrency: exactly one code per approved request
    cid2, csec2 = register("Remediation Double-Complete")
    verifier2 = secrets.token_urlsafe(48)
    status, _, body = authorize(cid2, verifier2)
    m = re.search(r"Request ID: <b[^>]*>([A-Z2-9]{6})</b>", body)
    req_id = m.group(1) if m else ""
    record("CC authorize issued a request id", bool(req_id))
    out = subprocess.run(ADMIN + ["approve", req_id],
                         capture_output=True, text=True)
    record("CC owner approval applied", out.returncode == 0,
           out.stdout.strip()[:60])
    s1, h1, _ = req("GET", BASE + f"/oauth/authorize/complete?req={req_id}")
    loc1 = h1.get("Location", "") if h1 else ""
    code1 = urllib.parse.parse_qs(
        urllib.parse.urlparse(loc1).query).get("code", [""])[0]
    record("CC first completion -> 302 with a code",
           s1 == 302 and bool(code1), f"status={s1}")
    s2, h2, b2 = req("GET", BASE + f"/oauth/authorize/complete?req={req_id}")
    loc2 = h2.get("Location", "") if h2 else ""
    record("CC second completion issues NO second code",
           s2 == 200 and "code=" not in loc2 and "already completed" in b2,
           f"status={s2}")
    basic = "Basic " + base64.b64encode(f"{cid2}:{csec2}".encode()).decode()
    status, _, body = req("POST", BASE + "/oauth/token", form={
        "grant_type": "authorization_code", "code": code1,
        "redirect_uri": REDIRECT, "code_verifier": verifier2},
        headers={"Authorization": basic})
    tok = json.loads(body) if status == 200 else {}
    record("CC the single issued code exchanges for a token",
           status == 200 and bool(tok.get("access_token")),
           f"status={status}")


def final_revision_checks():
    # ---- State encoding: hostile state must round-trip identically
    cid, _ = register("Remediation State Echo")
    evil_state = "x&code=FORGED y+z"
    verifier = secrets.token_urlsafe(48)
    challenge = b64url(hashlib.sha256(verifier.encode()).digest())
    q = urllib.parse.urlencode({
        "response_type": "code", "client_id": cid, "redirect_uri": REDIRECT,
        "scope": "read", "state": evil_state,
        "code_challenge": challenge, "code_challenge_method": "S256",
    })
    status, _, body = req("GET", BASE + "/oauth/authorize?" + q)
    m = re.search(r"Request ID: <b[^>]*>([A-Z2-9]{6})</b>", body)
    req_id = m.group(1) if m else ""
    subprocess.run(ADMIN + ["approve", req_id],
                   capture_output=True, text=True)
    s, h, _ = req("GET", BASE + f"/oauth/authorize/complete?req={req_id}")
    loc = h.get("Location", "") if h else ""
    qs = urllib.parse.parse_qs(urllib.parse.urlparse(loc).query)
    record("ST completion redirects with a code",
           s == 302 and bool(qs.get("code")), f"status={s}")
    record("ST exactly one code param, and it is not the forged one",
           len(qs.get("code", [])) == 1 and qs["code"][0] != "FORGED")
    record("ST hostile state echoed identically after parsing",
           qs.get("state") == [evil_state], f"state={qs.get('state')}")

    # ---- Localhost validation: parsed loopback hosts only
    def reg_status(uri):
        status, _, _ = req("POST", BASE + "/oauth/register", data={
            "client_name": "Remediation Redirect Probe",
            "redirect_uris": [uri],
            "grant_types": ["authorization_code"],
            "response_types": ["code"]})
        return status

    record("LH http://localhost.evil.example refused",
           reg_status("http://localhost.evil.example/cb") == 400)
    record("LH http://localhost@evil.example refused",
           reg_status("http://localhost@evil.example/cb") == 400)
    record("LH http://localhost:8765 accepted",
           reg_status("http://localhost:8765/cb") == 201)
    record("LH http://127.0.0.1:9000 accepted",
           reg_status("http://127.0.0.1:9000/cb") == 201)
    record("LH plain http non-loopback still refused",
           reg_status("http://evil.example.com/cb") == 400)


def main():
    asyncio.run(mcp_checks())
    oauth_checks()
    final_revision_checks()
    passed = sum(1 for _, ok in RESULTS if ok)
    print(f"SUMMARY: {passed}/{len(RESULTS)} passed")
    sys.exit(0 if passed == len(RESULTS) else 1)


if __name__ == "__main__":
    main()
