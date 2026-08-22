# 항공기 충돌 규제 비교 DB (RAG용)

원자력시설에 대한 **항공기 충돌(aircraft impact / aircraft crash)** 규제 요건을
체코 · EU · IAEA · 미국 4개 축으로 수집하여 정규화하고, **NEI 07-13(미국 산업계
방법론)을 기준선으로** 상호 대조한 뒤, 검색·인용이 가능한 SQLite 데이터베이스로
빌드하는 저장소입니다.

## 대상 문서

| 관할 | 문서 | 성격 | 구속력 |
|---|---|---|---|
| 미국 | 10 CFR 50.150 Aircraft impact assessment | 연방규정 | O |
| 미국 | Regulatory Guide 1.217 (Rev.0, 2011.8) | 규제지침 | X |
| 미국 | **NEI 07-13 Rev.8P (2011.4)** — 비교 기준선 | 산업계 방법론 | X |
| 체코 | zákon č. 263/2016 Sb. (원자력법) | 법률 | O |
| 체코 | vyhláška č. 329/2017 Sb. (설계 요건) | 시행령 | O |
| 체코 | vyhláška č. 378/2016 Sb. (부지) | 시행령 | O (확인필요) |
| EU | European Utility Requirements Vol.2 Rev.E | 사업자 요건 | 계약상 |
| EU | Council Directive 2014/87/Euratom | 지침 | O |
| EU | WENRA SRL 2020 / Issue TU External Hazards | 조화기준 | X |
| IAEA | SSR-2/1 Rev.1 Requirement 17 | 안전요건 | X |
| IAEA | **SSG-68** (외부사건 대비 설계, 2021) | 안전지침 | X |
| IAEA | SSG-79 (부지평가 인위적 외부사건) | 안전지침 | X |
| IAEA | SRS No. 86 / **No. 87** / No. 88 | 안전보고서 | X |

> 요청하신 "IAEA 68, 87"은 조회 결과 **SSG-68**(Design of Nuclear Installations
> Against External Events Excluding Earthquakes)과 **Safety Reports Series
> No. 87**(Human Induced External Events: Assessment of Structures)로 확인되어
> 그렇게 수록했습니다. SSG-87은 연구·교육용 방사선원 안전에 관한 문서로 항공기
> 충돌과 무관합니다.

## 빠른 시작

```bash
./run setup            # 설치 + 빌드 + 앱 생성 (처음 한 번)
./run find 관통         # 검색
./run app              # 브라우저 앱 열기
```

### 설치 없이 쓰려면

`web/aircraft-impact.html` 파일 하나를 더블클릭하면 됩니다. 서버도 인터넷도
필요 없는 단독 파일이고, 검색·비교표·문서목록이 다 들어 있습니다.
저작권 있는 축자 원문은 빠져 있어 그대로 공유해도 안전합니다.

전체 명령과 실제 업무 시나리오는 **[`docs/usage.md`](docs/usage.md)** 를 보세요.

## 구조

```
config/sources.yaml            문서 레지스트리(서지정보·URL·저작권 조건)
corpus/clauses/*.yaml          조항 단위 정규화 레코드 (30건)
corpus/crosswalk/topics.yaml   비교 축 15개 (T01~T15)
corpus/crosswalk/crosswalk.yaml NEI 07-13 대비 대조표 12건
corpus/raw/                    원문 보관소 (.gitignore — 저작권 문서 비커밋)
scripts/build_db.py            SQLite + FTS5 빌드
scripts/ingest_raw.py          PDF/TXT → 축자 청크 색인
scripts/retrieval.py           BM25 + 메타데이터 필터 + 크로스워크 확장
scripts/query.py               검색 CLI
scripts/answer.py              Claude 기반 인용형 RAG 응답
scripts/export_rag.py          JSONL 내보내기 (벡터스토어 연동용)
scripts/make_matrix.py         비교 매트릭스 문서 생성
scripts/export_web.py          단독 브라우저 앱 생성
scripts/report_gaps.py         출처 검증 상태 보고
docs/comparison-matrix.md      비교 매트릭스 (자동생성)
docs/methodology.md            방법론·출처검증 정책·한계
docs/acquisition-checklist.md  확보해야 할 원문 목록 (우선순위별)
docs/usage.md                  활용법 — 브라우저 앱 · CLI · 인용답변
web/aircraft-impact.html       단독 브라우저 앱 (설치 불필요)
run                            한 줄 실행 스크립트
```

## 데이터베이스 스키마

