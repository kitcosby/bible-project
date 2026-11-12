#!/usr/bin/env bash
# Restore the verified source snapshot into a new isolated Hebrew variant shadow DB.
# This script does not connect to or modify the production database except through
# the source dump file, which must already exist and match the pinned SHA-256.
set -euo pipefail

DUMP=/var/tmp/bible-hebrew-variant-source-20261107.dump
EXPECTED_SHA256=2ea0a1b12a4335d11393c1baddd1d0e0327f67f70059973f82f52c9bb557a540
DB=bible_hebrew_variant_shadow_20261107

test -f "$DUMP"
printf '%s  %s\n' "$EXPECTED_SHA256" "$DUMP" | sha256sum --check -
pg_restore --list "$DUMP" > "$DUMP.list"

# createdb fails if the target already exists; it will not overwrite a database.
runuser -u postgres -- createdb --host=127.0.0.1 --template=template0 \
  --encoding=UTF8 --lc-collate=C --lc-ctype=C "$DB"

runuser -u postgres -- pg_restore --jobs=4 --exit-on-error --no-owner --no-acl \
  --host=127.0.0.1 --dbname="$DB" "$DUMP"

# Keep the shadow database private to the postgres owner.
runuser -u postgres -- psql -X -h 127.0.0.1 -d postgres -v ON_ERROR_STOP=1 \
  -c "REVOKE CONNECT, TEMPORARY ON DATABASE $DB FROM PUBLIC"

runuser -u postgres -- psql -X -h 127.0.0.1 -d "$DB" -v ON_ERROR_STOP=1 \
  -c "SELECT current_database(), pg_size_pretty(pg_database_size(current_database()))"
