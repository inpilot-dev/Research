"""Seam — 사전등록 평가변수 ↔ 논문 보고 결과. 가짜 등록·논문 쌍만 쓴다. 네트워크도 LLM 도 없다.

세 경로를 본다: 일치 · 다름 · 확인 불가. 그리고 그 셋이 서로 새지 않는지를 본다 —
논문을 못 읽은 것이 `다름` 으로 나오면 그것이 이 제품에서 가장 큰 결함이다 (ADR 0002·0003).
"""
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import adapters as ad  # noqa: E402
import prereg as pr  # noqa: E402
import report_gate as g  # noqa: E402

NCT = "NCT04280705"
PMID = "32445440"

# 논문이 스스로 "primary outcome" 이라고 적은 문장이 대조의 기준이다.
PAPER = ("BACKGROUND: We evaluated an antiviral agent. METHODS: The primary outcome was the time to "
         "recovery, defined as the first day on which the patient satisfied category 1, 2, or 3. "
         "RESULTS: Those who received the drug had a median recovery time of 10 days, as compared "
         "with 15 days among those who received placebo. Mortality by day 14 was 6.7% versus 11.9%. "
         "The trial is registered with ClinicalTrials.gov, number NCT04280705.")
PAPER_NO_PRIMARY = ("BACKGROUND: We evaluated an antiviral agent. RESULTS: Median recovery took 10 "
                    "days versus 15 days. Mortality by day 14 was 6.7% versus 11.9%.")


def record(primary, secondary=(), registered="2020-02-19", start="2020-02-21"):
    """ClinicalTrials.gov API v2 응답의 모양만 흉내 낸다 — 평가변수는 객체 목록이다."""
    def outs(rows):
        return [{"measure": m, "timeFrame": tf, "description": ""} for m, tf in rows]
    return json.dumps({"protocolSection": {
        "identificationModule": {"nctId": NCT, "officialTitle": "Adaptive COVID-19 Treatment Trial"},
        "statusModule": {"studyFirstSubmitDate": registered,
                         "startDateStruct": {"date": start},
                         "primaryCompletionDateStruct": {"date": "2020-04-28"}},
        "outcomesModule": {"primaryOutcomes": outs(primary), "secondaryOutcomes": outs(secondary)}}})


MATCHING = [("Time to recovery", "Day 1 through Day 29")]
SWITCHED = [("Percentage of subjects reporting each severity rating on an 8-point ordinal scale",
             "Day 15")]


def getter(body, status=200):
    def get(url, timeout=10):
        return (status, {}, body if status and 200 <= status < 400 else "")
    return get


def paper_registry(text=PAPER, status=200):
    """논문 어댑터. 실제 sources/*.json 을 그대로 쓰고 응답만 가짜다."""
    def get(url, timeout=10):
        return (status, {}, text if status and 200 <= status < 400 else "")
    return ad.Registry(getter=get, sleeper=lambda s: None)


def run(primary=MATCHING, secondary=(), paper=PAPER, paper_status=200, registry_status=200,
        judge=None, tokens=(NCT, PMID), **kw):
    return pr.run(list(tokens), judge=judge,
                  getter=getter(record(primary, secondary, **kw), registry_status),
                  registry=paper_registry(paper, paper_status))


class Match(unittest.TestCase):
    def test_the_registered_primary_outcome_is_found_in_the_paper(self):
        out = run()
        row = out["rows"][0]
        self.assertEqual((row["verdict"], row["how"]), ("일치", "exact"))
        self.assertEqual(out["summary"]["일치"], 1)
        self.assertEqual(out["summary"]["다름"], 0)
        self.assertEqual(out["registry"]["id"], NCT)

    def test_the_time_frame_comes_with_the_outcome(self):
        """평가변수는 문자열이 아니라 measure·timeFrame 의 짝이다 — 짝이 깨지면 대조가 무의미하다."""
        out = run()
        self.assertEqual(out["registry"]["primary"][0]["time_frame"], "Day 1 through Day 29")
        self.assertFalse(out["rows"][0]["time_frame_in_paper"])   # 논문에 그 시점 문구는 없다

    def test_the_nct_number_can_come_from_the_paper_itself(self):
        out = run(tokens=(PMID,))
        self.assertEqual(out["registry"]["id"], NCT)
        self.assertEqual(out["rows"][0]["verdict"], "일치")


