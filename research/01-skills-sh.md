# skills.sh 레지스트리 조사 — research 특화 에이전트 베타 출시 관점

조사일: 2026-09-01 · 조사자: Orca worker (task_9290f981caeb)
조사 방법: 로컬 `skills` CLI(`/opt/homebrew/bin/skills`) 실검색 + skills.sh 웹/문서 WebFetch + GitHub API(`gh api`)로 star·생성일 교차확인.

표기 규칙:
- **[사실]** = 이 조사에서 직접 관측한 CLI 출력·웹 문서·GitHub API 응답.
- **[추론]** = 관측값에서 끌어낸 해석. 검증 안 된 가설.
- 설치수는 CLI가 출력한 반올림 값(예: `417.7K`). 조사 시점 스냅샷이며 매일 변한다.

---

## 1. 레지스트리 실검색 결과

`skills find <query>`는 비대화형(`< /dev/null`)으로도 실행되며, 설치수 내림차순으로 결과를 낸다. **[사실]**

> 관측 특이점 **[사실]**: `skills find search`의 상위 결과가 `skills find research`와 거의 동일했다(1~4위가 `research`, `ai-research-explore`, `ai-research-reproduction`, `customer-research`). `web` 검색도 `website-to-video`, `web-search` 등을 반환했다.
> → **[추론]** `find`는 스킬 **이름 문자열의 부분일치**로 매칭하고 설치수로 정렬한다. 설명(description) 전문검색이 아니다. **이름에 어떤 토큰을 넣느냐가 곧 발견 가능성이다.**

### 1-1. `skills find research` (상위 19건) **[사실]**

| # | owner/repo@skill | 설치수 | 링크 |
|---|---|---|---|
| 1 | mattpocock/skills@research | 417.7K | https://skills.sh/mattpocock/skills/research |
| 2 | lllllllama/rigorpilot-skills@ai-research-explore | 311.1K | https://skills.sh/lllllllama/rigorpilot-skills/ai-research-explore |
| 3 | lllllllama/rigorpilot-skills@ai-research-reproduction | 310.9K | https://skills.sh/lllllllama/rigorpilot-skills/ai-research-reproduction |
| 4 | coreyhaines31/marketingskills@customer-research | 87K | https://skills.sh/coreyhaines31/marketingskills/customer-research |
| 5 | nexscope-ai/amazon-skills@amazon-product-research | 77.6K | https://skills.sh/nexscope-ai/amazon-skills/amazon-product-research |
| 6 | firecrawl/firecrawl-workflows@firecrawl-deep-research | 33.5K | https://skills.sh/firecrawl/firecrawl-workflows/firecrawl-deep-research |
| 7 | firecrawl/firecrawl-workflows@firecrawl-research-papers | 32.6K | https://skills.sh/firecrawl/firecrawl-workflows/firecrawl-research-papers |
| 8 | firecrawl/firecrawl-workflows@firecrawl-market-research | 31.8K | https://skills.sh/firecrawl/firecrawl-workflows/firecrawl-market-research |
| 9 | firecrawl/firecrawl-workflows@firecrawl-lead-research | 31K | https://skills.sh/firecrawl/firecrawl-workflows/firecrawl-lead-research |
| 10 | googleworkspace/cli@persona-researcher | 27.6K | https://skills.sh/googleworkspace/cli/persona-researcher |
| 11 | firecrawl/skills@firecrawl-research-index | 19.8K | https://skills.sh/firecrawl/skills/firecrawl-research-index |
| 12 | tavily-ai/skills@tavily-research | 17.2K | https://skills.sh/tavily-ai/skills/tavily-research |
| 13 | warpdotdev/common-skills@research | 16.8K | https://skills.sh/warpdotdev/common-skills/research |
| 14 | parallel-web/parallel-agent-skills@parallel-deep-research | 13.7K | https://skills.sh/parallel-web/parallel-agent-skills/parallel-deep-research |
| 15 | tavily-ai/skills@research | 6.6K | https://skills.sh/tavily-ai/skills/research |
| 16 | langchain-ai/deepagents@web-research | 3.9K | https://skills.sh/langchain-ai/deepagents/web-research |
| 17 | apify/agent-skills@apify-market-research | 3.4K | https://skills.sh/apify/agent-skills/apify-market-research |
| 18 | anthropics/knowledge-work-plugins@research-synthesis | 3.3K | https://skills.sh/anthropics/knowledge-work-plugins/research-synthesis |
| 19 | github/awesome-copilot@autoresearch | 3.3K | https://skills.sh/github/awesome-copilot/autoresearch |

