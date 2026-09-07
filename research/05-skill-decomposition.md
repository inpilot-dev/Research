# 상위 research 플러그인의 스킬 분해 구조 해부

조사일: 2026-09-01 · 조사자: Orca worker (task_3cc5ead87751)
조사 방법: 전부 `gh api repos/<r>/git/trees/<branch>?recursive=1`로 **실제 파일 트리를 받고**, `gh api repos/<r>/contents/<path>`로 **SKILL.md 원문을 base64 디코드해 직접 읽음**. 아래 파일 목록은 전부 실제 API 응답이다. 추측으로 채운 항목 없음.

**접근 실패: 없음. 8개 레포 전부 접근 성공.**
단, `assafelovic/gpt-researcher`에는 **`skills/` 디렉터리가 존재하지 않는다**(태스크 전제와 다름 — 5절 참조).

---

## 0. 한눈에 보는 비교표 (전부 실측)

| 레포 | ★ | 스킬 수 | 에이전트 수 | 커맨드 수 | hooks.json | 분해 축 |
|---|---|---|---|---|---|---|
| Imbad0202/academic-research-skills | 44,455 | **4** | **39 (+노출 3)** | 16 | **있음** | 산출물/역할 (스킬) + 파이프라인 단계 (에이전트) |
| Marazii/research-co-pilot | 13 | **15** | 6 | 16 | 없음 | **연구 활동(작업 종류)** |
| Jerrymwolf/Scriptorium-Cowork | 0 | **14** | 0 | 0 | 없음 | **순수 파이프라인 단계(동사)** |
| oduffy-delphi/deep-research-claude | 0 | **1** | 6 (+notebooklm 3) | 2 (+1) | 없음 | 에이전트 역할(scout/specialist/synthesizer) |
| avivlyweb/nagomi-pubmed-plugin | 0 | **5** | 0 | 0 | 없음 | **도메인 접두사 + 파이프라인 단계** |
| lidapengpeng/paper-review-system | 2 | **1** | 4 | 3 | **있음** | 단일 스킬 + 단계별 에이전트 |
| RehgLab/ArcDeck-Claude-Plugin | 0 | **1** | 13 (스펙 문서) | 0 | 없음 | 단일 스킬 + 파이프라인 DAG |
| assafelovic/gpt-researcher | 29,228 | **1** (`.claude/SKILL.md`) | 10 (Python 클래스) | 0 | 없음 | 스킬은 코드베이스 가이드, 에이전트는 런타임 |

★는 `gh api repos/<r>` 실측 (2026-09-01).

---

## 1. Imbad0202/academic-research-skills (44,455★, 카테고리 1위)

### 1-1. 실제 파일 목록

**SKILL.md — 딱 4개** (`.tree[]|select(.path|endswith("SKILL.md"))` 결과 전부):
```
academic-paper/SKILL.md
academic-paper-reviewer/SKILL.md
academic-pipeline/SKILL.md
deep-research/SKILL.md
```
> 스킬이 저장소 **루트 바로 아래** 있다. `skills/` 디렉터리를 쓰지 않는다.

**agents/ — 스킬 디렉터리 안에 분산 (총 39개) + 루트에 노출용 3개**

`deep-research/agents/` (14):
```
bibliography_agent.md          devils_advocate_agent.md      editor_in_chief_agent.md
ethics_review_agent.md         meta_analysis_agent.md        monitoring_agent.md
report_compiler_agent.md       research_architect_agent.md   research_question_agent.md
risk_of_bias_agent.md          socratic_mentor_agent.md      source_verification_agent.md
synthesis_agent.md             timeline_extraction_agent.md
```
`academic-paper/agents/` (12):
```
abstract_bilingual_agent.md    argument_builder_agent.md     citation_compliance_agent.md
draft_writer_agent.md          formatter_agent.md            intake_agent.md
literature_strategist_agent.md peer_reviewer_agent.md        revision_coach_agent.md
socratic_mentor_agent.md       structure_architect_agent.md  visualization_agent.md
```
`academic-paper-reviewer/agents/` (7):
```
devils_advocate_reviewer_agent.md  domain_reviewer_agent.md   editorial_synthesizer_agent.md
eic_agent.md                       field_analyst_agent.md     methodology_reviewer_agent.md
perspective_reviewer_agent.md
```
`academic-pipeline/agents/` (5):
```
claim_ref_alignment_audit_agent.md  collaboration_depth_agent.md  integrity_verification_agent.md
pipeline_orchestrator_agent.md      state_tracker_agent.md
```
`shared/agents/` (1): `compliance_agent.md`
**루트 `agents/` (3 — 플러그인에 실제로 노출되는 것)**: `report_compiler_agent.md`, `research_architect_agent.md`, `synthesis_agent.md`

**commands/ (16)**: `ars-3w`, `ars-abstract`, `ars-cache-invalidate`, `ars-citation-check`, `ars-disclosure`, `ars-format-convert`, `ars-full`, `ars-lit-review`, `ars-mark-read`, `ars-outline`, `ars-plan`, `ars-rebuttal-audit`, `ars-reviewer`, `ars-revision-coach`, `ars-revision`, `ars-unmark-read`

