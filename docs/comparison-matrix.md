# 비교 매트릭스 — 항공기 충돌 규제 (NEI 07-13 기준)

> 자동 생성 파일입니다. 직접 수정하지 마세요.
> `corpus/crosswalk/crosswalk.yaml` 을 고친 뒤 `python3 scripts/build_db.py && python3 scripts/make_matrix.py` 를 실행하세요.

기준(baseline)은 미국 방법론(10 CFR 50.150 → RG 1.217 → NEI 07-13)이며, 각 칸은 그 기준 대비 해당 문서의 위치를 나타냅니다.

| # | 비교 항목 | 10 CFR 50.150 | RG 1.217 | NEI 07-13 | CZ 329/2017 | EUR | WENRA | SSG-68 | SRS-87 |
|---|---|---|---|---|---|---|---|---|---|
| CW-01 | 항공기 충돌 요건은 어떤 형식의 문서가 담고 있으며 구속력이 있는가? | **기준** | **기준** | – | 구조 상이 | 구조 상이 | 부분 | 부분 | – |
| CW-02 | 적용 대상이 신규 원전에 한정되는가, 기존 원전도 포함하는가? | **기준** | – | – | 구조 상이 | – | – | – | – |
| CW-03 | 항공기 위협은 어떻게 정의되며, 수치는 공개되는가? | **기준** | – | – | 구조 상이 | 비공개 | – | 부분 | – |
| CW-04 | 대형 항공기 충돌은 설계기준사건인가, 설계기준초과사건인가? | **기준** | – | – | 구조 상이 | 구조 상이 | 부분 | 동등 | – |
| CW-05 | 항공기 추락 포함 여부를 정하는 명시적 확률 스크리닝 기준이 있는가? | **기준** | – | – | 구조 상이 | – | – | – | – |
| CW-06 | 어떤 구조물과 기기를 평가해야 하는가? | – | – | **기준** | 부분 | – | – | 부분 | – |
| CW-07 | 충돌하중은 어떻게 정의되며 특정 방법이 강제되는가? | – | – | **기준** | 없음 | – | – | – | 동등 |
| CW-08 | 국부손상(침투·배면박리·관통)은 어떻게 평가하는가? | – | – | **기준** | 없음 | 비공개 | – | – | 동등 |
| CW-09 | 합격/불합격 판정기준은 무엇인가? | **기준** | – | **기준** | 부분 | 구조 상이 | – | – | – |
| CW-10 | 고의적 충돌과 우발적 충돌을 함께 다루는가? | **기준** | – | – | – | 부분 | – | – | – |
| CW-11 | 운전원 조치를 어느 정도까지 인정할 수 있는가? | **기준** | – | – | 없음 | 비공개 | – | 없음 | – |
| CW-12 | 평가결과는 어떻게 문서화·심사·공개되는가? | **기준** | – | **기준** | 부분 | – | – | – | – |

범례: `baseline` = **기준** · `equivalent` = 동등 · `partial` = 부분 · `stricter` = 더 엄격 · `looser` = 더 완화 · `different-architecture` = 구조 상이 · `no-equivalent` = 없음 · `not-public` = 비공개 · `–` 해당 항목에 기재 없음

---

## 항목별 상세

### CW-01 — 항공기 충돌 요건은 어떤 형식의 문서가 담고 있으며 구속력이 있는가?

*주제 축: T01 법적 근거 및 구속력 (Legal basis and binding nature)*

**EN:** What kind of instrument carries the aircraft impact requirement, and is it binding?

미국은 구속력 있는 연방규정(10 CFR 50.150)이 '평가 의무'만 규정하고, 기술적 방법론은 비구속 규제지침(RG 1.217)이 승인한 산업계 문서(NEI 07-13)에 있다. 체코는 반대로, 구속력 있는 시행령(329/2017 Sb.)이 설계기준 자체를 직접 규정하되 상세 해석방법은 규정하지 않는다. EUR은 법령이 아닌 계약문서이고, IAEA·WENRA는 비구속 권고이다.

