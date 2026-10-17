"""Canonical Gate 6 scope/boundaries and causal controls; live facts are not replaced by fakes."""

from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import tomllib
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))

import ledger_common
import policies
from check_functional_acceptance import functional_requirement_ids

CHECKPOINT = ROOT / "docs/checkpoints/GATE-6-CP-0001"


def load_harness(name):
    spec = importlib.util.spec_from_file_location("gate6_" + name,
        CHECKPOINT / "audit-harness" / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_actor():
    spec = importlib.util.spec_from_file_location("gate6_live_actor",
        ROOT / "scripts/iacode/scenarios/experience_store_e2e.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Gate6SpecificationTests(unittest.TestCase):
    def test_retrospective_preserves_template_and_every_current_gate_lesson(self):
        import re

        template = (ROOT / ".iacode/templates/retrospective/TEMPLATE.md").read_text(encoding="utf-8")
        document = (ROOT / ".iacode/memory/retrospectives" / (CHECKPOINT.name + ".md")).read_text(encoding="utf-8")
        required = re.findall(r"^## .+$", template, flags=re.MULTILINE)
        self.assertTrue(required)
        self.assertEqual(re.findall(r"^## .+$", document, flags=re.MULTILINE), required)
        lessons = [json.loads(line) for line in (ROOT / ".iacode/memory/lessons.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
        current = [row for row in lessons if row["source"]["checkpoint"] == CHECKPOINT.name]
        self.assertTrue(current)
        for lesson in current:
            self.assertIn(lesson["lessonId"], document)
            for guard in lesson["guardrails"]:
                self.assertIn(guard, document)
        self.assertIn("does not predict a Gate verdict", document)
        self.assertIn("independent M2", document)

    def test_functional_denominator_covers_every_mandatory_runtime_criterion(self):
        rows = policies.canonical_requirements(ROOT, "GATE-6")
        expected = {"GATE-6-" + row["key"] for row in rows
                    if 2 <= int(row["key"].split(".")[0]) <= 7}
        self.assertEqual(len(expected), 37)
        self.assertEqual(set(functional_requirement_ids(ROOT, "GATE-6")), expected)

    def test_complete_checklist_registry_and_derived_set_agree(self):
        parsed = policies.parse_checklist((ROOT / "docs/GATE-6-CHECKLIST.md").read_text(encoding="utf-8"))
        self.assertEqual(len(parsed), 51)
        registry = json.loads((ROOT / ".iacode/policies/canonical-requirements.json").read_bytes())
        # Use the canonical lookup, not a second interpretation of the registry envelope.
        preflight = ledger_common.load_json(CHECKPOINT / "LESSON-PREFLIGHT.json")
        expected = policies.expected_requirement_refs(ROOT, "GATE-6", CHECKPOINT.name, preflight)
        matrix = json.loads((CHECKPOINT / "REQUIREMENTS-MATRIX.json").read_bytes())
        self.assertEqual({row["sourceRef"] for row in matrix["requirements"]}, set(expected))
        self.assertTrue(registry)

    def test_no_inherited_mandatory_gate_is_removed(self):
        state = json.loads((CHECKPOINT / "STATE.json").read_bytes())
        old = json.loads(subprocess.check_output(["git", "show",
            state["baseCommit"] + ":.iacode/policies/quality-gates.json"], cwd=ROOT))
        current = json.loads((ROOT / ".iacode/policies/quality-gates.json").read_bytes())
        old_ids = {row["id"] for row in old["gates"] if row["mandatory"]}
        current_ids = {row["id"] for row in current["gates"] if row["mandatory"]}
        self.assertTrue(old_ids | {"experienceTests"} <= current_ids)
        self.assertGreaterEqual(len(current_ids), len(old_ids) + 1)

    def test_new_counted_root_is_explicit_and_has_no_fixture_exclusion(self):
        suites = json.loads((ROOT / ".iacode/policies/test-suites.json").read_bytes())["suites"]
        rows = [row for row in suites if row["id"] == "experience"]
        self.assertEqual(len(rows), 1)
        self.assertTrue(rows[0]["counted"])
        self.assertEqual(rows[0]["root"], "services/experience/tests")
        self.assertNotIn("inputRepositories", rows[0])

    def test_current_scope_preserves_knowledge_and_training_reservations(self):
        current = ledger_common.load_json(ledger_common.resolve_latest(ROOT) / "STATE.json")["gate"]
        self.assertEqual(policies.scope_violations(ROOT, current), [])
        future = {row["path"] for row in policies.reservations_in_force(ROOT, "GATE-6")}
        self.assertTrue({"services/knowledge", "services/training", "datasets", "training", "evaluation"} <= future)
        self.assertNotIn("services/experience", future)


class Gate6BoundaryTests(unittest.TestCase):
    def test_domain_imports_only_stdlib_and_declared_shared_contracts(self):
        allowed = set(sys.stdlib_module_names) | {"iacode_common", "iacode_contracts", "pydantic",
                                                "iacode_experience", "__future__"}
        for path in (ROOT / "services/experience/src").rglob("*.py"):
            for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
                if isinstance(node, ast.Import):
                    modules = [row.name for row in node.names]
                elif isinstance(node, ast.ImportFrom) and node.level == 0:
                    modules = [node.module or ""]
                else:
                    continue
                for module in modules:
                    self.assertIn(module.partition(".")[0], allowed, str(path) + ": " + module)

    def test_library_has_no_production_memory_store_or_executor(self):
        for path in (ROOT / "services/experience/src").rglob("*.py"):
            classes = [node.name for node in ast.walk(ast.parse(path.read_text(encoding="utf-8")))
                       if isinstance(node, ast.ClassDef)]
            self.assertFalse(any(name.startswith(("Memory", "Fake", "Stub")) for name in classes))
        project = tomllib.loads((ROOT / "services/experience/pyproject.toml").read_text(encoding="utf-8"))["project"]
        self.assertEqual(set(project["dependencies"]), {
            "iacode-common==0.1.0", "iacode-contracts==0.1.0", "pydantic==2.13.5"})

    def test_schema_carries_all_categories_and_closed_objects(self):
        schema = json.loads((ROOT / ".iacode/schemas/experience.schema.json").read_bytes())
        categories = {"task", "environment", "provider", "model", "effort", "repository", "baseCommit",
            "trajectorySummary", "actions", "toolCalls", "commands", "files", "attempts", "failures",
            "corrections", "tests", "quality", "humanReview", "agentReview", "finalResult", "provenance",
            "trainingEligibility", "schemaVersion"}
        self.assertEqual(set(schema["properties"]), categories)
        self.assertEqual(set(schema["required"]), categories)
        self.assertIs(schema["additionalProperties"], False)
        for name, definition in schema["$defs"].items():
            if definition.get("type") == "object":
                self.assertIs(definition["additionalProperties"], False, name)
        for name in ("effort", "repository", "baseCommit", "humanReview", "agentReview"):
            self.assertEqual(schema["properties"][name]["type"], "null")

    def test_every_policy_limit_has_a_runtime_consumer(self):
        policy = json.loads((ROOT / ".iacode/policies/experience-policy.json").read_bytes())
        roots = [ROOT / "services/experience/src", ROOT / "apps/api/src/iacode_api/experience",
                 ROOT / "apps/api/src/iacode_api/routes/experiences.py"]
        attributes = set()
        for root in roots:
            for path in ([root] if root.is_file() else root.rglob("*.py")):
                attributes.update(node.attr for node in ast.walk(ast.parse(path.read_text(encoding="utf-8")))
                                  if isinstance(node, ast.Attribute))
        self.assertEqual(set(policy) - {"schemaVersion"} - attributes, set())
        self.assertGreaterEqual(policy["tombstoneRetentionSeconds"], policy["captureMaxAgeSeconds"])


class Gate6BookkeepingCausalTests(unittest.TestCase):
    def test_inherited_gate_assertion_accepts_growth_but_refuses_removal_or_optional_controls(self):
        from test_gate5_clients import Gate5QualityIntegrationTests

        case = Gate5QualityIntegrationTests(
            "test_every_inherited_gate_remains_and_clients_are_mandatory")
        assertion = case.test_every_inherited_gate_remains_and_clients_are_mandatory
        actual = policies.gate_definitions(ROOT)
        with mock.patch.object(policies, "gate_definitions", return_value={
                **actual, "futureRequired": {"mandatory": True}}):
            assertion()
        for name in actual:
            with self.subTest(optional=name), mock.patch.object(policies, "gate_definitions",
                    return_value={**actual, name: {**actual[name], "mandatory": False}}):
                with self.assertRaises(AssertionError):
                    assertion()
            if name == "experienceTests":
                continue  # The Gate6-specific inherited-policy test owns this additional control.
            with self.subTest(removed=name), mock.patch.object(policies, "gate_definitions",
                    return_value={key: value for key, value in actual.items() if key != name}):
                with self.assertRaises(AssertionError):
                    assertion()

    def test_repository_preflight_accepts_all_declared_filters_but_refuses_unexplained_omission(self):
        import test_development_ledger as inherited

        case = inherited.LessonPreflightTests(
            "test_the_repository_preflight_covers_every_applicable_lesson")
        assertion = case.test_the_repository_preflight_covers_every_applicable_lesson
        selectors = {"gates": ["GATE-6"], "scopes": ["independent-audit"],
                     "technologies": ["Python"], "modules": ["services/experience"]}
        with tempfile.TemporaryDirectory(prefix="iacode-gate6-preflight-selectors-") as raw:
            root = Path(raw)
            for dimension, values in selectors.items():
                applicability = {"gates": ["*"], "scopes": [], "technologies": [], "modules": []}
                applicability[dimension] = values
                inherited.save_lessons(root, [inherited.make_lesson(applicability=applicability)])
                with self.subTest(dimension=dimension), mock.patch.object(inherited, "PROJECT_ROOT", root):
                    assertion()
            inherited.save_lessons(root, [inherited.make_lesson()])
            with mock.patch.object(inherited, "PROJECT_ROOT", root):
                assertion()
                # A producer cannot hide an unfiltered active lesson even if it lies about count.
                with mock.patch.object(inherited, "build_preflight", return_value={
                        "lessonsApplicable": 0, "applicable": []}):
                    with self.assertRaises(AssertionError):
                        assertion()

    def test_local_handoff_renderer_preserves_the_complete_canonical_contract(self):
        from validate_checkpoint import HANDOFF_HEADINGS

        renderer = load_harness("assemble_source_ready")
        actual = renderer.render_handoff(renderer.local_handoff_sections())
        positions = [actual.index(heading) for heading in HANDOFF_HEADINGS]
        self.assertEqual(positions, sorted(positions))
        self.assertTrue(all(actual.count(heading) == 1 for heading in HANDOFF_HEADINGS))
        self.assertIn("Current Status: IN_PROGRESS", actual)
        self.assertIn("## Required next action", renderer.render_next("Continue the complete ordered internal Gate6 assurance."))

    def test_local_handoff_renderer_refuses_omitted_or_empty_sections_and_next_action(self):
        renderer = load_harness("assemble_source_ready")
        sections = renderer.local_handoff_sections()
        for heading in sections:
            with self.subTest(heading=heading):
                with self.assertRaises(ValueError):
                    renderer.render_handoff({key: value for key, value in sections.items() if key != heading})
                with self.assertRaises(ValueError):
                    renderer.render_handoff({**sections, heading: " "})
        with self.assertRaises(ValueError):
            renderer.render_next(" ")

    def test_authored_functional_map_cannot_omit_a_canonical_runtime_requirement(self):
        mapping = load_harness("complete_functional_acceptance").SCENARIOS
        actual = {"GATE-6-" + key for group in mapping.values()
                  for key in group["requirements"].split()}
        self.assertEqual(actual, set(functional_requirement_ids(ROOT, "GATE-6")))

    def test_current_producer_bytes_survive_actual_consumer_failure_and_owned_cleanup(self):
        publisher = load_harness("run_full_verification")
        with tempfile.TemporaryDirectory(prefix="iacode-gate6-raw-capture-") as raw:
            archive = Path(raw) / "retained"
            # A real consumer failure must leave exact original observations, not a Gate verdict.
            report_bytes = b'{\r\n  "result": "FAIL", "stages": []\r\n}\r\n'
            source_bytes = b'{\r\n  "result": "FAIL", "observed": "example"\r\n}\r\n'
            with self.assertRaisesRegex(RuntimeError, "stage"):
                with publisher.verification_directory() as owner:
                    clone = owner["path"] / "repository"
                    (clone / "var").mkdir(parents=True)
                    producer = clone / "full.json"
                    producer.write_bytes(report_bytes)
                    (clone / "var/experience-store-e2e.json").write_bytes(source_bytes)
                    publisher.collect_producer_observations(clone, producer, archive, "fixture")
            self.assertTrue(owner["removed"])
            self.assertFalse(clone.exists())
            manifest = json.loads(next(archive.glob("*-MANIFEST.json")).read_bytes())
            self.assertFalse(manifest["gateVerdictIssued"])
            self.assertEqual(manifest["refusedReports"], [])
            expected = {"full.json": report_bytes, "experience-store-e2e.json": source_bytes}
            self.assertEqual({row["producerName"] for row in manifest["reports"]}, set(expected))
            for row in manifest["reports"]:
                content = (archive / row["archive"]).read_bytes()
                self.assertEqual(content, expected[row["producerName"]])
                self.assertEqual(hashlib.sha256(content).hexdigest(), row["sha256"])
                self.assertEqual(len(content), row["bytes"])

    def test_current_producer_capture_refuses_unsafe_bytes_without_losing_neutral_inventory(self):
        publisher = load_harness("run_full_verification")
        with tempfile.TemporaryDirectory(prefix="iacode-gate6-unsafe-producer-") as raw:
            directory = Path(raw)
            clone = directory / "repository"
            clone.mkdir()
            producer = clone / "full.json"
            producer.write_text('{"value":"API_' + 'KEY=' + "a" * 64 + '"}', encoding="utf-8")
            archive = directory / "retained"
            with self.assertRaisesRegex(RuntimeError, "unsafe"):
                publisher.capture_producer_reports(clone, producer, archive, "fixture")
            files = list(archive.iterdir())
            self.assertEqual(len(files), 1)
            manifest = json.loads(files[0].read_bytes())
            self.assertFalse(manifest["gateVerdictIssued"])
            self.assertEqual(manifest["reports"], [])
            self.assertEqual(manifest["refusedReports"][0]["reason"], "SECRET_MATERIAL")

    def test_actual_child_completion_precedes_next_phase(self):
        harness = load_harness("validate_serial_bookkeeping")
        with tempfile.TemporaryDirectory(prefix="iacode-gate6-serial-") as raw:
            directory = Path(raw)
            first = directory / "first.py"
            second = directory / "second.py"
            first.write_text("import pathlib,time\ntime.sleep(.15)\npathlib.Path('finished').write_text('done')\n", encoding="utf-8")
            second.write_text("import pathlib\nassert pathlib.Path('finished').read_text() == 'done'\npathlib.Path('observed').write_text('after-completion')\n", encoding="utf-8")
            self.assertEqual(harness.run_sequence([[sys.executable, str(first)],
                                                   [sys.executable, str(second)]], directory), 0)
            self.assertEqual((directory / "observed").read_text(), "after-completion")

    def test_actual_failed_child_stops_before_another_writer(self):
        harness = load_harness("validate_serial_bookkeeping")
        with tempfile.TemporaryDirectory(prefix="iacode-gate6-stop-") as raw:
            directory = Path(raw)
            first, second = directory / "first.py", directory / "second.py"
            first.write_text("raise SystemExit(7)\n", encoding="utf-8")
            second.write_text("import pathlib\npathlib.Path('forbidden').write_text('wrong')\n", encoding="utf-8")
            self.assertEqual(harness.run_sequence([[sys.executable, str(first)],
                                                   [sys.executable, str(second)]], directory), 7)
            self.assertFalse((directory / "forbidden").exists())

    def test_actual_captured_output_hashes_and_git_attributes_preserve_bytes(self):
        reports = list((CHECKPOINT / "suite-attempts").glob("*.json"))
        self.assertTrue(reports)
        for path in reports:
            report = json.loads(path.read_bytes())
            artifact = report.get("safeOutputArtifact")
            if not artifact:
                continue
            observed = report if "outputSha256" in report else report["commands"][-1]
            payload = (ROOT / artifact).read_bytes()
            self.assertEqual(hashlib.sha256(payload).hexdigest(), observed["outputSha256"])
            self.assertEqual(len(payload), observed["outputBytes"])
            attributes = subprocess.check_output(["git", "check-attr", "text", "--", artifact], cwd=ROOT).decode()
            self.assertTrue(attributes.strip().endswith(": unset"), attributes)


class Gate6LiveProducerControls(unittest.TestCase):
    def test_real_import_failure_retires_a_stale_pass_before_project_imports(self):
        with tempfile.TemporaryDirectory(prefix="iacode-gate6-import-failure-") as raw:
            root = Path(raw)
            target = root / "scripts/iacode/scenarios/experience_store_e2e.py"
            target.parent.mkdir(parents=True)
            target.write_bytes((ROOT / "scripts/iacode/scenarios/experience_store_e2e.py").read_bytes())
            report = root / "var/experience-store-e2e.json"
            report.parent.mkdir()
            report.write_text('{"result":"PASS"}\n', encoding="utf-8")
            child = subprocess.run([sys.executable, "-I", "-S", str(target)], cwd=root,
                capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
            self.assertNotEqual(child.returncode, 0)
            self.assertIn("ModuleNotFoundError", child.stderr)
            self.assertFalse(report.exists())

    def test_actor_help_is_an_actual_cold_stdlib_host_probe(self):
        child = subprocess.run([sys.executable, "-I", "-S",
            "scripts/iacode/scenarios/experience_store_e2e.py", "--help"], cwd=ROOT,
            capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
        self.assertEqual(child.returncode, 0, child.stderr)
        self.assertIn("--report", child.stdout)

    def test_actor_consumes_the_actual_public_success_envelope(self):
        actor = load_actor()
        value = {"snapshotId": "observed-id", "trainingAllowed": False}
        envelope = {"version": actor.PROTOCOL["version"], "operation": "snapshot", "data": value}
        with mock.patch.object(actor, "protocol_operation", return_value=(200, envelope)):
            self.assertEqual(actor.operation("http://127.0.0.1", "decision-fixture", "snapshot", {}),
                             (200, value))
        with mock.patch.object(actor, "protocol_operation", return_value=(200, value)):
            with self.assertRaises(actor.StackError):
                actor.operation("http://127.0.0.1", "decision-fixture", "snapshot", {})

    def test_control_facts_cannot_override_the_observed_result(self):
        actor = load_actor()
        report = {"steps": []}
        actor.record(report, "valid-null-control", True, count=1)
        self.assertEqual(report["steps"][0]["result"], "PASS")
        with self.assertRaises(ValueError):
            actor.record(report, "forged-control", False, result="PASS")
        self.assertEqual(len(report["steps"]), 1)

    def test_privileged_object_actor_refuses_an_operational_namespace_before_io(self):
        actor = load_actor()
        with mock.patch.dict(actor.os.environ, {"COMPOSE_PROJECT_NAME": "iacode"}), mock.patch.object(
                actor, "compose", side_effect=AssertionError("no operational IO allowed")) as engine:
            with self.assertRaises(actor.StackError):
                actor.source_adversary("00000000-0000-4000-8000-000000000001", "corrupt")
            engine.assert_not_called()


if __name__ == "__main__":
    unittest.main()
