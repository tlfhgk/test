# 드론 고속 충돌 + 배터리 폭발 — 2층 상가 건물 (LS-DYNA)

Ansys Student / LS-DYNA Student 에서 그대로 돌아가는 explicit 충돌·파괴 해석 덱입니다.
드론이 40 m/s 로 날아가 2층 상가 건물 전면 유리에 처박히고, 충돌 1.5 ms 뒤
LiPo 배터리가 터지면서 기체가 산산조각 나는 시나리오입니다.

```
drone_impact/
├── generate_model.py   메쉬 생성기 (파이썬 3, 외부 라이브러리 불필요)
├── main.k              마스터 덱 — control / material / section / contact / load
├── building.k          [자동생성] 건물 절점·요소·경계절점세트·세그먼트세트
├── drone.k             [자동생성] 드론 절점·요소·세그먼트세트
└── blast.k             [자동생성] *LOAD_BLAST_ENHANCED (배터리 폭발)
```

---

## 1. 단위계 — kg / mm / ms / kN / GPa

**LS-DYNA 는 단위를 모릅니다. 아래 조합을 반드시 지켜야 합니다.**

| 물리량 | 단위 | 예 |
|---|---|---|
| 길이 | mm | 건물 폭 12000 |
| 시간 | ms | 해석 종료 35.0 |
| 질량 | kg | 드론 2.167 |
| 힘 | kN | |
| **응력·탄성계수** | **GPa** | 강재 E = 210, 콘크리트 30 |
| **밀도** | **kg/mm³** | 강재 7.85E-6, 콘크리트 2.4E-6 |
| 속도 | mm/ms = **m/s** | 40.0 = 40 m/s |
| 중력 | mm/ms² | 9.81E-3 |
| 에너지 | kJ | |

> MPa 로 물성을 찾았다면 **÷1000** 해서 GPa 로 넣으세요. (30 MPa → 0.030)

---

## 2. 모델 형상

### 2층 상가 건물 (12 m × 8 m × 7 m)

| PID | 부재 | 요소 | 물성 |
|---|---|---|---|
| 101 | RC 기둥 400×400, 4×3 = 12본 | beam | 철근 스미어 콘크리트 |
| 102 | RC 큰보 300×500 (2F·지붕) | beam | 〃 |
| 103 | 2층 슬래브 t=180 | shell | 콘크리트 |
| 104 | 지붕 슬래브 t=180 | shell | 콘크리트 |
| 105 | 전면 콘크리트 띠 (하부 벽·스팬드럴·파라펫) t=150 | shell | 콘크리트 |
| 106 | **1층 상가 전면유리 t=10** (Z 500–3250) | shell | 취성 유리 |
| 107 | **2층 전면유리 t=10** (Z 3750–6750) ← **충돌 지점** | shell | 취성 유리 |
| 108 | 알루미늄 커튼월 멀리언 60×100, 1 m 간격 | beam | 알루미늄 |
| 109 | 측벽·후면벽 조적 t=200 | shell | 조적 |
| 110 | 지반 (강체, 완전구속) | shell | *MAT_RIGID |

* 층고 3.5 m, 전면 = Y 0 평면. 기둥/보/슬래브/벽 절점은 **좌표 기준 자동 병합**되어 완전히 연결돼 있습니다.
* 바닥 절점(Z=0) 162개는 `*BOUNDARY_SPC_SET` 으로 6자유도 고정.

### 쿼드콥터 드론 (총 2.167 kg, 모터 간 700 mm)

| PID | 부재 | 요소 | 물성 | 질량 |
|---|---|---|---|---|
| 201 | 동체 프레임 200×200×80, t=1.5 | shell | CFRP (취성) | 0.335 kg |
| 202 | 암 20×20 각파이프 ×4, t=2.0 | shell | CFRP (취성) | 0.253 kg |
| 203 | BLDC 모터 40×40×30 ×4 | solid | 알루미늄+동선 | 0.480 kg |
| 204 | 프로펠러 260 mm ×4, t=3.0 | shell | 폴리카보네이트 | 0.072 kg |
| 205 | **LiPo 배터리 160×60×40** | solid | *MAT_CRUSHABLE_FOAM | 0.768 kg |
| 206 | 짐벌/카메라 포드 | solid | ABS | 0.259 kg |

* 초기 위치 (6000, −570, 5000), 벽까지 이격 220 mm.
* 초기속도 **Vy = +40 m/s** → **5.5 ms 에 2층 유리 충돌**, 운동에너지 **1.73 kJ**.

---

## 3. "박살나는 걸" 만들어내는 키워드

파괴 연출은 아래 네 가지가 전부입니다. 여기만 만지면 됩니다.

**(1) 소성변형률 파단 — `*MAT_PIECEWISE_LINEAR_PLASTICITY` 의 FAIL**
```
$# mid,ro,e,pr,sigy,etan,fail,tdel
202,1.55E-6,60.0,0.30,0.500,0.0,0.004,0.0     <- CFRP 암: 0.4% 에서 요소 삭제
```
FAIL 을 작게 → 더 잘 부서짐 / 크게 → 질기게 찌그러짐.

**(2) 유리 취성 파괴 — `*MAT_ELASTIC` + `*MAT_ADD_EROSION`**
```
$# mnpres,sigp1,sigvm,mxeps,...
0.0,0.060,0.0,0.0020,0.0,0.0,0.0,0.0          <- 최대주응력 60 MPa 또는 변형률 0.2%
```
`NUMFIP=1` 이라 두께방향 적분점 하나만 깨져도 요소가 사라져 유리가 시원하게 터집니다.

