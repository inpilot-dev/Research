# AI 리서치 리포트 인용 검증 — 선점자 조사

**조사 목적**: 검증 플러그인 1순위 페르소나 후보 — "gpt-researcher / Perplexity / Gemini Deep Research 등이 만든 AI 리서치 리포트를 받은 사람이, 그 리포트의 인용 N개가 실제로 그 페이지에 그 내용이 있는지 확인한다" — 이 자리가 정말 비어 있는지 검증. 근거 없는 낙관 금지, 미확인은 미확인으로 표기.

**검증 레벨 정의**
- **L1** = 링크 살아있음 / 서지 실존 (URL 200, DOI/논문 존재)
- **L2** = 인용된 페이지에 인용문·수치가 문자 그대로(또는 퍼지 매칭으로) 존재
- **L3** = 주장이 출처에 의해 의미적으로 뒷받침됨 (entailment / support classification)

---

## 0. 결론 먼저 (TL;DR)

> **"임의의 제3자 AI 리서치 리포트를 통째로 받아서, 인용 URL을 웹에서 fetch하고, L1→L2→L3까지 자동으로 판정해주는 범용 독립 도구"는 확인된 범위 내에서 존재하지 않는다.**

- **L1(링크 생존/서지 실존)**: 사실상 포화 상태. 학술 인용 전용 도구가 매우 많고, 2026년에 정확히 이 문제("상용 LLM/딥리서치 에이전트가 만든 URL 인용의 hallucination")를 다룬 논문과 그 부산물로 나온 오픈소스 도구(`urlhealth`)까지 있다. **다만 전부 "URL이 살아있는가"까지만 본다.**
- **L2(인용문·수치 대조)**: 부분적으로만 존재. 결정론적으로(문자열/퍼지 매칭) 구현 가능한 범위지만, "임의의 제3자 리포트"를 받는 범용 도구는 거의 없고 대부분 "내가 쓰는 중인 글의 자기 검증" 용도로 매몰돼 있다.
- **L3(의미적 entailment)**: 학계 벤치마크(SAFE, VeriScore, AttributionBench, ALCE)는 풍부하지만 전부 "모델 자신의 출력을 평가하는 연구용 파이프라인"이지, "당신이 받은 임의의 리포트+URL 목록을 넣으면 판정해주는 소비자용 도구"가 아니다. 근접한 상용/OSS 시도(SemanticCite, CiteGenie, CiteGuardian)는 있지만 전부 **학술 논문(PDF/DOI) 중심**이거나 **초기 단계(★ 두 자릿수, 커밋 적음)**다.
- **자리가 비어 있는 이유는 야망 부족이 아니라 기술적 난점**: 동적 렌더링 SPA, 페이월, 스크래핑 차단(403/Cloudflare/robots.txt), PDF 파싱, 그리고 L3의 의미 판정 정확도가 최선의 LLM 심판으로도 80% 안팎에 머무른다는 점(§7) 때문에 "제3자 문서를 신뢰성 있게 자동 판정"하는 제품을 만들기 어렵다.
- **판단**: 페르소나 후보의 자리는 **완전히 비어 있지는 않지만(L1은 붐빔, L2/L3 근접 시도가 존재), "제3자 리포트 수신자를 위한 범용 L2/L3 검증 도구"라는 좁은 정의로 보면 실질적으로 빈 자리**로 볼 근거가 있다. 단, 6개월~1년 내 유사 도구가 빠르게 나올 수 있는 영역(연구 논문+OSS 도구가 막 나오기 시작한 시점)이라는 점은 리스크로 남는다.

---

## 1. skills.sh 실검색 결과

키워드: fact-check, citation, hallucination, verify, source, link-check, claim, evidence, grounding, attribution. 각 검색 상위 결과 중 실제로 SKILL.md를 열어 확인한 항목만 판정을 매겼다(나머지는 이름만으로는 판정 불가이므로 "미확인"으로 남김).

