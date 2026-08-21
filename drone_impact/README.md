# 드론 고속 충돌 + 배터리 폭발 — 2층 상가 건물 (LS-DYNA)

**Ansys 2025 R1 (LS-DYNA R14.1) Student** 에서 그대로 돌아가는 explicit 충돌·파괴 해석 덱입니다.
드론이 40 m/s 로 날아가 2층 상가 건물 전면 유리에 처박히고, 충돌 1.5 ms 뒤
LiPo 배터리가 터지면서 기체가 산산조각 나는 시나리오입니다.

```
drone_impact/
├── generate_model.py   메쉬 생성기 (파이썬 3, 외부 라이브러리 불필요)
├── main.k              마스터 덱 (LS-DYNA용) — control / material / section / contact / load
├── make_openradioss.py main.k → main_openradioss.k 변환기
├── main_openradioss.k  [자동생성] OpenRadioss용 덱 (라이선스 불필요)
├── run_openradioss.bat OpenRadioss 실행 스크립트 (Windows)
├── building.k          [자동생성] 건물 절점·요소·바닥 구속 절점세트
├── drone.k             [자동생성] 드론 절점·요소
└── blast.inc           [자동생성] 배터리 폭발 하중 + 세그먼트세트 903/902
                        (`.k` 가 아닌 이유: OpenRadioss 리더가 실행폴더의
                         `.k` 파일을 include 하지 않아도 주워 읽습니다)
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
* 하중은 **세그먼트세트 903** 하나에 걸립니다 = 건물 전면(법선 실내쪽 → 벽이 밖으로
  뜯겨나감) + 드론 동체 내면(법선 폭원쪽 → 패널이 바깥으로 터짐), 총 2,784 세그먼트.
  세트 902(동체 내면 1,440개)는 아래 대체 압력펄스 모델용으로 따로 남겨뒀습니다.

**(4) 침식 접촉 — `*CONTACT_ERODING_SINGLE_SURFACE`**
요소가 삭제된 뒤에도 새로 드러난 면으로 접촉이 계속 이어져야 파편이 서로 부딪히며 흩어집니다.
`*CONTROL_CONTACT` 의 `ENMASS=2` 로 삭제된 절점의 질량을 남겨 **파편 구름**이 보이게 했습니다.

---

## 4. 실행 — Ansys 2025 R1 (LS-DYNA R14.1)

**Ansys 2025 R1 에 들어있는 LS-DYNA 는 R15 가 아니라 R14.1 입니다.**
이 덱에 쓴 카드는 전부 R14 정식 지원 범위 안이라 수정 없이 그대로 돌아갑니다.

> Workbench LS-DYNA(Mechanical) 는 `.k` 덱을 직접 먹지 않습니다.
> 아래 **LS-Run** 또는 커맨드라인으로 푸세요.

### (a) LS-Run — 권장
1. 메쉬 재생성이 필요하면 먼저 `python3 generate_model.py`
2. 시작메뉴에서 **LS-Run** 실행 (Ansys LS-DYNA Student 와 같이 설치됨)
3. `Input file` 에 `main.k` 지정 → **Working directory 가 반드시
   `building.k / drone.k / blast.k` 와 같은 폴더**여야 합니다 (`*INCLUDE` 가 상대경로)
4. Solver = `SMP`, Precision = `Single`, `NCPU = 4` → **Run**
5. 라이선스 환경변수는 LS-Run 이 알아서 잡아줍니다.

### (b) 커맨드라인
```bat
cd /d <이 폴더>
"C:\Program Files\ANSYS Inc\v251\ansys\bin\winx64\lsdyna_sp.exe" ^
    i=main.k ncpu=4 memory=200m
