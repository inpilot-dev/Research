#!/usr/bin/env python3
"""prereg — 사전등록한 평가변수와 논문이 보고한 결과를 대조한다. 어댑터 위에 얇게 얹는다.

레지스트리(ClinicalTrials.gov)는 일차·이차 평가변수와 측정 시점을 **구조화 필드**로 갖고 있다.
논문은 그것을 산문으로 적는다. 둘이 다르면(outcome switching) 그 자체가 독자가 알아야 할 사실이다.

**"다르다"를 보고하되 "속였다"고 말하지 않는다.** 바꾼 것이 곧 부정은 아니다 — 논문이 사유를
밝혔을 수도 있고, 프로토콜 개정이 등록에 반영됐을 수도 있다. 이 모듈은 차이만 적는다.

판정은 셋이다.

  일치     — 등록된 평가변수 문구가 논문의 일차 평가변수 문장에서 확인됐다 (L2, --deep 이면 L3)
  다름     — 논문이 일차 평가변수를 밝혔고, 그 문장에 등록된 문구가 없다
  확인 불가 — 레지스트리나 논문 원문을 못 읽었거나, 논문이 무엇을 일차로 봤는지 밝히지 않았다

`근거 없음`과 `확인 불가`를 섞지 않는 규칙(ADR 0002·0003)이 여기서도 그대로다 — 논문 본문을
못 읽었으면 `다름`이 아니라 `확인 불가`다. 어댑터가 깨진 것을 "논문이 바꿔 보고했다"로
바꿔 말하지 않는다.

  python3 scripts/prereg.py NCT04280705 32445440
  python3 scripts/prereg.py 32445440              # 논문에서 NCT 번호를 찾아낸다
  python3 scripts/prereg.py NCT04280705 32445440 --report --deep
"""
import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import adapters as ad  # noqa: E402
import cite_check as cc  # noqa: E402

# 레지스트리 어댑터가 구조화 필드를 어디에 두는지는 sources/*.json 의 이 키에 데이터로 있다 (ADR 0002).
STRUCT = "structured"
NCT = re.compile(r"NCT\d{8}")

# 논문이 "무엇을 일차로 봤는지" 스스로 밝힌 문장. 이 문장이 없으면 대조할 기준이 없다 → 확인 불가.
PRIMARY = re.compile(r"(?i)\bprimary\s+(?:efficacy\s+|clinical\s+|safety\s+|study\s+|composite\s+)?"
                     r"(?:outcome|end\s?point|measure|variable)s?\b")

MATCHED = ("exact", "fuzzy", "entails")


# ── 레지스트리 쪽 ────────────────────────────────────────────────────────────────

def fetch_registry(token, getter=None, timeout=10, adapters=None):
    """NCT 토큰 → (등록 기록, 사유). 못 읽으면 (None, 사유) — 그 사유가 확인 불가의 이유가 된다.

    Registry.fetch 는 대조용 **텍스트**를 돌려주므로 여기서는 못 쓴다. 평가변수는 문자열 목록이
    아니라 객체 목록이고(measure·timeFrame·description), 필요한 것은 그 구조 자체다.
    그래서 같은 어댑터 설정의 endpoint 를 그대로 쓰되 원본 JSON 을 받는다.
    """
    adapter, ident = ad.identify(token, adapters)
    if not adapter or STRUCT not in adapter:
        return None, f"등록 레지스트리 어댑터를 찾지 못했습니다({token})"
    status, _, body = (getter or ad._default_get)(adapter["endpoint"].format(id=ident), timeout)
    if not cc.alive(status):
        return None, f"레지스트리 응답 실패(status={status})"
    try:
        doc = json.loads(body)
    except ValueError:
        return None, "레지스트리 응답이 설정과 다른 모양입니다(JSON 아님)"
    rec = _record(adapter, doc, ident)
    rec["status"], rec["adapter"] = status, adapter["name"]
    return rec, ""


