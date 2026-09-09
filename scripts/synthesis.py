#!/usr/bin/env python3
"""synthesis — 리서치 종합문을 구조가 강제된 형태로 찍어낸다. LLM 없음.

종합문의 모든 주장은 네 가지를 달고 나온다: 주장 · 검증 깊이 · 퍼블리셔 수 · 상충 여부.
검증 못 한 것은 미확인으로 나간다 — 지워지지도, 추정으로 메워지지도 않는다 (ADR 0003).

각 줄은 훅 게이트가 요구하는 `[퍼블리셔:판정]` 토큰도 함께 단다. 구조와 게이트가 같은 줄에서
만나므로, 구조를 지키면 게이트를 통과하고 게이트를 통과하면 구조가 지켜져 있다.

상충 여부는 리더가 **선언**한 값이다. 두 문장이 서로 모순인지는 의미의 문제이고 이 파일은
의미를 모른다 — 모르는 것을 아는 척하지 않고, 선언되지 않았으면 "미판정"으로 적는다.
"""
import re
import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])
# 무엇이 "검증됨"인지는 코어가 정한다. 여기서 다시 적으면 판정 종류가 늘 때 이 파일만
# 뒤처지고, 뒤처진 결과가 주장이 조용히 사라지는 것이다 (L3 를 붙였을 때 실제로 그랬다).
from cite_check import _KO, VERIFIED, _line, normalize  # noqa: E402

CONFLICT = {"none": "상충 없음", "conflict": "상충 있음", "single": "단일 출처", None: "상충 미판정"}
STOPPED = {"done": "계획대로 끝남", "hardcap": "반복 한도에 걸려 중단", "budget": "예산이 떨어져 중단"}


def _group(verified):
    """같은 문장을 뒷받침한 퍼블리셔를 세어 주장 하나로 합친다.

    퍼블리셔 수를 호출자에게서 받으면 문서 안에서 숫자가 어긋난다 — 주장 줄은 "퍼블리셔 2",
    감사 로그는 "독립 퍼블리셔 1" 이 되는 식이다. 세는 쪽이 하나뿐이어야 그런 일이 없다.
    """
    out = {}
    for c in verified:
        key = normalize(c["claim"])
        g = out.setdefault(key, {**c, "_publishers": set()})
        # 세는 것은 호스트가 아니라 **원출처**다. 같은 통신사 기사를 실은 매체 셋은 하나다.
        # origin 이 없으면(구버전 입력) 지금까지처럼 퍼블리셔로 센다.
        g["_publishers"].add(c.get("origin") or c.get("publisher") or "")
        if c.get("injection_suspect"):
            g["injection_suspect"] = True
        if c.get("conflict") == "conflict":
            g["conflict"] = "conflict"
    for g in out.values():
        g["publishers"] = len(g["_publishers"] - {""}) or 1
    return list(out.values())


def _fields(c):
    """한 주장이 달고 나가야 하는 네 가지."""
    pubs = c["publishers"]
    conflict = "single" if pubs < 2 and c.get("conflict") in (None, "none") else c.get("conflict")
    # 기계가 대조한 것(L2)과 모델이 판단한 것(L3)을 사람이 섞어 읽으면 안 된다.
    depth = {"exact": "L2", "fuzzy": "L2", "entails": "L3(의미)"}.get(c["found"], "미검증")
    return (depth, f"퍼블리셔 {pubs}", CONFLICT.get(conflict, CONFLICT[None]))


