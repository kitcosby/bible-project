#!/usr/bin/env python3
"""Create the mcp_ro read-only PostgreSQL role for the MCP gateway.

Run as the postgres OS user (peer auth via the /tmp socket). Generates the
role password in-process, stores it ONLY in /home/mcpgw/secrets/
pg_mcp_ro.password (0600, mcpgw-owned), and never prints it.
"""
import os
import secrets
import sys

import psycopg2
from psycopg2 import sql

ALLOWLIST = [
    "bible",
    "bible_app",
    "bible_search_prod_20261111",
    "bible_search_stage_20261109",
    "bible_reconcile_20261111",
    "bible_hebrew_variant_shadow_20261107",
]
SECRET_PATH = "/home/mcpgw/secrets/pg_mcp_ro.password"


def main():
    # The credential arrives via a one-shot drop file written by the root
    # prep step (which also wrote the gateway's secret file). Read + remove.
    with open("/tmp/.mcp_ro_cred") as f:
        cred = f.read().strip()
    os.unlink("/tmp/.mcp_ro_cred")

    admin = psycopg2.connect(host="/tmp", dbname="postgres", user="postgres")
    admin.autocommit = True
    cur = admin.cursor()
    cur.execute("SELECT 1 FROM pg_roles WHERE rolname = 'mcp_ro'")
    if cur.fetchone():
        cur.execute(
            sql.SQL("ALTER ROLE mcp_ro WITH LOGIN PASSWORD {}").format(
                sql.Literal(cred)
            )
        )
        print("role existed: credential rotated")
    else:
        cur.execute(
            sql.SQL("CREATE ROLE mcp_ro LOGIN PASSWORD {}").format(
                sql.Literal(cred)
            )
        )
        print("role created")
    cur.execute("ALTER ROLE mcp_ro SET default_transaction_read_only = on")
    cur.execute("ALTER ROLE mcp_ro SET statement_timeout = '30s'")
    for db in ALLOWLIST:
        cur.execute(
            sql.SQL("GRANT CONNECT ON DATABASE {} TO mcp_ro").format(
                sql.Identifier(db)
            )
        )
        conn = psycopg2.connect(host="/tmp", dbname=db, user="postgres")
        conn.autocommit = True
        c2 = conn.cursor()
        c2.execute("GRANT USAGE ON SCHEMA public TO mcp_ro")
        c2.execute("GRANT SELECT ON ALL TABLES IN SCHEMA public TO mcp_ro")
        c2.execute("GRANT SELECT ON ALL SEQUENCES IN SCHEMA public TO mcp_ro")
        conn.close()
        print("granted:", db)
    admin.close()

    # Verify as mcp_ro over TCP: read works, write is refused.
    test = psycopg2.connect(
        host="127.0.0.1", dbname="bible", user="mcp_ro", password=cred
    )
    tc = test.cursor()
    tc.execute("SELECT count(*) FROM words")
    print("verify read: bible.words =", tc.fetchone()[0])
    tc.execute("SHOW default_transaction_read_only")
    print("verify read-only txn default:", tc.fetchone()[0])
    for stmt in (
        "CREATE TABLE mcp_ro_probe (x int)",
        "UPDATE words SET strongs = strongs WHERE false",
    ):
        try:
            tc.execute(stmt)
            print("PROBLEM: write unexpectedly allowed:", stmt[:30])
            test.rollback()
        except psycopg2.Error as e:
            test.rollback()
            print("verify write refused:", stmt[:30], "->", e.pgerror.strip().splitlines()[0][:80])
    test.close()
    print("SETUP_OK")


if __name__ == "__main__":
    sys.exit(main())
