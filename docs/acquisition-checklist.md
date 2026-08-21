# 확보해야 할 원문 목록

이 DB는 현재 **3개 문서만 원문(축자) 색인**되어 있습니다. 나머지는 요약 레코드입니다.
아래는 무엇을, 어디서, 왜 받아야 하는지를 효과 순으로 정리한 것입니다.

살아있는 상태는 언제나 `python3 scripts/report_gaps.py` 로 확인하세요.

## 이미 확보된 것 (추가 작업 불필요)

| 문서 | 쪽수 | 축자 청크 |
|---|---|---|
| NEI 07-13 Rev. 8P | 69 | 146 |
| IAEA SSG-68 | 112 | 226 |
| IAEA SRS No. 87 | 220 | 332 |

---

## P1 — 10 CFR 50.150 원문 · **가장 효과 큼**

미국 연방정부 저작물(퍼블릭 도메인)이라 받아서 커밋까지 해도 됩니다.

- **왜:** 이 문서 하나가 **미검증 레코드 5건**(`(a)(2) (a)(3) (b) (c) (d)`)과
  **비교항목 6건**(CW-02, CW-03, CW-04, CW-05, CW-10, CW-12)을 한꺼번에 해소합니다.
  현재 이 5건은 제 배경지식으로 쓴 것이라 조문 구조·항호 번호가 검증되지 않았습니다.
  특히 `(c)` 변경관리 조항은 신뢰도 `low`입니다.
- **어디서:**
  - https://www.ecfr.gov/current/title-10/chapter-I/part-50/subject-group-ECFR448a4b6d297d970/section-50.150
  - https://www.govinfo.gov/content/pkg/CFR-2025-title10-vol1/pdf/CFR-2025-title10-vol1-sec50-150.pdf
- **넣을 위치:** `corpus/raw/US-10CFR50.150/`

## P2 — Regulatory Guide 1.217 · **판단이 갈리는 지점**

- **왜:** NEI 07-13 Rev.8 승인에 **단서가 붙었는지**를 결정합니다. 반복 검색해도
  승인 문장 한 줄만 나오고 예외 조항이 안 보이지만, 그것으로 "무조건부 승인"을
  확정할 수는 없습니다. 이 문서가 CW-07·CW-08에서 확정한 경험식 선택
  (Modified NDRC / reduced Chang / reduced Degen / CEA-EDF)을 규제기관이
  **그대로 받아들였는지** 아니면 조건을 달았는지를 가릅니다.
- **어디서:** ADAMS **ML092900004**
  - https://www.nrc.gov/docs/ML0929/ML092900004.pdf
- **넣을 위치:** `corpus/raw/US-RG-1.217/`

## P3 — 체코 법령 3종

§ 조문번호와 체코어 문구는 검색으로 복구해 `web_verified`로 기록했지만,
관보 원문으로 확인해야 인허가 문서에 인용할 수 있습니다.

| 문서 | 상태 | 받을 곳 |
|---|---|---|
| vyhláška 329/2017 Sb. (설계) | § 6, § 12, § 13(2)(b) 복구됨 — 원문 미확인 | https://sujb.gov.cz/fileadmin/sujb/docs/legislativa/vyhlasky/329_2017.pdf |
| zákon 263/2016 Sb. (원자력법) | 위임조항만 확인 | https://www.zakonyprolidi.cz/cs/2016-263 |
| **vyhláška 378/2016 Sb. (부지)** | **시행령 번호 자체가 미확인** | https://www.zakonyprolidi.cz/cs/2016-378 |

- **왜:** 329/2017은 §13(2)(b) 문구 확정(현재 인용문이 2차 출처 기반),
  378/2016은 **번호가 맞는지부터** 확인이 필요합니다. 부지단계 항공교통 평가가
  1E-7/년 입력을 어디서 만드는지가 여기 달려 있습니다.
- **넣을 위치:** `corpus/raw/CZ-329-2017/`, `corpus/raw/CZ-263-2016/`, `corpus/raw/CZ-378-2016/`

