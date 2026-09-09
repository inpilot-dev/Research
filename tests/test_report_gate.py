"""Seam — the gate's verdict. A pure text function: report in, offending lines out."""
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import cite_check as cc  # noqa: E402
import report_gate as g  # noqa: E402

GOOD = """# 검증 리포트

## 검증됨 (2)

- [nejm.org:exact] The primary outcome was the time to recovery. — L2 · 2020-05-22 · https://nejm.org/a
- [who.int:fuzzy 0.91] Mortality did not fall in hospitalised patients. — L2 · 게시일 미상 · https://who.int/b

## 미확인 (1)

단정하지 않는다. 검증을 통과하지 못했다는 뜻이지 거짓이라는 뜻이 아니다.

- 확인 불가: The trial enrolled 1062 patients. — https://nejm.org/c
  · 막힌 곳: 칸 6 · 사유: bot-wall

## 감사 로그

- 입력 3건 · 페치 URL 3개
- 독립 퍼블리셔 2 (www. 제거한 호스트 기준)
"""


class Gate(unittest.TestCase):
    def test_a_clean_report_passes(self):
        self.assertEqual(g.offenders(GOOD), [])

    def test_a_real_rendered_report_passes(self):
        out = cc.check([{"claim": "The primary outcome was the time to recovery",
                         "url": "https://nejm.org/a"},
                        {"claim": "Nothing like this appears anywhere", "url": "https://nejm.org/a"}],
                       fetcher=lambda u, t: (200, "text/html",
                                             "<html><body><p>The primary outcome was the time to "
                                             "recovery.</p><p>Second sentence here.</p></body></html>"))
        self.assertEqual(g.offenders(cc.render(out)), [])

    def test_tables_headings_and_blank_lines_are_not_assertions(self):
        self.assertEqual(g.offenders("# 검증 리포트\n\n## 검증됨 (0)\n\n| a | b |\n|---|---|\n\n---\n"), [])

    def test_an_untokened_assertion_in_the_verified_section_is_blocked(self):
        bad = g.offenders(GOOD.replace(
            "- [who.int:fuzzy 0.91] Mortality did not fall in hospitalised patients.",
            "- Mortality did not fall in hospitalised patients."))
        self.assertEqual(len(bad), 1)
        self.assertIn("Mortality did not fall", bad[0][1])

    def test_prose_smuggled_into_the_verified_section_is_blocked(self):
        bad = g.offenders(GOOD.replace("## 검증됨 (2)\n",
                                       "## 검증됨 (2)\n\nRemdesivir is effective for every patient.\n"))
        self.assertEqual(len(bad), 1)
        self.assertIn("Remdesivir is effective", bad[0][1])

    def test_an_assertion_after_the_audit_log_heading_ends_is_blocked(self):
        bad = g.offenders(GOOD + "\n## 결론\n\n렘데시비르는 표준 치료로 확립되었다고 볼 수 있다.\n")
        self.assertEqual(len(bad), 1)
        self.assertIn("렘데시비르", bad[0][1])

    def test_unverified_lines_pass_without_a_token(self):
        self.assertEqual(g.offenders(GOOD.replace("- 확인 불가: The trial enrolled 1062 patients.",
                                                  "- 확인 불가: A sentence with no token at all here.")), [])

    def test_the_gate_only_judges_documents_that_claim_to_be_reports(self):
        self.assertFalse(g.looks_like_report("# 회의록\n\n오늘 배포는 미뤘다. 다음 주에 다시 본다.\n"))
        self.assertTrue(g.looks_like_report(GOOD))

    def test_a_heading_inside_a_code_fence_does_not_open_a_free_zone(self):
        md = GOOD.replace("## 미확인 (1)",
                          "```\n## 감사 로그\n```\n\n렘데시비르는 모든 환자의 사망을 완전히 예방한다.\n\n## 미확인 (1)")
        bad = g.offenders(md)
        self.assertEqual(len(bad), 1)
        self.assertIn("렘데시비르는 모든", bad[0][1])

    def test_a_heading_that_merely_contains_a_free_name_is_not_free(self):
        md = GOOD + "\n## 미확인 항목에 대한 우리의 결론\n\n렘데시비르는 코로나 사망률을 완전히 없앤다.\n"
        self.assertEqual(len(g.offenders(md)), 1)

    def test_prose_under_the_real_section_headings_is_allowed(self):
        for head in ("## 미확인 (2)", "## 감사 로그", "## 확인됐으나 기준 미달 (1)"):
            with self.subTest(head=head):
                self.assertEqual(g.offenders(f"# 검증 리포트\n\n{head}\n\n토큰 없는 설명 문장이 여기 있다.\n"), [])

    def test_an_item_under_미확인_without_a_reason_label_is_blocked(self):
        md = GOOD.replace("## 감사 로그", "- 렘데시비르는 모든 환자의 사망을 예방한다는 것이 확인됐다.\n\n## 감사 로그")
        bad = g.offenders(md)
        self.assertEqual(len(bad), 1)
        self.assertIn("모든 환자의 사망", bad[0][1])

    def test_a_claim_under_기준미달_still_needs_its_token(self):
        md = ("# 검증 리포트\n\n## 확인됐으나 기준 미달 (1)\n\n설명 문장은 통과한다.\n\n"
              "- 렘데시비르는 사망률을 낮췄다 — L2 · 퍼블리셔 1 · 단일 출처\n")
        self.assertEqual(len(g.offenders(md)), 1)

    def test_there_is_no_way_to_turn_the_gate_off(self):
        with open(os.path.join(os.path.dirname(__file__), "..", "scripts", "report_gate.py"),
                  encoding="utf-8") as f:
            src = f.read()
        for escape in ("environ", "getenv", "--force", "--no-gate", "skip", "bypass", "argparse"):
            self.assertNotIn(escape, src, f"게이트에 우회 경로가 생겼다: {escape}")


