"""Seam — question → research type → reliability settings. A table test, no network, no LLM."""
import io
import json
import os
import sys
import unittest
from contextlib import redirect_stdout

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import route as r  # noqa: E402

ACADEMIC = [
    "렘데시비르 무작위 시험의 일차 평가변수가 뭐였어?",
    "이 주장에 대한 메타분석이 있나?",
    "What does the systematic review say about statin adherence?",
    "Find the cohort study behind this p-value claim",
    "이 논문 DOI 로 원문 확인해줘",
    "arxiv 에 올라온 후속 연구가 있는지",
]
TECH = [
    "How do I use the streaming endpoint in this SDK?",
    "pip 로 설치한 라이브러리 버전이 뭐가 최신이야",
    "이 함수 파라미터가 어떻게 바뀌었는지 changelog 봐줘",
    "Is this API flag deprecated?",
    "migration guide 대로 하면 되는 거 맞아?",
]
QUICK = [
    "이 회사 설립 연도가 언제야",
    "When did the release date land?",
    "How many countries signed it?",
    "Who was the first person to hold that post?",
    "capital of that province 확인해줘",
]
UNSUPPORTED = [
    "오늘 점심 뭐 먹을까",
    "이거 어떻게 생각해?",
    "좀 도와줘",
]


class Route(unittest.TestCase):
    def kind(self, q):
        return r.route(q)["type"]

    def test_academic_questions_route_to_academic_literature(self):
        for q in ACADEMIC:
            with self.subTest(q=q):
                self.assertEqual(self.kind(q), "academic-literature")

    def test_technical_questions_route_to_tech_docs(self):
        for q in TECH:
            with self.subTest(q=q):
                self.assertEqual(self.kind(q), "tech-docs")

    def test_short_factual_questions_route_to_quick_facts(self):
        for q in QUICK:
            with self.subTest(q=q):
                self.assertEqual(self.kind(q), "quick-facts")

    def test_an_unrecognised_question_gets_the_strictest_setting_and_says_so(self):
        for q in UNSUPPORTED:
            with self.subTest(q=q):
                out = r.route(q)
                self.assertEqual(out["matched"], {})
                self.assertEqual(out["settings"]["strictness"], 3)
                self.assertIn("미지원", out["reason"])

    def test_a_mixed_question_takes_the_strictest_type_never_the_looser_one(self):
        mixed = [("이 라이브러리를 쓴 논문이 있는지 API 문서랑 같이 확인해줘", "academic-literature"),
                 ("When did the study release date land?", "academic-literature"),
                 ("이 SDK 설립 연도가 언제야", "tech-docs")]
        for q, expect in mixed:
            with self.subTest(q=q):
                out = r.route(q)
                self.assertGreater(len(out["matched"]), 1, "두 유형이 다 잡혀야 혼합 테스트가 성립한다")
                self.assertEqual(out["type"], expect)
                self.assertIn("가장 엄격한", out["reason"])

    def test_every_type_carries_the_settings_a_report_needs(self):
        p = r.load()
        for name, t in p["types"].items():
            with self.subTest(type=name):
                for key in ("strictness", "label", "depth", "min_independent_publishers",
                            "require_publication_date", "uncertainty", "sources", "signals"):
                    self.assertIn(key, t)
                self.assertIn(t["depth"], ("L1", "L2", "L3"))
        self.assertEqual(len(p["types"]), 3)
        self.assertEqual(len(p["reserved"]), 6)          # 9유형 슬롯 중 v1은 셋
        self.assertIn(p["unsupported_default"], p["types"])

    def test_the_strictest_type_is_the_unsupported_default(self):
        p = r.load()
        self.assertEqual(p["unsupported_default"],
                         max(p["types"], key=lambda n: p["types"][n]["strictness"]))

    def test_settings_live_in_data_not_in_code(self):
        with open(os.path.join(os.path.dirname(__file__), "..", "scripts", "route.py"),
                  encoding="utf-8") as f:
            src = f.read()
        for leaked in ("pubmed", "arxiv", "npm", "systematic review"):
            self.assertNotIn(leaked, src, "유형 세팅이 코드로 새어 들어왔다 (ADR 0002)")

    def test_cli_prints_the_decision_as_json(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            self.assertEqual(r.main(["이 논문 결과 확인해줘"]), 0)
        d = json.loads(buf.getvalue())
        self.assertEqual(set(d), {"type", "settings", "matched", "reason"})


if __name__ == "__main__":
    unittest.main()
