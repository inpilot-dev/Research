#!/usr/bin/env python3
"""adapters — 출처 API 를 설정 데이터로 붙인다. 새 출처는 sources/*.json 하나면 된다 (ADR 0002).

식별자(DOI·PMID)나 URL 을 주면 맡을 어댑터를 찾아 API 로 원문 텍스트를 받아온다.
반환은 코어와 같은 계약이다: (status, content_type, text).

어댑터가 실패하면 그 주장만 확인 불가가 된다 — 어댑터가 깨진 것을 "출처에 그 말이 없다"로
바꿔 말하지 않는다. 사용량·비용 헤더는 감사 로그로 넘긴다: 학술 API 가 공짜라고 전제하지 않는다.

  python3 scripts/adapters.py 32445440 10.1056/NEJMoa2007764
"""
import json
import os
import re
import sys
import time
from urllib.parse import urlparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cite_check import has_source_text  # noqa: E402

SOURCES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "sources")


def load(directory=SOURCES):
    out = []
    for fn in sorted(os.listdir(directory)):
        if fn.endswith(".json"):
            with open(os.path.join(directory, fn), encoding="utf-8") as f:
                out.append(json.load(f))
    return out


def candidates(token, adapters=None):
    """이 토큰을 맡을 수 있는 어댑터 전부, 우선순위 순.

    한 식별자를 여러 API 가 안다. Crossref 는 NEJM 초록을 안 갖고 있고 OpenAlex 는 갖고 있다 —
    첫 어댑터가 텍스트를 못 주면 다음으로 넘어가는 편이 대조할 원문을 훨씬 자주 얻는다.
    """
    found = []
    for a in adapters if adapters is not None else load():
        ident = _match(a, token)
        if ident:
            found.append((a, ident))
    return sorted(found, key=lambda x: x[0].get("priority", 99))


def _match(adapter, token):
    """이 어댑터가 이 토큰을 맡을 수 있나 → 식별자, 아니면 None.

    URL 이면 **호스트가 맞을 때만** 본문 패턴을 적용한다. 패턴만 보고 아무 데서나 찾으면
    `?term=32445440` 이 붙은 남의 URL 이 PubMed 논문으로 둔갑해, 인용하지도 않은 출처를 읽고
    "근거 없음" 을 찍게 된다.
    """
    ident, t = adapter["identifier"], token.strip()
    if re.fullmatch(ident["pattern"], t):
        return t
    if "://" in t:
        try:
            host = urlparse(t).netloc.rsplit("@", 1)[-1].split(":")[0].lower()
        except ValueError:
            return None
        allowed = {h.lower().removeprefix("www.") for h in adapter.get("hosts", [])}
        if host.removeprefix("www.") not in allowed:
            return None
    for pat in ident.get("url_patterns", []):
        m = re.search(pat, t)
        if m:
            return m.group(1)
    return None


def identify(token, adapters=None):
    """토큰(식별자 또는 URL) → (어댑터, id). 맡을 어댑터가 없으면 (None, None)."""
    got = candidates(token, adapters)
    return got[0] if got else (None, None)


def canonical_url(token, adapters=None):
    """리포트에 적을 사람이 여는 주소. 못 알아보면 토큰 그대로."""
    a, ident = identify(token, adapters)
    return a["identifier"]["canonical_url"].format(id=ident) if a else token


def _dig(obj, path):
    for key in path.split("."):
        if not isinstance(obj, dict) or key not in obj:
            return None
        obj = obj[key]
    return obj


def _uninvert(index):
    """OpenAlex 초록은 낱말→위치 역색인으로 온다. 원문 순서로 되돌린다.

    한 자리에 두 낱말이 오거나 위치가 음수인 응답도 온다. 덮어쓰면 낱말이 사라져 문장의 뜻이
    바뀌므로 같은 자리는 모아 두고, 음수는 버린다 — 대조할 원문을 우리가 왜곡하면 안 된다.
    """
    if not isinstance(index, dict):
        return ""
    slots = {}
    for word, positions in index.items():
        if not isinstance(word, str) or not isinstance(positions, (list, tuple)):
            continue
        for p in positions:
            if isinstance(p, int) and p >= 0:
                slots.setdefault(p, []).append(word)
    return " ".join(w for k in sorted(slots) for w in slots[k])


