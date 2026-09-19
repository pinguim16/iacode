from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = PROJECT_ROOT / "scripts" / "development-ledger"
sys.path.insert(0, str(SCRIPTS))

from ledger_common import redact_text  # noqa: E402


NOW = "2026-09-19T12:00:00Z"
REQUIRED_MARKDOWN = {
    "STATUS.md": "# Status\n\nIN_PROGRESS\n",
    "HANDOFF.md": "# Handoff\n\nCurrent Gate: TEST\nCurrent Status: IN_PROGRESS\n\n## Objective\n\nValidate an isolated checkpoint fixture.\n\n## Validation commands\n\nRun the checkpoint validator.\n",
    "PLAN.md": "# Plan\n\nValidate the fixture and preserve the source repository.\n",
    "DECISIONS.md": "# Decisions\n\nUse an isolated temporary Git repository.\n",
    "DIFF-SUMMARY.md": "# Diff Summary\n\nThe fixture contains only checkpoint validation data.\n",
    "RISKS.md": "# Risks\n\nTemporary repository setup could fail; test errors expose that failure.\n",
    "NEXT.md": "# Next\n\nContinue only after this isolated checkpoint validates successfully.\n",
}


def run(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)


class LedgerValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        shutil.copytree(PROJECT_ROOT / ".iacode", self.root / ".iacode")
        (self.root / "docs" / "checkpoints" / "TEST-CP-0001").mkdir(parents=True)
        self.checkpoint = self.root / "docs" / "checkpoints" / "TEST-CP-0001"
        self._write_fixture()
        self._git("init", "-b", "main")
        self._git("config", "user.name", "IACode Tests")
        self._git("config", "user.email", "iacode-tests@example.invalid")
        self._git("add", ".")
        self._git("commit", "-m", "test: create valid checkpoint fixture")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def _git(self, *args: str) -> None:
        completed = run(["git", *args], self.root)
        self.assertEqual(completed.returncode, 0, completed.stdout)

    def _write_json(self, name: str, value: object) -> None:
        (self.checkpoint / name).write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")

    def _write_fixture(self) -> None:
        for name, content in REQUIRED_MARKDOWN.items():
            (self.checkpoint / name).write_text(content, encoding="utf-8")
        (self.root / "docs" / "checkpoints" / "LATEST.md").write_text(
            "# Latest Checkpoint\n\nCheckpoint: `docs/checkpoints/TEST-CP-0001`\n",
            encoding="utf-8",
        )
        self._write_json("STATE.json", {
            "schemaVersion": "1.0.0", "phase": "test", "gate": "TEST", "status": "IN_PROGRESS",
            "branch": "main", "baseCommit": "UNBORN", "currentCommit": "HEAD", "dirty": False,
            "startedAt": NOW, "updatedAt": NOW, "nextAllowedAction": "Run validation.", "blockedBy": [],
        })
        self._write_json("RUN-METADATA.json", {
            "tool": "unittest", "toolVersion": sys.version.split()[0], "provider": "python",
            "model": "not-applicable", "effort": "not-applicable", "operatingSystem": sys.platform,
            "startedAt": NOW, "finishedAt": NOW, "branch": "main", "initialCommit": "UNBORN", "finalCommit": "HEAD",
        })
        command = {
            "timestamp": NOW, "command": "fixture validation", "workingDirectory": str(self.root),
            "exitCode": 0, "durationMs": 1, "stdoutArtifact": None, "stderrArtifact": None,
        }
        (self.checkpoint / "COMMANDS.jsonl").write_text(json.dumps(command) + "\n", encoding="utf-8")
        self._write_json("FILES.json", {
            "filesRead": [{"path": "START-HERE.md", "reason": "fixture input"}],
            "filesCreated": [], "filesModified": [], "filesDeleted": [],
        })
        result = {"executed": False, "passed": 0, "failed": 0, "command": None, "evidence": None}
        self._write_json("TESTS.json", {"schemaVersion": "1.0.0", "unit": result, "integration": result, "e2e": result})
        self._write_json("QUALITY.json", {
            "schemaVersion": "1.0.0", "build": "NOT_APPLICABLE", "unitTests": "NOT_EXECUTED",
            "integrationTests": "NOT_APPLICABLE", "e2e": "NOT_APPLICABLE", "lint": "NOT_EXECUTED",
            "staticAnalysis": "NOT_EXECUTED", "security": "NOT_EXECUTED", "documentation": "PASS",
            "checkpointValidation": "NOT_EXECUTED", "redTeam": "NOT_EXECUTED",
        })
        self._write_json("PROVENANCE.json", {
            "schemaVersion": "1.0.0",
            "artifacts": [{
                "artifact": "fixture", "sourceType": "test-generated", "provider": "python",
                "model": "not-applicable", "ownership": "project", "license": "project-policy",
                "rights": {"storageAllowed": True, "ragAllowed": False, "trainingAllowed": False, "distillationAllowed": False},
                "evidence": "Generated in an isolated temporary directory.", "notes": "Deleted after test.",
            }],
        })

    def _validate(self) -> subprocess.CompletedProcess[str]:
        return run([sys.executable, str(SCRIPTS / "validate_checkpoint.py"), "--root", str(self.root)], self.root)

    def test_valid_checkpoint_passes(self) -> None:
        result = self._validate()
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("CHECKPOINT_VALID", result.stdout)

    def test_missing_handoff_fails(self) -> None:
        (self.checkpoint / "HANDOFF.md").unlink()
        self.assertNotEqual(self._validate().returncode, 0)

    def test_invalid_json_fails(self) -> None:
        (self.checkpoint / "STATE.json").write_text("{invalid", encoding="utf-8")
        self.assertNotEqual(self._validate().returncode, 0)

    def test_invalid_status_fails(self) -> None:
        state = json.loads((self.checkpoint / "STATE.json").read_text(encoding="utf-8"))
        state["status"] = "ALMOST_DONE"
        self._write_json("STATE.json", state)
        self.assertNotEqual(self._validate().returncode, 0)

    def test_wrong_commit_fails(self) -> None:
        state = json.loads((self.checkpoint / "STATE.json").read_text(encoding="utf-8"))
        state["currentCommit"] = "0" * 40
        self._write_json("STATE.json", state)
        result = self._validate()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("commit mismatch", result.stdout)

    def test_latest_to_nonexistent_checkpoint_fails(self) -> None:
        (self.root / "docs" / "checkpoints" / "LATEST.md").write_text(
            "# Latest Checkpoint\n\nCheckpoint: `docs/checkpoints/DOES-NOT-EXIST`\n", encoding="utf-8"
        )
        self.assertNotEqual(self._validate().returncode, 0)

    def test_secret_present_fails(self) -> None:
        credential = "sk-" + ("a" * 20)
        with (self.checkpoint / "HANDOFF.md").open("a", encoding="utf-8") as stream:
            stream.write("\nUnsafe fixture value: " + credential + "\n")
        result = self._validate()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("secret pattern detected", result.stdout)
        self.assertNotIn(credential, result.stdout)

    def test_missing_provenance_fails(self) -> None:
        (self.checkpoint / "PROVENANCE.json").unlink()
        self.assertNotEqual(self._validate().returncode, 0)

    def test_missing_next_fails(self) -> None:
        (self.checkpoint / "NEXT.md").unlink()
        self.assertNotEqual(self._validate().returncode, 0)

    def test_redactor_replaces_known_shapes(self) -> None:
        source = "Authorization: Basic abcdefgh\nBearer abcdefghijkl\nAPI_KEY=abcdefghijkl\n" + "dw_live_" + ("x" * 12)
        redacted = redact_text(source)
        self.assertNotIn("abcdefghijkl", redacted)
        self.assertNotIn("dw_live_", redacted)
        self.assertGreaterEqual(redacted.count("[REDACTED]"), 4)


