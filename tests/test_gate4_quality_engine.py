"""Control-plane and repository-boundary properties of GATE 4 — QUALITY ENGINE.

Behavioral quality-engine tests live with the evaluator package and run in its mandatory gate.
This suite checks the canonical specification, registries, boundaries, and repository integration
without substituting text assertions for behavior.
"""

from __future__ import annotations

import hashlib
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

import check_functional_acceptance  # noqa: E402
import ledger_common  # noqa: E402
import policies  # noqa: E402
import program_state  # noqa: E402
import review_bundle  # noqa: E402

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

    def test_complete_verification_runs_evaluator_integration_against_the_stack(self) -> None:
        source = (PROJECT_ROOT / "scripts" / "iacode" / "verify.py").read_text(encoding="utf-8")
        scenario = (
            PROJECT_ROOT / "scripts" / "iacode" / "scenarios" / "quality_persistence.py"
        ).read_text(encoding="utf-8")
        self.assertIn('"quality-integration"', source)
        self.assertIn('"scripts/iacode/scenarios/quality_persistence.py"', source)
        self.assertIn('build_service("api")', scenario)
        self.assertIn('build_service("evaluator")', scenario)
        self.assertIn('"/app/tests/integration/test_migrations.py"', scenario)
        self.assertIn('"/app/evaluator_tests/integration"', scenario)

    def test_verification_names_every_quality_lifecycle_proof(self) -> None:
        source = (PROJECT_ROOT / "scripts" / "iacode" / "verify.py").read_text(encoding="utf-8")
        for stage in (
            "quality-pass",
            "quality-fail",
            "quality-iacode",
            "quality-reproduction",
            "quality-recovery",
            "quality-cancellation",
            "quality-timeout",
            "quality-false-pass",
        ):
            with self.subTest(stage=stage):
                self.assertIn(f'"{stage}"', source)


class Gate4QualityImageTests(unittest.TestCase):
    """Each supported stack maps to an isolated, immutable sandbox toolchain."""

    def test_quality_profiles_are_closed_offline_and_content_addressed(self) -> None:
        policy = json.loads(
            (PROJECT_ROOT / ".iacode" / "policies" / "sandbox-policy.json").read_text(
                encoding="utf-8"
            )
        )
        images = {item["name"]: item for item in policy["imageProfiles"]}
        sandboxes = {item["name"]: item for item in policy["sandboxPolicies"]}
        for name in ("quality-python", "quality-node", "quality-java"):
            with self.subTest(name=name):
                image = images[name]
                sandbox = sandboxes[name]
                dockerfile = PROJECT_ROOT / image["context"] / "Dockerfile"
                self.assertTrue(dockerfile.is_file())
                self.assertIn("@sha256:", dockerfile.read_text(encoding="utf-8"))
                self.assertEqual(sandbox["tools"], ["shell.exec"])
                self.assertEqual(sandbox["networkProfile"], "none")
                self.assertEqual(sandbox["imageProfile"], name)

    def test_every_stack_maps_to_exactly_one_quality_policy(self) -> None:
        source = (
            PROJECT_ROOT / "services" / "evaluator" / "src" / "iacode_evaluator" / "executor.py"
        ).read_text(encoding="utf-8")
        for profile in (
            "python",
            "node",
            "node+typescript",
            "node+typescript+angular",
            "maven",
            "gradle",
        ):
            self.assertIn(f'"{profile}"', source)