**hooks/ (있음)**: `hooks/hooks.json`, `hooks/run_guard.sh` — 원문:
```json
{"hooks":{
  "SessionStart":[{"hooks":[{"type":"command","command":"bash \"${CLAUDE_PLUGIN_ROOT}/scripts/announce-ars-loaded.sh\""}]}],
  "PreToolUse":[{"matcher":"Write|Edit|MultiEdit|Bash","hooks":[{"type":"command","command":"bash \"${CLAUDE_PLUGIN_ROOT}/hooks/run_guard.sh\""}]}]
}}
```

### 1-2. 분류

| 스킬 | 유형 |
|---|---|
| `deep-research` | **파이프라인 단계형**(리서치 수행 전체) — 단, 단일 스킬 안에 8모드 내장 |
| `academic-paper` | **산출물형** (논문) |
| `academic-paper-reviewer` | **역할형** (심사자) |
| `academic-pipeline` | **오케스트레이터형** (위 3개를 10단계로 엮음) |

에이전트 39개는 거의 전부 **파이프라인 단계형**(`research_question` → `research_architect` → `source_verification` → `synthesis` → `report_compiler` → `editor_in_chief` → `devils_advocate`).
→ **핵심: 스킬은 "산출물/역할" 축, 에이전트는 "파이프라인 단계" 축으로 완전히 분리돼 있다.**

### 1-3. 비율·훅

- 스킬:에이전트 = **4 : 39 ≈ 1 : 10**
- 커맨드 16개 전부 `ars-` 접두사 (네임스페이스 충돌 방어)
- hooks.json 사용 ✅ — SessionStart 안내 + PreToolUse 가드(Write/Edit/Bash 차단 로직)
- plugin.json 원문에 명시: `"4 skills, 27 modes, 39 prompt roles (3 plugin-exposed agents; the rest run inline by default)"`
  → **39개 에이전트 중 3개만 Claude Code 서브에이전트로 노출하고, 나머지 36개는 "프롬프트 롤"로 인라인 실행한다**고 저자가 직접 밝히고 있다.

### 1-4. description 패턴 (원문 인용)

> `academic-pipeline`:
> `"Orchestrator for the full academic research pipeline: research -> write -> integrity check -> review -> revise -> re-review -> re-revise -> final integrity check -> finalize. Coordinates deep-research, academic-paper, and academic-paper-reviewer into a seamless 10-stage workflow... Triggers on: academic pipeline, research to paper, full paper workflow, ... 연구부터 논문까지, 연구 주제 설정부터 논문 완성까지, 논문 전체 워크플로."`

패턴: **`<기능 요약 + 수치(N-agent, N modes)> + "Triggers on:" + 영/중/한 3개 국어 트리거 키워드 나열`**. description이 매우 길고(400자+), 다국어 트리거 키워드가 절반을 차지한다.

frontmatter에 `metadata:` 블록으로 `version`, `last_updated`, `status`, `data_access_level`, `task_type`, `related_skills`, `depends_on`를 넣는다 — **스킬 간 의존 그래프를 frontmatter에 선언한다**(실측):
```yaml
metadata:
  version: "3.21.1"
  depends_on: "deep-research, academic-paper, academic-paper-reviewer"
  related_skills: [deep-research, academic-paper, academic-paper-reviewer]
```

---

## 2. Marazii/research-co-pilot (13★)

> 태스크는 "13 스킬 주장"이었으나 **실측 15개**다. 레포 description은 "14 skills"라고 쓰여 있고 `dist/`에도 15개 zip이 있다. 숫자가 셋 다 어긋난다.

### 2-1. 실제 파일 목록

`skills/` (15, 각각 `SKILL.md` + `README.md`):
```
citation-formatter  data-analysis      ethics-committee    grant-writer
literature-review   manuscript-drafter methodology-advisor peer-review
qualitative-coding  replication-designer  research-brainstorm  reviewer-response
survey-design       talk-builder       vault
```
`agents/` (6):
```
data-cruncher.md  manuscript-drafter.md  source-finder.md
stats-validator.md  transcript-coder.md  vault-organizer.md
```
`commands/` (16):
```
analyze  brainstorm  cite  code-themes  draft  ethics  grant  lit-review
methodology  peer-review  replicate  research  respond  survey  talk  vault
```
hooks: **없음** (트리에 hooks 관련 파일 0개)

### 2-2. 분류

| 유형 | 스킬 |
|---|---|
| **파이프라인 단계형** | `literature-review`, `peer-review`, `research-brainstorm`, `qualitative-coding`, `data-analysis` |
| **산출물형** | `manuscript-drafter`, `grant-writer`, `talk-builder`, `survey-design`, `reviewer-response`, `citation-formatter` |
| **역할/게이트형** | `ethics-committee`, `methodology-advisor`, `replication-designer` |
| **인프라형** | `vault` (프로젝트 폴더·지식 레이어 관리) |

