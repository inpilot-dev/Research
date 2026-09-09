#!/usr/bin/env python3
"""pdf_text — PDF 본문 추출기. 코어 밖이다.

코어는 표준 라이브러리만 쓴다 (ADR 0001). PDF 추출은 선택 의존성이고, 없으면 지금까지처럼
`미지원(PDF)` 로 나가고 감사 로그에 "건너뜀(미설치)" 이 남는다 — 칸 3·4와 같은 방식이다.

추출기 계약 — 호출 가능한 것 하나:

    extractor(raw_bytes) -> str      # 본문 텍스트, 텍스트 층이 없으면 빈 문자열
    예외를 던지면 그 출처는 `확인 불가` 다. 빈 문자열도 `확인 불가` 다 — **`근거 없음` 이 아니다.**

스캔본(텍스트 층이 없는 PDF)에서 빈 텍스트를 읽고 "출처에 그 문장이 없다"고 적으면 그것은
거짓말이다. 우리가 못 읽은 것이지 원문에 없는 것이 아니다 (ADR 0002).

**왜 pypdf 인가** — 2026-09-09 실측(`evals/measure_pdf.py` 로 받은 두 PDF):

| | govinfo 5쪽 | arXiv 15쪽 | 비고 |
|---|---|---|---|
| pypdf 6.14 | 8,043자 0.0s | 39,611자 0.3s | 순수 파이썬, MIT, 시스템 의존성 없음 |
| pdfminer.six | 8,854자 0.0s | 39,675자 0.5s | arXiv 세로 사이드바를 `3 2 0 2 g u A` 로 흘린다 |

PyMuPDF 는 더 빠르지만 AGPL 이고 wheel 이 크다. 사다리에서 192 MB 짜리 playwright 를 깔지
않기로 한 것과 같은 이유로 고르지 않았다.

  python3 scripts/pdf_text.py <파일.pdf>
"""
import io
import sys

# ponytail: 앞부분만 읽지 않고 전부 읽는다. 인용 문장은 논문 어디에나 있다 —
# 창을 자르는 것은 모델에게 보낼 때(judge_llm.window)이지 대조할 때가 아니다.
MAX_PAGES = 200        # 200쪽을 넘는 PDF 는 리서치 인용이 아니라 자료집이다. 앞 200쪽만 본다


class PdfUnavailable(RuntimeError):
    """추출기를 쓸 수 없다. '텍스트가 없다'와 구분되어야 하므로 별개의 사건이다."""


def extract(raw, max_pages=MAX_PAGES):
    """PDF 바이트 → 본문 텍스트. 텍스트 층이 없으면 "" 를 돌려준다.

    pypdf 가 없으면 PdfUnavailable — 조용히 빈 문자열을 돌려주면 스캔본과 구분되지 않는다.
    """
    try:
        import pypdf                      # lazy: 코어는 이것 없이도 돈다
    except ImportError as e:
        raise PdfUnavailable(f"pypdf 미설치: {e}") from e
    reader = pypdf.PdfReader(io.BytesIO(raw))
    parts = []
    for page in reader.pages[:max_pages]:
        try:
            parts.append(page.extract_text() or "")
        except Exception:
            continue                      # 한 쪽이 깨졌다고 나머지를 버리지 않는다
    return "\n".join(parts).strip()


extract.name = "pypdf"


def demo():
    """텍스트 층이 없는 PDF 가 빈 문자열로 나오는지 — 그 경로가 확인 불가로 이어진다."""
    import pypdf
    buf = io.BytesIO()
    w = pypdf.PdfWriter()
    w.add_blank_page(width=612, height=792)   # 쪽은 있고 텍스트 층은 없다 — 스캔본과 같은 모습
    w.write(buf)
    assert extract(buf.getvalue()) == "", "텍스트 층 없는 PDF 는 빈 문자열이어야 한다"
    try:
        extract(b"not a pdf at all")
    except PdfUnavailable:
        raise AssertionError("깨진 PDF 를 미설치로 보고하면 안 된다")
    except Exception:
        pass                                  # 예외는 확인 불가로 이어진다 — 빈 문자열과 다른 사건
    print("ok")


if __name__ == "__main__":
    if len(sys.argv) == 1:
        demo()
    else:
        with open(sys.argv[1], "rb") as f:
            text = extract(f.read())
        print(f"{len(text)}자", file=sys.stderr)
        print(text[:2000])
