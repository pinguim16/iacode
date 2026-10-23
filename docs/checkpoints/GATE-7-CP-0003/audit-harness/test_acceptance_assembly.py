"""Read-only assembly controls, not execution or simulation of full runtime acceptance."""

from __future__ import annotations

import unittest
from unittest.mock import patch

import acceptance_evidence as acceptance
import complete_requirements as requirements


class AcceptanceAssemblyControls(unittest.TestCase):
    def test_actual_latest_publication_is_selected_not_an_older_passing_epoch(self):
        from ledger_common import load_json

        publication = acceptance.current_publication()
        candidates = [
            load_json(path) for path in acceptance.CHECKPOINT.glob("RUNTIME-V*-PUBLICATION.json")
        ]
        versions = [int(row["tag"].rsplit("-v", 1)[1]) for row in candidates]
        self.assertEqual(int(publication["tag"].rsplit("-v", 1)[1]), max(versions))
        self.assertTrue(publication["tag"].startswith("iacode-subjects/GATE-7-CP-0003-"))

    def test_closed_sealed_loader_refuses_an_unreviewed_name(self):
        from ledger_common import LedgerError

        with (
            self.assertRaises(LedgerError),
            patch.object(acceptance.subprocess, "check_output") as command,
        ):
            acceptance.sealed_module("../../outside")
        command.assert_not_called()

    def test_actual_unchanged_sealed_functional_mapping_is_complete(self):
        from check_functional_acceptance import functional_requirement_ids

        with patch.object(
            acceptance.subprocess, "check_output", wraps=acceptance.subprocess.check_output
        ) as actual_git:
            module = acceptance.sealed_functional_module()
        self.assertEqual(actual_git.call_count, 1)
        self.assertEqual(actual_git.call_args.args[0][:3], ["git", "-c", "core.longpaths=true"])
        self.assertEqual(module.CHECKPOINT, acceptance.CHECKPOINT)
        actual = {
            "GATE-7-" + value
            for group in module.GROUPS.values()
            for value in group["requirements"].split()
        }
        self.assertEqual(actual, set(functional_requirement_ids(acceptance.ROOT, "GATE-7")))

    def test_reviewed_direct_mapping_names_actual_current_artifacts(self):
        from ledger_common import load_json

        closure = load_json(acceptance.CHECKPOINT / "CLOSURE-REQUIREMENTS.json")
        lessons = {
            row["sourceRef"].removeprefix("lesson:")
            for row in closure["requirements"]
            if row["sourceRef"].startswith("lesson:")
        }
        self.assertTrue(set(requirements.DIRECT) <= lessons)
        for identifier, (artifacts, tests, proofs) in requirements.DIRECT.items():
            for value in [*artifacts, *tests]:
                path = acceptance.ROOT / requirements.artifact(value).removeprefix("file:")
                self.assertTrue(path.is_file(), (identifier, value))
            for value in proofs:
                self.assertTrue((acceptance.CHECKPOINT / value).is_file(), (identifier, value))
        for references in requirements.CURRENT_CANONICAL.values():
            for reference in references:
                kind, _, value = reference.partition(":")
                base = acceptance.CHECKPOINT if kind == "checkpoint" else acceptance.ROOT
                self.assertTrue((base / value).is_file(), reference)

    def test_actual_sealed_baseline_and_new_membership_are_exact(self):
        import json

        from ledger_common import load_json

        with patch.object(
            requirements.subprocess, "check_output", wraps=requirements.subprocess.check_output
        ) as actual_git:
            baseline = json.loads(requirements.baseline_document("CLOSURE-REQUIREMENTS.json"))
        self.assertEqual(actual_git.call_count, 1)
        self.assertEqual(actual_git.call_args.args[0][:3], ["git", "-c", "core.longpaths=true"])
        inherited = {row["sourceRef"] for row in baseline["requirements"]}
        current = load_json(acceptance.CHECKPOINT / "CLOSURE-REQUIREMENTS.json")
        references = [row["sourceRef"] for row in current["requirements"]]
        self.assertEqual(len(references), len(set(references)))
        self.assertEqual(
            set(references),
            inherited
            | {
                "lesson:LSN-0152",
                "lesson:LSN-0153",
                "lesson:LSN-0154",
                "finding:M2-F-001",
                "finding:M2-F-002",
                "attack:M2-RT-01",
            },
        )

    def test_inherited_bindings_resolve_without_borrowing_a_command_verdict(self):
        import json

        from delivery_assurance import (
            collect_test_ids,
            command_succeeded,
            load_command_results,
            resolve_evidence,
        )
        from derive_requirements import EVIDENCE_FIELDS

        closure = json.loads(requirements.baseline_document("CLOSURE-REQUIREMENTS.json"))
        originals = requirements.baseline_document("COMMANDS.jsonl")
        prior_commands = {
            row["id"]: row
            for row in (json.loads(line) for line in originals.splitlines() if line.strip())
        }
        commands = load_command_results(acceptance.CHECKPOINT)
        tests = collect_test_ids(acceptance.ROOT)
        bindings = []
        for row in closure["requirements"]:
            for field in EVIDENCE_FIELDS:
                for reference in row[field]:
                    translated = requirements.inherited(reference, prior_commands, bindings)
                    self.assertIsNone(
                        resolve_evidence(
                            acceptance.ROOT, acceptance.CHECKPOINT, translated, commands, tests
                        ),
                        (row["sourceRef"], reference, translated),
                    )
                    if reference.startswith("command:"):
                        self.assertTrue(translated.startswith("file:"))
        expected = {
            value
            for row in closure["requirements"]
            for field in EVIDENCE_FIELDS
            for value in row[field]
            if value.startswith("command:")
        }
        self.assertEqual({binding["original"] for binding in bindings}, expected)
        # The real baseline uses file bindings. Independently exercise the command branch
        # with an actual successful sealed record, not an invented fixture command.
        actual = next(row for row in prior_commands.values() if command_succeeded(row))
        translated = requirements.inherited("command:" + actual["id"], prior_commands, bindings)
        self.assertEqual(translated, "file:docs/checkpoints/GATE-7-CP-0001/COMMANDS.jsonl")
        self.assertTrue(bindings)
        for binding in bindings:
            self.assertEqual(
                binding["record"], prior_commands[binding["original"].removeprefix("command:")]
            )

    def test_missing_current_execution_refuses_before_sealed_writer_or_artifact_change(self):
        from ledger_common import LedgerError

        paths = [
            acceptance.CHECKPOINT / name
            for name in (
                "STATE.json",
                "QUALITY.json",
                "REQUIREMENTS-MATRIX.json",
                "FUNCTIONAL-ACCEPTANCE.json",
            )
        ]
        before = {path: path.read_bytes() if path.exists() else None for path in paths}
        # A labeled injected precondition failure only; no modeled PASS or producer is created.
        with (
            patch.object(
                acceptance, "current_execution", side_effect=LedgerError("CONTROL_REFUSAL")
            ),
            patch.object(acceptance, "sealed_functional_module") as writer,
            self.assertRaises(LedgerError),
        ):
            acceptance.main()
        writer.assert_not_called()
        self.assertEqual(
            before, {path: path.read_bytes() if path.exists() else None for path in paths}
        )


if __name__ == "__main__":
    from ledger_common import use_utf8_stdout

    use_utf8_stdout()
    unittest.main()
