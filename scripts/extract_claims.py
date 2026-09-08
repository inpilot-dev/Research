#!/usr/bin/env python3
"""extract_claims — 리서치 문서에서 "이 문장은 이 링크를 근거로 든다" 쌍을 뽑아낸다.

AI 리서치 리포트를 그대로 넣으면 검증할 주장 목록이 나온다. LLM 없음, 표준 라이브러리만.
링크가 붙은 문장은 주장이 되고, 링크 없이 단정하는 문장은 "출처 없음"으로 따로 센다.

세 가지 인용 형태를 모두 읽는다:
  인라인   [텍스트](https://…)  ·  <https://…>  ·  벌거벗은 https://…
  참조     [텍스트][1]  ·  축약 [1]  +  [1]: https://…
  각주     문장[^1]     +  [^1]: https://…

  python3 scripts/extract_claims.py report.md > claims.json
  python3 scripts/extract_claims.py report.md --stats
"""
import argparse
import json
import re
import sys

FENCE = re.compile(r"^\s*(```|~~~)")
REFDEF = re.compile(r"^\s{0,3}\[([^\]]+)\]:\s*<?(\S+?)>?\s*(?:\"[^\"]*\")?\s*$")
INLINE = re.compile(r"\[([^\]\n]*)\]\((\s*<?(?P<url>[^)\s>]+)>?[^)]*)\)")
REFLINK = re.compile(r"\[([^\]\n]*)\]\[([^\]\n]+)\]")
# 축약 참조: 문장 끝의 [1] 이 아래 [1]: url 을 가리킨다. ^로 시작하면 각주라 제외.
SHORTCUT = re.compile(r"\[([^\]\n^][^\]\n]*)\](?![(\[:])")
FOOTREF = re.compile(r"\[\^([^\]\s]+)\]")
BARE = re.compile(r"<(https?://[^>\s]+)>|(?<![(\]<\"'])\b(https?://[^\s<>)\]\"'`]+)")
# 문장 끝의 마침표·쉼표는 주소가 아니다. 삼키면 404 가 되어 멀쩡한 인용이 확인 불가로 떨어진다.
_TRAIL = ".,;:!?'\"`)]}>"
# 문장 부호가 없는 줄(제목·표·목록 머리)은 주장이 아니다.
SKIP_LINE = re.compile(r"^\s{0,3}(#{1,6}\s|\||\s*[-*+]\s*$|>\s*$|\[\^?[^\]]+\]:)")
EMPHASIS = re.compile(r"(\*\*|__|\*|_|`)")
SENT_END = re.compile(r"(?<=[.!?。？！])\s+|\n{2,}")
_WORD = re.compile(r"[A-Za-z가-힣0-9]+")


def _strip_code(md):
    """Fenced code blocks are not citations — a URL in a snippet is an example, not a source."""
    out, fenced = [], False
    for line in md.splitlines():
        if FENCE.match(line):
            fenced = not fenced
            continue
        out.append("" if fenced else line)
    return "\n".join(out)


def _refs(md):
    """[1]: url and [^1]: url definitions, keyed by label."""
    refs = {}
    for line in md.splitlines():
        m = REFDEF.match(line)
        if m and re.match(r"https?://", m.group(2)):
            refs[m.group(1).lstrip("^").lower()] = m.group(2)
    return refs


def _flatten(text, refs=()):
    """Markdown → the prose a reader sees, so it can be compared with the source page."""
    text = INLINE.sub(r"\1", text)
    text = REFLINK.sub(r"\1", text)
    text = FOOTREF.sub("", text)
    # 해석되는 축약 참조만 지운다 — 그냥 대괄호 친 낱말은 본문이므로 남긴다.
    text = SHORTCUT.sub(lambda m: "" if m.group(1).lower() in refs else m.group(1), text)
    text = BARE.sub("", text)
    text = EMPHASIS.sub("", text)
    text = re.sub(r"\s+([.,;:!?])", r"\1", text)      # 각주를 지운 자리에 남는 " ." 를 붙인다
    return re.sub(r"\s+", " ", text).strip(" \t,;")


def _urls(sentence, refs):
    """Every source this sentence points at, in the order it points at them."""
    found = []
    for m in INLINE.finditer(sentence):
        found.append(m.group("url"))
    for m in REFLINK.finditer(sentence):
        if m.group(2).lower() in refs:
            found.append(refs[m.group(2).lower()])
    for m in FOOTREF.finditer(sentence):
        if m.group(1).lower() in refs:
            found.append(refs[m.group(1).lower()])
    for m in SHORTCUT.finditer(sentence):
        if m.group(1).lower() in refs:
            found.append(refs[m.group(1).lower()])
    for m in BARE.finditer(sentence):
        found.append((m.group(1) or m.group(2)).rstrip(_TRAIL))
    seen, out = set(), []
    for u in found:  # 같은 문장이 같은 URL 을 두 번 가리켜도 주장은 하나
        if u not in seen:
            seen.add(u)
            out.append(u)
    return out


def sentences(md):
    """Sentences that could carry a claim — headings, tables and bare list markers dropped."""
    body = "\n".join("" if SKIP_LINE.match(l) else l for l in md.splitlines())
    out = []
    for para in re.split(r"\n{2,}", body):
        para = re.sub(r"^\s{0,3}[-*+]\s+|^\s{0,3}\d+[.)]\s+", "", para.strip(), flags=re.M)
        for s in SENT_END.split(para.replace("\n", " ")):
            s = s.strip()
            if s:
                out.append(s)
    return out


def parse(md):
    """→ {claims: [{claim, url}], unsourced: [sentence, …]}"""
    md = _strip_code(md)
    refs = _refs(md)
    claims, unsourced = [], []
    for s in sentences(md):
        urls = _urls(s, refs)
        text = _flatten(s, refs)
        # ponytail: 단정문 판정은 낱말 수 — 품사 분석은 이 도구가 할 일이 아니다.
        # 한국어는 교착어라 낱말 셋이면 이미 완결된 단정문이다("백신은 자폐를 유발한다").
        # 여기서 버리면 검증도 못 받고 "출처 없음" 으로 세지지도 않아 통째로 사라진다.
        if len(_WORD.findall(text)) < 3:
            continue
        if urls:
            claims += [{"claim": text, "url": u} for u in urls]
        else:
            unsourced.append(text)
    return {"claims": claims, "unsourced": unsourced}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file", help="markdown/text document, or - for stdin")
    ap.add_argument("--stats", action="store_true", help="print counts to stderr instead of claims to stdout")
    a = ap.parse_args(argv)
    with (sys.stdin if a.file == "-" else open(a.file, encoding="utf-8")) as f:
        out = parse(f.read())
    if a.stats:
        print(f"주장 {len(out['claims'])}건 · 출처 없음 {len(out['unsourced'])}건 · "
              f"URL {len({c['url'] for c in out['claims']})}개", file=sys.stderr)
    else:
        json.dump(out["claims"], sys.stdout, ensure_ascii=False, indent=2)
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
