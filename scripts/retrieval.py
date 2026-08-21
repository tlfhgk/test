"""Shared retrieval layer over the aircraft-impact database.

BM25 (FTS5) with metadata filters, plus a substring fallback. Korean queries
work because FTS5's unicode61 tokenizer treats Hangul as letters and Korean is
space-delimited; the fallback covers the case where a query word is glued to a
particle (e.g. "항공기충돌" vs the indexed "항공기 충돌").
"""
from __future__ import annotations

import pathlib
import re
import sqlite3

ROOT = pathlib.Path(__file__).resolve().parent.parent
DEFAULT_DB = ROOT / "db" / "aircraft_impact.db"

# Words that add nothing to a BM25 query over this corpus.
_STOP = {
    "the", "a", "an", "of", "for", "and", "or", "to", "in", "on", "is", "are",
    "what", "which", "how", "does", "do", "vs", "versus",
    "무엇", "어떻게", "인가", "인가요", "알려줘", "비교", "차이",
}
_TOKEN_RE = re.compile(r"[0-9A-Za-z가-힣À-ɏ._§/-]+")


def connect(db: pathlib.Path | str = DEFAULT_DB) -> sqlite3.Connection:
    db = pathlib.Path(db)
    if not db.exists():
        raise SystemExit(f"database not found: {db}\nrun: python3 scripts/build_db.py")
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    return con


def tokenize(query: str) -> list[str]:
    toks = [t for t in _TOKEN_RE.findall(query)]
    kept = [t for t in toks if t.lower() not in _STOP and len(t) > 1]
    return kept or toks


def to_fts_query(query: str) -> str:
    """Build an OR-of-terms FTS5 expression; BM25 then ranks by term overlap.

    Each term is double-quoted so that '§', '.', '/' and '10 CFR 50.150' style
    tokens cannot be read as FTS5 operators.
    """
    terms = [t.replace('"', '""') for t in tokenize(query)]
    return " OR ".join(f'"{t}"' for t in terms) if terms else '""'


def _filter_sql(jurisdiction=None, source_id=None, topic=None, kind=None,
                verification=None) -> tuple[str, list]:
    clauses, params = [], []
    if jurisdiction:
        clauses.append("c.jurisdiction = ?")
        params.append(jurisdiction)
    if source_id:
        clauses.append("c.source_id = ?")
        params.append(source_id)
    if topic:
        clauses.append("(',' || c.topics || ',') LIKE ?")
        params.append(f"%,{topic},%")
    if kind:
        clauses.append("c.kind = ?")
        params.append(kind)
    if verification:
        clauses.append("c.verification = ?")
        params.append(verification)
    return (" AND " + " AND ".join(clauses)) if clauses else "", params


def search(con: sqlite3.Connection, query: str, k: int = 8, **filters) -> list[sqlite3.Row]:
    where, params = _filter_sql(**filters)
    sql = f"""
        SELECT c.*, bm25(chunks_fts, 2.0, 1.0) AS score
        FROM chunks_fts
        JOIN chunks c ON c.chunk_id = chunks_fts.rowid
        WHERE chunks_fts MATCH ?{where}
        ORDER BY score
        LIMIT ?
    """
    rows = con.execute(sql, [to_fts_query(query), *params, k]).fetchall()
    if rows:
        return rows
    return _substring_search(con, query, k, filters)


def _substring_search(con: sqlite3.Connection, query: str, k: int, filters: dict) -> list[sqlite3.Row]:
    where, params = _filter_sql(**filters)
    terms = tokenize(query)
    if not terms:
        return []
    like = " OR ".join(["c.text LIKE ?"] * len(terms))
    sql = f"SELECT c.*, 0.0 AS score FROM chunks c WHERE ({like}){where} LIMIT ?"
    return con.execute(sql, [*[f"%{t}%" for t in terms], *params, k]).fetchall()


def get_chunk(con: sqlite3.Connection, ref_id: str) -> sqlite3.Row | None:
    return con.execute("SELECT *, 0.0 AS score FROM chunks WHERE ref_id = ? LIMIT 1", (ref_id,)).fetchone()


def expand_with_crosswalk(con: sqlite3.Connection, rows: list[sqlite3.Row],
                          limit: int = 4) -> list[sqlite3.Row]:
    """Pull in the crosswalk entries that cite any retrieved clause.

    Comparison questions ("how does X differ from NEI 07-13") are answered by the
    crosswalk records, but a query phrased in the vocabulary of one clause often
    retrieves only that clause. This closes the gap.
    """
    have = {r["ref_id"] for r in rows}
    clause_ids = [r["ref_id"] for r in rows if r["kind"] == "clause"]
    if not clause_ids:
        return rows
    extra: list[sqlite3.Row] = []
    placeholders = ",".join("?" * len(clause_ids))
    cw_ids = con.execute(
        f"""SELECT DISTINCT cw.cw_id FROM crosswalk cw, json_each(cw.clause_ids) je
            WHERE je.value IN ({placeholders})""",
        clause_ids,
    ).fetchall()
    for row in cw_ids:
        if row["cw_id"] in have or len(extra) >= limit:
            continue
        chunk = get_chunk(con, row["cw_id"])
        if chunk is not None:
            extra.append(chunk)
            have.add(row["cw_id"])
    return rows + extra


def format_context(rows) -> str:
    """Assemble retrieved chunks into a citable prompt context block."""
    blocks = []
    for i, r in enumerate(rows, 1):
        blocks.append(
            f"<doc id=\"{i}\" ref=\"{r['ref_id']}\" kind=\"{r['kind']}\" "
            f"jurisdiction=\"{r['jurisdiction']}\" verification=\"{r['verification']}\">\n"
            f"{r['text']}\n</doc>"
        )
    return "\n\n".join(blocks)
