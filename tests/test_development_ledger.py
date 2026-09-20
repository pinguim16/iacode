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
    _validate_command_reproducibility,
    _validate_delivery_assurance,
    _validate_memory_policy,
    _validate_quality_evidence,
    _validate_second_tool,
    _validate_status_blockers,
)
from delivery_assurance import evaluate_matrix  # noqa: E402
from ledger_common import (  # noqa: E402
    MILESTONES,
    milestone_for,
    requires_external_validation,
)
from lessons import (  # noqa: E402
    build_preflight,
    load_lessons,
    preventive_controls,
    recurrence_key,
    register_recurrence,
    save_lessons,
    validate_lessons as validate_memory,
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
    "test-rework-greenkeeper",
    "delivery-completeness-validator",
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


BASE_QUALITY_DIMENSIONS = (
    "build", "unitTests", "integrationTests", "e2e", "lint", "staticAnalysis",
    "security", "documentation", "checkpointValidation", "redTeam",
)


def copy_ledger_tooling(root: Path) -> None:
    """A real IACode repository ships its ledger tooling, so recorded tool paths resolve from it."""
    shutil.copytree(SCRIPTS, root / "scripts" / "development-ledger",
                    ignore=shutil.ignore_patterns("__pycache__"))


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json_file(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8", newline="\n")


def downgrade_to_evidence_schema(checkpoint: Path) -> None:
    """Pin a freshly created checkpoint to schemaVersion 2.0.0.

    The 2.0.0 rules stay under test after 3.0.0 arrives, and the inventory, detached-HEAD, and
    finalization controls are shared by both versions.
    """
    state = read_json(checkpoint / "STATE.json")
    state["schemaVersion"] = "2.0.0"
    for key in ("requirementsMatrix", "greenKeeper", "deliveryCompleteness", "reworkCycles",
                "independentReview", "redTeam", "lessonPreflight", "milestone",
                "externalAuditRequired", "externalAuditReason"):
        state.pop(key, None)
    write_json_file(checkpoint / "STATE.json", state)
    for name in ("TESTS.json", "PROVENANCE.json"):
        document = read_json(checkpoint / name)
        document["schemaVersion"] = "2.0.0"
        write_json_file(checkpoint / name, document)
    quality = read_json(checkpoint / "QUALITY.json")
    quality["schemaVersion"] = "2.0.0"
    quality["checks"] = {
        name: entry for name, entry in quality["checks"].items() if name in BASE_QUALITY_DIMENSIONS
    }
    write_json_file(checkpoint / "QUALITY.json", quality)
    for name in ("REQUIREMENTS-MATRIX.json", "REQUIREMENTS-MATRIX.md", "REWORK-LOG.jsonl"):
        target = checkpoint / name
        if target.exists():
            target.unlink()


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
            downgrade_to_evidence_schema(checkpoint)
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
        downgrade_to_evidence_schema(checkpoint)

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
            failures = [item for item in records if item.get("operation") == "finalize-checkpoint"]
            self.assertEqual(len(failures), 1)
            self.assertEqual(failures[0]["exitCode"], 1)
            self.assertEqual(failures[0]["resultCode"], "E_VALIDATION_FAILED")
            self.assertIn("validation error", failures[0]["failureReason"])
            self.assertTrue(
                failures[0]["command"].startswith("python scripts/development-ledger/finalize_checkpoint.py"),
                failures[0]["command"],
            )

            # Correction, then a second attempt that must succeed.
            self._seal(root, checkpoint)

            records = [
                json.loads(line)
                for line in (checkpoint / "COMMANDS.jsonl").read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            attempts = [item for item in records if item.get("operation") == "finalize-checkpoint"]
            self.assertEqual([item["exitCode"] for item in attempts], [1, 0])
            self.assertEqual([item["attemptId"] for item in attempts],
                             ["finalize-attempt-0001", "finalize-attempt-0002"])
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

    def test_third_sealed_checkpoint_still_validates(self) -> None:
        self._assert_historical_checkpoint_validates("iacode-checkpoints/SETUP-00-CP-0003")

    def test_fourth_sealed_checkpoint_still_validates(self) -> None:
        self._assert_historical_checkpoint_validates("iacode-checkpoints/SETUP-00-CP-0004")

    def test_fifth_sealed_checkpoint_still_validates(self) -> None:
        self._assert_historical_checkpoint_validates("iacode-checkpoints/SETUP-00-CP-0005")


class FinalizationAttemptRecordingTests(DeltaCheckpointFixture):
    """CP-0004 R3.1 and RT-02: a refusal decided before the operation still reaches the ledger."""

    def _records(self, checkpoint: Path) -> list[dict]:
        return [
            json.loads(line)
            for line in (checkpoint / "COMMANDS.jsonl").read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

    def _attempts(self, checkpoint: Path) -> list[dict]:
        return [item for item in self._records(checkpoint) if item.get("operation") == "finalize-checkpoint"]

    def test_detached_head_refusal_is_recorded(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            checkpoint = self._build(root)
            self._seal(root, checkpoint)
            before = len(self._attempts(checkpoint))
            self._git(root, "checkout", "--detach", f"refs/tags/{self.TAG}")
            result = run([
                sys.executable, str(SCRIPTS / "finalize_checkpoint.py"), "--root", str(root),
                "--status", "READY_FOR_REVIEW", "--commit-ref", f"refs/tags/{self.TAG}",
            ], root)
            self.assertEqual(result.returncode, 2, result.stdout)
            attempts = self._attempts(checkpoint)
            self.assertEqual(len(attempts), before + 1)
            refusal = attempts[-1]
            self.assertEqual(refusal["result"], "PRECONDITION_REJECTED")
            self.assertEqual(refusal["resultCode"], "E_DETACHED_HEAD")
            self.assertIsNone(refusal["exitCode"])
            self.assertIn("attached branch", refusal["failureReason"])
            self.assertEqual(refusal["phase"], "precondition")
            self.assertTrue(refusal["repositoryState"]["detached"])
            names = {item["name"]: item["satisfied"] for item in refusal["preconditions"]}
            self.assertFalse(names["attached-branch"])
            self.assertTrue(names["checkpoint-is-latest"])

    def test_non_latest_checkpoint_refusal_is_recorded(self) -> None:
        with tempfile.TemporaryDirectory() as temporary, tempfile.TemporaryDirectory() as external:
            root = Path(temporary)
            checkpoint = self._build(root)
            self._seal(root, checkpoint)
            before = len(self._attempts(checkpoint))
            outside = Path(external)
            sentinel = outside / "STATE.json"
            sentinel.write_text('{"status":"IN_PROGRESS"}\n', encoding="utf-8")
            result = run([
                sys.executable, str(SCRIPTS / "finalize_checkpoint.py"), "--root", str(root),
                "--checkpoint", str(outside), "--status", "GATE_FAIL",
            ], root)
            self.assertEqual(result.returncode, 2, result.stdout)
            self.assertEqual(sentinel.read_text(encoding="utf-8"), '{"status":"IN_PROGRESS"}\n')
            attempts = self._attempts(checkpoint)
            self.assertEqual(len(attempts), before + 1)
            self.assertEqual(attempts[-1]["resultCode"], "E_NOT_LATEST_CHECKPOINT")
            self.assertEqual(attempts[-1]["result"], "PRECONDITION_REJECTED")

    def test_invalid_commit_reference_refusal_is_recorded(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            checkpoint = self._build(root)
            self._seal(root, checkpoint)
            before = len(self._attempts(checkpoint))
            result = run([
                sys.executable, str(SCRIPTS / "finalize_checkpoint.py"), "--root", str(root),
                "--status", "READY_FOR_REVIEW", "--commit-ref", "refs/heads/main",
            ], root)
            self.assertEqual(result.returncode, 2, result.stdout)
            attempts = self._attempts(checkpoint)
            self.assertEqual(len(attempts), before + 1)
            self.assertEqual(attempts[-1]["resultCode"], "E_INVALID_COMMIT_REF")
            self.assertIsNone(attempts[-1]["exitCode"])

    def test_recorded_finalizer_command_is_executable_from_its_working_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            checkpoint = self._build(root)
            self._seal(root, checkpoint)
            attempts = self._attempts(checkpoint)
            self.assertTrue(attempts)
            for attempt in attempts:
                command = attempt["command"]
                self.assertTrue(command.startswith("python "), command)
                script = command.split()[1]
                self.assertTrue(script.endswith("finalize_checkpoint.py"), command)
                self.assertTrue((PROJECT_ROOT / script).is_file(), script)


class CommandReproducibilityTests(unittest.TestCase):
    """CP-0004 RT-02: a record must say what ran, where, against which commit, and why."""

    def _record(self, **overrides: object) -> dict:
        record = {
            "id": "cmd-0001",
            "timestamp": NOW,
            "runtime": "python 3.13.15",
            "command": "python scripts/development-ledger/validate_checkpoint.py",
            "workingDirectory": str(PROJECT_ROOT),
            "commit": "0" * 40,
            "purpose": "Validate the checkpoint.",
            "result": "COMPLETED",
            "resultCode": "OK",
            "exitCode": 0,
            "durationMs": 10,
            "stdoutArtifact": None,
            "stderrArtifact": None,
        }
        record.update(overrides)
        return record

    def _errors(self, **overrides: object) -> list[str]:
        errors: list[str] = []
        _validate_command_reproducibility(PROJECT_ROOT, self._record(**overrides), 1, errors)
        return errors

    def test_complete_record_passes(self) -> None:
        self.assertEqual(self._errors(), [])

    def test_missing_purpose_fails(self) -> None:
        self.assertTrue(any("requires purpose" in error for error in self._errors(purpose="")))

    def test_missing_runtime_fails(self) -> None:
        self.assertTrue(any("requires runtime" in error for error in self._errors(runtime="")))

    def test_missing_commit_fails(self) -> None:
        self.assertTrue(any("requires commit" in error for error in self._errors(commit="")))

    def test_bare_script_name_is_rejected(self) -> None:
        errors = self._errors(command="validate_checkpoint.py")
        self.assertTrue(any("explicit runtime" in error for error in errors), errors)

    def test_unresolvable_script_path_is_rejected(self) -> None:
        errors = self._errors(command="python scripts/development-ledger/absent_tool.py")
        self.assertTrue(any("does not resolve" in error for error in errors), errors)

    def test_precondition_rejection_must_not_fake_an_exit_code(self) -> None:
        errors = self._errors(
            result="PRECONDITION_REJECTED", resultCode="E_DETACHED_HEAD", exitCode=2,
            failureReason="detached")
        self.assertTrue(any("fabricated exitCode" in error for error in errors), errors)

    def test_precondition_rejection_requires_a_reason(self) -> None:
        errors = self._errors(result="PRECONDITION_REJECTED", resultCode="E_DETACHED_HEAD", exitCode=None)
        self.assertTrue(any("requires a failureReason" in error for error in errors), errors)

    def test_completed_record_requires_an_exit_code(self) -> None:
        errors = self._errors(exitCode=None)
        self.assertTrue(any("requires an integer exitCode" in error for error in errors), errors)

    def test_declared_input_must_exist(self) -> None:
        errors = self._errors(inputs=["scripts/development-ledger/absent.py"])
        self.assertTrue(any("recorded input does not exist" in error for error in errors), errors)


class StatusBlockerInvariantTests(unittest.TestCase):
    """CP-0004 RT-01: readiness and blockage can never be claimed at the same time."""

    def _errors(self, status: str, blockers: list[str]) -> list[str]:
        errors: list[str] = []
        _validate_status_blockers({"status": status, "blockedBy": blockers}, errors)
        return errors

    def test_ready_for_review_with_blocker_fails(self) -> None:
        errors = self._errors("READY_FOR_REVIEW", ["waiting on a credential"])
        self.assertTrue(any("incompatible with a non-empty blockedBy" in error for error in errors), errors)

    def test_ready_for_red_team_with_blocker_fails(self) -> None:
        self.assertTrue(self._errors("READY_FOR_RED_TEAM", ["blocked"]))

    def test_gate_pass_with_blocker_fails(self) -> None:
        self.assertTrue(self._errors("GATE_PASS", ["blocked"]))

    def test_ready_for_review_without_blocker_passes(self) -> None:
        self.assertEqual(self._errors("READY_FOR_REVIEW", []), [])

    def test_blocked_requires_a_reason(self) -> None:
        errors = self._errors("BLOCKED", [])
        self.assertTrue(any("requires at least one entry" in error for error in errors), errors)

    def test_rework_required_may_carry_blockers(self) -> None:
        self.assertEqual(self._errors("REWORK_REQUIRED", ["needs a decision"]), [])


class ResealedBlockerFixtureTests(DeltaCheckpointFixture):
    """The escaped RT-01 attack, reproduced end to end through the real finalizer and validator."""

    def test_resealed_ready_for_review_with_blocker_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            checkpoint = self._build(root)
            self._seal(root, checkpoint)
            self.assertEqual(self._validate(root).returncode, 0)

            state = self._read(checkpoint, "STATE.json")
            state["blockedBy"] = ["validation fixture blocker"]
            self._write(checkpoint, "STATE.json", state)
            declare_inventory(root, checkpoint)
            finalized = run([
                sys.executable, str(SCRIPTS / "finalize_checkpoint.py"), "--root", str(root),
                "--status", "READY_FOR_REVIEW", "--commit-ref", f"refs/tags/{self.TAG}",
            ], root)
            self.assertNotEqual(finalized.returncode, 0, finalized.stdout)
            self.assertIn("incompatible with a non-empty blockedBy", finalized.stdout)

            self._reseal(root)
            result = self._validate(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("incompatible with a non-empty blockedBy", result.stdout)


def build_matrix(*statuses: tuple[str, bool, list[str]]) -> dict:
    """Matrix fixture: (status, mandatory, evidence) per requirement."""
    requirements = []
    for index, (status, mandatory, evidence) in enumerate(statuses, 1):
        requirements.append({
            "id": "REQ-%04d" % index,
            "source": "fixture",
            "description": "fixture requirement",
            "mandatory": mandatory,
            "status": status,
            "implementationEvidence": list(evidence),
            "testEvidence": [],
            "documentationEvidence": [],
            "validationEvidence": [],
            "notes": "fixture justification" if status == "NOT_APPLICABLE" else "",
        })
    return {"schemaVersion": "1.0.0", "gate": "TEST", "checkpoint": "TEST-CP-0001",
            "requirements": requirements}


class DeliveryCompletenessMatrixTests(unittest.TestCase):
    """The completeness audit refuses anything short of a total, evidenced delivery."""

    EVIDENCE = ["file:START-HERE.md"]

    def _evaluate(self, matrix: dict) -> dict:
        return evaluate_matrix(PROJECT_ROOT, PROJECT_ROOT / "docs" / "checkpoints", matrix, {}, set())

    def test_every_requirement_complete_passes(self) -> None:
        report = self._evaluate(build_matrix(
            ("COMPLETE", True, self.EVIDENCE), ("COMPLETE", True, self.EVIDENCE)))
        self.assertEqual(report["result"], "PASS")
        self.assertEqual(report["coveragePercent"], 100.0)
        self.assertEqual(report["evidenceCoveragePercent"], 100.0)

    def test_one_requirement_short_of_total_fails(self) -> None:
        rows = [("COMPLETE", True, self.EVIDENCE)] * 99 + [("IN_PROGRESS", True, [])]
        report = self._evaluate(build_matrix(*rows))
        self.assertEqual(report["result"], "FAIL")
        self.assertEqual(report["coveragePercent"], 99.0)

    def test_missing_mandatory_requirement_fails(self) -> None:
        report = self._evaluate(build_matrix(
            ("COMPLETE", True, self.EVIDENCE), ("MISSING", True, [])))
        self.assertEqual(report["result"], "FAIL")
        self.assertEqual(report["missing"], 1)

    def test_partial_requirement_fails(self) -> None:
        report = self._evaluate(build_matrix(
            ("COMPLETE", True, self.EVIDENCE), ("PARTIAL", True, self.EVIDENCE)))
        self.assertEqual(report["result"], "FAIL")
        self.assertEqual(report["partial"], 1)

    def test_not_applicable_without_justification_fails(self) -> None:
        matrix = build_matrix(("NOT_APPLICABLE", False, []))
        matrix["requirements"][0]["notes"] = ""
        report = self._evaluate(matrix)
        self.assertEqual(report["result"], "FAIL")
        self.assertTrue(any("justification" in finding["detail"] for finding in report["findings"]))

    def test_not_applicable_with_justification_counts_as_covered(self) -> None:
        report = self._evaluate(build_matrix(("NOT_APPLICABLE", False, [])))
        self.assertEqual(report["result"], "PASS")
        self.assertEqual(report["notApplicable"], 1)

    def test_complete_without_evidence_fails(self) -> None:
        report = self._evaluate(build_matrix(("COMPLETE", True, [])))
        self.assertEqual(report["result"], "FAIL")
        self.assertTrue(any("at least one evidence" in finding["detail"] for finding in report["findings"]))

    def test_complete_with_unresolvable_evidence_fails(self) -> None:
        report = self._evaluate(build_matrix(("COMPLETE", True, ["file:does/not/exist.md"])))
        self.assertEqual(report["result"], "FAIL")
        self.assertEqual(report["evidenceCoveragePercent"], 0.0)

    def test_evidence_may_reference_a_successful_command(self) -> None:
        matrix = build_matrix(("COMPLETE", True, ["command:cmd-0001"]))
        report = evaluate_matrix(
            PROJECT_ROOT, PROJECT_ROOT, matrix,
            {"cmd-0001": {"result": "COMPLETED", "exitCode": 0}}, set())
        self.assertEqual(report["result"], "PASS")

    def test_evidence_referencing_a_failed_command_fails(self) -> None:
        matrix = build_matrix(("COMPLETE", True, ["command:cmd-0001"]))
        report = evaluate_matrix(
            PROJECT_ROOT, PROJECT_ROOT, matrix,
            {"cmd-0001": {"result": "COMPLETED", "exitCode": 1}}, set())
        self.assertEqual(report["result"], "FAIL")

    def test_evidence_may_reference_an_existing_test(self) -> None:
        matrix = build_matrix(("COMPLETE", True, ["test:StatusBlockerInvariantTests.test_ready_for_review_with_blocker_fails"]))
        report = evaluate_matrix(
            PROJECT_ROOT, PROJECT_ROOT, matrix, {},
            {"StatusBlockerInvariantTests.test_ready_for_review_with_blocker_fails"})
        self.assertEqual(report["result"], "PASS")

    def test_evidence_referencing_an_absent_test_fails(self) -> None:
        matrix = build_matrix(("COMPLETE", True, ["test:NoSuchTests.test_nothing"]))
        report = evaluate_matrix(PROJECT_ROOT, PROJECT_ROOT, matrix, {}, set())
        self.assertEqual(report["result"], "FAIL")

    def test_empty_matrix_fails(self) -> None:
        report = self._evaluate({"schemaVersion": "1.0.0", "gate": "TEST",
                                 "checkpoint": "TEST-CP-0001", "requirements": []})
        self.assertEqual(report["result"], "FAIL")


class DeliveryAssuranceGateTests(unittest.TestCase):
    """GREEN_KEEPER_GATE and DELIVERY_COMPLETENESS_GATE guard READY_FOR_REVIEW."""

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.checkpoint = Path(self.temporary.name)
        (self.checkpoint / "PLAN.md").write_text("# Plan\n\nfixture\n", encoding="utf-8")
        self.matrix = build_matrix(("COMPLETE", True, ["checkpoint:PLAN.md"]))
        write_json_file(self.checkpoint / "REQUIREMENTS-MATRIX.json", self.matrix)
        (self.checkpoint / "REWORK-LOG.jsonl").write_text(
            json.dumps({
                "cycle": 1, "timestamp": NOW, "trigger": "fixture", "failedGate": None,
                "failureEvidence": [], "rootCauseSummary": None, "filesChanged": [],
                "commandsExecuted": ["cmd-0001"], "result": "GREEN", "remainingFailures": 0,
            }) + "\n", encoding="utf-8", newline="\n")
        self.report = {
            "schemaVersion": "1.0.0", "checkpoint": "TEST-CP-0001", "generatedAt": NOW,
            "matrix": "REQUIREMENTS-MATRIX.json", "auditor": "fixture",
            "totalRequirements": 1, "mandatoryRequirements": 1, "complete": 1, "partial": 0,
            "missing": 0, "notApplicable": 0, "inProgress": 0, "notStarted": 0,
            "coveragePercent": 100.0, "evidenceCoveragePercent": 100.0, "result": "PASS",
            "findings": [],
        }
        write_json_file(self.checkpoint / "COMPLETENESS-REPORT.json", self.report)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def _state(self, **overrides: object) -> dict:
        state = {
            "schemaVersion": "3.0.0",
            "status": "READY_FOR_REVIEW",
            "blockedBy": [],
            "requirementsMatrix": {
                "path": "REQUIREMENTS-MATRIX.json", "total": 1, "mandatory": 1, "complete": 1,
                "partial": 0, "missing": 0, "notApplicable": 0, "coveragePercent": 100.0,
            },
            "greenKeeper": {
                "status": "PASS", "cycles": 1, "remainingFailures": 0,
                "unresolvedReworkItems": 0, "log": "REWORK-LOG.jsonl",
                "externalBlockers": [], "evidence": [],
            },
            "deliveryCompleteness": {
                "status": "PASS", "report": "COMPLETENESS-REPORT.json", "coveragePercent": 100.0,
                "evidenceCoveragePercent": 100.0, "auditor": "fixture", "evidence": [],
            },
            "reworkCycles": 1,
            "independentReview": {"status": "PENDING"},
            "redTeam": {"status": "PENDING"},
        }
        state.update(overrides)
        return state

    def _quality(self, **overrides: str) -> dict:
        checks = {name: {"status": "PASS", "evidence": ["checkpoint:PLAN.md"], "justification": None}
                  for name in BASE_QUALITY_DIMENSIONS + ("greenKeeper", "deliveryCompleteness")}
        checks["redTeam"] = {"status": "NOT_EXECUTED", "evidence": [], "justification": None}
        for name, status in overrides.items():
            checks[name] = {"status": status, "evidence": [], "justification": None}
        return checks

    def _tests(self, failed: int = 0) -> dict:
        result = {"executed": True, "passed": 5, "failed": failed,
                  "command": "python -m unittest discover -s tests", "evidence": "fixture"}
        return {"schemaVersion": "3.0.0", "unit": result, "integration": result,
                "e2e": {"executed": False, "passed": 0, "failed": 0, "command": None, "evidence": None}}

    def _errors(self, state: dict | None = None, quality: dict | None = None,
                tests: dict | None = None) -> list[str]:
        errors: list[str] = []
        _validate_delivery_assurance(
            PROJECT_ROOT, self.checkpoint, state or self._state(),
            quality or self._quality(), tests or self._tests(), errors)
        return errors

    def test_complete_delivery_passes_every_gate(self) -> None:
        self.assertEqual(self._errors(), [])

    def test_green_keeper_not_executed_blocks_review(self) -> None:
        state = self._state(greenKeeper={
            "status": "NOT_EXECUTED", "cycles": 1, "remainingFailures": 0,
            "unresolvedReworkItems": 0, "log": "REWORK-LOG.jsonl"})
        errors = self._errors(state)
        self.assertTrue(any("GREEN_KEEPER_GATE=PASS" in error for error in errors), errors)

    def test_completeness_validator_not_executed_blocks_review(self) -> None:
        state = self._state(deliveryCompleteness={
            "status": "NOT_EXECUTED", "report": None, "coveragePercent": 0.0})
        errors = self._errors(state)
        self.assertTrue(any("DELIVERY_COMPLETENESS_GATE=PASS" in error for error in errors), errors)

    def test_green_keeper_pass_with_a_real_failure_is_rejected(self) -> None:
        (self.checkpoint / "REWORK-LOG.jsonl").write_text(
            json.dumps({
                "cycle": 1, "timestamp": NOW, "trigger": "fixture", "failedGate": "tests",
                "failureEvidence": ["cmd-0001"], "rootCauseSummary": "unfixed",
                "filesChanged": [], "commandsExecuted": ["cmd-0001"], "result": "STILL_RED",
                "remainingFailures": 1,
            }) + "\n", encoding="utf-8", newline="\n")
        errors = self._errors()
        self.assertTrue(any("contradicts the last rework cycle" in error for error in errors), errors)

    def test_green_keeper_pass_with_red_tests_is_rejected(self) -> None:
        errors = self._errors(tests=self._tests(failed=2))
        self.assertTrue(any("contradicts TESTS.json" in error for error in errors), errors)

    def test_red_tests_block_review(self) -> None:
        errors = self._errors(quality=self._quality(unitTests="FAIL"))
        self.assertTrue(any("unitTests=FAIL" in error for error in errors), errors)

    def test_unresolved_rework_blocks_review(self) -> None:
        state = self._state(greenKeeper={
            "status": "PASS", "cycles": 1, "remainingFailures": 0,
            "unresolvedReworkItems": 2, "log": "REWORK-LOG.jsonl"})
        errors = self._errors(state)
        self.assertTrue(any("unresolvedReworkItems" in error for error in errors), errors)

    def test_completeness_report_inconsistent_with_the_matrix_is_rejected(self) -> None:
        report = dict(self.report)
        report["complete"] = 5
        report["totalRequirements"] = 5
        write_json_file(self.checkpoint / "COMPLETENESS-REPORT.json", report)
        errors = self._errors()
        self.assertTrue(any("contradicts the recomputed value" in error for error in errors), errors)

    def test_completeness_pass_claimed_over_an_incomplete_matrix_is_rejected(self) -> None:
        write_json_file(self.checkpoint / "REQUIREMENTS-MATRIX.json",
                        build_matrix(("PARTIAL", True, ["checkpoint:PLAN.md"])))
        errors = self._errors()
        self.assertTrue(any("contradicts the recomputed value" in error for error in errors), errors)
        self.assertTrue(any("zero PARTIAL requirements" in error for error in errors), errors)

    def test_state_matrix_counts_must_match_the_matrix(self) -> None:
        state = self._state(requirementsMatrix={
            "path": "REQUIREMENTS-MATRIX.json", "total": 7, "complete": 7, "partial": 0,
            "missing": 0, "notApplicable": 0, "coveragePercent": 100.0})
        errors = self._errors(state)
        self.assertTrue(any("does not match the matrix value" in error for error in errors), errors)

    def test_cycle_count_must_match_the_rework_log(self) -> None:
        state = self._state(greenKeeper={
            "status": "PASS", "cycles": 9, "remainingFailures": 0,
            "unresolvedReworkItems": 0, "log": "REWORK-LOG.jsonl"})
        errors = self._errors(state)
        self.assertTrue(any("recorded rework cycles" in error for error in errors), errors)

    def test_self_claimed_independent_review_blocks_review(self) -> None:
        state = self._state(independentReview={"status": "APPROVED"})
        errors = self._errors(state)
        self.assertTrue(any("independentReview to be PENDING" in error for error in errors), errors)

    def test_self_claimed_red_team_blocks_review(self) -> None:
        state = self._state(redTeam={"status": "RED_TEAM_PASS"})
        errors = self._errors(state)
        self.assertTrue(any("redTeam to be PENDING" in error for error in errors), errors)

    def test_gate_consistency_is_provisional_while_work_is_in_progress(self) -> None:
        """A checkpoint under construction may hold provisional gate values.

        This is what lets the Green Keeper validate the very checkpoint that records its cycles.
        The same inconsistency is rejected the moment the delivery is offered for review.
        """
        (self.checkpoint / "REWORK-LOG.jsonl").write_text(
            json.dumps({
                "cycle": 1, "timestamp": NOW, "trigger": "fixture", "failedGate": "tests",
                "failureEvidence": ["cmd-0001"], "rootCauseSummary": "still being repaired",
                "filesChanged": [], "commandsExecuted": ["cmd-0001"], "result": "STILL_RED",
                "remainingFailures": 1,
            }) + "\n", encoding="utf-8", newline="\n")
        self.assertEqual(self._errors(self._state(status="IN_PROGRESS")), [])
        self.assertTrue(self._errors(self._state(status="READY_FOR_REVIEW")))

    def test_missing_assurance_block_is_rejected(self) -> None:
        state = self._state()
        del state["greenKeeper"]
        errors = self._errors(state)
        self.assertTrue(any("requires the greenKeeper block" in error for error in errors), errors)


class GreenKeeperToolTests(unittest.TestCase):
    """The Green Keeper harness must refuse to report green while a gate is red."""

    def _bootstrap(self, root: Path, failing: bool) -> Path:
        shutil.copytree(PROJECT_ROOT / ".iacode", root / ".iacode")
        (root / "docs" / "checkpoints").mkdir(parents=True)
        copy_ledger_tooling(root)
        (root / "tests").mkdir()
        body = "self.assertEqual(1, 2)" if failing else "self.assertEqual(1, 1)"
        (root / "tests" / "test_fixture.py").write_text(
            "import unittest\n\n\nclass FixtureTests(unittest.TestCase):\n"
            f"    def test_case(self):\n        {body}\n", encoding="utf-8")
        self.assertEqual(run(["git", "init", "-b", "main"], root).returncode, 0)
        for key, value in (("user.name", "IACode Tests"), ("user.email", "iacode-tests@example.invalid")):
            self.assertEqual(run(["git", "config", key, value], root).returncode, 0)
        self.assertEqual(run(["git", "add", "."], root).returncode, 0)
        self.assertEqual(run(["git", "commit", "-m", "test: bootstrap"], root).returncode, 0)
        created = run([
            sys.executable, str(SCRIPTS / "new_checkpoint.py"), "--root", str(root),
            "--gate", "TEST", "--status", "IN_PROGRESS",
        ], root)
        self.assertEqual(created.returncode, 0, created.stdout)
        return root / "docs" / "checkpoints" / "TEST-CP-0001"

    def _cycles(self, checkpoint: Path) -> list[dict]:
        text = (checkpoint / "REWORK-LOG.jsonl").read_text(encoding="utf-8")
        return [json.loads(line) for line in text.splitlines() if line.strip()]

    def test_red_gate_is_reported_as_still_red(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            checkpoint = self._bootstrap(root, failing=True)
            result = run([
                sys.executable, str(SCRIPTS / "green_keeper.py"), "--root", str(root),
                "--gates", "tests", "--trigger", "fixture red gate", "--quiet",
            ], root)
            self.assertEqual(result.returncode, 1, result.stdout)
            self.assertIn("GREEN_KEEPER_GATE=FAIL", result.stdout)
            cycles = self._cycles(checkpoint)
            self.assertEqual(len(cycles), 1)
            self.assertEqual(cycles[0]["result"], "STILL_RED")
            self.assertEqual(cycles[0]["failedGate"], "tests")
            self.assertEqual(cycles[0]["remainingFailures"], 1)
            self.assertTrue(cycles[0]["commandsExecuted"])

    def test_repaired_gate_is_reported_as_green_in_a_new_cycle(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            checkpoint = self._bootstrap(root, failing=True)
            run([sys.executable, str(SCRIPTS / "green_keeper.py"), "--root", str(root),
                 "--gates", "tests", "--quiet"], root)
            (root / "tests" / "test_fixture.py").write_text(
                "import unittest\n\n\nclass FixtureTests(unittest.TestCase):\n"
                "    def test_case(self):\n        self.assertEqual(1, 1)\n", encoding="utf-8")
            result = run([
                sys.executable, str(SCRIPTS / "green_keeper.py"), "--root", str(root),
                "--gates", "tests", "--trigger", "after repair",
                "--root-cause", "fixture assertion was wrong", "--files-changed", "tests/test_fixture.py",
            ], root)
            self.assertEqual(result.returncode, 0, result.stdout)
            self.assertIn("GREEN_KEEPER_GATE=PASS", result.stdout)
            cycles = self._cycles(checkpoint)
            self.assertEqual([item["result"] for item in cycles], ["STILL_RED", "GREEN"])
            self.assertEqual(cycles[1]["cycle"], 2)
            self.assertEqual(cycles[1]["remainingFailures"], 0)
            self.assertEqual(cycles[1]["filesChanged"], ["tests/test_fixture.py"])

    def test_external_blocker_never_reports_pass(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            checkpoint = self._bootstrap(root, failing=True)
            result = run([
                sys.executable, str(SCRIPTS / "green_keeper.py"), "--root", str(root),
                "--gates", "tests", "--external-blocker", "fixture service unavailable", "--quiet",
            ], root)
            self.assertEqual(result.returncode, 2, result.stdout)
            self.assertIn("GREEN_KEEPER_GATE=FAIL", result.stdout)
            cycles = self._cycles(checkpoint)
            self.assertEqual(cycles[-1]["result"], "BLOCKED_EXTERNAL")
            self.assertEqual(cycles[-1]["externalBlocker"], "fixture service unavailable")

    def test_gate_invocations_are_recorded_reproducibly(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            checkpoint = self._bootstrap(root, failing=False)
            run([sys.executable, str(SCRIPTS / "green_keeper.py"), "--root", str(root),
                 "--gates", "tests", "--quiet"], root)
            records = [
                json.loads(line)
                for line in (checkpoint / "COMMANDS.jsonl").read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            gate_records = [item for item in records if item.get("operation") == "green-keeper-gate"]
            self.assertEqual(len(gate_records), 1)
            record = gate_records[0]
            self.assertEqual(record["command"], "python -m unittest discover -s tests")
            self.assertEqual(record["result"], "COMPLETED")
            self.assertEqual(record["exitCode"], 0)
            self.assertTrue(record["purpose"])
            self.assertTrue(record["runtime"].startswith("python "))
            self.assertEqual(len(record["commit"]), 40)


class DeliveryLifecycleTests(unittest.TestCase):
    """The whole mandatory order, end to end, in an isolated repository."""

    TAG = "iacode-checkpoints/SETUP-00-CP-0001"

    def _git(self, root: Path, *args: str) -> None:
        completed = run(["git", *args], root)
        self.assertEqual(completed.returncode, 0, completed.stdout)

    def test_full_delivery_assurance_flow_reaches_ready_for_review(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            shutil.copytree(PROJECT_ROOT / ".iacode", root / ".iacode")
            (root / "docs" / "checkpoints").mkdir(parents=True)
            copy_ledger_tooling(root)
            (root / "tests").mkdir()
            (root / "tests" / "test_fixture.py").write_text(
                "import unittest\n\n\nclass FixtureTests(unittest.TestCase):\n"
                "    def test_case(self):\n        self.assertEqual(1, 1)\n", encoding="utf-8")
            self._git(root, "init", "-b", "main")
            self._git(root, "config", "user.name", "IACode Tests")
            self._git(root, "config", "user.email", "iacode-tests@example.invalid")
            self._git(root, "add", ".")
            self._git(root, "commit", "-m", "test: bootstrap")

            # One fixture lesson, so the preflight derives exactly one requirement.
            save_lessons(root, [make_lesson()])

            created = run([
                sys.executable, str(SCRIPTS / "new_checkpoint.py"), "--root", str(root),
                "--gate", "SETUP-00", "--status", "IN_PROGRESS",
            ], root)
            self.assertEqual(created.returncode, 0, created.stdout)
            checkpoint = root / "docs" / "checkpoints" / "SETUP-00-CP-0001"

            preflight = run([
                sys.executable, str(SCRIPTS / "lesson_preflight.py"), "--root", str(root),
                "--gate", "SETUP-00", "--scope", "control-plane", "--write",
            ], root)
            self.assertEqual(preflight.returncode, 0, preflight.stdout)
            derived = read_json(checkpoint / "LESSON-PREFLIGHT.json")["derivedRequirements"]
            self.assertEqual(len(derived), 1)

            write_final_report(checkpoint)
            matrix = build_matrix(("COMPLETE", True, ["checkpoint:PLAN.md"]))
            matrix["requirements"].append({
                "id": derived[0]["id"], "source": "lesson preflight",
                "description": derived[0]["description"], "mandatory": True, "status": "COMPLETE",
                "implementationEvidence": ["checkpoint:LESSON-PREFLIGHT.json"], "testEvidence": [],
                "documentationEvidence": [], "validationEvidence": [], "notes": "",
            })
            write_json_file(checkpoint / "REQUIREMENTS-MATRIX.json", matrix)
            (checkpoint / "REQUIREMENTS-MATRIX.md").write_text(
                "# Requirements Matrix\n\nOne fixture requirement plus one derived from a lesson.\n",
                encoding="utf-8")

            keeper = run([
                sys.executable, str(SCRIPTS / "green_keeper.py"), "--root", str(root),
                "--gates", "tests,staticAnalysis", "--trigger", "delivery gate run", "--quiet",
            ], root)
            self.assertEqual(keeper.returncode, 0, keeper.stdout)

            audit = run([
                sys.executable, str(SCRIPTS / "check_completeness.py"), "--root", str(root),
                "--auditor", "fixture auditor", "--write",
            ], root)
            self.assertEqual(audit.returncode, 0, audit.stdout)
            self.assertIn("DELIVERY_COMPLETENESS_GATE=PASS", audit.stdout)

            result = {"executed": True, "passed": 1, "failed": 0,
                      "command": "python -m unittest discover -s tests", "evidence": "fixture suite"}
            write_json_file(checkpoint / "TESTS.json", {
                "schemaVersion": "3.1.0", "unit": result, "integration": result,
                "e2e": {"executed": False, "passed": 0, "failed": 0, "command": None, "evidence": None}})
            checks = {name: {"status": "PASS", "evidence": ["command:cmd-0001"], "justification": None}
                      for name in BASE_QUALITY_DIMENSIONS + ("greenKeeper", "deliveryCompleteness")}
            checks["redTeam"] = {"status": "NOT_EXECUTED", "evidence": [], "justification": None}
            checks["e2e"] = {"status": "NOT_APPLICABLE", "evidence": [],
                             "justification": "no runtime in the fixture"}
            write_json_file(checkpoint / "QUALITY.json", {"schemaVersion": "3.1.0", "checks": checks})

            state = read_json(checkpoint / "STATE.json")
            state["requirementsMatrix"] = {
                "path": "REQUIREMENTS-MATRIX.json", "total": 2, "mandatory": 2, "complete": 2,
                "partial": 0, "missing": 0, "notApplicable": 0, "coveragePercent": 100.0}
            state["lessonPreflight"] = {
                "path": "LESSON-PREFLIGHT.json", "gate": "SETUP-00", "scope": "control-plane",
                "lessonsConsidered": 1, "lessonsApplicable": 1, "derivedRequirements": 1,
                "evidence": []}
            state["greenKeeper"] = {
                "status": "PASS", "cycles": 1, "remainingFailures": 0, "unresolvedReworkItems": 0,
                "log": "REWORK-LOG.jsonl", "externalBlockers": [], "evidence": []}
            state["deliveryCompleteness"] = {
                "status": "PASS", "report": "COMPLETENESS-REPORT.json", "coveragePercent": 100.0,
                "evidenceCoveragePercent": 100.0, "auditor": "fixture auditor", "evidence": []}
            state["reworkCycles"] = 1
            write_json_file(checkpoint / "STATE.json", state)

            declare_inventory(root, checkpoint)
            finalized = run([
                sys.executable, str(SCRIPTS / "finalize_checkpoint.py"), "--root", str(root),
                "--status", "READY_FOR_REVIEW", "--commit-ref", f"refs/tags/{self.TAG}",
            ], root)
            self.assertEqual(finalized.returncode, 0, finalized.stdout)
            self._git(root, "add", "-A")
            self._git(root, "commit", "-m", "test: seal delivery")
            self._git(root, "tag", self.TAG)
            validated = run([
                sys.executable, str(SCRIPTS / "validate_checkpoint.py"), "--root", str(root)], root)
            self.assertEqual(validated.returncode, 0, validated.stdout)

            sealed = read_json(checkpoint / "STATE.json")
            self.assertEqual(sealed["status"], "READY_FOR_REVIEW")
            self.assertEqual(sealed["greenKeeper"]["status"], "PASS")
            self.assertEqual(sealed["deliveryCompleteness"]["status"], "PASS")
            self.assertEqual(sealed["blockedBy"], [])


LESSON_TEMPLATE = {
    "lessonId": "LSN-0001",
    "title": "A checkpoint may never claim readiness while it also claims to be blocked",
    "category": "checkpoint",
    "severity": "HIGH",
    "source": {"gate": "SETUP-00", "checkpoint": "TEST-CP-0001", "finding": "RT-01"},
    "symptom": "A resealed checkpoint validated while it declared a blocker.",
    "rootCauseSummary": "The blocker list was inspected only for one status.",
    "resolution": "The invariant now applies to every readiness status and every schema version.",
    "prevention": [{"kind": "test", "reference": "StatusBlockerInvariantTests",
                    "description": "Readiness with a blocker is refused."}],
    "evidence": ["file:docs/CHECKPOINT-PROTOCOL.md"],
    "applicability": {"gates": ["*"], "scopes": [], "technologies": [], "modules": []},
    "status": "GUARDED",
    "recurrenceKey": "checkpoint/readiness-with-blockers",
    "recurrenceCount": 0,
    "guardrailFailures": [],
    "createdAt": NOW,
    "updatedAt": NOW,
    "provenance": {"sourceType": "repository-generated", "provider": "local-analysis",
                   "model": None, "ownership": "project", "license": "not-applicable",
                   "notes": None},
    "trainingEligibility": {"trainingAllowed": False, "ragAllowed": False,
                            "distillationAllowed": False, "justification": None},
    "notes": None,
}


def make_lesson(**overrides: object) -> dict:
    lesson = json.loads(json.dumps(LESSON_TEMPLATE))
    for key, value in overrides.items():
        lesson[key] = value
    return lesson


class EngineeringMemoryStructureTests(unittest.TestCase):
    """The memory exists, belongs to the project, and its own rules hold."""

    MEMORY = PROJECT_ROOT / ".iacode" / "memory"

    def test_memory_tree_exists(self) -> None:
        self.assertTrue((self.MEMORY / "README.md").is_file())
        self.assertTrue((self.MEMORY / "LESSONS.md").is_file())
        self.assertTrue((self.MEMORY / "lessons.jsonl").is_file())
        for name in ("patterns", "anti-patterns", "incidents", "guardrails", "retrospectives"):
            self.assertTrue((self.MEMORY / name).is_dir(), name)

    def test_memory_states_it_is_organizational_not_personal(self) -> None:
        text = (self.MEMORY / "README.md").read_text(encoding="utf-8").lower()
        self.assertIn("engineering organization", text)
        self.assertIn("not** the user's personal memory", text)

    def test_repository_memory_is_valid(self) -> None:
        self.assertEqual(validate_memory(PROJECT_ROOT), [])

    def test_repository_lessons_deny_training_by_default(self) -> None:
        lessons = load_lessons(PROJECT_ROOT)
        self.assertTrue(lessons)
        for lesson in lessons:
            rights = lesson["trainingEligibility"]
            self.assertFalse(rights["trainingAllowed"], lesson["lessonId"])
            self.assertFalse(rights["distillationAllowed"], lesson["lessonId"])

    def test_every_guarded_lesson_names_a_real_control(self) -> None:
        for lesson in load_lessons(PROJECT_ROOT):
            if lesson["status"] != "GUARDED":
                continue
            controls = preventive_controls(lesson)
            self.assertTrue(controls, lesson["lessonId"])

    def test_the_guardrail_principle_is_documented(self) -> None:
        for path in (self.MEMORY / "README.md", PROJECT_ROOT / "docs" / "ENGINEERING-MEMORY.md"):
            text = path.read_text(encoding="utf-8").lower()
            self.assertIn("guardrail", text, str(path))


class LessonValidationTests(unittest.TestCase):
    """validate_lessons is the control that keeps the memory honest."""

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        shutil.copytree(PROJECT_ROOT / ".iacode" / "schemas", self.root / ".iacode" / "schemas")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def _errors(self, *lessons: dict) -> list[str]:
        save_lessons(self.root, list(lessons))
        return validate_memory(self.root)

    def test_valid_lesson_passes(self) -> None:
        self.assertEqual(self._errors(make_lesson()), [])

    def test_invalid_lesson_fails(self) -> None:
        errors = self._errors(make_lesson(category="astrology", severity="URGENT"))
        self.assertTrue(any("category" in error for error in errors), errors)
        self.assertTrue(any("severity" in error for error in errors), errors)

    def test_missing_required_field_fails(self) -> None:
        lesson = make_lesson()
        del lesson["rootCauseSummary"]
        errors = self._errors(lesson)
        self.assertTrue(any("rootCauseSummary" in error for error in errors), errors)

    def test_duplicate_lesson_id_fails(self) -> None:
        errors = self._errors(make_lesson(), make_lesson(recurrenceKey="checkpoint/other-key"))
        self.assertTrue(any("duplicate lessonId" in error for error in errors), errors)

    def test_guarded_without_preventive_evidence_fails(self) -> None:
        errors = self._errors(make_lesson(prevention=[]))
        self.assertTrue(any("GUARDED requires at least one preventive control" in error
                            for error in errors), errors)

    def test_documentation_alone_does_not_guard_a_lesson(self) -> None:
        errors = self._errors(make_lesson(prevention=[
            {"kind": "documentation", "reference": "docs/ENGINEERING-MEMORY.md",
             "description": "It is written down."}]))
        self.assertTrue(any("documentation alone is not a guardrail" in error
                            for error in errors), errors)

    def test_secret_in_a_lesson_fails(self) -> None:
        # Assembled at runtime so this source file does not itself carry a secret-shaped literal.
        leaked = "OPENAI_" + "API_KEY=" + "sk-" + "liveexamplekey0123456789"
        errors = self._errors(make_lesson(symptom=f"The run failed because {leaked} was rejected."))
        self.assertTrue(any("secret pattern detected" in error for error in errors), errors)

    def test_training_allowed_requires_a_rights_justification(self) -> None:
        errors = self._errors(make_lesson(trainingEligibility={
            "trainingAllowed": True, "ragAllowed": False, "distillationAllowed": False,
            "justification": None}))
        self.assertTrue(any("rights justification" in error for error in errors), errors)

    def test_reused_recurrence_key_fails(self) -> None:
        errors = self._errors(make_lesson(), make_lesson(lessonId="LSN-0002"))
        self.assertTrue(any("already used by" in error for error in errors), errors)

    def test_unresolved_guardrail_failure_cannot_stay_guarded(self) -> None:
        errors = self._errors(make_lesson(recurrenceCount=1, guardrailFailures=[
            {"observedAt": NOW, "checkpoint": "TEST-CP-0001", "detail": "GUARDRAIL_FAILURE: repeated"}]))
        self.assertTrue(any("GUARDED is not a valid status" in error for error in errors), errors)

    def test_superseded_requires_a_successor(self) -> None:
        errors = self._errors(make_lesson(status="SUPERSEDED", prevention=[]))
        self.assertTrue(any("SUPERSEDED requires supersededBy" in error for error in errors), errors)


class LessonRecurrenceTests(unittest.TestCase):
    def test_recurrence_key_is_stable_for_a_failure_class(self) -> None:
        first = recurrence_key("checkpoint", "The finalization refusal was not recorded in the ledger")
        second = recurrence_key("checkpoint", "the finalization refusal was NOT recorded in the ledger!")
        self.assertEqual(first, second)

    def test_recurrence_key_separates_different_classes(self) -> None:
        self.assertNotEqual(
            recurrence_key("checkpoint", "a refusal was not recorded"),
            recurrence_key("testing", "the suite was red at handoff"))

    def test_recurrence_increments_the_counter(self) -> None:
        lesson = make_lesson(status="CONFIRMED", prevention=[])
        repeated = register_recurrence(lesson, "TEST-CP-0002", "it happened again")
        self.assertEqual(repeated["recurrenceCount"], 1)
        self.assertEqual(repeated["status"], "CONFIRMED")
        self.assertEqual(repeated["guardrailFailures"], [])

    def test_a_repeat_against_a_guarded_lesson_is_a_guardrail_failure(self) -> None:
        repeated = register_recurrence(make_lesson(), "TEST-CP-0002", "the control let it through")
        self.assertEqual(repeated["recurrenceCount"], 1)
        self.assertEqual(repeated["status"], "CONFIRMED")
        self.assertEqual(len(repeated["guardrailFailures"]), 1)
        self.assertIn("GUARDRAIL_FAILURE", repeated["guardrailFailures"][0]["detail"])
        self.assertEqual(repeated["severity"], "CRITICAL")


class LessonPreflightTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        shutil.copytree(PROJECT_ROOT / ".iacode" / "schemas", self.root / ".iacode" / "schemas")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def _preflight(self, lessons: list[dict], gate: str = "GATE 0", scope: str = "runtime",
                   technologies: list[str] | None = None, modules: list[str] | None = None) -> dict:
        save_lessons(self.root, lessons)
        return build_preflight(self.root, gate, scope, technologies or [], modules or [])

    def test_preflight_selects_an_applicable_lesson(self) -> None:
        preflight = self._preflight([make_lesson()])
        self.assertEqual(preflight["lessonsApplicable"], 1)
        selected = preflight["applicable"][0]
        self.assertEqual(selected["lessonId"], "LSN-0001")
        self.assertTrue(selected["reasonApplicable"])
        self.assertTrue(selected["requiredCheck"])
        self.assertTrue(selected["requiredEvidence"])

    def test_preflight_ignores_a_lesson_declared_for_another_gate(self) -> None:
        lesson = make_lesson(applicability={"gates": ["GATE 7"], "scopes": [], "technologies": [],
                                            "modules": []})
        preflight = self._preflight([lesson], gate="GATE 0")
        self.assertEqual(preflight["lessonsConsidered"], 1)
        self.assertEqual(preflight["lessonsApplicable"], 0)
        self.assertEqual(preflight["derivedRequirements"], [])

    def test_preflight_ignores_a_lesson_whose_technology_is_absent(self) -> None:
        lesson = make_lesson(applicability={"gates": ["*"], "scopes": [],
                                            "technologies": ["postgresql"], "modules": []})
        self.assertEqual(self._preflight([lesson], technologies=["python"])["lessonsApplicable"], 0)
        self.assertEqual(self._preflight([lesson], technologies=["postgresql"])["lessonsApplicable"], 1)

    def test_preflight_ignores_a_retired_lesson(self) -> None:
        preflight = self._preflight([make_lesson(status="RETIRED", prevention=[])])
        self.assertEqual(preflight["lessonsApplicable"], 0)
        self.assertEqual(preflight["derivedRequirements"], [])

    def test_preflight_ignores_a_superseded_lesson(self) -> None:
        preflight = self._preflight([make_lesson(status="SUPERSEDED", prevention=[],
                                                 supersededBy="LSN-0099")])
        self.assertEqual(preflight["lessonsApplicable"], 0)

    def test_an_applicable_lesson_becomes_a_derived_requirement(self) -> None:
        preflight = self._preflight([make_lesson()])
        derived = preflight["derivedRequirements"]
        self.assertEqual(len(derived), 1)
        self.assertEqual(derived[0]["id"], "LESSON-REQ-0001")
        self.assertEqual(derived[0]["lessonId"], "LSN-0001")
        self.assertTrue(derived[0]["mandatory"])
        self.assertIn("verify", derived[0]["description"].lower())

    def test_the_repository_preflight_covers_every_active_lesson(self) -> None:
        preflight = build_preflight(PROJECT_ROOT, "SETUP-00", "control-plane", [], [])
        active = [lesson for lesson in load_lessons(PROJECT_ROOT)
                  if lesson["status"] not in ("SUPERSEDED", "RETIRED")]
        self.assertEqual(preflight["lessonsApplicable"], len(active))


class DerivedRequirementCompletenessTests(unittest.TestCase):
    """A lesson that the preflight selected cannot be dropped from the matrix."""

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.checkpoint = Path(self.temporary.name)
        (self.checkpoint / "PLAN.md").write_text("# Plan\n\nfixture\n", encoding="utf-8")
        write_json_file(self.checkpoint / "LESSON-PREFLIGHT.json", {
            "schemaVersion": "1.0.0", "gate": "TEST", "scope": "fixture", "technologies": [],
            "modules": [], "generatedAt": NOW, "lessonsConsidered": 1, "lessonsApplicable": 1,
            "applicable": [{
                "lessonId": "LSN-0001", "title": "fixture", "status": "GUARDED", "severity": "HIGH",
                "reasonApplicable": "applies to every Gate", "requiredCheck": "check it",
                "requiredEvidence": "evidence", "derivedRequirementId": "LESSON-REQ-0001"}],
            "derivedRequirements": [{
                "id": "LESSON-REQ-0001", "lessonId": "LSN-0001",
                "description": "Verify the fixture lesson", "mandatory": True,
                "requiredEvidence": "evidence"}],
        })

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def _evaluate(self, matrix: dict) -> dict:
        return evaluate_matrix(PROJECT_ROOT, self.checkpoint, matrix, {}, set())

    def test_a_missing_derived_requirement_blocks_completeness(self) -> None:
        report = self._evaluate(build_matrix(("COMPLETE", True, ["checkpoint:PLAN.md"])))
        self.assertEqual(report["result"], "FAIL")
        self.assertTrue(any("the matrix does not declare it" in finding["detail"]
                            for finding in report["findings"]), report["findings"])

    def test_a_declared_derived_requirement_passes(self) -> None:
        matrix = build_matrix(("COMPLETE", True, ["checkpoint:PLAN.md"]))
        matrix["requirements"].append({
            "id": "LESSON-REQ-0001", "source": "lesson preflight",
            "description": "Verify the fixture lesson", "mandatory": True, "status": "COMPLETE",
            "implementationEvidence": ["checkpoint:PLAN.md"], "testEvidence": [],
            "documentationEvidence": [], "validationEvidence": [], "notes": "",
        })
        self.assertEqual(self._evaluate(matrix)["result"], "PASS")


class MilestoneValidationPolicyTests(unittest.TestCase):
    def test_milestone_grouping_matches_the_published_plan(self) -> None:
        identifiers = [identifier for identifier, _title, _gates in MILESTONES]
        self.assertEqual(identifiers, ["M0", "M1", "M2", "M3", "M4", "M5", "M6"])
        self.assertEqual(milestone_for("SETUP-00")[0], "M0")
        for gate, expected in (("GATE 0", "M1"), ("GATE 3", "M1"), ("GATE 4", "M2"),
                               ("GATE 7", "M2"), ("GATE 8", "M3"), ("GATE 11", "M3"),
                               ("GATE 12", "M4"), ("GATE 15", "M4"), ("GATE 16", "M5"),
                               ("GATE 19", "M5"), ("GATE 20", "M6"), ("GATE 23", "M6")):
            self.assertEqual(milestone_for(gate)[0], expected, gate)

    def test_every_planned_gate_belongs_to_exactly_one_milestone(self) -> None:
        seen: set[str] = set()
        for _identifier, _title, gates in MILESTONES:
            for gate in gates:
                self.assertNotIn(gate, seen, gate)
                seen.add(gate)
        self.assertEqual(len(seen), 25)

    def test_an_intermediate_gate_does_not_require_external_validation(self) -> None:
        for gate in ("GATE 0", "GATE 1", "GATE 2", "GATE 4", "GATE 21"):
            self.assertFalse(requires_external_validation(gate), gate)

    def test_a_milestone_closing_gate_requires_external_validation(self) -> None:
        for gate in ("SETUP-00", "GATE 3", "GATE 7", "GATE 11", "GATE 15", "GATE 19", "GATE 23"):
            self.assertTrue(requires_external_validation(gate), gate)

    def test_an_extraordinary_audit_can_be_requested_earlier(self) -> None:
        self.assertFalse(requires_external_validation("GATE 1"))
        self.assertTrue(requires_external_validation("GATE 1", external_audit_required=True))

    def test_an_unplanned_gate_is_treated_conservatively(self) -> None:
        self.assertIsNone(milestone_for("GATE 99"))
        self.assertTrue(requires_external_validation("GATE 99"))


class MemoryPolicyValidationTests(unittest.TestCase):
    """The 3.1.0 checkpoint rules for the preflight, the milestone and extraordinary audits."""

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.checkpoint = Path(self.temporary.name)
        self.preflight = {
            "schemaVersion": "1.0.0", "gate": "SETUP-00", "scope": "control-plane",
            "technologies": [], "modules": [], "generatedAt": NOW,
            "lessonsConsidered": 2, "lessonsApplicable": 1,
            "applicable": [{
                "lessonId": "LSN-0001", "title": "fixture", "status": "GUARDED", "severity": "HIGH",
                "reasonApplicable": "applies to every Gate", "requiredCheck": "check it",
                "requiredEvidence": "evidence", "derivedRequirementId": "LESSON-REQ-0001"}],
            "derivedRequirements": [{
                "id": "LESSON-REQ-0001", "lessonId": "LSN-0001", "description": "Verify it",
                "mandatory": True, "requiredEvidence": "evidence"}],
        }
        write_json_file(self.checkpoint / "LESSON-PREFLIGHT.json", self.preflight)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def _state(self, **overrides: object) -> dict:
        state = {
            "schemaVersion": "3.1.0",
            "gate": "SETUP-00",
            "status": "IN_PROGRESS",
            "blockedBy": [],
            "secondToolValidation": {"status": "PENDING_MANUAL"},
            "lessonPreflight": {
                "path": "LESSON-PREFLIGHT.json", "gate": "SETUP-00", "scope": "control-plane",
                "lessonsConsidered": 2, "lessonsApplicable": 1, "derivedRequirements": 1},
            "milestone": {"id": "M0", "title": "Development control plane",
                          "gates": ["SETUP-00"], "status": "PENDING"},
            "externalAuditRequired": False,
            "externalAuditReason": None,
        }
        state.update(overrides)
        return state

    def _errors(self, state: dict | None = None) -> list[str]:
        errors: list[str] = []
        _validate_memory_policy(PROJECT_ROOT, self.checkpoint, state or self._state(), errors)
        return errors

    def test_a_consistent_checkpoint_passes(self) -> None:
        self.assertEqual(self._errors(), [])

    def test_a_missing_preflight_block_fails(self) -> None:
        state = self._state()
        del state["lessonPreflight"]
        errors = self._errors(state)
        self.assertTrue(any("requires the lessonPreflight block" in error for error in errors), errors)

    def test_preflight_counts_must_match_the_artifact(self) -> None:
        state = self._state(lessonPreflight={
            "path": "LESSON-PREFLIGHT.json", "gate": "SETUP-00", "scope": "control-plane",
            "lessonsConsidered": 99, "lessonsApplicable": 1, "derivedRequirements": 1})
        errors = self._errors(state)
        self.assertTrue(any("does not match" in error for error in errors), errors)

    def test_a_wrong_milestone_grouping_fails(self) -> None:
        state = self._state(milestone={"id": "M3", "gates": ["SETUP-00"], "status": "PENDING"})
        errors = self._errors(state)
        self.assertTrue(any("does not match the planned milestone" in error for error in errors), errors)

    def test_an_extraordinary_audit_requires_a_recorded_trigger(self) -> None:
        errors = self._errors(self._state(externalAuditRequired=True))
        self.assertTrue(any("demands externalAuditReason" in error for error in errors), errors)

    def test_an_extraordinary_audit_reason_must_name_a_known_trigger(self) -> None:
        errors = self._errors(self._state(externalAuditRequired=True,
                                          externalAuditReason="because it feels risky"))
        self.assertTrue(any("must name one of the recorded triggers" in error for error in errors), errors)

    def test_a_recorded_trigger_is_accepted(self) -> None:
        self.assertEqual(self._errors(self._state(
            externalAuditRequired=True,
            externalAuditReason="sandbox-boundary change in the execution policy")), [])

    def test_a_reason_without_a_request_is_rejected(self) -> None:
        errors = self._errors(self._state(externalAuditReason="secret-handling"))
        self.assertTrue(any("while externalAuditRequired is false" in error for error in errors), errors)

    def test_a_milestone_pass_requires_external_validation(self) -> None:
        state = self._state(
            status="MILESTONE_EXTERNAL_PASS",
            milestone={"id": "M0", "gates": ["SETUP-00"], "status": "PASSED"},
            secondToolValidation={"status": "PENDING_MANUAL"})
        errors = self._errors(state)
        self.assertTrue(any("requires secondToolValidation=PASSED" in error for error in errors), errors)
        self.assertTrue(any("may only be PASSED when secondToolValidation is PASSED" in error
                            for error in errors), errors)

    def test_an_internal_pass_may_not_carry_an_external_verdict(self) -> None:
        state = self._state(status="INTERNAL_GATE_PASS",
                            secondToolValidation={"status": "PASSED"})
        errors = self._errors(state)
        self.assertTrue(any("an external PASS belongs to" in error for error in errors), errors)

    def test_an_offered_checkpoint_requires_the_preflight_artifact(self) -> None:
        (self.checkpoint / "LESSON-PREFLIGHT.json").unlink()
        errors = self._errors(self._state(status="READY_FOR_REVIEW"))
        self.assertTrue(any("the lesson preflight is mandatory" in error for error in errors), errors)


class MemoryStatusVocabularyTests(unittest.TestCase):
    def test_internal_and_external_pass_are_distinct_statuses(self) -> None:
        from ledger_common import EXTERNAL_PASS_STATUS, INTERNAL_PASS_STATUS, STATUSES

        self.assertIn(INTERNAL_PASS_STATUS, STATUSES)
        self.assertIn(EXTERNAL_PASS_STATUS, STATUSES)
        self.assertNotEqual(INTERNAL_PASS_STATUS, EXTERNAL_PASS_STATUS)

    def test_neither_pass_status_may_carry_a_blocker(self) -> None:
        for status in ("INTERNAL_GATE_PASS", "MILESTONE_EXTERNAL_PASS"):
            errors: list[str] = []
            _validate_status_blockers({"status": status, "blockedBy": ["blocked"]}, errors)
            self.assertTrue(errors, status)


if __name__ == "__main__":
    unittest.main()
