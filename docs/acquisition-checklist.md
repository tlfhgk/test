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

## 남은 것 — 2건

### 1. IAEA SRS No. 88 — 잘못된 파일이 왔습니다

`IAEA SRS 88.pdf` 는 **STI/PUB/771 「Medical Handling of Accidentally Exposed
Individuals」**(1988년 의료 피폭 문헌)였습니다. "88"로 검색하다 연도가 걸린 것으로 보입니다.

- 필요한 것: *Human Induced External Events: **Margin Assessment***
- https://www.iaea.org/publications/10914/safety-aspects-of-nuclear-power-plants-in-human-induced-external-events-margin-assessment
- 푸는 것: CW-09의 IAEA 여유도(HCLPF) 근거 — 현재 `web_verified`

### 2. EUR Volume 2 Rev. E — 유료, 대체 불가

비교 매트릭스에서 EUR 칸이 CW-03 · CW-08 · CW-11에서 `비공개`로 남은 유일한 원인입니다.

- https://europeanutilityrequirements.eu/ (라이선스 구매)
- **사기 전에 판단하세요:** RG 1.217 원문에서 미국도 위협 수치를 SGI(안전조치정보)로
  통제한다는 것이 확인되었으므로, EUR을 구매해도 3자 수치 비교는 여전히 반쪽입니다.
- 라이선스 문서이므로 본문을 저장소에 커밋하지 마세요.

### 참고 — 다시 받을 필요 없는 것

`IAEA SSR 68.pdf` 로 주신 파일은 SSR-6(방사성물질 안전수송)이었으나,
**진짜 SSG-68은 이미 색인되어 있습니다.**

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
