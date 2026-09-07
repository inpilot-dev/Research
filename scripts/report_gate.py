#!/usr/bin/env python3
"""report_gate — 검증 토큰 없는 단정문이 리포트로 나가는 것을 막는 순수 함수.

스킬 텍스트는 모델이 무시할 수 있다. 훅은 못 무시한다 — 그게 이 게이트가 있는 이유다(ADR 0003).
그래서 끄는 스위치를 두지 않는다. 플래그도, 환경변수도, "빠른 모드"도 없다.

통과 규칙
  `## 미확인` · `## 감사 로그` 안의 줄은 그냥 통과한다. 거기 있는 문장은 단정이 아니라 표기다.
  그 밖의 모든 줄은 `[퍼블리셔:판정]` 토큰을 달고 있어야 한다. 제목·빈 줄·표·구분선은 문장이 아니다.
"""
import re
import sys

TOKEN = re.compile(r"\[[A-Za-z0-9.\-]+:(?:exact|fuzzy(?:\s+[0-9.]+)?)\]")
SECTION = re.compile(r"^\s*#{1,6}\s*(.+?)\s*$")
FREE = ("미확인", "감사 로그")          # 이 섹션 안은 단정이 아니다
NOT_A_SENTENCE = re.compile(r"^\s*(\||[-*_=]{3,}|>\s*$|\s*·|```|~~~)")
_WORD = re.compile(r"[A-Za-z가-힣0-9]+")


def offenders(report):
    """토큰 없이 단정한 줄들 → [(줄번호, 줄), …]. 빈 리스트면 나가도 된다."""
    free, bad = False, []
    for i, line in enumerate(report.splitlines(), 1):
        head = SECTION.match(line)
        if head:
            free = any(k in head.group(1) for k in FREE)
            continue
        if free or not line.strip() or NOT_A_SENTENCE.match(line):
            continue
        if len(_WORD.findall(line)) >= 4 and not TOKEN.search(line):
            bad.append((i, line.strip()))
    return bad


def looks_like_report(text):
    """이 게이트가 관여할 문서인가 — 검증 리포트라고 스스로 말하는 것만 본다."""
    return "## 검증됨" in text or "## 미확인" in text


def explain(bad):
    lines = "\n".join(f"  {n}행: {t[:110]}" for n, t in bad[:8])
    more = f"\n  … 외 {len(bad) - 8}건" if len(bad) > 8 else ""
    return ("검증 토큰이 없는 단정문이 있어 쓰기를 막았습니다 (ADR 0003).\n" + lines + more +
            "\n\n검증된 주장에는 `[퍼블리셔:exact]` 또는 `[퍼블리셔:fuzzy 0.93]` 토큰이 붙어야 하고,\n"
            "검증하지 못한 것은 `## 미확인` 아래에 사유와 함께 두어야 합니다. 지어내서 메우지 마십시오.")


if __name__ == "__main__":
    text = open(sys.argv[1], encoding="utf-8").read() if len(sys.argv) > 1 else sys.stdin.read()
    bad = offenders(text) if looks_like_report(text) else []
    if bad:
        print(explain(bad), file=sys.stderr)
    sys.exit(2 if bad else 0)
