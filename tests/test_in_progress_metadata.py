from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))

from ledger_common import LedgerError, write_json
from sync_in_progress_metadata import synchronize


class InProgressMetadataTests(unittest.TestCase):
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
