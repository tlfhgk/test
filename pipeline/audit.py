# -*- coding: utf-8 -*-
"""전작 단위 정합성 감사 — check.py가 못 보는 '회차 사이'를 본다.

check.py  : 회차 하나 안에서 닫히는 오류 (분량·조판·금지어·인용구 글자수)
audit.py  : 회차를 가로질러야 보이는 오류 (고아 번호·장기 부재·복선 미회수·수치 드리프트)

검사 범주는 Novalist(Drommedhar)의 Story Validator 여섯 갈래를 이 원고 구조에
맞춰 옮긴 것이다. 타임라인 / 인물(고아·장기부재) / 플롯 공백 / 구조 / 연속성 / 페이싱.

사용법: python3 pipeline/audit.py [--quiet]
"""
import csv, glob, json, os, re, sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R = lambda *a: os.path.join(ROOT, *a)

# 마당에 실제로 거주하는 주요 인물 (장기 부재 검사 대상)
CAST = ["곽진강", "천 노인", "임 노파", "구 노인", "백 영감", "화척", "표일도", "유백", "남궁호"]
ABSENCE_LIMIT = {"곽진강": 3, "천 노인": 25, "임 노파": 25, "구 노인": 40,
                 "백 영감": 30, "화척": 20, "표일도": 40, "유백": 45, "남궁호": 60}
MAX_HO = 13          # 정전 최대 번호 (농노는 2호~13호 열둘. 130화 유백은 9호를 물려받는다)
NAME = re.compile(r"[가-힣]{2,4}(?=[이가은는을를의에게와과도]?\s)")


def episodes():
    out = []
    for p in sorted(glob.glob(R("episodes", "part*", "ep_*.md"))):
        n = int(re.search(r"ep_(\d+)", p).group(1))
        txt = "\n".join(l.rstrip() for l in open(p, encoding="utf-8").read().split("\n"))
        out.append((n, p, txt))
    return out


