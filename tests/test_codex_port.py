"""Seam — the Codex surface. Two things can rot silently here, so they are tests.

1. Frontmatter drift. `.agents/skills/<n>/SKILL.md` must announce itself exactly as the
   Claude Code skill does, or the two harnesses fire on different things.
2. The honest label. Codex has no PreToolUse hook, so the write gate is gone. If that
   warning ever falls out of the Codex docs we are shipping a weak gate quietly — which
   is the one thing this port was not allowed to do.
"""
import os
import re
import unittest

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
SKILLS = ("verify", "research")


def read(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    assert m, "SKILL.md must open with YAML frontmatter"
    return dict(re.findall(r"^(name|description):\s*(.+)$", m.group(1), re.M))


class CodexSkills(unittest.TestCase):
    def test_frontmatter_matches_the_claude_code_skill(self):
        for name in SKILLS:
            with self.subTest(name):
                mine = frontmatter(read(".agents", "skills", name, "SKILL.md"))
                theirs = frontmatter(read("skills", name, "SKILL.md"))
                self.assertEqual(mine.get("name"), name)
                self.assertEqual(mine, theirs)

    def test_procedure_is_not_copied_but_pointed_at(self):
        """The core is shared; so is the procedure. A second copy drifts from the first."""
        for name in SKILLS:
            with self.subTest(name):
                text = read(".agents", "skills", name, "SKILL.md")
                self.assertIn("../../../skills/%s/SKILL.md" % name, text)
                self.assertLess(len(text), len(read("skills", name, "SKILL.md")))

    def test_says_the_write_gate_is_gone_and_how_to_run_it_by_hand(self):
        for doc in [read("AGENTS.md")] + [read(".agents", "skills", n, "SKILL.md") for n in SKILLS]:
            self.assertIn("게이트가 없다", doc)
            self.assertIn("scripts/report_gate.py", doc)

    def test_readme_and_agents_md_carry_the_same_warning(self):
        self.assertIn("두 하네스", read("README.md"))
        for word in ("근거 없음", "확인 불가", "자격증명은 성역"):
            self.assertIn(word, read("AGENTS.md"))


class ClaudeCodeUnchanged(unittest.TestCase):
    def test_the_hook_is_still_wired(self):
        self.assertIn("hooks/gate.py", read(".claude-plugin", "plugin.json"))


if __name__ == "__main__":
    unittest.main()
