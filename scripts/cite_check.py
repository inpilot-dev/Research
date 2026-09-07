#!/usr/bin/env python3
"""cite_check — deterministic L1/L2 citation verification. No LLM, stdlib only.

L1: does the source exist and respond?
L2: does the claim sentence appear in the source text (exact or fuzzy)?
Plus: unique-publisher count (circular-reporting dedup) and published date.

Input  JSON: [{"claim": "...", "url": "..."}, ...]
Output JSON: {"results": [...], "summary": {...}}

  python3 scripts/cite_check.py claims.json
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


def check(items, fuzzy=0.85, timeout=10, fetcher=fetch):
    results, cache = [], {}
    for it in items:
        claim, url = it["claim"], it["url"]
        if url not in cache:
            cache[url] = fetcher(url, timeout)  # ponytail: sequential; add per-publisher delay if sites rate-limit
        status, ctype, body = cache[url]
        alive = status is not None and 200 <= status < 400
        published, kind, score = None, "none", 0.0
        if alive and "pdf" in ctype.lower():
            kind = "unsupported-pdf"  # ponytail: PDF ceiling → PyMuPDF when needed
        elif alive:
            text, published = extract(body)
            # ponytail: 203 (e.g. NCBI bot wall) or a miss on a near-empty body = interstitial,
            # not the source. Report "blocked" (확인 불가), never "none" (근거 없음).
            # A real match is never blocked. Escalate fetch (API adapter / browser) later.
            if status == 203:
                kind = "blocked"
            else:
                kind, score = match(claim, text, fuzzy)
                if kind == "none" and len(text) < 200:
                    kind = "blocked"
        results.append({"claim": claim, "url": url, "alive": alive, "status": status,
                        "found": kind, "score": score, "published": published,
                        "publisher": publisher(url)})
    kinds = [r["found"] for r in results]
    summary = {"n": len(results), "alive": sum(r["alive"] for r in results),
               "exact": kinds.count("exact"), "fuzzy": kinds.count("fuzzy"),
               "none": kinds.count("none") + kinds.count("unsupported-pdf"),
               "blocked": kinds.count("blocked"),
               "unique_publishers": len({r["publisher"] for r in results})}
    return {"results": results, "summary": summary}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file", help="claims JSON path, or - for stdin")
    ap.add_argument("--fuzzy", type=float, default=0.85, help="fuzzy match threshold (default 0.85)")
    ap.add_argument("--timeout", type=int, default=10)
    ap.add_argument("--strict", action="store_true", help="exit 1 if any claim is not found")
    a = ap.parse_args(argv)
    items = json.load(sys.stdin if a.file == "-" else open(a.file, encoding="utf-8"))
    out = check(items, a.fuzzy, a.timeout)
    json.dump(out, sys.stdout, ensure_ascii=False, indent=2)
    print()
    return 1 if a.strict and (out["summary"]["none"] or out["summary"]["blocked"]) else 0


if __name__ == "__main__":
    sys.exit(main())
