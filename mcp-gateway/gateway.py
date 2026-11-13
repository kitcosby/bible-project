#!/usr/bin/env python3
"""Lampy MCP gateway - Phases 2-5.

Serves a Streamable HTTP MCP endpoint on 127.0.0.1 only, authenticated by
opaque bearer tokens from a local token store (hashed, scoped, revocable).
The Phase 2 read tools are open to any read-scope token. Phase 5 adds
fs_write / fs_edit / exec_run for tokens carrying the "write" scope: file
writes are confined to the write roots under the same denylist as reads,
and execution runs as root via a single setuid-launched helper - the
general-access path the owner granted so the connected agent can work in
the Lampy environment and run the project's test suites through this
gateway. All calls are audit-logged without secrets.

Design notes (requirements doc 2026-11-12):
- SEC-1: binds localhost; exposure is a separate phase.
- SEC-2: dedicated credentials, stored hashed, rotation/revocation via
  gw_admin.py. The OAuth authorization server for ChatGPT (Phase 4) will
  issue tokens into this same store; the verifier does not change.
- SEC-4: runs as the unprivileged mcpgw user; filesystem tools are
  confined to allowlisted roots with a secret-file denylist; PostgreSQL
  access goes through the mcp_ro role (read-only transactions enforced
  server-side) plus a statement filter here as defense in depth.
- SEC-5: audit JSONL at /home/mcpgw/logs/audit.jsonl.
"""
import asyncio
import base64
import hashlib
import hmac
import json
import os
import re
import socket
import subprocess
import time
import urllib.request
import urllib.error
from datetime import datetime, timedelta, timezone
from pathlib import Path

import psycopg2
from oauth_as import PUBLIC_PREFIXES, mount_oauth
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

BASE = Path("/home/mcpgw")
SECRETS = BASE / "secrets"
TOKEN_STORE = SECRETS / "tokens.json"
PG_CRED_FILE = SECRETS / "pg_mcp_ro.password"
AUDIT_LOG = BASE / "logs" / "audit.jsonl"
HOST = os.environ.get("MCPGW_HOST", "127.0.0.1")
PORT = int(os.environ.get("MCPGW_PORT", "8765"))
ALLOWED_HOSTS = os.environ.get(
    "MCPGW_ALLOWED_HOSTS", "127.0.0.1:*,localhost:*"
).split(",")

ROOTS = {
    "projects": BASE / "projects",
    "bible-website": Path("/opt/bible/website"),
    "bible-data": Path("/opt/bible"),
}
REPOS = {
    "bible-project": BASE / "projects" / "bible-project",
    "BibleApp": BASE / "projects" / "BibleApp",
}
PG_DATABASES = [
    "bible",
    "bible_app",
    "bible_search_prod_20261111",
    "bible_search_stage_20261109",
    "bible_reconcile_20261111",
    "bible_hebrew_variant_shadow_20261107",
]
DENY_COMPONENT = re.compile(
    r"((^|\.)env($|\.)|\.envrc$|secret|credential|\.key$|\.pem$"
    r"|^id_(rsa|ed25519|toe)|\.password$|\.cred$|tokens\.json$)",
    re.IGNORECASE,
)
MAX_READ_BYTES = 256 * 1024
WRITE_ROOTS = {
    **ROOTS,
    "stage": Path("/opt/stage"),
    "bible-app-api": Path("/opt/bible-app-api"),
}
MAX_WRITE_BYTES = 1024 * 1024
# The distro ships no sudo: the privileged path is a setuid launcher
# (root:root 4755) that refuses every caller except mcpgw and execs the
# root-owned helper. See root_helper_launcher.c / root_helper.py.
ROOT_HELPER = "/usr/local/bin/mcpgw-root-helper"

# ---------------------------------------------------------------- LAMPY-CR-001
# Dedicated inbox tools for the Muse->GPT channel in the gpt-queue
# (Phase 6). The queue lives inside the existing "projects" root, so
# no new filesystem roots are needed. MCPGW_QUEUE_DIR exists as a
# testability hook only: it lets a development instance run against a
# scratch queue with zero production contact. The default is exactly
# the production layout.
QUEUE_DIR = Path(os.environ.get(
    "MCPGW_QUEUE_DIR", str(BASE / "projects" / "gpt-queue")))
INBOX_DIR = QUEUE_DIR / "inbox"
ACKS_DIR = INBOX_DIR / "acks"
OUTBOX_DIR = QUEUE_DIR / "outbox"
MESSAGE_TYPES = ("note", "question", "decision", "handoff", "blocker",
                 "urgent")
MESSAGE_ID_RE = re.compile(
    r"^\d{8}T\d{6}Z-(note|question|decision|handoff|blocker|urgent)"
    r"-[a-z0-9][a-z0-9-]{0,63}$")
SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")
TASK_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$")
ACK_STATES = ("read", "acted")  # forward-only: rank increases only
ACK_RANK = {state: rank for rank, state in enumerate(ACK_STATES, start=1)}


# ---------------------------------------------------------------- audit
def audit(event):
    event = {"ts": datetime.now(timezone.utc).isoformat(), **event}
    try:
        AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(AUDIT_LOG, "a") as f:
            f.write(json.dumps(event) + "\n")
    except OSError:
        pass


# ---------------------------------------------------------------- auth
def load_tokens():
    try:
        return json.loads(TOKEN_STORE.read_text()).get("tokens", [])
    except (OSError, json.JSONDecodeError):
        return []


