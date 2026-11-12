#!/usr/bin/env python3
"""Privileged helper for the Lampy MCP gateway (Phase 5).

Installed root-owned at /usr/local/sbin/mcpgw-root-helper.py and reachable
from the unprivileged gateway process ONLY through a setuid launcher
(root_helper_launcher.c, root:root mode 4755) that refuses every caller
except the mcpgw user - the distro ships no sudo, so the launcher is the
gateway's single privileged path, and this file is root-owned precisely
so the invoking account cannot modify the code it elevates. The gateway
(running as mcpgw) passes one JSON request on stdin and reads one JSON
reply on stdout:

  {"op": "write", "root": ..., "subpath": ..., "content_b64": ...}
  {"op": "edit",  "root": ..., "subpath": ..., "old": ..., "new": ...}
  {"op": "exec",  "command": ..., "cwd_root": ..., "cwd_subpath": ...,
   "timeout": 60}

Filesystem ops are confined to the gateway's advertised write roots,
canonicalized here again (the helper does not trust its caller), with
the gateway's secret-file denylist applied to every path component.
exec runs the command with bash as root, in a working directory inside
those roots: it is the general-access path the owner granted, and the
gateway audit-logs every invocation before making it.
"""
import base64
import binascii
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOTS = {
    "projects": Path("/home/mcpgw/projects"),
    "bible-website": Path("/opt/bible/website"),
    "bible-data": Path("/opt/bible"),
    "stage": Path("/opt/stage"),
    "bible-app-api": Path("/opt/bible-app-api"),
}
DENY_COMPONENT = re.compile(
    r"((^|\.)env($|\.)|\.envrc$|secret|credential|\.key$|\.pem$"
    r"|^id_(rsa|ed25519|toe)|\.password$|\.cred$|tokens\.json$)",
    re.IGNORECASE,
)
MAX_WRITE_BYTES = 1024 * 1024
MAX_OUTPUT_CHARS = 20000


def reply(obj):
    print(json.dumps(obj))
    sys.exit(0)


def fail(msg):
    reply({"ok": False, "error": str(msg)[:500]})


def resolve(root_name, subpath):
    if root_name not in ROOTS:
        fail(f"unknown root {root_name!r}")
    root = ROOTS[root_name].resolve()
    target = (root / subpath).resolve() if subpath else root
    if not target.is_relative_to(root):
        fail("path escapes the allowlisted root")
    for part in target.relative_to(root).parts:
        if part == ".git" or DENY_COMPONENT.search(part):
            fail(f"path component denied: {part}")
    return target


def atomic_write(target, data):
    mode = None
    if target.exists():
        if not target.is_file():
            fail(f"not a file: {target}")
        mode = target.stat().st_mode & 0o777
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".mcpgw-", dir=str(target.parent))
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
        os.chmod(tmp, mode if mode is not None else 0o644)
        os.replace(tmp, target)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def op_write(req):
    try:
        data = base64.b64decode(req["content_b64"], validate=True)
    except (binascii.Error, KeyError):
        fail("content_b64 missing or invalid")
    if len(data) > MAX_WRITE_BYTES:
        fail("content larger than the 1 MB write cap")
    target = resolve(req["root"], req["subpath"])
    if target.is_dir():
        fail("target is a directory")
    atomic_write(target, data)
    reply({"ok": True, "bytes": len(data), "path": str(target)})


def op_edit(req):
    old, new = req.get("old", ""), req.get("new", "")
    if not old:
        fail("old must be non-empty")
    if len(new.encode("utf-8")) > MAX_WRITE_BYTES:
        fail("replacement larger than the 1 MB write cap")
    target = resolve(req["root"], req["subpath"])
    if not target.is_file():
        fail(f"not a file: {target}")
    try:
        text = target.read_bytes().decode("utf-8")
    except UnicodeDecodeError:
        fail("not a UTF-8 text file")
    count = text.count(old)
    if count != 1:
        fail(f"old occurs {count} times (exactly 1 required)")
    data = text.replace(old, new).encode("utf-8")
    atomic_write(target, data)
    reply({"ok": True, "bytes": len(data), "path": str(target)})


def _text(value):
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value


def op_exec(req):
    command = req.get("command", "")
    if not command.strip():
        fail("command must be non-empty")
    cwd = resolve(req.get("cwd_root", "projects"),
                  req.get("cwd_subpath", ""))
    if not cwd.is_dir():
        fail(f"cwd is not a directory: {cwd}")
    timeout = max(1, min(int(req.get("timeout", 60)), 600))
    timed_out = False
    try:
        proc = subprocess.run(
            ["/bin/bash", "-c", command], cwd=str(cwd),
            capture_output=True, text=True, timeout=timeout,
        )
        exit_code, out, err = proc.returncode, proc.stdout, proc.stderr
    except subprocess.TimeoutExpired as e:
        timed_out = True
        exit_code, out, err = None, _text(e.stdout), _text(e.stderr)
    reply({
        "ok": True,
        "exit_code": exit_code,
        "timed_out": timed_out,
        "stdout": (out or "")[:MAX_OUTPUT_CHARS],
        "stderr": (err or "")[:MAX_OUTPUT_CHARS],
        "stdout_truncated": len(out or "") > MAX_OUTPUT_CHARS,
        "stderr_truncated": len(err or "") > MAX_OUTPUT_CHARS,
        "cwd": str(cwd),
    })


def _become_root():
    # The launcher sets our effective uid to 0 but leaves the real uid
    # as mcpgw, and bash (our exec child) drops euid to ruid at startup
    # unless they already match. Set both to 0 so every child process
    # is unambiguously root. When the helper is invoked WITHOUT the
    # launcher (euid != 0 and setuid refused), fail closed.
    if os.geteuid() == 0:
        try:
            os.setuid(0)
        except OSError:
            pass
    if os.geteuid() != 0 or os.getuid() != 0:
        fail("root helper is not running as root")


def main():
    _become_root()
    try:
        req = json.load(sys.stdin)
    except json.JSONDecodeError:
        fail("request is not JSON")
    op = req.get("op")
    try:
        if op == "write":
            op_write(req)
        elif op == "edit":
            op_edit(req)
        elif op == "exec":
            op_exec(req)
        else:
            fail(f"unknown op {op!r}")
    except Exception as e:  # noqa: BLE001 - report, never crash silently
        fail(e)


if __name__ == "__main__":
    main()
