# 에이전틱 딥리서치 시스템의 내부 아키텍처

**조사 목적**: 신뢰성 있는 리서치 에이전트를 설계하기 위해, 공개된 최상위권 시스템들이 내부적으로 어떤 구조·프롬프트 설계·평가 방법을 쓰는지, 그리고 어떤 아키텍처 선택이 "신뢰 가능한 출력"과 상관관계가 있다고 실제로 밝혀졌는지를 원문 근거와 함께 정리한다. 벤더 자체 발표 수치(자기보고)와 제3자 검증 수치를 구분하고, 확인 안 된 것은 확인 안 됐다고 명시한다.

---

## 0. 결론 먼저 (TL;DR)

- **Anthropic의 멀티에이전트 리서치 시스템**은 orchestrator(lead agent) + 병렬 subagent 구조로, 내부 평가에서 단일 에이전트(Claude Opus 4) 대비 **90.2% 성능 향상**을 보고했다(자기보고, 내부 리서치 eval 기준). 대가는 토큰 소비 15배. 토큰 사용량 자체가 성능 분산의 80%를 설명한다고 밝혔다 — 즉 "많이 읽고 많이 생각하는 것"이 실제 승부처였다는 뜻. [Anthropic 원문](https://www.anthropic.com/engineering/multi-agent-research-system)
- **Stanford STORM**(NAACL 2024)은 "관점 유도 질문(perspective-guided question asking)"과 "시뮬레이션 전문가 대화"로 기사 작성 *전 단계*(사전 리서치·개요 작성)를 자동화한다. 기준선 대비 조직성 +25%p, 주제 커버리지 +10%p (논문 자기보고). [arXiv:2402.14207](https://arxiv.org/abs/2402.14207)
- **Co-STORM**(EMNLP 2024)은 STORM을 인간-AI 협업형으로 확장 — 여러 LLM 페르소나 + Moderator 에이전트가 턴을 주고받고, 인간이 언제든 대화에 개입할 수 있으며, 결과를 동적 마인드맵으로 유지한다. [ACL Anthology 2024.emnlp-main.554](https://aclanthology.org/2024.emnlp-main.554.pdf)
- **OpenAI Deep Research**(2025-02)는 o3 기반 단일 에이전트로, GAIA validation set에서 **72.57%**(당시 리더보드 1위, 자기보고·공개 리더보드 제출값), Humanity's Last Exam **26.6%**를 기록했다고 발표. 강화학습으로 브라우징·툴 사용을 훈련했다고 밝혔으나, RL 보상 설계·데이터 구성 등 세부 학습 방법은 **미공개**. [OpenAI 발표](https://openai.com/index/introducing-deep-research/)
- **Google Gemini Deep Research**는 단일 에이전트 아키텍처 + RL 파인튜닝으로 계획·검색·종합을 수행한다고 공개했지만, GAIA 등 표준 벤치마크 수치는 **공개된 1차 자료에서 확인되지 않음**(3rd-party 서베이 표에서도 "-"로 공백 처리됨). 세부 아키텍처(에이전트 수, 재순위 방식 등)도 대부분 **미공개**. [Google AI for Developers](https://ai.google.dev/gemini-api/docs/deep-research)
- **공통 루프**는 plan → search/read → reflect·critique → synthesize → verify로 수렴하지만, 종료 조건(반복 상한/토큰 예산/신뢰도 임계값)에 대한 학계의 명시적 논의는 상대적으로 빈약하다 — 대부분 시스템이 하드캡+예산 소진 조합을 쓰는 것으로 보이나 원문에서 상세 공식을 공개한 사례는 드물다.
- **오케스트레이션 판단 기준**: 병렬화는 "읽기 중심(read-heavy)·서로 독립적·컨텍스트가 단일 윈도우를 초과하는" 작업에 유리하고, "쓰기 중심(write-heavy)·에이전트 간 의존성이 많은" 작업(예: 코딩)은 순차/단일 에이전트가 낫다는 것이 LangChain·Anthropic 양쪽의 공통 결론이다. [LangChain 블로그](https://www.langchain.com/blog/how-and-when-to-build-multi-agent-systems)

---

## 1. Anthropic — "How we built our multi-agent research system"

원문: [anthropic.com/engineering/multi-agent-research-system](https://www.anthropic.com/engineering/multi-agent-research-system) (2025-06, Anthropic 엔지니어링 블로그, Claude의 Research 기능을 만든 팀 작성)

### 1.1 Orchestrator-worker 구조

리드 에이전트(orchestrator)가 쿼리를 분석해 전략을 세우고, 그 전략에 따라 서브에이전트(worker)들을 병렬로 생성한다.

> "the lead agent analyzes it, develops a strategy, and spawns subagents to explore different aspects simultaneously"

리드 에이전트는 컨텍스트 윈도우가 넘칠 것에 대비해 계획을 별도 메모리에 저장해 전략을 유지한다.

### 1.2 서브에이전트 분리의 이유 — "컨텍스트 압축"

서브에이전트를 두는 이유는 단순 병렬 처리가 아니라 **정보 압축**이다:

> "Subagents facilitate compression by operating in parallel with their own context windows, exploring different aspects of the question simultaneously before condensing the most important tokens for the lead research agent."

각 서브에이전트는 독립적 컨텍스트 윈도우로 조사 용량을 확장하고, 경로 의존성(초반 검색 결과에 이후 사고가 고착되는 문제)을 줄이며, 도구·프롬프트·탐색 궤적을 분리해 관심사 분리를 달성한다.

### 1.3 토큰 이코노미 (구체적 수치)

> "agents typically use about 4× more tokens than chat interactions, and multi-agent systems use about 15× more tokens than chats"

그런데도 정당화되는 이유:

> token usage by itself explains 80% of the variance (내부 리서치 평가에서)

즉 결과 품질을 가장 잘 예측하는 단일 변수가 "얼마나 많은 토큰을 썼는가"였다는 뜻이며, 이 때문에 경제성은 **고가치 작업**에서만 성립한다고 명시한다.

### 1.4 멀티에이전트 vs 단일 에이전트 (벤치마크)

> "our multi-agent system with Claude Opus 4 as the lead agent and Claude Sonnet 4 subagents outperformed single-agent Claude Opus 4 by 90.2%"

*(자기보고, Anthropic 내부 리서치 eval 기준 — 공개 표준 벤치마크가 아님)*

구체 사례: S&P 500 IT 섹터 전체 기업의 이사진을 찾는 작업에서, 멀티에이전트는 작업을 병렬 분해해 성공했지만 단일 에이전트는 순차 탐색이 느려 실패했다.

모델 업그레이드 효과도 언급된다: "Claude Sonnet 4로 업그레이드하는 것이 Claude Sonnet 3.7에서 토큰 예산을 두 배로 늘리는 것보다 더 큰 성능 향상"이었다 — 아키텍처보다 모델 자체의 향상이 더 크게 기여한 지점도 있었다는 뜻.

### 1.5 프롬프트 엔지니어링 8원칙 (요지)

1. **에이전트처럼 생각하기** — Console에서 단계별 시뮬레이션으로 실패 모드를 직접 관찰.
2. **오케스트레이터에게 위임법을 가르치기** — "각 서브에이전트는 목표, 출력 형식, 사용할 도구/출처에 대한 안내, 명확한 작업 경계가 필요하다." 초기엔 "반도체 부족 조사"처럼 모호한 지시를 내려 일부는 2021년 자동차 칩 위기를, 다른 일부는 2025년 공급망을 중복 조사하는 낭비가 발생했다.
3. **쿼리 복잡도에 비례해 노력 확장** — 단순 사실 조사는 에이전트 1개·툴 호출 3~10회, 직접 비교는 서브에이전트 2~4개·각 10~15회, 복잡한 리서치는 서브에이전트 10개 이상.
4. **도구 설계가 성패를 가른다** — "the right tool을 쓰는 것은 효율적일 뿐 아니라, 종종 엄격하게 필수적이다." 모든 가용 도구를 먼저 검토하고, 범용 도구보다 전문 도구를 우선한다는 휴리스틱.
5. **에이전트에게 자기 개선을 맡기기** — Claude 4 계열은 프롬프트와 실패 사례를 주면 스스로 원인을 진단하고 개선안을 제시할 수 있었고, 이렇게 만든 "도구 테스트 에이전트" 도입으로 **작업 완료 시간 40% 단축**.
6. **넓게 보고 좁혀가기** — 에이전트가 너무 이른 시점에 지나치게 구체적인 검색을 하는 경향을 막기 위해 "전문가처럼: 먼저 지형을 훑고 나서 세부로 들어가라"를 명시.
7. **사고 과정을 가이드하기** — extended thinking으로 계획을, interleaved thinking으로 도구 결과 평가를 유도.
8. **병렬 도구 호출** — 복잡한 쿼리에서 리서치 시간을 최대 90%까지 단축. 리드 에이전트는 서브에이전트 3~5개를 동시에 생성하고, 서브에이전트는 도구 3개 이상을 동시 호출하도록 지시.

### 1.6 실패 사례와 교훈

- **조정 실패**: "초기 에이전트들은 단순 쿼리에 서브에이전트 50개를 생성하거나, 존재하지 않는 출처를 끝없이 웹에서 찾아 헤매거나, 과도한 업데이트로 서로를 방해하는 오류를 냈다."
- **위임의 모호성**: 위 3.2 사례(반도체 부족).
- **출처 품질 편향**: 인간 테스터들이 시스템이 SEO 최적화된 콘텐츠 농장을 학술 PDF나 개인 블로그보다 선호하는 편향을 발견 → 프롬프트에 출처 품질 휴리스틱을 명시적으로 추가해 해결.
- **동기식 실행의 병목**: 리드 에이전트가 서브에이전트를 동기적으로 기다리므로, 서브에이전트 하나의 지연이 전체 파이프라인을 막는다 — Anthropic은 향후 비동기 실행으로 추가 병렬성을 확보할 계획이라고 언급.
- **상태·에러 복구**: "에러가 발생한 지점에서 에이전트가 재개할 수 있는 시스템을 구축했다" — 처음부터 재시작하는 비용이 크기 때문에 체크포인트 기반 복구가 필요했다는 프로덕션 교훈.
- **배포**: 실행 중인 장시간 에이전트가 배포로 중단되지 않도록 rainbow deployment 전략을 사용.

### 1.7 평가 방법론

- **소규모로 시작**: "실제 사용 패턴을 대표하는 약 20개 쿼리 세트로 시작했다." 초기 단계에서는 프롬프트 조정만으로 성공률이 30%→80%로 뛸 만큼 신호가 커서, 적은 표본으로도 충분히 영향력을 측정할 수 있었다고 밝힘.
- **LLM-as-judge**: 단일 LLM 호출로 0.0~1.0 점수와 pass/fail 판정. 평가 기준은 "사실 정확성(주장이 출처와 일치하는가), 인용 정확성(인용된 출처가 주장과 일치하는가), 완전성(요청된 모든 측면을 다뤘는가), 출처 품질(1차 출처를 저품질 2차 출처보다 우선했는가), 도구 효율성"의 5가지. 명확한 정답이 있는 케이스(예: "제약사 R&D 예산 상위 3곳")에서 특히 효과적이었다고 명시.
- **인간 평가는 필수불가결**: 자동화 평가가 놓치는 것 — 드문 쿼리에서의 환각, 시스템 장애, 미묘한 출처 선택 편향. "엣지 케이스를 잡아내는 것은 결국 사람"이라는 취지.

---

## 2. Stanford STORM / Co-STORM

### 2.1 STORM (NAACL 2024)

원문: **"Assisting in Writing Wikipedia-like Articles From Scratch with Large Language Models"**, [arXiv:2402.14207](https://arxiv.org/abs/2402.14207) / [stanford-oval/storm](https://github.com/stanford-oval/storm)

STORM = **S**ynthesis of **T**opic **O**utlines through **R**etrieval and **M**ulti-perspective question asking. 위키피디아급 장문 기사를 "처음부터(from scratch)" 쓰는 문제 중, 특히 **사전 작성(pre-writing) 단계** — 리서치와 개요 작성 — 를 자동화하는 데 집중한다.

**핵심 메커니즘 2가지**
1. **Perspective-guided question asking**: 비슷한 주제의 기존 위키피디아 기사들을 조사해 "이 주제는 어떤 관점들로 다뤄지는가"를 먼저 발견하고, 그 관점들을 이용해 질문 생성을 유도한다. 즉 질문자 역할의 LLM이 단일 시점이 아니라 여러 역할(예: 기자 A, 기자 B…)로 나뉘어 서로 다른 각도에서 질문한다.
2. **Simulated conversation**: 위키피디아 작가 역할과, 신뢰 가능한 인터넷 출처에 기반해 답하는 "주제 전문가" 역할 사이의 대화를 시뮬레이션한다. 이 대화를 통해 모델이 주제에 대한 이해를 갱신하고 후속 질문을 생성한다.

**2단계 파이프라인**: (1) Pre-writing — 인터넷 기반 리서치 → 참고자료 수집 → 기사 개요 생성, (2) Writing — 개요와 참고자료를 이용해 인용이 달린 완성된 기사를 생성.

**평가 — FreshWiki 벤치마크**: 최근에 작성된 고품질 위키피디아 기사들로 구성된 자체 벤치마크를 만들어 평가했다. 기준선 대비 STORM 결과물이 **조직성(organization) +25%p, 주제 커버리지(coverage) +10%p** 향상됐다고 보고한다(논문 자기보고 수치, 절대적 벤치마크가 아니라 논문이 정의한 지표 기준). 저자들은 한계로 **출처 편향의 전이**(정보원의 편향이 그대로 기사에 옮겨감)와 **무관한 사실들의 과도한 연결(불필요한 전환문 생성)** 문제를 전문가 피드백을 통해 지적한다.

### 2.2 Co-STORM (EMNLP 2024)

원문: **"Into the Unknown Unknowns: Engaged Human Learning through Participation in Language Model Agent Conversations"**, [ACL Anthology 2024.emnlp-main.554](https://aclanthology.org/2024.emnlp-main.554.pdf) / [stanford-oval/storm](https://github.com/stanford-oval/storm)

Co-STORM은 STORM을 "거의 완전 자동화된 파이프라인"에서 **인간-AI 협업형 지식 큐레이션**으로 확장한다.

- **협업 담화 프로토콜(collaborative discourse protocol)**: 턴 관리 정책을 두어, 외부 지식으로 근거한 답변을 생성하거나 담화 이력에 기반해 후속 질문을 던지는 여러 LLM "전문가" 에이전트 간 협업을 매끄럽게 만든다.
- **Moderator 에이전트**: 검색기(retriever)가 찾아냈지만 이전 턴에서 직접 쓰이지 않은 정보에서 착안해, 생각을 자극하는 질문을 새로 던지는 역할을 한다 — 대화가 한 방향으로만 좁혀지는 것을 막는 장치.
- **인간의 개입 지점**: 사용자는 대화를 관찰만 해도 되고, 언제든 발화를 주입해 논의 방향을 조종할 수도 있다 — "부모/교사의 대화를 듣고 참여하며 배우는" 교육 시나리오를 본뜬 설계라고 설명한다.
- **동적 마인드맵**: 수집된 정보를 계층적 개념 구조로 계속 갱신하며 유지해, 인간과 시스템이 공유하는 개념 공간을 만든다.

**STORM/Co-STORM 계열의 시사점**: "관점을 먼저 분기시키고, 그 관점별로 독립적인 질문-답변 스레드를 진행한 뒤 합친다"는 구조가 Anthropic의 orchestrator-worker와 사실상 같은 원리(작업을 독립 관점/하위질문으로 쪼개 병렬 탐색 후 압축)를 학술 측에서 먼저 정식화한 것으로 볼 수 있다. 다만 STORM은 "글 한 편 생성"에 최적화된 2단계 파이프라인이고, Anthropic 시스템은 범용 리서치 태스크에 대한 동적 서브에이전트 생성이라는 차이가 있다.

---

## 3. OpenAI Deep Research / Google Gemini Deep Research — 공개 vs 미공개

### 3.1 OpenAI Deep Research

공식 발표: [openai.com/index/introducing-deep-research](https://openai.com/index/introducing-deep-research/) (2025-02-02), 시스템 카드: [cdn.openai.com/deep-research-system-card.pdf](https://cdn.openai.com/deep-research-system-card.pdf) (2025-02-25)

**공개된 것**:
- o3 계열 모델을 기반으로 하며, 브라우징·코드 실행(Python)·파일 처리 도구를 통합한 에이전트라는 점.
- 강화학습으로 "실제 브라우징 작업에 대해" 다단계 추론과 도구 사용을 훈련했다는 서술 방향(단, 보상 설계·데이터 구성의 세부 내용은 공개 안 됨).
- 작업 완료에 5~30분이 걸리는 장시간 에이전틱 실행이라는 점.
- **벤치마크(자기보고)**: GAIA validation set 정확도 **72.57%**로 당시 공개 리더보드 1위 달성. Humanity's Last Exam(3,000여 문항, 로켓과학부터 분석철학까지)에서 **26.6%**를 기록했으며, 이는 직전 최고 기록(o1·DeepSeek-R1의 약 9%대)의 약 3배 수준이라고 보도됐다. *(주의: GAIA 리더보드는 벤더 자체 제출 방식이라 제3자 재현 검증이 아니다. 이후 GAIA 리더보드 자체가 "더 이상 유의미하지 않다"는 이유로 검증셋 제출이 마감됐다는 보도도 있어, 이 숫자를 현재 시점의 SOTA로 오인하면 안 된다.)*

**미공개인 것**: 정확한 아키텍처 다이어그램(단일 에이전트인지 내부적으로 서브태스크 분해가 있는지 세부 불명), RL 보상 함수와 훈련 데이터 구성, 검색/재순위 알고리즘 세부, 실패율·환각률의 정량 데이터.

### 3.2 Google Gemini Deep Research

공식 문서: [Gemini Deep Research agent — Gemini API](https://ai.google.dev/gemini-api/docs/deep-research)

**공개된 것**:
- **단일 에이전트 아키텍처**라는 점이 명시적으로 강조된다 — Anthropic의 멀티에이전트 접근과 대비되는 설계 선택: "Gemini's reinforcement learning-driven fine-tuning, facilitated by a single-agent architecture, enhances planning and adaptive research capabilities."
- 워크플로우는 Plan → Multi-source search → Iterate → Output의 4단계로, 사용자가 계획 단계에서 리뷰·수정할 수 있는 상호작용 지점을 둔다.
- 비동기 태스크 관리 아키텍처로 여러 작업을 동시에 처리한다고 서술.
- 멀티모달(텍스트·이미지 등)을 통합해 종합한다는 점.
- Deep Research Max 변형은 수십 회의 검색 반복을 수행하며 3~15분(단순 질문은 2~3분) 소요.

**미공개(확인 안 됨)인 것**: 표준 벤치마크(GAIA 등) 수치가 1차 자료(Google 공식 문서·블로그)에서 확인되지 않는다. 3자 서베이 비교표에서도 Gemini 계열 항목이 "-"(공백)로 처리된 경우가 있었다 — 즉 **공개 벤치마크 미제출/미공개**로 보는 것이 정확하다. Humanity's Last Exam에서 26.9%~32.4%(고연산 설정)를 기록했다는 서드파티 서베이 인용이 있었으나, 이는 Deep Research 제품 자체가 아니라 기반 모델(Gemini 2.5) 단독 평가일 가능성이 있어 **Deep Research 제품 성능으로 단정할 근거가 부족**하다(원 출처인 Gemini 2.5 기술보고서에서 이 항목이 Deep Research 제품용 수치인지 별도 확인 필요 — 미확인).

### 3.3 세 시스템 설계 대비

| | Anthropic (Claude Research) | OpenAI Deep Research | Gemini Deep Research |
|---|---|---|---|
| 에이전트 구조 | 멀티에이전트 (orchestrator + 병렬 subagent) | 불명(단일 에이전트로 추정, 세부 미공개) | **명시적으로 단일 에이전트** |
| 학습 방식 | 프롬프트 엔지니어링 + 기존 모델(Opus/Sonnet 4) 조합 | RL로 브라우징/툴 사용 파인튜닝 (세부 미공개) | RL 파인튜닝으로 계획·적응 능력 강화 |
| 공개 벤치마크 | 내부 eval만 공개(자기보고), 외부 표준 벤치마크 수치 없음 | GAIA 72.57%, HLE 26.6% (자기보고, 리더보드 제출) | 확인된 GAIA 수치 없음 |
| 핵심 설계 서사 | "컨텍스트 압축"을 위한 병렬 서브에이전트 | "단일 강력 추론 모델 + RL 훈련된 도구 사용" | "단일 에이전트 + RL로 계획력 확보" |

이 대비에서 흥미로운 점은, **가장 화려하게 멀티에이전트 구조를 설파한 것은 Anthropic이고, 경쟁사 두 곳(OpenAI·Google)은 오히려 단일 에이전트 + 강력한 기반 모델 + RL 훈련이라는 방향을 택했다고 공개**했다는 것이다. 세 회사 모두 자사 방식이 우월하다고 자기보고할 유인이 있으므로, "멀티에이전트가 무조건 낫다"는 결론으로 일반화하기보다는 **작업 특성(읽기 중심·병렬화 가능·고가치)에 따라 다른 최적점이 존재한다**는 4~5절의 논의로 이어서 봐야 한다.

---

## 4. 공통 루프 해부

여러 시스템·서베이를 종합하면 공통 루프는 대략 다음 단계로 수렴한다: **plan → search/read → reflect·critique → synthesize → verify** (일부는 replanning으로 되돌아감).

- **Plan**: 쿼리를 하위 질문/작업으로 분해. Gemini는 이 단계를 사용자에게 노출해 리뷰·수정을 받는다([Gemini 문서](https://ai.google.dev/gemini-api/docs/deep-research)). Anthropic은 계획을 리드 에이전트의 메모리에 저장해 컨텍스트 초과 시에도 유지한다.
- **Search/Read**: 웹 검색, 벡터 검색, 코드 실행 등 도구 호출. Perplexity DeepResearch는 Bing 스타일 인덱스와 자체 Sonar API(BM25 + 키워드 + 밀집벡터 재순위 결합)를 혼합한다고 알려져 있다("Deep Research: A Survey of Autonomous Research Agents", [arXiv:2508.12752](https://arxiv.org/html/2508.12752v1)).
- **Reflect/Critique**: 학계에서는 Reflexion류(자기비평 후 재시도), Multi-Agent Reflexion(MAR, 단일 자기비평 대신 페르소나가 다른 여러 비평자의 구조화된 토론으로 대체 — [arXiv:2512.20845](https://arxiv.org/html/2512.20845)) 같은 패턴이 연구되고 있다. Multi-agent debate는 단일 에이전트 기준 대비 사실 정확도 +7.8점, 산술 정확도 +14.8점 향상을 보고한 사례가 있다(서베이 인용, 원 논문 미특정 — 추가 확인 필요). 다만 "Isolated Self-Correction Prevails Over Unguided Homogeneous Multi-Agent Debate"([arXiv:2605.00914](https://arxiv.org/pdf/2605.00914)) 같은 반례 연구도 존재해, **비평/토론이 항상 이긴다고 단정할 근거는 없다** — 가이드되지 않은 동종(homogeneous) 에이전트 토론보다 고립된 자기교정이 더 나을 수 있다는 결과다.
- **Synthesize**: 검색된 근거를 종합해 보고서 생성. Anthropic·STORM 모두 이 단계에서 인용을 소스에 되짚어 붙이는 절차를 둔다.
- **Verify**: Anthropic의 LLM-judge 5기준(사실성·인용 정확성·완전성·출처 품질·도구 효율성)이 가장 구체적으로 공개된 사례다. 다만 이는 "생성 이후 오프라인 평가"이지, 루프 내부에서 매 스텝 실행되는 실시간 검증은 아니라는 점에 주의.
- **Replanning**: "Search-in-the-Chain"류는 중간 검색 결과를 보고 동적으로 다음 행동을 바꾼다는 서술이 있으나(서베이 인용), 구체적 트리거 조건(언제 재계획하는가)은 원문에서 상세히 공개되지 않은 경우가 많다.

**종료 조건 — 미확인이 많은 영역**: "Deep Research: A Survey of Autonomous Research Agents" 자체는 종료 조건(반복 상한/토큰 예산/신뢰도 임계값)을 명시적으로 다루지 않는다. 일반적인 에이전트 루프 설계 논의에서는 세 갈래로 정리된다 — (1) **loop-until-done**: `complete_answer_found`나 신뢰도 임계값 같은 조건 만족 시 종료, (2) **loop-until-budget**: 토큰/비용 쿼터 소진 시 종료, (3) **hard cap**: N회 시도 후 무조건 종료. 실무 사례로는 단일 도구 ReAct 패턴이 보통 3~5회 반복 예산을 쓴다는 서술이 있고, AB-RAG류 적응형 예산 RAG는 "답을 생성 → 신뢰도 계산 → 임계값 도달 시 즉시 반환, 아니면 예산이 남았을 때 증거 집합을 넓혀 재시도, 예산 소진 시 최선의 답 반환"이라는 구체적 정책을 제시한다([arXiv:2606.29090](https://arxiv.org/pdf/2606.29090)). **다만 이것이 업계 표준이라는 근거는 없고, 각 시스템이 자체적으로 하드캡+예산 조합을 쓰는 것으로 추정될 뿐 Anthropic·OpenAI·Google 모두 정확한 종료 로직 공식은 공개하지 않았다** — 이 부분은 명확히 "미확인"으로 남긴다.

---

## 5. 오케스트레이션 패턴 — 언제 병렬, 언제 순차

핵심 출처: [LangChain, "How and when to build multi-agent systems"](https://www.langchain.com/blog/how-and-when-to-build-multi-agent-systems), [Anthropic 멀티에이전트 블로그](https://www.anthropic.com/engineering/multi-agent-research-system)

**병렬 팬아웃이 유리한 조건**:
> "Multi-agent systems excel at valuable tasks that involve heavy parallelization, information that exceeds single context windows..."

즉 (a) 하위 작업들이 서로 독립적이고, (b) 필요한 정보 총량이 단일 컨텍스트 윈도우를 넘고, (c) 작업 가치가 늘어난 토큰 비용(Anthropic 기준 15배)을 정당화할 만큼 높을 때.

**순차/단일 에이전트가 유리한 조건**:
- **쓰기 중심(write-heavy) 작업**: "conflicting decisions carry bad results" — 여러 에이전트가 동시에 같은 코드베이스를 고치면 충돌·모순이 발생하기 쉽다. 이 때문에 코딩 같은 작업은 멀티에이전트 병렬화에 상대적으로 부적합하다고 명시.
- **에이전트 간 의존성이 많거나 같은 컨텍스트를 공유해야 하는 도메인**: "Some domains that require all agents to share the same context or involve many dependencies between agents are not a good fit for multi-agent systems."

**컨텍스트 격리(context isolation) — "원문을 읽고 요약만 반환"**: Anthropic 시스템의 핵심 메커니즘이 바로 이것이다. 서브에이전트가 자신의 컨텍스트 윈도우 안에서 대량의 원문(웹페이지, 문서)을 읽어 처리하고, 리드 에이전트에게는 **압축된 핵심 토큰만** 반환한다("condensing the most important tokens for the lead research agent"). 이 격리 덕분에:
1. 리드 에이전트의 컨텍스트 윈도우가 원문으로 오염되지 않는다.
2. 서브에이전트마다 별도의 탐색 궤적을 가져 초반 판단에 서로 발이 묶이는 경로 의존성이 줄어든다.
3. 도구·프롬프트를 서브에이전트별로 특화할 수 있어 관심사 분리가 명확해진다.

단, 대가는 명확하다 — 위임 지시가 모호하면(3.2절의 "반도체 부족" 사례) 압축 과정에서 컨텍스트가 유실되거나 중복 작업이 발생한다. LangChain 블로그도 같은 문제를 지적한다: "simple, short instructions often were vague enough that subagents misinterpreted the task or performed the exact same searches." 즉 **컨텍스트 격리의 이점은 위임 프롬프트의 명세 품질에 강하게 종속된다** — 격리 자체가 공짜로 신뢰성을 주는 게 아니라, 잘 설계된 태스크 명세(목표·출력형식·도구 가이드·경계)와 짝을 이뤄야만 작동한다.

---

## 6. 우리 설계에 이식할 패턴

신뢰성과 상관관계가 있다고 원문에서 실제로 뒷받침된 아키텍처 선택만 추린다. 각 항목에 근거와 적용 조건을 함께 남긴다.

1. **서브에이전트 위임 시 4요소를 항상 강제한다: 목표·출력 형식·도구/출처 가이드·명확한 경계.** [Anthropic §2](https://www.anthropic.com/engineering/multi-agent-research-system) — "반도체 부족" 실패 사례가 정확히 이 4요소 부재로 발생했다. 우리 시스템에서 서브태스크를 분배하는 프롬프트 템플릿에 이 4개 필드를 필수 항목으로 못박는다.
2. **컨텍스트 격리(원문을 읽는 에이전트와 종합하는 에이전트 분리)는 "읽기 중심 + 병렬화 가능 + 컨텍스트가 큰" 작업에만 적용하고, 쓰기/의존성 많은 작업에는 쓰지 않는다.** [Anthropic](https://www.anthropic.com/engineering/multi-agent-research-system) + [LangChain](https://www.langchain.com/blog/how-and-when-to-build-multi-agent-systems) 양쪽이 일치하는 결론. 우리 리서치 스트림처럼 "여러 출처를 읽고 압축 요약만 상위로 올리는" 작업은 정확히 이 조건에 부합한다.
3. **출처 품질 휴리스틱을 프롬프트에 명시적으로 박아넣는다** (SEO 콘텐츠 농장 > 학술 PDF/1차 출처를 선호하는 편향은 자동으로 해결되지 않았다 — 프롬프트에 명시하고 나서야 고쳐졌다). [Anthropic §3, 출처 편향 사례].
4. **평가는 LLM-judge의 5기준(사실성·인용 정확성·완전성·출처 품질·도구 효율성) + 소규모(약 20개) 대표 쿼리 세트로 시작 + 인간 검토를 반드시 병행한다.** 자동화 평가만으로는 드문 쿼리의 환각과 미묘한 출처 편향을 못 잡는다는 것이 Anthropic이 실측한 한계다.
5. **넓게 훑고 좁히는 탐색 순서를 강제한다** (early over-narrowing 방지). Anthropic이 실패에서 학습해 프롬프트에 추가한 원칙 — 우리도 초기 검색 쿼리가 지나치게 구체적으로 좁혀지지 않도록 계획 단계에 체크를 둔다.
6. **비평/토론(multi-agent debate, Reflexion류)은 만능이 아니다 — 가이드 없는 동종 토론은 오히려 고립된 자기교정보다 못할 수 있다는 반례가 있으므로**([arXiv:2605.00914](https://arxiv.org/pdf/2605.00914)), 비평 단계를 넣을 때는 반드시 (a) 비평자에게 원 에이전트와 다른 역할/기준을 명시적으로 부여하거나 (b) 최소한 "고립된 자기교정"과 비교해 실제로 개선되는지 우리 자체 eval로 검증한 뒤 채택한다. 이식하되 무비판적으로 넣지 않는다.
7. **종료 조건은 하드캡 + 예산(토큰/반복) 소진의 조합으로 설계하고, 신뢰도 임계값 종료는 아직 업계 표준이 확인되지 않은 영역이므로 우리가 직접 계측해서 정한다.** 이 부분은 공개 문헌에서 세부 공식이 확인되지 않는 만큼, "따라 하기"보다 "우리 eval로 직접 튜닝"이 맞는 접근이다.
8. **병렬 vs 순차는 작업 유형별로 미리 분류해둔다** — 읽기/조사형 서브태스크는 병렬 팬아웃, 코드 수정·문서 편집처럼 상태를 공유하며 쓰는 작업은 순차 단일 에이전트. 이 분기 기준 자체를 오케스트레이터의 최상위 규칙으로 코드화한다.
9. **모델 성능이 아키텍처보다 큰 지렛대일 수 있다는 점을 과소평가하지 않는다** — Anthropic도 "Sonnet 3.7→4 업그레이드가 토큰 예산 2배보다 효과적"이었다고 밝혔다. 멀티에이전트 구조를 정교화하는 데 투자하기 전에, 기반 모델 교체만으로 얻을 수 있는 개선분을 먼저 측정해본다.
10. **자기보고 수치는 절대 그대로 재인용하지 않는다.** 이번 조사에서만도 GAIA 72.57%(OpenAI), 90.2%(Anthropic) 모두 벤더 자체 측정치이고, Gemini는 비교 가능한 수치 자체가 공개되어 있지 않았다. 우리 문서·발표 자료에 타사 벤치마크를 인용할 때는 반드시 "자기보고" 표기를 유지한다.

---

## 부록 — 확인 안 됨(미확인) 목록

- Multi-agent debate의 "+7.8pt 사실 정확도, +14.8pt 산술 정확도" 수치의 원 논문 — 서베이 재인용이며 1차 출처를 직접 확인하지 못함.
- Gemini Deep Research의 Humanity's Last Exam 26.9%/32.4% 수치가 Deep Research 제품 자체의 평가인지, 기반 모델(Gemini 2.5) 단독 평가인지 — 미확인.
- OpenAI Deep Research가 내부적으로 서브태스크를 분해하는 멀티에이전트인지, 순수 단일 에이전트인지 — 시스템 카드에서 명시적으로 밝히지 않음.
- 세 시스템 모두 "재계획(replanning)이 정확히 어떤 트리거로 발동하는가"에 대한 상세 로직 — 공개 안 됨.