class Differs(unittest.TestCase):
    def test_a_registered_outcome_absent_from_the_paper_primary_sentence_is_다름(self):
        out = run(primary=SWITCHED)
        row = out["rows"][0]
        self.assertEqual(row["verdict"], "다름")
        self.assertIn("primary outcome was the time to recovery", row["paper_primary"])
        self.assertFalse(row["elsewhere_in_paper"])
        self.assertEqual(out["summary"]["다름"], 1)

    def test_it_names_what_differs_and_nothing_else(self):
        md = pr.render(run(primary=SWITCHED))
        self.assertIn("8-point ordinal scale", md)          # 등록 쪽 문구
        self.assertIn("Day 15", md)                          # 측정 시점
        self.assertIn("논문이 일차로 적은 문장", md)             # 논문 쪽 문구
        for word in ("조작", "속임", "속였", "부정행위", "은폐", "의심스", "위반", "거짓", "기만"):
            self.assertNotIn(word, md, f"판단 문구가 리포트에 들어갔다: {word}")

    def test_a_registered_secondary_showing_up_as_the_paper_primary_is_reported(self):
        out = run(primary=SWITCHED, secondary=[("Time to recovery", "Day 29")])
        self.assertEqual(out["summary"]["promoted_secondary"], 1)
        self.assertIn("등록 시 이차", pr.render(out))

    def test_an_outcome_only_elsewhere_in_the_paper_is_said_so(self):
        out = run(primary=[("Mortality by day 14", "Day 14")])
        row = out["rows"][0]
        self.assertEqual(row["verdict"], "다름")
        self.assertTrue(row["elsewhere_in_paper"])
        self.assertIn("다른 곳에는 나타납니다", pr.render(out))


class Blocked(unittest.TestCase):
    def test_an_unreadable_paper_is_확인_불가_not_다름(self):
        out = run(primary=SWITCHED, paper_status=404)
        row = out["rows"][0]
        self.assertEqual(row["verdict"], "확인 불가")
        self.assertIn("논문 원문을 읽지 못했습니다", row["reason"])
        self.assertEqual((out["summary"]["다름"], out["summary"]["확인 불가"]), (0, 1))

    def test_a_paper_that_never_says_which_outcome_was_primary_is_확인_불가(self):
        out = run(primary=SWITCHED, paper=PAPER_NO_PRIMARY)
        self.assertEqual(out["rows"][0]["verdict"], "확인 불가")
        self.assertIn("일차 평가변수를 밝힌 문장", out["rows"][0]["reason"])

    def test_an_unreadable_registry_is_확인_불가(self):
        out = run(registry_status=500)
        self.assertEqual(out["rows"][0]["verdict"], "확인 불가")
        self.assertIn("레지스트리 응답 실패", out["summary"]["registry_error"])

    def test_no_nct_anywhere_is_확인_불가(self):
        out = run(tokens=(PMID,), paper=PAPER_NO_PRIMARY)
        self.assertEqual(out["rows"][0]["verdict"], "확인 불가")
        self.assertIn("NCT 번호를 찾지 못했습니다", out["summary"]["registry_error"])


class Registration(unittest.TestCase):
    def test_registering_after_the_trial_started_is_flagged(self):
        out = run(registered="2020-06-01", start="2020-02-21")
        self.assertIs(out["summary"]["retrospective_registration"], True)
        self.assertIn("사후 등록", pr.render(out))

    def test_registering_before_the_trial_started_is_not(self):
        self.assertIs(run()["summary"]["retrospective_registration"], False)

    def test_a_partial_date_is_compared_only_as_far_as_it_is_known(self):
        """'2020-02' 를 '2020-02-01' 로 채우면 같은 달에 시작한 시험이 사후 등록으로 찍힌다."""
        self.assertFalse(pr._after("2020-02-19", "2020-02"))
        self.assertTrue(pr._after("2020-03-19", "2020-02"))

    def test_missing_dates_are_not_a_verdict(self):
        out = run(registered="", start="")
        self.assertIsNone(out["summary"]["retrospective_registration"])
        self.assertIn("판정하지 않습니다", out["summary"]["registration_dates"])


class Judge:
    name = "fake-judge"

    def __init__(self, verdict):
        self.verdict, self.seen = verdict, []

    def __call__(self, claim, text):
        self.seen.append(claim)
        if isinstance(self.verdict, Exception):
            raise self.verdict
        supported, quote = self.verdict
        return {"critique": "…", "quote": quote, "supported": supported}