def verify_token(presented):
    """Return the token record for a valid bearer token, else None."""
    if not presented or not presented.startswith("mcpgw1."):
        return None
    parts = presented.split(".")
    if len(parts) != 3:
        return None
    token_id, secret = parts[1], parts[2]
    digest = hashlib.sha256(secret.encode()).hexdigest()
    for rec in load_tokens():
        if rec.get("id") != token_id or rec.get("revoked"):
            continue
        if rec.get("expires") and rec["expires"] < time.time():
            continue
        if hmac.compare_digest(rec.get("sha256", ""), digest):
            return rec
    return None


PUBLIC_ORIGIN = os.environ.get(
    "MCPGW_PUBLIC_ORIGIN", "https://lampy.taila7a335.ts.net"
).rstrip("/")


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        if request.url.path.startswith(PUBLIC_PREFIXES):
            return await call_next(request)  # OAuth/well-known self-authenticate
        auth = request.headers.get("authorization", "")
        token = auth[7:] if auth.lower().startswith("bearer ") else ""
        rec = verify_token(token)
        if rec is None:
            audit({"kind": "auth_reject", "path": request.url.path})
            return JSONResponse(
                {"error": "unauthorized"}, status_code=401,
                headers={
                    "WWW-Authenticate": (
                        'Bearer resource_metadata="'
                        + PUBLIC_ORIGIN
                        + '/.well-known/oauth-protected-resource"'
                    )
                },
            )
        request.state.token_id = rec["id"]
        request.state.scopes = rec.get("scopes", [])
        if "read" not in request.state.scopes:
            return JSONResponse({"error": "insufficient scope"}, status_code=403)
        return await call_next(request)


# ---------------------------------------------------------------- helpers
def safe_path(root_name, subpath, roots=None):
    roots = ROOTS if roots is None else roots
    if root_name not in roots:
        raise ValueError(
            f"unknown root {root_name!r}; choose from {sorted(roots)}")
    root = roots[root_name].resolve()
    target = (root / subpath).resolve() if subpath else root
    if not target.is_relative_to(root):
        raise ValueError("path escapes the allowlisted root")
    rel_parts = target.relative_to(root).parts
    for part in rel_parts:
        if part == ".git" or DENY_COMPONENT.search(part):
            raise ValueError(f"path component denied: {part}")
    return target


def run_fixed(argv, cwd=None, timeout=25, max_lines=400):
    proc = subprocess.run(
        argv, cwd=cwd, capture_output=True, text=True, timeout=timeout
    )
    out = (proc.stdout or "").splitlines()
    err = (proc.stderr or "").strip()
    return {
        "exit_code": proc.returncode,
        "stdout": "\n".join(out[:max_lines]),
        "truncated": len(out) > max_lines,
        **({"stderr": err[:500]} if err else {}),
    }


def pg_connect(database):
    if database not in PG_DATABASES:
        raise ValueError(
            f"database {database!r} not allowlisted; choose from {PG_DATABASES}"
        )
    cred = PG_CRED_FILE.read_text().strip()
    return psycopg2.connect(
        host="127.0.0.1", dbname=database, user="mcp_ro", password=cred,
        connect_timeout=10,
    )


# ---------------------------------------------------------------- server
mcp = FastMCP(
    "lampy-bible-gateway",
    host=HOST,
    port=PORT,
    stateless_http=True,
    transport_security=TransportSecuritySettings(
        enable_dns_rebinding_protection=True,
        allowed_hosts=ALLOWED_HOSTS,
        allowed_origins=[f"http://{h}" for h in ALLOWED_HOSTS]
        + [f"https://{h}" for h in ALLOWED_HOSTS],
    ),
)
RO = {"readOnlyHint": True, "destructiveHint": False, "openWorldHint": False}


@mcp.tool(annotations=RO)
def fs_list(root: str, subpath: str = "") -> dict:
    """List a directory inside an allowlisted root.
    Roots: projects (gateway clones), bible-website, bible-data."""
    target = safe_path(root, subpath)
    if not target.is_dir():
        raise ValueError(f"not a directory: {subpath or '.'}")
    entries = []
    for p in sorted(target.iterdir())[:500]:
        entries.append(
            {
                "name": p.name,
                "type": "dir" if p.is_dir() else "file",
                **({"size": p.stat().st_size} if p.is_file() else {}),
            }
        )
    audit({"kind": "tool", "tool": "fs_list", "root": root, "subpath": subpath})
    return {"root": root, "subpath": subpath, "entries": entries}


@mcp.tool(annotations=RO)
def fs_read(root: str, subpath: str) -> str:
    """Read a UTF-8 text file (max 256 KB) inside an allowlisted root.
    Secret-shaped files (.env, keys, credential stores) are denied.

    Returns the file content as a plain string. (Changed 2026-11-12 from
    a {root, subpath, content} dict: ChatGPT's connector surfaced the
    structured result to the agent as an empty object {}, which blocked
    read-dependent workflows; plain text content is surfaced correctly.)"""
    target = safe_path(root, subpath)
    if not target.is_file():
        raise ValueError(f"not a file: {subpath}")
    if target.stat().st_size > MAX_READ_BYTES:
        raise ValueError("file larger than 256 KB read cap")
    try:
        text = target.read_bytes().decode("utf-8")
    except UnicodeDecodeError:
        raise ValueError("not a UTF-8 text file")
    audit({"kind": "tool", "tool": "fs_read", "root": root, "subpath": subpath})
    return text


def _denied_name(name):
    return name == ".git" or bool(DENY_COMPONENT.search(name))


