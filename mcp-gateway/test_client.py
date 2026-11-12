#!/usr/bin/env python3
"""Phase 2 local battery for the Lampy MCP gateway.

Runs on Lampy as mcpgw against http://127.0.0.1:8765/mcp. Positive tool
calls over the real MCP client SDK; negative auth checks over raw HTTP;
guard checks through the SDK; audit-log hygiene and token revocation
verified at the end. Prints one line per check and a SUMMARY.
"""
import asyncio
import json
import subprocess
import sys
import urllib.request
import urllib.error

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

URL = "http://127.0.0.1:8765/mcp"
TOKEN = open("/home/mcpgw/secrets/client-token.txt").read().strip()
RESULTS = []


def record(name, ok, detail=""):
    RESULTS.append((name, ok))
    print(("PASS " if ok else "FAIL ") + name + (f"  [{detail}]" if detail else ""))


def raw_status(headers):
    req = urllib.request.Request(URL, data=b"{}", method="POST")
    for k, v in headers.items():
        req.add_header(k, v)
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "application/json, text/event-stream")
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception:  # noqa: BLE001
        return None


def tool_json(result):
    if result.isError:
        return None
    for item in result.content:
        text = getattr(item, "text", None)
        if text:
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                return {"_text": text}
    return {}


async def main():
    # --- raw auth negatives (middleware answers before MCP routing)
    record("no-token -> 401", raw_status({}) == 401)
    record("garbage-token -> 401",
           raw_status({"Authorization": "Bearer mcpgw1.deadbeef.nope"}) == 401)
    record("wrong-scheme -> 401",
           raw_status({"Authorization": "Token abc"}) == 401)

    headers = {"Authorization": f"Bearer {TOKEN}"}
    async with streamablehttp_client(URL, headers=headers) as (rd, wr, _):
        async with ClientSession(rd, wr) as session:
            await session.initialize()
            tools = await session.list_tools()
            names = sorted(t.name for t in tools.tools)
            record("tools/list returns the 11 read tools",
                   len(names) == 11, ", ".join(names))

            async def call(name, args):
                return await session.call_tool(name, args)

            r = tool_json(await call("fs_read", {
                "root": "projects",
                "subpath": "bible-project/README.md"}))
            record("fs_read bible-project README",
                   bool(r and "content" in r and len(r["content"]) > 50))

            r = tool_json(await call("fs_list", {
                "root": "projects", "subpath": "BibleApp"}))
            record("fs_list BibleApp clone",
                   bool(r and any(e["name"] == "artifacts"
                                  for e in r["entries"])))

            r = tool_json(await call("git_status", {"repo": "bible-project"}))
            record("git_status bible-project",
                   bool(r and r.get("exit_code") == 0
                        and "master" in r.get("stdout", "")),
                   (r or {}).get("stdout", "")[:60].replace("\n", " "))

            r = tool_json(await call("git_log", {"repo": "BibleApp",
                                                 "count": 3}))
            record("git_log BibleApp mentions redeploy addendum",
                   bool(r and "cbafdb4" in r.get("stdout", "")))

            r = tool_json(await call("pg_databases", {}))
            ok = bool(r) and all(d["reachable"] for d in r["databases"])
            bible = next((d for d in r["databases"]
                          if d["database"] == "bible"), {})
            record("pg_databases all 6 reachable", ok,
                   f"bible public_tables={bible.get('public_tables')}")

            r = tool_json(await call("pg_query", {
                "database": "bible",
                "sql": "SELECT count(*) AS n FROM words"}))
            record("pg_query bible.words = 264217",
                   bool(r and r["rows"] and r["rows"][0][0] == "264217"),
                   str((r or {}).get("rows")))

            r = tool_json(await call("pg_query", {
                "database": "bible_hebrew_variant_shadow_20261107",
                "sql": "SELECT count(*) AS n FROM hebrew_vowel_variant_group"}))
            record("pg_query shadow groups = 3349 (explicit db, no substitution)",
                   bool(r and r["rows"] and r["rows"][0][0] == "3349"))

            r = tool_json(await call("svc_probe", {}))
            record("svc_probe estate answers",
                   bool(r and r["tcp"].get("flask_prod") == "open"
                        and r["http"].get("flask_prod_books") == 200
                        and r["http"].get("express_prod_variant_noauth") == 403),
                   str((r or {}).get("http")))

            # --- guard negatives through the SDK (tool errors expected)
            async def expect_error(name, args):
                res = await call(name, args)
                return res.isError

            record("pg_query DELETE refused",
                   await expect_error("pg_query", {
                       "database": "bible",
                       "sql": "DELETE FROM words WHERE false"}))
            record("pg_query two statements refused",
                   await expect_error("pg_query", {
                       "database": "bible",
                       "sql": "SELECT 1; SELECT 2"}))
            record("pg_query non-allowlisted database refused",
                   await expect_error("pg_query", {
                       "database": "postgres", "sql": "SELECT 1"}))
            record("fs_read traversal refused",
                   await expect_error("fs_read", {
                       "root": "projects",
                       "subpath": "../../etc/passwd"}))
            record("fs_read .env denied",
                   await expect_error("fs_read", {
                       "root": "projects", "subpath": "probe.env"}))
            record("fs_read outside roots refused",
                   await expect_error("fs_read", {
                       "root": "bible-data",
                       "subpath": "../../root/bible-app-api.env"}))
            record("fs_read binary refused",
                   await expect_error("fs_read", {
                       "root": "bible-data",
                       "subpath": "word_variants_embeddings_recovery.db"}))
            record("git unknown repo refused",
                   await expect_error("git_status", {"repo": "rtheory"}))

    # --- audit hygiene: the presented token must never appear in the log
    secret_part = TOKEN.split(".")[2]
    log = open("/home/mcpgw/logs/audit.jsonl").read()
    record("audit log has tool events, no token material",
           '"tool": "pg_query"' in log and secret_part not in log
           and TOKEN not in log)
    record("audit log recorded auth rejects",
           '"auth_reject"' in log)

    # --- revocation (AT-14 shape): mint, use, revoke, reuse -> 401
    admin = "/home/mcpgw/gateway/.venv/bin/python"
    gw = "/home/mcpgw/gateway/gw_admin.py"
    tok2 = subprocess.run([admin, gw, "mint", "revocation-probe"],
                          capture_output=True, text=True).stdout.strip()
    id2 = tok2.split(".")[1]
    ok_before = raw_status({"Authorization": f"Bearer {tok2}"}) != 401
    subprocess.run([admin, gw, "revoke", id2], capture_output=True, text=True)
    ok_after = raw_status({"Authorization": f"Bearer {tok2}"}) == 401
    record("revoked token rejected (AT-14)", ok_before and ok_after)

    failed = [n for n, ok in RESULTS if not ok]
    print(f"SUMMARY total={len(RESULTS)} pass={len(RESULTS) - len(failed)} "
          f"fail={len(failed)}")
    if failed:
        print("FAILED:", "; ".join(failed))
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    asyncio.run(main())
