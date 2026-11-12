#!/usr/bin/env python3
"""Rebuild word_variants_embeddings in an ISOLATED database.

Recovery for the 2026-09-30..2026-10-15 data-loss incident (see
NOTATION_LEDGER section 10, EMBEDDING-LOSS entry). The original script
(/usr/local/bin/embed-word-variants.py) no longer exists; this is a
reconstruction from the contemporaneous 2026-09-30 record:

RECOVERED parameters (from the project log of 2026-09-30):
  - model: nomic-embed-text:latest, called via the local Ollama HTTP API
  - output table word_variants_embeddings(word_id, variant_seq, embedding)
  - embedding: 768-dim float32 little-endian, 3,072-byte BLOB
  - resume-safe: skip (word_id, variant_seq) already present
  - commit every 100 rows; progress report every 1,000; abort after
    20 consecutive errors
  - original scope: the 528,565 variant_kind='spelling' rows that existed
    on 2026-09-30 (textual rows arrived later and were never embedded)

RECONSTRUCTION DECISION (not a recovered fact): the original record does
not state which text was embedded per row. This rebuild embeds the
variant's `letters` form (falling back to `unpointed`, then
`variant_text`), and stamps that choice in the meta table so no future
reader mistakes it for the recovered original.

Isolation: the source corpus is opened READ-ONLY; all writes go to the
separate --target-db file. The live corpus is never modified.
"""
import argparse, json, sqlite3, struct, sys, time
import urllib.request

OLLAMA = "http://127.0.0.1:11434/api/embeddings"
MODEL = "nomic-embed-text:latest"
DIMS = 768


def embed(text):
    req = urllib.request.Request(
        OLLAMA,
        data=json.dumps({"model": MODEL, "prompt": text}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=120) as r:
        vec = json.loads(r.read())["embedding"]
    if len(vec) != DIMS:
        raise ValueError(f"expected {DIMS} dims, got {len(vec)}")
    return struct.pack(f"<{DIMS}f", *vec)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source-db", required=True)
    ap.add_argument("--target-db", required=True)
    ap.add_argument("--kind", default="spelling")
    args = ap.parse_args()

    src = sqlite3.connect(f"file:{args.source_db}?mode=ro", uri=True)
    tgt = sqlite3.connect(args.target_db)
    tgt.execute(
        "CREATE TABLE IF NOT EXISTS word_variants_embeddings("
        "word_id INTEGER NOT NULL, variant_seq INTEGER NOT NULL,"
        "embedding BLOB NOT NULL, PRIMARY KEY(word_id, variant_seq))"
    )
    tgt.execute(
        "CREATE TABLE IF NOT EXISTS embedding_meta(key TEXT PRIMARY KEY, value TEXT)"
    )
    for k, v in [
        ("model", MODEL),
        ("dimensions", str(DIMS)),
        ("input_field", "letters (fallback unpointed, variant_text)"),
        ("scope", f"variant_kind='{args.kind}'"),
        ("rebuilt_by", "rebuild_variant_embeddings.py (reconstruction)"),
        ("started_utc", time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())),
    ]:
        tgt.execute("INSERT OR REPLACE INTO embedding_meta VALUES (?,?)", (k, v))
    tgt.commit()

    done = {tuple(r) for r in tgt.execute(
        "SELECT word_id, variant_seq FROM word_variants_embeddings")}
    total = src.execute(
        "SELECT COUNT(*) FROM word_variants WHERE variant_kind=?",
        (args.kind,)).fetchone()[0]
    print(f"scope rows: {total}; already embedded: {len(done)}", flush=True)

    rows = src.execute(
        "SELECT word_id, variant_seq, letters, unpointed, variant_text "
        "FROM word_variants WHERE variant_kind=? ORDER BY word_id, variant_seq",
        (args.kind,))
    pending = errors = since_commit = 0
    t0 = time.time()
    for word_id, seq, letters, unpointed, variant_text in rows:
        if (word_id, seq) in done:
            continue
        text = letters or unpointed or variant_text
        try:
            blob = embed(text)
        except Exception as e:
            errors += 1
            print(f"error at ({word_id},{seq}): {e}", flush=True)
            if errors >= 20:
                print("ABORT: 20 consecutive errors", flush=True)
                tgt.commit()
                return 1
            continue
        errors = 0
        tgt.execute("INSERT INTO word_variants_embeddings VALUES (?,?,?)",
                    (word_id, seq, blob))
        pending += 1
        since_commit += 1
        if since_commit >= 100:
            tgt.commit()
            since_commit = 0
        if pending % 1000 == 0:
            rate = pending / max(time.time() - t0, 1)
            print(f"{pending} embedded this run ({rate:.1f}/s)", flush=True)
    tgt.commit()
    final = tgt.execute("SELECT COUNT(*) FROM word_variants_embeddings").fetchone()[0]
    print(f"DONE: target holds {final} embeddings; scope was {total}", flush=True)
    return 0 if final == total else 2


if __name__ == "__main__":
    sys.exit(main())
