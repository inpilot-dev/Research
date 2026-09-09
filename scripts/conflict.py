#!/usr/bin/env python3
"""conflict — 검증된 주장들 사이의 모순을 짚는다. 쌍 고르기는 결정론적, 판정만 모델.

지금까지 상충은 리더가 **선언**하는 값이었고, 선언이 없으면 `상충 미판정` 으로 적혔다.
정직했지만 그 결과 **서로 모순인 두 출처가 `확인된 것` 에 나란히 실렸다.** 독자는 둘 다
검증됐다고 읽는다 — 교차확인이 채워질수록 오히려 위험해지는 자리다.

ADR 0001 의 선을 그대로 쓴다.

  결정론  어느 쌍을 볼지 고른다 (낱말 겹침 + 상한). 어떤 모델도 이 선택에 관여하지 않는다.
  모델    그 쌍이 모순인지 본다. 없으면 `상충 미판정` 이다 — 조용히 `상충 없음` 이 되지 않는다.
  결정론  모델이 든 두 문장이 **각자의 출처 원문에** 실제로 있는지 다시 본다. 하나라도
          없으면 판정을 버린다. 지어낸 모순으로 멀쩡한 주장을 끌어내리면 안 된다.

판정기 계약:

    conflict_judge(claim_a, text_a, claim_b, text_b)
        -> {"critique": str, "verdict": "conflict"|"independent"|"same",
            "quote_a": str, "quote_b": str}

`확인 불가` 는 대상이 아니다. 원문을 못 읽었으면 모순인지도 모른다 (ADR 0002).

  python3 scripts/conflict.py          # 자체 점검, 모델 호출 없음
"""
import itertools
import re
import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from cite_check import VERIFIED, L3_MIN_QUOTE, normalize  # noqa: E402

# 두 주장이 같은 것을 말하고 있을 때만 모순일 수 있다. 겹치는 낱말이 이보다 적으면
# 서로 다른 얘기라 모순이 성립하지 않는다 — 모델에게 물어볼 값어치가 없다.
MIN_OVERLAP = 3
# 전수 비교는 O(n²) 이고 그대로 두면 주장 40개에서 780번 모델을 부른다.
# ponytail: 겹침이 큰 쌍부터 상한까지만 본다. 상한 밖의 모순은 놓친다 — 놓치면
# `상충 미판정` 으로 남을 뿐 `상충 없음` 이라고 말하지 않는다.
MAX_PAIRS = 24

_WORD = re.compile(r"[a-z0-9]+|[가-힣]+")
# 어느 문서에나 있는 낱말은 겹쳐도 같은 주제라는 증거가 못 된다.
_STOP = {"the", "and", "for", "with", "that", "this", "was", "were", "have", "has", "from",
         "were", "than", "which", "study", "trial", "patients", "results", "있다", "했다", "된다"}


def _collapsed(c):
    """origins 가 이 주장을 다른 정체성으로 접었나 — 접힌 것끼리는 상충 판정 대상이 아니다."""
    return bool(c.get("origin")) and c["origin"] != (c.get("publisher") or "")


def _keys(text):
    return {w for w in _WORD.findall((text or "").lower()) if len(w) > 2 and w not in _STOP}


def pairs(claims, min_overlap=MIN_OVERLAP, max_pairs=MAX_PAIRS):
    """비교할 쌍을 고른다 → [(i, j)]. 결정론적이고, 같은 입력에 같은 순서를 낸다.

    - 검증된 주장만 본다 (`확인 불가` 는 모순 판정 대상이 아니다)
    - **같은 문서**(같은 URL)끼리는 보지 않는다
    - **하나로 접힌 것끼리도** 보지 않는다. 같은 통신사 기사 둘이 어긋나는 것은 상충이 아니라
      우리 추출이 흔들린 것이다. 단, 호스트가 같다는 것만으로 접지 않는다 — PubMed 는 서로
      다른 시험 수천 건을 얹은 집합소이지 하나의 취재원이 아니다(실측: ACTT-1 과 Solidarity
      가 같은 호스트라는 이유로 비교조차 되지 않았다)
    - 겹치는 낱말이 많은 쌍부터. 동점이면 입력 순서 — 재현되지 않는 판정은 판정이 아니다
    """
    idx = [i for i, c in enumerate(claims) if c.get("found") in VERIFIED]
    scored = []
    for a, b in itertools.combinations(idx, 2):
        ca, cb = claims[a], claims[b]
        if ca["url"] == cb["url"]:
            continue
        if _collapsed(ca) and _collapsed(cb) and ca["origin"] == cb["origin"]:
            continue
        if normalize(ca["claim"]) == normalize(cb["claim"]):
            continue                       # 같은 문장은 교차확인이지 상충이 아니다
        overlap = len(_keys(ca["claim"]) & _keys(cb["claim"]))
        if overlap >= min_overlap:
            scored.append((-overlap, a, b))
    scored.sort()
    return [(a, b) for _, a, b in scored[:max_pairs]]


