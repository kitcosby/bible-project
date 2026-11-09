"""Isolated ownership tests for the legacy Flask translation routes.

Run from the repository root with:
    python -m unittest discover -s website/tests -v

The tests replace appdb() with an in-memory fake and never connect to PostgreSQL.
"""
import os
import sys
import unittest
from unittest.mock import patch

os.environ.setdefault("BIBLEAPP_SESSION_SECRET", "isolated-test-secret-at-least-32-bytes")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import app_v2 as mod


class FakeDB:
    def __init__(self):
        self.users = {
            10: {"user_id": 10, "username": "alice", "display_name": "Alice", "is_active": 1},
            20: {"user_id": 20, "username": "bob", "display_name": "Bob", "is_active": 1},
        }
        self.translations = {
            1: {"translation_id": 1, "name": "KJV", "description": "Built-in",
                "owner_id": None, "user_id": 1, "updated_at": "now"},
            2: {"translation_id": 2, "name": "Young's", "description": "Built-in",
                "owner_id": None, "user_id": 1, "updated_at": "now"},
            100: {"translation_id": 100, "name": "Alice private", "description": "private A",
                  "owner_id": 10, "user_id": 1, "updated_at": "now"},
            200: {"translation_id": 200, "name": "Bob private", "description": "private B",
                  "owner_id": 20, "user_id": 1, "updated_at": "now"},
            300: {"translation_id": 300, "name": "Unassigned legacy", "description": "legacy",
                  "owner_id": None, "user_id": 1, "updated_at": "now"},
        }
        self.calls = []
        self.commits = 0

    def execute(self, sql, params=()):
        q = " ".join(sql.lower().split())
        self.calls.append((q, params))
        if q.startswith("select * from translation where translation_id="):
            return Cursor(self.translations.get(int(params[0])))
        if q.startswith("select * from user_accounts where user_id="):
            row = self.users.get(int(params[0]))
            return Cursor(row if row and row["is_active"] == 1 else None)
        if "from translation t left join user_accounts" in q:
            owner_id = params[0]
            rows = [dict(t, owner_name=(self.users.get(t["owner_id"]) or {}).get("display_name"))
                    for t in self.translations.values()
                    if ((t["owner_id"] is None and
                         ((t["translation_id"] == 1 and t["name"] == "KJV") or
                          (t["translation_id"] == 2 and t["name"] == "Young's"))) or
                        t["owner_id"] == owner_id)]
            return Cursor(rows=rows)
        if q.startswith("select count(*) c from word_choice"):
            return Cursor({"c": 0})
        if q.startswith("select count(*) c from other_option"):
            return Cursor({"c": 0})
        if q.startswith("select * from translation where translation_id=") and "for update" in q:
            return Cursor(self.translations.get(int(params[0])))
        if q.startswith("select user_id from app_user"):
            return Cursor({"user_id": 1})
        if q.startswith("insert into translation"):
            self.calls.append(("translation insert owner", params))
            return Cursor({"translation_id": 900})
        if q.startswith("update translation set updated_at"):
            return Cursor()
        raise AssertionError("Unexpected SQL: " + q)

    def commit(self):
        self.commits += 1

    def rollback(self):
        pass


class Cursor:
    def __init__(self, row=None, rows=None):
        self.row = row
        self.rows = rows
    def fetchone(self):
        return self.row
    def fetchall(self):
        return self.rows if self.rows is not None else []


