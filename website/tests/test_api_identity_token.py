import base64
import json
import os
import sys
import time
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import app_v2 as mod


class FakeDB:
    def execute(self, sql, params=()):
        if "FROM user_accounts WHERE user_id=" in sql:
            return Cursor({
                "user_id": int(params[0]), "username": "tester",
                "display_name": "Tester", "is_active": 1,
            })
        raise AssertionError("Unexpected SQL: " + sql)


class Cursor:
    def __init__(self, row):
        self.row = row
    def fetchone(self):
        return self.row


class ApiIdentityTokenTests(unittest.TestCase):
    def setUp(self):
        self.db_patch = patch.object(mod, "appdb", return_value=FakeDB())
        self.db_patch.start()
        self.env_patch = patch.dict(os.environ, {
            "BIBLEAPP_IDENTITY_TOKEN_SECRET": "test-identity-secret-32-bytes-minimum",
            "BIBLEAPP_ALLOWED_ORIGINS": "https://reader.example",
        })
        self.env_patch.start()
        self.client = mod.app.test_client()
        mod.app.config.update(TESTING=True)

    def tearDown(self):
        self.env_patch.stop()
        self.db_patch.stop()

    def login(self, csrf="csrf-test-token"):
        with self.client.session_transaction() as sess:
            sess["user_id"] = 42
            sess["_csrf_token"] = csrf

    def decode(self, token):
        header, payload, signature = token.split(".")
        return (
            json.loads(base64.urlsafe_b64decode(header + "=" * (-len(header) % 4))),
            json.loads(base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4))),
            signature,
        )

    def test_csrf_bootstrap_requires_active_session_and_returns_no_store(self):
        response = self.client.get(
            "/api/auth/csrf", headers={"Origin": "https://reader.example"})
        self.assertEqual(response.status_code, 401)
        self.login()
        response = self.client.get(
            "/api/auth/csrf", headers={"Origin": "https://reader.example"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["csrf_token"], "csrf-test-token")
        self.assertEqual(response.headers["Cache-Control"], "no-store")
        self.assertEqual(response.headers["Access-Control-Allow-Origin"],
                         "https://reader.example")
        self.assertEqual(response.headers["Access-Control-Allow-Credentials"], "true")

    def test_token_rejects_missing_session_and_bad_csrf(self):
        headers = {"Origin": "https://reader.example"}
        self.assertEqual(self.client.post("/api/auth/token", headers=headers).status_code, 401)
        self.login()
        self.assertEqual(self.client.post("/api/auth/token", headers=headers).status_code, 400)

    def test_token_rejects_unapproved_origin(self):
        self.login()
        response = self.client.post("/api/auth/token", headers={
            "Origin": "https://attacker.example",
            "X-CSRF-Token": "csrf-test-token",
        })
        self.assertEqual(response.status_code, 403)

    def test_token_contains_expected_identity_and_five_minute_expiry(self):
        self.login()
        response = self.client.post("/api/auth/token", headers={
            "Origin": "https://reader.example",
            "X-CSRF-Token": "csrf-test-token",
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["token_type"], "Bearer")
        self.assertEqual(response.json["expires_in"], 300)
        self.assertEqual(response.headers["Cache-Control"], "no-store")
        header, claims, signature = self.decode(response.json["access_token"])
        self.assertEqual(header, {"alg": "HS256", "typ": "JWT"})
        self.assertEqual(claims["iss"], "bibleapp-flask")
        self.assertEqual(claims["aud"], "bibleapp-api")
        self.assertEqual(claims["sub"], "42")
        self.assertEqual(claims["exp"] - claims["iat"], 300)
        self.assertGreaterEqual(claims["exp"], int(time.time()))
        self.assertGreaterEqual(len(claims["jti"]), 16)
        self.assertTrue(signature)

    def test_missing_signing_secret_fails_closed(self):
        self.login()
        with patch.dict(os.environ, {"BIBLEAPP_IDENTITY_TOKEN_SECRET": ""}):
            response = self.client.post("/api/auth/token", headers={
                "Origin": "https://reader.example",
                "X-CSRF-Token": "csrf-test-token",
            })
        self.assertEqual(response.status_code, 503)


if __name__ == "__main__":
    unittest.main()
