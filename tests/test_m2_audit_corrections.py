"""Causal regressions for literal checkpoint emission and producer/cleanup evidence."""

from __future__ import annotations

import json
import os
import shlex
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))
sys.path.insert(0, str(ROOT / "scripts/iacode"))

import client_checks
from promotion_fixture import copy_ledger_runtime


class CheckpointInvocationProducerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.owner = tempfile.TemporaryDirectory(prefix="iacode-literal-producer-")
        self.addCleanup(self.owner.cleanup)
        self.root = Path(self.owner.name)
        copy_ledger_runtime(self.root)
        (self.root / ".iacode").mkdir(exist_ok=True)
        (self.root / "START-HERE.md").write_text("# Isolated fixture\n", encoding="utf-8")
        (self.root / "docs/checkpoints").mkdir(parents=True)
        self.run_child(["git", "init", "-b", "main"])
        self.run_child(["git", "-c", "user.name=Fixture", "-c",
                        "user.email=fixture@example.invalid", "commit", "--allow-empty", "-m", "fixture"])
        self.script = "scripts/development-ledger/new_checkpoint.py"

    def run_child(self, argv: list[str] | str, cwd: Path | None = None) -> subprocess.CompletedProcess:
        result = subprocess.run(argv, cwd=cwd or self.root, capture_output=True, text=True,
                                encoding="utf-8", errors="strict", timeout=30, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result

    def produce_and_replay(self, options: list[str], cwd: Path | None = None) -> None:
        working = cwd or self.root
        script = Path(os.path.relpath(self.root / self.script, working)).as_posix()
        supplied = [script, *options]
        self.run_child([sys.executable, *supplied], working)
        checkpoints = self.root / "docs/checkpoints"
        original = sorted(path for path in checkpoints.iterdir() if path.is_dir())[-1]
        state = json.loads((original / "STATE.json").read_text(encoding="utf-8"))
        record = json.loads((original / "COMMANDS.jsonl").read_text(encoding="utf-8"))
        self.assertEqual(record["arguments"], supplied)
        self.assertEqual(Path(record["workingDirectory"]), working)
        # Execute the recorded human replay command, not an independently reconstructed argv.
        command = record["command"]
        replay = command if os.name == "nt" else shlex.split(command)
        self.run_child(replay, Path(record["workingDirectory"]))
        successor = sorted(path for path in checkpoints.iterdir() if path.is_dir())[-1]
        replayed = json.loads((successor / "STATE.json").read_text(encoding="utf-8"))
        self.assertNotEqual(original, successor)
        for field in ("gate", "phase", "status"):
            self.assertEqual(replayed[field], state[field])

    def test_default_null_control_preserves_supplied_invocation(self) -> None:
        self.produce_and_replay(["--gate", "TEST", "--status", "IN_PROGRESS"])

    def test_custom_phase_and_quoted_unicode_replay_are_literal(self) -> None:
        self.produce_and_replay(["--phase", 'Auditoria ç "quoted" C:\\phase\\',
                                 "--gate=TEST", "--root=."])

    def test_omitted_default_status_is_not_invented(self) -> None:
        self.produce_and_replay(["--gate", "TEST"])

    def test_nested_working_directory_and_explicit_root_replay(self) -> None:
        nested = self.root / "operator directory"
        nested.mkdir()
        self.produce_and_replay(["--root", "..", "--gate", "TEST", "--phase=Nested phase"], nested)

    def test_registered_m2_attack_runs_actual_null_and_phase_human_replay(self) -> None:
        from m0_red_team import Fixture, build_attacks

        fixture = Fixture.__new__(Fixture)
        fixture.path = self.root
        attack = next(row for row in build_attacks() if row["attackId"] == "M2-RT-01")
        observed, defended = attack["run"](fixture)
        self.assertTrue(defended, observed)
        self.assertIn("[True, True]", observed)

    def test_registered_m2_attack_reproduces_old_phase_escape_with_valid_null(self) -> None:
        from m0_red_team import Fixture, build_attacks

        old = subprocess.run(["git", "show", "823cf164c6931dab7f957c92721ded7a916655bd:" + self.script],
                             cwd=ROOT, capture_output=True, timeout=30, check=True).stdout
        # Exact immutable pre-fix producer in this disposable fixture only.
        (self.root / self.script).write_bytes(old)
        fixture = Fixture.__new__(Fixture)
        fixture.path = self.root
        attack = next(row for row in build_attacks() if row["attackId"] == "M2-RT-01")
        observed, defended = attack["run"](fixture)
        self.assertFalse(defended, observed)
        self.assertIn("[True, False]", observed)


class ClientProducerCleanupEvidenceTests(unittest.TestCase):
    def execute(self, producer_exit: int = 0, cleanup_exit: int = 0,
                producer_mode: str = "exit", cleanup_mode: str = "exit",
                output: str = "producer-out ç") -> tuple[object, list[list[str]], Path]:
        actual_run = subprocess.run
        calls: list[list[str]] = []
        capsule_path: list[Path] = []

        def transport(argv: list[str], **kwargs: object) -> subprocess.CompletedProcess:
            calls.append(list(argv))
            cleanup = argv[1] == "rm"
            mode = cleanup_mode if cleanup else producer_mode
            if mode == "launch":
                raise FileNotFoundError("synthetic unavailable executable")
            marker = "cleanup-out" if cleanup else output
            error = "No such container: " + argv[-1] if mode == "absent" else (
                "cleanup-error" if cleanup else "producer-error")
            expression = repr(marker) if len(marker) < 10000 else repr(marker[0]) + "*" + str(len(marker))
            code = "import sys,time; print(" + expression + ",flush=True); " + (
                "print(" + repr(error) + ",file=sys.stderr,flush=True); "
            ) + ("time.sleep(10)" if mode == "timeout" else
                 "sys.exit(" + str(cleanup_exit if cleanup else producer_exit) + ")")
            options = dict(kwargs)
            options["env"] = {**os.environ, "PYTHONIOENCODING": "utf-8"}
            if mode == "timeout":
                options["timeout"] = 0.5
            result = actual_run([sys.executable, "-c", code], **options)
            result.args = argv
            return result

        def empty_capsule(directory: Path) -> None:
            capsule_path.append(directory)
            for project in ("cli", "vscode-extension"):
                (directory / project / "tests").mkdir(parents=True)

        with mock.patch.object(client_checks, "capsule", empty_capsule), \
                mock.patch.object(client_checks.subprocess, "run", side_effect=transport):
            try:
                outcome = client_checks.run_node(guard=True)
            except RuntimeError as exc:
                outcome = exc
        self.assertEqual(len(calls), 2)
        name = calls[0][calls[0].index("--name") + 1]
        self.assertEqual(calls[1], ["docker", "rm", "-f", name])
        self.assertRegex(name, r"^iacode-client-unit-[0-9a-f]{32}$")
        self.assertFalse(capsule_path[0].exists(), "actual temporary owner must be removed")
        return outcome, calls, capsule_path[0]

    def report(self, outcome: object) -> dict:
        self.assertIsInstance(outcome, RuntimeError)
        report = getattr(outcome, "report", None)
        self.assertIsInstance(report, dict, "cleanup must retain structured producer evidence")
        return report

    def test_clean_null_control_returns_actual_producer(self) -> None:
        outcome, _calls, _directory = self.execute()
        self.assertIsInstance(outcome, subprocess.CompletedProcess)
        self.assertEqual(outcome.returncode, 0)
        self.assertEqual(outcome.stdout, "producer-out ç" + os.linesep)

    def test_both_failures_retain_distinct_actual_exit_and_streams(self) -> None:
        outcome, calls, _directory = self.execute(17, 23)
        report = self.report(outcome)
        self.assertEqual(report["producer"]["exitCode"], 17)
        self.assertEqual(report["producer"]["stdout"], "producer-out ç" + os.linesep)
        self.assertEqual(report["producer"]["stderr"], "producer-error" + os.linesep)
        self.assertEqual(report["producer"]["arguments"], calls[0])
        self.assertEqual(report["cleanup"]["exitCode"], 23)
        self.assertEqual(report["cleanup"]["stderr"], "cleanup-error" + os.linesep)

    def test_successful_producer_with_failed_cleanup_cannot_pass(self) -> None:
        outcome, _calls, _directory = self.execute(0, 23)
        report = self.report(outcome)
        self.assertEqual(report["producer"]["exitCode"], 0)
        self.assertEqual(report["result"], "FAIL")

    def test_failed_producer_with_successful_cleanup_keeps_original_result(self) -> None:
        outcome, _calls, _directory = self.execute(17, 0)
        self.assertIsInstance(outcome, subprocess.CompletedProcess)
        self.assertEqual(outcome.returncode, 17)
        self.assertEqual(outcome.stderr, "producer-error" + os.linesep)

    def test_timeout_and_failed_cleanup_preserve_partial_real_output(self) -> None:
        outcome, _calls, _directory = self.execute(cleanup_exit=23, producer_mode="timeout")
        report = self.report(outcome)
        self.assertEqual(report["producer"]["status"], "TIMEOUT")
        self.assertIsNone(report["producer"]["exitCode"])
        self.assertEqual(report["producer"]["stdout"], "producer-out ç" + os.linesep)
        self.assertEqual(report["cleanup"]["exitCode"], 23)

    def test_launch_error_and_cleanup_error_are_separate(self) -> None:
        outcome, _calls, _directory = self.execute(producer_mode="launch", cleanup_mode="launch")
        report = self.report(outcome)
        self.assertEqual(report["producer"]["status"], "LAUNCH_ERROR")
        self.assertEqual(report["cleanup"]["status"], "LAUNCH_ERROR")

    def test_cleanup_timeout_retains_successful_producer(self) -> None:
        outcome, _calls, _directory = self.execute(cleanup_mode="timeout")
        report = self.report(outcome)
        self.assertEqual(report["producer"]["exitCode"], 0)
        self.assertEqual(report["cleanup"]["status"], "TIMEOUT")

    def test_absent_owned_container_is_successful_cleanup(self) -> None:
        outcome, _calls, _directory = self.execute(cleanup_exit=1, cleanup_mode="absent")
        self.assertIsInstance(outcome, subprocess.CompletedProcess)
        self.assertEqual(outcome.returncode, 0)

    def test_absence_of_another_owner_does_not_waive_cleanup_failure(self) -> None:
        from client_checks import _owned_container_absent

        observation = {"status": "COMPLETED", "exitCode": 1,
                       "stderr": "Error response from daemon: No such container: other-owner"}
        self.assertFalse(_owned_container_absent(observation, "this-owner"))
        observation["stderr"] = "permission denied; No such container: this-owner"
        self.assertFalse(_owned_container_absent(observation, "this-owner"))

    def test_invalid_utf8_retains_original_digest_without_replacement_text(self) -> None:
        import hashlib
        from client_checks import _attempt

        actual_run = subprocess.run
        raw = bytes([255, 254, 65])

        def producer(_argv: list[str], **kwargs: object) -> subprocess.CompletedProcess:
            return actual_run([sys.executable, "-c", "import sys;sys.stdout.buffer.write(bytes([255,254,65]))"],
                              **kwargs)

        with mock.patch.object(client_checks.subprocess, "run", side_effect=producer):
            _result, observation = _attempt(["docker", "run", "owned"], 30)
        self.assertIsNone(observation["stdout"])
        self.assertEqual(observation["stdoutRefusal"], "OUTPUT_ENCODING")
        self.assertEqual(observation["stdoutSha256"], hashlib.sha256(raw).hexdigest())
        self.assertEqual(observation["stdoutBytes"], 3)

    def test_secret_and_oversized_output_are_not_disclosed(self) -> None:
        marker = "sk-" + "CausalSyntheticMarker" * 3
        for output in (marker, "x" * 300000):
            with self.subTest(size=len(output)):
                outcome, _calls, _directory = self.execute(cleanup_exit=23, output=output)
                report = self.report(outcome)
                self.assertIsNone(report["producer"]["stdout"])
                self.assertNotIn(output, str(outcome))
                self.assertEqual(len(report["producer"]["stdoutSha256"]), 64)

    def test_explicit_native_runtime_has_no_docker_cleanup(self) -> None:
        actual_run = subprocess.run
        calls = []

        def native(argv: list[str], **kwargs: object) -> subprocess.CompletedProcess:
            calls.append(argv)
            result = actual_run([sys.executable, "-c", "print('native-result')"], **kwargs)
            result.args = argv
            return result

        with mock.patch.object(client_checks.subprocess, "run", side_effect=native):
            outcome = client_checks.run_node(node=Path(sys.executable), guard=True)
        self.assertEqual(outcome.returncode, 0)
        self.assertEqual(outcome.stdout, "native-result\n")
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0][0], sys.executable)
        self.assertNotIn("docker", calls[0])


if __name__ == "__main__":
    unittest.main()
