# research 특화 에이전트 — 조사 종합 (2026-09-01)

Orca 워커 7개 병렬 조사. 전부 API 실측·원본 파일 열람 기반이며, 확인 못 한 것은 각 문서에 "미확인"으로 남겼다.

| # | 문서 | 무엇을 확인했나 |
|---|---|---|
| 01 | [skills-sh](01-skills-sh.md) | skills.sh 레지스트리 실검색 27개 키워드, 랭킹 메커니즘 |
| 02 | [oss-agents](02-oss-agents.md) | GitHub OSS 40여 개 ★·라이선스·활성도 실측 |
| 03 | [claude-ecosystem](03-claude-ecosystem.md) | 플러그인 마켓 2,282개 파싱, MCP 레지스트리 |
| 04 | [community-market](04-community-market.md) | 유통 채널 10곳, HN 실데이터, 상용 8종 |
| 05 | [skill-decomposition](05-skill-decomposition.md) | 상위 8개 레포 SKILL.md **원본 해부** |
| 06 | [domain-axis](06-domain-axis.md) | 7개 도메인 API를 curl로 **직접 호출** |
| 07 | [plugin-skeleton](07-plugin-skeleton.md) | v1 골격 설계 (진행 중) |
| 08 | [medical-anchor](08-medical-anchor.md) | 의학 앵커 선점자 정밀 확인 |

---

## 결론 3줄

1. **"질문 넣으면 인용 달린 리포트"는 죽은 땅.** 들어가면 진다.
2. **비어 있는 건 "리서치 수행"이 아니라 "리서치 검증"** — 7개 조사가 독립적으로 같은 결론.
3. **가장 깊은 빈칸은 L3(논문 ↔ 외부 1차 출처 대조)이고, 의학의 NCT 사전등록 대조가 그 실물이다.**

---

## A. 시장 — 어디가 포화이고 어디가 비었나

### 포화된 곳
- OSS: gpt-researcher 29.2k★(**이미 Claude Skill로 배포**), deer-flow 81.2k★, deepagents 28.8k★
- 플러그인 마켓: 2,282개 중 research 키워드 **76개**
- skills.sh: `deep-research`라는 **동일 이름 스킬만 10개 이상**
- Claude Code에 `WebSearch`/`WebFetch` **무료 내장** → "검색해서 요약"은 이미 기본값

### 교차 검증된 빈칸

| 빈칸 | 상태 | 출처 |
|---|---|---|
| **인용 시점 검증** | 메이저 중 기본값으로 켠 곳 **0** | 01,02,03 |
| **재현성**(코퍼스 스냅샷) | 확인된 구현 **0건** | 02 |
| **사전 비용 예측** | **0건** (Jina·mole만 사후 예산) | 02,04 |
| **로컬/오프라인 우선** | local-deep-research가 거의 유일 | 02,04 |
| **L3 검증**(논문↔외부 1차 출처) | **자동화 0건** | 08 |

---

## B. 반직관적 사실 (전부 실측)

1. **HN은 이 카테고리에서 안 통한다.** gpt-researcher Show HN = **4점**, 현재 29.2k★. 최근 12개월 deep-research Show HN 중 100점 넘은 건 1건. 실제 경로는 **마켓플레이스 + GitHub Trending**.
2. **star ≠ 설치수.** star 44K가 8.7K 설치, star 480이 450.8K 설치. 설치수는 인기가 아니라 **번들 유통 경로**를 잰다.
3. **skills.sh 1위 `mattpocock/skills@research`는 SKILL.md가 13줄.** 깊이가 아니라 저장소 인지도가 순위를 만든다.
4. **콜드스타트가 구조적으로 불리.** 전체 1위 `find-skills`(3.2M)가 **설치 1K·star 100 미만을 필터링**한다.
5. **star는 생존을 보장 안 한다.** STORM 31.2k★ 11개월 정체, LangChain open_deep_research 12.7k★ **아카이브**, RobotReviewer·Trialstreamer 2022년 이후 무커밋.
6. **research 1위 플러그인은 MCP를 안 쓴다.** 스킬 + 40 서브에이전트 + bash/python 직접 HTTP 호출.

---

## C. 설계 — 무엇을 어떻게 쪼개나 (05, 06)