| 문서 | 관계 | 내용 |
|---|---|---|
| `US-10CFR50.150` | **기준** | Binding rule; states the duty and the acceptance criteria, contains no methodology. |
| `US-RG-1.217` | **기준** | Non-binding guide; supplies the method by endorsing NEI 07-13 Rev. 8. |
| `CZ-329-2017` | 구조 상이 | Binding decree that itself fixes the design-basis selection rule; method left to the applicant. |
| `EU-EUR` | 구조 상이 | Contractual utility requirement; binds only via the procurement contract. |
| `IAEA-SSG-68` | 부분 | Non-binding recommendations; becomes binding only through national adoption. |
| `EU-WENRA-SRL` | 부분 | Harmonisation reference implemented through member regulators. |

근거 조항: `US-10CFR50.150-a-1`, `US-RG-1.217-endorsement`, `CZ-263-2016-enabling`, `EU-EUR-scope`, `IAEA-SSG-68-scope`, `EU-WENRA-external-hazards`

### CW-02 — 적용 대상이 신규 원전에 한정되는가, 기존 원전도 포함하는가?

*주제 축: T02 적용범위 (Applicability and scope)*

**EN:** Which plants are covered — new build only, or the existing fleet as well?

미국 규정은 신규 원전 신청자에게만 적용되는 장래효 규정이다. 체코 시행령은 원자로 열출력 50 MW 초과 시설이라는 출력 기준으로 적용범위를 정한다. IAEA SRS 86/87/88은 기존 원전과 신규 원전 모두를 대상으로 방법론을 기술한다.

| 문서 | 관계 | 내용 |
|---|---|---|
| `US-10CFR50.150` | **기준** | New reactor applicants only (DC, SDA, COL, ML, CP, OL); existing fleet excluded. |
| `CZ-329-2017` | 구조 상이 | Applicability keyed to reactor thermal power > 50 MW, not to licensing vintage. |
| `IAEA-SRS-86` | 부분 | Explicitly addresses application to both existing and new plants. |

근거 조항: `US-10CFR50.150-a-3`, `CZ-329-2017-aircraft-dbe`, `IAEA-SRS-86-framework`

### CW-03 — 항공기 위협은 어떻게 정의되며, 수치는 공개되는가?

*주제 축: T03 위협(항공기) 정의 (Threat / aircraft characterisation)*

**EN:** How is the aircraft threat defined, and are the numbers public?

가장 큰 실무적 차이. 미국은 '미국 내 장거리 운항 대형 상용항공기'라는 정성적 정의만 공개하고, 질량·속도·연료량 등 구체적 수치는 보안정보로 비공개한다. 체코는 위협을 수치로 지정하지 않고 '빈도 1E-7/년 초과 물체의 영향 강도'라는 확률기준으로 도출하게 한다. EUR은 복수의 위협 시나리오를 명시하나 문서가 유료·비공개다. 따라서 세 체계의 위협 파라미터를 직접 수치 비교하는 것은 공개자료만으로는 불가능하다.

| 문서 | 관계 | 내용 |
|---|---|---|
| `US-10CFR50.150` | **기준** | Qualitative definition public; impact speed/angle/mass/fuel supplied by NRC as security-related information. |
| `CZ-329-2017` | 구조 상이 | No prescribed aircraft; the threat is whatever object exceeds the 1E-7/yr fall frequency at the site. |
| `EU-EUR` | 비공개 | Defines multiple explicit threat scenarios, but the values are behind a licence. |
| `IAEA-SSG-68` | 부분 | Recommends how to characterise the hazard; does not prescribe a threat aircraft. |

> **차이점/유의사항:** CRITICAL for any benchmarking exercise: a numeric comparison of threat parameters between the US, Czech and EUR frameworks cannot be performed from public sources. Comparison is only meaningful at the level of method and acceptance logic.

근거 조항: `US-10CFR50.150-a-2`, `CZ-329-2017-aircraft-dbe`, `EU-EUR-aircraft-crash`, `IAEA-SSG-68-scope`

### CW-04 — 대형 항공기 충돌은 설계기준사건인가, 설계기준초과사건인가?

*주제 축: T04 설계기준 대 설계기준초과 (Design basis vs beyond design basis)*

**EN:** Is the large aircraft impact a design-basis event or a beyond-design-basis event?

미국은 명시적으로 설계기준초과(BDB)로 두고, 보수적 설계기준 해석이 아닌 현실적 (realistic) 해석을 요구한다. 체코는 우발적 항공기 추락을 설계기준 안에 두고, 빈도 기준을 넘으면 설계기준 외부 기인사건으로 편입한다. EUR과 최근 IAEA 문서는 DBEE와 BDBEE(DEC) 두 수준을 모두 정의하는 다단계 구조를 취한다. 즉 세 체계는 같은 사건을 서로 다른 규제 계층에 배치하고 있으며, 이것이 요건 대 요건 매핑이 성립하지 않는 근본 원인이다.

