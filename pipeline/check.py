# -*- coding: utf-8 -*-
"""회차 검수기 — 집필 후 반드시 돌린다.

《은자림 막내일기》를 쓰면서 실제로 저지른 오류들을 유형화해 기계로 잡는다.
사용법:
    python3 pipeline/check.py            # 전 회차
    python3 pipeline/check.py 29 30 31   # 지정 회차
    python3 pipeline/check.py --range 1 50
"""
import glob, json, os, re, sys

FLOOR, CEIL = 3500, 4500
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

NUM = {"한": 1, "두": 2, "세": 3, "네": 4, "다섯": 5, "여섯": 6, "일곱": 7,
       "여덟": 8, "아홉": 9, "열": 10, "열한": 11, "열두": 12}
NUM_R = {v: k for k, v in NUM.items()}
MONTH = ["한", "두", "석", "넉", "다섯", "여섯", "일곱", "여덟", "아홉", "열", "열한", "열두"]

SEP = re.compile(r"^\s*(\*|◇|---|===|~~~)\s*$")
BANNED_PUNCT = [("!!!", "감탄사 남발"), ("?!", "금지 문장부호"),
                ("~", "물결 금지"), ("!?", "금지 문장부호")]
EMOJI = re.compile(r"[\U0001F300-\U0001FAFF☀-➿]")
QUOTE = re.compile(r'[「"\'](.{1,24}?)[」"\']')
CNTCLAIM = re.compile(r"(한|두|세|네|다섯|여섯|일곱|여덟|아홉|열한|열두|열)\s*글자(?!씩)")
ONOM = re.compile(r"(쿵|쾅|퍽|턱|툭|탁|딱|우르르|와르르|쨍|철썩|후두둑|스르륵|쿠궁|콰|삐걱)")
META = re.compile(r"\d+\s*화(의|에|에서|를|는|가)?\s")
HANJA = re.compile(r"([가-힣]{2,6})\(([一-龥]{1,6})\)")


def norm_quote(q):
    """인용구에서 앞뒤 문장부호를 떼어낸 알맹이. 글자 수는 이것으로 센다."""
    q = q.strip().strip("…").strip()
    q = q.rstrip(".?!,…").strip()
    q = q.lstrip("…").strip()
    return q


def load(path):
    txt = open(path, encoding="utf-8").read()
    return [l.rstrip() for l in txt.split("\n")]


def body_chars(lines):
    return len("".join(lines))


def sentences(line):
    s = re.sub(r'^[「"\'].*[」"\']$', "", line)
    return len(re.findall(r"[.?!](?:\s|$)", s))