def _record(adapter, doc, ident):
    """설정이 가리키는 자리에서 평가변수·날짜를 꺼낸다. 모양이 다르면 빈 목록으로 남는다."""
    spec = adapter[STRUCT]
    fields = spec.get("outcome_fields") or {}

    def outcomes(path):
        items = ad._dig(doc, path) if path else None
        rows = []
        for it in items if isinstance(items, list) else []:
            if isinstance(it, dict):
                row = {k: re.sub(r"\s+", " ", str(it.get(v) or "")).strip() for k, v in fields.items()}
                if row.get("measure"):
                    rows.append(row)
        return rows

    dates = {k: str(ad._dig(doc, p) or "") for k, p in (spec.get("dates") or {}).items()}
    return {"id": ad._dig(doc, spec.get("id", "")) or ident,
            "title": ad._dig(doc, spec.get("title", "")) or "",
            "primary": outcomes(spec.get("primary_outcomes")),
            "secondary": outcomes(spec.get("secondary_outcomes")),
            "dates": dates,
            "url": adapter["identifier"]["canonical_url"].format(id=ident)}


def _after(a, b):
    """a 가 b 보다 나중인가. 부분 날짜('2020-02')는 **겹치는 자리까지만** 본다.

    '2020-02' 를 '2020-02-01' 로 채워 넣으면 같은 달에 시작한 시험이 사후 등록으로 찍힌다.
    모르는 자리는 모른다고 두고, 애매하면 아니라고 한다 — 없는 사실을 만들지 않는다.
    """
    if not a or not b:
        return False
    n = min(len(a), len(b))
    return a[:n] > b[:n]


def retrospective(dates):
    """사후 등록 — 시험이 시작된 뒤에 등록된 것. → (참/거짓/None, 설명)."""
    reg, start = dates.get("registered", ""), dates.get("start", "")
    if not reg or not start:
        return None, "등록일 또는 시험 시작일이 등록 기록에 없어 판정하지 않습니다"
    if _after(reg, start):
        return True, f"등록일 {reg} 이 시험 시작일 {start} 보다 나중입니다(사후 등록)"
    return False, f"등록일 {reg} · 시험 시작일 {start}"


# ── 논문 쪽 ─────────────────────────────────────────────────────────────────────

def fetch_paper(token, registry=None, timeout=10):
    """논문 토큰(PMID·DOI·URL) → 원문 텍스트. 어댑터가 실패하면 text 가 빈 문자열이다."""
    reg = registry if registry is not None else ad.Registry()
    reg.used = None
    status, _, text = reg.fetch(token, timeout)
    url = ad.canonical_url(token, reg.adapters)
    return {"token": token, "url": url, "publisher": cc.publisher(url), "text": text,
            "status": status, "adapter": reg.used,
            "reason": "" if text else f"논문 원문을 읽지 못했습니다(status={status}, "
                                      f"어댑터={reg.used or '없음'})"}


def primary_statements(text):
    """논문이 일차 평가변수를 밝힌 문장들. 없으면 빈 목록 — 그때는 대조하지 않는다.

    줄바꿈을 먼저 눕힌다. PubMed E-utilities 는 초록을 80칸에서 하드 랩해서 주고,
    `sentences()` 는 줄바꿈을 문장 경계로 본다 — 실측(2026-09-09) ACTT-1 초록의
    "The primary\\noutcome was the time to recovery" 가 두 문장으로 쪼개져 한 건도 안 잡혔다.
    """
    return [s for s in cc.sentences(re.sub(r"\s+", " ", text or "")) if PRIMARY.search(s)]


# ── 대조 ────────────────────────────────────────────────────────────────────────

def _how(kind, score):
    return f"fuzzy {score}" if kind == "fuzzy" else kind