**(3) 배터리 폭발 — `blast.k` 의 `*LOAD_BLAST_ENHANCED`**
```
$#     bid         m       xbo       ybo       zbo       tbo      unit     blast
         1     0.030       0.0       0.0       0.0       7.0         5         2
$#     cfm       cfl       cft       cfp     nidbo     death   negphs
       1.0     0.001     0.001    1.0E+9    503088   1.0E+20         0
```
* `M = 0.030` kg TNT 상당 — 6S/10Ah LiPo 열폭주 시 급속 방출분에 해당하는 크기.
* `TBO = 7.0` ms — 충돌(5.5 ms) 1.5 ms 후 점화.
* `NIDBO = 503088` — 폭원이 **배터리 중앙 절점을 따라다닙니다**(고정 좌표 아님).
* `UNIT=5` + `CFM/CFL/CFT/CFP` = 1 / 0.001 / 0.001 / 1.0E+9 → kg-mm-ms-GPa 를 SI 로 환산.
* 하중은 두 세그먼트 세트에 걸립니다: **902 = 동체 내면**(법선 안쪽 → 패널이 바깥으로 터짐),
  **901 = 건물 전면**(법선 실내쪽 → 벽이 밖으로 뜯겨나감).

**(4) 침식 접촉 — `*CONTACT_ERODING_SINGLE_SURFACE`**
요소가 삭제된 뒤에도 새로 드러난 면으로 접촉이 계속 이어져야 파편이 서로 부딪히며 흩어집니다.
`*CONTROL_CONTACT` 의 `ENMASS=2` 로 삭제된 절점의 질량을 남겨 **파편 구름**이 보이게 했습니다.

---

## 4. 실행

```bash
python3 generate_model.py          # 메쉬 재생성 (형상·요소크기 바꿨을 때만)
lsdyna i=main.k ncpu=4 memory=200m # 또는 Ansys LS-DYNA Student GUI 에서 main.k 열기
```

* 규모: **절점 11,526 / 요소 12,300** → Student 버전 제한(10만) 안쪽.
* 임계 시간증분 ≈ 1.2E-3 ms, 약 29,000 스텝. 노트북 4코어 기준 수 분.
* `*DATABASE_BINARY_D3PLOT` dt = 0.25 ms → **애니메이션 140 프레임**.

### 결과 보기 (LS-PrePost)
1. `d3plot` 열기 → Animate 재생.
2. Fringe → **Effective Plastic Strain** 또는 **von Mises Stress**.
3. 파편이 잘 보이게: `Appearance → Shading`, 그리고 Part 106/107(유리) 만 켜서 파단 확인.
4. `glstat` 로 에너지 보존 확인 — **Added mass 가 전체 질량의 5% 를 넘으면**
   `*CONTROL_TIMESTEP` 의 `DT2MS` 를 더 작게(예 −2.0E-4) 주세요.

---

## 5. 자주 바꾸는 값

| 목적 | 파일 | 위치 |
|---|---|---|
| 충돌 속도 | `main.k` | `*INITIAL_VELOCITY_GENERATION` 의 `40.0` (m/s) |
| 충돌 지점·기체 위치 | `generate_model.py` | `DX, DY, DZ` |
| 폭약량·점화시각 | `generate_model.py` | `write_blast()` 의 `0.030`, `7.0` |
| 해석 종료 시간 | `main.k` | `*CONTROL_TERMINATION` 의 `35.0` |
| 애니메이션 프레임 | `main.k` | `*DATABASE_BINARY_D3PLOT` 의 `0.25` |
| 메쉬 크기 | `generate_model.py` | `H_BLD`(건물 250) / `H_DRN`(드론 10) |

> `H_DRN` 을 5 로 줄이면 파편이 훨씬 곱게 나오지만 요소 수가 4배, 시간증분이 절반이라
> 계산시간은 약 8배가 됩니다.

---

## 6. 문제가 생기면

| 증상 | 조치 |
|---|---|
| `*CONTROL_SHELL` 4번째 카드에서 입력 오류 | 구버전 솔버입니다. `1,1,0,0,0` 줄과 그 위 `$# nfail1...` 주석을 지우세요. |
| `*LOAD_BLAST_ENHANCED` 가 라이선스에 없음 | `main.k` 상단의 `*INCLUDE blast.k` 두 줄을 주석 처리하고, 맨 아래 **ALTERNATIVE BURST MODEL** 블록(`*LOAD_SEGMENT_SET` + 압력 곡선)의 `$` 를 제거하세요. |
| 폭압이 너무 세거나 약함 | `blast.k` 의 `M` 조정. 환산계수 정의(모델단위→SI)는 솔버 버전별로 확인하고, `d3plot` 의 blast pressure 로 검증하세요. |
| 초기에 에너지가 튐 | `*CONTROL_CONTACT` 의 `SLSFAC` 를 0.05 로 낮추거나 접촉 `SOFT=2` 로 변경. |
| 요소가 과도하게 뭉개져 계산이 느려짐 | `*CONTROL_TIMESTEP` 의 `ERODE=1` 이 켜져 있는지 확인. |

---

## 7. 주의

물성치와 폭발 규모는 **공개 문헌 수준의 대표값**이며 실측 캘리브레이션 값이 아닙니다.
정량적 결론(관통 여부, 잔여속도, 손상 범위)을 내려면 재료시험 데이터로
`SIGY / FAIL / SIGP1` 을 보정하고 메쉬 수렴성 검토를 먼저 하세요.
지금 상태는 **파괴 거동을 보여주는 데모/스터디용**으로 튜닝돼 있습니다.
