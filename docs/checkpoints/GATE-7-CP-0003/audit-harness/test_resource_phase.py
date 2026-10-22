"""Actual filesystem/child controls; engine inventories are labeled isolated doubles."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import current_resources as phase
from ledger_common import load_json, write_json


class ResourcePhaseTests(unittest.TestCase):
    def setUp(self):
        self.owner = tempfile.TemporaryDirectory(prefix="iacode-m2cp3-phase-unit-")
        self.config = tempfile.TemporaryDirectory(prefix="iacode-m2cp3-buildx-unit-")
        self.addCleanup(self.owner.cleanup)
        self.addCleanup(self.config.cleanup)
        self.checkpoint = Path(self.owner.name).resolve()
        self.addCleanup(patch.stopall)
        patch.object(phase, "CHECKPOINT", self.checkpoint).start()
        self.directory = self.checkpoint / "resource-phases/phase-0002"
        self.directory.mkdir(parents=True)
        self.path = self.directory / "OWNED-DOCKER-SCOPE.json"
        self.project = "iacode-m2cp3-" + "a" * 32
        self.inventory = {"containers": [], "images": [], "networks": [], "volumes": [],
                          "dockerConfigHash": "f" * 64}
        self.scope = {"phase": "phase-0002", "status": "ACTIVE",
                      "builder": "iacode-m2cp3-unit-phase",
                      "privateBuildxConfig": self.config.name,
                      "inheritedOwnedProject": self.project, "registeredProjects": [self.project],
                      "before": self.inventory}
        write_json(self.path, self.scope)
        self.marker = {"schemaVersion": "1.0.0", "phase": "phase-0002",
                       "scopePath": "resource-phases/phase-0002/OWNED-DOCKER-SCOPE.json"}
        write_json(self.checkpoint / "ACTIVE-DOCKER-PHASE.json", self.marker)
        (self.directory / "RUNTIME-OWNER.txt").write_bytes(
            ("COMPOSE_PROJECT_NAME=" + self.project + "\nIACODE_VERSION=0.1.0\n").encode())
        self.old = self.checkpoint / "OWNED-DOCKER-SCOPE.json"
        self.old.write_bytes(b"HISTORICAL_DISPOSED_SCOPE_MUST_NOT_CHANGE")
        self.disposal = self.checkpoint / "OWNED-RESOURCE-CLEANUP.json"
        self.disposal.write_bytes(b"HISTORICAL_FAILED_COMPARISON_MUST_NOT_CHANGE")

    def test_real_child_environment_selects_new_phase_without_global_environment_change(self):
        before = dict(os.environ)
        environment = phase.child_environment()
        self.assertEqual(self.path, phase.current_scope_path())
        self.assertEqual(self.project, environment["COMPOSE_PROJECT_NAME"])
        self.assertEqual(self.scope["builder"], environment["BUILDX_BUILDER"])
        self.assertEqual(Path(self.config.name), Path(environment["BUILDX_CONFIG"]))
        self.assertEqual(self.directory / "RUNTIME-OWNER.txt", phase.current_owner_file())
        self.assertEqual(before, dict(os.environ))
        self.assertEqual(b"HISTORICAL_DISPOSED_SCOPE_MUST_NOT_CHANGE", self.old.read_bytes())

    def test_marker_parent_component_is_refused_before_engine_access(self):
        self.marker["scopePath"] = "resource-phases/phase-0002/../phase-0002/OWNED-DOCKER-SCOPE.json"
        write_json(self.checkpoint / "ACTIVE-DOCKER-PHASE.json", self.marker)
        with patch.object(phase.operator, "docker") as engine:
            with self.assertRaises(ValueError):
                phase.child_environment()
        engine.assert_not_called()

    def test_existing_pointer_refuses_new_phase_before_engine_access(self):
        original = self.path.read_bytes()
        with patch.object(phase.operator, "prepare") as creation:
            with self.assertRaisesRegex(ValueError, "DO_NOT_REPLACE_RESOURCE_PHASE_POINTER"):
                phase.prepare()
        creation.assert_not_called()
        self.assertEqual(original, self.path.read_bytes())

    def test_actual_hardlinked_receipt_is_refused(self):
        os.link(self.path, self.directory / "linked-receipt.json")
        with patch.object(phase.operator, "docker") as engine:
            with self.assertRaisesRegex(ValueError, "LINKED_RESOURCE_PHASE"):
                phase.child_environment()
        engine.assert_not_called()

    def test_disposed_current_phase_refuses_replay(self):
        self.scope["status"] = "CLEANED"
        write_json(self.path, self.scope)
        with self.assertRaisesRegex(ValueError, "OWNED_SCOPE_NOT_ACTIVE"):
            phase.child_environment()

    def test_runtime_owner_tamper_is_refused(self):
        (self.directory / "RUNTIME-OWNER.txt").write_bytes(b"COMPOSE_PROJECT_NAME=other-project\n")
        with self.assertRaisesRegex(ValueError, "RESOURCE_PHASE_RUNTIME_OWNER_MISMATCH"):
            phase.current_owner_file()

    def test_bootstrap_observation_is_one_shot_before_any_process_effect(self):
        target = self.directory / "BUILDER-BOOTSTRAP.json"
        target.write_bytes(b"PRIOR_BOOTSTRAP_OBSERVATION")
        with patch.object(phase, "run_owned") as launch:
            with self.assertRaises(ValueError):
                phase.bootstrap_builder()
        launch.assert_not_called()
        self.assertEqual(b"PRIOR_BOOTSTRAP_OBSERVATION", target.read_bytes())

    def test_separate_cleanup_receipt_preserves_historical_bytes_and_removes_only_owned_fixture(self):
        original = {path: path.read_bytes() for path in (self.old, self.disposal)}
        real_run = subprocess.run

        def engine_double(arguments, **kwargs):
            self.assertEqual(["docker", "buildx", "rm", self.scope["builder"]], arguments)
            return real_run([sys.executable, "-c", "print('OWNED_PHASE_CLEANUP_NULL')"], **kwargs)

        with patch.object(phase.operator, "snapshot", return_value=self.inventory), \
                patch.object(phase.operator, "configuration_hash", return_value="f" * 64), \
                patch.object(phase.operator.subprocess, "run", side_effect=engine_double):
            self.assertEqual(0, phase.operator.cleanup(self.path))
        self.assertEqual("PASS", load_json(self.directory / "OWNED-RESOURCE-CLEANUP.json")["result"])
        self.assertFalse(Path(self.config.name).exists())
        for path, raw in original.items():
            self.assertEqual(raw, path.read_bytes())
        with patch.object(phase.operator, "snapshot") as query:
            with self.assertRaises(ValueError):
                phase.operator.cleanup(self.path)
        query.assert_not_called()


if __name__ == "__main__":
    from ledger_common import use_utf8_stdout
    use_utf8_stdout()
    unittest.main()
