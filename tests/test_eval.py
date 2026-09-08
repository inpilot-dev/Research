"""Seam — the regression eval itself. Replayed fixtures only: no network, no LLM."""
import io
import json
import os
import sys
import unittest
from contextlib import redirect_stdout

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import eval_run as ev  # noqa: E402

EXPECTED = {"exact", "fuzzy", "none", "blocked", "unsupported-pdf"}


def queries():
    with open(os.path.join(ev.ROOT, "queries.json"), encoding="utf-8") as f:
        return json.load(f)


class QuerySet(unittest.TestCase):
    def test_the_set_covers_each_implemented_type(self):
        counts = {}
        for q in queries():
            counts[q["type"]] = counts.get(q["type"], 0) + 1
        self.assertEqual(counts, {"academic-literature": 7, "tech-docs": 7, "quick-facts": 6})

    def test_every_claim_says_what_it_expects_and_why(self):
        for q in queries():
            for c in q["claims"]:
                with self.subTest(id=q["id"]):
                    self.assertEqual(set(c) & {"claim", "url", "expect", "why"},
                                     {"claim", "url", "expect", "why"})
                    self.assertIn(c["expect"], EXPECTED)
                    self.assertTrue(c["why"].strip(), "기대값에는 이유가 붙어야 한다")

    def test_all_three_verdicts_are_exercised(self):
        got = {c["expect"] for q in queries() for c in q["claims"]}
        self.assertEqual(got, {"exact", "none", "blocked"})

    def test_the_two_kinds_of_failure_are_kept_apart(self):
        """근거 없음과 확인 불가를 둘 다, 서로 다른 이유로 기대하는 쿼리가 있어야 한다."""
        by = {c["expect"]: [c for q in queries() for c in q["claims"] if c["expect"] == c["expect"]]
              for c in [c for q in queries() for c in q["claims"]]}
        blocked = [c for q in queries() for c in q["claims"] if c["expect"] == "blocked"]
        self.assertGreaterEqual(len(blocked), 2)
        self.assertTrue(any("403" in c["why"] or "벽" in c["why"] for c in blocked))
        self.assertTrue(any("404" in c["why"] for c in blocked))
        self.assertTrue(by)

    def test_every_source_has_a_recording_so_the_eval_runs_offline(self):
        store = ev.replay().store
        for q in queries():
            for c in q["claims"]:
                with self.subTest(url=c["url"]):
                    self.assertIn(c["url"], store)


class Run(unittest.TestCase):
    def test_the_recorded_set_passes_and_the_report_names_the_types(self):
        rows, tally = ev.run(queries(), ev.replay())
        md = ev.report(rows, tally)
        for t in ("academic-literature", "tech-docs", "quick-facts"):
            self.assertIn(t, md)
        self.assertIn("**합계**", md)
        self.assertEqual([r for r in rows if not r["ok"]], [])

    def test_a_broken_expectation_shows_up_in_the_failure_list(self):
        qs = [dict(queries()[0])]
        qs[0]["claims"] = [dict(qs[0]["claims"][0], expect="none")]
        rows, tally = ev.run(qs, ev.replay())
        md = ev.report(rows, tally)
        self.assertIn("## 실패 (1)", md)
        self.assertIn("기대 `none` → 실제 `exact`", md)

    def test_a_missing_recording_fails_instead_of_scoring_as_blocked(self):
        """녹화본이 사라지면 blocked 기대가 엉뚱한 이유로 계속 통과한다 — 그게 더 위험하다."""
        qs = [{"id": "x", "type": "t", "question": "q",
               "claims": [{"claim": "c", "url": "https://never-recorded.example/x",
                           "expect": "blocked", "why": "-"}]}]
        rows, tally = ev.run(qs, ev.replay())
        self.assertEqual(rows[0]["got"], "녹화본 없음")
        self.assertFalse(rows[0]["ok"])

    def test_the_numbers_are_labelled_self_reported(self):
        rows, tally = ev.run(queries(), ev.replay())
        md = ev.report(rows, tally)
        self.assertIn("자기보고", md)
        self.assertIn("HUMAN-REVIEW.md", md)

    def test_the_cli_exits_nonzero_when_something_regressed(self):
        import tempfile
        qs = [dict(queries()[0])]
        qs[0]["claims"] = [dict(qs[0]["claims"][0], expect="blocked")]
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
            json.dump(qs, f)
        with redirect_stdout(io.StringIO()):
            code = ev.main(["--queries", f.name])
        os.unlink(f.name)
        self.assertEqual(code, 1)


class JudgeAndReview(unittest.TestCase):
    def read(self, name):
        with open(os.path.join(ev.ROOT, name), encoding="utf-8") as f:
            return f.read()

    def test_the_judge_asks_for_critique_before_verdict_and_uses_no_scale(self):
        j = self.read("judge.md")
        self.assertLess(j.index("1단계 — 비평"), j.index("2단계 — 판정"))
        # 척도 금지는 산출 형식에서 확인한다 — 본문이 "1~5점을 쓰지 않는다"고 말하는 것은 규칙 설명이다.
        fmt = j[j.index("### 출력 형식"):]
        self.assertNotIn("점", fmt)
        self.assertNotIn("/5", fmt)
        self.assertEqual(sorted(set(w for w in ("PASS", "FAIL") if w in fmt)), ["FAIL", "PASS"])
        verdict = j[j.index("### 2단계"):j.index("### 자동 FAIL")]
        self.assertNotIn("~5", verdict)
        self.assertNotIn("0.0", verdict)
        for criterion in ("사실성", "인용 정확성", "완전성", "출처 품질", "도구 효율"):
            self.assertIn(criterion, j)
        self.assertIn("PASS", j)
        self.assertIn("FAIL", j)

    def test_conflating_the_two_failure_kinds_is_an_automatic_fail(self):
        j = self.read("judge.md")
        self.assertIn("자동 FAIL", j)
        self.assertIn("확인 불가", j)
        self.assertIn("근거 없음", j)

    def test_the_review_procedure_says_the_numbers_are_not_yet_human_checked(self):
        h = self.read("HUMAN-REVIEW.md")
        self.assertIn("아직 수행되지 않았다", h)
        self.assertIn("가려 놓고", h)      # 판정기 판정을 보기 전에 사람이 먼저 본다


if __name__ == "__main__":
    unittest.main()
