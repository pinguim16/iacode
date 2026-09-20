from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = PROJECT_ROOT / "scripts" / "development-ledger"
sys.path.insert(0, str(SCRIPTS))

from ledger_common import (  # noqa: E402
    blob_hash,
    canonical_hash_path,
    find_secrets,
    git_delta,
    redact_text,
)
from validate_checkpoint import (  # noqa: E402
    _validate_quality_evidence,
    _validate_second_tool,
)


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

CANONICAL_AGENT_NAMES = {
    "architect",
    "engineering-lead",
    "historian",
    "implementer",
    "planner",
    "provenance-rights",
    "qa-validator",
    "red-team",
    "reviewer",
    "security-reviewer",
}


def run(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)


FINAL_REPORT_FIXTURE = "\n".join(
    ["# Final Report", ""]
    + [
        line
        for heading in (
            "Status", "Environment", "Tool / Model / Effort", "Deliverables", "Files Created",
            "Files Modified", "Validation", "Tests", "Red Team", "Known Risks", "Remaining Work",
            "Handoff Readiness", "Next Gate", "Evidence",
        )
        for line in (f"## {heading}", "", "Fixture content.", "")
    ]
)


def write_final_report(checkpoint: Path) -> None:
    (checkpoint / "FINAL-REPORT.md").write_text(FINAL_REPORT_FIXTURE, encoding="utf-8")


def declare_inventory(root: Path, checkpoint: Path, reason: str = "declared by test scaffolding") -> None:
    """Author a complete FILES.json for the current change set, the way a human author must."""
    state = json.loads((checkpoint / "STATE.json").read_text(encoding="utf-8"))
    base = state["baseCommit"]
    delta = git_delta(root, base, None)
    files = json.loads((checkpoint / "FILES.json").read_text(encoding="utf-8"))
    buckets: dict[str, list[dict[str, object]]] = {"filesCreated": [], "filesModified": [], "filesDeleted": []}
    self_referential = str((checkpoint / "FILES.json").relative_to(root)).replace("\\", "/")
    for path, status in sorted(delta.items()):
        entry: dict[str, object] = {"path": path, "reason": reason}
        if path != self_referential:
            if status in ("A", "M"):
                entry["hashAfter"] = canonical_hash_path(root / path)
            if status in ("M", "D"):
                entry["hashBefore"] = blob_hash(root, base, path)
        buckets["filesCreated" if status == "A" else "filesModified" if status == "M" else "filesDeleted"].append(entry)
    files.update(buckets)
    (checkpoint / "FILES.json").write_text(json.dumps(files, indent=2) + "\n", encoding="utf-8")


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
            checkpoint = root / "docs" / "checkpoints" / "TEST-CP-0001"
            write_final_report(checkpoint)
            declare_inventory(root, checkpoint)
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


class ClaudeAdapterTests(unittest.TestCase):
    def test_project_agents_match_canonical_role_names(self) -> None:
        canonical = {path.stem for path in (PROJECT_ROOT / ".iacode" / "agents").glob("*.md")}
        adapters = {path.stem for path in (PROJECT_ROOT / ".claude" / "agents").glob("*.md")}
        self.assertEqual(canonical, CANONICAL_AGENT_NAMES)
        self.assertEqual(adapters, canonical)

    def test_project_agents_have_supported_required_frontmatter(self) -> None:
        for path in sorted((PROJECT_ROOT / ".claude" / "agents").glob("*.md")):
            text = path.read_text(encoding="utf-8")
            self.assertTrue(text.startswith("---\n"), path)
            _, frontmatter, body = text.split("---", 2)
            fields = {
                key.strip(): value.strip()
                for line in frontmatter.strip().splitlines()
                for key, separator, value in [line.partition(":")]
                if separator
            }
            self.assertEqual(fields.get("name"), path.stem, path)
            self.assertTrue(fields.get("description"), path)
            self.assertEqual(fields.get("model"), "inherit", path)
            self.assertTrue(body.strip(), path)

    def test_project_agents_defer_to_canonical_contracts(self) -> None:
        for path in sorted((PROJECT_ROOT / ".claude" / "agents").glob("*.md")):
            text = path.read_text(encoding="utf-8")
            canonical_path = f".iacode/agents/{path.name}"
            self.assertIn(canonical_path, text, path)
            self.assertIn("canonical role contract", text, path)