| 문서 | 관계 | 내용 |
|---|---|---|
| `US-10CFR50.150` | **기준** | Explicitly beyond design basis; realistic (best-estimate) analysis, not design-basis conservatism. |
| `CZ-329-2017` | 구조 상이 | Accidental crash sits INSIDE the design basis once the frequency criterion is met. |
| `EU-EUR` | 구조 상이 | Multi-level: both DBEE and BDBEE/DEC performance objectives. |
| `IAEA-SSG-68` | 동등 | Covers both levels; explicitly recommends selecting BDB external events to verify margins — the closest structural match to the US posture plus a design-basis layer. |
| `EU-WENRA-SRL` | 부분 | Aircraft crash in the design per site; DEC for events exceeding the design basis. |
| `IAEA-SRS-88` | 부분 | Supplies the margin-assessment layer that the BDB level needs. |

> **차이점/유의사항:** This is the single largest divergence in the corpus. Consequences: (a) US analyses may use realistic material properties and best-estimate methods that a Czech design-basis analysis would not accept; (b) Czech/EUR results carry design-basis safety classification obligations that the US BDB assessment does not trigger.

근거 조항: `US-10CFR50.150-a-1`, `US-10CFR50.150-a-2`, `CZ-329-2017-aircraft-dbe`, `EU-EUR-aircraft-crash`, `IAEA-SSG-68-scope`, `EU-WENRA-external-hazards`, `IAEA-SRS-88-margins`

### CW-05 — 항공기 추락 포함 여부를 정하는 명시적 확률 스크리닝 기준이 있는가?

*주제 축: T05 확률론적 스크리닝 기준 (Probabilistic screening criterion)*

**EN:** Is there an explicit probabilistic screening criterion for including aircraft crash?

체코와 IAEA는 사실상 동일한 기준을 쓴다. 체코 시행령의 '1천만 년에 1회 초과'는 IAEA의 스크리닝 확률수준(SPL) 1E-7/원자로-년과 같은 값이다. 반면 미국 10 CFR 50.150은 확률 스크리닝을 두지 않는다 — 대형 상용항공기 충돌은 빈도와 무관하게 규정에 의해 직접 지정된 결정론적 시나리오이다.

| 문서 | 관계 | 내용 |
|---|---|---|
| `US-10CFR50.150` | **기준** | NO screening criterion. The threat is prescribed by rule, not selected by frequency. |
| `CZ-329-2017` | 구조 상이 | > 1 in 10,000,000 years (i.e. > 1E-7/yr) for an object falling on an area where it could cause a basic external initiating event. |
| `IAEA-SSG-79` | 구조 상이 | 1E-7 per reactor-year SPL, applied collectively to all events of the same type (e.g. all aircraft crashes). |

> **차이점/유의사항:** Strongest quantitative link in the crosswalk: CZ 329/2017 and IAEA SSG-79 use the same 1E-7/yr level. Note the IAEA caveat that the value is conservative only when applied to ALL events of one type collectively — applying 1E-7 to a single crash scenario is a different and less conservative reading.

근거 조항: `US-10CFR50.150-a-2`, `CZ-329-2017-aircraft-dbe`, `IAEA-SSG-79-spl`

### CW-06 — 어떤 구조물과 기기를 평가해야 하는가?

*주제 축: T06 평가대상 구조물·계통·기기 선정 (Target and SSC selection)*

**EN:** Which structures and components must be assessed?

NEI 07-13은 대상을 명확히 한정한다: 핵연료를 포함한 구조물(격납건물, 사용후핵연료 저장조)과 붕괴열 제거 기기를 수용한 구조물, 그리고 그 기능을 지원하는 전원·케이블 경로까지. 체코·IAEA는 '안전에 중요한 SSC'라는 일반적 범주를 쓰므로 범위가 더 넓지만 덜 구체적이다.

