import os
import sys
import unittest
from unittest.mock import patch
from werkzeug.security import generate_password_hash

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import app_v2 as mod


class Cursor:
    def __init__(self, row=None):
        self.row = row

    def fetchone(self):
        return self.row


class FakeDB:
    def __init__(self):
        self.users = {}
        self.next_id = 1

    def execute(self, sql, params=()):
        q = " ".join(sql.lower().split())
        if q.startswith("select * from user_accounts where username="):
            row = self.users.get(params[0])
            return Cursor(dict(row) if row and row["is_active"] == 1 else None)
        if q.startswith("select * from user_accounts where user_id="):
            row = next((u for u in self.users.values()
                        if u["user_id"] == params[0]), None)
            return Cursor(dict(row) if row and row["is_active"] == 1 else None)
        if q.startswith("insert into user_accounts"):
            username, password_hash, display_name = params
            if username in self.users:
                raise mod.psycopg2.IntegrityError("duplicate username")
            row = {"user_id": self.next_id, "username": username,
                   "password_hash": password_hash, "display_name": display_name,
                   "is_active": 1}
            self.users[username] = row
            self.next_id += 1
            return Cursor({"user_id": row["user_id"]})
        if q.startswith("update user_accounts set last_login_at"):
            return Cursor()
        raise AssertionError("Unexpected SQL: " + q)

    def commit(self):
        pass

    def rollback(self):
        pass


class JsonAuthTests(unittest.TestCase):
    def setUp(self):
        self.db = FakeDB()
        self.db.users["legacy"] = {
            "user_id": 41, "username": "legacy",
            "password_hash": generate_password_hash("legacy-password"),
            "display_name": "Legacy", "is_active": 1,
        }
        self.db_patch = patch.object(mod, "appdb", return_value=self.db)
        self.db_patch.start()
        self.env_patch = patch.dict(os.environ, {
            "BIBLEAPP_ALLOWED_ORIGINS": "https://reader.example",
            "BIBLEAPP_IDENTITY_TOKEN_SECRET": "test-identity-secret-32-bytes-minimum",
        })
        self.env_patch.start()
        mod.app.config.update(TESTING=True)
        self.client = mod.app.test_client()
        self.origin = {"Origin": "https://reader.example"}

    def tearDown(self):
        self.env_patch.stop()
        self.db_patch.stop()

    def bootstrap(self):
        response = self.client.get("/api/auth/bootstrap", headers=self.origin)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["Cache-Control"], "no-store")
        self.assertFalse(response.json["authenticated"])
        self.assertTrue(response.json["csrf_token"])
        return response.json["csrf_token"]

    def test_pre_auth_bootstrap_and_origin_scoped_preflight(self):
        csrf = self.bootstrap()
        response = self.client.options("/api/auth/login", headers={
            **self.origin,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type,x-csrf-token",
        })
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.headers["Access-Control-Allow-Origin"],
                         "https://reader.example")
        self.assertIn("X-CSRF-Token",
                      response.headers["Access-Control-Allow-Headers"])
        self.assertTrue(csrf)

    def test_login_preserves_legacy_hash_and_rotates_csrf(self):
        csrf = self.bootstrap()
        response = self.client.post("/api/auth/login", headers={
            **self.origin, "X-CSRF-Token": csrf,
        }, json={"username": "legacy", "password": "legacy-password"})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json["authenticated"])
        self.assertEqual(response.json["user"]["user_id"], 41)
        self.assertNotEqual(response.json["csrf_token"], csrf)
        with self.client.session_transaction() as sess:
            self.assertEqual(sess["user_id"], 41)
            self.assertTrue(sess.permanent)

    def test_signup_enforces_policy_and_creates_existing_account_type(self):
        csrf = self.bootstrap()
        short = self.client.post("/api/auth/signup", headers={
            **self.origin, "X-CSRF-Token": csrf,
        }, json={"username": "newuser", "password": "short"})
        self.assertEqual(short.status_code, 400)
        self.assertNotIn("newuser", self.db.users)
        response = self.client.post("/api/auth/signup", headers={
            **self.origin, "X-CSRF-Token": csrf,
        }, json={"username": "newuser", "password": "a-long-enough-passphrase"})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json["user"]["username"], "newuser")
        with self.client.session_transaction() as sess:
            self.assertEqual(sess["user_id"], self.db.users["newuser"]["user_id"])

    def test_mutations_reject_bad_csrf_and_unapproved_origin(self):
        csrf = self.bootstrap()
        bad = self.client.post("/api/auth/login", headers=self.origin,
                               json={"username": "legacy",
                                     "password": "legacy-password"})
        self.assertEqual(bad.status_code, 400)
        denied = self.client.post("/api/auth/login", headers={
            "Origin": "https://attacker.example", "X-CSRF-Token": csrf,
        }, json={"username": "legacy", "password": "legacy-password"})
        self.assertEqual(denied.status_code, 403)

    def test_logout_clears_session_and_rotates_pre_auth_csrf(self):
        csrf = self.bootstrap()
        logged_in = self.client.post("/api/auth/login", headers={
            **self.origin, "X-CSRF-Token": csrf,
        }, json={"username": "legacy", "password": "legacy-password"})
        csrf2 = logged_in.json["csrf_token"]
        response = self.client.post("/api/auth/logout", headers={
            **self.origin, "X-CSRF-Token": csrf2,
        }, json={})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json["authenticated"])
        self.assertNotEqual(response.json["csrf_token"], csrf2)
        with self.client.session_transaction() as sess:
            self.assertNotIn("user_id", sess)

    def test_token_exchange_after_login_and_denied_after_logout(self):
        csrf = self.bootstrap()
        logged_in = self.client.post("/api/auth/login", headers={
            **self.origin, "X-CSRF-Token": csrf,
        }, json={"username": "legacy", "password": "legacy-password"})
        csrf2 = logged_in.json["csrf_token"]
        token = self.client.post("/api/auth/token", headers={
            **self.origin, "X-CSRF-Token": csrf2,
        })
        self.assertEqual(token.status_code, 200)
        self.assertEqual(token.json["expires_in"], 300)
        logged_out = self.client.post("/api/auth/logout", headers={
            **self.origin, "X-CSRF-Token": csrf2,
        }, json={})
        denied = self.client.post("/api/auth/token", headers={
            **self.origin, "X-CSRF-Token": logged_out.json["csrf_token"],
        })
        self.assertEqual(denied.status_code, 401)




