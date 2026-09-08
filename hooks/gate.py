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
    """이 도구 호출이 파일에 남기려는 텍스트."""
    ti = payload.get("tool_input") or {}
    return ti.get("content") or ti.get("new_string") or ""


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
