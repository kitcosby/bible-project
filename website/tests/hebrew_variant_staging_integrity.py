#!/usr/bin/env python3
"""Read-only staging drift check. This script never restages or restarts services."""
import hashlib
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(os.environ.get("BIBLE_VARIANT_QA_STAGE_ROOT", "/opt/stage"))
API_URL = os.environ.get("BIBLE_VARIANT_QA_API_BASE", "http://127.0.0.1:5058").rstrip("/") + "/api/search/variants?q=" + urllib.parse.quote("בראשית")
EXPECTED = {
    "Flask app_v2.py": ("flask/app_v2.py", "ca35e1314c98832f4840ef1ee2d9cb77471ec9b449ed088ac5844c7382a24205"),
    "PWA index.html": ("pwa/index.html", "9da35996ca6a6db0c107bf43894829d8754732aa03b84c34a587e74d2cede7df"),
    "PWA sw.js": ("pwa/sw.js", "8154f321893373633d219e1e57a703cde5a7a9a35eef65281acc30dcbbbd28ae"),
    # Staging config intentionally differs from branch default; validate its overrides below.
}
failures = 0
blocked = 0
passes = 0


def report(status, label, detail=""):
    global failures, blocked, passes
    print("%s %s%s" % (status, label, (": " + detail) if detail else ""))
    if status == "PASS":
        passes += 1
    elif status == "FAIL":
        failures += 1
    elif status == "BLOCKED":
        blocked += 1


for label, (relative, expected) in EXPECTED.items():
    path = ROOT / relative
    if not path.is_file():
        report("FAIL", label + " exists", str(path))
        continue
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual == expected:
        report("PASS", label + " SHA-256 matches branch head", actual)
    else:
        report("FAIL", label + " SHA-256 mismatch", "staged=%s expected=%s" % (actual, expected))

sw_path = ROOT / "pwa/sw.js"
if sw_path.is_file():
    sw = sw_path.read_text(encoding="utf-8")
    match = re.search(r'const CACHE = "byot-v(\d+)";', sw)
    if match and int(match.group(1)) >= 20 and '/api/search/variants' in sw:
        report("PASS", "service-worker cache version and Hebrew network-only bypass")
    else:
        report("FAIL", "service-worker cache version or Hebrew network-only bypass", "cache=%s" % (match.group(1) if match else "missing"))

config_path = ROOT / "pwa/config.js"
if config_path.is_file():
    config = config_path.read_text(encoding="utf-8")
    if '"/stage-bible"' in config and '"/api-stage"' in config:
        report("PASS", "staging config targets /stage-bible and /api-stage")
    else:
        report("FAIL", "staging config overrides", "required /stage-bible and /api-stage values not found")

try:
    request = urllib.request.Request(API_URL, headers={"Accept": "application/json"})
    with urllib.request.urlopen(request, timeout=60) as response:
        body = json.loads(response.read().decode("utf-8"))
        if response.status == 200 and isinstance(body, list):
            report("PASS", "running Flask process serves variant-search route", "HTTP 200")
        else:
            report("FAIL", "running Flask process serves variant-search route", "HTTP %s" % response.status)
except urllib.error.HTTPError as exc:
    report("FAIL", "running Flask process serves variant-search route", "HTTP %s: %s" % (exc.code, exc.read().decode("utf-8", "replace")))
except urllib.error.URLError as exc:
    report("BLOCKED", "running Flask process serves variant-search route", "staging listener unavailable: %s" % getattr(exc, "reason", exc))
except Exception as exc:
    report("FAIL", "running Flask process serves variant-search route", str(exc))

print("STAGING INTEGRITY COUNTS passes=%d failures=%d blocked=%d" % (passes, failures, blocked))
raise SystemExit(1 if failures else 0)
