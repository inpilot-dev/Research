"""Seam — PDF. 추출기를 주입해 네 경로를 본다: 성공 · 미설치 · 스캔본 · 깨진 PDF.

네트워크 없음, pypdf 없이도 돈다 — 추출기는 주입되는 것이지 여기서 부르는 것이 아니다.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import cite_check as cc  # noqa: E402

SENT = ("The primary outcome was the time to recovery, defined by discharge. "
        "Serious adverse events were reported in 131 of the 532 patients.")
PDF_BYTES = b"%PDF-1.7\n%\xe2\xe3\xcf\xd3\n1 0 obj\n<</Type/Catalog>>\nendobj\n"


def fetch(url, timeout=10):
    """PDF 는 바이트로, HTML 은 문자열로 — 코어가 실제로 받는 모습 그대로."""
    if "octet" in url:                                  # content-type 이 거짓말하는 서버
        return 200, "application/octet-stream", PDF_BYTES
    if "pdf" in url:
        return 200, "application/pdf", PDF_BYTES
    if "legacy" in url:                                 # 녹화본처럼 문자열이 된 PDF 응답
        return 200, "application/pdf", "%PDF-1.7 mangled"
    return 200, "text/html", f"<html><body><p>{SENT}</p></body></html>"


def run(extractor, claim=None, url="https://arxiv.org/pdf/1706.03762"):
    out = cc.check([{"claim": claim or "The primary outcome was the time to recovery",
                     "url": url}], fetcher=fetch, pdf_extractor=extractor)
    return out["results"][0], out["summary"]


class Pdf(unittest.TestCase):
    def test_extracted_text_is_matched_like_any_other_source(self):
        row, s = run(lambda raw: SENT)
        self.assertEqual(row["found"], "exact")
        self.assertNotIn("pdf", s)                      # 정상 경로는 감사 로그를 어지럽히지 않는다

    def test_a_sentence_absent_from_the_pdf_is_근거_없음(self):
        row, _ = run(lambda raw: SENT, claim="Remdesivir cured every patient in a single day.")
        self.assertEqual(row["found"], "none")          # 원문을 읽었고 문장이 없었다

    def test_without_an_extractor_it_stays_unsupported_pdf(self):
        row, s = run(None)
        self.assertEqual(row["found"], "unsupported-pdf")
        self.assertEqual(s["pdf"]["missing"], 1)
        self.assertIn("pypdf", cc.render({"results": [row], "summary": s}))

    def test_a_scanned_pdf_is_확인_불가_never_근거_없음(self):
        """텍스트 층이 없는 PDF 에서 빈 텍스트를 읽고 '없다'고 하면 그건 거짓말이다."""
        row, s = run(lambda raw: "   ")
        self.assertEqual(row["found"], "blocked")
        self.assertEqual(s["pdf"]["scan"], 1)
        self.assertIn("스캔본", cc.render({"results": [row], "summary": s}))

    def test_a_broken_pdf_is_확인_불가(self):
        def boom(raw):
            raise ValueError("invalid pdf header")
        row, s = run(boom)
        self.assertEqual(row["found"], "blocked")
        self.assertEqual(s["pdf"]["broken"], 1)

    def test_a_missing_library_is_reported_as_missing_not_broken(self):
        """추출기가 없는 것과 PDF 가 깨진 것은 다른 사건이다 — 사용자가 할 일이 다르다."""
        def unavailable(raw):
            from pdf_text import PdfUnavailable
            raise PdfUnavailable("pypdf 미설치")
        row, s = run(unavailable)
        self.assertEqual(row["found"], "unsupported-pdf")
        self.assertEqual(s["pdf"]["missing"], 1)

    def test_a_cover_page_with_too_few_sentences_is_확인_불가(self):
        row, s = run(lambda raw: "Annual Report 2020")
        self.assertEqual(row["found"], "blocked")
        self.assertEqual(s["pdf"]["thin"], 1)

    def test_a_pdf_served_as_octet_stream_is_still_a_pdf(self):
        """content-type 을 믿으면 이 응답은 HTML 파서로 들어가 본문이 사라진다."""
        self.assertTrue(cc.is_pdf("application/octet-stream", PDF_BYTES))
        row, _ = run(lambda raw: SENT, url="https://x.example/octet")
        self.assertEqual(row["found"], "exact")

    def test_a_recorded_pdf_response_has_no_bytes_so_it_stays_unsupported(self):
        """녹화본은 문자열이다. 바이트가 없으면 추출도 없다 — 조용히 근거 없음이 되지 않는다."""
        row, s = run(lambda raw: SENT, url="https://x.example/legacy.doc")
        self.assertEqual(row["found"], "unsupported-pdf")
        self.assertEqual(s["pdf"]["missing"], 1)

    def test_the_fetcher_hands_pdf_bytes_through_undecoded(self):
        """`.decode(..., 'replace')` 를 한 번이라도 거치면 어떤 추출기도 못 읽는다."""
        seen = []
        run(lambda raw: seen.append(raw) or SENT)
        self.assertEqual(seen, [PDF_BYTES])
        self.assertIsInstance(seen[0], bytes)


if __name__ == "__main__":
    unittest.main()
