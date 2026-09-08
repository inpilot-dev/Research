#!/usr/bin/env python3
"""route — 질문이 어떤 종류의 리서치인지 보고 그 종류의 신뢰성 기준을 고른다. LLM 없음.

유형마다 무엇을 믿을 만한 출처로 볼지, 얼마나 깊이 검증할지, 시점을 어떻게 적을지가 다르다.
모르는 유형이면 가장 엄격한 기준으로 처리하고 그렇게 했다고 말한다 — 조용히 느슨해지지 않는다.
세팅은 profiles/types.json 에 데이터로 있다 (ADR 0002).

  python3 scripts/route.py "렘데시비르 임상시험 결과가 뭐야?"
"""
import json
import os
import re
import sys

PROFILES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "profiles", "types.json")
_WORD = re.compile(r"[A-Za-z가-힣0-9]+")


def load(path=PROFILES):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


_ASCII = re.compile(r"[a-z0-9 .\-]+")


def _pattern(signal):
    """낱말 경계로 본다 — 'capital' 안의 'api' 가 기술 문서 신호로 잡히면 안 된다.
    짧은 신호는 앞뒤를 다 막고, 긴 신호는 앞만 막아 어미 변화(randomi→randomized)를 허용한다."""
    s = signal.strip()
    if not _ASCII.fullmatch(s):
        return re.compile(re.escape(s))          # 한국어는 경계 개념이 없어 그대로 본다
    # `\b` 는 한글 앞에서 경계로 치지 않는다 — 파이썬의 \w 가 한글을 포함하기 때문이다.
    # 그래서 "api를" 의 api 를 놓친다. 영숫자만 경계로 보도록 직접 쓴다.
    tail = r"s?(?![A-Za-z0-9])" if len(s) <= 3 else ""
    return re.compile(r"(?<![A-Za-z0-9])" + re.escape(s) + tail)


def _hits(question, signals):
    q = question.lower()
    return sorted({s for s in signals if _pattern(s).search(q)})


def route(question, profiles=None):
    """→ {type, settings, reason, matched}. 혼합이면 가장 엄격한 쪽, 미지원이면 기본값."""
    p = profiles or load()
    types = p["types"]
    matched = {name: h for name, h in ((n, _hits(question, t["signals"])) for n, t in types.items()) if h}
    if not matched:
        name = p["unsupported_default"]
        return {"type": name, "settings": types[name], "matched": {},
                "reason": f"어느 유형에도 걸리지 않아 가장 엄격한 기준({types[name]['label']})으로 처리한다. "
                          f"미지원 유형이므로 결과를 더 보수적으로 읽어야 한다."}
    # 아래로 완화하지 않는다 — 섞였으면 가장 엄격한 쪽을 따른다.
    name = max(matched, key=lambda n: (types[n]["strictness"], len(matched[n])))
    if len(matched) > 1:
        others = ", ".join(f"{types[n]['label']}({'·'.join(matched[n][:3])})" for n in matched if n != name)
        reason = (f"{types[name]['label']} 신호({'·'.join(matched[name][:3])})와 {others} 가 함께 잡혔다. "
                  f"혼합 질문은 가장 엄격한 쪽을 따른다.")
    else:
        reason = f"{types[name]['label']} 신호({'·'.join(matched[name][:3])})가 잡혔다."
    return {"type": name, "settings": types[name], "matched": matched, "reason": reason}


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv:
        print("usage: route.py \"질문\"", file=sys.stderr)
        return 2
    out = route(" ".join(argv))
    json.dump(out, sys.stdout, ensure_ascii=False, indent=2)
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
