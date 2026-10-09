"""Control-plane and repository-boundary properties of GATE 4 — QUALITY ENGINE.

Behavioral quality-engine tests live with the evaluator package and run in its mandatory gate.
This suite checks the canonical specification, registries, boundaries, and repository integration
without substituting text assertions for behavior.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
LEDGER = PROJECT_ROOT / "scripts" / "development-ledger"
sys.path.insert(0, str(LEDGER))

import ledger_common  # noqa: E402
import policies  # noqa: E402

GATE = "GATE-4"
SPECIFICATION = PROJECT_ROOT / "docs" / "GATE-4-CHECKLIST.md"


class Gate4CanonicalSpecificationTests(unittest.TestCase):
    """The requirement denominator is parsed from the repository and cannot be narrowed."""

    def test_the_specification_exists_and_parses_every_required_row(self) -> None:
        rows = policies.parse_checklist(SPECIFICATION.read_text(encoding="utf-8"))
        self.assertEqual(len(rows), 105)
        self.assertEqual(len({row["key"] for row in rows}), len(rows))
        for row in rows:
            with self.subTest(key=row["key"]):
                self.assertTrue(row["description"].strip())
                self.assertTrue(row["artifact"].strip())
                self.assertTrue(row["evidence"].strip())

    def test_the_registry_mirrors_the_specification_row_for_row(self) -> None:
        declared = policies.canonical_requirements(PROJECT_ROOT, GATE)
        parsed = policies.parse_checklist(SPECIFICATION.read_text(encoding="utf-8"))
        self.assertEqual(
            [
                (row["key"], row["description"], row["artifact"], row["evidence"])
                for row in declared
            ],
            [(row["key"], row["description"], row["artifact"], row["evidence"]) for row in parsed],
        )
        self.assertTrue(all(row["mandatory"] for row in declared))

    def test_a_dropped_registry_row_is_refused(self) -> None:
        with tempfile.TemporaryDirectory(prefix="iacode-g4-spec-") as directory:
            root = Path(directory)
            shutil.copytree(PROJECT_ROOT / ".iacode" / "policies", root / ".iacode" / "policies")
            (root / "docs").mkdir()
            shutil.copy2(SPECIFICATION, root / "docs" / SPECIFICATION.name)
            self.assertEqual(len(policies.canonical_requirements(root, GATE)), 105)

            registry_path = root / ".iacode" / "policies" / "canonical-requirements.json"
            registry = json.loads(registry_path.read_text(encoding="utf-8"))
            entry = next(item for item in registry["gates"] if item["gate"] == GATE)
            entry["requirements"].pop()
            registry_path.write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")
            with self.assertRaises(ledger_common.LedgerError):
                policies.canonical_requirements(root, GATE)

    def test_the_specification_closes_the_false_pass_and_host_execution_paths(self) -> None:
        text = SPECIFICATION.read_text(encoding="utf-8")
        for statement in (
            "every command runs in the Gate 3 sandbox",
            "can never become `PASS`",
            "Python, Node, TypeScript, Angular, Java with",
            "passing fixture",
            "failing fixture",
            "real snapshot of IACode",
            "ends at `READY_FOR_REVIEW`",
        ):
            with self.subTest(statement=statement):
                self.assertIn(statement, text)


class Gate4InitialScopeTests(unittest.TestCase):
    """Gate 4 owns the evaluator and preserves later reservations while it starts."""

    def test_the_evaluator_reservation_belongs_to_gate_4(self) -> None:
        reservations = {item["path"]: item for item in policies.load_gate_scope(PROJECT_ROOT)}
        self.assertEqual(
            ledger_common.normalize_gate(reservations["services/evaluator"]["gate"]),
            ledger_common.normalize_gate(GATE),
        )

    def test_later_gate_reservations_are_still_in_force(self) -> None:
        in_force = {item["path"] for item in policies.reservations_in_force(PROJECT_ROOT, GATE)}
        for path in (
            "apps/cli",
            "apps/vscode-extension",
            "services/experience",
            "services/knowledge",
            "training",
            "evaluation",
            "datasets",
        ):
            with self.subTest(path=path):
                self.assertIn(path, in_force)

    def test_review_bundles_are_permanently_ignored(self) -> None:
        ignored = (PROJECT_ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
        self.assertIn("artifacts/review/", ignored)

    def test_the_evaluator_reservation_is_consumed_and_later_scope_is_clean(self) -> None:
        in_force = {item["path"] for item in policies.reservations_in_force(PROJECT_ROOT, GATE)}
        self.assertNotIn("services/evaluator", in_force)
        self.assertEqual(policies.scope_violations(PROJECT_ROOT, GATE), [])
        readme = (PROJECT_ROOT / "services" / "evaluator" / "README.md").read_text(encoding="utf-8")
        self.assertNotIn(policies.RESERVATION_MARKER, readme)


class Gate4MandatoryGateTests(unittest.TestCase):
    RUNNER = PROJECT_ROOT / "scripts" / "iacode" / "gates" / "evaluator_tests.py"

    def test_the_evaluator_gate_is_mandatory_and_builds_what_it_measures(self) -> None:
        gates = policies.gate_definitions(PROJECT_ROOT)
        self.assertIn("evaluatorTests", gates)
        self.assertTrue(gates["evaluatorTests"]["mandatory"])
        self.assertEqual(
            gates["evaluatorTests"]["command"],
            ["python", "scripts/iacode/gates/evaluator_tests.py"],
        )
        source = self.RUNNER.read_text(encoding="utf-8")
        self.assertLess(source.index('build_service("evaluator")'), source.index("pytest"))

    def test_the_evaluator_suite_is_declared_counted_and_present(self) -> None:
        suites = {item["id"]: item for item in policies.load_test_suites(PROJECT_ROOT)}
        self.assertEqual(suites["evaluator"]["root"], "services/evaluator/tests")
        self.assertEqual(suites["evaluator"]["framework"], "python-pytest")
        self.assertTrue(suites["evaluator"]["counted"])
        self.assertTrue((PROJECT_ROOT / suites["evaluator"]["root"]).is_dir())

    def test_the_evaluator_service_has_no_engine_socket_or_host_project_mount(self) -> None:
        compose_directory = PROJECT_ROOT / "infra" / "compose"
        completed = subprocess.run(
            [
                "docker",
                "compose",
                "--project-directory",
                str(compose_directory),
                "--file",
                str(compose_directory / "docker-compose.yml"),
                "--env-file",
                str(compose_directory / ".env"),
                "config",
                "--format",
                "json",
            ],
            cwd=compose_directory,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr[-1000:])
        compose = json.loads(completed.stdout)
        evaluator = compose["services"]["evaluator"]
        self.assertFalse(evaluator.get("volumes"))
        self.assertNotIn("ports", evaluator)
        self.assertNotIn("group_add", evaluator)


if __name__ == "__main__":
    unittest.main()
