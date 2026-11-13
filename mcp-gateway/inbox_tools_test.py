#!/usr/bin/env python3
"""Function-level battery for the LAMPY-CR-001 inbox tools.

Drives the five new gateway tools (inbox_status / inbox_read /
inbox_ack / inbox_send / inbox_diagnostics) directly against scratch
queue directories, plus the registration and no-regression checks for
the original fourteen tools. The gateway module is imported once with
MCPGW_QUEUE_DIR pointed at a bootstrap scratch; scenarios then rebind
the module's queue globals to their own scratch trees. Write-scope
enforcement is bypassed here by patching _require_write (the real
scope path is exercised over HTTP by the E2E round trip); the token
identity is patched to a fixed test id.

The permission-denial block re-executes this file as uid/gid 65534
(nobody) via setpriv, because the suite itself runs as root and root
bypasses the mode bits the denial depends on.

Prints one line per check and a SUMMARY; exit 1 on any failure.
"""
import hashlib
import json
import os
import pwd
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESULTS = []


def record(name, ok, detail=""):
    RESULTS.append((name, ok))
    print(("PASS " if ok else "FAIL ") + name
          + (f"  [{detail}]" if detail else ""))


def expect_value_error(name, fn, needle):
    try:
        fn()
    except ValueError as e:
        record(name, needle in str(e), str(e)[:140])
        return
    except Exception as e:  # noqa: BLE001
        record(name, False, f"wrong exception {type(e).__name__}: {e}")
        return
    record(name, False, "no error raised")


# ---------------------------------------------------------------- worker
def nobody_worker():
    """Runs as uid 65534 against the queue named by CR001_PERM_QUEUE.
    Prints one JSON object with the observed outcomes."""
    sys.path.insert(0, str(HERE))
    import gateway
    gateway._require_write = lambda: None  # scope is orthogonal here
    gateway._current_token_id = lambda: "nobody-worker"
    # Never let a worker's audit() reach a real log: point it inside
    # the (non-writable) scratch queue, where the open fails and the
    # failure is swallowed by design, exactly as audit() intends.
    gateway.AUDIT_LOG = (Path(os.environ["CR001_PERM_QUEUE"])
                         / "worker-audit.jsonl")
    out = {}
    mid = os.environ["CR001_PERM_MID"]
    st = gateway.inbox_status()
    out["status_unread"] = st["unread_count"]
    try:
        gateway.inbox_ack(mid, "read")
        out["ack"] = "NO ERROR (unexpected)"
    except ValueError as e:
        out["ack"] = str(e)
    try:
        gateway.inbox_send("note", "perm-probe", "body", "none")
        out["send"] = "NO ERROR (unexpected)"
    except ValueError as e:
        out["send"] = str(e)
    diag = gateway.inbox_diagnostics()
    out["inbox_writable"] = diag["inbox_dir"]["writable"]
    out["acks_writable"] = diag["acks_dir"]["writable"]
    out["outbox_writable"] = diag["outbox_dir"]["writable"]
    print("WORKER-JSON " + json.dumps(out))


if os.environ.get("CR001_NOBODY_WORKER"):
    nobody_worker()
    sys.exit(0)

# ---------------------------------------------------------------- setup
BOOT = Path(tempfile.mkdtemp(prefix="cr001-boot-"))
os.environ["MCPGW_QUEUE_DIR"] = str(BOOT / "gpt-queue")
sys.path.insert(0, str(HERE))
import gateway  # noqa: E402

SCRATCH_AUDIT = BOOT / "audit.jsonl"
gateway.AUDIT_LOG = SCRATCH_AUDIT
gateway._require_write = lambda: None
gateway._current_token_id = lambda: "test-token-1"


def bind_queue(qdir):
    gateway.QUEUE_DIR = qdir
    gateway.INBOX_DIR = qdir / "inbox"
    gateway.ACKS_DIR = qdir / "inbox" / "acks"
    gateway.OUTBOX_DIR = qdir / "outbox"
    (qdir / "inbox" / "acks").mkdir(parents=True, exist_ok=True)
    (qdir / "outbox").mkdir(parents=True, exist_ok=True)
    return qdir


