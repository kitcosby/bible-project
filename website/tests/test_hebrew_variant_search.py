import json
import os
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import app_v2 as mod


class Cursor:
    def __init__(self, rows=None):
        self.rows = rows or []

    def fetchall(self):
        return self.rows


class FakeVariantDB:
    def __init__(self, exact_rows, semantic_rows):
        self.exact_rows = exact_rows
        self.semantic_rows = semantic_rows
        self.statements = []
        self.fail_exact = None

    def execute(self, statement, params=()):
        self.statements.append((statement, params))
        if "FROM word_variants v" in statement and self.fail_exact is not None:
            raise self.fail_exact
        if statement.startswith("SET ivfflat.probes"):
            return Cursor()
        if "e.embedding" in statement:
            return Cursor(self.semantic_rows)
        if "FROM word_variants v" in statement:
            return Cursor(self.exact_rows)
        raise AssertionError("Unexpected SQL: " + statement)


class FakeEmbeddingResponse:
    def __init__(self, prompt, dimensions=768):
        self.prompt = prompt
        self.dimensions = dimensions

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return json.dumps({"embedding": [0.0] * self.dimensions}).encode("utf-8")


def result_row(word_id, variant_seq, spelling, score_marker=None):
    row = {
        "word_id": word_id,
        "variant_seq": variant_seq,
        "spelling": spelling,
        "letters": spelling,
        "unpointed": spelling,
        "variant_text": "",
        "variant_kind": "spelling",
        "variant_source": "OSHB",
        "witness": "MT",
        "convention": "test",
        "variant_type": "spelling",
        "basis": "test",
        "pointed": "בְּרֵאשִׁית",
        "strongs": "H7225",
        "word_pos": 1,
        "book_id": 1,
        "chapter": 1,
        "verse": 1,
        "name_en": "Genesis",
    }
    if score_marker is not None:
        row["score"] = score_marker
    return row


