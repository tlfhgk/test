#!/usr/bin/env python3
"""Export the chunk table as JSONL for an external vector store / RAG framework.

    python3 scripts/export_rag.py --out export/chunks.jsonl
    python3 scripts/export_rag.py --kind clause --jurisdiction CZ

Each line is {id, text, metadata} — the shape LangChain, LlamaIndex, Chroma,
pgvector loaders and the OpenAI/Voyage embedding batch APIs all accept.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sqlite3
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DEFAULT_DB = ROOT / "db" / "aircraft_impact.db"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--db", type=pathlib.Path, default=DEFAULT_DB)
    ap.add_argument("--out", type=pathlib.Path, default=ROOT / "export" / "chunks.jsonl")
    ap.add_argument("--kind")
    ap.add_argument("--jurisdiction")
    args = ap.parse_args()

    if not args.db.exists():
        raise SystemExit(f"database not found: {args.db}\nrun: python3 scripts/build_db.py")
    con = sqlite3.connect(args.db)
    con.row_factory = sqlite3.Row

    where, params = [], []
    if args.kind:
        where.append("kind = ?"); params.append(args.kind)
    if args.jurisdiction:
        where.append("jurisdiction = ?"); params.append(args.jurisdiction)
    sql = "SELECT * FROM chunks" + (" WHERE " + " AND ".join(where) if where else "") + " ORDER BY chunk_id"

    args.out.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with args.out.open("w", encoding="utf-8") as fh:
        for r in con.execute(sql, params):
            meta = json.loads(r["metadata"] or "{}")
            meta.update({
                "kind": r["kind"], "ref_id": r["ref_id"], "source_id": r["source_id"],
                "jurisdiction": r["jurisdiction"], "framework": r["framework"],
                "topics": [t for t in (r["topics"] or "").split(",") if t],
                "text_status": r["text_status"], "verification": r["verification"],
                "title": r["title"],
            })
            fh.write(json.dumps({"id": r["ref_id"], "text": r["text"], "metadata": meta},
                                ensure_ascii=False) + "\n")
            n += 1
    con.close()
    print(f"wrote {n} chunks -> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