```
* `v251` = 2025 R1. **설치된 버전에 맞춰 폴더명을 바꾸세요** (2026 R1 이면 `v261`).
  `dir "C:\Program Files\ANSYS Inc"` 로 확인하면 됩니다.
* 정밀도: 이 모델은 **단정밀도(`lsdyna_sp.exe`) 로 충분**하고 배정밀도보다 약 2배 빠릅니다.
  `glstat` 에서 에너지 밸런스가 이상하면 `lsdyna_dp.exe` 로 바꿔 보세요.
* 직접 exe 를 부를 때 라이선스를 못 찾으면 `set LSTC_LICENSE=ansys` 를 먼저 주세요.
* `ncpu=4` 가 거부되면 학생 라이선스 코어 수에 맞춰 2 또는 1 로 낮추세요.

### 규모
* **절점 11,526 / 요소 12,300** → Ansys Student LS-DYNA 제한(약 128,000 절점·요소) 대비 10% 수준.
  메쉬를 훨씬 촘촘하게 키울 여유가 있습니다.
* 임계 시간증분 ≈ 1.2E-3 ms, 약 29,000 스텝. 노트북 4코어 기준 수 분.
* `*DATABASE_BINARY_D3PLOT` dt = 0.25 ms → **애니메이션 140 프레임**.

### 결과 보기 (LS-PrePost)
1. `d3plot` 열기 → Animate 재생.
2. Fringe → **Effective Plastic Strain** 또는 **von Mises Stress**.
3. 파편이 잘 보이게: `Appearance → Shading`, 그리고 Part 106/107(유리) 만 켜서 파단 확인.
4. `glstat` 로 에너지 보존 확인 — **Added mass 가 전체 질량의 5% 를 넘으면**
   `*CONTROL_TIMESTEP` 의 `DT2MS` 를 더 작게(예 −2.0E-4) 주세요.

---

## 4-B. 라이선스 없이 돌리기 — OpenRadioss

[OpenRadioss](https://github.com/OpenRadioss/OpenRadioss)는 Altair가 오픈소스로 공개한
상용급 explicit 충돌 솔버입니다. **무료, 라이선스 서버 불필요, 요소 수 제한 없음**,
그리고 **LS-DYNA `.k` 파일을 네이티브로 읽습니다.**

### 설치 (Windows, 10분)

1. **OpenRadioss 받기** — https://github.com/OpenRadioss/OpenRadioss/releases
   에서 최신 릴리스의 Windows 바이너리 zip 다운로드. 빌드할 필요 없습니다.
2. **압축 풀기** — 예: `C:\OpenRadioss`
   (안에 `exec`, `hm_cfg_files`, `extlib` 폴더가 보이면 정상)
3. **ParaView 받기** — https://www.paraview.org/download/ (무료, 결과 보기용)
   * 페이지 상단 드롭다운을 `Version = 최신`, `Type = ParaView Binary Installers`,
     `OS = Windows` 로 두고, 파일명이 아래 형태인 **`.msi`** 를 받으세요:
     `ParaView-<버전>-MPI-Windows-Python<버전>-msvc<연도>-AMD64.msi`
   * 파일명에 **`osmesa`** 가 붙은 것은 화면 없는 서버용(소프트웨어 렌더링)이라
     받지 마세요. 느립니다.
   * `MPI` 가 붙어 있어도 그냥 단독 실행됩니다 — 신경 쓰실 필요 없습니다.
   * `.zip` 은 설치 없이 압축만 푸는 버전입니다. 어느 쪽이든 무관합니다.
4. `run_openradioss.bat` 을 열어 맨 위 두 줄만 수정:
   ```bat
   set OPENRADIOSS_PATH=C:\OpenRadioss    :: 2번에서 푼 위치
   set OMP_NUM_THREADS=4                   :: 쓸 CPU 코어 수
   ```
5. **`run_openradioss.bat` 더블클릭.** 끝입니다.

> **경로에 한글이 있으면 주의.** OpenRadioss 의 Starter/Engine 은 포트란 파일 I/O 를
> 쓰기 때문에 한글·공백이 섞인 경로에서 파일을 못 여는 경우가 있습니다. 원인 모를
> file-not-found 가 뜨면 폴더째 `C:\sim\drone` 같은 **영문 경로로 복사**해서 다시
> 돌려보세요. OpenRadioss 설치 경로(`C:\OpenRadioss`)도 마찬가지입니다.

> **`.k` 파일 4개가 `.bat` 과 같은 폴더에 평평하게** 있어야 합니다
> (`main_openradioss.k`, `building.k`, `drone.k`, 그리고 LS-DYNA 용 `main.k`/`blast.k`).
> 압축을 풀 때 `drone_impact` 하위폴더가 생겼다면 안쪽 파일들을 꺼내거나, `.bat` 을
> 그 폴더 안으로 옮기세요.

Intel oneAPI 런타임은 릴리스 zip에 `extlib\intelOneAPI_runtime` 로 같이 들어있어서
따로 설치할 필요 없습니다. MPI도 필요 없습니다 — 이 스크립트는 SMP(스레드 병렬)로 돌립니다.

### 스크립트가 하는 일

```bat
starter_win64.exe -i main_openradioss.k -np 1   :: .k 를 읽어 리스타트 파일 생성
engine_win64.exe  -i main_openradioss_0001.rad  :: 실제 해석
anim_to_vtk_win64.exe <animfile> > <animfile>.vtk   :: ParaView 용으로 변환
```
환경변수(`RAD_CFG_PATH`, `RAD_H3D_PATH`, `KMP_STACKSIZE`, `PATH`)는 스크립트가
OpenRadioss `INSTALL.md` 대로 알아서 설정합니다. 실행 폴더도 스크립트 자기 위치로
맞추기 때문에 `*INCLUDE` 경로 문제가 생기지 않습니다.

### 결과 보기 (ParaView)

1. ParaView → `File > Open` → `main_openradiossA0..vtk` (`..` 로 묶인 시리즈 선택) → Apply
2. 좌상단 드롭다운에서 표시할 값 선택 (변위/응력/소성변형률)
3. 재생 버튼으로 애니메이션, `File > Save Animation` 으로 PNG 시퀀스 또는 avi 저장

### LS-DYNA 덱과 무엇이 다른가

OpenRadioss 는 LS-DYNA 키워드 **전부**가 아니라 리더(`dyna2rad`)가 매핑하는 것만
읽습니다. `make_openradioss.py` 가 아래 네 군데를 바꿔서 `main_openradioss.k` 를
만듭니다. 리더 소스를 직접 확인한 결과입니다.

| 항목 | 처리 | 근거 |
|---|---|---|
| `*CONTACT_ERODING_SINGLE_SURFACE` | **그대로 사용** → `/INTER/TYPE7` | `convertcontacts.cxx` 가 부분문자열로 인식 |
| `*LOAD_BODY_Z` | **그대로 사용** → `/GRAV` | `convertloads.cxx` |
| `*LOAD_BLAST_ENHANCED` | **삭제** → `*LOAD_SHELL_SET` 압력펄스로 대체 | 개발자가 "blast/ALE 키워드는 미지원"이라고 명시 |
| `*MAT_CRUSHABLE_FOAM` (배터리) | `*MAT_024` 로 교체 | 이름 맵에는 있으나 실제 변환 여부 미확인 |
| `*MAT_ELASTIC` + `*MAT_ADD_EROSION` (유리) | 취성 `*MAT_024` 로 교체 | `convertprops.cxx` 가 파단두께만 읽어서 `SIGP1` 기준이 조용히 사라짐 |

폭발은 `*LOAD_SHELL_SET`(→`/PLOAD`)로 드론 동체 셸세트 210에 압력펄스를 겁니다.
동체 면적 144,000 mm², 질량 0.335 kg 기준으로 8.0E-4 GPa × 0.5 ms 삼각펄스 →
패널이 약 85 m/s 로 튕겨나갑니다.

### 실행 폴더 격리 (스크립트가 알아서 합니다)

OpenRadioss 의 LS-DYNA 리더는 **실행 폴더에 있는 `.k` 파일을 include 하지 않아도
읽습니다.** `main.k` 가 같은 폴더에 있으면 그것도 읽히고, `main.k` 는 `blast.inc` 를
include 하므로 결국 아래 에러가 납니다.

```
ERROR ID : 100210  ** ERROR IN INPUT OPTIONS
-- BLOCK: *LOAD_BLAST_ENHANCED
Unrecognized option: *LOAD_BLAST_ENHANCED
```

그래서 `run_openradioss.bat` 은 실행할 때마다 `_run_openradioss\` 하위폴더를 만들어
**`main_openradioss.k` / `building.k` / `drone.k` 세 개만 복사한 뒤 거기서 돌립니다.**
원본 폴더에 `main.k`, `blast.inc`, 뭐가 있든 상관없습니다.
결과 파일(`.out`, `A0xx`, `.vtk`)도 전부 이 하위폴더에 쌓입니다.

### 배터리 폭발은 기본적으로 꺼져 있습니다

OpenRadioss 덱은 `BURST = "off"` 로 생성됩니다. 충돌·파괴만 계산합니다.
드론이 40 m/s, 1.73 kJ 로 들어오는 것이 기체를 찢는 주된 원인이라 폭발 없이도
파괴 장면은 그대로 나옵니다.

첫 시도였던 `*LOAD_SHELL_SET` 은 Starter 가 거부했습니다:
```
ERROR ID : 3066  ** ERROR IN PRESSURE LOAD DEFINITION (SURFACE)
   -- PRESSURE LOAD ID: 210 ...  NO SURFACE REFERENCED IN THE OPTION
