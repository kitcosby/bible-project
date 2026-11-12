#!/usr/bin/env python3
"""Minimal single-user OAuth 2.1 authorization server for the MCP gateway.

Implements exactly what ChatGPT's MCP client needs (MCP authorization
profile): protected-resource metadata, authorization-server metadata,
dynamic client registration, authorization-code flow with PKCE (S256),
and rotating refresh tokens (offline_access).

Owner consent is OUT OF BAND: /oauth/authorize creates a pending request;
the owner approves it with gw_admin.py (approve <id>) over the existing
authenticated channel. No password database exists anywhere in this
design. Access tokens are issued into the gateway's existing token store
(../secrets/tokens.json), so the gateway's verifier never changes.
"""
import base64
import hashlib
import hmac
import json
import os
import secrets
import threading
import time
from pathlib import Path

from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse, RedirectResponse
from starlette.routing import Route

SECRETS = Path("/home/mcpgw/secrets")
CLIENTS_FILE = SECRETS / "oauth_clients.json"
PENDING_FILE = SECRETS / "oauth_pending.json"
CODES_FILE = SECRETS / "oauth_codes.json"
REFRESH_FILE = SECRETS / "oauth_refresh.json"
TOKENS_FILE = SECRETS / "tokens.json"
ORIGIN = os.environ.get(
    "MCPGW_PUBLIC_ORIGIN", "https://lampy.taila7a335.ts.net"
).rstrip("/")
RESOURCE = ORIGIN + "/mcp"
SCOPES = ["read", "offline_access"]
LOCK = threading.Lock()
REQ_ALPHABET = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"


# ------------------------------------------------------------------ store
def _load(path, key):
    try:
        return json.loads(path.read_text()).get(key, {})
    except (OSError, json.JSONDecodeError):
        return {}


def _save(path, key, data):
    path.write_text(json.dumps({key: data}, indent=2))
    path.chmod(0o600)


def _sha(text):
    return hashlib.sha256(text.encode()).hexdigest()


# ------------------------------------------------------------------ tokens
def issue_access_token(client_label, expires_in=3600):
    secret = secrets.token_urlsafe(32)
    token_id = secrets.token_hex(4)
    with LOCK:
        try:
            data = json.loads(TOKENS_FILE.read_text())
        except (OSError, json.JSONDecodeError):
            data = {"tokens": []}
        data["tokens"].append(
            {
                "id": token_id,
                "label": client_label,
                "sha256": _sha(secret),
                "scopes": ["read"],
                "created": int(time.time()),
                "expires": int(time.time()) + expires_in,
                "revoked": False,
            }
        )
        _save(TOKENS_FILE, "tokens", data["tokens"])
    return f"mcpgw1.{token_id}.{secret}"


def issue_refresh_token(client_id, scope):
    plaintext = "mcpgwr1." + secrets.token_urlsafe(40)
    with LOCK:
        store = _load(REFRESH_FILE, "tokens")
        store[_sha(plaintext)] = {
            "client_id": client_id,
            "scope": scope,
            "created": int(time.time()),
            "revoked": False,
        }
        _save(REFRESH_FILE, "tokens", store)
    return plaintext


# ------------------------------------------------------------------ pages
def _page(title, body):
    return (
        "<!doctype html><meta charset=utf-8><title>" + title + "</title>"
        "<body style='font-family:system-ui;max-width:34em;margin:3em auto;"
        "padding:0 1em'><h2>" + title + "</h2>" + body + "</body>"
    )


# ------------------------------------------------------------------ handlers
async def protected_resource(request: Request):
    return JSONResponse(
        {
            "resource": RESOURCE,
            "authorization_servers": [ORIGIN],
            "scopes_supported": SCOPES,
            "bearer_methods_supported": ["header"],
        }
    )


async def authorization_server(request: Request):
    return JSONResponse(
        {
            "issuer": ORIGIN,
            "authorization_endpoint": ORIGIN + "/oauth/authorize",
            "token_endpoint": ORIGIN + "/oauth/token",
            "registration_endpoint": ORIGIN + "/oauth/register",
            "scopes_supported": SCOPES,
            "response_types_supported": ["code"],
            "grant_types_supported": ["authorization_code", "refresh_token"],
            "code_challenge_methods_supported": ["S256"],
            "token_endpoint_auth_methods_supported": [
                "client_secret_basic",
                "client_secret_post",
            ],
        }
    )


