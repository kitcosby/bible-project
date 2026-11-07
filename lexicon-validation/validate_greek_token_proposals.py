#!/usr/bin/env python3
"""Read-only validation for the six contextual YLT/Greek function-token proposals.

Usage:
    python3 validate_greek_token_proposals.py --dsn "$BIBLE_DATABASE_URL"

Requires psycopg2. The script opens a read-only transaction and never changes data.
"""
from __future__ import annotations

import argparse
import os
import sys

import psycopg2


EXPECTED = {
    "function:192:ylt:2": ("AC", 5, 12, 1, 2, "δια", "through", "function_word", "high"),
    "function:99:ylt:15": ("MT", 2, 23, 10, 15, "το", "that", "phrase_member", "moderate"),
    "function:134:ylt:3": ("AC", 26, 20, 2, 3, "τοις", "those", "function_word", "high"),
    "function:137:ylt:9": ("1CO", 13, 2, 7, 9, "τα", "the", "function_word", "high"),
    "function:159:ylt:3": ("JUDE", 1, 24, 1, 3, "τω", "Him", "phrase_member", "moderate"),
    "function:133:ylt:37": ("AC", 26, 18, 29, 37, "τη", "that", "phrase_member", "moderate"),
}


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

        for key, expected in EXPECTED.items():
            cur.execute(
                """
                SELECT b.code, gv.chapter, gv.verse, g.position, yt.ylt_word_pos,
                       g.surface, yt.surface, a.alignment_kind, a.review_status,
                       a.confidence, a.sequence_dependency_status,
                       r.review_status, r.proposed_alignment_count
                FROM ylt_profile_shadow.ylt_greek_alignment a
                JOIN ylt_profile_shadow.gnt_sequence_word g
                  ON g.sequence_profile_id = a.sequence_profile_id
                 AND g.gnt_verse_id = a.gnt_verse_id
                 AND g.position = a.gnt_position
                JOIN ylt_profile_shadow.ylt_token yt
                  ON yt.ylt_verse_id = a.ylt_verse_id
                 AND yt.ylt_word_pos = a.ylt_word_pos
                JOIN public.gnt_verses gv ON gv.gnt_verse_id = a.gnt_verse_id
                JOIN public.gnt_books b ON b.book_id = gv.book_id
                JOIN ylt_profile_shadow.gnt_token_review r
                  ON r.profile_id = a.alignment_profile_id
                 AND r.sequence_profile_id = a.sequence_profile_id
                 AND r.gnt_verse_id = a.gnt_verse_id
                 AND r.gnt_position = a.gnt_position
                WHERE a.alignment_profile_id = 4
                  AND a.sequence_profile_id = 3
                  AND a.source_record_key = %s
                """,
                (key,),
            )
            rows = cur.fetchall()
            assert len(rows) == 1, (key, "expected exactly one alignment", rows)
            row = rows[0]
            actual = (
                row[0], row[1], row[2], row[3], row[4],
                row[5], row[6], row[7], row[9],
            )
            assert actual == expected, (key, "proposal mismatch", actual, expected)
            assert row[8] == "proposed", (key, "alignment not proposed", row[8])
            assert row[10] == "provisional_candidate_sequence", (key, row[10])
            assert row[11] == "proposed" and row[12] == 1, (key, row[11:13])

        cur.execute(
            """
            SELECT review_status, count(*)
            FROM ylt_profile_shadow.gnt_token_review
            GROUP BY review_status
            """
        )
        greek_review = dict(cur.fetchall())
        assert greek_review == {
            "legacy_overlap_review": 25,
            "pending_review": 33,
            "proposed": 477,
        }, greek_review

        cur.execute(
            """
            SELECT review_status, count(*)
            FROM ylt_profile_shadow.ylt_greek_alignment
            GROUP BY review_status
            """
        )
        alignment_review = dict(cur.fetchall())
        assert alignment_review == {
            "not_expressed": 20,
            "proposed": 519,
            "unresolved": 13,
        }, alignment_review

        cur.execute(
            """
            SELECT
              count(*) FILTER (WHERE a.review_status = 'proposed'
                               AND (a.ylt_verse_id IS NULL OR a.gnt_verse_id IS NULL)),
              count(*) FILTER (WHERE a.alignment_group_id IS NOT NULL
                               AND ag.alignment_group_id IS NULL)
            FROM ylt_profile_shadow.ylt_greek_alignment a
            LEFT JOIN ylt_profile_shadow.alignment_group ag
              ON ag.alignment_group_id = a.alignment_group_id
            """
        )
        incomplete_proposals, orphan_groups = cur.fetchone()
        assert incomplete_proposals == 0, incomplete_proposals
        assert orphan_groups == 0, orphan_groups

        cur.execute("SELECT count(*) FROM public.gnt_words")
        gnt_words = cur.fetchone()[0]
        cur.execute("SELECT count(*) FROM public.gnt_ylt_renderings")
        legacy_renderings = cur.fetchone()[0]
        assert (gnt_words, legacy_renderings) == (141009, 143227), (
            gnt_words, legacy_renderings
        )

        print("PASS: six contextual proposals match their exact YLT/Greek endpoints.")
        print("PASS: Greek-token review counts:", greek_review)
        print("PASS: alignment review counts:", alignment_review)
        print("PASS: no incomplete proposals or orphan alignment groups.")
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
