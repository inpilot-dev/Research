# Claude Code 스킬/플러그인/MCP 생태계 내 "research" 포지션 조사

- 조사일: 2026-09-01
- 조사 대상: Claude Code 공식/커뮤니티 스킬·플러그인 마켓플레이스, MCP 레지스트리·디렉터리
- 수치 출처: GitHub REST API(`stargazers_count`, `pushed_at`), npm registry downloads API, 공식 MCP Registry API, `anthropics/claude-plugins-community`의 `marketplace.json` 원본 파싱
- 원칙: 확인 안 된 건 **미확인**으로 명시

---

## TL;DR

1. **research는 이미 레드오션에 가깝다.** Anthropic 공식 커뮤니티 마켓플레이스에 등록된 플러그인은 **2,282개**이고, 그중 research/논문/검색 키워드에 걸리는 것만 **76개**다. ([marketplace.json](https://github.com/anthropics/claude-plugins-community/blob/main/.claude-plugin/marketplace.json))
2. **단, 승자는 "학술 논문 파이프라인" 한 축에 극단적으로 쏠려 있다.** [imbad0202/academic-research-skills](https://github.com/imbad0202/academic-research-skills)가 **44,454★**로 독주하고, 나머지 research 플러그인은 대부분 2~300★ 수준이다. 즉 *일반 웹 리서치* 쪽은 아직 명확한 승자가 없다.
3. **MCP 쪽은 "데이터 접근"만 담당하고 있고, 이미 상용 벤더가 장악했다.** Firecrawl 455K/월, Exa 120K/월, Tavily 118K/월 npm 다운로드. 새로 만들 여지가 거의 없다.
4. **배포 형식 추천: 플러그인(= 스킬 다수 + 서브에이전트 + 훅 번들), MCP 서버는 만들지 말 것.** 근거는 §4.

---

## 1. Claude Code 공식/커뮤니티 스킬·플러그인 생태계

### 1-0. 먼저: Claude Code에 이미 내장된 research 표면

새 도구를 만들기 전에 "이미 기본 제공되는 것"을 기준선으로 잡아야 한다.

| 내장 표면 | 내용 | 링크 |
|---|---|---|
| `WebSearch` 툴 | 모델이 직접 호출하는 웹 검색. 도메인 allow/block 필터 지원. 별도 API 키 불필요 | [docs](https://code.claude.com/docs/en/settings) |
| `WebFetch` 툴 | URL → 마크다운 변환 후 소형 모델로 프롬프트 응답. 15분 캐시 | 동일 |
| `Explore` 서브에이전트 | 읽기 전용 광역 탐색 에이전트(코드베이스 대상). 결론만 회수 | [Subagents](https://code.claude.com/docs/en/sub-agents) |
| `Agent` 툴 + 커스텀 서브에이전트 | 병렬 fan-out 리서치의 기본 프리미티브 | 동일 |
| `Workflow` 툴 | 결정론적 다단계 오케스트레이션(pipeline/parallel/판정단) | 미확인(공개 문서 링크 확인 못 함, 하네스 내장으로만 확인) |

> **함의**: "웹 검색해서 요약" 수준은 이미 무료 내장이다. 신규 research 도구가 팔리려면 *검증·인용·증거 그래프·재현성* 같은 상위 레이어여야 한다. 실제로 상위 플러그인들이 전부 그 방향이다.

### 1-1. 공식 레포 — `anthropics/skills`

- [github.com/anthropics/skills](https://github.com/anthropics/skills) — **172,853★** / 20.5k fork (2026-08-21 push)
- Agent Skills 사양(`spec/`), 템플릿(`template/`), 예제 스킬(`skills/`) 보유
- 수록 카테고리: Creative & Design / Development & Technical / Enterprise & Communication / Document Skills
- **research 전용 스킬은 없다.** 가장 근접한 것은 문서 처리 계열 `docx`, `pdf`, `pptx`, `xlsx`뿐 (PDF 폼 추출·문서 생성).
- → **공식이 research 자리를 비워 두고 있다**는 것이 이 조사의 가장 중요한 발견 중 하나.

### 1-2. 공식 마켓플레이스 2종

Anthropic이 운영하는 공개 마켓플레이스는 두 개다. ([공식 문서](https://code.claude.com/docs/en/plugins#submit-your-plugin-to-the-community-marketplace))

| 마켓플레이스 | 성격 | 등록 방법 |
|---|---|---|
| `claude-plugins-official` | Anthropic 큐레이션. **신청 경로 없음**, 전적으로 Anthropic 재량 | 최초 대화형 실행 시 자동 등록 |
| `claude-community` ([anthropics/claude-plugins-community](https://github.com/anthropics/claude-plugins-community), **3,070★**) | 심사 통과한 서드파티 공개 마켓 | [claude.ai 제출 폼](https://claude.ai/admin-settings/directory/submissions/plugins/new) 또는 [Console 폼](https://platform.claude.com/plugins/submit) |

- 커뮤니티 마켓 등록 절차: `claude plugin validate ./your-plugin` 로컬 통과 → 폼 제출 → 자동 안전성 스크리닝 + 리뷰 → 승인 시 특정 commit SHA로 pin → **야간 동기화**로 `marketplace.json` 반영
- 개인 개발자도 Console 폼으로 제출 가능(Team/Enterprise 조직 불필요)

### 1-3. 커뮤니티 마켓플레이스 research 항목 — **전수 나열**

`marketplace.json` 직접 파싱 결과: **전체 2,282개 플러그인 중 research/논문/인용/학술/웹검색 키워드 매칭 76개.** 그중 실제로 research가 본질인 것만 추리면 아래와 같다.

#### (a) 범용 딥리서치 / 웹 리서치

| 플러그인 | 설명 | 소스 |
|---|---|---|
| `deep-research` | 멀티에이전트 딥리서치 파이프라인. 인터넷 리서치 + 레포 분석 + 스키마 기반 구조화 리서치 + 미디어 리서치(NotebookLM 경유). Agent Team 조율 | [oduffy-delphi/deep-research-claude](https://github.com/oduffy-delphi/deep-research-claude) |
| `learn` | `/learn <주제>` → 웹에서 ~20개 소스 검색, 100점 스코어링, RAG 최적화 인덱스가 붙은 학습 가이드 생성 | [agent-sh/learn](https://github.com/agent-sh/learn) |
| `scout` | 프라이버시 인식 툴 선택 기반 웹 검색·페치. 모호한 질문 → 최적화된 멀티엔진 쿼리, 결과 품질 평가 후 재검색. HyDE 시맨틱 기법 포함 | [shidoyu/scout](https://github.com/shidoyu/scout) |
| `searchwave` | 리서치 합성 플러그인. Wave(빠른 수집) / Deepwave(심층) 두 커맨드 계열. "minimum viable context collection" 컨셉 | [rowbradley/searchwave](https://github.com/rowbradley/searchwave) |
| `arcanum` | 디버깅·코드리뷰·**딥리서치**·기술문서·반자율 개발 워크플로. 병렬 이론 검증, 팀 기반 리서치, war room | [burnsbert/claude-arcanum](https://github.com/burnsbert/claude-arcanum) |
| `auto-research` | Karpathy의 autoresearch 방법론 기반. 5개 병렬 에이전트(도메인 전문가·품질 감사·경쟁 분석·갭 분석 등) 스폰해 스킬 자체를 개선 | [gyoz-ai/auto-research](https://github.com/gyoz-ai/auto-research) |
| `ultrapowers` | 코드 작성 전 지식 검증을 강제하는 research-driven 개발 워크플로. Superpowers를 딥리서치·스킬 감사로 확장 | [ennio-datatide/ultrapowers](https://github.com/ennio-datatide/ultrapowers) |
| `foresight-engine` | 예측 질문 → 4시나리오(Probable/Plausible/Possible/Preferable) 구조 분석, 라이브 데이터 백업 | [isanthoshgandhi/foresight-engine](https://github.com/isanthoshgandhi/foresight-engine) |
| `popper-probe` | Karl Popper 반증주의 기반 리서치 컴패니언. 가설을 반증하는 방향으로 심문하는 적대적 슈퍼바이저 | [mashathepotato/popper-probe](https://github.com/mashathepotato/popper-probe) |
| `colosseum` | 검색 결과로 반증되는 다중 에이전트 토론 + 점수화. 최종 합성 전에 Devil's Advocate 투입 | 마켓 등재(소스 URL 미확인) |
| `pinrag` | 로컬 RAG. PDF·YouTube·GitHub 레포·Discord 익스포트 인덱싱 후 인용과 함께 질의. `pinrag-mcp` 번들 | [ndjordjevic/pinrag-plugin](https://github.com/ndjordjevic/pinrag-plugin) |
| `wiki-knowledge-complier` | Ingest → Compile → Link → Query → Write-back → Improve 지식관리 루프 | 마켓 등재(소스 URL 미확인) |

#### (b) 학술 논문 파이프라인

| 플러그인 | 설명 | 소스 |
|---|---|---|
| `research-co-pilot` | Claude Code + claude.ai용 종합 리서치 코파일럿. **13개 스킬**: 문헌리뷰·방법론·연구윤리 심사·데이터 분석·질적 코딩·브레인스토밍·원고 작성 | [Marazii/research-co-pilot](https://github.com/Marazii/research-co-pilot) |
| `scriptorium-cowork` | 반쯤 잡힌 주제 → 방어 가능한 문헌리뷰까지. 지시형 인터뷰, 연구질문 도출, **PRISMA 감사** 기반 검색·합성 | [Jerrymwolf/Scriptorium-Cowork](https://github.com/Jerrymwolf/Scriptorium-Cowork) |
| `paper-search` | OpenAlex 경유 논문 검색. 키워드/DOI 조회, 페이지네이션·정렬 | [ykdojo/paper-search](https://github.com/ykdojo/paper-search) |
| `paper-review-system` | 자동 논문 리뷰. PDF 파싱(marker-pdf + PyMuPDF) + 레퍼런스 검증(CrossRef + DBLP + Semantic Scholar) + SOTA 비교 | [lidapengpeng/paper-review-system](https://github.com/lidapengpeng/paper-review-system) |
| `read-paper` | 논문 심층 분석(영/중 이중언어). PDF 경로·붙여넣기 텍스트·arXiv 링크 입력 → 5섹션 구조화 리포트 | [xiaotianzhao/read-paper-plugin](https://github.com/xiaotianzhao/read-paper-plugin) |
| `deep-review` | 논문·기술 산출물 엄밀 리뷰. 연구자의 "edit volume" 감소가 목표 | [dipakkrishnan/deep-review-skill](https://github.com/dipakkrishnan/deep-review-skill) |
| `phd-deepread` | 학술 PDF → Obsidian용 구조화 문헌 노트 + 비판적 사고 캔버스. 증거 표, validity 매트릭스 | [heleninsights-dot/phd-deepread-workflow](https://github.com/heleninsights-dot/phd-deepread-workflow) |
| `thesis-engine` | 논문/장문 글쓰기용 리서치 피더. 라이브·저경쟁 주제 스캔, 5개 소스군에서 1차 자료 수집 | [estevanhernandez-stack-ed/Thesis-Engine](https://github.com/estevanhernandez-stack-ed/Thesis-Engine) |
| `vibe-thesis` | Claude Code 내 학위논문 저작. 학위논문·석사논문·장문 연구논문 스캐폴딩 및 공동집필 | [estevanhernandez-stack-ed/Vibe-Thesis](https://github.com/estevanhernandez-stack-ed/Vibe-Thesis) |
| `arcdeck` | 학술 PDF → 내러티브 PPT. **13개 전용 에이전트**, discourse parsing + critique-revise-judge 루프 | [RehgLab/ArcDeck-Claude-Plugin](https://github.com/RehgLab/ArcDeck-Claude-Plugin) |
| `content-analysis` | 학술 연구용 과학적 내용분석. 코드북 개발, 질적/양적 코딩, 주제 분석 | [PeterMalmkjaer/content-analysis-plugin](https://github.com/PeterMalmkjaer/content-analysis-plugin) |
| `thesis-polish` | 중국 학부생 대상 학술 글 자연스러움·가독성 개선 | 마켓 등재(소스 URL 미확인) |
| `github-reuse-assistant` | ML/DL GitHub 프로젝트 재현 6단계 워크플로(clone → 학습·테스트 성공까지) | 마켓 등재(소스 URL 미확인) |

#### (c) 인용 검증 / 출처 검증 — **이 조사에서 가장 밀도 높은 니치**

| 플러그인 | 설명 | 소스 |
|---|---|---|
| `bibtidy` | BibTeX 엔트리 내용을 Google Scholar·CrossRef 대조 검증 | [mathpluscode/bibtidy](https://github.com/mathpluscode/bibtidy) |
| `sourceverify` | SourceVerify API로 학술 인용·레퍼런스 검증 | [SourceVerify-ai/sourceverify-skill](https://github.com/SourceVerify-ai/sourceverify-skill) |
| `cite2fn` | Word 문서 내 하이퍼링크 인용·괄호 참조·저자-연도 언급을 Bluebook 각주/미주로 변환 | [anitasrinivasan/cite2fn](https://github.com/anitasrinivasan/cite2fn) |

#### (d) 도메인 특화 리서치

| 플러그인 | 도메인 | 소스 |
|---|---|---|
| `nagomi` | PubMed 3,600만+ 생의학 논문. PICO 구조 쿼리, **GRADE** 신뢰도 등급 증거 합성 | [avivlyweb/nagomi-pubmed-plugin](https://github.com/avivlyweb/nagomi-pubmed-plugin) |
| `bettercallclaude` | 스위스 법률. 20 에이전트 / 19 커맨드 / 14 스킬 / **9 MCP 서버**. BGE/ATF/DTF 판례 리서치 + 인용 검증 | 마켓 등재(소스 URL 미확인) |
| `fluidityiq-patent-intelligence` | 특허. FluidityIQ Patents MCP 경유 글로벌 특허 시맨틱 선행기술 검색 | 마켓 등재(소스 URL 미확인) |
| `credit-memo` | 금융. SEC EDGAR + SerpApi + 신용평가사에서 3~5년 재무 자동 수집 | 마켓 등재(소스 URL 미확인) |
| `patristic` | 러시아 정교회 교부 문헌 코퍼스(~2,100 저작, 86 교부, 726K 문단, 1.98M bge-m3 임베딩) | 마켓 등재(소스 URL 미확인) |
| `techknowmad-ai-skills` | 자율 AI/ML 리서치랩 운영 20 스킬(research-commander, patent-researcher 등) | 마켓 등재(소스 URL 미확인) |
| `saas-corpus` | B2B SaaS 사례 지식베이스 153 엔트리(인용 백업) | 마켓 등재(소스 URL 미확인) |

#### (e) 검색 백엔드 브릿지 (플러그인 형태로 배포된 검색 API)

| 플러그인 | 백엔드 | 소스 |
|---|---|---|
| `gsearch` | Google Search grounding 무료. `google_search` MCP 툴 + 인라인 `[1][2][3]` 인용. **API 키 불필요** | [daanielcruz/gsearch-mcp](https://github.com/daanielcruz/gsearch-mcp) |
| `serpapi-claude-plugin` | SerpApi. Google·Amazon·YouTube·**Google Scholar** 등 100+ 엔진 | [serpapi/serpapi-claude-plugin](https://github.com/serpapi/serpapi-claude-plugin) |
| `ceramic-search` | Ceramic AI 고품질 에이전트용 웹 검색 MCP | [CeramicTeam/ceramic-claude-code-plugins](https://github.com/CeramicTeam/ceramic-claude-code-plugins) |
| `anakin-claude-plugin` | 웹사이트 → LLM-ready 데이터. 단일/배치(최대 10 URL) 스크레이핑 + AI 웹 검색 | [Anakin-Inc/anakin-claude-plugin](https://github.com/Anakin-Inc/anakin-claude-plugin) |

### 1-4. GitHub 스타 기준 실제 채택도 (2026-09-01, GitHub API 직접 조회)

| 레포 | ★ | 최근 push | 성격 |
|---|---:|---|---|
| [anthropics/skills](https://github.com/anthropics/skills) | **172,853** | 2026-08-21 | 공식 스킬 사양·예제 |
| [ComposioHQ/awesome-claude-skills](https://github.com/ComposioHQ/awesome-claude-skills) | **74,167** | 2026-08-10 | 큐레이션 목록 |
| [hesreallyhim/awesome-claude-code](https://github.com/hesreallyhim/awesome-claude-code) | **53,310** | 2026-09-01 | 큐레이션 목록 |
| **[imbad0202/academic-research-skills](https://github.com/imbad0202/academic-research-skills)** | **44,454** | 2026-08-30 | **research 카테고리 1위** |
| [wshobson/agents](https://github.com/wshobson/agents) | 39,310 | 2026-08-31 | 멀티하네스 서브에이전트 마켓 |
| [davila7/claude-code-templates](https://github.com/davila7/claude-code-templates) | 30,472 | 2026-09-01 | CLI 설정·모니터링 (내부에 `scientific/literature-review` 스킬 포함) |
| [travisvn/awesome-claude-skills](https://github.com/travisvn/awesome-claude-skills) | 14,916 | 2026-04-28 | 큐레이션 목록 (research 항목 없음) |
| [anthropics/claude-plugins-community](https://github.com/anthropics/claude-plugins-community) | 3,070 | 2026-08-25 | 공식 커뮤니티 마켓 미러 |
| [rohitg00/awesome-claude-code-toolkit](https://github.com/rohitg00/awesome-claude-code-toolkit) | 2,577 | 2026-05-12 | 툴킷 |
| [lingzhi227/agent-research-skills](https://github.com/lingzhi227/agent-research-skills) | 301 | 2026-02-27 | 멀티소스 학술 검색 스킬 |
| [joshzyj/open-scholar-skill](https://github.com/joshzyj/open-scholar-skill) | 134 | 2026-08-29 | 로컬 벡터 DB + GraphRAG 문헌리뷰 |
| [imbad0202 외] `JeanDiable/academic-research-plugin` | 20 | 2026-03-25 | AI/ML 박사용 8 스킬 |
| [marciob/skill-research-papers](https://github.com/marciob/skill-research-papers) | 6 | 2026-05-10 | arXiv/OpenAlex/ACM/DBLP/S2/PubMed/SSRN 통합 검색 |
| [Defiect/deep-research-plugin](https://github.com/Defiect/deep-research-plugin) | 2 | 2026-02-08 | 증거 그래프 + 품질 게이트 |

> **분포의 모양**: 44,454 → 301 → 134 → 20 → 6 → 2. **극단적 롱테일**이다. 1등 하나가 카테고리 전체를 먹었고, 2등부터는 사실상 무명이다.

### 1-5. 카테고리 1위 해부 — `academic-research-skills` (44,454★)

배포 형식과 기술 선택을 그대로 참고할 만한 레퍼런스다.

- **구성**: 4개 스킬 / **~40개 전문 에이전트**
  1. Deep Research v2.12.1 — 13-에이전트 리서치 팀, 8개 모드(full research, systematic review, Socratic-guided 등)
  2. Academic Paper v3.3.1 — 12-에이전트 집필 파이프라인, 11개 모드
  3. Academic Paper Reviewer v1.11.1 — 7-에이전트 다관점 리뷰
  4. Academic Pipeline v3.21.1 — 10단계 오케스트레이터 + 무결성 검증 게이트
- **배포**: `/plugin marketplace add Imbad0202/academic-research-skills` (권장) / git clone + `~/.claude/skills/` 심링크 / Claude Science 직접 import
- **MCP를 쓰지 않는다.** 검증은 전부 **bash/python 스크립트**(인용 검증, 시점 감사, 클레임 정합성). API는 Semantic Scholar, OpenAlex, Crossref, arXiv resolver를 직접 호출
- **캐시**: `~/.cache/ars/verification.db` (SQLite, 90일 TTL)
- **차별점**: 인간 개입 강제 게이트(Stage 2.5, 4.5), S2+OpenAlex+Crossref 삼각검증, Material Passport(실험·프로버넌스·개정 이력 메타데이터)
- **비용 공개**: ~15,000단어 논문 풀 파이프라인 $4~6
- **라이선스**: CC-BY-NC 4.0 (비상업 한정)
- 다국어: 영/번체중/일/한/간체중

> **가장 중요한 시사점**: 카테고리 1위가 **MCP 서버를 쓰지 않았다**. 스킬 + 서브에이전트 + 로컬 스크립트만으로 44K★를 찍었다.

---

## 2. MCP 생태계 — research 관련 서버

### 2-1. 공식 레퍼런스 서버 ([modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers), 89,990★)

- **활성 레퍼런스 서버**: Fetch(웹 콘텐츠 페치·변환), Git, Memory(지식그래프 영속 메모리), Everything, Filesystem, Sequential Thinking, Time
- **아카이브/폐기**: Brave Search(→ Brave 공식 서버로 대체), GitHub, PostgreSQL, Puppeteer, Slack
- → **공식 레퍼런스에는 research/학술 서버가 없다.** `Fetch` 하나가 유일한 웹 접점이며, 레포 스스로 "교육용 레퍼런스 구현이지 프로덕션 솔루션이 아니다"라고 명시.

### 2-2. 공식 MCP Registry ([registry.modelcontextprotocol.io](https://registry.modelcontextprotocol.io), [modelcontextprotocol/registry](https://github.com/modelcontextprotocol/registry) 7,207★)

Registry API 직접 조회 결과 (2026-09-01). **주의: 응답에 버전 중복이 섞여 있어 "고유 서버 수"를 별도 집계했다.**

| 검색어 | 반환 엔트리 | 고유 서버 |
|---|---:|---:|
| `arxiv` | 57 | **8** |
| `pubmed` | 82 | **5** |
| `openalex` | 42 | **2** |
| `exa` | 100+ | **26** |
| `perplexity` | 31 | **9** |
| `firecrawl` | 24 | **3** |
| `tavily` | 4 | **4** |
| `citation` | 29 | 미집계 |
| `semantic scholar` | **0** | **0** |
| `web search` | **0** | **0** |
| `deep research` | 0 (완전일치 검색 한계) | 0 |

> `semantic scholar` / `web search` 0건은 레지스트리 검색이 토큰 완전일치 위주라 발생한 것으로 보인다 — **해당 서버가 없다는 뜻이 아니다**(PulseMCP에는 존재). 레지스트리 색인 커버리지가 아직 얇다는 신호로 읽는 게 맞다.

`research` 검색 시 반환된 서버(대부분 상업용 SaaS 브릿지):
Fodda Deep Research, Fodda Topic & Trend Research, **LivingMeta — AI in Research**(AI-in-Research 코퍼스 12,400편 논문·갭·우선순위 아젠다 read-only MCP), OpenHelm Deep Research, Smithery Financial Research, Market Research API(TrendsAPI), Market Research Trends MCP, UserIntuition Research, FRTracker, alpha402x Equity Research, BiaEdge Immigration Research, Crawdar Business Research, Money-Engine x402 Research, DropWatch Research Intel.

→ **레지스트리의 "research"는 학술이 아니라 시장/금융/법률 인텔리전스가 다수다.**

### 2-3. 웹 검색·크롤 MCP — 실제 인기도

npm 월간 다운로드 (npm registry downloads API, last-month, 2026-09-01 기준):

| 패키지 | 월 다운로드 | GitHub ★ | 레포 |
|---|---:|---:|---|
| `@modelcontextprotocol/server-sequential-thinking` | **484,365** | (모노레포) | [modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers) |
| `firecrawl-mcp` | **455,722** | **7,358** | [firecrawl/firecrawl-mcp-server](https://github.com/firecrawl/firecrawl-mcp-server) |
| `exa-mcp-server` | **120,238** | 4,949 | [exa-labs/exa-mcp-server](https://github.com/exa-labs/exa-mcp-server) |
| `tavily-mcp` | **117,690** | 2,364 | [tavily-ai/tavily-mcp](https://github.com/tavily-ai/tavily-mcp) |
| `@modelcontextprotocol/server-brave-search` | 92,927 | (아카이브됨) | 동일 |
| Perplexity 공식 | 미확인(npm 패키지명 미확인) | 2,494 | [perplexityai/modelcontextprotocol](https://github.com/perplexityai/modelcontextprotocol) |

> **Sequential Thinking이 Firecrawl과 동급 1위**라는 점이 흥미롭다. 사용자들이 "검색 도구"만큼이나 "추론 구조화 도구"를 설치하고 있다는 뜻이다. Smithery 사용량 랭킹에서도 Sequential Thinking이 5,550+ uses로 1위, Brave Search 680+, Web Research 533+로 격차가 크다 ([pedrojaques99/popular-mcp-servers](https://github.com/pedrojaques99/popular-mcp-servers) 집계, 다만 이 수치는 스냅샷 시점이 불명확 — **부분 미확인**).

### 2-4. 학술 MCP 서버

| 서버 | 커버리지 | ★ | 링크 |
|---|---|---:|---|
| `blazickjp/arxiv-mcp-server` | arXiv 검색·전문 다운로드·시맨틱 검색·인용 그래프·알림. 원본 LaTeX 섹션 읽기, arXiv 메타데이터 BibTeX | **3,099** | [github](https://github.com/blazickjp/arxiv-mcp-server) |
| `cyanheads/openalex-mcp-server` | OpenAlex 2억 7천만+ 출판물. STDIO & HTTP | 미확인 | [MCP Registry](https://registry.modelcontextprotocol.io) 등재 |
| `cyanheads/pubmed-mcp-server` | PubMed/NCBI E-utilities. 검색·페치·인용·탐색 | 미확인 | 동일 |
| `Taru0208/pubmed-mcp-server` | PubMed 3,600만+ + ClinicalTrials.gov | 미확인 | 동일 |
| `andybrandt/mcp-simple-arxiv` | arXiv 검색·읽기 | 199 | [github](https://github.com/andybrandt/mcp-simple-arxiv) |
| `JackKuo666/semanticscholar-MCP-Server` | Semantic Scholar API | 80 | [github](https://github.com/JackKuo666/semanticscholar-MCP-Server) — **2025-03-25 이후 push 없음(사실상 방치)** |
| `reading-plus-ai/mcp-server-deep-research` | 딥리서치 | 214 | [github](https://github.com/reading-plus-ai/mcp-server-deep-research) — **2025-03-25 이후 push 없음** |
| Academic Author Network | Semantic Scholar + OpenAlex + Crossref + Google Scholar 집계, 협력자 발굴 | 미확인 | [PulseMCP](https://www.pulsemcp.com/servers/academic-author-network) |
| `arxivsub/arxivsub-mcp` | arXiv + 주요 AI/ML/CV/NLP/로보틱스 학회 논문 + related work | 미확인 | MCP Registry 등재 |

### 2-5. 디렉터리 현황

| 디렉터리 | 성격 | 링크 |
|---|---|---|
| 공식 MCP Registry | 커뮤니티 주도 공식 레지스트리, API 공개 | [registry.modelcontextprotocol.io](https://registry.modelcontextprotocol.io) |
| Smithery | 사용량(uses) 지표 제공. Sequential Thinking 1위 | [smithery.ai](https://smithery.ai) |
| mcp.so | 대형 디렉터리 ([chatmcp/mcpso](https://github.com/chatmcp/mcpso), 2,105★) | [mcp.so](https://mcp.so) |
| PulseMCP | arXiv·Semantic Scholar 등 학술 서버 목록이 가장 촘촘 | [pulsemcp.com](https://www.pulsemcp.com) |
| MCP Toplist | 랭킹 | [mcptoplist.com](https://mcptoplist.com) |

> **MCP 학술 서버의 구조적 문제**: 상위 몇 개(`blazickjp/arxiv-mcp-server` 3,099★)를 빼면 대부분 **2025년 초에 만들어지고 방치**되어 있다. `JackKuo666/semanticscholar-MCP-Server`, `reading-plus-ai/mcp-server-deep-research` 둘 다 2025-03 이후 커밋 없음. 유지보수 공백이 크다.

---

## 3. 스킬 vs MCP 서버 vs 플러그인 vs 서브에이전트

### 3-1. 정의와 경계 (공식 문서 기준)

| 형식 | 본질 | 공식 문서 |
|---|---|---|
| **Agent Skill** | `SKILL.md` 하나. YAML frontmatter(`description`) + 절차 지시문. **본문은 쓸 때만 로드**되므로 안 쓰면 토큰 비용 ≈ 0. `/skill-name`으로 직접 호출하거나 Claude가 맥락 보고 자동 호출 | [Skills](https://code.claude.com/docs/en/skills) |
| **MCP 서버** | 외부 시스템 접근 프로토콜. 툴 스키마가 컨텍스트에 상주(단, Claude Code는 deferred tool + ToolSearch로 지연 로딩 지원) | [MCP](https://code.claude.com/docs/en/mcp) |
| **서브에이전트** | `agents/` 디렉터리의 에이전트 정의. 별도 컨텍스트 창, 독자 시스템 프롬프트·툴 제한·모델 지정. 병렬 fan-out의 단위 | [Subagents](https://code.claude.com/docs/en/sub-agents) |
| **플러그인** | 위 셋 + 훅 + LSP + 백그라운드 모니터 + 기본 설정을 하나로 묶은 **배포 단위**. `.claude-plugin/plugin.json` 매니페스트 | [Plugins](https://code.claude.com/docs/en/plugins) |

**중요**: 이건 4지선다가 아니다. **플러그인은 나머지 셋의 컨테이너다.** 실제 선택지는 "① 무엇을 만들 것인가(스킬/에이전트/MCP)"와 "② 어떻게 배포할 것인가(standalone `.claude/` vs 플러그인)" 두 축이다.

플러그인이 담을 수 있는 것 (공식 문서 디렉터리 표):

```
plugin-root/
├── .claude-plugin/plugin.json   # 매니페스트
├── skills/<name>/SKILL.md       # 스킬
├── commands/                    # 구형 플랫 커맨드(신규는 skills/ 권장)
├── agents/                      # 서브에이전트
├── hooks/hooks.json             # 이벤트 훅
├── .mcp.json                    # MCP 서버 설정
├── .lsp.json                    # LSP 서버
├── monitors/monitors.json       # 백그라운드 모니터
├── bin/                         # Bash PATH에 추가되는 실행파일
└── settings.json                # 기본 설정(agent, subagentStatusLine)
```

- 커스텀 커맨드는 **스킬로 통합**되었다. `.claude/commands/deploy.md`와 `.claude/skills/deploy/SKILL.md` 둘 다 `/deploy`를 만든다. 신규는 `skills/` 권장.
- 스킬 하나짜리 플러그인은 `SKILL.md`를 플러그인 루트에 바로 둬도 된다.
- 플러그인 스킬은 **항상 네임스페이스**된다(`/plugin-name:skill-name`) — 충돌 방지.
- `claude plugin init my-tool` → `~/.claude/skills/my-tool/`에 스캐폴딩, 마켓/설치 절차 없이 `my-tool@skills-dir`로 자동 로드.

### 3-2. 장단점 비교

| 축 | 스킬 | MCP 서버 | 서브에이전트 | 플러그인(번들) |
|---|---|---|---|---|
| **미사용 시 토큰 비용** | ≈0 (progressive disclosure) | 툴 스키마 상주(Claude Code는 deferred+ToolSearch로 완화) | 정의만 상주, 실행 시 별도 컨텍스트 | 포함물에 따름 |
| **설치 마찰** | 파일 복사 / 플러그인 설치 | **높음** — 런타임(node/python/uvx) + **API 키 발급** + 설정 파일 | 파일 복사 | `/plugin install` 한 줄 |
| **오프라인 동작** | 가능 | 대부분 불가(외부 API) | 가능 | 포함물에 따름 |
| **라이브 데이터 접근** | 불리(bash/curl로 우회 가능) | **강점** | 불리 | MCP 포함 시 가능 |
| **절차·판단·품질기준 인코딩** | **강점** | 불가(툴은 "무엇에 접근"만 답함) | 강점(역할 분리) | 강점 |
| **병렬 처리 / 컨텍스트 격리** | 불가 | 불가 | **강점** | 강점 |
| **버전 관리·배포** | 수동 | 패키지 매니저(npm/pypi) | 수동 | **강점** — SHA pin, 버전 필드, 마켓 |
| **크로스 하네스 이식성** | Codex/Cursor 등도 SKILL.md 채택 확산 중 | **가장 높음**(표준 프로토콜) | 하네스별 상이 | Claude Code/Cowork 중심 |
| **디버깅 난이도** | 낮음(마크다운) | 높음(프로세스·전송·인증) | 중간 | 중간 |

한 줄 요약(업계 공통 프레이밍, [Atlan](https://atlan.com/know/ai-agent/ai-agent-skills/agent-skills-vs-mcp/) · [The Circuit](https://metacircuits.substack.com/p/the-285-billion-question-skills-vs) · [Developers Digest](https://www.developersdigest.tech/blog/mcp-servers-vs-agent-skills-2026)):
> **MCP는 "에이전트가 무엇에 닿을 수 있는가"에 답하고, 스킬은 "에이전트가 그 일을 어떻게 해야 하는가"에 답한다.**
> 데이터가 호출 간에 변하면 MCP, 몇 주 단위로 안정적이면 스킬.

### 3-3. 현재 채택 추세 — 관측된 사실

1. **research 카테고리 1위가 MCP를 안 쓴다.** `academic-research-skills`(44,454★)는 스킬 + ~40 서브에이전트 + bash/python 스크립트 조합이고, Semantic Scholar/OpenAlex/Crossref/arXiv를 **직접 HTTP 호출**한다. MCP 계층을 건너뛴 것이 채택에 불리하게 작용하지 않았다.
2. **커스텀 커맨드 → 스킬 통합.** Anthropic이 `commands/`를 스킬로 흡수하고 신규는 `skills/`를 권장한다. 스킬이 확장의 기본 단위가 되었다.
3. **플러그인이 배포 표준으로 굳었다.** 2,282개 등록, 공식 심사 파이프라인 + commit SHA pin + 야간 동기화. 초기 생태계를 지배하던 서브에이전트 컬렉션([wshobson/agents](https://github.com/wshobson/agents) 39,310★)조차 지금은 스스로를 "멀티하네스 **agentic plugin marketplace**"로 재정의했다.
4. **MCP는 상용 데이터 벤더 계층으로 수렴 중.** Firecrawl·Exa·Tavily·Perplexity·SerpApi 등 API 사업자가 공식 서버를 내고, 개인이 만든 학술 MCP 서버는 대부분 2025년 초 이후 방치.
5. **번들 규모가 커지고 있다.** 상위 플러그인들이 13~40 에이전트, 10~20 스킬, 다중 MCP를 한 패키지로 낸다(`bettercallclaude`: 20 에이전트/19 커맨드/14 스킬/9 MCP). "단일 스킬 하나"로는 눈에 띄지 않는 국면.
6. **검증·인용이 차별화 축이다.** 상위 research 플러그인 대부분이 PRISMA·GRADE·삼각검증·증거 그래프·품질 게이트를 세일즈 포인트로 내세운다. 단순 검색·요약은 내장 `WebSearch`와 경쟁이 안 된다.

---

## 4. 배포 형식 추천 (1개)

### **플러그인으로 배포하라 — 내용물은 "스킬 다수 + 서브에이전트", MCP 서버는 만들지 말 것.**

구체적으로:

```
research-plugin/
├── .claude-plugin/plugin.json
├── skills/
│   ├── deep-research/SKILL.md      # 오케스트레이션 절차
│   ├── source-verify/SKILL.md      # 인용·출처 검증 절차
│   └── synthesize/SKILL.md         # 합성·리포트 포맷
├── agents/
│   ├── scout.md                    # 병렬 소스 발굴(저비용 모델)
│   ├── analyst.md                  # 심층 독해·클레임 추출
│   └── skeptic.md                  # 적대적 반증
├── hooks/hooks.json                # 산출물 없이 완료 못 하게 막는 품질 게이트
└── scripts/                        # OpenAlex/Crossref/arXiv 직접 호출 (bash/python)
```

**이유:**

1. **플러그인이 유일한 배포 채널이다.** 공식 커뮤니티 마켓(2,282개)에 들어가는 유일한 형식이고, `/plugin install` 한 줄로 끝난다. 스킬만 배포하면 사용자가 수동 clone + 심링크를 해야 하고, 실제 카테고리 1위도 "플러그인 설치를 권장(recommended)"으로 안내한다.
2. **플러그인은 나머지 셋을 다 담는다.** 형식 선택으로 잃는 게 없다. 나중에 MCP가 필요해지면 `.mcp.json`만 추가하면 된다 — 되돌릴 수 없는 결정이 아니다.
3. **MCP 서버를 직접 만들 이유가 없다.**
   - 데이터 소스(arXiv/OpenAlex/Crossref/Semantic Scholar)는 **전부 인증 없는 공개 REST API**다. MCP 계층을 하나 더 얹으면 사용자에게 런타임 설치 + 설정 파일 편집이라는 마찰만 추가된다.
   - 웹 검색은 이미 내장 `WebSearch`가 무료로 있고, 더 필요하면 Firecrawl(455K/월)·Exa(120K)·Tavily(118K)를 사용자가 이미 깔아 뒀을 확률이 높다. 여기서 경쟁하면 진다.
   - 44,454★ 1위가 MCP 없이 그 자리에 갔다. 반례가 없다.
   - 오프라인/네트워크 제한 환경에서 MCP 서버는 첫 번째로 깨지는 지점이다.
4. **서브에이전트는 반드시 포함해야 한다.** research의 본질은 fan-out(다수 소스 병렬 수집)과 컨텍스트 격리(각 소스를 깊게 읽되 메인 컨텍스트를 오염시키지 않음)다. 이건 스킬 텍스트만으로는 안 되고 별도 컨텍스트 창이 필요하다. 상위 플러그인들이 예외 없이 10~40 에이전트를 쓰는 이유.
5. **훅으로 품질 게이트를 강제하는 게 차별화 지점이다.** `Defiect/deep-research-plugin`이 명시한 "hooks prevent agents from completing tasks without required deliverables" 패턴 — 인용 없는 클레임, 산출물 없는 완료를 기계적으로 차단. 스킬 텍스트는 모델이 무시할 수 있지만 훅은 못 무시한다.

**포지셔닝 관련 경고 (범위 밖이지만 명시):** 학술 논문 파이프라인은 44K★ 1위가 이미 점유했다. 일반 웹 리서치 + 증거 검증 쪽이 비어 있고, 공식 `anthropics/skills`에도 research 스킬이 없다.

---

## 부록: 확인하지 못한 것 (미확인)

- Smithery의 최신 사용량 수치 — 인용한 랭킹([pedrojaques99/popular-mcp-servers](https://github.com/pedrojaques99/popular-mcp-servers))의 **스냅샷 시점이 불명확**. Smithery 공식 API로 재확인 못 함
- `claude-plugins-official`(Anthropic 큐레이션 마켓)의 **전체 플러그인 목록** — 레포/JSON 공개 경로를 찾지 못함. research 항목 유무 미확인
- 플러그인별 **실제 설치 수** — 마켓플레이스가 설치 카운트를 공개하지 않아 GitHub ★로 대리 측정. `colosseum`, `thesis-polish`, `bettercallclaude`, `fluidityiq-patent-intelligence`, `credit-memo`, `patristic`, `techknowmad-ai-skills`, `saas-corpus`, `wiki-knowledge-complier`, `github-reuse-assistant`는 `marketplace.json`에 소스 URL이 표준 GitHub 형태가 아니거나 확인하지 못해 ★ 미집계
- Perplexity 공식 MCP의 **npm 패키지명/다운로드 수** — 패키지명 미확인
- `cyanheads/openalex-mcp-server`, `cyanheads/pubmed-mcp-server`, `Taru0208/pubmed-mcp-server`, `arxivsub/arxivsub-mcp`의 **GitHub ★** — 레지스트리에만 확인, API 조회 미실시
- MCP Registry의 **전체 서버 수** — API 응답 메타데이터가 페이지 단위 카운트만 반환해 총계 확인 못 함
- `Workflow` 툴의 공개 문서 링크 — 하네스 내장으로만 확인, docs.claude.com에서 페이지 찾지 못함
- `mcp.so`, `MCP Toplist`의 research 카테고리 **정량 지표** — 사이트 API 미확인