class TranslationOwnershipTests(unittest.TestCase):
    def setUp(self):
        self.db = FakeDB()
        self.appdb_patch = patch.object(mod, "appdb", lambda: self.db)
        self.appdb_patch.start()
        self.client = mod.app.test_client()
        mod.app.config.update(TESTING=True)

    def tearDown(self):
        self.appdb_patch.stop()

    def login_as(self, user_id, csrf="test-csrf"):
        with self.client.session_transaction() as sess:
            sess["user_id"] = user_id
            sess["_csrf_token"] = csrf

    def test_builtin_translations_are_public_read_only(self):
        with mod.app.test_request_context("/"):
            self.assertEqual(mod.accessible_translation(1)["name"], "KJV")
            self.assertEqual(mod.accessible_translation(2)["name"], "Young's")
            self.assertIsNone(mod.accessible_translation(300))

    def test_private_translation_is_owner_only(self):
        with mod.app.test_request_context("/"):
            mod.session["user_id"] = 10
            self.assertEqual(mod.accessible_translation(100)["owner_id"], 10)
            self.assertIsNone(mod.accessible_translation(200))
        with mod.app.test_request_context("/"):
            mod.session["user_id"] = 20
            self.assertEqual(mod.accessible_translation(200)["owner_id"], 20)
            self.assertIsNone(mod.accessible_translation(100))

    def test_translation_list_excludes_other_users_and_unassigned_rows(self):
        self.login_as(20)
        response = self.client.get("/translations")
        body = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("KJV", body)
        self.assertIn("Bob private", body)
        self.assertNotIn("Alice private", body)
        self.assertNotIn("Unassigned legacy", body)

    def test_anonymous_cannot_create_translation(self):
        response = self.client.post("/translations", data={"name": "No owner"})
        self.assertEqual(response.status_code, 401)
        self.assertFalse(any("insert into translation" in q for q, _ in self.db.calls))

    def test_creation_assigns_server_authenticated_owner(self):
        self.login_as(20)
        response = self.client.post("/translations", data={
            "name": "Bob's new work", "description": "owned",
            "csrf_token": "test-csrf",
        })
        self.assertEqual(response.status_code, 302)
        insert = next(params for q, params in self.db.calls if q == "translation insert owner")
        self.assertEqual(insert[-1], 20)

    def test_choice_requires_login_and_csrf(self):
        anonymous = self.client.post("/choice?t=100", data={"word_id": "5", "item": "1"})
        self.assertEqual(anonymous.status_code, 401)
        self.login_as(10)
        invalid_csrf = self.client.post("/choice?t=100", data={"word_id": "5", "item": "1"})
        self.assertEqual(invalid_csrf.status_code, 400)

    def test_choice_rejects_non_owner_and_builtin_without_writes(self):
        self.login_as(20)
        with patch.object(mod, "word_with_lex", return_value={"word_id": 5}), \
             patch.object(mod, "other_options", return_value=[]), \
             patch.object(mod, "dropdown_items", return_value=[("default", ""), ("KJV: word", "word")]), \
             patch.object(mod, "write_choice") as write:
            denied = self.client.post("/choice?t=100", data={
                "word_id": "5", "item": "1", "csrf_token": "test-csrf",
            })
            builtin = self.client.post("/choice?t=1", data={
                "word_id": "5", "item": "1", "csrf_token": "test-csrf",
            })
            self.assertEqual(denied.status_code, 404)
            self.assertEqual(builtin.status_code, 404)
            write.assert_not_called()

    def test_owner_can_write_choice_in_one_authorized_transaction(self):
        self.login_as(10)
        with patch.object(mod, "word_with_lex", return_value={
                 "word_id": 5, "strongs": "H1", "root_code": "root",
             }), \
             patch.object(mod, "other_options", return_value=[]), \
             patch.object(mod, "dropdown_items", return_value=[
                 ("default", ""), ("KJV: word", "word"),
             ]), \
             patch.object(mod, "write_choice") as write, \
             patch.object(mod, "record_lemma_default") as lemma:
            response = self.client.post("/choice?t=100", data={
                "word_id": "5", "item": "1", "csrf_token": "test-csrf",
            })
        self.assertEqual(response.status_code, 302)
        write.assert_called_once_with(100, 5, 1)
        lemma.assert_called_once()
        self.assertEqual(self.db.commits, 1)
        self.assertTrue(any("for update" in q for q, _ in self.db.calls))

    def test_private_read_and_export_reject_non_owner(self):
        self.login_as(20)
        self.assertEqual(self.client.get("/reading/100/1/1/1").status_code, 404)
        self.assertEqual(self.client.get("/export/100").status_code, 404)


if __name__ == "__main__":
    unittest.main()
