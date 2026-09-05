#!/usr/bin/env python3
"""회차 본문 글자 수 측정. CLAUDE.md 1항 기준 3,500~4,500자.

측정 기준: `*` 구분선 줄을 제외한 모든 줄의 글자 수(공백 포함).
사용법: python3 pipeline/count.py [회차번호 ...]
"""
import glob, re, sys

FLOOR, CEIL = 3500, 4500


def count(path):
    t = open(path).read()
    return len("".join(l for l in t.split("\n") if l.strip() != "*"))


def main():
    want = set(int(a) for a in sys.argv[1:])
    rows = []
    for p in sorted(glob.glob("episodes/part*/ep_*.md")):
        n = int(re.search(r"ep_(\d+)", p).group(1))
        if want and n not in want:
            continue
        rows.append((n, count(p)))

    for n, c in rows:
        mark = "  " if FLOOR <= c <= CEIL else ("↓ " if c < FLOOR else "↑ ")
        print("%s%3d화  %5d자" % (mark, n, c))

    if not rows:
        return
    nums = [c for _, c in rows]
    under = [n for n, c in rows if c < FLOOR]
    over = [n for n, c in rows if c > CEIL]
    print("-" * 24)
    print("%d편  평균 %d자  (%d~%d)" % (len(rows), sum(nums) / len(nums), min(nums), max(nums)))
    print("미달 %d편: %s" % (len(under), under or "없음"))
    print("초과 %d편: %s" % (len(over), over or "없음"))


if __name__ == "__main__":
    main()
