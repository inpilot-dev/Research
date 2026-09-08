#!/usr/bin/env python3
"""demo_end_to_end — 유형 하나당 질문 하나로 파이프라인 전체를 실물 출처에 태운다.

라우터 → 접근 사다리 → 코어 → 종합 → 훅 게이트. 원문에서 뽑은 문장은 exact 가,
지어낸 문장은 근거 없음이 나와야 하고, 종합문은 구조 위반 0 으로 게이트를 통과해야 한다.
네트워크를 쓴다 — 오프라인 회귀는 eval_run.py 쪽이다 (#7 수용 기준의 실행본).

  python3 evals/demo_end_to_end.py
"""
import json
import subprocess
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
import access_ladder as al, cite_check as cc, report_gate as g, route as rt, synthesis as sy

CASES = [
    ("렘데시비르 무작위 시험의 일차 평가변수가 뭐였어?",
     "https://pubmed.ncbi.nlm.nih.gov/32445440/",
     ["remdesivir no benefit", "remdesivir trial criticism"]),
    ("How do I use difflib SequenceMatcher in the Python standard library?",
     "https://docs.python.org/3/library/difflib.html",
     ["difflib SequenceMatcher wrong results", "difflib ratio limitations"]),
    ("When was the World Health Organization founded?",
     "https://www.who.int/about",
     ["WHO founding date disputed", "WHO established year correction"]),
]

for question, url, refutations in CASES:
    route = rt.route(question)
    lad = al.AccessLadder(allow_session={}, budget=45)
    status, ctype, body = lad(url, 15)
    text, published = cc.extract(body)
    sents = [s for s in cc.sentences(text) if 60 < len(s) < 220]
    real = sents[0] if sents else "(원문에서 문장을 못 뽑음)"
    claims = [{"claim": real, "url": url},
              {"claim": "This sentence was invented and appears in no source anywhere.", "url": url}]
    out = cc.check(claims, fetcher=lad)
    enriched = []
    for r in out["results"]:
        tr = r.get("trace") or {}
        enriched.append({**r, "publishers": 1, "conflict": "none",
                         "injection_suspect": tr.get("injection_suspect", False)})
    md = sy.synthesize(question, route, enriched,
                       {"stopped_by": "done", "iterations": 3, "hardcap": 3, "refutations": refutations})
    struct = sy.problems(md)
    gate = subprocess.run([sys.executable, "hooks/gate.py"],
                          input=json.dumps({"tool_name": "Write",
                                            "tool_input": {"file_path": "/tmp/s.md", "content": md}}),
                          capture_output=True, text=True)
    print(f"{route['type']:22} via={(out['results'][0].get('trace') or {}).get('via')} "
          f"판정={[r['found'] for r in out['results']]} 구조위반={len(struct)} "
          f"게이트={'통과' if gate.returncode == 0 else '차단'}")
    print(f"   원문 문장: {real[:88]}")
