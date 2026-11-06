#!/usr/bin/env python3
"""Read-only, full-corpus integrity checks for the YLT lexicon database.

Usage:
  BIBLE_DATABASE_URL='dbname=bible_restore_verify_20261106 host=/tmp user=postgres' \
    python3 eval/validate_ylt_lexicon_postgres.py

The connection is explicitly READ ONLY. No DDL, DML, rebuild or repair is run.
Run against a restored snapshot first. A nonzero exit status means at least
one structural invariant failed; known lexical/provenance limitations are
reported as diagnostics and do not by themselves fail the run.
"""
from __future__ import annotations

import json
import os
import string
import sys

import psycopg2


TABLES = (
    "verses", "ylt_verses", "words", "ylt_renderings",
    "lexicon", "lexicon_ylt_rendering", "lexicon_ylt_context",
    "kjv_words", "kjv_renderings", "word_alignment",
    "gnt_verses", "gnt_words", "gnt_alignment", "gnt_ylt_renderings",
    "gntb_verses", "gntb_words", "gntb_alignment", "gntb_ylt_renderings",
    "gnts_verses", "gnts_words", "gnts_alignment", "gnts_ylt_renderings",
    "lxx_words", "morph_patterns", "strongs",
)

SQL_CHECKS = {
    "hebrew_words_missing_verse": """
        SELECT count(*) AS n FROM words w
        LEFT JOIN verses v ON v.verse_id = w.verse_id
        WHERE v.verse_id IS NULL
    """,
    "hebrew_words_missing_root_vowel": """
        SELECT count(*) AS n FROM words w
        LEFT JOIN root_vowel r
          ON r.root_id = w.root_id
         AND r.root_form_seq = w.root_form_seq
         AND r.vowel_seq = w.root_vowel_seq
        WHERE r.root_id IS NULL
    """,
    "hebrew_orphan_renderings": """
        SELECT count(*) AS n FROM ylt_renderings y
        LEFT JOIN words w ON w.word_id = y.word_id
        WHERE w.word_id IS NULL
    """,
    "hebrew_renderings_missing_ylt_text": """
        SELECT count(*) AS n FROM ylt_renderings y
        JOIN words w ON w.word_id = y.word_id
        LEFT JOIN ylt_verses t ON t.verse_id = w.verse_id
        WHERE t.verse_id IS NULL
    """,
    "hebrew_word_alignment_missing_verse": """
        SELECT count(*) AS n FROM word_alignment a
        LEFT JOIN verses v ON v.verse_id = a.verse_id
        WHERE v.verse_id IS NULL
    """,
    "hebrew_word_alignment_missing_word": """
        SELECT count(*) AS n FROM word_alignment a
        LEFT JOIN words w ON w.word_id = a.hebrew_word_id
        WHERE a.hebrew_word_id IS NOT NULL AND w.word_id IS NULL
    """,
    "hebrew_word_alignment_missing_kjv_word": """
        SELECT count(*) AS n FROM word_alignment a
        LEFT JOIN kjv_words k ON k.kjv_word_id = a.kjv_word_id
        WHERE a.kjv_word_id IS NOT NULL AND k.kjv_word_id IS NULL
    """,
    "hebrew_word_alignment_missing_ylt_rendering": """
        SELECT count(*) AS n FROM word_alignment a
        LEFT JOIN ylt_renderings y ON y.rendering_id = a.ylt_rendering_id
        WHERE a.ylt_rendering_id IS NOT NULL AND y.rendering_id IS NULL
    """,
    "kjv_words_missing_verse": """
        SELECT count(*) AS n FROM kjv_words k
        LEFT JOIN verses v ON v.verse_id = k.verse_id
        WHERE v.verse_id IS NULL
    """,
    "kjv_renderings_missing_word": """
        SELECT count(*) AS n FROM kjv_renderings k
        LEFT JOIN words w ON w.word_id = k.word_id
        WHERE w.word_id IS NULL
    """,
    "root_forms_missing_root": """
        SELECT count(*) AS n FROM root_form f
        LEFT JOIN root_entry r ON r.root_id = f.root_id
        WHERE r.root_id IS NULL
    """,
    "root_vowels_missing_form": """
        SELECT count(*) AS n FROM root_vowel v
        LEFT JOIN root_form f
          ON f.root_id = v.root_id AND f.form_seq = v.root_form_seq
        WHERE f.root_id IS NULL
    """,
    "lexicon_entries_missing_root_vowel": """
        SELECT count(*) AS n FROM lexicon l
        LEFT JOIN root_vowel r
          ON r.root_id = l.root_id
         AND r.root_form_seq = l.root_form_seq
         AND r.vowel_seq = l.vowel_seq
        WHERE r.root_id IS NULL
    """,
    "lexicon_ylt_renderings_missing_root_vowel": """
        SELECT count(*) AS n FROM lexicon_ylt_rendering l
        LEFT JOIN root_vowel r
          ON r.root_id = l.root_id
         AND r.root_form_seq = l.root_form_seq
         AND r.vowel_seq = l.vowel_seq
        WHERE r.root_id IS NULL
    """,
    "lexicon_ylt_context_missing_verse": """
        SELECT count(*) AS n FROM lexicon_ylt_context l
        LEFT JOIN verses v ON v.verse_id = l.verse_id
        WHERE v.verse_id IS NULL
    """,
    "word_morphology_missing_pattern": """
        SELECT count(*) AS n FROM words w
        LEFT JOIN morph_patterns m ON m.pattern_id = w.morph_pattern_id
        WHERE w.morph_pattern_id IS NOT NULL AND m.pattern_id IS NULL
    """,
    "word_strongs_source_missing": """
        SELECT count(*) AS n FROM words w
        LEFT JOIN strongs_sources s ON s.source_id = w.strongs_source_id
        WHERE w.strongs_source_id IS NOT NULL AND s.source_id IS NULL
    """,

    "tr_alignment_missing_verse": """
        SELECT count(*) AS n FROM gnt_alignment a
        LEFT JOIN gnt_verses v ON v.corpus_verse_id = a.corpus_verse_id
        WHERE v.gnt_verse_id IS NULL
    """,
    "tr_alignment_out_of_range": """
        SELECT count(*) AS n
        FROM gnt_alignment a
        LEFT JOIN gnt_verses v ON v.corpus_verse_id = a.corpus_verse_id
        LEFT JOIN (
          SELECT gnt_verse_id, max(position) AS max_position
          FROM gnt_words GROUP BY gnt_verse_id
        ) w ON w.gnt_verse_id = v.gnt_verse_id
        WHERE a.gnt_position IS NULL OR a.gnt_position < 1
           OR a.gnt_position > coalesce(w.max_position, 0)
    """,
    "tr_kjv_position_out_of_range": """
        SELECT count(*) AS n
        FROM gnt_alignment a
        LEFT JOIN (
          SELECT verse_id, max(kjv_pos) AS max_position
          FROM kjv_words GROUP BY verse_id
        ) k ON k.verse_id = a.corpus_verse_id
        WHERE a.kjv_pos IS NULL OR a.kjv_pos < 1
           OR a.kjv_pos > coalesce(k.max_position, 0)
    """,
    "tr_rendering_orphans": """
        SELECT count(*) AS n FROM gnt_ylt_renderings y
        LEFT JOIN gnt_words w
          ON w.gnt_verse_id = y.gnt_verse_id
         AND w.position = y.gnt_position
        WHERE w.gnt_verse_id IS NULL
    """,
    "tr_renderings_missing_ylt_text": """
        SELECT count(*) AS n FROM gnt_ylt_renderings y
        JOIN gnt_verses v ON v.gnt_verse_id = y.gnt_verse_id
        LEFT JOIN ylt_verses t ON t.verse_id = v.corpus_verse_id
        WHERE t.verse_id IS NULL
    """,
    "tr_duplicate_alignment_keys": """
        SELECT count(*) AS n FROM (
          SELECT corpus_verse_id, kjv_pos, gnt_position
          FROM gnt_alignment GROUP BY 1,2,3 HAVING count(*) > 1
        ) d
    """,
    "tr_duplicate_ylt_keys": """
        SELECT count(*) AS n FROM (
          SELECT gnt_verse_id, gnt_position, ylt_word_pos
          FROM gnt_ylt_renderings GROUP BY 1,2,3 HAVING count(*) > 1
        ) d
    """,

    "byzantine_alignment_missing_verse": """
        SELECT count(*) AS n FROM gntb_alignment a
        LEFT JOIN gntb_verses v ON v.corpus_verse_id = a.corpus_verse_id
        WHERE v.gnt_verse_id IS NULL
    """,
    "byzantine_alignment_out_of_range": """
        SELECT count(*) AS n
        FROM gntb_alignment a
        LEFT JOIN gntb_verses v ON v.corpus_verse_id = a.corpus_verse_id
        LEFT JOIN (
          SELECT gnt_verse_id, max(position) AS max_position
          FROM gntb_words GROUP BY gnt_verse_id
        ) w ON w.gnt_verse_id = v.gnt_verse_id
        WHERE a.corpus_verse_id IS NULL OR a.kjv_pos IS NULL
           OR a.gntb_position IS NULL OR a.kjv_pos < 1
           OR a.gntb_position < 1
           OR a.gntb_position > coalesce(w.max_position, 0)
    """,
    "byzantine_kjv_position_out_of_range": """
        SELECT count(*) AS n
        FROM gntb_alignment a
        LEFT JOIN (
          SELECT verse_id, max(kjv_pos) AS max_position
          FROM kjv_words GROUP BY verse_id
        ) k ON k.verse_id = a.corpus_verse_id
        WHERE a.kjv_pos IS NULL OR a.kjv_pos < 1
           OR a.kjv_pos > coalesce(k.max_position, 0)
    """,
    "byzantine_rendering_orphans": """
        SELECT count(*) AS n FROM gntb_ylt_renderings y
        LEFT JOIN gntb_words w
          ON w.gnt_verse_id = y.gntb_verse_id
         AND w.position = y.gntb_position
        WHERE w.gnt_verse_id IS NULL
    """,
    "byzantine_renderings_missing_ylt_text": """
        SELECT count(*) AS n FROM gntb_ylt_renderings y
        JOIN gntb_verses v ON v.gnt_verse_id = y.gntb_verse_id
        LEFT JOIN ylt_verses t ON t.verse_id = v.corpus_verse_id
        WHERE t.verse_id IS NULL
    """,
    "byzantine_duplicate_alignment_keys": """
        SELECT count(*) AS n FROM (
          SELECT corpus_verse_id, kjv_pos, gntb_position
          FROM gntb_alignment GROUP BY 1,2,3 HAVING count(*) > 1
        ) d
    """,
    "byzantine_duplicate_ylt_keys": """
        SELECT count(*) AS n FROM (
          SELECT gntb_verse_id, gntb_position, ylt_word_pos
          FROM gntb_ylt_renderings GROUP BY 1,2,3 HAVING count(*) > 1
        ) d
    """,

    "sbl_alignment_missing_verse": """
        SELECT count(*) AS n FROM gnts_alignment a
        LEFT JOIN gnts_verses v ON v.corpus_verse_id = a.corpus_verse_id
        WHERE v.gnt_verse_id IS NULL
    """,
    "sbl_alignment_out_of_range": """
        SELECT count(*) AS n
        FROM gnts_alignment a
        LEFT JOIN gnts_verses v ON v.corpus_verse_id = a.corpus_verse_id
        LEFT JOIN (
          SELECT gnt_verse_id, max(position) AS max_position
          FROM gnts_words GROUP BY gnt_verse_id
        ) w ON w.gnt_verse_id = v.gnt_verse_id
        WHERE a.corpus_verse_id IS NULL OR a.kjv_pos IS NULL
           OR a.gnts_position IS NULL OR a.kjv_pos < 1
           OR a.gnts_position < 1
           OR a.gnts_position > coalesce(w.max_position, 0)
    """,
    "sbl_kjv_position_out_of_range": """
        SELECT count(*) AS n
        FROM gnts_alignment a
        LEFT JOIN (
          SELECT verse_id, max(kjv_pos) AS max_position
          FROM kjv_words GROUP BY verse_id
        ) k ON k.verse_id = a.corpus_verse_id
        WHERE a.kjv_pos IS NULL OR a.kjv_pos < 1
           OR a.kjv_pos > coalesce(k.max_position, 0)
    """,
    "sbl_rendering_orphans": """
        SELECT count(*) AS n FROM gnts_ylt_renderings y
        LEFT JOIN gnts_words w
          ON w.gnt_verse_id = y.gnts_verse_id
         AND w.position = y.gnts_position
        WHERE w.gnt_verse_id IS NULL
    """,
    "sbl_renderings_missing_ylt_text": """
        SELECT count(*) AS n FROM gnts_ylt_renderings y
        JOIN gnts_verses v ON v.gnt_verse_id = y.gnts_verse_id
        LEFT JOIN ylt_verses t ON t.verse_id = v.corpus_verse_id
        WHERE t.verse_id IS NULL
    """,
    "sbl_duplicate_alignment_keys": """
        SELECT count(*) AS n FROM (
          SELECT corpus_verse_id, kjv_pos, gnts_position
          FROM gnts_alignment GROUP BY 1,2,3 HAVING count(*) > 1
        ) d
    """,
    "sbl_duplicate_ylt_keys": """
        SELECT count(*) AS n FROM (
          SELECT gnts_verse_id, gnts_position, ylt_word_pos
          FROM gnts_ylt_renderings GROUP BY 1,2,3 HAVING count(*) > 1
        ) d
    """,
}


