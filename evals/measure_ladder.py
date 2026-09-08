#!/usr/bin/env python3
"""measure_ladder — 출처들을 사다리에 태워 "왜 못 읽었나" 분포를 센다.

선택 의존성(칸 3 curl_cffi · 칸 4 playwright)을 깔 값어치가 있는지 짐작 대신 숫자로
정할 때 쓴다. 2026-09-08 실측: 25건 중 읽음 13 · bot-wall 4 · dynamic 3 · robots 2 ·
dead 2 · captcha 1. dynamic 셋 중 리서치에 중요한 ClinicalTrials.gov 는 공개 API
어댑터로 해결돼, 192 MB 짜리 헤드리스 브라우저를 깔지 않기로 했다.

  python3 evals/measure_ladder.py
"""
import collections
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
import access_ladder as al

URLS = [
 # 학술 (정적일 가능성 높음)
 "https://arxiv.org/abs/2103.00020",
 "https://www.biorxiv.org/content/10.1101/2020.03.30.015347v1",
 "https://www.medrxiv.org/content/10.1101/2020.04.16.20067835v1",
 "https://pmc.ncbi.nlm.nih.gov/articles/PMC7262788/",
 "https://www.semanticscholar.org/paper/10.1056/NEJMoa2007764",
 "https://www.researchgate.net/publication/341468040",
 "https://scholar.google.com/scholar?q=remdesivir",
 # 임상·통계 (SPA 의심)
 "https://clinicaltrials.gov/study/NCT04280705",
 "https://data.worldbank.org/indicator/SP.POP.TOTL",
 "https://ourworldindata.org/coronavirus",
 "https://fred.stlouisfed.org/series/GDP",
 "https://ec.europa.eu/eurostat/databrowser/view/tps00001/default/table",
 "https://www.statista.com/statistics/262858/",
 # 기관
 "https://www.cdc.gov/coronavirus/2019-ncov/index.html",
 "https://www.who.int/emergencies/diseases/novel-coronavirus-2019",
 "https://www.fda.gov/news-events/press-announcements",
 # 문서
 "https://react.dev/reference/react/useEffect",
 "https://nextjs.org/docs/app/building-your-application/routing",
 "https://github.com/python/cpython/blob/main/README.rst",
 "https://kubernetes.io/docs/concepts/overview/",
 # 소셜·SPA
 "https://x.com/AnthropicAI",
 "https://www.reddit.com/r/science/",
 "https://www.linkedin.com/company/anthropicresearch/",
 "https://observablehq.com/@d3/gallery",
 "https://www.kaggle.com/datasets",
]

tally, rows = collections.Counter(), []
for u in URLS:
    lad = al.AccessLadder(allow_session={}, budget=25)
    try:
        st, ct, body = lad(u, 12)
    except Exception as e:
        st, body = f"err {type(e).__name__}", ""
    tr = lad.trace.get(u, {})
    reason = tr.get("reason") or "읽음"
    tally[reason] += 1
    rows.append((reason, tr.get("via"), st, len(body or ""), u))
    print(f"{reason:<10} via={str(tr.get('via')):<4} {str(st):<5} {u[:62]}", flush=True)

print("\n=== 사유 분포 ===")
for k, v in tally.most_common():
    print(f"  {k:<12} {v}")
print(f"\n칸 4(playwright)가 도울 수 있는 건: dynamic {tally['dynamic']}건 / 전체 {len(URLS)}건")
