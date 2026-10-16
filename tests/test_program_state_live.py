"""Actual CLI/Git controls for a live observation, never a simulated Gate verdict."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY = {"schemaVersion": "1.0.0", "output": "var/program-state.json",
          "snapshotSchemaVersion": "1.1.0"}


def write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value) + "\n", encoding="utf-8")


class LiveProgramStateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="iacode-program-state-control-")
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.root = self.base / "checkout"
        self.root.mkdir()
        self.remote = self.base / "remote.git"
        self.git(self.base, "init", "--bare", str(self.remote))
        self.git(self.root, "init", "-b", "main")
        self.git(self.root, "config", "user.name", "IACode control")
        self.git(self.root, "config", "user.email", "control@example.invalid")
        self.git(self.root, "config", "commit.gpgsign", "false")
        self.policy = self.root / ".iacode/policies/program-state.json"
        write(self.policy, POLICY)
        schema = self.root / ".iacode/schemas/program-state.schema.json"
        schema.parent.mkdir(parents=True)
        shutil.copy2(ROOT / ".iacode/schemas/program-state.schema.json", schema)
        self.checkpoint = self.root / "docs/checkpoints/GATE-4-CP-9000"
        self.checkpoint.mkdir(parents=True)
        (self.checkpoint.parent / "LATEST.md").write_text(
            "# Latest\n\nCheckpoint: docs/checkpoints/GATE-4-CP-9000\n", encoding="utf-8")
        self.state = {"gate": "GATE-4", "status": "IN_PROGRESS", "blockedBy": [],
                      "branch": "main", "currentCommit": "HEAD",
                      "nextAllowedAction": "Execute the real current controls."}
        write(self.checkpoint / "STATE.json", self.state)
        self.steps = {"gate": "GATE-4", "checkpoint": self.checkpoint.name,
                      "steps": [self.step("G4-S00", "COMPLETE"),
                                self.step("G4-S01", "IN_PROGRESS")]}
        write(self.checkpoint / "STEPS.json", self.steps)
        (self.root / ".gitignore").write_text("var/\n", encoding="utf-8")
        (self.root / "payload.txt").write_text("original\n", encoding="utf-8")
        self.legacy = self.root / "docs/program/PROGRAM-STATE.json"
        write(self.legacy, {"historicalObservation": "must remain byte-identical"})
        self.legacy_bytes = self.legacy.read_bytes()
        self.git(self.root, "add", ".")
        self.git(self.root, "commit", "-m", "actual program-state fixture")
        self.git(self.root, "remote", "add", "origin", str(self.remote))
        self.git(self.root, "push", "origin", "main")
        self.live = self.root / "var/program-state.json"

    @staticmethod
    def step(identifier: str, status: str) -> dict:
        return {"stepId": identifier, "status": status, "requirements": ["GATE-4-18.2"],
                "expectedBehavior": "Record truthful observed state.",
                "implementation": ["payload.txt"], "tests": ["actual CLI control"],
                "functionalProof": "A real CLI/Git metadata observation, not a Gate approval.",
                "evidence": ["actual fixture input"] if status == "COMPLETE" else []}

    def git(self, root: Path, *arguments: str) -> str:
        result = subprocess.run(["git", *arguments], cwd=root, capture_output=True, text=True,
                                encoding="utf-8", errors="replace", check=False)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result.stdout.strip()

    def cli(self, *arguments: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(ROOT / "scripts/development-ledger/program_state.py"),
             "--root", str(self.root), *arguments], cwd=self.root,
            capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)

    def generate(self) -> dict:
        result = self.cli("--write")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue(self.live.is_file(), "the live observation must not be committed content")
        return json.loads(self.live.read_text(encoding="utf-8"))

    def test_live_policy_requires_generated_program_state(self) -> None:
        self.assertEqual(json.loads((ROOT / ".iacode/policies/program-state.json").read_text()),
                         POLICY)
        ignored = subprocess.run(["git", "check-ignore", "--quiet", "var/program-state.json"],
                                 cwd=ROOT, check=False)
        self.assertEqual(ignored.returncode, 0)

    def test_real_cli_roundtrip_is_clean_and_supports_internal_closure(self) -> None:
        self.state["status"] = "INTERNAL_GATE_PASS"
        write(self.checkpoint / "STATE.json", self.state)
        self.git(self.root, "add", ".")
        self.git(self.root, "commit", "-m", "observe declared internal status")
        self.git(self.root, "push", "origin", "main")
        document = self.generate()
        self.assertEqual(document["schemaVersion"], "1.1.0")
        self.assertEqual(document["status"], "INTERNAL_GATE_PASS")
        self.assertEqual(document["checkpoint"], self.checkpoint.name)
        self.assertEqual(document["localCommit"], self.git(self.root, "rev-parse", "HEAD"))
        self.assertEqual(document["localCommit"], document["remoteCommit"])
        self.assertEqual((document["step"], document["lastCompletedStep"]), ("G4-S01", "G4-S00"))
        self.assertEqual(self.cli().returncode, 0)
        self.assertEqual(self.git(self.root, "status", "--porcelain"), "")
        self.assertEqual(self.legacy.read_bytes(), self.legacy_bytes)

    def test_local_git_movement_refuses_stale_observation_without_rewriting(self) -> None:
        self.generate()
        before = self.live.read_bytes()
        (self.root / "payload.txt").write_text("changed\n", encoding="utf-8")
        self.git(self.root, "add", "payload.txt")
        self.git(self.root, "commit", "-m", "advance local subject")
        result = self.cli()
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("localCommit", result.stdout)
        self.assertEqual(self.live.read_bytes(), before)
        document = self.generate()
        self.assertNotEqual(document["localCommit"], document["remoteCommit"])
        self.assertEqual(self.cli().returncode, 0)

    def test_remote_git_movement_refuses_stale_observation_without_rewriting(self) -> None:
        self.generate()
        before = self.live.read_bytes()
        peer = self.base / "peer"
        self.git(self.base, "clone", "--no-local", "--branch", "main", str(self.remote), str(peer))
        (peer / "payload.txt").write_text("remote change\n", encoding="utf-8")
        self.git(peer, "add", "payload.txt")
        self.git(peer, "-c", "user.name=IACode control", "-c", "user.email=control@example.invalid",
                 "-c", "commit.gpgsign=false", "commit", "-m", "advance actual remote")
        self.git(peer, "push", "origin", "main")
        result = self.cli()
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("remoteCommit", result.stdout)
        self.assertEqual(self.live.read_bytes(), before)
        document = self.generate()
        self.assertEqual(document["remoteCommit"], self.git(peer, "rev-parse", "HEAD"))
        self.assertNotEqual(document["localCommit"], document["remoteCommit"])
        self.assertEqual(self.cli().returncode, 0)

    def test_contradictory_steps_cannot_replace_a_valid_observation(self) -> None:
        self.generate()
        before = self.live.read_bytes()
        variants = [dict(self.steps, gate="GATE-3"),
                    dict(self.steps, checkpoint="GATE-4-CP-8999"),
                    dict(self.steps, steps=[self.steps["steps"][0]] * 2),
                    dict(self.steps, steps=[self.step("G4-S00", "ASSERTED")])]
        for variant in variants:
            with self.subTest(variant=variant):
                write(self.checkpoint / "STEPS.json", variant)
                result = self.cli("--write")
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertEqual(self.live.read_bytes(), before)
        (self.checkpoint / "STEPS.json").unlink()
        self.assertEqual(self.cli("--write").returncode, 1)
        self.assertEqual(self.live.read_bytes(), before)

    def test_unsafe_or_unknown_policy_cannot_overwrite_source(self) -> None:
        source = (self.root / "payload.txt").read_bytes()
        for changes in ({"output": "payload.txt"}, {"output": "../outside.json"},
                        {"schemaVersion": "unknown"}, {"snapshotSchemaVersion": "1.0.0"}):
            with self.subTest(changes=changes):
                write(self.policy, POLICY | changes)
                result = self.cli("--write")
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertEqual((self.root / "payload.txt").read_bytes(), source)
                self.assertFalse((self.base / "outside.json").exists())

    def test_redirected_runtime_directory_cannot_write_outside_the_checkout(self) -> None:
        outside = self.base / "outside"
        outside.mkdir()
        if os.name == "nt":
            result = subprocess.run(["cmd", "/c", "mklink", "/J", str(self.root / "var"),
                                     str(outside)], capture_output=True, check=False)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        else:
            (self.root / "var").symlink_to(outside, target_is_directory=True)
        result = self.cli("--write")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertFalse((outside / "program-state.json").exists())

    def test_legacy_storage_and_status_semantics_are_not_reinterpreted(self) -> None:
        self.policy.unlink()
        result = self.cli("--write")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        document = json.loads(self.legacy.read_text())
        self.assertEqual(document["schemaVersion"], "1.0.0")
        self.assertFalse(self.live.exists())
        self.assertEqual(self.cli().returncode, 0)
        self.state["status"] = "MILESTONE_PASS"
        write(self.checkpoint / "STATE.json", self.state)
        self.assertEqual(self.cli("--write").returncode, 0)
        self.assertEqual(self.cli().returncode, 0)
        self.state["status"] = "INTERNAL_GATE_PASS"
        write(self.checkpoint / "STATE.json", self.state)
        before = self.legacy.read_bytes()
        self.assertEqual(self.cli("--write").returncode, 1)
        self.assertEqual(self.legacy.read_bytes(), before)

    def test_wrong_checkpoint_or_tampered_observation_is_refused(self) -> None:
        document = self.generate()
        document["status"] = "READY_FOR_REVIEW"
        write(self.live, document)
        tampered = self.live.read_bytes()
        self.assertEqual(self.cli().returncode, 1)
        self.assertEqual(self.live.read_bytes(), tampered)
        self.assertEqual(self.cli("--write", "--checkpoint",
                                  "docs/checkpoints/GATE-4-CP-8999").returncode, 1)
        self.assertEqual(self.live.read_bytes(), tampered)

    def test_checkpoint_contradictions_are_not_silently_coerced(self) -> None:
        self.generate()
        before = self.live.read_bytes()
        for changes in ({"blockedBy": "not an array"}, {"nextAllowedAction": None},
                        {"branch": "not-main"}, {"currentCommit": "0" * 40}):
            with self.subTest(changes=changes):
                write(self.checkpoint / "STATE.json", self.state | changes)
                result = self.cli("--write")
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertEqual(self.live.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
