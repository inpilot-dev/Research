# 소스 접근/검색/페치 도구 지형 (Research Stream 13)

**조사 목적**: 리서치 에이전트가 실제로 소스 본문을 확보하는 레이어 전체를 넓게 조사. `insane-search`는 별도 스트림에서 조사 중이므로 이 문서에서는 다루지 않고, 그 외 대안 전부를 6개 카테고리로 나눠 공식 문서/레포 기준으로 비교한다.

**원칙**: 가격·rate limit·★ 수 등은 전부 공식 문서/가격 페이지/GitHub에서 직접 확인한 값만 싣는다. 확인하지 못한 값은 추측하지 않고 **"미확인"**으로 남긴다. 조사 시점은 2026-09-03(문서 내 개별 확인 시점은 각 표 참고).

---

## TL;DR — 결론 먼저

- **완전 무료 + 완전 로컬(오프라인) 조합은 "본문 추출 + PDF/문서 추출 + 브라우저 자동화"까지만 가능하고, "검색(웹에서 관련 URL을 찾는 것)"만큼은 오프라인으로 대체할 방법이 이번 조사 범위에서 확인되지 않았다.** 검색 API 8종 전부 클라우드 호스티드이며 온프레미스/셀프호스팅 옵션은 공식 문서 어디에도 없다.
- 본문 추출(trafilatura, Readability.js), PDF 추출(PyMuPDF, marker, docling, Grobid), 브라우저 자동화(Playwright)는 전부 오픈소스 로컬 라이브러리로 완전 오프라인 실행이 가능하다 — 폐쇄망 환경에서도 핵심 파이프라인은 구성 가능하다.
- 안티봇 우회는 상용 클라우드 서비스(ScrapingBee/Bright Data/ScraperAPI/Zyte) 4종 모두 클라우드 전용이고, 로컬/셀프호스팅이 가능한 건 `curl_cffi`(TLS 임퍼서네이션 라이브러리)와 `FlareSolverr`(Cloudflare 챌린지 우회 프록시 서버) 둘뿐이다.
- MCP 서버 계층에서는 `mcp-server-fetch`(공식, PyPI)가 API 키 없이 완전 로컬 stdio로 뜨는 유일한 선택지이고, Firecrawl/Exa/Tavily MCP는 전부 API 키가 필요한 클라우드 백엔드에 의존한다(단 셋 다 로컬 stdio 프로세스로는 뜬다).
- Postlight Parser(구 Mercury Parser)는 **사실상 유지보수 중단**(마지막 실질 커밋 2023-03, 마지막 릴리스 2022-10) 상태라 신규 채택 리스크가 크다.

---

## 1. 검색 API

리서치 에이전트가 "무엇을 찾을지" 결정하는 첫 레이어. 조사 대상: Tavily, Exa, Brave Search API, SerpAPI, Serper, Google Programmable Search(Custom Search JSON API), Kagi(Search API/FastGPT), You.com API.

