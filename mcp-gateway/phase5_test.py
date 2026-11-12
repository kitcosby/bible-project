#!/usr/bin/env python3
"""Phase 5 battery for the Lampy MCP gateway (write + execution tools).

Runs on Lampy against http://127.0.0.1:8765/mcp. Mints two throwaway
tokens through gw_admin.py (one read+write, one read-only), exercises
fs_write / fs_edit / exec_run positively with the write token, proves
the read-only token is refused by the scope gate, checks the denylist
and traversal guards on the write path, verifies the audit log, then
revokes both tokens. Prints one line per check and a SUMMARY.
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
ADMIN = "/home/mcpgw/gateway/.venv/bin/python"
GW = "/home/mcpgw/gateway/gw_admin.py"
RESULTS = []


def record(name, ok, detail=""):
    RESULTS.append((name, ok))
    print(("PASS " if ok else "FAIL ") + name
          + (f"  [{detail}]" if detail else ""))


def admin(*args):
    return subprocess.run([ADMIN, GW, *args],
                          capture_output=True, text=True).stdout.strip()


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


def tool_error_text(result):
    for item in result.content:
        text = getattr(item, "text", None)
        if text:
            return text
    return ""


async def main():
    write_token = admin("mint", "phase5-battery", "--scopes", "read,write")
    read_token = admin("mint", "phase5-battery-readonly")
    write_id = write_token.split(".")[1]
    read_id = read_token.split(".")[1]
    try:
        headers = {"Authorization": f"Bearer {write_token}"}
        async with streamablehttp_client(URL, headers=headers) as (rd, wr, _):
            async with ClientSession(rd, wr) as s:
                await s.initialize()
                tools = await s.list_tools()
                names = sorted(t.name for t in tools.tools)
                record("tools/list includes the 3 write tools",
                       all(n in names for n in
                           ("fs_write", "fs_edit", "exec_run")),
                       ", ".join(names))

                async def call(name, args):
                    return await s.call_tool(name, args)

                r = tool_json(await call("fs_write", {
                    "root": "projects",
                    "subpath": "phase5-battery/scratch.txt",
                    "content": "phase5 line one\ndup dup\n"}))
                record("fs_write creates a file (parent dirs made)",
                       bool(r and r.get("bytes") == 24), str(r))

                r = tool_json(await call("fs_read", {
                    "root": "projects",
                    "subpath": "phase5-battery/scratch.txt"}))
                record("fs_read reads back the written file",
                       bool(r and r.get("content")
                            == "phase5 line one\ndup dup\n"))

                r = tool_json(await call("fs_edit", {
                    "root": "projects",
                    "subpath": "phase5-battery/scratch.txt",
                    "old": "line one", "new": "line 1"}))
                record("fs_edit replaces a unique string", bool(r))

                r = tool_json(await call("fs_read", {
                    "root": "projects",
                    "subpath": "phase5-battery/scratch.txt"}))
                record("fs_read confirms the edit landed",
                       bool(r and "phase5 line 1" in r.get("content", "")))

                res = await call("fs_edit", {
                    "root": "projects",
                    "subpath": "phase5-battery/scratch.txt",
                    "old": "dup", "new": "pair"})
                record("fs_edit ambiguous match refused", res.isError)

                res = await call("fs_write", {
                    "root": "projects", "subpath": "probe.env",
                    "content": "X=1\n"})
                record("fs_write secret-shaped path denied", res.isError)

                res = await call("fs_write", {
                    "root": "projects", "subpath": "../escape.txt",
                    "content": "x"})
                record("fs_write traversal refused", res.isError)

                r = tool_json(await call("exec_run", {
                    "command": "whoami", "cwd_root": "projects",
                    "cwd_subpath": "phase5-battery"}))
                record("exec_run runs as root",
                       bool(r and r.get("exit_code") == 0
                            and r.get("stdout", "").strip() == "root"),
                       str(r)[:120])

                r = tool_json(await call("exec_run", {
                    "command": "echo exec-ok > exec-marker.txt",
                    "cwd_root": "projects",
                    "cwd_subpath": "phase5-battery"}))
                r2 = tool_json(await call("fs_read", {
                    "root": "projects",
                    "subpath": "phase5-battery/exec-marker.txt"}))
                record("exec_run side effect visible via fs_read",
                       bool(r and r.get("exit_code") == 0 and r2
                            and r2.get("content", "").strip() == "exec-ok"))

                r = tool_json(await call("exec_run", {
                    "command": "pwd", "cwd_root": "stage"}))
                record("exec_run honours the stage root as cwd",
                       bool(r and r.get("stdout", "").strip() == "/opt/stage"),
                       str(r)[:120])

                r = tool_json(await call("exec_run", {
                    "command": "sleep 30", "cwd_root": "projects",
                    "timeout_seconds": 5}))
                record("exec_run timeout enforced",
                       bool(r and r.get("timed_out") is True), str(r)[:120])

                r = tool_json(await call("exec_run", {
                    "command": "rm -rf /home/mcpgw/projects/phase5-battery",
                    "cwd_root": "projects"}))
                record("exec_run cleanup of the battery directory",
                       bool(r and r.get("exit_code") == 0))

        headers = {"Authorization": f"Bearer {read_token}"}
        async with streamablehttp_client(URL, headers=headers) as (rd, wr, _):
            async with ClientSession(rd, wr) as s:
                await s.initialize()

                async def call(name, args):
                    return await s.call_tool(name, args)

                res = await call("fs_write", {
                    "root": "projects", "subpath": "phase5-battery/x.txt",
                    "content": "x"})
                record("read-only token: fs_write refused by scope gate",
                       res.isError
                       and "write" in tool_error_text(res),
                       tool_error_text(res)[:100])

                res = await call("exec_run", {"command": "whoami"})
                record("read-only token: exec_run refused by scope gate",
                       res.isError
                       and "write" in tool_error_text(res),
                       tool_error_text(res)[:100])

                r = tool_json(await call("pg_databases", {}))
                record("read-only token: read tools still work",
                       bool(r and all(d["reachable"]
                                      for d in r["databases"])))

        log = open("/home/mcpgw/logs/audit.jsonl").read()
        secret_part = write_token.split(".")[2]
        record("audit log has fs_write + exec_run events, no token material",
               '"tool": "fs_write"' in log and '"tool": "exec_run"' in log
               and secret_part not in log and write_token not in log)
    finally:
        admin("revoke", write_id)
        admin("revoke", read_id)
    record("revoked write token rejected",
           raw_status({"Authorization": f"Bearer {write_token}"}) == 401)

    failed = [n for n, ok in RESULTS if not ok]
    print(f"SUMMARY total={len(RESULTS)} pass={len(RESULTS) - len(failed)} "
          f"fail={len(failed)}")
    if failed:
        print("FAILED:", "; ".join(failed))
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    asyncio.run(main())
