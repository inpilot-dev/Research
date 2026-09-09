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

# entails 는 L3(모델 판정)다. 게이트는 "검증을 거쳤는가"만 본다 — 어느 층이었는지는
# 리포트가 줄마다 따로 적는다.
TOKEN = re.compile(r"\[[A-Za-z0-9.\-]+:(?:exact|fuzzy(?:\s+[0-9.]+)?|entails)\]")
SECTION = re.compile(r"^\s*#{1,6}\s*(.+?)\s*$")
FENCE = re.compile(r"^\s*(`{3,}|~{3,})\s*")
# 섹션마다 요구하는 것이 다르다. 제목은 **정확히** 일치해야 한다 — 부분 일치로 두면
# "## 미확인 항목에 대한 우리의 결론" 같은 제목 하나로 아무 단정문이나 통과시킬 수 있다.
SECTIONS = ((re.compile(r"^미확인(\s*\(\d+\))?$"), "unverified"),   # 사유 딱지를 단 항목만
            (re.compile(r"^감사 로그$"), "audit"),                     # 기록이지 주장이 아니다
            (re.compile(r"^확인됐으나 기준 미달(\s*\(\d+\))?$"), "thin"),   # 주장 줄엔 토큰이 필요
            # 상충 섹션도 같다 — 섹션 설명문은 주장이 아니고, 주장 줄은 여전히 토큰을 단다.
            (re.compile(r"^상충(\s*\(\d+\))?$"), "thin"))
UNVERIFIED_LABELS = ("근거 없음:", "확인 불가:", "미지원(PDF):")
NOT_A_SENTENCE = re.compile(r"^\s*(\||[-*_=]{3,}|>\s*$|\s*·|```|~~~)")
_WORD = re.compile(r"[A-Za-z가-힣0-9]+")


def prose_lines(text):
    """코드 블록 밖의 줄만 → [(줄번호, 줄), …].

    펜스 규칙은 **여기 한 곳에만** 있다. 예전에는 `offenders()` 만 펜스를 건너뛰고
    `looks_like_report()` 는 문자열 포함 검사였다 — 그래서 README 의 예시 출력 안에 있는
    `## 검증됨` 이 리포트 제목으로 읽혀, 리포트가 아닌 문서가 게이트에 걸렸다.

    닫는 펜스는 **여는 펜스와 같은 문자에 길이가 같거나 더 긴 것**만 인정한다. 그래야
    ```` 안에 든 ``` 이 블록을 조기에 닫지 않는다.
    """
    out, marker = [], None
    for i, line in enumerate(text.splitlines(), 1):
        m = FENCE.match(line)
        if m:
            f = m.group(1)
            if marker is None:
                marker, opened = f, i
                continue
            if f[0] == marker[0] and len(f) >= len(marker):
                marker = None
                continue                 # 짧은 안쪽 펜스는 닫지 못하고 그냥 블록 내용이다
        if marker is None:
            out.append((i, line))
    if marker is not None:
        # 펜스가 닫히지 않았다. 무엇이 코드고 무엇이 산문인지 알 수 없다 — 애매하면 막는 쪽으로
        # 간다(ADR 0003). 열린 펜스를 없는 것으로 보고 전부 산문으로 취급한다.
        return [(i, ln) for i, ln in enumerate(text.splitlines(), 1) if i != opened]
    return out


def offenders(report):
    """규칙을 어긴 줄들 → [(줄번호, 줄), …]. 빈 리스트면 나가도 된다."""
    kind, bad = "claim", []
    for i, line in prose_lines(report):
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
    """이 게이트가 관여할 문서인가 — 검증 리포트라고 스스로 말하는 것만 본다.

    두 가지를 요구한다. 코드 블록 **밖**일 것 — 블록 안의 제목은 예시이지 이 문서의 제목이
    아니다(README). 그리고 제목이 **줄 맨 앞**일 것 — 표 칸 안의 `## 미확인` 은 그 말을
    인용한 것이지 섹션을 여는 것이 아니다(SKILL.md). 실제 리포트는 `render()` 가 항상 줄
    맨 앞에 찍는다.

    관여 여부만 정확해질 뿐, 관여하기로 한 문서의 판정은 조금도 달라지지 않는다 (ADR 0003).
    """
    return any((m := SECTION.match(ln)) and m.group(1).strip().startswith(("검증됨", "미확인"))
               for _, ln in prose_lines(text))


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