def compare(record, paper, fuzzy=0.85, judge=None):
    """등록 기록 ↔ 논문 → {rows, summary, ...}. 판정은 일치·다름·확인 불가 셋뿐이다.

    ponytail: 등록된 일차 평가변수를 하나씩 독립으로 본다. 그래서 레지스트리가 같은 지표를
    하위집단별로 쪼개 놓았거나(ACTT-1 의 "Time to Recovery by Race/Ethnicity/Sex", 실측)
    플랫폼 시험이 뒤에 다른 코호트의 co-primary 를 더해 두면(RECOVERY, 실측) `다름` 이 여러 건
    나온다. 전부 사실이지만 신호를 묻는다. 묶어 세는 규칙을 넣으려면 "같은 지표인가" 를 판정해야
    하고 그건 L2 가 할 수 있는 일이 아니다 — 필요해지면 `--deep` 의 판정기에게 묶음을 맡긴다.
    """
    rows, l3 = [], {"model": re.sub(r"\s+", " ", str(getattr(judge, "name", "unknown"))).strip(),
                    "ran": 0, "supported": 0, "unsupported": 0, "failed": 0, "errors": []}
    text = (paper or {}).get("text") or ""
    stmts = primary_statements(text)
    target = " ".join(stmts)
    # 확인 불가의 이유는 하나로 뭉뚱그리지 않는다 — 못 읽은 것과 논문이 안 밝힌 것은 다른 사건이다.
    blocked = ""
    if not record:
        blocked = "등록 기록을 읽지 못했습니다"
    elif not record["primary"]:
        blocked = "등록 기록에 일차 평가변수가 없습니다"
    elif not text:
        blocked = (paper or {}).get("reason") or "논문 원문을 읽지 못했습니다"
    elif not stmts:
        blocked = "논문 본문에서 일차 평가변수를 밝힌 문장을 찾지 못했습니다(초록만 읽혔을 수 있습니다)"

    for oc in (record or {}).get("primary", []) or [{"measure": "", "time_frame": ""}]:
        row = {"level": "일차", "measure": oc.get("measure", ""),
               "time_frame": oc.get("time_frame", "")}
        if blocked:
            rows.append({**row, "verdict": "확인 불가", "how": "blocked", "reason": blocked})
            continue
        kind, score = cc.match(row["measure"], target, fuzzy)
        quote = ""
        if kind == "none" and judge is not None:
            l3["ran"] += 1
            claim = f"The paper reports this as a primary outcome: {row['measure']}"
            verdict, q, err = cc._l3_verdict(claim, target, judge)
            if verdict is None:
                l3["failed"] += 1
                l3["errors"].append(err)
                row["l3_error"] = err
            elif verdict:
                l3["supported"] += 1
                kind, quote = "entails", q
            else:
                l3["unsupported"] += 1
        row["how"], row["score"] = _how(kind, score), score
        if quote:
            row["quote"] = quote
        if kind in MATCHED:
            row["verdict"] = "일치"
            # 이름이 같아도 측정 시점이 다르면 다른 평가변수다. 있는 그대로 적고 판단은 하지 않는다.
            row["time_frame_in_paper"] = bool(row["time_frame"]) and \
                cc.match(row["time_frame"], text, fuzzy)[0] in MATCHED
        else:
            row["verdict"] = "다름"
            row["paper_primary"] = stmts[0] if stmts else ""
            row["elsewhere_in_paper"] = cc.match(row["measure"], text, fuzzy)[0] in MATCHED
        rows.append(row)

    promoted = []
    for out in (record or {}).get("secondary", []):
        if not blocked and cc.match(out["measure"], target, fuzzy)[0] in MATCHED:
            promoted.append(out)

    verdicts = [r["verdict"] for r in rows]
    n_primary = len((record or {}).get("primary", []))
    retro, retro_why = retrospective((record or {}).get("dates", {}))
    summary = {"registry": (record or {}).get("id", ""), "paper": (paper or {}).get("url", ""),
               "primary_registered": n_primary,
               "secondary_registered": len((record or {}).get("secondary", [])),
               "일치": verdicts.count("일치"), "다름": verdicts.count("다름"),
               "확인 불가": verdicts.count("확인 불가"),
               "promoted_secondary": len(promoted),
               "retrospective_registration": retro, "registration_dates": retro_why,
               "unmatched_paper_primary": bool(rows) and not blocked and "일치" not in verdicts}
    if l3["ran"]:
        summary["l3"] = l3
    return {"registry": record, "paper": paper, "rows": rows, "promoted_secondary": promoted,
            "paper_primary_statements": stmts, "summary": summary}


