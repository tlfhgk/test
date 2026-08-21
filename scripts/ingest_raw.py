#!/usr/bin/env python3
"""Ingest official source documents into the same database as verbatim chunks.

The curated YAML corpus contains summaries. Once you have the real documents,
drop them in corpus/raw/<SOURCE_ID>/ and run this script to index their actual
text alongside the summaries, with kind='raw'.

    corpus/raw/US-10CFR50.150/50.150.txt
    corpus/raw/IAEA-SSG-68/PUB1968_web.pdf
    corpus/raw/CZ-329-2017/329_2017.pdf

    python3 scripts/ingest_raw.py                 # ingest everything present
    python3 scripts/ingest_raw.py --source CZ-329-2017 --replace

Accepted: .txt, .md, .pdf. PDFs need one of `pdftotext` (poppler) or `pypdf`.
corpus/raw/ is gitignored: documents whose licence forbids redistribution stay
on your machine, and the database you build from them is yours, not the repo's.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import shutil
import sqlite3
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
RAW = ROOT / "corpus" / "raw"
DEFAULT_DB = ROOT / "db" / "aircraft_impact.db"

# ~1200 characters keeps a chunk inside a couple of regulation paragraphs, which
# is the granularity a citation needs to stay checkable.
CHUNK_CHARS = 1200
OVERLAP_CHARS = 150


def pdf_to_text(path: pathlib.Path) -> str:
    if shutil.which("pdftotext"):
        out = subprocess.run(["pdftotext", "-layout", str(path), "-"],
                             capture_output=True, text=True, check=False)
        if out.returncode == 0 and out.stdout.strip():
            return out.stdout
    try:
        import pypdf  # type: ignore
    except ImportError:
        raise SystemExit(
            f"cannot read {path.name}: install poppler-utils (pdftotext) or `pip install pypdf`"
        )
    reader = pypdf.PdfReader(str(path))
    return "\n".join((page.extract_text() or "") for page in reader.pages)


def read_document(path: pathlib.Path) -> str:
    if path.suffix.lower() == ".pdf":
        return pdf_to_text(path)
    return path.read_text(encoding="utf-8", errors="replace")


def normalise(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\f", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def split_paragraphs(text: str) -> list[str]:
    return [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]


def chunk_text(text: str, size: int = CHUNK_CHARS, overlap: int = OVERLAP_CHARS) -> list[str]:
    """Pack paragraphs up to `size`; hard-split any paragraph that alone exceeds it."""
    chunks: list[str] = []
    buf = ""
    for para in split_paragraphs(text):
        while len(para) > size:
            head, para = para[:size], para[size - overlap:]
            if buf:
                chunks.append(buf.strip())
                buf = ""
            chunks.append(head.strip())
        if not buf:
            buf = para
        elif len(buf) + len(para) + 2 <= size:
            buf += "\n\n" + para
        else:
            chunks.append(buf.strip())
            buf = para
    if buf.strip():
        chunks.append(buf.strip())
    return chunks


# Locator hints so a retrieved raw chunk still says where in the document it came
# from: US "§ 50.150(a)(1)", Czech "§ 12", IAEA "3.47", EUR "2.4.1".
LOCATOR_PATTERNS = [
    re.compile(r"§\s*\d+[\w.()–-]*"),
    re.compile(r"\b\d+\.\d+(?:\.\d+)*\b"),
]


def guess_locator(chunk: str) -> str | None:
    head = chunk[:300]
    for pat in LOCATOR_PATTERNS:
        m = pat.search(head)
        if m:
            return m.group(0)
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--db", type=pathlib.Path, default=DEFAULT_DB)
    ap.add_argument("--source", help="ingest only this source_id directory")
    ap.add_argument("--replace", action="store_true",
                    help="delete existing raw chunks for the ingested sources first")
    ap.add_argument("--chunk-chars", type=int, default=CHUNK_CHARS)
    args = ap.parse_args()

    if not args.db.exists():
        raise SystemExit(f"database not found: {args.db}\nrun: python3 scripts/build_db.py")
    con = sqlite3.connect(args.db)
    con.row_factory = sqlite3.Row

    known = {r["source_id"]: r for r in con.execute("SELECT * FROM sources")}
    dirs = sorted(d for d in RAW.iterdir() if d.is_dir()) if RAW.exists() else []
    if args.source:
        dirs = [d for d in dirs if d.name == args.source]
        if not dirs:
            raise SystemExit(f"no directory corpus/raw/{args.source}/")
    if not dirs:
        print("nothing to ingest — see the docstring for the expected layout, and")
        print("scripts/fetch_sources.sh for where to download each document.")
        return 0

    total = 0
    for d in dirs:
        sid = d.name
        if sid not in known:
            print(f"skip {sid}: not a source_id in config/sources.yaml")
            continue
        src = known[sid]
        if src["access"] == "proprietary":
            print(f"warning: {sid} is marked proprietary — indexing locally only, never commit corpus/raw/")
        if args.replace:
            con.execute("DELETE FROM chunks WHERE kind='raw' AND source_id=?", (sid,))

        files = [p for p in sorted(d.rglob("*")) if p.suffix.lower() in {".txt", ".md", ".pdf"}]
        if not files:
            print(f"skip {sid}: no .txt/.md/.pdf files")
            continue
        for path in files:
            text = normalise(read_document(path))
            if not text:
                print(f"skip {path.name}: no extractable text (scanned PDF? run OCR first)")
                continue
            pieces = chunk_text(text, size=args.chunk_chars)
            for i, piece in enumerate(pieces):
                locator = guess_locator(piece)
                header = f"[{src['jurisdiction']} | {src['doc_number']}] {locator or ''}".strip()
                con.execute(
                    """INSERT INTO chunks (kind, ref_id, source_id, jurisdiction, framework, topics,
                                           text_status, verification, title, text, metadata)
                       VALUES ('raw',?,?,?,?,'','verbatim','primary_source',?,?,?)""",
                    (f"{sid}#{path.stem}#{i:04d}", sid, src["jurisdiction"], src["framework"],
                     f"{src['doc_number']} {locator or path.stem}".strip(),
                     header + "\n\n" + piece,
                     json.dumps({"file": path.name, "ord": i, "locator": locator,
                                 "source_url": json.loads(src["urls"] or "[]")[:1]}, ensure_ascii=False)),
                )
            total += len(pieces)
            print(f"{sid}: {path.name} -> {len(pieces)} chunks")

    con.execute("INSERT INTO chunks_fts(chunks_fts) VALUES('optimize')")
    con.commit()
    con.close()
    print(f"\ningested {total} verbatim chunks")
    print("verification='primary_source' — these outrank the curated summaries; "
          "prefer them when both are retrieved.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
