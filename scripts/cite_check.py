#!/usr/bin/env python3
"""cite_check — deterministic L1/L2 citation verification. No LLM, stdlib only.

L1: does the source exist and respond?
L2: does the claim sentence appear in the source text (exact or fuzzy)?
Plus: unique-publisher count (circular-reporting dedup) and published date.

Input  JSON: [{"claim": "...", "url": "..."}, ...]
Output     : JSON {"results": [...], "summary": {...}} to stdout, or a markdown
             report with --report. --json PATH additionally writes results.json.
             --deep is reserved (L3); v1 prints a notice and runs L2.

  python3 scripts/cite_check.py claims.json
  python3 scripts/cite_check.py claims.json --report --json results.json > report.md
  cat claims.json | python3 scripts/cite_check.py - --fuzzy 0.85 --strict
"""
import argparse
import difflib
import json
import re
import sys
from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

UA = "cite-check/0.1 (+https://github.com/inpilot-dev/Research)"
_DATE_KEYS = {"article:published_time", "date", "pubdate", "publishdate",
              "dc.date", "dc.date.issued", "citation_publication_date"}


class _Text(HTMLParser):
    """Collect visible text and a published date; skip script/style/noscript."""

    def __init__(self):
        super().__init__()
        self.parts, self.published, self._skip = [], None, 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript"):
            self._skip += 1
        a = dict(attrs)
        if tag == "meta" and not self.published:
            key = (a.get("property") or a.get("name") or "").lower()
            if key in _DATE_KEYS and a.get("content"):
                self.published = a["content"]
        if tag == "time" and not self.published and a.get("datetime"):
            self.published = a["datetime"]

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript") and self._skip:
            self._skip -= 1

    def handle_data(self, data):
        if not self._skip:
            self.parts.append(data)


def extract(html_text):
    """Return (visible_text, published_date_or_None)."""
    p = _Text()
    p.feed(html_text)
    return re.sub(r"\s+", " ", " ".join(p.parts)).strip(), p.published


def normalize(s):
    s = s.lower().replace("“", '"').replace("”", '"').replace("’", "'")
    return re.sub(r"\s+", " ", s).strip()


def sentences(text):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n+", text) if s.strip()]


def match(claim, text, fuzzy=0.85):
    """Return (kind, score): kind in exact|fuzzy|none."""
    c, t = normalize(claim), normalize(text)
    if c and c in t:
        return "exact", 1.0
    # ponytail: sentence + 2-sentence-window fuzzy; paraphrase detection (L3) needs an LLM
    sents = sentences(t)
    windows = sents + [f"{a} {b}" for a, b in zip(sents, sents[1:])]
    best = max((difflib.SequenceMatcher(None, c, w).ratio() for w in windows), default=0.0)
    return ("fuzzy" if best >= fuzzy else "none"), round(best, 3)


def publisher(url):
    host = urlparse(url).netloc.lower()
    return host[4:] if host.startswith("www.") else host


def fetch(url, timeout=10):
    """Return (status, content_type, body_text). status None on network error."""
    req = Request(url, headers={"User-Agent": UA, "Accept": "text/html,*/*"})
    try:
        with urlopen(req, timeout=timeout) as r:
            ctype = r.headers.get("Content-Type", "")
            return r.status, ctype, r.read().decode(r.headers.get_content_charset() or "utf-8", "replace")
    except HTTPError as e:
        return e.code, "", ""
    except (URLError, TimeoutError, ValueError):
        return None, "", ""


KINDS = ("exact", "fuzzy", "none", "blocked", "unsupported-pdf")


def check(items, fuzzy=0.85, timeout=10, fetcher=fetch):
    results, cache = [], {}
    for it in items:
        claim, url = it["claim"], it["url"]
        if url not in cache:
            cache[url] = fetcher(url, timeout)  # ponytail: sequential; add per-publisher delay if sites rate-limit
        status, ctype, body = cache[url]
        alive = status is not None and 200 <= status < 400
        # Invariant (ADR 0002): "none" (근거 없음) is only ever produced by a real match attempt on
        # real source text. Anything that stopped us from reading the source is "blocked" (확인 불가).
        published, kind, score = None, "blocked", 0.0
        if alive and "pdf" in ctype.lower():
            kind = "unsupported-pdf"  # ponytail: PDF ceiling → PyMuPDF when needed
        elif alive:
            text, published = extract(body)
            # Interstitial signals, all observed: 203 (NCBI bot wall); a body with no visible text;
            # a body with fewer than two sentences (200-status consent/cookie walls, SPA shells).
            # ponytail: sentence count, not char length — short *real* pages still have sentences.
            if status != 203 and len(sentences(text)) >= 2:
                kind, score = match(claim, text, fuzzy)
        results.append({"claim": claim, "url": url, "alive": alive, "status": status,
                        "found": kind, "score": score, "published": published,
                        "publisher": publisher(url)})
    kinds = [r["found"] for r in results]
    summary = {"n": len(results), "alive": sum(r["alive"] for r in results),
               **{k.replace("-", "_"): kinds.count(k) for k in KINDS},
               "unique_publishers": len({r["publisher"] for r in results})}
    return {"results": results, "summary": summary}