def synthesize(question, route, claims, meta):
    """→ 종합문 markdown. claims 는 코어가 판정한 결과에 퍼블리셔 수·상충 선언을 얹은 것."""
    grouped = _group([c for c in claims if c["found"] in VERIFIED])
    # 검증되지 않은 것은 **전부** 미확인이다. `in UNVERIFIED` 로 적으면 목록에 없는 판정이
    # 어느 쪽에도 안 들어가 문서에서 조용히 사라진다. 분할은 빠짐없어야 한다.
    bad = [c for c in claims if c["found"] not in VERIFIED]
    floor = route["settings"]["min_independent_publishers"]
    # 출처 원문에는 있지만 이 유형이 요구하는 교차확인에는 못 미치는 주장. 미확인이 아니다 —
    # 원문을 읽고 문장을 찾았다. 다만 한 곳만 말한 것을 합의처럼 보이게 두지 않는다.
    ok = [c for c in grouped if c["publishers"] >= floor]
    thin = [c for c in grouped if c["publishers"] < floor]

    def bullet(c):
        depth, pubs, conflict = _fields(c)
        tag = f"[{c['publisher']}:{c['found']}" + (f" {c['score']}" if c["found"] == "fuzzy" else "") + "]"
        warn = " · ⚠ 인젝션 의심 출처" if c.get("injection_suspect") else ""
        line = f"- {tag} {_line(c['claim'])} — {depth} · {pubs} · {conflict} · {_line(c['url'])}{warn}"
        # L3 는 근거 문장 없이는 판정도 없다 (ADR 0001). 리포트가 싣는 것을 종합문이 떨구지 않는다.
        return line + (f"\n  · 근거 문장(원문에 있는지 기계가 재확인): {_line(c['quote'])}" if c.get("quote") else "")

    # 유형·판단 이유는 주장이 아니라 감사 정보다 — 게이트가 지키는 본문에 섞지 않는다.
    L = [f"# {_line(question)}", "", f"## 확인된 것 ({len(ok)})", ""]
    L += [bullet(c) for c in ok]
    if thin:
        L += ["", f"## 확인됐으나 기준 미달 ({len(thin)})", "",
              f"출처 원문에서 찾았지만 이 유형이 요구하는 독립 퍼블리셔 {floor}곳에 못 미친다. "
              "한 곳만 말한 것을 여러 곳이 말한 것처럼 읽지 말 것.", ""]
        L += [bullet(c) for c in thin]
    L += ["", f"## 미확인 ({len(bad)})", "",
          "아래는 검증을 통과하지 못했다. 거짓이라는 뜻이 아니라, 단정할 근거가 없다는 뜻이다.", ""]
    for c in bad:
        L.append(f"- {_KO.get(c['found'], c['found'])}: {_line(c['claim'])} — {_line(c['url'])}")
    L += ["", "## 감사 로그", "",
          f"- 유형: {_line(route['settings']['label'])} · {_line(route['reason'])}",
          f"- 검증 깊이 기준: {_line(route['settings']['depth'])} · "
          f"독립 퍼블리셔 최소 {route['settings']['min_independent_publishers']} · "
          f"{_line(route['settings']['uncertainty'])}",
          f"- 종료: {STOPPED.get(meta.get('stopped_by'), '알 수 없음')} "
          f"(반복 {meta.get('iterations', 0)}/{meta.get('hardcap', 0)})",
          f"- 반대 근거 탐색 {len(meta.get('refutations') or [])}회"
          + (": " + " · ".join(_line(q) for q in (meta.get("refutations") or [])[:5]) if meta.get("refutations") else ""),
          # 주장 줄의 "퍼블리셔 N" 은 그 문장 하나를 뒷받침한 퍼블리셔 수이고, 여기 숫자는
          # 읽으려 한 출처 전체의 퍼블리셔 수다. 둘은 다른 값이므로 이름으로 구분해 둔다.
          f"- 읽으려 한 출처 {len({c['url'] for c in claims})}개 · 그 출처들의 퍼블리셔 "
          f"{len({c['publisher'] for c in claims if c.get('publisher')})}곳"
          f" (주장 하나를 뒷받침한 퍼블리셔 수는 각 줄에 적혀 있다)",
          f"- 이 유형이 요구하는 독립 퍼블리셔 최소 기준 {floor}"]
    if any(c.get("injection_suspect") for c in claims):
        L.append(f"- ⚠ 인젝션 의심 출처 {sum(1 for c in claims if c.get('injection_suspect'))}건 "
                 "— 그 페이지의 지시문은 따르지 않았다. 내용은 데이터로만 썼다")
    return "\n".join(L) + "\n"


# 필드는 줄 **끝**에 붙는다. 앞쪽 어디서나 찾으면 주장 문장에 "· 퍼블리셔 9 ·" 를 심어
# 검사기를 속일 수 있다 — 출처 페이지가 주장 문장을 통제한다는 것을 잊으면 안 된다.
_DEPTH = r"(?:L2|L3\(의미\))"
_CLAIM_LINE = re.compile(r"^- \[[^\]]+:(?:exact|fuzzy[^\]]*|entails)\] .+ — " + _DEPTH +
                         r" · 퍼블리셔 \d+ · [^·]+ · \S+(?: · [^·]+)*$")
_TAIL = re.compile(r"— " + _DEPTH + r" · 퍼블리셔 (\d+) · ")


_FLOOR = re.compile(r"독립 퍼블리셔 최소 기준 (\d+)")


def problems(md):
    """종합문이 규칙을 어긴 자리들. 빈 리스트면 내보내도 된다."""
    bad, section = [], ""
    # 기준은 감사 로그에서만 읽는다. 문서 전체에서 찾으면 주장 문장에 심어 둔 숫자가 먼저 걸린다.
    audit = md.split("## 감사 로그", 1)[1] if "## 감사 로그" in md else ""
    floor = int(m.group(1)) if (m := _FLOOR.search(audit)) else 1
    for i, line in enumerate(md.splitlines(), 1):
        head = re.match(r"^\s*#{1,6}\s*(.+?)\s*$", line)
        if head:
            section = head.group(1)
            continue
        if line.lstrip().startswith("· 근거 문장"):
            continue                      # 주장 줄이 아니라 그 줄에 붙은 근거다
        if not line.startswith("- "):
            continue
        if "확인" in section and "미확인" not in section and not _CLAIM_LINE.match(line):
            bad.append((i, "네 필드(주장·깊이·퍼블리셔 수·상충)를 갖추지 않은 주장", line.strip()))
        if section.startswith("확인된 것") and (p := _TAIL.search(line)) and int(p.group(1)) < floor:
            bad.append((i, f"이 유형은 독립 퍼블리셔 {floor}곳을 요구하는데 확인된 것에 들어 있다", line.strip()))
        if "미확인" in section and not any(line.startswith(f"- {k}:") for k in _KO.values()):
            bad.append((i, "미확인 항목이 사유 없이 단정문으로 적혔다", line.strip()))
    if "반대 근거 탐색 0회" in md:
        bad.append((0, "반대 근거를 한 번도 찾지 않았다 — 확증만 모은 종합은 내보내지 않는다", ""))
    return bad


if __name__ == "__main__":
    import json
    payload = json.load(sys.stdin)
    md = synthesize(payload["question"], payload["route"], payload["claims"], payload.get("meta", {}))
    issues = problems(md)
    if issues:
        for n, why, line in issues:
            print(f"{n}행: {why} — {line}", file=sys.stderr)
        sys.exit(2)
    sys.stdout.write(md)