def write_msg(qdir, mid, frm="claude", to="gpt", typ="note", task="none",
              created="2026-11-13T06:00:00Z", body="hello"):
    text = (f"id: {mid}\nfrom: {frm}\nto: {to}\ntype: {typ}\n"
            f"task: {task}\ncreated: {created}\n\n{body}")
    p = qdir / "inbox" / f"{mid}.md"
    p.write_text(text)
    return p


def parse_header_local(text):
    header, _, body = text.partition("\n\n")
    out = {}
    for line in header.splitlines():
        k, _, v = line.partition(":")
        out[k.strip()] = v.strip()
    return out, body


def now_id(typ, slug):
    n = datetime.now(timezone.utc)
    return f"{n.strftime('%Y%m%dT%H%M%SZ')}-{typ}-{slug}"


# ------------------------------------------------------- registration (10)
tools = gateway.mcp._tool_manager.list_tools()
names = sorted(t.name for t in tools)
ORIGINAL = ["exec_run", "fs_edit", "fs_list", "fs_read", "fs_search",
            "fs_write", "git_branches", "git_diff", "git_log",
            "git_status", "pg_databases", "pg_query", "pg_schema",
            "svc_probe"]
NEW = ["inbox_ack", "inbox_diagnostics", "inbox_read", "inbox_send",
       "inbox_status"]
record("10: 19 tools registered, original 14 unchanged",
       names == sorted(ORIGINAL + NEW), ", ".join(names))

# fs_list smoke against a patched scratch root
smoke_root = Path(tempfile.mkdtemp(prefix="cr001-roots-"))
(smoke_root / "planted.txt").write_text("x")
gateway.ROOTS = {"projects": smoke_root}
r = gateway.fs_list("projects", "")
record("10: fs_list smoke call on scratch root",
       any(e["name"] == "planted.txt" for e in r["entries"]))

# ------------------------------------------------------------- scenario A
qa = bind_queue(Path(tempfile.mkdtemp(prefix="cr001-a-")) / "gpt-queue")
M1 = "20261113T060000Z-urgent-e2e-probe"
BODY1 = "Round-trip probe body line 1.\nSecond line: colons — unicode."
p1 = write_msg(qa, M1, typ="urgent", body=BODY1)
hash_before = hashlib.sha256(p1.read_bytes()).hexdigest()

st = gateway.inbox_status()
record("1: status discovers exactly the placed message",
       st["unread_count"] == 1 and st["unread_ids"] == [M1]
       and st["read_count"] == 0 and st["acted_count"] == 0
       and st["malformed"] == [], json.dumps(st)[:200])
record("1: status next/oldest/urgent fields",
       st["next_unread_id"] == M1
       and st["oldest_unread_created"] == "2026-11-13T06:00:00Z"
       and st["urgent_unread"] == [M1])

msg = gateway.inbox_read(M1)
record("2: read returns complete header and body",
       msg["id"] == M1 and msg["from"] == "claude"
       and msg["to"] == "gpt" and msg["type"] == "urgent"
       and msg["task"] == "none"
       and msg["created"] == "2026-11-13T06:00:00Z"
       and msg["body"] == BODY1
       and msg["ack_state"] == "written-not-received")
expect_value_error("2: read unknown id refused",
                   lambda: gateway.inbox_read(
                       "20261113T060000Z-note-not-there"),
                   "unknown message id")
expect_value_error("2: read traversal id refused",
                   lambda: gateway.inbox_read("../../etc/passwd"),
                   "invalid message id")

ack = gateway.inbox_ack(M1, "read")
record("3: ack records read with token identity",
       ack["updated"] is True and ack["state"] == "read"
       and ack["agent"] == "test-token-1")
ack_file = qa / "inbox" / "acks" / f"{M1}.ack.md"
hdr, _ = parse_header_local(ack_file.read_text())
record("5: receipt verifiable from the files alone",
       hdr.get("state") == "read" and hdr.get("id") == M1
       and hashlib.sha256(p1.read_bytes()).hexdigest() == hash_before)

ack_bytes = ack_file.read_bytes()
again = gateway.inbox_ack(M1, "read")
record("8: duplicate ack is a no-op, bytes stable",
       again["updated"] is False and ack_file.read_bytes() == ack_bytes)
