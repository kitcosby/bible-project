#!/usr/bin/env python3
"""Read-only Hebrew/Aramaic vowel-only variant inventory for PostgreSQL.

Connects to the Bible database using psycopg2. Run as a role with SELECT-only
access (or as the local postgres OS account if using peer authentication).
The transaction is explicitly read-only. No DDL/DML is issued.

A candidate group has identical NFC-normalized strings after removing only
the vowel points U+05B0..U+05BB and U+05C7. All other characters remain
significant. Hebrew and Aramaic are kept in separate populations.
"""
import argparse
import collections
import csv
import json
import unicodedata
from pathlib import Path
import psycopg2
import psycopg2.extras

VOWEL_POINTS = set(range(0x05B0, 0x05BC)) | {0x05C7}
VOWEL_NAMES = {
    0x05B0: "sheva", 0x05B1: "hataf-segol", 0x05B2: "hataf-patah",
    0x05B3: "hataf-qamats", 0x05B4: "hiriq", 0x05B5: "tsere",
    0x05B6: "segol", 0x05B7: "patah", 0x05B8: "qamats",
    0x05B9: "holam", 0x05BA: "holam-haser-for-vav",
    0x05BB: "qubuts", 0x05C7: "qamats-qatan",
}

def signature(form):
    return "".join(c for c in form if ord(c) not in VOWEL_POINTS)

def codepoints(value):
    return " ".join(f"U+{ord(c):04X}" for c in value)

def vowel_labels(form):
    return "; ".join(
        f"{VOWEL_NAMES[ord(c)]} (U+{ord(c):04X})"
        for c in form if ord(c) in VOWEL_POINTS
    )

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--database", default="bible")
    ap.add_argument("--user", default="postgres")
    ap.add_argument("--host", default=None, help="Omit to use the local Unix socket")
    ap.add_argument("--out-prefix", required=True)
    args = ap.parse_args()

    conn = psycopg2.connect(dbname=args.database, user=args.user, host=args.host)
    conn.set_session(readonly=True, autocommit=False)
    groups = collections.defaultdict(lambda: collections.defaultdict(list))
    total = 0
    try:
        with conn.cursor(name="hebrew_vowel_variant_scan") as cur:
            cur.itersize = 5000
            cur.execute("""
                SELECT w.word_id, w.pointed, w.is_aramaic,
                       w.root_id, w.root_form_seq, w.root_vowel_seq,
                       b.name_en AS book, v.chapter, v.verse, w.word_pos
                FROM public.words AS w
                JOIN public.verses AS v ON v.verse_id = w.verse_id
                JOIN public.books AS b ON b.book_id = v.book_id
                ORDER BY w.word_id
            """)
            while True:
                rows = cur.fetchmany(5000)
                if not rows:
                    break
                for row in rows:
                    total += 1
                    (word_id, raw, aramaic, root_id, form_seq, vowel_seq,
                     book, chapter, verse, word_pos) = row
                    raw = raw or ""
                    normalized = unicodedata.normalize("NFC", raw)
                    sig = signature(normalized)
                    if not sig:
                        continue
                    groups[(aramaic, sig)][normalized].append({
                        "word_id": word_id,
                        "raw": raw,
                        "root_form": f"{root_id}.{form_seq}",
                        "root_vowel": f"{root_id}.{form_seq}.{vowel_seq}",
                        "reference": f"{book} {chapter}:{verse}",
                        "word_pos": word_pos,
                    })
        conn.commit()
    finally:
        conn.close()

    candidates = []
    for (aramaic, sig), forms in groups.items():
        if len(forms) < 2:
            continue
        members = []
        all_rows = [r for occurrences in forms.values() for r in occurrences]
        for form, occurrences in sorted(forms.items()):
            members.append({
                "pointed_form_nfc": form,
                "raw_forms": sorted({r["raw"] for r in occurrences}),
                "vowel_points": vowel_labels(form),
                "codepoints": codepoints(form),
                "occurrence_count": len(occurrences),
                "word_ids": [r["word_id"] for r in occurrences],
                "references": sorted({r["reference"] for r in occurrences}),
                "root_form_ids": sorted({r["root_form"] for r in occurrences}),
                "root_vowel_ids": sorted({r["root_vowel"] for r in occurrences}),
            })
        candidates.append({
            "language_population": (
                "Hebrew" if aramaic == 0 else
                "Aramaic" if aramaic == 1 else "Unknown"
            ),
            "is_aramaic": aramaic,
            "signature": sig,
            "signature_codepoints": codepoints(sig),
            "distinct_form_count": len(forms),
            "occurrence_count": len(all_rows),
            "root_form_count": len({r["root_form"] for r in all_rows}),
            "root_vowel_count": len({r["root_vowel"] for r in all_rows}),
            "members": members,
        })

    candidates.sort(key=lambda g: (
        g["language_population"], g["signature"], g["distinct_form_count"]
    ))
    by_language = {}
    for language in ("Hebrew", "Aramaic", "Unknown"):
        subset = [g for g in candidates if g["language_population"] == language]
        if not subset:
            continue
        by_language[language] = {
            "candidate_groups": len(subset),
            "distinct_forms": sum(g["distinct_form_count"] for g in subset),
            "occurrences": sum(g["occurrence_count"] for g in subset),
            "groups_within_one_root_form": sum(g["root_form_count"] == 1 for g in subset),
            "groups_spanning_multiple_root_forms": sum(g["root_form_count"] > 1 for g in subset),
        }

    prefix = Path(args.out_prefix)
    prefix.parent.mkdir(parents=True, exist_ok=True)
    csv_path = str(prefix) + ".csv"
    json_path = str(prefix) + ".summary.json"
    with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "language_population", "signature", "signature_codepoints",
            "pointed_form_nfc", "raw_forms", "vowel_points", "codepoints",
            "occurrence_count", "word_ids", "references",
            "root_form_ids", "root_vowel_ids",
        ])
        writer.writeheader()
        for group in candidates:
            for member in group["members"]:
                writer.writerow({
                    "language_population": group["language_population"],
                    "signature": group["signature"],
                    "signature_codepoints": group["signature_codepoints"],
                    "pointed_form_nfc": member["pointed_form_nfc"],
                    "raw_forms": " || ".join(member["raw_forms"]),
                    "vowel_points": member["vowel_points"],
                    "codepoints": member["codepoints"],
                    "occurrence_count": member["occurrence_count"],
                    "word_ids": ";".join(map(str, member["word_ids"])),
                    "references": ";".join(member["references"]),
                    "root_form_ids": ";".join(member["root_form_ids"]),
                    "root_vowel_ids": ";".join(member["root_vowel_ids"]),
                })

    summary = {
        "database": args.database,
        "transaction_read_only": True,
        "database_modified": False,
        "rows_scanned": total,
        "unicode_normalization": "NFC for comparison; raw source strings retained in output",
        "removed_vowel_codepoints": [f"U+{cp:04X}" for cp in sorted(VOWEL_POINTS)],
        "populations": by_language,
        "candidate_groups": candidates,
        "limitations": [
            "Mechanical orthographic candidates only; no lemma or meaning equivalence is inferred.",
            "Qere/ketiv rows and alternate source populations require separate apparatus review.",
            "The output does not modify schema, source text, lexical entries, or alignments.",
            "Vowel-point codepoints must remain explicitly versioned and reviewed.",
        ],
        "csv": csv_path,
    }
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(json.dumps({
        "database": args.database,
        "transaction_read_only": True,
        "database_modified": False,
        "rows_scanned": total,
        "populations": by_language,
        "csv": csv_path,
        "json": json_path,
    }, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
