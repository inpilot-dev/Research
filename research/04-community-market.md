# 04 — 커뮤니티·유통 채널 및 상용 제품 지형

> 조사일: **2026-09-01**
> 대상: 베타 단계 오픈소스 research 에이전트의 (a) 유통 채널 선택 (b) 상용 제품 대비 포지셔닝
> 수치 출처 표기: **[1차]** = GitHub REST API / HN Algolia API / 공식 가격 페이지를 이 조사에서 직접 호출한 값. **[2차]** = 검색으로 확인한 서드파티 집계(오차 가능, 그대로 인용하지 말 것).

---

## 0. TL;DR — 이 문서에서 실제로 나온 결론 3줄

1. **Hacker News는 이 카테고리에서 작동하지 않는다.** 최근 12개월 Show HN 중 "deep research 에이전트"로 100점을 넘긴 글은 **단 하나**(`Mole`, 100pts)다. 반면 같은 기간 500점 이상 Show HN 25건은 전부 물리적·시각적·즉시 놀라운 것들이었다. → HN을 "메인 런칭"으로 잡으면 거의 확실히 무반응이다.
2. **실제로 터진 최근 사례 3건의 공통 경로는 HN도 Reddit도 아니다.** ① 저자 개인 X 계정의 기존 팔로워 자산(`virattt/dexter`), ② Claude Code / Agent Skills **플러그인 마켓플레이스 + GitHub Trending**(`mvanhorn/last30days-skill`), ③ 제품 카테고리 자체를 갈아끼우는 서사(`tinyhumansai/openhuman`). 셋 다 HN 점수는 1~3점이었다.
3. **상용 제품(OpenAI/Gemini/Perplexity/Elicit)을 "품질"로 이기려는 포지셔닝은 지는 싸움이다.** 오픈소스가 구조적으로 이기는 축은 딱 4개 — 데이터 경계(로컬/사설 코퍼스), 비용 구조(내 API 키/로컬 모델), 검증 가능성(중간 산출물·프롬프트·인용 전부 공개), 확장성(내 도메인 툴을 붙일 수 있음). 이 4개 중 **1개를 골라 제목에 박아야** 한다.

---

## 1. 유통 채널 전수 조사

### 1.1 Hacker News (Show HN)

