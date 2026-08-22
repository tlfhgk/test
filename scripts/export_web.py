#!/usr/bin/env python3
"""Build the standalone browser app from the database.

    python3 scripts/export_web.py

Reads db/aircraft_impact.db, injects the CURATED layer as JSON into
web/template.html and writes web/aircraft-impact.html — a single self-contained
file that needs no server, no install and no network.

Only the curated layer ships: clause records, crosswalk entries, the source
registry and the topic axes. Verbatim chunks from NEI 07-13, the IAEA
publications, WENRA and EUR stay in the local database, because those documents
are copyrighted or licensed and this file is meant to be shared.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sqlite3
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DEFAULT_DB = ROOT / "db" / "aircraft_impact.db"
TEMPLATE = ROOT / "web" / "template.html"
DEFAULT_OUT = ROOT / "web" / "aircraft-impact.html"

MARKER = "/*__DATA__*/"


def build_payload(con: sqlite3.Connection) -> dict:
    con.row_factory = sqlite3.Row

    sources = {}
    for r in con.execute("SELECT * FROM sources"):
        raw = json.loads(r["raw"] or "{}")
        sources[r["source_id"]] = {
            "id": r["source_id"],
            "j": r["jurisdiction"],
            "doc": r["doc_number"],
            "title": r["title_orig"],
            "ko": r["title_ko"],
            "issuer": r["issuer"],
            "type": r["instrument_type"],
            "binding": bool(r["binding"]),
            "version": r["version"],
            "access": r["access"],
            "role": r["role"],
            "urls": json.loads(r["urls"] or "[]"),
            "obtained": raw.get("obtained"),
            "note": raw.get("acquisition_note"),
        }

    clauses = []
    for r in con.execute("SELECT * FROM clauses ORDER BY source_id, clause_id"):
        src = sources.get(r["source_id"], {})
        clauses.append({
            "id": r["clause_id"],
            "s": r["source_id"],
            "doc": src.get("doc"),
            "j": src.get("j"),
            "loc": r["locator"],
            "he": r["heading_en"],
            "hk": r["heading_ko"],
            "t": json.loads(r["topics"] or "[]"),
            "ts": r["text_status"],
            "v": r["verification"],
            "en": r["summary_en"],
            "ko": r["summary_ko"],
            "kp": json.loads(r["key_parameters"] or "null"),
            "u": r["source_url"],
            "nt": r["notes"],
        })

    positions = {}
    for r in con.execute("SELECT * FROM crosswalk_positions"):
        positions.setdefault(r["cw_id"], []).append(
            {"s": r["source_id"], "rel": r["relation"], "n": r["note"]})

    crosswalk = []
    for r in con.execute("SELECT * FROM crosswalk ORDER BY cw_id"):
        crosswalk.append({
            "id": r["cw_id"],
            "topic": r["topic_id"],
            "qe": r["question_en"],
            "qk": r["question_ko"],
            "ko": r["summary_ko"],
            "div": r["divergence_note"],
            "cl": json.loads(r["clause_ids"] or "[]"),
            "pos": positions.get(r["cw_id"], []),
        })

    topics = [dict(zip(("id", "en", "ko", "d"), tuple(r)))
              for r in con.execute(
                  "SELECT topic_id,label_en,label_ko,description_ko FROM topics ORDER BY topic_id")]

    raw_counts = {r["source_id"]: r["n"] for r in con.execute(
        "SELECT source_id, count(*) n FROM chunks WHERE kind='raw' GROUP BY source_id")}
    for sid, s in sources.items():
        s["raw"] = raw_counts.get(sid, 0)

    return {
        "clauses": clauses,
        "crosswalk": crosswalk,
        "sources": list(sources.values()),
        "topics": topics,
        "stats": {
            "clauses": len(clauses),
            "crosswalk": len(crosswalk),
            "sources": len(sources),
            "raw": sum(raw_counts.values()),
            "primary": sum(1 for c in clauses if c["v"] == "primary_source"),
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--db", type=pathlib.Path, default=DEFAULT_DB)
    ap.add_argument("--template", type=pathlib.Path, default=TEMPLATE)
    ap.add_argument("--out", type=pathlib.Path, default=DEFAULT_OUT)
    args = ap.parse_args()

    if not args.db.exists():
        raise SystemExit(f"database not found: {args.db}\nrun: python3 scripts/build_db.py")
    if not args.template.exists():
        raise SystemExit(f"template not found: {args.template}")

    con = sqlite3.connect(f"file:{args.db}?mode=ro", uri=True)
    payload = build_payload(con)
    con.close()

    html = args.template.read_text(encoding="utf-8")
    if MARKER not in html:
        raise SystemExit(f"template is missing the {MARKER} marker")
    # json.dumps output is embedded in a <script>; </script> inside a string
    # would close the tag early, so neutralise the sequence.
    blob = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(html.replace(MARKER, "const DB=" + blob + ";"), encoding="utf-8")

    kb = args.out.stat().st_size / 1024
    print(f"wrote {args.out}  ({kb:.0f} KB)")
    for k, v in payload["stats"].items():
        print(f"  {k:10s} {v}")
    print("\ncurated layer only — verbatim text from copyrighted sources stays in the local DB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
