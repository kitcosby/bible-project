# bible.db backup 2026-10-06

SQLite database dump of the Bible research database (research complete).

## Contents
- `bible-tables.zip.part-aa`, `bible-tables.zip.part-ab`: split zip of per-table SQL dumps (11 tables, 223MB SQL)
- `SAD-architecture.md`: system-analysis diagrams (context, level-1 DFD, ER diagram)
- `reassemble.sh`: reassembly script

## Reassemble
```bash
cat bible-tables.zip.part-* > bible-tables.zip
unzip bible-tables.zip
for f in tables/*.sql; do sqlite3 bible.db < "$f"; done
```