### 1-2. `skills find deep-research` (상위 14건) **[사실]**

| # | owner/repo@skill | 설치수 |
|---|---|---|
| 1 | firecrawl/firecrawl-workflows@firecrawl-deep-research | 33.5K |
| 2 | parallel-web/parallel-agent-skills@parallel-deep-research | 13.7K |
| 3 | code.deepline.com@deepline-pre-research | 10.9K |
| 4 | 199-biotechnologies/claude-deep-research-skill@deep-research | 9.6K |
| 5 | affaan-m/ecc@deep-research | 8.7K |
| 6 | imbad0202/academic-research-skills@deep-research | 6.1K |
| 7 | claude-office-skills/skills@deep-research | 4.2K |
| 8 | langchain-ai/deepagents@web-research | 3.9K |
| 9 | shubhamsaboo/awesome-llm-apps@deep-research | 3.8K |
| 10 | bytedance/deer-flow@github-deep-research | 2.5K |
| 11 | bytedance/deer-flow@deep-research | 2.3K |
| 12 | samber/cc-skills@deep-research | 2.1K |
| 13 | lingzhi227/agent-research-skills@deep-research | 1.6K |
| 14 | daymade/claude-code-skills@deep-research | 1.3K |

> **[사실]** `deep-research`라는 이름의 스킬은 최소 10개 이상이 서로 다른 owner 아래 중복 존재하며, 최상위조차 33.5K로 `research`(417.7K)보다 한 자릿수 낮다.

### 1-3. `skills find paper` (상위 14건) **[사실]**

| # | owner/repo@skill | 설치수 |
|---|---|---|
| 1 | lllllllama/rigorpilot-skills@paper-context-resolver | 450.8K |
| 2 | firecrawl/firecrawl-workflows@firecrawl-research-papers | 32.6K |
| 3 | yuan1z0825/nature-skills@nature-paper2ppt | 9.7K |
| 4 | lllllllama/rigorpilot-skills@ai-paper-reproduction | 9.1K |
| 5 | imbad0202/academic-research-skills@academic-paper | 8.7K |
| 6 | imbad0202/academic-research-skills@academic-paper-reviewer | 7.9K |
| 7 | yuan1z0825/nature-skills@nature-paper-to-patent | 6.6K |
| 8 | lijigang/ljg-skills@ljg-paper | 6.6K |
| 9 | lijigang/ljg-skills@ljg-paper-flow | 5.4K |
| 10 | lijigang/ljg-skills@ljg-paper-river | 5.2K |
| 11 | bahayonghang/academic-writing-skills@latex-paper-en | 5.1K |
| 12 | yuan1z0825/nature-skills@nature-paper-card | 4.4K |
| 13 | paperclipai/paperclip@paperclip | 3.3K |
| 14 | ailabs-393/ai-labs-claude-skills@research-paper-writer | 3.2K |

### 1-4. `skills find literature` (상위 14건) **[사실]**

