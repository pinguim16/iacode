"""Control-plane and repository-structure properties of GATE 3 — SANDBOX.

What this suite can check is what can be read from the repository, or exercised with the standard
library alone: the Gate's canonical specification and its registries, the ledger controls the Gate
repaired before it started, the boundary between the agent runtime and the sandbox, the sandbox
policy, the documents, and the scope of the Gate.

What it deliberately does not check is sandbox behaviour against a container engine. That suite
runs inside the sandbox service's image, which has the container client, and in the recorded
scenarios; duplicating a behavioural assertion here with a text search would be a second, weaker
control that disagrees with the first.

Every scan and every refusal here carries a **null control**: the identical path over an unmutated
fixture, which must be accepted, so a refusal is attributed to the mutation under test and not to
leftover state.
"""

from __future__ import annotations

import ast
import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = PROJECT_ROOT / "scripts" / "development-ledger"
sys.path.insert(0, str(SCRIPTS))

import ledger_common  # noqa: E402
import record_command  # noqa: E402
import validate_checkpoint  # noqa: E402


def _git(root: Path, *arguments: str) -> None:
    subprocess.run(["git", *arguments], cwd=root, check=True, capture_output=True)


# ---------------------------------------------------------------------------------------------
# 0. Pre-gate maintenance inherited from GATE 2
# ---------------------------------------------------------------------------------------------


