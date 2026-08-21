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
pip install -r requirements.txt

python3 scripts/build_db.py            # YAML 코퍼스 → db/aircraft_impact.db
python3 scripts/query.py "체코 항공기 추락 설계기준 빈도"
python3 scripts/make_matrix.py         # docs/comparison-matrix.md 재생성
python3 scripts/report_gaps.py         # 미검증 항목 점검
```

원문을 넣어 축자(verbatim) 색인까지 하려면:

```bash
bash scripts/fetch_sources.sh          # 공개 문서를 corpus/raw/ 로 내려받기
python3 scripts/ingest_raw.py --replace
```

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
scripts/report_gaps.py         출처 검증 상태 보고
docs/comparison-matrix.md      비교 매트릭스 (자동생성)
docs/methodology.md            방법론·출처검증 정책·한계
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

현재 30개 조항 레코드 중 **12건이 미검증 상태**입니다
(`python3 scripts/report_gaps.py`로 확인). 주된 원인은 이 DB를 구축한 실행
환경에서 ecfr.gov, nrc.gov, sujb.gov.cz, iaea.org 등 원문 도메인에 대한 아웃바운드
접근이 조직 egress 정책으로 차단되어 원문 PDF를 내려받을 수 없었기 때문입니다.
`scripts/fetch_sources.sh` → `scripts/ingest_raw.py`를 네트워크가 열린 환경에서
실행하면 축자 텍스트가 같은 DB에 들어가고, 검색 시 요약본보다 우선하게 됩니다.

## 핵심 결론 3가지

`docs/comparison-matrix.md`의 상세 근거를 요약하면:

1. **CW-04 — 규제 계층이 다릅니다.** 미국은 대형 상용항공기 충돌을 설계기준
   *초과*(BDB)로 두고 현실적 해석을 요구합니다. 체코는 우발적 추락을 설계기준
   *안*에 둡니다. 같은 사건을 다른 계층에 배치하므로 요건 대 요건 1:1 매핑은
   성립하지 않습니다.
2. **CW-05 — 정량적으로 일치하는 지점은 하나입니다.** 체코 시행령의
   "1천만 년에 1회 초과"와 IAEA SSG-79의 스크리닝 확률수준 1E-7/원자로-년은
   같은 값입니다. 반면 미국 규정에는 확률 스크리닝 자체가 없습니다.
3. **CW-03 — 위협 수치의 정량 비교는 공개자료로 불가능합니다.** 미국은 충돌
   속도·각도·질량·연료량을 보안정보로 비공개하고, EUR은 유료 문서입니다.
   비교는 방법론과 판정논리 수준에서만 유효합니다.

## 저작권

- 10 CFR 50.150, RG 1.217: 미국 연방정부 저작물(퍼블릭 도메인)
- NEI 07-13: © Nuclear Energy Institute — 요약만 수록, 본문 비커밋
- IAEA 문서: © IAEA — 무료 배포이나 저작권 있음, 본문 비커밋
- EUR: 라이선스 필요 — 본문 미수록, 공개된 목차·역할 정보만 기재
- 체코 법령: 관보 공표 문서

`corpus/raw/`는 `.gitignore` 처리되어 있습니다. 내려받은 원문을 커밋하지 마세요.