```
셸요소 세트를 면(surface)으로 바꾸지 못한 것입니다. 세그먼트 세트는 그 자체가
면이라 가능성이 더 높지만 **아직 실제로 확인하지 못했습니다.**

켜보시려면 `make_openradioss.py` 맨 위를 고치고 다시 돌리세요:
```python
BURST = "segment"      # "off" | "segment"
```
```bash
python3 make_openradioss.py
```

### 처음 돌릴 때 반드시 볼 것

`main_openradioss_0000.out` — **Starter 가 읽지 못한 키워드를 여기에 전부 적어줍니다.**
아직 검증 못한 것이 남아 있습니다: `*SECTION_BEAM`(RC 기둥·보), `*MAT_RIGID` 의
`CMO` 구속, `*CONTROL_*` 각종 카드, `*DATABASE_BINARY_D3PLOT` → 애니메이션 출력 매핑.
이 파일 내용을 알려주시면 남은 것도 맞춰 드립니다.

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
| `PART 11 not found: *INITIAL_VELOCITY_GENERATION` | `STYP` 값 문제. **`STYP=1` 이 파트세트, `STYP=2` 가 단일 파트 ID** 입니다(`*CONTACT` 의 `SSTYP` 와 규칙이 반대라 헷갈립니다). `11,1,0.0,0.0,40.0,...` 이어야 합니다. |
| `Missing data in Keyword - *LOAD_BLAST_SEGMENT_SET` | `blast.inc` 를 재생성하세요. 카드를 하나로 합치고(세트 903), `aleid`·`sfnrb` 까지 전 필드를 명시했으며, `*SET_SEGMENT` 를 하중카드 **뒤**로 옮겨 하중카드가 파일 끝에 오지 않게 했습니다. |
| `Request name dyna does not exist in the licensing pool` + `Error 70022` | **학생 라이선스 만료**입니다. 모델 문제가 아닙니다. 라이선스가 설치파일에 내장돼 있어서 **최신 Ansys Student 를 새로 받아 재설치**하는 것이 유일한 방법입니다(2020Rx 부터 라이선스 파일 교체 방식은 폐지). |
| `E R R O R ... *INCLUDE ... file not found` | LS-Run 의 **Working directory** 가 `.k` 파일들이 있는 폴더가 아닙니다. |
| 폭압이 너무 세거나 약함 | `blast.inc` 의 `M`(현재 0.030 kg) 조정. `*DATABASE_BINARY_D3PLOT` 에서 blast pressure fringe 로 실제 걸린 압력을 먼저 확인하세요. |
| 폭발이 아예 안 걸림 | `messag` 에서 `LOAD_BLAST` 경고 확인. 세그먼트 법선이 폭원 반대쪽이면 하중이 0 입니다. 정 안 되면 `main.k` 맨 아래 **ALTERNATIVE BURST MODEL** 블록(`*LOAD_SEGMENT_SET` + 압력 곡선)의 `$` 를 지우고, 상단 `*INCLUDE blast.k` 두 줄을 `$` 로 막으세요. |
| 초기에 에너지가 튐 | `*CONTROL_CONTACT` 의 `SLSFAC` 를 0.05 로 낮추거나 접촉 `SOFT=2` 로 변경. |
| 요소가 과도하게 뭉개져 계산이 느려짐 | `*CONTROL_TIMESTEP` 의 `ERODE=1` 이 켜져 있는지 확인. |

---

## 6-B. 결과물을 공개/수익화할 때

| 도구 | 라이선스 | 영상 공개·수익화 |
|---|---|---|
| **OpenRadioss** | AGPL-3.0 | **가능.** AGPL은 소프트웨어의 배포·개조에 조건을 걸 뿐, 실행해서 나온 해석 결과에는 제한이 없습니다. 상업적 사용도 허용. |
| **ParaView** | BSD | 가능. 제약 없음. |
| **Ansys Student** | 교육용 한정 | **주의.** 상업 활동 금지이고 결과물 공개(publishing work)도 제한됩니다. 수익화 채널이면 OpenRadioss 쪽으로 만드세요. |
| 이 폴더의 `.k` / `.py` | 사용자 소유 | 제약 없음. |

OpenRadioss를 **고쳐서 웹서비스로 제공**하면 그때는 AGPL의 소스 공개 조항이 걸립니다.
영상 제작은 해당 없습니다. 크레딧 표기는 의무가 아니지만 관례상 넣어주면 좋습니다.

---

## 7. 주의

물성치와 폭발 규모는 **공개 문헌 수준의 대표값**이며 실측 캘리브레이션 값이 아닙니다.
정량적 결론(관통 여부, 잔여속도, 손상 범위)을 내려면 재료시험 데이터로
`SIGY / FAIL / SIGP1` 을 보정하고 메쉬 수렴성 검토를 먼저 하세요.
지금 상태는 **파괴 거동을 보여주는 데모/스터디용**으로 튜닝돼 있습니다.