up = gateway.inbox_ack(M1, "acted")
back = gateway.inbox_ack(M1, "read")
record("8: state moves forward only (read->acted, never back)",
       up["updated"] is True and up["state"] == "acted"
       and back["updated"] is False and back["state"] == "acted"
       and len(list((qa / "inbox" / "acks").glob("*.ack.md"))) == 1)
msg2 = gateway.inbox_read(M1)
st2 = gateway.inbox_status()
record("8: duplicate read harmless; status reflects acted",
       msg2["ack_state"] == "acted" and st2["unread_count"] == 0
       and st2["acted_count"] == 1 and st2["next_unread_id"] is None)

sent = gateway.inbox_send("note", "e2e-reply", "Reply body from GPT.",
                          "none")
sp = Path(sent["path"])
shdr, sbody = parse_header_local(sp.read_text())
record("6/7: send publishes a well-formed reply to the outbox",
       sp.parent == qa / "outbox" and shdr.get("id") == sent["id"]
       and sp.name == sent["id"] + ".md"
       and shdr.get("from") == "gpt" and shdr.get("to") == "claude"
       and shdr.get("type") == "note" and "Reply body from GPT." in sbody)
sent2 = gateway.inbox_send("note", "e2e-reply", "Second reply.", "none")
record("6: back-to-back sends never collide or overwrite",
       sent2["id"] != sent["id"] and Path(sent2["path"]).is_file()
       and sp.is_file())
expect_value_error("6: send refuses a bad type",
                   lambda: gateway.inbox_send("memo", "x", "b"),
                   "type must be one of")
expect_value_error("6: send refuses a bad slug",
                   lambda: gateway.inbox_send("note", "Bad Slug!", "b"),
                   "invalid slug")
expect_value_error("6: send refuses an empty body",
                   lambda: gateway.inbox_send("note", "x", ""),
                   "body must be non-empty")

# ------------------------------------------------------------- scenario B
qb = bind_queue(Path(tempfile.mkdtemp(prefix="cr001-b-")) / "gpt-queue")
OLD = "20261110T060000Z-note-old-unacked"
write_msg(qb, OLD, created="2026-11-10T06:00:00Z", body="old")
FRESH = now_id("note", "fresh-unacked")
write_msg(qb, FRESH,
          created=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
          body="fresh")
DUPB = "20261113T061400Z-note-dup-b"
write_msg(qb, DUPB, body="the real dup target")
(qb / "inbox" / "20261113T061300Z-note-dup-a.md").write_text(
    f"id: {DUPB}\nfrom: claude\nto: gpt\ntype: note\ntask: none\n"
    "created: 2026-11-13T06:13:00Z\n\nimpostor")
(qb / "inbox" / "random-file.md").write_text("not a message")
(qb / "inbox" / "20261113T061000Z-note-broken-header.md").write_text(
    "id: 20261113T061000Z-note-broken-header\nfrom: claude\n")
(qb / "inbox" / "20261113T061100Z-note-truncated.md").write_text(
    "id: 20261113T061100Z-note-truncated\nfrom: cla")
(qb / "inbox" / ".20261113T061200Z-note-partial.tmp").write_text(
    "id: 20261113T061200Z-note-partial\nfrom: claude\nto: g")
(qb / "inbox" / "acks" / f".{OLD}.ack.1234.tmp").write_text("id: part")

stb = gateway.inbox_status()
mal_names = sorted(e["name"] for e in stb["malformed"])
record("9: status counts only valid messages, lists malformed",
       stb["unread_count"] == 3
       and sorted(stb["unread_ids"]) == sorted([OLD, FRESH, DUPB])
       and mal_names == ["20261113T061000Z-note-broken-header.md",
                         "20261113T061100Z-note-truncated.md",
                         "20261113T061300Z-note-dup-a.md",
                         "random-file.md"],
       f"unread={stb['unread_count']} malformed={mal_names}")
record("9: interrupted-write temp is invisible to status",
       all("partial" not in n for n in mal_names))
expect_value_error("9: read of a malformed message fails precisely",
                   lambda: gateway.inbox_read(
                       "20261113T061100Z-note-truncated"),
                   "malformed")

diag = gateway.inbox_diagnostics()
cen = diag["message_census"]
cen_names = [e["name"] for e in cen["malformed"]]
record("9: diagnostics census flags every planted defect",
       cen["total"] == 3
       and ".20261113T061200Z-note-partial.tmp" in cen_names
       and f"acks/.{OLD}.ack.1234.tmp" in cen_names
       and cen["duplicate_ids"] == [DUPB],
       json.dumps(cen)[:300])
