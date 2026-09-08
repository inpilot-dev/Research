# Research

`verify` — 리서치 산출물의 주장을 출처 원문과 대조하는 Claude Code 플러그인. 사용법과 한계는 `README.md`.

## 이 저장소에서 일할 때

- **판정은 `scripts/cite_check.py` 만 한다** (ADR 0001). 스킬·에이전트는 얇은 래퍼이고, 프롬프트로 판정을 다시 하거나 바꾸지 않는다.
- **`근거 없음`과 `확인 불가`를 섞지 않는다.** `근거 없음`은 원문을 읽고 못 찾은 것, `확인 불가`는 원문을 못 읽은 것이다. 이 구분이 무너지는 변경은 그 자체로 결함이다 (ADR 0002·0003).
- **자격증명은 성역이다** (ADR 0004). 비밀번호·키체인·브라우저 저장소를 읽지 않고, 로그인 폼을 채우지 않고, CAPTCHA 를 풀지 않는다. `tests/test_access_ladder.py` 의 `SacredList` 가 이를 코드로 강제한다 — 그 테스트를 느슨하게 만드는 변경은 하지 않는다.
- **도메인·유형·출처는 데이터다**, 코드가 아니다 (ADR 0002). 새 출처는 `sources/*.json`, 새 유형 세팅은 `profiles/types.json`.
- 표준 라이브러리만 쓴다. 칸 3·4의 선택 의존성은 `requirements-access.txt` 에만 있고, 없으면 건너뛰고 감사 로그에 남긴다.

## 확인

```bash
python3 -m unittest discover -s tests   # 네트워크·LLM 없음
python3 scripts/eval_run.py             # 녹화본 회귀 평가 (오프라인)
claude plugin validate .

python3 evals/demo_end_to_end.py        # 실물 출처로 3유형 전체 파이프라인 (네트워크)
python3 evals/measure_ladder.py         # 사다리가 어디서 왜 막히는지 분포 (네트워크)
```

선택 의존성을 깔지 말지는 `measure_ladder.py` 로 **재보고** 정한다. 짐작으로 깔지 않는다 —
2026-09-08 측정에서 `dynamic` 이 25건 중 3건이었고, 그중 중요한 하나는 API 어댑터로 해결돼
playwright 를 깔지 않았다. `curl_cffi` 는 403 다섯 곳 중 셋을 열어 설치했다.

평가 통과율은 **자기보고**다. 사람 검수 절차는 `evals/HUMAN-REVIEW.md` 이고 아직 수행되지 않았다.

## 구조

| 경로 | 내용 |
|---|---|
| `scripts/` | 결정론적 코어와 도구 (판정·접근 사다리·어댑터·추출·라우터·게이트·종합·평가) |
| `skills/`, `agents/`, `hooks/` | 플러그인 표면 |
| `sources/`, `profiles/` | 어댑터·유형 설정 데이터 |
| `evals/` | 회귀 평가 세트·녹화본·판정기·검수 절차 |
| `docs/adr/` | 설계 결정. `CONTEXT.md` 는 용어집 |
| `research/` | 이 제품을 정하기까지의 조사 기록 (01~17) |

## Agent skills

### Issue tracker

GitHub Issues on `inpilot-dev/Research`, via the `gh` CLI. See `docs/agents/issue-tracker.md`.

### Triage labels

The five canonical labels, unchanged (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`). See `docs/agents/triage-labels.md`.

### Domain docs

Single-context — `CONTEXT.md` + `docs/adr/` at the repo root. See `docs/agents/domain.md`.