→ 순수 동사도 순수 명사도 아니다. **"연구자가 하는 일의 단위"**로 쪼갰다. 각 스킬이 곧 하나의 `/command`와 1:1 대응한다(15 스킬 ↔ 16 커맨드).

### 2-3. 비율·훅

- 스킬:에이전트 = **15 : 6 ≈ 2.5 : 1** (imbad0202과 정반대)
- 6개 에이전트는 전부 **컨텍스트 격리용 워커**다. `source-finder` frontmatter 원문에 명시:
  > `"Returns one structured extract per source — citation, claim, evidence type, sample, methods, key findings, limitations, and quality flags — **without polluting the parent context with raw paper content.**"`
- hooks 미사용

### 2-4. description 패턴 (원문 인용)

> `literature-review`:
> ```
> description: |
>   Conduct rigorous, fact-checked academic literature reviews. Synthesizes sources, traces citation chains,
>   flags weak claims, and produces structured outputs (narrative, systematic, scoping, or thematic).
>   Trigger when: user asks for a "literature review", "lit review", "background research", "state of the field",
>   "what does the research say about…", "summarize the literature on…", "find sources on…", or runs /lit-review.
> ```

> `research-brainstorm`:
> ```
>   Generate, sharpen, and pressure-test research ideas — research questions, hypotheses, study angles,
>   novel contributions, and contrarian framings. Pushes beyond obvious next steps to find what's actually
>   worth studying. Useful at the start of a project or when stuck.
>   Trigger when: user asks to "brainstorm research", "generate research ideas", ... or runs /brainstorm.
> ```

> `vault`:
> ```
>   Manage the research project's vault — the clean, visible, templated project folder (research/<project>/)
>   ... Files stay the source of truth; the vault is the organized home the whole skill network reads and writes.
>   Trigger when: user mentions "vault", "project folder", "organize my research", ... or runs /vault.
> ```

패턴: **`<동사로 시작하는 기능 서술 2~3문장> + "Trigger when: user asks to \"...\", \"...\", or runs /<command>."`**
frontmatter에 `argument-hint:`와 `allowed-tools:` 목록을 명시적으로 넣는다(실측). `research-brainstorm`은 `allowed-tools`에 `Skill`을 포함시켜 다른 스킬을 호출한다.

---

## 3. Jerrymwolf/Scriptorium-Cowork (0★) — **가장 순수한 파이프라인 단계형**

### 3-1. 실제 파일 목록

`skills/` (14, 전부 단일 `SKILL.md`):
```
setup  scope  research-direction  grill-question  search  screen  extract
contradictions  synthesize  review  audit  render  publish  using-scriptorium
```
`agents/`: **없음** (트리에 agents 디렉터리 0개)
`commands/`: **없음**
`hooks`: **없음**
대신 `runtime/cite-check.py`, `scripts/cite-check.py`, `scripts/build-viewer.py` 등 결정론적 스크립트를 둔다.

### 3-2. 분류 — 14개 중 11개가 순수 동사

| 유형 | 스킬 |
|---|---|
| **파이프라인 단계형(동사)** | `scope`, `search`, `screen`, `extract`, `contradictions`, `synthesize`, `audit`, `render`, `publish` (9) |
| **온보딩/디스패처형** | `setup`, `using-scriptorium` (2) |
| **오케스트레이터형** | `review` (1) |
| **상류 발산형** | `research-direction`, `grill-question` (2) |
| **도메인형** | **0개** |
| **산출물형** | **0개** (`render`/`publish`는 동사로 표현) |

### 3-3. 비율·훅

- 스킬:에이전트 = **14 : 0** — 에이전트를 아예 쓰지 않는다.
- 대신 **`review` 스킬 하나가 오케스트레이터**로서 나머지 스킬을 순서대로 디스패치한다. description 원문:
  > `"Orchestrates the full pipeline — scope, search, screen, extract, synthesize, contradictions, audit, and optional publishing — by dispatching to the per-phase skills in order."`
- 그리고 **`using-scriptorium`이 라우터**다:
  > `"...Probes which Cowork connectors are available, picks the state home, teaches the three disciplines, and dispatches to the phase-appropriate skill (scope / search / screen / extract / synthesize / contradictions / audit / publish, or the direction skills upstream — research-direction / grill-question)."`

### 3-4. description 패턴 (원문 인용)

> `screen`:
> `"Use after search when the user wants to apply inclusion/exclusion criteria (year range, language, must-include/exclude keywords) to the corpus. Marks papers kept or dropped with a reason and records the decision in the audit trail."`

> `synthesize`:
> `"Use when the user asks to draft a literature review section, write a synthesis, or summarize the evidence. Produces synthesis.md with every claim backed by [paper_id:locator] tokens and runs a mandatory cite-check before committing."`