record("9: diagnostics ages unacked messages honestly",
       cen["unacked_older_than_24h"] == [OLD]
       and diag["watcher_relay_health"]["status"] == "unknown"
       and "off-gateway" in diag["watcher_relay_health"]["reason"])
record("9: diagnostics dir checks ok on a healthy scratch queue",
       diag["inbox_dir"]["status"] == "ok"
       and diag["outbox_dir"]["writable"] is True
       and diag["audit_log"]["present"] in (True, False)
       and diag["token_store"]["status"] in ("ok", "failed"))

# planted audit log: last gateway_start is picked up
fake_log = Path(tempfile.mkdtemp(prefix="cr001-log-")) / "audit.jsonl"
fake_log.write_text(
    json.dumps({"ts": "2026-11-13T00:00:00+00:00",
                "kind": "gateway_start"}) + "\n"
    + json.dumps({"ts": "2026-11-13T01:00:00+00:00",
                  "kind": "tool", "tool": "fs_list"}) + "\n")
gateway.AUDIT_LOG = fake_log
diag2 = gateway.inbox_diagnostics()
record("9: diagnostics reports the last gateway_start from the log",
       diag2["audit_log"]["present"] is True
       and diag2["audit_log"]["last_gateway_start"]
       == "2026-11-13T00:00:00+00:00")
gateway.AUDIT_LOG = SCRATCH_AUDIT

# ------------------------------------------------------------- scenario C
missing = Path(tempfile.mkdtemp(prefix="cr001-c-")) / "no-queue-here"
gateway.QUEUE_DIR = missing
gateway.INBOX_DIR = missing / "inbox"
gateway.ACKS_DIR = missing / "inbox" / "acks"
gateway.OUTBOX_DIR = missing / "outbox"
stc = gateway.inbox_status()
record("9: unavailable inbox -> status is clean structured zeros",
       stc["unread_count"] == 0 and stc["unread_ids"] == []
       and stc["next_unread_id"] is None and stc["malformed"] == [])
diagc = gateway.inbox_diagnostics()
record("9: unavailable inbox -> diagnostics reports failed, not a crash",
       diagc["inbox_dir"]["status"] == "failed"
       and diagc["inbox_dir"]["exists"] is False
       and diagc["message_census"]["total"] == 0)
expect_value_error("9: read against a missing inbox fails closed",
                   lambda: gateway.inbox_read(
                       "20261113T060000Z-note-not-there"),
                   "unknown message id")
expect_value_error("9: ack against a missing inbox fails closed",
                   lambda: gateway.inbox_ack(
                       "20261113T060000Z-note-not-there", "read"),
                   "unknown message id")
expect_value_error("9: send against a missing outbox fails closed",
                   lambda: gateway.inbox_send("note", "x", "body"),
                   "outbox directory does not exist")

# ------------------------------------------------------------- scenario D
# Permission denial needs a non-root process (root bypasses mode bits).
# This VM additionally blocks non-root uids from the home tree entirely,
# so the worker runs from a staged copy under /tmp: as the mcpgw user
# with the production venv where that exists (the distro - also the
# highest-fidelity identity, since the gateway runs as mcpgw), else as
# nobody with a scratch /tmp venv mirroring the gateway's dependencies.
def prepare_worker():
    stage = Path(tempfile.mkdtemp(prefix="cr001-stage-"))
    for f in ("gateway.py", "oauth_as.py", "inbox_tools_test.py"):
        shutil.copy2(HERE / f, stage / f)
        os.chmod(stage / f, 0o644)  # copies inherit 660 root:root
    os.chmod(stage, 0o755)
    try:
        pw = pwd.getpwnam("mcpgw")
        venv_py = Path("/home/mcpgw/gateway/.venv/bin/python")
        if venv_py.exists():
            return (["setpriv", f"--reuid={pw.pw_uid}",
                     f"--regid={pw.pw_gid}", "--clear-groups",
                     str(venv_py), "-B",
                     str(stage / "inbox_tools_test.py")], "mcpgw")
    except KeyError:
        pass
    wvenv = Path("/tmp/cr001-worker-venv")
    if not (wvenv / ".cr001-ready").exists():
        if not (wvenv / "bin" / "python").exists():
            subprocess.run([sys.executable, "-m", "venv", str(wvenv)],
                           check=True, capture_output=True, text=True)
            subprocess.run(
                [str(wvenv / "bin" / "pip"), "install", "-q",
                 "mcp==1.30.0", "psycopg2-binary==2.9.13",
                 "uvicorn==0.54.0", "starlette==1.7.0"],
                check=True, capture_output=True, text=True)
        # This sandbox's root umask makes pip install 770/660 root:root;
        # the worker uid must be able to read the packages.
        subprocess.run(["chmod", "-R", "a+rX", str(wvenv)], check=True)
        (wvenv / ".cr001-ready").touch()
    return (["setpriv", "--reuid=65534", "--regid=65534",
             "--clear-groups", str(wvenv / "bin" / "python"), "-B",
             str(stage / "inbox_tools_test.py")], "nobody")


