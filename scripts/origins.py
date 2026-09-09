#!/usr/bin/env python3
"""origins — 여러 출처가 실은 하나의 원출처로 수렴하는지 본다. 결정론적, 표준 라이브러리만.

`독립 퍼블리셔` 는 지금까지 `www.` 를 뗀 호스트 수였다. 같은 통신사 기사를 실은 서로 다른
매체 셋이 **독립 출처 셋**으로 세어졌고, 그러면 교차확인 기준이 실제보다 후하게 채워진다.
한 곳이 한 말을 세 곳이 한 말처럼 보이게 하는 것은 이 도구가 막으려는 바로 그 실패다.

완전한 원출처 추적은 여기 범위가 아니다. **눈에 보이는 신호 네 가지**만 결정론적으로 본다.

| 신호 | 무엇을 보나 | 왜 믿을 만한가 |
|---|---|---|
| `wire` | 본문 앞부분의 통신사 크레딧 문구 | 매체가 스스로 "이건 우리 취재가 아니다"라고 적은 것이다 |
| `canonical` | `rel=canonical` 이 **다른 호스트**를 가리킴 | 그 페이지가 스스로 원본이 저기라고 선언한 것이다 |
| `owner` | 같은 소유주의 도메인 묶음 | 한 회사가 굴리는 두 매체는 독립적이지 않다 |
| `duplicate` | 긴 문단이 두 퍼블리셔에 **글자 그대로** 반복 | 크레딧 없이 그대로 실은 재배포. 우연히 일치할 길이가 아니다 |

**애매하면 줄이는 쪽으로 간다.** 부풀리는 실수(한 곳을 셋으로)가 줄이는 실수(셋을 하나로)보다
나쁘다 — 앞은 없는 합의를 만들어 내고, 뒤는 있는 합의를 못 보고 넘어가는 것뿐이다.

데이터는 `profiles/publishers.json` 이다. 새 통신사·새 소유주는 그 파일에 줄을 더한다 (ADR 0002).

  python3 scripts/origins.py            # 데이터 파일 자체 점검
"""
import hashlib
import json
import os
import re

# `sources/` 가 아니라 `profiles/` 다 — `sources/*.json` 은 어댑터 레지스트리가 glob 으로
# 읽는 곳이고, 어댑터가 아닌 파일을 거기 두면 레지스트리가 깨진다.
DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "profiles", "publishers.json")
# 크레딧은 기사 머리나 서명 줄에 붙는다. 끝까지 훑으면 '관련 기사' 목록의 매체명에 걸린다.
CREDIT_WINDOW = 1200
# 우연히 같을 수 없는 길이. 짧게 잡으면 상투적인 한 문장("코로나19가 확산되고 있다")이
# 서로 다른 취재를 하나로 접어 버린다 — 그쪽이 이 기능의 유일한 위험이다.
DUP_MIN_CHARS = 240


def load(path=DATA):
    with open(path, encoding="utf-8") as f:
        d = json.load(f)
    owners = {host: group for group, hosts in d["owners"].items()
              if not group.startswith("_") for host in hosts}
    wire = {w: [p.lower() for p in pats] for w, pats in d["wire"].items() if not w.startswith("_")}
    return owners, wire


def _host(url):
    m = re.match(r"^\w+://([^/?#]+)", url or "")
    if not m:
        return ""
    h = m.group(1).rsplit("@", 1)[-1].split(":")[0].lower()
    return h[4:] if h.startswith("www.") else h


def paragraph_prints(text, min_chars=DUP_MIN_CHARS):
    """본문에서 '우연히 같을 리 없는' 긴 조각들의 지문. 재배포 탐지에만 쓴다.

    문단 단위로 자르되 공백을 정규화한다 — 매체마다 줄바꿈과 들여쓰기는 다르지만
    통신사 기사를 그대로 실으면 문장은 글자 그대로 같다.
    """
    out = set()
    for para in re.split(r"\n\s*\n|(?<=[.!?])\s{2,}", text or ""):
        p = re.sub(r"\s+", " ", para).strip()
        if len(p) >= min_chars:
            out.add(hashlib.sha1(p.lower().encode("utf-8")).hexdigest()[:16])
    return out


