"""Seam — 상충 판정. 다섯 경로: 모순 · 무관 · 같은 말 · 근거 문장 위조 · 판정기 없음.

실제 LLM 호출 없음. 쌍 고르기는 결정론적이라 그것부터 따로 본다.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import cite_check as cc  # noqa: E402
import conflict as cf  # noqa: E402
import report_gate as g  # noqa: E402
import route as r  # noqa: E402
import synthesis as sy  # noqa: E402

A = "Mortality was 6.7 percent with remdesivir at day 15 among hospitalized adults."
B = "Mortality with remdesivir at day 15 was 24 percent among hospitalized adults."
PAGES = {"https://a.example/1": A, "https://b.example/1": B}


def claims():
    return [{"claim": A, "url": "https://a.example/1", "publisher": "a.example", "found": "exact"},
            {"claim": B, "url": "https://b.example/1", "publisher": "b.example", "found": "exact"}]


class Judge:
    name = "fake-conflict-judge"

    def __init__(self, verdict, qa=A, qb=B, boom=None):
        self.verdict, self.qa, self.qb, self.boom, self.seen = verdict, qa, qb, boom, []

    def __call__(self, ca, ta, cb, tb):
        self.seen.append((ca, cb))
        if self.boom:
            raise self.boom
        return {"critique": "…", "verdict": self.verdict, "quote_a": self.qa, "quote_b": self.qb}


class Pairing(unittest.TestCase):
    def test_only_verified_claims_are_compared(self):
        """`확인 불가` 는 상충 판정 대상이 아니다 — 원문을 못 읽었으면 모순인지도 모른다."""
        cl = claims() + [{"claim": B, "url": "https://c.example/1", "publisher": "c.example",
                          "found": "blocked"}]
        self.assertEqual(cf.pairs(cl), [(0, 1)])

    def test_the_same_origin_is_not_compared_with_itself(self):
        cl = claims()
        cl[1]["origin"] = cl[0]["origin"] = "wire:reuters"
        self.assertEqual(cf.pairs(cl), [])

    def test_unrelated_claims_are_not_sent_to_the_judge(self):
        cl = claims() + [{"claim": "Rainfall in April exceeded the seasonal average.",
                          "url": "https://d.example/1", "publisher": "d.example", "found": "exact"}]
        self.assertEqual(cf.pairs(cl), [(0, 1)])

    def test_identical_sentences_are_corroboration_not_conflict(self):
        cl = claims()
        cl[1]["claim"] = A
        self.assertEqual(cf.pairs(cl), [])

    def test_pairing_is_deterministic_and_capped(self):
        cl = [{"claim": f"Mortality with remdesivir at day 15 was {n} percent among adults.",
               "url": f"https://p{n}.example/1", "publisher": f"p{n}.example", "found": "exact"}
              for n in range(12)]
        first = cf.pairs(cl)
        self.assertEqual(first, cf.pairs(cl))              # 같은 입력에 같은 순서
        self.assertLessEqual(len(first), cf.MAX_PAIRS)


class Verdicts(unittest.TestCase):
    def run_with(self, judge):
        cl = claims()
        decl, log = cf.find(cl, PAGES, judge)
        cf.apply(cl, decl)
        return cl, decl, log

    def test_a_real_conflict_marks_both_sides(self):
        cl, decl, log = self.run_with(Judge("conflict"))
        self.assertEqual(sorted(decl), [0, 1])
        self.assertTrue(all(c["conflict"] == "conflict" for c in cl))
        self.assertEqual((log["conflict"], log["failed"]), (1, 0))

    def test_independent_claims_are_left_alone(self):
        cl, decl, log = self.run_with(Judge("independent"))
        self.assertEqual(decl, {})
        self.assertEqual(log["independent"], 1)
        self.assertFalse(any(c.get("conflict") == "conflict" for c in cl))

    def test_the_same_statement_twice_is_not_a_conflict(self):
        _, decl, log = self.run_with(Judge("same"))
        self.assertEqual((decl, log["same"]), ({}, 1))

    def test_a_forged_quote_throws_the_verdict_away(self):
        """지어낸 모순으로 멀쩡한 주장 둘을 함께 끌어내리면 안 된다."""
        _, decl, log = self.run_with(Judge("conflict", qb="Never written in any source at all."))
        self.assertEqual(decl, {})
        self.assertEqual(log["failed"], 1)
        self.assertIn("근거 문장이 원문에 없음", log["errors"])

    def test_a_quote_from_the_wrong_source_is_rejected(self):
        """quote_b 는 B 의 원문에서 와야 한다. A 의 문장을 내밀면 판정을 버린다."""
        _, decl, _ = self.run_with(Judge("conflict", qb=A))
        self.assertEqual(decl, {})

    def test_a_failed_call_leaves_the_pair_unjudged(self):
        _, decl, log = self.run_with(Judge("conflict", boom=RuntimeError("boom")))
        self.assertEqual(decl, {})
        self.assertEqual(log["failed"], 1)

    def test_without_a_judge_nothing_is_declared(self):
        cl = claims()
        decl, log = cf.find(cl, PAGES, None)
        self.assertEqual((decl, log), ({}, None))
        self.assertFalse(any(c.get("conflict") for c in cl))


class ThroughTheCore(unittest.TestCase):
    def fetch(self, url, timeout=10):
        # 두 문장 이상이어야 코어가 "진짜 본문" 으로 친다 (has_source_text).
        body = PAGES.get(url, "Nothing here at all.") + " The trial ran across sixty sites."
        return 200, "text/html", f"<html><body><p>{body}</p></body></html>"

    def test_the_audit_log_records_conflicts_and_the_model(self):
        out = cc.check([{"claim": A, "url": "https://a.example/1"},
                        {"claim": B, "url": "https://b.example/1"}],
                       fetcher=self.fetch, conflict_judge=Judge("conflict"))
        md = cc.render(out)
        self.assertEqual(out["summary"]["conflict"]["conflict"], 1)
        self.assertIn("상충: 1쌍 판정", md)
        self.assertIn("fake-conflict-judge", md)

    def test_deep_without_a_conflict_judge_says_미판정_not_없음(self):
        out = cc.check([{"claim": A, "url": "https://a.example/1"}], fetcher=self.fetch)
        line = next(x for x in cc.render(out, deep_requested=True).splitlines() if x.startswith("- 상충:"))
        self.assertIn("판정하지 않았습니다", line)
        self.assertIn("`상충 없음` 이 아니라 `상충 미판정`", line)

    def test_conflicting_claims_leave_확인된_것_and_the_gate_still_passes(self):
        route = r.route("렘데시비르 무작위 시험의 일차 평가변수가 뭐였어?")
        meta = {"stopped_by": "done", "iterations": 2, "hardcap": 3, "refutations": ["x"]}

        def c(claim, pub, **kw):
            return {"claim": claim, "found": "exact", "score": 1.0, "url": f"https://{pub}/1",
                    "publisher": pub, "conflict": "none", **kw}
        cl = [c(A, "a.example", conflict="conflict", conflict_quotes=[A]),
              c(A, "a2.example", conflict="conflict", conflict_quotes=[A]),
              c(B, "b.example", conflict="conflict", conflict_quotes=[B]),
              c(B, "b2.example", conflict="conflict", conflict_quotes=[B])]
        md = sy.synthesize("q", route, cl, meta)
        self.assertIn("## 확인된 것 (0)", md)
        self.assertIn("## 상충 (2)", md)                   # 한쪽만 고르지 않는다
        self.assertIn("어느 쪽이 옳은지 이 도구는 모른다", md)
        self.assertEqual(sy.problems(md), [])
        self.assertEqual(g.offenders(md), [])

    def test_the_상충_section_still_blocks_a_tokenless_assertion(self):
        """섹션을 하나 열어 준 것이 게이트에 구멍을 낸 것은 아니어야 한다."""
        md = ("# q\n\n## 상충 (1)\n\n설명 문장은 주장이 아니다.\n\n"
              "- 토큰 없는 단정문이 여기 있다\n\n## 미확인 (0)\n\n## 감사 로그\n\n- x\n")
        self.assertTrue(g.offenders(md))


if __name__ == "__main__":
    unittest.main()