> `research-direction`:
> `"Use when the user has a research topic but doesn't yet know what they want from engaging with it... Grills the user about their relationship to the topic (purpose, audience, artifact, depth) — NOT about the topic's content. **Do NOT fire when** the user wants to learn the topic itself, and **do NOT fire on** a bare \"grill me\" about a plan, design, or decision — that request belongs to a general-purpose grilling skill, not this one."`

패턴: **`"Use when/after <조건>. <구체적 산출 파일명·동작>."`** — 여기가 다른 레포와 결정적으로 다르다:
1. **선행 단계를 조건에 박아 넣는다** (`Use **after search** when...`, `OR when invoked by review`, `OR when search finds no scope object`) — 스킬 순서가 description에 인코딩돼 있다.
2. **부정 조건(`Do NOT fire when...`)을 명시한다** — 인접 스킬과의 경계를 description에서 직접 방어한다. 8개 레포 중 여기만 이걸 한다.
3. 산출물 파일명(`synthesis.md`, `corpus.jsonl`, `evidence.jsonl`)과 인용 토큰 문법(`[paper_id:locator]`)을 description에 넣어 **스킬 간 데이터 계약**을 만든다.

---

## 4. oduffy-delphi/deep-research-claude (0★)

### 4-1. 실제 파일 목록

`skills/` — **파일 1개뿐, 디렉터리 구조 아님**:
```
skills/eval-output.md
```
`agents/` (6):
```
repo-scout.md  repo-specialist.md  research-scout.md
research-specialist.md  research-synthesizer.md  structured-synthesizer.md
```
`notebooklm/agents/` (3): `research-scout.md`, `research-sweep.md`, `research-worker.md`
`commands/` (2): `research.md`, `setup.md` (+ `notebooklm/commands/research.md`)
`pipelines/` (22개 프롬프트 템플릿·프로토콜 문서): `PIPELINE.md`, `eval-rubric.md`, `repo-driver.md`, `web-driver.md`, `structured-driver.md`, `team-protocol.md`, `scout-prompt-template.md`, `specialist-prompt-template.md`, `spec-format.md` 등
hooks: `.claude/settings.json`은 `{"enabledPlugins":{"clangd-lsp@claude-plugins-official":false}}`뿐 — **hooks 없음**. (`tests/plugins/hooks.test.js`는 테스트 파일)

### 4-2. 분류

유일한 스킬 `eval-output`은 **검증형**. 나머지는 전부 에이전트/파이프라인 문서다.
에이전트 이름은 **모델 티어 × 역할** 축으로 쪼갰다 — plugin.json 원문:
> `"All pipelines use Agent Teams with **Haiku scouts, Sonnet specialists, and Opus sweep agents**."`

`research-scout.md` frontmatter 실측: `model: haiku`, `tools: ["WebSearch","WebFetch","Write","Read","Bash","ToolSearch","TaskUpdate","TaskList","TaskGet"]`, `access-mode: read-write`, `color: yellow`.

### 4-3. 비율·훅

- 스킬:에이전트 = **1 : 9** — 스킬을 거의 안 쓴다.
- 로직은 `pipelines/*.md` **프롬프트 템플릿**에 있고, 커맨드가 그 템플릿을 읽어 에이전트를 스폰한다.

### 4-4. description 패턴 (원문 인용)

> 스킬 `eval-output`: `"Score a research output against the 5-criteria eval rubric. Dispatches a Sonnet evaluator."` (한 줄)

> 에이전트 `research-scout`: `"Haiku scout for Agent Teams-based deep research. Spawned as a teammate by the deep-research-web-teams command. Executes search queries from scope.md, mechanically vets source accessibility, and writes a shared source corpus for Sonnet specialists to consume.\n\nExamples:\n\n<example>\nContext: EM has scoped research and written search queries to scope.md.\nuser: \"Execute search queries...\"\n<commentary>Scout reads queries from disk (written by EM during scoping), executes them mechanically, writes results to source-corpus.md. Task completion unblocks specialists.</commentary></example>"`

→ **에이전트 description은 `<example>` + `<commentary>` 블록을 포함하는 긴 형식, 스킬 description은 한 줄.** 형식이 다르다.

---

## 5. assafelovic/gpt-researcher (29,228★) — **`skills/` 디렉터리가 없다**

트리 전체 검색 결과 `skills/`로 시작하는 경로는 **0건**이다. 대신:

- **`.claude/SKILL.md` 단 1개** + `.claude/references/` 14개 문서(`architecture.md`, `deep-research.md`, `multi-agents.md`, `retrievers.md`, `mcp.md`, `prompts.md`, `flows.md`, `components.md`, `config-reference.md`, `api-reference.md`, `adding-features.md`, `advanced-patterns.md`)
- 이 스킬은 **리서치를 수행하는 스킬이 아니라 "이 코드베이스를 다루는 법" 가이드다.** frontmatter 원문:
  > `name: gpt-researcher`
  > `description: GPT Researcher is an autonomous deep research agent... **Use this skill when helping developers understand, extend, debug, or integrate with GPT Researcher** - including adding features, understanding the architecture, working with the API, customizing research workflows, adding new retrievers, integrating MCP data sources, or troubleshooting research pipelines.`