def _searchable_files(base):
    """Yield the files under base that fs_read would be allowed to open:
    no denied path component (the same DENY_COMPONENT rule fs_read
    enforces), no .git, and no symlinks. This keeps the fs_search
    boundary identical to the fs_read boundary (finding F6)."""
    if os.path.isfile(base):
        yield str(base)
        return
    for dirpath, dirnames, filenames in os.walk(str(base)):
        dirnames[:] = sorted(
            d for d in dirnames
            if not _denied_name(d)
            and not os.path.islink(os.path.join(dirpath, d))
        )
        for name in sorted(filenames):
            if _denied_name(name):
                continue
            fpath = os.path.join(dirpath, name)
            if not os.path.islink(fpath):
                yield fpath


@mcp.tool(annotations=RO)
def fs_search(root: str, pattern: str, subpath: str = "") -> dict:
    """Search file contents (regex) under an allowlisted root.
    Returns at most 200 matching lines in grep -n format. Traversal
    applies exactly the fs_read denylist, so files fs_read would refuse
    (secret/credential/env/key material) are never searched."""
    target = safe_path(root, subpath)
    try:
        rx = re.compile(pattern)
    except re.error as e:
        raise ValueError(f"invalid regex: {e}")
    matches = []
    truncated = False
    for fpath in _searchable_files(target):
        try:
            if os.path.getsize(fpath) > 1024 * 1024:
                continue
            with open(fpath, "rb") as f:
                raw = f.read()
        except OSError:
            continue
        if b"\x00" in raw[:8192]:
            continue  # binary file, like grep -I
        text = raw.decode("utf-8", errors="replace")
        for lineno, line in enumerate(text.splitlines(), 1):
            if rx.search(line):
                matches.append(f"{fpath}:{lineno}:{line[:1000]}")
                if len(matches) >= 200:
                    truncated = True
                    break
        if truncated:
            break
    audit({"kind": "tool", "tool": "fs_search", "root": root})
    return {"root": root, "subpath": subpath,
            "matches": "\n".join(matches), "truncated": truncated}


def _repo_path(repo):
    if repo not in REPOS:
        raise ValueError(f"unknown repo {repo!r}; choose from {sorted(REPOS)}")
    return REPOS[repo]


@mcp.tool(annotations=RO)
def git_status(repo: str) -> dict:
    """Working-tree status and HEAD of a gateway repo clone
    (bible-project or BibleApp)."""
    path = _repo_path(repo)
    res = run_fixed(["git", "status", "--porcelain=v1", "--branch"], cwd=path)
    audit({"kind": "tool", "tool": "git_status", "repo": repo})
    return {"repo": repo, **res}


@mcp.tool(annotations=RO)
def git_log(repo: str, count: int = 20) -> dict:
    """Recent commit log of a gateway repo clone."""
    path = _repo_path(repo)
    count = max(1, min(int(count), 100))
    res = run_fixed(
        ["git", "log", f"-{count}", "--oneline", "--decorate"], cwd=path
    )
    audit({"kind": "tool", "tool": "git_log", "repo": repo})
    return {"repo": repo, **res}


@mcp.tool(annotations=RO)
def git_branches(repo: str) -> dict:
    """Local and remote branches of a gateway repo clone."""
    path = _repo_path(repo)
    res = run_fixed(["git", "branch", "-a"], cwd=path)
    audit({"kind": "tool", "tool": "git_branches", "repo": repo})
    return {"repo": repo, **res}


def _resolve_ref(path, ref):
    """Resolve a user-supplied ref to a verified commit SHA, or raise.
    Refs are never passed to git unresolved: a leading-dash ref would be
    parsed by git as an option (e.g. --output writes a file), so the
    only values that ever reach a git command line are hex SHAs
    (finding F7)."""
    if not ref or ref.startswith("-") or \
            not re.fullmatch(r"[A-Za-z0-9._/\-^~]+", ref):
        raise ValueError(f"suspicious ref: {ref!r}")
    res = run_fixed(
        ["git", "rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}"],
        cwd=path,
    )
    sha = (res["stdout"] or "").strip()
    if res["exit_code"] != 0 or not re.fullmatch(r"[0-9a-f]{40}", sha):
        raise ValueError(f"unresolvable ref: {ref!r}")
    return sha


def _resolve_diff_spec(path, ref_a, ref_b):
    if ref_b:
        return [_resolve_ref(path, ref_a), _resolve_ref(path, ref_b)]
    if "..." in ref_a:
        a, _, b = ref_a.partition("...")
        return [f"{_resolve_ref(path, a)}...{_resolve_ref(path, b)}"]
    if ".." in ref_a:
        a, _, b = ref_a.partition("..")
        return [f"{_resolve_ref(path, a)}..{_resolve_ref(path, b)}"]
    return [_resolve_ref(path, ref_a)]


@mcp.tool(annotations=RO)
def git_diff(repo: str, ref_a: str = "HEAD", ref_b: str = "") -> dict:
    """Diff of a gateway repo clone: ref_a..ref_b, or working tree vs ref_a
    when ref_b is empty. Output capped at 400 lines. Refs are resolved to
    commit SHAs before use (see _resolve_ref)."""
    path = _repo_path(repo)
    argv = ["git", "diff", "--stat"] + _resolve_diff_spec(path, ref_a, ref_b)
    res = run_fixed(argv, cwd=path)
    audit({"kind": "tool", "tool": "git_diff", "repo": repo})
    return {"repo": repo, **res}