class DeltaCheckpointFixture(unittest.TestCase):
    """Builds a sealed schemaVersion 2.0.0 delta checkpoint in an isolated repository."""

    TAG = "iacode-checkpoints/TEST-CP-0001"

    def _git(self, root: Path, *args: str) -> str:
        completed = run(["git", *args], root)
        self.assertEqual(completed.returncode, 0, completed.stdout)
        return completed.stdout.strip()

    def _build(self, root: Path) -> Path:
        shutil.copytree(PROJECT_ROOT / ".iacode", root / ".iacode")
        (root / "docs" / "checkpoints").mkdir(parents=True)
        (root / "content").mkdir()
        (root / "content" / "keep.md").write_text("# Keep\n\noriginal\n", encoding="utf-8")
        (root / "content" / "remove.md").write_text("# Remove\n\noriginal\n", encoding="utf-8")
        self._git(root, "init", "-b", "main")
        self._git(root, "config", "user.name", "IACode Tests")
        self._git(root, "config", "user.email", "iacode-tests@example.invalid")
        self._git(root, "add", ".")
        self._git(root, "commit", "-m", "test: bootstrap")

        created = run([
            sys.executable, str(SCRIPTS / "new_checkpoint.py"), "--root", str(root),
            "--gate", "TEST", "--status", "IN_PROGRESS",
        ], root)
        self.assertEqual(created.returncode, 0, created.stdout)
        checkpoint = root / "docs" / "checkpoints" / "TEST-CP-0001"

        (root / "content" / "keep.md").write_text("# Keep\n\nchanged\n", encoding="utf-8")
        (root / "content" / "added.md").write_text("# Added\n\nnew\n", encoding="utf-8")
        (root / "content" / "remove.md").unlink()
        write_final_report(checkpoint)
        return checkpoint

    def _seal(self, root: Path, checkpoint: Path) -> None:
        declare_inventory(root, checkpoint)
        finalized = run([
            sys.executable, str(SCRIPTS / "finalize_checkpoint.py"), "--root", str(root),
            "--status", "READY_FOR_REVIEW", "--commit-ref", f"refs/tags/{self.TAG}",
        ], root)
        self.assertEqual(finalized.returncode, 0, finalized.stdout)
        self._git(root, "add", "-A")
        self._git(root, "commit", "-m", "test: seal delta checkpoint")
        self._git(root, "tag", "-f", self.TAG)

    def _reseal(self, root: Path, message: str = "test: attack") -> None:
        self._git(root, "add", "-A")
        self._git(root, "commit", "-m", message)
        self._git(root, "tag", "-f", self.TAG)

    def _validate(self, root: Path) -> subprocess.CompletedProcess[str]:
        return run([sys.executable, str(SCRIPTS / "validate_checkpoint.py"), "--root", str(root)], root)

    def _read(self, checkpoint: Path, name: str) -> dict:
        return json.loads((checkpoint / name).read_text(encoding="utf-8"))

    def _write(self, checkpoint: Path, name: str, value: object) -> None:
        (checkpoint / name).write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


