"""Seam — identifier or URL → the API that knows it → text we can compare. Fake responses only."""
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import adapters as ad  # noqa: E402
import cite_check as cc  # noqa: E402

ABSTRACT = ("BACKGROUND: Several agents were evaluated. METHODS: We conducted a double-blind trial. "
            "RESULTS: The primary outcome was the time to recovery. CONCLUSIONS: Remdesivir shortened it.")


def responder(**by_host):
    """A fake HTTP getter: (status, headers, body) chosen by a substring of the URL."""
    def get(url, timeout):
        for needle, value in by_host.items():
            if needle in url:
                return value
        return 404, {}, ""
    return get


def registry(getter, **kw):
    kw.setdefault("sleeper", lambda s: None)
    return ad.Registry(getter=getter, **kw)


class Identify(unittest.TestCase):
    def test_a_bare_pmid_and_its_url_reach_pubmed(self):
        for token in ("32445440", "https://pubmed.ncbi.nlm.nih.gov/32445440/"):
            with self.subTest(token=token):
                a, ident = ad.identify(token)
                self.assertEqual((a["name"], ident), ("pubmed", "32445440"))

    def test_a_bare_doi_is_claimed_by_crossref_first_then_openalex(self):
        self.assertEqual([a["name"] for a, _ in ad.candidates("10.1056/NEJMoa2007764")],
                         ["crossref", "openalex"])

    def test_a_trial_registration_number_reaches_clinicaltrials(self):
        """연구 페이지가 SPA 라 직접 fetch 로는 본문이 없다 — 헤드리스 대신 이 API 를 쓴다."""
        for token in ("NCT04280705", "https://clinicaltrials.gov/study/NCT04280705",
                      "https://clinicaltrials.gov/ct2/show/NCT04280705"):
            with self.subTest(token=token):
                a, ident = ad.identify(token)
                self.assertEqual((a["name"], ident), ("clinicaltrials", "NCT04280705"))

    def test_an_unknown_token_has_no_adapter(self):
        self.assertEqual(ad.identify("https://example.com/blog/post"), (None, None))

    def test_an_identifier_becomes_the_address_a_person_can_open(self):
        self.assertEqual(ad.canonical_url("32445440"), "https://pubmed.ncbi.nlm.nih.gov/32445440/")
        self.assertEqual(ad.canonical_url("10.1056/x"), "https://doi.org/10.1056/x")
        self.assertEqual(ad.canonical_url("https://example.com/a"), "https://example.com/a")


class Fetch(unittest.TestCase):
    def test_pubmed_returns_the_abstract_as_plain_text(self):
        r = registry(responder(**{"eutils.ncbi": (200, {}, ABSTRACT)}))
        status, ctype, text = r.fetch("32445440")
        self.assertEqual((status, r.used), (200, "pubmed"))
        self.assertIn("time to recovery", text)

    def test_a_title_only_answer_is_not_enough_and_the_next_adapter_is_tried(self):
        """제목 한 줄로 문장을 대조할 수는 없다 — 그걸 통과시키면 제목만 보고 근거 없음을 찍는다."""
        r = registry(responder(**{
            "api.crossref": (200, {}, json.dumps({"message": {"title": ["A title and nothing else"]}})),
            "api.openalex": (200, {"x-ratelimit-cost-usd": "0.001"},
                             json.dumps({"title": "A title", "abstract_inverted_index":
                                         {"The": [0], "primary": [1], "outcome": [2], "was": [3],
                                          "recovery.": [4], "A": [5], "second": [6], "sentence.": [7]}}))}))
        status, _, text = r.fetch("10.1056/x")
        self.assertEqual((status, r.used), (200, "openalex"))
        self.assertIn("The primary outcome was recovery.", text)

    def test_the_inverted_index_comes_back_in_reading_order(self):
        self.assertEqual(ad._uninvert({"world": [1], "hello": [0]}), "hello world")
        self.assertEqual(ad._uninvert(None), "")

    def test_usage_and_cost_headers_are_captured(self):
        r = registry(responder(**{
            "api.crossref": (404, {}, ""),
            "api.openalex": (200, {"x-ratelimit-cost-usd": "0.002", "x-ratelimit-remaining-usd": "0.098"},
                             json.dumps({"title": "T", "abstract_inverted_index":
                                         {"One": [0], "sentence.": [1], "Two": [2], "here.": [3]}}))}))
        r.fetch("10.1056/x")
        self.assertEqual(r.usage["openalex"]["x-ratelimit-cost-usd"], "0.002")
        self.assertEqual(r.usage["openalex"]["x-ratelimit-remaining-usd"], "0.098")

    def test_an_adapter_failure_yields_no_text_rather_than_a_wrong_verdict(self):
        r = registry(responder(**{"api.": (500, {}, "")}))
        status, _, text = r.fetch("10.1056/x")
        self.assertEqual(text, "")
        self.assertNotEqual(status, 200)

    def test_a_response_shaped_unlike_the_config_is_not_read_as_text(self):
        r = registry(responder(**{"api.": (200, {}, "<html>not json at all</html>")}))
        self.assertEqual(r.fetch("10.1056/x")[2], "")

    def test_requests_to_one_api_are_spaced_by_its_rate_limit(self):
        slept, now = [], [0.0]
        r = ad.Registry(getter=responder(**{"eutils.ncbi": (200, {}, ABSTRACT)}),
                        clock=lambda: now[0], sleeper=lambda s: slept.append(round(s, 3)))
        r.fetch("32445440")
        r.fetch("32445440")            # 시계가 안 움직였으니 한도만큼 기다려야 한다
        self.assertEqual(slept, [round(1 / 3, 3)])   # pubmed: 키 없이 3 req/s


