# GitHub 오픈소스 Research 에이전트 지형 조사

**조사 시점: 2026-09-01 (KST)**
**스타수 출처: GitHub REST API `repos/{owner}/{repo}` 직접 조회 (조사 시점 실측값)**

> ⚠️ 수치 신뢰도에 대한 고지
> - **스타수·라이선스·최종 푸시일·생성일**: GitHub API 실측. 신뢰 가능.
> - **성장률(최근 N개월 증가분)**: `stargazers` 타임스탬프 엔드포인트가 이 환경의 토큰 권한으로 404를 반환해 **직접 측정 불가 → "미확인"**. 3장은 측정된 성장률 대신 **생성일 + 커밋 활성도 + 아카이브 이벤트**라는 검증 가능한 대리 지표로만 논증한다.
> - **벤치마크 수치**: 각 프로젝트가 자기 README/논문에 주장한 값(self-reported). 제3자 재현 여부는 대부분 미확인.

---

## 1. 경쟁자 인벤토리

### 1-1. 직접 경쟁 — "리서치 리포트 생성"이 본업인 것

| 레포 | ⭐ (2026-09-01) | 라이선스 | 최종 푸시 |
|---|---:|---|---|
| [assafelovic/gpt-researcher](https://github.com/assafelovic/gpt-researcher) | 29,228 | Apache-2.0 | 2026-08-27 |
| [stanford-oval/storm](https://github.com/stanford-oval/storm) | 31,193 | MIT | **2025-09-30** |
| [khoj-ai/khoj](https://github.com/khoj-ai/khoj) | 36,848 | AGPL-3.0 | 2026-08-02 |
| [bytedance/deer-flow](https://github.com/bytedance/deer-flow) | 81,195 | MIT | 2026-09-01 |
| [langchain-ai/deepagents](https://github.com/langchain-ai/deepagents) | 28,780 | MIT | 2026-09-01 |
| [langchain-ai/open_deep_research](https://github.com/langchain-ai/open_deep_research) | 12,680 | MIT | **아카이브됨** |
| [dzhng/deep-research](https://github.com/dzhng/deep-research) | 19,620 | MIT | 2026-04-11 |
| [Alibaba-NLP/DeepResearch](https://github.com/Alibaba-NLP/DeepResearch) | 19,898 | Apache-2.0 | 2026-02-27 |
| [jina-ai/node-DeepResearch](https://github.com/jina-ai/node-DeepResearch) | 5,225 | Apache-2.0 | 2026-05-01 |
| [LearningCircuit/local-deep-research](https://github.com/LearningCircuit/local-deep-research) | 9,014 | MIT | 2026-09-01 |
| [Future-House/paper-qa](https://github.com/Future-House/paper-qa) (PaperQA2) | 9,133 | Apache-2.0 | 2026-08-26 |
| [SakanaAI/AI-Scientist](https://github.com/SakanaAI/AI-Scientist) | 14,476 | NOASSERTION | 2025-12-19 |
| [SakanaAI/AI-Scientist-v2](https://github.com/SakanaAI/AI-Scientist-v2) | 7,069 | NOASSERTION | 2025-12-19 |
| [huggingface/smolagents](https://github.com/huggingface/smolagents) (`examples/open_deep_research`) | 29,087 | Apache-2.0 | 2026-08-25 |
| [nickscamara/open-deep-research](https://github.com/nickscamara/open-deep-research) (Firecrawl) | 6,283 | NOASSERTION | 2025-05-07 |
| [btahir/open-deep-research](https://github.com/btahir/open-deep-research) | 2,141 | MIT | **아카이브됨** |
| [u14app/deep-research](https://github.com/u14app/deep-research) | 4,682 | MIT | 2026-06-18 |
| [MiroMindAI/MiroFlow](https://github.com/MiroMindAI/MiroFlow) | 3,103 | Apache-2.0 | 2026-07-06 |
| [TheBlewish/Automated-AI-Web-Researcher-Ollama](https://github.com/TheBlewish/Automated-AI-Web-Researcher-Ollama) | 3,011 | MIT | **2024-12-14 (사실상 사망)** |

### 1-2. 인접 — 답변 엔진 / 범용 에이전트 하니스 (같은 사용자를 놓고 경쟁)

| 레포 | ⭐ | 라이선스 | 비고 |
|---|---:|---|---|
| [FoundationAgents/OpenManus](https://github.com/FoundationAgents/OpenManus) | 58,141 | MIT | 범용 자율 에이전트 |
| [ItzCrazyKns/Vane](https://github.com/ItzCrazyKns/Vane) (구 Perplexica) | 36,563 | MIT | **2026년에 리브랜딩됨** |
| [OpenBMB/ChatDev](https://github.com/OpenBMB/ChatDev) | 34,169 | Apache-2.0 | 멀티에이전트 협업 |
| [openai/openai-agents-python](https://github.com/openai/openai-agents-python) | 29,105 | MIT | 프레임워크 |
| [camel-ai/owl](https://github.com/camel-ai/owl) | 20,117 | 미확인(null) | 멀티에이전트 태스크 자동화 |
| [google-gemini/gemini-fullstack-langgraph-quickstart](https://github.com/google-gemini/gemini-fullstack-langgraph-quickstart) | 18,325 | Apache-2.0 | 레퍼런스 구현 |
| [HKUDS/DeepCode](https://github.com/HKUDS/DeepCode) | 16,457 | MIT | 논문→코드 |
| [zaidmukaddam/scira](https://github.com/zaidmukaddam/scira) | 11,854 | AGPL-3.0 | 인용 달린 검색엔진 |
| [miurla/morphic](https://github.com/miurla/morphic) | 9,079 | Apache-2.0 | generative UI 검색 |
| [firecrawl/firecrawl](https://github.com/firecrawl/firecrawl) | 174,925 | AGPL-3.0 | **인프라 계층** (대부분이 의존) |
| [exa-labs/exa-mcp-server](https://github.com/exa-labs/exa-mcp-server) | 4,949 | MIT | 검색 MCP |

### 1-3. 연구계(RL·논문) — 제품 경쟁자는 아니나 기법 소스

| 레포 | ⭐ | 라이선스 |
|---|---:|---|
| [RUC-NLPIR/WebThinker](https://github.com/RUC-NLPIR/WebThinker) (NeurIPS 2025) | 1,467 | MIT |
| [RUC-NLPIR/Search-o1](https://github.com/RUC-NLPIR/Search-o1) (EMNLP 2025) | 1,244 | MIT |
| [GAIR-NLP/DeepResearcher](https://github.com/GAIR-NLP/DeepResearcher) | 801 | Apache-2.0 |
| [Future-House/aviary](https://github.com/Future-House/aviary) | 278 | Apache-2.0 |
| [OSU-NLP-Group/QUEST](https://github.com/OSU-NLP-Group/QUEST) | 249 | 미확인 |
| [simplexai-labs/LiteResearcher](https://github.com/simplexai-labs/LiteResearcher) (COLM 2026) | 131 | 미확인 |

---

## 2. 개별 프로파일

### GPT Researcher — 29,228⭐ / Apache-2.0 / 2023-05 생성 / 활발
- **포지셔닝**: "웹과 로컬 문서 모두에 대해 인용 달린 리포트를 뽑는 최초의 오픈 딥리서치 에이전트."
- **실행 형태**: Python 라이브러리 + CLI + Next.js 웹앱 + MCP 서버 + **Claude Skill** (`npx skills add assafelovic/gpt-researcher`).
- **강점**: 카테고리 원조. Planner/Executor 분리를 병렬화해 속도가 빠름. LLM·검색 제공자 교체가 자유로움. 한국어 포함 다국어 README. **경쟁자 중 유일하게 Claude Skill로 이미 패키징을 마쳤다.**
- **약점**: 3년치 기능이 쌓여 설정 표면이 거대함(설정 파일·환경변수 다수). 리포트 품질이 붙인 검색 API 등급에 강하게 종속. 인용 검증 로직은 "출처를 붙인다"에 가깝고 주장↔출처 일치 검사는 미확인.
- **🔴 이 조사에서 가장 중요한 발견**: 사용자가 노리는 "research 특화 스킬" 슬롯을 이미 이 레포가 점유했다. 차별화 축을 새로 세우지 않으면 정면 충돌한다.

### Stanford STORM / Co-STORM — 31,193⭐ / MIT / **최종 푸시 2025-09-30 (약 11개월 정체)**
- **포지셔닝**: 위키피디아형 장문 글을 인용과 함께 자동 작성. NAACL 2024 / Co-STORM은 EMNLP 2024.
- **실행 형태**: `pip install knowledge-storm` 라이브러리 + Streamlit 데모 + 호스팅 연구 프리뷰(storm.genie.stanford.edu, README 기준 누적 7만 명 이상 시도).
- **강점**: 카테고리 유일의 **학술적으로 검증된 방법론** — "관점 유도 질문 생성(Perspective-Guided Question Asking)"과 "시뮬레이션 대화"라는, 남들이 그냥 프롬프트로 때우는 부분에 논문 근거가 있음. Co-STORM은 인간-AI 협업 담화 프로토콜을 추가.
- **약점**: **약 11개월간 커밋 없음.** 스타 3만은 관성이지 활성도가 아님. README도 "편집 없이 출판 가능한 글은 못 만든다"고 자인. 최신 모델·MCP·에이전트 하니스 흐름에 미대응.
- **함의**: 스타는 높지만 실질 경쟁 압력은 낮다. 반대로 **STORM의 방법론을 현대 하니스에 이식하는 것**은 열려 있는 빈칸이다.

### LangChain 계열 — open_deep_research(12,680⭐, **아카이브**) → deepagents(28,780⭐, 활발)
- **일어난 일**: `open_deep_research`가 아카이브(마지막 푸시 2026-08-10)되고, 2025-07 생성된 `deepagents`("배터리 포함 에이전트 하니스")가 매일 커밋되는 후계 자리에 있다. **두 레포의 공식 승계 선언은 웹 검색으로 확인 못 함 → 미확인.** 확인된 사실은 "전자는 아카이브, 후자는 활발" 뿐.
- **deepagents 포지셔닝**: 딥리서치 전용이 아니라 **범용 하니스**(플래너·서브에이전트·파일시스템 도구를 기본 탑재). 딥리서치는 그 위의 한 레시피로 격하됨.
- **강점**: LangGraph 위라 스트리밍·체크포인팅·LangSmith 추적/평가/배포가 공짜로 딸려옴. 기업 도입 경로가 가장 짧다.
- **약점**: LangChain 스택 종속. 리서치 도메인 지식(인용 규율, 출처 위계, 재현성)은 사용자가 직접 채워야 함.
- **함의**: 이 분야의 무게중심이 "딥리서치 앱"에서 **"범용 하니스 + 리서치 레시피"**로 이동했다는 가장 강한 신호.

### ByteDance DeerFlow — 81,195⭐ / MIT / 2025-05 생성 / 2026-09-01 푸시
- **포지셔닝**: 자기 설명이 이미 딥리서치를 넘었다 — "샌드박스·메모리·툴·스킬·서브에이전트·메시지 게이트웨이를 갖춘, 수 분~수 시간짜리 장기 과업용 SuperAgent 하니스."
- **실행 형태**: 웹앱 + 서버 + 워크플로 엔진.
- **강점**: 이 조사에서 딥리서치 태생 레포 중 **최대 스타(8만)**. 대기업 리소스, 매일 푸시. 스킬·서브에이전트를 1급 개념으로 채택.
- **약점**: 무겁다. 도입 비용이 크고, "SuperAgent"로 스코프가 넓어지면서 리서치 특화도는 오히려 희석됨. 로컬/오프라인 실행 난이도 미확인.

### dzhng/deep-research — 19,620⭐ / MIT / 2025-02 생성 / 2026-04 푸시
- **포지셔닝**: "딥리서치 에이전트의 가장 단순한 구현" — 명시적으로 미니멀리즘을 표방.
- **실행 형태**: TypeScript CLI (~수백 줄).
- **강점**: 읽고 이해하는 데 한 시간이면 충분. breadth/depth 파라미터로 재귀 탐색 폭을 직접 조절. 포크 베이스로 최적.
- **약점**: Firecrawl 유료 API에 강결합. 인용 관리·리포트 서식이 얕음. 5개월 가까이 푸시 없음.

### Jina node-DeepResearch — 5,225⭐ / Apache-2.0 / 2026-05 푸시
- **포지셔닝**: "답을 찾거나 토큰 예산을 소진할 때까지 검색·읽기·추론을 반복."
- **강점**: **토큰 예산을 1급 종료 조건으로 만든 유일한 축.** 비용 폭주라는 이 분야 공통 실패를 설계로 막음. Jina Reader/Embeddings와 수직 통합.
- **약점**: Jina 자사 API 생태계 종속. 장문 리포트보다 단답 QA 성향.

### Local Deep Research — 9,014⭐ / MIT / 2026-09-01 푸시 (가장 활발한 소형 레포)
- **포지셔닝**: 완전 로컬·암호화. arXiv·PubMed·사내 문서 포함 10개 이상 검색 백엔드.
- **주장 성적(self-reported)**: RTX 3090 + Qwen3.6-27B 단일 장비에서 **SimpleQA ~95% (n=500)**, **xbench-DeepSearch 77% (n=100)**. 벤치마크 데이터셋을 HuggingFace에 공개. **제3자 재현 미확인.**
- **강점**: Ollama + SearXNG + Docker 3줄이면 **API 키 0개로 완전 오프라인 구동**. 프라이버시가 유일한 진짜 해자.
- **약점**: 셀프호스팅 운영 부담(v1.10.3부터 사설 엔진 URL 기본 차단 등 보안 설정이 늘어남). 로컬 모델 품질 상한에 갇힘.
- **함의**: 사용자의 로컬 폴백(Ollama/qwen) 노선과 아키텍처가 가장 가깝다. **직접 참조할 1순위.**

### PaperQA2 — 9,133⭐ / Apache-2.0 / 2026-08-26 푸시
- **포지셔닝**: 과학 문헌 대상 고정확도 RAG. 웹 서핑이 아니라 **PDF 코퍼스**가 대상.
- **실행 형태**: Python 라이브러리 + CLI. 2025-12부터 CalVer 채택.
- **강점**: 인용 정확도를 최우선으로 설계한 사실상 유일한 프로젝트. 논문에서 QA·요약·모순 탐지에서 초인적 성능을 주장(self-reported). 근거 수집→재순위→답변의 다단계 파이프라인.
- **약점**: 웹 딥리서치가 아니다(범위가 다름). PDF 파싱 품질·임베딩 비용에 종속. 학술 도메인 밖에서는 이점이 줄어듦.
- **함의**: 경쟁자가 아니라 **인용 신뢰성 모듈의 참고 구현**으로 다룰 것.

### Sakana AI-Scientist / v2 — 14,476 + 7,069⭐ / NOASSERTION / 최종 푸시 2025-12-19
- **포지셔닝**: 리서치가 아니라 **연구 자체의 자동화** — 아이디어→실험→논문 작성→리뷰. v2는 agentic tree search.
- **강점**: 야심의 상한선을 보여줌. 트리 탐색 기반 실험 설계는 재사용 가치 있음.
- **약점**: **NOASSERTION 라이선스 = 상업적 사용에 법무 검토 필요.** 8개월 이상 정체. 실행 비용이 매우 큼. 산출 논문 품질에 대한 학계 비판이 알려져 있음(구체 출처 미확인).

### HuggingFace open-deep-research (smolagents 예제) — 29,087⭐ (모레포) / Apache-2.0
- **포지셔닝**: OpenAI Deep Research의 오픈 재현.
- **성적**: README 명시 **GAIA validation pass@1 55%** vs 원본 Deep Research 67%. 이 분야에서 **자기 격차를 숫자로 공개한 드문 사례.**
- **강점**: "코드로 사고하는" smolagents 위라 코드가 짧고 읽힘. 텍스트/비전 브라우저 비교 노트북 동봉.
- **약점**: 제품이 아니라 **예제 디렉터리**. SerpApi/Serper 유료 키 필수. 독립 유지보수 없음.

### Khoj — 36,848⭐ / **AGPL-3.0** / 2026-08 푸시
- **포지셔닝**: "당신의 AI 세컨드 브레인" — 개인 문서 + 웹, 딥리서치는 여러 기능 중 하나.
- **강점**: 완성된 제품(데스크톱·브라우저·Obsidian·WhatsApp). 셀프호스팅 가능. 자동화/스케줄링 내장.
- **약점**: **AGPL-3.0 — SaaS로 감싸면 소스 공개 의무.** 리서치 특화도는 낮고 개인 지식관리 쪽에 무게중심.

### Alibaba Tongyi DeepResearch — 19,898⭐ / Apache-2.0 / **최종 푸시 2026-02-27 (6개월 정체)**
- **포지셔닝**: "선도적 오픈소스 딥리서치 에이전트" — 전용 학습 모델 + 에이전트 프레임워크 동봉.
- **강점**: 모델까지 함께 여는 몇 안 되는 사례. Apache-2.0.
- **약점**: 6개월 정체. 자사 모델 결합도가 높아 부분 채택이 어려움.

---

## 3. 최근 6~12개월 급성장 후보 (⚠️ 성장률 직접 측정 불가 — 대리 지표 기반)

측정 불가 사유는 문서 최상단 고지 참조. 아래는 **"생성일이 최근이면서 절대 스타가 큼" + "현재 커밋이 살아있음"**이라는 검증된 사실만으로 고른 5개다.

**1. bytedance/deer-flow — 81,195⭐ (2025-05-07 생성, 약 16개월)**
16개월 만에 8만. 이 카테고리 최대치다. 이유: 대기업 배포력 + "딥리서치"에서 "장기 과업 SuperAgent"로 스코프를 넓혀 검색 유입 자체가 커짐.

**2. langchain-ai/deepagents — 28,780⭐ (2025-07-27 생성, 약 13개월)**
13개월 만에 2.9만이며 조사 당일에도 푸시. 결정적 신호는 **선행 레포 `open_deep_research`(12,680⭐)의 아카이브** — LangChain이 딥리서치 전용 앱을 접고 범용 하니스로 자원을 옮겼다는 사실이 API로 확인된다.

**3. LearningCircuit/local-deep-research — 9,014⭐ (2025-02-09 생성)**
소형이지만 조사 당일 푸시. 로컬 하드웨어 SimpleQA ~95% 주장이 r/LocalLLaMA에서 확산된 것이 README에 링크로 남아 있다(성장 기여도는 미확인). **로컬 실행 = 프라이버시 + API 비용 0**이라는 축이 유효하다는 증거.

**4. Alibaba-NLP/DeepResearch — 19,898⭐ (2025-01-09 생성)**
20개월 만에 2만. 다만 **2026-02 이후 푸시 없음** — 성장이 끝났을 가능성이 크다. 급성장 사례이자 "모델 결합형은 유지보수가 끊긴다"는 경고 사례로 함께 읽어야 한다.

**5. MiroMindAI/MiroFlow — 3,103⭐ (2025-08-05 생성, 약 13개월)**
규모는 작지만 "5개 이상 벤치마크 Top-1"을 내세우는 벤치마크 주도 포지셔닝. 같은 팀이 [MiroEval](https://github.com/MiroMindAI/MiroEval) 벤치마크(2026-03 생성)도 운영. **평가 프레임을 직접 소유하는 것이 신생 프로젝트의 진입 전략이 됐다**는 흐름을 보여준다.

**신규 진입 패턴 (2025-09 이후 생성, `gh search repos` 실측)**
스타 300 이하의 소형 신규 레포가 몰리는 방향이 두 갈래로 갈렸다 —
(a) **검증 강화**: `CYC2002tommy/Deep-Research-Agent`(301⭐, DOI 강제 검증 + Scopus/OpenAlex/Semantic Scholar 다중 조회 + APA 7th .docx), `lajosdeme/mole`(298⭐, **강제 예산 + 인용문 검증 + 로컬 데이터 프라이버시 경계**).
(b) **도메인 특화**: `liangdabiao/Claude-Code-Stock-Deep-Research-Agent`(369⭐, **Claude Code 위에서 28개 병렬 서브에이전트로 주식 실사**).
→ 범용 딥리서치는 이미 포화, **신규 진입은 "검증 강화" 아니면 "도메인 특화"로만 뚫리고 있다.**

---

## 4. 공통 아키텍처 패턴과 공통 실패 지점

### 4-1. 사실상 표준이 된 5단 파이프라인

```
쿼리 → [플래너] → [검색] → [읽기] → [합성] → [인용] → 리포트
          ↑                              │
          └──────── 반성/재계획 루프 ──────┘
```

| 단계 | 하는 일 | 구현 편차가 큰 지점 |
|---|---|---|
| **플래너** | 질문을 하위 질문으로 분해, 탐색 폭·깊이 결정 | STORM은 "관점"을 먼저 뽑고, dzhng은 breadth/depth 숫자 파라미터, deepagents는 서브에이전트 위임 |
| **검색** | 다중 쿼리 병렬 발사 | Tavily/Serper/SerpApi(유료) vs SearXNG(셀프호스팅) vs arXiv/PubMed(도메인) |
| **읽기** | HTML→본문 추출, 청킹, 관련성 필터 | Firecrawl / Jina Reader / MinerU-HTML. **비용과 품질이 여기서 갈린다** |
| **합성** | 근거를 섹션 초안으로 압축 | map-reduce vs 반복 정련 vs 트리 탐색(AI-Scientist v2) |
| **인용** | 문장에 출처 부착 | **대부분 사후에 붙임 — 이것이 카테고리 최대 취약점** |
| **반성 루프** | 지식 공백 탐지 후 재검색 | 종료 조건이 제각각: 반복 횟수 / 신뢰도 / **토큰 예산(Jina)** |

**공통 부품**: LiteLLM(모델 추상화) · 검색 API 어댑터 · Markdown 리포트 렌더러 · MCP 서버 노출.
**진행 중인 이동**: 전용 앱 → 범용 하니스(deepagents, deer-flow) 위의 **레시피/스킬**. gpt-researcher가 Claude Skill로 배포되고 anthropics/skills(172,853⭐) 생태계가 커진 것이 같은 흐름이다.

### 4-2. 모두가 실패하는 지점

**① 인용 신뢰성 — 가장 크고, 가장 안 풀린 문제**
대부분의 구현이 인용을 *생성 후 부착*한다. 즉 문장이 실제로 그 출처에서 나왔는지 검증하지 않는다. 2026년 문헌은 이 문제를 정면으로 다루기 시작했다:
- [DeepResearch Bench](https://arxiv.org/abs/2506.11763) — 22개 분야 PhD급 100태스크. **유효 인용 수와 인용 정확도를 별도 지표로 분리.** DeepResearch Bench II(2026-02-06)는 9,430개 세분 이진 루브릭으로 확장.
- ["Why Your Deep Research Agent Fails?"](https://arxiv.org/html/2601.22984v1) — 최종 산출물이 아니라 **전체 리서치 궤적**에서 환각을 평가하는 PIES 분류체계 + DeepHalluBench. 결과 중심 → **과정 중심 평가로의 전환**을 주장.
- [Detecting and Correcting Reference Hallucinations](https://arxiv.org/html/2604.03173v1) — 인문학 DOI 환각률 89.4% vs 자연과학 29.1%. **도메인에 따라 3배 차이.**

→ 방어책은 세 가지뿐이고, 셋 다 소수만 한다: **(a) 인용 시점 검증**(주장↔인용문 대조, `lajosdeme/mole`), **(b) 식별자 강제 검증**(DOI/OpenAlex 조회, `CYC2002tommy/Deep-Research-Agent`), **(c) 근거 우선 파이프라인**(PaperQA2).

**② 유료 검색 API 종속**
dzhng→Firecrawl, HF 예제→SerpApi/Serper, node-DeepResearch→Jina. 결과적으로 (1) 재현하려면 남의 유료 키가 필요하고, (2) 리포트 품질이 자기 코드가 아니라 **붙인 검색 등급의 함수**가 되며, (3) 벤더 가격·정책 변경 한 번에 프로젝트가 흔들린다. 벗어난 사례는 SearXNG 셀프호스팅(local-deep-research)뿐이다.

**③ 토큰 비용**
"깊이" = 더 많은 검색 × 더 많은 페이지 × 더 긴 컨텍스트이므로 비용이 질문 하나당 폭주한다. **예산을 아키텍처 1급 시민으로 만든 건 Jina(토큰 예산 소진 시 종료)와 mole(강제 예산)뿐**이고, 나머지는 반복 횟수 상한이라는 간접 대리로 때운다. 사용자에게 사전 비용 예측을 보여주는 프로젝트는 이 조사에서 확인되지 않음.

**④ 재현성**
같은 질문을 두 번 던지면 다른 리포트가 나온다 — 웹 인덱스가 변하고, 모델이 비결정적이고, 검색 결과 순위가 흔들리기 때문. **캐시된 코퍼스 스냅샷으로 실행을 고정하는 구현을 이 조사에서 확인하지 못했다.** 학술·컴플라이언스 용도에서는 치명적이며, 규제 도메인 진입을 막는 실질 장벽이다.

**⑤ 유지보수 절벽 (조사에서 새로 관측됨)**
스타수와 생존은 무관하다. STORM 31,193⭐가 11개월 정체, Alibaba DeepResearch 19,898⭐가 6개월 정체, `langchain-ai/open_deep_research` 12,680⭐와 `btahir/open-deep-research` 2,141⭐는 아카이브, `TheBlewish/...-Ollama` 3,011⭐는 2024-12 이후 무커밋. **의존 대상을 고를 때 스타가 아니라 `pushed_at`을 봐야 한다.**

**⑥ 라이선스 지뢰**
AGPL-3.0: khoj(36,848⭐), scira(11,854⭐), firecrawl(174,925⭐) → SaaS로 감싸면 공개 의무.
NOASSERTION: AI-Scientist, nickscamara/open-deep-research, camel-ai/owl(null) → 상업 사용 전 법무 확인 필수.
안전지대: Apache-2.0 / MIT(gpt-researcher, STORM, deepagents, PaperQA2, local-deep-research 등).

---

## 5. 경쟁 지형 요약 — 빈칸은 어디인가

**포화된 곳**: 범용 웹 딥리서치("질문 넣으면 인용 달린 리포트"). gpt-researcher·deer-flow·deepagents·개인 구현 수십 개가 이미 있다. 여기로 들어가면 정면 충돌한다.

**아직 빈 곳** — 조사에서 실제로 주인이 없다고 확인된 축:
1. **인용 시점 검증이 기본값인 리서치 에이전트.** 2026년 문헌이 문제를 정의했고 소형 신규 레포 2~3개가 시도 중이지만, 메이저 중에 이걸 기본으로 켜둔 곳이 없다.
2. **재현성**(코퍼스 스냅샷 고정 → 같은 입력에 같은 리포트). 확인된 구현 0건.
3. **사전 비용 예측 + 강제 예산.** Jina와 mole만 부분적으로 시도.
4. **Anthropic 공식 스킬 목록(19개)에 리서치 스킬이 없다.** `discernment-nudge`(출처 비판적 사고)는 있지만 리서치 워크플로 스킬은 없음. 단, **gpt-researcher가 이미 서드파티 Claude Skill로 이 슬롯에 들어와 있다** — 빈칸이 아니라 "선점자 1명 있는 칸"으로 취급할 것.
5. **오프라인/로컬 우선.** local-deep-research가 거의 유일. 사용자의 Ollama 폴백 노선과 정확히 겹치는 축이다.

**참조 순위 제안**: 아키텍처 골격은 `dzhng/deep-research`(가장 읽기 쉬움) → 인용 검증은 `PaperQA2` → 로컬/오프라인은 `local-deep-research` → 예산 통제는 `jina-ai/node-DeepResearch` → 방법론 깊이는 `STORM` 논문(코드는 정체됨).

---

## 부록: 확인 못 한 것 (미확인 목록)

- 모든 레포의 **스타 증가 속도**(월별·6개월 델타) — `stargazers` 타임스탬프 API 접근 불가.
- `langchain-ai/open_deep_research` → `deepagents`의 **공식 승계 여부** (아카이브 사실만 확인).
- 각 프로젝트 self-reported 벤치마크의 **제3자 재현 여부** (local-deep-research 95% SimpleQA, PaperQA2 "초인적 성능", MiroFlow "5개 벤치 Top-1", Alibaba "선도적" 모두 자기 주장).
- `camel-ai/owl`, `OSU-NLP-Group/QUEST`, `simplexai-labs/LiteResearcher`의 **라이선스**(API가 null 반환).
- deer-flow의 **로컬/오프라인 실행 가능 여부**.
- gpt-researcher의 **주장↔출처 일치 검증 로직 유무**(README 수준에서 확인 불가).
- AI-Scientist 산출 논문 품질에 대한 **학계 비판의 구체 출처**.
- Claude Skill 형태로 배포된 리서치 스킬들의 **실제 설치·사용 규모**(skills.sh 통계 미조회).

---

**Sources**
- [assafelovic/gpt-researcher](https://github.com/assafelovic/gpt-researcher) · [stanford-oval/storm](https://github.com/stanford-oval/storm) · [khoj-ai/khoj](https://github.com/khoj-ai/khoj) · [bytedance/deer-flow](https://github.com/bytedance/deer-flow) · [langchain-ai/deepagents](https://github.com/langchain-ai/deepagents) · [langchain-ai/open_deep_research](https://github.com/langchain-ai/open_deep_research) · [dzhng/deep-research](https://github.com/dzhng/deep-research) · [Alibaba-NLP/DeepResearch](https://github.com/Alibaba-NLP/DeepResearch) · [jina-ai/node-DeepResearch](https://github.com/jina-ai/node-DeepResearch) · [LearningCircuit/local-deep-research](https://github.com/LearningCircuit/local-deep-research) · [Future-House/paper-qa](https://github.com/Future-House/paper-qa) · [SakanaAI/AI-Scientist](https://github.com/SakanaAI/AI-Scientist) · [huggingface/smolagents](https://github.com/huggingface/smolagents) · [anthropics/skills](https://github.com/anthropics/skills)
- [DeepResearch Bench (arXiv 2506.11763)](https://arxiv.org/abs/2506.11763) · [Why Your Deep Research Agent Fails? (arXiv 2601.22984)](https://arxiv.org/html/2601.22984v1) · [Detecting and Correcting Reference Hallucinations (arXiv 2604.03173)](https://arxiv.org/html/2604.03173v1) · [MiroEval (arXiv 2603.28407)](https://arxiv.org/pdf/2603.28407) · [ADRA-Bank (arXiv 2512.00986)](https://arxiv.org/pdf/2512.00986) · [deep_research_bench](https://github.com/Ayanami0730/deep_research_bench)
- [LangChain deepagents reference](https://reference.langchain.com/python/deepagents) · [HuggingFace open-deep-research blog](https://huggingface.co/blog/open-deep-research)