### 스킬은 6유형으로만 나타난다
라우터 · 오케스트레이터 · **파이프라인 단계(동사)** · 역할/게이트 · 산출물 · 인프라

**도메인형(산업 이름) 스킬은 8개 레포 통틀어 0건.**

### 경계선 2개
- **사용자가 부르면 스킬, 스킬이 부르면 에이전트**
- 실질 기준은 **컨텍스트 오염** — 대량 원문 읽기 → 에이전트, 판단·대화 → 스킬

### 입도는 스타수와 무상관
44k★ 1위가 스킬 4개, 0★도 스킬 4개. 얇게(15개) vs 두껍게(4개) 우열 증거 없음 → **적게 시작해 늘리는 쪽이 안전**.

### 도메인 = 스킬이 아니라 어댑터/프로파일 데이터

증거 3개가 독립적으로 동일 결론:
- `nagomi-pubmed-plugin`은 PubMed 전용인데 스킬이 `pubmed-search/analyze/verify/synthesis/export` — 도메인은 **접두사**일 뿐
- `paper-review-system`은 **10개 학회를 10개 스킬로 안 만들고** `venue-profiles.md` 하나로 처리
- `Aperivue/medsci-skills`는 가이드라인 **52개를 마크다운**으로 두고 **`add-journal`(데이터 추가 스킬)**까지 만들었다

**결정적 이유는 유지보수.** 특허 도메인 실측: 2025-05 `api.patentsview.org` 410 Gone → 키 필수화 → 2026-01 PTAB v2 폐기 → **오늘 후속 호스트 2개 DNS A 레코드 없음.** 18개월에 파괴적 변경 3회.

더 나쁜 건 ClinicalTrials.gov v1→v2 — 필드가 자유텍스트→열거형으로 바뀌어 **구코드가 예외 없이 조용히 틀린 결과**를 낸다. 에이전트가 빈 결과를 "근거 없음"으로 보고한다.

### 스킬 간 데이터 계약이 없으면 쪼갠 스킬이 안 이어진다
Scriptorium만 제대로 함: `corpus.jsonl → evidence.jsonl → report.md`, 인용 토큰 `[source_id:locator]`, `cite-check.py`가 커밋 전 강제 검증. **파일명을 description에 박아야 스킬이 서로를 찾는다.**

---

## D. 도메인 등급 (06 — API 직접 호출 실측)

| 도메인 | 등급 | 근거 |
|---|---|---|
| **의학·생명과학** | **높음** | 무인증 API 4종 200 OK, 식별자 4종, **NCT 사전등록 대조**라는 고유 검증. 최강 선점자 149★ |
| **금융(미국)** | **높음** | SEC EDGAR 무인증 200, 공시 원문이 곧 정본. 최강 MCP 353★ |
| 학술 논문 | 중간 | A·B 만점이나 C가 44,456★로 막힘, 수요 약함(6.1K) → **어댑터 1순위, 제품축 부적절** |
| 법률(한국) | 중간 | 검증 경로가 인증 뒤. 2,539★가 이미 인용검증 포지션 |
| 한국어 1차 소스 | 중간 | 무인증 REST 0개 + k-skill 7,384★ 선점 완료. **단 k-skill에 없는 게 검증층** |
| 특허 | **낮음** | 식별자는 만점인데 **API가 무너짐** |
| 시장·경쟁사 | **낮음** | **수요 최대(87K)인데 정본 식별자 0** → 인용 검증이 원리적으로 불가 |

> 시장·경쟁사가 가장 유혹적이고 가장 위험하다. 들어가는 순간 제품이 "검색 요약"으로 변질된다.

**부수 발견**: OpenAlex가 크레딧/USD 미터링 헤더를 이미 내보낸다(무료 1,000크레딧=$0.10/약 19시간, `prepaid-remaining-usd` 필드 존재). **"학술 API는 공짜"라는 전제 위에 설계하면 안 된다.**

---

## E. 의학 앵커 정밀 확인 (08)

### L3는 비어 있다 — 검증 깊이 전수

L0 검색만 / L1 서지 실존 / L2 논문 내부 정합성 / **L3 논문↔외부 1차 출처**

