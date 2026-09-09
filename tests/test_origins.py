"""Seam — 순환보고 판별. 한 곳이 한 말을 여러 곳이 한 말처럼 세지 않는지. 네트워크·LLM 없음."""
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import cite_check as cc  # noqa: E402
import origins as og  # noqa: E402
import route as r  # noqa: E402
import synthesis as sy  # noqa: E402

CLAIM = "A total of 1062 patients underwent randomization"
BODY = f"{CLAIM} in the trial. The primary outcome was the time to recovery."
LONG = ("The trial randomly assigned 1062 hospitalized adults with Covid-19 to remdesivir or "
        "placebo and followed them for 29 days, measuring the time to recovery as the primary "
        "endpoint and mortality as a secondary endpoint across sixty international sites. ")


def page(body, canonical=None, head=""):
    link = f'<link rel="canonical" href="{canonical}">' if canonical else ""
    return f"<html><head>{link}</head><body><p>{head}{body}</p></body></html>"


class Signals(unittest.TestCase):
    def test_a_wire_credit_collapses_three_outlets_into_one(self):
        def fetch(url, timeout=10):
            return 200, "text/html", page(BODY, head="SEOUL (Reuters) - ")
        out = cc.check([{"claim": CLAIM, "url": f"https://outlet{i}.example/a"} for i in "abc"],
                       fetcher=fetch)
        self.assertEqual(out["summary"]["unique_publishers"], 1)
        self.assertTrue(all(x["origin"] == "wire:reuters" for x in out["results"]))

    def test_three_independent_outlets_stay_three(self):
        def fetch(url, timeout=10):
            return 200, "text/html", page(f"{CLAIM} — reported by our own newsroom at {url}.")
        out = cc.check([{"claim": CLAIM, "url": f"https://outlet{i}.example/a"} for i in "abc"],
                       fetcher=fetch)
        self.assertEqual(out["summary"]["unique_publishers"], 3)
        self.assertNotIn("collapsed", out["summary"])

    def test_a_canonical_pointing_elsewhere_is_that_host(self):
        def fetch(url, timeout=10):
            return 200, "text/html", page(BODY, canonical="https://origin.example/story")
        out = cc.check([{"claim": CLAIM, "url": "https://mirror.example/a"}], fetcher=fetch)
        self.assertEqual(out["results"][0]["origin"], "origin.example")

    def test_a_canonical_to_its_own_host_changes_nothing(self):
        def fetch(url, timeout=10):
            return 200, "text/html", page(BODY, canonical="https://www.mirror.example/a")
        out = cc.check([{"claim": CLAIM, "url": "https://mirror.example/a"}], fetcher=fetch)
        self.assertEqual(out["results"][0]["origin"], "mirror.example")
        self.assertNotIn("collapsed", out["summary"])

    def test_same_owner_domains_are_one_source(self):
        def fetch(url, timeout=10):
            return 200, "text/html", page(BODY)
        out = cc.check([{"claim": CLAIM, "url": "https://www.wsj.com/a"},
                        {"claim": CLAIM, "url": "https://nypost.com/b"}], fetcher=fetch)
        self.assertEqual(out["summary"]["unique_publishers"], 1)

    def test_a_paragraph_copied_verbatim_across_outlets_collapses(self):
        """크레딧 없이 그대로 실은 재배포. 우연히 같을 길이가 아니다."""
        def fetch(url, timeout=10):
            return 200, "text/html", page(LONG if "copy" in url else "Our own reporting. " * 30)
        out = cc.check([{"claim": CLAIM, "url": "https://copy-a.example/1"},
                        {"claim": CLAIM, "url": "https://copy-b.example/1"},
                        {"claim": CLAIM, "url": "https://own.example/1"}], fetcher=fetch)
        self.assertEqual(out["summary"]["unique_publishers"], 2)

    def test_a_short_shared_sentence_does_not_collapse_anything(self):
        """상투적인 한 문장으로 서로 다른 취재를 하나로 접으면 그게 더 나쁜 결함이다."""
        shared = "The pandemic continued to spread."
        def fetch(url, timeout=10):
            return 200, "text/html", page(f"{shared} {url} has its own reporting here.")
        out = cc.check([{"claim": CLAIM, "url": f"https://outlet{i}.example/a"} for i in "abc"],
                       fetcher=fetch)
        self.assertEqual(out["summary"]["unique_publishers"], 3)


