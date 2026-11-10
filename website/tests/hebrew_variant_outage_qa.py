#!/usr/bin/env python3
"""End-to-end Ollama outage regression. Never leaves staging intentionally stopped.

Set OLLAMA_STOP_COMMAND and OLLAMA_START_COMMAND to the actual staging service
manager commands. The script refuses to stop anything without both commands.
"""
import json
import os
import shlex
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

API_BASE = os.environ.get("BIBLE_VARIANT_QA_API_BASE", "http://127.0.0.1:5058").rstrip("/")
OLLAMA_BASE = os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434").rstrip("/")
STOP = os.environ.get("OLLAMA_STOP_COMMAND")
START = os.environ.get("OLLAMA_START_COMMAND")


def reachable(url):
    parsed = urllib.parse.urlparse(url)
    try:
        with socket.create_connection((parsed.hostname, parsed.port or 80), timeout=1.5):
            return True
    except OSError:
        return False


def run_command(command):
    return subprocess.run(command, shell=True, text=True, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, timeout=30, check=False)


def wait_for_ollama(expected, seconds=30):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(OLLAMA_BASE + "/api/tags", timeout=2) as response:
                active = response.status == 200
        except Exception:
            active = False
        if active == expected:
            return True
        time.sleep(0.5)
    return False


def get(path):
    request = urllib.request.Request(API_BASE + path, headers={"Accept": "application/json"})
    try:
        response = urllib.request.urlopen(request, timeout=60)
        status, headers, body = response.status, response.headers, response.read()
    except urllib.error.HTTPError as exc:
        status, headers, body = exc.code, exc.headers, exc.read()
    try:
        payload = json.loads(body.decode("utf-8"))
    except Exception:
        payload = None
    return status, headers, payload, body.decode("utf-8", "replace")


def main():
    if not reachable(API_BASE):
        print("BLOCKED Layer 3: staging Flask is not listening at " + API_BASE)
        return 0
    if not wait_for_ollama(True, seconds=2):
        print("BLOCKED Layer 3: Ollama was already stopped; refusing to change its prior state")
        return 0
    if not STOP or not START:
        print("BLOCKED Layer 3: OLLAMA_STOP_COMMAND and OLLAMA_START_COMMAND must be supplied; no service state changed")
        return 0

    stop_attempted = False
    failure = None
    try:
        stop_attempted = True
        result = run_command(STOP)
        if result.returncode != 0:
            raise RuntimeError("Ollama stop command failed (exit %d)" % result.returncode)
        if not wait_for_ollama(False):
            raise RuntimeError("Ollama did not stop within 30 seconds")

        exact = get("/api/search/variants?q=" + urllib.parse.quote("בראשית"))
        assert exact[0] == 200, "exact-match outage response was %s: %s" % (exact[0], exact[3])
        assert exact[2] and any(row.get("match_type") == "exact" for row in exact[2]), "exact results missing during Ollama outage"
        assert exact[1].get("X-Hebrew-Semantic-Search") == "unavailable", "semantic-unavailable header missing"
        assert exact[1].get("Access-Control-Expose-Headers") == "X-Hebrew-Semantic-Search", "CORS expose header missing"
        assert exact[1].get("Cache-Control") == "no-store", "no-store missing during outage"
        print("PASS exact matches survive Ollama outage with exposed semantic-unavailable header")

        no_exact_query = "א" * 300
        no_exact = get("/api/search/variants?q=" + urllib.parse.quote(no_exact_query))
        assert no_exact[0] == 503, "expected documented 503 with no exact matches; got %s: %s" % (no_exact[0], no_exact[3])
        assert no_exact[2] == {"error": "Hebrew variant embedding search unavailable"}, "unexpected no-exact outage body: %s" % no_exact[3]
        assert no_exact[1].get("Cache-Control") == "no-store", "no-store missing on 503"
        print("PASS no-exact-match query returns documented generic 503 during Ollama outage")
    except Exception as exc:
        failure = str(exc)
        print("FAIL Layer 3: " + failure)
    finally:
        if stop_attempted:
            # A stop command can partially succeed and still exit non-zero.
            # Check the observed service state, not only the command's exit code.
            if not wait_for_ollama(True, seconds=2):
                restored = run_command(START)
                if restored.returncode != 0 or not wait_for_ollama(True, seconds=45):
                    print("FAIL RESTORE: Ollama restart command failed or service did not become healthy")
                    return 2
            print("PASS RESTORE: Ollama is healthy again (or remained healthy)")

    if failure:
        return 1
    resumed = get("/api/search/variants?q=" + urllib.parse.quote("בראשית"))
    if resumed[0] != 200 or resumed[1].get("X-Hebrew-Semantic-Search") == "unavailable":
        print("FAIL RESUME: normal semantic search did not resume: %s %s" % (resumed[0], resumed[3]))
        return 1
    print("PASS RESUME: normal semantic search returned HTTP 200 after Ollama restart")
    return 0


if __name__ == "__main__":
    sys.exit(main())