def wire_credit(text, wire):
    """본문 앞부분에 통신사 크레딧이 있나 → 통신사 이름 또는 None."""
    head = re.sub(r"\s+", " ", (text or "")[:CREDIT_WINDOW]).lower()
    for name, patterns in sorted(wire.items()):
        if any(p in head for p in patterns):
            return name
    return None


def identify(rows, owners=None, wire=None):
    """각 행에 원출처 정체성을 붙인다. rows 는 {publisher, url, text, canonical} 을 가진 dict 들.

    → [(identity, reason)] — 행과 같은 순서. reason 이 빈 문자열이면 퍼블리셔 그대로 센 것이다.

    우선순위는 **선언이 추론보다 앞선다**: 페이지가 스스로 밝힌 것(크레딧·canonical)을 먼저
    믿고, 우리가 미루어 짐작하는 것(소유주 묶음·문단 중복)은 그다음이다.
    """
    if owners is None or wire is None:
        o, w = load()
        owners, wire = (o if owners is None else owners), (w if wire is None else wire)
    out = [None] * len(rows)

    # 3순위(문단 중복)는 행들 사이를 봐야 하므로 지문을 먼저 모은다.
    seen = {}
    for i, r in enumerate(rows):
        for fp in paragraph_prints(r.get("text")):
            seen.setdefault(fp, []).append(i)
    dup_owner = {}
    for fp, idxs in seen.items():
        pubs = {rows[i].get("publisher") for i in idxs}
        if len(pubs) < 2:
            continue                       # 같은 매체 안의 반복은 재배포가 아니다
        first = min(idxs)                  # 누가 원본인지는 모른다 — 하나로 접기만 한다
        for i in idxs:
            dup_owner.setdefault(i, f"dup:{rows[first].get('publisher') or fp}")

    for i, r in enumerate(rows):
        pub = r.get("publisher") or ""
        if w := wire_credit(r.get("text"), wire):
            out[i] = (f"wire:{w}", f"본문에 {w} 크레딧 — 자기 취재가 아니라 통신사 기사")
            continue
        canon = _host(r.get("canonical"))
        if canon and pub and canon != pub:
            out[i] = (canon, f"rel=canonical 이 {canon} 을 가리킴 — 원본이 그쪽이라고 스스로 밝혔다")
            continue
        if group := owners.get(pub):
            out[i] = (f"owner:{group}", f"{pub} 는 {group} 소유 — 같은 회사의 매체는 독립 출처가 아니다")
            continue
        if i in dup_owner:
            out[i] = (dup_owner[i], "다른 퍼블리셔와 긴 문단이 글자 그대로 같음 — 재배포로 본다")
            continue
        out[i] = (pub, "")
    return out


def demo():
    owners, wire = load()
    assert owners["wsj.com"] == "news-corp" and owners["nypost.com"] == "news-corp"
    assert wire_credit("SEOUL (Reuters) - The trial enrolled 1062 patients.", wire) == "reuters"
    assert wire_credit("본문 " * 400 + "(Reuters)", wire) is None      # 꼬리의 크레딧은 안 본다

    body = "통신사 기사 본문이 그대로 실렸다. " * 16   # DUP_MIN_CHARS 를 넘겨야 지문이 생긴다
    rows = [{"publisher": "a.com", "url": "https://a.com/1", "text": body},
            {"publisher": "b.com", "url": "https://b.com/1", "text": body},
            {"publisher": "c.com", "url": "https://c.com/1", "text": "완전히 다른 취재. " * 30}]
    ids = identify(rows, owners, wire)
    assert ids[0][0] == ids[1][0] and ids[2][0] == "c.com", ids
    assert len({i for i, _ in ids}) == 2, ids

    rows = [{"publisher": "x.com", "url": "https://x.com/1", "text": "짧다.",
             "canonical": "https://origin.example/story"}]
    assert identify(rows, owners, wire)[0][0] == "origin.example"
    print("ok")


if __name__ == "__main__":
    demo()
