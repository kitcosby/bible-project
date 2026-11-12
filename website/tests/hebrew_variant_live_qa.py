#!/usr/bin/env python3
"""Read-only live API and pgvector QA for Hebrew spelling-variant search.

Defaults target Lampy staging only. No database writes are issued.
"""
import json
import os
import socket
import time
import unittest
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

API_BASE = os.environ.get("BIBLE_VARIANT_QA_API_BASE", "http://127.0.0.1:5058").rstrip("/")
OLLAMA_BASE = os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434").rstrip("/")
ENV_FILE = Path(os.environ.get("BIBLE_VARIANT_QA_ENV_FILE", "/root/bible_app_pwa_stage_20261109.env"))


def load_staging_env():
    if not ENV_FILE.is_file():
        return
    for raw in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip("'").strip('"'))


def can_connect(url):
    parsed = urllib.parse.urlparse(url)
    try:
        with socket.create_connection((parsed.hostname, parsed.port or (443 if parsed.scheme == "https" else 80)), timeout=1.5):
            return True
    except OSError:
        return False


def ollama_ready():
    try:
        with urllib.request.urlopen(OLLAMA_BASE + "/api/tags", timeout=2) as response:
            return response.status == 200
    except Exception:
        return False


load_staging_env()
API_READY = can_connect(API_BASE)
OLLAMA_READY = ollama_ready()
LIVE_READY = API_READY and OLLAMA_READY
BLOCK_REASON = (
    "BLOCKED: staging Flask at %s is unreachable" % API_BASE if not API_READY
    else "BLOCKED: Ollama at %s is unreachable" % OLLAMA_BASE
)


def http_get(path):
    request = urllib.request.Request(API_BASE + path, headers={"Accept": "application/json"})
    started = time.perf_counter()
    try:
        response = urllib.request.urlopen(request, timeout=60)
        status = response.status
        headers = response.headers
        body = response.read()
    except urllib.error.HTTPError as exc:
        status, headers, body = exc.code, exc.headers, exc.read()
    elapsed = time.perf_counter() - started
    try:
        payload = json.loads(body.decode("utf-8"))
    except Exception:
        payload = None
    return status, headers, payload, elapsed, body.decode("utf-8", "replace")


def search(query, limit=25):
    return http_get("/api/search/variants?q=" + urllib.parse.quote(query) + "&limit=" + str(limit))


def exact_identity_set(payload):
    return sorted((row.get("word_id"), row.get("spelling")) for row in payload
                  if row.get("match_type") == "exact")