TOKEN_QUERIES = {
    "hebrew": """
        SELECT y.word_id, y.ylt_word_pos, y.ylt_word, t.text
        FROM ylt_renderings y
        JOIN words w ON w.word_id = y.word_id
        LEFT JOIN ylt_verses t ON t.verse_id = w.verse_id
    """,
    "tr": """
        SELECT y.gnt_verse_id, y.ylt_word_pos, y.ylt_word, t.text
        FROM gnt_ylt_renderings y
        JOIN gnt_verses v ON v.gnt_verse_id = y.gnt_verse_id
        LEFT JOIN ylt_verses t ON t.verse_id = v.corpus_verse_id
    """,
    "byzantine": """
        SELECT y.gntb_verse_id, y.ylt_word_pos, y.ylt_word, t.text
        FROM gntb_ylt_renderings y
        JOIN gntb_verses v ON v.gnt_verse_id = y.gntb_verse_id
        LEFT JOIN ylt_verses t ON t.verse_id = v.corpus_verse_id
    """,
    "sbl": """
        SELECT y.gnts_verse_id, y.ylt_word_pos, y.ylt_word, t.text
        FROM gnts_ylt_renderings y
        JOIN gnts_verses v ON v.gnt_verse_id = y.gnts_verse_id
        LEFT JOIN ylt_verses t ON t.verse_id = v.corpus_verse_id
    """,
}