| 프로젝트 | ★ | 레벨 |
|---|---|---|
| K-Dense-AI/scientific-agent-skills | 41,055★ | L0 |
| google-deepmind/science-skills | 2,810★ | L0 |
| **Aperivue/medsci-skills** | 278★ | **L2** (90개 파이썬 detector 실물) |
| cyanheads/pubmed-mcp-server | 142★ | L0~L1 |
| Future-House/paper-qa | 9,133★ | L1 |
| RobotReviewer / Trialstreamer | 177★ / 23★ | L2 — **2022년 이후 무커밋, 호스트 DNS 실패** |
| nagomi-pubmed-plugin | 0★ | L1 |

**L3 자동화 0건.** L2 최고봉 Aperivue조차 레지스트리 대조는 "저자가 첨부했다면" 수동 조건부고, detector 90개 중 registry 대조는 0개.

임상시험 스킬은 전부 (a)검색 (b)새 시험 설계 (c)환자 매칭. **끝난 시험이 정직하게 보고됐는지 검사하는 건 없다.**

### 왜 비었나 — 기술이 아니라 노동·인센티브
COMPare(2015-16)가 정확히 이걸 **전수 수작업**으로 했다. 67건 중 완벽 보고 9건. 저널에 편지 58통 → **게재 6, 거절 16, 무응답 36.** 코드 없이 종료.

병목은 "탐지"가 아니라 "탐지해도 아무 일도 안 일어난다"였다 → 자동화가 정확히 푸는 종류. **단, 포지셔닝을 "저널을 고치겠다"로 잡으면 같은 벽에 부딪힌다. "논문 읽는 사람에게 30초 안에 경고"여야 한다.**

### 기술 실현성 확인됨
- CT.gov API v2가 `primaryOutcomes[]`를 `{measure, description, timeFrame}` **구조화 필드**로 제공 — NLP 불필요
- `referencesModule`이 **PMID를 직접 제공** — 논문 연결도 공짜
- ACTT-1 실제 대조 성립. 초록 한 문장으로 됨
- 2024-25 RCT 54,309건 중 26.7%가 CT.gov 링크, 그중 30.4%는 **초록만으로** 대조 가능, 57.6%는 PMC 전문 있음

### 세부 분야는 프로파일 데이터 — 단, 커버리지가 2배 차이

| 분야 | CT.gov 링크/RCT 비 |
|---|---|
| **종양학** | **1.09** |
| 감염병 | 0.93 |
| 정신과 | 0.54 |
| 외과 | 0.52 |

**v1 데모 앵커는 종양학.** 외과·정신과로 잡으면 "찾을 수 없음"이 절반 나온다. 종양학은 대리지표(PFS/ORR)↔최종지표(OS) 전환 서사도 가장 선명하다.

---

## F. 런칭 (04)