@unittest.skipUnless(LIVE_READY, BLOCK_REASON)
class LiveHebrewVariantApiTests(unittest.TestCase):
    def test_00_latency_cold_and_warm_record(self):
        cold = search("בראשית")
        warm = search("בראשית")
        self.assertEqual(cold[0], 200, cold[4])
        self.assertEqual(warm[0], 200, warm[4])
        flags = []
        if warm[3] > 10:
            flags.append("warm exceeds 10 seconds")
        if cold[3] > 45:
            flags.append("cold exceeds 45 seconds")
        print("LATENCY cold=%.3fs warm=%.3fs flags=%s" %
              (cold[3], warm[3], ",".join(flags) if flags else "none"))

    def test_01_pointed_unpointed_and_cantillation_normalize_to_same_exact_set(self):
        forms = ["בראשית", "בְּרֵאשִׁית", "בְּרֵאשִׁ֖ית"]
        sets = []
        for form in forms:
            status, headers, payload, _, body = search(form)
            self.assertEqual(status, 200, body)
            self.assertIsInstance(payload, list)
            sets.append(exact_identity_set(payload))
        self.assertTrue(sets[0], "unpointed form should have exact matches")
        self.assertEqual(sets[1], sets[0])
        self.assertEqual(sets[2], sets[0])

    def test_02_final_and_medial_mem_are_distinct_exact_conventions(self):
        final = search("שלום")
        medial = search("שלומ")
        self.assertEqual(final[0], 200, final[4])
        self.assertEqual(medial[0], 200, medial[4])
        final_rows = [r for r in final[2] if r.get("match_type") == "exact"]
        medial_rows = [r for r in medial[2] if r.get("match_type") == "exact"]
        self.assertTrue(final_rows, "final-form query returned no exact rows")
        self.assertTrue(medial_rows, "medial-form query returned no exact rows")
        self.assertEqual({r["spelling"] for r in final_rows}, {"שלום"})
        self.assertEqual({r["spelling"] for r in medial_rows}, {"שלומ"})
        final_keys = {(r.get("word_id"), r.get("variant_seq")) for r in final_rows}
        medial_keys = {(r.get("word_id"), r.get("variant_seq")) for r in medial_rows}
        self.assertTrue(final_keys.isdisjoint(medial_keys), "final-form and medial-form exact rows overlap")

    def test_03_exact_order_scores_and_duplicate_suppression(self):
        status, headers, payload, _, body = search("בראשית")
        self.assertEqual(status, 200, body)
        exact_positions = [i for i, row in enumerate(payload) if row.get("match_type") == "exact"]
        semantic_positions = [i for i, row in enumerate(payload) if row.get("match_type") == "embedding"]
        self.assertTrue(exact_positions, "no exact results")
        self.assertTrue(semantic_positions, "no semantic neighbors")
        self.assertLess(max(exact_positions), min(semantic_positions))
        exact_rows = [r for r in payload if r.get("match_type") == "exact"]
        self.assertEqual(exact_rows[0].get("ref"), "Genesis 1:1")
        self.assertTrue(all(r.get("score") is None for r in exact_rows))
        self.assertTrue(all(isinstance(r.get("score"), (int, float)) for r in payload if r.get("match_type") == "embedding"))
        pairs = [(r.get("word_id"), r.get("spelling")) for r in payload]
        self.assertEqual(len(pairs), len(set(pairs)), "duplicate (word_id, spelling) result")

    def test_04_surrounding_whitespace_preserves_results(self):
        bare = search("בראשית")
        padded = search("  בראשית  ")
        self.assertEqual(bare[0], 200, bare[4])
        self.assertEqual(padded[0], 200, padded[4])
        signature = lambda rows: [
            (r.get("word_id"), r.get("spelling"), r.get("match_type"), r.get("score"))
            for r in rows
        ]
        self.assertEqual(signature(padded[2]), signature(bare[2]))

    def test_05_invalid_queries_have_standard_400_and_no_store(self):
        cases = [
            ("non-Hebrew", "creation", {"error": "Hebrew spelling query required"}),
            ("empty", "", {"error": "q required"}),
            ("whitespace", "   ", {"error": "q required"}),
            ("paseq-only", "׀", {"error": "Hebrew spelling query required"}),
        ]
        for label, query, expected in cases:
            with self.subTest(label=label):
                status, headers, payload, _, body = http_get(
                    "/api/search/variants?q=" + urllib.parse.quote(query)
                )
                self.assertEqual(status, 400, "%s: %s" % (label, body))
                self.assertEqual(payload, expected, "%s: %s" % (label, body))
                self.assertEqual(headers.get("Cache-Control"), "no-store", label)

    def test_06_passage_search_is_unchanged(self):
        status, headers, payload, _, body = http_get("/api/search?q=light")
        self.assertEqual(status, 200, body)
        self.assertIsInstance(payload, list)

    def test_07_ivfflat_top_ten_is_within_exact_distance_boundary(self):
        import psycopg2
        db_url = os.environ.get("BIBLE_VARIANT_SEARCH_DATABASE_URL")
        self.assertTrue(db_url, "staging BIBLE_VARIANT_SEARCH_DATABASE_URL is not configured")
        sql = """
            SELECT word_id, variant_seq, embedding <=> %s::vector AS distance
            FROM word_variant_embeddings
            ORDER BY embedding <=> %s::vector
            LIMIT 10
        """
        connection = psycopg2.connect(db_url, connect_timeout=10)
        try:
            connection.set_session(readonly=True, autocommit=False)
            with connection.cursor() as cursor:
                # Do not compare ordered row identities: embeddings use letters alone,
                # so many rows with identical letters forms have exact distance ties.
                # Scan plans may choose different members/order within those tie masses.
                for query in ("בראשית", "בראשיט"):
                    with self.subTest(query=query):
                        embedding_request = urllib.request.Request(
                            OLLAMA_BASE + "/api/embeddings",
                            data=json.dumps({
                                "model": "nomic-embed-text:latest",
                                "prompt": query,
                            }).encode("utf-8"),
                            headers={"Content-Type": "application/json"},
                        )
                        with urllib.request.urlopen(embedding_request, timeout=45) as response:
                            vector = json.loads(response.read())["embedding"]
                        self.assertEqual(len(vector), 768, "unexpected embedding dimension for " + query)
                        vector_literal = "[" + ",".join(repr(float(value)) for value in vector) + "]"

                        cursor.execute("SET ivfflat.probes = 16")
                        cursor.execute("SET enable_seqscan = off")
                        cursor.execute("EXPLAIN " + sql, (vector_literal, vector_literal))
                        plan = "\n".join(str(row[0]) for row in cursor.fetchall())
                        self.assertIn("Index Scan", plan, "IVFFlat index was not selected for %s: %s" % (query, plan))
                        cursor.execute(sql, (vector_literal, vector_literal))
                        indexed = cursor.fetchall()

                        cursor.execute("SET enable_indexscan = off")
                        cursor.execute("SET enable_bitmapscan = off")
                        cursor.execute("SET enable_seqscan = on")
                        cursor.execute(sql, (vector_literal, vector_literal))
                        sequential = cursor.fetchall()

                        self.assertEqual(len(indexed), 10, "IVFFlat did not return ten rows for " + query)
                        self.assertEqual(len(sequential), 10, "exact scan did not return ten rows for " + query)
                        exact_rank_10_distance = float(sequential[-1][2])
                        tolerance = 1e-6
                        worst_indexed_distance = max(float(row[2]) for row in indexed)
                        self.assertLessEqual(
                            worst_indexed_distance,
                            exact_rank_10_distance + tolerance,
                            "%s: IVFFlat returned a row beyond exact rank-10 distance "
                            "(indexed worst=%.12f, exact boundary=%.12f, tolerance=%.1e)"
                            % (query, worst_indexed_distance, exact_rank_10_distance, tolerance),
                        )
                        print(
                            "IVFFLAT query=%s probes=16 exact_rank10=%.12f indexed_worst=%.12f "
                            "recall_boundary=PASS" %
                            (query, exact_rank_10_distance, worst_indexed_distance)
                        )
        finally:
            connection.rollback()
            connection.close()



if __name__ == "__main__":
    unittest.main(verbosity=2)
