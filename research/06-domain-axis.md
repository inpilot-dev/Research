# "산업 도메인"은 research 에이전트의 유효한 축인가 — 근거 기반 판정

**조사 시점: 2026-09-01 (KST)**

**조사 방법**
- **A(API 가용성)**: 문서를 읽는 대신 **실제로 호출**했다. 아래 표의 HTTP 코드는 이 머신에서 `curl`로 직접 측정한 값이다. 인증 필요 여부는 "키 없이 호출했을 때 실제로 무엇이 돌아왔는가"로 판정했다.
- **C(선점자)**: GitHub REST API 실측(`stargazers_count`, `pushed_at`) + `gh search repos` + 레포 `contents` 트리 직접 파싱.
- **D(수요 신호)**: 선행 리포트 [01-skills-sh.md](01-skills-sh.md)의 skills.sh 설치수 실측치와 [03-claude-ecosystem.md](03-claude-ecosystem.md)의 marketplace.json 파싱 결과를 인용.
- 확인 못 한 것은 전부 §7에 모아 "미확인"으로 명시했다. 추정치를 사실처럼 쓰지 않았다.

---

## 1. 결론 먼저

### 판정: **"산업 도메인"은 유효한 축이지만, 당신이 생각하는 층위에서는 아니다.**

세 문장으로 줄이면:

1. **도메인은 "스킬"의 축이 아니라 "소스 어댑터"의 축이다.** 이 분야에서 가장 크고 가장 신뢰할 만한 세 개의 스킬 컬렉션(google-deepmind 2,809★ · nomadamas/k-skill 7,384★ · lingzhi227 301★)이 **전부 독립적으로 산업이 아닌 다른 축으로 쪼갰다.** 하나는 데이터 소스별, 하나는 소스별, 하나는 리서치 작업 단계별이다. **7개 산업으로 나눈 사례를 이 조사에서 하나도 찾지 못했다.**
2. **도메인이 진짜로 갈리는 지점은 "산업"이 아니라 "안정적 식별자가 있느냐"다.** DOI·PMID·NCT·CIK·특허번호가 있는 도메인은 인용 검증을 기계적으로 할 수 있고, 없는 도메인은 못 한다. 이 선이 7개 후보를 정확히 둘로 가른다 — 그리고 이 선은 [00-SUMMARY.md](00-SUMMARY.md)가 지목한 "인용 시점 검증"이라는 빈칸과 **정확히 같은 선**이다.
3. **도메인을 늘리는 비용은 실측된 상수가 아니라 폭탄이다.** 특허 도메인은 최근 18개월 사이 공식 API가 **두 번** 갈아엎어졌고, 오늘 기준 후속 호스트 두 개가 **DNS 해석조차 되지 않는다**(§6). 도메인 7개는 유지보수 표면 7개가 아니라, 서로 다른 기관의 서로 다른 폐기 일정 7개다.

### 그래서 뭘 하라는 것인가

**산업별 스킬 7개를 만들지 말 것.** 대신 2층으로 나눌 것:

```
[2층] 리서치 작업 스킬 (도메인 무관, 소수)   ← 여기가 당신의 제품
        verify-citations / snapshot-corpus / budget-guard
                    ↕  (소스 레지스트리 = 설정 데이터)
[1층] 소스 어댑터 (도메인별, 다수·얇음)      ← 여기는 데이터
        openalex / crossref / pubmed / ctgov / edgar / law.go.kr / dart …
```

도메인은 **1층의 설정 데이터**여야 한다. 근거는 §5에서 사례로 논증한다.

---

## 2. 한눈에 보기 — 7개 도메인 × 4축

| # | 도메인 | A. 무인증 1차 소스 | B. 안정 식별자 | C. 선점자 최강 | D. 수요 | **판정** |
|---|---|---|---|---|---|---|
| 1 | 학술/과학 논문 | ✅ **다수** (OpenAlex·Crossref·arXiv·S2·OpenAIRE 전부 200 OK) | ✅ DOI·arXiv ID·OpenAlex W-ID | Imbad0202 44,456★ / arxiv-mcp 3,099★ | 설치 6.1K (약함) | **중간** |
| 2 | 의학·생명과학 | ✅ **다수** (PubMed·ClinicalTrials v2·EuropePMC·openFDA 전부 200 OK) | ✅ **PMID·PMCID·NCT·DOI** | deepmind science-skills 2,809★ / nagomi 플러그인 | 미확인(개별 수치 없음) | **높음** |
| 3 | 법률 | ⚠️ **반쪽** (CourtListener 검색 200 / 상세 **401**, 한국 법령 **OC 필수**) | ✅ 사건번호·법령ID | chrisryugj/korean-law-mcp **2,539★** | k-skill 4.6K | **중간(한국) / 낮음(해외)** |
| 4 | 금융·기업실사 | ✅ **SEC EDGAR 무인증 200** / ❌ DART·data.go.kr 키 필수 | ✅ CIK·LEI·사업자번호 | sec-edgar-mcp 353★ / k-skill **7,384★** | competitor-profiling 67.7K (**최대**) | **높음** |
| 5 | 특허 | ❌ **전멸** (EPO OPS 403 / PatentsView·USPTO ODP **DNS 미해석** / KIPRIS 키 필수) | ✅ 출원·공개·등록번호 | riemannzeta 76★ (작음) | 미확인 | **낮음** |
| 6 | 시장·경쟁사 리서치 | ❌ **1차 소스라는 개념 자체가 없음** | ❌ **없음** | coreyhaines31 46,352★ | **67.7K~87K (최대)** | **낮음(전략적으로)** |
| 7 | 한국어 1차 소스 | ❌ 전부 키 필수 (법령 OC·DART·data.go.kr·KCI) | ✅ 사업자번호·법령ID·공시접수번호 | **nomadamas/k-skill 7,384★ (~120 스킬)** | 4.6K | **중간(단, 선점 완료)** |

> **읽는 법**: A와 B가 모두 ✅인데 C가 약한 칸이 진입 지점이다. 표에서 그런 칸은 **2번(의학) 하나뿐**이고, **4번(금융)이 절반쯤** 해당한다.

---

## 3. 도메인별 상세

### (1) 학술/과학 논문 — 판정: **중간**

**A. API 가용성 — 실측 (전부 무인증 성공)**