qd = Path(tempfile.mkdtemp(prefix="cr001-d-"))
os.chmod(qd, 0o755)
qdir = qd / "gpt-queue"
(qdir / "inbox" / "acks").mkdir(parents=True)
(qdir / "outbox").mkdir(parents=True)
os.chmod(qdir, 0o755)
os.chmod(qdir / "inbox", 0o755)
MID = "20261113T060000Z-note-perm-probe"
write_msg(qdir, MID, body="perm probe")
os.chmod(qdir / "inbox" / f"{MID}.md", 0o644)  # readable, as in production
os.chmod(qdir / "inbox" / "acks", 0o555)
os.chmod(qdir / "outbox", 0o555)
env = dict(os.environ, CR001_NOBODY_WORKER="1",
           MCPGW_QUEUE_DIR=str(qdir), CR001_PERM_MID=MID,
           CR001_PERM_QUEUE=str(qdir))
try:
    wcmd, wwho = prepare_worker()
    proc = subprocess.run(wcmd, capture_output=True, text=True, env=env,
                          timeout=300,
                          cwd=str(Path(wcmd[-1]).parent))
    wline = [ln for ln in proc.stdout.splitlines()
             if ln.startswith("WORKER-JSON ")]
    w = json.loads(wline[0][len("WORKER-JSON "):]) if wline else {}
    record(f"9: as {wwho}, status still reads a read-only inbox",
           w.get("status_unread") == 1, proc.stderr[-200:])
    record(f"9: as {wwho}, ack fails closed on a read-only acks dir",
           "Permission denied" in w.get("ack", ""), w.get("ack", "")[:140])
    record(f"9: as {wwho}, send fails closed on a read-only outbox",
           "Permission denied" in w.get("send", ""),
           w.get("send", "")[:140])
    record(f"9: as {wwho}, diagnostics reports writable=false",
           w.get("inbox_writable") is False
           and w.get("acks_writable") is False
           and w.get("outbox_writable") is False, json.dumps(w)[:200])
except Exception as e:  # noqa: BLE001
    record("9: permission-denial worker ran", False, str(e)[:200])

# ------------------------------------------------------- audit + default
log_text = SCRATCH_AUDIT.read_text() if SCRATCH_AUDIT.exists() else ""
record("audit: the new tools write audit events like the existing ones",
       all(f'"tool": "{t}"' in log_text for t in
           ("inbox_status", "inbox_read", "inbox_ack", "inbox_send",
            "inbox_diagnostics")))
proc = subprocess.run(
    [sys.executable, "-B", "-c",
     "import sys; sys.path.insert(0, '.'); import gateway; "
     "print(gateway.QUEUE_DIR)"],
    capture_output=True, text=True, cwd=str(HERE),
    env={k: v for k, v in os.environ.items()
         if k != "MCPGW_QUEUE_DIR"})
record("design: QUEUE_DIR default is the production layout",
       proc.stdout.strip() == "/home/mcpgw/projects/gpt-queue",
       proc.stdout.strip() or proc.stderr[-200:])

failed = [n for n, ok in RESULTS if not ok]
print(f"SUMMARY total={len(RESULTS)} pass={len(RESULTS) - len(failed)} "
      f"fail={len(failed)}")
if failed:
    print("FAILED:", "; ".join(failed))
sys.exit(1 if failed else 0)
