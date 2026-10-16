from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))

from ledger_common import LedgerError, resolve_latest, validate_schema, write_json
from sync_in_progress_metadata import synchronize


class InProgressMetadataTests(unittest.TestCase):
    def test_validation_runner_keeps_the_synchronizers_derived_state(self) -> None:
        path = resolve_latest(ROOT) / "audit-harness/run_checkpoint_validation.py"
        spec = importlib.util.spec_from_file_location("metadata_validation_runner", path)
        assert spec is not None and spec.loader is not None
        runner = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(runner)

        class ReachedHashBoundary(Exception):
            pass

        with tempfile.TemporaryDirectory() as directory:
            checkpoint = Path(directory)
            write_json(checkpoint / "STATE.json", {
                "status": "IN_PROGRESS", "gate": "GATE-4", "currentCommit": "HEAD",
                "dirty": False, "lessonPreflight": {"lessonsConsidered": 1},
            })
            write_json(checkpoint / "RUN-METADATA.json", {"finalCommit": "old"})
            write_json(checkpoint / "LESSON-PREFLIGHT.json", {
                "gate": "GATE-4", "scope": "runner boundary", "lessonsConsidered": 7,
                "lessonsApplicable": 3, "derivedRequirements": [{}, {}, {}],
            })
            # Stop before hash binding/validator execution; this measures metadata, not a fake PASS.
            with (
                mock.patch.object(runner, "ROOT", checkpoint),
                mock.patch.object(runner, "CHECKPOINT", checkpoint),
                mock.patch("sync_in_progress_metadata.run_git", return_value=(1, "")),
                mock.patch.object(runner, "refresh_declared_hashes",
                                  side_effect=ReachedHashBoundary),
                self.assertRaises(ReachedHashBoundary),
            ):
                runner.main()
            state = json.loads((checkpoint / "STATE.json").read_text())
            self.assertTrue(state["dirty"])
            self.assertEqual(state["lessonPreflight"]["lessonsConsidered"], 7)
            self.assertEqual(state["lessonPreflight"]["derivedRequirements"], 3)
            self.assertEqual(state["status"], "IN_PROGRESS")

    def test_lesson_timestamp_transport_rejects_locale_rendering(self) -> None:
        lesson = next(
            json.loads(line) for line in (ROOT / ".iacode/memory/lessons.jsonl").read_text(
                encoding="utf-8",
            ).splitlines() if json.loads(line)["lessonId"] == "LSN-0105"
        )
        schema = json.loads((ROOT / ".iacode/schemas/lesson.schema.json").read_text())
        transported = json.loads(json.dumps(lesson))
        self.assertEqual(validate_schema(transported, schema), [])
        transported["guardrailFailures"][0]["observedAt"] = "10/15/2026 18:27:52"
        errors = validate_schema(transported, schema)
        self.assertTrue(any("observedAt: invalid date-time" in value for value in errors))

    def test_preflight_aggregates_and_commit_semantics_are_derived_without_promotion(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            checkpoint = Path(directory)
            state = {"status": "IN_PROGRESS", "gate": "GATE-4", "currentCommit": "HEAD",
                     "dirty": False, "lessonPreflight": {"evidence": ["command:cmd-0018"]},
                     "secondToolValidation": {"status": "PENDING_MANUAL"}}
            write_json(checkpoint / "STATE.json", state)
            write_json(checkpoint / "RUN-METADATA.json", {"finalCommit": "old"})
            write_json(checkpoint / "LESSON-PREFLIGHT.json", {
                "gate": "GATE-4", "scope": "internal audit", "lessonsConsidered": 7,
                "lessonsApplicable": 3, "derivedRequirements": [{}, {}, {}],
            })
            with mock.patch("sync_in_progress_metadata.run_git", return_value=(1, "")):
                synchronize(checkpoint, checkpoint)
            observed = json.loads((checkpoint / "STATE.json").read_text())
            metadata = json.loads((checkpoint / "RUN-METADATA.json").read_text())
            self.assertEqual(observed["status"], "IN_PROGRESS")
            self.assertEqual(observed["lessonPreflight"]["derivedRequirements"], 3)
            self.assertEqual(observed["lessonPreflight"]["evidence"], ["command:cmd-0018"])
            self.assertEqual(metadata["finalCommit"], "HEAD")
            self.assertTrue(observed["dirty"])
            self.assertEqual(observed["secondToolValidation"], state["secondToolValidation"])

    def test_a_sealed_or_terminal_checkpoint_is_never_rewritten(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            checkpoint = Path(directory)
            for status, code in (("IN_PROGRESS", 0), ("READY_FOR_REVIEW", 1)):
                write_json(checkpoint / "STATE.json", {"status": status})
                before = (checkpoint / "STATE.json").read_bytes()
                with mock.patch("sync_in_progress_metadata.run_git", return_value=(code, "")):
                    with self.assertRaises(LedgerError):
                        synchronize(checkpoint, checkpoint)
                self.assertEqual((checkpoint / "STATE.json").read_bytes(), before)

    def test_a_different_gate_preflight_is_refused_not_reconciled(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            checkpoint = Path(directory)
            write_json(checkpoint / "STATE.json", {"status": "IN_PROGRESS", "gate": "GATE-4"})
            write_json(checkpoint / "LESSON-PREFLIGHT.json", {"gate": "GATE-5"})
            before = (checkpoint / "STATE.json").read_bytes()
            with mock.patch("sync_in_progress_metadata.run_git", return_value=(1, "")):
                with self.assertRaises(LedgerError):
                    synchronize(checkpoint, checkpoint)
            self.assertEqual((checkpoint / "STATE.json").read_bytes(), before)
