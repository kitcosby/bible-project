#!/usr/bin/env python3
"""Gateway token administration (run on Lampy as root or mcpgw).

  gw_admin.py mint <label> [--days N]   print a new token ONCE
  gw_admin.py list                      ids, labels, scopes, status (no secrets)
  gw_admin.py revoke <token-id>         mark a token revoked

Tokens are stored hashed (sha256 of the secret part) in
/home/mcpgw/secrets/tokens.json; the plaintext exists only at mint time.
"""
import hashlib
import json
import secrets
import sys
import time
from pathlib import Path

STORE = Path("/home/mcpgw/secrets/tokens.json")


def load():
    if STORE.exists():
        return json.loads(STORE.read_text())
    return {"tokens": []}


def save(data):
    STORE.write_text(json.dumps(data, indent=2))
    STORE.chmod(0o600)


def mint(label, days):
    secret = secrets.token_urlsafe(32)
    token_id = secrets.token_hex(4)
    rec = {
        "id": token_id,
        "label": label,
        "sha256": hashlib.sha256(secret.encode()).hexdigest(),
        "scopes": ["read"],
        "created": int(time.time()),
        "expires": int(time.time()) + days * 86400 if days else None,
        "revoked": False,
    }
    data = load()
    data["tokens"].append(rec)
    save(data)
    print(f"mcpgw1.{token_id}.{secret}")


def list_tokens():
    for rec in load()["tokens"]:
        status = "revoked" if rec.get("revoked") else "active"
        print(
            f"{rec['id']}  {status:8}  scopes={','.join(rec.get('scopes', []))}"
            f"  expires={rec.get('expires')}  label={rec.get('label')}"
        )


PENDING = Path("/home/mcpgw/secrets/oauth_pending.json")


def _load_pending():
    if PENDING.exists():
        return json.loads(PENDING.read_text())
    return {"requests": {}}


def list_pending():
    data = _load_pending()
    shown = False
    for req_id, rec in data["requests"].items():
        if rec.get("status") in ("pending", "approved", "denied"):
            age = int(time.time()) - rec.get("created", 0)
            print(
                f"{req_id}  {rec['status']:9}  age={age}s  "
                f"client={rec.get('client_name')}  scope={rec.get('scope')}"
            )
            shown = True
    if not shown:
        print("no authorize requests recorded")


def set_pending(req_id, status):
    data = _load_pending()
    rec = data["requests"].get(req_id)
    if rec is None:
        print("no such request id")
        return
    rec["status"] = status
    PENDING.write_text(json.dumps(data, indent=2))
    PENDING.chmod(0o600)
    print(f"request {req_id} -> {status}")


def revoke(token_id):
    data = load()
    hit = False
    for rec in data["tokens"]:
        if rec["id"] == token_id:
            rec["revoked"] = True
            hit = True
    save(data)
    print("revoked" if hit else "no such token id")


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(2)
    if args[0] == "mint":
        days = 0
        if "--days" in args:
            days = int(args[args.index("--days") + 1])
        mint(args[1], days)
    elif args[0] == "list":
        list_tokens()
    elif args[0] == "revoke":
        revoke(args[1])
    elif args[0] == "pending":
        list_pending()
    elif args[0] == "approve":
        set_pending(args[1], "approved")
    elif args[0] == "deny":
        set_pending(args[1], "denied")
    else:
        print(__doc__)
        sys.exit(2)
