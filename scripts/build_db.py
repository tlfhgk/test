#!/usr/bin/env python3
"""Build the aircraft-impact regulatory SQLite database used for RAG.

Reads the curated YAML corpus and produces a single self-contained SQLite file
with full-text search (FTS5/BM25) over retrieval-ready chunks.

    python3 scripts/build_db.py --db db/aircraft_impact.db

The build is idempotent: it drops and rebuilds every curated table. Chunks that
came from scripts/ingest_raw.py (kind='raw') live in the same tables but are
preserved across rebuilds unless --purge-raw is given.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sqlite3
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
DEFAULT_DB = ROOT / "db" / "aircraft_impact.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS sources (
    source_id       TEXT PRIMARY KEY,
    jurisdiction    TEXT NOT NULL,
    framework       TEXT,
    doc_number      TEXT,
    title_orig      TEXT,
    title_en        TEXT,
    title_ko        TEXT,
    issuer          TEXT,
    instrument_type TEXT,
    binding         INTEGER,
    version         TEXT,
    issue_date      TEXT,
    effective_date  TEXT,
    language        TEXT,
    access          TEXT,
    copyright_note  TEXT,
    role            TEXT,
    urls            TEXT,           -- json array
    raw             TEXT            -- full source record as json
);

CREATE TABLE IF NOT EXISTS topics (
    topic_id       TEXT PRIMARY KEY,
    label_en       TEXT,
    label_ko       TEXT,
    description_ko TEXT
);

CREATE TABLE IF NOT EXISTS clauses (
    clause_id    TEXT PRIMARY KEY,
    source_id    TEXT NOT NULL REFERENCES sources(source_id),
    locator      TEXT,
    heading_en   TEXT,
    heading_ko   TEXT,
    topics       TEXT,              -- json array of topic_id
    text_status  TEXT,              -- summary | verbatim | editorial
    verification TEXT,              -- web_verified | model_knowledge | to_verify
    confidence   TEXT,
    summary_en   TEXT,
    summary_ko   TEXT,
    key_parameters TEXT,            -- json object
    source_url   TEXT,
    notes        TEXT
);

CREATE TABLE IF NOT EXISTS crosswalk (
    cw_id           TEXT PRIMARY KEY,
    topic_id        TEXT REFERENCES topics(topic_id),
    question_en     TEXT,
    question_ko     TEXT,
    summary_ko      TEXT,
    divergence_note TEXT,
    clause_ids      TEXT             -- json array
);

CREATE TABLE IF NOT EXISTS crosswalk_positions (
    cw_id     TEXT NOT NULL REFERENCES crosswalk(cw_id),
    source_id TEXT NOT NULL REFERENCES sources(source_id),
    relation  TEXT NOT NULL,
    note      TEXT,
    PRIMARY KEY (cw_id, source_id)
);

CREATE TABLE IF NOT EXISTS chunks (
    chunk_id        INTEGER PRIMARY KEY,
    kind            TEXT NOT NULL,   -- clause | crosswalk | source | raw
    ref_id          TEXT NOT NULL,   -- clause_id / cw_id / source_id / raw doc key
    source_id       TEXT,
    jurisdiction    TEXT,
    framework       TEXT,
    topics          TEXT,            -- comma separated topic ids (filterable)
    text_status     TEXT,
    verification    TEXT,
    title           TEXT,
    text            TEXT NOT NULL,
    metadata        TEXT,            -- json
    embedding       BLOB,            -- optional, filled by an external embedder
    embedding_model TEXT
);

CREATE INDEX IF NOT EXISTS idx_chunks_kind      ON chunks(kind);
CREATE INDEX IF NOT EXISTS idx_chunks_source    ON chunks(source_id);
CREATE INDEX IF NOT EXISTS idx_chunks_juris     ON chunks(jurisdiction);
CREATE INDEX IF NOT EXISTS idx_clauses_source   ON clauses(source_id);

CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(
    title,
    text,
    content='chunks',
    content_rowid='chunk_id',
    tokenize="unicode61 remove_diacritics 2"
);

CREATE TRIGGER IF NOT EXISTS chunks_ai AFTER INSERT ON chunks BEGIN
    INSERT INTO chunks_fts(rowid, title, text) VALUES (new.chunk_id, new.title, new.text);
END;
CREATE TRIGGER IF NOT EXISTS chunks_ad AFTER DELETE ON chunks BEGIN
    INSERT INTO chunks_fts(chunks_fts, rowid, title, text) VALUES('delete', old.chunk_id, old.title, old.text);
END;
CREATE TRIGGER IF NOT EXISTS chunks_au AFTER UPDATE ON chunks BEGIN
    INSERT INTO chunks_fts(chunks_fts, rowid, title, text) VALUES('delete', old.chunk_id, old.title, old.text);
    INSERT INTO chunks_fts(rowid, title, text) VALUES (new.chunk_id, new.title, new.text);
END;
"""

