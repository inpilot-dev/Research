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

    def test_there_is_no_way_to_turn_the_gate_off(self):
        with open(os.path.join(os.path.dirname(__file__), "..", "scripts", "report_gate.py"),
                  encoding="utf-8") as f:
            src = f.read()
        for escape in ("environ", "getenv", "--force", "--no-gate", "skip", "bypass", "argparse"):
            self.assertNotIn(escape, src, f"게이트에 우회 경로가 생겼다: {escape}")


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
            "file_path": "/tmp/report.md", "old_string": "x",
            "new_string": "## 검증됨 (1)\n\n- Mortality fell by half in the treatment arm.\n"}})
        self.assertEqual(code, 2)

    def test_an_unreadable_payload_does_not_block_every_write(self):
        """하네스가 형식을 바꿨다고 모든 쓰기를 막으면 게이트가 아니라 고장이다."""
        import subprocess
        p = subprocess.run([sys.executable,
                            os.path.join(os.path.dirname(__file__), "..", "hooks", "gate.py")],
                           input="not json at all", capture_output=True, text=True)
        self.assertEqual(p.returncode, 0)