class LedgerCommandReplayabilityTests(unittest.TestCase):
    """`R-G2-010` / `G2-F-011`: the recorder refuses, before running it, a command the validator
    would later refuse, and both ask one rule rather than two copies of it."""

    def setUp(self) -> None:
        self._directory = tempfile.TemporaryDirectory(prefix="iacode-replay-")
        self.root = Path(self._directory.name)
        (self.root / ".iacode").mkdir()
        self.checkpoint = self.root / "docs" / "checkpoints" / "FIXTURE-CP-0001"
        self.checkpoint.mkdir(parents=True)
        (self.root / "probe.py").write_text(
            "from pathlib import Path\nPath('executed.marker').write_text('ran')\n",
            encoding="utf-8")
        _git(self.root, "init", "-q")
        _git(self.root, "config", "user.name", "Fixture")
        _git(self.root, "config", "user.email", "fixture@example.invalid")
        _git(self.root, "add", ".")
        _git(self.root, "commit", "-q", "-m", "fixture")

    def tearDown(self) -> None:
        self._directory.cleanup()

    def record(self, *command: str) -> tuple[int, list[dict]]:
        argv = ["record_command.py", "--root", str(self.root), "--checkpoint",
                str(self.checkpoint), "--quiet", "--purpose", "fixture", "--", *command]
        with mock.patch.object(sys, "argv", argv), contextlib.redirect_stdout(io.StringIO()):
            exit_code = record_command.main()
        commands = self.checkpoint / "COMMANDS.jsonl"
        records = [json.loads(line) for line in commands.read_text(encoding="utf-8").splitlines()
                   if line.strip()] if commands.is_file() else []
        return exit_code, records

    def executed(self) -> bool:
        return (self.root / "executed.marker").is_file()

    def test_valid_command_executes_and_records(self) -> None:
        """The null control: the identical path accepts a replayable command and runs it."""
        exit_code, records = self.record("python", "probe.py")

        self.assertEqual(exit_code, 0)
        self.assertTrue(self.executed())
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["result"], "COMPLETED")
        self.assertEqual(records[0]["exitCode"], 0)
        errors: list[str] = []
        validate_checkpoint._validate_command_reproducibility(self.root, records[0], 1, errors)
        self.assertEqual(errors, [])

    def test_unsupported_runtime_is_rejected_before_execution(self) -> None:
        exit_code, records = self.record(sys.executable, "probe.py")

        self.assertNotEqual(exit_code, 0)
        self.assertFalse(self.executed(), "a refused command was executed anyway")
        self.assertEqual(len(records), 1)
        record = records[0]
        self.assertEqual(record["result"], "PRECONDITION_REJECTED")
        self.assertEqual(record["resultCode"], "E_UNREPLAYABLE_COMMAND")
        self.assertIsNone(record["exitCode"], "a refusal must not fabricate an exit code")
        self.assertIn("explicit runtime", record["failureReason"])

    def test_unresolved_python_script_is_rejected_before_execution(self) -> None:
        exit_code, records = self.record("python", "tools/absent_probe.py")

        self.assertNotEqual(exit_code, 0)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["result"], "PRECONDITION_REJECTED")
        self.assertEqual(records[0]["resultCode"], "E_UNREPLAYABLE_COMMAND")
        self.assertIsNone(records[0]["exitCode"])
        self.assertIn("does not resolve", records[0]["failureReason"])

    def test_rejected_command_is_never_executed(self) -> None:
        """A refusal is a refusal of the process: nothing of the command runs."""
        with mock.patch.object(record_command.subprocess, "run",
                               wraps=subprocess.run) as launched:
            exit_code, records = self.record(sys.executable, "probe.py")

        self.assertNotEqual(exit_code, 0)
        launched_commands = [call.args[0] for call in launched.call_args_list if call.args]
        self.assertFalse(any("probe.py" in list(command) for command in launched_commands),
                         f"the refused command was launched: {launched_commands}")
        self.assertTrue(launched_commands, "the wrapper observed nothing, so it proves nothing")
        self.assertEqual(records[0]["result"], "PRECONDITION_REJECTED")

    def test_the_refusal_record_is_valid_ledger_evidence(self) -> None:
        """The record of a refusal keeps the checkpoint valid, and cannot be evidence of a PASS."""
        _exit_code, records = self.record(sys.executable, "probe.py")
        errors: list[str] = []
        validate_checkpoint._validate_command_reproducibility(self.root, records[0], 1, errors)
        self.assertEqual(errors, [])
        self.assertNotIsInstance(records[0].get("exitCode"), int)

    def test_a_refusal_the_rule_does_not_support_is_refused(self) -> None:
        """A replayable command recorded as refused-for-being-unreplayable is a false record."""
        _exit_code, records = self.record("python", "probe.py")
        forged = dict(records[0], result="PRECONDITION_REJECTED",
                      resultCode="E_UNREPLAYABLE_COMMAND", exitCode=None,
                      failureReason="forged")
        errors: list[str] = []
        validate_checkpoint._validate_command_reproducibility(self.root, forged, 1, errors)
        self.assertTrue(any("does not refuse" in error for error in errors), errors)

    def test_recorder_and_validator_share_one_rule(self) -> None:
        self.assertIs(record_command.command_replay_errors, ledger_common.command_replay_errors)
        self.assertIs(validate_checkpoint.command_replay_errors,
                      ledger_common.command_replay_errors)
        for module in (record_command, validate_checkpoint):
            tree = ast.parse(Path(module.__file__).read_text(encoding="utf-8"))
            assigned = {target.id for node in ast.walk(tree) if isinstance(node, ast.Assign)
                        for target in node.targets if isinstance(target, ast.Name)}
            with self.subTest(module=module.__name__):
                self.assertNotIn("RUNTIME_TOKENS", assigned,
                                 "a second copy of the runtime token set")

    def test_the_guard_is_what_refuses(self) -> None:
        """Mutation control: without the shared rule the same command runs, so the refusal above
        is the rule's and not an accident of the fixture."""
        with mock.patch.object(record_command, "command_replay_errors", return_value=[]):
            exit_code, records = self.record(sys.executable, "probe.py")

        self.assertEqual(exit_code, 0)
        self.assertTrue(self.executed())
        self.assertEqual(records[0]["result"], "COMPLETED")


if __name__ == "__main__":
    unittest.main()
