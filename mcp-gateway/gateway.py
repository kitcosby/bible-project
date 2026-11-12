#!/usr/bin/env python3
"""Lampy MCP gateway - Phase 2 (local, read-only).

Serves a Streamable HTTP MCP endpoint on 127.0.0.1 only, authenticated by
opaque bearer tokens from a local token store (hashed, scoped, revocable).
Every tool is read-only. All calls are audit-logged without secrets.

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
from datetime import datetime, timezone
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
def safe_path(root_name, subpath):
    if root_name not in ROOTS:
        raise ValueError(f"unknown root {root_name!r}; choose from {sorted(ROOTS)}")
    root = ROOTS[root_name].resolve()
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
def fs_read(root: str, subpath: str) -> dict:
    """Read a UTF-8 text file (max 256 KB) inside an allowlisted root.
    Secret-shaped files (.env, keys, credential stores) are denied."""
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
    return {"root": root, "subpath": subpath, "content": text}


@mcp.tool(annotations=RO)
def fs_search(root: str, pattern: str, subpath: str = "") -> dict:
    """Search file contents (regex) under an allowlisted root.
    Returns at most 200 matching lines; .git and denied names excluded."""
    target = safe_path(root, subpath)
    res = run_fixed(
        [
            "grep", "-rInE", "--exclude-dir=.git", "--exclude=*.env",
            "--exclude=tokens.json", "--", pattern, str(target),
        ],
        timeout=30, max_lines=200,
    )
    audit({"kind": "tool", "tool": "fs_search", "root": root})
    return {"root": root, "subpath": subpath, "matches": res["stdout"],
            "truncated": res["truncated"]}


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


@mcp.tool(annotations=RO)
def git_diff(repo: str, ref_a: str = "HEAD", ref_b: str = "") -> dict:
    """Diff of a gateway repo clone: ref_a..ref_b, or working tree vs ref_a
    when ref_b is empty. Output capped at 400 lines."""
    path = _repo_path(repo)
    for ref in (ref_a, ref_b):
        if ref and not re.fullmatch(r"[A-Za-z0-9._/\-^~]+", ref):
            raise ValueError(f"suspicious ref: {ref!r}")
    argv = ["git", "diff", "--stat", ref_a] + ([ref_b] if ref_b else [])
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


def main():
    import uvicorn

    app = mcp.streamable_http_app()
    mount_oauth(app)
    app.add_middleware(AuthMiddleware)
    audit({"kind": "gateway_start", "host": HOST, "port": PORT})
    uvicorn.run(app, host=HOST, port=PORT, log_level="warning")


if __name__ == "__main__":
    main()