# ── 리포트 ──────────────────────────────────────────────────────────────────────

def render(out):
    """→ 마크다운. 검증 토큰을 달고 나가므로 훅 게이트(ADR 0003)를 그대로 통과한다.

    토큰은 장식이 아니다. `일치` 줄의 토큰은 등록 문구를 논문 원문에 댄 L2/L3 판정 그 자체이고,
    `다름` 줄의 `[clinicaltrials.gov:exact]` 는 그 줄이 인용하는 등록 문구가 **실제로 받아온
    레지스트리 기록의 설정된 자리에서 그대로 복사된 것**이라는 뜻이다. 사람이 붙이지 않는다.
    """
    rec, paper, s = out["registry"], out["paper"] or {}, out["summary"]
    pub = paper.get("publisher") or "출처"
    reg_pub = cc.publisher(rec["url"]) if rec else "출처"
    told = [r for r in out["rows"] if r["verdict"] != "확인 불가"]
    bad = [r for r in out["rows"] if r["verdict"] == "확인 불가"]
    title = cc._line(rec["title"]) if rec else ""
    L = ["# 사전등록 ↔ 논문 결과 대조", "", f"## 대조 ({len(told)})", ""]
    for r in told:
        m, tf = cc._line(r["measure"]), cc._line(r["time_frame"])
        if r["verdict"] == "일치":
            L.append(f"- [{pub}:{r['how']}] 일치 · {r['level']} 등록: {m} — 논문의 일차 평가변수 문장에서 확인")
            L.append(f"  · 등록 측정시점: {tf or '없음'}" +
                     ("" if not tf or r.get("time_frame_in_paper") else
                      " — 이 시점 문구는 논문 본문에서 확인되지 않았습니다"))
            if r.get("quote"):
                L.append(f"  · 근거 문장(원문에 있는지 기계가 재확인): {cc._line(r['quote'])}")
        else:
            L.append(f"- [{reg_pub}:exact] 다름 · {r['level']} 등록: {m} — "
                     f"논문의 일차 평가변수 문장에서 이 문구를 찾지 못했습니다")
            L.append(f"  · 등록 측정시점: {tf or '없음'}")
            L.append(f"  · 논문이 일차로 적은 문장: {cc._line(r.get('paper_primary'))}")
            if r.get("elsewhere_in_paper"):
                L.append("  · 이 문구는 논문 본문의 다른 곳에는 나타납니다")
            if r.get("l3_error"):
                L.append(f"  · L3 실패: {cc._line(r['l3_error'])} — L2 결과 그대로 둡니다")
            L.append("  · 다른 것이 곧 부정은 아닙니다 — 논문이 변경 사유를 밝혔는지 함께 보십시오")
    for out2 in out["promoted_secondary"]:
        L.append(f"- [{reg_pub}:exact] 등록 시 이차: {cc._line(out2['measure'])} — "
                 f"논문의 일차 평가변수 문장에 이 문구가 나타납니다")
        L.append(f"  · 등록 측정시점: {cc._line(out2.get('time_frame')) or '없음'}")
    L += ["", f"## 미확인 ({len(bad)})", "",
          "단정하지 않는다. 대조하지 못했다는 뜻이지 다르다는 뜻이 아니다.", ""]
    for r in bad:
        L.append(f"- 확인 불가: {r['level']} 등록: {cc._line(r['measure']) or '(없음)'} — {cc._line(r['reason'])}")
    L += ["", "## 감사 로그", ""]
    if rec:
        L.append(f"- 등록: {rec['id']} · {rec['url']} · 어댑터 {rec.get('adapter')} · status {rec.get('status')}"
                 + (f" · {title}" if title else ""))
    L += [f"- 논문: {cc._line(paper.get('url')) or '없음'} · 어댑터 {paper.get('adapter') or '없음'} · "
          f"status {paper.get('status')} · 읽은 길이 {len(paper.get('text') or '')}자",
          f"- 등록 평가변수: 일차 {s['primary_registered']} · 이차 {s['secondary_registered']} · "
          f"논문이 일차라고 밝힌 문장 {len(out['paper_primary_statements'])}개",
          f"- 판정: 일치 {s['일치']} / 다름 {s['다름']} / 확인 불가 {s['확인 불가']} · "
          f"등록 시 이차였던 항목이 논문 일차 문장에 나타남 {s['promoted_secondary']}건",
          f"- 등록 시점: {cc._line(s['registration_dates'])}"]
    if s["unmatched_paper_primary"]:
        L.append("- 논문의 일차 평가변수 문장에 대응되는 등록 평가변수가 하나도 없습니다 — 추가되었을 수 있습니다")
    if s.get("l3"):
        l3 = s["l3"]
        L.append(f"- L3: {l3['ran']}건 시도 · 뒷받침 {l3['supported']} · 뒷받침 안 됨 {l3['unsupported']} · "
                 f"실패 {l3['failed']} · 모델 {cc._line(l3['model'])}")
    L += ["- 대조 기준: 논문이 스스로 \"primary outcome/end point\" 라고 적은 문장과 등록 문구를 대조한다. "
          "초록만 읽힌 경우 전문에만 있는 서술은 보이지 않는다",
          "- 이 리포트는 차이만 적는다. 다른 것이 곧 부정은 아니며, 사유를 밝힌 변경도 여기서는 '다름'으로 나온다"]
    return "\n".join(L) + "\n"


