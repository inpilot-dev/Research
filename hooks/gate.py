#!/usr/bin/env python3
"""PreToolUse 훅 — 검증 토큰 없는 단정문이 파일로 나가는 것을 막는다.

Claude Code 가 stdin 으로 {tool_name, tool_input:{file_path, content | old_string,new_string}} 을
준다. 검증 리포트로 보이는 내용만 판정하고, 나머지 쓰기는 건드리지 않는다.
판정은 scripts/report_gate.py 의 순수 함수가 한다 — 여기서는 프로토콜만 다룬다.
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
from report_gate import explain, looks_like_report, offenders  # noqa: E402


def written_text(payload):
    """이 도구 호출이 끝난 뒤 **파일에 남을** 텍스트.

    Edit 의 조각만 보면 게이트가 통째로 새어 나간다 — 제목 없는 조각에는 `## 검증됨` 이 없으니
    리포트로 보이지 않고, 검증된 리포트에 단정문을 덧붙이는 일이 공짜가 된다. 그래서 대상 파일을
    읽어 편집을 적용한 결과를 판정한다.
    """
    ti = payload.get("tool_input") or {}
    if "content" in ti:
        return ti["content"] or ""
    edits = ti.get("edits") or ([{"old_string": ti.get("old_string", ""),
                                  "new_string": ti.get("new_string", "")}] if "new_string" in ti else [])
    if not edits:
        return ""
    try:
        with open(ti.get("file_path", ""), encoding="utf-8") as f:
            text = f.read()
    except OSError:
        return "\n".join(e.get("new_string", "") for e in edits)   # 새 파일이면 조각만 본다
    for e in edits:
        old, new = e.get("old_string", ""), e.get("new_string", "")
        text = text.replace(old, new, -1 if e.get("replace_all") else 1) if old else text + new
    return text


def main():
    try:
        payload = json.load(sys.stdin)
    except (ValueError, OSError):
        return 0                                   # 훅이 입력을 못 읽었다고 작업을 막지는 않는다
    text = written_text(payload)
    bad = offenders(text) if looks_like_report(text) else []
    if not bad:
        return 0
    json.dump({"hookSpecificOutput": {"hookEventName": "PreToolUse",
                                      "permissionDecision": "deny",
                                      "permissionDecisionReason": explain(bad)}}, sys.stdout)
    print()
    print(explain(bad), file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