def text_of(adapter, body):
    """설정이 가리키는 자리에서 대조할 텍스트를 꺼낸다. 모양이 다르면 빈 문자열."""
    spec = adapter["text"]
    if spec["type"] == "plain":
        return body
    try:
        doc = json.loads(body)
    except ValueError:
        return ""
    parts = [_dig(doc, f) for f in spec.get("fields", [])]
    parts = [" ".join(x for x in p if isinstance(x, str)) if isinstance(p, list) else p for p in parts]
    if spec.get("inverted_index"):
        parts.append(_uninvert(_dig(doc, spec["inverted_index"])))
    return re.sub(r"<[^>]+>", " ", " ".join(p for p in parts if isinstance(p, str) and p)).strip()


class Registry:
    """어댑터 묶음. 요청 사이를 벌려 rate limit 을 지키고, 사용량 헤더를 모아 둔다."""

    def __init__(self, adapters=None, getter=None, clock=time.monotonic, sleeper=time.sleep):
        self.adapters = adapters if adapters is not None else load()
        self.clock, self.sleeper, self.usage, self.used, self._last = clock, sleeper, {}, None, {}
        self._get = getter or _default_get

    def _wait(self, adapter):
        gap = 1.0 / max(adapter.get("rate_limit_per_second") or 1, 0.001)
        since = self.clock() - self._last.get(adapter["name"], -1e9)
        if since < gap:
            self.sleeper(gap - since)
        self._last[adapter["name"]] = self.clock()

    def fetch(self, token, timeout=10):
        """→ (status, ctype, text). 텍스트를 준 첫 어댑터를 쓴다. 아무도 못 맡으면 (None, '', '')."""
        last = (None, "", "")
        for adapter, ident in candidates(token, self.adapters):
            self._wait(adapter)
            status, headers, body = self._get(adapter["endpoint"].format(id=ident), timeout)
            headers = {k.lower(): v for k, v in (headers or {}).items()}
            for h in adapter.get("usage_headers", []):
                v = headers.get(h.lower())
                if v is not None:
                    self.usage.setdefault(adapter["name"], {})[h] = v
            if status is None or not (200 <= status < 400):
                last = (status, "", "")     # 어댑터 실패 → 다음 어댑터, 끝내 없으면 확인 불가
                continue
            try:
                text = text_of(adapter, body)
            except Exception:      # 한 어댑터의 예상 밖 응답이 인용 목록 전체를 죽이지 않는다
                last = (502, "", "")
                continue
            # 제목 한 줄로는 문장을 대조할 수 없다. "원문을 읽었다"의 기준은 코어와 같은 것 하나뿐이다 —
            # 여기서 느슨하게 통과시키면 제목만 보고 "근거 없음"을 찍게 된다.
            if has_source_text(status, text):
                self.used = adapter["name"]
                return status, "text/plain", text
            last = (204, "", "")            # 응답은 왔는데 대조할 원문이 없다
        return last


def _lower(headers):
    """HTTP 헤더 이름은 대소문자를 가리지 않는다 — 한 가지 모양으로 눕혀 놓고 찾는다."""
    return {k.lower(): v for k, v in dict(headers or {}).items()}


def _default_get(url, timeout):
    from http.client import HTTPException
    from urllib.error import HTTPError, URLError
    from urllib.request import Request, urlopen
    try:
        req = Request(url, headers={"User-Agent": "cite-check/0.1 (mailto:alstmdqls03@gmail.com)",
                                    "Accept": "application/json, text/plain, */*"})
        with urlopen(req, timeout=timeout) as r:
            return (r.status, _lower(r.headers),
                    r.read().decode(r.headers.get_content_charset() or "utf-8", "replace"))
    except HTTPError as e:
        return e.code, _lower(e.headers), ""
    except (URLError, TimeoutError, ValueError, OSError, HTTPException):
        return None, {}, ""


if __name__ == "__main__":
    reg = Registry()
    for token in sys.argv[1:]:
        a, ident = identify(token)
        reg.used = None
        st, ct, tx = reg.fetch(token, 15)
        print(f"{token}\n  후보={[c[0]['name'] for c in candidates(token)]} 사용={reg.used or '없음'} "
              f"id={ident} status={st} 길이={len(tx)}")
        print(f"  {tx[:160].strip()}")
    if reg.usage:
        print("사용량:", json.dumps(reg.usage, ensure_ascii=False))