async def register(request: Request):
    try:
        body = await request.json()
    except Exception:  # noqa: BLE001
        return JSONResponse({"error": "invalid_request"}, status_code=400)
    redirect_uris = body.get("redirect_uris") or []
    if not isinstance(redirect_uris, list) or not redirect_uris:
        return JSONResponse(
            {"error": "invalid_redirect_uri",
             "error_description": "redirect_uris required"},
            status_code=400,
        )
    for uri in redirect_uris:
        if not (uri.startswith("https://") or uri.startswith("http://localhost")):
            return JSONResponse(
                {"error": "invalid_redirect_uri",
                 "error_description": "https required (localhost excepted)"},
                status_code=400,
            )
    client_id = "mcpgwc_" + secrets.token_hex(8)
    csec = secrets.token_urlsafe(32)
    with LOCK:
        clients = _load(CLIENTS_FILE, "clients")
        clients[client_id] = {
            "secret_sha256": _sha(csec),
            "client_name": str(body.get("client_name", "unnamed"))[:80],
            "redirect_uris": redirect_uris,
            "created": int(time.time()),
        }
        _save(CLIENTS_FILE, "clients", clients)
    return JSONResponse(
        {
            "client_id": client_id,
            "client_secret": csec,
            "client_id_issued_at": int(time.time()),
            "client_secret_expires_at": 0,
            "client_name": clients[client_id]["client_name"],
            "redirect_uris": redirect_uris,
            "grant_types": ["authorization_code", "refresh_token"],
            "response_types": ["code"],
            "token_endpoint_auth_method": "client_secret_basic",
            "scope": "read offline_access",
        },
        status_code=201,
    )


def _new_req_id():
    return "".join(secrets.choice(REQ_ALPHABET) for _ in range(6))


async def authorize(request: Request):
    q = request.query_params
    clients = _load(CLIENTS_FILE, "clients")
    client = clients.get(q.get("client_id", ""))
    err = None
    if q.get("response_type") != "code":
        err = "response_type must be code"
    elif client is None:
        err = "unknown client_id"
    elif q.get("redirect_uri") not in (client or {}).get("redirect_uris", []):
        err = "redirect_uri not registered for this client"
    elif not q.get("code_challenge") or q.get("code_challenge_method") != "S256":
        err = "PKCE with S256 is required"
    scope = q.get("scope", "read")
    if not set(scope.split()).issubset(set(SCOPES)):
        err = "requested scope not supported"
    if err:
        return HTMLResponse(_page("Connection refused", f"<p>{err}</p>"),
                            status_code=400)
    req_id = _new_req_id()
    with LOCK:
        pending = _load(PENDING_FILE, "requests")
        pending[req_id] = {
            "client_id": q["client_id"],
            "client_name": client["client_name"],
            "redirect_uri": q["redirect_uri"],
            "scope": scope,
            "state": q.get("state", ""),
            "code_challenge": q["code_challenge"],
            "resource": q.get("resource", ""),
            "status": "pending",
            "created": int(time.time()),
        }
        _save(PENDING_FILE, "requests", pending)
    body = (
        f"<p><b>{client['client_name']}</b> is asking to connect to the "
        f"Lampy Bible gateway (scope: {scope}).</p>"
        f"<p>Request ID: <b style='font-size:1.3em'>{req_id}</b></p>"
        "<p>The owner approves requests out of band. Once approved, use "
        "the button below to finish connecting.</p>"
        f"<p><a href='/oauth/authorize/complete?req={req_id}'>"
        "Check approval &amp; continue</a></p>"
    )
    return HTMLResponse(_page("Connection request pending", body))


