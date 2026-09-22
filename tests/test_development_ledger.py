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
from delivery_assurance import completeness_scope, evaluate_matrix  # noqa: E402
from ledger_common import (  # noqa: E402
    MILESTONES,
    milestone_for,
    requires_external_validation,
)
from lessons import (  # noqa: E402
    build_preflight,
    is_applicable,
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
    "m0-closure-auditor",
}


def run(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd, text=True, encoding="utf-8", errors="replace",
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)


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


def clone_with_worktree(destination: Path) -> bool:
    """Clone the repository and overlay the current working tree onto the clone.

    A validator under development is not committed yet. Cloning HEAD alone would test the previous
    revision, so the clone is brought up to the working tree and committed, which is exactly the
    content the delivery is about to seal.
    """
    if run(["git", "clone", "--no-local", "--quiet", str(PROJECT_ROOT), str(destination)],
           PROJECT_ROOT).returncode != 0:
        return False
    listed = run(["git", "ls-files", "--cached", "--others", "--exclude-standard"], PROJECT_ROOT)
    if listed.returncode != 0:
        return False
    wanted = {line.replace("\\", "/") for line in listed.stdout.splitlines() if line.strip()}
    present = run(["git", "ls-files"], destination)
    for relative in {line.replace("\\", "/") for line in present.stdout.splitlines() if line.strip()}:
        if relative not in wanted and (destination / relative).is_file():
            (destination / relative).unlink()
    for relative in sorted(wanted):
        source = PROJECT_ROOT / relative
        if not source.is_file():
            continue
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    for command in (["git", "add", "-A"],
                    ["git", "-c", "user.name=IACode Tests",
                     "-c", "user.email=iacode-tests@example.invalid",
                     "commit", "--quiet", "--allow-empty", "-m", "test: working tree under test"]):
        if run(command, destination).returncode != 0:
            return False
    return True


def install_fixture_memory(root: Path, test_reference: str,
                           checkpoint: str = "TEST-CP-0001") -> None:
    """A minimal but complete engineering memory for an isolated fixture repository.

    The memory validator resolves what a lesson claims, so a fixture repository needs a memory that
    describes the fixture rather than the real project: one lesson, one guardrail, and a control
    that really exists in the fixture's own suite.
    """
    memory = root / ".iacode" / "memory"
    (memory / "guardrails").mkdir(parents=True, exist_ok=True)
    write_json_file(memory / "POLICY.json", {
        "schemaVersion": "2.0.0",
        "policy": "Fixture memory under the resolving policy; the registry path is fixed.",
    })
    write_json_file(memory / "guardrails" / "registry.json", {
        "schemaVersion": "1.0.0",
        "guardrails": [{
            "guardrailId": "GRD-0001",
            "title": "The fixture control",
            "kind": "test",
            "reference": test_reference,
            "verifiedBy": [test_reference],
            "lessons": ["LSN-0001"],
            "removingItWouldAllow": "The fixture failure class to recur.",
        }],
    })
    documentation = root / "docs"
    documentation.mkdir(parents=True, exist_ok=True)
    (documentation / "CHECKPOINT-PROTOCOL.md").write_text(
        "# Checkpoint Protocol\n\nFixture document.\n", encoding="utf-8")
    # An isolated fixture repository has sealed nothing, so it carries no integrity anchors.
    anchors = root / ".iacode" / "anchors" / "checkpoint-chain.json"
    if anchors.is_file():
        anchors.unlink()
    save_lessons(root, [make_lesson(
        source={"gate": "SETUP-00", "checkpoint": checkpoint, "finding": None},
        prevention=[{"kind": "test", "reference": test_reference,
                     "description": "The fixture control."}],
    )])


