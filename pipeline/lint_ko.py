# -*- coding: utf-8 -*-
"""한국어 문장 검사 — 형태소 분석기로 조사·어미를 구분해서 본다.

check.py / audit.py 가 못 보는 것을 본다. 맞춤법이 아니라 **문장의 기계적 오류**다.

- 조사 일치: 받침 유무와 조사가 안 맞는 곳 (「구 노인가」 → 「구 노인이」)
- 지문 나열: 같은 종결어로 끝나는 줄이 연달아 놓인 곳 (CLAUDE.md 3항 나쁜 예)
- 문장 반복: 한 회차 안에서 같은 문장이 두 번 이상
- 긴 문장: 한 줄이 지나치게 긴 곳

형태소 분석은 KoNLPy(Okt)를 쓴다. 조사(Josa) 태그가 붙은 것만 검사하므로
「있는」·「않는」 같은 관형형 어미를 조사로 오인하지 않는다.
    python3 -m pip install konlpy jpype1     (JVM 필요)

사용법: python3 pipeline/lint_ko.py [회차번호 ...]
"""
import glob, os, re, sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LONG = 60          # 한 줄 글자 수 상한
RUN = 3            # 같은 종결어가 연달아 나오면 지적할 줄 수

PAIR = {"이": "가", "가": "이", "은": "는", "는": "은",
        "을": "를", "를": "을", "과": "와", "와": "과"}
NEED_JONG = {"이", "은", "을", "과"}       # 받침 있을 때 쓰는 쪽
# 형태소 분석기가 명사로 잘못 끊는 어미들. 조사 검사에서 뺀다.
# 「가」는 조사 말고도 쓰임이 많다. 실제로 걸린 오탐을 그대로 막는다.
#   의문형 어미: 무림맹인가 / 무슨 소린가 / 어쩔 텐가 / 그게 다인가
#   부사: 어디선가 / 어디론가      성씨: 곽가 / 임가 / 박가      명사: 개울가
NOT_JOSA = re.compile(
    r"(?:겐|건|는|던|런|은|을|ㄹ|인|선|론|텐|만)[가과]$"
    r"|^[가-힣]가$"
    r"|(?:울|물|길|닷|냇|바닷)가$"
    r"|[다까요네지]$")
ENDING = re.compile(r"([가-힣]{2,6})\.$")


def jong(ch):
    """받침이 있으면 True, 없으면 False, 한글이 아니면 None."""
    if not ("가" <= ch <= "힣"):
        return None
    return (ord(ch) - 0xAC00) % 28 != 0


def load(path):
    return [l.rstrip() for l in open(path, encoding="utf-8").read().split("\n")]


def check_josa(okt, lines, add):
    for i, s in enumerate(lines, 1):
        s = s.strip()
        if not s or s.startswith("#"):
            continue
        toks = okt.pos(s)
        for k, (form, tag) in enumerate(toks):
            if tag != "Josa" or form not in PAIR or k == 0:
                continue
            pf, pt = toks[k - 1]
            if pt not in ("Noun", "Alpha", "Number"):
                continue
            if NOT_JOSA.search(pf + form):
                continue
            # 「-ㄴ가」 의문형은 문장 끝에 온다. 조사 「가」는 문장 중간에 온다.
            # 「무림맹인가.」는 어미, 「구 노인가 한숨을 쉬었다」는 조사 오류다.
            if form == "가" and jong(pf[-1]) and (ord(pf[-1]) - 0xAC00) % 28 == 4:
                rest = "".join(t[0] for t in toks[k + 1:]).strip()
                if rest in ("", ".", "?", "!", '."', ".'", "…", ".…"):
                    continue
            j = jong(pf[-1])
            if j is None:
                continue
            if (form in NEED_JONG) != j:
                add("조사", "%d행 %r → %r  | %s" % (i, pf + form, pf + PAIR[form], s[:46]))


def check_run(lines, add):
    """지문이 같은 종결어로 연달아 끝나면 리듬이 죽는다."""
    run, prev, start = 1, None, 0
    for i, s in enumerate(lines, 1):
        t = s.strip()
        if not t or t.startswith(('"', "「", "'", "#")):
            run, prev = 1, None
            continue
        m = ENDING.search(t)
        cur = m.group(1) if m else None
        if cur and cur == prev:
            run += 1
            if run == RUN:
                add("리듬", "%d~%d행 「%s」로 끝나는 줄이 %d개 연달아 있다" % (start, i, cur, run))
            elif run > RUN:
                pass
        else:
            run, prev, start = 1, cur, i


def check_dup(lines, add):
    body = [s.strip() for s in lines if len(s.strip()) > 12 and not s.startswith("#")]
    for s, c in Counter(body).items():
        if c > 1:
            add("반복", "같은 문장이 %d번 나온다: %r" % (c, s[:50]))


def check_long(lines, add):
    for i, s in enumerate(lines, 1):
        t = s.strip()
        if len(t) > LONG and not t.startswith("#"):
            add("장문", "%d행 %d자 — 한 문장이 너무 길다 | %s…" % (i, len(t), t[:44]))


def main():
    want = {int(a) for a in sys.argv[1:] if a.isdigit()}
    try:
        from konlpy.tag import Okt
        okt = Okt()
    except Exception as e:
        print("형태소 분석기를 못 불러왔다 (%s). 조사 검사는 건너뛴다." % type(e).__name__)
        print("  python3 -m pip install konlpy jpype1")
        okt = None

    rep = []
    eps = 0
    for p in sorted(glob.glob(os.path.join(ROOT, "episodes", "part*", "ep_*.md"))):
        n = int(re.search(r"ep_(\d+)", p).group(1))
        if want and n not in want:
            continue
        eps += 1
        lines = load(p)
        add = lambda cat, msg, _n=n: rep.append((_n, cat, msg))
        if okt:
            check_josa(okt, lines, add)
        check_run(lines, add)
        check_dup(lines, add)
        check_long(lines, add)

    by = Counter(c for _, c, _ in rep)
    for n, c, m in rep:
        print("%s %3d화  %s" % ({"조사": "✗", "반복": "✗"}.get(c, "·"), n, m))
    print("-" * 60)
    print("검사 %d편 / " % eps + " / ".join("%s %d건" % (k, v) for k, v in by.most_common()))


if __name__ == "__main__":
    main()