- **필수**: 한 문장 포지셔닝(`<제약> 하에서 <결과>`) · **한 줄 설치** · README 인라인 데모 GIF([vhs](https://github.com/charmbracelet/vhs)) · **MIT** · GitHub Topics · "아직 못 하는 것" 섹션
- **채널 우선순위**: 마켓플레이스 + GitHub Trending > r/LocalLLaMA·r/ClaudeAI > X > HN(기대치 낮게)
- **환율**: HN 100점 ≈ 스타 300
- **성공 판정**: star가 아니라 ① 실행 리포트 ② 재현정보 붙은 첫 버그 이슈 ③ 첫 외부 PR
- **이름**: `skills find`는 **이름 부분일치** → `research`/`verify`/`citation` 같은 짧은 일반명사

---

## G. 위험 목록

### 🔴 착수 전 반드시 해소
- **npj Digital Medicine 2026-07** 논문이 LLM으로 outcome change 탐지, sensitivity 0.97. 초록상 *"registry ↔ posted results"* 내부 대조라 우리와 다르지만, **본문·코드 공개 여부를 확인 못 했다**(nature.com IdP 차단, Europe PMC 미색인). 저자들이 논문 쪽으로 확장할 가능성이 실재한다.

### 🟡 설계에 반영
- **구현 안 한 프레임워크 이름을 빌리지 말 것.** nagomi가 "GRADE-style"이라 광고하지만 실제 코드는 저널명 하드코딩 + 초록 정규식 + 출판연도 가중합이고, GRADE의 5개 강등 도메인이 코드에 없다. 의료 종사자는 이름을 보면 구현했다고 읽는다 — 소스 공개 시 즉시 지적당한다.
- **체크리스트 라이선스 지뢰**: TRIPOD·QUADAS·PROBAST·PRISMA-DTA는 오픈 라이선스 없음(© ACP/AMA), ROBINS-I는 **CC BY-NC**. 원문 번들 시 상업 배포에 문제.
- PubMed rate limit **키 없이 3 req/s** — 병렬 에이전트가 쉽게 넘긴다. 어댑터 스로틀 필요.
- 임상 판단 도구로 오인되지 않도록 README 면책 필요.

### ⚪ 미확인 (추정으로 메우지 않음)
- 의학 리서치 스킬의 **수요 지표** — skills.sh에 pubmed/clinical 단독 집계 없음. **A·B·C만으로 고른 선택**
- 신규 스킬이 skills.sh에 **언제 등록되는지** ([Issue #880](https://github.com/vercel-labs/skills/issues/880) 미답변) → 더미 스킬로 실측 필요
- 서브레딧 규칙·구독자 수 (Reddit 403 차단) → 런칭 전 직접 확인
- 상용 가격 일부 2차 출처 (집계 사이트가 Elicit 가격을 틀리게 적은 사례 확인)
- ClinicalTrials.gov v2 문서상 rate limit
- OpenAlex 요금제 전문·정책 방향
- 각 프로젝트 self-reported 벤치마크의 제3자 재현 여부

---

## H. 현재 결정 상태

| 항목 | 결정 | 근거 |
|---|---|---|
| 포지셔닝 | 리서치 **검증** | A |
| 배포 형식 | Claude Code **플러그인**, MCP 서버 안 만듦 | 03 |
| 구조 | 2층 (작업 스킬 / 소스 어댑터) | 06 |
| v1 도메인 앵커 | **의학·생명과학** | 06, 08 |
| v1 데모 세부 분야 | **종양학** | 08 |
| 세부 분야 처리 | 프로파일 데이터 (스킬 아님) | 08 |
| 라이선스 | MIT | 04 |
| **미결** | npj 논문 확인 · 스킬 최종 목록 확정 · 이름 | — |

---

## I. 리서치 방법론 조사 (2026-09-03, 5스트림 병렬) — 제품 재정의

"리서치를 한다"는 행위 자체를 조사해 신뢰성 있는 리서치 에이전트 설계 근거 확보.

| # | 문서 | 요지 |
|---|---|---|
| 11 | [research-methodology](11-research-methodology.md) | 인간 전문가 규율 → **에이전트가 따를 규칙 12개**로 증류 (SIFT·삼각검증·PRISMA·Admiralty·ACH·2-source) |
| 12 | [agent-architectures](12-agent-architectures.md) | Anthropic 멀티에이전트·STORM·Deep Research 해부 → **신뢰성과 상관있는 이식 패턴 10개** (자기보고 성능은 배제) |
| 13 | [access-tools](13-access-tools.md) | 검색·페치·안티봇·브라우저·PDF·MCP 32종 비교 → 무료/오프라인 권장 스택 |
| 14 | [research-taxonomy](14-research-taxonomy.md) | 리서치 **9유형 × 신뢰성 정의** → "전체를 아우름 = 도메인 스킬이 아니라 라우팅" |
| 15 | [failure-modes](15-failure-modes.md) | 신뢰성 상실 9지점 + **우선순위 방어 5개** (간접 프롬프트 인젝션 = 보안위협) |
| 16 | [**synthesis**](16-synthesis-research-agent.md) | **위 전부를 하나의 설계로**: 신뢰성 척추 6축 + 라우팅 + 파이프라인 게이트 |

**재정의**: 제품 = "인용 검증"(좁게) → **"신뢰성을 강제하는 파이프라인"**(라우팅으로 전 유형 리서치 아우름). 의학 NCT 대조는 유형2+4의 **프리미엄 모듈 1개**로 격하 — 사용자의 "논문 하나에 가둬지지 말자"와 일치. 상세·다음 결정은 16번 §7.
