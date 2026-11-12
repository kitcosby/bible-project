#!/usr/bin/env python3
"""Read-only validator for the 19 YLT variant-selection decisions.

Usage:
    python3 validate_ylt_variant_decisions.py --dsn "$BIBLE_DATABASE_URL"

Requires psycopg2. The script opens a read-only transaction and never changes data.
"""
from __future__ import annotations

import argparse
import os
import sys

import psycopg2


REVIEWED = {
    "43:6": "A",   # John 8:6
    "44:3": "A",   # Acts 3:3
    "45:7": "A",   # Romans 16:27
    "49:3": "A",   # Ephesians 6:24
    "62:3": "B",   # 1 John 2:23
}

NOT_APPLICABLE = (
    "45:8", "46:7", "47:10", "48:2", "49:4", "50:4", "52:5",
    "53:3", "54:5", "55:3", "56:2", "57:2", "58:9",
)

UNRESOLVED = "66:9"  # Revelation 7:3


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dsn", default=os.environ.get("BIBLE_DATABASE_URL"))
    args = parser.parse_args()
    if not args.dsn:
        parser.error("provide --dsn or set BIBLE_DATABASE_URL")

    conn = psycopg2.connect(args.dsn)
    try:
        conn.autocommit = False
        cur = conn.cursor()
        cur.execute("SET TRANSACTION READ ONLY")

        for group_key, branch in REVIEWED.items():
            cur.execute(
                """
                SELECT selected_branch, decision_status, rationale
                FROM ylt_profile_shadow.profile_variant_selection
                WHERE profile_id = 3 AND group_key = %s
                """,
                (group_key,),
            )
            row = cur.fetchone()
            assert row and row[0] == branch and row[1] == "reviewed_against_translation", (
                group_key, row
            )

        for group_key in NOT_APPLICABLE:
            cur.execute(
                """
                SELECT selected_branch, decision_status, rationale
                FROM ylt_profile_shadow.profile_variant_selection
                WHERE profile_id = 3 AND group_key = %s
                """,
                (group_key,),
            )
            row = cur.fetchone()
            assert row and row[0] is None and row[1] == "not_applicable_to_verse_alignment", (
                group_key, row
            )
            assert "subscription" in row[2].lower() or "colophon" in row[2].lower(), (
                group_key, row[2]
            )

        cur.execute(
            """
            SELECT selected_branch, decision_status, rationale
            FROM ylt_profile_shadow.profile_variant_selection
            WHERE profile_id = 3 AND group_key = %s
            """,
            (UNRESOLVED,),
        )
        row = cur.fetchone()
        assert row and row[0] is None and row[1] == "unresolved", row

        cur.execute(
            """
            SELECT decision_status, count(*)
            FROM ylt_profile_shadow.profile_variant_selection
            WHERE profile_id = 3
            GROUP BY decision_status
            """
        )
        counts = dict(cur.fetchall())
        expected_counts = {
            "inherited_provisional": 224,
            "not_applicable_to_verse_alignment": 14,
            "proposed": 5,
            "reviewed_against_translation": 17,
            "unresolved": 1,
        }
        assert counts == expected_counts, counts

        # The six verse-text references are intentionally not yet materialized
        # in the 116-verse shadow sequence fixture.
        cur.execute(
            """
            SELECT count(*)
            FROM ylt_profile_shadow.gnt_sequence_word g
            JOIN public.gnt_verses v ON v.gnt_verse_id = g.gnt_verse_id
            JOIN public.gnt_books b ON b.book_id = v.book_id
            WHERE g.sequence_profile_id = 3 AND (
                 (b.code = 'JOH' AND v.chapter = 8 AND v.verse = 6)
              OR (b.code = 'AC' AND v.chapter = 3 AND v.verse = 3)
              OR (b.code = 'RO' AND v.chapter = 16 AND v.verse = 27)
              OR (b.code = 'EPH' AND v.chapter = 6 AND v.verse = 24)
              OR (b.code = '1JO' AND v.chapter = 2 AND v.verse = 23)
              OR (b.code = 'RE' AND v.chapter = 7 AND v.verse = 3)
            )
            """
        )
        sequence_rows = cur.fetchone()[0]
        assert sequence_rows == 0, sequence_rows

        cur.execute(
            """
            SELECT count(*)
            FROM ylt_profile_shadow.gnt_sequence_word g
            WHERE g.sequence_profile_id = 3
              AND g.source_variant_groups ?| %s
            """,
            (list(NOT_APPLICABLE),),
        )
        subscription_dependencies = cur.fetchone()[0]
        assert subscription_dependencies == 0, subscription_dependencies

        cur.execute("SELECT count(*) FROM public.gnt_words")
        gnt_words = cur.fetchone()[0]
        cur.execute("SELECT count(*) FROM public.gnt_ylt_renderings")
        legacy_renderings = cur.fetchone()[0]
        assert (gnt_words, legacy_renderings) == (141009, 143227), (
            gnt_words, legacy_renderings
        )

        print("PASS: five YLT branch choices match stored YLT verse wording.")
        print("PASS: thirteen subscription/colophon groups are not applicable to verse alignment.")
        print("PASS: Revelation 7:3 remains unresolved.")
        print("PASS: selection counts:", counts)
        print("PASS: no sequence rows were prematurely materialized for the six variant verses.")
        print("PASS: no paratextual subscription group contaminates the materialized verse sequence.")
        print("PASS: production baselines unchanged:", gnt_words, legacy_renderings)
        conn.rollback()
        return 0
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