| 문서 | 관계 | 내용 |
|---|---|---|
| `US-NEI-07-13` | **기준** | Containment, SFP, structures housing heat-removal equipment; plus power supplies, cable runs and supporting components. |
| `CZ-329-2017` | 부분 | Generic 'structures, systems and components important to safety' — broader in principle, less prescriptive in practice. |
| `IAEA-SSG-68` | 부분 | Protection of SSCs important to safety, based on site hazard evaluation and installation layout. |

근거 조항: `US-NEI-07-13-scope`, `US-NEI-07-13-safety-function-assessment`, `CZ-329-2017-external-events-general`, `IAEA-SSG-68-scope`

### CW-07 — 충돌하중은 어떻게 정의되며 특정 방법이 강제되는가?

*주제 축: T07 충돌하중 정의 (Impact load definition)*

**EN:** How is the impact load defined and is a specific method mandated?

NEI 07-13은 국부하중과 전체하중의 산정, 재료 특성화, 파괴기준을 하나의 방법론으로 묶어 제공하며 RG 1.217이 이를 승인한다. IAEA SRS 87이 이에 대응하는 문서이나 권고가 아닌 정보성 안전보고서이다. 체코 시행령과 EU 지침은 하중 산정 방법을 규정하지 않는다 — 방법 선택은 신청자와 규제기관 협의에 맡겨진다.

| 문서 | 관계 | 내용 |
|---|---|---|
| `US-NEI-07-13` | **기준** | Integrated method: local + global loading, material characterisation, failure criteria; endorsed by RG 1.217. |
| `IAEA-SRS-87` | 동등 | IAEA counterpart for structural assessment of aircraft crash loading — but a Safety Report, i.e. informative only. |
| `CZ-329-2017` | 없음 | Decree sets the design basis, not the analysis method. |
| `EU-2014-87-EURATOM` | 없음 | Directive prescribes no load or method. |

근거 조항: `US-NEI-07-13-elements`, `US-RG-1.217-endorsement`, `IAEA-SRS-87-structures`, `CZ-329-2017-aircraft-dbe`, `EU-2014-87-framework`

### CW-08 — 국부손상(침투·배면박리·관통)은 어떻게 평가하는가?

*주제 축: T08 국부손상(관통·박리) (Local damage (perforation, scabbing))*

**EN:** How is local damage — penetration, scabbing, perforation — evaluated?

NEI 07-13은 경성 미사일이 철근콘크리트 벽체에 충돌할 때의 침투깊이, 배면 박리, 완전관통을 평가하는 산식을 직접 제공한다. 이 수준의 구체적 산식을 담은 대응 문서는 본 코퍼스에서 IAEA SRS 87뿐이다. 체코·EU 문서에는 대응 조항이 없다.

| 문서 | 관계 | 내용 |
|---|---|---|
| `US-NEI-07-13` | **기준** | Explicit formulae for missile penetration, backside scabbing and complete perforation of RC walls. |
| `IAEA-SRS-87` | 동등 | Same technical territory; formulation and empirical basis to be compared once both texts are ingested. |
| `CZ-329-2017` | 없음 |  |
| `EU-EUR` | 비공개 |  |

> **차이점/유의사항:** OPEN TECHNICAL QUESTION for the next iteration: which empirical perforation/scabbing correlations each document adopts (modified NDRC, Degen, Chang, CEA-EDF, etc.) and whether they agree. This cannot be answered from the summaries in this database — it requires ingesting NEI 07-13 Rev. 8P and IAEA SRS No. 87 into corpus/raw/.

근거 조항: `US-NEI-07-13-failure-modes`, `IAEA-SRS-87-structures`

### CW-09 — 합격/불합격 판정기준은 무엇인가?

*주제 축: T12 허용기준 및 안전기능 (Acceptance criteria / safety functions)*

**EN:** What is the pass/fail criterion?

미국 기준은 매우 구체적이다: 운전원 조치 의존을 줄인 상태에서 (노심냉각 또는 격납 건전성) 그리고 (사용후핵연료 냉각 또는 저장조 건전성). 두 쌍 모두 OR 구조라는 점이 중요하다 — 격납건전성 자체가 절대요건이 아니다. 체코·EUR·IAEA는 이런 형태의 단일 판정문 대신 안전기능 유지와 방사선학적 결과 제한이라는 일반 목표를 사용하며, EUR은 다단계 성능목표를 둔다.

