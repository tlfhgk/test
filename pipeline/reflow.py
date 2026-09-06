# -*- coding: utf-8 -*-
"""문단을 괴력난신식 블록으로 묶는다.
- 대사 연속 = 한 블록
- 서술 = 2~3줄 블록. 장면 전환 줄 앞에서는 반드시 끊는다
- 블록 사이만 빈 줄
"""
import re

# 장면/시점/시간이 바뀌는 줄 (앞에서 반드시 끊는다)
SCENE = re.compile(
    r'^(같은 (시각|날|밤|무렵|달|해|월|주|시간)|한편|훗날|정확히 그 시각|그리고 같은'
    r'|그날 (밤|저녁|아침|오후|이후)|이튿날|다음 날|며칠 뒤|얼마 뒤|해가 |밤이 |새벽[에이가 ]|아침[에이가 ])'
    r'|^.{0,20}?(전날 밤|다음 날|이튿날|무렵|시진 뒤|달 뒤|해 뒤|년 뒤|일 뒤|주 뒤),'
    r'|^(하루|이틀|사흘|나흘|닷새|엿새|이레|여드레|아흐레|열흘|보름|한 달|두 달|석 달|넉 달|반년|일 년)'
    r'(째)?( 되던)?\s*(날|저녁|아침|밤|새벽|오후|낮|뒤|만에|째)'
)
# 장소 표제 (짧은 명사구)
HEAD = re.compile(r'^.{2,26}\.$')
PLACE = re.compile(r'(무림맹|총단|원로원|기록실|은자림|폐사|초소|하촌|저잣거리|주막|관아|철권문|산 아래|마당)')
VERB = re.compile(r'(다|요|오|까|네|지|군|세)\.$')
TAG = re.compile(r'(말했다|물었다|대답했다|되물었다|덧붙였다|중얼거렸다|외쳤다|소리쳤다|잘랐다)\.$')

def is_dial(l):
    return l.startswith(('"', '「', "'"))

def is_scene(l):
    if SCENE.search(l):
        return True
    return bool(HEAD.match(l) and PLACE.search(l) and not VERB.search(l))

def chunk(lines):
    out, i, n = [], 0, len(lines)
    while i < n:
        take = 1
        while take < 3 and i + take < n and not is_scene(lines[i + take]):
            take += 1
        if n - (i + take) == 1 and take == 3:   # 1줄 꼬리 방지
            take = 2
        out.append(lines[i:i + take])
        i += take
    return out

def reflow(text):
    lines = text.split('\n')
    title, body = lines[0], [l for l in lines[1:] if l.strip()]
    blocks, i, n = [], 0, len(body)
    while i < n:
        j = i
        while j < n and is_dial(body[j]) == is_dial(body[i]):
            j += 1
        run = body[i:j]
        if is_dial(body[i]):
            blocks.append(run)
        else:
            tail = None
            # 대사 직전의 짧은 지문 한 줄은 따로 세운다
            if j < n and len(run) > 1 and (TAG.search(run[-1]) or len(run[-1]) <= 30):
                tail, run = run[-1], run[:-1]
            # 회차 마지막 강조 문장은 반드시 한 줄로
            last = None
            if j >= n and len(run) > 1 and run[-1].startswith('**'):
                last, run = run[-1], run[:-1]
            # 장면 전환 줄에서 먼저 쪼갠 뒤 각 조각을 2~3줄로
            seg, cur = [], []
            for l in run:
                if cur and is_scene(l):
                    seg.append(cur); cur = []
                cur.append(l)
            if cur: seg.append(cur)
            for s in seg:
                blocks.extend(chunk(s))
            if tail:
                blocks.append([tail])
            if last:
                blocks.append([last])
        i = j
    # 회차 마지막 문장은 항상 한 줄로 세운다 (부 완결 표시가 있으면 그 앞 줄까지)
    if blocks and len(blocks[-1]) > 1:
        blocks.append([blocks[-1].pop()])
    if len(blocks) > 1 and blocks[-1][0].startswith('\u2015') and len(blocks[-2]) > 1:
        blocks.insert(-1, [blocks[-2].pop()])
    return title + '\n\n' + '\n\n'.join('\n'.join(b) for b in blocks) + '\n'


if __name__ == '__main__':
    import sys, glob
    targets = sys.argv[1:] or sorted(glob.glob('episodes/part*/ep_*.md'))
    for path in targets:
        src = open(path).read()
        out = reflow(src)
        if out != src:
            with open(path, 'w') as f:
                f.write(out)
            print('재조판:', path)