CURATED_TABLES = ["crosswalk_positions", "crosswalk", "clauses", "topics", "sources"]


def load_yaml(path: pathlib.Path):
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def j(value) -> str | None:
    return None if value is None else json.dumps(value, ensure_ascii=False)


def _chunk_title(src: dict, clause: dict) -> str:
    """Doc number + locator, without repeating the doc number when the locator
    already carries it (Czech locators do, US ones do not)."""
    doc = (src.get("doc_number") or "").strip()
    loc = (clause.get("locator") or "").strip()
    if loc and doc and loc.startswith(doc):
        return loc
    return f"{doc} {loc}".strip()


def build_clause_chunk_text(clause: dict, source: dict) -> str:
    """One chunk per clause, carrying its own citation header.

    The header is repeated inside the chunk body on purpose: after retrieval the
    chunk is pasted into a prompt on its own, and it has to stay self-describing.
    Both language fields go in the same chunk so Korean and English queries hit
    the same record.
    """
    lines = [
        f"[{source.get('jurisdiction')} | {source.get('doc_number')}] {clause.get('locator') or ''}".strip(),
        f"{clause.get('heading_en') or ''} / {clause.get('heading_ko') or ''}".strip(" /"),
        "",
    ]
    if clause.get("summary_en"):
        lines += ["EN: " + clause["summary_en"].strip(), ""]
    if clause.get("summary_ko"):
        lines += ["KO: " + clause["summary_ko"].strip(), ""]
    kp = clause.get("key_parameters")
    if kp:
        lines.append("KEY PARAMETERS: " + json.dumps(kp, ensure_ascii=False))
        lines.append("")
    if clause.get("notes"):
        lines += ["NOTE: " + clause["notes"].strip(), ""]
    lines.append(
        "PROVENANCE: source={sid} status={st} verification={v} confidence={c} url={u}".format(
            sid=clause.get("source_id"),
            st=clause.get("text_status"),
            v=clause.get("verification"),
            c=clause.get("confidence") or "n/a",
            u=clause.get("source_url") or (source.get("urls") or [""])[0],
        )
    )
    return "\n".join(lines).strip()


def build_crosswalk_chunk_text(cw: dict, positions: list[dict]) -> str:
    lines = [
        f"[CROSSWALK {cw['cw_id']} | topic {cw.get('topic_id')}]",
        f"Q(EN): {cw.get('question_en','')}",
        f"Q(KO): {cw.get('question_ko','')}",
        "",
    ]
    if cw.get("summary_ko"):
        lines += [cw["summary_ko"].strip(), ""]
    lines.append("POSITIONS:")
    for p in positions:
        lines.append(f"  - {p['source_id']}: [{p['relation']}] {p.get('note','')}".rstrip())
    if cw.get("divergence_note"):
        lines += ["", "DIVERGENCE: " + cw["divergence_note"].strip()]
    return "\n".join(lines).strip()