@mcp.tool(annotations=RO)
def pg_databases() -> dict:
    """The allowlisted PostgreSQL databases, each with a live connection
    check and public-schema table count. The database is always chosen
    explicitly by name - never substituted."""
    out = []
    for db in PG_DATABASES:
        try:
            conn = pg_connect(db)
            cur = conn.cursor()
            cur.execute(
                "SELECT count(*) FROM information_schema.tables "
                "WHERE table_schema = 'public'"
            )
            out.append({"database": db, "reachable": True,
                        "public_tables": cur.fetchone()[0]})
            conn.close()
        except Exception as e:  # noqa: BLE001 - report, never hide
            out.append({"database": db, "reachable": False,
                        "error": str(e)[:200]})
    audit({"kind": "tool", "tool": "pg_databases"})
    return {"databases": out}


@mcp.tool(annotations=RO)
def pg_schema(database: str, table: str = "") -> dict:
    """Column listing for the public schema of an allowlisted database
    (one table when `table` is given)."""
    conn = pg_connect(database)
    cur = conn.cursor()
    if table:
        cur.execute(
            "SELECT column_name, data_type, is_nullable FROM "
            "information_schema.columns WHERE table_schema='public' AND "
            "table_name=%s ORDER BY ordinal_position", (table,),
        )
    else:
        cur.execute(
            "SELECT table_name, column_name, data_type, is_nullable FROM "
            "information_schema.columns WHERE table_schema='public' "
            "ORDER BY table_name, ordinal_position LIMIT 1000"
        )
    rows = [list(map(str, r)) for r in cur.fetchall()]
    conn.close()
    audit({"kind": "tool", "tool": "pg_schema", "database": database})
    return {"database": database, "table": table or None, "columns": rows}


SQL_FORBIDDEN = re.compile(
    r"\b(insert|update|delete|drop|alter|create|grant|revoke|truncate|copy|"
    r"vacuum|analyze|call|do|merge|replace|lock|comment|reindex|cluster|"
    r"refresh|security|definer)\b",
    re.IGNORECASE,
)


@mcp.tool(annotations=RO)
def pg_query(database: str, sql: str) -> dict:
    """Run ONE read-only SELECT/WITH query against an explicitly named
    allowlisted database. Writes are refused three ways: this filter,
    the read-only transaction default, and the mcp_ro role's grants.
    Rows capped at 200."""
    stmt = sql.strip().rstrip(";").strip()
    if ";" in stmt:
        raise ValueError("a single statement only (no semicolons)")
    if not re.match(r"(?is)^(select|with)\b", stmt):
        raise ValueError("only SELECT / WITH queries are permitted")
    if SQL_FORBIDDEN.search(stmt):
        raise ValueError("statement contains a forbidden keyword")
    conn = pg_connect(database)
    try:
        cur = conn.cursor()
        cur.execute(stmt)
        cols = [d[0] for d in cur.description] if cur.description else []
        rows = [
            [None if v is None else str(v) for v in row]
            for row in cur.fetchmany(200)
        ]
        return {"database": database, "columns": cols, "rows": rows,
                "row_count": len(rows), "capped": len(rows) == 200}
    finally:
        conn.rollback()
        conn.close()
        audit({"kind": "tool", "tool": "pg_query", "database": database})


@mcp.tool(annotations=RO)
def svc_probe() -> dict:
    """Availability probes for the Lampy service estate: TCP reachability
    of the fixed service ports plus three HTTP checks. (Supervisor's own
    socket is root-only by design, so this tool probes, it does not ask
    supervisor.)"""
    ports = {
        "flask_prod": 5057, "flask_staging": 5058, "express_prod": 8799,
        "express_staging": 8798, "postgres": 5432, "ollama": 11434,
        "apache": 80,
    }
    tcp = {}
    for name, port in ports.items():
        s = socket.socket()
        s.settimeout(2)
        try:
            s.connect(("127.0.0.1", port))
            tcp[name] = "open"
        except OSError:
            tcp[name] = "closed"
        finally:
            s.close()

    def http(url):
        try:
            with urllib.request.urlopen(url, timeout=5) as r:
                return r.status
        except urllib.error.HTTPError as e:
            return e.code
        except Exception:  # noqa: BLE001
            return None

    audit({"kind": "tool", "tool": "svc_probe"})
    return {
        "tcp": tcp,
        "http": {
            "flask_prod_books": http("http://127.0.0.1:5057/api/books"),
            "flask_staging_books": http("http://127.0.0.1:5058/api/books"),
            "express_prod_variant_noauth": http(
                "http://127.0.0.1:8799/api/lexicon/hebrew-vowel-variants/"
                "by-word/238432"
            ),
        },
    }


# ---------------------------------------------------------------- Phase 5
# Write + execution tools. These exist so the connected agent can do real
# work in the Lampy environment through this gateway - edit code, run the
# project's test suites, administer services - instead of through a
# separate remote-desktop tunnel. They require the "write" scope on the
# caller's token; the read tools above never do. File operations stay
# inside WRITE_ROOTS under the same denylist as reads; execution is
# delegated to a root helper reachable from this process only through a
# setuid launcher that accepts no caller but mcpgw.
WR = {"readOnlyHint": False, "destructiveHint": True, "openWorldHint": False}


def _current_scopes():
    """Scopes of the token on the in-flight request, as the
    AuthMiddleware recorded them. Fail closed: no context, no scopes."""
    try:
        request = mcp.get_context().request_context.request
        return list(getattr(request.state, "scopes", []) or [])
    except Exception:  # noqa: BLE001 - fail closed on any doubt
        return []


def _require_write():
    scopes = _current_scopes()
    if "write" not in scopes:
        raise ValueError(
            "this tool requires the 'write' scope "
            f"(token scopes: {scopes or 'none'})"
        )