| 문서 | 관계 | 내용 |
|---|---|---|
| `US-10CFR50.150` | **기준** | (core cooling OR containment integrity) AND (SFP cooling OR SFP integrity), with reduced use of operator actions. |
| `US-NEI-07-13` | **기준** | Translates structural damage into these safety-function outcomes. |
| `EU-EUR` | 구조 상이 | Multi-level performance objectives graded by threat scenario. |
| `IAEA-SRS-88` | 부분 | Margin-based plant/system performance evaluation rather than a binary criterion. |
| `CZ-329-2017` | 부분 | General design-basis safety-function requirements; no aircraft-specific pass/fail statement. |

근거 조항: `US-10CFR50.150-a-1`, `US-NEI-07-13-safety-function-assessment`, `EU-EUR-aircraft-crash`, `IAEA-SRS-88-margins`, `CZ-329-2017-external-events-general`

### CW-10 — 고의적 충돌과 우발적 충돌을 함께 다루는가?

*주제 축: T13 고의충돌 대 우발충돌 (Malicious vs accidental crash)*

**EN:** Are malicious (intentional) impacts treated together with accidental ones?

미국은 두 가지를 하나의 규정 안에서 다루되 위협 수치를 비공개로 처리한다 (10 CFR 50.150 + 2.390 비공개). EUR은 고의적 충돌을 별도 항목으로 명시적으로 둔다. EU 원자력안전지침은 보안·악의적 행위를 적용범위에서 명시적으로 제외한다. 체코는 설계 시행령이 아니라 물리적방호 체계에서 다루는 것으로 보인다.

| 문서 | 관계 | 내용 |
|---|---|---|
| `US-10CFR50.150` | **기준** | One rule covers the large commercial aircraft impact; the threat characterisation is withheld under 10 CFR 2.390. |
| `EU-EUR` | 부분 | Explicit separate treatment of the intentional aircraft crash alongside the accidental one. |
| `EU-2014-87-EURATOM` | 없음 | Security and malicious acts are expressly outside the nuclear safety directive's scope. |
| `CZ-263-2016` | 구조 상이 | Handled through nuclear security / physical protection provisions, not the public design decree. |

근거 조항: `US-10CFR50.150-a-2`, `US-10CFR50.150-d`, `EU-EUR-aircraft-crash`, `EU-2014-87-framework`, `CZ-malicious-separation`

### CW-11 — 운전원 조치를 어느 정도까지 인정할 수 있는가?

*주제 축: T15 운전원 조치 및 완화전략 (Operator action and mitigative strategies)*

**EN:** How much credit may be taken for operator action?

미국 규정은 'reduced use of operator actions'라는 명시적 제약을 판정기준 안에 넣은 유일한 문서이다. 본 코퍼스의 다른 어떤 문서도 항공기 충돌에 대해 이에 상응하는 명시적 제약을 두지 않는다.

| 문서 | 관계 | 내용 |
|---|---|---|
| `US-10CFR50.150` | **기준** | 'with reduced use of operator actions' is written into the acceptance criterion itself. |
| `CZ-329-2017` | 없음 |  |
| `IAEA-SSG-68` | 없음 |  |
| `EU-EUR` | 비공개 |  |

근거 조항: `US-10CFR50.150-a-1`

### CW-12 — 평가결과는 어떻게 문서화·심사·공개되는가?

*주제 축: T14 문서화·심사·정보통제 (Documentation, review and information control)*

**EN:** How are the assessment results documented, reviewed and disclosed?

미국은 핵심 설계특성을 FSAR에 기재하고 변경을 통제하며, NRC의 AIA 검사 프로그램으로 실제 구현 여부를 확인하되 평가내용 자체는 비공개할 수 있다. 그 결과 AP1000, US-EPR 등의 실제 평가결과는 공개 FSAR에 없고, 공개자료로는 방법론 수준의 비교만 가능하다.

| 문서 | 관계 | 내용 |
|---|---|---|
| `US-10CFR50.150` | **기준** | Key design features in the FSAR, change control, withholding under 2.390. |
| `US-NEI-07-13` | **기준** | NRC AIA inspection programme verifies as-built implementation. |
| `CZ-329-2017` | 부분 | Documented within the standard Czech safety documentation and SÚJB review; specifics not captured in this database. |

근거 조항: `US-10CFR50.150-b`, `US-10CFR50.150-c`, `US-10CFR50.150-d`, `US-NEI-07-13-aia-inspection`