async def authorize_complete(request: Request):
    req_id = request.query_params.get("req", "")
    with LOCK:
        pending = _load(PENDING_FILE, "requests")
        rec = pending.get(req_id)
    if rec is None:
        return HTMLResponse(_page("Unknown request",
                                  "<p>No such request ID.</p>"), status_code=404)
    if time.time() - rec["created"] > 1800:
        return HTMLResponse(_page("Request expired",
                                  "<p>Start the connection again.</p>"),
                            status_code=400)
    if rec["status"] == "denied":
        return HTMLResponse(_page("Request denied",
                                  "<p>The owner denied this request.</p>"),
                            status_code=403)
    if rec["status"] != "approved":
        body = (
            f"<p>Request <b>{req_id}</b> is still awaiting owner approval.</p>"
            f"<p><a href='/oauth/authorize/complete?req={req_id}'>"
            "Check again</a></p>"
        )
        return HTMLResponse(_page("Still pending", body))
    code = secrets.token_urlsafe(32)
    with LOCK:
        codes = _load(CODES_FILE, "codes")
        codes[_sha(code)] = {
            "client_id": rec["client_id"],
            "redirect_uri": rec["redirect_uri"],
            "code_challenge": rec["code_challenge"],
            "scope": rec["scope"],
            "expires": int(time.time()) + 600,
            "used": False,
        }
        _save(CODES_FILE, "codes", codes)
        pending[req_id]["status"] = "completed"
        _save(PENDING_FILE, "requests", pending)
    sep = "&" if "?" in rec["redirect_uri"] else "?"
    url = f"{rec['redirect_uri']}{sep}code={code}"
    if rec["state"]:
        url += f"&state={rec['state']}"
    return RedirectResponse(url, status_code=302)


def _client_auth(request: Request, form):
    auth = request.headers.get("authorization", "")
    client_id = form.get("client_id", "")
    csec = form.get("client_secret", "")
    if auth.lower().startswith("basic "):
        try:
            decoded = base64.b64decode(auth[6:]).decode()
            client_id, _, csec = decoded.partition(":")
        except Exception:  # noqa: BLE001
            return None
    clients = _load(CLIENTS_FILE, "clients")
    client = clients.get(client_id)
    if client is None or not csec:
        return None
    if not hmac.compare_digest(client["secret_sha256"], _sha(csec)):
        return None
    return client_id, client


async def token(request: Request):
    form = dict(await request.form())
    grant = form.get("grant_type", "")
    authed = _client_auth(request, form)
    if authed is None:
        return JSONResponse(
            {"error": "invalid_client"}, status_code=401,
            headers={"WWW-Authenticate": 'Basic realm="mcpgw"'},
        )
    client_id, _client = authed
    if grant == "authorization_code":
        code = form.get("code", "")
        with LOCK:
            codes = _load(CODES_FILE, "codes")
            rec = codes.get(_sha(code))
            if rec is None or rec["used"] or rec["expires"] < time.time():
                return JSONResponse({"error": "invalid_grant"}, status_code=400)
            if rec["client_id"] != client_id:
                return JSONResponse({"error": "invalid_grant"}, status_code=400)
            if form.get("redirect_uri") != rec["redirect_uri"]:
                return JSONResponse({"error": "invalid_grant"}, status_code=400)
            verifier = form.get("code_verifier", "")
            digest = base64.urlsafe_b64encode(
                hashlib.sha256(verifier.encode()).digest()
            ).rstrip(b"=").decode()
            if not verifier or not hmac.compare_digest(digest, rec["code_challenge"]):
                return JSONResponse(
                    {"error": "invalid_grant",
                     "error_description": "PKCE verification failed"},
                    status_code=400,
                )
            rec["used"] = True
            _save(CODES_FILE, "codes", codes)
        access = issue_access_token(f"oauth:{_client['client_name']}")
        resp = {
            "access_token": access,
            "token_type": "Bearer",
            "expires_in": 3600,
            "scope": "read",
        }
        if "offline_access" in rec["scope"].split():
            resp["refresh_token"] = issue_refresh_token(client_id, rec["scope"])
        return JSONResponse(resp)
    if grant == "refresh_token":
        presented = form.get("refresh_token", "")
        with LOCK:
            store = _load(REFRESH_FILE, "tokens")
            rec = store.get(_sha(presented))
            if rec is None or rec["revoked"] or rec["client_id"] != client_id:
                return JSONResponse({"error": "invalid_grant"}, status_code=400)
            rec["revoked"] = True
            _save(REFRESH_FILE, "tokens", store)
        access = issue_access_token(f"oauth:{_client['client_name']}")
        return JSONResponse(
            {
                "access_token": access,
                "token_type": "Bearer",
                "expires_in": 3600,
                "scope": "read",
                "refresh_token": issue_refresh_token(client_id, rec["scope"]),
            }
        )
    return JSONResponse({"error": "unsupported_grant_type"}, status_code=400)


