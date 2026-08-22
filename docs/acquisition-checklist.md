# 확보해야 할 원문 목록

살아있는 상태는 `python3 scripts/report_gaps.py` 로 확인하세요.

## 확보 완료 — 10개 문서, 축자 청크 1,519개

| 문서 | 분량 | 상태 |
|---|---|---|
| 10 CFR 50.150 (2026-08-20 기준) | 3 p | ✔ |
| Regulatory Guide 1.217 | 6 p | ✔ |
| NEI 07-13 Rev. 8P | 69 p | ✔ |
| vyhláška 329/2017 Sb. | 48 p | ✔ |
| WENRA SRL 2020 (Issue TU) | — | ✔ |
| IAEA SSG-68 | 112 p | ✔ |
| IAEA SSG-79 | 114 p | ✔ |
| IAEA SSR-2/1 | 99 p | ✔ |
| IAEA SRS No. 86 | 104 p | ✔ |
| IAEA SRS No. 87 | 220 p | ✔ |

레코드 등급: `primary_source` 36 · `web_verified` 7 · `model_knowledge` 2 · `to_verify` 1

---

## 다시 받아야 하는 것 — 파일은 주셨으나 사용 불가

세 건은 폴더에 있었지만 쓸 수 없었습니다. `.quarantine/` 에 보관 중입니다.

### 1. IAEA SRS No. 88 — **다른 문서가 들어왔습니다**

받은 `IAEA SRS 88.pdf` 는 **STI/PUB/771 「Medical Handling of Accidentally Exposed
Individuals」** 였습니다. 1988년 의료 피폭 문헌으로 항공기와 무관합니다.
"88"로 검색하다 연도가 걸린 것으로 보입니다.

- 필요한 것: *Safety Aspects of NPPs in Human Induced External Events: **Margin Assessment***
- https://www.iaea.org/publications/10914/safety-aspects-of-nuclear-power-plants-in-human-induced-external-events-margin-assessment
- 푸는 것: CW-09의 IAEA 여유도(HCLPF) 근거

### 2. IAEA SSG-68 — **이미 갖고 있으니 다시 받을 필요 없습니다**

받은 `IAEA SSR 68.pdf` 는 **SSR-6 「Regulations for the Safe Transport of Radioactive
Material」**(2012)이었습니다. SSG-68과 SSR-6이 섞인 것 같습니다.
**진짜 SSG-68은 이미 색인되어 있으므로 추가 조치가 필요 없습니다.**

### 3. 체코 원자력법 263/2016 · 부지 시행령 378/2016 — **스캔본**

두 파일 모두 **텍스트 레이어가 없는 이미지 PDF**입니다(각각 0자 추출).
이 환경에는 OCR 엔진이 없어 읽지 못했습니다.

- 필요한 것: 텍스트가 선택되는 PDF (zakonyprolidi.cz 또는 e-sbirka.gov.cz 의 HTML/PDF)
- https://www.zakonyprolidi.cz/cs/2016-263 · https://www.zakonyprolidi.cz/cs/2016-378
- **378/2016은 시행령 번호 자체가 아직 미확인**입니다 — 번호만 알려주셔도 됩니다.
- 푸는 것: 마지막 남은 `to_verify` 1건

---

## 아직 안 받은 것

### 4. Council Directive 2014/87/Euratom — 추출 실패

폴더의 `Council Directive 2014 87 Euratom.pdf` 는 EUR-Lex 웹페이지를 인쇄한 것으로
보이며 본문이 추출되지 않았습니다(머리글만 나옴).

- 필요한 것: EUR-Lex의 **공식 PDF**(본문 포함)
- https://eur-lex.europa.eu/eli/dir/2014/87/oj
- 푸는 것: 남은 `model_knowledge` 2건 중 1건, CW-07 · CW-10

### 5. EUR Volume 2 Rev. E — **유료, 대체 불가**

비교 매트릭스에서 EUR 칸이 CW-03 · CW-08 · CW-11에서 `비공개`로 남은 유일한 원인입니다.

- https://europeanutilityrequirements.eu/ (라이선스 구매)
- **판단이 필요합니다:** 미국도 위협 수치를 SGI로 통제하므로, EUR을 사도 3자
  수치 비교는 여전히 반쪽입니다. 수치 비교가 실제로 필요한지 먼저 정하세요.
- 라이선스 문서이므로 본문을 저장소에 커밋하지 마세요.

### 6. 논문 2편 — 선택사항

폴더의 aircraft crash 구조평가 논문 2편은 규제문서가 아니라 참고문헌입니다.
Drive 다운로드 경로가 복구되면 넣겠습니다.

---

## 파일 형식 요령

Drive의 `download_file_content` 경로가 현재 불안정합니다(검색·읽기는 정상).
텍스트 레이어가 있는 PDF는 `read_file_content` 로 우회 추출이 가능하지만,
**스캔본은 어느 경로로도 읽을 수 없습니다.** 가능하면 관보·기관 사이트의
원본 PDF(텍스트 선택 가능)를 올려 주세요.

## 받은 뒤

```bash
python3 scripts/ingest_raw.py --replace
python3 scripts/report_gaps.py
```
