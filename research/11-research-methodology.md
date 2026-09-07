# 인간 전문가의 신뢰성 있는 리서치 방법론 — 리서치 에이전트가 따를 규칙 증류

**조사 목적**: "어떤 종류의 리서치든 아울러 신뢰성 있는 자료를 내놓는" 리서치 에이전트를 설계하기 전, 인간 전문가(사서, 팩트체커, 역학·의학 연구자, 정보분석관, 탐사보도 기자)가 신뢰 가능한 지식을 세우기 위해 실제로 쓰는 6가지 방법론을 1차/권위 출처로 확인한다. 조사만 수행하며 구현은 하지 않는다. 근거 없는 낙관 금지, 미확인은 미확인으로 표기.

---

## 1. 출처 위계 — 1차/2차/3차 출처

여러 대학 도서관 연구 가이드(정의가 거의 동일하게 수렴)를 기준으로:

- **1차 출처(primary source)**: 원래의 연구·발견·아이디어를 보고하는 자료. 편지·원고·일기·연설·인터뷰·정부기관 생산 문서·사진·영상·연구 원자료(raw data)·유물 등. 사건이나 발견에 **직접 관여한 당사자**가 만든 기록.
- **2차 출처(secondary source)**: 1차 출처를 해석·논평·평가하는 자료. 사건·아이디어·1차 출처를 분석·요약·논평.
- **3차 출처(tertiary source)**: 1차/2차 출처의 모음. 백과사전·연감·색인·초록·매뉴얼·교과서 등. **새로운 정보나 분석을 제공하지 않고**, 복잡한 1차/2차 담론을 비전문가가 입문할 수 있는 수준으로 압축.

**왜 1차가 2차 write-up보다 우선인가**: 2차·3차 출처는 원 자료를 거치며 선택·요약·프레이밍이 개입한다 — 이 과정에서 맥락 손실, 저자의 해석 편향, 단순화 오류가 누적된다. 1차 출처는 그 개입 이전의 원본이므로, 2차 출처의 주장을 검증하려면 그것이 인용하는 1차 출처(원 논문, 원 문서, 원 데이터)까지 거슬러 올라가는 것이 표준이다. 다만 1차 출처도 무비판적으로 신뢰할 수는 없다(작성자의 이해관계·오류 가능성) — 그래서 §2~§6의 검증 규율이 필요하다.

