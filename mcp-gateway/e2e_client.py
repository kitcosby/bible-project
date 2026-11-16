#!/usr/bin/env python3
"""LAMPY-CR-001 end-to-end client: drives the sandbox gateway over
real MCP HTTP (the house pattern from test_client.py) through the
CR section-5 round trip: Muse's message is planted in the sandbox
inbox as a file, then discovered, read, acknowledged and answered
through the dedicated inbox tools only.

Expects: server on 127.0.0.1:8899, tokens in
/home/mcpgw/secrets/client-token.txt (read+write) and
/home/mcpgw/secrets/client-token-ro.txt (read only).
Prints one line per check and a SUMMARY; exit 1 on any failure.
"""
import asyncio
import json
import sys
import urllib.request
import urllib.error
from pathlib import Path

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

URL = "http://127.0.0.1:8899/mcp"
TOKEN = Path("/home/mcpgw/secrets/client-token.txt").read_text().strip()
TOKEN_RO = Path("/home/mcpgw/secrets/client-token-ro.txt").read_text().strip()
QUEUE = Path("/home/mcpgw/projects/gpt-queue")
MID = "20261113T070000Z-urgent-e2e-roundtrip"
BODY = ("E2E round-trip probe.\n"
        "Discover me with inbox_status, read me with inbox_read, "
        "ack me with inbox_ack.")
RESULTS = []


def record(name, ok, detail=""):
    RESULTS.append((name, ok))
    print(("PASS " if ok else "FAIL ") + name
          + (f"  [{detail}]" if detail else ""))


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
    record("auth: no token -> 401", raw_status({}) == 401)
    record("auth: garbage token -> 401",
           raw_status({"Authorization": "Bearer mcpgw1.deadbeef.nope"})
           == 401)

    headers = {"Authorization": f"Bearer {TOKEN}"}
    async with streamablehttp_client(URL, headers=headers) as (rd, wr, _):
        async with ClientSession(rd, wr) as session:
            await session.initialize()
            tools = await session.list_tools()
            names = sorted(t.name for t in tools.tools)
            record("10: tools/list = 19 (14 original + 5 inbox)",
                   len(names) == 19
                   and all(n in names for n in (
                       "fs_list", "fs_read", "fs_search", "fs_write",
                       "fs_edit", "exec_run", "git_status", "git_log",
                       "git_branches", "git_diff", "pg_databases",
                       "pg_schema", "pg_query", "svc_probe",
                       "inbox_status", "inbox_read", "inbox_ack",
                       "inbox_send", "inbox_diagnostics")),
                   ", ".join(names))

            async def call(name, args):
                return await session.call_tool(name, args)

            st = tool_json(await call("inbox_status", {}))
            record("1: status discovers the planted message",
                   bool(st) and st["unread_count"] == 1
                   and st["next_unread_id"] == MID
                   and st["urgent_unread"] == [MID]
                   and st["oldest_unread_created"]
                   == "2026-11-13T07:00:00Z",
                   json.dumps(st))

            msg = tool_json(await call("inbox_read", {"message_id": MID}))
            record("2/3: read returns the complete message",
                   bool(msg) and msg["body"] == BODY
                   and msg["from"] == "claude" and msg["to"] == "gpt"
                   and msg["type"] == "urgent"
                   and msg["ack_state"] == "written-not-received")

            ack = tool_json(await call(
                "inbox_ack", {"message_id": MID, "state": "read"}))
            record("4: ack records read, agent = caller token id",
                   bool(ack) and ack["updated"] is True
                   and ack["state"] == "read"
                   and ack["agent"] == "cr001-e2e",
                   json.dumps(ack))

            st2 = tool_json(await call("inbox_status", {}))
            record("4: status now shows the message read",
                   bool(st2) and st2["unread_count"] == 0
                   and st2["read_count"] == 1)

            sent = tool_json(await call("inbox_send", {
                "type": "note", "slug": "e2e-reply",
                "body": "Reply from GPT over the sandbox round trip.",
                "task": "none"}))
            record("6: send publishes GPT's reply",
                   bool(sent) and sent["id"].endswith("Z-note-e2e-reply")
                   and Path(sent["path"]).is_file(),
                   json.dumps(sent))
            globals()["SENT_ID"] = sent["id"] if sent else None

            diag = tool_json(await call("inbox_diagnostics", {}))
            record("diag: watcher unknown, census and dirs honest",
                   bool(diag)
                   and diag["watcher_relay_health"]["status"] == "unknown"
                   and diag["message_census"]["total"] == 1
                   and diag["outbox_dir"]["writable"] is True
                   and diag["token_store"]["present"] is True
                   and diag["audit_log"]["present"] is True
                   and diag["audit_log"]["last_gateway_start"] is not None,
                   json.dumps(diag)[:400])

            fl = tool_json(await call("fs_list",
                                      {"root": "projects", "subpath": ""}))
            record("10: fs_list smoke call unaffected",
                   bool(fl) and any(e["name"] == "gpt-queue"
                                    for e in fl["entries"]))

    # read-only token: ack must be refused by the real scope path
    headers_ro = {"Authorization": f"Bearer {TOKEN_RO}"}
    async with streamablehttp_client(URL, headers=headers_ro) as (rd, wr, _):
        async with ClientSession(rd, wr) as session:
            await session.initialize()
            res = await session.call_tool(
                "inbox_ack", {"message_id": MID, "state": "acted"})
            record("scope: read-only token cannot ack (write scope)",
                   res.isError)

    # --- file-level verification, independent of the tools (test 5/7)
    ack_text = (QUEUE / "inbox" / "acks" / f"{MID}.ack.md").read_text()
    record("5: ack file on disk carries state read + agent",
           "state: read" in ack_text and "agent: cr001-e2e" in ack_text
           and f"id: {MID}" in ack_text)
    sent_id = globals().get("SENT_ID")
    reply = (QUEUE / "outbox" / f"{sent_id}.md").read_text()
    hdr, _, rbody = reply.partition("\n\n")
    fields = dict(line.partition(": ")[::2]
                  for line in hdr.splitlines())
    record("7: reply retrievable from the outbox files, format valid",
           fields.get("id") == sent_id
           and fields.get("from") == "gpt"
           and fields.get("to") == "claude"
           and fields.get("type") == "note"
           and "Reply from GPT over the sandbox round trip." in rbody)
    audit_text = Path("/home/mcpgw/logs/audit.jsonl").read_text()
    record("audit: sandbox log has gateway_start + inbox tool events, "
           "no token material",
           '"gateway_start"' in audit_text
           and '"tool": "inbox_ack"' in audit_text
           and TOKEN.split(".")[2] not in audit_text)

    failed = [n for n, ok in RESULTS if not ok]
    print(f"SUMMARY total={len(RESULTS)} "
          f"pass={len(RESULTS) - len(failed)} fail={len(failed)}")
    if failed:
        print("FAILED:", "; ".join(failed))
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    asyncio.run(main())
