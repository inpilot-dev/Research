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
FENCE = re.compile(r"^\s*(```|~~~)")
# 섹션마다 요구하는 것이 다르다. 제목은 **정확히** 일치해야 한다 — 부분 일치로 두면
# "## 미확인 항목에 대한 우리의 결론" 같은 제목 하나로 아무 단정문이나 통과시킬 수 있다.
SECTIONS = ((re.compile(r"^미확인(\s*\(\d+\))?$"), "unverified"),   # 사유 딱지를 단 항목만
            (re.compile(r"^감사 로그$"), "audit"),                     # 기록이지 주장이 아니다
            (re.compile(r"^확인됐으나 기준 미달(\s*\(\d+\))?$"), "thin"))  # 주장 줄엔 토큰이 필요
UNVERIFIED_LABELS = ("근거 없음:", "확인 불가:", "미지원(PDF):")
NOT_A_SENTENCE = re.compile(r"^\s*(\||[-*_=]{3,}|>\s*$|\s*·|```|~~~)")
_WORD = re.compile(r"[A-Za-z가-힣0-9]+")


def offenders(report):
    """규칙을 어긴 줄들 → [(줄번호, 줄), …]. 빈 리스트면 나가도 된다."""
    kind, fenced, bad = "claim", False, []
    for i, line in enumerate(report.splitlines(), 1):
        if FENCE.match(line):
            fenced = not fenced          # 코드 블록 안의 "## 감사 로그" 는 제목이 아니다
            continue
        if fenced:
            continue
        head = SECTION.match(line)
        if head:
            title = head.group(1).strip()
            kind = next((k for pat, k in SECTIONS if pat.match(title)), "claim")
            continue
        if not line.strip() or NOT_A_SENTENCE.match(line):
            continue
        bullet = line.lstrip().startswith("- ")
        if kind == "audit":
            continue
        if kind == "unverified":
            # 사유 없이 적힌 항목은 미확인이 아니라 그냥 단정문이다.
            if bullet and not any(line.lstrip()[2:].startswith(k) for k in UNVERIFIED_LABELS):
                bad.append((i, line.strip()))
            continue
        if kind == "thin" and not bullet:
            continue                     # 섹션 설명문은 주장이 아니다
        if len(_WORD.findall(line)) >= 3 and not TOKEN.search(line):
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
