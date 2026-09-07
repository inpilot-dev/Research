# 플러그인 골격 — `verify` (v1 확정)

2026-09-03 재작성. 결정 근거: [16 종합](16-synthesis-research-agent.md) · [CONTEXT.md](../CONTEXT.md) · ADR [0001](../docs/adr/0001-deterministic-verification-core.md) [0002](../docs/adr/0002-domains-are-data-not-skills.md) [0003](../docs/adr/0003-no-output-without-verification-gate.md)

---

## 0. 제품 한 줄

**리서치 산출물의 주장을 출처 원문과 대조해, 검증 못 한 건 "미확인"으로만 내보내는 파이프라인.** 입력은 문서(AI 리서치 리포트·논문·참고문헌 목록)이거나 질문이다. 검색·요약은 남이 하고, 우리는 게이트다.

## 1. 확정된 결정

| 항목 | 결정 |
|---|---|
| 이름 | `verify` (skills.sh `find`가 이름 부분일치 → 짧은 일반명사, fact-check 계열에 강자 없음) |
| v1 유형 | **학술 문헌 · 기술/API 문서 · 빠른 팩트** 3개. 라우터는 9유형 슬롯을 두되 3개만 채움 |
| 검증 깊이 | **L2 기본**(원문 fetch + 텍스트 대조, 결정론적). L3(의미적)는 `--deep` 옵션, LLM 사용 |
| 첫 구현 | `scripts/cite_check.py` — 신뢰성 척추 ①독립성 ②원문대조를 파일 하나로 증명 |
| 배포 | Claude Code 플러그인. MCP 서버 안 만듦. 로직은 `scripts/`, CLI는 같은 스크립트 |
| 도메인 | 어댑터·프로파일 데이터. 의학 NCT 대조는 **프리미엄 모듈**로 v2 이후 |
| 라이선스 | MIT |

## 2. 구조

```
verify/
├── .claude-plugin/plugin.json
├── CONTEXT.md                      # 용어집 (있음)
├── docs/adr/                       # 0001~0003 (있음)
├── skills/
│   ├── verify/SKILL.md             # 입력: 문서/URL목록/DOI → cite_check → 리포트
│   └── research/SKILL.md           # 입력: 질문 → 라우터 → 리더 → 게이트 → 종합
├── agents/
│   └── reader.md                   # 출처 원문 격리 읽기, 구조화 추출만 반환
├── hooks/hooks.json                # 산출물 Write 전: 출처 토큰 없는 단정문 차단
├── scripts/
│   └── cite_check.py               # ★ 결정론적 코어 (있음)
├── sources/
│   ├── crossref.json               # DOI → 서지 (무인증)
│   └── openalex.json               # 학술 메타 (크레딧 헤더 주의)
├── profiles/                       # v1 비움. 의학 모듈 때 oncology.yaml
└── tests/
    └── test_cite_check.py          # (있음)
```

스킬 2 : 에이전트 1. 05의 "얇게 시작" — `skeptic`(반증 탐색)은 eval에서 필요가 보이면 추가. 12가 "가이드 없는 동종 토론은 자기교정보다 못할 수 있다"고 경고.

## 3. 신뢰성 척추 ↔ 구현 매핑

| 원리 | 어디서 | 결정론? |
|---|---|---|
| ① 독립성 검증 | `cite_check` unique-publisher dedup | ✅ |
| ② 원문 대조 | `cite_check` L2 exact/fuzzy | ✅ |
| ③ 감사 가능성 | `cite_check` summary + 리포트에 검색/채택/제외 수 | ✅ |
| ④ 신뢰도≠사실 | 리포트 템플릿 [주장–L레벨–퍼블리셔수–상충] | 템플릿 |
| ⑤ 반증 지향 | `research` 스킬 계획 단계 규칙("넓게→좁게", 반대 근거 1회 검색) | 프롬프트 |
| ⑥ 지시/데이터 분리 | `reader` 에이전트 읽기 전용 · fetch 내용은 데이터로만 | 권한 설정 |

## 4. 데이터 계약 (스킬이 서로를 찾는 방식 — 05)

```
claims.json     [{claim, url}]                       ← verify 입력 / reader 출력
results.json    {results:[{claim,url,alive,status,found,score,published,publisher}], summary}
report.md       주장마다 [publisher:found] 토큰. "미확인"은 단정문 금지
```
파일명을 SKILL.md description에 박는다 (`Use after reader when claims.json exists…`).

## 5. 착수 순서

1. ✅ `scripts/cite_check.py` + 테스트
2. `skills/verify/SKILL.md` — cite_check 래퍼 + 리포트 템플릿
3. `hooks/hooks.json` — 출처 토큰 없는 단정문 Write 차단 (ADR 0003 기계화)
4. 라우터 3유형 + `skills/research/SKILL.md` + `agents/reader.md`
5. `sources/crossref.json`, `openalex.json`
6. eval 세트 — 유형별 대표 쿼리 20개 + LLM-judge 5기준 + 인간 검토 (12 권고)
7. README: 한 줄 설치 · vhs GIF · "아직 못 하는 것" · MIT

**보류(v2)**: `trial-check`(의학 NCT) · `snapshot`(재현성) · `budget`(사전 비용) · L3 `--deep` · 나머지 6유형.

## 6. 남은 리스크

- 인용 fetch가 출처 사이트를 대량 호출함 — rate limit·차단. `cite_check`에 per-publisher 간격 필요 (v1은 순차 호출로 회피, ponytail 천장 표시).
- npj Digital Medicine 2026 (outcome switching 자동탐지) — **의학 모듈 착수 전에만** 확인. v1 무관.
- 콜드스타트(01): find-skills가 설치 1K·star 100 미만 필터링. 초기 유통은 사람 링크로.