# ------------------------------------------------------- conduct register
# A2A agent card + owner consent for the MCP Conduct Register
# (HORIZON SHIELD verification gate). The card is descriptive metadata
# only; the endpoint speaks MCP, not A2A, and says so in its description.
# The compensation declaration is truthful: the owner funds this gateway
# out of pocket; nobody pays for its use and no fee of any kind exists.
# One COMPENSATION object is referenced in both spec locations (top-level
# key and the Conduct Extension params) so the two can never disagree.
GATE = "https://gate.horizonshield.dev"
CONDUCT_EXT_URI = GATE + "/ext/conduct/v1"
COMPENSATION = {
    "paid_by": "other",
    "referral_fee": False,
    "listing_fee": False,
    "success_fee_pct": 0,
}

AGENT_CARD = {
    "name": "Lampy Bible MCP Gateway",
    "description": (
        "Read-only MCP server (Streamable HTTP) for the Bible project: "
        "owner-authorized access to the project's PostgreSQL Bible corpus, "
        "its git repositories, and service health probes, hosted on the "
        "owner's machine (Lampy). This endpoint speaks MCP only, not A2A; "
        "the card is published for discovery and conduct measurement. "
        "Access requires OAuth 2.1 authorization granted out of band by "
        "the owner; unauthenticated requests receive HTTP 401."
    ),
    "url": RESOURCE,
    "version": "1.0",
    "provider": {"organization": "Bible Project (Kit Cosby)"},
    "capabilities": {
        "streaming": False,
        "pushNotifications": False,
        "extensions": [
            {
                "uri": CONDUCT_EXT_URI,
                "description": (
                    "Who pays this agent, where its measured conduct record "
                    "lives, and where to file a witness walk. The "
                    "specification is served at the URI."
                ),
                "required": False,
                "params": {
                    "compensation": COMPENSATION,
                    "measured_endpoints": [RESOURCE],
                    "conduct_record": (
                        GATE + "/history?endpoint="
                        "https%3A%2F%2Flampy.taila7a335.ts.net%2Fmcp"
                    ),
                    "verdict_recipe": GATE + "/spec",
                    "witness_intake": "https://ledger.horizonshield.dev/witness",
                    "register": GATE + "/register",
                    "consent": ORIGIN + "/.well-known/mcp-conduct.json",
                },
            }
        ],
    },
    "defaultInputModes": ["application/json"],
    "defaultOutputModes": ["application/json"],
    "skills": [
        {
            "id": "bible-corpus-query",
            "name": "Bible corpus query",
            "description": (
                "Read-only SQL (SELECT/WITH) against the project's named "
                "PostgreSQL databases, plus schema and database listing."
            ),
            "tags": ["mcp", "postgresql", "bible", "read-only"],
        },
        {
            "id": "project-files-and-git",
            "name": "Project files and git",
            "description": (
                "Read-only listing, reading, and search of the gateway's "
                "own project clones and website roots, plus git status, "
                "log, branches, and diff."
            ),
            "tags": ["mcp", "files", "git", "read-only"],
        },
        {
            "id": "service-probes",
            "name": "Service probes",
            "description": "Fixed reachability probes of the Lampy services.",
            "tags": ["mcp", "health", "read-only"],
        },
    ],
    "compensation": COMPENSATION,
}

CONDUCT_CONSENT = {"allow_tool_call": True, "endpoints": [RESOURCE]}


async def agent_card(request: Request):
    return JSONResponse(AGENT_CARD)


async def conduct_consent(request: Request):
    return JSONResponse(CONDUCT_CONSENT)


ROUTES = [
    Route("/.well-known/agent-card.json", agent_card, methods=["GET"]),
    Route("/.well-known/mcp-conduct.json", conduct_consent, methods=["GET"]),
    Route("/.well-known/oauth-protected-resource", protected_resource,
          methods=["GET"]),
    Route("/.well-known/oauth-protected-resource/mcp", protected_resource,
          methods=["GET"]),
    Route("/.well-known/oauth-authorization-server", authorization_server,
          methods=["GET"]),
    Route("/oauth/register", register, methods=["POST"]),
    Route("/oauth/authorize", authorize, methods=["GET"]),
    Route("/oauth/authorize/complete", authorize_complete, methods=["GET"]),
    Route("/oauth/token", token, methods=["POST"]),
]

PUBLIC_PREFIXES = ("/.well-known/", "/oauth/")


def mount_oauth(app):
    app.routes.extend(ROUTES)
    return app
