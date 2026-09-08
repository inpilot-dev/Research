#!/usr/bin/env python3
"""eval_run — 신뢰성이 후퇴했는지 잡는 회귀 평가. LLM 없음, 기본은 네트워크도 없음.

쿼리마다 "이 문장을 이 출처에 대면 이렇게 나와야 한다"를 적어 두고, 코어가 실제로 그렇게
판정하는지 본다. 판정이 달라지면 프롬프트·라우터·어댑터 중 무언가가 신뢰성을 바꾼 것이다.

출처 응답은 evals/fixtures/ 에 녹화해 두고 재생한다 — 평가가 남의 서버 상태에 흔들리면
회귀 평가가 아니다. `--live` 로 다시 받아 녹화한다.

  python3 scripts/eval_run.py                 # 녹화본으로 평가
  python3 scripts/eval_run.py --live --record # 실제로 받아서 다시 녹화
"""
import argparse
import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cite_check as cc  # noqa: E402

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "evals")
FIXTURES = os.path.join(ROOT, "fixtures")


def _slug(url):
    return hashlib.sha1(url.encode()).hexdigest()[:16] + ".json"


def record(url, timeout=20):
    """실제로 한 번 받아서, 대조에 쓰이는 텍스트만 저장한다 (본문 전체는 너무 크다)."""
    from access_ladder import AccessLadder
    lad = AccessLadder(allow_session={}, budget=45)
    status, ctype, body = lad(url, timeout)
    text, published = cc.extract(body) if body else ("", None)
    tr = lad.trace.get(url, {})
    return {"url": url, "status": status, "ctype": ctype, "text": text, "published": published,
            "via": tr.get("via"), "reason": tr.get("reason")}


def replay(directory=FIXTURES):
    """녹화본을 코어의 fetcher 계약으로 되돌린다. 텍스트는 그대로 통과한다."""
    store = {}
    for fn in os.listdir(directory):
        if fn.endswith(".json"):
            with open(os.path.join(directory, fn), encoding="utf-8") as f:
                d = json.load(f)
            store[d["url"]] = d

    def fetcher(url, timeout=10):
        d = store.get(url)
        if d is None:
            return None, "", ""
        return d["status"], d["ctype"], d["text"]
    fetcher.store = store
    return fetcher


def run(queries, fetcher):
    """→ (rows, per-type tallies). 각 행은 한 주장의 기대와 실제."""
    rows = []
    for q in queries:
        for c in q["claims"]:
            out = cc.check([{"claim": c["claim"], "url": c["url"]}], fetcher=fetcher)
            got = out["results"][0]["found"]
            rows.append({"type": q["type"], "id": q["id"], "question": q["question"],
                         "url": c["url"], "expect": c["expect"], "got": got,
                         "ok": got == c["expect"], "why": c.get("why", "")})
    tally = {}
    for r in rows:
        t = tally.setdefault(r["type"], {"pass": 0, "total": 0})
        t["total"] += 1
        t["pass"] += bool(r["ok"])
    return rows, tally


def report(rows, tally):
    L = ["# 회귀 평가 — 유형별 통과율", "",
         "판정은 결정론적 코어가 한다. 아래 숫자는 **자기보고**다 — 우리가 만든 기대값을 우리가",
         "채점한 것이고, 사람이 검수한 결과가 아니다. 검수 절차는 `evals/HUMAN-REVIEW.md`.", "",
         "| 유형 | 통과 | 전체 | 통과율 |", "|---|---|---|---|"]
    for t in sorted(tally):
        v = tally[t]
        L.append(f"| {t} | {v['pass']} | {v['total']} | {100 * v['pass'] // max(v['total'], 1)}% |")
    tot_p, tot_n = sum(v["pass"] for v in tally.values()), sum(v["total"] for v in tally.values())
    L.append(f"| **합계** | **{tot_p}** | **{tot_n}** | **{100 * tot_p // max(tot_n, 1)}%** |")
    bad = [r for r in rows if not r["ok"]]
    L += ["", f"## 실패 ({len(bad)})", ""]
    L += [f"- `{r['id']}` 기대 `{r['expect']}` → 실제 `{r['got']}` · {r['url']}\n  · {r['why']}"
          for r in bad] or ["없음."]
    return "\n".join(L) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--live", action="store_true", help="녹화본 대신 실제로 받아온다")
    ap.add_argument("--record", action="store_true", help="받아온 응답을 녹화본으로 저장한다")
    ap.add_argument("--queries", default=os.path.join(ROOT, "queries.json"))
    a = ap.parse_args(argv)
    with open(a.queries, encoding="utf-8") as f:
        queries = json.load(f)
    urls = sorted({c["url"] for q in queries for c in q["claims"]})
    if a.live:
        os.makedirs(FIXTURES, exist_ok=True)
        for u in urls:
            d = record(u)
            print(f"녹화 {d['status']} via={d['via']} len={len(d['text']):>6}  {u}", file=sys.stderr)
            if a.record:
                with open(os.path.join(FIXTURES, _slug(u)), "w", encoding="utf-8") as f:
                    json.dump(d, f, ensure_ascii=False, indent=2)
    fetcher = replay()
    missing = [u for u in urls if u not in fetcher.store]
    if missing:
        print("녹화본 없음: " + "\n  ".join(missing), file=sys.stderr)
    rows, tally = run(queries, fetcher)
    sys.stdout.write(report(rows, tally))
    return 1 if any(not r["ok"] for r in rows) else 0


if __name__ == "__main__":
    sys.exit(main())
