from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / ".agents" / "skills" / "gitea-issue-decomposition" / "scripts" / "reconcile_parent.py"
SPEC = importlib.util.spec_from_file_location("reconcile_parent", SCRIPT)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"could not load {SCRIPT}")
reconcile_parent = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(reconcile_parent)


class ParentReconciliationTests(unittest.TestCase):
    def setUp(self):
        self.children = reconcile_parent.validate_children(
            [
                {
                    "number": 11,
                    "title": "Add validation",
                    "url": "https://git.example.com/acme/app/issues/11",
                    "responsibility": "Validate input at the API boundary",
                    "depends_on": [],
                    "state": "open",
                },
                {
                    "number": 12,
                    "title": "Persist the accepted value",
                    "url": "https://git.example.com/acme/app/issues/12",
                    "responsibility": "Store only validated values",
                    "depends_on": [11],
                    "state": "open",
                },
            ]
        )

    def test_preserves_original_parent_body(self):
        original = "Original requirements\n\nDo not rewrite this section."
        updated = reconcile_parent.reconcile(original, reconcile_parent.render(self.children))
        self.assertTrue(updated.startswith(original))
        self.assertEqual(1, updated.count(reconcile_parent.START))
        self.assertIn("[#11]", updated)
        self.assertIn("Depends on: #11", updated)

    def test_reconciliation_is_idempotent(self):
        block = reconcile_parent.render(self.children)
        once = reconcile_parent.reconcile("Original", block)
        twice = reconcile_parent.reconcile(once, block)
        self.assertEqual(once, twice)

    def test_rejects_duplicate_child_numbers(self):
        with self.assertRaisesRegex(reconcile_parent.ReconcileError, "duplicate"):
            reconcile_parent.validate_children(
                [
                    {"number": 11, "title": "One", "responsibility": "First"},
                    {"number": 11, "title": "Two", "responsibility": "Second"},
                ]
            )


if __name__ == "__main__":
    unittest.main()