**공식 규칙** ([news.ycombinator.com/showhn.html](https://news.ycombinator.com/showhn.html)):
- "Show HN is for something you've made that other people can play with" — 사용자가 **직접 돌려볼 수 있어야** 한다.
- 블로그 글, 가입 페이지, 뉴스레터, 랜딩 페이지, 리스트는 **부적격**.
- 마이너 버전 업데이트(`Foo 1.3.1`) 부적격.
- "The project must be something you've worked on personally and which you're around to discuss" — 저자가 댓글에 붙어 있어야 함.
- **친구에게 업보트 요청 금지** (명시적 금지 조항).

**실증 데이터 — 이 카테고리의 HN 성적표** [1차, HN Algolia API, 2026-09-01 조회]

최근 12개월(2025-09-01 이후) `research` 키워드 Show HN 상위:

| 점수 | 날짜 | 제목 |
|---:|---|---|
| 100 | 2026-08-14 | [Show HN: Mole – Deep research agent for your terminal](https://news.ycombinator.com/item?id=49303046) |
| 91 | 2025-09-10 | [Show HN: Building a Deep Research Agent Using MCP-Agent](https://news.ycombinator.com/item?id=45199256) |
| 85 | 2026-07-09 | [Show HN: I mapped 8.5M research papers into an interactive atlas](https://news.ycombinator.com/item?id=48840207) |
| 85 | 2025-10-28 | [Show HN: Research Hacker News, ArXiv & Google with Hierarchical Bayesian Models](https://news.ycombinator.com/item?id=45734429) |
| 34 | 2025-12-16 | [Show HN: Ekphos – Open-source Markdown research tool in Rust](https://news.ycombinator.com/item?id=46287722) |
| 17 | 2026-02-01 | [Show HN: My Open Source Deep Research tools beats Google and I can Prove it](https://news.ycombinator.com/item?id=46848479) |
| 14 | 2026-04-21 | [Show HN: Almanac MCP, turn Claude Code into a Deep Research agent](https://news.ycombinator.com/item?id=47855284) |

> **핵심**: "내 오픈소스 deep research가 구글을 이긴다"는 가장 공격적인 제목조차 **17점**. 이 카테고리는 HN에서 이미 포화·피로 상태다.

대조군 — 같은 기간 500점 이상 Show HN(상위 7건):

| 점수 | 제목 |
|---:|---|
| 2935 | [I replaced a $120k bowling center system with $1,600 in ESP32s](https://news.ycombinator.com/item?id=48968606) |
| 1680 | [Elevators](https://news.ycombinator.com/item?id=49124218) |
| 1481 | [Homebrew 6.0.0](https://news.ycombinator.com/item?id=48490024) |
| 1033 | [Bento – An entire PowerPoint in one HTML file](https://news.ycombinator.com/item?id=49008211) |
| 937 | [Getting GLM 5.2 running on my slow computer](https://news.ycombinator.com/item?id=48842459) |
| 919 | [Open-source engine running Gemma 4 26B in 2 GB RAM on any M-series Mac](https://news.ycombinator.com/item?id=49098510) |
| 915 | [I built a tiny LLM to demystify how language models work](https://news.ycombinator.com/item?id=47655408) |

**패턴**: HN이 보상하는 것은 "카테고리"가 아니라 **제약 조건의 극단성**이다 — *$120k → $1,600*, *26B 모델을 2GB RAM에서*, *PowerPoint 전체를 HTML 한 파일로*. "research 에이전트를 만들었다"는 제약이 없다. **"X라는 제약 하에서 research를 한다"**로 바꿔야 한다.

**참고**: 오히려 이 카테고리에서 HN 점수가 높았던 글들은 **Show HN이 아니라 제3자 제출**이었다 —
[Tongyi DeepResearch (365pts)](https://news.ycombinator.com/item?id=45789602), [DeepSearcher (229pts)](https://news.ycombinator.com/item?id=43172338), [Local Deep Research (190pts)](https://news.ycombinator.com/item?id=43330164), [STORM (145pts)](https://news.ycombinator.com/item?id=41553875). 자기가 올린 `Show HN: GPT Researcher`는 [4점](https://news.ycombinator.com/item?id=41234914)이었지만 그 레포는 현재 **29,228★**다. → **HN 점수와 프로젝트 성공은 이 카테고리에서 상관이 거의 없다.**

**결론(HN)**: 우선순위 **중하**. 올리긴 하되 성공 지표로 삼지 말 것. 올린다면 화·수·목 ET 오전 9~12시, 제목에 숫자 제약을 박고, 첫 댓글에 "왜 만들었나 + 아직 못 하는 것 하나"를 붙인다 ([Lucas da Costa의 HN 런칭 가이드](https://www.lucasfcosta.com/blog/hn-launch), [daily.dev 정리](https://business.daily.dev/resources/hacker-news-marketing-developer-tools-show-hn-launch-day-sustained-coverage/)).

---

### 1.2 Reddit

> ⚠️ Reddit은 이 조사 환경에서 API·웹 직접 접근이 모두 차단되어(403/HTML 셸) **구독자 수는 전부 [2차] 출처**다. 실제 런칭 전 각 서브레딧의 `about/rules` 페이지를 직접 눈으로 확인할 것.

| 서브레딧 | 규모 [2차] | self-promo 정책 | 먹히는 포맷 | 판정 |
|---|---:|---|---|---|
| [r/LocalLLaMA](https://www.reddit.com/r/LocalLLaMA/) | ~814k (2026-07) | "1/10 가이드라인" — 자기 홍보는 전체 활동의 1/10 이하, **소속 공개 필수**. 용인되지만 감시됨 | 벤치마크 표, VRAM/토큰 실측, "로컬 모델로 X 돌렸다" 후기. 툴은 *맥락*으로만 등장 | **최우선.** 로컬 폴백(Ollama/qwen) 경로가 있으면 이 서브가 정확히 우리 관객 |
| [r/ClaudeAI](https://www.reddit.com/r/ClaudeAI/) | ~1.09M (2026-08) | 상대적으로 관대. 워크플로·스킬 공유 문화 | "Claude Code로 X 자동화한 세팅 공유" + 레포 링크 | **최우선.** 특히 Agent Skill / MCP 형태로 배포한다면 |
| [r/MachineLearning](https://www.reddit.com/r/MachineLearning/) | 대형 | **엄격.** 플레어 `[P]` 필수, 그 외 홍보는 주간 `[D] Self-Promotion Thread`로 강제 이동 | `[P]` + 재현 가능한 평가·코드. 마케팅 문장 0 | 중. 평가 결과(recall/FP 같은 실측)가 있을 때만 |
| [r/singularity](https://www.reddit.com/r/singularity/) | ~3.95M (2026-08) | 뉴스 피드 성격, 홍보 비선호 | 담론/스크린샷. 개발자 전환율 낮음 | 하. 노이즈 대비 실익 적음 |

출처: [Prowlo r/singularity 통계](https://prowlo.com/tools/subreddit-stats/singularity) · [Prowlo r/ClaudeAI 통계](https://prowlo.com/tools/subreddit-stats/claudeai) · [GummySearch r/LocalLLaMA](https://gummysearch.com/r/LocalLLaMA/) · [LaunchWake r/LocalLLaMA 홍보 규칙](https://www.launchwake.com/channels/r-localllama) · [Intoru r/localllama 규칙](https://intoru.ai/subreddits/localllama)

**공통 룰(모든 서브 통용)**: 90/10 비율 — 도움되는 활동 9, 자기 것 1. 소속·저자임을 첫 줄에 밝힐 것. 링크만 던지는 글은 삭제 대상.
([Reddit 자기홍보 규칙 종합](https://redship.io/blog/reddit-self-promotion-rules), [dev.to 프레임워크](https://dev.to/sh20raj/reddit-self-promotion-framework-how-to-post-smart-and-stay-unbanned-1kfg))

---

### 1.3 X / Twitter (AI 커뮤니티)

**이번 조사에서 가장 강한 증거가 나온 채널.** `virattt/dexter`는 [저자의 X 게시물](https://x.com/virattt/status/1978224884464357579)("Introducing Dexter. An open source financial agent in ~200 lines of code. Think: Claude Code, but for finance.")로 공개됐고, 같은 프로젝트의 HN 제출은 [1점](https://news.ycombinator.com/item?id=46237014)이었다. 현재 **27,561★** [1차].

- 작동 원리: **팔로워 자산이 있어야 작동한다.** virattt는 이미 [`ai-hedge-fund` 63,114★](https://github.com/virattt/ai-hedge-fund)의 저자였다 [1차]. 자산 없이 X에 던지면 0이다.
- 자산이 없을 때의 대안: 큰 계정이 인용하도록 **인용 가능한 아티팩트**를 만드는 것 — 벤치마크 표 1장, before/after GIF 1개, "200줄" 같은 숫자 훅.
- 포맷: 한 줄 포지셔닝(`X, but for Y`) + 30초 데모 영상/GIF + 레포 링크. 스레드보다 단일 포스트 + 영상이 강하다.

**판정**: 팔로워가 없다면 **X는 메인이 아니라 증폭기**다. 다른 채널에서 만든 순간을 X로 확산시키는 용도.

---

### 1.4 GitHub 자체 (Trending + 마켓플레이스) — **이번 조사의 최우선 권고**

`mvanhorn/last30days-skill`: **60,810★, 5,313 forks, MIT, 2026-01-23 생성** [1차]. HN 제출들은 [3점](https://news.ycombinator.com/item?id=49130905), [2점](https://news.ycombinator.com/item?id=46963949), [2점](https://news.ycombinator.com/item?id=46764597)에 그쳤다.

이 프로젝트의 유통 경로는 **HN도 Reddit도 아닌 설치 경로 그 자체**였다 ([README](https://github.com/mvanhorn/last30days-skill)):
```
/plugin marketplace add mvanhorn/last30days-skill      # Claude Code
npx skills add mvanhorn/last30days-skill -g            # Agent Skills CLI, 50+ 호스트
```
Grok / Codex / Cursor / Copilot / Gemini CLI / claude.ai / Claude Desktop(`.mcpb`) / OpenClaw 전부 커버. README에 저자가 직접 적은 문장: *"5 of the 10 trending repos on GitHub today are Claude tools. #1: mvanhorn/last30days-skill."*

**GitHub Trending 알고리즘의 성질**: 절대 스타 수가 아니라 **star velocity**(자기 과거 평균 대비 급증)를 본다. 하루 2스타 받던 레포가 10개 받으면, 하루 50개 받던 레포가 60개 받는 것보다 트렌딩 점수가 높다. 따라서 **48시간 안에 집중**시키는 게 7일에 분산시키는 것보다 압도적으로 유리하고, 언어별 트렌딩 페이지(Python/TypeScript)는 All Languages보다 경쟁이 훨씬 낮다.
([GitHub Community 토론 #163970](https://github.com/orgs/community/discussions/163970), [스타 획득 케이스 스터디](https://gingiris.github.io/growth-tools/blog/2026/03/25/how-to-get-more-github-stars-the-definitive-guide-33k-stars-case-study/), [star-history 플레이북](https://www.star-history.com/blog/playbook-for-more-github-stars/))

**판정**: **1순위.** 베타 research 에이전트를 "설치해서 쓰는 스킬/플러그인" 형태로 포장하는 것이 이번 조사에서 가장 재현성 높은 경로다.

---

### 1.5 awesome-* 리스트 PR

- 대표 규칙: [sindresorhus/awesome CONTRIBUTING](https://github.com/sindresorhus/awesome/blob/main/contributing.md) — 제안 1건당 PR 1개, 왜 awesome한지 서술 필수. [PR 템플릿](https://github.com/sindresorhus/awesome/blob/main/pull_request_template.md).
- 타깃 리스트(이 도메인): [DavidZWZ/Awesome-Deep-Research](https://github.com/DavidZWZ/Awesome-Deep-Research), [awesome-ai-agents-2026](https://github.com/caramaschiHG/awesome-ai-agents-2026), GitHub 토픽 [`deep-research`](https://github.com/topics/deep-research) / [`deep-research-agent`](https://github.com/topics/deep-research-agent).
- 효과: **느리지만 복리.** 즉시 스파이크는 없고, 몇 달에 걸쳐 트래픽·포크·기여자가 누적되는 유형. 병합되려면 리스트 규칙(알파벳 순, 설명 길이, 링크 형식)을 정확히 지켜야 하며 안 맞으면 수정 요구를 받는다.
- **비용 대비**: PR 1개당 10분. 런칭 주 이전에 미리 5~10개 넣어두고 잊는 게 맞다. 런칭 당일 지표로 삼지 말 것.

**추가로 반드시 할 것**: GitHub **Topics** 지정. `deep-research`, `deep-research-agent`, `ai-agent`, `llm`, `mcp`, `claude-code`. 토픽 페이지가 사실상 무료 카테고리 리스팅이다.

---

### 1.6 Product Hunt

- **규칙** ([Product Hunt Launch 가이드](https://www.producthunt.com/launch)): 개인 계정으로만 등록(**회사 계정 금지**), 메이커가 직접 헌팅해도 불이익 없음, **12:01am PT 등록**이 하루 노출을 최대화. **"업보트 해달라"고 직접 요청하는 것은 금지** — "보고 코멘트 남겨달라"까지만 허용. 의미 있는 제품 이터레이션마다 재런칭 가능.
- **개발자 툴 적합도**: 여전히 유효하지만 **단독 채널로는 부족**하다는 게 2026년 공통 평가. 준비(에셋·커뮤니티 사전 동원) 없이 올리면 묻힌다.
  ([Infrasity 개발자 툴 PH 플레이북](https://www.infrasity.com/blog/product-hunt-launch-for-developer-tools), [Hackmamba 2026 가이드](https://hackmamba.io/developer-marketing/how-to-launch-on-product-hunt/))
- **판정**: 우선순위 **하**. Product Hunt 관객은 "설치해서 쓰는 CLI/스킬"보다 "가입해서 쓰는 SaaS"에 맞다. 베타 오픈소스 단계에서는 준비 비용이 수익을 못 넘긴다. 나중에 호스팅 버전이 생기면 그때.

---

### 1.7 Discord

- **MCP 커뮤니티 Discord**: 2,900+ 기여자 규모, Anthropic이 플래티넘 멤버·코어 메인테이너로 참여 [2차]. 2026년 초 기준 커뮤니티 MCP 서버 1,000개 이상 공개.
  ([MCP Discord 커뮤니티 개요](https://agentpedia.codes/mcp/discord-server), [Anthropic 공식 Discord 플러그인](https://github.com/anthropics/claude-plugins-official/blob/main/external_plugins/discord/README.md))
- **성질**: Discord는 **런칭 채널이 아니라 유지 채널**이다. 스파이크를 만들지 못하지만, 초기 사용자 10~30명의 버그 리포트를 가장 빠르게 받는 곳이다. SurfSense가 README 상단에 Discord 초대 링크를 박아두는 이유가 그것 ([SurfSense](https://github.com/MODSetter/SurfSense), 16,046★ [1차]).
- **판정**: 런칭 지표에서 제외. 단, **자기 Discord를 만들지 말고** 기존 MCP/LangChain/로컬 LLM 서버의 `#showcase` 채널에 던지는 것부터. 사용자 100명 넘기 전에 자체 서버 만드는 건 낭비.

---

### 1.8 Lobsters

- **구조적 장벽**: 초대제. 초대 트리로 스팸을 막고, 신규 유저는 **70일간 초록색 표시 + 권한 제한**.
- **자기 홍보 규칙(공식 문구)**: *"self-promo should be less than a quarter of one's stories and comments"* — 자기 글이 전체 활동의 1/4 미만. 공지/트래픽 유도용 write-only 도구로 쓰지 말 것.
- 출처: [lobste.rs/about](https://lobste.rs/about)
- **판정**: 우선순위 **하**. 규모가 HN보다 훨씬 작고, 초대를 못 구하면 시작조차 안 된다. 이미 계정이 있으면 보너스, 없으면 여기에 시간 쓰지 말 것.

---

### 1.9 dev.to / Hashnode

- **규모**: dev.to 등록 개발자 300만+, 월 방문 추정 700만 [2차] ([posterly dev.to 가이드](https://www.poster.ly/guides/devto-guide)).
- **작동 방식**: 제품 소개는 안 먹고, **튜토리얼/구현기**가 먹는다. `canonical_url` 프론트매터를 지원하므로 자기 블로그를 원본으로 두고 SEO 손실 없이 크로스포스트 가능 ([크로스포스팅 가이드](https://dasroot.net/posts/2026/03/cross-posting-technical-content-devto-medium-hashnode/)).
- **판정**: 우선순위 **중하**, 그러나 **비용이 거의 0**(이미 쓴 글 재활용). "research 에이전트를 어떻게 구현했나" 기술 글 1개를 canonical 설정해서 올려두는 것 정도.

---

### 1.10 채널 우선순위 요약

| 순위 | 채널 | 왜 | 성공 지표 |
|---:|---|---|---|
| 1 | **GitHub Trending + 스킬/플러그인 마켓플레이스** | 최근 최대 사례(`last30days`, 60.8k★)의 실제 경로. velocity 기반이라 소규모도 진입 가능 | 48h 내 star velocity, 언어별 트렌딩 진입 |
| 2 | **r/LocalLLaMA + r/ClaudeAI** | 정확히 우리 관객. 로컬 폴백·스킬 형태와 궁합 | 유의미한 댓글 수(스타 아님), 첫 이슈 제출자 |
| 3 | **X** (팔로워 자산 있을 때) / 인용 유도(없을 때) | dexter 케이스. 자산 없으면 증폭기 역할만 | 리트윗한 계정의 질 |
| 4 | awesome-* PR + GitHub Topics | 복리, 비용 0 | 병합 수 (런칭 후 몇 달) |
| 5 | Show HN | 이 카테고리는 포화. 하되 기대 낮게 | — |
| 6 | dev.to 크로스포스트, Discord `#showcase` | 잔여 비용 0 / 유지 채널 | — |
| — | Product Hunt, Lobsters | 베타 오픈소스 단계에선 ROI 미달 | — |

---

## 2. 최근 12개월 실제로 터진 유사 오픈소스 research 툴 3건

> 선정 기준: GitHub 생성일이 **2025-09-01 이후**이고, research/에이전트 카테고리이며, 2026-09-01 기준 스타 1,000★ 이상. 수치는 전부 GitHub API 직접 호출 [1차].

### 케이스 A — `virattt/dexter` (27,561★ / 3,413 forks / 2025-10-14 생성)
[github.com/virattt/dexter](https://github.com/virattt/dexter) · "An autonomous agent for deep financial research"

- **런칭 경로**: 저자 X 계정 단일 포스트 ([2025-10-14, "Introducing Dexter... ~200 lines of code. Think: Claude Code, but for finance."](https://x.com/virattt/status/1978224884464357579)) → GitHub Trending 진입(7일간 3,108스타 순증으로 24,801★ 도달, [2차](https://andrew.ooo/posts/dexter-autonomous-financial-research-agent-review/)) → 서드파티 리뷰 블로그 확산.
- **HN 성적**: [1점](https://news.ycombinator.com/item?id=46237014). 무관했다.
- **재현 가능한 것**: ① **"X, but for Y"** 포지셔닝(Claude Code, but for finance). ② **숫자 훅** — "~200 lines of code"가 트윗의 실질 후크였다. ③ **버티컬로 좁힘** — 범용 research가 아니라 금융. 범용은 이미 포화, 버티컬은 비어 있다.
- **재현 불가능한 것**: 저자가 이미 [`ai-hedge-fund` 63,114★](https://github.com/virattt/ai-hedge-fund)를 가진 상태였다. 팔로워 자산이 부트스트랩 스파이크를 만들었다.
- **주의**: dexter는 **라이선스가 없다**(GitHub API `license: null`) [1차]. 이건 따라하지 말 것 — §4 참조.

### 케이스 B — `mvanhorn/last30days-skill` (60,810★ / 5,313 forks / MIT / 2026-01-23 생성)
[github.com/mvanhorn/last30days-skill](https://github.com/mvanhorn/last30days-skill)

- **런칭 경로**: HN 아님(제출 3건 전부 2~3점). 경로는 **설치 표면 자체** — Claude Code `/plugin marketplace add`, Agent Skills CLI `npx skills add`, 그리고 Grok/Codex/Cursor/Copilot/Gemini CLI/Claude Desktop/OpenClaw까지 **50+ 호스트 동시 지원**. 거기서 GitHub Trending 상위 진입.
- **재현 가능한 것**: ① **"레포"가 아니라 "설치 가능한 스킬"로 포장**. 사용자가 `git clone` → 의존성 설치 → `.env` 세팅을 하는 순간 전환율이 붕괴한다. 한 줄 설치가 곧 유통이다. ② **다중 호스트 지원**이 곧 다중 유통 채널. ③ MIT + "No tracking. No analytics." 를 README에 명시 — 신뢰 축이 곧 마케팅 축.
- **우리와의 직접 관련**: 이 스킬은 실제로 이 사용자의 로컬 환경에도 설치되어 있다. 즉 배포 경로가 **실증적으로 관측 가능**한 사례다.

### 케이스 C — `tinyhumansai/openhuman` (39,237★ / 3,855 forks / GPL-3.0 / 2026-02-18 생성)
[github.com/tinyhumansai/openhuman](https://github.com/tinyhumansai/openhuman) · "Your Personal AI super intelligence. A brain that builds a local-first memory..."

- **런칭 경로**: 2026년 상반기를 지배한 [`openclaw/openclaw` (388,365★)](https://github.com/openclaw/openclaw) 담론에 **직접 올라탐**. HN에서 openclaw는 4자리 점수를 반복해서 찍었고([1349pts](https://news.ycombinator.com/item?id=47963204), [1099pts](https://news.ycombinator.com/item?id=47633396), [802pts](https://news.ycombinator.com/item?id=47115805)), openhuman은 "[OpenClaw is toast. OpenHuman just landed](https://news.ycombinator.com/item?id=47839564)" 같은 **제3자 프레이밍**으로 확산됐다. 자기 [Show HN은 3점](https://news.ycombinator.com/item?id=47876182).
- **재현 가능한 것**: ① **기존 대형 담론에 대한 포지션 취하기** — 새 카테고리를 만들려 하지 말고, 이미 논쟁 중인 것의 "반대편"이 되는 것. ② **local-first / 프라이버시**가 이 사이클에서 실제로 팔리는 축이라는 증거.
- **주의**: GPL-3.0. 기업 채택을 막는 라이선스인데도 39k★가 나왔다 — 즉 **스타는 라이선스와 무관**하지만 기업 도입은 별개다.

### 세 사례의 교집합
1. **HN 점수: 1점, 3점, 3점.** 셋 다 HN이 아니었다.
2. 셋 다 **설치 즉시 결과를 보여주는 것**이 있었다(200줄 코드 / 한 줄 설치 / 로컬 브레인).
3. 셋 다 **한 문장 포지셔닝**이 존재했다 — "Claude Code but for finance", "지난 30일간 사람들이 실제로 뭐라 했는지", "openclaw의 대안".

### 대조군: 최근 12개월에도 잘 안 된 사례
`lajosdeme/mole` — **298★**, 2026-08-01 생성, Apache-2.0 [1차]. [Show HN 100점](https://news.ycombinator.com/item?id=49303046)으로 이 카테고리 최근 12개월 1위였는데도 스타는 300 미만. **HN 100점 = 스타 300** 이 이 카테고리의 실제 환율이다. 이 숫자를 기대치의 기준선으로 삼을 것.

---

## 3. 상용 제품 지형

> 가격은 2026-09-01 기준. **[공식]** 표기는 이 조사에서 해당 벤더 페이지를 직접 확인한 값.

### 3.1 범용 Deep Research

| 제품 | 가격 | 강점 | 오픈소스가 못 이기는 지점 | 오픈소스가 이기는 지점 |
|---|---|---|---|---|
| **OpenAI Deep Research** (ChatGPT) | Plus $20/mo, Deep Research 월 ~10회 [2차] | 모델 품질, 브라우징 인프라 | 프론티어 모델 + 전용 브라우징 스택. 순수 품질로는 못 이김 | 결과 재현·중간 산출물 접근·자기 코퍼스 |
| **Gemini Deep Research** | 무료 티어 존재. AI Plus $4.99/mo, AI Pro $19.99/mo [2차] | Gmail/Drive/Docs 네이티브 연동, 압도적으로 싼 진입가 | **$4.99라는 가격.** "싸다"로는 절대 못 이김 | 구글 계정 밖의 데이터, 자기 도메인 툴 |
| **Perplexity** | Pro $20/mo. Sonar Deep Research API $2/M in, $8/M out + $5/1k searches [2차] | 속도(대부분 3분 내), 유일한 전용 research API | 검색 인덱스 자체 | 인용 검증 가능성, 커스텀 소스 |

> ⚠️ 위 세 줄의 **가격·한도는 서드파티 집계**다 ([findskill.ai](https://findskill.ai/blog/ai-pricing-comparison-2026/), [perspectiveai](https://perspectiveai.xyz/ai-pricing-guide-2026-every-plan-compared/), [Glasp 비교](https://glasp.co/articles/deep-research-tools-compared)). 벤더가 2026년에 한도를 크게 바꿨다는 보도가 여럿이므로(예: Perplexity Pro의 Deep Research 한도 축소), **문서·발표에 인용하기 전 공식 페이지 재확인 필수.**

### 3.2 학술 특화

| 제품 | 가격 [공식] | 강점 | 못 이기는 지점 | 이기는 지점 |
|---|---|---|---|---|
| **Elicit** ([pricing](https://elicit.com/pricing)) | Free / **Pro $49/mo** / **Scale $169/mo** / Enterprise | 1억 3,800만 논문 인덱스, 최대 5,000편 스크리닝, PRISMA급 추출, 135~200개 데이터 소스 | **논문 인덱스 자체**와 구조화 추출 파이프라인 | 가격($49~169는 개인에게 비쌈), 커스텀 스키마 |
| **Undermind** ([undermind.ai](https://www.undermind.ai/)) | Free / **Pro $16/mo**(연납) / Team $15/인/mo | 인용 체인 추적, 자체 백서 기준 "Google Scholar 대비 10배" 주장 | 논문 검색 품질 튜닝에 들어간 시간 | 커버리지 밖 소스(사내 문서, 웹, 코드) |
| **Consensus** | Free / Pro ~$10 / Deep ~$45 [2차, 공식 페이지 403] | 논문 근거 기반 YES/NO 합의 시각화 | 학술 UX | 학술 밖 도메인 |
| **Scite** | Free ~ $20/인/mo [2차] | 인용을 supporting/contrasting/mentioning으로 분류 | 인용 분류 데이터셋(고유 자산) | — |
| **NotebookLM** | Free(소스 50/노트북) / AI Plus $4.99 / AI Pro $19.99(소스 300, Deep Research 20/일) / Ultra $99.99 [2차] | UX 완성도, Audio/Video Overview | **무료 티어의 존재 자체.** "내 문서로 research"의 기본값 | 문서를 구글에 올릴 수 없는 경우, 자동화·파이프라인 편입 |

출처: [Elicit 공식 pricing](https://elicit.com/pricing) · [Undermind 공식](https://www.undermind.ai/) · [NotebookLM 가격 정리(2차)](https://elephas.app/blog/notebooklm-free-vs-plus) · [Consensus/Scite 비교(2차)](https://theaiagentindex.com/compare/scite-ai-vs-consensus)

### 3.3 포지셔닝 결론 — 싸울 축 4개

오픈소스가 상용 대비 **구조적으로** 우위인 곳은 여기뿐이다. 이 중 **하나**를 골라 README 첫 줄에 박아야 한다.

1. **데이터 경계 (Data boundary)** — "이 문서는 내 디스크를 떠나지 않는다." NotebookLM $0, Gemini $4.99를 이길 수 있는 유일한 이유. `openhuman`(local-first)과 `SurfSense`(OSS NotebookLM 대안)가 실제로 이 축으로 각각 39k★, 16k★를 얻었다.
2. **비용 구조** — 구독료가 아니라 내 API 키. 헤비 유저에게만 유효한 논리이므로 "월 100회 이상 돌린다면"이라는 조건을 같이 써야 정직하다. 참고로 `open_deep_research`는 전체 평가 1회에 **$45~200+**가 든다고 자기 README에 명시했다 — 오픈소스가 항상 싼 게 아니다.
3. **검증 가능성 (Auditability)** — 프롬프트·중간 계획·인용을 전부 열어둔다. 상용 제품은 구조적으로 이걸 못 준다. `mole`이 "enforced budget, verified quotes, privacy boundary"로 잡은 축이 정확히 이것이고, HN에서 이 카테고리 최고점을 받은 이유다(스타로는 전환 안 됐지만).
4. **확장성** — 내 도메인 툴/사내 DB/MCP 서버를 붙일 수 있다. 상용은 벤더가 허용한 커넥터만.

**하지 말아야 할 포지셔닝**: "OpenAI Deep Research보다 좋다". [Show HN: My Open Source Deep Research tools beats Google and I can Prove it](https://news.ycombinator.com/item?id=46848479) → **17점**. 실증적으로 안 먹힌다.

---

## 4. 베타 단계 런칭 체크리스트 (실증 근거 부착)

### 필수 (하나라도 빠지면 유입이 새는 곳)

- [ ] **한 문장 포지셔닝** — `<익숙한 것>, but for <좁은 도메인>` 또는 `<제약> 하에서 <결과>`.
      *근거*: dexter의 "Claude Code, but for finance" / HN 500+ 상위권이 전부 제약 기반 제목.
- [ ] **30초 설치 — 한 줄 명령어**. `git clone` + `pip install -r` + `.env` 편집은 실패로 간주.
      *근거*: `last30days-skill`(60.8k★)의 유통 경로 자체가 `npx skills add ...` / `/plugin marketplace add ...` 였다.
- [ ] **README 안에 인라인 데모 GIF**. 랜딩페이지 아님 — **레포가 랜딩페이지다**.
      *근거*: HN 공식 팁이 "직접 돌려볼 수 있어야" / README 디자인에서 "인라인 데모가 단일 최중요 요소"라는 게 공통 권고.
      *도구*: [charmbracelet/vhs](https://github.com/charmbracelet/vhs) — `.tape` 파일로 터미널 데모를 **코드로** 기록(창 크기·테마·타이핑 속도·일시정지 지정, GIF/MP4/WebM 출력). 대안 asciinema + agg. 수동 녹화는 재촬영 비용 때문에 유지가 안 된다.
- [ ] **LICENSE 파일** — 없으면 기본값은 "모든 권리 유보"이고 기업은 손도 못 댄다.
      *근거*: 이번에 조사한 성공 레포의 라이선스 분포 [1차] — MIT: `last30days-skill`, `deer-flow`, `local-deep-research`, `open_deep_research`, `browser-use`, `dzhng/deep-research`, `storm`. Apache-2.0: `gpt-researcher`, `mole`. GPL-3.0: `openhuman`. **없음: `dexter`**(27k★인데도 라이선스 없음 — 채택 관점에서는 결함).
      → **MIT를 권장.** 이 카테고리 성공 사례의 다수파이고 채택 마찰이 가장 낮다.
- [ ] **GitHub Topics 지정** — `deep-research`, `deep-research-agent`, `ai-agent`, `llm`, `mcp`, `claude-code`. 토픽 페이지가 무료 카테고리 리스팅.
- [ ] **"아직 못 하는 것" 섹션** — README와 첫 HN/Reddit 댓글 양쪽에.
      *근거*: HN 런칭 가이드 공통 권고 — 한계를 먼저 밝히면 비판이 대화로 바뀐다. 이 관객은 마케팅 문장을 즉시 감지한다.

### 강력 권장

- [ ] **재현 가능한 평가 결과 1개** — 벤치마크 표, 또는 "N개 질의에서 recall X/N, false positive Y". 스크립트도 같이.
      *근거*: r/MachineLearning `[P]`와 r/LocalLLaMA에서 실제로 통과하는 유일한 포맷. 그리고 X에서 인용 가능한 아티팩트가 된다.
- [ ] **이슈 템플릿** (`.github/ISSUE_TEMPLATE/bug_report.yml`, `feature_request.yml`) — 첫 100명이 오면 재현 정보 없는 이슈가 쏟아진다.
- [ ] **로컬 모델 폴백 경로 문서화** — r/LocalLLaMA 진입권이자, 네트워크 제약 환경 대응. (이 사용자의 경우 Ollama/qwen 폴백 요구사항과 정확히 일치)
- [ ] **비용 정직 표기** — "1회 실행에 대략 $X". `open_deep_research`가 $45~200+를 명시한 것처럼. 이걸 숨기면 첫 이슈가 "왜 이렇게 비싸냐"가 된다.

### 런칭 실행 순서 (48시간 압축 — velocity 알고리즘 대응)

1. **D-7**: awesome-* PR 5~10개 제출(병합은 나중에 와도 됨), Topics 지정, LICENSE·GIF·이슈 템플릿 완비.
2. **D-1**: 스킬/플러그인 마켓플레이스 등록(Claude Code, Agent Skills CLI). 설치 명령어 실제로 처음부터 검증.
3. **D-Day 화/수/목**:
   - 오전 — r/LocalLLaMA + r/ClaudeAI (각각 다른 앵글. 같은 글 복붙 금지, 크로스포스팅은 양쪽에서 감점)
   - 같은 날 — X 단일 포스트 + 30초 데모 영상
   - 같은 날 ET 09~12시 — Show HN (기대치: **100점 = 스타 300** 환율)
   - Discord `#showcase` 채널들
4. **D+1~2**: 모든 스레드에 붙어서 응답. GitHub Trending은 이 48시간 velocity로 결정된다.
5. **D+7**: dev.to에 구현기 크로스포스트(canonical_url 설정).

**성공 판정 기준(정직하게)**: 스타가 아니라 **① 설치 후 실제로 돌렸다는 리포트, ② 재현 정보가 붙은 첫 버그 이슈, ③ 첫 외부 PR**. 위 3사례 중 어느 것도 첫 주에 스타로 성공을 판단하지 않았다.

---

## 부록 — 이번 조사에서 직접 확인한 레포 스냅샷 [1차, GitHub API, 2026-09-01]

| 레포 | ★ | forks | 라이선스 | 생성일 | 비고 |
|---|---:|---:|---|---|---|
| [openclaw/openclaw](https://github.com/openclaw/openclaw) | 388,365 | — | — | 2025-11-24 | 2026 상반기 담론 지배 |
| [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent) | 239,102 | — | — | 2025-07-22 | |
| [firecrawl/firecrawl](https://github.com/firecrawl/firecrawl) | 174,925 | — | — | 2024-04-15 | |
| [browser-use/browser-use](https://github.com/browser-use/browser-use) | 111,881 | 12,288 | MIT | 2024-10-31 | [Launch HN 259pts](https://news.ycombinator.com/item?id=43173378) (YC W25) |
| [bytedance/deer-flow](https://github.com/bytedance/deer-flow) | 81,195 | 11,195 | MIT | 2025-05-07 | HN 최고 4점 |
| [unclecode/crawl4ai](https://github.com/unclecode/crawl4ai) | 80,616 | — | — | 2024-05-09 | |
| [virattt/ai-hedge-fund](https://github.com/virattt/ai-hedge-fund) | 63,114 | 11,098 | MIT | 2024-11-29 | dexter의 팔로워 자산 원천 |
| [mvanhorn/last30days-skill](https://github.com/mvanhorn/last30days-skill) | 60,810 | 5,313 | MIT | 2026-01-23 | **케이스 B** |
| [tinyhumansai/openhuman](https://github.com/tinyhumansai/openhuman) | 39,237 | 3,855 | GPL-3.0 | 2026-02-18 | **케이스 C** |
| [stanford-oval/storm](https://github.com/stanford-oval/storm) | 31,193 | 2,937 | MIT | 2024-03-24 | 2025-09-30 이후 push 없음 |
| [assafelovic/gpt-researcher](https://github.com/assafelovic/gpt-researcher) | 29,228 | 3,964 | Apache-2.0 | 2023-05-12 | Show HN 4점 |
| [virattt/dexter](https://github.com/virattt/dexter) | 27,561 | 3,413 | **없음** | 2025-10-14 | **케이스 A** |
| [Alibaba-NLP/DeepResearch](https://github.com/Alibaba-NLP/DeepResearch) | 19,898 | — | — | 2025-01-09 | [HN 365pts](https://news.ycombinator.com/item?id=45789602) |
| [dzhng/deep-research](https://github.com/dzhng/deep-research) | 19,620 | 1,992 | MIT | 2025-02-04 | |
| [MODSetter/SurfSense](https://github.com/MODSetter/SurfSense) | 16,046 | 1,535 | (비표준) | 2024-07-30 | OSS NotebookLM 대안 |
| [langchain-ai/open_deep_research](https://github.com/langchain-ai/open_deep_research) | 12,680 | 1,821 | MIT | 2024-11-20 | **2026-08-21 아카이브됨** |
| [LearningCircuit/local-deep-research](https://github.com/LearningCircuit/local-deep-research) | 9,014 | 800 | MIT | 2025-02-09 | [HN 190pts](https://news.ycombinator.com/item?id=43330164) |
| [zilliztech/deep-searcher](https://github.com/zilliztech/deep-searcher) | 8,232 | — | — | 2025-02-08 | [HN 229pts](https://news.ycombinator.com/item?id=43172338) |
| [lajosdeme/mole](https://github.com/lajosdeme/mole) | 298 | 16 | Apache-2.0 | 2026-08-01 | [HN 100pts](https://news.ycombinator.com/item?id=49303046) — 환율 대조군 |

> **한 가지 경고 신호**: LangChain의 `open_deep_research`가 **2026-08-21 아카이브**됐다. 12.7k★ 프로젝트가 유지 중단된 것은 이 카테고리의 유지비가 높고 벤더 기능에 잠식된다는 신호다. 베타 단계부터 "유지 범위"를 README에 좁게 명시하는 편이 낫다.

---

## 조사 한계 (숨기지 않고 명시)

- **Reddit 직접 접근 차단**: `reddit.com`/`old.reddit.com` 모두 이 환경에서 403 또는 HTML 셸을 반환했다. §1.2의 구독자 수·규칙 요약은 서드파티 집계 기반이며, 런칭 전 각 서브레딧 규칙 페이지를 직접 확인해야 한다.
- **가격 정보 중 일부는 2차 출처**: OpenAI/Gemini/Perplexity/Consensus/Scite/NotebookLM 가격은 공식 페이지 접근 실패(403) 또는 미확인이다. Elicit·Undermind만 공식 페이지에서 직접 확인했다. 실제로 Elicit은 서드파티 집계가 "$0~79" 또는 "$120~780"으로 서로 모순됐고 **공식값은 Pro $49 / Scale $169**였다 — 집계 사이트를 신뢰하면 안 된다는 직접 증거다.
- **X/Twitter 인게이지먼트 수치 미확보**: dexter 트윗의 실제 임프레션·리트윗 수는 확인하지 못했다. 트윗 존재와 문구만 확인했다.
