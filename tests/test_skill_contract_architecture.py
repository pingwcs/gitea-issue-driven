from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / ".agents" / "skills"
PROFILE = SKILLS / "gitea-connector-profile.md"
REMOTE_SKILLS = (
    "gitea-issue-decomposition",
    "gitea-issue-triage",
    "gitea-issue-execution",
    "gitea-pr-delivery",
)
BASELINE_TOOL_NAMES = (
    "issue_read",
    "issue_write",
    "label_read",
    "list_issues",
    "list_pull_requests",
    "pull_request_read",
    "pull_request_write",
)


class SkillContractArchitectureTests(unittest.TestCase):
    def test_remote_skills_share_one_connector_profile(self):
        profile = PROFILE.read_text(encoding="utf-8")
        self.assertIn("The live schema is authoritative", profile)
        for tool_name in BASELINE_TOOL_NAMES:
            self.assertIn(tool_name, profile)

        for skill_name in REMOTE_SKILLS:
            skill_dir = SKILLS / skill_name
            skill = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
            contract_path = skill_dir / "references" / "capability-contract.md"
            contract = contract_path.read_text(encoding="utf-8")

            self.assertIn("../gitea-connector-profile.md", skill)
            self.assertIn("references/capability-contract.md", skill)
            self.assertIn("../../gitea-connector-profile.md", contract)
            for tool_name in BASELINE_TOOL_NAMES:
                self.assertNotIn(tool_name, contract)

    def test_legacy_per_skill_mcp_contracts_are_removed(self):
        for skill_name in REMOTE_SKILLS:
            legacy = SKILLS / skill_name / "references" / "mcp-contract.md"
            self.assertFalse(legacy.exists(), str(legacy))

    def test_evidence_skill_stays_outside_mcp_boundary(self):
        evidence = (SKILLS / "gitea-issue-evidence" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("does not use the shared Gitea connector profile", evidence)
        self.assertFalse(
            (SKILLS / "gitea-issue-evidence" / "references" / "capability-contract.md").exists()
        )


if __name__ == "__main__":
    unittest.main()
