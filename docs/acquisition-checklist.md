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

## 남은 것 — EUR 요건 본문 1건

15개 소스 전부가 색인되었습니다. EUR만 **공개 목차 수준**입니다.

### EUR Volume 2 Rev. E — 요건 본문 (라이선스 필요)

공개 챕터 목차로 **구조는 확정**되었습니다. 없는 것은 요건 본문과 그림의 **수치**입니다.

확보된 목차 정보:

| 위치 | 내용 |
|---|---|
| Ch. 2.4 §1.3.3.1 | Accidental Aircraft crash — **Fig. 4 Light Aircraft**, **Fig. 5 Military Aircraft** 하중함수 |
| Ch. 2.4 §1.3.3.2 | Intentional Aircraft crash — Fig. 6 하중함수 예시 |
| Ch. 2.4 §1.4 | Sabotage (별도 인위적 재해) |
| Ch. 2.4 §5.8.1.4 | Aircraft impact (건물 설계하중) |
| Ch. 2.1 §2.6.2.1.1 | Accidental aircraft crash (표준설계 외부재해 식별) |
| Ch. 2.1 §8.3.3 | Intentional aircraft crash (**§8.3 Security** 하위) |

없는 것: Figure 4·5·6의 하중-시간 값, 성능목표 수치, §5.9 하중조합, §5.1.7 저항수준의 정의.

- https://europeanutilityrequirements.eu/ (라이선스 구매)
- **구매 판단:** 목차만으로 EUR이 미국·체코와 **다른 사건**을 다룬다는 사실이 이미 확정
  되었으므로(CW-03), 구조 비교 목적이라면 추가 구매가 불필요합니다. 하중값 대 하중값
  비교가 목표일 때만 의미가 있는데, 미국 측 값이 SGI로 통제되므로 그 경우에도 3자 비교는
  성립하지 않습니다.
- 라이선스 문서이므로 본문을 저장소에 커밋하지 마세요.

### 선택사항 — EUR 나머지 챕터 목차 18개

Drive `EUR TABLE VOLUME 2` 폴더에 2.2, 2.3, 2.5~2.20 목차가 있습니다. 항공기 관련 항목은
2.1과 2.4에 집중되어 있어 읽지 않았습니다. 필요하시면 마저 색인하겠습니다.

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