# ── CLI ─────────────────────────────────────────────────────────────────────────

def run(tokens, fuzzy=0.85, timeout=10, judge=None, getter=None, registry=None):
    """토큰 목록(NCT·PMID·DOI·URL 섞어도 된다) → 대조 결과."""
    nct = next((t for t in tokens if (ad.identify(t, registry.adapters if registry else None)[0] or {})
                .get("name") == "clinicaltrials"), None)
    papers = [t for t in tokens if t != nct]
    paper = fetch_paper(papers[0], registry, timeout) if papers else \
        {"token": "", "url": "", "publisher": "", "text": "", "status": None, "adapter": None,
         "reason": "논문 식별자(PMID·DOI)가 주어지지 않았습니다"}
    # NCT 를 안 줬으면 논문 본문에서 찾는다 — 임상시험 논문은 등록번호를 본문에 적는다.
    if not nct:
        m = NCT.search(paper["text"] or "")
        nct = m.group() if m else None
    record, why = fetch_registry(nct, getter, timeout,
                                 registry.adapters if registry else None) if nct else \
        (None, "NCT 번호를 찾지 못했습니다(인자로 주거나 논문 본문에 있어야 합니다)")
    out = compare(record, paper, fuzzy, judge)
    if not record:
        out["summary"]["registry_error"] = why
    return out


def main(argv=None, judge=None, getter=None, registry=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("tokens", nargs="+", help="NCT 번호와 논문 식별자(PMID·DOI·URL). 순서는 상관없다")
    ap.add_argument("--fuzzy", type=float, default=0.85)
    ap.add_argument("--timeout", type=int, default=15)
    ap.add_argument("--report", action="store_true", help="JSON 대신 마크다운 리포트")
    ap.add_argument("--deep", action="store_true",
                    help="L2 가 못 잡은 평가변수만 L3(의미) 로 다시 본다 — 판정기가 필요하다")
    ap.add_argument("--model", help="L3 판정기 모델")
    a = ap.parse_args(argv)
    if a.deep and judge is None:
        try:  # lazy: 판정기는 코어 밖이다. 없으면 L2 결과 그대로 남는다 (ADR 0001).
            from judge_llm import ClaudeCLI
            judge = ClaudeCLI(model=a.model)
        except Exception as e:
            print(f"[prereg] --deep: L3 판정기를 쓸 수 없습니다 ({e}) — L2 결과 그대로 둡니다.", file=sys.stderr)
    out = run(a.tokens, a.fuzzy, a.timeout, judge, getter, registry)
    if a.report:
        sys.stdout.write(render(out))
    else:
        json.dump(out, sys.stdout, ensure_ascii=False, indent=2)
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