def build_source_chunk_text(src: dict) -> str:
    lines = [
        f"[SOURCE {src['source_id']}] {src.get('doc_number','')} — {src.get('title_orig','')}",
        f"KO: {src.get('title_ko','')}",
        f"Issuer: {src.get('issuer','')} | type: {src.get('instrument_type','')} | binding: {src.get('binding')}",
        f"Version: {src.get('version','')} | jurisdiction: {src.get('jurisdiction')} | language: {src.get('language')}",
        f"Access: {src.get('access')}",
    ]
    if src.get("supersedes"):
        lines.append(f"Supersedes: {src['supersedes']}")
    if src.get("role"):
        lines += ["", "ROLE: " + src["role"].strip()]
    if src.get("copyright_note"):
        lines += ["", "COPYRIGHT: " + src["copyright_note"].strip()]
    lines += ["", "URLS: " + " | ".join(src.get("urls") or [])]
    return "\n".join(lines).strip()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--db", type=pathlib.Path, default=DEFAULT_DB)
    ap.add_argument("--purge-raw", action="store_true",
                    help="also delete chunks previously added by ingest_raw.py")
    args = ap.parse_args()

    args.db.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(args.db)
    con.execute("PRAGMA foreign_keys = ON")
    con.executescript(SCHEMA)

    # Rebuild curated content only; raw-ingested chunks survive unless purged.
    con.execute("DELETE FROM chunks WHERE kind != 'raw'")
    if args.purge_raw:
        con.execute("DELETE FROM chunks WHERE kind = 'raw'")
    for table in CURATED_TABLES:
        con.execute(f"DELETE FROM {table}")

    # ---- sources -------------------------------------------------------
    src_doc = load_yaml(ROOT / "config" / "sources.yaml")
    sources: dict[str, dict] = {}
    for s in src_doc["sources"]:
        sources[s["source_id"]] = s
        con.execute(
            """INSERT INTO sources (source_id, jurisdiction, framework, doc_number, title_orig,
                                    title_en, title_ko, issuer, instrument_type, binding, version,
                                    issue_date, effective_date, language, access, copyright_note,
                                    role, urls, raw)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (s["source_id"], s["jurisdiction"], s.get("framework"), s.get("doc_number"),
             s.get("title_orig"), s.get("title_en"), s.get("title_ko"), s.get("issuer"),
             s.get("instrument_type"), 1 if s.get("binding") else 0, s.get("version"),
             s.get("issue_date"), s.get("effective_date"), s.get("language"), s.get("access"),
             s.get("copyright_note"), s.get("role"), j(s.get("urls")), j(s)),
        )
        con.execute(
            """INSERT INTO chunks (kind, ref_id, source_id, jurisdiction, framework, topics,
                                   text_status, verification, title, text, metadata)
               VALUES ('source',?,?,?,?,'','editorial','web_verified',?,?,?)""",
            (s["source_id"], s["source_id"], s["jurisdiction"], s.get("framework"),
             f"{s.get('doc_number')} — {s.get('title_orig')}",
             build_source_chunk_text(s), j({"urls": s.get("urls"), "access": s.get("access")})),
        )

    # ---- topics --------------------------------------------------------
    topic_doc = load_yaml(ROOT / "corpus" / "crosswalk" / "topics.yaml")
    for t in topic_doc["topics"]:
        con.execute("INSERT INTO topics VALUES (?,?,?,?)",
                    (t["topic_id"], t.get("label_en"), t.get("label_ko"), t.get("description_ko")))

    # ---- clauses -------------------------------------------------------
    n_clauses = 0
    for path in sorted((ROOT / "corpus" / "clauses").glob("*.yaml")):
        doc = load_yaml(path)
        default_sid = doc["source_id"]
        for c in doc["clauses"]:
            sid = c.get("source_id", default_sid)
            if sid not in sources:
                raise SystemExit(f"{path.name}: clause {c['clause_id']} references unknown source {sid}")
            src = sources[sid]
            topics = c.get("topics") or []
            con.execute(
                """INSERT INTO clauses VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (c["clause_id"], sid, c.get("locator"), c.get("heading_en"), c.get("heading_ko"),
                 j(topics), c.get("text_status"), c.get("verification"), c.get("confidence"),
                 (c.get("summary_en") or "").strip(), (c.get("summary_ko") or "").strip(),
                 j(c.get("key_parameters")), c.get("source_url"), (c.get("notes") or "").strip()),
            )
            c_full = dict(c, source_id=sid)
            con.execute(
                """INSERT INTO chunks (kind, ref_id, source_id, jurisdiction, framework, topics,
                                       text_status, verification, title, text, metadata)
                   VALUES ('clause',?,?,?,?,?,?,?,?,?,?)""",
                (c["clause_id"], sid, src["jurisdiction"], src.get("framework"), ",".join(topics),
                 c.get("text_status"), c.get("verification"),
                 _chunk_title(src, c),
                 build_clause_chunk_text(c_full, src),
                 j({"locator": c.get("locator"), "confidence": c.get("confidence"),
                    "source_url": c.get("source_url"), "topics": topics})),
            )
            n_clauses += 1

    # ---- crosswalk -----------------------------------------------------
    cw_doc = load_yaml(ROOT / "corpus" / "crosswalk" / "crosswalk.yaml")
    for cw in cw_doc["crosswalk"]:
        positions = cw.get("positions") or []
        con.execute("INSERT INTO crosswalk VALUES (?,?,?,?,?,?,?)",
                    (cw["cw_id"], cw.get("topic_id"), cw.get("question_en"), cw.get("question_ko"),
                     (cw.get("summary_ko") or "").strip(), (cw.get("divergence_note") or "").strip(),
                     j(cw.get("clause_ids"))))
        for p in positions:
            if p["source_id"] not in sources:
                raise SystemExit(f"crosswalk {cw['cw_id']} references unknown source {p['source_id']}")
            con.execute("INSERT OR REPLACE INTO crosswalk_positions VALUES (?,?,?,?)",
                        (cw["cw_id"], p["source_id"], p["relation"], p.get("note")))
        con.execute(
            """INSERT INTO chunks (kind, ref_id, source_id, jurisdiction, framework, topics,
                                   text_status, verification, title, text, metadata)
               VALUES ('crosswalk',?,NULL,'MULTI','crosswalk',?, 'editorial','web_verified',?,?,?)""",
            (cw["cw_id"], cw.get("topic_id") or "",
             f"{cw['cw_id']}: {cw.get('question_ko') or cw.get('question_en')}",
             build_crosswalk_chunk_text(cw, positions),
             j({"topic_id": cw.get("topic_id"),
                "sources": [p["source_id"] for p in positions],
                "clause_ids": cw.get("clause_ids")})),
        )

    # ---- referential integrity -------------------------------------------
    # crosswalk.clause_ids is a json array of clause_id, so SQLite cannot
    # enforce it. Records get rewritten often; a dangling id silently drops a
    # citation from the retrieved context, so fail the build instead.
    dangling = con.execute(
        """SELECT cw.cw_id, je.value FROM crosswalk cw, json_each(cw.clause_ids) je
           WHERE je.value NOT IN (SELECT clause_id FROM clauses)"""
    ).fetchall()
    if dangling:
        lines = "\n".join(f"  {cw} -> {cid}" for cw, cid in dangling)
        raise SystemExit(f"dangling crosswalk clause_ids:\n{lines}")

    con.commit()
    counts = {t: con.execute(f"SELECT count(*) FROM {t}").fetchone()[0]
              for t in ["sources", "topics", "clauses", "crosswalk", "crosswalk_positions", "chunks"]}
    by_kind = dict(con.execute("SELECT kind, count(*) FROM chunks GROUP BY kind").fetchall())
    con.execute("INSERT INTO chunks_fts(chunks_fts) VALUES('optimize')")
    con.commit()
    con.close()

    print(f"built {args.db}")
    for k, v in counts.items():
        print(f"  {k:22s} {v}")
    print(f"  chunks by kind        {by_kind}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
