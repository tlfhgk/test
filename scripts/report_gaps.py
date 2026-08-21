#!/usr/bin/env python3
"""List every record in the database that is not backed by a verified source.

    python3 scripts/report_gaps.py

Run this before quoting anything from the database in a real document.
"""
from __future__ import annotations

import argparse
import pathlib
import sqlite3
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DEFAULT_DB = ROOT / "db" / "aircraft_impact.db"

RANK = {"primary_source": 0, "web_verified": 1, "model_knowledge": 2, "to_verify": 3}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--db", type=pathlib.Path, default=DEFAULT_DB)
    args = ap.parse_args()
    if not args.db.exists():
        raise SystemExit(f"database not found: {args.db}\nrun: python3 scripts/build_db.py")
    con = sqlite3.connect(args.db)
    con.row_factory = sqlite3.Row

    print("verification status of clause records")
    print("-" * 72)
    for r in con.execute("""SELECT verification, count(*) n FROM clauses
                            GROUP BY verification"""):
        print(f"  {r['verification'] or 'unset':16s} {r['n']}")

    raw = con.execute("SELECT count(*) n FROM chunks WHERE kind='raw'").fetchone()["n"]
    print(f"\n  verbatim chunks from ingested primary sources: {raw}")
    if raw == 0:
        print("  -> no primary text indexed yet. run: bash scripts/fetch_sources.sh")

    print("\nrecords needing verification before citation")
    print("-" * 72)
    rows = sorted(
        con.execute("""SELECT clause_id, source_id, locator, verification, confidence, notes
                       FROM clauses WHERE verification != 'web_verified'"""),
        key=lambda r: (RANK.get(r["verification"], 9), r["clause_id"]),
    )
    for r in rows:
        print(f"\n  [{r['verification']}/{r['confidence'] or '?'}] {r['clause_id']}")
        print(f"      {r['source_id']}  {r['locator'] or ''}")
        if r["notes"]:
            print(f"      note: {r['notes'][:200]}")

    print(f"\n{len(rows)} record(s) to verify.")
    con.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