- 실제 에이전트는 **Python 클래스**다. `multi_agents/agents/__init__.py` 원문:
  ```python
  from .researcher import ResearchAgent
  from .writer import WriterAgent
  from .publisher import PublisherAgent
  from .reviser import ReviserAgent
  from .reviewer import ReviewerAgent
  from .editor import EditorAgent
  from .human import HumanAgent
  from .fact_checker import FactCheckerAgent
  from .visualizer import VisualizerAgent
  from .orchestrator import ChiefEditorAgent
  ```
  `multi_agents/agents/` 트리 실측 파일: `editor.py human.py orchestrator.py publisher.py researcher.py reviewer.py reviser.py writer.py` (+`utils/`).
  > **관측 불일치**: `__init__.py`가 import하는 `fact_checker.py`, `visualizer.py`가 트리에 없다. 원인 미확인 — 단정하지 않는다.

- 역할 축: `researcher / writer / editor / reviewer / reviser / publisher / fact_checker / visualizer / human / orchestrator(ChiefEditor)` = **편집국 은유(newsroom metaphor)**.
- hooks 없음. `.claude-plugin/` 없음 — Claude Code 플러그인이 아니다.

---

## 6. avivlyweb/nagomi-pubmed-plugin (0★) — 도메인 특화의 정석

### 6-1. 실제 파일 목록

`.claude/skills/` (5):
```
pubmed-search/SKILL.md    pubmed-analyze/SKILL.md   pubmed-verify/SKILL.md
pubmed-synthesis/SKILL.md pubmed-export/SKILL.md
```
`agents/`: **없음** · `commands/`: **없음** · `hooks`: **없음**
대신 `.mcp.json` + `pubmed-mcp/pubmed_mcp.py` (자체 MCP 서버) + `pubmed-mcp/reference_checker/` (apa_checker, document_parser, reference_extractor, report_generator, verification_engine)
※ `pubmed-mcp/venv/`가 통째로 커밋돼 있다(수백 개 site-packages 파일). 위생 문제이지 설계와 무관.

### 6-2. 분류 — **도메인 접두사 + 파이프라인 동사 하이브리드**

| 스킬 | 접두사 | 동사 |
|---|---|---|
| `pubmed-search` | 도메인 | search |
| `pubmed-analyze` | 도메인 | analyze |
| `pubmed-verify` | 도메인 | verify |
| `pubmed-synthesis` | 도메인 | synthesize |
| `pubmed-export` | 도메인 | export |

→ **도메인형이냐 파이프라인형이냐의 이분법 자체가 틀렸음을 보여주는 사례.** 도메인은 **네임스페이스**(접두사)로 쓰고, 분해 축은 **파이프라인 단계**다.

### 6-3. description 패턴 (원문 인용)

> `pubmed-verify`: `"Verify a list of academic references for hallucinations, fake citations, and formatting issues using the ABC-TOM 6-tier classification system. Use when the user wants to check citations in a document, paper, or reference list."`

> `pubmed-synthesis`: `"Generate a PhD-level systematic evidence synthesis on a medical topic. Searches multiple PubMed studies, resolves contradictions, and produces a comprehensive clinical research report. **Use for deep topic reviews, not single-article analysis.**"`

> `pubmed-analyze`: `"Analyze a specific PubMed article by PMID. Get full trustworthiness assessment, study design classification, key findings extraction, and evidence grade. Use when the user provides a PMID or asks to analyze a specific paper."`

패턴: **`<동사 원형으로 시작하는 1문장> + "Use when <상황>."`** — 5개 중 가장 짧고 균일하다. `pubmed-synthesis`는 `analyze`와의 경계를 `"not single-article analysis"`로 명시해 방어한다(Scriptorium의 부정 조건과 같은 기법).
frontmatter에 `disable-model-invocation: false`를 5개 전부 명시(실측).

---

## 7. lidapengpeng/paper-review-system (2★)

### 7-1. 실제 파일 목록

`skills/` (1): `skills/paper-review/SKILL.md` + `references/` 4개(`review-template.md`, `scoring-guide.md`, `venue-profiles.md`, `venue-review-criteria.md`)
`agents/` (4): `paper-analyzer.md`, `paper-comparator.md`, `reference-auditor.md`, `technical-reviewer.md`
`commands/` (3): `pre-screen.md`, `rebuttal.md`, `review-paper.md`
`hooks/hooks.json` — **있음**. 원문:
```json
{"hooks":{"SessionStart":[{"matcher":"","hooks":[{"type":"command","command":"bash ${CLAUDE_PLUGIN_ROOT}/scripts/check-deps.sh","timeout":15}]}]}}
```
> 훅의 용도가 **의존성 체크(Python/MCP 준비 여부)**다. imbad0202의 SessionStart 훅(로드 안내)과 목적이 다르다.

