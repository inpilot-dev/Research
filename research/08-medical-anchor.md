# 08 — 의학 리서치 스킬 선점자 확인 + 세부 분야(specialty) 축 검증

> 조사일: **2026-09-01**
> 대상: Claude Code research 플러그인 v1의 의학·생명과학 앵커. 핵심 가설 = **"NCT 사전등록 1차 결과지표 ↔ 논문 보고 결과지표 대조로 outcome switching 탐지"**
> 근거 표기: **[직접]** = 이 조사에서 API/파일을 직접 호출·열람한 값. **[2차]** = 검색으로 확인한 서드파티 요약. **[미확인]** = 확인 실패.

---

## 0. 판정 요약 (결론부터)

### 질문 1 판정: **비어 있다. 단, "아무도 생각 못 한 것"이 아니라 "아무도 자동화하지 않은 것"이다.**

| 층위 | 상태 | 근거 |
|---|---|---|
| Claude 스킬/플러그인/MCP 생태계 | **완전히 비어 있음** | `skills find`로 10+ 키워드 전수 검색 → registry↔publication 결과지표 대조를 하는 스킬 **0건** [직접] |
| GitHub 오픈소스 | **사실상 비어 있음** | GitHub 검색 `outcome+reporting+bias+clinicaltrials` → **0건**, `prespecified+outcome+publication+comparison` → **0건**, `outcome+switching` → 53건 전부 무관(모노폴리 게임, 유저스크립트 등) [직접] |
| 학술계 | **아이디어는 확립됨, 도구는 죽었거나 다른 것을 함** | COMPare(2015–16)는 **전수 수작업**, 코드 없음, 종료. trialstreamer/RobotReviewer는 **2022년 이후 커밋 없음** [직접] |
| 최신 SOTA | **인접하지만 다름 — 여기가 유일한 진짜 위협** | npj Digital Medicine 2026 논문이 LLM으로 outcome change를 탐지하나, **"registry ↔ registry에 게시된 결과(posted results)"** 비교이지 registry↔논문이 아님 [2차, 초록 인용] |

**"시도됐다가 실패했는가?"에 대한 답 — 실패의 원인은 기술이 아니라 노동·인센티브였다.**
COMPare는 기술적으로 막힌 게 아니다. 67개 트라이얼을 사람이 손으로 대조했고, 저널에 편지 58통을 보냈는데 **6통만 게재, 16통 거절, 36통은 4주 뒤에도 무응답**이었다 [2차]. 즉 병목은 "탐지"가 아니라 "탐지 후에 아무 일도 일어나지 않는다"였다. 이건 **자동화가 정확히 해결하는 종류의 병목**이다(사람이 안 하니까 안 되는 것). 반대로 말하면, 이 도구의 가치 제안을 "저널을 고치겠다"로 잡으면 COMPare와 같은 벽에 부딪힌다. **"이 논문을 읽는 사람에게 30초 안에 경고를 준다"**로 잡아야 한다.

**기술적으로 안 되는 이유는 발견되지 않았다.** 오히려 직접 측정한 수치는 우호적이다(§1.4).

### 질문 2 판정: **세부 분야는 스킬이 아니라 프로파일 데이터다.**
선례가 실재한다 — `Aperivue/medsci-skills`는 보고 가이드라인 **52개를 마크다운 파일**로, 저널 관행을 **저널 프로파일 파일**로 두고, 스킬은 라우팅만 한다. 그리고 `add-journal`이라는 "데이터를 추가하는 스킬"까지 있다 [직접]. **세부 분야로 스킬을 나눈 사례는 검색 범위 내에서 0건.**

### 질문 3 판정: **기존 의학 스킬의 "검증"은 대부분 서지 검증(citation exists?)에서 멈춘다.** 주장↔데이터 검증까지 간 것은 `Aperivue/medsci-skills` 하나뿐이고, 그것조차 **저자가 자기 원고를 투고 전에 점검하는 용도**이지 **출판된 문헌을 독자가 감사하는 용도**가 아니다. 이 축이 비어 있다.

---

## 1. 질문 1 — NCT 사전등록 대조 / outcome switching 선점자 조사

### 1.1 Claude 스킬 / 플러그인 / MCP 생태계 [직접 검색]

`skills` CLI(skills.sh 레지스트리)로 다음 키워드를 전수 검색했다:
`pubmed`, `clinical`, `trial`, `medical`, `evidence`, `systematic`, `grade`, `prisma`, `cochrane`, `pico`, `outcome switching`, `registry`, `clinicaltrials`, `risk of bias`, `reproducibility`, `retraction`, `spin`, `meta-analysis`, `epidemiology`, `oncology`, `cardiology`, `psychiatry`, `registration timing`, `protocol deviation`, `CONSORT`, `STROBE`, `trial registry publication`.

**결과: registry ↔ publication 결과지표 대조를 수행하는 스킬은 0건.**

임상시험 관련 스킬로 실제 존재하는 것 전부:

