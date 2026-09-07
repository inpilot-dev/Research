import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import cite_check as cc  # noqa: E402

PAGE = """<html><head><meta property="article:published_time" content="2026-05-01">
<script>var x = "The primary outcome was fake";</script></head>
<body><h1>ACTT-1</h1><p>The primary outcome was the time to recovery, defined by discharge.</p>
<p>Secondary outcomes included mortality at day 29.</p></body></html>"""


def fake_fetch(url, timeout):
    if "dead" in url:
        return 404, "", ""
    if "pdf" in url:
        return 200, "application/pdf", ""
    if "wall" in url:
        return 203, "text/html", "<html><body>cookies required</body></html>"
    return 200, "text/html", PAGE


class CiteCheck(unittest.TestCase):
    def test_extract_skips_script_and_reads_date(self):
        text, published = cc.extract(PAGE)
        self.assertIn("time to recovery", text)
        self.assertNotIn("fake", text)
        self.assertEqual(published, "2026-05-01")

    def test_match_levels(self):
        text, _ = cc.extract(PAGE)
        self.assertEqual(cc.match("The primary outcome was the time to recovery", text)[0], "exact")
        self.assertEqual(cc.match("The primary outcome was time to recovery, defined by discharge", text)[0], "fuzzy")
        self.assertEqual(cc.match("Patients were given placebo for ninety days", text)[0], "none")

    def test_check_summary_and_publisher_dedup(self):
        items = [
            {"claim": "The primary outcome was the time to recovery", "url": "https://www.nejm.org/a"},
            {"claim": "Secondary outcomes included mortality at day 29.", "url": "https://nejm.org/b"},
            {"claim": "anything", "url": "https://dead.example/x"},
            {"claim": "anything", "url": "https://files.example/paper.pdf"},
            {"claim": "anything", "url": "https://wall.example/consent"},
        ]
        out = cc.check(items, fetcher=fake_fetch)
        s = out["summary"]
        self.assertEqual((s["n"], s["alive"], s["exact"], s["none"], s["blocked"]), (5, 4, 2, 2, 1))
        self.assertEqual(s["unique_publishers"], 4)  # www.nejm.org == nejm.org
        self.assertEqual(out["results"][3]["found"], "unsupported-pdf")
        self.assertEqual(out["results"][4]["found"], "blocked")  # 확인 불가 ≠ 근거 없음
        self.assertFalse(out["results"][2]["alive"])


if __name__ == "__main__":
    unittest.main()