class DeltaInventoryTests(DeltaCheckpointFixture):
    def test_exact_inventory_validates(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            checkpoint = self._build(root)
            self._seal(root, checkpoint)
            result = self._validate(root)
            self.assertEqual(result.returncode, 0, result.stdout)

    def test_removed_manifest_entry_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            checkpoint = self._build(root)
            self._seal(root, checkpoint)
            files = self._read(checkpoint, "FILES.json")
            files["filesCreated"] = [
                item for item in files["filesCreated"] if item["path"] != "content/added.md"
            ]
            self._write(checkpoint, "FILES.json", files)
            self._reseal(root)
            result = self._validate(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("FILES.json omits a changed path: content/added.md", result.stdout)

    def test_silent_tracked_modification_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            checkpoint = self._build(root)
            self._seal(root, checkpoint)
            (root / "content" / "keep.md").write_text("# Keep\n\ntampered\n", encoding="utf-8")
            self._reseal(root)
            result = self._validate(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("hashAfter does not match the repository content of content/keep.md", result.stdout)

    def test_undeclared_addition_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            checkpoint = self._build(root)
            self._seal(root, checkpoint)
            (root / "content" / "smuggled.md").write_text("# Smuggled\n", encoding="utf-8")
            self._reseal(root)
            result = self._validate(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("FILES.json omits a changed path: content/smuggled.md", result.stdout)

    def test_undeclared_deletion_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            checkpoint = self._build(root)
            self._seal(root, checkpoint)
            (root / "content" / "keep.md").unlink()
            self._reseal(root)
            result = self._validate(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("content/keep.md", result.stdout)

    def test_wrong_hash_after_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            checkpoint = self._build(root)
            self._seal(root, checkpoint)
            files = self._read(checkpoint, "FILES.json")
            for item in files["filesCreated"]:
                if item["path"] == "content/added.md":
                    item["hashAfter"] = "0" * 64
            self._write(checkpoint, "FILES.json", files)
            self._reseal(root)
            result = self._validate(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("hashAfter does not match the repository content of content/added.md", result.stdout)

    def test_wrong_hash_before_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            checkpoint = self._build(root)
            self._seal(root, checkpoint)
            files = self._read(checkpoint, "FILES.json")
            for item in files["filesModified"]:
                if item["path"] == "content/keep.md":
                    item["hashBefore"] = "1" * 64
            self._write(checkpoint, "FILES.json", files)
            self._reseal(root)
            result = self._validate(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("hashBefore does not match the baseCommit content of content/keep.md", result.stdout)

    def test_deleted_entry_requires_absence(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            checkpoint = self._build(root)
            self._seal(root, checkpoint)
            files = self._read(checkpoint, "FILES.json")
            files["filesModified"].append({
                "path": "content/remove.md", "reason": "contradictory declaration",
                "hashBefore": "2" * 64, "hashAfter": "3" * 64,
            })
            self._write(checkpoint, "FILES.json", files)
            self._reseal(root)
            result = self._validate(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("more than one category", result.stdout)


class DetachedHeadValidationTests(DeltaCheckpointFixture):
    def test_detached_head_at_checkpoint_tag_validates(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            checkpoint = self._build(root)
            self._seal(root, checkpoint)
            self._git(root, "checkout", "--detach", f"refs/tags/{self.TAG}")
            result = self._validate(root)
            self.assertEqual(result.returncode, 0, result.stdout)

    def test_detached_head_at_wrong_commit_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            checkpoint = self._build(root)
            self._seal(root, checkpoint)
            self._git(root, "commit", "--allow-empty", "-m", "test: unrelated later commit")
            self._git(root, "checkout", "--detach", "HEAD")
            result = self._validate(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("commit mismatch", result.stdout)

    def test_detached_head_with_moved_tag_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            checkpoint = self._build(root)
            self._seal(root, checkpoint)
            sealed = self._git(root, "rev-parse", "HEAD")
            self._git(root, "tag", "-f", self.TAG, "HEAD~1")
            self._git(root, "checkout", "--detach", sealed)
            result = self._validate(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("commit mismatch", result.stdout)

    def test_detached_head_with_dirty_worktree_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            checkpoint = self._build(root)
            self._seal(root, checkpoint)
            self._git(root, "checkout", "--detach", f"refs/tags/{self.TAG}")
            (root / "content" / "keep.md").write_text("# Keep\n\ndirty\n", encoding="utf-8")
            result = self._validate(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("detached HEAD validation requires a clean worktree", result.stdout)

    def test_attached_wrong_branch_still_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            checkpoint = self._build(root)
            self._seal(root, checkpoint)
            self._git(root, "checkout", "-b", "other")
            result = self._validate(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("branch mismatch", result.stdout)

    def test_finalization_refuses_detached_head(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            checkpoint = self._build(root)
            self._seal(root, checkpoint)
            self._git(root, "checkout", "--detach", f"refs/tags/{self.TAG}")
            result = run([
                sys.executable, str(SCRIPTS / "finalize_checkpoint.py"), "--root", str(root),
                "--status", "READY_FOR_REVIEW", "--commit-ref", f"refs/tags/{self.TAG}",
            ], root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("detached HEAD is read-only", result.stdout)


class FinalizationLedgerTests(DeltaCheckpointFixture):
    def test_failed_and_successful_finalizations_are_both_recorded(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            checkpoint = self._build(root)

            # First attempt: the inventory has not been declared, so finalization must fail.
            first = run([
                sys.executable, str(SCRIPTS / "finalize_checkpoint.py"), "--root", str(root),
                "--status", "READY_FOR_REVIEW", "--commit-ref", f"refs/tags/{self.TAG}",
            ], root)
            self.assertEqual(first.returncode, 1, first.stdout)
            self.assertEqual(self._read(checkpoint, "STATE.json")["status"], "IN_PROGRESS")

            records = [
                json.loads(line)
                for line in (checkpoint / "COMMANDS.jsonl").read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            failures = [item for item in records if item["command"].startswith("finalize_checkpoint.py")]
            self.assertEqual(len(failures), 1)
            self.assertEqual(failures[0]["exitCode"], 1)
            self.assertIn("validation error", failures[0]["notes"])

            # Correction, then a second attempt that must succeed.
            self._seal(root, checkpoint)

            records = [
                json.loads(line)
                for line in (checkpoint / "COMMANDS.jsonl").read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            attempts = [item for item in records if item["command"].startswith("finalize_checkpoint.py")]
            self.assertEqual([item["exitCode"] for item in attempts], [1, 0])
            self.assertEqual(len({item["id"] for item in records}), len(records))

            state = self._read(checkpoint, "STATE.json")
            self.assertEqual(state["status"], "READY_FOR_REVIEW")
            self.assertIn("--status READY_FOR_REVIEW", attempts[1]["command"])
            self.assertEqual(state["currentCommit"], f"refs/tags/{self.TAG}")
            self.assertIn(f"--commit-ref refs/tags/{self.TAG}", attempts[1]["command"])

            result = self._validate(root)
            self.assertEqual(result.returncode, 0, result.stdout)

    def test_successful_finalization_record_is_covered_by_the_inventory(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            checkpoint = self._build(root)
            self._seal(root, checkpoint)
            files = self._read(checkpoint, "FILES.json")
            declared = {
                item["path"]: item.get("hashAfter")
                for item in files["filesCreated"]
            }
            relative = "docs/checkpoints/TEST-CP-0001/COMMANDS.jsonl"
            self.assertIn(relative, declared)
            self.assertEqual(declared[relative], canonical_hash_path(root / relative))


class SecondToolValidationTests(unittest.TestCase):
    def _state(self, **overrides: object) -> dict:
        state = {
            "schemaVersion": "2.0.0",
            "status": "READY_FOR_REVIEW",
            "secondToolValidation": {"status": "PENDING_MANUAL"},
        }
        state.update(overrides)
        return state

    def _errors(self, state: dict, target: Path | None = None) -> list[str]:
        errors: list[str] = []
        _validate_second_tool(state, target or PROJECT_ROOT, state["schemaVersion"], errors)
        return errors

    def test_pending_manual_is_valid_before_review(self) -> None:
        self.assertEqual(self._errors(self._state()), [])

    def test_pending_manual_cannot_grant_gate_pass(self) -> None:
        errors = self._errors(self._state(status="GATE_PASS"))
        self.assertTrue(any("requires secondToolValidation" in error for error in errors), errors)

    def test_failed_cross_tool_validation_cannot_grant_gate_pass(self) -> None:
        state = self._state(status="GATE_PASS", secondToolValidation={"status": "FAILED"})
        errors = self._errors(state)
        self.assertTrue(any("requires secondToolValidation" in error for error in errors), errors)

    def test_passed_cross_tool_validation_allows_gate_pass(self) -> None:
        state = self._state(status="GATE_PASS", secondToolValidation={
            "status": "PASSED", "tool": "codex", "provider": "openai",
            "model": "not-exposed", "validatedAt": "2026-09-20T10:00:00Z",
        })
        self.assertEqual(self._errors(state), [])

    def test_passed_requires_complete_attribution(self) -> None:
        state = self._state(status="GATE_PASS", secondToolValidation={"status": "PASSED"})
        errors = self._errors(state)
        self.assertTrue(any("requires tool" in error for error in errors), errors)
        self.assertTrue(any("requires provider" in error for error in errors), errors)

    def test_not_required_demands_justification(self) -> None:
        state = self._state(secondToolValidation={"status": "NOT_REQUIRED"})
        errors = self._errors(state)
        self.assertTrue(any("requires a justification" in error for error in errors), errors)

    def test_missing_record_fails_for_current_schema(self) -> None:
        state = {"schemaVersion": "2.0.0", "status": "IN_PROGRESS"}
        self.assertTrue(self._errors(state))

    def test_legacy_checkpoint_keeps_its_original_rule(self) -> None:
        state = {"schemaVersion": "1.0.0", "status": "GATE_PASS"}
        errors: list[str] = []
        _validate_second_tool(state, PROJECT_ROOT / "docs" / "checkpoints" / "SETUP-00-CP-0002", "1.0.0", errors)
        self.assertEqual(errors, [])

    def test_unknown_status_is_rejected_by_the_schema(self) -> None:
        schema = json.loads((PROJECT_ROOT / ".iacode" / "schemas" / "checkpoint.schema.json").read_text(encoding="utf-8"))
        from ledger_common import validate_schema as schema_check

        document = {
            "schemaVersion": "2.0.0", "phase": "p", "gate": "TEST", "status": "IN_PROGRESS",
            "branch": "main", "baseCommit": "UNBORN", "currentCommit": "HEAD", "dirty": False,
            "startedAt": NOW, "updatedAt": NOW, "nextAllowedAction": "x", "blockedBy": [],
            "secondToolValidation": {"status": "MAYBE"},
        }
        self.assertTrue(schema_check(document, schema))


class QualityEvidenceTests(unittest.TestCase):
    def _quality(self, dimension: str, entry: dict) -> dict:
        checks = {name: {"status": "NOT_EXECUTED", "evidence": []} for name in (
            "build", "unitTests", "integrationTests", "e2e", "lint", "staticAnalysis",
            "security", "documentation", "checkpointValidation", "redTeam",
        )}
        checks[dimension] = entry
        return {"schemaVersion": "2.0.0", "checks": checks}

    def _errors(self, quality: dict, command_ids: dict[str, int], target: Path) -> list[str]:
        errors: list[str] = []
        from validate_checkpoint import _normalize_quality

        _validate_quality_evidence(target, quality, _normalize_quality(quality), command_ids, "2.0.0", errors)
        return errors

    def test_pass_without_evidence_fails(self) -> None:
        quality = self._quality("staticAnalysis", {"status": "PASS", "evidence": []})
        errors = self._errors(quality, {"cmd-0001": 0}, PROJECT_ROOT)
        self.assertTrue(any("requires at least one evidence reference" in error for error in errors), errors)

    def test_pass_with_successful_command_evidence_passes(self) -> None:
        quality = self._quality("staticAnalysis", {"status": "PASS", "evidence": ["command:cmd-0001"]})
        self.assertEqual(self._errors(quality, {"cmd-0001": 0}, PROJECT_ROOT), [])

    def test_pass_referencing_a_failed_command_fails(self) -> None:
        quality = self._quality("staticAnalysis", {"status": "PASS", "evidence": ["command:cmd-0001"]})
        errors = self._errors(quality, {"cmd-0001": 1}, PROJECT_ROOT)
        self.assertTrue(any("which exited 1" in error for error in errors), errors)

    def test_pass_referencing_an_unknown_command_fails(self) -> None:
        quality = self._quality("staticAnalysis", {"status": "PASS", "evidence": ["command:cmd-9999"]})
        errors = self._errors(quality, {"cmd-0001": 0}, PROJECT_ROOT)
        self.assertTrue(any("unknown command id" in error for error in errors), errors)

    def test_pass_referencing_a_missing_file_fails(self) -> None:
        quality = self._quality("documentation", {"status": "PASS", "evidence": ["file:ABSENT.md"]})
        errors = self._errors(quality, {}, PROJECT_ROOT / "docs" / "checkpoints" / "SETUP-00-CP-0002")
        self.assertTrue(any("missing or empty file" in error for error in errors), errors)

    def test_pass_referencing_an_existing_checkpoint_file_passes(self) -> None:
        quality = self._quality("documentation", {"status": "PASS", "evidence": ["file:DECISIONS.md"]})
        self.assertEqual(self._errors(quality, {}, PROJECT_ROOT / "docs" / "checkpoints" / "SETUP-00-CP-0002"), [])

    def test_not_applicable_requires_justification(self) -> None:
        quality = self._quality("e2e", {"status": "NOT_APPLICABLE", "evidence": []})
        errors = self._errors(quality, {}, PROJECT_ROOT)
        self.assertTrue(any("requires a justification" in error for error in errors), errors)

    def test_evidence_cannot_escape_the_checkpoint(self) -> None:
        quality = self._quality("documentation", {"status": "PASS", "evidence": ["file:../../../START-HERE.md"]})
        errors = self._errors(quality, {}, PROJECT_ROOT / "docs" / "checkpoints" / "SETUP-00-CP-0002")
        self.assertTrue(any("outside the checkpoint" in error for error in errors), errors)

    def test_legacy_quality_requires_every_flat_dimension(self) -> None:
        errors: list[str] = []
        from validate_checkpoint import _normalize_quality

        quality = {"schemaVersion": "1.0.0", "build": "PASS"}
        _validate_quality_evidence(PROJECT_ROOT, quality, _normalize_quality(quality), {}, "1.0.0", errors)
        self.assertTrue(any("missing the required dimension" in error for error in errors), errors)


class SetupChecklistTests(unittest.TestCase):
    CHECKLIST = PROJECT_ROOT / "docs" / "SETUP-00-CHECKLIST.md"

    def test_checklist_exists_and_is_referenced(self) -> None:
        self.assertTrue(self.CHECKLIST.is_file())
        text = self.CHECKLIST.read_text(encoding="utf-8")
        for requirement in (
            "START-HERE.md", "AGENTS.md", "CLAUDE.md", "MASTER-PLAN.md", "DEVELOPMENT-CONTRACT.md",
            "HANDOFF-PROTOCOL.md", "CHECKPOINT-PROTOCOL.md", "DEFINITION-OF-DONE.md", "QUALITY-GATES.md",
            ".iacode/agents", ".iacode/schemas", "scripts/development-ledger", "redact_secrets.py",
            "PROVENANCE", "experience.schema.json", "LATEST.md", "HANDOFF.md", "cold-start",
            "Red Team", "Gate 0",
        ):
            self.assertIn(requirement, text, requirement)
        plan = (PROJECT_ROOT / "docs" / "MASTER-PLAN.md").read_text(encoding="utf-8")
        self.assertIn("SETUP-00-CHECKLIST.md", plan)
        self.assertIn("SETUP-00-CHECKLIST.md", (PROJECT_ROOT / "START-HERE.md").read_text(encoding="utf-8"))

    def test_documentation_links_resolve(self) -> None:
        pattern = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
        broken: list[str] = []
        for document in sorted(PROJECT_ROOT.rglob("*.md")):
            if ".git" in document.parts:
                continue
            for target in pattern.findall(document.read_text(encoding="utf-8")):
                if target.startswith(("http://", "https://", "#", "mailto:")):
                    continue
                candidate = (document.parent / target.split("#", 1)[0]).resolve()
                if not candidate.exists():
                    broken.append(f"{document.relative_to(PROJECT_ROOT)} -> {target}")
        self.assertEqual(broken, [])


class HistoricalCheckpointCompatibilityTests(unittest.TestCase):
    """The corrected tooling must still interpret the sealed 1.0.0 checkpoints."""

    def _clone_at(self, commit: str, destination: Path) -> bool:
        if run(["git", "rev-parse", "--verify", f"{commit}^{{commit}}"], PROJECT_ROOT).returncode != 0:
            return False
        if run(["git", "clone", "--no-local", "--quiet", str(PROJECT_ROOT), str(destination)], PROJECT_ROOT).returncode != 0:
            return False
        return run(["git", "checkout", "--detach", "--quiet", commit], destination).returncode == 0

    def _assert_historical_checkpoint_validates(self, tag: str) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            clone = Path(temporary) / "repo"
            if not self._clone_at(f"refs/tags/{tag}", clone):
                self.skipTest(f"historical reference {tag} is unavailable in this clone")
            result = run([
                sys.executable, str(SCRIPTS / "validate_checkpoint.py"), "--root", str(clone)
            ], clone)
            self.assertEqual(result.returncode, 0, result.stdout)

    def test_first_sealed_checkpoint_still_validates(self) -> None:
        self._assert_historical_checkpoint_validates("iacode-checkpoints/SETUP-00-CP-0001")

    def test_second_sealed_checkpoint_still_validates(self) -> None:
        self._assert_historical_checkpoint_validates("iacode-checkpoints/SETUP-00-CP-0002")


if __name__ == "__main__":
    unittest.main()