class LedgerLifecycleTests(unittest.TestCase):
    def test_new_finalize_commit_validate(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            shutil.copytree(PROJECT_ROOT / ".iacode", root / ".iacode")
            (root / "docs" / "checkpoints").mkdir(parents=True)
            init = run(["git", "init", "-b", "main"], root)
            self.assertEqual(init.returncode, 0, init.stdout)
            for key, value in (("user.name", "IACode Tests"), ("user.email", "iacode-tests@example.invalid")):
                self.assertEqual(run(["git", "config", key, value], root).returncode, 0)
            self.assertEqual(run(["git", "add", "."], root).returncode, 0)
            self.assertEqual(run(["git", "commit", "-m", "test: bootstrap"], root).returncode, 0)

            created = run([
                sys.executable, str(SCRIPTS / "new_checkpoint.py"), "--root", str(root),
                "--gate", "TEST", "--status", "IN_PROGRESS",
            ], root)
            self.assertEqual(created.returncode, 0, created.stdout)
            finalized = run([
                sys.executable, str(SCRIPTS / "finalize_checkpoint.py"), "--root", str(root),
                "--status", "READY_FOR_REVIEW",
            ], root)
            self.assertEqual(finalized.returncode, 0, finalized.stdout)
            self.assertEqual(run(["git", "add", "."], root).returncode, 0)
            self.assertEqual(run(["git", "commit", "-m", "test: finalize checkpoint"], root).returncode, 0)
            validated = run([sys.executable, str(SCRIPTS / "validate_checkpoint.py"), "--root", str(root)], root)
            self.assertEqual(validated.returncode, 0, validated.stdout)


if __name__ == "__main__":
    unittest.main()