## P4 — IAEA 나머지 4종 · 무료

무료 다운로드지만 저작권이 있으므로 `corpus/raw/`(gitignore)에만 두세요.

| 문서 | 해소되는 것 |
|---|---|
| **SSG-79** | 1E-7 기준의 귀속 정정 확인, NS-G-3.1 대체 여부 확정 (현재 `to_verify`) |
| SSR-2/1 Rev.1 | Requirement 17 문구 확정 (현재 `model_knowledge`) |
| SRS No. 86 | 3부작 체계 |
| SRS No. 88 | HCLPF 여유도 평가 — CW-09의 IAEA 쪽 근거 보강 |

- **어디서:** https://www.iaea.org/publications — 각 문서 페이지에서 무료 PDF
  - SSG-79: https://www-pub.iaea.org/MTCD/Publications/PDF/PUB2036_web.pdf
  - SRS-86: https://www-pub.iaea.org/MTCD/Publications/PDF/P1721_web.pdf

## P5 — EUR Volume 2 · **유료, 대체 불가**

- **왜:** 비교 매트릭스에서 EUR 칸이 CW-03·CW-08·CW-11에서 `비공개`로 남아 있는
  유일한 원인입니다. 위협 시나리오와 다단계 성능목표의 **수치**는 이 문서에만
  있습니다. 다른 어떤 공개자료로도 대체되지 않습니다.
- **어디서:** https://europeanutilityrequirements.eu/ (라이선스 구매 필요)
- **주의:** 라이선스 문서이므로 본문을 저장소에 **커밋하지 마세요.**
  `corpus/raw/EU-EUR/`는 이미 gitignore 처리되어 있습니다.

## P6 — 유럽 무료 문서 2종

- Council Directive 2014/87/Euratom — https://eur-lex.europa.eu/eli/dir/2014/87/oj
  (현재 `model_knowledge`, CW-07·CW-10이 의존)
- WENRA SRL 2020 / Issue TU — https://wenra.eu/sites/default/files/publications/wenra_safety_reference_level_for_existing_reactors_2020.pdf

## P7 — Google Drive 재인증

Drive에 있던 다음 2편은 다운로드 중 **세션이 만료**되어 못 받았습니다.
재인증만 하면 바로 색인할 수 있습니다. 규제문서가 아니라 참고문헌으로 편입됩니다.

- `Safety assessment of a nuclear power plant building subjected to an aircraft crash.pdf`
- `Effects of reinforcement ratio and arrangement on the structural behavior of a nuclear building under aircraft impact.pdf`

---

## 받은 뒤 할 일

파일을 `corpus/raw/<SOURCE_ID>/` 에 넣고 한 줄이면 끝납니다.

```bash
python3 scripts/ingest_raw.py --replace     # 원문 → 축자 청크 색인
python3 scripts/report_gaps.py              # 남은 공백 재확인
```

`scripts/fetch_sources.sh` 는 위 URL들을 자동으로 받도록 이미 작성되어 있습니다.
네트워크가 열린 환경(사내망 아닌 개인 PC 등)에서 실행하세요.

```bash
bash scripts/fetch_sources.sh && python3 scripts/ingest_raw.py --replace
```

## 왜 제가 직접 못 받는지

이 세션의 아웃바운드 HTTPS는 조직 egress 정책으로 **전면 차단**되어 있습니다.
`ecfr.gov`, `nrc.gov`, `govinfo.gov`, `sujb.gov.cz`, `zakonyprolidi.cz`,
`www-pub.iaea.org`, `eur-lex.europa.eu`, `wenra.eu` 모두 CONNECT 단계에서 403을
반환하며, 허용된 호스트는 패키지 레지스트리와 Anthropic API뿐입니다. 정책 거부이므로
TLS 검증 해제나 프록시 우회로 회피하지 않았습니다. 확보한 3개 문서는 사용자
Google Drive 커넥터를 통해 받은 것입니다.
