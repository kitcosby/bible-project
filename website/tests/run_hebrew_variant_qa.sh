#!/usr/bin/env bash
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
BACKEND_ROOT="$(cd "$HERE/../.." && pwd)"
PWA_DIR="${PWA_DIR:-$BACKEND_ROOT/../BibleApp-pwa}"
echo "=== Layer 1: Flask mock-based unit tests ==="
(cd "$BACKEND_ROOT" && python3 -m unittest discover -s website/tests -p 'test_hebrew_variant_search.py' -v)
L1=$?
echo "=== Layer 2: live API + staging index battery ==="
python3 "$HERE/hebrew_variant_live_qa.py"
L2=$?
echo "=== Layer 3: Ollama outage / restore regression ==="
python3 "$HERE/hebrew_variant_outage_qa.py"
L3=$?
echo "=== Layer 4: PWA tests (canonical glob invocation) ==="
if [ -d "$PWA_DIR/tests" ]; then
  (cd "$PWA_DIR" && node --test tests/*.test.mjs)
  L4=$?
else
  echo "BLOCKED Layer 4: PWA_DIR does not identify a local BibleApp-pwa checkout"
  L4=0
fi
echo "=== Layer 5: staging integrity / drift checks ==="
python3 "$HERE/hebrew_variant_staging_integrity.py"
L5=$?
echo "=== Runner exit summary ==="
echo "Layer 1 exit=$L1; Layer 2 exit=$L2; Layer 3 exit=$L3; Layer 4 exit=$L4; Layer 5 exit=$L5"
[ "$L1" -eq 0 ] && [ "$L2" -eq 0 ] && [ "$L3" -eq 0 ] && [ "$L4" -eq 0 ] && [ "$L5" -eq 0 ]