| 스킬 | 설치수 | 실제로 하는 일 | 대조 기능 |
|---|---:|---|---|
| [google-deepmind/science-skills @clinical-trials-database](https://github.com/google-deepmind/science-skills/tree/main/skills/clinical_trials_database) | 1.7K | ClinicalTrials.gov APIv2 **CLI 래퍼**. 서브커맨드는 `get_study`, `get_eligibility`, `search`, `count`, `raw_query` 뿐 [직접, 스크립트 확인] | ❌ 없음 |
| [anthropics/healthcare @clinical-trial-protocol](https://github.com/anthropics/healthcare) | 412 | FDA/NIH 규격 **프로토콜 작성**. (marketplace.json에 `deprecated` 태그, `healthcare@healthcare`로 통합) [직접] | ❌ 없음 (작성 방향) |
| [mims-harvard/ToolUniverse](https://github.com/mims-harvard/ToolUniverse) @clinical-trial-design / @clinical-trial-matching | 431 / 375 | 시험 설계·환자 매칭 | ❌ 없음 |
| jaechang-hits/sciagent-skills @clinicaltrials-database-search | 66 | 검색 | ❌ 없음 |
| yorkeccak/scientific-skills @clinical-trials-search | 170 | 검색 | ❌ 없음 |
| open-medica/open-medical-skills @clinical-trials-search | 25 | 검색 (실체는 YAML 인덱스 엔트리) [직접] | ❌ 없음 |

> **패턴**: 임상시험 스킬은 전부 (a) 검색하거나 (b) 새 시험을 설계하거나 (c) 환자를 매칭한다. **이미 끝난 시험이 정직하게 보고됐는지 검사하는 스킬은 없다.**

### 1.2 GitHub 오픈소스 [직접, GitHub Search API]

| 쿼리 | 총 결과 | 관련 있는 것 |
|---|---:|---|
| `outcome+switching` | 53 | **0** (Monty Hall 시뮬레이터, 유저스크립트, 게임 봇 등) |
| `outcome+reporting+bias+clinicaltrials` | **0** | — |
| `prespecified+outcome+publication+comparison` | **0** | — |
| `clinicaltrials+pubmed+compare+outcomes` | 1 | 0 (SkimLit, 초록 문장 분류 튜토리얼) |

### 1.3 학술계 선행 연구 — 각각 무엇을 했고 왜 안 쓰이는가

#### (a) COMPare Trials — [compare-trials.org](https://www.compare-trials.org/)
- **방법: 전수 수작업.** 사이트 본문 표현 그대로 "compared each clinical trial report with its protocol or registry entry" 후 "wrote a letter to the journal" [직접 열람].
- **기간: 2015년 10월 ~ 2016년 1월.** 상위 5개 의학 저널에 실린 모든 트라이얼.
- **결과**: 67건 중 완벽 보고는 **9건뿐**. 미보고 결과지표 301개, 조용히 추가된 결과지표 357개. 평균적으로 사전지정 결과지표의 **62.0%만 보고**하고 **5.3개를 몰래 추가** [2차].
- **저널 반응**: 편지 58통 → **게재 6, 거절 16, 4주 뒤 무응답 36** [2차].
- **코드/도구: 없음.** 사이트에 데이터셋·코드 저장소 링크가 존재하지 않음 [직접 확인].
- **왜 널리 안 쓰이나**: 애초에 "도구"가 아니라 **감사 캠페인**이었다. 사람이 한 편씩 읽는 방식이라 확장 불가능했고, 2016년 이후 활동 흔적 없음.

#### (b) Trialstreamer / RobotReviewer — **둘 다 사실상 사망** [직접, GitHub API]

| 레포 | ★ | 라이선스 | 마지막 push | 상태 |
|---|---:|---|---|---|
| [ijmarshall/trialstreamer](https://github.com/ijmarshall/trialstreamer) | **23** | 없음 | **2022-06-24** | 4년 이상 정체 |
| [ijmarshall/robotreviewer](https://github.com/ijmarshall/robotreviewer) | **177** | GPL-3.0 | **2022-07-18** | 4년 이상 정체 |

- 하는 일: RCT 자동 식별, PICO 추출, **Cochrane Risk of Bias 자동 평가**. 82만 건 이상의 RCT 라이브 DB를 표방 [2차].
- **registry↔publication 결과지표 대조는 하지 않는다.** RoB 도구는 논문 내부 서술만 본다.
- 호스팅 인스턴스(`trialstreamer.ieai.robotreviewer.net`)는 **DNS 해석 실패**(`ENOTFOUND`) [직접]. 서드파티 문서는 아직 살아 있다고 적고 있으나, 이 조사 시점에 접속되지 않았다.
- **왜 안 쓰이나**: 학술 프로젝트의 전형적 종말 — 논문이 나오고 그랜트가 끝나면 유지보수가 멈춘다. ★23은 "커뮤니티가 형성된 적이 없다"는 뜻이다.

#### (c) Trials to Publications (UIC Arrowsmith) — **연결 문제는 이미 풀렸다**
- 논문: [PMC9006700](https://pmc.ncbi.nlm.nih.gov/articles/PMC9006700/) / [PubMed 35020887](https://pubmed.ncbi.nlm.nih.gov/35020887/)
- NCT 번호를 주면 그 시험의 결과를 보고했을 가능성이 높은 PubMed 논문을 확률 순위로 반환. 21,430개의 알려진 trial-publication 쌍으로 학습한 로지스틱 회귀. **Recall@10 78–91%, precision 90.4%, AUC 0.95** [직접 열람].
- 한계(저자 명시): 실시간 처리에 최대 10분, adaptive/platform trial 매칭 난이도, 같은 연구자가 유사 시험을 여러 개 돌린 경우 오매칭.
- **의미**: 우리 파이프라인의 1단계(NCT→논문 링크)는 **이미 해결된 문제**이며, 게다가 우리는 더 싼 경로가 있다(§1.4).

#### (d) npj Digital Medicine 2026 — **가장 주의해야 할 인접 연구**
- [An automated approach to improve clinical trial registration and to identify outcome changes on ClinicalTrials.gov](https://www.nature.com/articles/s41746-026-03045-y), npj Digital Medicine, 2026-07.
- 성능(초록 인용, [2차]): 불완전 등록 식별 **sensitivity 0.91 / PPV 0.98**. 결과지표 변경 식별 **sensitivity 0.97 / PPV 0.95**, 누락 결과지표 96.1% / 추가 결과지표 97.9% 정확 식별.
- **결정적 차이**: 초록 문구가 *"When comparing prospective registrations with **posted results**"* 이다. **posted results = ClinicalTrials.gov에 게시된 결과 섹션**이지 논문이 아니다. 즉 **레지스트리 내부 대조**다.
- ⚠️ **[미확인]** — nature.com이 IdP 리다이렉트(303)로 막혔고 Europe PMC에도 아직 색인되지 않아(DOI 조회 결과 0건, [직접]) **본문·코드 공개 여부·데이터셋을 확인하지 못했다.** 이 논문의 저자들이 다음 단계로 "논문 쪽"까지 확장할 가능성은 실재하는 위험이며, **본문을 반드시 직접 읽어야 한다.**

#### (e) Aperivue/medsci-skills — **스킬 생태계 안에서 가장 가까운 것** [직접, 파일 열람]
- [Aperivue/medsci-skills](https://github.com/Aperivue/medsci-skills) · **278★ · MIT · 2026-04-06 생성 · 2026-08-31 push** (활발)
- **90개의 실제 파이썬 detector**를 보유(`metadata/detectors_catalog.json`, 90건 [직접 파싱]). 예: `check_reported_p_from_counts`(2×2 표 정수 카운트에서 P값 재계산해 불일치 플래그), `check_prisma_figure`(PRISMA Figure 1 산술 감사), `check_table_percentages`(n(p%) 셀을 분모로 재계산), `check_scope_coherence`(엔드포인트↔결론 범위 일치).
- **registry 관련 항목이 딱 하나 있다**: `skills/check-reporting/references/step4c_registration_timing.md` [직접 열람]. 그 안의 4번 항목이 우리 가설과 정확히 겹친다:
  > "**When the author provides the registry record** (PROSPERO PDF, ClinicalTrials.gov export) as a supplement or accompanying document: Primary outcome(s), eligibility criteria, and analysis plan described in Methods must agree with the registry entry... A silent discrepancy between registry and Methods is a `[REGISTRATION-TIMING]` finding."
- **그러나 세 가지가 다르다**:
  1. **API를 호출하지 않는다.** "저자가 레지스트리 기록을 제출했을 때" 조건부다. 자동 fetch·자동 diff가 없다.
  2. **대상이 원고(manuscript)다.** 투고 전 저자 자가점검용이다. 이미 출판된 논문을 독자가 감사하는 방향이 아니다.
  3. **detector 90개 중 registry 대조 detector는 0개.** 카탈로그 전문을 grep했으나 `registr`/`NCT`/`prespecified` 매칭은 파일 헤더 주석("Machine-readable **registry** of the detector suite")뿐이었다 [직접].

### 1.4 기술적 실현 가능성 — 직접 측정

#### (i) ClinicalTrials.gov API v2: primaryOutcome은 완전히 구조화돼 있다 ✅ [직접 curl]

```
GET https://clinicaltrials.gov/api/v2/studies/NCT04280705?format=json
```
응답 구조(실측):
- `protocolSection.outcomesModule.primaryOutcomes[]` → 각 원소가 `{measure, description, timeFrame}` **구조화 필드**
- `protocolSection.outcomesModule.secondaryOutcomes[]` 동일
- `resultsSection.outcomeMeasuresModule.outcomeMeasures[]` → 각 원소에 `type: "PRIMARY" | "SECONDARY"`, `title`, `description`, `populationDescription`, `timeFrame` (이 시험은 43개)
- `hasResults: true` 플래그
- **`protocolSection.referencesModule.references[]` → 각 원소에 `pmid`와 `citation` 문자열, `type: "DERIVED"`** ← **레지스트리가 직접 PMID를 준다**

> 즉 **레지스트리 쪽은 파싱이 아니라 필드 읽기**다. NLP가 전혀 필요 없다. 그리고 §1.3(c)의 ML 링킹 도구조차 상당 부분 불필요하다 — CT.gov가 이미 PMID를 들고 있다.

#### (ii) 논문 쪽 결과지표 추출 난이도 — 초록만으로 되는가? 직접 실험

ACTT-1(NCT04280705)의 주논문 [PMID 32445440](https://pubmed.ncbi.nlm.nih.gov/32445440/) 초록을 E-utilities로 받아 확인 [직접]:

> "METHODS: ... **The primary outcome was the time to recovery**, defined by either discharge from the hospital or hospitalization for infection-control purposes only."
> "CONCLUSIONS: ... (Funded by ...; ACTT-1 **ClinicalTrials.gov number, NCT04280705**.)"

레지스트리 값은 `primaryOutcomes[0].measure = "Time to Recovery"`. **초록 한 문장으로 대조가 성립한다.** NCT 번호도 초록 안에 있다. PMCID도 있다.

#### (iii) 그러면 이게 전체 문헌의 몇 %에서 되는가? — PubMed E-utilities로 직접 카운트

2024–2025년 출판, `randomized controlled trial[pt]` 기준 [직접, esearch]:

| 항목 | 건수 | 비율 |
|---|---:|---:|
| A. RCT 전체 | **54,309** | 100% |
| B. PubMed 메타데이터에 ClinicalTrials.gov 링크 존재 (`clinicaltrials.gov[si]`) | **14,517** | **26.7%** (A 대비) |
| C. B 중 초록에 "primary outcome/endpoint" 언급 (`[tiab]`) | **4,407** | **30.4%** (B 대비) |
| D. B 중 PMC 무료 전문 존재 | **8,357** | **57.6%** (B 대비) |

**해석 — 이 숫자가 프로젝트의 실제 스코프를 정한다:**
- 링킹은 **ML 없이 PubMed `[si]` 필드만으로** 연 7천여 건(2년 14,517건)이 확보된다. 여기에 CT.gov `referencesModule.pmid`를 합치면 더 늘어난다.
- 대상 논문의 **약 30%는 초록만으로 즉시 대조 가능**(가장 싸고 빠른 경로).
- **약 58%는 PMC 전문 접근 가능** → Methods 섹션 파싱 경로.
- 나머지(초록에 1차 결과지표 언급 없음 + PMC 없음)는 **판정 불가로 남겨야 한다.** 여기서 추측하면 도구가 죽는다.
- ⚠️ 반대로, **"초록에 1차 결과지표를 명시하지 않은 것" 자체가 CONSORT 위반 신호**다(CONSORT for Abstracts). 즉 판정 불가 케이스도 버리지 말고 별도 등급으로 보고할 여지가 있다.

#### (iv) 문제의 규모 — 이게 실제로 흔한가 [2차]
- RCT: 등록↔출판 1차 결과지표 불일치 **중앙값 31%**, 전향적 등록만 보면 **41%** ([PMC4650202](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4650202/))
- 메타분석: 1차 결과지표 불일치 **29–37%**, 2차 결과지표 불일치 **50–75%** ([PMC10551944](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10551944/))
- 관찰연구(중재): outcome switching **47%**, 1차 결과지표를 완전 사전지정한 연구는 **18%뿐**, 변경 사유를 밝힌 연구는 **2%** ([BMJ Group 요약](https://bmjgroup.com/outcome-switching-in-cohort-studies-of-interventions-meta-epidemiological-study/))
- RCT 후속 논문에서 outcome switching 고빈도 ([J Clin Epidemiol 2021](https://www.jclinepi.com/article/S0895-4356(21)00146-3/fulltext))

> **3건 중 1건꼴로 걸린다.** 이건 "가끔 잡히는 희귀 이벤트"가 아니라 **데모에서 랜덤으로 논문을 골라도 히트가 나는 밀도**다. 런칭 데모 관점에서 매우 유리하다.

### 1.5 질문 1 최종 판정 — 낙관하지 않고 정리

**비어 있다. 다만 다음 4개는 진짜 리스크다:**

1. **npj 2026 팀의 확장.** 레지스트리 내부 대조를 sensitivity 0.97로 푼 팀이 논문 쪽으로 확장하는 것은 자연스러운 다음 논문이다. **본문을 직접 읽어 코드 공개 여부와 Future Work를 확인해야 한다.** [현재 미확인]
2. **"탐지 후 아무 일도 안 일어난다"는 COMPare의 벽.** 저널은 반응하지 않았다. 가치 제안을 저널 교정이 아니라 **독자 측 경고**로 잡아야 한다.
3. **판정 불가 비율.** 초록에 1차 결과지표가 없고 PMC 전문도 없는 케이스가 상당수다. 이걸 억지로 판정하면 false positive가 나오고, 이 도메인에서 FP는 치명적이다(존재하지 않는 부정행위를 지목하는 것).
4. **"불일치 = 부정행위"가 아니다.** 정당한 프로토콜 수정, 등록 오기, 시점 차이가 존재한다. 출력은 **"switching이다"가 아니라 "레지스트리와 논문이 이 지점에서 다르다, 논문에 사유 설명이 있는가/없는가"**여야 한다. COMPare가 저널과 싸운 지점이 정확히 이 해석 문제였다.

---

## 2. 질문 2 — 의학 세부 분야(specialty) 축

### 2.1 세부 분야가 리서치 관점에서 실제로 다른 점

#### (a) RCT 가능 여부 / 증거 위계 — 직접 측정 [PubMed esearch, 2024–2025]

| MeSH major topic | 전체 논문 | RCT[pt] | RCT 비율 | CT.gov 링크 | 링크/RCT 비 |
|---|---:|---:|---:|---:|---:|
| Neoplasms (종양) | 276,340 | 5,800 | 2.1% | 6,309 | **1.09** |
| Cardiovascular Diseases (심혈관) | 154,188 | 5,591 | 3.6% | 5,089 | **0.91** |
| Mental Disorders (정신) | 108,460 | 5,145 | 4.7% | 2,771 | **0.54** |
| Communicable Diseases (감염) | 26,704 | 1,024 | 3.8% | 957 | 0.93 |
| Surgical Procedures, Operative (외과) | 169,327 | 9,189 | 5.4% | 4,734 | **0.52** |
| Pediatrics | 2,096 | 30 | 1.4% | 10 | 0.33 |

> ⚠️ `Pediatrics[majr]`는 질환이 아니라 **진료과 자체**를 가리키는 좁은 MeSH여서 다른 행과 직접 비교 불가다. 소아 문헌 규모를 보려면 `Child`/`Infant`로 다시 재야 한다. **[측정 방법의 한계로 표시]**

**우리 도구에 직결되는 발견 — "링크/RCT 비" 열을 보라.**
종양학·심혈관·감염병의 RCT는 CT.gov 링크가 RCT 수와 거의 1:1로 붙는다. 반면 **정신과(0.54)와 외과(0.52)는 RCT의 절반가량이 PubMed 메타데이터에 레지스트리 링크가 없다.** 즉 **이 도구의 커버리지는 세부 분야마다 2배 차이가 난다.** v1 데모를 외과나 정신과로 잡으면 "찾을 수 없음"이 절반 나온다. **v1 앵커는 종양학 또는 심혈관이어야 한다.**

#### (b) 보고 가이드라인이 분야마다 다르다 — 실물 목록 [직접, Aperivue 파일 트리]
`Aperivue/medsci-skills`가 번들한 체크리스트 **52개 파일**이 그대로 이 축의 지도다:

| 연구 유형/분야 | 가이드라인 |
|---|---|
| RCT | CONSORT (2025), CONSORT-AI, SPIRIT/SPIRIT-AI(프로토콜) |
| 관찰연구 | STROBE, STROBE-MR(멘델리안 무작위화), RECORD(청구/EHR/레지스트리), TARGET(target trial emulation) |
| 진단정확도 | STARD, STARD-AI, QUADAS-2/3/C |
| 예측모델 | TRIPOD, TRIPOD+AI, TRIPOD-LLM, PROBAST/PROBAST+AI, PGS-RS |
| 체계적 문헌고찰 | PRISMA 2020, PRISMA-Abstracts, PRISMA-DTA, PRISMA-P, PRISMA-ScR, MOOSE, AMSTAR 2, ROBIS, SWiM |
| 종양(예후 바이오마커) | REMARK |
| 증례보고 | CARE |
| 영상/방사선 | CLAIM 2024, CLEAR(radiomics) |
| 질적연구 | SRQR, COREQ |
| 보건경제 | CHEERS 2022 |
| 설문 | CROSS, CHERRIES |
| 동물 | ARRIVE 2.0 |
| 질 향상 | SQUIRE 2.0 |
| RoB 도구 | RoB 2, ROBINS-I, ROBINS-E, ROB-ME, NOS, COSMIN, RoB NMA |

> ⚠️ **라이선스 지뢰**: 이 파일들의 라이선스가 균일하지 않다. Aperivue가 자체 기록한 바에 따르면 TRIPOD(2015), QUADAS-2/3, PROBAST, PRISMA-DTA는 **오픈 라이선스 없음(© ACP / © AMA)**, ROBINS-I는 **CC BY-NC(비상업)**, CARE는 오픈 라이선스 미확인이다 [직접, SKILL.md 열람]. 체크리스트 원문을 번들할 계획이라면 이 목록을 그대로 따라가야 하고, 상업적 배포를 염두에 둔다면 NC 조항이 문제가 된다.

#### (c) 결과지표 관행 — 우리 가설과 직결
- **종양학**: 대리 지표(PFS, ORR) ↔ 최종 지표(OS)의 전환이 outcome switching의 전형적 무대. 실제로 [종양 RCT 대리 엔드포인트 outcome switching 횡단연구(PMC5569019)](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5569019/)가 존재한다.
- **심혈관**: 복합 엔드포인트(MACE) 구성 요소를 바꾸는 형태.
- **정신과**: 평가척도 자체가 바뀌거나(HAM-D↔MADRS) 시점이 바뀌는 형태.
- **[미확인]** 분야별 switching 유형 분포를 정량화한 통합 연구는 이번 조사에서 확인하지 못했다.

### 2.2 세부 분야별로 스킬을 나눈 사례가 있는가? → **없다** [직접 검색]

- `skills find oncology/cardiology/psychiatry/epidemiology` 전수 확인 결과, 세부 분야 이름이 붙은 **리서치** 스킬 세트는 없다.
- 존재하는 것은 (a) **툴 도메인** 스킬 — `mims-harvard/tooluniverse@tooluniverse-precision-oncology`, `@tooluniverse-epidemiological-analysis` 등. 이건 분석 도구지 문헌 리서치가 아니다. (b) **개인 콘텐츠 스킬** — `drshailesh88/integrated_content_os@cardiology-visual-system`, `@cardiology-editorial`. 심장내과 의사의 SNS 콘텐츠 제작용이다.
- [Open-Medica/open-medical-skills](https://github.com/Open-Medica/open-medical-skills)(15★)는 주제별 스킬을 나열하지만 실체가 `content/skills/*.yaml` **인덱스 엔트리**이고, 분야 축이 아니라 평평한 목록이다 [직접, 파일 트리].
- [K-Dense-AI/scientific-agent-skills](https://github.com/K-Dense-AI/scientific-agent-skills)(41,055★)는 **163개 스킬**을 가졌지만 축이 **라이브러리별**이다(scanpy, rdkit, polars, pydicom, statsmodels…). 세부 분야 축이 아니다 [직접, 트리 파싱].

### 2.3 세부 분야를 데이터로 처리한 사례는 있는가? → **있다. 이게 답이다** [직접]

`Aperivue/medsci-skills`의 구조:

```
skills/check-reporting/references/checklists/*.md      ← 가이드라인 52개 = 데이터
skills/find-journal/references/journal_profiles/*.md   ← 저널 프로파일 (AJR, NEJM,
                                                          Annals, Chest, BMC Medicine,
                                                          AJKD, AJNR, ... ) = 데이터
skills/analyze-stats/references/table-standards/journal-profiles/*.yaml
                                                       ← 저널별 표 규격 = 데이터
skills/add-journal/SKILL.md                            ← "프로파일을 추가하는 스킬"
skills/check-reporting/SKILL.md                        ← 라우팅만 하는 단일 스킬
```

핵심은 **`add-journal`의 존재**다. 확장 지점이 "새 스킬 작성"이 아니라 **"새 데이터 파일 추가"**로 설계돼 있고, 그 추가 작업 자체를 스킬로 만들어 뒀다. 그리고 저널 프로파일이 방사선과에 편중돼 있다(AJR, Radiology, AJNR, European Radiology, Clinical Radiology, Academic Radiology, BJR…) — **저자의 전공이 데이터로만 드러나고 코드에는 전혀 스며들지 않았다.** 이것이 정확히 우리가 원하는 성질이다.

### 2.4 질문 2 최종 판정

> **세부 분야 = 프로파일 데이터. 스킬도 아니고 어댑터도 아니다. 그렇다고 무시해도 되는 것도 아니다.**

| 선택지 | 판정 | 이유 |
|---|---|---|
| 세부 분야마다 스킬 | ❌ | 선례 0건. 스킬 N개는 유지비만 N배. 로직이 99% 동일하다 |
| 어댑터(코드) | ❌ | 분야 차이는 코드 분기가 아니라 **어떤 표를 참조하느냐**의 차이다 |
| **프로파일 데이터 (YAML/MD)** | ✅ | Aperivue가 52개 체크리스트 + 저널 프로파일로 실증. `add-journal` 패턴까지 존재 |
| 아예 무시 | ❌ | §2.1(a)에서 측정했듯 **커버리지가 분야마다 2배 차이**난다. 무시하면 데모가 깨진다 |

**v1 구체 권고**:
- 프로파일 파일 하나당 담을 것: 해당 분야의 **기본 보고 가이드라인**(RCT→CONSORT), **전형적 1차 결과지표 어휘**(종양: OS/PFS/ORR/DFS, 심혈관: MACE 구성요소, 정신: HAM-D/MADRS/PANSS), **대리 지표 목록**, **주요 저널·레지스트리**.
- 코드에는 분야가 등장하지 않게 할 것. 분야는 `profiles/oncology.yaml` 하나를 더 얹는 것으로 끝나야 한다.
- **v1은 종양학 하나만.** §2.1(a)에서 레지스트리 링크율이 가장 좋고(링크/RCT 1.09), 대리 지표 전환이라는 서사가 가장 선명하다. 외과·정신과는 커버리지 절반이라 v1 데모에 부적합하다.

---

## 3. 질문 3 — 기존 의학 리서치 스킬의 "검증" 깊이 전수

### 3.1 검증 깊이 표 [전부 직접 파일/README 열람]

검증 레벨 정의: **L0** 검색만 · **L1** 서지 존재 검증(이 인용이 실재하는가) · **L2** 논문 내부 정합성(Methods↔Results, 표 산술) · **L3** 논문 ↔ **외부 1차 출처** 대조(레지스트리·원자료)

| 프로젝트 | ★ / 활성 | 실체 | 검증 레벨 | 근거 |
|---|---|---|---|---|
| [avivlyweb/nagomi-pubmed-plugin](https://github.com/avivlyweb/nagomi-pubmed-plugin) | **0★** / 2026-02-27 | 스킬 5개 + MCP 서버(`pubmed_mcp.py` 4,314줄) + `reference_checker/`(1,361줄) | **L1** | §3.2 |
| [Aperivue/medsci-skills](https://github.com/Aperivue/medsci-skills) | 278★ / 2026-08-31 | 60개 스킬, **90개 파이썬 detector** | **L2** (+L3 조건부·수동) | §1.3(e) |
| [K-Dense-AI/scientific-agent-skills](https://github.com/K-Dense-AI/scientific-agent-skills) | **41,055★** / 2026-08-31 | 163개 스킬, 대부분 파이썬 라이브러리 래퍼 | **L0** | 트리 파싱: scanpy/rdkit/polars… `literature-review`·`scientific-critical-thinking`은 프롬프트 |
| [google-deepmind/science-skills](https://github.com/google-deepmind/science-skills) | 2,810★ / 2026-07-07 | DB 래퍼 모음(ChEMBL, ClinVar, dbSNP, ClinicalTrials, PubMed…) | **L0** | CLI 서브커맨드가 `get/search/count/raw_query`뿐 |
| [cyanheads/pubmed-mcp-server](https://github.com/cyanheads/pubmed-mcp-server) | 142★ / 2026-08-21 | MCP 툴 11개 | **L0~L1** | `pubmed_lookup_citation`(ECitMatch로 부분 서지→PMID 해석)이 L1에 걸침. 나머지는 검색/조회/인용포맷 |
| Taru0208/pubmed-mcp-server | **[미확인]** | — | — | GitHub API **404 Not Found** [직접]. 삭제·비공개·이름 변경 중 하나. 동명 대안은 [JackKuo666/PubMed-MCP-Server](https://github.com/JackKuo666/PubMed-MCP-Server) 126★ 등 다수 |
| [Future-House/paper-qa](https://github.com/Future-House/paper-qa) | 9,133★ / 2026-08-26 | RAG 기반 논문 QA. 답변에 **문장 단위 근거 인용**을 강제 | **L1** (인용 정합성) | 논문 간·외부 출처 대조는 범위 밖 |
| [anthropics/healthcare](https://github.com/anthropics/healthcare) | 403★ / 2026-08-27 | 스킬 11개: prior-auth, icd10-cm, procedure-coding, fhir, fraud-detection, clinical-trial-protocol… | **L0** (문헌 검증 아님) | 트리 확인. 축이 **지불자/의료기관 업무**이지 연구 검증이 아니다 |
| [ijmarshall/robotreviewer](https://github.com/ijmarshall/robotreviewer) | 177★ / **2022-07-18** | Cochrane RoB 자동 평가 | **L2** | 죽음 |
| [ijmarshall/trialstreamer](https://github.com/ijmarshall/trialstreamer) | **23★** / **2022-06-24** | RCT 라이브 DB | **L0~L2** | 죽음, 호스트 DNS 실패 |

> **빈 칸이 명확하다: L3(논문 ↔ 외부 1차 출처)를 자동으로 하는 것이 하나도 없다.** L2 최고봉인 Aperivue조차 L3은 "저자가 파일을 첨부했다면"이라는 수동 조건부다.

### 3.2 nagomi의 "ABC-TOM"과 "GRADE" 원본 확인 — 요청대로 코드까지 팠다

#### ABC-TOM → **실제 코드다** ✅
`pubmed-mcp/reference_checker/verification_engine.py` (1,361줄) 안에 진짜 구현돼 있다 [직접, 소스 열람]:
```python
class VerificationStatus(str, Enum):
    VERIFIED_LEGACY_DOI = "VERIFIED_LEGACY_DOI"
    GREY_LITERATURE     = "GREY_LITERATURE"
    LOW_QUALITY_SOURCE  = "LOW_QUALITY_SOURCE"
    SUSPICIOUS          = "SUSPICIOUS"
    DEFINITE_FAKE       = "DEFINITE_FAKE"
    ...
THRESHOLD_SUSPICIOUS = 0.50
GREY_LITERATURE_KEYWORDS = { ... }
```
우선순위 분기(`Priority 1: DEFINITE_FAKE` → `Priority 5: SUSPICIOUS`)와 "Frankenstein citation"(DOI는 유효하나 전혀 다른 논문을 가리킴) 판정이 실제 조건문으로 구현돼 있다. **아이디어 자체는 좋고, 우리가 참고할 만하다.**

> ⚠️ 다만 **"6-tier"는 틀린 수치다.** SKILL.md frontmatter의 `description`은 "ABC-TOM **6-tier** classification system"이라고 적혀 있는데, 같은 파일 본문의 표는 **"ABC-TOM Classification System (8-Tier)"**이고 실제 항목도 8개다 [직접, 원문 대조]. 문서 내부 모순이다.

#### GRADE → **GRADE가 아니다** ❌ (이게 가장 중요한 확인)
README는 "GRADE-style confidence ratings"라고 쓰지만, `pubmed_mcp.py` 실제 코드는 **자체 제작 가중합 휴리스틱**이다 [직접, 소스 열람]:

```python
STUDY_DESIGN_SCORES = {"systematic_review":95, "rct":85, "cohort":70,
                       "case_control":60, "cross_sectional":50, "case_series":40, "unknown":30}
EVIDENCE_GRADES = {(80,100):"A", (60,79):"B", (40,59):"C", (0,39):"D"}

overall_score = int(base_score*0.35 + methodology_score*0.25 +
                    sample_size_score*0.15 + recency_score*0.10 + journal_score*0.15)
```
구성 요소의 실제 구현:
- `_estimate_sample_size_score`: **초록에 정규식** `r"n\s*=\s*(\d+)"`, `r"(\d+)\s*patients"` 등을 걸어 최대값을 취한 뒤 구간 매핑.
- `_calculate_journal_score`: 하드코딩된 `HIGH_IMPACT_JOURNALS` 문자열 리스트에 저널명이 부분일치하면 95, 중간이면 70, 아니면 50.
- `_calculate_recency_score`: 출판연도.

**GRADE 프레임워크의 5개 강등 도메인(risk of bias, inconsistency, indirectness, imprecision, publication bias)은 코드 어디에도 없다.** 이건 "GRADE-style"이라기보다 **저널 명성 + 초록 정규식 + 출판연도로 만든 A/B/C/D 라벨**이다. 실제 GRADE 등급과 같은 이름의 문자를 출력하기 때문에 **오해를 유발한다.**

> **우리 프로젝트에 주는 교훈**: 이 도메인에서 "GRADE"·"Cochrane"·"PRISMA" 같은 이름을 붙이면 의료 종사자는 그 프레임워크를 실제로 구현했다고 읽는다. 현장 검증에서 코드를 열어 보이는 순간 nagomi와 같은 지적을 받는다. **구현하지 않은 프레임워크의 이름을 빌리지 말 것.**

기타 관찰: 이 레포는 **`pubmed-mcp/venv/`(가상환경 전체)를 커밋**했다 [직접, 트리]. `aiohttp`의 `.so` 바이너리까지 들어 있다. ★0의 이유 중 하나로 보인다.

---

## 4. 종합 — 이 프로젝트가 서야 할 자리

```
                     외부 1차 출처 대조 (L3)
                              ↑
                       ██ 여기가 비어 있음 ██
                              |
  Aperivue medsci-skills ●    |  (L2, 90 detectors, 단 "저자 자가점검" 방향)
                              |
  RobotReviewer ○(2022 사망)   |  (L2, RoB)
                              |
  nagomi ●  paper-qa ●        |  (L1, 서지/인용 검증)
                              |
  DeepMind science-skills ●   |  (L0, DB 래퍼)
  K-Dense (41k★) ●            |  (L0, 라이브러리 래퍼)
```

**차별화 문장(사실만으로 구성 가능)**:
> "ClinicalTrials.gov에 사전등록된 1차 결과지표와 논문이 실제로 보고한 1차 결과지표를 자동으로 대조한다. 레지스트리 쪽은 API v2의 구조화 필드를 그대로 읽고(NLP 불필요), 논문 쪽은 초록의 primary outcome 문장 또는 PMC 전문에서 뽑는다. 불일치를 발견하면 '부정행위'라고 부르지 않고, **레지스트리 값·논문 값·논문이 사유를 설명했는지 여부**를 나란히 보여준다."

**즉시 해야 할 검증(이 조사에서 못 한 것)**:
1. **npj Digital Medicine 2026 논문 본문 확보** — 코드 공개 여부와 Future Work. 이 프로젝트의 유일한 실질 위협.
2. **파일럿 100건 수동 검증** — §1.4(iii)의 26.7%/30.4%/57.6%는 메타데이터 카운트일 뿐, "대조가 실제로 성립하는 비율"이 아니다. 종양학 RCT 100건을 뽑아 실제로 몇 건에서 정확한 판정이 나오는지 직접 재야 한다. **false positive가 1건이라도 나오면 규칙을 조여야 한다.**
3. **체크리스트 라이선스 정리** — CONSORT/PRISMA는 CC BY지만 TRIPOD·QUADAS·PROBAST는 오픈 라이선스가 없고 ROBINS-I는 CC BY-NC다(§2.1(b)).

---

## 5. 확인하지 못한 것 (미확인 명시)

| 항목 | 사유 |
|---|---|
| npj Digital Medicine 2026 논문 **본문·코드 공개 여부·데이터셋** | nature.com이 IdP 인증 리다이렉트(303)로 차단. Europe PMC DOI 조회 결과 0건(미색인) [직접 시도] |
| `Taru0208/pubmed-mcp-server` | GitHub API **404 Not Found** [직접]. 삭제/비공개/리네임 중 하나로 추정되나 확인 불가 |
| Trialstreamer 호스팅 인스턴스의 현재 상태 | `trialstreamer.ieai.robotreviewer.net` **DNS 해석 실패(ENOTFOUND)** [직접]. 일시적 장애인지 서비스 종료인지 구분 불가 |
| Consensus 등 일부 사이트 | 이 조사 범위 밖 |
| 세부 분야별 outcome switching **유형** 분포 정량화 | 통합 연구를 찾지 못함 |
| `Pediatrics[majr]` 행의 비교가능성 | 진료과 MeSH라 질환 MeSH와 직접 비교 불가. `Child`/`Infant`로 재측정 필요 |
| skills.sh 레지스트리의 **전수성** | `skills find`는 레지스트리 검색이다. 레지스트리에 등록하지 않고 GitHub에만 있는 스킬은 §1.2의 GitHub 검색으로 보완했으나 100% 전수는 아니다 |