def _current_token_id():
    """Id of the token on the in-flight request, as the AuthMiddleware
    recorded it. This is the strongest caller identity the gateway has:
    token-grade, not a cryptographic agent identity. None when there is
    no request context."""
    try:
        request = mcp.get_context().request_context.request
        return getattr(request.state, "token_id", None)
    except Exception:  # noqa: BLE001 - no context, no identity
        return None


def _root_helper(req, timeout=40):
    proc = subprocess.run(
        [ROOT_HELPER],
        input=json.dumps(req), capture_output=True, text=True,
        timeout=timeout,
    )
    if proc.returncode != 0:
        raise ValueError(
            f"root helper failed (exit {proc.returncode}): "
            f"{(proc.stderr or '').strip()[:300]}"
        )
    try:
        res = json.loads(proc.stdout)
    except json.JSONDecodeError:
        raise ValueError("root helper returned unparseable output")
    if not res.get("ok"):
        raise ValueError(res.get("error", "root helper error"))
    return res


@mcp.tool(annotations=WR)
async def fs_write(root: str, subpath: str, content: str) -> dict:
    """Create or overwrite a UTF-8 text file inside a writable root
    (projects, bible-website, bible-data, stage, bible-app-api), making
    parent directories as needed. Max 1 MB. Secret-shaped paths are
    denied by the same rule as reads. Requires the 'write' scope."""
    _require_write()
    safe_path(root, subpath, roots=WRITE_ROOTS)
    data = content.encode("utf-8")
    if len(data) > MAX_WRITE_BYTES:
        raise ValueError("content larger than the 1 MB write cap")
    res = await asyncio.to_thread(
        _root_helper,
        {"op": "write", "root": root, "subpath": subpath,
         "content_b64": base64.b64encode(data).decode()},
    )
    audit({"kind": "tool", "tool": "fs_write", "root": root,
           "subpath": subpath, "bytes": res["bytes"]})
    return {"root": root, "subpath": subpath, "bytes": res["bytes"],
            "path": res["path"]}


@mcp.tool(annotations=WR)
async def fs_edit(root: str, subpath: str, old: str, new: str) -> dict:
    """Replace the single occurrence of `old` with `new` in a text file
    inside a writable root. Refuses when `old` occurs zero times or more
    than once, so an edit can never land ambiguously. Requires the
    'write' scope."""
    _require_write()
    safe_path(root, subpath, roots=WRITE_ROOTS)
    if not old:
        raise ValueError("old must be non-empty")
    if len(new.encode("utf-8")) > MAX_WRITE_BYTES:
        raise ValueError("replacement larger than the 1 MB write cap")
    res = await asyncio.to_thread(
        _root_helper,
        {"op": "edit", "root": root, "subpath": subpath,
         "old": old, "new": new},
    )
    audit({"kind": "tool", "tool": "fs_edit", "root": root,
           "subpath": subpath})
    return {"root": root, "subpath": subpath, "bytes": res["bytes"],
            "path": res["path"]}


@mcp.tool(annotations=WR)
async def exec_run(command: str, cwd_root: str = "projects",
                   cwd_subpath: str = "",
                   timeout_seconds: int = 120) -> dict:
    """Run a shell command (bash) as root on Lampy, in a working
    directory inside a writable root (default: the projects root).
    This is the gateway's general-access path: run the project's test
    suites, build, restart services, inspect anything the read tools
    cannot reach. Output is capped; the command and its exit code are
    audit-logged. Requires the 'write' scope."""
    _require_write()
    if not command or not command.strip():
        raise ValueError("command must be non-empty")
    if len(command) > 20000:
        raise ValueError("command larger than the 20 KB cap")
    safe_path(cwd_root, cwd_subpath, roots=WRITE_ROOTS)
    timeout = max(5, min(int(timeout_seconds), 600))
    res = await asyncio.to_thread(
        _root_helper,
        {"op": "exec", "command": command, "cwd_root": cwd_root,
         "cwd_subpath": cwd_subpath, "timeout": timeout},
        timeout + 30,
    )
    audit({"kind": "tool", "tool": "exec_run", "command": command[:300],
           "cwd_root": cwd_root, "cwd_subpath": cwd_subpath,
           "exit_code": res["exit_code"]})
    return {
        "exit_code": res["exit_code"], "timed_out": res["timed_out"],
        "stdout": res["stdout"], "stderr": res["stderr"],
        "stdout_truncated": res["stdout_truncated"],
        "stderr_truncated": res["stderr_truncated"], "cwd": res["cwd"],
    }


# ---------------------------------------------------------------- Phase 6
# LAMPY-CR-001: dedicated messaging tools for the Muse->GPT inbox in
# the gpt-queue, so the connected agent can discover, read, acknowledge
# and answer channel messages with single calls instead of sequences of
# generic fs calls. Message files are append-only and their contents
# are data: stored and returned verbatim, never executed or
# interpreted. State (written-not-received / read / acted) is derived
# from the message and ack files on every call - there is no cached
# state to corrupt, and duplicate calls cannot create duplicate
# records. Caller-supplied ids are validated against a strict pattern
# before any path is built from them.

def _iso_z(dt):
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _parse_header(text):
    """Parse a channel header block: 'key: value' lines up to the first
    blank line. Returns (header dict, body). Raises ValueError on any
    structural problem."""
    lines = text.split("\n")
    header = {}
    for i, line in enumerate(lines):
        if line.strip() == "":
            return header, "\n".join(lines[i + 1:])
        if ":" not in line:
            raise ValueError(f"header line {i + 1} is not 'key: value'")
        key, _, value = line.partition(":")
        header[key.strip()] = value.strip()
    raise ValueError("no blank line separating header from body")