| # | owner/repo@skill | 설치수 |
|---|---|---|
| 1 | yuan1z0825/nature-skills@nature-literature-pipeline | 6.1K |
| 2 | affaan-m/ecc@literature-review | 5.3K |
| 3 | lingzhi227/agent-research-skills@literature-review | 3.6K |
| 4 | google-deepmind/science-skills@literature-search-arxiv | 2.4K |
| 5 | lingzhi227/agent-research-skills@literature-search | 2.3K |
| 6 | google-deepmind/science-skills@literature-search-openalex | 2.2K |
| 7 | bytedance/deer-flow@systematic-literature-review | 1.9K |
| 8 | google-deepmind/science-skills@literature-search-europepmc | 1.9K |
| 9 | google-deepmind/science-skills@literature-search-biorxiv | 1.8K |
| 10 | k-dense-ai/scientific-agent-skills@literature-review | 1.5K |
| 11 | huangwb8/chineseresearchlatex@systematic-literature-review | 841 |
| 12 | collaborative-deep-research/agent-papers-cli@literature-review | 720 |
| 13 | mims-harvard/tooluniverse@tooluniverse-literature-deep-research | 634 |
| 14 | yorkeccak/scientific-skills@literature-search | 598 |

> **[사실]** `literature` 카테고리 최상위가 6.1K다. `research`(417.7K)와 비교하면 **70배 차이**. 학술 문헌 쪽은 시장이 작거나 아직 승자가 없다.

### 1-5. `skills find search` / `web` (부분일치 확인용) **[사실]**

`search`에서 research 계열을 뺀 순수 검색 스킬:

| owner/repo@skill | 설치수 |
|---|---|
| firecrawl/cli@firecrawl-search | 81.1K |
| skills-101/superpowers@web-search | 62.6K |
| firecrawl/skills@firecrawl-build-search | 59.4K |
| anysearch-ai/anysearch-skill@anysearch | 37.3K |
| skills.volces.com@byted-web-search | 40.7K |

`web` 상위(참고 — 대부분 research 무관, 디자인/테스트 계열): vercel-labs/agent-skills@web-design-guidelines 596.1K, leonxlnx/taste-skill@imagegen-frontend-web 253.6K, anthropics/skills@webapp-testing 147.2K.

### 1-6. 인접 카테고리 탐침 **[사실]**

| 쿼리 | 1위 | 설치수 | 관측 |
|---|---|---|---|
| `arxiv` | karpathy/nanochat@read-arxiv-paper | 2.6K | 전체가 3K 미만. 매우 얇다 |
| `citation` | yuan1z0825/nature-skills@nature-citation | 9.5K | 2위부터 1.8K로 급락 |
| `zotero` | k-dense-ai/scientific-agent-skills@pyzotero | 1.3K | 전부 1.3K 이하 |
| `peer-review` | k-dense-ai/scientific-agent-skills@peer-review | 1.4K | 4건 전부 1.5K 이하 |
| `hypothesis` | deanpeters/product-manager-skills@epic-hypothesis | 2K | 과학용은 1.4K |
| `grant` | k-dense-ai/scientific-agent-skills@research-grants | 1.3K | 사실상 무주공산 |
| `survey` | refoundai/lenny-skills@designing-surveys | 1.9K | 설문설계지 서베이논문 아님 |
| `fact-check` | shubhamsaboo/awesome-llm-apps@fact-checker | 3.3K | 전부 3.3K 이하 |
| `notebooklm` | teng-lin/notebooklm-py@notebooklm | 8.9K | |
| `competitor` | coreyhaines31/marketingskills@competitor-profiling | 67.7K | **비즈니스 리서치는 자릿수가 다르다** |
| `obsidian` | mattpocock/skills@obsidian-vault | 201.3K | 노트 파이프라인 수요 큼 |
| `korean` | nomadamas/k-skill@korean-law-search | 4.6K | 한국어 스킬 전반 5K 이하 |

---

## 2. skills.sh 레지스트리 동작 방식

### 2-1. 등록 방법 — **별도 등록 절차가 없다** **[사실]**