class WhatTheGateEngagesWith(unittest.TestCase):
    """#16 — 관여 여부는 정확해지되, 관여한 문서의 판정은 조금도 약해지지 않는다."""

    NAKED = "이 문장은 토큰이 없는 단정문이다 완전히."

    def doc(self, body):
        return f"# 어떤 문서\n\n{body}\n"

    def test_a_report_heading_inside_a_fence_does_not_engage_the_gate(self):
        md = self.doc("예시 출력:\n\n```\n## 검증됨 (1)\n- 아무 문장\n```\n\n" + self.NAKED)
        self.assertFalse(g.looks_like_report(md))

    def test_the_repo_s_own_docs_are_not_reports(self):
        """실제로 막혔던 것들이다 — README 는 펜스, SKILL.md 는 표 칸 안의 인라인 코드."""
        root = os.path.join(os.path.dirname(__file__), "..")
        for name in ("README.md", "CONTEXT.md", "skills/verify/SKILL.md", "evals/judge.md"):
            with self.subTest(name=name), open(os.path.join(root, name), encoding="utf-8") as f:
                self.assertFalse(g.looks_like_report(f.read()))

    def test_a_heading_outside_a_fence_still_engages(self):
        md = self.doc("## 검증됨 (0)\n\n" + self.NAKED)
        self.assertTrue(g.looks_like_report(md))
        self.assertTrue(g.offenders(md))          # 관여했으면 막는다

    def test_a_heading_both_inside_and_outside_engages(self):
        md = self.doc("```\n## 미확인 (9)\n```\n\n## 검증됨 (0)\n\n" + self.NAKED)
        self.assertTrue(g.looks_like_report(md))

    def test_an_unclosed_fence_engages_rather_than_hiding_the_document(self):
        """애매하면 막는 쪽이다 — 열린 펜스로 게이트를 통째로 끌 수 있으면 안 된다."""
        md = self.doc("```\n## 검증됨 (0)\n\n" + self.NAKED)
        self.assertTrue(g.looks_like_report(md))
        self.assertTrue(g.offenders(md))

    def test_a_short_inner_fence_does_not_close_a_longer_one(self):
        md = self.doc("````\n```\n## 검증됨 (0)\n```\n````\n\n" + self.NAKED)
        self.assertFalse(g.looks_like_report(md))

    def test_tilde_fences_work_the_same(self):
        md = self.doc("~~~\n## 검증됨 (0)\n~~~\n\n" + self.NAKED)
        self.assertFalse(g.looks_like_report(md))

    def test_the_fence_rule_is_defined_once(self):
        """offenders 와 looks_like_report 가 같은 함수를 쓴다 — 다시 갈라지면 #16 이 재발한다."""
        import inspect
        for fn in (g.offenders, g.looks_like_report):
            self.assertIn("prose_lines", inspect.getsource(fn))