class HebrewVariantSearchTests(unittest.TestCase):
    def setUp(self):
        self.exact = result_row(1, 1, "בראשית")
        self.semantic_duplicate = result_row(1, 2, "בראשית", 0.99)
        self.semantic_neighbor = result_row(2, 1, "ברא", 0.77)
        self.db = FakeVariantDB(
            [self.exact],
            [self.semantic_duplicate, self.semantic_neighbor],
        )
        self.db_patch = patch.object(mod, "variant_search_db", return_value=self.db)
        self.db_patch.start()
        self.config_patch = patch.object(
            mod, "BIBLE_VARIANT_SEARCH_DATABASE_URL", "postgresql://stage-search"
        )
        self.config_patch.start()
        self.client = mod.app.test_client()
        mod.app.config.update(TESTING=True)

    def tearDown(self):
        self.config_patch.stop()
        self.db_patch.stop()

    def test_exact_matches_precede_deduplicated_embedding_neighbors(self):
        captured = {}

        def fake_urlopen(request, timeout=0):
            captured["payload"] = json.loads(request.data.decode("utf-8"))
            return FakeEmbeddingResponse(captured["payload"]["prompt"])

        with patch("urllib.request.urlopen", side_effect=fake_urlopen):
            response = self.client.get(
                "/api/search/variants?q=%D7%91%D6%BC%D6%B0%D7%A8%D6%B5%D7%90%D7%A9%D7%81%D6%B4%D7%99%D7%AA"
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["Cache-Control"], "no-store")
        self.assertEqual(captured["payload"]["model"], "nomic-embed-text:latest")
        self.assertEqual(captured["payload"]["prompt"], "בראשית")
        self.assertEqual(len(response.json), 2)
        self.assertEqual(response.json[0]["match_type"], "exact")
        self.assertEqual(response.json[0]["ref"], "Genesis 1:1")
        self.assertIsNone(response.json[0]["score"])
        self.assertEqual(response.json[1]["match_type"], "embedding")
        self.assertEqual(response.json[1]["spelling"], "ברא")
        self.assertEqual(response.json[1]["score"], 0.77)
        self.assertEqual(response.json[1]["source"], "hebrew-variant-embedding")

    def test_non_hebrew_query_is_rejected_before_embedding(self):
        with patch("urllib.request.urlopen") as urlopen:
            response = self.client.get("/api/search/variants?q=creation")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.headers['Cache-Control'], 'no-store')
        urlopen.assert_not_called()

    def test_exact_matches_survive_embedding_service_outage(self):
        with patch("urllib.request.urlopen", side_effect=OSError("Ollama offline")):
            response = self.client.get("/api/search/variants?q=בראשית")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["Cache-Control"], "no-store")
        self.assertEqual(
            response.headers["X-Hebrew-Semantic-Search"], "unavailable"
        )
        self.assertEqual(
            response.headers["Access-Control-Expose-Headers"],
            "X-Hebrew-Semantic-Search",
        )
        self.assertEqual(len(response.json), 1)
        self.assertEqual(response.json[0]["match_type"], "exact")
        self.assertIsNone(response.json[0]["score"])


    def test_error_responses_all_carry_no_store(self):
        cases = [
            ("non-Hebrew 400", lambda: self.client.get("/api/search/variants?q=creation")),
            ("database 503", self._database_failure_response),
            ("embedding dimension 502", self._dimension_failure_response),
        ]
        for label, make_response in cases:
            with self.subTest(label=label):
                response = make_response()
                self.assertIn(response.status_code, (400, 502, 503))
                self.assertEqual(response.headers.get("Cache-Control"), "no-store")

    def _database_failure_response(self):
        self.db.fail_exact = RuntimeError("postgres://admin:super-secret-token@db.internal/search")
        return self.client.get("/api/search/variants?q=בראשית")

    def _dimension_failure_response(self):
        self.db.exact_rows = []
        with patch("urllib.request.urlopen", return_value=FakeEmbeddingResponse("בראשית", 512)):
            return self.client.get("/api/search/variants?q=בראשית")

    def test_database_exception_does_not_leak_secret_or_internal_detail(self):
        secret = "postgres://admin:super-secret-token@db.internal/search"
        self.db.fail_exact = RuntimeError(secret)
        response = self.client.get("/api/search/variants?q=בראשית")
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json, {"error": "Hebrew variant search unavailable"})
        self.assertNotIn(secret, response.get_data(as_text=True))
        self.assertNotIn("db.internal", response.get_data(as_text=True))
        self.assertEqual(response.headers.get("Cache-Control"), "no-store")

    def test_wrong_embedding_dimension_returns_generic_502(self):
        self.db.exact_rows = []
        with patch("urllib.request.urlopen", return_value=FakeEmbeddingResponse("בראשית", 512)):
            response = self.client.get("/api/search/variants?q=בראשית")
        self.assertEqual(response.status_code, 502)
        self.assertEqual(response.json, {"error": "unexpected embedding dimensions"})
        self.assertEqual(response.headers.get("Cache-Control"), "no-store")

    def test_limit_is_clamped_to_one_and_twenty_five_and_honors_two(self):
        self.db.exact_rows = [
            result_row(i, 1, f"בראשית{i}") for i in range(1, 31)
        ]
        self.db.semantic_rows = []
        with patch("urllib.request.urlopen", return_value=FakeEmbeddingResponse("בראשית")):
            zero = self.client.get("/api/search/variants?q=בראשית&limit=0")
            two = self.client.get("/api/search/variants?q=בראשית&limit=2")
            large = self.client.get("/api/search/variants?q=בראשית&limit=999")
        self.assertEqual(len(zero.json), 1)
        self.assertEqual(len(two.json), 2)
        self.assertEqual(len(large.json), 25)
        exact_limits = [
            params[-1] for statement, params in self.db.statements
            if "FROM word_variants v" in statement
        ]
        semantic_limits = [
            params[-1] for statement, params in self.db.statements
            if "e.embedding" in statement
        ]
        self.assertEqual(exact_limits[-3:], [1, 2, 25])
        self.assertEqual(semantic_limits[-3:], [3, 6, 75])

    def test_three_hundred_hebrew_characters_are_accepted(self):
        query = "א" * 300
        captured = {}

        def fake_urlopen(request, timeout=0):
            captured["prompt"] = json.loads(request.data.decode("utf-8"))["prompt"]
            return FakeEmbeddingResponse(query)

        self.db.exact_rows = []
        with patch("urllib.request.urlopen", side_effect=fake_urlopen):
            response = self.client.get("/api/search/variants?q=" + query)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(captured["prompt"], query)
        self.assertEqual(len(captured["prompt"]), 300)
        self.assertEqual(response.headers.get("Cache-Control"), "no-store")

    def test_missing_variant_database_configuration_fails_closed(self):
        with patch.object(mod, "BIBLE_VARIANT_SEARCH_DATABASE_URL", None):
            with patch("urllib.request.urlopen") as urlopen:
                response = self.client.get("/api/search/variants?q=בראשית")
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.headers["Cache-Control"], "no-store")
        urlopen.assert_not_called()


if __name__ == "__main__":
    unittest.main()