def scalar(cur, sql):
    cur.execute(sql)
    return cur.fetchone()[0]


def token_check(cur, name, sql, strip_chars):
    cur.execute(sql)
    total = missing_text = out_of_range = mismatches = 0
    bad_positions = []
    bad_words = []
    while True:
        rows = cur.fetchmany(5000)
        if not rows:
            break
        for verse_word_id, position, ylt_word, text in rows:
            total += 1
            if text is None:
                missing_text += 1
                continue
            tokens = [
                token for raw in text.split()
                if (token := raw.strip(strip_chars))
            ]
            if position is None or position < 1 or position > len(tokens):
                out_of_range += 1
                if len(bad_positions) < 10:
                    bad_positions.append({
                        "word_or_verse_id": verse_word_id,
                        "position": position,
                        "ylt_word": ylt_word,
                        "token_count": len(tokens),
                    })
                continue
            expected = tokens[position - 1].lower().strip(strip_chars)
            actual = (ylt_word or "").lower().strip(strip_chars)
            if actual != expected:
                mismatches += 1
                if len(bad_words) < 10:
                    bad_words.append({
                        "word_or_verse_id": verse_word_id,
                        "position": position,
                        "stored": ylt_word,
                        "source_token": tokens[position - 1],
                    })
    return {
        "rows": total,
        "missing_ylt_text": missing_text,
        "out_of_range": out_of_range,
        "token_mismatches": mismatches,
        "out_of_range_samples": bad_positions,
        "mismatch_samples": bad_words,
    }