| 스킬 | 설치수 | 실제로 하는 일 (SKILL.md 확인) | 입력 범위 | 판정 |
|---|---|---|---|---|
| [wanshuiyin/auto-claude-code-research-in-sleep@citation-audit](https://skills.sh/wanshuiyin/auto-claude-code-research-in-sleep/citation-audit) | 345 | `\cite{...}`가 있는 논문 bib 파일을 대상으로 (1)실존 (2)메타데이터 정확성 (3)"인용된 논문이 실제로 그 주장을 뒷받침하는가"까지 LLM 리뷰어(Codex MCP)가 판정. 실제 웹/DBLP/arXiv 조회를 강제("real web/DBLP/arXiv lookups, not pattern-match from memory") | **논문 매뉴스크립트 전용.** 외부 임의 문서는 받지 않음 — "does not ingest arbitrary external documents" | L1+L2+L3 (학술 인용 한정) |
| [boom5426/nature-paper-skills@claim-source-verification](https://skills.sh/boom5426/nature-paper-skills/claim-source-verification) | 14 | "인용이 완벽히 실재하고 포맷도 맞아도, 그 논문이 문장이 주장하는 바를 말하지 않으면 틀린 것"이라는 원칙 아래 의미 불일치(`does_not_support_claim`), 메타데이터 오류, 대상군 오류, 1차자료 요구, 페이월 등으로 분류 | 학술 논문/Nature 계열 원고 전용으로 보임 | L2~L3 (학술 한정) |
| [galaxy-dawn/claude-scholar@citation-verification](https://skills.sh/galaxy-dawn/claude-scholar/citation-verification) | 1.3K | "글 쓰는 동안 프로그래밍적/정본 학술 출처로 선제적으로 모든 인용을 검증" — 거짓 인용, 저자/제목/연도 불일치, 누락 인용 탐지. 구현 세부는 공개 페이지에 없음 | 저작 중인 자기 글(글쓰기 워크플로 내장) | L1~L2로 추정 (미확인) |
| [liangdabiao/claude-code-stock-deep-research-agent@citation-validator](https://skills.sh/liangdabiao/claude-code-stock-deep-research-agent/citation-validator) | 214 | "Verify citations actually support the claims", "Detect Hallucinations: claims with no supporting sources" — 원칙만 명시, 구현(웹 fetch 여부 등) 비공개 | 특정 stock 리서치 에이전트 결과물 전용으로 보이나 명시적 제한은 없음 | L2 주장(미검증) |
| [serenakeyitan/citation-check-skill@citation-check-skill](https://skills.sh/serenakeyitan/citation-check-skill/citation-check-skill) | 73 | "Validates every claim against authoritative sources or provided documents." 웹검색 기반 모드(기본)와 문서 전용 모드 2종. "Deterministic verification. Same input → Same output." | 웹 검색 기반 모드는 범용 콘텐츠 대상으로 보임 (임의 리포트도 가능성 있음) | L1~L2 (미확인, 가장 유망해 보이나 확증 부족) |
| [jamditis/claude-skills-journalism@fact-check-workflow](https://skills.sh/jamditis/claude-skills-journalism/fact-check-workflow) / [source-verification](https://skills.sh/jamditis/claude-skills-journalism/source-verification) | 468 / 344 | 저널리즘 팩트체크 워크플로. 이름상 취재원 검증이지 "AI 리포트의 URL 인용 대조"가 목적이 아님 | 저널리즘 기사 초안 | 미확인 |
| [av/facts@facts](https://skills.sh/av/facts/facts) (+facts-discover, facts-implement) | 103 | "프로젝트에 대해 참이어야 하는 것을 지정한 뒤 현실이 일치하는지 검증" — 이는 **소프트웨어 스펙 검증**(코드가 스펙대로 동작하는지) 용도로, 리서치 리포트 인용 검증과 무관 | 코드베이스 | 해당 없음 |
| [levnikolaevich/claude-code-skills@ln-614-docs-fact-checker](https://skills.sh/levnikolaevich/claude-code-skills/ln-614-docs-fact-checker) | 236 | 이름상 "문서 팩트체커"이나 리포지토리 맥락(`ln-614`)상 **사내 개발 문서**가 실제 코드와 일치하는지 확인하는 용도로 추정 | 사내 문서 vs 코드 | 미확인, 목적 다름 |

**소결**: skills.sh에는 "인용 검증" 관련 스킬이 수십 개 있지만, 실제로 열어본 것들은 거의 전부 **(a) 학술 논문 bib/DOI 대상**이거나 **(b) 저작 중인 자기 글의 자기검증용**이다. "타인이 만든 AI 리서치 리포트를 그대로 받아서 URL 인용을 검증"하는, 사용자가 원하는 정확한 시나리오에 맞는 것은 확인되지 않았다.

---

## 2. Claude 플러그인 마켓 (`anthropics/claude-plugins-community`)

`.claude-plugin/marketplace.json`(2,282개 플러그인, [원본](https://github.com/anthropics/claude-plugins-community/blob/main/.claude-plugin/marketplace.json))을 다운로드해 이름+설명에서 `citation`, `fact-check`, `hallucin`, `grounding`, `claim verif`, `source verif`, `link-check`, `attribution` 키워드로 전수 검색.

| 플러그인 | 설명 요지 | 판정 |
|---|---|---|
| [sourceverify](https://github.com/anthropics/claude-plugins-community) | "Verify academic citations and references using the SourceVerify API" | 학술 인용 전용 (L1 추정) |
| [bettercallclaude](https://github.com/anthropics/claude-plugins-community) | 스위스 법률 인텔리전스, 판례 인용 검증 포함 | 법률 판례 전용 (도메인 특화) |
| [germany-legal](https://github.com/anthropics/claude-plugins-community) | 독일 법령 조문 인용, gesetze-im-internet.de 대조 | 법령 전용 |
| [cite2fn](https://github.com/anthropics/claude-plugins-community) | Word 문서의 하이퍼링크 인용을 Bluebook 각주로 변환 | 포맷 변환, 검증 아님 |
| [botsee-skill](https://github.com/anthropics/claude-plugins-community) | ChatGPT/Perplexity/Gemini/Grok에서 자기 브랜드가 얼마나 인용되는지 모니터링 | GEO/브랜드 모니터링, 정반대 방향(우리 콘텐츠가 인용되는지) |
| [geo-generative-engine-optimisation](https://github.com/anthropics/claude-plugins-community) | AI 검색 노출 최적화(GEO) | 위와 동일 범주, 검증 도구 아님 |
| [gsearch](https://github.com/anthropics/claude-plugins-community) | Google Search grounding으로 `[1][2][3]` 인용 붙여주는 MCP 툴 | 리포트 **생성** 보조, 사후 검증 아님 |
| [nagomi](https://github.com/anthropics/claude-plugins-community) | PubMed 서지 리서치 엔진, GRADE 신뢰도 평가·Oxford CEBM 계층 비평 | 의학 문헌 검증(자체 검색 결과 대상), 제3자 리포트 검증 아님 |

**소결**: 마켓 전수 검색에서도 "제3자 AI 리포트의 URL 인용 대조" 전용 플러그인은 없었다. `sourceverify`가 이름은 가장 근접하지만 "academic citations and references"로 스코프가 학술로 한정된다(공식 API 문서 미확인, 이름과 설명 문구 기준 판단).

---

## 3. GitHub 레포 검색 — 인용/hallucination 검증 도구

| 레포 | ★ | 최근 활동 | 하는 일 | L레벨 | 제3자 임의 문서 가능? |
|---|---|---|---|---|---|
| [gianlucasb/hallucinator](https://github.com/gianlucasb/hallucinator) | 356 | 2026-09-01 (활발) | PDF 논문에서 참고문헌을 추출해 위조/환각 여부 탐지 | L1 | 학술 PDF 전용 |
| [markrussinovich/refchecker](https://github.com/markrussinovich/refchecker) | 486 | 2026-08-17 | Semantic Scholar/OpenAlex/CrossRef/DBLP/ACL Anthology 대조 + LLM 딥웹서치로 위조 의심 참고문헌 탐지, 검증 캐시 유지 | L1 (일부 L2 근접) | 학술 논문 전용 |
| [davidjurgens/hallucinated-reference-finder](https://github.com/davidjurgens/hallucinated-reference-finder) | 40 | 2026-04-17 | 논문에서 인용을 추출해 여러 학술 DB 대조 후 위조 가능성 랭킹 리포트 생성 | L1 | 학술 논문 전용 |
| [Vikranth3140/Citation-Hallucination-Detection](https://github.com/Vikranth3140/Citation-Hallucination-Detection) | 4 | 2026-04-24 | 정확 서지 조회+퍼지 매칭+선택적 LLM 검증으로 유효/부분유효/환각 3분류 | L1 | 학술 문서 전용, 초기 단계 |
| [rpatrik96/hallmark](https://github.com/rpatrik96/hallmark) | 12 | 2026-09-02 (매우 활발) | ML 논문 인용 환각 탐지 **벤치마크**(2,525건, 14종 환각 유형, 3단 난이도, LLM 포함 10개 베이스라인) | 벤치마크(도구 아님) | N/A |
| [aaFrostnova/CiteTracer](https://github.com/aaFrostnova/CiteTracer) | 12 | 2026-07-28 | 멀티에이전트 캐스케이드로 인용 환각 탐지, 외부 서지 DB 질의 | L1 | 학술 논문 전용, 초기 단계 |
| [DWFlanagan/llm-citation-verifier](https://github.com/DWFlanagan/llm-citation-verifier) | 7 | 2025-07-14 | Crossref DOI 대조로 가짜 DOI 탐지 | L1 | DOI 있는 학술 인용 전용 |
| [sebhaan/SemanticCite](https://github.com/sebhaan/semanticcite) | 25 | 2025-11-28 | PDF/TXT/Markdown 업로드 또는 URL 다운로드 → 전체 본문 분석으로 Supported/Partially Supported/Unsupported/Uncertain 4단 분류, 근거 스니펫 제시 | **L3** (가장 근접) | **임의 문서 가능** (학술 한정 아님) — 다만 ★25, 포크 6, 이슈/PR 0으로 초기 단계 |
| **[urlhealth](https://arxiv.org/abs/2604.03173)** (Rao/Wong/Callison-Burch, UPenn, DARPA SciFy 지원) | 논문 부속 도구, 별도 GitHub 스타 미확인(pip 패키지 + agentskills.io 스킬로 배포, MIT 라이선스, 83줄) | 2026년 arXiv 게재 | **LLM 출력에서 나온 URL을 사후적으로(model-agnostic) 검증**: HTTP 상태 + Wayback Machine 스냅샷 대조로 LIVE/DEAD(한때 존재)/LIKELY_HALLUCINATED/UNKNOWN 4분류. gpt-researcher류 딥리서치 에이전트(Gemini 2.5 Pro Deep Research 등)를 포함한 10개 상용 모델을 DRBench(URL 53,090개)·ExpertQA(URL 168,021개)로 실측 | **L1** | **임의의 LLM 출력(제3자 리포트 포함) 가능** — 정확히 이 과제 도메인을 다룬 유일한 논문+공개 도구 |

**핵심 발견**: `urlhealth`는 이 조사에서 찾은 것 중 "임의의 AI 리서치 리포트(딥리서치 에이전트 출력 포함)를 받아 URL 인용을 검증"한다는 문제 정의에 **가장 정확히 부합**하는 공개 도구다. 단, **L1(URL 생존)까지만** 하고 L2/L3(인용문·수치·의미 대조)는 하지 않는다. 논문 자체가 "우리 추정치는 보수적 하한선"이라고 명시할 만큼 Wayback Machine 커버리지에 의존하는 한계도 있다.

`SemanticCite`는 L3까지 시도하는 유일한 범용(비학술 한정) 도구이지만 ★25·이슈/PR 0으로 사실상 검증되지 않은 실험 단계다.

---

## 4. 상용/내장 기능 — 제3자 문서 검증 가능 여부

| 제품 | 하는 일 | 제3자 문서 검증 가능? |
|---|---|---|
| **Gemini "Double-check response"** | 응답 생성 후 Google 검색으로 문장 단위 교차검증, 초록(유사)/주황(상이·근거부족) 하이라이트 | **불가**. Gemini **자신의** 응답에만 적용됨. 사용자가 Perplexity나 gpt-researcher가 만든 리포트를 붙여넣고 검증받는 기능 없음 |
| **Perplexity 출처 표시** | 답변에 인라인 각주로 출처 링크 표시 | **불가**(자기 출력 전용). 오히려 Perplexity 자체의 인용 신뢰도가 문제로 지적됨(§6) |
| **NotebookLM 인용** | 업로드한 소스 문서 내 위치를 클릭 가능한 인용으로 연결, 하이라이트로 원문 대조 지원 | **부분적으로 유사하지만 방향이 다름**: 사용자가 소스를 업로드하고 NotebookLM이 그 소스 안에서 답을 생성할 때의 자기-근거화(self-grounding)이지, "이미 작성된 리포트+URL 목록"을 검증 대상으로 넣는 기능이 아님. 페이지 번호 없이 "Source 3"처럼 모호하게 표시되는 한계도 보고됨 |
| **Bing/Copilot** | 자체 검색 결과 인용 | 미확인, 자기 출력 전용으로 추정 |
| **OpenAI Deep Research 인용** | 자체 검색 결과 인용 | 미확인, 자기 출력 전용으로 추정 |
| **Google Cloud Vertex AI "Check Grounding" API** | 답변 텍스트와 **사용자가 제공한 근거(facts) 집합**을 대조해 0~1 지지 점수와 클레임별 인용 반환 | **개발자용 API이지 최종사용자 도구가 아님.** 그리고 결정적으로 — 근거 텍스트를 **API 호출자가 직접 넘겨야 함**. URL을 스스로 fetch해서 "그 페이지에 실제로 그 내용이 있는지"를 확인하는 게 아니라, 이미 확보된 근거와 답변의 정합성만 채점한다. RAG 개발자가 자기 파이프라인 품질을 재는 도구이지, 리포트 수신자가 URL만 갖고 검증하는 용도가 아님 |

**소결**: 상용 AI 제품들의 "인용/검증" 기능은 예외 없이 **자기 출력 검증용(self-verification)**이거나, **개발자가 근거 텍스트를 직접 공급해야 하는 API**다. "받은 리포트를 그대로 붙여넣고 URL만으로 검증"하는 사용자 시나리오를 충족하는 상용 기능은 확인되지 않았다.

---

## 5. 학술 벤치마크 및 오픈소스 구현

| 벤치마크/방법 | 기관/출처 | 무엇을 평가하나 | 임의 문서+URL을 입력받아 돌릴 수 있는 도구가 있는가 |
|---|---|---|---|
| [ALCE](https://github.com/princeton-nlp/ALCE) (★528) | Princeton NLP, EMNLP 2023 | LLM이 인용을 포함해 텍스트를 생성하는 능력 자체를 평가(정답 코퍼스 기반, ASQA/QAMPARI/ELI5) | **아니오.** 고정 데이터셋+정답 코퍼스 기반 생성 평가이지, 임의 문서 사후검증 도구가 아님 |
| [AttributionBench](https://github.com/OSU-NLP-Group/AttributionBench) (★10) | OSU NLP Group, ACL'24 Findings | 기존 attribution 데이터셋을 모아 "클레임이 인용된 근거에 의해 완전히 뒷받침되는가"를 이진분류로 자동 평가하는 것이 얼마나 어려운지 측정 | **아니오.** 벤치마크 데이터셋+평가 코드. 파인튜닝된 GPT-3.5조차 이진분류 macro-F1 ~80% 수준(§7) — "자동 attribution 평가는 생각보다 어렵다"는 게 논문의 결론 |
| SAFE / [LongFact](https://github.com/google-deepmind/long-form-factuality) (★693) | Google DeepMind, 2024 | 장문 응답을 개별 사실로 분해 → Google 검색으로 각 사실을 독립 검증하는 파이프라인. "초인간적"이라 홍보됨 | **부분적으로 가능** — 코드가 공개돼 있어 원칙적으로 임의 텍스트에 돌릴 수 있음. 그러나 설계 목적은 "모델이 스스로 만든 장문 응답의 사실성 채점"이며, "URL 인용이 실제로 그 페이지에 있는가"를 확인하는 워크플로가 아니라 사실 단위로 새로 검색해 재검증하는 방식(원 인용 URL을 신뢰하지 않고 독립적으로 재검색) |
| [VeriScore](https://arxiv.org/pdf/2406.19276) | UMD/AI2 계열, 2024 | 클레임 추출→증거 검색(Google Search)→클레임 검증 3단계 파이프라인 | 위와 유사, 원칙적으로 재사용 가능하나 "기존 인용 URL의 진위"가 아니라 자체 재검색 기반 사실성 평가가 목적 |
| SemanticCite, urlhealth | §3 참조 | — | 위 두 항목만이 "이미 주어진 URL/문서"를 대상으로 하는 실제 실행 가능 도구 |

**소결**: 학술 벤치마크·방법론은 모두 **"모델이 자체적으로 무엇을 다시 검색해서 사실 여부를 판단하는가"**를 다룬다. 사용자가 원하는 시나리오 — "이미 리포트에 박혀 있는 특정 URL 인용이, 그 URL 페이지의 실제 내용과 일치하는가" — 는 이들과 인접하지만 동일하지 않다. 인접 개념이라 재사용은 가능하지만, "그대로 쓸 수 있는 기성 도구"로서는 존재하지 않는다.

---

## 6. 문제의 실재성 — 왜 이 자리가 중요한가

- **Columbia Journalism Review (Tow Center, 2025-03-06)**: [8개 AI 검색엔진 200개 테스트](https://www.cjr.org/tow_center/we-compared-eight-ai-search-engines-theyre-all-bad-at-citing-news.php) 중 60% 이상이 출처를 잘못 식별. Perplexity 37% 오답, Grok 3는 94% 오답. ChatGPT는 200건 중 134건 오답이면서 불확실성 표시는 15회뿐, 거부는 0회.
- **urlhealth 논문(2026)**: 딥리서치 에이전트(예: gemini-2.5-pro-deepresearch)의 URL 환각률 13.3%, 검색증강 LLM은 3.0~8.8%. 도메인별로 5.4%(비즈니스)~11.4%(신학) 편차.
- 즉, "AI 리서치 리포트를 받았을 때 인용을 못 믿을 이유"는 데이터로 뒷받침된다. 다만 이 조사들 자체는 **연구자가 만든 일회성 벤치마크/논문**이지, 리포트 수신자가 상시로 쓸 수 있는 도구가 아니다 — 이것이 바로 그 자리가 비어 있다는 방증이기도 하다.

---

## 7. 기술 난이도 평가

### L2 (인용문/수치 대조) — LLM 없이 결정론적으로 구현 가능한 범위

- **정확 문자열 매칭**: 인용문이 페이지 텍스트에 정규화 후(공백/대소문자/마크업 무시) 그대로 존재하는지 `in` 연산으로 확인 가능. Hermes Agent의 `sources.py verify` 방식이 정확히 이것 — "따옴표는 fetch한 페이지 텍스트에 문자 그대로(대소문자/공백/마크업 무관) 있어야 하며, 없으면 reject"([Hermes Agent 문서](https://hermes-agent.nousresearch.com/docs/user-guide/skills/bundled/research/research-grounded-citations)). **LLM 불필요**, 단순 텍스트 검색으로 충분.
- **수치 대조**: 인용된 숫자(예: "94% net P&L")가 페이지 내 숫자와 단위/자릿수까지 일치하는지 정규식+퍼지 매칭(레벤슈타인 거리, 천단위 구분자 정규화 등)으로 결정론적 구현 가능.
- **퍼지 매칭**: 패러프레이징(같은 뜻, 다른 표현)까지 잡으려면 완전 결정론적으로는 한계가 있으나, n-gram overlap이나 fuzzy string matching(예: RapidFuzz)으로 "부분 일치/거의 일치"까지는 LLM 없이 근사 가능.
- **여기서 막히는 지점(L2를 어렵게 만드는 것은 매칭 로직이 아니라 "페이지를 손에 넣는 것" 자체)**:
  - **동적 렌더링(SPA/JS)**: 단순 HTTP GET으로는 본문이 비어 있음 → 헤드리스 브라우저(Playwright 등) 필요, 비용·속도 증가.
  - **페이월**: 대부분 접근 불가 → "확인 불가"로만 표시 가능(boom5426 nature-paper-skills의 `paywalled_unverifiable` 분류가 이 현실을 인정).
  - **PDF**: 파싱은 가능하나 레이아웃 깨짐, 표/그림 안 수치 추출 정확도 저하.
  - **스크래핑 차단**: 403/Cloudflare/robots.txt로 자동화된 요청을 막는 사이트가 많아, "그 페이지에 실제로 있는지"조차 확인 못 하는 경우가 상당수 발생. urlhealth 논문도 "우리 환각률 추정치는 보수적 하한선"이라고 인정하는 이유가 이것.

### L3 (의미적 entailment) — LLM/NLI가 필요한 지점과 보고된 정확도

- L3는 본질적으로 자연어추론(NLI) 문제: "페이지 내용 X가 주장 Y를 함의(entail)하는가"는 문자열 매칭으로 판정 불가능(패러프레이즈, 함축, 부분지지, 맥락 왜곡 등) → LLM 또는 전용 NLI 모델 필요.
- **보고된 정확도(모두 확인된 수치)**:
  - **SAFE**([Wei et al., "Long-form factuality in large language models," DeepMind, 2024](https://arxiv.org/abs/2403.18802)): 약 16,000개 개별 사실에 대해 크라우드소싱 인간 평가자와 **72% 일치**. 불일치한 100건 표본 중 SAFE가 **76%**의 경우 더 정확(→ "초인간적"이라는 주장의 근거). 단, 이는 "인간 대비 상대적으로 낫다"는 것이지 절대 정확도가 아니며, Gary Marcus 등은 "초인간"이 "저임금 크라우드워커보다 낫다"는 의미일 뿐이라고 반박.
  - **VeriScore**([Song et al., 2024](https://arxiv.org/pdf/2406.19276)): 삼중 주석된 50개 클레임에서 완전 일치 82%, Fleiss' κ = 0.7316(상당한 일치도). 클레임 추출 방식은 SAFE/FActScore 대비 8개 과제에서 93% 선호됨.
  - **AttributionBench**([Li et al., ACL'24 Findings](https://arxiv.org/abs/2402.15089)): 이진 분류(지지/비지지) 기준으로 **파인튜닝된 GPT-3.5조차 macro-F1 약 80%에 그침**. 클레임·근거가 짧은 과제(AttributedQA, AttrEval-GenSearch)에서는 GPT-3.5/GPT-4가 80% 이상(GPT-4는 AttrEval-GenSearch에서 81~83% 정확도)이지만, 근거가 긴 과제일수록 성능 하락. 논문 결론: "자동 attribution 평가는 최신 LLM에게도 어렵다."
- **정리**: L3는 최선의 방법론으로도 **정확도 상한이 대략 75~85% 구간**에 머문다. 즉 L3 자동 판정 도구를 만들어도 "5건 중 1건꼴로 틀릴 수 있는 판정"이라는 한계를 이용자에게 명확히 알려야 하며, 100% 신뢰 가능한 자동 심판은 현재 기술 수준에서 존재하지 않는다.

---

## 8. 리스크 및 미확인 사항

- SemanticCite, citation-check-skill(serenakeyitan), citation-validator(liangdabiao) 등은 **README/SKILL.md 요약본만 확인**했고 실제 코드를 clone해 동작을 재현하지는 않았다 — 설명과 실제 동작이 다를 가능성 있음.
- `sourceverify` 플러그인의 실제 범위(정말 학술 논문 한정인지)는 API 문서를 직접 열람하지 못해 **이름+한 줄 설명 기준의 추정**이다.
- Bing Copilot, OpenAI Deep Research의 "제3자 문서 검증 가능 여부"는 공식 문서를 직접 대조하지 못했고 일반적 통념 기반 추정이다.
- 이 분야는 2025~2026년 사이에 급격히 논문·도구가 늘고 있는 영역(`urlhealth`가 2026년 게재)이라, **지금 비어 있어도 몇 달 내 경쟁자가 나올 개연성**이 있다.
- 유료 SaaS(CiteCheck, CiteMe, CiteGenie, CiteGuardian 등)는 랜딩페이지 문구만 확인했고 실제 가입해서 기능을 테스트하지는 않았다 — 문구와 실제 기능 사이 갭이 있을 수 있다.

---

## 부록: 조사에 사용한 원본 링크 모음

- [urlhealth 논문 — Detecting and Correcting Reference Hallucinations in Commercial LLMs and Deep Research Agents (arXiv:2604.03173)](https://arxiv.org/abs/2604.03173)
- [SAFE / LongFact — Long-form factuality in large language models (arXiv:2403.18802)](https://arxiv.org/abs/2403.18802) / [GitHub](https://github.com/google-deepmind/long-form-factuality)
- [VeriScore (arXiv:2406.19276)](https://arxiv.org/pdf/2406.19276)
- [AttributionBench (arXiv:2402.15089)](https://arxiv.org/abs/2402.15089) / [GitHub](https://github.com/OSU-NLP-Group/AttributionBench)
- [ALCE — Enabling LLMs to Generate Text with Citations (arXiv:2305.14627)](https://arxiv.org/abs/2305.14627) / [GitHub](https://github.com/princeton-nlp/ALCE)
- [Columbia Journalism Review, Tow Center — AI Search Has a Citation Problem (2025-03-06)](https://www.cjr.org/tow_center/we-compared-eight-ai-search-engines-theyre-all-bad-at-citing-news.php)
- [SemanticCite GitHub](https://github.com/sebhaan/semanticcite)
- [RefChecker GitHub](https://github.com/markrussinovich/refchecker)
- [hallucinator GitHub](https://github.com/gianlucasb/hallucinator)
- [Hermes Agent — grounded-citations skill 문서](https://hermes-agent.nousresearch.com/docs/user-guide/skills/bundled/research/research-grounded-citations)
- [Google Cloud Check Grounding API 문서](https://docs.cloud.google.com/generative-ai-app-builder/docs/check-grounding)
- [Gemini Apps — related sources & double-check responses](https://support.google.com/gemini/answer/14143489?hl=en)
- [Claude 커뮤니티 마켓 marketplace.json](https://github.com/anthropics/claude-plugins-community/blob/main/.claude-plugin/marketplace.json)
