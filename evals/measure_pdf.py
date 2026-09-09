#!/usr/bin/env python3
"""measure_pdf — PDF 천장이 실제로 얼마나 걸리는지, 그리고 어떤 PDF 인지 센다.

`measure_ladder.py` 는 "왜 못 읽었나"를 재고, 이건 "PDF 라서 못 읽은 것이 얼마나 되나"를 잰다.
추출기를 깔지 말지는 짐작이 아니라 이 숫자로 정한다 (#11, 칸 3·4를 정한 것과 같은 방식).

두 가지를 잰다.

1. **빈도** — 학술 인용이 실제로 PDF 로 떨어지는 비율. 리다이렉트 뒤 content-type 과
   매직 바이트(`%PDF-`)를 둘 다 본다. content-type 만 믿으면 `application/octet-stream`
   으로 내려주는 서버를 놓친다.
2. **종류** — 텍스트 층이 있는 PDF 인가, 스캔본인가. 스캔본은 추출기를 깔아도 못 읽고,
   빈 텍스트를 읽고 `근거 없음` 을 내면 거짓말이 된다 — `확인 불가` 로 남아야 한다.

종류 판별은 **표준 라이브러리만으로** 한다. PDF 의 콘텐츠 스트림은 대개 FlateDecode 라
`zlib` 으로 풀 수 있고, 텍스트 층이 있으면 `Tj`/`TJ` 연산자가 나온다. 추출기를 깔기 전에
"깔면 읽히긴 하는가"를 알아야 하므로 이 판별이 먼저다.

  python3 evals/measure_pdf.py
"""
import collections
import re
import sys
import zlib
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

# 사다리로 재지 않는다. 사다리는 모든 응답을 `.decode(..., "replace")` 로 문자열화하므로
# PDF 바이트가 되돌릴 수 없게 망가진다 — 그 사실 자체가 #11 의 첫 번째 제약이다.
# 여기서는 무엇이 PDF 이고 그 PDF 가 읽히는 종류인지만 재면 되므로 직접 바이트로 받는다.
UA = "cite-check/0.1 (+https://github.com/inpilot-dev/Research)"
CAP = 8 * 1024 * 1024      # 텍스트 층 판별에 앞부분이면 충분하다. loc.gov 한 건이 148 MB 다

URLS = [
    # 학술 프리프린트·오픈액세스 — 리서치 인용이 가장 자주 떨어지는 곳
    "https://arxiv.org/pdf/2103.00020",
    "https://arxiv.org/pdf/1706.03762",
    "https://www.biorxiv.org/content/10.1101/2020.03.30.015347v1.full.pdf",
    "https://www.medrxiv.org/content/10.1101/2020.04.16.20067835v1.full.pdf",
    "https://pmc.ncbi.nlm.nih.gov/articles/PMC7262788/pdf/main.pdf",
    "https://pmc.ncbi.nlm.nih.gov/articles/PMC7383595/pdf/",
    # 저널 (상당수가 막힐 것으로 예상 — 막히면 PDF 문제가 아니라 접근 문제다)
    "https://www.nejm.org/doi/pdf/10.1056/NEJMoa2007764",
    "https://www.bmj.com/content/bmj/369/bmj.m1985.full.pdf",
    "https://jamanetwork.com/journals/jama/articlepdf/2764727",
    # 기관 보고서 — 정책·통계 인용의 표준 형태
    "https://iris.who.int/bitstream/handle/10665/331665/WHO-2019-nCoV-IPC-2020.3-eng.pdf",
    "https://www.cdc.gov/mmwr/volumes/69/wr/pdfs/mm6915e3-H.pdf",
    "https://www.federalreserve.gov/monetarypolicy/files/20200315a1.pdf",
    "https://www.oecd.org/coronavirus/policy-responses/oecd-economic-outlook.pdf",
    # 스캔본이 섞이는 곳 — 텍스트 층이 없는 PDF 가 실제로 있는지 확인용
    "https://www.govinfo.gov/content/pkg/GPO-CONAN-1992/pdf/GPO-CONAN-1992-8.pdf",
    "https://tile.loc.gov/storage-services/service/ll/llsalvol/llsal_001/llsal_001.pdf",
    # 대조군 — HTML 로 떨어지는 것들. PDF 빈도의 분모가 된다
    "https://arxiv.org/abs/2103.00020",
    "https://pubmed.ncbi.nlm.nih.gov/32445440/",
    "https://www.who.int/about",
]

_TEXT_OP = re.compile(rb"(?:\bTj\b|\bTJ\b|\bT\*\b)")


def is_pdf(ctype, body):
    """content-type 을 믿지 않는다 — 매직 바이트가 최종 심판이다."""
    if "pdf" in (ctype or "").lower():
        return True
    return (body or b"")[:1024].lstrip().startswith(b"%PDF-")


def has_text_layer(raw):
    """스트림을 풀어 텍스트 연산자를 찾는다. → True(텍스트 층 있음) / False(스캔본으로 보임).

    표준 라이브러리만 쓴다. 암호화되었거나 FlateDecode 가 아닌 PDF 는 못 푸는데, 그 경우
    False 가 아니라 None 을 돌려준다 — "텍스트가 없다"와 "못 읽었다"를 여기서도 섞지 않는다.
    """
    if _TEXT_OP.search(raw):
        return True                      # 압축되지 않은 콘텐츠 스트림
    decoded, failed = False, 0
    for m in re.finditer(rb"stream\r?\n", raw):
        chunk = raw[m.end():m.end() + 200000]
        try:
            out = zlib.decompressobj().decompress(chunk)
        except zlib.error:
            failed += 1
            continue
        decoded = True
        if _TEXT_OP.search(out):
            return True
    if not decoded and failed:
        return None                      # 스트림을 하나도 못 풀었다 — 판정하지 않는다
    return False


def fetch_bytes(url, timeout=20):
    """→ (status, content_type, bytes). 문자열로 만들지 않는다."""
    try:
        with urlopen(Request(url, headers={"User-Agent": UA, "Accept": "*/*"}), timeout=timeout) as r:
            return r.status, r.headers.get("Content-Type", ""), r.read(CAP)
    except HTTPError as e:
        return e.code, "", b""
    except (URLError, TimeoutError, ValueError, OSError) as e:
        return f"err {type(e).__name__}", "", b""


def main():
    tally, rows = collections.Counter(), []
    for u in URLS:
        st, ct, raw = fetch_bytes(u)
        if not isinstance(st, int) or not 200 <= st < 400:
            kind = f"막힘:{st}"
        elif not is_pdf(ct, raw):
            kind = "HTML"
        else:
            kind = {True: "PDF:텍스트층", False: "PDF:스캔본", None: "PDF:판정불가"}[has_text_layer(raw)]
        tally[kind] += 1
        rows.append((kind, st, len(raw), u))
        print(f"{kind:<16} {str(st):<5} {len(raw):>9}  {u[:64]}", flush=True)

    print("\n=== 분포 ===")
    for k, v in tally.most_common():
        print(f"  {k:<16} {v}")
    pdf = sum(v for k, v in tally.items() if k.startswith("PDF:"))
    readable = tally["PDF:텍스트층"]
    print(f"\nPDF 로 떨어진 것 {pdf}/{len(URLS)} · 그중 텍스트 층이 있는 것 {readable}")
    print("추출기를 깔면 열리는 것은 텍스트 층이 있는 것뿐이다. 스캔본은 깔아도 확인 불가로 남는다.")


if __name__ == "__main__":
    main()