class ThroughTheCore(unittest.TestCase):
    def test_an_adapter_failure_blocks_only_its_own_claim(self):
        r = registry(responder(**{"eutils.ncbi": (200, {}, ABSTRACT), "api.": (503, {}, "")}))
        out = cc.check([{"claim": "The primary outcome was the time to recovery",
                         "url": "https://pubmed.ncbi.nlm.nih.gov/32445440/"},
                        {"claim": "anything", "url": "https://doi.org/10.9999/broken"}],
                       fetcher=lambda u, t: r.fetch(u, t))
        self.assertEqual([x["found"] for x in out["results"]], ["exact", "blocked"])

    def test_a_bare_identifier_in_a_claims_file_becomes_a_real_url(self):
        import tempfile
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
            json.dump([{"claim": "c", "url": "32445440"}, {"claim": "d", "url": "10.1056/x"}], f)
        items, _ = cc.load_claims(f.name)
        os.unlink(f.name)
        self.assertEqual([i["url"] for i in items],
                         ["https://pubmed.ncbi.nlm.nih.gov/32445440/", "https://doi.org/10.1056/x"])

    def test_the_audit_log_prints_what_the_api_cost(self):
        out = cc.check([{"claim": "x y z w", "url": "https://a.example/1"}],
                       fetcher=lambda u, t: (404, "", ""))
        out["summary"]["api_usage"] = {"openalex": {"x-ratelimit-cost-usd": "0.002"}}
        self.assertIn("openalex 사용량: x-ratelimit-cost-usd=0.002", cc.render(out))


class Configs(unittest.TestCase):
    def test_every_adapter_config_declares_what_the_registry_needs(self):
        for a in ad.load():
            with self.subTest(name=a.get("name")):
                for key in ("name", "label", "hosts", "identifier", "endpoint", "auth",
                            "rate_limit_per_second", "text", "priority", "note"):
                    self.assertIn(key, a)
                self.assertIn("{id}", a["endpoint"])
                self.assertIn(a["text"]["type"], ("plain", "json"))
                self.assertIn("{id}", a["identifier"]["canonical_url"])
                self.assertIsNone(a["auth"], "키가 필요한 출처는 사용자가 발급한다 (ADR 0004)")

    def test_the_adapters_are_data_not_code(self):
        self.assertEqual(sorted(a["name"] for a in ad.load()),
                         ["clinicaltrials", "crossref", "openalex", "pubmed"])
        with open(os.path.join(os.path.dirname(__file__), "..", "scripts", "adapters.py"),
                  encoding="utf-8") as f:
            src = f.read()
        for leaked in ("eutils", "api.crossref", "api.openalex", "abstract_inverted_index",
                       "clinicaltrials.gov", "protocolSection"):
            self.assertNotIn(leaked, src, "어댑터 설정이 코드로 새어 들어왔다 (ADR 0002)")


if __name__ == "__main__":
    unittest.main()
