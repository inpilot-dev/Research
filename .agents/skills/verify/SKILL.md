---
name: verify
description: Verify that each claim in a research output is actually present in its cited source (L1 exists, L2 text match, L3 semantic entailment with --deep) and write a markdown report where unverified claims appear only as "미확인", never as assertions. Input is a claims JSON file ([{claim, url}]) — the data contract is claims.json → results.json → report.md. Use when the user asks to verify, fact-check, or audit citations/sources of a report, paper, or reference list, or runs /verify <claims.json>. Do NOT fire when the user wants research performed, a summary written, or a web search — this skill only checks what is already claimed against what the source says.
argument-hint: <claims.json> [--deep] [--strict]
---

# verify — Codex 판

**절차와 절대 규칙은 [`skills/verify/SKILL.md`](../../../skills/verify/SKILL.md) 에 있다. 먼저 그 파일을 읽어라.** 여기 다시 옮겨 적지 않는다 — 두 벌이 되면 갈라진다.

같은 코어(`scripts/cite_check.py`)가 두 하네스에서 똑같이 돈다. 판정은 거기서만 난다 (ADR 0001).

## 이 하네스에서 달라지는 것 (셋뿐이다)

### 1. ⚠️ 쓰기 게이트가 없다 — 리포트를 쓴 직후 손으로 돌려라

공유 스킬 문서에 "훅 게이트가 실제로 돈다 · 끄는 방법은 없다"고 적혀 있다. **그것은 Claude Code 이야기다.** Codex 에는 PreToolUse 훅에 해당하는 것이 없어서 **검증 토큰 없는 단정문이 그대로 파일로 나갈 수 있다.** 막는 것이 없다.

그래서 리포트를 저장한 **직후에 반드시** 이것을 돌린다:

```bash
python3 scripts/report_gate.py <리포트.md>    # 종료 코드 2 = 토큰 없는 단정문이 있다
```

종료 코드가 2면 어느 줄이 문제인지 나온다. 그 줄을 지어내서 메우지 말고 `## 미확인` 아래로 사유와 함께 옮긴다.

미확인이 하나라도 있으면 검증 단계에서 미리 멈추고 싶다면 `--strict` 를 준다 (종료 코드 1):

```bash
python3 scripts/cite_check.py <문서.md 또는 claims.json> --strict --report --json results.json > report.md
```

**둘 다 사후·수동이고 건너뛸 수 있다.** 훅과 다르다. 사용자에게 요약할 때 게이트를 돌렸는지 아닌지를 밝힌다.

### 2. `${CLAUDE_PLUGIN_ROOT}` 가 없다

공유 스킬 문서의 명령에 그 변수가 나오면 **이 저장소 루트**로 읽는다. 위 예시들처럼 저장소 루트에서 `python3 scripts/...` 로 돌리면 된다.

### 3. `--deep` (L3) 은 `claude` CLI 가 있어야 돈다

L3 판정기는 `scripts/judge_llm.py` 이고 `claude -p` 를 부른다. 그 CLI 가 없으면 **L3 는 돌지 않는다.** 그 주장은 L2 결과 그대로 남고 감사 로그에 `L3 실패` 가 적힌다 — **실패는 통과가 아니다.** 사용자에게 L3 를 못 돌렸다고 말한다.

## 호출

Claude Code 에서는 `/verify`, 여기서는 `$verify`.