def copy_ledger_tooling(root: Path) -> None:
    """A real IACode repository ships its ledger tooling, so recorded tool paths resolve from it.

    The ignore rules come with it: without them a fixture's own bytecode cache looks like an
    undeclared change, which would make the fixture fail for the fixture's reasons.

    The canonical policies are then restricted to what this fixture actually contains. A fixture
    inherits the real repository's policies and almost none of its content, and two of those
    policies name things by path: the Gate specifications and the commands of the mandatory gates.
    Copying the names without the files makes the fixture fail for its own reasons, which is what
    happened when GATE 0 added four gates whose commands live outside `scripts/development-ledger`.
    """
    shutil.copytree(SCRIPTS, root / "scripts" / "development-ledger",
                    ignore=shutil.ignore_patterns("__pycache__"))
    for name in (".gitignore", ".gitattributes"):
        if (PROJECT_ROOT / name).is_file():
            shutil.copy2(PROJECT_ROOT / name, root / name)
    if (root / ".iacode" / "policies").is_dir():
        sys.path.insert(0, str(SCRIPTS))
        from promotion_fixture import restrict_policies_to_available_content

        restrict_policies_to_available_content(root)


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

    def _seal_with_symbolic_head(self, root: Path, checkpoint: Path) -> None:
        """Finalize at a status that may keep the symbolic HEAD, commit and tag: G2-F-013's shape."""
        declare_inventory(root, checkpoint)
        finalized = run([
            sys.executable, str(SCRIPTS / "finalize_checkpoint.py"), "--root", str(root),
            "--status", "IN_PROGRESS",
        ], root)
        self.assertEqual(finalized.returncode, 0, finalized.stdout)
        self.assertEqual(self._read(checkpoint, "STATE.json")["currentCommit"], "HEAD")
        self._git(root, "add", "-A")
        self._git(root, "commit", "-m", "test: checkpoint committed with the symbolic HEAD")
        self._git(root, "tag", "-f", self.TAG)

    def test_a_symbolic_head_validates_from_its_own_canonical_tag(self) -> None:
        """G2-F-013: GATE-2-CP-0001 was sealed at BLOCKED with currentCommit HEAD and then could
        not be validated from its own tag at all. The binding is derived from the checkpoint's
        identity: its canonical tag must be the checked-out commit."""
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            checkpoint = self._build(root)
            self._seal_with_symbolic_head(root, checkpoint)
            self._git(root, "checkout", "--detach", f"refs/tags/{self.TAG}")
            result = self._validate(root)
            self.assertEqual(result.returncode, 0, result.stdout)

    def test_a_symbolic_head_away_from_its_canonical_tag_is_still_refused(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            checkpoint = self._build(root)
            self._seal_with_symbolic_head(root, checkpoint)
            self._git(root, "commit", "--allow-empty", "-m", "test: unrelated later commit")
            self._git(root, "checkout", "--detach", "HEAD")
            result = self._validate(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("checkpoint tag does not resolve to the checked-out commit", result.stdout)

    def test_sealing_refuses_a_state_that_does_not_name_its_own_tag(self) -> None:
        """The recurrence control: a seal is refused before it creates a tag the state never names."""
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            checkpoint = self._build(root)
            self._seal_with_symbolic_head(root, checkpoint)
            self._git(root, "tag", "-d", self.TAG)
            result = run([sys.executable, str(SCRIPTS / "seal_checkpoint.py"), "--root", str(root)],
                         root)
            self.assertEqual(result.returncode, 2, result.stdout)
            self.assertIn("CHECKPOINT_NOT_SEALED", result.stdout)
            self.assertIn("a sealed checkpoint names its own tag", result.stdout)
            self.assertEqual(run(["git", "tag", "--list", self.TAG], root).stdout.strip(), "")

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
        (root / "docs").mkdir(parents=True, exist_ok=True)
        shutil.copy2(PROJECT_ROOT / "docs" / "SETUP-00-CHECKLIST.md",
                     root / "docs" / "SETUP-00-CHECKLIST.md")
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
            "--gate", "SETUP-00", "--status", "IN_PROGRESS",
        ], root)
        self.assertEqual(created.returncode, 0, created.stdout)
        checkpoint = root / "docs" / "checkpoints" / "SETUP-00-CP-0001"
        install_fixture_memory(root, "FixtureTests.test_case", checkpoint.name)
        self.assertEqual(run([
            sys.executable, str(SCRIPTS / "lesson_preflight.py"), "--root", str(root),
            "--gate", "SETUP-00", "--scope", "fixture", "--write"], root).returncode, 0)
        state = read_json(checkpoint / "STATE.json")
        state["lessonPreflight"] = {
            "path": "LESSON-PREFLIGHT.json", "gate": "SETUP-00", "scope": "fixture",
            "lessonsConsidered": 1, "lessonsApplicable": 1, "derivedRequirements": 1,
            "evidence": []}
        write_json_file(checkpoint / "STATE.json", state)
        self.assertEqual(run([
            sys.executable, str(SCRIPTS / "derive_requirements.py"), "--root", str(root),
            "--write"], root).returncode, 0)
        matrix = read_json(checkpoint / "REQUIREMENTS-MATRIX.json")
        for row in matrix["requirements"]:
            row["status"] = "COMPLETE"
            row["implementationEvidence"] = ["checkpoint:PLAN.md"]
        write_json_file(checkpoint / "REQUIREMENTS-MATRIX.json", matrix)
        closure = read_json(checkpoint / "CLOSURE-REQUIREMENTS.json")
        for row in closure["requirements"]:
            row["implementationStatus"] = "COMPLETE"
            row["finalStatus"] = "COMPLETE"
            row["implementationEvidence"] = ["checkpoint:PLAN.md"]
        write_json_file(checkpoint / "CLOSURE-REQUIREMENTS.json", closure)
        declare_inventory(root, checkpoint)
        return checkpoint

    def _cycles(self, checkpoint: Path) -> list[dict]:
        text = (checkpoint / "REWORK-LOG.jsonl").read_text(encoding="utf-8")
        return [json.loads(line) for line in text.splitlines() if line.strip()]

    def test_red_gate_is_reported_as_still_red(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            checkpoint = self._bootstrap(root, failing=True)
            result = run([
                sys.executable, str(SCRIPTS / "green_keeper.py"), "--root", str(root),
                "--trigger", "fixture red gate", "--quiet",
            ], root)
            self.assertEqual(result.returncode, 1, result.stdout)
            self.assertIn("GREEN_KEEPER_GATE=FAIL", result.stdout)
            cycles = self._cycles(checkpoint)
            self.assertEqual(len(cycles), 1)
            self.assertEqual(cycles[0]["result"], "STILL_RED")
            self.assertEqual(cycles[0]["failedGate"], "tests")
            self.assertGreaterEqual(cycles[0]["remainingFailures"], 1)
            self.assertTrue(cycles[0]["commandsExecuted"])
            self.assertEqual(cycles[0]["requiredGates"], list(mandatory_gates(root)))

    def test_repaired_gate_is_reported_as_green_in_a_new_cycle(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            checkpoint = self._bootstrap(root, failing=True)
            run([sys.executable, str(SCRIPTS / "green_keeper.py"), "--root", str(root),
                 "--quiet"], root)
            (root / "tests" / "test_fixture.py").write_text(
                "import unittest\n\n\nclass FixtureTests(unittest.TestCase):\n"
                "    def test_case(self):\n        self.assertEqual(1, 1)\n", encoding="utf-8")
            declare_inventory(root, checkpoint)
            result = run([
                sys.executable, str(SCRIPTS / "green_keeper.py"), "--root", str(root),
                "--trigger", "after repair",
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
                "--external-blocker", "fixture service unavailable", "--quiet",
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
                 "--quiet"], root)
            records = [
                json.loads(line)
                for line in (checkpoint / "COMMANDS.jsonl").read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            gate_records = [item for item in records if item.get("operation") == "green-keeper-gate"]
            self.assertEqual([item["phase"] for item in gate_records], list(mandatory_gates(root)))
            record = next(item for item in gate_records if item["phase"] == "tests")
            self.assertEqual(record["command"], "python -m unittest discover -s tests")
            self.assertEqual(record["result"], "COMPLETED")
            self.assertEqual(record["exitCode"], 0)
            self.assertTrue(record["purpose"])
            self.assertTrue(record["runtime"].startswith("python "))
            self.assertEqual(len(record["commit"]), 40)


class DeliveryLifecycleTests(unittest.TestCase):
    """The whole mandatory order, end to end, in an isolated repository.

    This is the rehearsal of the real sealing workflow: derive the requirement set from the
    canonical sources, run the closed mandatory gate set, audit completeness, record the internal
    assurance artifacts, finalize, commit the content, validate that commit with a clean worktree,
    and seal the result under its tag.
    """

    TAG = "iacode-checkpoints/SETUP-00-CP-0001"

    def _git(self, root: Path, *args: str) -> None:
        completed = run(["git", *args], root)
        self.assertEqual(completed.returncode, 0, completed.stdout)

    def _tool(self, root: Path, name: str, *args: str) -> subprocess.CompletedProcess[str]:
        return run([sys.executable, str(SCRIPTS / name), "--root", str(root), *args], root)

    def _complete(self, checkpoint: Path) -> None:
        evidence = ["checkpoint:PLAN.md"]
        matrix = read_json(checkpoint / "REQUIREMENTS-MATRIX.json")
        for row in matrix["requirements"]:
            row["status"] = "COMPLETE"
            row["implementationEvidence"] = list(evidence)
        write_json_file(checkpoint / "REQUIREMENTS-MATRIX.json", matrix)
        closure = read_json(checkpoint / "CLOSURE-REQUIREMENTS.json")
        for row in closure["requirements"]:
            row["implementationStatus"] = "COMPLETE"
            row["finalStatus"] = "COMPLETE"
            row["implementationEvidence"] = list(evidence)
        write_json_file(checkpoint / "CLOSURE-REQUIREMENTS.json", closure)
        return matrix

    def test_full_delivery_assurance_flow_reaches_ready_for_review(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            shutil.copytree(PROJECT_ROOT / ".iacode", root / ".iacode")
            (root / "docs" / "checkpoints").mkdir(parents=True)
            shutil.copy2(PROJECT_ROOT / "docs" / "SETUP-00-CHECKLIST.md",
                         root / "docs" / "SETUP-00-CHECKLIST.md")
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

            created = self._tool(root, "new_checkpoint.py", "--gate", "SETUP-00",
                                 "--status", "IN_PROGRESS")
            self.assertEqual(created.returncode, 0, created.stdout)
            checkpoint = root / "docs" / "checkpoints" / "SETUP-00-CP-0001"
            install_fixture_memory(root, "FixtureTests.test_case", checkpoint.name)

            preflight = self._tool(root, "lesson_preflight.py", "--gate", "SETUP-00",
                                   "--scope", "control-plane", "--write")
            self.assertEqual(preflight.returncode, 0, preflight.stdout)
            derived = read_json(checkpoint / "LESSON-PREFLIGHT.json")["derivedRequirements"]
            self.assertEqual(len(derived), 1)
            state = read_json(checkpoint / "STATE.json")
            state["lessonPreflight"] = {
                "path": "LESSON-PREFLIGHT.json", "gate": "SETUP-00", "scope": "control-plane",
                "lessonsConsidered": 1, "lessonsApplicable": 1, "derivedRequirements": 1,
                "evidence": []}
            write_json_file(checkpoint / "STATE.json", state)

            # The requirement set is derived from the canonical sources, never transcribed.
            requirements = self._tool(root, "derive_requirements.py", "--write")
            self.assertEqual(requirements.returncode, 0, requirements.stdout)
            matrix = self._complete(checkpoint)
            canonical = len(canonical_requirements(root, "SETUP-00"))
            self.assertEqual(len(matrix["requirements"]), canonical + 1)

            write_final_report(checkpoint)
            result = {"executed": True, "passed": 1, "failed": 0,
                      "command": "python -m unittest discover -s tests",
                      "evidence": "fixture suite"}
            write_json_file(checkpoint / "TESTS.json", {
                "schemaVersion": "3.2.0", "unit": result,
                "integration": {"executed": False, "passed": 0, "failed": 0, "command": None,
                                "evidence": None},
                "e2e": {"executed": False, "passed": 0, "failed": 0, "command": None,
                        "evidence": None}})

            declare_inventory(root, checkpoint)
            keeper = self._tool(root, "green_keeper.py", "--trigger", "delivery gate run",
                                "--quiet")
            self.assertEqual(keeper.returncode, 0, keeper.stdout)
            self.assertIn("GREEN_KEEPER_GATE=PASS", keeper.stdout)
            cycle = [json.loads(line) for line
                     in (checkpoint / "REWORK-LOG.jsonl").read_text(encoding="utf-8").splitlines()
                     if line.strip()][-1]
            self.assertEqual(cycle["requiredGates"], list(mandatory_gates(root)))

            audit = self._tool(root, "check_completeness.py", "--auditor", "fixture auditor",
                               "--write")
            self.assertEqual(audit.returncode, 0, audit.stdout)
            self.assertIn("DELIVERY_COMPLETENESS_GATE=PASS", audit.stdout)
            report = read_json(checkpoint / "COMPLETENESS-REPORT.json")

            # The internal assurance artifacts of a 3.2.0 delivery.
            write_json_file(checkpoint / "M0-INTERNAL-RED-TEAM.json", {
                "schemaVersion": "1.1.0", "checkpoint": checkpoint.name, "generatedAt": NOW,
                "targetFingerprint": scope_fingerprint(root), "source": "fixture",
                "baselineControl": {"result": "VALID", "detail": "null-mutation control"},
                "attacks": [{
                    "attackId": "A", "description": "fixture", "target": "fixture",
                    "mutation": "fixture", "expectedDefense": "reject", "observed": "rejected",
                    "result": "DEFENDED", "evidence": ["attack:A"], "mandatory": True}],
                "total": 1, "defended": 1, "escaped": 0, "mandatoryTotal": 1,
                "mandatoryDefended": 1, "result": "RED_TEAM_PASS"})
            write_json_file(checkpoint / "M0-INTERNAL-MIRROR.json", {
                "schemaVersion": "1.0.0", "checkpoint": checkpoint.name, "milestone": "M0",
                "generatedAt": NOW, "targetFingerprint": scope_fingerprint(root),
                "auditorRole": "M0 Closure Auditor",
                "independence": "Internal quality assurance, not external validation.",
                "checks": [{"id": "MIR-001", "dimension": "fixture", "expectation": "fixture",
                            "observed": "fixture", "result": "PASS",
                            "evidence": ["checkpoint:PLAN.md"]}],
                "total": 1, "passed": 1, "failed": 0, "notApplicable": 0, "result": "PASS"})
            counts = self._tool(root, "derive_counts.py", "--write")
            self.assertEqual(counts.returncode, 0, counts.stdout)

            checks = {name: {"status": "PASS", "evidence": ["command:cmd-0001"],
                             "justification": None}
                      for name in BASE_QUALITY_DIMENSIONS + ("greenKeeper", "deliveryCompleteness")}
            checks["redTeam"] = {"status": "NOT_EXECUTED", "evidence": [], "justification": None}
            for name in ("integrationTests", "e2e"):
                checks[name] = {"status": "NOT_APPLICABLE", "evidence": [],
                                "justification": "no runtime in the fixture"}
            write_json_file(checkpoint / "QUALITY.json",
                            {"schemaVersion": "3.2.0", "checks": checks})

            measured = guardrail_effectiveness(root)
            state = read_json(checkpoint / "STATE.json")
            state["requirementsMatrix"] = {
                "path": "REQUIREMENTS-MATRIX.json", "total": report["totalRequirements"],
                "mandatory": report["mandatoryRequirements"], "complete": report["complete"],
                "partial": 0, "missing": 0, "notApplicable": 0, "coveragePercent": 100.0}
            state["greenKeeper"] = {
                "status": "PASS", "cycles": 1, "remainingFailures": 0, "unresolvedReworkItems": 0,
                "log": "REWORK-LOG.jsonl", "externalBlockers": [], "evidence": [],
                "requiredGates": list(mandatory_gates(root)),
                "scopeFingerprint": cycle["scopeFingerprint"]}
            state["deliveryCompleteness"] = {
                "status": "PASS", "report": "COMPLETENESS-REPORT.json", "coveragePercent": 100.0,
                "evidenceCoveragePercent": 100.0, "auditor": "fixture auditor", "evidence": [],
                "scopeFingerprint": report["scopeFingerprint"]}
            state["reworkCycles"] = 1
            state["guardrailEffectiveness"] = {
                key: measured[key] for key in (
                    "guardrailsTotal", "guardrailsResolved", "guardrailsTested",
                    "guardrailsEffective", "guardrailFailures")}
            state["integrity"] = {"status": "PASS", "anchors": 0,
                                  "chainFile": ".iacode/anchors/checkpoint-chain.json",
                                  "evidence": []}
            write_json_file(checkpoint / "STATE.json", state)

            declare_inventory(root, checkpoint)
            finalized = self._tool(root, "finalize_checkpoint.py", "--status", "READY_FOR_REVIEW",
                                   "--commit-ref", f"refs/tags/{self.TAG}")
            self.assertEqual(finalized.returncode, 0, finalized.stdout)

            self._git(root, "add", "-A")
            self._git(root, "commit", "-m", "test: seal delivery content")
            content_commit = run(["git", "rev-parse", "HEAD"], root).stdout.strip()

            sealed = self._tool(root, "seal_checkpoint.py")
            self.assertEqual(sealed.returncode, 0, sealed.stdout)
            self.assertIn("CHECKPOINT_SEALED", sealed.stdout)

            validated = self._tool(root, "validate_checkpoint.py")
            self.assertEqual(validated.returncode, 0, validated.stdout)

            records = [json.loads(line) for line
                       in (checkpoint / "COMMANDS.jsonl").read_text(encoding="utf-8").splitlines()
                       if line.strip()]
            seal_records = [item for item in records
                            if item.get("operation") == "post-commit-validation"]
            self.assertTrue(seal_records)
            self.assertEqual(seal_records[-1]["commit"], content_commit)
            self.assertIs(seal_records[-1]["repositoryState"]["dirty"], False)

            final = read_json(checkpoint / "STATE.json")
            self.assertEqual(final["status"], "READY_FOR_REVIEW")
            self.assertEqual(final["greenKeeper"]["status"], "PASS")
            self.assertEqual(final["deliveryCompleteness"]["status"], "PASS")
            self.assertEqual(final["blockedBy"], [])


LESSON_TEMPLATE = {
    "lessonId": "LSN-0001",
    "title": "A checkpoint may never claim readiness while it also claims to be blocked",
    "category": "checkpoint",
    "severity": "HIGH",
    "source": {"gate": "SETUP-00", "checkpoint": "TEST-CP-0001", "finding": "RT-01"},
    "symptom": "A resealed checkpoint validated while it declared a blocker.",
    "rootCauseSummary": "The blocker list was inspected only for one status.",
    "resolution": "The invariant now applies to every readiness status and every schema version.",
    "prevention": [{
        "kind": "test",
        "reference": "StatusBlockerInvariantTests.test_ready_for_review_with_blocker_fails",
        "description": "Readiness with a blocker is refused."}],
    "guardrails": ["GRD-0001"],
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


def build_memory_fixture(root: Path) -> None:
    """A realistic root for the memory validator.

    The validator resolves what a lesson claims -- its control, its evidence and its source -- so a
    fixture that lacks a suite, a documentation tree and a checkpoint would fail for the fixture's
    reasons rather than the lesson's. The fixture is made real; the control is not weakened.
    """
    shutil.copytree(PROJECT_ROOT / ".iacode" / "schemas", root / ".iacode" / "schemas")
    shutil.copytree(PROJECT_ROOT / "tests", root / "tests",
                    ignore=shutil.ignore_patterns("__pycache__"))
    copy_ledger_tooling(root)
    documentation = root / "docs"
    documentation.mkdir(parents=True, exist_ok=True)
    for name in ("CHECKPOINT-PROTOCOL.md", "ENGINEERING-MEMORY.md"):
        (documentation / name).write_text(
            "# " + name + "\n\nFixture document.\n", encoding="utf-8")
    checkpoint = documentation / "checkpoints" / "TEST-CP-0001"
    checkpoint.mkdir(parents=True, exist_ok=True)
    (checkpoint / "REVIEW-REPORT.md").write_text(
        "# Review\n\nFinding RT-01 was recorded here.\n", encoding="utf-8")
    registry = root / ".iacode" / "memory" / "guardrails"
    registry.mkdir(parents=True, exist_ok=True)
    write_json_file(registry / "registry.json", {
        "schemaVersion": "1.0.0",
        "guardrails": [{
            "guardrailId": "GRD-0001",
            "title": "Readiness and blockage are mutually exclusive",
            "kind": "test",
            "reference": "StatusBlockerInvariantTests.test_ready_for_review_with_blocker_fails",
            "verifiedBy": [
                "StatusBlockerInvariantTests.test_ready_for_review_with_blocker_fails"],
            "lessons": ["LSN-0001"],
            "removingItWouldAllow": "A checkpoint to claim readiness and blockage at once.",
        }],
    })


class LessonValidationTests(unittest.TestCase):
    """validate_lessons is the control that keeps the memory honest."""

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        build_memory_fixture(self.root)

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

    def test_the_repository_preflight_covers_every_applicable_lesson(self) -> None:
        """Every active lesson that applies to the declared scope is selected, and only those.

        A lesson may declare the scopes it constrains -- an audit run's lessons do not constrain an
        implementing Gate -- so the expectation is computed with the same applicability rule the
        preflight uses, and every exclusion must name a scope the lesson itself declares.
        """
        gate, scope = "SETUP-00", "control-plane"
        preflight = build_preflight(PROJECT_ROOT, gate, scope, [], [])
        active = [lesson for lesson in load_lessons(PROJECT_ROOT)
                  if lesson["status"] not in ("SUPERSEDED", "RETIRED")]
        applicable = [lesson for lesson in active
                      if is_applicable(lesson, gate, scope, [], [])[0]]
        self.assertEqual(preflight["lessonsApplicable"], len(applicable))
        self.assertEqual(
            {item["lessonId"] for item in preflight["applicable"]},
            {lesson["lessonId"] for lesson in applicable})
        for lesson in active:
            if lesson in applicable:
                continue
            self.assertTrue(lesson["applicability"]["scopes"],
                            f"{lesson['lessonId']} is excluded without declaring a scope")


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
        self.assertTrue(
            any("an independently audited PASS belongs to" in error for error in errors), errors)

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


# ==============================================================================================
# M0 closure controls (schemaVersion 3.2.0)
#
# Every class below exists because the independent M0 audit of SETUP-00-CP-0006 escaped through
# the gap it covers. Each test is written as the attack, so removing the control fails the suite.
# ==============================================================================================

from anchors import (  # noqa: E402
    anchor_hash,
    build_anchor,
    load_anchors,
    pending_anchor_checkpoint,
    pending_anchor_exclusion,
    rebuild,
    sealed_checkpoint_ids,
    sealed_checkpoints_in_history_order,
    verify_chain,
)
from attestation import (  # noqa: E402
    derive_milestone_verdict,
    resolve_external_pass,
    sealed_commit_of,
    statuses_for_mechanism,
    verify_attestation,
)
from derive_counts import count_test_cases, derive_counts  # noqa: E402
from ledger_common import (  # noqa: E402
    CLOSURE_SCHEMA_VERSION,
    assurance_scope_files,
    in_assurance_scope,
    scope_fingerprint,
)
from lessons import (  # noqa: E402
    guardrail_effectiveness,
    guardrail_registry_path,
    load_guardrails,
    memory_fingerprint,
    preflight_fingerprint,
    preflight_staleness,
    resolve_control,
    resolve_lesson_evidence,
    suite_test_ids,
)
from policies import (  # noqa: E402
    audit_attacks,
    audit_findings,
    load_audit_registry,
    canonical_requirements,
    compare_requirement_sets,
    declared_requirement_refs,
    expected_requirement_refs,
    mandatory_gates,
    open_audits,
    parse_attacks,
    parse_checklist,
    parse_findings,
    source_ref,
)
from validate_checkpoint import (  # noqa: E402
    COUNT_CLAIM,
    POSITIVE_TERMINAL_STATUSES,
    _validate_closure_controls,
    _validate_derived_counts,
    _validate_findings_closure,
    _validate_guardrail_effectiveness,
    _validate_internal_assurance,
    _validate_seal_chronology,
)

CLOSURE_CHECKPOINT = PROJECT_ROOT / "docs" / "checkpoints" / "SETUP-00-CP-0008"
AUDIT_CHECKPOINT = PROJECT_ROOT / "docs" / "checkpoints" / "SETUP-00-CP-0007"


class ClosureFixture(unittest.TestCase):
    """A copy of the real closure checkpoint, made internally consistent, then attacked.

    Copying the delivery rather than inventing one keeps the expected requirement set real: the
    fixture carries the complete canonical anchored reference set, which no hand-written fixture
    could reproduce without also reproducing the bug the set exists to prevent. The cardinality is
    deliberately not stated here: a count in prose drifts away from its derivation, which is
    finding CP9-F-003, and every count that is evidence lives in COUNTS.json.
    """

    MILESTONE = "M0"

    def setUp(self) -> None:
        if not CLOSURE_CHECKPOINT.is_dir():
            self.skipTest("the closure checkpoint is not present in this checkout")
        self.temporary = tempfile.TemporaryDirectory()
        self.checkpoint = Path(self.temporary.name) / CLOSURE_CHECKPOINT.name
        shutil.copytree(CLOSURE_CHECKPOINT, self.checkpoint)
        self._refresh_derived_inputs()
        self.fingerprint = scope_fingerprint(PROJECT_ROOT)
        self.completeness_fingerprint = scope_fingerprint(
            PROJECT_ROOT, completeness_scope(PROJECT_ROOT, self.checkpoint))
        self._complete_matrix()
        self._write_rework_log()
        self._write_report()
        self._write_internal_assurance()
        self._write_findings_closure()
        self._neutralize_markdown_counts()
        self._write_counts()

    def tearDown(self) -> None:
        self.temporary.cleanup()

    # -- fixture construction ------------------------------------------------------------
    def _refresh_derived_inputs(self) -> None:
        """Re-derive the copied checkpoint's preflight and requirement set from current policy.

        The copy is a template, not a historical claim. Its sealed preflight was fresh for the
        memory of its own day and its matrix declared the expected set of its own day, so a fixture
        that kept both would fail for the fixture's own reasons every time a lesson or a checklist
        row is added. Re-deriving them keeps every attack below aimed at the control under test.
        """
        from derive_requirements import build
        from lessons import build_preflight

        recorded = read_json(self.checkpoint / "LESSON-PREFLIGHT.json")
        preflight = build_preflight(
            PROJECT_ROOT, str(recorded.get("gate") or "SETUP-00"),
            str(recorded.get("scope") or "control-plane"),
            list(recorded.get("technologies") or []), list(recorded.get("modules") or []))
        write_json_file(self.checkpoint / "LESSON-PREFLIGHT.json", preflight)
        self.preflight = preflight

        closure, matrix = build(PROJECT_ROOT, self.checkpoint, "SETUP-00")
        write_json_file(self.checkpoint / "CLOSURE-REQUIREMENTS.json", closure)
        write_json_file(self.checkpoint / "REQUIREMENTS-MATRIX.json", matrix)

    def _complete_matrix(self) -> None:
        evidence = ["checkpoint:PLAN.md"]
        matrix = read_json(self.checkpoint / "REQUIREMENTS-MATRIX.json")
        for row in matrix["requirements"]:
            row["status"] = "COMPLETE"
            row["implementationEvidence"] = list(evidence)
        write_json_file(self.checkpoint / "REQUIREMENTS-MATRIX.json", matrix)
        closure = read_json(self.checkpoint / "CLOSURE-REQUIREMENTS.json")
        for row in closure["requirements"]:
            row["implementationStatus"] = "COMPLETE"
            row["finalStatus"] = "COMPLETE"
            row["implementationEvidence"] = list(evidence)
        write_json_file(self.checkpoint / "CLOSURE-REQUIREMENTS.json", closure)
        self.matrix = matrix
        self.total = len(matrix["requirements"])
        self.mandatory = sum(1 for row in matrix["requirements"] if row["mandatory"])

    def _write_rework_log(self) -> None:
        entry = {
            "cycle": 1, "timestamp": NOW, "trigger": "fixture", "failedGate": None,
            "failureEvidence": [], "rootCauseSummary": None, "filesChanged": [],
            "commandsExecuted": ["cmd-0001"],
            "requiredGates": list(mandatory_gates(PROJECT_ROOT)),
            "gateResults": [
                {"gate": gate, "commandId": "cmd-0001", "exitCode": 0, "mandatory": True}
                for gate in mandatory_gates(PROJECT_ROOT)
            ],
            "scopeFingerprint": self.fingerprint,
            "result": "GREEN", "remainingFailures": 0,
        }
        (self.checkpoint / "REWORK-LOG.jsonl").write_text(
            json.dumps(entry) + "\n", encoding="utf-8", newline="\n")

    def _write_report(self) -> None:
        report = evaluate_matrix(PROJECT_ROOT, self.checkpoint, self.matrix)
        report = {
            "schemaVersion": "2.0.0", "checkpoint": self.checkpoint.name, "generatedAt": NOW,
            "matrix": "REQUIREMENTS-MATRIX.json", "auditor": "fixture",
            "scopeFingerprint": self.completeness_fingerprint, **report,
        }
        write_json_file(self.checkpoint / "COMPLETENESS-REPORT.json", report)
        self.report = report

    def _write_internal_assurance(self) -> None:
        # The rendered reports belong to the real run; the fixture replaces the machine-readable
        # ones, so a stale rendering would state counts the fixture no longer produces.
        for name in (f"{self.MILESTONE}-INTERNAL-RED-TEAM.md",
                     f"{self.MILESTONE}-INTERNAL-MIRROR.md"):
            stale = self.checkpoint / name
            if stale.is_file():
                stale.unlink()
        # Every registered audit, not only the one whose corrective delivery this fixture models.
        # A delivery inherits the mandatory battery of every audit the registry carries, so a
        # fixture that modelled one audit's rows would report the rest as missing the moment a new
        # audit is registered -- and that is a property of the fixture, not of the battery.
        attacks = []
        seen: set[str] = set()
        for audit in load_audit_registry(PROJECT_ROOT):
            for attack in audit_attacks(PROJECT_ROOT, audit):
                if attack["id"] in seen:
                    continue
                seen.add(attack["id"])
                attacks.append({
                    "attackId": attack["id"], "description": attack["mutation"],
                    "target": attack["target"], "mutation": attack["mutation"],
                    "expectedDefense": attack["expectedDefense"], "observed": "rejected",
                    "result": "DEFENDED", "evidence": ["attack:" + attack["id"]],
                    "mandatory": attack["mandatory"] == "true",
                })
        mandatory = [item for item in attacks if item["mandatory"]]
        write_json_file(self.checkpoint / f"{self.MILESTONE}-INTERNAL-RED-TEAM.json", {
            "schemaVersion": "1.1.0", "checkpoint": self.checkpoint.name, "generatedAt": NOW,
            "targetFingerprint": self.fingerprint, "source": "fixture",
            "baselineControl": {"result": "VALID",
                                "detail": "the unmutated fixture validates before any attack"},
            "attacks": attacks,
            "total": len(attacks), "defended": len(attacks), "escaped": 0,
            "mandatoryTotal": len(mandatory), "mandatoryDefended": len(mandatory),
            "result": "RED_TEAM_PASS",
        })
        write_json_file(self.checkpoint / f"{self.MILESTONE}-INTERNAL-MIRROR.json", {
            "schemaVersion": "1.0.0", "checkpoint": self.checkpoint.name,
            "milestone": self.MILESTONE, "generatedAt": NOW,
            "targetFingerprint": self.fingerprint,
            "auditorRole": "M0 Closure Auditor",
            "independence": "Internal quality assurance, not independent external validation.",
            "checks": [{
                "id": "MIR-001", "dimension": "fixture", "expectation": "fixture",
                "observed": "fixture", "result": "PASS", "evidence": ["checkpoint:PLAN.md"]}],
            "total": 1, "passed": 1, "failed": 0, "notApplicable": 0, "result": "PASS",
        })

    def _write_findings_closure(self) -> None:
        findings = []
        for audit in open_audits(PROJECT_ROOT, "SETUP-00", self.checkpoint.name):
            self.audit = audit
            for finding in audit_findings(PROJECT_ROOT, audit):
                findings.append({
                    "findingId": finding["id"], "severity": finding["severity"] or "HIGH",
                    "title": finding["title"], "originalExpected": "fixture",
                    "originalObserved": "fixture", "rootCause": "fixture",
                    "implementation": ["fixture"], "regressionTest": ["fixture"],
                    "verificationCommand": "python -m unittest discover -s tests",
                    "evidence": ["checkpoint:PLAN.md"], "status": "CLOSED",
                })
        # The artifact name and the audit identifier are read from the registry entry that binds
        # this audit to this corrective checkpoint, so the fixture follows the repository instead
        # of encoding one checkpoint's file name.
        closure_name = str(self.audit.get("findingsClosureFile") or "FINDINGS-CLOSURE.json")
        write_json_file(self.checkpoint / closure_name, {
            "schemaVersion": "1.0.0", "checkpoint": self.checkpoint.name,
            "auditId": self.audit.get("auditId"), "source": "fixture", "findings": findings,
            "total": len(findings), "closed": len(findings), "result": "CLOSED",
        })

    def _neutralize_markdown_counts(self) -> None:
        """Quote the counts the copied reports state.

        The fixture replaces the machine-readable assurance artifacts with its own, so the real
        reports' counts no longer describe it. Leaving them would make every test in this class
        fail on a claim the fixture itself invalidated. A test that needs a Markdown claim
        writes one.
        """
        claim = re.compile(
            r"(?<![0-9])(\d+)\s*/\s*(\d+)\s+"
            r"(TESTS|REQUIREMENTS|FINDINGS|ATTACKS|LESSONS|GUARDRAILS)\b")
        for document in sorted(self.checkpoint.glob("*.md")):
            text = document.read_text(encoding="utf-8")
            rewritten = claim.sub(
                lambda match: f"{match.group(1)} of {match.group(2)} {match.group(3)}", text)
            if rewritten != text:
                document.write_text(rewritten, encoding="utf-8", newline="\n")

    def _write_counts(self) -> None:
        counts = derive_counts(PROJECT_ROOT, self.checkpoint)
        write_json_file(self.checkpoint / "COUNTS.json", {
            "schemaVersion": "1.0.0", "checkpoint": self.checkpoint.name,
            "generatedAt": NOW, "counts": counts,
        })

    # -- state and probes ----------------------------------------------------------------
    def state(self, **overrides: object) -> dict:
        state = {
            "schemaVersion": CLOSURE_SCHEMA_VERSION,
            "gate": "SETUP-00",
            "status": "READY_FOR_REVIEW",
            "blockedBy": [],
            "secondToolValidation": {"status": "PENDING_MANUAL"},
            "requirementsMatrix": {
                "path": "REQUIREMENTS-MATRIX.json", "total": self.total,
                "mandatory": self.mandatory, "complete": self.total, "partial": 0, "missing": 0,
                "notApplicable": 0, "coveragePercent": 100.0,
            },
            "greenKeeper": {
                "status": "PASS", "cycles": 1, "remainingFailures": 0,
                "unresolvedReworkItems": 0, "log": "REWORK-LOG.jsonl", "externalBlockers": [],
                "evidence": [], "requiredGates": list(mandatory_gates(PROJECT_ROOT)),
                "scopeFingerprint": self.fingerprint,
            },
            "deliveryCompleteness": {
                "status": "PASS", "report": "COMPLETENESS-REPORT.json", "coveragePercent": 100.0,
                "evidenceCoveragePercent": 100.0, "auditor": "fixture", "evidence": [],
                "scopeFingerprint": self.completeness_fingerprint,
            },
            "reworkCycles": 1,
            "independentReview": {"status": "PENDING"},
            "redTeam": {"status": "PENDING"},
            "milestone": {"id": "M0", "title": "Development control plane",
                          "gates": ["SETUP-00"], "status": "PENDING"},
            "externalAuditRequired": False,
            "externalAuditReason": None,
            "guardrailEffectiveness": {
                key: guardrail_effectiveness(PROJECT_ROOT)[key] for key in (
                    "guardrailsTotal", "guardrailsResolved", "guardrailsTested",
                    "guardrailsEffective", "guardrailFailures")
            },
            "integrity": {"status": "PASS", "anchors": len(load_anchors(PROJECT_ROOT)),
                          "chainFile": ".iacode/anchors/checkpoint-chain.json", "evidence": []},
            "externalAttestation": {"status": "NONE", "path": None, "auditId": None,
                                    "evidence": []},
        }
        state.update(overrides)
        return state

    def quality(self, **overrides: str) -> dict:
        checks = {name: {"status": "PASS", "evidence": ["checkpoint:PLAN.md"],
                         "justification": None}
                  for name in BASE_QUALITY_DIMENSIONS + ("greenKeeper", "deliveryCompleteness")}
        checks["redTeam"] = {"status": "NOT_EXECUTED", "evidence": [], "justification": None}
        for name, status in overrides.items():
            checks[name] = {"status": status, "evidence": [], "justification": None}
        return checks

    def suite_results(self, failed: int = 0) -> dict:
        result = {"executed": True, "passed": 5, "failed": failed,
                  "command": "python -m unittest discover -s tests", "evidence": "fixture"}
        return {"schemaVersion": CLOSURE_SCHEMA_VERSION, "unit": result, "integration": result,
                "e2e": {"executed": False, "passed": 0, "failed": 0, "command": None,
                        "evidence": None}}

    def assurance_errors(self, state: dict | None = None, quality: dict | None = None,
                         tests: dict | None = None) -> list[str]:
        errors: list[str] = []
        _validate_delivery_assurance(
            PROJECT_ROOT, self.checkpoint, state or self.state(),
            quality or self.quality(), tests or self.suite_results(), errors, closure=True)
        return errors

    def memory_errors(self, state: dict | None = None) -> list[str]:
        errors: list[str] = []
        _validate_memory_policy(
            PROJECT_ROOT, self.checkpoint, state or self.state(), errors, closure=True)
        return errors

    def edit(self, name: str, mutate) -> None:
        document = read_json(self.checkpoint / name)
        mutate(document)
        write_json_file(self.checkpoint / name, document)


class PromotionInvariantTests(ClosureFixture):
    """M0-F-001: one invariant covers every positive terminal status, not only one of them."""

    RED_DIMENSIONS = ("unitTests", "staticAnalysis", "documentation", "greenKeeper",
                      "deliveryCompleteness")

    def test_the_consistent_delivery_passes(self) -> None:
        self.assertEqual(self.assurance_errors(), [])

    def test_every_positive_status_rejects_a_red_green_keeper(self) -> None:
        for status in POSITIVE_TERMINAL_STATUSES:
            state = self.state(status=status)
            state["greenKeeper"] = {**state["greenKeeper"], "status": "FAIL"}
            errors = self.assurance_errors(state)
            self.assertTrue(any("GREEN_KEEPER_GATE=PASS" in error for error in errors), status)

    def test_every_positive_status_rejects_a_red_completeness_gate(self) -> None:
        for status in POSITIVE_TERMINAL_STATUSES:
            state = self.state(status=status)
            state["deliveryCompleteness"] = {**state["deliveryCompleteness"], "status": "FAIL"}
            errors = self.assurance_errors(state)
            self.assertTrue(
                any("DELIVERY_COMPLETENESS_GATE=PASS" in error for error in errors), status)

    def test_every_positive_status_rejects_every_red_quality_dimension(self) -> None:
        for status in POSITIVE_TERMINAL_STATUSES:
            for dimension in self.RED_DIMENSIONS:
                errors = self.assurance_errors(
                    self.state(status=status), self.quality(**{dimension: "FAIL"}))
                self.assertTrue(
                    any(f"{dimension}=FAIL" in error for error in errors),
                    f"{status}/{dimension}: {errors}")

    def test_every_positive_status_rejects_an_unexecuted_mandatory_dimension(self) -> None:
        for status in POSITIVE_TERMINAL_STATUSES:
            errors = self.assurance_errors(
                self.state(status=status), self.quality(staticAnalysis="NOT_EXECUTED"))
            self.assertTrue(any("to be executed" in error for error in errors), status)

    def test_every_positive_status_rejects_a_partial_requirement(self) -> None:
        self.edit("REQUIREMENTS-MATRIX.json",
                  lambda d: d["requirements"][0].update({"status": "PARTIAL"}))
        for status in POSITIVE_TERMINAL_STATUSES:
            errors = self.assurance_errors(self.state(status=status))
            self.assertTrue(any("PARTIAL" in error for error in errors), status)

    def test_a_terminal_status_requires_an_independent_verdict(self) -> None:
        for status in ("INTERNAL_GATE_PASS", "MILESTONE_EXTERNAL_PASS", "GATE_PASS"):
            errors = self.assurance_errors(self.state(status=status))
            self.assertTrue(
                any("independent review verdict" in error for error in errors), status)
            self.assertTrue(any("Red Team verdict" in error for error in errors), status)

    def test_review_ready_still_requires_a_pending_verdict(self) -> None:
        errors = self.assurance_errors(self.state(
            independentReview={"status": "APPROVED"}, redTeam={"status": "RED_TEAM_PASS"}))
        self.assertTrue(any("PENDING" in error for error in errors), errors)


class MandatoryGatePolicyTests(ClosureFixture):
    """M0-F-005: the mandatory gate set belongs to policy, not to the caller."""

    def test_the_policy_declares_a_non_empty_closed_set(self) -> None:
        gates = mandatory_gates(PROJECT_ROOT)
        self.assertTrue(gates)
        self.assertIn("tests", gates)
        self.assertIn("checkpointValidation", gates)

    def test_a_cycle_measured_against_no_gate_is_rejected(self) -> None:
        log = self.checkpoint / "REWORK-LOG.jsonl"
        entry = json.loads(log.read_text(encoding="utf-8").strip())
        entry["requiredGates"] = []
        entry["gateResults"] = []
        log.write_text(json.dumps(entry) + "\n", encoding="utf-8", newline="\n")
        errors = self.assurance_errors()
        self.assertTrue(any("canonical mandatory set" in error for error in errors), errors)

    def test_a_cycle_missing_one_mandatory_gate_is_rejected(self) -> None:
        log = self.checkpoint / "REWORK-LOG.jsonl"
        entry = json.loads(log.read_text(encoding="utf-8").strip())
        entry["requiredGates"] = entry["requiredGates"][:-1]
        entry["gateResults"] = entry["gateResults"][:-1]
        log.write_text(json.dumps(entry) + "\n", encoding="utf-8", newline="\n")
        errors = self.assurance_errors()
        self.assertTrue(any("canonical mandatory set" in error for error in errors), errors)

    def test_a_mandatory_gate_that_exited_nonzero_is_rejected(self) -> None:
        log = self.checkpoint / "REWORK-LOG.jsonl"
        entry = json.loads(log.read_text(encoding="utf-8").strip())
        entry["gateResults"][0]["exitCode"] = 1
        log.write_text(json.dumps(entry) + "\n", encoding="utf-8", newline="\n")
        errors = self.assurance_errors()
        self.assertTrue(any("exiting 1" in error for error in errors), errors)

    def test_a_gate_without_command_evidence_is_rejected(self) -> None:
        log = self.checkpoint / "REWORK-LOG.jsonl"
        entry = json.loads(log.read_text(encoding="utf-8").strip())
        entry["gateResults"][0]["commandId"] = ""
        log.write_text(json.dumps(entry) + "\n", encoding="utf-8", newline="\n")
        errors = self.assurance_errors()
        self.assertTrue(any("no command evidence" in error for error in errors), errors)

    def test_a_pass_measured_before_a_source_change_is_stale(self) -> None:
        log = self.checkpoint / "REWORK-LOG.jsonl"
        entry = json.loads(log.read_text(encoding="utf-8").strip())
        entry["scopeFingerprint"] = "0" * 64
        log.write_text(json.dumps(entry) + "\n", encoding="utf-8", newline="\n")
        state = self.state()
        state["greenKeeper"] = {**state["greenKeeper"], "scopeFingerprint": "0" * 64}
        errors = self.assurance_errors(state)
        self.assertTrue(any("STALE" in error for error in errors), errors)

    def test_a_cycle_without_a_fingerprint_cannot_pass(self) -> None:
        log = self.checkpoint / "REWORK-LOG.jsonl"
        entry = json.loads(log.read_text(encoding="utf-8").strip())
        entry.pop("scopeFingerprint")
        log.write_text(json.dumps(entry) + "\n", encoding="utf-8", newline="\n")
        state = self.state()
        state["greenKeeper"] = {**state["greenKeeper"], "scopeFingerprint": None}
        errors = self.assurance_errors(state)
        self.assertTrue(any("scope fingerprint" in error for error in errors), errors)

    def test_the_assurance_scope_covers_code_tests_and_policy(self) -> None:
        self.assertTrue(in_assurance_scope("scripts/development-ledger/validate_checkpoint.py"))
        self.assertTrue(in_assurance_scope("tests/test_development_ledger.py"))
        self.assertTrue(in_assurance_scope(".iacode/policies/quality-gates.json"))
        self.assertFalse(in_assurance_scope(f"docs/checkpoints/{CLOSURE_CHECKPOINT.name}/STATE.json"))
        self.assertIn("tests/test_development_ledger.py", assurance_scope_files(PROJECT_ROOT))


class ExpectedRequirementSetTests(ClosureFixture):
    """M0-F-006: the denominator is derived from sources the delivery does not own."""

    def test_the_expected_set_is_derived_from_the_canonical_sources(self) -> None:
        preflight = read_json(self.checkpoint / "LESSON-PREFLIGHT.json")
        expected = expected_requirement_refs(
            PROJECT_ROOT, "SETUP-00", self.checkpoint.name, preflight)
        canonical = canonical_requirements(PROJECT_ROOT, "SETUP-00")
        self.assertEqual(
            sum(1 for key in expected if key.startswith("canonical:")), len(canonical))
        self.assertTrue(any(key.startswith("finding:") for key in expected))
        self.assertTrue(any(key.startswith("attack:") for key in expected))
        self.assertTrue(any(key.startswith("lesson:") for key in expected))

    def test_the_checklist_is_reparsed_rather_than_trusted(self) -> None:
        rows = parse_checklist(
            (PROJECT_ROOT / "docs" / "SETUP-00-CHECKLIST.md").read_text(encoding="utf-8"))
        self.assertEqual([row["key"] for row in rows],
                         [item["key"] for item in canonical_requirements(PROJECT_ROOT, "SETUP-00")])

    def test_deleting_a_requirement_and_recomputing_the_counts_still_fails(self) -> None:
        self.edit("REQUIREMENTS-MATRIX.json",
                  lambda d: d.update({"requirements": d["requirements"][1:]}))
        self._write_report()
        state = self.state()
        state["requirementsMatrix"] = {
            **state["requirementsMatrix"], "total": self.total - 1, "complete": self.total - 1}
        errors = self.assurance_errors(state)
        self.assertTrue(
            any("canonical expected set requires" in error for error in errors), errors)

    def test_an_unexpected_anchored_requirement_is_rejected(self) -> None:
        def mutate(document: dict) -> None:
            row = json.loads(json.dumps(document["requirements"][0]))
            row["id"] = "REQ-9999"
            row["sourceRef"] = "canonical:SETUP-00#99.9"
            document["requirements"].append(row)

        self.edit("REQUIREMENTS-MATRIX.json", mutate)
        errors = self.assurance_errors()
        self.assertTrue(any("canonical:SETUP-00#99.9" in error for error in errors), errors)

    def test_a_requirement_without_an_anchor_is_rejected(self) -> None:
        self.edit("REQUIREMENTS-MATRIX.json",
                  lambda d: d["requirements"][0].pop("sourceRef", None))
        errors = self.assurance_errors()
        self.assertTrue(any("anchored sourceRef" in error for error in errors), errors)

    def test_two_requirements_may_not_claim_the_same_anchor(self) -> None:
        def mutate(document: dict) -> None:
            document["requirements"][1]["sourceRef"] = document["requirements"][0]["sourceRef"]

        self.edit("REQUIREMENTS-MATRIX.json", mutate)
        errors = self.assurance_errors()
        self.assertTrue(any("more than one requirement" in error for error in errors), errors)

    def test_the_state_mandatory_count_is_cross_checked(self) -> None:
        state = self.state()
        state["requirementsMatrix"] = {**state["requirementsMatrix"],
                                       "mandatory": self.mandatory + 3}
        errors = self.assurance_errors(state)
        self.assertTrue(any("mandatory" in error for error in errors), errors)

    def test_a_downgraded_matrix_cannot_escape_the_comparison(self) -> None:
        self.edit("REQUIREMENTS-MATRIX.json", lambda d: d.update({"schemaVersion": "1.0.0"}))
        errors: list[str] = []
        _validate_closure_controls(
            PROJECT_ROOT, self.checkpoint, self.state(), {}, [], errors, allow_pending_seal=True)
        self.assertTrue(any("schemaVersion 2.0.0" in error for error in errors), errors)

    def test_the_two_requirement_views_must_agree(self) -> None:
        self.edit("CLOSURE-REQUIREMENTS.json",
                  lambda d: d["requirements"][0].update({"finalStatus": "PARTIAL"}))
        errors: list[str] = []
        _validate_closure_controls(
            PROJECT_ROOT, self.checkpoint, self.state(), {}, [], errors, allow_pending_seal=True)
        self.assertTrue(any("closure view records" in error for error in errors), errors)

    def test_set_comparison_reports_omission_and_addition(self) -> None:
        expected = {"canonical:G#1.1": {"sourceReference": "row 1.1"}}
        findings = compare_requirement_sets(expected, {"canonical:G#9.9": ["REQ-0001"]})
        self.assertEqual(len(findings), 2)
        self.assertTrue(all(finding["severity"] == "BLOCKING" for finding in findings))

    def test_source_reference_parsing_accepts_only_known_kinds(self) -> None:
        self.assertEqual(source_ref("canonical:SETUP-00#1.1"), ("canonical", "SETUP-00#1.1"))
        self.assertEqual(source_ref("local:something"), ("local", "something"))
        self.assertIsNone(source_ref("nonsense"))
        self.assertIsNone(source_ref("unknownkind:value"))


class ExternalAttestationTests(ClosureFixture):
    """M0-F-002: a milestone verdict is derived from an attestation, never self-asserted.

    The attestation document itself is exercised by ``AuditAttestationModelTests``, which works
    against the repository's own sealed history. This class keeps the *state* cases: what a
    checkpoint may and may not claim about itself.
    """

    def _sealed_pair(self) -> tuple[str, str]:
        sealed = sealed_checkpoints_in_history_order(PROJECT_ROOT)
        if len(sealed) < 2:
            self.skipTest("the repository has fewer than two sealed checkpoints")
        return sealed[-2], sealed[-1]

    def _attestation(self, **overrides: object) -> dict:
        subject, audit = self._sealed_pair()
        document = {
            "schemaVersion": "2.0.0", "auditId": "M0-TEST", "milestone": "M0",
            "validationMechanism": "FRESH_SESSION_INDEPENDENT_AUDIT",
            "crossToolValidation": "NOT_AVAILABLE",
            "auditorRole": "milestone independent auditor", "tool": "a tool",
            "provider": "a provider", "model": "a model", "freshSession": True,
            "subjectCheckpoint": subject,
            "subjectCommit": sealed_commit_of(PROJECT_ROOT, subject),
            "auditCheckpoint": audit,
            "reviewResult": "APPROVED", "redTeamResult": "RED_TEAM_PASS",
            "completeness": 100.0, "evidenceCoverage": 100.0, "testResult": "PASS",
            "createdAt": NOW,
        }
        document.update(overrides)
        document["__path"] = "fixture-attestation.json"
        return document

    def test_an_implementer_checkpoint_cannot_declare_an_external_pass(self) -> None:
        state = self.state(status="MILESTONE_EXTERNAL_PASS")
        state["milestone"] = {**state["milestone"], "status": "PASSED"}
        state["secondToolValidation"] = {"status": "PASSED", "tool": "self",
                                         "provider": "self", "model": "self",
                                         "validatedAt": NOW, "justification": None,
                                         "evidence": []}
        errors = self.memory_errors(state)
        self.assertTrue(
            any("belongs to the audit checkpoint" in error for error in errors), errors)

    def test_second_tool_validation_alone_is_not_enough(self) -> None:
        state = self.state()
        state["secondToolValidation"] = {"status": "PASSED", "tool": "a tool",
                                         "provider": "a provider", "model": "a model",
                                         "validatedAt": NOW, "justification": None,
                                         "evidence": []}
        errors = self.memory_errors(state)
        self.assertTrue(any("independent audit" in error for error in errors), errors)

    def test_a_verdict_naming_a_subject_without_an_attestation_is_refused(self) -> None:
        state = self.state(status="MILESTONE_INDEPENDENT_AUDIT_PASS")
        state["milestone"] = {**state["milestone"], "status": "PASSED"}
        state["secondToolValidation"] = {"status": "PASSED", "tool": "a tool",
                                         "provider": "a provider", "model": "a model",
                                         "validatedAt": NOW, "justification": None,
                                         "evidence": []}
        state["externalAttestation"] = {"status": "VERIFIED", "path": None, "auditId": None,
                                        "subjectCheckpoint": "SETUP-00-CP-9999",
                                        "subjectCommit": None, "validationMechanism": None,
                                        "evidence": []}
        errors = self.memory_errors(state)
        self.assertTrue(any("may not be self-asserted" in error for error in errors), errors)

    def test_an_attestation_naming_the_subject_as_its_own_auditor_is_rejected(self) -> None:
        subject, _audit = self._sealed_pair()
        errors = verify_attestation(
            PROJECT_ROOT, self._attestation(auditCheckpoint=subject), subject, None)
        self.assertTrue(
            any("may not be authored by the delivery it judges" in error for error in errors),
            errors)

    def test_a_failed_review_cannot_produce_an_external_pass(self) -> None:
        """Kept under its original name: sealed matrices and the memory cite this case."""
        subject, _audit = self._sealed_pair()
        errors = verify_attestation(
            PROJECT_ROOT, self._attestation(reviewResult="REWORK_REQUIRED"), subject, None)
        self.assertTrue(any("requires APPROVED" in error for error in errors), errors)

    def test_a_failed_red_team_cannot_produce_an_external_pass(self) -> None:
        subject, _audit = self._sealed_pair()
        errors = verify_attestation(
            PROJECT_ROOT, self._attestation(redTeamResult="RED_TEAM_FAIL"), subject, None)
        self.assertTrue(any("requires RED_TEAM_PASS" in error for error in errors), errors)

    def test_no_attestation_means_no_external_pass(self) -> None:
        attestation, reasons = resolve_external_pass(
            PROJECT_ROOT, "M0", "SETUP-00-CP-9999", None)
        self.assertIsNone(attestation)
        self.assertTrue(any("may not be self-asserted" in reason for reason in reasons), reasons)

    def test_an_intermediate_gate_cannot_take_the_external_status(self) -> None:
        state = self.state(status="MILESTONE_EXTERNAL_PASS", gate="GATE 1")
        state["milestone"] = {"id": "M1", "title": "IACode V0 foundation",
                              "gates": ["GATE 0", "GATE 1", "GATE 2", "GATE 3"],
                              "status": "PASSED"}
        state["secondToolValidation"] = {"status": "PASSED", "tool": "t", "provider": "p",
                                         "model": "m", "validatedAt": NOW,
                                         "justification": None, "evidence": []}
        errors = self.memory_errors(state)
        self.assertTrue(
            any("milestone-closing Gate" in error for error in errors), errors)


class PreflightFreshnessTests(ClosureFixture):
    """M0-F-003: the preflight is recomputed, not compared with a copy of its own counts."""

    def test_the_repository_preflight_is_fresh(self) -> None:
        preflight = read_json(self.checkpoint / "LESSON-PREFLIGHT.json")
        self.assertEqual(preflight_staleness(PROJECT_ROOT, preflight, "SETUP-00"), [])

    def test_the_fingerprint_covers_the_memory(self) -> None:
        first = memory_fingerprint(PROJECT_ROOT)
        self.assertEqual(first, memory_fingerprint(PROJECT_ROOT))
        self.assertNotEqual(
            preflight_fingerprint(PROJECT_ROOT, "SETUP-00", "a", [], []),
            preflight_fingerprint(PROJECT_ROOT, "GATE 1", "a", [], []))

    def test_the_preflight_of_the_current_delivery_is_fresh(self) -> None:
        """The real invariant: the preflight the delivery ships recomputes against the memory.

        The fixture regenerates its own copy, so this case reads the checkpoint LATEST names and
        recomputes that one. It is derived, never a checkpoint written here by name.
        """
        from ledger_common import resolve_latest

        latest = resolve_latest(PROJECT_ROOT)
        path = latest / "LESSON-PREFLIGHT.json"
        if not path.is_file():
            self.skipTest("the latest checkpoint carries no preflight yet")
        state = read_json(latest / "STATE.json")
        self.assertEqual(
            preflight_staleness(PROJECT_ROOT, read_json(path), str(state.get("gate"))), [])

    def test_a_changed_fingerprint_makes_the_preflight_stale(self) -> None:
        preflight = read_json(self.checkpoint / "LESSON-PREFLIGHT.json")
        preflight["inputsFingerprint"] = "0" * 64
        messages = preflight_staleness(PROJECT_ROOT, preflight, "SETUP-00")
        self.assertTrue(any("STALE" in message for message in messages), messages)

    def test_a_preflight_from_another_gate_is_refused(self) -> None:
        preflight = read_json(self.checkpoint / "LESSON-PREFLIGHT.json")
        messages = preflight_staleness(PROJECT_ROOT, preflight, "GATE 1")
        self.assertTrue(
            any("may not be reused across Gates" in message for message in messages), messages)

    def test_a_dropped_lesson_makes_the_preflight_stale(self) -> None:
        preflight = read_json(self.checkpoint / "LESSON-PREFLIGHT.json")
        preflight["applicable"] = preflight["applicable"][:-1]
        preflight["derivedRequirements"] = preflight["derivedRequirements"][:-1]
        messages = preflight_staleness(PROJECT_ROOT, preflight, "SETUP-00")
        self.assertTrue(any("STALE" in message for message in messages), messages)

    def test_the_checkpoint_refuses_a_stale_preflight(self) -> None:
        self.edit("LESSON-PREFLIGHT.json",
                  lambda d: d.update({"inputsFingerprint": "0" * 64}))
        errors = self.memory_errors()
        self.assertTrue(any("STALE" in error for error in errors), errors)

    def test_a_closure_checkpoint_requires_the_versioned_preflight(self) -> None:
        self.edit("LESSON-PREFLIGHT.json", lambda d: d.update({"schemaVersion": "1.0.0"}))
        errors = self.memory_errors()
        self.assertTrue(any("schemaVersion 2.0.0" in error for error in errors), errors)


class IntegrityAnchorTests(unittest.TestCase):
    """M0-F-007: sealed history is anchored outside the content it describes."""

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name) / "clone"
        if not clone_with_worktree(self.root):
            self.skipTest("the repository cannot be cloned in this environment")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def _verify(self) -> list[str]:
        """Verify the chain the way the product does, with a derived exclusion.

        CP9-F-002: this call named ``SETUP-00-CP-0008`` by literal while ``verify_integrity.py``
        derived the same exclusion from repository state. Performing the protocol's own next step
        -- a successor anchoring its sealed predecessor -- then turned the mandatory ``tests`` gate
        red. The rule now has one implementation, ``anchors.pending_anchor_exclusion``, which the
        CLI, the validator and this suite all ask.
        """
        return verify_chain(self.root, require_sealed=True,
                            exclude=pending_anchor_exclusion(self.root))

    def _anchored_checkpoint_that_is_not_pending(self) -> str:
        """A checkpoint the chain anchors and the pending rule does not forgive."""
        pending = pending_anchor_checkpoint(self.root)
        candidates = [item["checkpointId"] for item in load_anchors(self.root)
                      if item["checkpointId"] != pending]
        self.assertTrue(candidates, "the chain anchors nothing beyond the pending checkpoint")
        return candidates[-1]

    def _edit_anchors(self, mutate) -> None:
        path = self.root / ".iacode" / "anchors" / "checkpoint-chain.json"
        document = read_json(path)
        mutate(document)
        write_json_file(path, document)

    def test_the_repository_chain_verifies(self) -> None:
        self.assertEqual(self._verify(), [])

    def test_a_moved_historical_tag_is_detected(self) -> None:
        anchors = load_anchors(self.root)
        self.assertGreaterEqual(len(anchors), 3, "the chain is too short to move a tag inside it")
        moved, onto = anchors[1]["checkpointId"], anchors[2]["checkpointId"]
        run(["git", "tag", "-f", f"iacode-checkpoints/{moved}",
             f"refs/tags/iacode-checkpoints/{onto}"], self.root)
        errors = self._verify()
        self.assertTrue(any(moved in error for error in errors), errors)

    def test_an_anchor_pointing_at_another_commit_is_detected(self) -> None:
        self._edit_anchors(lambda d: d["anchors"][1].update({"commit": d["anchors"][2]["commit"]}))
        errors = self._verify()
        self.assertTrue(any("anchorHash" in error or "tag" in error for error in errors), errors)

    def test_an_unexpected_tree_is_detected(self) -> None:
        def mutate(document: dict) -> None:
            document["anchors"][2]["treeHash"] = "0" * 40
            document["anchors"][2]["anchorHash"] = anchor_hash(document["anchors"][2])
            previous = document["anchors"][2]["anchorHash"]
            for anchor in document["anchors"][3:]:
                anchor["previousAnchorHash"] = previous
                anchor["anchorHash"] = anchor_hash(anchor)
                previous = anchor["anchorHash"]

        self._edit_anchors(mutate)
        errors = self._verify()
        self.assertTrue(any("tree" in error for error in errors), errors)

    def test_a_broken_link_between_anchors_is_detected(self) -> None:
        self._edit_anchors(lambda d: d["anchors"][2].update({"previousAnchorHash": "0" * 64}))
        errors = self._verify()
        self.assertTrue(any("chain" in error for error in errors), errors)

    def test_a_recomputed_anchor_hash_must_match_its_fields(self) -> None:
        self._edit_anchors(lambda d: d["anchors"][0].update({"anchorHash": "0" * 64}))
        errors = self._verify()
        self.assertTrue(any("anchorHash" in error for error in errors), errors)

    def test_a_sealed_checkpoint_without_an_anchor_is_detected(self) -> None:
        victim = self._anchored_checkpoint_that_is_not_pending()
        self._edit_anchors(lambda d: d.update({
            "anchors": [item for item in d["anchors"] if item["checkpointId"] != victim]}))
        errors = self._verify()
        self.assertTrue(
            any("no integrity anchor" in error and victim in error for error in errors), errors)

    def test_the_pending_exclusion_is_the_newest_sealed_checkpoint(self) -> None:
        """The exclusion rule is a property of history, not a name someone typed."""
        sealed = sealed_checkpoints_in_history_order(self.root)
        self.assertEqual(pending_anchor_checkpoint(self.root), sealed[-1])
        self.assertEqual(pending_anchor_exclusion(self.root), {sealed[-1]})
        self.assertEqual(set(sealed), set(sealed_checkpoint_ids(self.root)))

    def test_every_sealed_checkpoint_but_the_newest_is_anchored(self) -> None:
        anchored = {item["checkpointId"] for item in load_anchors(self.root)}
        owed = set(sealed_checkpoints_in_history_order(self.root)) - anchored
        self.assertTrue(owed <= pending_anchor_exclusion(self.root), sorted(owed))

    def test_the_chain_can_be_rebuilt_from_the_repository(self) -> None:
        anchors = load_anchors(self.root)
        rebuilt = rebuild(self.root, [item["checkpointId"] for item in anchors])
        self.assertEqual(rebuilt["anchors"], anchors)

    def test_an_anchor_binds_its_predecessor(self) -> None:
        anchors = load_anchors(self.root)
        first = anchors[0]
        second = build_anchor(self.root, anchors[1]["checkpointId"], anchors[1]["commit"], first)
        self.assertEqual(second["anchorHash"], anchors[1]["anchorHash"])
        other = build_anchor(self.root, anchors[1]["checkpointId"], anchors[1]["commit"], None)
        self.assertNotEqual(other["anchorHash"], anchors[1]["anchorHash"])

    def test_the_trust_model_is_documented_without_overclaiming(self) -> None:
        document = read_json(self.root / ".iacode" / "anchors" / "checkpoint-chain.json")
        text = document["trustModel"].lower()
        self.assertIn("tamper evident", text)
        self.assertIn("not a signature", text)


class LessonResolutionTests(unittest.TestCase):
    """M0-F-004: a control reference is resolved against the repository, not merely typed."""

    def test_a_test_control_must_exist_in_the_suite(self) -> None:
        self.assertIsNone(resolve_control(PROJECT_ROOT, {
            "kind": "test",
            "reference": "StatusBlockerInvariantTests.test_ready_for_review_with_blocker_fails"}))
        self.assertIn("does not exist in the suite", resolve_control(PROJECT_ROOT, {
            "kind": "test", "reference": "NoSuchTests.test_nothing"}) or "")

    def test_an_invariant_control_must_be_defined_in_the_tooling(self) -> None:
        self.assertIsNone(resolve_control(PROJECT_ROOT, {
            "kind": "invariant", "reference": "validate_checkpoint._validate_status_blockers"}))
        self.assertIn("defined nowhere", resolve_control(PROJECT_ROOT, {
            "kind": "invariant", "reference": "_no_such_invariant"}) or "")

    def test_a_path_control_must_exist(self) -> None:
        self.assertIsNone(resolve_control(PROJECT_ROOT, {
            "kind": "validator", "reference": "scripts/development-ledger/validate_lessons.py"}))
        self.assertIn("does not exist", resolve_control(PROJECT_ROOT, {
            "kind": "policy", "reference": "docs/NOTHING-HERE.md"}) or "")

    def test_a_control_path_may_not_escape_the_repository(self) -> None:
        message = resolve_control(PROJECT_ROOT, {"kind": "schema", "reference": "../escape.json"})
        self.assertIn("escapes", message or "")

    def test_lesson_evidence_must_resolve(self) -> None:
        self.assertIsNone(resolve_lesson_evidence(PROJECT_ROOT, "file:START-HERE.md"))
        self.assertIn("does not exist",
                      resolve_lesson_evidence(PROJECT_ROOT, "file:docs/nothing.md") or "")
        self.assertIn("unsupported",
                      resolve_lesson_evidence(PROJECT_ROOT, "command:cmd-0001") or "")

    def test_the_suite_identifiers_include_class_qualified_names(self) -> None:
        identifiers = suite_test_ids(PROJECT_ROOT)
        self.assertIn("LessonResolutionTests.test_lesson_evidence_must_resolve", identifiers)


class GuardrailRegistryTests(unittest.TestCase):
    """A GUARDED lesson names a registry entry, and the entry is verified by a real test."""

    def test_every_guarded_lesson_names_a_registered_guardrail(self) -> None:
        guardrails = load_guardrails(PROJECT_ROOT)
        self.assertTrue(guardrails)
        for lesson in load_lessons(PROJECT_ROOT):
            if lesson["status"] != "GUARDED":
                continue
            declared = lesson.get("guardrails") or []
            self.assertTrue(declared, lesson["lessonId"])
            for identifier in declared:
                self.assertIn(identifier, guardrails, lesson["lessonId"])
                self.assertIn(lesson["lessonId"], guardrails[identifier]["lessons"])

    def test_every_guardrail_is_verified_by_a_test_that_exists(self) -> None:
        identifiers = suite_test_ids(PROJECT_ROOT)
        for guardrail in load_guardrails(PROJECT_ROOT).values():
            self.assertTrue(guardrail["verifiedBy"], guardrail["guardrailId"])
            for test_id in guardrail["verifiedBy"]:
                self.assertIn(test_id, identifiers, guardrail["guardrailId"])

    def test_every_guardrail_control_resolves(self) -> None:
        for guardrail in load_guardrails(PROJECT_ROOT).values():
            message = resolve_control(
                PROJECT_ROOT, {"kind": guardrail["kind"], "reference": guardrail["reference"]})
            self.assertIsNone(message, f"{guardrail['guardrailId']}: {message}")

    def test_guardrail_effectiveness_is_measured_not_asserted(self) -> None:
        measured = guardrail_effectiveness(PROJECT_ROOT)
        self.assertEqual(measured["guardrailsResolved"], measured["guardrailsTotal"])
        self.assertEqual(measured["guardrailsTested"], measured["guardrailsTotal"])
        self.assertEqual(measured["guardrailsEffective"], measured["guardrailsTotal"])
        self.assertEqual(measured["guardrailFailures"], 0)

    def test_an_unresolved_guardrail_failure_is_counted(self) -> None:
        lessons = json.loads(json.dumps(load_lessons(PROJECT_ROOT)))
        baseline = guardrail_effectiveness(PROJECT_ROOT, lessons)["guardrailFailures"]
        guarded = next(item for item in lessons if item["status"] == "GUARDED")
        guarded["guardrailFailures"] = [
            {"observedAt": NOW, "checkpoint": "TEST", "detail": "GUARDRAIL_FAILURE: bypassed"}]
        guarded["recurrenceCount"] = 1
        measured = guardrail_effectiveness(PROJECT_ROOT, lessons)
        self.assertEqual(measured["guardrailFailures"], baseline + 1)
        self.assertIn(guarded["lessonId"], measured["lessonsWithUnresolvedFailures"])

    def test_a_resolved_guardrail_failure_no_longer_blocks(self) -> None:
        lessons = json.loads(json.dumps(load_lessons(PROJECT_ROOT)))
        baseline = guardrail_effectiveness(PROJECT_ROOT, lessons)["guardrailFailures"]
        guarded = next(item for item in lessons if item["status"] == "GUARDED")
        guarded["guardrailFailures"] = [{
            "observedAt": NOW, "checkpoint": "TEST",
            "detail": "GUARDRAIL_FAILURE: bypassed", "resolvedIn": "SETUP-00-CP-0008"}]
        guarded["recurrenceCount"] = 1
        measured = guardrail_effectiveness(PROJECT_ROOT, lessons)
        self.assertEqual(measured["guardrailFailures"], baseline)
        self.assertNotIn(guarded["lessonId"], measured["lessonsWithUnresolvedFailures"])

    def test_the_registry_may_not_name_an_unknown_lesson(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            shutil.copytree(PROJECT_ROOT / ".iacode", root / ".iacode")
            copy_ledger_tooling(root)
            shutil.copytree(PROJECT_ROOT / "tests", root / "tests",
                            ignore=shutil.ignore_patterns("__pycache__"))
            registry = root / ".iacode" / "memory" / "guardrails" / "registry.json"
            document = read_json(registry)
            document["guardrails"][0]["lessons"] = ["LSN-9999"]
            write_json_file(registry, document)
            errors = validate_memory(root)
            self.assertTrue(any("not in the memory" in error for error in errors), errors)


class LessonProvenanceTests(unittest.TestCase):
    """M0-F-011: a lesson must cite a source that records the finding it names."""

    def test_every_repository_lesson_cites_a_resolvable_source(self) -> None:
        self.assertEqual(validate_memory(PROJECT_ROOT), [])

    def test_a_finding_absent_from_the_cited_checkpoint_is_rejected(self) -> None:
        from lessons import _resolve_source_locator

        lesson = make_lesson(source={
            "gate": "SETUP-00", "checkpoint": "SETUP-00-CP-0003", "finding": "R9999"})
        message = _resolve_source_locator(PROJECT_ROOT, lesson)
        self.assertIn("appears in none of the checkpoints", message or "")

    def test_a_nonexistent_checkpoint_is_rejected(self) -> None:
        from lessons import _resolve_source_locator

        lesson = make_lesson(source={
            "gate": "SETUP-00", "checkpoint": "SETUP-00-CP-9999", "finding": "R1"})
        message = _resolve_source_locator(PROJECT_ROOT, lesson)
        self.assertIn("not a checkpoint in this repository", message or "")

    def test_a_correct_locator_resolves(self) -> None:
        from lessons import _resolve_source_locator

        lesson = make_lesson(source={
            "gate": "SETUP-00", "checkpoint": "SETUP-00-CP-0004", "finding": "R3"})
        self.assertIsNone(_resolve_source_locator(PROJECT_ROOT, lesson))


class DerivedCountTests(ClosureFixture):
    """M0-F-008: an evidential count is derived once and verified wherever it is stated."""

    def test_the_stored_counts_match_the_derivation(self) -> None:
        errors: list[str] = []
        _validate_derived_counts(PROJECT_ROOT, self.checkpoint, self.state(), errors)
        self.assertEqual(errors, [])

    def test_a_forged_count_is_rejected(self) -> None:
        self.edit("COUNTS.json",
                  lambda d: d["counts"]["LESSONS"].update({"numerator": 999}))
        errors: list[str] = []
        _validate_derived_counts(PROJECT_ROOT, self.checkpoint, self.state(), errors)
        self.assertTrue(any("contradicts the derived" in error for error in errors), errors)

    def test_a_markdown_claim_that_contradicts_the_derivation_is_rejected(self) -> None:
        (self.checkpoint / "FINAL-REPORT.md").write_text(
            "# Final Report\n\nTests: 9999/9999 TESTS PASS\n", encoding="utf-8", newline="\n")
        errors: list[str] = []
        _validate_derived_counts(PROJECT_ROOT, self.checkpoint, self.state(), errors)
        self.assertTrue(any("contradicts the derived" in error for error in errors), errors)

    def test_a_markdown_claim_that_matches_the_derivation_is_accepted(self) -> None:
        counts = derive_counts(PROJECT_ROOT, self.checkpoint)["LESSONS"]
        (self.checkpoint / "FINAL-REPORT.md").write_text(
            f"# Final Report\n\nLessons: {counts['numerator']}/{counts['denominator']} LESSONS "
            f"guarded.\n", encoding="utf-8", newline="\n")
        errors: list[str] = []
        _validate_derived_counts(PROJECT_ROOT, self.checkpoint, self.state(), errors)
        self.assertEqual(errors, [])

    def test_a_missing_counts_artifact_is_rejected(self) -> None:
        (self.checkpoint / "COUNTS.json").unlink()
        errors: list[str] = []
        _validate_derived_counts(PROJECT_ROOT, self.checkpoint, self.state(), errors)
        self.assertTrue(any("requires COUNTS.json" in error for error in errors), errors)

    def test_the_test_count_comes_from_discovery(self) -> None:
        self.assertGreater(count_test_cases(PROJECT_ROOT), 0)
        counts = derive_counts(PROJECT_ROOT, self.checkpoint)
        self.assertEqual(counts["TESTS"]["denominator"], count_test_cases(PROJECT_ROOT))


class CommandInputBindingTests(unittest.TestCase):
    """M0-F-009: a record that names an input binds it by content."""

    def _record(self, **overrides: object) -> dict:
        record = {
            "id": "cmd-0001", "timestamp": NOW, "runtime": "python 3.13.0",
            "command": "python scripts/development-ledger/validate_checkpoint.py",
            "arguments": ["scripts/development-ledger/validate_checkpoint.py"],
            "inputs": ["scripts/development-ledger/validate_checkpoint.py"],
            "inputsDigest": [{
                "path": "scripts/development-ledger/validate_checkpoint.py",
                "hash": canonical_hash_path(SCRIPTS / "validate_checkpoint.py")}],
            "workingDirectory": str(PROJECT_ROOT), "commit": "a" * 40,
            "purpose": "fixture", "result": "COMPLETED", "resultCode": "OK",
            "exitCode": 0, "durationMs": 1, "stdoutArtifact": None, "stderrArtifact": None,
        }
        record.update(overrides)
        return record

    def _errors(self, record: dict) -> list[str]:
        errors: list[str] = []
        _validate_command_reproducibility(PROJECT_ROOT, record, 1, errors, bind_inputs=True)
        return errors

    def test_a_bound_record_passes(self) -> None:
        self.assertEqual(self._errors(self._record()), [])

    def test_a_record_without_a_digest_is_rejected(self) -> None:
        record = self._record()
        record.pop("inputsDigest")
        self.assertTrue(any("inputsDigest" in error for error in self._errors(record)))

    def test_a_digest_that_omits_an_input_is_rejected(self) -> None:
        record = self._record(inputsDigest=[])
        self.assertTrue(any("does not bind" in error for error in self._errors(record)))

    def test_a_digest_for_an_undeclared_input_is_rejected(self) -> None:
        record = self._record()
        record["inputsDigest"].append({"path": "START-HERE.md", "hash": "0" * 64})
        self.assertTrue(any("not a declared input" in error for error in self._errors(record)))

    def test_a_malformed_digest_is_rejected(self) -> None:
        record = self._record()
        record["inputsDigest"][0]["hash"] = "not-a-digest"
        self.assertTrue(any("sha-256" in error for error in self._errors(record)))

    def test_a_clean_tree_claim_is_checked_against_the_declared_commit(self) -> None:
        code = run(["git", "rev-parse", "HEAD"], PROJECT_ROOT)
        if code.returncode != 0:
            self.skipTest("no commit is available")
        record = self._record(
            commit=code.stdout.strip(),
            repositoryState={"branch": "main", "head": code.stdout.strip(), "dirty": False,
                             "detached": False},
            inputsDigest=[{"path": "scripts/development-ledger/validate_checkpoint.py",
                           "hash": "0" * 64}])
        errors = self._errors(record)
        self.assertTrue(any("different content there" in error for error in errors), errors)

    def test_a_dirty_tree_record_is_accepted_when_the_digest_binds_the_input(self) -> None:
        record = self._record(
            repositoryState={"branch": "main", "head": "a" * 40, "dirty": True,
                             "detached": False})
        self.assertEqual(self._errors(record), [])

    def test_the_recorder_binds_inputs_automatically(self) -> None:
        from ledger_common import build_command_record

        record = build_command_record(
            PROJECT_ROOT, command="python START-HERE.md", purpose="fixture",
            inputs=["START-HERE.md"], exit_code=0)
        self.assertEqual(record["inputsDigest"][0]["path"], "START-HERE.md")
        self.assertEqual(record["inputsDigest"][0]["hash"],
                         canonical_hash_path(PROJECT_ROOT / "START-HERE.md"))


class SealChronologyTests(ClosureFixture):
    """M0-F-010: sealing is monotonic, post-commit, and its evidence describes the sealed commit."""

    def _commands(self, **overrides: object) -> list[dict]:
        record = {
            "id": "cmd-0100", "timestamp": NOW, "operation": "post-commit-validation",
            "exitCode": 0, "commit": "a" * 40,
            "repositoryState": {"branch": "main", "head": "a" * 40, "dirty": False,
                                "detached": False},
        }
        record.update(overrides)
        return [record]

    def _errors(self, commands: list[dict], metadata: dict | None = None) -> list[str]:
        errors: list[str] = []
        _validate_seal_chronology(
            PROJECT_ROOT, self.checkpoint, self.state(),
            metadata or {"finishedAt": "2026-12-31T23:59:59Z"}, commands, errors)
        return errors

    def test_a_missing_post_commit_validation_is_rejected(self) -> None:
        errors = self._errors([])
        self.assertTrue(any("post-commit-validation" in error for error in errors), errors)

    def test_a_failed_post_commit_validation_is_not_evidence(self) -> None:
        errors = self._errors(self._commands(exitCode=1))
        self.assertTrue(any("post-commit-validation" in error for error in errors), errors)

    def test_a_dirty_tree_validation_is_not_evidence_of_a_sealed_commit(self) -> None:
        errors = self._errors(self._commands(
            repositoryState={"branch": "main", "head": "a" * 40, "dirty": True,
                             "detached": False}))
        self.assertTrue(any("clean worktree" in error for error in errors), errors)

    def test_a_validation_of_an_unrelated_commit_is_rejected(self) -> None:
        errors = self._errors(self._commands())
        self.assertTrue(any("neither HEAD nor its parent" in error for error in errors), errors)

    def test_a_record_after_the_end_of_the_run_is_rejected(self) -> None:
        errors = self._errors(
            self._commands(timestamp="2026-12-31T23:59:59Z"),
            {"finishedAt": "2026-01-01T00:00:00Z"})
        self.assertTrue(any("monotonic" in error for error in errors), errors)

    def test_the_validation_of_head_itself_is_accepted(self) -> None:
        head = run(["git", "rev-parse", "HEAD"], PROJECT_ROOT)
        if head.returncode != 0:
            self.skipTest("no commit is available")
        errors = self._errors(self._commands(
            commit=head.stdout.strip(),
            repositoryState={"branch": "main", "head": head.stdout.strip(), "dirty": False,
                             "detached": False}))
        self.assertEqual(errors, [])

    def test_the_sealing_tool_does_not_expose_a_pending_seal_bypass(self) -> None:
        text = (SCRIPTS / "validate_checkpoint.py").read_text(encoding="utf-8")
        self.assertNotIn("--allow-pending-seal", text)
        self.assertNotIn("--allow-dirty", text)


class InternalAssuranceTests(ClosureFixture):
    """The internal Red Team and mirror audit are required, verified and never called external."""

    def _errors(self, state: dict | None = None) -> list[str]:
        errors: list[str] = []
        _validate_internal_assurance(
            PROJECT_ROOT, self.checkpoint, state or self.state(), errors)
        return errors

    def test_the_consistent_fixture_passes(self) -> None:
        self.assertEqual(self._errors(), [])

    def test_an_escaped_attack_cannot_produce_a_pass(self) -> None:
        self.edit(f"{self.MILESTONE}-INTERNAL-RED-TEAM.json",
                  lambda d: d["attacks"][0].update({"result": "ESCAPED"}))
        errors = self._errors()
        self.assertTrue(any("escaped" in error for error in errors), errors)

    def test_a_missing_mandatory_attack_is_rejected(self) -> None:
        def mutate(document: dict) -> None:
            document["attacks"] = [item for item in document["attacks"]
                                   if item["attackId"] != "C"]
            document["total"] = len(document["attacks"])
            document["defended"] = len(document["attacks"])
            document["mandatoryTotal"] = sum(1 for item in document["attacks"] if item["mandatory"])
            document["mandatoryDefended"] = document["mandatoryTotal"]

        self.edit(f"{self.MILESTONE}-INTERNAL-RED-TEAM.json", mutate)
        errors = self._errors()
        self.assertTrue(any("mandatory attack C" in error for error in errors), errors)

    def test_a_report_without_a_null_mutation_control_is_rejected(self) -> None:
        """An adversarial battery is believed only once its unmutated control is accepted."""
        self.edit(f"{self.MILESTONE}-INTERNAL-RED-TEAM.json",
                  lambda d: d.pop("baselineControl", None))
        errors = self._errors()
        self.assertTrue(any("null-mutation control" in error for error in errors), errors)

    def test_a_failed_null_mutation_control_cannot_produce_a_pass(self) -> None:
        self.edit(f"{self.MILESTONE}-INTERNAL-RED-TEAM.json",
                  lambda d: d.update({"baselineControl": {
                      "result": "INVALID", "detail": "the fixture did not validate"}}))
        errors = self._errors()
        self.assertTrue(any("null-mutation control" in error for error in errors), errors)

    def test_a_stale_red_team_result_is_rejected(self) -> None:
        self.edit(f"{self.MILESTONE}-INTERNAL-RED-TEAM.json",
                  lambda d: d.update({"targetFingerprint": "0" * 64}))
        errors = self._errors()
        self.assertTrue(any("STALE" in error for error in errors), errors)

    def test_a_failed_mirror_check_cannot_produce_a_pass(self) -> None:
        self.edit(f"{self.MILESTONE}-INTERNAL-MIRROR.json",
                  lambda d: d["checks"][0].update({"result": "FAIL"}))
        errors = self._errors()
        self.assertTrue(any("failed" in error.lower() for error in errors), errors)

    def test_a_stale_mirror_audit_is_rejected(self) -> None:
        self.edit(f"{self.MILESTONE}-INTERNAL-MIRROR.json",
                  lambda d: d.update({"targetFingerprint": "0" * 64}))
        errors = self._errors()
        self.assertTrue(any("STALE" in error for error in errors), errors)

    def test_the_mirror_must_declare_that_it_is_internal(self) -> None:
        self.edit(f"{self.MILESTONE}-INTERNAL-MIRROR.json",
                  lambda d: d.update({"independence": "fully independent external validation"}))
        errors = self._errors()
        self.assertTrue(any("independence must state" in error for error in errors), errors)

    def test_a_missing_internal_red_team_is_rejected(self) -> None:
        (self.checkpoint / f"{self.MILESTONE}-INTERNAL-RED-TEAM.json").unlink()
        errors = self._errors()
        self.assertTrue(any("INTERNAL-RED-TEAM" in error for error in errors), errors)

    def test_a_missing_mirror_audit_is_rejected(self) -> None:
        (self.checkpoint / f"{self.MILESTONE}-INTERNAL-MIRROR.json").unlink()
        errors = self._errors()
        self.assertTrue(any("INTERNAL-MIRROR" in error for error in errors), errors)


class FindingsClosureTests(ClosureFixture):
    """Every finding of an open audit is closed before the delivery is offered."""

    def _errors(self) -> list[str]:
        errors: list[str] = []
        _validate_findings_closure(PROJECT_ROOT, self.checkpoint, self.state(), errors)
        return errors

    def test_the_consistent_fixture_passes(self) -> None:
        self.assertEqual(self._errors(), [])

    def test_an_open_finding_blocks_the_delivery(self) -> None:
        def mutate(document: dict) -> None:
            document["findings"][0]["status"] = "OPEN"
            document["closed"] -= 1
            document["result"] = "OPEN"

        self.edit("CP7-FINDINGS-CLOSURE.json", mutate)
        errors = self._errors()
        self.assertTrue(any("remain open" in error for error in errors), errors)

    def test_a_missing_finding_is_detected(self) -> None:
        def mutate(document: dict) -> None:
            document["findings"] = document["findings"][1:]
            document["total"] = len(document["findings"])
            document["closed"] = len(document["findings"])

        self.edit("CP7-FINDINGS-CLOSURE.json", mutate)
        errors = self._errors()
        self.assertTrue(any("not accounted for" in error for error in errors), errors)

    def test_an_invented_finding_is_detected(self) -> None:
        def mutate(document: dict) -> None:
            row = json.loads(json.dumps(document["findings"][0]))
            row["findingId"] = "M0-F-999"
            document["findings"].append(row)
            document["total"] = len(document["findings"])
            document["closed"] = len(document["findings"])

        self.edit("CP7-FINDINGS-CLOSURE.json", mutate)
        errors = self._errors()
        self.assertTrue(any("M0-F-999" in error for error in errors), errors)

    def test_the_stored_totals_are_cross_checked(self) -> None:
        self.edit("CP7-FINDINGS-CLOSURE.json", lambda d: d.update({"closed": 99}))
        errors = self._errors()
        self.assertTrue(any("closed does not match" in error for error in errors), errors)

    def test_a_missing_closure_artifact_is_rejected(self) -> None:
        (self.checkpoint / "CP7-FINDINGS-CLOSURE.json").unlink()
        errors = self._errors()
        self.assertTrue(any("requires CP7-FINDINGS-CLOSURE.json" in error for error in errors),
                        errors)


class GuardrailEffectivenessGateTests(ClosureFixture):
    """A delivery cannot be offered while a guardrail is ineffective or has failed."""

    def test_the_measured_effectiveness_is_recorded_truthfully(self) -> None:
        errors: list[str] = []
        _validate_guardrail_effectiveness(PROJECT_ROOT, self.state(), errors)
        self.assertEqual(errors, [])

    def test_a_forged_effectiveness_block_is_rejected(self) -> None:
        state = self.state()
        state["guardrailEffectiveness"] = {**state["guardrailEffectiveness"],
                                           "guardrailsEffective": 999}
        errors: list[str] = []
        _validate_guardrail_effectiveness(PROJECT_ROOT, state, errors)
        self.assertTrue(any("does not match the measured" in error for error in errors), errors)

    def test_a_missing_effectiveness_block_is_rejected(self) -> None:
        state = self.state()
        state.pop("guardrailEffectiveness")
        errors: list[str] = []
        _validate_guardrail_effectiveness(PROJECT_ROOT, state, errors)
        self.assertTrue(any("guardrailEffectiveness block" in error for error in errors), errors)


class AuditSourceParsingTests(unittest.TestCase):
    """The audit's findings and attacks are re-parsed from the sealed reports, never transcribed."""

    def test_every_finding_of_the_sealed_review_is_parsed(self) -> None:
        findings = parse_findings(
            (AUDIT_CHECKPOINT / "REVIEW-REPORT.md").read_text(encoding="utf-8"))
        self.assertEqual([item["id"] for item in findings],
                         ["M0-F-%03d" % number for number in range(1, 12)])

    def test_every_mandatory_attack_of_the_sealed_report_is_parsed(self) -> None:
        attacks = parse_attacks(
            (AUDIT_CHECKPOINT / "RED-TEAM-REPORT.md").read_text(encoding="utf-8"))
        mandatory = [item["id"] for item in attacks if item["mandatory"] == "true"]
        self.assertEqual(mandatory, [chr(code) for code in range(ord("A"), ord("Z") + 1)])
        self.assertEqual(len(mandatory), 26)

    def test_the_escaped_attacks_are_recorded_as_escaped(self) -> None:
        attacks = parse_attacks(
            (AUDIT_CHECKPOINT / "RED-TEAM-REPORT.md").read_text(encoding="utf-8"))
        escaped = {item["id"] for item in attacks if item["result"] == "ESCAPED"}
        self.assertTrue({"C", "I", "J", "Q", "R", "S", "U", "V"}.issubset(escaped))

    def test_the_registry_binds_the_audit_to_this_corrective_checkpoint(self) -> None:
        audits = open_audits(PROJECT_ROOT, "SETUP-00", CLOSURE_CHECKPOINT.name)
        self.assertEqual([audit["auditId"] for audit in audits], ["M0-CP-0007"])
        self.assertEqual(len(audit_findings(PROJECT_ROOT, audits[0])), 11)

    def test_the_red_team_battery_implements_every_mandatory_attack(self) -> None:
        """Every mandatory attack of every registered audit is implemented, not only one audit's.

        Deriving the expectation from the whole registry is what keeps the battery correct when a
        new audit is registered: the next corrective delivery inherits its predecessors' mandatory
        attacks instead of silently dropping them.
        """
        from m0_red_team import build_attacks
        from policies import load_audit_registry

        implemented = {item["attackId"] for item in build_attacks() if item["mandatory"]}
        expected: set[str] = set()
        for audit in load_audit_registry(PROJECT_ROOT):
            expected |= {item["id"] for item in audit_attacks(PROJECT_ROOT, audit)
                         if item["mandatory"] == "true"}
        self.assertTrue(expected, "the registry declares no mandatory attack")
        self.assertEqual(implemented, expected)

    def test_the_battery_also_covers_the_additional_and_new_surfaces(self) -> None:
        from m0_red_team import build_attacks

        identifiers = {item["attackId"] for item in build_attacks()}
        self.assertTrue({"AA", "AB", "AC", "AD", "AE", "AF"}.issubset(identifiers))
        self.assertTrue({"AI", "AL", "AR", "AT"}.issubset(identifiers))




# ==============================================================================================
# CP-0009 findings (schemaVersion 3.2.0, corrective delivery SETUP-00-CP-0010)
#
# Every class below exists because the fresh-session M0 audit of SETUP-00-CP-0008 found the gap it
# covers. CP9-F-001 and CP9-F-002 were both failures of a control that had only ever been tested
# from one side, so each class here executes the positive path as well as the refusals.
# ==============================================================================================

from promotion_fixture import (  # noqa: E402
    run_positive_promotion,
    run_successor_durability,
)
from derive_counts import executed_test_runs  # noqa: E402
from lessons import validate_memory_policy_document  # noqa: E402


def _sealed_pair(root: Path) -> tuple[str, str]:
    """The newest sealed checkpoint and the one before it, derived from history."""
    sealed = sealed_checkpoints_in_history_order(root)
    if len(sealed) < 2:
        raise unittest.SkipTest("the repository has fewer than two sealed checkpoints")
    return sealed[-2], sealed[-1]


class AuditAttestationModelTests(unittest.TestCase):
    """CP9-F-001: the verdict belongs to the audit checkpoint, and the subject stays immutable.

    The previous model consumed the attestation as if it belonged to the checkpoint being
    promoted, which required a tree containing its own commit identifier. Nothing could satisfy
    it, so every forgery was refused and no honest audit could pass. These cases are written
    against the repository's own sealed history, so the subject and its auditor are derived rather
    than named.
    """

    def setUp(self) -> None:
        self.subject, self.audit = _sealed_pair(PROJECT_ROOT)
        self.subject_commit = sealed_commit_of(PROJECT_ROOT, self.subject)

    def attestation(self, **overrides: object) -> dict:
        document = {
            "schemaVersion": "2.0.0",
            "auditId": "M0-TEST",
            "milestone": "M0",
            "validationMechanism": "FRESH_SESSION_INDEPENDENT_AUDIT",
            "crossToolValidation": "NOT_AVAILABLE",
            "auditorRole": "milestone independent auditor",
            "tool": "a tool",
            "provider": "a provider",
            "model": "a model",
            "freshSession": True,
            "subjectCheckpoint": self.subject,
            "subjectCommit": self.subject_commit,
            "auditCheckpoint": self.audit,
            "reviewResult": "APPROVED",
            "redTeamResult": "RED_TEAM_PASS",
            "completeness": 100.0,
            "evidenceCoverage": 100.0,
            "testResult": "PASS",
            "createdAt": NOW,
        }
        document.update(overrides)
        document["__path"] = "fixture-attestation.json"
        return document

    def verify(self, attestation: dict, **kwargs: object) -> list[str]:
        return verify_attestation(
            PROJECT_ROOT, attestation, attestation.get("subjectCheckpoint", self.subject),
            None, **kwargs)

    # -- the positive case, which is the finding ---------------------------------------
    def test_a_legitimate_attestation_over_the_sealed_history_is_accepted(self) -> None:
        self.assertEqual(self.verify(self.attestation()), [])

    def test_the_attestation_never_names_the_commit_of_the_tree_that_contains_it(self) -> None:
        schema = read_json(
            PROJECT_ROOT / ".iacode" / "schemas" / "external-audit-attestation.schema.json")
        self.assertNotIn("auditCommit", schema["properties"])
        self.assertIn("subjectCommit", schema["required"])

    def test_the_schema_of_the_circular_model_is_refused(self) -> None:
        errors = self.verify(self.attestation(schemaVersion="1.0.0"))
        self.assertTrue(any("schemaVersion" in error for error in errors), errors)

    # -- the subject -------------------------------------------------------------------
    def test_an_attestation_naming_the_subject_as_its_own_auditor_is_rejected(self) -> None:
        errors = self.verify(self.attestation(auditCheckpoint=self.subject))
        self.assertTrue(
            any("may not be authored by the delivery it judges" in error for error in errors),
            errors)

    def test_an_attestation_for_another_checkpoint_is_rejected(self) -> None:
        other = sealed_checkpoints_in_history_order(PROJECT_ROOT)[0]
        errors = verify_attestation(
            PROJECT_ROOT, self.attestation(subjectCheckpoint=other), self.subject, None)
        self.assertTrue(any("attests checkpoint" in error for error in errors), errors)

    def test_an_attestation_for_another_commit_is_rejected(self) -> None:
        errors = verify_attestation(
            PROJECT_ROOT, self.attestation(), self.subject, "b" * 40)
        self.assertTrue(any("attests commit" in error for error in errors), errors)

    def test_a_subject_commit_that_is_not_the_sealed_one_is_rejected(self) -> None:
        errors = self.verify(self.attestation(subjectCommit="c" * 40))
        self.assertTrue(
            any("resolves to" in error or "not the commit" in error for error in errors), errors)

    def test_an_unsealed_subject_is_rejected(self) -> None:
        unsealed = [item.name for item in sorted(
            (PROJECT_ROOT / "docs" / "checkpoints").iterdir())
            if item.is_dir() and item.name not in set(sealed_checkpoint_ids(PROJECT_ROOT))]
        if not unsealed:
            self.skipTest("every checkpoint directory in this checkout is sealed")
        errors = verify_attestation(
            PROJECT_ROOT, self.attestation(subjectCheckpoint=unsealed[-1]), unsealed[-1], None)
        self.assertTrue(any("is not sealed" in error for error in errors), errors)

    def test_attesting_an_older_checkpoint_than_the_audit_succeeds_is_rejected(self) -> None:
        """An audit judges the delivery it follows, not an older, easier checkpoint.

        Without this rule every other check would hold for an old checkpoint: it is sealed,
        anchored and an ancestor of everything after it, so a milestone could be claimed on a
        delivery the audit never examined.
        """
        sealed = sealed_checkpoints_in_history_order(PROJECT_ROOT)
        if len(sealed) < 3:
            self.skipTest("the repository has fewer than three sealed checkpoints")
        older = sealed[-3]
        errors = verify_attestation(
            PROJECT_ROOT,
            self.attestation(subjectCheckpoint=older,
                             subjectCommit=sealed_commit_of(PROJECT_ROOT, older)),
            older, None)
        self.assertTrue(
            any("is not the sealed checkpoint this audit succeeds" in error for error in errors),
            errors)

    # -- the auditor -------------------------------------------------------------------
    def test_an_attestation_naming_a_checkpoint_that_does_not_exist_is_rejected(self) -> None:
        errors = self.verify(self.attestation(auditCheckpoint="SETUP-00-CP-9999"))
        self.assertTrue(any("does not exist" in error for error in errors), errors)

    def test_a_checkpoint_may_not_claim_a_verdict_another_checkpoint_authored(self) -> None:
        errors = self.verify(self.attestation(), claiming_checkpoint="SETUP-00-CP-9999")
        self.assertTrue(
            any("may only carry the verdict of the audit it performed" in error
                for error in errors), errors)

    # -- the verdict -------------------------------------------------------------------
    def test_a_failed_review_cannot_produce_a_milestone_pass(self) -> None:
        errors = self.verify(self.attestation(reviewResult="REWORK_REQUIRED"))
        self.assertTrue(any("requires APPROVED" in error for error in errors), errors)

    def test_a_failed_red_team_cannot_produce_a_milestone_pass(self) -> None:
        errors = self.verify(self.attestation(redTeamResult="RED_TEAM_FAIL"))
        self.assertTrue(any("requires RED_TEAM_PASS" in error for error in errors), errors)

    def test_incomplete_audit_coverage_cannot_produce_a_milestone_pass(self) -> None:
        errors = self.verify(self.attestation(completeness=93.22))
        self.assertTrue(any("requires 100.0" in error for error in errors), errors)

    def test_a_failed_test_result_cannot_produce_a_milestone_pass(self) -> None:
        errors = self.verify(self.attestation(testResult="FAIL"))
        self.assertTrue(any("requires PASS" in error for error in errors), errors)

    def test_a_missing_field_is_refused_before_anything_else(self) -> None:
        attestation = self.attestation()
        attestation.pop("auditorRole")
        errors = self.verify(attestation)
        self.assertEqual(len(errors), 1, errors)
        self.assertIn("requires auditorRole", errors[0])

    # -- the mechanism -----------------------------------------------------------------
    def test_an_unknown_validation_mechanism_is_rejected(self) -> None:
        errors = self.verify(self.attestation(validationMechanism="TRUST_ME"))
        self.assertTrue(any("recognised mechanisms" in error for error in errors), errors)

    def test_a_cross_tool_claim_without_cross_tool_availability_is_rejected(self) -> None:
        errors = self.verify(self.attestation(
            validationMechanism="CROSS_TOOL_INDEPENDENT_AUDIT",
            crossToolValidation="NOT_AVAILABLE"))
        self.assertTrue(any("contradicts the mechanism" in error for error in errors), errors)

    def test_a_fresh_session_claim_requires_a_fresh_session(self) -> None:
        errors = self.verify(self.attestation(freshSession=False))
        self.assertTrue(any("freshSession" in error for error in errors), errors)

    def test_a_fresh_session_audit_may_not_produce_the_external_status(self) -> None:
        self.assertEqual(
            statuses_for_mechanism("FRESH_SESSION_INDEPENDENT_AUDIT"),
            ("MILESTONE_INDEPENDENT_AUDIT_PASS",))
        self.assertIn("MILESTONE_EXTERNAL_PASS",
                      statuses_for_mechanism("CROSS_TOOL_INDEPENDENT_AUDIT"))

    def test_the_status_vocabulary_separates_the_two_verdicts(self) -> None:
        from ledger_common import (
            EXTERNAL_PASS_STATUS,
            INDEPENDENT_AUDIT_PASS_STATUS,
            INTERNAL_PASS_STATUS,
            STATUSES,
            UNBLOCKED_STATUSES,
        )

        self.assertIn(INDEPENDENT_AUDIT_PASS_STATUS, STATUSES)
        self.assertIn(INDEPENDENT_AUDIT_PASS_STATUS, UNBLOCKED_STATUSES)
        self.assertIn(INDEPENDENT_AUDIT_PASS_STATUS, POSITIVE_TERMINAL_STATUSES)
        self.assertNotIn(INDEPENDENT_AUDIT_PASS_STATUS,
                         (INTERNAL_PASS_STATUS, EXTERNAL_PASS_STATUS))

    # -- the derivation ----------------------------------------------------------------
    def test_no_attestation_means_no_milestone_pass(self) -> None:
        attestation, reasons = resolve_external_pass(
            PROJECT_ROOT, "M0", "SETUP-00-CP-9999", None)
        self.assertIsNone(attestation)
        self.assertTrue(any("may not be self-asserted" in reason for reason in reasons), reasons)

    def test_the_milestone_verdict_is_derived_and_not_read_from_a_status(self) -> None:
        verdict = derive_milestone_verdict(PROJECT_ROOT, "M0")
        self.assertIn(verdict["status"], ("PASSED", "NOT_PASSED"))
        if verdict["status"] == "NOT_PASSED":
            self.assertTrue(verdict["reasons"])


class AdversarialCategoryTests(ClosureFixture):
    """CP-0009's report could be read two ways; a category is derived, and the totals never overlap."""

    def _document(self) -> dict:
        from affected_red_team import build

        return build(PROJECT_ROOT, self.checkpoint)

    def test_every_category_is_derived_from_the_executed_battery(self) -> None:
        document = self._document()
        executed = read_json(
            self.checkpoint / f"{self.MILESTONE}-INTERNAL-RED-TEAM.json")["attacks"]
        self.assertEqual(document["totalAdversarialScenarios"], len(executed))
        categories = document["categories"]
        self.assertEqual(
            categories["originalRedTeam"]["count"] + categories["additionalControlAttacks"]["count"],
            len(executed))

    def test_the_mandatory_category_matches_the_registry(self) -> None:
        from policies import load_audit_registry

        expected: set[str] = set()
        for audit in load_audit_registry(PROJECT_ROOT):
            expected |= {item["id"] for item in audit_attacks(PROJECT_ROOT, audit)
                         if item["mandatory"] == "true"}
        document = self._document()
        self.assertEqual(set(document["categories"]["originalRedTeam"]["required"]), expected)
        self.assertEqual(document["categories"]["originalRedTeam"]["missing"], [])

    def test_a_battery_missing_a_mandatory_attack_does_not_report_defended(self) -> None:
        def prune(report: dict) -> None:
            report["attacks"] = [item for item in report["attacks"] if item["attackId"] != "A"]
            report["total"] = len(report["attacks"])
            report["defended"] = len(report["attacks"])
            report["mandatoryTotal"] = sum(1 for item in report["attacks"] if item["mandatory"])
            report["mandatoryDefended"] = report["mandatoryTotal"]

        self.edit(f"{self.MILESTONE}-INTERNAL-RED-TEAM.json", prune)
        document = self._document()
        self.assertIn("A", document["categories"]["originalRedTeam"]["missing"])
        self.assertEqual(document["result"], "FAIL")

    def test_the_null_mutation_control_is_carried_into_the_report(self) -> None:
        document = self._document()
        self.assertEqual((document["baselineControl"] or {}).get("result"), "VALID")


class PositivePromotionTests(unittest.TestCase):
    """CP9-F-001: a milestone PASS is reachable by an honest sequence of repository states.

    The whole promotion is executed once in a disposable repository: a subject checkpoint is
    delivered and sealed, a second checkpoint is authored as its audit, and the verdict is derived
    afterwards from the repository.
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        try:
            cls.result = run_positive_promotion(Path(cls.temporary.name))
        except Exception as exc:  # noqa: BLE001 - the simulation failing is the finding
            cls.temporary.cleanup()
            raise AssertionError(f"the positive promotion could not be executed: {exc}") from exc

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_the_audit_checkpoint_validates_as_sealed(self) -> None:
        self.assertIn("CHECKPOINT_VALID", self.result["audit"]["validatorOutput"])

    def test_the_audit_checkpoint_carries_the_milestone_verdict(self) -> None:
        self.assertEqual(self.result["audit"]["status"], "MILESTONE_INDEPENDENT_AUDIT_PASS")

    def test_the_milestone_verdict_is_derived_as_passed(self) -> None:
        verdict = self.result["milestoneVerdict"]
        self.assertEqual(verdict["status"], "PASSED", verdict["reasons"])
        self.assertEqual(len(verdict["accepted"]), 1, verdict)

    def test_the_subject_is_not_rewritten_by_its_own_audit(self) -> None:
        self.assertTrue(self.result["subjectImmutable"])
        self.assertEqual(self.result["subjectStatusAfter"], "READY_FOR_REVIEW")

    def test_the_attestation_lives_in_the_audit_checkpoints_change_set(self) -> None:
        self.assertTrue(str(self.result["attestation"]).startswith(".iacode/attestations/"))

    def test_the_integrity_chain_still_verifies_after_the_audit(self) -> None:
        self.assertEqual(self.result["chainErrors"], [])

    def test_a_fresh_session_audit_cannot_reach_the_external_status(self) -> None:
        """The honest status is available; the one that would overclaim is refused."""
        with tempfile.TemporaryDirectory() as workdir:
            with self.assertRaises(Exception) as refused:
                run_positive_promotion(Path(workdir), status="MILESTONE_EXTERNAL_PASS")
        self.assertIn("MILESTONE_EXTERNAL_PASS", str(refused.exception))


class SuccessorDurabilityTests(unittest.TestCase):
    """CP9-F-002: advancing the sealed chain never requires editing a guardrail.

    Three checkpoints are sealed in succession in a disposable repository, each anchoring its
    predecessor, and the chain controls are re-run at every state with a derived exclusion.
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        try:
            cls.result = run_successor_durability(Path(cls.temporary.name), successors=2)
        except Exception as exc:  # noqa: BLE001 - the simulation failing is the finding
            cls.temporary.cleanup()
            raise AssertionError(f"the succession could not be executed: {exc}") from exc

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_three_checkpoints_were_sealed_in_succession(self) -> None:
        self.assertEqual(len(self.result["checkpoints"]), 3)

    def test_every_state_of_the_chain_verifies(self) -> None:
        for state in self.result["states"]:
            self.assertEqual(state["chainErrors"], [], state["state"])
            self.assertEqual(state["integrityExit"], 0, state["state"])

    def test_the_pending_exclusion_moves_with_the_chain(self) -> None:
        pending = [state["pendingAnchor"] for state in self.result["states"]]
        self.assertEqual(pending, [item["checkpoint"] for item in self.result["checkpoints"]])
        self.assertEqual(len(set(pending)), len(pending))

    def test_each_successor_anchors_its_predecessor(self) -> None:
        names = [item["checkpoint"] for item in self.result["checkpoints"]]
        self.assertEqual(self.result["states"][-1]["anchored"], names[:-1])

    def test_a_missing_anchor_is_still_detected_after_the_chain_advances(self) -> None:
        self.assertTrue(self.result["detected"], self.result["detectionErrors"])
        self.assertEqual(self.result["restoredChainErrors"], [])


class DerivedTestCountTests(ClosureFixture):
    """CP-0009's own defect: one physical run recorded twice is one measurement, not two."""

    def test_one_run_recorded_in_two_categories_counts_once(self) -> None:
        entry = {"executed": True, "passed": 306, "failed": 0,
                 "command": "python -m unittest discover -s tests", "evidence": "one run"}
        runs = executed_test_runs({"unit": dict(entry), "integration": dict(entry),
                                   "e2e": {"executed": False, "passed": 0, "failed": 0,
                                           "command": None, "evidence": None}})
        self.assertEqual(sum(runs.values()), 306)

    def test_an_explicit_run_identifier_deduplicates_across_categories(self) -> None:
        runs = executed_test_runs({
            "unit": {"executed": True, "passed": 306, "failed": 0, "command": "a",
                     "runId": "suite", "evidence": None},
            "integration": {"executed": True, "passed": 300, "failed": 0, "command": "b",
                            "runId": "suite", "evidence": None},
        })
        self.assertEqual(sum(runs.values()), 306)

    def test_two_real_executions_are_both_counted(self) -> None:
        runs = executed_test_runs({
            "unit": {"executed": True, "passed": 10, "failed": 0, "command": "unit",
                     "runId": "unit-run", "evidence": None},
            "e2e": {"executed": True, "passed": 4, "failed": 0, "command": "e2e",
                    "runId": "e2e-run", "evidence": None},
        })
        self.assertEqual(sum(runs.values()), 14)

    def test_a_count_larger_than_what_exists_is_refused(self) -> None:
        def forge(document: dict) -> None:
            for name in ("unit", "integration"):
                document[name] = {"executed": True, "passed": 10 ** 6, "failed": 0,
                                  "command": f"{name} run", "runId": name, "evidence": "forged"}

        self.edit("TESTS.json", forge)
        errors: list[str] = []
        _validate_derived_counts(PROJECT_ROOT, self.checkpoint, self.state(), errors)
        self.assertTrue(any("counts more than exists" in error for error in errors), errors)


class SourceCardinalityPolicyTests(unittest.TestCase):
    """CP9-F-003: a cardinality written in prose is not evidence, and no source may state one.

    The decision recorded in docs/QUALITY-GATES.md is that every count used as evidence lives in
    COUNTS.json, derived once and recomputed during validation. Comments and docstrings describe
    semantics; a number written there has no derivation behind it and drifts, which is exactly what
    happened when a docstring kept claiming a requirement-set size the derivation had outgrown.

    Only comments and docstrings are inspected. A count inside an ordinary string literal is data:
    the Red Team forges one on purpose, and forbidding that would forbid the attack that proves the
    control works.
    """

    CARDINALITY = re.compile(
        r"(?:derived|expected|canonical|anchored)\s+(?:reference\s+)?set\s+"
        r"(?:is|has|contains)\s+(\d+)", re.IGNORECASE)

    def _sources(self) -> list[Path]:
        paths: list[Path] = []
        for directory in ("scripts", "tests"):
            for path in sorted((PROJECT_ROOT / directory).rglob("*.py")):
                if "__pycache__" not in path.parts:
                    paths.append(path)
        return paths

    def _prose(self, path: Path) -> list[str]:
        """Every comment and docstring of a module, which is where prose claims live."""
        import ast
        import io
        import tokenize

        text = path.read_text(encoding="utf-8")
        prose: list[str] = []
        try:
            for token in tokenize.generate_tokens(io.StringIO(text).readline):
                if token.type == tokenize.COMMENT:
                    prose.append(token.string)
        except (tokenize.TokenError, IndentationError):
            pass
        try:
            tree = ast.parse(text)
        except SyntaxError:
            return prose
        for node in ast.walk(tree):
            if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                document = ast.get_docstring(node, clean=False)
                if document:
                    prose.append(document)
        return prose

    def test_no_comment_or_docstring_states_the_cardinality_of_a_derived_set(self) -> None:
        offenders = []
        for path in self._sources():
            for prose in self._prose(path):
                for match in self.CARDINALITY.finditer(prose):
                    offenders.append(f"{path.relative_to(PROJECT_ROOT)}: {match.group(0)}")
        self.assertEqual(offenders, [])

    def test_no_comment_or_docstring_states_a_derived_count_claim(self) -> None:
        offenders = []
        for path in self._sources():
            for prose in self._prose(path):
                for numerator, denominator, label in COUNT_CLAIM.findall(prose):
                    offenders.append(
                        f"{path.relative_to(PROJECT_ROOT)}: {numerator}/{denominator} {label}")
        self.assertEqual(offenders, [])

    def test_the_control_detects_a_cardinality_written_in_a_docstring(self) -> None:
        """The check must fail on the shape the audit found, not merely pass on clean sources."""
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "sample.py"
            path.write_text(
                '"""A module whose docstring claims the derived set is 119 anchored references."""\n'
                "# and a comment stating 305/306 TESTS\n",
                encoding="utf-8")
            prose = self._prose(path)
        self.assertTrue(any(self.CARDINALITY.search(item) for item in prose), prose)
        self.assertTrue(any(COUNT_CLAIM.search(item) for item in prose), prose)

    def test_the_count_policy_is_documented(self) -> None:
        text = (PROJECT_ROOT / "docs" / "QUALITY-GATES.md").read_text(encoding="utf-8")
        self.assertIn("A count stated in a source comment or docstring is not evidence", text)


class MemoryPolicyDocumentTests(unittest.TestCase):
    """CP9-F-005 and CP9-F-004: the policy declares only what is read, and prose cannot lie."""

    def test_the_declared_policy_validates_against_its_schema(self) -> None:
        self.assertEqual(validate_memory_policy_document(PROJECT_ROOT), [])

    def test_a_setting_no_code_reads_cannot_be_declared(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / ".iacode" / "memory").mkdir(parents=True)
            (root / ".iacode" / "schemas").mkdir(parents=True)
            shutil.copy2(
                PROJECT_ROOT / ".iacode" / "schemas" / "memory-policy.schema.json",
                root / ".iacode" / "schemas" / "memory-policy.schema.json")
            write_json_file(root / ".iacode" / "memory" / "POLICY.json", {
                "schemaVersion": "2.0.0", "policy": "fixture",
                "guardrailRegistry": "guardrails/registry.json"})
            errors = validate_memory_policy_document(root)
        self.assertTrue(any("guardrailRegistry" in error for error in errors), errors)

    def test_the_guardrail_registry_path_has_one_resolver(self) -> None:
        self.assertEqual(
            guardrail_registry_path(PROJECT_ROOT),
            PROJECT_ROOT / ".iacode" / "memory" / "guardrails" / "registry.json")
        self.assertTrue(guardrail_registry_path(PROJECT_ROOT).is_file())

    def test_a_guarded_lesson_may_not_describe_itself_as_unguarded(self) -> None:
        lessons = load_lessons(PROJECT_ROOT)
        lesson = dict(next(item for item in lessons if item["status"] == "GUARDED"))
        lesson["notes"] = "Not guarded: nothing can prove this from the artifact alone."
        errors = validate_memory(PROJECT_ROOT, [lesson])
        self.assertTrue(any("not guarded" in error for error in errors), errors)

    def test_the_repository_memory_has_no_status_contradiction(self) -> None:
        for lesson in load_lessons(PROJECT_ROOT):
            if lesson["status"] == "GUARDED":
                self.assertNotRegex(str(lesson.get("notes") or ""), r"(?i)\bnot\s+guarded\b",
                                    lesson["lessonId"])


class AuditRegistrySuccessionTests(unittest.TestCase):
    """A second registered audit inherits its own findings and its own mandatory battery."""

    def test_the_second_audit_is_registered_against_this_corrective_checkpoint(self) -> None:
        audits = {audit["auditId"]: audit for audit in load_audit_registry(PROJECT_ROOT)}
        self.assertIn("M0-CP-0009", audits)
        self.assertEqual(audits["M0-CP-0009"]["subjectCheckpoint"], "SETUP-00-CP-0008")
        self.assertEqual(audits["M0-CP-0009"]["auditCheckpoint"], "SETUP-00-CP-0009")

    def test_every_finding_of_the_second_audit_is_parsed(self) -> None:
        audits = {audit["auditId"]: audit for audit in load_audit_registry(PROJECT_ROOT)}
        findings = audit_findings(PROJECT_ROOT, audits["M0-CP-0009"])
        self.assertEqual([item["id"] for item in findings],
                         ["CP9-F-%03d" % number for number in range(1, 6)])

    def test_the_battery_of_an_additional_section_is_not_promoted_to_mandatory(self) -> None:
        """The battery a row belongs to is decided by its section, not by its table shape."""
        audits = {audit["auditId"]: audit for audit in load_audit_registry(PROJECT_ROOT)}
        for identifier in ("M0-CP-0007", "M0-CP-0009"):
            attacks = audit_attacks(PROJECT_ROOT, audits[identifier])
            mandatory = [item["id"] for item in attacks if item["mandatory"] == "true"]
            self.assertEqual(mandatory,
                             [chr(code) for code in range(ord("A"), ord("Z") + 1)], identifier)
            additional = [item["id"] for item in attacks if item["mandatory"] == "false"]
            self.assertTrue(additional, identifier)
            self.assertTrue(all(len(item) == 2 for item in additional), identifier)

    def test_a_rendered_verdict_is_parsed_whether_or_not_it_is_quoted(self) -> None:
        rows = parse_attacks(
            "## Mandatory battery\n"
            "| A | target | mutation | reject | rejected | DEFENDED | evidence |\n"
            "| B | target | mutation | reject | rejected | `DEFENDED` |\n"
            "## Additional battery\n"
            "| AA | mutation | reject | rejected | DEFENDED |\n")
        self.assertEqual([(item["id"], item["mandatory"]) for item in rows],
                         [("A", "true"), ("B", "true"), ("AA", "false")])


# ==============================================================================================
# CP-0011 findings (schemaVersion 3.2.0, corrective delivery SETUP-00-CP-0012)
#
# CP11-F-001 was one control that could not tell two states apart: an empty applicable set, where
# the canonical sources name nothing of this kind to judge, and a missing required set, where they
# name something the delivery does not carry. The first is legitimate and the second is a failure,
# and collapsing them made every delivery that corrects no audit unshippable. Each class below
# executes the states rather than asserting them, including the states that would turn the repair
# into a way of passing without auditing anything.
# ==============================================================================================

import inspect  # noqa: E402

import m0_mirror_audit  # noqa: E402
from ledger_common import LedgerError  # noqa: E402
from m0_mirror_audit import INDEPENDENCE as MIRROR_INDEPENDENCE  # noqa: E402
from m0_mirror_audit import Mirror, NotApplicable  # noqa: E402
from mirror_semantics_validation import SCENARIOS as MIRROR_SEMANTICS_SCENARIOS  # noqa: E402
from mirror_semantics_validation import run as run_mirror_semantics  # noqa: E402
from gate_transition_simulation import evaluate as evaluate_gate_transition  # noqa: E402
from policies import audit_applicability  # noqa: E402
from promotion_fixture import run_gate_transition  # noqa: E402


class SealedReportRenderingTests(unittest.TestCase):
    """Three sealed audits rendered their reports three ways, and all three must still parse.

    A parser that recognises one rendering reads the others as empty, and an empty parse of a report
    that has findings is exactly the confusion this delivery exists to remove: it looks like "this
    audit raised nothing" and it means "this report could not be read". The tooling refuses the
    second rather than believing the first, and these cases hold the earlier parses fixed so the
    expected requirement set of a sealed checkpoint never moves under it.
    """

    def _report(self, checkpoint: str, name: str) -> str:
        path = PROJECT_ROOT / "docs" / "checkpoints" / checkpoint / name
        if not path.is_file():
            self.skipTest(f"{checkpoint} is not present in this checkout")
        return path.read_text(encoding="utf-8")

    def test_the_first_audits_parse_is_unchanged(self) -> None:
        attacks = parse_attacks(self._report("SETUP-00-CP-0007", "RED-TEAM-REPORT.md"))
        self.assertEqual([item["id"] for item in attacks if item["mandatory"] == "true"],
                         [chr(code) for code in range(ord("A"), ord("Z") + 1)])
        self.assertEqual([item["id"] for item in attacks if item["mandatory"] == "false"],
                         ["AA", "AB", "AC", "AD", "AE", "AF"])
        self.assertEqual(
            [item["id"] for item in parse_findings(
                self._report("SETUP-00-CP-0007", "REVIEW-REPORT.md"))],
            ["M0-F-%03d" % number for number in range(1, 12)])

    def test_the_second_audits_parse_is_unchanged(self) -> None:
        attacks = parse_attacks(self._report("SETUP-00-CP-0009", "RED-TEAM-REPORT.md"))
        self.assertEqual([item["id"] for item in attacks if item["mandatory"] == "true"],
                         [chr(code) for code in range(ord("A"), ord("Z") + 1)])
        self.assertEqual([item["id"] for item in attacks if item["mandatory"] == "false"],
                         ["A" + chr(code) for code in range(ord("A"), ord("Z") + 1)])
        self.assertEqual(
            [item["id"] for item in parse_findings(
                self._report("SETUP-00-CP-0009", "REVIEW-REPORT.md"))],
            ["CP9-F-00%d" % number for number in range(1, 6)])

    def test_the_third_audits_battery_is_read_from_its_category_column(self) -> None:
        attacks = parse_attacks(self._report("SETUP-00-CP-0011", "RED-TEAM-REPORT.md"))
        self.assertTrue(attacks, "the third sealed report parsed as containing no attack")
        mandatory = [item["id"] for item in attacks if item["mandatory"] == "true"]
        self.assertEqual(mandatory, ["INT-01", "INT-02", "INT-03", "INT-04", "INT-05", "PRE-01",
                                     "MEM-01", "STL-01", "STL-02", "STL-04", "STL-05", "SEC-01"])
        self.assertTrue(all(item["id"].startswith("ATT-")
                            for item in attacks[:1]), attacks[:1])

    def test_a_table_that_is_not_a_table_of_attacks_is_not_read_as_one(self) -> None:
        """The positive control, the guardrail probes and the scenario logs are not attacks."""
        attacks = parse_attacks(self._report("SETUP-00-CP-0009", "RED-TEAM-REPORT.md"))
        identifiers = {item["id"] for item in attacks}
        for foreign in ("POS-EXT", "GK-001", "HIST-001", "EXT-000"):
            self.assertNotIn(foreign, identifiers)

    def test_a_findings_section_bounds_what_the_report_raises_as_its_own(self) -> None:
        """An audit verifying its predecessor's findings is not raising them again."""
        findings = [item["id"] for item in parse_findings(
            self._report("SETUP-00-CP-0011", "REVIEW-REPORT.md"))]
        self.assertEqual(findings, ["CP11-F-001"])
        for earlier in ("CP9-F-001", "CP9-F-005"):
            self.assertNotIn(earlier, findings)

    def test_a_report_whose_findings_cannot_be_parsed_is_refused_rather_than_read_as_empty(
            self) -> None:
        """A missing required set is never an empty applicable set, not even in the parser."""
        with tempfile.TemporaryDirectory() as workdir:
            root = Path(workdir)
            (root / "report.md").write_text(
                "# Review\n\n## Findings\n\nnone could be rendered\n",
                encoding="utf-8", newline="\n")
            with self.assertRaises(LedgerError) as refused:
                audit_findings(root, {"auditId": "X", "reviewReport": "report.md"})
        self.assertIn("no finding could be parsed", str(refused.exception))

    def test_the_registry_binds_the_third_audit_to_this_corrective_checkpoint(self) -> None:
        audits = open_audits(PROJECT_ROOT, "SETUP-00", "SETUP-00-CP-0012")
        self.assertEqual([audit["auditId"] for audit in audits], ["M0-CP-0011"])
        self.assertEqual([item["id"] for item in audit_findings(PROJECT_ROOT, audits[0])],
                         ["CP11-F-001"])


class ApplicableSetDerivationTests(unittest.TestCase):
    """The applicable set comes from the canonical sources and no delivery can shrink it."""

    def test_the_applicable_set_of_this_delivery_is_derived_from_the_registry(self) -> None:
        applicable = audit_applicability(PROJECT_ROOT, "SETUP-00", "SETUP-00-CP-0012")
        self.assertEqual(applicable["auditIds"], ["M0-CP-0011"])
        self.assertEqual([item["id"] for item in applicable["findings"]], ["CP11-F-001"])
        self.assertTrue(applicable["mandatoryAttacks"])
        self.assertIn("audit-registry.json", applicable["derivationSource"])

    def test_a_checkpoint_no_audit_names_has_an_empty_applicable_set(self) -> None:
        applicable = audit_applicability(PROJECT_ROOT, "SETUP-00", "SETUP-00-CP-9999")
        self.assertEqual(applicable["findings"], [])
        self.assertEqual(applicable["mandatoryAttacks"], [])
        self.assertEqual(applicable["auditIds"], [])

    def test_an_unreadable_audit_report_raises_instead_of_reducing_to_an_empty_set(self) -> None:
        with tempfile.TemporaryDirectory() as workdir:
            root = Path(workdir)
            policies = root / ".iacode" / "policies"
            policies.mkdir(parents=True)
            write_json_file(policies / "audit-registry.json", {
                "schemaVersion": "1.0.0", "policy": "fixture",
                "audits": [{
                    "auditId": "FIXTURE", "milestone": "M0", "gate": "SETUP-00",
                    "auditor": "fixture", "auditCheckpoint": "A", "subjectCheckpoint": "B",
                    "subjectCommit": "0" * 40, "verdict": "REWORK_REQUIRED",
                    "reviewReport": "missing-report.md", "correctiveCheckpoint": "C",
                    "findingsClosureFile": "CLOSURE.json"}]})
            with self.assertRaises(LedgerError):
                audit_applicability(root, "SETUP-00", "C")

    def test_the_mirror_derives_its_own_expected_set_and_takes_none_from_its_caller(self) -> None:
        """No entry point offers a way to hand the mirror the set it is supposed to derive.

        A control that trusts its own input is not a control, which is the CP-0006 lesson about a
        shrinkable denominator. The audit is invoked with a root and a checkpoint, and every
        applicable item is derived from the canonical sources inside.
        """
        signature = inspect.signature(m0_mirror_audit.run_audit)
        self.assertEqual(list(signature.parameters), ["root", "checkpoint", "clean_clone"])
        source = inspect.getsource(m0_mirror_audit.run_audit)
        self.assertIn("audit_applicability(root, gate, checkpoint.name)", source)


class NotApplicableRecordingTests(unittest.TestCase):
    """An inapplicable dimension justifies itself, or it is recorded as a failure of the auditor."""

    def _mirror(self) -> Mirror:
        checkpoint = PROJECT_ROOT / "docs" / "checkpoints" / "SETUP-00-CP-0011"
        if not (checkpoint / "STATE.json").is_file():
            self.skipTest("the audit checkpoint is not present in this checkout")
        return Mirror(PROJECT_ROOT, checkpoint)

    def test_an_inapplicable_outcome_cannot_be_constructed_without_a_reason(self) -> None:
        with self.assertRaises(LedgerError):
            NotApplicable(reason="  ", derivation_source="registry", observed="nothing")

    def test_an_inapplicable_outcome_cannot_be_constructed_without_a_derivation_source(
            self) -> None:
        with self.assertRaises(LedgerError):
            NotApplicable(reason="nothing applies", derivation_source="", observed="nothing")

    def test_an_inapplicable_check_records_its_reason_count_and_source(self) -> None:
        mirror = self._mirror()
        mirror.check("MIR-TEST", "fixture", "fixture", ["checkpoint:PLAN.md"],
                     lambda: NotApplicable(reason="nothing applies",
                                           derivation_source="the fixture registry",
                                           observed="0 applicable items"))
        recorded = mirror.checks[-1]
        self.assertEqual(recorded["result"], "NOT_APPLICABLE")
        self.assertEqual(recorded["expectedCount"], 0)
        self.assertEqual(recorded["reason"], "nothing applies")
        self.assertEqual(recorded["derivationSource"], "the fixture registry")

    def test_an_unjustified_inapplicable_record_becomes_a_failure(self) -> None:
        mirror = self._mirror()
        mirror.record("MIR-TEST", "fixture", "fixture", "0 applicable items", "NOT_APPLICABLE",
                      [], reason="", expected_count=0, derivation_source="")
        self.assertEqual(mirror.checks[-1]["result"], "FAIL")

    def test_an_inapplicable_record_with_items_becomes_a_failure(self) -> None:
        mirror = self._mirror()
        mirror.record("MIR-TEST", "fixture", "fixture", "3 applicable items", "NOT_APPLICABLE",
                      [], reason="nothing applies", expected_count=3,
                      derivation_source="the fixture registry")
        self.assertEqual(mirror.checks[-1]["result"], "FAIL")
        self.assertIn("3 applicable item", mirror.checks[-1]["observed"])


class MirrorApplicabilityValidationTests(ClosureFixture):
    """Checkpoint validation judges an inapplicable dimension instead of believing it."""

    def _mirror_document(self) -> dict[str, Any]:
        return read_json(self.checkpoint / f"{self.MILESTONE}-INTERNAL-MIRROR.json")

    def _write_mirror(self, document: dict[str, Any]) -> None:
        write_json_file(self.checkpoint / f"{self.MILESTONE}-INTERNAL-MIRROR.json", document)

    def _errors(self) -> list[str]:
        errors: list[str] = []
        _validate_internal_assurance(PROJECT_ROOT, self.checkpoint, self.state(), errors)
        return errors

    def state(self) -> dict[str, Any]:
        return read_json(self.checkpoint / "STATE.json")

    def test_the_unmutated_fixture_is_accepted(self) -> None:
        self.assertEqual([error for error in self._errors() if "MIRROR" in error], [])

    def test_a_justified_inapplicable_dimension_is_accepted(self) -> None:
        document = self._mirror_document()
        document["schemaVersion"] = "1.1.0"
        document["checks"].append({
            "id": "MIR-999", "dimension": "fixture", "expectation": "fixture",
            "observed": "0 applicable items", "result": "NOT_APPLICABLE",
            "evidence": ["checkpoint:PLAN.md"], "reason": "nothing of this kind applies",
            "expectedCount": 0, "derivationSource": ".iacode/policies/audit-registry.json"})
        document["total"] += 1
        document["notApplicable"] = 1
        self._write_mirror(document)
        self.assertEqual([error for error in self._errors() if "MIRROR" in error], [])

    def test_an_inapplicable_dimension_without_a_reason_is_refused(self) -> None:
        document = self._mirror_document()
        document["schemaVersion"] = "1.1.0"
        document["checks"].append({
            "id": "MIR-999", "dimension": "fixture", "expectation": "fixture",
            "observed": "0 applicable items", "result": "NOT_APPLICABLE",
            "evidence": ["checkpoint:PLAN.md"], "expectedCount": 0,
            "derivationSource": ".iacode/policies/audit-registry.json"})
        document["total"] += 1
        document["notApplicable"] = 1
        self._write_mirror(document)
        self.assertTrue(any("without a reason" in error for error in self._errors()))

    def test_an_inapplicable_dimension_with_items_is_refused(self) -> None:
        document = self._mirror_document()
        document["schemaVersion"] = "1.1.0"
        document["checks"].append({
            "id": "MIR-999", "dimension": "fixture", "expectation": "fixture",
            "observed": "3 applicable items", "result": "NOT_APPLICABLE",
            "evidence": ["checkpoint:PLAN.md"], "reason": "nothing of this kind applies",
            "expectedCount": 3, "derivationSource": ".iacode/policies/audit-registry.json"})
        document["total"] += 1
        document["notApplicable"] = 1
        self._write_mirror(document)
        self.assertTrue(any("is not inapplicable" in error for error in self._errors()))

    def test_an_inapplicable_dimension_under_the_older_report_version_is_refused(self) -> None:
        document = self._mirror_document()
        document["schemaVersion"] = "1.0.0"
        document["checks"].append({
            "id": "MIR-999", "dimension": "fixture", "expectation": "fixture",
            "observed": "0 applicable items", "result": "NOT_APPLICABLE",
            "evidence": ["checkpoint:PLAN.md"]})
        document["total"] += 1
        document["notApplicable"] = 1
        self._write_mirror(document)
        self.assertTrue(any("justification fields" in error for error in self._errors()))

    def test_a_registry_bound_dimension_cannot_be_declared_inapplicable(self) -> None:
        """The escape the repair opens: declaring away work the canonical sources still name."""
        applicable = audit_applicability(PROJECT_ROOT, "SETUP-00", self.checkpoint.name)
        if not applicable["findings"]:
            self.skipTest("this fixture checkpoint corrects no audit")
        document = self._mirror_document()
        document["schemaVersion"] = "1.1.0"
        document["checks"].append({
            "id": "MIR-002", "dimension": "Audit findings", "expectation": "fixture",
            "observed": "0 applicable audit findings", "result": "NOT_APPLICABLE",
            "evidence": ["checkpoint:PLAN.md"],
            "reason": "this delivery decided it has nothing to close", "expectedCount": 0,
            "derivationSource": "declared by this delivery"})
        document["total"] += 1
        document["notApplicable"] = 1
        self._write_mirror(document)
        self.assertTrue(any("while the canonical sources name" in error
                            for error in self._errors()))

    def test_an_inapplicable_dimension_counted_as_a_pass_is_refused(self) -> None:
        document = self._mirror_document()
        document["schemaVersion"] = "1.1.0"
        document["checks"].append({
            "id": "MIR-999", "dimension": "fixture", "expectation": "fixture",
            "observed": "0 applicable items", "result": "NOT_APPLICABLE",
            "evidence": ["checkpoint:PLAN.md"], "reason": "nothing of this kind applies",
            "expectedCount": 0, "derivationSource": ".iacode/policies/audit-registry.json"})
        document["total"] += 1
        document["passed"] += 1
        document["notApplicable"] = 1
        self._write_mirror(document)
        errors = self._errors()
        self.assertTrue(any("passed does not match" in error for error in errors)
                        or any("must add up to the total" in error for error in errors), errors)


class LocalRequirementDeclarationTests(ClosureFixture):
    """A delivery may declare a requirement of its own without escaping the derived set.

    The matrix defines a ``local:`` kind for a delivery-specific requirement, and the exact set
    comparison already refuses an omitted, substituted or duplicated anchor. A control that also
    demanded the total to equal the derived set would refuse a delivery for recording its own work
    -- the same shape as treating an empty applicable set as a failure.
    """

    LOCAL_ROW = {
        "id": "REQ-9001",
        "source": "FINAL-CORRECTION-REQUIREMENTS.json FCR-999",
        "sourceRef": "local:FCR-999",
        "description": "A requirement this delivery declared for itself.",
        "mandatory": True,
        "status": "COMPLETE",
        "implementationEvidence": ["checkpoint:PLAN.md"],
        "testEvidence": [],
        "documentationEvidence": [],
        "validationEvidence": [],
        "justification": None,
        "notes": "Declared locally and audited like every other row.",
    }

    def _report(self) -> dict[str, Any]:
        return evaluate_matrix(PROJECT_ROOT, self.checkpoint,
                               read_json(self.checkpoint / "REQUIREMENTS-MATRIX.json"))

    def test_the_anchored_count_excludes_a_locally_declared_requirement(self) -> None:
        before = self._report()
        self.edit("REQUIREMENTS-MATRIX.json",
                  lambda document: document["requirements"].append(dict(self.LOCAL_ROW)))
        after = self._report()
        self.assertEqual(after["anchoredRequirements"], before["anchoredRequirements"])
        self.assertEqual(after["totalRequirements"], before["totalRequirements"] + 1)
        self.assertEqual(after["anchoredRequirements"], after["expectedRequirements"])

    def test_a_locally_declared_requirement_does_not_fail_the_audit(self) -> None:
        self.edit("REQUIREMENTS-MATRIX.json",
                  lambda document: document["requirements"].append(dict(self.LOCAL_ROW)))
        report = self._report()
        self.assertEqual(report["result"], "PASS", report["findings"])

    def test_a_locally_declared_requirement_cannot_replace_an_anchored_one(self) -> None:
        def mutate(document: dict[str, Any]) -> None:
            anchored = [row for row in document["requirements"]
                        if str(row.get("sourceRef", "")).startswith("canonical:")]
            document["requirements"].remove(anchored[0])
            document["requirements"].append(dict(self.LOCAL_ROW))

        self.edit("REQUIREMENTS-MATRIX.json", mutate)
        report = self._report()
        self.assertEqual(report["result"], "FAIL")
        self.assertTrue(any("does not declare it" in finding["detail"]
                            for finding in report["findings"]), report["findings"])

    def test_a_local_requirement_without_evidence_is_still_refused(self) -> None:
        def mutate(document: dict[str, Any]) -> None:
            row = dict(self.LOCAL_ROW)
            row["implementationEvidence"] = []
            document["requirements"].append(row)

        self.edit("REQUIREMENTS-MATRIX.json", mutate)
        report = self._report()
        self.assertEqual(report["result"], "FAIL")
        self.assertTrue(any("requires at least one evidence reference" in finding["detail"]
                            for finding in report["findings"]), report["findings"])


class MirrorApplicabilitySemanticsTests(unittest.TestCase):
    """CP11-F-001, executed: every applicability state the mirror audit can be in.

    The tool itself runs in every state. Nothing here writes the report the tool would have
    produced, because writing it is how the defect survived a passing rehearsal.
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        try:
            cls.report = run_mirror_semantics(Path(cls.temporary.name))
        except Exception as exc:  # noqa: BLE001 - the validation failing is the finding
            cls.temporary.cleanup()
            raise AssertionError(
                f"the mirror semantics validation could not be executed: {exc}") from exc

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def _check(self, identifier: str) -> dict[str, Any]:
        return next(item for item in self.report["checks"] if item["id"] == identifier)

    def test_every_applicability_state_behaves_as_specified(self) -> None:
        failures = [item for item in self.report["checks"] if item["result"] != "PASS"]
        self.assertEqual(failures, [], self.report["result"])

    def test_an_empty_applicable_set_is_not_applicable_and_the_mirror_passes(self) -> None:
        check = self._check("MSV-001")
        self.assertEqual(check["findingsCheck"]["result"], "NOT_APPLICABLE")
        self.assertEqual(check["attacksCheck"]["result"], "NOT_APPLICABLE")
        self.assertEqual(check["findingsCheck"]["expectedCount"], 0)
        self.assertTrue(check["findingsCheck"]["reason"])
        self.assertTrue(check["findingsCheck"]["derivationSource"])
        self.assertIn("overall=PASS", check["observed"])
        self.assertIn("sealed=True", check["observed"])

    def test_a_satisfied_applicable_set_passes(self) -> None:
        check = self._check("MSV-002")
        self.assertEqual(check["findingsCheck"]["result"], "PASS")
        self.assertEqual(check["attacksCheck"]["result"], "PASS")

    def test_an_open_finding_fails(self) -> None:
        check = self._check("MSV-003")
        self.assertEqual(check["findingsCheck"]["result"], "FAIL")
        self.assertIn("overall=FAIL", check["observed"])
        self.assertIn("sealed=False", check["observed"])

    def test_a_missing_required_set_fails_rather_than_being_inapplicable(self) -> None:
        check = self._check("MSV-004")
        self.assertEqual(check["findingsCheck"]["result"], "FAIL")
        self.assertIn("missing", check["findingsCheck"]["observed"])

    def test_a_delivery_cannot_declare_its_own_applicable_set_empty(self) -> None:
        check = self._check("MSV-005")
        self.assertEqual(check["findingsCheck"]["result"], "FAIL")
        self.assertNotEqual(check["findingsCheck"]["result"], "NOT_APPLICABLE")

    def test_an_unexecuted_mandatory_attack_fails(self) -> None:
        check = self._check("MSV-006")
        self.assertEqual(check["attacksCheck"]["result"], "FAIL")

    def test_every_state_was_produced_by_executing_the_tool(self) -> None:
        for check in self.report["checks"]:
            self.assertTrue(check["mirrorCommand"].endswith(
                "m0_mirror_audit.py --write --checkpoint " + check["mirrorCommand"].split()[-1]),
                check["mirrorCommand"])
            self.assertIsNotNone(check["mirrorExitCode"])

    def test_the_declared_states_cover_both_sides_of_the_distinction(self) -> None:
        covered = self.report["statesCovered"]
        self.assertIn("emptyApplicableSet", covered)
        self.assertIn("missingRequiredSet", covered)
        self.assertEqual(len(MIRROR_SEMANTICS_SCENARIOS), self.report["total"])


class GateTransitionSimulationTests(unittest.TestCase):
    """CP11-F-001, second consequence: the first delivery of the next Gate can be handed over.

    A Gate's first delivery corrects no audit, so before the repair its mirror reported FAIL and
    checkpoint validation refused every positive terminal status. The whole transition is executed
    here in a disposable repository. No Gate 0 work exists in this repository and none is created:
    the next Gate's specification is synthetic and lives only in the fixture.
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        try:
            cls.result = run_gate_transition(Path(cls.temporary.name))
            cls.report = evaluate_gate_transition(cls.result)
        except Exception as exc:  # noqa: BLE001 - the transition failing is the finding
            cls.temporary.cleanup()
            raise AssertionError(
                f"the Gate transition could not be executed: {exc}") from exc

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_the_preceding_milestone_is_derived_as_passed(self) -> None:
        self.assertEqual(self.result["milestoneVerdictBeforeTransition"], "PASSED")

    def test_the_first_checkpoint_of_the_next_gate_reaches_review_readiness(self) -> None:
        self.assertEqual(self.result["statusReached"], "READY_FOR_REVIEW")
        self.assertIn("CHECKPOINT_VALID", self.result["validatorOutput"])

    def test_its_mirror_audit_passes_with_the_empty_dimensions_inapplicable(self) -> None:
        mirror = self.result["mirror"]
        self.assertEqual(mirror["result"], "PASS")
        self.assertEqual(mirror["failed"], 0)
        self.assertTrue(self.result["inapplicable"])
        for item in self.result["inapplicable"]:
            self.assertTrue(item["reason"])
            self.assertTrue(item["derivationSource"])
            self.assertEqual(item["expectedCount"], 0)

    def test_its_mirror_audit_was_executed_rather_than_written(self) -> None:
        self.assertEqual(self.result["mirror"]["producedBy"], "execution")
        self.assertEqual(self.result["mirror"]["exitCode"], 0)

    def test_the_integrity_chain_survives_the_transition(self) -> None:
        self.assertEqual(self.result["chainErrors"], [])

    def test_no_runtime_of_the_next_gate_was_implemented(self) -> None:
        self.assertTrue(self.result["noGateRuntime"])

    def test_every_recorded_check_of_the_simulation_passes(self) -> None:
        failures = [item for item in self.report["checks"] if item["result"] != "PASS"]
        self.assertEqual(failures, [], self.report["result"])


class SimulationExecutesProductionControlsTests(unittest.TestCase):
    """A simulation that says a control passed ran that control.

    ``promotion_simulation.py`` used to write the mirror report by hand, so the rehearsal reached a
    milestone status while the real path was blocked for every delivery. The artifact the simulation
    seals is now bound to the tool's own output by content, not by a claim.
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        try:
            cls.result = run_positive_promotion(Path(cls.temporary.name))
        except Exception as exc:  # noqa: BLE001
            cls.temporary.cleanup()
            raise AssertionError(f"the positive promotion could not be executed: {exc}") from exc

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def _sealed_mirrors(self) -> list[dict[str, Any]]:
        documents = []
        for item in (self.result["subject"], self.result["audit"]):
            path = Path(item["path"]) / f"{item['milestone']}-INTERNAL-MIRROR.json"
            documents.append(read_json(path))
        return documents

    def test_every_simulated_mirror_is_recorded_as_executed(self) -> None:
        for item in (self.result["subject"], self.result["audit"]):
            self.assertEqual(item["mirror"]["producedBy"], "execution")
            self.assertEqual(item["mirror"]["exitCode"], 0)
            self.assertIn("m0_mirror_audit.py", item["mirror"]["command"])

    def test_the_sealed_artifact_is_the_tools_own_output(self) -> None:
        """Bound by content: the auditor role, the independence text and the whole dimension set."""
        for document in self._sealed_mirrors():
            self.assertEqual(document["independence"], MIRROR_INDEPENDENCE)
            self.assertIn("m0-closure-auditor.md", document["auditorRole"])
            identifiers = [check["id"] for check in document["checks"]]
            self.assertIn("MIR-001", identifiers)
            self.assertIn("MIR-018", identifiers)
            self.assertEqual(len(identifiers), len(set(identifiers)))

    def test_the_simulated_mirror_reaches_a_pass_with_inapplicable_dimensions(self) -> None:
        for document in self._sealed_mirrors():
            self.assertEqual(document["result"], "PASS")
            inapplicable = [check for check in document["checks"]
                            if check["result"] == "NOT_APPLICABLE"]
            self.assertTrue(inapplicable, document["checkpoint"])
            self.assertEqual(document["notApplicable"], len(inapplicable))

    def test_the_simulation_declares_which_artifacts_it_modelled(self) -> None:
        """What is executed and what is modelled is stated, so neither is mistaken for the other."""
        from promotion_simulation import evaluate

        report = evaluate(self.result)
        provenance = report["artifactProvenance"]
        self.assertEqual(len(provenance), 2)
        for entry in provenance.values():
            self.assertEqual(entry["internalMirror"]["producedBy"], "execution")
            self.assertEqual(entry["internalRedTeam"]["producedBy"], "modelled")


class HistoricalClosureCompatibilityTests(HistoricalCheckpointCompatibilityTests):
    """The closure tooling still interprets every sealed checkpoint."""

    def test_sixth_sealed_checkpoint_still_validates(self) -> None:
        self._assert_historical_checkpoint_validates("iacode-checkpoints/SETUP-00-CP-0006")

    def test_seventh_sealed_checkpoint_still_validates(self) -> None:
        self._assert_historical_checkpoint_validates("iacode-checkpoints/SETUP-00-CP-0007")

if __name__ == "__main__":
    unittest.main()
