#!/usr/bin/env python3
"""Read-only inventory of Hebrew/Aramaic niqqud-only form variants.

The SQLite database is opened with mode=ro. The script never writes to it.
It emits a CSV of candidate groups and a JSON summary to the requested output
prefix. It supports the v2 schema (words.pointed) and legacy v1
(words.word_pointed) when the expected location columns are available.

Strict rule: after NFC normalization, forms must be identical when only the
explicit Hebrew vowel-point code points are removed. All consonants, matres,
final forms, dagesh/mapiq, meteg, shin/sin dots, cantillation, punctuation,
maqaf, and morpheme separators remain significant.

This is an inventory, not an adjudication or a production migration.
"""
import argparse
import collections
import csv
import json
import sqlite3
import unicodedata
from pathlib import Path

# Hebrew vowel points: sheva through qubuts, plus qamats qatan.
VOWEL_POINTS = set(range(0x05B0, 0x05BC)) | {0x05C7}
VOWEL_NAMES = {
    0x05B0: "sheva", 0x05B1: "hataf-segol", 0x05B2: "hataf-patah",
    0x05B3: "hataf-qamats", 0x05B4: "hiriq", 0x05B5: "tsere",
    0x05B6: "segol", 0x05B7: "patah", 0x05B8: "qamats",
    0x05B9: "holam", 0x05BA: "holam-haser/legacy-holam",
    0x05BB: "qubuts", 0x05C7: "qamats-qatan",
}

def codepoints(s):
    return " ".join(f"U+{ord(c):04X}" for c in s)

def strict_signature(s):
    nfc = unicodedata.normalize("NFC", s or "")
    return "".join(c for c in nfc if ord(c) not in VOWEL_POINTS)