def _verify(quote, text):
    """모델이 든 문장이 그 출처 원문에 실제로 있나. 이것이 상충 판정을 결정론에 묶는 못이다."""
    q = re.sub(r"\s+", " ", str(quote or "")).strip()
    return len(q) >= L3_MIN_QUOTE and normalize(q) in normalize(text or "")


def find(claims, texts, judge):
    """→ (declarations, log). declarations[i] = "conflict" 인 인덱스만 담긴 dict.

    판정기가 없으면 아무것도 선언하지 않는다 — 호출부는 `상충 미판정` 을 그대로 쓴다.
    """
    log = {"model": re.sub(r"\s+", " ", str(getattr(judge, "name", "unknown"))).strip(),
           "pairs": 0, "conflict": 0, "independent": 0, "same": 0, "failed": 0, "errors": []}
    out = {}
    if judge is None:
        return out, None
    for a, b in pairs(claims):
        log["pairs"] += 1
        ta, tb = texts.get(claims[a]["url"], ""), texts.get(claims[b]["url"], "")
        try:
            v = judge(claims[a]["claim"], ta, claims[b]["claim"], tb)
        except Exception as e:
            log["failed"] += 1
            log["errors"].append(f"호출 실패({type(e).__name__})")
            continue
        verdict = (v or {}).get("verdict") if isinstance(v, dict) else None
        if verdict in ("independent", "same"):
            log[verdict] += 1
            continue
        if verdict != "conflict":
            log["failed"] += 1
            log["errors"].append("응답 형식 오류")
            continue
        if not (_verify(v.get("quote_a"), ta) and _verify(v.get("quote_b"), tb)):
            # 지어낸 모순으로 멀쩡한 주장을 끌어내리지 않는다.
            log["failed"] += 1
            log["errors"].append("근거 문장이 원문에 없음")
            continue
        log["conflict"] += 1
        for i, q in ((a, v["quote_a"]), (b, v["quote_b"])):
            out.setdefault(i, []).append(re.sub(r"\s+", " ", q).strip())
    return out, log


def apply(claims, declarations):
    """선언을 주장에 얹는다. 어느 쪽이 옳은지 고르지 않는다 — **둘 다** 상충으로 표시한다."""
    for i, quotes in declarations.items():
        claims[i]["conflict"] = "conflict"
        claims[i]["conflict_quotes"] = quotes
    return claims


def demo():
    """다섯 경로 중 결정론적인 것들 — 모델 호출 없음."""
    def c(claim, url, pub, found="exact"):
        return {"claim": claim, "url": url, "publisher": pub, "found": found}
    A = "Mortality was 6.7 percent with remdesivir at day 15 in hospitalized adults."
    B = "Mortality with remdesivir at day 15 was 24 percent in hospitalized adults."
    claims = [c(A, "https://a.example/1", "a.example"), c(B, "https://b.example/1", "b.example"),
              c("Unrelated statement about weather patterns.", "https://c.example/1", "c.example"),
              c(A, "https://d.example/1", "d.example", found="blocked")]
    assert pairs(claims) == [(0, 1)], pairs(claims)          # 무관·확인 불가는 쌍에 안 든다

    texts = {"https://a.example/1": A, "https://b.example/1": B}
    forged = lambda *a: {"verdict": "conflict", "quote_a": A, "quote_b": "Never written anywhere."}
    decl, log = find(claims, texts, forged)
    assert decl == {} and log["failed"] == 1, (decl, log)     # 위조는 판정을 못 만든다

    real = lambda *a: {"verdict": "conflict", "quote_a": A, "quote_b": B}
    decl, log = find(claims, texts, real)
    assert sorted(decl) == [0, 1] and log["conflict"] == 1, (decl, log)
    apply(claims, decl)
    assert claims[0]["conflict"] == claims[1]["conflict"] == "conflict"
    assert claims[2].get("conflict") is None                 # 한쪽만 고르지 않고, 무관은 안 건드린다

    assert find(claims, texts, None) == ({}, None)           # 판정기 없음 → 아무 선언 없음
    print("ok")


if __name__ == "__main__":
    demo()
