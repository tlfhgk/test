# -*- coding: utf-8 -*-
"""깃허브에서도 드라이브와 같은 줄바꿈으로 보이게 한다.

마크다운은 홑줄바꿈을 무시하고 한 문단으로 이어 붙인다.
그래서 「한 문장 = 한 줄」로 써도 깃허브에서는 벽돌 문단으로 보인다.
줄 끝에 공백 두 칸(마크다운 강제 개행)을 붙여 그것을 막는다.

- 제목 줄(#)과 빈 줄에는 붙이지 않는다.
- 블록 마지막 줄에도 붙이지 않는다. 빈 줄이 이미 문단을 끊기 때문이다.
- 공백 두 칸은 마크업이므로 글자 수에 세지 않는다 (count.py가 rstrip 한다).

사용법: python3 pipeline/mdbreak.py [파일...]   (인자 없으면 전 회차)
"""
import sys, glob

BR = "  "


def apply(text):
    lines = [l.rstrip() for l in text.split("\n")]
    out = []
    for i, l in enumerate(lines):
        nxt = lines[i + 1] if i + 1 < len(lines) else ""
        # 빈 줄, 제목 줄, 블록의 마지막 줄은 그대로 둔다
        if not l or l.startswith("#") or not nxt:
            out.append(l)
        else:
            out.append(l + BR)
    return "\n".join(out)


def strip(text):
    return "\n".join(l.rstrip() for l in text.split("\n"))


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    undo = "--strip" in sys.argv
    targets = args or sorted(glob.glob("episodes/part*/ep_*.md"))
    n = 0
    for path in targets:
        src = open(path, encoding="utf-8").read()
        out = strip(src) if undo else apply(src)
        if out != src:
            open(path, "w", encoding="utf-8").write(out)
            n += 1
    print("%s: %d개 파일" % ("해제" if undo else "강제 개행 적용", n))
