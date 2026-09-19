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

from ledger_common import find_secrets, redact_text  # noqa: E402


NOW = "2026-09-19T12:00:00Z"
REQUIRED_MARKDOWN = {
    "STATUS.md": "# Status\n\nIN_PROGRESS\n",
    "HANDOFF.md": """# Handoff

Current Gate: TEST
Current Status: IN_PROGRESS

Last valid commit: HEAD
Current branch: main

## Objective

Validate an isolated checkpoint fixture.

## What was completed

Fixture creation.

## What was NOT completed

No production work exists.

## Current repository state

Clean test repository.

## Files changed

Fixture files only.

## Important decisions

Use isolation.

## Tests executed

Validator invocation.

## Known failures

None.

## Known risks

Fixture-only behavior.

## Do not repeat

Do not alter the source repository.

## Required next action

Run validation.

## Exact continuation sequence

Execute the validator and inspect its exit code.

## Validation commands

Run the checkpoint validator.

## Stop conditions

Stop on any unexpected source-repository change.
""",
    "PLAN.md": "# Plan\n\nValidate the fixture and preserve the source repository.\n",
    "DECISIONS.md": "# Decisions\n\nUse an isolated temporary Git repository.\n",
    "DIFF-SUMMARY.md": "# Diff Summary\n\nThe fixture contains only checkpoint validation data.\n",
    "RISKS.md": "# Risks\n\nTemporary repository setup could fail; test errors expose that failure.\n",
    "NEXT.md": "# Next\n\n## Required next action\n\nContinue only after this isolated checkpoint validates successfully.\n",
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

    def test_status_document_mismatch_fails(self) -> None:
        (self.checkpoint / "STATUS.md").write_text("# Status\n\nGATE_FAIL\n", encoding="utf-8")
        result = self._validate()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("status mismatch", result.stdout)

    def test_wrong_commit_fails(self) -> None:
        state = json.loads((self.checkpoint / "STATE.json").read_text(encoding="utf-8"))
        state["currentCommit"] = "0" * 40
        self._write_json("STATE.json", state)
        result = self._validate()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("commit mismatch", result.stdout)

    def test_checkpoint_tag_detects_later_commit(self) -> None:
        commit_ref = "refs/tags/iacode-checkpoints/TEST-CP-0001"
        state = json.loads((self.checkpoint / "STATE.json").read_text(encoding="utf-8"))
        state["currentCommit"] = commit_ref
        self._write_json("STATE.json", state)
        metadata = json.loads((self.checkpoint / "RUN-METADATA.json").read_text(encoding="utf-8"))
        metadata["finalCommit"] = commit_ref
        self._write_json("RUN-METADATA.json", metadata)
        self._git("add", ".")
        self._git("commit", "-m", "test: bind checkpoint reference")
        self._git("tag", "iacode-checkpoints/TEST-CP-0001")
        self.assertEqual(self._validate().returncode, 0)
        (self.root / "later.txt").write_text("later commit\n", encoding="utf-8")
        self._git("add", "later.txt")
        self._git("commit", "-m", "test: later commit")
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

    def test_empty_next_fails(self) -> None:
        (self.checkpoint / "NEXT.md").write_text("", encoding="utf-8")
        self.assertNotEqual(self._validate().returncode, 0)

    def test_junk_next_fails(self) -> None:
        (self.checkpoint / "NEXT.md").write_text("x" * 100, encoding="utf-8")
        self.assertNotEqual(self._validate().returncode, 0)

    def test_file_hash_mismatch_fails(self) -> None:
        files = json.loads((self.checkpoint / "FILES.json").read_text(encoding="utf-8"))
        files["filesCreated"].append({
            "path": "docs/checkpoints/TEST-CP-0001/STATE.json",
            "reason": "Exercise hash verification.",
            "hashAfter": "0" * 64,
        })
        self._write_json("FILES.json", files)
        result = self._validate()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("hash mismatch", result.stdout)

    def test_whitespace_only_commands_fail(self) -> None:
        (self.checkpoint / "COMMANDS.jsonl").write_text("   \n", encoding="utf-8")
        result = self._validate()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("no command records", result.stdout)

    def test_quality_cannot_contradict_tests(self) -> None:
        tests = json.loads((self.checkpoint / "TESTS.json").read_text(encoding="utf-8"))
        tests["unit"] = {"executed": False, "passed": 0, "failed": 3, "command": None, "evidence": "fixture"}
        self._write_json("TESTS.json", tests)
        quality = json.loads((self.checkpoint / "QUALITY.json").read_text(encoding="utf-8"))
        quality["unitTests"] = "PASS"
        self._write_json("QUALITY.json", quality)
        result = self._validate()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("contradicts", result.stdout)

    def test_quality_pass_requires_positive_evidence(self) -> None:
        tests = json.loads((self.checkpoint / "TESTS.json").read_text(encoding="utf-8"))
        tests["unit"] = {"executed": True, "passed": 0, "failed": 0, "command": None, "evidence": None}
        self._write_json("TESTS.json", tests)
        quality = json.loads((self.checkpoint / "QUALITY.json").read_text(encoding="utf-8"))
        quality["unitTests"] = "PASS"
        self._write_json("QUALITY.json", quality)
        result = self._validate()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("contradicts", result.stdout)

    def test_run_metadata_mismatch_fails(self) -> None:
        metadata = json.loads((self.checkpoint / "RUN-METADATA.json").read_text(encoding="utf-8"))
        metadata["branch"] = "invented"
        metadata["finalCommit"] = "0" * 40
        self._write_json("RUN-METADATA.json", metadata)
        result = self._validate()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("does not match STATE.json", result.stdout)

    def test_gate_pass_without_quality_evidence_fails(self) -> None:
        state = json.loads((self.checkpoint / "STATE.json").read_text(encoding="utf-8"))
        state["status"] = "GATE_PASS"
        self._write_json("STATE.json", state)
        (self.checkpoint / "STATUS.md").write_text("# Status\n\nGATE_PASS\n", encoding="utf-8")
        result = self._validate()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("GATE_PASS", result.stdout)

    def test_secret_outside_checkpoint_fails(self) -> None:
        credential = "sk-" + ("q" * 20)
        (self.root / "README.md").write_text("unsafe " + credential, encoding="utf-8")
        result = self._validate()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("secret pattern detected", result.stdout)
        self.assertNotIn(credential, result.stdout)

    def test_json_escaped_secret_fails(self) -> None:
        path = self.checkpoint / "PROVENANCE.json"
        text = path.read_text(encoding="utf-8")
        encoded = "sk-" + ("\\u0061" * 20)
        path.write_text(text.replace('"notes": "Deleted after test."', '"notes": "' + encoded + '"'), encoding="utf-8")
        result = self._validate()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("secret pattern detected", result.stdout)

    def test_jsonl_escaped_secret_fails_without_disclosure(self) -> None:
        encoded = "sk-" + ("\\u0061" * 20)
        line = (
            '{"timestamp":"' + NOW + '","command":"' + encoded
            + '","workingDirectory":"fixture","exitCode":0,"durationMs":1,'
            + '"stdoutArtifact":null,"stderrArtifact":null}'
        )
        with (self.checkpoint / "COMMANDS.jsonl").open("a", encoding="utf-8") as stream:
            stream.write(line + "\n")
        result = self._validate()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("secret pattern detected", result.stdout)
        self.assertNotIn("sk-" + ("a" * 20), result.stdout)

    def test_handoff_ready_status_requires_commit_anchor(self) -> None:
        state = json.loads((self.checkpoint / "STATE.json").read_text(encoding="utf-8"))
        state["status"] = "READY_FOR_REVIEW"
        self._write_json("STATE.json", state)
        (self.checkpoint / "STATUS.md").write_text("# Status\n\nREADY_FOR_REVIEW\n", encoding="utf-8")
        result = self._validate()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("must be anchored", result.stdout)

    def test_all_required_schemas_are_loaded(self) -> None:
        (self.root / ".iacode" / "schemas" / "decision.schema.json").write_text("{invalid", encoding="utf-8")
        result = self._validate()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("invalid JSON", result.stdout)

    def test_non_rfc3339_datetime_fails(self) -> None:
        state = json.loads((self.checkpoint / "STATE.json").read_text(encoding="utf-8"))
        state["updatedAt"] = "2026-09-19 12:00:00"
        self._write_json("STATE.json", state)
        self.assertNotEqual(self._validate().returncode, 0)

    def test_redactor_replaces_known_shapes(self) -> None:
        source = (
            "Authorization" + ": Basic " + "abcdefgh" + "\n"
            + "Bearer" + " " + "abcdefghijkl" + "\n"
            + "API_KEY" + "=" + "abcdefghijkl" + "\n"
            + "dw_live_" + ("x" * 12)
        )
        redacted = redact_text(source)
        self.assertNotIn("abcdefgh", redacted)
        self.assertNotIn("abcdefghijkl", redacted)
        self.assertNotIn("dw_live_", redacted)
        self.assertGreaterEqual(redacted.count("[REDACTED]"), 4)

    def test_redactor_covers_named_secret_families_and_json(self) -> None:
        keys = ("TOKEN", "SECRET", "PASSWORD", "OPENAI_API_KEY")
        source = "\n".join('"' + key + '": "' + ("z" * 12) + '"' for key in keys)
        redacted = redact_text(source)
        self.assertNotIn("z" * 12, redacted)
        self.assertEqual(redacted.count("[REDACTED]"), len(keys))

    def test_redactor_removes_complete_headers_and_private_key_block(self) -> None:
        markers = ("basicmarker123", "bearermarker123", "privatebodymarker123")
        source = (
            "Authorization" + ": Basic " + markers[0] + "\n"
            + "Authorization" + ": Bearer " + markers[1] + "\n"
            + "-----BEGIN " + "OPENSSH PRIVATE KEY-----\n" + markers[2]
            + "\n-----END " + "OPENSSH PRIVATE KEY-----\n"
        )
        redacted = redact_text(source)
        for marker in markers:
            self.assertNotIn(marker, redacted)
        self.assertEqual(redacted.count("[REDACTED]"), 3)

    def test_redactor_covers_provider_and_cloud_key_shapes(self) -> None:
        markers = ("anthropicvalue123", "githubvalue12345678901234567890", "AKIA1234567890ABCDEF")
        source = (
            "ANTHROPIC_" + "API_KEY=" + markers[0] + "\n"
            + "github_" + "pat_" + markers[1] + "\n"
            + "AWS_" + "ACCESS_KEY_ID=" + markers[2] + "\n"
        )
        redacted = redact_text(source)
        for marker in markers:
            self.assertNotIn(marker, redacted)
        self.assertEqual(redacted.count("[REDACTED]"), 3)

    def test_documentation_placeholder_is_not_a_secret(self) -> None:
        self.assertEqual(find_secrets("API_KEY=example"), [])


class LedgerLifecycleTests(unittest.TestCase):
    def _bootstrap(self, root: Path) -> None:
        shutil.copytree(PROJECT_ROOT / ".iacode", root / ".iacode")
        (root / "docs" / "checkpoints").mkdir(parents=True)
        self.assertEqual(run(["git", "init", "-b", "main"], root).returncode, 0)
        for key, value in (("user.name", "IACode Tests"), ("user.email", "iacode-tests@example.invalid")):
            self.assertEqual(run(["git", "config", key, value], root).returncode, 0)
        self.assertEqual(run(["git", "add", "."], root).returncode, 0)
        self.assertEqual(run(["git", "commit", "-m", "test: bootstrap"], root).returncode, 0)

    def test_new_finalize_commit_validate(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self._bootstrap(root)

            created = run([
                sys.executable, str(SCRIPTS / "new_checkpoint.py"), "--root", str(root),
                "--gate", "TEST", "--status", "IN_PROGRESS",
            ], root)
            self.assertEqual(created.returncode, 0, created.stdout)
            finalized = run([
                sys.executable, str(SCRIPTS / "finalize_checkpoint.py"), "--root", str(root),
                "--status", "READY_FOR_REVIEW", "--commit-ref", "refs/tags/iacode-checkpoints/TEST-CP-0001",
            ], root)
            self.assertEqual(finalized.returncode, 0, finalized.stdout)
            self.assertEqual(run(["git", "add", "."], root).returncode, 0)
            self.assertEqual(run(["git", "commit", "-m", "test: finalize checkpoint"], root).returncode, 0)
            self.assertEqual(run(["git", "tag", "iacode-checkpoints/TEST-CP-0001"], root).returncode, 0)
            validated = run([sys.executable, str(SCRIPTS / "validate_checkpoint.py"), "--root", str(root)], root)
            self.assertEqual(validated.returncode, 0, validated.stdout)

    def test_new_checkpoint_rejects_path_traversal_gate(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self._bootstrap(root)
            result = run([
                sys.executable, str(SCRIPTS / "new_checkpoint.py"), "--root", str(root),
                "--gate", "..\\..\\escaped", "--status", "IN_PROGRESS",
            ], root)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(list((root / "docs" / "checkpoints").iterdir()), [])

    def test_finalize_rejects_external_checkpoint_without_writing(self) -> None:
        with tempfile.TemporaryDirectory() as temporary, tempfile.TemporaryDirectory() as external_temporary:
            root = Path(temporary)
            self._bootstrap(root)
            created = run([
                sys.executable, str(SCRIPTS / "new_checkpoint.py"), "--root", str(root),
                "--gate", "TEST", "--status", "IN_PROGRESS",
            ], root)
            self.assertEqual(created.returncode, 0, created.stdout)
            external = Path(external_temporary)
            sentinel = external / "STATE.json"
            sentinel.write_text('{"status":"IN_PROGRESS"}\n', encoding="utf-8")
            before = sentinel.read_text(encoding="utf-8")
            result = run([
                sys.executable, str(SCRIPTS / "finalize_checkpoint.py"), "--root", str(root),
                "--checkpoint", str(external), "--status", "GATE_FAIL",
            ], root)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(sentinel.read_text(encoding="utf-8"), before)

    def test_validation_cli_does_not_allow_dirty_bypass(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self._bootstrap(root)
            result = run([
                sys.executable, str(SCRIPTS / "validate_checkpoint.py"), "--root", str(root), "--allow-dirty"
            ], root)
            self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