`sources` → `clauses` → `chunks` 계층이며, `crosswalk` / `crosswalk_positions`가
문서 간 대응관계를 담습니다. 검색은 `chunks_fts`(FTS5, BM25)로 수행하고,
`chunks.embedding` 컬럼을 비워 두어 임베딩을 추가로 채울 수 있게 했습니다.

청크 종류(`chunks.kind`):

- `clause` — 조항 레코드 (영문·국문 요약 + 핵심 파라미터 + 출처)
- `crosswalk` — 비교 항목 (질문 + 각 문서 입장 + 차이점)
- `source` — 문서 서지 레코드
- `raw` — `ingest_raw.py`로 색인한 원문 축자 청크

각 청크는 한 덩어리만 떼어 프롬프트에 붙여도 출처가 드러나도록 자체 인용
헤더와 `PROVENANCE:` 줄을 포함합니다.

## 출처 신뢰도 표시 — 반드시 확인하세요

이 저장소는 **요약본과 원문을 구분해서 다룹니다.** 모든 레코드에
`verification` 값이 붙습니다.

| 값 | 의미 | 인용 가능 여부 |
|---|---|---|
| `primary_source` | `ingest_raw.py`로 색인한 원문 축자 텍스트 | 그대로 인용 가능 |
| `web_verified` | 이번 구축 과정에서 출처 조회로 확인한 요약 | 신뢰 가능, 인용 시 원문 확인 권장 |
| `model_knowledge` | 확인하지 못한 요약 | **인용 전 반드시 원문 대조** |
| `to_verify` | 조문번호 또는 내용이 불확실 | **그대로 인용 금지** |

`scripts/query.py` 출력의 `✓ ~ !` 기호가 이 값을 나타내며,
`scripts/answer.py`는 시스템 프롬프트로 모델에게 이 등급을 답변에 반영하도록
강제합니다.

현재 상태 (`python3 scripts/report_gaps.py`):

| 등급 | 조항 레코드 |
|---|---|
| `primary_source` | **50** |
| `web_verified` | 1 |
| `model_knowledge` | **0** |
| `to_verify` | **0** |

유일한 `web_verified` 1건은 NRC의 AIA 검사 프로그램으로, 코퍼스에 포함된 문서가 아니라
NRC 웹페이지가 출처입니다.

여기에 더해 **축자 청크 2,184개**가 색인되어 있습니다 — **15개 소스 전부**:
10 CFR 50.150, RG 1.217, NEI 07-13, 체코 원자력법 263/2016 · 설계 시행령 329/2017 ·
부지 시행령 378/2016, Euratom 지침 2014/87, WENRA SRL 2020,
IAEA SSG-68 · SSG-79 · SSR-2/1 · SRS-86 · SRS-87 · SRS-88.
**EUR만 공개 목차 수준**입니다 — 조·항 번호와 제목은 확보했고 요건 본문·하중값은
라이선스 대상이라 없습니다.

이 DB를 구축한 실행환경은 아웃바운드 HTTPS가 조직 egress 정책으로 전면 차단되어
(ecfr.gov, nrc.gov, sujb.gov.cz, www-pub.iaea.org 모두 CONNECT 403) 웹에서 원문을
내려받을 수 없었습니다. 위 3개 문서는 **사용자 Google Drive에 보관된 사본**을 통해
확보했습니다. 남은 것은 **EUR 요건 본문**뿐이며 이는 라이선스 구매 없이는 확보할 수 없습니다.
다만 목차만으로도 EUR의 구조는 확정되었습니다 — 아래 3번 참조.
자세한 내용은 `docs/acquisition-checklist.md`를 보세요.

## 핵심 결론 3가지

`docs/comparison-matrix.md`의 상세 근거를 요약하면:

0. **10 CFR 50.150에는 일몰 조항이 있습니다.** 2026년 4월 개정으로 추가된 (d)항에
   따라 본 조는 **2027년 4월 8일에 실효**하며, NRC가 공중의견을 수렴해 최대 5년까지
   연장하기로 결정하지 않는 한 소멸합니다. 미국 측 비교 대상 자체에 만료일이 있습니다.

1. **CW-04 / CW-09 — 규제 계층이 다릅니다.** 미국은 대형 상용항공기 충돌을
   설계기준*초과*(BDB)로 두고 현실적 해석을 요구합니다. IAEA SSG-68은 두 계층을
   모두 갖습니다: **5.185**는 *우발적* 충돌에 대해 격납구조물의 **무관통**을
   요구하고(설계기준), **5.192**는 완전급유 상용항공기의 *설계기준초과* 충돌에
   대해 "대량·조기 방출 방지에 필요한 안전상 중요 품목의 기능 유지"를 최소
   허용기준으로 두며 최적추정 해석을 허용합니다. 체코는 우발적 추락을 설계기준
   안에 둡니다. 같은 사건이 서로 다른 계층에 놓이므로 요건 1:1 매핑은 성립하지
   않습니다.
