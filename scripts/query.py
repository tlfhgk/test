#!/usr/bin/env python3
"""Search the aircraft-impact regulatory database.

    python3 scripts/query.py "체코 항공기 추락 설계기준 빈도"
    python3 scripts/query.py "beyond design basis" --jurisdiction US -k 5
    python3 scripts/query.py "국부손상 관통" --topic T08 --context
"""
from __future__ import annotations

import argparse
import json
import pathlib
import signal
import sys

# Let `query.py ... | head` exit quietly instead of raising BrokenPipeError.
try:
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)
except (AttributeError, ValueError):  # non-POSIX
    pass

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import retrieval  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("query")
    ap.add_argument("--db", type=pathlib.Path, default=retrieval.DEFAULT_DB)
    ap.add_argument("-k", type=int, default=6, help="number of chunks to retrieve")
    ap.add_argument("--jurisdiction", help="US | CZ | EU | INT | MULTI")
    ap.add_argument("--source", dest="source_id", help="e.g. US-NEI-07-13")
    ap.add_argument("--topic", help="e.g. T08")
    ap.add_argument("--kind", help="clause | crosswalk | source | raw")
    ap.add_argument("--verification", help="web_verified | model_knowledge | to_verify")
    ap.add_argument("--no-expand", action="store_true", help="do not pull in related crosswalk entries")
    ap.add_argument("--context", action="store_true", help="print the assembled RAG context block")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    con = retrieval.connect(args.db)
    rows = retrieval.search(
        con, args.query, k=args.k,
        jurisdiction=args.jurisdiction, source_id=args.source_id,
        topic=args.topic, kind=args.kind, verification=args.verification,
    )
    if not args.no_expand:
        rows = retrieval.expand_with_crosswalk(con, rows)

    if args.json:
        print(json.dumps([dict(r) | {"embedding": None} for r in rows], ensure_ascii=False, indent=2))
    elif args.context:
        print(retrieval.format_context(rows))
    else:
        if not rows:
            print("no results")
            return 1
        for i, r in enumerate(rows, 1):
            flag = {"primary_source": "★", "web_verified": "✓",
                    "model_knowledge": "~", "to_verify": "!"}.get(r["verification"], " ")
            print(f"\n{i:>2}. [{flag}] {r['ref_id']}  ({r['kind']}, {r['jurisdiction']}, bm25={r['score']:.2f})")
            print(f"    {r['title']}")
            body = r["text"].split("\n")
            for line in body[:10]:
                print(f"    | {line}")
            if len(body) > 10:
                print(f"    | … ({len(body)-10} more lines — use --context or --json for the full chunk)")
        print("\nlegend: ★ verbatim primary source   ✓ web-verified   "
              "~ model knowledge, unverified   ! locator/content to verify")
    return 0


if __name__ == "__main__":
    sys.exit(main())
