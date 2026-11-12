#!/usr/bin/env python3
"""Read-only integrity checks for the live PostgreSQL YLT lexicon bridges.

Usage:
  BIBLE_DATABASE_URL='dbname=bible host=/tmp user=postgres' \
    python3 eval/validate_ylt_lexicon_postgres.py

The script explicitly starts a READ ONLY transaction. It does not update,
delete, create, or recompute any database object. Run against a restored
snapshot first; production execution is optional and read-only.
"""
from __future__ import annotations

import json
import os
import sys

import psycopg2
from psycopg2.extras import RealDictCursor


def main() -> int:
    dsn = os.environ.get("BIBLE_DATABASE_URL")
    if not dsn:
        print("ERROR: set BIBLE_DATABASE_URL to a PostgreSQL DSN", file=sys.stderr)
        return 2

    conn = psycopg2.connect(dsn)
    report: dict[str, object] = {"mode": "read-only", "checks": {}}
    failures: list[str] = []

    try:
        conn.set_session(readonly=True, autocommit=False)
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT current_database() AS database, current_user AS role, version() AS version")
            report["database"] = dict(cur.fetchone())

            checks = {
                "baseline_counts": """
                    SELECT
                      (SELECT count(*) FROM words) AS hebrew_words,
                      (SELECT count(*) FROM ylt_renderings) AS hebrew_ylt_renderings,
                      (SELECT count(*) FROM lexicon_ylt_rendering) AS hebrew_lexicon_ylt_renderings,
                      (SELECT count(*) FROM gnt_words) AS tr_words,
                      (SELECT count(*) FROM gnt_ylt_renderings) AS tr_ylt_renderings,
                      (SELECT count(*) FROM gntb_words) AS byzantine_words,
                      (SELECT count(*) FROM gntb_ylt_renderings) AS byzantine_ylt_renderings,
                      (SELECT count(*) FROM gnts_words) AS sbl_words,
                      (SELECT count(*) FROM lxx_words) AS lxx_words
                """,
                "hebrew_orphan_renderings": """
                    SELECT count(*) AS n
                    FROM ylt_renderings y
                    LEFT JOIN words w ON w.word_id = y.word_id
                    WHERE w.word_id IS NULL
                """,
                "tr_alignment_out_of_range": """
                    SELECT count(*) AS n
                    FROM gnt_alignment a
                    JOIN gnt_verses v ON v.corpus_verse_id = a.corpus_verse_id
                    LEFT JOIN (
                      SELECT gnt_verse_id, max(position) AS max_position
                      FROM gnt_words GROUP BY gnt_verse_id
                    ) w ON w.gnt_verse_id = v.gnt_verse_id
                    WHERE a.gnt_position < 1
                       OR a.gnt_position > coalesce(w.max_position, 0)
                """,
                "tr_rendering_orphans": """
                    SELECT count(*) AS n
                    FROM gnt_ylt_renderings y
                    LEFT JOIN gnt_words w
                      ON w.gnt_verse_id = y.gnt_verse_id
                     AND w.position = y.gnt_position
                    WHERE w.gnt_verse_id IS NULL
                """,
                "byzantine_alignment_out_of_range": """
                    SELECT count(*) AS n
                    FROM gntb_alignment a
                    JOIN gntb_verses v ON v.corpus_verse_id = a.corpus_verse_id
                    LEFT JOIN (
                      SELECT gnt_verse_id, max(position) AS max_position
                      FROM gntb_words GROUP BY gnt_verse_id
                    ) w ON w.gnt_verse_id = v.gnt_verse_id
                    WHERE a.gntb_position < 1
                       OR a.gntb_position > coalesce(w.max_position, 0)
                """,
                "byzantine_rendering_orphans": """
                    SELECT count(*) AS n
                    FROM gntb_ylt_renderings y
                    LEFT JOIN gntb_words w
                      ON w.gnt_verse_id = y.gntb_verse_id
                     AND w.position = y.gntb_position
                    WHERE w.gnt_verse_id IS NULL
                """,
                "tr_duplicate_alignment_keys": """
                    SELECT count(*) AS n FROM (
                      SELECT corpus_verse_id, kjv_pos, gnt_position
                      FROM gnt_alignment
                      GROUP BY corpus_verse_id, kjv_pos, gnt_position
                      HAVING count(*) > 1
                    ) d
                """,
                "tr_duplicate_ylt_keys": """
                    SELECT count(*) AS n FROM (
                      SELECT gnt_verse_id, gnt_position, ylt_word_pos
                      FROM gnt_ylt_renderings
                      GROUP BY gnt_verse_id, gnt_position, ylt_word_pos
                      HAVING count(*) > 1
                    ) d
                """,
                "byzantine_duplicate_ylt_keys": """
                    SELECT count(*) AS n FROM (
                      SELECT gntb_verse_id, gntb_position, ylt_word_pos
                      FROM gntb_ylt_renderings
                      GROUP BY gntb_verse_id, gntb_position, ylt_word_pos
                      HAVING count(*) > 1
                    ) d
                """,
                "tr_g0_occurrences": """
                    SELECT count(*) AS n FROM gnt_words WHERE strongs = 'G0'
                """,
                "sbl_words_with_exact_lxx_lemma_match": """
                    SELECT count(*) AS n
                    FROM gnts_words s
                    WHERE EXISTS (
                      SELECT 1 FROM lxx_words l
                      WHERE l.lemma = s.lemma
                        AND nullif(trim(l.gloss), '') IS NOT NULL
                    )
                """,
            }

            for name, sql in checks.items():
                cur.execute(sql)
                row = dict(cur.fetchone())
                report["checks"][name] = row["n"] if "n" in row else row
                if name in {
                    "hebrew_orphan_renderings",
                    "tr_alignment_out_of_range",
                    "tr_rendering_orphans",
                    "byzantine_alignment_out_of_range",
                    "byzantine_rendering_orphans",
                    "tr_duplicate_alignment_keys",
                    "tr_duplicate_ylt_keys",
                    "byzantine_duplicate_ylt_keys",
                } and row["n"] != 0:
                    failures.append(name)

            # Focused evidence for the two known TR cases.
            for label, book_id, chapter, verse in (
                ("john_9_21", 43, 9, 21),
                ("colossians_4_10", 51, 4, 10),
            ):
                cur.execute(
                    """
                    SELECT v.book_id, v.chapter, v.verse,
                           w.position, w.surface, w.strongs,
                           coalesce(string_agg(y.ylt_word, ' ' ORDER BY y.ylt_word_pos), '') AS ylt
                    FROM gnt_verses v
                    JOIN gnt_words w ON w.gnt_verse_id = v.gnt_verse_id
                    LEFT JOIN gnt_ylt_renderings y
                      ON y.gnt_verse_id = w.gnt_verse_id
                     AND y.gnt_position = w.position
                    WHERE v.book_id = %s AND v.chapter = %s AND v.verse = %s
                    GROUP BY v.book_id, v.chapter, v.verse, w.position, w.surface, w.strongs
                    ORDER BY w.position
                    """,
                    (book_id, chapter, verse),
                )
                report[label] = [dict(row) for row in cur.fetchall()]

            conn.rollback()
    finally:
        conn.close()

    report["structural_failures"] = failures
    print(json.dumps(report, ensure_ascii=False, indent=2, default=str))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
