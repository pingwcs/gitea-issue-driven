from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / ".agents" / "skills" / "gitea-pr-delivery" / "SKILL.md"
TEMPLATE = ROOT / ".agents" / "skills" / "gitea-pr-delivery" / "assets" / "pr-body-template.md"


class CloseOnMergeRuleTests(unittest.TestCase):
    def test_template_requires_a_conditional_close_reference(self):
        template = TEMPLATE.read_text(encoding="utf-8")
        self.assertIn("## Issue closure on merge", template)
        self.assertIn("Closes #<source-issue-number>", template)
        self.assertIn("Issue closure: not requested", template)

    def test_skill_blocks_unsafe_auto_closure(self):
        skill = SKILL.read_text(encoding="utf-8")
        self.assertIn("same Gitea repository, is open", skill)
        self.assertIn("not a decomposition parent/tracker", skill)
        self.assertIn("Do not call `issue_write(method=update, state=closed)`", skill)
        self.assertIn("do not merge the PR", skill)


if __name__ == "__main__":
    unittest.main()