class RowsCursor:
    def __init__(self, rows):
        self.rows = rows

    def fetchall(self):
        return self.rows


class FakeCorpus:
    def __init__(self, rows):
        self.rows = rows
        self.calls = []

    def execute(self, sql, params=()):
        self.calls.append((sql, params))
        return RowsCursor(self.rows)


class WordOptionsTests(unittest.TestCase):
    def setUp(self):
        self.client = mod.app.test_client()

    def test_word_options_returns_occurrence_lemma_and_exact_phrase_groups(self):
        rows = [
            {"word_id": 10, "strongs": "H430", "root_code": "10.1.1"},
            {"word_id": 11, "strongs": None, "root_code": "11.1.2"},
        ]
        corpus = FakeCorpus(rows)
        phrase_maps = (
            {"H430": ["God", "gods"], "root:11.1.2": ["a root rendering"]},
            {},
            {"H430": ["Gods"], "root:11.1.2": ["root Young's"]},
            {},
        )
        with patch.object(mod, "bible", return_value=corpus), \
             patch.object(mod, "lemma_phrases", return_value=phrase_maps):
            response = self.client.get("/api/word-options?wordIds=11,10,10")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(corpus.calls[0][1], ([10, 11],))
        self.assertIn("ANY(%s)", corpus.calls[0][0])
        self.assertEqual(response.json["words"], [
            {"wid": 10, "lemma": "H430", "strongs": "H430",
             "kjv_phrases": ["God", "gods"], "ylt_phrases": ["Gods"]},
            {"wid": 11, "lemma": "root:11.1.2", "strongs": None,
             "kjv_phrases": ["a root rendering"], "ylt_phrases": ["root Young's"]},
        ])

    def test_word_options_rejects_invalid_or_oversized_ids_before_query(self):
        corpus = FakeCorpus([])
        with patch.object(mod, "bible", return_value=corpus):
            bad = self.client.get("/api/word-options?wordIds=0")
            too_many = self.client.get("/api/word-options?wordIds=" +
                                       ",".join(str(i) for i in range(1, 102)))
        self.assertEqual(bad.status_code, 400)
        self.assertEqual(too_many.status_code, 400)
        self.assertEqual(corpus.calls, [])

if __name__ == "__main__":
    unittest.main()