MCP 서버 2개 자체 내장: `academic-search-mcp/`(crossref, dblp, semantic_scholar, codesota), `paper-parser-mcp/`(pymupdf, marker, figure_table_extractor, reference_parser)
`docs/reviewer-perspectives/` 11개: CVPR/NeurIPS/ICCV/ECCV/ICML/AAAI/ACL/ICLR/KDD/MICCAI 학회별 리뷰어 관점 문서

### 7-2. 분류

- 스킬 1개(`paper-review`) = **역할형**
- 에이전트 4개 = **파이프라인 단계형** (`analyzer` → `comparator` → `reference-auditor` → `technical-reviewer`)
- 학회별 차이는 **스킬로 쪼개지 않고 `references/venue-profiles.md` 데이터로 처리**했다. 10개 학회를 10개 스킬로 만들지 않았다는 게 핵심 관측.

### 7-3. description 패턴 (원문 인용)

> 스킬: `"This skill should be used when the user asks to \"审稿\", \"review paper\", \"审阅论文\", \"评审论文\", \"paper review\", \"检查论文质量\", provides a PDF path for academic review, mentions \"学术审稿\", \"conference review\", \"期刊审稿\", or wants to evaluate an academic paper's quality across multiple dimensions including novelty, technical soundness, experiments, and writing quality. Supports venue-specific review for CVPR, NeurIPS, ICML, ICLR, ECCV, ICCV, ACL, AAAI, KDD, MICCAI and more."`

패턴: `"This skill should be used when..."` + 중/영 트리거 키워드 나열 (imbad0202과 유사한 다국어 전략).

> 에이전트 `paper-analyzer`: `"Use this agent to parse and analyze academic PDF papers. **Trigger proactively when the /review-paper command enters Phase 1**, or when a user asks to \"解析论文\"..."` + `<example>` 블록
→ 에이전트 description에 **커맨드의 특정 Phase를 명시**한다. 파이프라인 위치를 description에 박는 방식.

---

## 8. RehgLab/ArcDeck-Claude-Plugin (0★) — "13 에이전트" 주장의 실체

### 8-1. 실제 파일 목록

`skills/` (1): `skills/arcdeck/SKILL.md`
`skills/arcdeck/agents/` (14 파일 = 개요 1 + 에이전트 13):
```
00-AGENT-OVERVIEW.md      01-pdf-preprocessor.md   02-asset-extractor.md
03-commitment-builder.md  04-discourse-parser.md   05-slide-planner.md
06-narrative-critic.md    07-slide-reviser.md      08-narrative-judge.md
09-image-table-filter.md  10-slide-composer.md     11-design-critic.md
12-design-refiner.md      13-pptx-builder.md
```
`skills/arcdeck/prompts/outline/` (8 `.txt`), `prompts/pipeline/` (7 `.yaml`), `reference/` (5), `scripts/` (6 py/js)
`commands/`: 없음 · `hooks`: 없음

### 8-2. 결정적 관측: **이 13개는 Claude Code 서브에이전트가 아니다**

`01-pdf-preprocessor.md` 원문 첫 줄이 `# Agent 1: PDF Preprocessor`다. **YAML frontmatter가 아예 없다.** `name:`/`description:`/`tools:` 없음. 즉 Claude Code가 에이전트로 등록하지 않는다.

`00-AGENT-OVERVIEW.md` 원문이 이를 확인해준다:
> `"ArcDeck decomposes paper-to-slides generation into 13 specialized agents across 3 phases. **Each agent is described in its own .md file that Claude Code reads and executes.**"`
> `"**Agents 10-13 are designed as Claude Code skill instructions** -- Claude Code acts as the LLM directly, with no external API calls needed for these phases."`

각 에이전트 문서는 `## Role` / `## Position in Pipeline`(Phase, Depends on, Produces for, LLM Required) / `## Inputs`(표) / `## Execution Steps` 구조를 가지며, 개요에 **실행 DAG를 ASCII로 그려둔다**.

### 8-3. 분류

13개 전부 **파이프라인 단계형**이며, 그중 `06-narrative-critic` → `07-slide-reviser` → `08-narrative-judge`와 `11-design-critic` → `12-design-refiner`가 **critique-revise-judge 루프**를 이룬다.
스킬 1개 = **산출물형**(paper → slides).

### 8-4. description (원문 인용)

> `"Convert academic PDF papers into polished, narrative-driven PowerPoint presentations using 13 specialized AI agents orchestrated by Claude Code. Based on RST discourse parsing with multi-agent critique-revise-judge refinement and CARP+ aesthetic design."`

패턴: **한 문장, 트리거 조건 없음.** 8개 레포 중 유일하게 `Use when` 절이 없다. 학술 논문 부산물(저자가 6명의 대학 연구자)이라 검색 최적화를 안 했다.

---

## 9. 관찰된 공통 분해 원칙 — 무엇이 스킬이고 무엇이 에이전트인가

아래는 **위 8개 레포의 실측 구조에서 반복 관측된 패턴**이다. 해석은 [추론]으로 표시했다.

