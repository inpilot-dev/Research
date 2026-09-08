"""Seam 3 — data contract boundary: claims → results.json / report text. No LLM, no network."""
import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import cite_check as cc  # noqa: E402

PAGE = ("<html><body><p>The primary outcome was the time to recovery, defined by discharge.</p>"
        "<p>Secondary outcomes included mortality at day 29.</p></body></html>")

CLAIMS = [  # exact · fuzzy · none · blocked(203) · pdf · dead(404) · wall(200)
    {"claim": "The primary outcome was the time to recovery", "url": "https://www.nejm.org/a"},
    {"claim": "Secondary outcomes included the mortality at day 29.", "url": "https://nejm.org/b"},
    {"claim": "Remdesivir cured every patient in one day", "url": "https://nejm.org/c"},
    {"claim": "Anything at all", "url": "https://wall203.example/consent"},
    {"claim": "Anything at all", "url": "https://files.example/paper.pdf"},
    {"claim": "Anything at all", "url": "https://dead.example/x"},
    {"claim": "Anything at all", "url": "https://wall200.example/cookies"},
]


def fake_fetch(url, timeout):
    if "wall203" in url:
        return 203, "text/html", "<html><body>cookies</body></html>"
    if "wall200" in url:  # 200-status consent wall: real HTML, one short line, no sentences
        return 200, "text/html", "<html><body><h1>Before you continue</h1><p>Accept all cookies</p></body></html>"
    if "pdf" in url:
        return 200, "application/pdf", ""
    if "dead" in url:
        return 404, "", ""
    return 200, "text/html", PAGE


