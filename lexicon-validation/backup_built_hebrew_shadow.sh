#!/usr/bin/env bash
# Create and validate a custom-format backup of the built isolated Hebrew shadow DB.
set -euo pipefail

DB=bible_hebrew_variant_shadow_20261107
OUT=/var/tmp/bible-hebrew-variant-shadow-built-20261107.dump

runuser -u postgres -- pg_dump --format=custom --compress=6 --no-owner --no-acl \
  --host=127.0.0.1 --username=postgres --file="$OUT" "$DB"

sha256sum "$OUT"
pg_restore --list "$OUT" > "$OUT.list"
wc -l "$OUT.list"
ls -lh "$OUT" "$OUT.list"
