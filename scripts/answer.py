#!/usr/bin/env python3
"""Answer a question from the database with Claude, citing the retrieved chunks.

    export ANTHROPIC_API_KEY=...        # or: ant auth login
    python3 scripts/answer.py "체코와 미국의 항공기 충돌 설계기준 차이는?"
    python3 scripts/answer.py "What screening frequency applies?" -k 10

Retrieval is grounded: the model is told to answer only from the supplied
documents and to carry each document's provenance flag into the answer, so a
summary written from unverified knowledge cannot silently become a citation.
"""
from __future__ import annotations

import argparse
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import retrieval  # noqa: E402

MODEL = "claude-opus-5"

SYSTEM = """You answer questions about aircraft impact / aircraft crash requirements for \
nuclear installations, using ONLY the regulatory documents supplied in <doc> blocks.

Rules:
1. Ground every statement in a supplied document and cite it by its ref attribute, \
e.g. (CZ-329-2017-aircraft-dbe) or (CW-04).
2. Each document carries a verification attribute. Respect it in your answer:
   - primary_source : verbatim text from the official document — cite freely.
   - web_verified   : summary confirmed against a retrieved source — reliable.
   - model_knowledge: an UNVERIFIED summary. Say so when you rely on it.
   - to_verify      : the locator or content is uncertain. Warn the reader explicitly.
3. If the documents do not answer the question, say so plainly. Do not fill the gap \
from your own knowledge of these regulations, and never invent a section number, a \
numeric threshold, or a quotation.
4. Where frameworks differ structurally rather than numerically, say that they are not \
directly comparable and explain why.
5. Answer in the language the user asked in."""


def build_prompt(question: str, context: str) -> str:
    return (
        f"<documents>\n{context}\n</documents>\n\n"
        f"Question: {question}\n\n"
        "Answer from the documents above, with inline (ref) citations."
    )


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("question")
    ap.add_argument("--db", type=pathlib.Path, default=retrieval.DEFAULT_DB)
    ap.add_argument("-k", type=int, default=8)
    ap.add_argument("--jurisdiction")
    ap.add_argument("--topic")
    ap.add_argument("--show-context", action="store_true")
    args = ap.parse_args()

    try:
        import anthropic
    except ImportError:
        raise SystemExit("pip install anthropic")

    con = retrieval.connect(args.db)
    rows = retrieval.expand_with_crosswalk(
        con,
        retrieval.search(con, args.question, k=args.k,
                         jurisdiction=args.jurisdiction, topic=args.topic),
    )
    if not rows:
        print("no matching documents in the database — nothing to ground an answer on")
        return 1
    context = retrieval.format_context(rows)
    if args.show_context:
        print(context, "\n" + "=" * 72 + "\n")

    client = anthropic.Anthropic()
    kwargs = dict(
        model=MODEL,
        max_tokens=16000,
        thinking={"type": "adaptive"},
        system=[{"type": "text", "text": SYSTEM, "cache_control": {"type": "ephemeral"}}],
        messages=[{"role": "user", "content": build_prompt(args.question, context)}],
    )
    try:
        # Server-side fallback keeps the call alive if a safety classifier declines.
        resp = client.beta.messages.create(
            betas=["server-side-fallback-2026-07-01"], fallbacks="default", **kwargs
        )
    except (AttributeError, TypeError, anthropic.APIStatusError):
        resp = client.messages.create(**kwargs)

    if getattr(resp, "stop_reason", None) == "refusal":
        detail = getattr(resp, "stop_details", None)
        print(f"the model declined to answer (stop_reason=refusal, details={detail})")
        return 1

    print("\n".join(b.text for b in resp.content if b.type == "text"))
    print("\n--- grounded on ---")
    for i, r in enumerate(rows, 1):
        print(f"  [{i}] {r['ref_id']} ({r['verification']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
