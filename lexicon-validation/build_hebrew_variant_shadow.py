#!/usr/bin/env python3
"""Build the Hebrew/Aramaic vowel-variant relation in an isolated shadow DB only."""
import collections
import hashlib
import json
import unicodedata
import psycopg2

DB = "bible_hebrew_variant_shadow_20261107"
SOURCE_SNAPSHOT_ID = "sha256:2ea0a1b12a4335d11393c1baddd1d0e0327f67f70059973f82f52c9bb557a540"
ALGORITHM_VERSION = "nfc-remove-u05b0-u05bb-u05c7-v1"
VOWEL_POINTS = set(range(0x05B0, 0x05BC)) | {0x05C7}

def signature(form):
    return "".join(ch for ch in form if ord(ch) not in VOWEL_POINTS)

def main():
    conn = psycopg2.connect(dbname=DB, user="postgres", host="127.0.0.1")
    conn.set_session(isolation_level="SERIALIZABLE", readonly=False, autocommit=False)
    try:
        groups = collections.defaultdict(lambda: {
            "forms": set(), "members": set(), "occurrences": 0, "root_forms": set()
        })
        scanned = 0
        with conn.cursor(name="variant_source_scan") as cur:
            cur.itersize = 5000
            cur.execute("""
                SELECT word_id, pointed, is_aramaic,
                       root_id, root_form_seq, root_vowel_seq
                FROM public.words
                ORDER BY word_id
            """)
            while True:
                batch = cur.fetchmany(5000)
                if not batch:
                    break
                for word_id, raw, aramaic, root_id, form_seq, vowel_seq in batch:
                    scanned += 1
                    if raw is None or raw == "":
                        continue
                    if aramaic not in (0, 1):
                        raise ValueError(f"Unexpected is_aramaic value: {aramaic!r} on word_id={word_id}")
                    normalized = unicodedata.normalize("NFC", raw)
                    sig = signature(normalized)
                    if not sig:
                        continue
                    key = (bool(aramaic), sig)
                    g = groups[key]
                    g["forms"].add(normalized)
                    g["members"].add((root_id, form_seq, vowel_seq))
                    g["root_forms"].add((root_id, form_seq))
                    g["occurrences"] += 1

        candidates = {
            key: value for key, value in groups.items()
            if len(value["forms"]) >= 2
        }
        member_keys = sorted({member for g in candidates.values() for member in g["members"]})
        if scanned != 264217 or len(candidates) != 3349:
            raise AssertionError(f"Snapshot mismatch: scanned={scanned}, groups={len(candidates)}")

        # Validate all member parents before creating any relation rows.
        with conn.cursor() as cur:
            cur.execute("""
                SELECT root_id, root_form_seq, vowel_seq, vowel_pattern
                FROM public.root_vowel
                WHERE (root_id, root_form_seq, vowel_seq) IN %s
            """, (tuple(member_keys),))
            root_vowels = {
                (r, f, v): pattern for r, f, v, pattern in cur.fetchall()
            }
            if set(root_vowels) != set(member_keys):
                raise AssertionError(f"Missing root_vowel members: {len(set(member_keys)-set(root_vowels))}")
            cur.execute("""
                SELECT root_id, root_form_seq, vowel_seq
                FROM public.lexicon
                WHERE (root_id, root_form_seq, vowel_seq) IN %s
            """, (tuple(member_keys),))
            lexicon_keys = set(cur.fetchall())
            if lexicon_keys != set(member_keys):
                raise AssertionError(f"Missing lexicon members: {len(set(member_keys)-lexicon_keys)}")
            for (language, sig), g in candidates.items():
                for key in g["members"]:
                    if signature(unicodedata.normalize("NFC", root_vowels[key])) != sig:
                        raise AssertionError(f"Member signature mismatch: {key} in {sig!r}")

        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE public.hebrew_vowel_variant_group (
                    variant_group_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                    is_aramaic BOOLEAN NOT NULL,
                    non_vowel_signature TEXT NOT NULL,
                    normalization_form TEXT NOT NULL DEFAULT 'NFC'
                        CHECK (normalization_form = 'NFC'),
                    algorithm_version TEXT NOT NULL,
                    source_snapshot_id TEXT NOT NULL,
                    source_relation TEXT NOT NULL DEFAULT 'public.words.pointed',
                    review_status TEXT NOT NULL DEFAULT 'candidate'
                        CHECK (review_status IN ('candidate','reviewed','rejected','superseded')),
                    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                    UNIQUE (is_aramaic, non_vowel_signature, algorithm_version, source_snapshot_id),
                    UNIQUE (variant_group_id, is_aramaic, algorithm_version, source_snapshot_id)
                )
            """)
            cur.execute("""
                CREATE TABLE public.hebrew_vowel_variant_member (
                    variant_group_id BIGINT NOT NULL,
                    is_aramaic BOOLEAN NOT NULL,
                    algorithm_version TEXT NOT NULL,
                    source_snapshot_id TEXT NOT NULL,
                    root_id BIGINT NOT NULL,
                    root_form_seq BIGINT NOT NULL,
                    vowel_seq BIGINT NOT NULL,
                    PRIMARY KEY (variant_group_id, root_id, root_form_seq, vowel_seq),
                    UNIQUE (is_aramaic, algorithm_version, source_snapshot_id,
                            root_id, root_form_seq, vowel_seq),
                    FOREIGN KEY (variant_group_id, is_aramaic, algorithm_version, source_snapshot_id)
                        REFERENCES public.hebrew_vowel_variant_group
                            (variant_group_id, is_aramaic, algorithm_version, source_snapshot_id),
                    FOREIGN KEY (root_id, root_form_seq, vowel_seq)
                        REFERENCES public.root_vowel(root_id, root_form_seq, vowel_seq)
                )
            """)
            cur.execute("""
                CREATE INDEX hebrew_vowel_variant_member_root_idx
                ON public.hebrew_vowel_variant_member(root_id, root_form_seq, vowel_seq)
            """)
            cur.execute("""
                CREATE INDEX hebrew_vowel_variant_group_signature_idx
                ON public.hebrew_vowel_variant_group(is_aramaic, non_vowel_signature)
            """)

            expected_occurrences = 0
            member_total = 0
            cross_root_total = 0
            for (language, sig), g in sorted(candidates.items(), key=lambda x:(x[0][0],x[0][1])):
                cur.execute("""
                    INSERT INTO public.hebrew_vowel_variant_group
                        (is_aramaic, non_vowel_signature, algorithm_version, source_snapshot_id)
                    VALUES (%s,%s,%s,%s)
                    RETURNING variant_group_id
                """, (language, sig, ALGORITHM_VERSION, SOURCE_SNAPSHOT_ID))
                group_id = cur.fetchone()[0]
                rows = [
                    (group_id, language, ALGORITHM_VERSION, SOURCE_SNAPSHOT_ID, *key)
                    for key in sorted(g["members"])
                ]
                cur.executemany("""
                    INSERT INTO public.hebrew_vowel_variant_member
                    (variant_group_id,is_aramaic,algorithm_version,source_snapshot_id,
                     root_id,root_form_seq,vowel_seq)
                    VALUES (%s,%s,%s,%s,%s,%s,%s)
                """, rows)
                expected_occurrences += g["occurrences"]
                member_total += len(rows)
                cross_root_total += len(g["root_forms"]) > 1

        conn.commit()
        print(json.dumps({
            "database": DB,
            "source_snapshot_id": SOURCE_SNAPSHOT_ID,
            "algorithm_version": ALGORITHM_VERSION,
            "source_rows_scanned": scanned,
            "groups_inserted": len(candidates),
            "members_inserted": member_total,
            "candidate_occurrences": expected_occurrences,
            "cross_root_groups": cross_root_total,
            "database_modified": True,
            "production_database_modified": False,
            "source_tables_modified": False
        }, ensure_ascii=False, indent=2))
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    main()