def main():
    dsn = os.environ.get("BIBLE_DATABASE_URL")
    if not dsn:
        print("ERROR: set BIBLE_DATABASE_URL to a PostgreSQL DSN", file=sys.stderr)
        return 2

    conn = psycopg2.connect(dsn)
    report = {
        "mode": "read-only",
        "checks": {},
        "token_checks": {},
        "diagnostics": {},
    }
    failures = []

    try:
        conn.set_session(readonly=True, autocommit=False)
        with conn.cursor() as cur:
            cur.execute("""
                SELECT current_database(), current_user, version(),
                       pg_size_pretty(pg_database_size(current_database()))
            """)
            db, role, version, size = cur.fetchone()
            report["database"] = {
                "database": db, "role": role, "version": version,
                "size": size,
            }

            for table in TABLES:
                report["checks"]["rows_" + table] = scalar(
                    cur, "SELECT count(*) FROM public." + table
                )

            for name, sql in SQL_CHECKS.items():
                value = scalar(cur, sql)
                report["checks"][name] = value
                if value:
                    failures.append(name)

            # These are diagnostics, not automatic pass/fail conditions.
            report["diagnostics"]["tr_g0_occurrences"] = scalar(
                cur, "SELECT count(*) FROM gnt_words WHERE strongs = 'G0'"
            )
            report["diagnostics"]["unparsed_morphology_patterns"] = scalar(
                cur, "SELECT count(*) FROM morph_patterns WHERE parse_status = 'unparsed'"
            )
            cur.execute("""
                SELECT language, count(*) FROM strongs
                GROUP BY language ORDER BY language
            """)
            report["diagnostics"]["strongs_dictionary_languages"] = [
                {"language": row[0], "rows": row[1]} for row in cur.fetchall()
            ]
            report["diagnostics"]["sbl_words_with_exact_lxx_lemma_gloss_match"] = scalar(
                cur, """
                    SELECT count(*) FROM gnts_words s
                    WHERE EXISTS (
                      SELECT 1 FROM lxx_words l
                      WHERE l.lemma = s.lemma
                        AND nullif(trim(l.gloss), '') IS NOT NULL
                    )
                """
            )

            nt_strip = string.punctuation + "".join(
                chr(code) for code in (0x2014, 0x2013, 0x2018, 0x2019, 0x201c, 0x201d)
            )
            ot_strip = nt_strip + "".join(chr(code) for code in (0x00ab, 0x00bb))
            for name, sql in TOKEN_QUERIES.items():
                result = token_check(
                    cur, name, sql, ot_strip if name == "hebrew" else nt_strip
                )
                report["token_checks"][name] = result
                if (
                    result["missing_ylt_text"]
                    or result["out_of_range"]
                    or result["token_mismatches"]
                ):
                    failures.append(name + "_ylt_token_alignment")

            # Focused diagnostic evidence for the two known TR failures.
            cur.execute("""
                SELECT v.book_id, v.chapter, v.verse,
                       a.kjv_pos, a.gnt_position, w.max_position
                FROM gnt_alignment a
                JOIN gnt_verses v ON v.corpus_verse_id = a.corpus_verse_id
                LEFT JOIN (
                  SELECT gnt_verse_id, max(position) AS max_position
                  FROM gnt_words GROUP BY gnt_verse_id
                ) w ON w.gnt_verse_id = v.gnt_verse_id
                WHERE a.gnt_position > coalesce(w.max_position, 0)
                ORDER BY v.book_id, v.chapter, v.verse, a.kjv_pos
            """)
            report["tr_out_of_range_samples"] = [
                dict(zip(
                    ("book_id", "chapter", "verse", "kjv_pos",
                     "gnt_position", "verse_token_count"), row
                ))
                for row in cur.fetchall()
            ]

            for label, book_id, chapter, verse in (
                ("john_9_21", 43, 9, 21),
                ("colossians_4_10", 51, 4, 10),
            ):
                cur.execute("""
                    SELECT v.book_id, v.chapter, v.verse,
                           w.position, w.surface, w.strongs,
                           coalesce(string_agg(y.ylt_word, ' ' ORDER BY y.ylt_word_pos), '') AS ylt
                    FROM gnt_verses v
                    JOIN gnt_words w ON w.gnt_verse_id = v.gnt_verse_id
                    LEFT JOIN gnt_ylt_renderings y
                      ON y.gnt_verse_id = w.gnt_verse_id
                     AND y.gnt_position = w.position
                    WHERE v.book_id = %s AND v.chapter = %s AND v.verse = %s
                    GROUP BY v.book_id, v.chapter, v.verse,
                             w.position, w.surface, w.strongs
                    ORDER BY w.position
                """, (book_id, chapter, verse))
                report[label] = [
                    dict(zip(
                        ("book_id", "chapter", "verse", "position",
                         "surface", "strongs", "ylt"), row
                    ))
                    for row in cur.fetchall()
                ]

        conn.rollback()
    finally:
        conn.close()

    report["structural_failures"] = sorted(set(failures))
    print(json.dumps(report, ensure_ascii=False, indent=2, default=str))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