def main():
    eps = episodes()
    total = len(eps)
    rep = []
    add = lambda cat, msg: rep.append((cat, msg))

    # ── 1. 번호 대장: 고아 번호와 정전 이탈 ────────────────────────────
    ho = defaultdict(list)
    for n, _, t in eps:
        for m in set(re.findall(r"(?<![0-9])([0-9]{1,2})호(?!선|수|남|각|텔)", t)):
            ho[int(m)].append(n)
    for k in sorted(ho):
        if k > MAX_HO:
            add("인물", "%d호는 정전 최대 %d호를 넘는다 — 등장: %s화"
                % (k, MAX_HO, ", ".join(map(str, ho[k][:6]))))
        elif len(ho[k]) == 1:
            add("인물", "%d호가 %d화에 단 한 번 나온다 (고아 번호). 입주 장면이 있는지 확인"
                % (k, ho[k][0]))

    # ── 2. 주요 인물 장기 부재 ────────────────────────────────────────
    for who in CAST:
        seen = [n for n, _, t in eps if who in t]
        if not seen:
            add("인물", "%s가 한 번도 안 나온다" % who)
            continue
        lim = ABSENCE_LIMIT.get(who, 30)
        prev = seen[0]
        for cur in seen[1:]:
            if cur - prev > lim:
                add("인물", "%s가 %d화 이후 %d화까지 %d화 동안 안 나온다"
                    % (who, prev, cur, cur - prev - 1))
            prev = cur
        if total - prev > lim:
            add("인물", "%s가 %d화 이후 끝까지 %d화 동안 안 나온다" % (who, prev, total - prev))

    # ── 3. 복선: 오해 로그 정합 ───────────────────────────────────────
    lp = R("settings", "nice-to-have", "misunderstanding-log.json")
    if os.path.exists(lp):
        log = json.load(open(lp, encoding="utf-8"))
        items = log.get("log", log if isinstance(log, list) else [])
        ids = set()
        MARK = re.compile(r"[0-9]부|미회수|미기록|예정|진행\s*중|안 올라감|없음")

        def num(v):
            """회차 번호를 숫자로. 「94화~」는 94, 「3부」·「영구 미기록」은 None."""
            if isinstance(v, int):
                return v
            t = str(v or "").strip()
            if t.isdigit():
                return int(t)
            m = re.fullmatch(r"(\d+)\s*화\s*[~-]?", t)
            return int(m.group(1)) if m else None

        def planned(v):
            return bool(MARK.search(str(v or "")))

        for e in items:
            i = e.get("id")
            o, s = num(e.get("ep_origin")), num(e.get("ep_surface"))
            if planned(e.get("ep_surface")):
                continue
            if i in ids:
                add("복선", "%s 항목이 중복이다" % i)
            ids.add(i)
            if o and o > total:
                add("복선", "%s의 ep_origin %d화가 아직 없다" % (i, o))
            if s and o and s < o:
                add("복선", "%s의 소문(%d화)이 사건(%d화)보다 먼저다" % (i, s, o))
            if s is None:
                add("복선", "%s의 ep_surface가 비어 있다 — 회수 회차나 「3부」 같은 표식을 적는다" % i)

    # ── 4. 트래커 동기화 ──────────────────────────────────────────────
    tp = R("pipeline", "plot-tracker.csv")
    if os.path.exists(tp):
        rows = list(csv.DictReader(open(tp, encoding="utf-8")))
        have = {int(r["ep"]): r for r in rows if r.get("ep", "").isdigit()}
        for n, p, t in eps:
            if n not in have:
                add("구조", "%d화가 plot-tracker.csv에 없다" % n)
                continue
            r = have[n]
            real = len(t.replace("\n", ""))
            try:
                rec = int(r.get("prose_chars") or 0)
            except ValueError:
                rec = 0
            if rec and abs(rec - real) > max(60, real * 0.02):
                add("구조", "%d화 트래커 분량 %d자 ≠ 실제 %d자 (%+d)" % (n, rec, real, real - rec))
            if (r.get("status") or "").strip() != "done":
                add("구조", "%d화 status가 %r다" % (n, r.get("status")))
            for col in ("hook", "laugh", "martial"):
                if not (r.get(col) or "").strip() or (r.get(col) or "").strip() == "-":
                    add("구조", "%d화 트래커 %s 칸이 비었다" % (n, col))
        for k in sorted(set(have) - {n for n, _, _ in eps}):
            add("구조", "트래커에 %d화 행이 있는데 원고가 없다" % k)

    # ── 5. 페이싱: 분량 이탈 ──────────────────────────────────────────
    lens = [(n, len(t.replace("\n", ""))) for n, _, t in eps]
    avg = sum(c for _, c in lens) / len(lens)
    for n, c in lens:
        if abs(c - avg) / avg > 0.18:
            add("페이싱", "%d화 %d자 — 전체 평균 %d자에서 %+.0f%% 벗어난다"
                % (n, c, avg, (c - avg) / avg * 100))

    # ── 6. 연속성: 회차 간 인원 표기 드리프트 ─────────────────────────
    # 「마당의 / 농노 + 수사」만 본다. 같은 대상에 서로 다른 수가 붙으면 어딘가 틀렸다.
    # 긴 것부터 놓아야 「열다섯」이 「열」로 잘리지 않는다
    CNT = (r"(열여덟|열일곱|열여섯|열다섯|열넷|열셋|열둘|열하나|열한|열두|열아홉|"
           r"스물|다섯|여섯|일곱|여덟|아홉|열|한|두|세|네)")
    crowd = defaultdict(list)
    for n, _, t in eps:
        # 수사 뒤에 셈을 받는 말이 와야 인원이다 (「마당에 한 사람이 서 있었다」는 제외)
        for m in re.findall(r"(?:마당의|농노)\s*" + CNT + r"(?=[이가은는도]\s|\s*(?:명|사람|쪽))", t):
            crowd[m].append(n)
    if len(crowd) > 1:
        for word, where in sorted(crowd.items(), key=lambda x: -len(x[1])):
            add("연속성", "마당 인원을 「%s」로 적은 회차가 %d편 (%s%s)"
                % (word, len(where), ", ".join(map(str, sorted(set(where))[:10])),
                   " …" if len(set(where)) > 10 else ""))
        add("연속성", "→ 인원 표기가 %d가지다. settings/continuity/retired.json의 "
                     "정전 수치와 대조할 것" % len(crowd))

    # ── 7. 연속성: 인물 나이·연차 드리프트 ────────────────────────────
    # 「삼백십이 년 산 노인」이 「이백사십 년 산 노인」과 섞여 있던 것을 잡는다.
    AGE = re.compile(r"([가-힣]{2,8})\s*(년 산|살)")
    age = defaultdict(list)
    for n, _, t in eps:
        for fig, kind in AGE.findall(t):
            if re.fullmatch(r"[일이삼사오육칠팔구십백천만가-힣]{2,8}", fig) and (
                    "백" in fig or "십" in fig):
                age[(fig, kind)].append(n)
    if age:
        top = max(len(v) for v in age.values())
        for (fig, kind), where in sorted(age.items(), key=lambda x: -len(x[1])):
            if len(where) <= 2 and top >= 5:
                add("연속성", "「%s %s」이 %d편에만 나온다 (%s) — 정전 수치와 대조"
                    % (fig, kind, len(where), ", ".join(map(str, sorted(set(where))))))

    # ── 8. 연속성: 마당 인원이 입주 일정과 맞는지 ──────────────────────
    # 9호는 이백 년 전부터 있었고 128화에 죽는다. 유백이 130화에 그 번호를 채운다.
    # 180화에 1호와 상촌 노인이 문턱을 넘어 마당이 열여덟이 된다
    ROSTER = [(1, 5, 6), (6, 12, 10), (13, 21, 11), (22, 127, 16), (128, 129, 15),
              (130, 180, 16), (181, 999, 18)]   # 180화는 넘는 장면 자체라 전후가 섞인다
    WORD = {"다섯": 5, "여섯": 6, "일곱": 7, "여덟": 8, "아홉": 9, "열": 10,
            "열하나": 11, "열한": 11, "열둘": 12, "열두": 12, "열셋": 13,
            "열넷": 14, "열다섯": 15, "열여섯": 16, "열일곱": 17}
    ALT = "|".join(sorted(WORD, key=len, reverse=True))
    HEAD = re.compile(r"(?:마당의|마당에|마당에서)\s*(" + ALT + r")(?=[이가은는도]\s|\s*(?:명|사람))")
    # 은자림이 아닌 마당(폐사·객잔·총단·하촌)은 이 셈에서 뺀다
    OUTSIDE = re.compile(r"폐사|객잔|주막|총단|무림맹|하촌|저잣거리|마교|관아")
    # 3부: 문턱 밖에 나가 있어서 마당 셈에서 빠지는 사람 (회차 구간, 빠지는 수)
    # 150화에 천 노인이 나가 못 돌아온다. 159화에 13호가 떡 하나로 막힌다.
    AWAY = [(150, 999, 1), (159, 165, 2)]
    for n, _, t in eps:
        want = next((v for a, b, v in ROSTER if a <= n <= b), None)
        if want is None:
            continue
        away = max([v for a, b, v in AWAY if a <= n <= b] or [0])
        ok = {want, want - away, want - away - 1}   # 세는 사람 자신을 뺀 경우도 허용
        lines = t.split("\n")
        for i, line in enumerate(lines):
            for w in set(HEAD.findall(line)):
                if WORD[w] in ok:
                    continue
                near = "\n".join(lines[max(0, i - 8):i + 3])
                if OUTSIDE.search(near):
                    continue          # 은자림 밖 이야기다
                add("연속성", "%d화 %d행이 마당을 「%s」(%d)로 적는다 — 입주 일정으로는 %d명이다"
                    % (n, i + 1, w, WORD[w], want))

    # ── 출력 ──────────────────────────────────────────────────────────
    quiet = "--quiet" in sys.argv
    order = ["인물", "복선", "구조", "페이싱", "연속성"]
    by = defaultdict(list)
    for c, m in rep:
        by[c].append(m)
    for c in order:
        if not by[c]:
            continue
        if quiet and c in ("페이싱", "연속성"):
            print("[%s] %d건 (--quiet으로 생략)" % (c, len(by[c])))
            continue
        print("\n[%s] %d건" % (c, len(by[c])))
        for m in by[c]:
            print("  ·", m)
    print("\n" + "-" * 60)
    print("원고 %d편 / 지적 %d건" % (total, len(rep)))
    print("이 감사는 '확인하라'는 목록이다. 전부 오류는 아니다.")


if __name__ == "__main__":
    main()
