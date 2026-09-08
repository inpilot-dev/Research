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
from cite_check import _KO, UNVERIFIED, _line  # noqa: E402

CONFLICT = {"none": "상충 없음", "conflict": "상충 있음", "single": "단일 출처", None: "상충 미판정"}
STOPPED = {"done": "계획대로 끝남", "hardcap": "반복 한도에 걸려 중단", "budget": "예산이 떨어져 중단"}


def _fields(c):
    """한 주장이 달고 나가야 하는 네 가지."""
    pubs = c.get("publishers") or 1
    conflict = "single" if pubs < 2 and c.get("conflict") in (None, "none") else c.get("conflict")
    return (f"L2" if c["found"] in ("exact", "fuzzy") else "미검증",
            f"퍼블리셔 {pubs}", CONFLICT.get(conflict, CONFLICT[None]))


def synthesize(question, route, claims, meta):
    """→ 종합문 markdown. claims 는 코어가 판정한 결과에 퍼블리셔 수·상충 선언을 얹은 것."""
    ok = [c for c in claims if c["found"] in ("exact", "fuzzy")]
    bad = [c for c in claims if c["found"] in UNVERIFIED]
    # 유형·판단 이유는 주장이 아니라 감사 정보다 — 게이트가 지키는 본문에 섞지 않는다.
    L = [f"# {_line(question)}", "", f"## 확인된 것 ({len(ok)})", ""]
    for c in ok:
        depth, pubs, conflict = _fields(c)
        tag = f"[{c['publisher']}:{c['found']}" + (f" {c['score']}" if c["found"] == "fuzzy" else "") + "]"
        warn = " · ⚠ 인젝션 의심 출처" if c.get("injection_suspect") else ""
        L.append(f"- {tag} {_line(c['claim'])} — {depth} · {pubs} · {conflict} · {_line(c['url'])}{warn}")
    L += ["", f"## 미확인 ({len(bad)})", "",
          "아래는 검증을 통과하지 못했다. 거짓이라는 뜻이 아니라, 단정할 근거가 없다는 뜻이다.", ""]
    for c in bad:
        L.append(f"- {_KO[c['found']]}: {_line(c['claim'])} — {_line(c['url'])}")
    L += ["", "## 감사 로그", "",
          f"- 유형: {_line(route['settings']['label'])} · {_line(route['reason'])}",
          f"- 검증 깊이 기준: {_line(route['settings']['depth'])} · "
          f"독립 퍼블리셔 최소 {route['settings']['min_independent_publishers']} · "
          f"{_line(route['settings']['uncertainty'])}",
          f"- 종료: {STOPPED.get(meta.get('stopped_by'), '알 수 없음')} "
          f"(반복 {meta.get('iterations', 0)}/{meta.get('hardcap', 0)})",
          f"- 반대 근거 탐색 {len(meta.get('refutations') or [])}회"
          + (": " + " · ".join(_line(q) for q in (meta.get("refutations") or [])[:5]) if meta.get("refutations") else ""),
          f"- 읽은 출처 {len({c['url'] for c in claims})}개 · 독립 퍼블리셔 "
          f"{len({c['publisher'] for c in claims if c.get('publisher')})}"]
    if any(c.get("injection_suspect") for c in claims):
        L.append(f"- ⚠ 인젝션 의심 출처 {sum(1 for c in claims if c.get('injection_suspect'))}건 "
                 "— 그 페이지의 지시문은 따르지 않았다. 내용은 데이터로만 썼다")
    return "\n".join(L) + "\n"


_CLAIM_LINE = re.compile(r"^- \[[^\]]+:(?:exact|fuzzy[^\]]*)\] .+ — (L2|미검증) · 퍼블리셔 \d+ · \S+")


def problems(md):
    """종합문이 규칙을 어긴 자리들. 빈 리스트면 내보내도 된다."""
    bad, section = [], ""
    for i, line in enumerate(md.splitlines(), 1):
        head = re.match(r"^\s*#{1,6}\s*(.+?)\s*$", line)
        if head:
            section = head.group(1)
            continue
        if not line.startswith("- "):
            continue
        if "확인된 것" in section and not _CLAIM_LINE.match(line):
            bad.append((i, "네 필드(주장·깊이·퍼블리셔 수·상충)를 갖추지 않은 주장", line.strip()))
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
