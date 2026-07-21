from __future__ import annotations

import importlib.util
import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


collector = load_module(
    "collect_attachments",
    ROOT / ".agents" / "skills" / "gitea-issue-evidence" / "scripts" / "collect_attachments.py",
)
logs = load_module(
    "analyze_logs",
    ROOT / ".agents" / "skills" / "gitea-issue-evidence" / "scripts" / "analyze_logs.py",
)


class TeaCredentialTests(unittest.TestCase):
    @mock.patch.object(collector.shutil, "which", return_value="tea")
    @mock.patch.object(collector.subprocess, "run")
    def test_uses_tea_helper_and_keeps_token_out_of_command(self, run, _which):
        run.return_value = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout="protocol=https\nhost=git.example.com\nusername=bot\npassword=super-secret\n",
            stderr="",
        )

        login, token = collector.resolve_tea_token("https://git.example.com", "work")

        self.assertEqual("work", login)
        self.assertEqual("super-secret", token)
        command = run.call_args.args[0]
        self.assertEqual(["tea", "login", "helper", "get", "--login", "work"], command)
        self.assertNotIn(token, " ".join(command))
        self.assertEqual("protocol=https\nhost=git.example.com\n\n", run.call_args.kwargs["input"])

    @mock.patch.object(collector.shutil, "which", return_value=None)
    def test_missing_tea_is_a_hard_error(self, _which):
        with self.assertRaisesRegex(collector.EvidenceError, "not found"):
            collector.resolve_tea_token("https://git.example.com", None)

    @mock.patch.object(collector.shutil, "which", return_value="tea")
    @mock.patch.object(collector.subprocess, "run")
    def test_rejects_mismatched_origin(self, run, _which):
        run.return_value = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout="protocol=https\nhost=evil.example\nusername=bot\npassword=secret\n",
            stderr="",
        )
        with self.assertRaisesRegex(collector.EvidenceError, "does not match"):
            collector.resolve_tea_token("https://git.example.com", None)

    @mock.patch.object(collector.shutil, "which", return_value="tea")
    @mock.patch.object(collector.subprocess, "run")
    def test_missing_tea_token_is_a_hard_error(self, run, _which):
        run.return_value = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout="protocol=https\nhost=git.example.com\nusername=bot\n",
            stderr="",
        )
        with self.assertRaisesRegex(collector.EvidenceError, "no token"):
            collector.resolve_tea_token("https://git.example.com", None)

    @mock.patch.object(collector, "resolve_tea_token", return_value=("work", "super-secret"))
    def test_credential_preflight_needs_no_issue_files_and_exposes_no_token(self, _resolve):
        output = io.StringIO()
        argv = [
            "collect_attachments.py",
            "--base-url",
            "https://git.example.com",
            "--tea-login",
            "work",
            "--credential-check-only",
        ]
        with mock.patch.object(sys, "argv", argv), contextlib.redirect_stdout(output):
            result = collector.main()
        self.assertEqual(0, result)
        self.assertIn("credential gate passed", output.getvalue())
        self.assertNotIn("super-secret", output.getvalue())


class EvidenceSafetyTests(unittest.TestCase):
    def test_redacts_attachment_query_values(self):
        safe = collector.redacted_url("https://git.example.com/a.png?token=abc&sig=def#fragment")
        self.assertNotIn("abc", safe)
        self.assertNotIn("def", safe)
        self.assertNotIn("fragment", safe)

    def test_redacts_log_secrets(self):
        safe = logs.redact("ERROR token=abc password:xyz Authorization: Bearer qwerty")
        self.assertNotIn("abc", safe)
        self.assertNotIn("xyz", safe)
        self.assertNotIn("qwerty", safe)


class PriorityTests(unittest.TestCase):
    def test_security_label_wins_over_bug(self):
        script = ROOT / ".agents" / "skills" / "gitea-issue-triage" / "scripts" / "prioritize_issue.py"
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "priority.json"
            completed = subprocess.run(
                [sys.executable, str(script), "--labels", "bug", "security", "--output", str(output)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, completed.returncode, completed.stderr)
            result = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual("P0", result["baseline_priority"])


if __name__ == "__main__":
    unittest.main()