def _parse_message_file(path, stem):
    """Validate one inbox message file. Returns (message dict, None) or
    (None, reason). The dict carries header fields plus body; ack state
    is attached by the caller."""
    try:
        if path.stat().st_size > MAX_READ_BYTES:
            return None, f"larger than the {MAX_READ_BYTES} byte read cap"
        text = path.read_bytes().decode("utf-8")
    except UnicodeDecodeError:
        return None, "not UTF-8 text"
    except OSError as e:
        return None, f"unreadable: {e.strerror or e}"
    try:
        header, body = _parse_header(text)
    except ValueError as e:
        return None, str(e)
    for key in ("id", "from", "to", "type", "task", "created"):
        if key not in header:
            return None, f"missing header field: {key}"
    if header["id"] != stem:
        return None, "header id does not match filename"
    if header["type"] != stem.split("-")[1]:
        return None, "header type does not match filename"
    try:
        datetime.strptime(header["created"], "%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        return None, "unparseable created timestamp"
    return {
        "id": header["id"], "from": header["from"], "to": header["to"],
        "type": header["type"], "task": header["task"],
        "created": header["created"], "body": body,
    }, None


def _ack_state(message_id):
    """(state, header, problem) for a message's ack file: state is
    'read' / 'acted' / None (no valid ack). A malformed ack yields
    state None plus a problem description - the message then counts as
    unacknowledged, the conservative state."""
    path = ACKS_DIR / f"{message_id}.ack.md"
    if not path.is_file():
        return None, None, None
    try:
        header, _ = _parse_header(path.read_bytes().decode("utf-8"))
    except (OSError, UnicodeDecodeError, ValueError) as e:
        return None, None, f"unparseable ack: {e}"
    if header.get("id") != message_id:
        return None, None, "ack header id does not match filename"
    if header.get("state") not in ACK_STATES:
        return None, None, f"ack state {header.get('state')!r} is not valid"
    return header["state"], header, None


def _scan_inbox():
    """(messages, malformed) for INBOX_DIR: every valid message with its
    derived ack state attached, sorted by id; malformed .md candidates
    listed by name with a reason. LEDGER.md and README.md are the
    channel's own furniture (the convention Muse's helper uses) and
    non-.md leftovers are not message candidates here - diagnostics
    reports those separately. Never raises on bad content."""
    messages, malformed = [], []
    if not INBOX_DIR.is_dir():
        return messages, malformed
    for p in sorted(INBOX_DIR.iterdir()):
        if not p.is_file() or p.name in ("LEDGER.md", "README.md"):
            continue
        if not p.name.endswith(".md"):
            continue
        stem = p.name[:-3]
        if not MESSAGE_ID_RE.fullmatch(stem):
            malformed.append({"name": p.name,
                              "reason": "filename is not a valid message id"})
            continue
        msg, reason = _parse_message_file(p, stem)
        if msg is None:
            malformed.append({"name": p.name, "reason": reason})
            continue
        state, _, _ = _ack_state(stem)
        msg["ack_state"] = state
        messages.append(msg)
    return messages, malformed


def _load_message(message_id):
    """Parse and validate one inbox message by id, distinguishing an
    invalid id, an unknown id, and a malformed file."""
    if not MESSAGE_ID_RE.fullmatch(message_id or ""):
        raise ValueError(f"invalid message id: {message_id!r}")
    path = INBOX_DIR / f"{message_id}.md"
    if not path.is_file():
        raise ValueError(f"unknown message id: {message_id}")
    msg, reason = _parse_message_file(path, message_id)
    if msg is None:
        raise ValueError(f"message {message_id} is malformed: {reason}")
    return msg


@mcp.tool(annotations=RO)
def inbox_status() -> dict:
    """Check the Muse->GPT inbox (gpt-queue/inbox): how many messages
    are unread, which one is next, and whether any unread message is
    urgent. State is derived from the message and acknowledgement
    files on every call. Malformed files are listed by name and
    excluded from the counts - never silently dropped, never a crash."""
    messages, malformed = _scan_inbox()
    unread = [m for m in messages if m["ack_state"] is None]
    audit({"kind": "tool", "tool": "inbox_status",
           "unread": len(unread)})
    return {
        "unread_count": len(unread),
        "unread_ids": [m["id"] for m in unread],
        "oldest_unread_created": unread[0]["created"] if unread else None,
        "urgent_unread": [m["id"] for m in unread if m["type"] == "urgent"],
        "next_unread_id": unread[0]["id"] if unread else None,
        "read_count": sum(1 for m in messages if m["ack_state"] == "read"),
        "acted_count": sum(1 for m in messages if m["ack_state"] == "acted"),
        "malformed": malformed,
    }


@mcp.tool(annotations=RO)
def inbox_read(message_id: str) -> dict:
    """Read exactly one Muse->GPT inbox message by its id: the full
    header (sender, recipient, type, related task, timestamp), the
    complete body, and its acknowledgement state
    (written-not-received / read / acted). Unknown or invalid ids are
    refused with a precise error - never a directory dump."""
    msg = _load_message(message_id)
    state, _, _ = _ack_state(message_id)
    audit({"kind": "tool", "tool": "inbox_read", "id": message_id})
    return {**msg, "ack_state": state or "written-not-received"}


@mcp.tool(annotations=WR)
def inbox_ack(message_id: str, state: str) -> dict:
    """Acknowledge one inbox message: record that you have read it
    (state "read"), or that you have acted on it (state "acted").
    Idempotent and forward-only: if an acknowledgement at the same or
    a later state already exists it is returned unchanged, and state
    can never move backwards, so duplicate calls cannot corrupt the
    record. The original message is never modified. The ack records
    your token id as the agent identity. Requires the 'write' scope."""
    _require_write()
    if state not in ACK_STATES:
        raise ValueError(f"state must be one of {list(ACK_STATES)}")
    _load_message(message_id)  # must exist and be well-formed
    existing, hdr, _ = _ack_state(message_id)
    if existing is not None and ACK_RANK[existing] >= ACK_RANK[state]:
        audit({"kind": "tool", "tool": "inbox_ack", "id": message_id,
               "state": existing, "updated": False})
        return {"id": message_id, "state": existing,
                "created": hdr.get("created"),
                "agent": hdr.get("agent", "unknown"), "updated": False}
    agent = _current_token_id() or "gpt"
    created = _iso_z(datetime.now(timezone.utc))
    content = (
        f"id: {message_id}\nstate: {state}\ncreated: {created}\n"
        f"agent: {agent}\n\n"
        "Acknowledged via the Lampy plugin inbox_ack tool.\n"
    )
    tmp = ACKS_DIR / f".{message_id}.ack.{os.getpid()}.tmp"
    try:
        ACKS_DIR.mkdir(parents=True, exist_ok=True)
        with open(tmp, "w") as f:
            f.write(content)
        os.replace(tmp, ACKS_DIR / f"{message_id}.ack.md")
    except OSError as e:
        try:
            tmp.unlink()
        except OSError:
            pass
        raise ValueError(
            f"cannot write ack for {message_id}: {e.strerror or e} "
            f"(acks dir: {ACKS_DIR})")
    audit({"kind": "tool", "tool": "inbox_ack", "id": message_id,
           "state": state, "updated": True})
    return {"id": message_id, "state": state, "created": created,
            "agent": agent, "updated": True}


@mcp.tool(annotations=WR)
def inbox_send(type: str, slug: str, body: str, task: str = "none") -> dict:
    """Send a message to Muse by publishing it to the GPT->Muse
    outbox (gpt-queue/outbox) in the channel's established format.
    `type` is one of note / question / decision / handoff / blocker /
    urgent; `slug` is a short lowercase-dash label; `task` is the
    related queue task id or "none". The message id is composed from
    the UTC time with microsecond precision. Publication is atomic
    and append-only: an existing message is never overwritten.
    Fails closed if the outbox is not writable. Requires the
    'write' scope."""
    _require_write()
    if type not in MESSAGE_TYPES:
        raise ValueError(
            f"type must be one of {list(MESSAGE_TYPES)}, got {type!r}")
    if not SLUG_RE.fullmatch(slug or ""):
        raise ValueError(
            f"invalid slug {slug!r}: lowercase letters, digits and "
            "dashes, starting with a letter or digit, max 64 chars")
    if not TASK_RE.fullmatch(task or ""):
        raise ValueError(f"invalid task {task!r}")
    if not body:
        raise ValueError("body must be non-empty")
    if len(body.encode("utf-8")) > MAX_WRITE_BYTES:
        raise ValueError("body larger than the 1 MB write cap")
    if not OUTBOX_DIR.is_dir():
        raise ValueError(f"outbox directory does not exist: {OUTBOX_DIR}")
    now = datetime.now(timezone.utc)
    message_id = (f"{now.strftime('%Y%m%dT%H%M%S')}"
                  f"{now.microsecond:06d}Z-{type}-{slug}")
    content = (
        f"id: {message_id}\nfrom: gpt\nto: claude\ntype: {type}\n"
        f"task: {task}\ncreated: {_iso_z(now)}\n\n{body}"
    )
    if not content.endswith("\n"):
        content += "\n"
    final = OUTBOX_DIR / f"{message_id}.md"
    tmp = OUTBOX_DIR / f".{message_id}.{os.getpid()}.tmp"
    try:
        fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
        with os.fdopen(fd, "w") as f:
            f.write(content)
        # Atomic publish that can never overwrite an existing message:
        # link(2) fails with FileExistsError if the final name is taken.
        os.link(tmp, final)
    except FileExistsError:
        raise ValueError(
            "message id already exists (append-only, refusing to "
            f"overwrite): {message_id}")
    except OSError as e:
        raise ValueError(
            f"cannot publish message to outbox {OUTBOX_DIR}: "
            f"{e.strerror or e}")
    finally:
        try:
            tmp.unlink()
        except OSError:
            pass
    audit({"kind": "tool", "tool": "inbox_send", "id": message_id,
           "type": type, "task": task})
    return {"id": message_id, "path": str(final)}


def _writable_by_bits(path):
    """Mode-bit writability for the effective uid. os.access alone
    answers True for every directory when the process runs as root,
    which would hide exactly the ownership problem diagnostics exists
    to surface."""
    st = path.stat()
    if os.geteuid() == 0:
        return True
    if st.st_uid == os.geteuid():
        return bool(st.st_mode & 0o200)
    if st.st_gid == os.getegid() or st.st_gid in os.getgroups():
        return bool(st.st_mode & 0o020)
    return bool(st.st_mode & 0o002)


def _dir_check(path):
    """Three-valued accessibility check for one queue directory. A
    'failed' here is a verified fact about the directory, reported
    with its reason - not a tool error."""
    if not path.exists():
        return {"status": "failed", "exists": False, "readable": False,
                "writable": False,
                "reason": f"directory does not exist: {path}"}
    if not path.is_dir():
        return {"status": "failed", "exists": True, "readable": False,
                "writable": False,
                "reason": f"path exists but is not a directory: {path}"}
    readable = os.access(path, os.R_OK)
    writable = os.access(path, os.W_OK) and _writable_by_bits(path)
    out = {"status": "ok" if (readable and writable) else "failed",
           "exists": True, "readable": readable, "writable": writable}
    if not writable:
        st = path.stat()
        out["reason"] = (
            f"not writable by the gateway process (effective uid "
            f"{os.geteuid()}): directory owned by uid {st.st_uid}, "
            f"mode {oct(st.st_mode & 0o777)}")
    elif not readable:
        out["reason"] = "not readable by the gateway process"
    return out


def _message_census():
    """Message census for diagnostics: valid total, every malformed or
    leftover file with its reason (including acks-dir problems and
    non-message leftovers such as interrupted-write temp files),
    duplicate header ids, and messages unacknowledged for over 24h."""
    messages, malformed = _scan_inbox()
    issues = list(malformed)
    known_stems = {m["id"] for m in messages}
    known_stems |= {e["name"][:-3] for e in malformed
                    if e["name"].endswith(".md")}
    if INBOX_DIR.is_dir():
        for p in sorted(INBOX_DIR.iterdir()):
            if p.is_file() and not p.name.endswith(".md"):
                issues.append({
                    "name": p.name,
                    "reason": "leftover non-message file "
                              "(possible interrupted write)"})
    if ACKS_DIR.is_dir():
        for p in sorted(ACKS_DIR.iterdir()):
            if not p.is_file():
                continue
            if not p.name.endswith(".ack.md"):
                issues.append({
                    "name": f"acks/{p.name}",
                    "reason": "leftover non-ack file in the acks dir "
                              "(possible interrupted write)"})
                continue
            mid = p.name[:-len(".ack.md")]
            _, _, problem = _ack_state(mid)
            if problem:
                issues.append({"name": f"acks/{p.name}",
                               "reason": f"malformed ack: {problem}"})
            elif mid not in known_stems:
                issues.append({
                    "name": f"acks/{p.name}",
                    "reason": "ack references a message that does "
                              "not exist"})
    counts = {}
    if INBOX_DIR.is_dir():
        for p in sorted(INBOX_DIR.iterdir()):
            if not p.is_file() or not p.name.endswith(".md"):
                continue
            if p.name in ("LEDGER.md", "README.md"):
                continue
            try:
                header, _ = _parse_header(
                    p.read_bytes().decode("utf-8"))
            except Exception:  # noqa: BLE001 - census only
                continue
            if header.get("id"):
                counts[header["id"]] = counts.get(header["id"], 0) + 1
    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
    unacked_old = []
    for m in messages:
        if m["ack_state"] is not None:
            continue
        try:
            ts = datetime.strptime(
                m["id"][:8] + m["id"][9:15], "%Y%m%d%H%M%S"
            ).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
        if ts < cutoff:
            unacked_old.append(m["id"])
    return {
        "total": len(messages),
        "malformed": issues,
        "duplicate_ids": sorted(k for k, v in counts.items() if v > 1),
        "unacked_older_than_24h": unacked_old,
    }


def _audit_log_check():
    """Audit log presence plus the most recent gateway_start in its
    tail. Existence and timestamps only - no event contents."""
    out = {"present": AUDIT_LOG.is_file(), "last_gateway_start": None}
    if out["present"]:
        try:
            with open(AUDIT_LOG, "rb") as f:
                f.seek(0, os.SEEK_END)
                f.seek(max(0, f.tell() - 262144))
                tail = f.read().decode("utf-8", errors="replace")
            for line in tail.splitlines():
                try:
                    ev = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if ev.get("kind") == "gateway_start":
                    out["last_gateway_start"] = ev.get("ts")
        except OSError:
            out["present"] = False
    out["status"] = "ok" if out["present"] else "failed"
    if not out["present"]:
        out["reason"] = f"audit log not found: {AUDIT_LOG}"
    return out


@mcp.tool(annotations=RO)
def inbox_diagnostics() -> dict:
    """Health report for the Muse->GPT channel, from the gateway's
    own vantage point: the inbox, acks and outbox directories
    (existence, readability, writability - with the ownership reason
    when a check fails), a message census (malformed files with
    reasons, duplicate ids, messages unacknowledged for over 24
    hours), the audit log's presence and last gateway start, and the
    token store's presence. Checks are three-valued (ok / failed /
    unknown): a failed check is a verified fact, and what the
    gateway cannot observe - the Claude-side watcher and relay,
    which run off this machine - is reported unknown, never guessed."""
    audit({"kind": "tool", "tool": "inbox_diagnostics"})
    return {
        "queue_dir": str(QUEUE_DIR),
        "inbox_dir": _dir_check(INBOX_DIR),
        "acks_dir": _dir_check(ACKS_DIR),
        "outbox_dir": _dir_check(OUTBOX_DIR),
        "message_census": _message_census(),
        "audit_log": _audit_log_check(),
        "token_store": {
            "status": "ok" if TOKEN_STORE.is_file() else "failed",
            "present": TOKEN_STORE.is_file(),
        },
        "watcher_relay_health": {
            "status": "unknown",
            "reason": "the Claude-side watcher runs off-gateway and "
                      "is not observable from here",
        },
    }


def main():
    import uvicorn

    app = mcp.streamable_http_app()
    mount_oauth(app)
    app.add_middleware(AuthMiddleware)
    audit({"kind": "gateway_start", "host": HOST, "port": PORT})
    uvicorn.run(app, host=HOST, port=PORT, log_level="warning")


if __name__ == "__main__":
    main()