| 이름 | 무료 티어 | 유료 가격 | 인증 방식 | Rate Limit | AI 에이전트 특화 기능 | 실패 모드 | 오프라인/로컬 |
|---|---|---|---|---|---|---|---|
| **[Tavily](https://docs.tavily.com/documentation/api-credits)** ([가격](https://tavily.com/pricing)) | 월 1,000 API 크레딧, 카드 불필요 (Researcher 플랜) | 종량제 $0.008/크레딧; Project 플랜 월 4,000크레딧부터 $30~$500대 | `Authorization: Bearer tvly-<KEY>` | Search Dev 100 RPM / Prod 1,000 RPM, Crawl 100 RPM, Research 20 RPM, Usage 10회/10분 | search/extract/crawl/research 엔드포인트 구분(순차 호출 전제 설계). 별도 "에이전트 특화" 마케팅 문구는 미확인 | 429 + `retry-after` 헤더 | 불가 (호스티드) |
| **[Exa](https://exa.ai/docs)** ([가격](https://exa.ai/pricing)) | 가입 시 $20 크레딧(약 2,800건 검색 상당), 이후 월 $10 무료 | Search $7/1,000건, Deep Search $12-15/1,000건, Answer $5/1,000건, Monitors $15/1,000건, Contents $1/1,000페이지, Agent API $0.012~$1.00 또는 $0.10/ACU | `Authorization: Bearer $EXA_API_KEY` | `/search` 10 QPS, `/contents` 100 QPS, `/answer` 10 QPS (상향은 Enterprise 문의) | Answer API(구조화 답변), Agent API(고정노력/ACU 기반, 이메일·전화 농축). 임베딩 기반 "neural search" 표방(세부 스펙 재검증 필요) | 쿼터 초과 시 구체적 동작 미확인 | 불가 (호스티드) |
| **[Brave Search API](https://api-dashboard.search.brave.com/app/documentation)** ([플랜](https://api-dashboard.search.brave.com/app/plans)) | 월 $5 무료 크레딧 자동 적용(약 1,000건 상당). ⚠️ 과거 "월 2,000건/1QPS 무료" 플랜은 2026년 초 신규가입 대상 종료 | Web Search $5/1,000건, Answers $4/1,000건+토큰당 $5/백만, Spellcheck·Autosuggest $5/10,000건 | `X-Subscription-Token: <KEY>` | Web Search 50 QPS, Answers 2 QPS, Spellcheck·Autosuggest 100 QPS | Answers 엔드포인트: 그라운딩·인용 지원 요약, "AI 최적화 LLM 컨텍스트" 명시, OpenAI SDK 호환 스트리밍 | 에러 코드 미확인 | 불가 (호스티드) |
| **[SerpAPI](https://serpapi.com/pricing)** | 월 250건, 시간당 50건 (Free) | Starter $25/월(1,000건/시간당200), Developer $75(5,000건/시간당1,000), Production $150(15,000건/시간당3,000), 최상위 월 최대 5천만건 | 쿼리파라미터 `api_key=<KEY>` | 플랜별 "시간당 처리량"만 명시, 초/분당 수치 미확인 | 표준 SERP 파싱 API 성격, 별도 에이전트 특화 기능 미확인 | [공식 에러코드](https://serpapi.com/api-status-and-error-codes): 400/401/403/404/410/429/500/503 | 불가 (호스티드) |
| **[Serper](https://serper.dev/)** | 2,500 무료 쿼리, 카드 불필요 | 공식 가격 페이지 확인 실패(반복 404) — **미확인** | 추정(미확인, 공식 페이지 접근 실패) | 미확인 | 미확인 | 미확인 | 불가 (호스티드로 추정) |
| **[Google Programmable Search](https://developers.google.com/custom-search/v1/overview)** (Custom Search JSON API) | 하루 100건 무료 | 추가 $5/1,000건, 유료도 프로젝트당 하루 10,000건 고정 상한(증액 불가) | 쿼리파라미터 `key=<KEY>` | 일일 상한만 확인(초/분당 미확인) | 표준 웹검색 JSON, 에이전트 특화 기능 미확인 | 에러 응답 미확인 | 불가 (호스티드). **⚠️ 2027-01-01 이후 서비스 종료 예정, 신규 가입 불가(기존 고객만)** |
| **[Kagi Search API](https://help.kagi.com/kagi/api/search.html) / [FastGPT](https://help.kagi.com/kagi/api/fastgpt.html)** ([가격](https://kagi.com/api/pricing)) | 무료 티어 없음(트라이얼만), 선불 크레딧제 | Search $12/1,000건, Extract $4/1,000페이지, FastGPT $15/1,000건(web_search 파라미터는 "서비스 중단" 상태 표기) | `Authorization: Bot $TOKEN` | 미확인(Enterprise "커스텀 rate limit"만 언급) | FastGPT는 "agent용" 명시, 근거자료(citations) 포함 응답. Extract API는 URL→Markdown 정제 | 크레딧 부족 시 "Insufficient credit..." 메시지 확인, 그 외 코드 미확인 | 불가 (호스티드) |
| **[You.com API](https://you.com/docs/api-reference)** ([가격](https://you.com/pricing)) | 가입 시 $100 크레딧, 일일 100건 한도 | Web Search $5/1,000건, Contents $1/1,000페이지, Answer $5/1,000건, Research $12/1,000건, Finance Research $110/1,000건 | `X-API-Key: <KEY>` | 구체적 QPS 미확인(Enterprise "Custom QPS"만 언급) | 3단계 콘텐츠 반환(Snippets/Highlights/Full Page) — Highlights는 "토큰 민감 에이전트 워크플로용" 명시, MCP 연동 지원 | 에러 코드 미확인 | 불가 (호스티드) |

**소결 — AI 에이전트용 검색 API가 전통 SERP 스크래핑과 다른 점**
- 처음부터 JSON/Markdown 등 파싱 완료 결과를 반환하고, 일부는 답변형 요약(Brave/You.com/Exa Answer)까지 제공해 LLM 컨텍스트 조립 단계를 줄인다.
- You.com Highlights처럼 "에이전트의 토큰 예산"을 명시적으로 겨냥한 응답 모드가 존재 — 전통 SERP API엔 없는 개념.
- 크레딧 소모형 + 엔드포인트별 분리 rate limit(검색/크롤/리서치)이 일반적 — 에이전트가 한 작업에서 여러 API를 순차 호출하는 패턴을 전제로 설계됨.
- **8개 전부 완전 자체 호스팅 옵션 없음.** Enterprise 플랜에서도 "ZDR(제로 데이터 보관)" 정도이지 온프레미스 배포는 아니다.

---

## 2. 페치/본문추출 (HTML → 클린 마크다운)

| 항목 | Firecrawl | Jina Reader (r.jina.ai) | trafilatura | Mozilla Readability | Postlight Parser |
|---|---|---|---|---|---|
| 링크 | [docs.firecrawl.dev](https://docs.firecrawl.dev) · [github](https://github.com/mendableai/firecrawl) | [jina.ai/reader](https://jina.ai/reader) · [github](https://github.com/jina-ai/reader) | [trafilatura.readthedocs.io](https://trafilatura.readthedocs.io) · [github](https://github.com/adbar/trafilatura) | [github](https://github.com/mozilla/readability) | [github](https://github.com/postlight/parser) |
| GitHub ★ | 미확인(실시간 수치 확보 실패) | ~11.4k~11.9k(측정 편차, 확정 못함) | 6,754 | 11,424 | 5,788 |
| 가격 | Free $0(1,000크레딧/2동시) → Hobby $16 → Standard $83 → Growth $333 → Scale $599(월) → Enterprise 커스텀 | 무키 무료(20RPM) / 가입 무료키(500RPM+1000만 토큰) / 유료는 토큰당 과금(정확 단가 미확인) | 무료(Apache-2.0) | 무료(Apache-2.0) | 무료(오픈소스) |
| 인증 | Bearer API 키(무키도 낮은 한도로 가능) | API 키(무키도 가능, 한도 낮음) | 없음(로컬) | 없음(로컬) | 없음(로컬) |
| Rate limit | Free 10req/min, 유료 티어별 100~10,000/min | 무키 20RPM, 무료키 500RPM, 유료 500RPM, 프리미엄 5,000RPM | N/A(로컬) | N/A | N/A |
| 추출 방식 | 헤드리스 브라우저 렌더링 + "auto" 모드, markdown/html/JSON(스키마·프롬프트 기반)/스크린샷 다중 포맷 | Readability 스타일 필터링 + curl-impersonate/헤드리스 Chrome 지능적 선택. "ReaderLM-v2"(1.5B HTML→MD 특화 모델) 홍보되나 기본 엔진 여부 미확인 | 자체 규칙 기반 + jusText/readability-lxml 폴백, 자체 벤치마크(2026) F-score 0.924 주장 | Arc90 원조 알고리즘 계승, 후보 스코어링(nbTopCandidates, charThreshold 등 파라미터 문서화) | 범용 추출기 + 사이트별 커스텀 익스트랙터 |
| 실패 모드 | 402/429/500, 프록시 basic/enhanced/auto 모드로 차단 우회 시도 | 403/CAPTCHA 명시적 에러코드 문서 못 찾음(미확인). `x-timeout`(최대180s) 등 제어 헤더 존재 | malformed HTML/encoding 시 일부 실패(비교 대상 도구 기준), 페이월 처리 미확인 | "unsafe content 제거는 목적 아님"(DOMPurify 권장), `isProbablyReaderable()`은 오탐 가능성 명시 | 필드 못 찾으면 null 반환만 명시 |
| 오프라인 | 클라우드 API 기본, 엔진은 AGPL-3.0 오픈소스로 셀프호스팅 가능 | 클라우드 기본, Apache-2.0 오픈소스로 Docker 셀프호스팅 가능 | 완전 로컬 가능 | 완전 로컬(네트워크 호출 없음) | 완전 로컬(사전 페치 HTML 처리 시) |
| 비고 | — | — | — | — | **사실상 유지보수 중단**: 마지막 커밋 2023-03-15, 릴리스 2022-10-24, open issue 116개 |

---

## 3. 안티봇/차단 우회 대안

| 항목 | ScrapingBee | Bright Data | ScraperAPI | Zyte API | curl_cffi | FlareSolverr |
|---|---|---|---|---|---|---|
| 링크 | [scrapingbee.com](https://scrapingbee.com/documentation) | [docs.brightdata.com](https://docs.brightdata.com) | [docs.scraperapi.com](https://docs.scraperapi.com) | [docs.zyte.com](https://docs.zyte.com) | [github](https://github.com/lexiforest/curl_cffi) (구 yifeikong/curl_cffi, 리네임) | [github](https://github.com/FlareSolverr/FlareSolverr) |
| GitHub ★ | N/A(SDK만) | N/A(클라우드) | N/A | N/A | 6,432 (최근 커밋 2026-09-02, 활발) | 15,389 |
| 가격 | Free 1,000크레딧 → Hobby $19(75k) → Freelance $49(250k) → Startup $99(1M) → Business $249(3M) → Business+ $599(8M). 성공 응답만 과금 | Unlocker/Scraper API 무료 5,000req/월, Scraping Browser 무료 5,000크레딧(1GB)/월. PAYG $1.50/1,000req, $8/GB(Browser). Scale $499/월 | 트라이얼 5,000크레딧 + 상시 무료 월1,000. 유료 $49(100k,20thread)~$1,975(21.5M,500thread) | 가입 시 $5 크레딧(30일). PAYG HTTP $0.13~1.27/1,000건, Browser $1.01~16.08/1,000건. 월정액 커밋 시 최대 ~50% 할인. 성공 응답만 과금 | 무료(MIT), 최신 핑거프린트 일부는 유료 `impersonate.pro` | 무료(MIT) |
| 인증 | API 키 | Unlocker/Scraper API: Bearer 토큰. Scraping Browser: CDP URL에 프록시 자격증명 임베드 | API 키 | API 키 | 없음(로컬) | 없음(자체호스팅) |
| Rate limit | 동시성 25~400(플랜별, 커스텀 상향 가능), 정확 RPS 미확인 | 전 상품 "무제한 동시성" 표방, 내부 스로틀 수치 미확인 | thread 20~500(플랜별), RPS 미확인 | 기본 3,000 RPM, 동시성 무제한, Enterprise 상향 가능 | N/A(로컬) | N/A(로컬) |
| 추출 방식 | `return_page_markdown`/`return_page_text`로 클린 텍스트 직접 제공 | Unlocker/Browser는 원문 HTML만 반환, Web Scraper API는 사이트별 템플릿 구조화 데이터 | 원문 HTML + "AI Parser"(스키마 기반 구조화) | 원문 응답 + 자체 AI 파싱/커스텀 속성 추출 | 추출 기능 없음 — TLS/JA3/HTTP2 핑거프린트 위장 HTTP 클라이언트만 | 추출 기능 없음 — Cloudflare 챌린지 통과 후 HTML+쿠키+UA만 반환 |
| 실패 모드 | 자동 재시도(최대30초), premium/stealth 프록시. 성공(200/404/410)만 과금 | CAPTCHA "자동 해결", "지능형 재시도/세션 복구" 표방 | 70초 타임아웃 권장, 403/CAPTCHA 세부 미확인 | 에러 문서 페이지 존재, 세부 미확인 | 표준 HTTP 예외만(자체 재시도/우회 로직 없음). 37개 브라우저 핑거프린트 프리셋(Chrome99~146, Firefox133~147, Safari, Edge, Tor 등) | 캡차 못 풀면 `"Captcha detected but no automatic solver is configured."` 에러로 종료, 폴백 없음 |
| 오프라인 | 불가(클라우드) | 불가(클라우드) | 불가(클라우드) | 불가(클라우드) | 로컬 라이브러리(대상 요청은 네트워크 필요) | 셀프호스팅(제3자 클라우드 의존 없음, 대상 요청은 네트워크 필요) |
| 합법성/ToS | "윤리적 스크래핑" 블로그 언급만, 구속력 정책 미확인 | [Trust Center](https://brightdata.com/trustcenter)에 공식 AUP·GDPR 정책 게시, 로그인 뒤 스크래핑 명시적 금지. 6개 중 가장 명확한 법적 입장 문서 보유 | 미확인, 사용 전 대상 ToS 검토 필요 | 미확인, 사용 전 대상 ToS 검토 필요 | README에 disclaimer 없음. 도구 자체는 합법이나 TLS 위장으로 대상 ToS 위반 가능성 있음 | README에 오남용 경고(`"DO NOT expose to the internet"`)는 있으나 ToS 언급 없음 |
| 비고 | — | — | — | — | 정본 저장소 `yifeikong/curl_cffi` → `lexiforest/curl_cffi` 리네임됨 | 동일 조직 산하 `FlareSolverr1`/`FlareSolverr2`는 2025-12-16 archived 이력 있어 혼동 주의. 메인 저장소는 archived 아님(최근 커밋 2026-08-25) |

---

## 4. 브라우저 자동화

| 이름 | 링크 | GitHub ★ | 라이선스/가격 | 인증 | 핵심 강점 | 실패 모드 | 오프라인 |
|---|---|---|---|---|---|---|---|
| **Playwright** | [github](https://github.com/microsoft/playwright) · [playwright.dev](https://playwright.dev) | 95.5k | Apache-2.0 | 없음(로컬). `storageState`로 쿠키·로컬스토리지·IndexedDB·WebAuthn을 JSON으로 저장/재사용해 로그인 세션 유지 | 실제 Chromium/Firefox/WebKit 구동 → 동적 렌더링(SPA)을 별도 처리 없이 지원 | 자체 캡차 우회·봇 탐지 회피 기능 없음(별도 stealth 설정 필요) | 가능(완전 로컬) |
| **browser-use** | [github](https://github.com/browser-use/browser-use) | 112.1k | MIT | 없음(로컬), LLM provider API 키 별도 | Playwright 기반 + AI 에이전트가 사람처럼 탐색/클릭/입력. "기존 Chrome 프로필 재사용" 또는 클라우드 `profile-use`로 세션 유지 | 캡차 자체 미지원, 공식 문서는 "Browser Use Cloud" stealth 브라우저/프록시 권장 | 브라우저 구동은 로컬 가능하나 LLM 호출 필요 — **부분적 오프라인**(오프라인 전용 공식 가이드는 없음, Ollama 연동 언급만 있음) |
| **Stagehand** | [github](https://github.com/browserbase/stagehand) · [docs.stagehand.dev](https://docs.stagehand.dev) | 24.1k | MIT | Browserbase API 키(클라우드 브라우저 인스턴스 실행용) | Playwright 스타일 API + "self-healing actions"(사이트 구조 변경 자동 대응), 토큰 효율 우선 | LLM 기반 액션 해석 실패 시 self-healing이 항상 정확하지 않을 수 있음(구체 실패율 미확인) | **불가** — `browserbase.launch()`로 클라우드 브라우저 인스턴스 실행이 필수, 로컬 드라이버 지원 명시 없음 |
| **Claude in Chrome** | [support.claude.com](https://support.claude.com/en/articles/12012173-get-started-with-claude-in-chrome) · [code.claude.com/docs/en/chrome](https://code.claude.com/docs/en/chrome) | 해당 없음(비공개) | 비공개, Anthropic 유료 플랜(Pro/Max/Team/Enterprise) 필요 | Anthropic 계정 로그인 | 자연어로 브라우저 탐색·폼작성·데이터추출·다단계 워크플로우, 사용자 절차 "기록"으로 반복작업 학습 | 미확인(공식 문서에 실패 모드 목록 없음) | 불가(Anthropic 클라우드 계정·확장 프로그램 필요) |

---

## 5. PDF/문서 추출

| 이름 | 링크 | GitHub ★ | 라이선스 | 핵심 강점(표·수식·레이아웃) | 실패 모드 | 오프라인 |
|---|---|---|---|---|---|---|
| **PyMuPDF (fitz)** | [github](https://github.com/pymupdf/PyMuPDF) · [pymupdf.readthedocs.io](https://pymupdf.readthedocs.io) | 10.6k | AGPL-3.0(오픈소스, 상용 라이선스 별도 존재·가격 미확인) | MuPDF 엔진 고속 텍스트 추출, `find_tables()`로 표를 Markdown/구조화 데이터로, PyMuPDF4LLM으로 LLM용 구조화 Markdown | **네이티브(디지털) PDF 전용** — 스캔본은 텍스트 0. `get_textpage_ocr()`로 OCR 가능하나 Tesseract 별도 필요 | 가능(완전 로컬) |
| **marker** | [github](https://github.com/VikParuchuri/marker) | 39.5k | Apache-2.0(코드)/모델은 Modified AI Pubs Open Rail-M | 표·양식·수식(인라인 math)·참고문헌·코드블록 포맷 유지, Markdown/JSON/HTML/청크 변환, VLM으로 수식 인식, 표 변환 벤치마크 73.4% | VLM 기반이라 GPU 없이 느림, 복잡 레이아웃/저품질 스캔에서 정확도 저하 가능(구체 실패율 미확인) | 가능(GPU/CPU/MPS 로컬) |
| **docling** | [github](https://github.com/docling-project/docling) | 65.9k | MIT(코드) | IBM Research 시작. 레이아웃·읽기순서·표구조·코드·수식·이미지 분류, `DoclingDocument` 통합 표현. **"에어갭 환경 로컬 실행"을 공식 셀링포인트로 명시** | 기본 OCR(EasyOCR)이 손글씨/저품질 스캔에서 정확도 낮음, 다단 레이아웃 평탄화로 시각적 순서 파괴 가능(서드파티 비교 리뷰 기준, 공식 벤치마크 별도 확인 필요) | 가능(공식 에어갭 지원 명시) |
| **unstructured** | [github](https://github.com/Unstructured-IO/unstructured) · [docs.unstructured.io](https://docs.unstructured.io) | 15.4k | Apache-2.0(라이브러리) / Serverless API 별도 상용($0.015/페이지, 월 무료 15,000페이지) | 60여 종 포맷을 LLM 친화 구조화 데이터로, 다양한 커넥터·MCP 서버 지원 | 표/레이아웃 처리 정확도 공식 벤치마크 미확인 | 오픈소스 라이브러리는 가능(로컬), Serverless API/엔터프라이즈는 클라우드 의존 |
| **Grobid** | [github](https://github.com/kermitt2/grobid)(조직 `grobidOrg/grobid`로 이전 표시) · [grobid.readthedocs.io](https://grobid.readthedocs.io) | 5.1k | Apache-2.0 | **학술 논문 특화**: 헤더(제목·저자·소속)·참고문헌·본문을 섹션/문단/표/그림 구조로, 좌표 정보 보존, **TEI XML** 출력. Docker 셀프호스팅 공식 지원 | 학습 데이터가 주로 영어(일부 독/불)라 타 언어 품질 불확실, 매우 긴 문서는 토큰 한도로 불안정 가능, 각주형 참고문헌 정확도 낮음 | **가능(로컬 Docker 서버로 완전 셀프호스팅 공식 지원)** |

---

## 6. MCP fetch/search 서버

| 항목 | Fetch (공식) | Firecrawl MCP | Exa MCP | Tavily MCP |
|---|---|---|---|---|
| 레포 | [modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers)(`src/fetch`) | [firecrawl/firecrawl-mcp-server](https://github.com/firecrawl/firecrawl-mcp-server) | [exa-labs/exa-mcp-server](https://github.com/exa-labs/exa-mcp-server) | [tavily-ai/tavily-mcp](https://github.com/tavily-ai/tavily-mcp) |
| GitHub ★ | 90,029(모노레포 전체, fetch 단독 수치는 미집계) | 7,377 | 4,955 | 2,366 |
| 패키지명 | **PyPI** `mcp-server-fetch` (npm 동명 패키지는 실제 서버 아닌 예약용 placeholder) | npm `firecrawl-mcp` | npm `exa-mcp-server` | npm `tavily-mcp` |
| 최신 버전/배포일 | 2026.8.18(PyPI) | 3.24.0(2026-08-12) | 3.4.1(2026-08-18) | 0.2.22(2026-08-05) |
| 주간 다운로드 | PyPI 118,282/주(2026-08-23~29) | npm 40,139(동 기간) | npm 25,462(동 기간) | npm 20,899(동 기간) |
| 유지보수 | 마지막 push 2026-09-02, 활발 | 마지막 push 2026-09-01, 활발 | 마지막 push 2026-08-21, 활발 | 마지막 push 2026-09-02, 활발 |
| 제공 도구 | `fetch(url, max_length, start_index, raw)` — HTML→markdown 단일 도구 | scrape, map, search, crawl, parse, agent(비동기 리서치), interact, monitor, developer_search 등 4개 중 가장 넓음 | 기본 `web_search_exa`, `web_fetch_exa` + 옵션 `agent_run`, `web_search_advanced_exa` | `tavily-search`, `tavily-extract`, `tavily-map`, `tavily-crawl` |
| 인증 | **불필요**(API 키 없음) | 필요(`FIRECRAWL_API_KEY`), scrape/search/parse는 keyless 무료(레이트리밋), self-host 시 `FIRECRAWL_API_URL`로 우회 가능 | 필요(OAuth 선호 또는 API 키), 익명도 가능(레이트리밋) | 필요(Tavily API 키), URL파라미터/헤더/OAuth 지원 |
| 로컬 실행 | **가능** — `uvx mcp-server-fetch` 또는 pip, Docker(`mcp/fetch`) 지원. 완전 로컬 stdio | 가능 — `npx -y firecrawl-mcp` 로컬 stdio(원격 `mcp.firecrawl.dev`도 별도 제공) | **미확인/불명확** — README가 호스팅형(`mcp.exa.ai/mcp`) 중심 안내, 로컬 npx stdio 여부 문서상 불명확 | 가능 — `npx -y tavily-mcp@latest`(Node≥20) 로컬 stdio(원격 `mcp.tavily.com`도 병행) |

**소결**: Fetch 서버는 npm이 아니라 **PyPI 패키지**임에 주의(npm 동명 패키지는 placeholder). API 키 없이 완전 로컬로 뜨는 유일한 선택지라 폐쇄망 워크플로우에 적합. Firecrawl MCP가 도구 표면이 가장 넓고 keyless로도 일부 동작. Tavily/Exa는 API 키가 사실상 필수. 4개 모두 2026-08~09월 기준 활발히 유지보수 중.

---

## 7. 권장 스택 (무료/오프라인 우선 관점)

사용자 환경(Ollama qwen2.5-7B 로컬 폴백, 폐쇄망/현장 네트워크 차단 리스크 대비)을 전제로, **"검색은 어차피 클라우드에 의존할 수밖에 없다"**는 제약을 인정한 뒤 그 다음 레이어부터 오프라인 내성을 최대화하는 조합을 제안한다.

**평상시(네트워크 정상) 기본 스택**
1. **검색**: Tavily(무료 월 1,000크레딧, RPM이 넉넉하고 문서화 상태 양호) 또는 Brave Search API($5 무료 크레딧) — 8종 중 가장 저렴하고 신뢰도 있는 무료 티어. Google Programmable Search는 2027-01 서비스 종료 예정이라 신규 도입은 피한다.
2. **본문추출**: `mcp-server-fetch`(PyPI, 키 불필요, 완전 로컬 stdio)를 1차로 시도 → 실패 시 Jina Reader(무키 20RPM 무료)로 폴백. 둘 다 안 되면 trafilatura로 원본 HTML을 직접 파싱(이미 로컬에 있으면 네트워크 자체가 불필요).
3. **동적 렌더링/로그인 필요 페이지**: Playwright(완전 로컬, `storageState`로 세션 유지) — Claude in Chrome은 이미 이 세션에서 쓰는 도구지만 Anthropic 계정·유료 플랜 전제라 현장 네트워크 차단 시 대체 불가.
4. **PDF/문서**: PyMuPDF(빠른 1차 추출) → 표/수식이 중요한 문서는 marker 또는 docling(둘 다 로컬 GPU/CPU 실행 가능) → 학술 논문은 Grobid(Docker 셀프호스팅, TEI XML).
5. **차단 대응이 꼭 필요할 때만**: curl_cffi(로컬 TLS 임퍼서네이션) 또는 FlareSolverr(로컬 Cloudflare 챌린지 우회) — 상용 안티봇 API(ScrapingBee 등)는 클라우드 의존이라 폐쇄망 폴백 경로가 아니므로 기본 스택에서 제외.

**폐쇄망/현장 데모(네트워크 완전 차단 가정) 폴백 스택**
- 검색 API는 대체 불가 — **사전에 필요한 URL/문서를 미리 크롤링해 로컬에 캐시**해두는 것이 유일한 실질적 대응(위 도구들로는 오프라인 검색 자체를 만들 수 없음).
- 캐시된 HTML/PDF는 trafilatura + Readability.js + PyMuPDF + Grobid로 완전 오프라인 파싱·재구성 가능.
- Playwright로 로컬에 저장된 페이지(또는 `file://`)를 렌더링해 재검증 가능.
- LLM 자체는 이미 Ollama qwen2.5-7B 로컬 폴백이 있으므로, 이 조합이면 "검색"만 사전 준비가 필요하고 나머지 파이프라인(페치→추출→구조화)은 오프라인으로 완결된다.

**보류/비권장**
- Postlight Parser: 유지보수 사실상 중단, 신규 채택 비권장.
- Stagehand: Browserbase 클라우드 필수라 오프라인 요건과 충돌.
- Google Programmable Search: 2027-01 서비스 종료 예정, 신규 의존 비권장.
- Serper: 가격/rate limit 등 공식 문서 확인 실패(미확인 다수) — 채택 전 재조사 필요.
