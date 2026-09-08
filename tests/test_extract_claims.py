"""Seam — document → claims. The pairing of a sentence with the link it leans on."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import extract_claims as ex  # noqa: E402

FIXTURE = os.path.join(os.path.dirname(__file__), "fixtures", "sample-report.md")


class Extract(unittest.TestCase):
    def parse(self, md):
        return ex.parse(md)

    def test_inline_link_pairs_its_sentence_with_its_url(self):
        out = self.parse("The [primary outcome was recovery time](https://a.example/x). Next line here.")
        self.assertEqual(out["claims"], [{"claim": "The primary outcome was recovery time.",
                                          "url": "https://a.example/x"}])

    def test_two_links_in_one_sentence_make_two_claims(self):
        out = self.parse("Both [trials](https://a.example/1) reached [the same result](https://b.example/2).")
        self.assertEqual([c["url"] for c in out["claims"]], ["https://a.example/1", "https://b.example/2"])
        self.assertEqual(len({c["claim"] for c in out["claims"]}), 1)  # 문장은 하나

    def test_the_same_url_twice_in_a_sentence_is_one_claim(self):
        out = self.parse("See [here](https://a.example/1) and [again](https://a.example/1) for this result.")
        self.assertEqual(len(out["claims"]), 1)

    def test_footnote_and_reference_styles_resolve_through_definitions(self):
        md = ("Mortality was 6.7 percent at day 15[^a]. Approval followed in October[1].\n\n"
              "[^a]: https://foot.example/n\n[1]: https://ref.example/n\n")
        self.assertEqual([c["url"] for c in self.parse(md)["claims"]],
                         ["https://foot.example/n", "https://ref.example/n"])

    def test_bare_and_angle_bracket_urls_count_as_citations(self):
        out = self.parse("The guideline is at https://who.example/g and also <https://bmj.example/b> today.")
        self.assertEqual(sorted(c["url"] for c in out["claims"]),
                         ["https://bmj.example/b", "https://who.example/g"])

    def test_markdown_syntax_is_stripped_so_the_claim_matches_page_prose(self):
        out = self.parse("The **primary** outcome was `recovery` [time](https://a.example/x) here.")
        self.assertEqual(out["claims"][0]["claim"], "The primary outcome was recovery time here.")

    def test_a_url_inside_a_code_fence_is_not_a_citation(self):
        md = "Real claim with a source [here](https://a.example/1).\n\n```\ncurl https://code.example/x\n```\n"
        self.assertEqual([c["url"] for c in self.parse(md)["claims"]], ["https://a.example/1"])

    def test_assertions_without_a_link_are_counted_not_dropped(self):
        out = self.parse("Remdesivir works for everyone without question. It is the standard of care now.")
        self.assertEqual(out["claims"], [])
        self.assertEqual(len(out["unsourced"]), 2)

    def test_headings_tables_and_definitions_are_not_assertions(self):
        md = ("## A heading that is long enough to look like prose\n\n"
              "| trial | result |\n|---|---|\n| ACTT-1 | shorter recovery |\n\n"
              "[1]: https://ref.example/n\n")
        out = self.parse(md)
        self.assertEqual(out["claims"], [])
        self.assertEqual(out["unsourced"], [])

    def test_a_real_looking_report_yields_the_pairs_a_reader_would_expect(self):
        with open(FIXTURE, encoding="utf-8") as f:
            out = self.parse(f.read())
        urls = [c["url"] for c in out["claims"]]
        self.assertGreaterEqual(len(out["claims"]), 10)
        self.assertEqual(len(urls), len(set(urls)), "픽스처의 인용은 서로 달라야 한다")
        self.assertNotIn("https://example.com/not-a-citation", urls)      # 코드 블록
        self.assertIn("https://www.nejm.org/doi/full/10.1056/NEJMoa2007764", urls)   # 각주
        self.assertIn("https://www.fda.gov/news-events/press-announcements/"
                      "fda-approves-first-treatment-covid-19", urls)      # 참조 링크
        self.assertIn("https://www.bmj.com/content/375/bmj.n2713", urls)  # <꺾쇠>
        # 넷: 근거 없이 단정한 두 문장 + 서론 두 문장. 서론은 사실 주장이 아니지만 낱말 수
        # 휴리스틱은 그걸 구분하지 못한다 — 세는 쪽이 놓치는 쪽보다 안전하다 (알려진 천장).
        self.assertEqual(len(out["unsourced"]), 4)
        for c in out["claims"]:
            self.assertNotIn("](", c["claim"])
            self.assertNotIn("http", c["claim"])

    def test_cli_writes_claims_json_the_core_can_read(self):
        import io
        import json
        from contextlib import redirect_stdout
        buf = io.StringIO()
        with redirect_stdout(buf):
            self.assertEqual(ex.main([FIXTURE]), 0)
        items = json.loads(buf.getvalue())
        self.assertTrue(all(set(i) == {"claim", "url"} for i in items))


if __name__ == "__main__":
    unittest.main()


class DocumentIntoTheCore(unittest.TestCase):
    """문서를 그대로 넣었을 때 코어가 알아서 주장을 뽑고, 출처 없는 단정문을 센다."""

    def setUp(self):
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
        import cite_check
        self.cc = cite_check

    def test_a_markdown_document_is_accepted_where_claims_json_is(self):
        items, unsourced = self.cc.load_claims(FIXTURE)
        self.assertGreaterEqual(len(items), 10)
        self.assertEqual(unsourced, 4)
        self.assertTrue(all(set(i) == {"claim", "url"} for i in items))

    def test_a_claims_json_still_loads_unchanged(self):
        import json
        import tempfile
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
            json.dump([{"claim": "a claim here", "url": "https://x.example/1"}], f)
        items, unsourced = self.cc.load_claims(f.name)
        os.unlink(f.name)
        self.assertEqual((len(items), unsourced), (1, 0))

    def test_the_audit_log_counts_the_unsourced_assertions(self):
        out = self.cc.check([{"claim": "x y z w", "url": "https://x.example/1"}],
                            fetcher=lambda u, t: (404, "", ""))
        out["summary"]["unsourced"] = 4
        self.assertIn("출처 없음 4건", self.cc.render(out))