### 원칙 1. 스킬 = 사용자가 부르는 것 / 에이전트 = 스킬이 부르는 것

관측 근거:
- Marazii는 스킬 15개 ↔ 커맨드 16개가 거의 1:1이고, 에이전트 6개는 커맨드가 없다. 에이전트 description에 `"without polluting the parent context"`라고 명시 — **호출자용이 아니라 컨텍스트 격리용**.
- oduffy의 `research-scout` description: `"Spawned as a teammate by the deep-research-web-teams command"` — 사용자가 아니라 커맨드가 스폰한다.
- lidapengpeng의 `paper-analyzer`: `"Trigger proactively when the /review-paper command enters Phase 1"`.

→ **경계선: 사용자가 "이걸 해줘"라고 말할 단위면 스킬, 그 안에서 병렬/격리 실행되는 하위 작업이면 에이전트.**

### 원칙 2. 컨텍스트 오염 여부가 실질적 경계다 [추론, 근거 강함]

에이전트로 뺀 것들의 공통점: **대량의 원문을 읽어야 하는 작업**(source-finder=논문 다수 읽기, paper-analyzer=PDF 파싱, research-scout=검색 결과 수집, pdf-preprocessor=PDF→Markdown). 스킬로 둔 것들의 공통점: **판단·대화가 필요한 작업**(scope, brainstorm, methodology-advisor, grill-question).
→ 토큰을 태우는 일은 에이전트, 사용자와 주고받는 일은 스킬.

### 원칙 3. 스킬 개수는 두 극단으로 갈린다 — 중간이 없다

| 전략 | 레포 | 스킬:에이전트 |
|---|---|---|
| **얇은 스킬 다수** | Scriptorium 14:0, Marazii 15:6, nagomi 5:0 | 스킬이 많고 에이전트가 적거나 없음 |
| **두꺼운 스킬 소수** | imbad0202 4:39, ArcDeck 1:13, lidapengpeng 1:4, oduffy 1:9 | 스킬 하나에 모드/에이전트를 몰아넣음 |

→ [추론] 44k★ 1위(imbad0202)와 0★ 무명(ArcDeck, lidapengpeng, oduffy)이 **같은 쪽**에 있고, Scriptorium·Marazii·nagomi가 반대쪽에 있다. **스타 수와 분해 전략 사이에 상관이 보이지 않는다.** 어느 쪽이 우월하다는 증거는 이 데이터에 없다.

### 원칙 4. 도메인은 분해 축이 아니라 **접두사(네임스페이스)**로 쓴다

- nagomi: `pubmed-*` 5개 — 도메인은 접두사, 분해는 동사(search/analyze/verify/synthesis/export).
- imbad0202: 커맨드 16개 전부 `ars-*`.
- lidapengpeng: 10개 학회를 **스킬 10개로 쪼개지 않고** `references/venue-profiles.md` 데이터 파일 하나로 처리.

→ **8개 레포 어디에도 "도메인별로 스킬을 쪼갠" 사례가 없다.** 도메인 특화(nagomi)조차 내부는 파이프라인 단계로 쪼갰다. **[관측 — 태스크의 핵심 질문에 대한 직접적 답]**

### 원칙 5. 파이프라인이 길면 반드시 **오케스트레이터 스킬 1개**를 따로 둔다

- Scriptorium: `review`(전체 파이프라인 디스패치) + `using-scriptorium`(라우터) — **오케스트레이터와 라우터를 분리**
- imbad0202: `academic-pipeline` (frontmatter에 `depends_on: "deep-research, academic-paper, academic-paper-reviewer"`)
- ArcDeck: `00-AGENT-OVERVIEW.md`에 실행 DAG
- oduffy: `pipelines/PIPELINE.md`, `*-driver.md`

→ **오케스트레이터는 단계 스킬과 같은 층에 두되 이름을 분리한다**(`review`, `academic-pipeline`). 단계 스킬 중 하나가 겸임하지 않는다.

### 원칙 6. 스킬 간 경계는 **description의 부정 조건**으로 방어한다

이걸 하는 곳: Scriptorium(`Do NOT fire when...`), nagomi(`Use for deep topic reviews, not single-article analysis`).
안 하는 곳: imbad0202(대신 다국어 트리거 키워드 나열), ArcDeck(트리거 절 자체 없음).

→ [추론] 스킬을 잘게 쪼갤수록(Scriptorium 14개) 오발동 위험이 커지므로 부정 조건이 필수가 된다. 두껍게 쪼개면(imbad0202 4개) 대신 트리거 키워드를 넓게 깔아 발동률을 올린다. **분해 입도와 description 전략이 연동된다.**

### 원칙 7. hooks는 소수만, 그것도 두 용도뿐

- 8개 중 **2개만** hooks.json 보유 (imbad0202, lidapengpeng).
- 용도 2가지: **SessionStart 준비 확인**(로드 안내 / 의존성 체크) + **PreToolUse 가드**(imbad0202의 `run_guard.sh`가 `Write|Edit|MultiEdit|Bash` 매칭).
- 나머지 6개는 hooks 없이도 성립한다.
→ **hooks는 선택 사항이며, 리서치 파이프라인 로직에는 쓰이지 않는다.**