| 소스 | 호출 | 결과 | 인증 | 확인된 제약 |
|---|---|---|---|---|
| [OpenAlex](https://api.openalex.org) | `works?search=...` | **HTTP 200** | 불필요 | ⚠️ **아래 별도 설명** |
| [Crossref](https://api.crossref.org) | `works/10.1038/nature12373` | **HTTP 200** | 불필요 | polite pool |
| [arXiv](https://export.arxiv.org/api/query) | `search_query=all:...` | **HTTP 200** (http→https 301) | 불필요 | 미확인 |
| [Semantic Scholar](https://api.semanticscholar.org) | `graph/v1/paper/DOI:...` | **HTTP 200** | 불필요(키는 권장) | 미확인 |
| [OpenAIRE](https://api.openaire.eu) | `search/publications` | **HTTP 200** (XML) | 불필요 | 미확인 |
| [Unpaywall](https://api.unpaywall.org) | `v2/{doi}?email=` | **HTTP 200** | email 파라미터 필수 | — |

**🔴 이 조사에서 새로 관측한 사실 — OpenAlex가 과금 체계로 이동 중이다.**
무인증 호출의 응답 헤더를 그대로 옮기면:
```
x-ratelimit-limit: 1000          x-ratelimit-limit-usd: 0.1
x-ratelimit-cost-usd: 0.0001     x-ratelimit-prepaid-remaining-usd: 0
x-ratelimit-remaining: 988       x-ratelimit-reset: 67759   (≈18.8시간)
```
호출 1건 = 1 크레딧 = **$0.0001**, 무료 한도 1,000 크레딧 = **$0.10**/약 19시간. `prepaid-remaining-usd` 필드가 있다는 건 **선불 충전 경로가 이미 구현돼 있다**는 뜻이다. `mailto`를 붙여도 헤더가 동일해 polite pool 차등은 확인되지 않았다.
→ **"학술 API는 공짜"라는 전제 위에 도메인 스킬을 세우면 안 된다는 실측 증거.** (요금제 전문·향후 정책은 미확인)

**Crossref polite pool은 실측으로 확인됐다** — `mailto` 포함 시 `x-api-pool: polite-array`, 미포함 시 `x-api-pool: public-array`. 즉 연락처만 넣으면 별도 키 없이 우대 풀로 들어간다.

**B. 검증 가능성 — ✅ 최상급.** DOI가 있고, **DOI → Crossref/OpenAlex 왕복 조회가 무인증으로 되므로 "이 인용이 실존하는가"를 기계적으로 판정 가능**하다. 위 실측에서 `10.1038/nature12373` 하나로 Crossref·OpenAlex·S2·Unpaywall 4개 소스가 모두 같은 논문을 반환하는 것을 확인했다 → **교차검증까지 가능**한 유일급 도메인.

**C. 선점자 — 강함.**

| 프로젝트 | ★ | 최종 푸시 | 비고 |
|---|---:|---|---|
| [Imbad0202/academic-research-skills](https://github.com/Imbad0202/academic-research-skills) | **44,456** | 2026-08-30 | 라이선스 NOASSERTION ⚠️ |
| [blazickjp/arxiv-mcp-server](https://github.com/blazickjp/arxiv-mcp-server) | **3,099** | 2026-08-26 | arXiv 단독 강자 |
| [google-deepmind/science-skills](https://github.com/google-deepmind/science-skills) | 2,809 | 2026-07-07 | Apache-2.0 |
| [lingzhi227/agent-research-skills](https://github.com/lingzhi227/agent-research-skills) | 301 | 2026-02-27 | 31 스킬 |

**D. 수요 — 약하다.** 01번 리포트 실측: `literature` 1위 설치 6.1K, `arxiv` 1위 2.6K, `citation` 2위부터 1.8K, `zotero` 1위 1.3K. 반면 `research` 1위는 **417.7K**. **70배 차이**다. 게다가 Imbad0202는 **star 44K인데 설치 8.7K** — star는 붙는데 설치가 안 되는 전형.

> **판정 근거**: A·B는 만점인데 C가 44K★로 막혀 있고 D가 약하다. 정면 진입은 부적절. 단 §5의 2층 구조에서 **1층 어댑터로는 최우선 편입 대상**이다(검증 왕복이 무인증으로 되는 유일한 도메인이므로).

---

### (2) 의학·생명과학 — 판정: **높음**

**A. API 가용성 — 실측 (전부 무인증 성공)**

| 소스 | 결과 | 인증 | rate limit |
|---|---|---|---|
| [PubMed E-utilities](https://eutils.ncbi.nlm.nih.gov) | **HTTP 200** | 불필요 | **키 없이 3 req/s, 키 발급 시 10 req/s** ([NCBI 가이드라인 문서 확인](https://www.ncbi.nlm.nih.gov/books/NBK25497/)) |
| [ClinicalTrials.gov API v2](https://clinicaltrials.gov/api/v2/studies) | **HTTP 200** | 불필요 | 응답 헤더에 ratelimit 없음 → 문서상 한도 미확인 |
| [Europe PMC](https://www.ebi.ac.uk/europepmc/webservices/rest) | **HTTP 200** | 불필요 | 미확인 |
| [openFDA](https://api.fda.gov) | **HTTP 200** | 불필요(키는 상향) | 미확인 |

**B. 검증 가능성 — ✅ 이 조사에서 가장 강한 도메인.**
- **PMID / PMCID / NCT 번호 / DOI** 네 종류의 식별자가 동시에 존재하고 상호 참조된다.
- **결정적으로, 의학 도메인만 "인용 검증"을 넘어 "증거 등급"까지 기계화 가능하다.** 임상시험 등록번호(NCT)는 *사전등록*되므로 "논문이 주장하는 결과가 사전등록한 1차 결과지표와 일치하는가"를 대조할 수 있다. 이건 학술·법률·금융 어디에도 없는 구조다.
- 실제로 이 축을 잡은 플러그인이 이미 존재한다 — `nagomi`(PubMed 3,600만+, **PICO 구조 쿼리 + GRADE 신뢰도 등급 증거 합성**, [avivlyweb/nagomi-pubmed-plugin](https://github.com/avivlyweb/nagomi-pubmed-plugin), 03번 리포트 실측).

**C. 선점자 — 분산돼 있다(= 기회).**

| 프로젝트 | ★ | 최종 푸시 |
|---|---:|---|
| [google-deepmind/science-skills](https://github.com/google-deepmind/science-skills) | 2,809 | 2026-07-07 |
| [cyanheads/pubmed-mcp-server](https://github.com/cyanheads/pubmed-mcp-server) | 142 | 2026-08-21 |
| [Darkroaster/pubmearch](https://github.com/Darkroaster/pubmearch) | 149 | **2025-05-07 (정체)** |
| [JackKuo666/ClinicalTrials-MCP-Server](https://github.com/JackKuo666/ClinicalTrials-MCP-Server) | 16 | **2025-04-09 (정체)** |

**PubMed 최강자가 149★이고 그마저 16개월 정체다.** 학술(44K★)·법률(2.5K★)과 비교하면 이 도메인만 방어자가 비어 있다. ClinicalTrials 쪽은 최강이 16★로 사실상 무주공산.

**D. 수요 — 미확인.** 01번 리포트에 `pubmed`/`clinical` 단독 설치수 집계가 없다. 03번 리포트의 MCP 디렉터리 집계에서 `pubmed` 검색 결과 82건이 확인될 뿐 설치·다운로드 수치는 미확인. **A/B/C가 좋아도 D를 모른다는 점은 그대로 리스크다.**

> **판정 근거**: 무인증 API 4종 + 식별자 4종 + 사전등록 대조라는 도메인 고유 검증 구조 + 최강 선점자 149★. **"인용 검증" 제품과 도메인이 가장 잘 맞고 방어자가 가장 약한 칸.**

---

### (3) 법률 — 판정: **중간(한국) / 낮음(해외)**

**A. API 가용성 — 반쪽짜리. 실측이 문서보다 정확했다.**

| 소스 | 호출 | 결과 |
|---|---|---|
| [CourtListener v4](https://www.courtlistener.com/api/rest/v4/) | `search/?q=copyright&type=o` | **HTTP 200** (36,636건, 무인증 성공) |
| CourtListener v4 | `opinions/?id=...` | **HTTP 401** `{"detail":"Authentication credentials were not provided."}` |
| [국가법령정보 DRF](https://www.law.go.kr/DRF/lawSearch.do) | `target=law&query=개인정보` | HTTP 200이지만 본문은 **`"필수 입력값이 존재하지 않습니다"`** → `OC`(신청자 ID) 필수 |
| [case.law 정적 벌크](https://static.case.law/) | 루트 | **HTTP 200** (Caselaw Access Project 정적 덤프 생존) |

> **⚠️ 여기가 도메인 스킬을 만들 때 가장 잘 밟는 지뢰다.** CourtListener는 **검색은 무인증으로 되는데 상세 조회는 401**이다. "무인증으로 되네"라고 판단하고 어댑터를 짜면 **인용 검증 단계(= 본문 대조)에서만 정확히 깨진다.** 검증이 목적인 제품에는 치명적이다. 문서만 읽고는 절대 못 잡는 종류의 함정이라 §5의 "어댑터는 얇게, 검증은 두껍게" 논거가 된다.

**B. 검증 가능성 — ✅ 있지만 인증 벽 뒤에 있다.** 사건번호·법령ID·조문번호는 안정적이다. 다만 위 401 때문에 **"판례가 실존하는가"는 무인증으로 되고 "그 판례가 실제로 그 내용인가"는 안 된다.** 미국 법률 LLM 환각률이 모델·심급에 따라 58~88%라는 보고([02번 리포트가 인용한 문헌](https://arxiv.org/html/2604.03173v1))가 있는 만큼 검증 수요 자체는 가장 크다.

**C. 선점자 — 한국은 이미 강자가 있다.**

| 프로젝트 | ★ | 최종 푸시 | 비고 |
|---|---:|---|---|
| [chrisryugj/korean-law-mcp](https://github.com/chrisryugj/korean-law-mcp) | **2,539** | 2026-08-29 | 설명에 **"법령·판례·조례 검색과 인용 검증"** 명시 |
| [SeoNaRu/korean-law-mcp](https://github.com/SeoNaRu/korean-law-mcp) | 73 | 2026-01-20 | |
| [paulieb89/uk-legal-mcp](https://github.com/paulieb89/uk-legal-mcp) | 13 | 2026-08-27 | |
| [moonlit-ai/legal-research-mcp](https://github.com/moonlit-ai/legal-research-mcp) | 0 | 2026-08-12 | 유럽법 20M+ 주장 |

**🔴 주목**: 2,539★짜리 `korean-law-mcp`가 스스로를 **"인용 검증"**으로 포지셔닝한다. 당신이 노리는 빈칸에 이미 한국 법률 도메인 한정으로 들어온 사람이 있다. 게다가 당신이 설치해 쓰는 `korean-law-search` 스킬의 SKILL.md가 **"설계는 chrisryugj/korean-law-mcp의 read-only 도구 표면을 참고했다"**고 직접 밝히고 있다 — 이미 아는 선점자다.

**D. 수요 — 약함.** `korean` 축 전체가 설치 5K 이하, `nomadamas/k-skill@korean-law-search`가 4.6K로 상위(01번 실측). 해외 법률은 별도 수치 미확인.

---

### (4) 금융·기업실사 — 판정: **높음(단, 미국 한정)**

**A. API 가용성 — 극단적으로 갈린다.**

| 소스 | 결과 | 인증 |
|---|---|---|
| [SEC EDGAR submissions](https://data.sec.gov/submissions/CIK0000320193.json) | **HTTP 200 (164KB)** | **불필요** |
| [SEC company_tickers](https://www.sec.gov/files/company_tickers.json) | **HTTP 200 (795KB)** | **불필요** — 전체 상장사 CIK↔티커 매핑 한 방에 |
| [GLEIF LEI](https://api.gleif.org/api/v1/lei-records) | **HTTP 200** | **불필요** (골든카피 2026-08-31 갱신 확인) |
| [Wikidata](https://www.wikidata.org/w/api.php) | **HTTP 200** | 불필요 |
| [DART OpenAPI](https://opendart.fss.or.kr/api/list.json) | 키 없으면 **HTML 에러 페이지** | 키 필수 |
| [data.go.kr 국세청 사업자상태](https://api.odcloud.kr) | **HTTP 401** `{"code":-4,"msg":"등록되지 않은 인증키 입니다."}` | 키 필수 |
| [OpenCorporates](https://api.opencorporates.com) | **HTTP 401** | 키 필수(유료) |
| [Companies House(영국)](https://api.company-information.service.gov.uk) | **HTTP 401** `{"error":"Empty Authorization header"}` | 키 필수(무료 발급) |

SEC EDGAR 정책은 **키 불필요 + User-Agent 신고 + 10 req/s** ([SEC Accessing EDGAR Data](https://www.sec.gov/search-filings/edgar-search-assistance/accessing-edgar-data)). 실측에서도 커스텀 UA로 전부 200이 떨어졌다.

**B. 검증 가능성 — ✅ 강함.** CIK(미국) · LEI(글로벌) · 사업자등록번호/법인등록번호(한국) · 공시 접수번호. **공시 원문 자체가 1차 소스이므로 "인용한 숫자가 10-K 어느 항목에서 왔는가"를 원문 대조 가능**하다.
- 단, 한국 쪽 함정을 당신 스킬이 이미 문서화해 뒀다: `fsc-corporate-info` SKILL.md가 **"`crno`(법인등록번호)는 사업자등록번호와 별개 번호임을 혼동하지 않는다"**, **"이 API는 사업자번호 단독 조회가 불가"**라고 명시한다. **식별자가 있다 ≠ 식별자가 하나다.** 도메인마다 식별자 매핑 지식이 따로 필요하다는 실증.

**C. 선점자 — 미국 쪽은 의외로 얇다.**

| 프로젝트 | ★ | 최종 푸시 |
|---|---:|---|
| [stefanoamorelli/sec-edgar-mcp](https://github.com/stefanoamorelli/sec-edgar-mcp) | **353** | 2026-08-21 |
| [nomadamas/k-skill](https://github.com/nomadamas/k-skill) | **7,384** | 2026-08-29 |
| `credit-memo` 플러그인 (SEC EDGAR + SerpApi 재무 자동수집) | 마켓 등재 | 소스 URL 미확인 |

**SEC EDGAR 최강 MCP가 353★.** 데이터가 완전 무료·무인증·구조화(XBRL)돼 있는데도 이 정도다.

**D. 수요 — 이 조사 전체에서 최대.** `coreyhaines31/marketingskills@competitor-profiling` **67.7K 설치**, 같은 저장소 `customer-research` **87K**(01번 실측). 학술(6.1K)의 **10~14배**.

> **판정 근거**: 무인증 1차 소스(EDGAR·GLEIF) + 강한 식별자 + 원문 대조 가능 + 최강 선점자 353★ + 최대 수요. **다만 이 수요는 §3-(6)에서 보듯 "실사"가 아니라 "마케팅 리서치"에 몰려 있어, 수치를 그대로 자기 수요로 읽으면 안 된다.**

---

### (5) 특허 — 판정: **낮음 (A가 무너졌다)**

**A. API 가용성 — 실측 결과가 참담하다.**

| 소스 | 호출 결과 |
|---|---|
| [EPO OPS](https://ops.epo.org/3.2/rest-services/) | **HTTP 403** — `This request has been rejected due to the violation of Fair Use policy` (OAuth 필수) |
| `api.patentsview.org` (레거시) | API가 아니라 **HTML SPA 반환** — 사실상 폐기 확인 |
| `search.patentsview.org` (PatentSearch API) | **DNS A 레코드 없음** — 로컬·8.8.8.8·1.1.1.1 **세 리졸버 모두 빈 응답** |
| `api.data.uspto.gov` (USPTO ODP) | **DNS A 레코드 없음** — 동일하게 세 리졸버 모두 빈 응답 |
| `developer.uspto.gov` | HTTP 301 (정상 해석) → 위 두 건은 로컬 네트워크 문제가 아님 |
| [KIPRIS Plus](http://plus.kipris.or.kr) | **HTTP 404** (엔드포인트 경로 변경 추정) + 키 필수 |

> **정직한 단서**: 두 호스트가 DNS에서 사라진 것은 실측이지만, **그것이 서비스 종료 때문인지 호스트명 변경 때문인지는 미확인.** 다만 어느 쪽이든 결론은 같다 — **오늘 문서를 보고 짠 특허 어댑터는 오늘 안 돈다.**

**공식 발표 이력** (문서 확인):
- 레거시 PatentsView API: 2025-05-01부터 **410 Gone** ([PatentsView 공지](https://patentsview.org/data-in-action/patentsview-ends-support-legacy-api))
- PatentSearch API로 이관 + **API 키 필수화**
- 그 PatentSearch API도 **2026-03-20 data.uspto.gov로 재이관** 예고
- PTAB API v2는 **2026-01-06 폐기** ([USPTO 공지](https://developer.uspto.gov/node/165448))
- R 생태계에서도 `patentsview` 패키지가 **breaking release**를 냈다 ([rOpenSci, 2026-03](https://ropensci.org/blog/2026/03/10/patentsview-breaking-release/))

**B. 검증 가능성 — ✅ 식별자는 최상급.** 출원번호·공개번호·등록번호·INPADOC 패밀리 ID까지 있다. **B는 만점인데 A가 0점이라 못 쓴다** — 7개 후보 중 유일하게 이 조합이다.

**C. 선점자 — 얇다.** [riemannzeta/patent_mcp_server](https://github.com/riemannzeta/patent_mcp_server) 76★(2026-08-23) / [handaas/patent-mcp-server](https://github.com/handaas/patent-mcp-server) 28★ / `fluidityiq-patent-intelligence` 플러그인(자사 MCP 경유, 소스 미확인). **선점자가 얇은 게 기회가 아니라 A가 무너져서 아무도 못 버틴 결과로 읽어야 한다.**

**D. 수요 — 미확인.** skills.sh `patent` 단독 집계 없음. `yuan1z0825/nature-skills@nature-paper-to-patent` 6.6K가 간접 신호이나 이건 학술→특허 변환이지 특허 검색이 아니다.

---

### (6) 시장·경쟁사 리서치 — 판정: **낮음 (전략적으로. 수요는 최대인데)**

**A. 1차 소스 — 없다. "없다"가 이 도메인의 정의다.**
"시장 규모", "경쟁사 포지셔닝", "TAM"에 대응하는 **권위 있는 1차 소스가 존재하지 않는다.** 대체 가능한 것은 두 종류뿐이고 둘 다 성격이 다르다:
- **기업 실체 데이터**(GLEIF 200 OK, SEC EDGAR 200 OK, Wikidata 200 OK) — 이건 §3-(4) 실사 도메인이지 시장 리서치가 아니다.
- **일반 웹 검색** — Tavily/Serper/Firecrawl 유료 API. 즉 **이 도메인의 "1차 소스"는 남의 유료 검색 API다.**

**B. 검증 가능성 — ❌ 없다. 이게 결정타다.**
"삼성의 파운드리 점유율이 몇 %인가"에는 **DOI가 없다.** 대조할 정본이 없으므로 **인용 시점 검증이라는 당신의 핵심 제품 기능이 원리적으로 작동하지 않는다.** 붙일 수 있는 건 "이 URL에 이런 문장이 있었다"는 스냅샷뿐이고, 그건 검증이 아니라 아카이빙이다.

**C. 선점자 — 압도적.** [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills) **46,352★**, 2026-08-28 푸시, MIT. `competitor-profiling` 67.7K · `customer-research` 87K 설치. [firecrawl/firecrawl-workflows@firecrawl-market-research](https://skills.sh/firecrawl/firecrawl-workflows/firecrawl-market-research) 31.8K, [apify/agent-skills@apify-market-research](https://skills.sh/apify/agent-skills/apify-market-research) 3.4K.

**D. 수요 — 조사 전체 최대(87K).**

> **판정 근거**: **D가 최대인데 B가 0이라 낮음으로 내린다.** 이 도메인에 들어가면 당신은 "검증하는 리서처"가 아니라 "검색해서 요약하는 리서처"가 되고, 그건 [00-SUMMARY](00-SUMMARY.md)가 "이미 죽은 땅"이라고 결론 낸 바로 그 자리다. **수요 숫자에 끌려 여기로 가는 것이 이 조사에서 가장 큰 함정이다.**

---

### (7) 한국어 1차 소스 — 판정: **중간 (선점 완료 — 그리고 그 선점자가 당신이 이미 쓰는 도구다)**

**A. API 가용성 — 전부 키 필수. 예외 없음.**

| 소스 | 실측 |
|---|---|
| 국가법령정보 DRF | `OC` 필수 (본문에 "필수 입력값이 존재하지 않습니다") |
| DART OpenAPI | 키 없으면 HTML 에러 |
| data.go.kr (odcloud) | **HTTP 401** `{"code":-4,"msg":"등록되지 않은 인증키 입니다."}` |
| KCI OpenAPI | HTTP 200이나 XML 응답에 `key` 검증 결과 반환 → 키 필수 |
| KIPRIS Plus | HTTP 404 + 키 필수 |
| RISS | **공개 REST API 없음** — HTML만 반환. 스크레이핑 경로 |

**한국 도메인의 구조적 특징: 무인증 공개 REST가 사실상 0이다.** 이건 미국(EDGAR·PubMed·ClinicalTrials 전부 무인증)과 정반대다.

**이 문제를 실제로 푼 방식이 이미 존재한다** — 당신이 설치해 쓰는 `korean-law-search`·`fsc-corporate-info` 스킬 문서에 답이 적혀 있다: **`k-skill-proxy` 서버가 키를 대신 들고 있어서 사용자는 키가 필요 없다.** (`"LAW_OC와 브라우저 User-Agent/Referer 주입은 proxy 서버에서만 처리한다"`)
- **장점**: 도메인 7개 × 키 7개 발급이라는 온보딩 지옥을 없앤다.
- **비용**: 프록시가 단일 장애점이 되고, 서버 운영·키 갱신·쿼터 책임을 제작자가 진다.
- **반례도 같은 저장소 안에 있다**: `k-dart`는 **프록시를 안 거치고** 사용자 `API_K_DART` 환경변수를 직접 쓴다. 즉 **한 컬렉션 안에서도 소스마다 인증 전략이 다르다** — 이게 도메인 어댑터층이 얇아야 하는 이유다.

**B. 검증 가능성 — ✅ 있다.** 사업자등록번호·법인등록번호·법령ID·DART 접수번호. 단 §3-(4)에서 봤듯 번호 종류가 여러 개이고 상호 변환이 안 되는 구간이 있다.

**C. 선점자 — 사실상 끝났다.**
[nomadamas/k-skill](https://github.com/nomadamas/k-skill) **7,384★, MIT, 2026-03-24 생성, 2026-08-29 푸시.** 레포 트리 실측 결과 **약 120개 스킬**을 보유하고, 당신이 후보로 꼽은 축을 이미 전부 덮었다:

| 당신의 후보 | k-skill의 기존 스킬 |
|---|---|
| 법령·판례 | `korean-law-search` |
| DART | `k-dart` |
| 공공데이터 | `fsc-corporate-info`, `national-pension-workplace`, `nts-business-registration`, `nts-tax-delinquency`, `localdata-business-status`, `g2b-sanctioned-supplier`, `kosis-stats`, `bok-ecos-stats` … |
| KCI/RISS | **`keris-academic-search`** (KERIS RISS 대상) |
| 특허 | **`korean-patent-search`** (KIPRIS Plus) |

**D. 수요 — 약함.** `korean` 축 전체 설치 5K 이하, `nomadamas/k-skill@korean-law-search`가 4.6K로 상위(01번 실측). 7,384★ vs 4.6K 설치 — 여기도 star≫설치.

---

## 4. 핵심 질문에 답한다 — 도메인은 "스킬"인가 "소스 어댑터/설정"인가

### 답: **소스 어댑터/설정 데이터다.** 근거는 사례 세 건이 독립적으로 같은 답을 냈다는 것이다.

#### 증거 ①: Google DeepMind는 산업으로 나누지 않았다 — 소스로 나눴다

[google-deepmind/science-skills](https://github.com/google-deepmind/science-skills)(2,809★, Apache-2.0)의 `skills/` 트리를 실측한 전체 목록:

```
alphafold_database_fetch_and_analyze  alphagenome_single_variant_analysis  chembl_database
clinical_trials_database  clinvar_database  dbsnp_database  embl_ebi_ols  encode_ccres_database
ensembl_database  foldseek_structural_search  gnomad_database  gtex_database
human_protein_atlas_database  interpro_database  jaspar_database
literature_search_arxiv  literature_search_biorxiv  literature_search_europepmc  literature_search_openalex
ncbi_sequence_fetch  openfda_database  opentargets_database  pdb_database  protein_sequence_msa
protein_sequence_similarity_search  pubchem_database  pubmed_database  quickgo_database
reactome_database  string_database  ucsc_conservation_and_tfbs  unibind_database  uniprot_database
predictingthepast  pymol  credentials  uv  workflow_skill_creator
```

**37개 중 30개가 `<소스명>_database` 또는 `literature_search_<소스명>`이다.** 산업·학문분야로 이름 붙은 스킬은 **0개**다. 심지어 "문헌 검색"조차 하나로 안 묶고 **arxiv / biorxiv / europepmc / openalex 4개로 소스별 분리**했다. 그리고 공통 관심사(`credentials`, `uv`, `workflow_skill_creator`)는 **별도 스킬로 뽑았다.**
→ **이게 정확히 §1의 2층 구조다.** 세계 최고 수준의 연구조직이 같은 문제를 풀면서 도달한 구조.

#### 증거 ②: 당신이 이미 쓰는 k-skill도 소스로 나눴다 — 그리고 그 위에 "복합 스킬"을 얹었다

`nomadamas/k-skill` 약 120개 스킬 중 대부분이 `<기관/서비스>-<동작>` 형태의 **1소스 1스킬**이다(`nts-tax-delinquency`, `national-pension-workplace`, `kosis-stats`, `bok-ecos-stats`, `localdata-business-status` …).

그리고 그 위에 **소수의 복합 스킬**이 얹혀 있다 — `biz-health-check`, `store-longevity-radar`, `corporate-registration-consulting`, `court-payment-order-assistant`.

`biz-health-check`의 SKILL.md가 이 아키텍처를 자기 입으로 설명한다:

> **"같은 레포의 단품 스킬 helper를 그대로 재사용한다(단일 진실원천)."**
> "한 항목 조회가 실패해도 전체를 막지 않고 그 항목만 정직하게 강등한다(`unavailable` + 사유)."
> "단품 helper를 찾지 못하면 해당 섹션만 건너뛰고 나머지를 진행한다."

**이게 결정적이다.** `biz-health-check`는 "기업실사"라는 도메인 스킬처럼 보이지만, 실제로는 **6개 소스 어댑터를 호출하는 오케스트레이터**이고, **어댑터 하나가 죽어도 자기는 안 죽도록** 설계돼 있다. 도메인 지식은 "어떤 소스를 어떤 순서로 묶는가"에만 들어 있고, API 호출 지식은 전부 1층에 있다.
→ **도메인 = 소스 조합 레시피.** 스킬이 아니라 설정에 가깝다는 것을 코드 구조가 증명한다.

#### 증거 ③: 학술 특화 컬렉션들은 "작업 단계"로 나눴다 — 역시 산업이 아니다

- [lingzhi227/agent-research-skills](https://github.com/lingzhi227/agent-research-skills) 31개: `literature-search`, `citation-management`, `novelty-assessment`, `experiment-design`, `rebuttal-writing`, `related-work-writing` … → **리서치 워크플로 단계별**
- [Imbad0202/academic-research-skills](https://github.com/Imbad0202/academic-research-skills) 44,456★인데 `skills/` 안에는 **단 4개**: `academic-paper`, `academic-paper-reviewer`, `academic-pipeline`, `deep-research` → **한 도메인 안에서 역할별**

**7개 산업으로 나눈 상위 컬렉션을 이 조사에서 하나도 찾지 못했다.**

### 왜 그런가 — 구조적 이유 3가지

1. **도메인 지식의 대부분은 "어느 API를 어떻게 부르는가"이고, 그건 코드지 프롬프트가 아니다.** SKILL.md에 담을 만한 진짜 도메인 지식은 놀랄 만큼 적다. `fsc-corporate-info`의 도메인 지식은 사실상 문장 두 개다 — "`crno`≠사업자번호", "사업자번호 단독 조회 불가". 이걸 위해 스킬 하나를 세우는 건 낭비고, 어댑터의 주석/스키마에 있으면 된다.
2. **검증 로직은 도메인을 넘어 동일하다.** "식별자를 뽑아 → 정본 API에 되물어 → 원문과 주장을 대조"는 DOI든 NCT든 CIK든 절차가 같다. **도메인마다 스킬을 나누면 이 공통 로직이 N번 복제되고, N번 따로 썩는다.**
3. **스킬 발견은 이름 부분일치로 일어난다**(01번 리포트 실측: `research` 417.7K > `deep-research` 33.5K > `literature-review` 5.3K, 이름이 짧고 일반적일수록 상위). **도메인 스킬 7개는 검색 노출을 7조각으로 쪼갠다.** 각 조각이 이미 그 도메인 선점자(44K★·2.5K★·46K★)와 정면 경쟁하게 된다 — 최악의 배분이다.

### 단, "그래서 도메인 스킬은 전부 무의미하다"는 아니다 — 예외 조건

`biz-health-check`가 살아있는 스킬인 이유는 **어댑터 호출 순서와 실패 강등 규칙이라는, 어댑터에는 담을 수 없는 판단**을 담기 때문이다. 도메인이 별도 스킬이 될 자격은 다음을 만족할 때뿐이다:

> **"이 도메인에는, 소스를 여러 개 묶는 순서/교차검증 규칙/실패 처리 방침이 있고, 그것이 다른 도메인과 다르다."**

의학의 **NCT 사전등록 ↔ 논문 결과 대조**가 정확히 이 조건을 만족한다. 시장·경쟁사 리서치는 만족하지 않는다(묶을 정본이 없으므로).

---

## 5. 도메인을 늘릴 때의 유지보수 비용 — 실증

### 실증 ① 특허: 18개월에 두 번 갈아엎어졌고, 지금은 호스트가 사라졌다

| 시점 | 사건 |
|---|---|
| 2024-09 | PatentsView 레거시 API 폐기 절차 시작 |
| 2025-05-01 | 레거시 `api.patentsview.org` → **410 Gone** ([공지](https://patentsview.org/data-in-action/patentsview-ends-support-legacy-api)) |
| — | 후속 PatentSearch API는 **API 키 필수화** (무인증 시대 종료) |
| 2026-01-06 | USPTO **PTAB API v2 폐기** ([공지](https://developer.uspto.gov/node/165448)) |
| 2026-03-10 | R `patentsview` 패키지 **breaking release** ([rOpenSci](https://ropensci.org/blog/2026/03/10/patentsview-breaking-release/)) |
| 2026-03-20 | PatentSearch API → `data.uspto.gov` 재이관 예고 |
| **2026-09-01 (실측)** | `search.patentsview.org`·`api.data.uspto.gov` **둘 다 DNS A 레코드 없음** (8.8.8.8/1.1.1.1 동일). `api.patentsview.org`는 HTML SPA 반환 |

**한 도메인이 18개월 만에 "무인증 공개 API" → "키 필수" → "다른 기관으로 이관" → "오늘 기준 해석 불가"를 거쳤다.** 특허 어댑터를 쓴 사람은 이 기간에 최소 3번 코드를 고쳐야 했다.

### 실증 ② 의학: 조용히 깨지는 종류의 변경

ClinicalTrials.gov classic API는 **2024-06-25 폐기**되고 v2로 이관됐다([NLM Technical Bulletin](https://www.nlm.nih.gov/pubs/techbull/ma24/ma24_clinicaltrials_api.html)). 변경 성격이 특히 나쁘다 — base URL·페이지네이션 모델(`min_rnk`/`max_rnk` → 토큰)·필터 문법이 전부 바뀌었고, 일부 필드는 **자유 텍스트에서 열거형으로 데이터 타입이 바뀌었다**. 즉 **v1 기준 코드가 v2에서 예외를 던지지 않고 조용히 틀린 결과를 낸다.**
→ **리서치 도구에서 가장 나쁜 실패 모드다.** 에이전트는 빈 결과를 "근거 없음"으로 보고하고, 사용자는 그게 버그인지 사실인지 구분할 수 없다.

### 실증 ③ 학술: 무료 전제가 무너지는 중

§3-(1) 실측대로 **OpenAlex가 크레딧/USD 미터링 헤더를 이미 내보내고 있다**(무료 1,000크레딧=$0.10/약 19시간, `prepaid-remaining-usd` 필드 존재). 이 조사에서 "무인증 200 OK"였던 소스도 **가격 정책이 붙는 중**이다. 도메인 어댑터의 유지보수는 코드 수정만이 아니라 **비용 모델 변경 추적**까지 포함된다.

### 실증 ④ 파서 깨짐: RISS

RISS는 **공개 REST API가 없다**(실측: HTML만 반환). k-skill의 `keris-academic-search`도 결국 공식 표면을 통과해야 한다. **HTML 스크레이핑 어댑터는 상대가 마크업만 바꿔도 깨지고, 사전 공지가 없다.** API 폐기는 최소한 공지라도 나오지만 스크레이퍼는 그것도 없다.

### 실증 ⑤ 그래서 실무는 어떻게 방어하는가 — k-skill의 답

k-skill의 `korean-patent-search`/`keris-academic-search` SKILL.md를 열어보면 내용이 없다. 대신 **스텁**이다:

```
<!-- k-skill:cli-stub — generated by scripts/generate-skill-stubs.js -->
npx -y @nomadamas/k-skill@0 instruct korean-patent-search
```
> "CLI가 현재 런타임을 감지해 적용 가능한 지시만 출력하며, **항상 최신 상태다.**"

**즉 120개 SKILL.md를 개별 관리하지 않는다.** 지시문은 npm 패키지 한 곳에 있고, SKILL.md는 그걸 부르는 스텁일 뿐이다. API가 바뀌면 **패키지 하나만 배포하면 설치된 모든 사용자에게 반영된다.**
→ **도메인 N개를 감당하는 유일하게 검증된 방법은 "N개를 각각 관리하지 않는 것"이다.** 이것 없이 도메인 7개로 출발하면, 위 실증 ①~④가 7배로 온다.

---

## 6. 종합 등급 및 권고

### 등급표

| 도메인 | 등급 | 한 줄 근거 |
|---|---|---|
| **의학·생명과학** | **높음** | 무인증 API 4종 실측 성공 + 식별자 4종 + **NCT 사전등록 대조라는 도메인 고유 검증** + 최강 선점자 149★(16개월 정체) |
| **금융·기업실사(미국)** | **높음** | SEC EDGAR·GLEIF 무인증 200 + 공시 원문이 곧 정본 + 최강 MCP 353★ + 수요 최대 축과 인접 |
| **학술/과학 논문** | **중간** | A·B 만점이나 **C가 44,456★로 막힘**, D는 6.1K로 약함. 어댑터로는 1순위, 제품 축으로는 부적절 |
| **법률(한국)** | **중간** | 식별자 있으나 **CourtListener 상세 401 / 법령 OC 필수**로 검증 경로가 인증 뒤. 2,539★가 이미 "인용 검증"으로 포지셔닝 |
| **한국어 1차 소스** | **중간** | 검증 가능하나 **무인증 REST 0개** + k-skill 7,384★/약 120스킬이 후보 축을 전부 선점 완료 |
| **특허** | **낮음** | B는 만점인데 **A가 무너짐** — 공식 호스트 2개가 오늘 DNS 미해석. 18개월 3회 파괴적 변경 |
| **시장·경쟁사 리서치** | **낮음** | **D가 최대(87K)인데 B가 0.** 정본이 없어 인용 검증이 원리적으로 불가 → 제품의 핵심 기능이 죽는다 |

### 권고

**1. 도메인은 스킬이 아니라 어댑터 레지스트리로 만들 것.** §4의 세 사례가 독립적으로 도달한 구조다. 구체적으로:
- 소스 하나당 얇은 어댑터 하나(엔드포인트·인증방식·식별자 스키마·rate limit만).
- 검증·스냅샷·예산 로직은 도메인 무관하게 **한 벌만** 둔다.
- 어댑터 목록은 코드가 아니라 **설정 데이터**로 두고, 어댑터 실패 시 `biz-health-check`처럼 **그 항목만 강등**한다.

**2. 어댑터 착수 순서**: `openalex → crossref → pubmed → clinicaltrials → sec-edgar`.
전부 무인증 200 실측 확인됐고, DOI/PMID/NCT/CIK로 **검증 왕복이 즉시 가능**하다. 여기서 검증 파이프라인이 돌아가는 걸 먼저 증명해야 나머지가 의미를 갖는다.

**3. 도메인 "스킬"은 만들되 하나만, 그리고 의학으로.** §4의 예외 조건(소스 묶는 순서 + 교차검증 규칙 + 실패 처리가 도메인 고유)을 만족하는 후보는 의학이 가장 뚜렷하다 — **NCT 사전등록 ↔ 논문 결과 대조**는 다른 도메인에 없는 규칙이고, 이건 어댑터에 담을 수 없다. 선점자도 149★로 가장 얇다.

**4. 특허와 시장·경쟁사는 v1에서 제외할 것.** 특허는 A가 무너져서, 시장은 B가 없어서다. **특히 시장·경쟁사는 수요 숫자(87K)가 가장 커서 가장 유혹적이고, 그래서 가장 위험하다** — 거기 들어가는 순간 제품의 정체성이 "검증"에서 "검색 요약"으로 바뀌고, 그 자리는 00-SUMMARY가 죽은 땅이라고 결론 낸 곳이다.

**5. 한국어 축을 하려면 k-skill과 경쟁하지 말고 그 위에 얹을 것.** 7,384★·약 120스킬·프록시 인프라를 새로 복제하는 건 승산이 없다. 반면 **k-skill에 없는 것은 검증층이다** — `biz-health-check`조차 "점수·등급·위험 판정 없음"을 설계 원칙으로 명시하며 판단을 사용자에게 넘긴다. **1층은 이미 지어져 있고 2층이 비어 있다.**

**6. 도메인을 늘리기로 결정했다면, 늘리기 전에 스텁 구조부터 만들 것.** §5-⑤. 지시문을 배포 가능한 한 곳(패키지/CLI)에 두고 SKILL.md는 스텁으로 유지하는 구조 없이 도메인 7개를 벌리면, 특허·ClinicalTrials급 파괴적 변경이 올 때마다 7곳을 손봐야 한다.

---

## 7. 미확인 목록 (추정으로 메우지 않은 것)

- **OpenAlex 요금제 전문·정책 방향.** 크레딧 헤더는 실측했으나 공식 가격 페이지·무료 티어 유지 여부는 확인 못 함.
- **`search.patentsview.org` / `api.data.uspto.gov`의 DNS 미해석 원인.** 서비스 종료인지 호스트명 변경인지 미확인. **현재 유효한 USPTO 특허 검색 API 호스트가 무엇인지 미확인.**
- **ClinicalTrials.gov v2 / Europe PMC / openFDA / arXiv / Semantic Scholar / OpenAIRE의 문서상 rate limit.** 응답 헤더에 없었고 문서 확인 안 함.
- **의학 도메인의 수요 지표(D).** skills.sh `pubmed`/`clinical` 단독 설치수 집계 없음. **A/B/C가 좋다는 것만 확인했고 D는 모른다.**
- **특허 도메인의 수요 지표(D).**
- **해외 법률(미국·EU) 수요 지표.**
- `fluidityiq-patent-intelligence`, `credit-memo`, `techknowmad-ai-skills` 플러그인의 **소스 URL·★·활성도** (마켓 등재만 확인, 03번 리포트도 동일하게 미확인 처리).
- **KIPRIS Plus의 현재 유효 엔드포인트.** 시험 호출이 404였으나 경로 변경인지 폐기인지 미확인.
- **`nomadamas/k-skill`과 사용자의 관계.** 로컬에 설치된 스킬 다수가 이 저장소 것이나, 사용자가 저자인지 이용자인지 이 조사로는 확인 불가 — 권고 5는 "이용자"를 가정하고 썼다.
- **Semantic Scholar 무인증 지속 가능성.** 200이 떨어졌으나 키 없이 장기 사용 시 제약은 미확인.
- **google-deepmind/science-skills의 설치수.** star(2,809)만 확인.

---

## Sources

**실측 호출 대상 (2026-09-01, curl)**
[api.openalex.org](https://api.openalex.org) · [api.crossref.org](https://api.crossref.org) · [export.arxiv.org](https://export.arxiv.org/api/query) · [api.semanticscholar.org](https://api.semanticscholar.org) · [api.openaire.eu](https://api.openaire.eu) · [api.unpaywall.org](https://api.unpaywall.org) · [eutils.ncbi.nlm.nih.gov](https://eutils.ncbi.nlm.nih.gov) · [clinicaltrials.gov/api/v2](https://clinicaltrials.gov/api/v2/studies) · [ebi.ac.uk/europepmc](https://www.ebi.ac.uk/europepmc/webservices/rest) · [api.fda.gov](https://api.fda.gov) · [courtlistener.com/api/rest/v4](https://www.courtlistener.com/api/rest/v4/) · [static.case.law](https://static.case.law/) · [law.go.kr/DRF](https://www.law.go.kr/DRF/lawSearch.do) · [data.sec.gov](https://data.sec.gov) · [sec.gov/files/company_tickers.json](https://www.sec.gov/files/company_tickers.json) · [api.gleif.org](https://api.gleif.org) · [api.opencorporates.com](https://api.opencorporates.com) · [api.company-information.service.gov.uk](https://api.company-information.service.gov.uk) · [wikidata.org/w/api.php](https://www.wikidata.org/w/api.php) · [ops.epo.org](https://ops.epo.org) · [api.odcloud.kr](https://api.odcloud.kr) · [opendart.fss.or.kr](https://opendart.fss.or.kr) · [open.kci.go.kr](https://open.kci.go.kr) · [plus.kipris.or.kr](http://plus.kipris.or.kr) · [riss.kr](https://www.riss.kr/)

**문서·공지**
[NCBI E-utilities 사용 가이드라인](https://www.ncbi.nlm.nih.gov/books/NBK25497/) · [SEC Accessing EDGAR Data](https://www.sec.gov/search-filings/edgar-search-assistance/accessing-edgar-data) · [PatentsView 레거시 API 종료 공지](https://patentsview.org/data-in-action/patentsview-ends-support-legacy-api) · [PatentsView 2025-02 전환 안내](https://patentsview.org/data-in-action/support-legacy-api-end-february-2025-switch-patentsearch-api-now) · [USPTO PTAB API v2 폐기 공지](https://developer.uspto.gov/node/165448) · [rOpenSci patentsview breaking release](https://ropensci.org/blog/2026/03/10/patentsview-breaking-release/) · [ClinicalTrials.gov API v2 (NLM Technical Bulletin)](https://www.nlm.nih.gov/pubs/techbull/ma24/ma24_clinicaltrials_api.html) · [ClinicalTrials.gov 현대화 전환 FAQ](https://clinicaltrials.gov/about-site/modernization-top-questions)

**GitHub (REST API 실측)**
[google-deepmind/science-skills](https://github.com/google-deepmind/science-skills) · [nomadamas/k-skill](https://github.com/nomadamas/k-skill) · [Imbad0202/academic-research-skills](https://github.com/Imbad0202/academic-research-skills) · [lingzhi227/agent-research-skills](https://github.com/lingzhi227/agent-research-skills) · [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills) · [chrisryugj/korean-law-mcp](https://github.com/chrisryugj/korean-law-mcp) · [blazickjp/arxiv-mcp-server](https://github.com/blazickjp/arxiv-mcp-server) · [stefanoamorelli/sec-edgar-mcp](https://github.com/stefanoamorelli/sec-edgar-mcp) · [cyanheads/pubmed-mcp-server](https://github.com/cyanheads/pubmed-mcp-server) · [riemannzeta/patent_mcp_server](https://github.com/riemannzeta/patent_mcp_server) · [avivlyweb/nagomi-pubmed-plugin](https://github.com/avivlyweb/nagomi-pubmed-plugin)

**로컬 실측**
`~/.claude/skills/` 설치본의 `biz-health-check`·`k-dart`·`korean-law-search`·`fsc-corporate-info` SKILL.md 원문

**선행 리포트**
[00-SUMMARY.md](00-SUMMARY.md) · [01-skills-sh.md](01-skills-sh.md) · [02-oss-agents.md](02-oss-agents.md) · [03-claude-ecosystem.md](03-claude-ecosystem.md) · [04-community-market.md](04-community-market.md)