_KO = {"none": "근거 없음", "blocked": "확인 불가", "unsupported-pdf": "미지원(PDF)"}
_WHY = {"none": "출처 원문에 해당 문장이 없음",
        "blocked": "출처에 접근하지 못함(죽은 링크·차단·203 봇 벽·동의벽·빈 본문) — 근거 없음과 다르다",
        "unsupported-pdf": "PDF 본문 추출은 v1 미지원"}
UNVERIFIED = ("none", "blocked", "unsupported-pdf")


def _line(s):
    """Collapse remote-controlled strings (claim/url/published) to one line so they cannot forge
    bullets, headings, or [publisher:kind] tokens in the report."""
    return re.sub(r"\s+", " ", str(s or "")).strip()


def render(out, deep_requested=False):
    """results → markdown report. 검증됨 / 미확인 / 감사 로그. Unverified claims never become assertions."""
    r, s = out["results"], out["summary"]
    ok = [x for x in r if x["found"] in ("exact", "fuzzy")]
    bad = [x for x in r if x["found"] in UNVERIFIED]
    L = ["# 검증 리포트", "", f"## 검증됨 ({len(ok)})", ""]
    for x in ok:
        tag = f"[{x['publisher']}:{x['found']}" + (f" {x['score']}" if x["found"] == "fuzzy" else "") + "]"
        L.append(f"- {tag} {_line(x['claim'])} — L2 · {_line(x['published']) or '게시일 미상'} · {_line(x['url'])}")
    L += ["", f"## 미확인 ({len(bad)})", "",
          "단정하지 않는다. 검증을 통과하지 못했다는 뜻이지 거짓이라는 뜻이 아니다.", ""]
    for x in bad:
        L.append(f"- {_KO[x['found']]}: {_line(x['claim'])} — {_line(x['url'])}")
    depth = "L2 (원문 텍스트 대조)" + (" — `--deep` 요청됨: L3(의미적 뒷받침)는 v1 미구현, L2로 진행" if deep_requested else "")
    L += ["", "## 감사 로그", "",
          f"- 입력 {s['n']}건 · 페치 URL {len({x['url'] for x in r})}개",
          f"- 판정: exact {s['exact']} / fuzzy {s['fuzzy']} / none {s['none']} / blocked {s['blocked']} / pdf {s['unsupported_pdf']}",
          f"- 독립 퍼블리셔 {s['unique_publishers']} (www. 제거한 호스트 기준; 순환보고 1차 근사)",
          f"- 검증 깊이: {depth}",
          "- 제외 사유:"] + [f"  - {_KO[k]}: {_WHY[k]}" for k in UNVERIFIED if s[k.replace("-", "_")]]
    return "\n".join(L) + "\n"


def unverified_count(summary):
    return sum(summary[k.replace("-", "_")] for k in UNVERIFIED)


def main(argv=None, fetcher=fetch):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file", help="claims JSON path, or - for stdin")
    ap.add_argument("--fuzzy", type=float, default=0.85, help="fuzzy match threshold (default 0.85)")
    ap.add_argument("--timeout", type=int, default=10)
    ap.add_argument("--strict", action="store_true", help="exit 1 if any claim is unverified (none/blocked/pdf)")
    ap.add_argument("--report", action="store_true", help="print a markdown report instead of JSON")
    ap.add_argument("--json", metavar="PATH", help="also write results JSON to PATH (one fetch, both artifacts)")
    ap.add_argument("--deep", action="store_true", help="request L3 (semantic) — reserved, v1 runs L2 only")
    a = ap.parse_args(argv)
    if a.deep:
        print("[cite_check] --deep: L3(의미적 뒷받침)는 v1 미구현 — L2(원문 대조)로 진행합니다.", file=sys.stderr)
    with (sys.stdin if a.file == "-" else open(a.file, encoding="utf-8")) as f:
        items = json.load(f)
    out = check(items, a.fuzzy, a.timeout, fetcher=fetcher)
    if a.json:
        with open(a.json, "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=2)
    if a.report:
        sys.stdout.write(render(out, deep_requested=a.deep))
    else:
        json.dump(out, sys.stdout, ensure_ascii=False, indent=2)
        print()
    return 1 if a.strict and unverified_count(out["summary"]) else 0


if __name__ == "__main__":
    sys.exit(main())