Sources: [Highline College Library](https://library.highline.edu/primarysources), [VCU Libraries — Identify Primary, Secondary, Tertiary Sources](https://guides.library.vcu.edu/sources), [UC Merced Library](https://libguides.ucmerced.edu/source-types)

---

## 2. Lateral Reading & SIFT — Mike Caulfield / Stanford History Education Group

### 2-1. SIFT (Four Moves) 원문

Mike Caulfield가 만든 웹 리터러시 방법론. 체크리스트형 평가(§2-3 CRAAP와 대비)가 아니라 **행동(move) 기반**.

- **Stop**: 읽거나 공유하기 전 멈춘다. 이 출처를 알고 있는가? 감정적 반응(분노·놀람을 유발하는 헤드라인)을 자각한다. 캐주얼한 열람과 깊은 조사는 다른 수준의 확인이 필요함을 인지한다.
- **Investigate the source**: 콘텐츠 자체를 읽기 전에 만든 주체의 전문성·동기·이력을 확인한다. Caulfield: "출처의 전문성과 의도(agenda)를 아는 것이 그들이 하는 말을 해석하는 데 핵심이다." 60초 내외의 짧은 조사로 충분하다고 권장 (Caulfield는 위키피디아에서 조직/사이트를 찾아보는 것을 추천).
- **Find better coverage**: 하나의 출처의 프레이밍을 그대로 받아들이지 않고, 그 **주장** 자체에 대해 다른 신뢰할 만한 보도·분석을 찾는다. 출처 자체는 잠시 제쳐두고 클레임 중심으로 재검색.
- **Trace claims (to original context)**: 인용문·수치·미디어를 원 맥락까지 추적해, 발췌 과정에서 왜곡되거나 편집되지 않았는지 확인한다.

네 가지 move의 공통 철학: 디지털 플랫폼이 흔히 제거해버리는 **맥락을 재구성**하는 것.

Source: [Hapgood — SIFT (The Four Moves), Mike Caulfield](https://hapgood.us/2019/06/19/sift-the-four-moves/)

### 2-2. Lateral Reading — Stanford History Education Group (SHEG) 연구

SHEG(Sam Wineburg 주도)가 스탠퍼드 학부생·4개 대학 역사학 교수·현직 프로 팩트체커를 대상으로 온라인 정보 신뢰도 평가 능력을 비교하는 실험을 수행했다.

- **방법**: 세 그룹에게 미국소아과학회(American Academy of Pediatrics, 정통 전문 단체)와 미국소아과대학(American College of Pediatricians, 실제로는 특정 의제를 감춘 위장 단체)의 웹사이트를 각각 신뢰도 평가하도록 시켰다.
- **핵심 발견**: 팩트체커 전원이 정통 단체를 정확히 식별한 반면, 역사학 박사급 교수는 50%만, 스탠퍼드 학부생은 20%만 정답을 맞혔다.
- **행동 차이**: 학부생·교수는 해당 웹페이지 안에 머물러 페이지 자체를 정독(**수직적 읽기, vertical reading**)한 반면, 팩트체커는 페이지를 빠르게 훑은 뒤 곧바로 새 탭을 여러 개 열어 다른 출처에서 그 출처 자체의 신뢰도를 교차 확인(**수평적 읽기, lateral reading**)했다.

**시사점**: 전문성(역사학 박사)이 웹 정보 신뢰도 판별 능력을 보장하지 않는다 — 오히려 **"페이지를 벗어나 검증하는 절차"** 자체가 결정적 변수였다.

Sources: [Stanford Report — "Fact-checkers outperform historians when evaluating online information"](https://news.stanford.edu/stories/2017/10/fact-checkers-outperform-historians-evaluating-online-information) *(원문 페이지 자체는 이번 조사에서 WebFetch 403으로 직접 열람 실패 — 검색 스니펫과 2차 인용을 통해 확인. 정확한 수치는 SHEG 공식 pdf로 재확인 권장, 미확인 표시)*, [UC Merced Library — SIFT Method](https://libguides.ucmerced.edu/news/evaluation/sift-method)

### 2-3. CRAAP 테스트와의 비교

- **CRAAP** = Currency(최신성)·Relevance(관련성)·Authority(권위)·Accuracy(정확성)·Purpose(목적). Sarah Blakeslee와 California State University, Chico 사서팀이 개발.
- **구조적 차이**: CRAAP은 **수직적(vertical) 읽기** — 하나의 출처를 그 페이지 안에서만 검사한다. SIFT/lateral reading은 **수평적** — 그 페이지를 떠나 다른 독립 출처로 교차 검증한다.
- **CRAAP의 알려진 한계**: 출처를 고립된 상태로 검사하기 때문에, 겉보기에 전문적이고 세련된 사이트가 표면적 기준(최신 날짜, 그럴듯한 저자 소개, 매끄러운 문체)은 잘 통과하면서도 내용은 오도적일 수 있다 — SHEG 실험에서 위장 단체 사이트가 정확히 이 함정이었다.
- **현재 정보 리터러시 실무 권고**: CRAAP을 완전히 버리기보다 **CRAAP(1차 스크리닝) + Lateral reading/SIFT(교차검증)를 병행**하는 것이 다수 사서 가이드의 결론.

Sources: [Wikipedia — CRAAP test](https://en.wikipedia.org/wiki/CRAAP_test), [Texas A&M-CC — CRAAP Test guide](https://guides.library.tamucc.edu/craap-test)

---

## 3. 삼각검증(Triangulation) vs 순환보고(Circular Reporting)

- **삼각검증(source triangulation)**: 하나의 사실을 **서로 독립적으로 정보를 획득한** 복수 출처로 교차 확인하는 것. 독립적 관점을 대조함으로써 사실을 확증하고 편향을 식별.
- **순환보고(circular reporting, false confirmation)**: 어떤 정보가 겉보기엔 여러 독립 출처에서 나온 것처럼 보이지만, 실제로는 단 하나의 원출처에서 파생된 것. 원인은 두 가지:
  - **의도치 않은 경우**: 부주의한 취재·정보수집 과정에서, 정보가 여러 채널을 거치며 서로를 인용하다가 우연히 다중 확증처럼 보이게 됨.
  - **의도적인 경우**: 출처나 보도자가 신뢰도를 인위적으로 부풀리기 위해 같은 정보를 여러 매체에 걸쳐 의도적으로 증폭.
- **판별 실패 사례**:
  - **이라크 전쟁 정보(니제르 우라늄 위조 문건)**: 이탈리아 군사정보국이 최초 유포한 문건이 여러 기관에 인용되며 확산됐지만, 생물무기 관련 평가의 "98%"가 단 한 명의 정보원(미국이 직접 인터뷰하지 않은)에서 나온 것으로 드러났다.
  - **위키피디아 인용순환(citogenesis)**: 위키피디아에 삽입된 근거 없는 주장이 뉴스 매체에 인용되고, 그 뉴스 기사가 다시 위키피디아의 "출처"로 재인용되며 자기강화 순환이 형성.
  - **Alex Haley의 『Roots』(1976)**: 감비아 구전 전승자(griot)가 "독립적으로" Haley의 조상 이야기를 확증한 것처럼 보였으나, 실제로는 Haley 본인이 사전에 들려준 이야기를 그대로 되풀이한 것이었다.
- **진짜 삼각검증과의 구분 기준**: 여러 출처가 **서로의 존재를 모른 채, 서로 다른 시점·경로·방법으로 독립적으로** 같은 결론에 도달했는가. "세 기사가 같은 사실을 보도한다"는 것 자체는 증거가 아니며, **각 기사의 취재원 계보(who talked to whom, first)를 거슬러 올라가** 그것이 하나의 원출처(정부 발표, 하나의 문서, 한 명의 정보원)로 수렴하는지 확인해야 한다.

Sources: [Wikipedia — Circular reporting](https://en.wikipedia.org/wiki/Circular_reporting), [Online Journalism Blog — "How 'triangulating' can help you identify more sources"](https://onlinejournalismblog.com/2023/01/19/how-triangulating-can-help-you-identify-more-sources/)

---

## 4. 체계적 문헌고찰 방법론 — PRISMA, GRADE, Cochrane RoB

### 4-1. PRISMA (Preferred Reporting Items for Systematic reviews and Meta-Analyses)

- 최신판은 **PRISMA 2020**(27개 항목 체크리스트 + 흐름도), 검색 전용 확장인 **PRISMA-S**가 있음.
- **흐름도(flow diagram)의 4단계**: **Identification(식별)** → **Screening(스크리닝)** → **Eligibility(적격성)** → **Included(포함)**. 각 단계마다 발견된 기록 수, 제외된 수, 그리고 **제외 사유**를 숫자로 명시한다.
- **재현성을 만드는 방식**: 모든 필터링 단계(검색→중복제거→제목/초록 스크리닝→전문 검토→최종 포함)를 사유와 함께 숫자로 기록하도록 강제함으로써, 독자나 다른 연구자가 **동일한 절차를 재구성하고, 왜 특정 논문이 빠졌는지 검증**할 수 있게 만든다. 즉 "감사 추적(audit trail)"이 리뷰 자체의 구조로 내장되어 있다.

Sources: [PRISMA 2020 flow diagram — 공식 statement](https://www.prisma-statement.org/prisma-2020-flow-diagram), [PRISMA 2020 explanation and elaboration, PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC8005925/)

### 4-2. GRADE (Grading of Recommendations Assessment, Development and Evaluation)

- 증거 확실성(certainty of evidence)을 **high / moderate / low / very low** 4단계로 평가.
- RCT는 기본적으로 high에서 시작, 관찰연구는 low에서 시작.
- **5개 강등(downgrade) 도메인**:
  1. **Risk of bias** — 연구 설계·수행상의 방법론적 결함
  2. **Inconsistency** — 연구들 간 결과의 이질성
  3. **Indirectness** — 임상 질문과 실제 근거 사이의 간접성(다른 인구·중재·비교군·결과지표)
  4. **Imprecision** — 넓은 신뢰구간 등 효과추정치의 불확실성
  5. **Publication bias** — 출판된 연구와 미출판 연구 간 체계적 차이
- (강등 외에 3개 격상(upgrade) 사유도 존재하나 이번 조사에서 세부 항목까지는 확인하지 않음 — 미확인)

Sources: [Cochrane Handbook Chapter 14 — GRADE](https://www.cochrane.org/authors/handbooks-and-manuals/handbook/current/chapter-14), [GRADE handbook (gradepro.org)](https://gradepro.org/handbook/), [CDC ACIP GRADE Handbook Ch.7](https://www.cdc.gov/acip-grade-handbook/hcp/chapter-7-grade-criteria-determining-certainty-of-evidence/index.html)

### 4-3. Cochrane Risk of Bias (RoB 2)

- 무작위 대조군 시험(RCT)에 대한 Cochrane 권장 도구, 2019년 개정판(RoB 2).
- **5개 편향 도메인**: (1) 무작위 배정 과정(randomization process), (2) 의도된 중재로부터의 이탈(deviations from intended interventions), (3) 결측 결과 데이터(missing outcome data), (4) 결과 측정(measurement of the outcome), (5) 보고된 결과의 선택(selection of the reported result).
- 각 도메인은 세부 "신호 질문(signalling questions)"에 대한 답을 바탕으로 알고리즘적으로 **Low / Some concerns / High** risk 판정을 도출.

**PRISMA+GRADE+RoB가 "재현성"을 만드는 공통 원리**: 사람의 주관적 종합 판단("이 문헌은 신뢰할 만하다")을 **명시적·구조화된 하위 판정 단위**로 쪼갠 뒤, 각 판정에 대해 누가 봐도 재현 가능한 근거(신호 질문 답변, 강등 사유, 제외 사유)를 남긴다. 결과가 아니라 **판정에 이르는 절차 자체를 감사 가능하게** 만드는 것이 핵심.

Sources: [Cochrane Methods — RoB 2](https://methods.cochrane.org/bias/resources/rob-2-revised-cochrane-risk-bias-tool-randomized-trials), [RoB 2 개정 논문, PubMed](https://pubmed.ncbi.nlm.nih.gov/31462531/)

---

## 5. 정보/인텔리전스 분석 규율

### 5-1. NATO Admiralty Code (STANAG 2511 계열 / "6×6 시스템")

제2차 세계대전 당시 영국 해군정보부(British Admiralty Naval Intelligence Division)에서 개발, 현재 NATO 표준으로 사용. **출처 신뢰도**와 **정보 신빙성**을 별개의 두 축으로 평가한다.

**출처 신뢰도 (A~F)**
| 등급 | 의미 |
|---|---|
| A | 완전히 신뢰 가능 — 진위·신뢰성·능력에 의심 없음, 완전 신뢰의 이력 |
| B | 대체로 신뢰 가능 — 사소한 의심, 대부분 유효한 정보의 이력 |
| C | 어느 정도 신뢰 가능 — 의심은 있으나 과거 유효 정보 제공 이력 있음 |
| D | 대체로 신뢰 불가 — 상당한 의심 있으나 과거 유효 정보 제공 이력은 있음 |
| E | 신뢰 불가 — 진위·신뢰성·능력 결여, 무효 정보의 이력 |
| F | 판단 불가 — 평가할 근거 자체가 없음 |

**정보 신빙성 (1~6)**
| 등급 | 의미 |
|---|---|
| 1 | 다른 출처로 확증됨 — 독립적 출처로 확증, 그 자체로 논리적, 다른 정보와 일치 |
| 2 | 아마 사실 — 미확증이나 논리적이고 다른 정보와 일치 |
| 3 | 사실일 가능성 있음 — 미확증, 어느 정도 논리적, 일부 다른 정보와 일치 |
| 4 | 의심스러움 — 미확증, 가능은 하나 비논리적, 다른 정보 없음 |
| 5 | 개연성 낮음 — 미확증, 비논리적, 다른 정보와 모순 |
| 6 | 판단 불가 — 평가할 근거 자체가 없음 |

두 축을 조합해 표기(예: B2 = 대체로 신뢰 가능한 출처가 아마 사실인 정보를 제공, F6 = 검증되지 않은 출처의 검증 불가능한 정보). **핵심 통찰: "신뢰할 만한 출처"와 "그 출처가 이번에 제공한 특정 정보가 사실인가"는 별개의 질문**이며 두 축을 분리해 평가해야 한다는 것이 이 체계의 요점이다.

Source: [Wikipedia — Admiralty code](https://en.wikipedia.org/wiki/Admiralty_code) *(WWII 기원·NATO STANAG 세부 지정 번호는 Wikipedia 발췌본에서 확인 안 됨 — 2차 출처(SANS, Pangea Research)로만 교차 확인, 미확인 표시)*

### 5-2. Analysis of Competing Hypotheses (ACH)

- CIA 방법론 전문가 **Richards J. Heuer Jr.**가 1970년대 중후반 개발, 그의 저서 *Psychology of Intelligence Analysis*(CIA Center for the Study of Intelligence 발간) 8장에 수록.
- **핵심 원리**: 분석가가 흔히 빠지는 함정 — "머릿속에 가설 하나를 먼저 세우고 그것을 뒷받침하는 증거만 찾는" 확증편향(confirmation bias) — 을 막기 위해, **하나의 최유력 가설을 입증하는 대신 여러 경쟁 가설을 동시에 나열하고, 각 증거가 각 가설을 반증(disprove)하는지를 매트릭스로 점검**한다.
- **효과에 대한 연구 결과(중요, 과장 금지)**: ACH가 확증편향을 실제로 줄이는지에 대해서는 **혼재된 근거(mixed evidence)**가 있으며, 일부 연구는 오히려 ACH가 분석가 간 **판단 불일치와 오류를 늘릴 수 있다**고 보고했다(Dhami, *Applied Cognitive Psychology*, 2019). 즉 ACH는 표준적으로 가르쳐지는 구조적 분석기법이지만 "만능 편향 해독제"로 단정할 근거는 없다.

Sources: [Heuer, *Psychology of Intelligence Analysis* 원문 PDF (CIA CSI, Internet Archive 미러)](https://archive.org/details/PsychologyOfIntelligenceAnalysis), [Dhami 2019, Wiley Online Library — "The 'analysis of competing hypotheses' in intelligence analysis"](https://onlinelibrary.wiley.com/doi/full/10.1002/acp.3550)

### 5-3. 확증편향 방어의 일반 원칙

ACH의 설계 철학 자체가 방어 원칙을 보여준다: **선호 가설을 입증할 증거를 찾지 말고, 각 경쟁 가설을 반증할 증거를 찾아라.** 이는 §2의 SIFT("Find better coverage" — 하나의 프레이밍에 안주하지 않기)와도 원리적으로 동일하다: 결론을 먼저 정하고 증거를 그 결론에 꿰맞추는 방향이 아니라, 결론에 반하는 증거를 적극적으로 탐색하는 방향으로 조사 순서를 뒤집는 것.

---

## 6. 탐사보도의 출처 검증

- **2개 이상 독립 출처 원칙("two-source rule")**: 워싱턴포스트의 워터게이트 취재(Woodward & Bernstein)에서 유래한 것으로 널리 알려진 관행 — 단, **이 특정 명칭·기원의 귀속 자체는 최소 한 명의 前 워싱턴포스트 편집자에 의해 이의가 제기된 바 있다**(Oxford Reference는 이를 "three-source rule"로 다르게 소개하는 자료도 존재함을 언급) — 정확한 기원은 미확인으로 남긴다. 확실한 것은 **핵심 주장은 반드시 복수의 독립 출처로 확증한 뒤에만 보도한다**는 원칙 자체가 현대 탐사보도의 표준 관행으로 정착했다는 점.
- **on/off record 구분**: 워터게이트 취재원들은 보복을 우려해 상당 부분 off-the-record로 정보를 제공했고, 기자들은 코드네임 등으로 신원을 철저히 보호했다. 익명 취재원 의존은 당시에도 논란이 있었고, 이후 저널리즘은 익명 취재원 사용에 대해 더 엄격한 기준(예: 정보의 성격, 취재원의 동기 공개, 편집진 승인 등)을 발전시켜왔다.
- **문서 원본 확인**: 공공기록·리크 문서·내부고발 자료 등 "shoe-leather reporting"(발로 뛰는 취재)과 결합해, 취재원의 증언을 문서 원본과 대조하는 것이 표준 관행.
- **SPJ(Society of Professional Journalists) 윤리강령**: "정보를 공개하기 전 반드시 검증하라(verify information before releasing it)"고 명시. **1차 출처(사람·간행물·역사적 문서·기타 최초 기록물)를 가능한 한 사용**할 것을 요구하며, "속도나 매체 형식이 부정확성의 변명이 될 수 없다"고 규정. 다른 뉴스 출처에서 가져온 정보는 **독립적으로 재검증**해야 하며, 직접 취재하지 않은 정보는 반드시 출처를 명시(attribute)해야 한다. 정확성의 책임은 취재원이 아니라 **기자 본인**에게 있다.

Sources: [Journalism in Action — "Covering Watergate"](https://www.journalisminaction.org/case/watergate), [Global Investigative Journalism Network — Watergate case study](https://impact.gijn.org/case-studies/watergate-united-states/), [SPJ Code of Ethics](https://www.spj.org/spj-code-of-ethics/), [Oxford Reference — "Three-source rule"](https://www.oxfordreference.com/display/10.1093/acref/9780199646241.001.0001/acref-9780199646241-e-1372) *(2-source vs 3-source 정확한 기원은 자료 간 불일치 — 미확인)*

---

## 7. 에이전트가 따를 규칙 (체크리스트, 기계적 적용 목표)

위 6개 방법론에서 공통적으로 추출되는 원리를 리서치 에이전트가 매 조사마다 적용할 수 있는 규칙으로 증류한다.

1. **출처 등급을 명시하라 (§1)**: 모든 주장에 대해 그것이 1차/2차/3차 출처 중 무엇에서 나왔는지 표시한다. 2차·3차 출처의 주장은 가능하면 그것이 인용하는 1차 출처까지 추적해 대조한다.
2. **결론 내기 전에 멈춰라 (§2 Stop)**: 헤드라인·요약문만 보고 바로 인용하지 않는다. 감정적으로 강한 주장일수록 검증 우선순위를 높인다.
3. **출처 자체를 먼저 조사하라, 콘텐츠보다 먼저 (§2 Investigate the source)**: 새로운 도메인·기관·저자를 만나면 콘텐츠를 읽기 전에 그 주체의 정체·전문성·이해관계를 먼저 확인한다.
4. **페이지를 벗어나 교차 확인하라 (§2 Lateral reading, §2-3 CRAAP 대비)**: 출처 내부 정보(자기소개, "About" 페이지, 최신 날짜)만으로 신뢰도를 판단하지 않는다. 반드시 그 출처에 대한 **제3자의 독립적 평가**를 검색한다.
5. **클레임을 원 맥락까지 추적하라 (§2 Trace claims)**: 인용문·통계·이미지가 재인용을 거쳤다면, 원문·원 데이터·원본 이미지까지 거슬러 올라가 발췌 과정에서 왜곡이 없었는지 확인한다.
6. **"여러 출처"를 계보로 검증하라 — 순환보고를 걸러내라 (§3)**: 같은 사실을 보도하는 기사가 여럿이어도, 각 기사의 취재원을 추적해 그것들이 실제로 독립적 경로로 확증됐는지, 아니면 하나의 원출처(하나의 보도자료, 하나의 문서, 한 명의 정보원)로 수렴하는지 확인한다. 수렴하면 "출처 1개"로 취급한다.
7. **판정 절차를 감사 가능한 형태로 기록하라 (§4 PRISMA/GRADE)**: 몇 건을 검색했고, 몇 건을 스크리닝했고, 몇 건을 최종 근거로 채택했으며 나머지는 왜 제외했는지 숫자와 사유를 남긴다. 최종 결론뿐 아니라 "왜 이 출처는 버렸는가"도 기록에 남긴다.
8. **증거의 확실성을 단일 등급이 아니라 구조화된 하위 판정으로 쪼개라 (§4 GRADE/RoB)**: "신뢰할 만함/아님"으로 뭉뚱그리지 않고, 최소한 (a) 방법론적 결함 여부, (b) 다른 출처와의 일관성, (c) 질문과의 직접적 관련성, (d) 불확실성의 폭 을 개별적으로 짚은 뒤 종합한다.
9. **출처 신뢰도와 이번 정보의 사실 여부를 분리해서 평가하라 (§5 Admiralty Code)**: "평소 신뢰할 만한 출처"라는 것과 "이번에 이 출처가 준 이 특정 정보가 사실"이라는 것은 별개다. 두 축을 따로 표시한다.
10. **선호 결론이 아니라 경쟁 가설을 반증하는 방향으로 검색하라 (§5 ACH)**: 조사 초반에 세운 가설을 뒷받침하는 근거만 쌓지 말고, 그 가설에 반하는 근거를 적극적으로 찾아 배치한다. 단, ACH류 구조적 기법이 확증편향을 완전히 제거한다고 과신하지 않는다(효과에 대한 근거는 혼재).
11. **핵심 주장은 최소 2개의 독립 출처로 확증한 뒤에만 확정 서술하라 (§6)**: 확증에 실패하면 "미확인" 또는 "단일 출처 주장"으로 명시적으로 표시하고, 그것을 사실인 것처럼 서술하지 않는다.
12. **정확성의 책임을 스스로 진다 (§6 SPJ)**: 다른 출처에서 가져온 정보는 반드시 재검증하고 출처를 명시한다. 속도(빨리 답해야 한다는 압박)가 미검증 주장을 내놓는 변명이 될 수 없다.

---

## 조사 방법 메모

- 모든 항목은 WebSearch(다건) + WebFetch(가능한 경우 원문 직접 열람)로 확인. Stanford 원문(news.stanford.edu)은 WebFetch가 403으로 차단되어 검색 스니펫과 2차 인용으로만 확인 — 정확한 수치 재검증이 필요하면 SHEG 공식 발행물을 별도로 확인할 것.
- NATO Admiralty Code의 정확한 STANAG 문서 번호, 두 번째 항목(2-source vs 3-source rule)의 정확한 기원, GRADE의 3개 격상(upgrade) 사유 세부 항목은 이번 조사에서 확정하지 못해 본문에 미확인으로 표시했다.