def vowel_description(s):
    found = []
    for c in unicodedata.normalize("NFC", s or ""):
        cp = ord(c)
        if cp in VOWEL_POINTS:
            found.append(f"{VOWEL_NAMES.get(cp, hex(cp))} (U+{cp:04X})")
    return "; ".join(found)

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--db", required=True, help="SQLite database path")
    ap.add_argument("--out-prefix", required=True,
                    help="Output prefix; writes .csv and .summary.json")
    args = ap.parse_args()

    db_uri = Path(args.db).resolve().as_uri() + "?mode=ro"
    con = sqlite3.connect(db_uri, uri=True)
    con.row_factory = sqlite3.Row
    try:
        tables = {r[0] for r in con.execute(
            "SELECT name FROM sqlite_master WHERE type='table'")}
        if "words" not in tables:
            raise SystemExit("Expected table 'words' was not found")
        cols = {r[1] for r in con.execute("PRAGMA table_info(words)")}
        pointed_col = "pointed" if "pointed" in cols else (
            "word_pointed" if "word_pointed" in cols else None)
        id_col = "word_id" if "word_id" in cols else None
        if not pointed_col or not id_col:
            raise SystemExit("words must contain word_id and pointed/word_pointed")

        select = [f"w.{id_col} AS word_id", f"w.{pointed_col} AS pointed"]
        for col in ("root_id", "root_form_seq", "root_vowel_seq", "is_aramaic"):
            if col in cols:
                select.append(f"w.{col} AS {col}")
            else:
                select.append(f"NULL AS {col}")

        joins = ""
        if "verse_id" in cols and "verses" in tables:
            select += ["v.book_id AS book_id", "v.chapter AS chapter", "v.verse AS verse"]
            joins = " LEFT JOIN verses v ON v.verse_id=w.verse_id"
            if "books" in tables:
                select.append("b.name_en AS book_name")
                joins += " LEFT JOIN books b ON b.book_id=v.book_id"
            else:
                select.append("NULL AS book_name")
        elif all(c in cols for c in ("book", "chapter", "verse")):
            select += ["w.book AS book_name", "w.chapter AS chapter", "w.verse AS verse",
                       "NULL AS book_id"]
        else:
            select += ["NULL AS book_id", "NULL AS book_name",
                       "NULL AS chapter", "NULL AS verse"]

        sql = "SELECT " + ", ".join(select) + " FROM words w" + joins + " ORDER BY w.word_id"
        groups = collections.defaultdict(list)
        total = 0
        for row in con.execute(sql):
            total += 1
            raw = row["pointed"] or ""
            normalized = unicodedata.normalize("NFC", raw)
            signature = strict_signature(normalized)
            if not signature:
                continue
            item = dict(row)
            item["raw_pointed"] = raw
            item["nfc_pointed"] = normalized
            item["vowels"] = vowel_description(normalized)
            item["codepoints"] = codepoints(normalized)
            groups[signature].append(item)

        candidates = []
        for signature, rows in groups.items():
            forms = collections.defaultdict(list)
            for row in rows:
                forms[row["nfc_pointed"]].append(row)
            if len(forms) < 2:
                continue
            # Every member has exactly the same non-vowel sequence by construction.
            # Require at least two distinct normalized pointed forms.
            members = []
            for form, occurrences in sorted(forms.items()):
                first = occurrences[0]
                members.append({
                    "pointed_form": form,
                    "vowel_points": first["vowels"],
                    "codepoints": first["codepoints"],
                    "occurrence_count": len(occurrences),
                    "word_ids": [r["word_id"] for r in occurrences],
                    "root_vowel_ids": sorted({
                        f'{r["root_id"]}.{r["root_form_seq"]}.{r["root_vowel_seq"]}'
                        for r in occurrences
                        if r["root_id"] is not None and
                           r["root_form_seq"] is not None and
                           r["root_vowel_seq"] is not None
                    }),
                    "references": sorted({
                        ":".join(str(x) for x in
                                 (r["book_name"] or r["book_id"] or "?",
                                  r["chapter"] or "?", r["verse"] or "?"))
                        for r in occurrences
                    }),
                    "aramaic_values": sorted({r["is_aramaic"] for r in occurrences
                                               if r["is_aramaic"] is not None}),
                })
            all_occurrences = [r for xs in forms.values() for r in xs]
            aramaic = sorted({r["is_aramaic"] for r in all_occurrences
                              if r["is_aramaic"] is not None})
            root_ids = sorted({
                f'{r["root_id"]}.{r["root_form_seq"]}.{r["root_vowel_seq"]}'
                for r in all_occurrences
                if r["root_id"] is not None and r["root_form_seq"] is not None
                and r["root_vowel_seq"] is not None
            })
            candidates.append({
                "signature": signature,
                "signature_codepoints": codepoints(signature),
                "members": members,
                "occurrence_count": len(all_occurrences),
                "distinct_form_count": len(forms),
                "aramaic_values": aramaic,
                "root_vowel_ids": root_ids,
            })

        candidates.sort(key=lambda x: (x["signature"], x["distinct_form_count"]))
        prefix = Path(args.out_prefix)
        prefix.parent.mkdir(parents=True, exist_ok=True)
        csv_path = str(prefix) + ".csv"
        json_path = str(prefix) + ".summary.json"
        with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=[
                "signature", "signature_codepoints", "pointed_form",
                "vowel_points", "codepoints", "occurrence_count", "word_ids",
                "root_vowel_ids", "references", "aramaic_values"])
            writer.writeheader()
            for group in candidates:
                for member in group["members"]:
                    writer.writerow({
                        "signature": group["signature"],
                        "signature_codepoints": group["signature_codepoints"],
                        "pointed_form": member["pointed_form"],
                        "vowel_points": member["vowel_points"],
                        "codepoints": member["codepoints"],
                        "occurrence_count": member["occurrence_count"],
                        "word_ids": ";".join(map(str, member["word_ids"])),
                        "root_vowel_ids": ";".join(member["root_vowel_ids"]),
                        "references": ";".join(member["references"]),
                        "aramaic_values": ";".join(map(str, member["aramaic_values"])),
                    })

        summary = {
            "database_open_mode": "read-only (SQLite URI mode=ro)",
            "database_modified": False,
            "unicode_normalization": "NFC for comparison; raw pointed strings retained in DB",
            "vowel_codepoints": [f"U+{cp:04X}" for cp in sorted(VOWEL_POINTS)],
            "rows_scanned": total,
            "candidate_signature_groups": len(candidates),
            "distinct_pointed_forms_in_candidate_groups":
                sum(g["distinct_form_count"] for g in candidates),
            "occurrences_in_candidate_groups":
                sum(g["occurrence_count"] for g in candidates),
            "candidate_groups_with_root_vowel_ids":
                sum(bool(g["root_vowel_ids"]) for g in candidates),
            "candidate_groups_spanning_multiple_root_vowel_ids":
                sum(len(g["root_vowel_ids"]) > 1 for g in candidates),
            "candidate_groups_aramaic_flagged":
                sum(1 in g["aramaic_values"] for g in candidates),
            "limitations": [
                "Candidates are mechanical orthographic matches, not adjudicated textual variants.",
                "The codepoint set must be checked against the corpus and the Unicode standard before production use.",
                "The script does not merge lemmas, morphology, Strong's numbers, meanings, or translation alignments.",
                "Qere/ketiv and source populations must be reviewed separately before any grouping is persisted.",
                "No database schema or data is changed."
            ],
            "csv": csv_path,
            "candidate_groups": candidates,
        }
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
            f.write("\n")
        print(json.dumps({k: v for k, v in summary.items()
                          if k not in ("candidate_groups", "limitations")}, indent=2))
    finally:
        con.close()

if __name__ == "__main__":
    main()