class AuditAndEffect(unittest.TestCase):
    def test_the_audit_log_says_why_it_counted_one(self):
        def fetch(url, timeout=10):
            return 200, "text/html", page(BODY, head="(AP) — ")
        md = cc.render(cc.check([{"claim": CLAIM, "url": "https://outlet-a.example/1"},
                                 {"claim": CLAIM, "url": "https://outlet-b.example/1"}],
                                fetcher=fetch))
        self.assertIn("원출처 수렴", md)
        self.assertIn("associated-press", md)
        self.assertIn("독립 퍼블리셔 1", md)

    def test_a_broken_data_file_does_not_stop_verification(self):
        """판별을 못 돌려도 판정은 나가야 한다. 다만 부풀린 채 셌다고 적는다."""
        real = og.load
        og.load = lambda *a, **k: (_ for _ in ()).throw(ValueError("broken"))
        try:
            out = cc.check([{"claim": CLAIM, "url": "https://a.example/1"}],
                           fetcher=lambda u, t: (200, "text/html", page(BODY)))
        finally:
            og.load = real
        self.assertEqual(out["results"][0]["found"], "exact")
        self.assertIn("판별을 돌리지 못했습니다", cc.render(out))

    def test_a_collapsed_claim_falls_out_of_확인된_것(self):
        """숫자만 줄이는 것이 아니라 종합문의 자리도 바뀌어야 한다 — 그게 이 티켓의 요점이다."""
        route = r.route("렘데시비르 무작위 시험의 일차 평가변수가 뭐였어?")
        meta = {"stopped_by": "done", "iterations": 2, "hardcap": 3, "refutations": ["x"]}
        def claim(pub, origin):
            return {"claim": CLAIM, "found": "exact", "score": 1.0, "conflict": "none",
                    "url": f"https://{pub}/1", "publisher": pub, "origin": origin}
        two = [claim("outlet-a.example", "outlet-a.example"), claim("outlet-b.example", "outlet-b.example")]
        self.assertIn("## 확인된 것 (1)", sy.synthesize("q", route, two, meta))
        one = [claim("outlet-a.example", "wire:reuters"), claim("outlet-b.example", "wire:reuters")]
        md = sy.synthesize("q", route, one, meta)
        self.assertIn("## 확인된 것 (0)", md)
        self.assertIn("## 확인됐으나 기준 미달 (1)", md)
        self.assertEqual(sy.problems(md), [])


class DataNotCode(unittest.TestCase):
    def test_the_lists_are_a_data_file(self):
        """새 통신사·새 소유주를 코드가 아니라 데이터로 더한다 (ADR 0002)."""
        with open(os.path.join(os.path.dirname(__file__), "..", "profiles", "publishers.json"),
                  encoding="utf-8") as f:
            d = json.load(f)
        self.assertIn("reuters", d["wire"])
        self.assertIn("wsj.com", d["owners"]["news-corp"])
        owners, wire = og.load()
        self.assertEqual(owners["thelancet.com"], "elsevier")
        self.assertNotIn("_note", wire)          # 주석 키가 통신사로 새어 들어가지 않는다

    def test_the_data_file_is_not_read_as_an_adapter(self):
        """`sources/*.json` 은 어댑터 레지스트리 전용이다 — 거기 두면 레지스트리가 깨진다."""
        import adapters as ad
        self.assertTrue(all("name" in a for a in ad.load()))


if __name__ == "__main__":
    unittest.main()