SENT = ("The primary outcome was the time to recovery, defined as the first day on which the "
        "patient satisfied category 1, 2, or 3.")


class L3(unittest.TestCase):
    def test_a_judge_can_turn_다름_into_일치_with_a_quote_from_the_paper(self):
        j = Judge((True, SENT))
        out = run(primary=[("Time to clinical improvement", "Day 29")], judge=j)
        row = out["rows"][0]
        self.assertEqual((row["verdict"], row["how"]), ("일치", "entails"))
        self.assertEqual(row["quote"], SENT)
        self.assertEqual(out["summary"]["l3"]["supported"], 1)
        self.assertIn("근거 문장(원문에 있는지 기계가 재확인)", pr.render(out))

    def test_a_forged_quote_is_thrown_away(self):
        j = Judge((True, "The primary outcome was mortality at ninety days in every subgroup."))
        out = run(primary=[("Time to clinical improvement", "Day 29")], judge=j)
        self.assertEqual(out["rows"][0]["verdict"], "다름")
        self.assertEqual(out["rows"][0]["l3_error"], "근거 문장이 원문에 없음")

    def test_a_judge_never_sees_a_paper_we_could_not_read(self):
        """모델이 확인 불가를 뒤집을 수 없다 (ADR 0002)."""
        j = Judge((True, SENT))
        out = run(primary=SWITCHED, paper_status=404, judge=j)
        self.assertEqual(out["rows"][0]["verdict"], "확인 불가")
        self.assertEqual(j.seen, [])
        self.assertNotIn("l3", out["summary"])

    def test_a_judge_that_raises_leaves_the_l2_result(self):
        out = run(primary=SWITCHED, judge=Judge(RuntimeError("boom")))
        self.assertEqual(out["rows"][0]["verdict"], "다름")
        self.assertEqual(out["summary"]["l3"]["failed"], 1)
        self.assertIn("L3 실패", pr.render(out))


class Report(unittest.TestCase):
    def test_the_hook_gate_lets_every_path_through(self):
        """리포트가 게이트를 통과한다 — 토큰 없는 단정문이 여기서도 나가지 않는다 (ADR 0003)."""
        for name, out in (("일치", run()), ("다름", run(primary=SWITCHED)),
                          ("확인 불가", run(paper_status=404)),
                          ("이차 승격", run(primary=SWITCHED,
                                          secondary=[("Time to recovery", "Day 29")]))):
            with self.subTest(name=name):
                md = pr.render(out)
                self.assertTrue(g.looks_like_report(md))
                self.assertEqual(g.offenders(md), [])

    def test_the_audit_log_says_where_everything_came_from(self):
        md = pr.render(run())
        self.assertIn("어댑터 clinicaltrials", md)
        self.assertIn("어댑터 pubmed", md)
        self.assertIn("등록 평가변수: 일차 1", md)

    def test_the_cli_prints_json_and_markdown(self):
        import io
        from contextlib import redirect_stdout
        for flags, needle in (([], '"verdict"'), (["--report"], "## 대조")):
            with self.subTest(flags=flags):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    code = pr.main([NCT, PMID] + flags, getter=getter(record(MATCHING)),
                                   registry=paper_registry())
                self.assertEqual(code, 0)
                self.assertIn(needle, buf.getvalue())


class Config(unittest.TestCase):
    def test_the_paths_live_in_the_adapter_json_not_in_the_code(self):
        """도메인·출처는 데이터다 (ADR 0002) — 경로를 코드에서 찾으면 실패한다."""
        adapter = next(a for a in ad.load() if a["name"] == "clinicaltrials")
        self.assertIn("outcomesModule", adapter["structured"]["primary_outcomes"])
        with open(os.path.join(os.path.dirname(__file__), "..", "scripts", "prereg.py"),
                  encoding="utf-8") as f:
            src = f.read()
        for path in ("outcomesModule", "primaryOutcomes", "timeFrame", "studyFirstSubmitDate"):
            self.assertFalse(f'"{path}' in src or f"'{path}" in src,
                             f"{path} 가 코드에 문자열로 박혔다 — sources/*.json 에 있어야 한다")

    def test_an_adapter_without_the_structured_block_is_skipped_not_crashed(self):
        rec, why = pr.fetch_registry(PMID, getter(record(MATCHING)))
        self.assertIsNone(rec)
        self.assertIn("어댑터를 찾지 못했습니다", why)


if __name__ == "__main__":
    unittest.main()
