#!/bin/bash
cat bible-tables.zip.part-* > bible-tables.zip
unzip -o bible-tables.zip
for f in tables/*.sql; do sqlite3 bible.db < "$f"; done
echo "bible.db rebuilt"