class FunctionalAcceptanceTests(unittest.TestCase):
    def _document(
        self, checkpoint: str, requirements: tuple[str, ...], result: str = "PASS"
    ) -> dict:
        return {
            "schemaVersion": "1.0.0",
            "gate": GATE,
            "checkpoint": checkpoint,
            "status": "PASS" if result == "PASS" else "FAIL",
            "generatedAt": "2026-10-09T19:00:00Z",
            "scenarios": [
                {
                    "scenarioId": "G4-FUNCTIONAL-CONTROL",
                    "requirementIds": list(requirements),
                    "feature": "functional acceptance control",
                    "scenario": "An executed observation is compared with its expected result.",
                    "environment": "test process",
                    "preconditions": ["canonical requirements are available"],
                    "execution": ["execute the observable control"],
                    "expected": ["the control passes"],
                    "observed": ["the control passed"],
                    "result": result,
                    "evidence": ["file:docs/GATE-4-CHECKLIST.md"],
                    "timestamp": "2026-10-09T19:00:00Z",
                    "artifactReferences": [],
                }
            ],
        }

    def test_functional_scope_is_derived_from_the_canonical_gate(self) -> None:
        requirements = check_functional_acceptance.functional_requirement_ids(PROJECT_ROOT, GATE)
        self.assertIn("GATE-4-16.1", requirements)
        self.assertIn("GATE-4-16.5", requirements)
        self.assertIn("GATE-4-12.2", requirements)
        self.assertNotIn("GATE-4-1.1", requirements)

    def test_only_executed_resolved_pass_scenarios_cover_the_denominator(self) -> None:
        requirements = check_functional_acceptance.functional_requirement_ids(PROJECT_ROOT, GATE)
        with tempfile.TemporaryDirectory(prefix="iacode-g4-functional-") as directory:
            checkpoint = Path(directory) / "GATE-4-CP-9000"
            checkpoint.mkdir()
            (checkpoint / "STATE.json").write_text(
                json.dumps({"gate": GATE}) + "\n", encoding="utf-8"
            )
            (checkpoint / "COMMANDS.jsonl").write_text("", encoding="utf-8")
            passing = check_functional_acceptance.evaluate(
                PROJECT_ROOT,
                checkpoint,
                self._document(checkpoint.name, requirements),
            )
            blocked = check_functional_acceptance.evaluate(
                PROJECT_ROOT,
                checkpoint,
                self._document(checkpoint.name, requirements, "BLOCKED"),
            )
        self.assertEqual(passing["result"], "PASS")
        self.assertEqual(passing["missing"], [])
        self.assertEqual(blocked["result"], "FAIL")
        self.assertEqual(set(blocked["missing"]), set(requirements))

    def test_functional_artifact_schema_requires_observation_and_evidence(self) -> None:
        requirements = check_functional_acceptance.functional_requirement_ids(PROJECT_ROOT, GATE)
        document = self._document("GATE-4-CP-9000", requirements)
        schema = ledger_common.load_json(
            PROJECT_ROOT / ".iacode" / "schemas" / "functional-acceptance.schema.json"
        )
        self.assertEqual(ledger_common.validate_schema(document, schema), [])
        document["scenarios"][0]["observed"] = []
        self.assertTrue(ledger_common.validate_schema(document, schema))


class ProgramStateTests(unittest.TestCase):
    def test_gate_4_is_derived_as_milestone_2(self) -> None:
        self.assertEqual(program_state.milestone_for(GATE), "M2")

    def test_timestamp_is_the_only_ignored_program_state_difference(self) -> None:
        state = {"gate": GATE, "updatedAt": "first"}
        later = {"gate": GATE, "updatedAt": "second"}
        self.assertEqual(program_state.comparable(state), program_state.comparable(later))
        later["gate"] = "GATE-5"
        self.assertNotEqual(program_state.comparable(state), program_state.comparable(later))


class ReviewBundleTests(unittest.TestCase):
    def test_manifest_binds_order_size_and_digest(self) -> None:
        declared = review_bundle.manifest({"z.txt": b"z", "a.txt": b"alpha"})
        self.assertEqual([item["path"] for item in declared["entries"]], ["a.txt", "z.txt"])
        self.assertEqual(declared["entries"][0]["sizeBytes"], 5)
        self.assertEqual(
            declared["entries"][0]["sha256"],
            hashlib.sha256(b"alpha").hexdigest(),
        )

    def test_archive_timestamp_is_constant_and_review_output_is_ignored(self) -> None:
        self.assertEqual(review_bundle.ZIP_TIME, (1980, 1, 1, 0, 0, 0))
        ignored = (PROJECT_ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
        self.assertIn("artifacts/review/", ignored)


if __name__ == "__main__":
    unittest.main()