### 원칙 8. 스킬 간 데이터 계약을 파일로 고정한다

- Scriptorium: `corpus.jsonl` → `evidence.jsonl` → `synthesis.md`, 인용 토큰 문법 `[paper_id:locator]`를 description에 명시, `cite-check.py`로 결정론적 검증.
- oduffy: `scope.md` → `source-corpus.md` (scout가 쓰고 specialist가 읽음, description에 명시).
- Marazii: `vault` 스킬이 `research/<project>/` 폴더를 "the organized home the whole skill network reads and writes"로 정의.
- imbad0202: frontmatter `metadata.depends_on` / `related_skills`로 의존 그래프 선언.

→ **스킬을 쪼갤 때 반드시 "무엇을 파일로 넘길지"를 같이 정한다. 이게 없으면 쪼갠 스킬들이 이어지지 않는다.**

---

## 10. 태스크 질문에 대한 직답

**"파이프라인 단계(동사)로 쪼갤 것인가, 산업 도메인(명사)으로 쪼갤 것인가?"**

**실측 답: 8개 레포 중 도메인으로 쪼갠 사례는 0건이다.** 도메인 특화 플러그인(nagomi)조차 도메인을 접두사로만 쓰고 내부는 `search/analyze/verify/synthesis/export`라는 파이프라인 동사로 쪼갰다. 도메인 다양성이 큰 lidapengpeng은 10개 학회를 스킬이 아닌 **참조 데이터 파일**로 처리했다.

실제로 갈리는 축은 도메인 vs 동사가 아니라 **입도(granularity)**다:
- **얇게(10~15 스킬, 에이전트 0~6)**: Scriptorium, Marazii, nagomi — 각 스킬이 커맨드 1개와 대응, 경계는 description 부정 조건으로 방어
- **두껍게(1~4 스킬, 에이전트 4~39)**: imbad0202(1위), ArcDeck, lidapengpeng, oduffy — 스킬 안에 모드를 넣고 파이프라인은 에이전트로 표현

그리고 **스킬과 에이전트를 서로 다른 축으로 쓴다** — imbad0202가 가장 명확하다: 스킬은 산출물/역할(논문/심사/파이프라인), 에이전트는 파이프라인 단계(39개). 두 축을 한 층에 섞은 레포는 관측되지 않았다.

---

## 11. 원본 근거 (전부 이 조사에서 직접 읽음)

| 레포 | 브랜치 | 확인한 것 |
|---|---|---|
| [Imbad0202/academic-research-skills](https://github.com/Imbad0202/academic-research-skills) | main | 전체 트리, 4× SKILL.md frontmatter, hooks/hooks.json, .claude-plugin/plugin.json, .claude-plugin/marketplace.json, deep-research/agents/synthesis_agent.md |
| [Marazii/research-co-pilot](https://github.com/Marazii/research-co-pilot) | main | 전체 트리, 15× SKILL.md frontmatter(3개 전문), .claude-plugin/plugin.json, agents/source-finder.md |
| [Jerrymwolf/Scriptorium-Cowork](https://github.com/Jerrymwolf/Scriptorium-Cowork) | main | 전체 트리, 14× SKILL.md frontmatter 전부 |
| [oduffy-delphi/deep-research-claude](https://github.com/oduffy-delphi/deep-research-claude) | main | 전체 트리, .claude-plugin/plugin.json, .claude/settings.json, agents/research-scout.md, skills/eval-output.md, publish-manifest.txt |
| [avivlyweb/nagomi-pubmed-plugin](https://github.com/avivlyweb/nagomi-pubmed-plugin) | main | 전체 트리, 5× SKILL.md frontmatter 전부, .claude-plugin/plugin.json |
| [lidapengpeng/paper-review-system](https://github.com/lidapengpeng/paper-review-system) | main | 전체 트리, skills/paper-review/SKILL.md, hooks/hooks.json, .claude-plugin/plugin.json, agents/paper-analyzer.md |
| [RehgLab/ArcDeck-Claude-Plugin](https://github.com/RehgLab/ArcDeck-Claude-Plugin) | main | 전체 트리, skills/arcdeck/SKILL.md, .claude-plugin/plugin.json, agents/00-AGENT-OVERVIEW.md, agents/01-pdf-preprocessor.md |
| [assafelovic/gpt-researcher](https://github.com/assafelovic/gpt-researcher) | master | 전체 트리(skills/ 부재 확인), .claude/SKILL.md, multi_agents/agents/__init__.py |

미해결 관측:
- Marazii 스킬 수가 태스크(13) / 레포 description(14) / 실제 트리(15)에서 전부 다름.
- gpt-researcher `multi_agents/agents/__init__.py`가 import하는 `fact_checker.py`, `visualizer.py`가 트리에 없음 — 원인 미확인.