if __name__ == "__main__":
    unittest.main()


class HookProtocol(unittest.TestCase):
    """훅은 Claude Code 와의 계약이다 — 차단은 종료 코드 2 와 deny 응답으로 나간다."""

    def run_hook(self, payload):
        import subprocess
        p = subprocess.run([sys.executable,
                            os.path.join(os.path.dirname(__file__), "..", "hooks", "gate.py")],
                           input=json.dumps(payload), capture_output=True, text=True)
        return p.returncode, p.stdout

    def test_an_untokened_report_is_denied_with_the_offending_line(self):
        code, out = self.run_hook({"tool_name": "Write", "tool_input": {
            "file_path": "/tmp/report.md",
            "content": "# 검증 리포트\n\n## 검증됨 (1)\n\n- Remdesivir cured everyone in the trial.\n"}})
        self.assertEqual(code, 2)
        d = json.loads(out)["hookSpecificOutput"]
        self.assertEqual(d["permissionDecision"], "deny")
        self.assertIn("Remdesivir cured everyone", d["permissionDecisionReason"])

    def test_a_clean_report_and_an_unrelated_file_both_pass(self):
        for content in (GOOD, "# 회의록\n\n오늘 배포는 미뤘다. 다음 주에 다시 본다.\n"):
            with self.subTest(content=content[:20]):
                code, _ = self.run_hook({"tool_name": "Write",
                                         "tool_input": {"file_path": "/tmp/x.md", "content": content}})
                self.assertEqual(code, 0)

    def test_an_edit_is_judged_on_the_text_it_would_leave_behind(self):
        code, _ = self.run_hook({"tool_name": "Edit", "tool_input": {
            "file_path": "/tmp/report-does-not-exist.md", "old_string": "x",
            "new_string": "## 검증됨 (1)\n\n- Mortality fell by half in the treatment arm.\n"}})
        self.assertEqual(code, 2)

    def test_appending_an_assertion_to_an_existing_report_is_not_free(self):
        """조각만 보면 제목이 없어 리포트로 안 보인다 — 결과 파일을 봐야 게이트가 산다."""
        import tempfile
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as f:
            f.write(GOOD)
        frag = "\n- 렘데시비르는 모든 환자의 사망을 완전히 예방한다는 것이 확인됐다.\n"
        code, out = self.run_hook({"tool_name": "Edit", "tool_input": {
            "file_path": f.name, "old_string": "## 감사 로그", "new_string": frag + "## 감사 로그"}})
        os.unlink(f.name)
        self.assertEqual(code, 2)
        self.assertIn("모든 환자의 사망", json.loads(out)["hookSpecificOutput"]["permissionDecisionReason"])

    def test_a_multi_edit_is_judged_on_the_whole_result(self):
        import tempfile
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as f:
            f.write(GOOD)
        code, _ = self.run_hook({"tool_name": "MultiEdit", "tool_input": {
            "file_path": f.name,
            "edits": [{"old_string": "## 감사 로그",
                       "new_string": "- 백신은 자폐를 유발한다는 것이 확인됐다.\n## 감사 로그"}]}})
        os.unlink(f.name)
        self.assertEqual(code, 2)

    def test_an_unreadable_payload_does_not_block_every_write(self):
        """하네스가 형식을 바꿨다고 모든 쓰기를 막으면 게이트가 아니라 고장이다."""
        import subprocess
        p = subprocess.run([sys.executable,
                            os.path.join(os.path.dirname(__file__), "..", "hooks", "gate.py")],
                           input="not json at all", capture_output=True, text=True)
        self.assertEqual(p.returncode, 0)