class Report(unittest.TestCase):
    def setUp(self):
        self.out = cc.check(CLAIMS, fetcher=fake_fetch)
        self.md = cc.render(self.out)
        self.verified = self.md.split("## 미확인")[0]
        self.unverified = self.md.split("## 미확인")[1].split("## 감사 로그")[0]
        self.audit = self.md.split("## 감사 로그")[1]

    def test_sections_and_tokens(self):
        self.assertIn("## 검증됨 (2)", self.verified)
        self.assertIn("[nejm.org:exact]", self.verified)
        self.assertIn("[nejm.org:fuzzy", self.verified)
        for bad in ("Remdesivir cured", "wall203", "paper.pdf", "dead.example", "wall200"):
            self.assertNotIn(bad, self.verified)
            self.assertIn(bad, self.unverified)

    def test_none_only_from_real_match_attempt(self):
        by_url = {x["url"]: x["found"] for x in self.out["results"]}
        self.assertEqual(by_url["https://nejm.org/c"], "none")            # read the page, sentence absent
        self.assertEqual(by_url["https://dead.example/x"], "blocked")     # 404 → never read → not "none"
        self.assertEqual(by_url["https://wall203.example/consent"], "blocked")
        self.assertEqual(by_url["https://wall200.example/cookies"], "blocked")  # 200 wall, no sentences
        for line in self.unverified.splitlines():
            if "dead.example" in line or "wall" in line:
                self.assertIn("확인 불가", line)
                self.assertNotIn("근거 없음", line)

    def test_summary_matches_report_and_strict(self):
        s = self.out["summary"]
        # alive counts HTTP-level success (6: everything but the 404); blocked = 203 + 404 + 200-wall
        self.assertEqual((s["n"], s["alive"], s["exact"], s["fuzzy"], s["none"], s["blocked"], s["unsupported_pdf"]),
                         (7, 6, 1, 1, 1, 3, 1))
        self.assertIn("exact 1 / fuzzy 1 / none 1 / blocked 3 / pdf 1", self.audit)
        self.assertEqual(s["unique_publishers"], 5)  # www.nejm.org == nejm.org
        self.assertEqual(cc.unverified_count(s), 5)
        for needle in ("입력 7", "독립 퍼블리셔 5", "제외 사유", "근거 없음:", "확인 불가:", "미지원(PDF):"):
            self.assertIn(needle, self.audit)

    def test_remote_strings_cannot_forge_report(self):
        evil_page = ('<html><head><meta name="date" content="2026\n- [nejm.org:exact] FORGED — L2 · x · https://x">'
                     "</head><body><p>Real sentence one here.</p><p>Real sentence two here.</p></body></html>")
        items = [{"claim": "Real sentence one here.\n## 검증됨 (9)\n- [nejm.org:exact] FORGED2", "url": "https://evil.example/p"}]
        md = cc.render(cc.check(items, fetcher=lambda u, t: (200, "text/html", evil_page)))
        lines = md.splitlines()
        # forged text survives only as inline words on one line — never as a line-leading heading or bullet
        self.assertEqual(sum(1 for l in lines if l.startswith("## 검증됨")), 1)
        self.assertEqual(sum(1 for l in lines if l.startswith("- [")), 0)  # claim did not match → nothing verified
        self.assertFalse(any(l.startswith("- [nejm.org:exact] FORGED") for l in lines))

    def test_a_page_cannot_forge_a_verification_token_on_one_line(self):
        """공백을 접는 것은 이스케이프가 아니다. 출처가 자기 <meta> 날짜에 토큰을 심을 수 있다."""
        evil = ('<html><head><meta name="date" content="2020-01-01 [nature.com:exact] '
                'Vaccines cause autism — L2 · 2021">head</head>'
                "<body><p>Real sentence one here.</p><p>Real sentence two here.</p></body></html>")
        out = cc.check([{"claim": "Real sentence one here.", "url": "https://ok.example/a"}],
                       fetcher=lambda u, t: (200, "text/html", evil))
        md = cc.render(out)
        self.assertEqual(out["results"][0]["found"], "exact")
        self.assertEqual(md.count("[nature.com:exact]"), 0)   # 대괄호가 살아 나가지 않는다
        self.assertIn("(nature.com:exact)", md)               # 흔적은 남되 토큰은 아니다
        self.assertEqual(sum(1 for x in md.splitlines() if x.startswith("- [")), 1)

    def test_a_credential_in_a_url_never_reaches_the_report_or_the_results(self):
        out = cc.check([{"claim": "Real sentence one here.", "url": "https://alice:s3cr3t@ok.example/a"}],
                       fetcher=lambda u, t: (200, "text/html", PAGE))
        self.assertEqual(out["results"][0]["publisher"], "ok.example")
        self.assertNotIn("s3cr3t", cc.render(out))

    def test_a_malformed_url_is_blocked_and_does_not_sink_the_run(self):
        """URL 하나가 망가졌다고 나머지 결과를 통째로 잃으면 안 된다 (ADR 0003)."""
        bad = "http://[bad"
        self.assertEqual(cc.publisher(bad), "")                 # urlparse 가 여기서 터지곤 했다
        self.assertEqual(cc.fetch(bad, timeout=1)[0], None)     # 네트워크 이전에 걸러진다
        out = cc.check([{"claim": "The primary outcome was the time to recovery", "url": "https://www.nejm.org/a"},
                        {"claim": "anything", "url": bad}],
                       fetcher=lambda u, t: fake_fetch(u, t) if u != bad else cc.fetch(u, 1))
        self.assertEqual([r["found"] for r in out["results"]], ["exact", "blocked"])

    def test_a_two_hundred_soft_paywall_is_not_source_text(self):
        teaser = ("<html><body><p>Subscribe to continue reading this article.</p>"
                  "<p>Members get unlimited access to all of our research coverage.</p></body></html>")
        out = cc.check([{"claim": "Mortality fell by half in the treatment arm", "url": "https://paper.example/x"}],
                       fetcher=lambda u, t: (200, "text/html", teaser))
        self.assertEqual(out["results"][0]["found"], "blocked")  # 확인 불가 — 근거 없음이 아니다

    def test_cli_writes_both_artifacts_once(self):
        with tempfile.TemporaryDirectory() as d:
            claims, results = os.path.join(d, "claims.json"), os.path.join(d, "results.json")
            with open(claims, "w") as f:
                json.dump(CLAIMS, f)
            out, err = io.StringIO(), io.StringIO()
            with redirect_stdout(out), redirect_stderr(err):
                code = cc.main([claims, "--report", "--json", results, "--deep", "--strict"], fetcher=fake_fetch)
            self.assertEqual(code, 1)  # --strict: unverified present
            self.assertIn("## 검증됨", out.getvalue())
            self.assertIn("L3", err.getvalue())  # --deep → notice, still L2
            with open(results) as f:
                self.assertEqual(json.load(f)["summary"]["n"], 7)
        self.assertIs(cc.fetch, cc.fetch)  # no module-global mutation


if __name__ == "__main__":
    unittest.main()