Vercel 공식 KB 문서: "There's **no special publish command**." 스킬을 git 저장소에 두고 `npx skills add owner/repo`로 설치되면, **설치 텔레메트리를 통해 skills.sh에 자동으로 나타난다.**
출처: [Vercel KB — Agent Skills: Creating, Installing, and Sharing Reusable Agent Context](https://vercel.com/kb/guide/agent-skills-creating-installing-and-sharing-reusable-agent-context)

- 필수 요건: `SKILL.md` + YAML frontmatter의 `name`(부모 디렉터리명과 일치, 소문자·숫자·하이픈만), `description`(무엇을 하는지 + **언제 쓰는지**). **[사실]**
- 권장 필드: `license`, `compatibility`, `metadata`(semver 등), `allowed-tools`(experimental). **[사실]**
- 권장 구조: `README.md`, 라이선스, 스크립트 안전성 노트, `scripts/` `references/` `assets/`. **[사실]**

> **[사실·주의]** 이 "자동 인덱싱"이 어느 시점에 트리거되는지는 **공식 문서에 명시돼 있지 않다.** 실제로 vercel-labs/skills 저장소에 [Issue #880 "How to submit/publish a new skill?"](https://github.com/vercel-labs/skills/issues/880)이 열려 있고 — 질문자 choigawoon이 "공개 GitHub repo를 자동 인덱싱하는가, 아니면 어딘가에 수동 제출해야 하는가"를 물었으나 — **조사 시점 기준 메인테이너 답변이 달려 있지 않다**(assignee·label·연결 PR 없음).
> → **[추론]** 첫 설치가 발생해야 등록된다면, 베타 런칭 시 **본인이 직접 최소 1회 `npx skills add`로 설치해 시드**해야 목록에 뜬다. 이건 실측으로 확인해야 할 항목이다.

### 2-2. 랭킹 = 설치 텔레메트리 **[사실]**

- skills.sh 문서: "The skills leaderboard ranks skills based on **anonymous telemetry data collected from the `skills` CLI**." 수집 대상은 "the skill name, skill files, and a timestamp—no personal or device information."
- 옵트아웃: `DISABLE_TELEMETRY=1`.
- README 배지 제공: `[![skills.sh](https://skills.sh/b/owner/repo)](https://skills.sh/owner/repo)`
출처: [skills.sh/docs](https://skills.sh/docs)

> **[추론·리스크]** 랭킹이 순수 설치 카운트 기반이고 개인정보 수집이 없다는 것은 곧 **중복 설치·CI 설치가 그대로 카운트될 수 있다**는 뜻이다. 설치수는 품질 지표가 아니라 유통 지표로 읽어야 한다. (아래 3-2의 별↔설치수 역전 현상이 이 해석을 뒷받침한다.)

### 2-3. 노출 면 **[사실]**

- 메인 페이지에 **Skills Leaderboard**: `All Time (1,348,407)` / `Trending (24h)` / `Hot` 뷰. 총 등록 스킬 수가 130만 건대라는 뜻이 아니라 표시된 카운터 값이며, 정확한 의미는 페이지에 설명이 없다. **[사실 — 값 그대로 인용]**
- 스킬별 상세 페이지에 표시되는 것: 설치수, GitHub star 수, **First seen 날짜**, 그리고 **보안 감사 배지 3종 — Gen Agent Trust Hub / Socket / Snyk (Pass / Warning)**. **[사실]** (예: [mattpocock/skills/research](https://skills.sh/mattpocock/skills/research)는 3종 모두 Pass, [rigorpilot/ai-research-explore](https://skills.sh/lllllllama/rigorpilot-skills/ai-research-explore)는 3종 모두 Warning)
- 지원 에이전트: Claude Code, Cursor, GitHub Copilot, Windsurf, Gemini 등. **[사실]**
- 참고: Snyk×Vercel 보안 파트너십 공식 블로그 — [Securing the Agent Skill Ecosystem](https://snyk.io/blog/snyk-vercel-securing-agent-skill-ecosystem/)
- `https://skills.sh/leaderboard`, `https://skills.sh/docs/overview`는 **404**였다. 리더보드는 루트 페이지에 있다. **[사실]**

### 2-4. 발견 경로가 하나 더 있다: `find-skills` (전체 1위, 3.2M 설치) **[사실 — 중요]**

skills.sh 전체 1위 스킬은 `vercel-labs/skills@find-skills`(3.2M)로, **에이전트가 다른 스킬을 찾아 추천할 때 쓰는 메타 스킬**이다. 그 SKILL.md가 명시한 선별 기준:

- `npx skills find [query]`와 skills.sh 리더보드를 본다
- **설치수 1K 이상 선호, 100 미만은 회의적으로 취급**
- `vercel-labs`, `anthropics`, `microsoft` 같은 공식 owner 신뢰
- **GitHub star 100 미만 저장소는 주의**

출처: [vercel-labs/skills — find-skills/SKILL.md](https://github.com/vercel-labs/skills/blob/main/skills/find-skills/SKILL.md)

> **[추론 — 베타 런칭의 핵심 제약]** 신규 스킬은 이 필터에 전부 걸린다(설치 0, star 0). 즉 **콜드스타트가 구조적으로 불리하다.** 초기에 star 100+ / 설치 1K+를 넘기기 전까지는 에이전트 자동 추천 경로가 사실상 닫혀 있고, 사람이 직접 링크를 보고 설치하는 경로만 열려 있다.

---

## 3. 상위 스킬이 인기인 이유 — 관측된 패턴

### 패턴 1. 설치수는 **스킬 단위가 아니라 저장소(번들) 단위로 끌려 올라간다** **[추론, 근거 강함]**

1위 `mattpocock/skills@research`의 SKILL.md 전문은 **frontmatter 포함 13줄**이다. **[사실 — `gh api`로 원문 확인]**

```
name: research
description: Investigate a question against high-trust primary sources and capture
  the findings as a Markdown file in the repo. Use when the user wants a topic
  researched, docs or API facts gathered, or reading legwork delegated to a
  background agent.

Spin up a background agent to do the research, so you keep working while it reads.
1. Investigate the question against primary sources ... not a secondary write-up
2. Write the findings to a single Markdown file, citing each claim's source.
3. Save it where the repo already keeps such notes ...
```

이게 417.7K로 research 카테고리 1위다. 같은 저장소의 `obsidian-vault`도 201.3K. 저장소 star는 **243,086**. **[사실 — GitHub API]**
→ **[추론]** 이 저장소는 `skills add mattpocock/skills`로 통째로 설치되는 번들이고, 저장소 인지도가 개별 스킬 설치수를 그대로 밀어 올린다. **깊이가 순위를 만든 게 아니다.**

같은 논리가 firecrawl(9개 스킬이 19.8K~81.1K로 고르게 분포), coreyhaines31/marketingskills(53.8K~87K 4건 밀집)에도 보인다. **[사실]**

### 패턴 2. star와 설치수가 **역전**한다 — 유통 채널이 별보다 세다 **[사실 + 추론]**

| repo | GitHub star | 대표 스킬 설치수 |
|---|---|---|
| mattpocock/skills | 243,086 | 417.7K |
| Imbad0202/academic-research-skills | **44,454** | **8.7K** |
| lllllllama/RigorPilot-Skills | **480** | **450.8K** |
| google-deepmind/science-skills | 2,809 | 2.4K |
| firecrawl/firecrawl-workflows | 145 | 33.5K |
| lingzhi227/agent-research-skills | 301 | 3.6K |

(star·생성일 전부 `gh api repos/<r>` 실측 **[사실]**)

star 44K인 academic-research-skills가 8.7K 설치인데, star 480짜리 RigorPilot이 450.8K 설치다.
→ **[추론]** 설치수는 "인기"가 아니라 **CLI 유통 경로에 얼마나 잘 물려 있는가**를 잰다. RigorPilot의 비정상적 격차는 (a) 어떤 상위 배포판/템플릿에 번들돼 반복 설치되거나 (b) 자동화된 반복 설치가 카운트되는 상황을 의심할 만하다. **검증 안 됨 — 단정하지 말 것.** 참고로 이 저장소 스킬들은 skills.sh 보안 배지 3종이 모두 Warning이다 **[사실]**.

### 패턴 3. **이름이 검색 인터페이스다** — 짧은 일반명사가 이긴다 **[추론, 근거 강함]**

`find`가 이름 부분일치라는 관측(1-0)과 결합하면:
- `research`(417.7K) > `deep-research`(33.5K) > `literature-review`(5.3K) — **이름이 짧고 일반적일수록 상위**.
- 반대로 firecrawl·tavily·nature·ljg 계열은 **브랜드 접두사**를 붙였다(`firecrawl-deep-research`, `nature-citation`, `ljg-paper`). 이건 `firecrawl` 쿼리에서 자기 스킬을 싹쓸이하는 대신, `research` 일반 쿼리에서 순위가 밀린다.
→ **[추론]** 접두사는 브랜드 방어에 유리하고 일반 발견에 불리하다. 트레이드오프를 의식적으로 선택해야 한다.

### 패턴 4. 상위권은 **"어떻게 조사하나"가 아니라 "무엇에 접속하나"를 판다** **[사실 + 추론]**

- firecrawl / tavily / parallel-web / apify / anysearch: 전부 **자사 검색 API 붙이는 스킬**. **[사실]**
- google-deepmind/science-skills는 37개 스킬 중 대부분이 **DB 커넥터**(uniprot, pubmed, chembl, gnomad, alphafold …). 문헌검색은 arxiv/openalex/europepmc/biorxiv 4개뿐. **[사실 — repo contents 실측]**
→ **[추론]** 벤더는 "리서치 방법론"이 아니라 **데이터 접근권**을 판다. 방법론만 있는 스킬(mattpocock@research 13줄)은 짧아도 1위를 하는데, 그 이유는 방법론의 깊이가 아니라 패턴 1(번들 유통) 때문이다. **방법론 깊이로 이기려는 전략은 현재 이 레지스트리에서 검증된 적이 없다.**

### 패턴 5. description에 **"when to use it"**을 쓰는 게 문서 규범이다 **[사실]**

Vercel KB가 description에 "what it does **and when to use it**"을 요구하고, 본문 구조로 purpose / usage context / inputs / step-by-step / validation criteria / **common failure modes**를 권장한다. 1위 mattpocock@research의 description도 정확히 이 형식("... **Use when** the user wants a topic researched...")이다. **[사실]**
→ **[추론]** 에이전트가 스킬을 자동 선택할 때 읽는 게 description이므로, 여기가 실사용 발동률을 좌우한다. 설치수와는 별개 축이다.

### 패턴 6(보조). 상위권은 **최근에 생겼다** **[사실]**

mattpocock/skills 2026-02-03 생성, RigorPilot 2026-03-30, firecrawl-workflows 2026-05-14, google-deepmind/science-skills 2026-05-13. 대부분 6개월 이내.
→ **[추론]** 생태계가 아직 어리다. 선점 여지가 남아 있고, 동시에 아무도 "정본"으로 굳어지지 않았다.

---

## 4. research 카테고리의 빈 구멍 (gap)

각 항목은 **[사실]인 관측 근거 → [추론]인 기회 판단** 순서로 적었다.

### Gap A. 문헌·학술 축 전체가 비어 있다 (가장 큰 구멍)
**[사실]** `literature` 1위 6.1K, `arxiv` 1위 2.6K, `citation` 2위부터 1.8K, `zotero` 1위 1.3K, `peer-review` 1위 1.4K, `grant` 1위 1.3K. 반면 `research` 1위는 417.7K, `competitor-profiling`은 67.7K.
**[추론]** 비즈니스/마케팅 리서치는 이미 자릿수가 다르고 경쟁이 붙었다. **학술 문헌 쪽은 1위가 한 자릿수 K에 머물러 "아무도 이기지 못한 상태"다.** 다만 이게 기회인지 수요 부재인지는 이 데이터만으로 구분 불가 — **[추론·미검증]**. 확인하려면 학술 스킬 저장소들의 star(academic-research-skills 44K star vs 8.7K 설치)를 보라. star는 높은데 설치가 안 된다는 건 **수요는 있는데 유통이 안 되고 있다**는 쪽에 가깝다.

### Gap B. **검증(verification) 레이어가 없다**
**[사실]** `fact-check` 전체가 3.3K 이하, `citation-verification`(galaxy-dawn/claude-scholar) 1.3K, `citation-audit`(wanshuiyin) 340, `citation-validator`(liangdabiao) 214.
**[사실]** 반면 "조사해서 보고서 쓴다"는 스킬은 `deep-research` 이름만 10개 이상 중복 존재한다.
**[추론]** 생태계 전체가 **생성(리서치 수행)에 몰려 있고 검증(할루시네이션 인용·죽은 링크·출처 왜곡 탐지)에는 사실상 아무도 없다.** LLM 리서치의 가장 큰 실패모드가 정확히 거기인데도 그렇다. 여기가 가장 방어 가능한 자리로 보인다.

### Gap C. 서로 다른 `deep-research` 10개가 **상호 호환 규격이 없다**
**[사실]** `deep-research`라는 동일 이름 스킬이 firecrawl / parallel-web / 199-biotechnologies / affaan-m / imbad0202 / claude-office-skills / shubhamsaboo / bytedance / samber / lingzhi227 / daymade 등에 각각 존재.
**[추론]** 출력 포맷(노트 스키마, 인용 형식, 파일 배치)의 공통 규격이 없다. **여러 리서치 스킬의 결과물을 하나로 합치는 오케스트레이션/스키마 계층**이 비어 있다. 다만 표준을 제안하는 건 채택률 싸움이라 베타 단계에서 어렵다 — **[추론·리스크]**.

### Gap D. 재현 가능한 리서치 산출물(감사 추적)
**[사실]** RigorPilot이 `ai-research-reproduction`(310.9K), `ai-paper-reproduction`(9.1K)으로 재현성 축을 잡고 있으나 그 저장소는 보안 배지 3종 Warning이고 star 480이다.
**[추론]** "무엇을 검색했고 어떤 소스를 읽었고 무엇을 버렸는가"를 **재실행 가능한 로그로 남기는** 스킬은 관측되지 않았다. mattpocock@research는 "cite each claim"까지만 요구하고 과정 로그는 없다.

### Gap E. 비영어 / 한국어 1차 소스
**[사실]** `korean` 검색 전체가 5K 이하(nomadamas/k-skill 계열이 상위 독점, 4.6K). `huangwb8/chineseresearchlatex`가 841.
**[추론]** 한국 공공데이터·논문DB(RISS/KCI)·법령·기업공시를 1차 소스로 다루는 리서치 스킬은 비어 있다. 시장이 작지만 경쟁도 0에 가깝다. (사용자의 기존 k-skill 자산과 인접 — 별도 검토 필요)

### Gap F. 노트 시스템과의 연결
**[사실]** `obsidian` 축은 mattpocock@obsidian-vault 201.3K, kepano/obsidian-skills 4종이 65.9K~82.7K로 **매우 두껍다**. `notebooklm`도 8.9K.
**[사실]** 그러나 `literature`·`citation`·`zotero` 축은 1K대다.
**[추론]** **"노트 수요는 크고 학술 수요는 작다"**가 아니라, **둘을 잇는 스킬이 없다**로 읽는 게 맞다(zotero-obsidian-bridge가 401 설치로 존재하긴 함). 리서치 결과를 기존 노트 볼트 컨벤션에 맞춰 떨구는 건 mattpocock@research도 3번 항목에서 요구하는 바다.

---

## 5. 베타 런칭 관점 요약 (전부 [추론])

1. **가장 큰 제약은 품질이 아니라 콜드스타트다.** `find-skills`(3.2M)가 설치 1K·star 100 미만을 필터링한다. 초기 유통 경로를 사람 링크(트위터/HN/커뮤니티)로 확보하지 못하면 레지스트리 내부 발견은 작동하지 않는다.
2. **단일 스킬보다 저장소 번들이 유리하다.** 관측된 상위권 전부가 다스킬 저장소이고, 저장소 인지도가 개별 설치수를 끌어올린다.
3. **이름은 짧고 일반적으로.** `find`가 이름 부분일치이므로 `research`, `literature`, `verify` 같은 토큰이 이름에 들어가야 한다. 브랜드 접두사는 일반 검색 노출을 포기하는 대가다.
4. **비어 있는 자리는 "리서치 수행"이 아니라 "리서치 검증"이다** (Gap B). 그 다음이 학술 문헌 축(Gap A)과 재현 로그(Gap D).
5. **보안 배지 3종 Pass를 처음부터 확보할 것.** 상세 페이지에 항상 노출되며, 경쟁 스킬 중 Warning인 것들이 실제로 있다.

---

## 6. 미확인 / 후속 검증 필요 항목

- 신규 스킬이 **몇 회 설치 후 / 얼마나 지연되어** skills.sh에 등록되는지 — 공식 문서에 없고 Issue #880도 미답변. **직접 더미 스킬로 실측해야 한다.**
- `All Time (1,348,407)` 카운터의 정확한 의미(총 설치수인지 스킬 수인지) — 페이지에 설명 없음.
- RigorPilot의 480 star ↔ 450.8K 설치 격차 원인 — 미검증.
- 카테고리/토픽 페이지의 노출 알고리즘 — `skills.sh/docs`가 "filtering by topic"을 언급하나 선정 기준은 문서화돼 있지 않음.
- 설치수 vs 실제 사용률의 관계 — 텔레메트리는 설치만 수집한다고 명시돼 있어 **사용률 지표는 레지스트리에 존재하지 않는다** **[사실]**.

---

## 출처

- [skills.sh (루트 — 리더보드)](https://skills.sh)
- [skills.sh/docs](https://skills.sh/docs)
- [skills.sh/docs/cli](https://skills.sh/docs/cli)
- [Vercel KB — Agent Skills: Creating, Installing, and Sharing Reusable Agent Context](https://vercel.com/kb/guide/agent-skills-creating-installing-and-sharing-reusable-agent-context)
- [Vercel Changelog — Introducing skills, the open agent skills ecosystem](https://vercel.com/changelog/introducing-skills-the-open-agent-skills-ecosystem)
- [vercel-labs/skills — find-skills/SKILL.md](https://github.com/vercel-labs/skills/blob/main/skills/find-skills/SKILL.md)
- [vercel-labs/skills Issue #880 — How to submit/publish a new skill?](https://github.com/vercel-labs/skills/issues/880)
- [Snyk — Securing the Agent Skill Ecosystem](https://snyk.io/blog/snyk-vercel-securing-agent-skill-ecosystem/)
- [skills.sh/mattpocock/skills/research](https://skills.sh/mattpocock/skills/research) · [원문 SKILL.md](https://github.com/mattpocock/skills/blob/main/skills/engineering/research/SKILL.md)
- [skills.sh/lllllllama/rigorpilot-skills/ai-research-explore](https://skills.sh/lllllllama/rigorpilot-skills/ai-research-explore)
- 로컬 CLI 실행: `skills find <research|deep-research|paper|literature|search|web|arxiv|citation|zotero|obsidian|survey|fact-check|korean|peer-review|hypothesis|grant|notebooklm|competitor>` (skills CLI, 2026-09-01)
- GitHub API: `gh api repos/{mattpocock/skills, lllllllama/RigorPilot-Skills, firecrawl/firecrawl-workflows, google-deepmind/science-skills, Imbad0202/academic-research-skills, lingzhi227/agent-research-skills}`
