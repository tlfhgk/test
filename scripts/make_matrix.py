#!/usr/bin/env python3
"""Regenerate docs/comparison-matrix.md from the database.

Keeps the human-readable matrix from drifting away from corpus/crosswalk/.

    python3 scripts/make_matrix.py
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sqlite3
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DEFAULT_DB = ROOT / "db" / "aircraft_impact.db"
DEFAULT_OUT = ROOT / "docs" / "comparison-matrix.md"

# Column order for the matrix: the US baseline first, then CZ, EU, IAEA.
COLUMNS = [
    ("US-10CFR50.150", "10 CFR 50.150"),
    ("US-RG-1.217", "RG 1.217"),
    ("US-NEI-07-13", "NEI 07-13"),
    ("CZ-329-2017", "CZ 329/2017"),
    ("EU-EUR", "EUR"),
    ("EU-WENRA-SRL", "WENRA"),
    ("IAEA-SSG-68", "SSG-68"),
    ("IAEA-SRS-87", "SRS-87"),
]

MARK = {
    "baseline": "**기준**",
    "equivalent": "동등",
    "partial": "부분",
    "stricter": "더 엄격",
    "looser": "더 완화",
    "different-architecture": "구조 상이",
    "no-equivalent": "없음",
    "not-public": "비공개",
}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--db", type=pathlib.Path, default=DEFAULT_DB)
    ap.add_argument("--out", type=pathlib.Path, default=DEFAULT_OUT)
    args = ap.parse_args()

    if not args.db.exists():
        raise SystemExit(f"database not found: {args.db}\nrun: python3 scripts/build_db.py")
    con = sqlite3.connect(args.db)
    con.row_factory = sqlite3.Row

    topics = {r["topic_id"]: r for r in con.execute("SELECT * FROM topics")}
    rows = list(con.execute("SELECT * FROM crosswalk ORDER BY cw_id"))
    positions: dict[str, dict[str, sqlite3.Row]] = {}
    for p in con.execute("SELECT * FROM crosswalk_positions"):
        positions.setdefault(p["cw_id"], {})[p["source_id"]] = p

    out: list[str] = [
        "# 비교 매트릭스 — 항공기 충돌 규제 (NEI 07-13 기준)",
        "",
        "> 자동 생성 파일입니다. 직접 수정하지 마세요.",
        "> `corpus/crosswalk/crosswalk.yaml` 을 고친 뒤 "
        "`python3 scripts/build_db.py && python3 scripts/make_matrix.py` 를 실행하세요.",
        "",
        "기준(baseline)은 미국 방법론(10 CFR 50.150 → RG 1.217 → NEI 07-13)이며, "
        "각 칸은 그 기준 대비 해당 문서의 위치를 나타냅니다.",
        "",
        "| # | 비교 항목 | " + " | ".join(label for _, label in COLUMNS) + " |",
        "|---|---|" + "---|" * len(COLUMNS),
    ]
    for r in rows:
        cells = []
        for sid, _ in COLUMNS:
            p = positions.get(r["cw_id"], {}).get(sid)
            cells.append(MARK.get(p["relation"], p["relation"]) if p else "–")
        q = (r["question_ko"] or r["question_en"] or "").replace("|", "\\|")
        out.append(f"| {r['cw_id']} | {q} | " + " | ".join(cells) + " |")

    out += ["", "범례: " + " · ".join(f"`{k}` = {v}" for k, v in MARK.items()) + " · `–` 해당 항목에 기재 없음", "",
            "---", "", "## 항목별 상세", ""]

    for r in rows:
        topic = topics.get(r["topic_id"])
        out += [
            f"### {r['cw_id']} — {r['question_ko'] or r['question_en']}",
            "",
            f"*주제 축: {r['topic_id']} {topic['label_ko'] if topic else ''} "
            f"({topic['label_en'] if topic else ''})*",
            "",
            f"**EN:** {r['question_en']}",
            "",
            r["summary_ko"] or "",
            "",
            "| 문서 | 관계 | 내용 |",
            "|---|---|---|",
        ]
        for sid, p in positions.get(r["cw_id"], {}).items():
            note = (p["note"] or "").replace("|", "\\|")
            out.append(f"| `{sid}` | {MARK.get(p['relation'], p['relation'])} | {note} |")
        if r["divergence_note"]:
            out += ["", f"> **차이점/유의사항:** {r['divergence_note']}"]
        refs = json.loads(r["clause_ids"] or "[]")
        if refs:
            out += ["", "근거 조항: " + ", ".join(f"`{c}`" for c in refs)]
        out.append("")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(out).rstrip() + "\n", encoding="utf-8")
    con.close()
    print(f"wrote {args.out} ({len(rows)} crosswalk entries)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
