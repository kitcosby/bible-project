#!/usr/bin/env python3
"""F3 regression test (2026-11-12): redirect_uri is REQUIRED at token
exchange when it was present in the authorization request (RFC 6749
4.1.3). Before the fix, an exchange omitting redirect_uri succeeded if
everything else was right. This test drives a full grant, then tries:
  1. exchange WITHOUT redirect_uri  -> must be 400 invalid_grant
  2. exchange with WRONG redirect_uri -> must be 400 invalid_grant
  3. exchange with the correct redirect_uri -> must succeed (also proves
     the failed attempts did not consume the single-use code)
Run as mcpgw on Lampy against localhost, same as oauth_test.py.
"""
import base64
import hashlib
import json
import re
import secrets
import subprocess
import urllib.error
import urllib.parse
import urllib.request

BASE = "http://127.0.0.1:8765"
REDIRECT = "https://chatgpt.com/connector_platform_oauth_redirect"
ADMIN = ["/home/mcpgw/gateway/.venv/bin/python",
         "/home/mcpgw/gateway/gw_admin.py"]
RESULTS = []


def record(name, ok, detail=""):
    RESULTS.append((name, ok))
    print(("PASS " if ok else "FAIL ") + name + (f" [{detail}]" if detail else ""))


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


opener = urllib.request.build_opener(NoRedirect)


def req(method, url, data=None, headers=None, form=None):
    h = dict(headers or {})
    body = None
    if data is not None:
        body = json.dumps(data).encode()
        h["Content-Type"] = "application/json"
    if form is not None:
        body = urllib.parse.urlencode(form).encode()
        h["Content-Type"] = "application/x-www-form-urlencoded"
    r = urllib.request.Request(url, data=body, headers=h, method=method)
    try:
        with opener.open(r) as resp:
            return resp.status, resp.headers, resp.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.headers, e.read().decode()


def b64url(raw):
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()


def main():
    status, _, body = req("POST", BASE + "/oauth/register", data={
        "client_name": "F3 Negative Test",
        "redirect_uris": [REDIRECT],
        "grant_types": ["authorization_code", "refresh_token"],
        "response_types": ["code"],
    })
    reg = json.loads(body) if status == 201 else {}
    cid, csec = reg.get("client_id", ""), reg.get("client_secret", "")
    record("setup: DCR register", status == 201 and bool(cid), f"status={status}")

    verifier = secrets.token_urlsafe(48)
    challenge = b64url(hashlib.sha256(verifier.encode()).digest())
    q = urllib.parse.urlencode({
        "response_type": "code", "client_id": cid, "redirect_uri": REDIRECT,
        "scope": "read", "state": "f3-state",
        "code_challenge": challenge, "code_challenge_method": "S256",
    })
    status, _, body = req("GET", BASE + "/oauth/authorize?" + q)
    m = re.search(r"Request ID: <b[^>]*>([A-Z2-9]{6})</b>", body)
    req_id = m.group(1) if m else ""
    record("setup: authorize -> pending id", status == 200 and bool(req_id))

    out = subprocess.run(ADMIN + ["approve", req_id],
                         capture_output=True, text=True).stdout
    record("setup: owner approval", "approved" in out, out.strip())
    status, headers, _ = req(
        "GET", BASE + f"/oauth/authorize/complete?req={req_id}")
    code = urllib.parse.parse_qs(urllib.parse.urlparse(
        headers.get("Location", "")).query).get("code", [""])[0]
    record("setup: complete -> code", status == 302 and bool(code))

    basic = "Basic " + base64.b64encode(f"{cid}:{csec}".encode()).decode()

    status, _, body = req("POST", BASE + "/oauth/token", form={
        "grant_type": "authorization_code", "code": code,
        "code_verifier": verifier}, headers={"Authorization": basic})
    record("F3: exchange WITHOUT redirect_uri -> invalid_grant",
           status == 400 and "invalid_grant" in body, f"status={status}")

    status, _, body = req("POST", BASE + "/oauth/token", form={
        "grant_type": "authorization_code", "code": code,
        "redirect_uri": "https://chatgpt.com/other",
        "code_verifier": verifier}, headers={"Authorization": basic})
    record("F3: exchange with WRONG redirect_uri -> invalid_grant",
           status == 400 and "invalid_grant" in body, f"status={status}")

    status, _, body = req("POST", BASE + "/oauth/token", form={
        "grant_type": "authorization_code", "code": code,
        "redirect_uri": REDIRECT, "code_verifier": verifier},
        headers={"Authorization": basic})
    tok = json.loads(body) if status == 200 else {}
    record("F3: exchange with correct redirect_uri -> token issued",
           status == 200 and bool(tok.get("access_token")), f"status={status}")

    passed = sum(1 for _, ok in RESULTS if ok)
    print(f"SUMMARY: {passed}/{len(RESULTS)} PASS")
    raise SystemExit(0 if passed == len(RESULTS) else 1)


if __name__ == "__main__":
    main()