2. **CW-08 — 국부손상 경험식은 "같은 식, 다른 지위"입니다(원문 대조 완료).**
   NEI 07-13 §2.1.2는 사용할 식을 **특정**합니다: Modified NDRC(침투),
   reduced Chang(박리 두께), reduced Degen(관통 두께), CEA-EDF(관통속도).
   IAEA SRS-87은 같은 계열(Chang, modified Chang, CRIEPI, NDRC, Degen)을
   **카탈로그로 나열**만 하고 선택을 강제하지 않으며, 고체 발사체 기반이므로
   항공기 엔진·착륙장치에는 **0.60~0.65 감소계수**를 권합니다. SSG-68 5.176은
   이 경험식들을 2차 미사일·파편용 *대안*으로 격하하고 연성 비선형 해석을
   주경로로 둡니다.
3. **CW-03 — 세 체계가 말하는 '항공기 충돌'은 서로 다른 사건입니다(EUR 목차로 확정).**
   EUR의 **우발적** 설계기준은 **경항공기 + 군용항공기** 하중함수입니다(제2.4장
   §1.3.3.1.1, §1.3.3.1.2) — 대형 상용항공기가 아닙니다. EUR에서 대형기는 **고의적**
   충돌(§1.3.3.2)이 담당하며, 제2.1장은 이를 **§8.3 보안(Security)** 아래 둡니다.
   미국은 대형 상용기, 체코는 1E-7/년을 넘는 모든 낙하물체(항공기 여부 무관)입니다.
   설계기준·허용기준을 논하기 전에 **대상 사건 자체가 다릅니다.**

4. **CW-05 — 체코는 단일 기준이 아니라 2단 구조입니다.** § 12는 일반 기본
   외부 설계사건을 **1E-4/년**으로, § 13(2)(b)는 항공기·물체 낙하를
   **1E-7/년**으로 정합니다. 3자릿수 차이 자체가 핵심입니다 — 항공기 추락을
   훨씬 희소한 사건으로 취급하기에 설계기준 안에 두면서도 설계 전체를 지배하지
   않게 됩니다. 또한 1E-7의 출처는 SSG-79가 아니라 **SSG-68 각주 9**이며,
   IAEA는 이를 "일부 국가가 사용하는" 값으로 제시할 뿐 강제하지 않습니다.
   미국 규정에는 확률 스크리닝 자체가 없습니다.
5. **체코는 임계값이 아니라 '루프'입니다.** 부지 시행령 378/2016 § 13은 *설계가 상정한
   저항성을 초과하는* 낙하의 확률을 구하라 하고, 설계 시행령 329/2017 § 11(4)(b)는 그
   저항성을 1E-7/년 기준으로 정합니다. 두 시행령이 서로의 출력을 입력으로 삼으므로
   반복 수렴이 필요합니다 — SSG-68 3.4가 권고하는 부지·설계 피드백 과정 그대로입니다.
   미국·EUR 어느 쪽도 부지와 설계를 이렇게 명시적으로 결합하지 않습니다.

6. **CW-07 — 위협 수치의 정량 비교는 여전히 불가능합니다(원문으로 확인).**
   NEI 07-13은 "규정이 항공기의 고유 모델이나 초기 충돌속도를 정의하지 않으며"
   Riera 함수는 "공급사에게 제공된다"고 명시합니다 — 즉 승인된 방법론 자체도
   하중값을 공개하지 않습니다. SSG-68 5.170은 대신 기종·질량·속도를
   "규제기관이 지정할 수 있다"고 합니다.

## 저작권

- 10 CFR 50.150, RG 1.217: 미국 연방정부 저작물(퍼블릭 도메인)
- NEI 07-13: © Nuclear Energy Institute — 요약만 수록, 본문 비커밋
- IAEA 문서: © IAEA — 무료 배포이나 저작권 있음, 본문 비커밋
- EUR: 라이선스 필요 — 본문 미수록, 공개된 목차·역할 정보만 기재
- 체코 법령: 관보 공표 문서

`corpus/raw/`는 `.gitignore` 처리되어 있습니다. 내려받은 원문을 커밋하지 마세요.