def check_one(path, reg, report):
    n = int(re.search(r"ep_(\d+)", path).group(1))
    lines = load(path)
    add = lambda sev, msg: report.append((n, sev, msg))

    # 1) 분량
    c = body_chars(lines)
    if c < FLOOR:
        add("오류", "분량 %d자 — 하한 미달. 문장을 늘리지 말고 장면을 하나 더 넣는다" % c)
    elif c > CEIL + 400:
        add("주의", "분량 %d자 — 상한 초과" % c)

    # 2) 제목 형식
    if not re.match(r"^# \d+화\. .+", lines[0]):
        add("오류", "첫 줄이 「# N화. 제목」 형식이 아니다: %r" % lines[0][:40])

    body = lines[1:]
    for i, l in enumerate(body, start=2):
        # 3) 구분선
        if SEP.match(l):
            add("오류", "%d행 구분선 사용 — 장면 전환은 문장이 짓는다" % i)
        # 4) 금지 문장부호
        for tok, why in BANNED_PUNCT:
            if tok in l:
                add("오류", "%d행 %s (%s)" % (i, tok, why))
        if EMOJI.search(l):
            add("오류", "%d행 이모티콘" % i)
        # 5) 벽돌 문단
        if sentences(l) >= 3:
            add("주의", "%d행 한 줄에 3문장 이상 — 한 문장 = 한 줄" % i)
        # 6) 메타 참조
        if META.search(l) and "화" in l and not l.startswith("#"):
            m = META.search(l)
            add("주의", "%d행 회차 번호 직접 언급(메타 참조): %r" % (i, m.group(0).strip()))

    # 7) 인접·근접 중복 문장
    strip = [l for l in body]
    for i in range(len(strip) - 1):
        a, b = strip[i].strip(), strip[i + 1].strip()
        if a and a == b and len(a) > 4:
            add("오류", "%d행 중복 문장: %r" % (i + 3, a[:40]))
    for i in range(len(strip) - 2):
        a, c2 = strip[i].strip(), strip[i + 2].strip()
        if a and c2 and not strip[i + 1].strip() and len(a) > 15 and (a in c2 or c2 in a) and a != c2:
            add("주의", "%d행 근접 중복: %r ↔ %r" % (i + 3, a[:30], c2[:30]))

    # 8) 인용구 글자 수 대조  ← 「다섯 글자 / 생사는 불문한다」류
    for i, l in enumerate(body, start=2):
        m = CNTCLAIM.search(l)
        if not m:
            continue
        claim = NUM[m.group(1)]
        lo, hi = max(0, i - 16), min(len(body), i + 10)
        cands = []
        for j in range(lo, hi):
            for q in QUOTE.findall(body[j]):
                q = norm_quote(q)
                if q:
                    cands.append(q)
            bare = body[j].strip()
            if bare and 1 < len(bare) <= 14 and not CNTCLAIM.search(bare):
                q = norm_quote(bare)
                if q:
                    cands.append(q)
        if not cands:
            continue
        exact = [q for q in cands if len(q.replace(" ", "")) == claim]
        if not exact:
            near = sorted({(len(q.replace(" ", "")), q) for q in cands})
            add("오류", "%d행 「%s 글자」 주장과 맞는 인용구가 없다 → 주변 후보: %s"
                % (i, m.group(1), ", ".join("%r=%d자" % (q, k) for k, q in near[:4])))

    # 9) 시간 표지 분포
    months = {}
    for i, l in enumerate(body, start=2):
        for mo in re.findall(r"(한|두|석|넉|다섯|여섯|일곱|여덟|아홉|열|열한|열두)\s*달", l):
            months.setdefault(mo, []).append(i)
    if len(months) >= 3:
        add("주의", "한 회차에 경과 표지가 %d종 혼재: %s — 같은 시점을 가리키는지 확인"
            % (len(months), ", ".join("%s 달×%d" % (k, len(v)) for k, v in months.items())))

    # 10) 폐기 표기 부활
    full = "\n".join(lines)
    for e in reg.get("폐기표기", []):
        if e["패턴"] in full:
            add("오류", "폐기 표기 부활 %r — %s (→ %s)" % (e["패턴"], e["사유"], e.get("대체", "")))
    for e in reg.get("금지어", []):
        if e["패턴"] in full:
            sev = "주의" if e.get("등급") == "문체" else "오류"
            add(sev, "금지어 %r — %s" % (e["패턴"], e["사유"]))

    # 11) 의성어 과다
    k = len(ONOM.findall(full))
    if k > 5:
        add("주의", "의성어 %d회 — 회차당 5회 이하. 뼈·바람·무게의 물리 감각으로 대체" % k)

    # 12) 마지막 문장은 한 줄 블록
    tail = [l for l in body if l.strip()]
    if tail:
        idx = len(body) - 1
        while idx >= 0 and not body[idx].strip():
            idx -= 1
        if idx >= 1 and body[idx - 1].strip():
            add("주의", "마지막 문장이 한 줄 블록이 아니다")

    return n, c


def main():
    argv = sys.argv[1:]
    if "--range" in argv:
        k = argv.index("--range")
        want = set(range(int(argv[k + 1]), int(argv[k + 2]) + 1))
    else:
        want = set(int(a) for a in argv if a.isdigit())

    reg = json.load(open(os.path.join(ROOT, "settings/continuity/retired.json"), encoding="utf-8"))
    report, seen = [], []
    for p in sorted(glob.glob(os.path.join(ROOT, "episodes/part*/ep_*.md"))):
        n = int(re.search(r"ep_(\d+)", p).group(1))
        if want and n not in want:
            continue
        seen.append(check_one(p, reg, report))

    # 13) 한자 병기 중복 (회차 간)
    first = {}
    dup = []
    for p in sorted(glob.glob(os.path.join(ROOT, "episodes/part*/ep_*.md"))):
        n = int(re.search(r"ep_(\d+)", p).group(1))
        for ko, ha in HANJA.findall(open(p, encoding="utf-8").read()):
            key = ko + "(" + ha + ")"
            if key in first:
                if not want or n in want:
                    dup.append((n, key, first[key]))
            else:
                first[key] = n
    for n, key, f in dup:
        report.append((n, "주의", "한자 병기 재등장 %s — 첫 등장 %d화 1회만" % (key, f)))

    err = [r for r in report if r[1] == "오류"]
    warn = [r for r in report if r[1] == "주의"]
    for n, sev, msg in sorted(report):
        print("%s %3d화  %s" % ("✗" if sev == "오류" else "·", n, msg))
    print("-" * 60)
    print("검사 %d편 / 오류 %d건 / 주의 %d건" % (len(seen), len(err), len(warn)))
    return 1 if err else 0


if __name__ == "__main__":
    sys.exit(main())
