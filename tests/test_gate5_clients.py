"""Gate 5 integration controls. Historical fixtures and live state have different owners."""

from __future__ import annotations

import runpy
import os
import ast
import sys
import json
import tempfile
import subprocess
import shutil
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))
sys.path.insert(0, str(ROOT / "scripts/iacode"))

import ledger_common  # noqa: E402
import policies  # noqa: E402
import secret_scan  # noqa: E402


class Gate5EnvironmentLiteralTests(unittest.TestCase):
    def test_host_literal_reader_matches_actual_compose_and_placeholder_semantics(self) -> None:
        from compose import read_env_file
        from iacode_common.redaction import is_placeholder

        cases = (
            "", '""', "''", '"example"', "'example'",
            '"not-placeholder"', "'not-placeholder'",
            r'"line\nnext"', r"'line\nnext'", r'"a\"b"', r"'a\'b'",
            "plain # comment", '"literal # content" # comment',
        )
        with tempfile.TemporaryDirectory(prefix="iacode-literal-control-") as temporary:
            directory = Path(temporary)
            env_file = directory / ".env"
            environment = dict(os.environ)
            environment.pop("IACODE_LITERAL_PROBE", None)
            for literal in cases:
                with self.subTest(literal=literal):
                    env_file.write_text("IACODE_LITERAL_PROBE=" + literal + "\n", encoding="utf-8")
                    rendered = subprocess.run(
                        ["docker", "compose", "--project-name", "iacode-literal-control",
                         "--project-directory", str(directory), "--env-file", str(env_file),
                         "--file", "-", "config", "--format", "json"],
                        input="services:\n  probe:\n    image: busybox:1.37.0\n"
                              "    environment:\n      IACODE_LITERAL_PROBE: $"
                              "{IACODE_LITERAL_PROBE}\n",
                        env=environment, capture_output=True, text=True, encoding="utf-8",
                        errors="strict", check=True,
                    )
                    actual = json.loads(rendered.stdout)["services"]["probe"]["environment"][
                        "IACODE_LITERAL_PROBE"]
                    host = read_env_file(env_file, {})["IACODE_LITERAL_PROBE"]
                    self.assertEqual(host, actual)
                    self.assertEqual(is_placeholder(host), actual in ("", "example"))

    def test_malformed_quoted_env_literals_fail_closed_without_exposing_content(self) -> None:
        from compose import StackError, read_env_file

        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / ".env"
            for literal in ('"unclosed-literal', "'unclosed-literal", '"literal" trailing'):
                with self.subTest(literal=literal):
                    path.write_text("IACODE_LITERAL_PROBE=" + literal + "\n", encoding="utf-8")
                    with self.assertRaises(StackError) as refused:
                        read_env_file(path, {})
                    self.assertNotIn(literal, str(refused.exception))

    def test_process_environment_overlays_are_values_not_dotenv_tokens(self) -> None:
        from compose import read_env_file

        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / ".env"
            path.write_text("IACODE_LITERAL_PROBE='example'\n", encoding="utf-8")
            value = '"not-placeholder"'
            observed = read_env_file(path, {
                "IACODE_LITERAL_PROBE": value, "IACODE_UNDECLARED_PROBE": "not-inherited",
            })
            self.assertEqual(observed, {"IACODE_LITERAL_PROBE": value})


class Gate5TransitionTests(unittest.TestCase):
    def test_historical_gate4_controls_keep_their_owning_gate(self) -> None:
        with mock.patch.object(ledger_common, "delivered_gate", return_value="GATE-6"):
            module = runpy.run_path(str(ROOT / "tests/test_gate4_quality_engine.py"))
        self.assertEqual(module["CURRENT_GATE"], "GATE-6")
        self.assertEqual(module["GATE"], module["SPECIFICATION"].stem.removesuffix("-CHECKLIST"))
        self.assertNotEqual(module["GATE"], module["CURRENT_GATE"])
        suite = unittest.TestSuite([
            module["Gate4CanonicalSpecificationTests"]("test_the_registry_mirrors_the_specification_row_for_row"),
            module["Gate4CanonicalSpecificationTests"]("test_a_dropped_registry_row_is_refused"),
            module["FunctionalAcceptanceTests"]("test_functional_scope_is_derived_from_the_canonical_gate"),
            module["ProgramStateTests"]("test_timestamp_is_the_only_ignored_program_state_difference"),
        ])
        result = unittest.TestResult()
        suite.run(result)
        self.assertEqual(result.testsRun, 4)
        self.assertTrue(result.wasSuccessful(), result.errors + result.failures)

    def test_scope_controls_evaluate_the_live_tree_with_current_gate(self) -> None:
        with mock.patch.object(ledger_common, "delivered_gate", return_value="GATE-6"):
            module = runpy.run_path(str(ROOT / "tests/test_gate4_quality_engine.py"))
        with mock.patch.object(policies, "scope_violations", return_value=[]) as check:
            module["Gate4InitialScopeTests"](
                "test_the_evaluator_reservation_is_consumed_and_later_scope_is_clean",
            ).test_the_evaluator_reservation_is_consumed_and_later_scope_is_clean()
        check.assert_called_once_with(ROOT, "GATE-6")

    def test_wrong_historical_selector_is_observed_by_the_unchanged_assertion(self) -> None:
        module = runpy.run_path(str(ROOT / "tests/test_gate4_quality_engine.py"))
        case = module["FunctionalAcceptanceTests"]("test_functional_scope_is_derived_from_the_canonical_gate")
        with mock.patch.dict(case.test_functional_scope_is_derived_from_the_canonical_gate.__globals__,
                             {"GATE": ledger_common.delivered_gate(ROOT)}):
            with self.assertRaises(AssertionError):
                case.test_functional_scope_is_derived_from_the_canonical_gate()


class Gate5DocumentationTests(unittest.TestCase):
    def test_current_provenance_is_validated_by_its_own_artifact_schema(self) -> None:
        from copy import deepcopy

        checkpoint = ledger_common.resolve_latest(ROOT)
        document = json.loads((checkpoint / "PROVENANCE.json").read_text(encoding="utf-8"))
        schema = json.loads((ROOT / ".iacode/schemas/provenance.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(ledger_common.validate_schema(document, schema), [])
        for invalid in (None, {}, [], False, 17):
            adverse = deepcopy(document)
            adverse["artifacts"][-1]["model"] = invalid
            errors = ledger_common.validate_schema(adverse, schema)
            if errors:
                break
        self.assertTrue(errors, "the artifact schema must reject an unsupported model field type")
        self.assertTrue(any(".model" in error for error in errors))

    def test_live_delivery_status_is_delegated_instead_of_hardcoded_in_rollups(self) -> None:
        import re

        def stale_lifecycle(text: str) -> bool:
            return bool(re.search(r"\b(?:in progress|partial adapters|not yet an accepted)\b", text, re.I))

        for relative in ("START-HERE.md", "docs/ARCHITECTURE.md"):
            with self.subTest(document=relative):
                header = "\n".join((ROOT / relative).read_text(encoding="utf-8").splitlines()[:15])
                self.assertFalse(stale_lifecycle(header), "live closure status belongs to LATEST, not a frozen overview")
                self.assertIn("checkpoints/LATEST.md", header)
                self.assertTrue(stale_lifecycle(header + "\nCurrent delivery is in progress; partial adapters."))

    def test_architecture_rollup_does_not_deny_its_delivered_quality_engine(self) -> None:
        text = (ROOT / "docs/ARCHITECTURE.md").read_text(encoding="utf-8")
        rollup = text.split("## Current state", 1)[1].split("## Control plane", 1)[0]
        self.assertTrue((ROOT / "services/evaluator/src/iacode_evaluator/service.py").is_file())
        self.assertIn("Quality Engine", rollup)
        self.assertNotIn("No quality runtime", rollup)
        self.assertIn("## The Quality Engine", text)


class Gate5SecretReviewTests(unittest.TestCase):
    def test_every_current_changed_path_uses_the_strict_detector_including_checkpoint_harnesses(self) -> None:
        checkpoint = ledger_common.resolve_latest(ROOT)
        base = json.loads((checkpoint / "STATE.json").read_text(encoding="utf-8"))["baseCommit"]
        paths = set()
        for arguments in (("diff", "--name-only", base), ("ls-files", "--others", "--exclude-standard")):
            observed = subprocess.run(["git", *arguments], cwd=ROOT, text=True, encoding="utf-8",
                                      capture_output=True, check=True)
            paths.update(observed.stdout.splitlines())
        self.assertTrue(paths)
        for relative in sorted(paths):
            target = ROOT / relative
            if not target.is_file():
                continue
            try:
                text = target.read_text(encoding="utf-8")
            except UnicodeError:
                continue  # Same text boundary as the checkpoint; no publication allowances.
            with self.subTest(path=relative):
                self.assertEqual(ledger_common.find_secrets(text), [], relative)

    def test_strict_checkpoint_sources_do_not_rely_on_publication_allowances(self) -> None:
        paths = ("apps/api/src/iacode_api/config.py", "apps/api/src/iacode_api/middleware/desktop_auth.py",
                 "apps/api/tests/unit/test_desktop_api.py", "apps/cli/src/client.cjs",
                 "services/orchestrator/src/iacode_orchestrator/config.py", "infra/compose/.env.example")
        for path in paths:
            with self.subTest(path=path):
                self.assertEqual(ledger_common.find_secrets((ROOT / path).read_text(encoding="utf-8")), [])
        adverse = "desktop_" + "token='" + "a" * 64 + "'"
        self.assertTrue(ledger_common.find_secrets(adverse))

    def test_reviewed_digest_does_not_exempt_a_different_value(self) -> None:
        tree = ast.parse((ROOT / "apps/api/src/iacode_api/config.py").read_text(encoding="utf-8"))
        field = next(node for node in ast.walk(tree) if isinstance(node, ast.AnnAssign)
                     and isinstance(node.target, ast.Name) and node.target.id == "database_url")
        url = next(keyword.value.value for keyword in field.value.keywords if keyword.arg == "default")
        scheme, rest = url.split("://", 1)
        authority, target = rest.split("@", 1)
        user = authority.partition(":")[0]
        adverse = scheme + "://" + user + ":" + "a" * 64 + "@" + target
        allowance = secret_scan.load_allowlist(ROOT)
        positive = secret_scan.scan_text(url, allowance)
        self.assertTrue(positive)
        self.assertTrue(all(item[2] for item in positive))
        combined = secret_scan.scan_text(url + "\n" + adverse, allowance)
        self.assertTrue(any(item[2] for item in combined))
        self.assertTrue(any(not item[2] for item in combined))

    def test_publication_review_never_waives_runtime_output_detection(self) -> None:
        from iacode_common.secret_scanning import find_secret_kinds

        annotation = "desktop_" + "token" + ": " + "Secret" + "Str"
        self.assertTrue(find_secret_kinds(annotation))


class Gate5SpecificationTests(unittest.TestCase):
    def test_canonical_gate5_rows_are_derived_from_the_full_specification(self) -> None:
        rows = policies.canonical_requirements(ROOT, "GATE-5")
        self.assertEqual(len(rows), 50)
        self.assertTrue(all(row["mandatory"] for row in rows))
        self.assertEqual(policies.gate_specification(ROOT, "GATE-5"), "docs/GATE-5-CHECKLIST.md")


class Gate5QualityIntegrationTests(unittest.TestCase):
    def test_exact_byte_evidence_survives_git_transport_and_detects_normalization(self) -> None:
        policy = (ROOT / ".gitattributes").read_bytes()
        relative = "docs/checkpoints/GATE-5-CP-0001/DESKTOP-LIVE.json"
        payload = b'{\r\n  "result": "PASS"\r\n}\r\n'
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = root / relative
            path.parent.mkdir(parents=True)
            path.write_bytes(payload)
            attributes = root / ".gitattributes"
            attributes.write_bytes(policy)

            def git(*arguments: str) -> bytes:
                return subprocess.run(["git", *arguments], cwd=root, check=True,
                                      capture_output=True).stdout

            git("init", "--quiet")
            git("config", "core.autocrlf", "true")
            git("add", ".gitattributes", relative)
            self.assertEqual(git("show", ":" + relative), payload,
                             "exact observed evidence bytes must survive Git export")
            for name in (relative, "docs/checkpoints/FUTURE/attempts/RED.json",
                         "docs/checkpoints/FUTURE/HARDENED-GATEWAY.json"):
                self.assertEqual(git("check-attr", "text", "--", name).decode().strip(),
                                 name + ": text: unset")
            # The negative control performs real Git conversion, not an invented report.
            attributes.write_bytes(b"* text=auto\n*.json text eol=lf\n")
            git("add", ".gitattributes")
            git("add", "--renormalize", relative)
            self.assertNotEqual(git("show", ":" + relative), payload)
            attributes.write_bytes(policy)
            git("add", ".gitattributes")
            git("add", "--renormalize", relative)
            self.assertEqual(git("show", ":" + relative), payload)

    def test_commonjs_and_esm_exports_have_explicit_lf_attributes(self) -> None:
        for name in ("apps/cli/bin/iacode.cjs", "future-entry.mjs"):
            result = subprocess.run(["git", "check-attr", "eol", "--", name], cwd=ROOT,
                                    text=True, encoding="utf-8", errors="replace",
                                    capture_output=True, check=True)
            self.assertEqual(result.stdout.strip(), name + ": eol: lf")

    def test_builder_refuses_a_crlf_executable_instead_of_shipping_a_broken_linux_shebang(self) -> None:
        import build_clients

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "entry.cjs"
            source.write_bytes(b"#!/usr/bin/env node\r\nconsole.log('clean');\r\n")
            with mock.patch.object(build_clients, "ROOT", root):
                with self.assertRaisesRegex(ValueError, "LF"):
                    build_clients.source_bytes({"bin/entry.cjs": "entry.cjs"})

    def test_full_verification_keeps_old_stages_and_requires_both_native_and_live_clients(self) -> None:
        import verify

        full = verify.build_stages(False)
        fast = verify.build_stages(True)
        expected = {"native-client-installation", "desktop-client-e2e", "gate:clientTests"}
        self.assertTrue(expected <= {stage.name for stage in full})
        self.assertTrue(expected <= {stage.name for stage in fast})
        self.assertTrue({"quality-pass", "quality-fail", "quality-iacode", "quality-false-pass",
                         "sandbox-coding", "gateway-smoke", "fresh-install", "restart"} <= {stage.name for stage in full})
        hardened = verify.verification_environment(ROOT, {"IACODE_DESKTOP_TOKEN": "not a configured credential",
                                                        "IACODE_DESKTOP_TOKEN_EXPIRES_AT": "unexpected"})
        self.assertEqual(hardened["IACODE_DESKTOP_TOKEN"], "")
        self.assertEqual(hardened["IACODE_DESKTOP_TOKEN_EXPIRES_AT"], "")

    def test_root_lint_scope_is_versioned_and_current_downgrades_are_refused(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.assertEqual(ledger_common.assurance_root_files(root), ())
            self.assertFalse(ledger_common.in_assurance_scope("ruff.toml"))
            with self.assertRaisesRegex(ledger_common.LedgerError, "requires"):
                ledger_common.assurance_root_files(root, required=True)
            policy = root / ".iacode/policies/assurance-scope.json"
            policy.parent.mkdir(parents=True)
            document = {"schemaVersion": "1.0.0", "additionalRootFiles": [".gitignore", "ruff.toml"]}
            policy.write_text(json.dumps(document), encoding="utf-8")
            for filename in ledger_common.assurance_root_files(root, required=True):
                self.assertTrue(ledger_common.in_assurance_scope(filename, (".gitignore", "ruff.toml")))
            document["additionalRootFiles"].remove("ruff.toml")
            policy.write_text(json.dumps(document), encoding="utf-8")
            with self.assertRaisesRegex(ledger_common.LedgerError, "narrowed"):
                ledger_common.assurance_root_files(root)
        self.assertEqual(ledger_common.assurance_root_files(ROOT, required=True), (".gitignore", "ruff.toml"))

    def test_every_inherited_gate_remains_and_clients_are_mandatory(self) -> None:
        gates = policies.gate_definitions(ROOT)
        inherited = {"tests", "staticAnalysis", "lessons", "integrity", "checkpointValidation",
                          "apiTests", "gatewayTests", "agentRuntimeTests", "sandboxTests", "evaluatorTests",
                          "webTests", "lint", "infraDefinition", "clientTests"}
        # These are the inherited minimum, not a ceiling on later mandatory gates.
        self.assertTrue(inherited <= set(gates), inherited - set(gates))
        self.assertTrue(all(gate["mandatory"] for gate in gates.values()))

    def test_native_suites_are_declared_and_never_invent_a_python_denominator(self) -> None:
        suites = {suite["id"]: suite for suite in policies.load_test_suites(ROOT)}
        for name in ("cli", "editor", "editor-host"):
            self.assertFalse(suites[name]["counted"])
            self.assertTrue(suites[name]["notCountedReason"])
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            directory = root / ".iacode/policies"
            directory.mkdir(parents=True)
            for version in ("1.0.0", "1.1.0"):
                (directory / "test-suites.json").write_text(json.dumps({"schemaVersion": version,
                    "suites": [suites["cli"]]}), encoding="utf-8")
                with self.assertRaisesRegex(ledger_common.LedgerError, "version"):
                    policies.load_test_suites(root)
            invalid = {**suites["cli"], "counted": True}
            (directory / "test-suites.json").write_text(json.dumps({"schemaVersion": "1.2.0",
                "suites": [invalid]}), encoding="utf-8")
            with self.assertRaisesRegex(ledger_common.LedgerError, "static count"):
                policies.load_test_suites(root)


class Gate5ClientRecoveryGuardTests(unittest.TestCase):
    def test_editor_preview_binding_uses_workspace_identity_not_path_spelling(self) -> None:
        from client_checks import run_node

        result = run_node(guard="native-root")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("# pass 1", result.stdout)
        self.assertIn("ok 1 - DesktopSnapshotTests: canonical filesystem spelling", result.stdout)

    def test_signed_malformed_mutation_keeps_uncertainty_identity_and_one_effect(self) -> None:
        from client_checks import run_node

        result = run_node(guard=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("# pass 1", result.stdout)
        self.assertIn("ok 1 - DesktopRecoveryTests: a signed malformed mutation result", result.stdout)
        self.assertNotIn("# pass 0", result.stdout)


class Gate5VerificationCollectorTests(unittest.TestCase):
    def test_bookkeeping_sequence_awaits_each_recorder_and_keeps_canonical_order(self) -> None:
        module = runpy.run_path(str(
            ROOT / "docs/checkpoints/GATE-5-CP-0001/audit-harness/validate_serial_bookkeeping.py"))
        commands = module["bookkeeping_commands"]()
        self.assertEqual(len(commands), 2)
        self.assertTrue(commands[0][-1].endswith("/audit-harness/declare_inventory.py"))
        self.assertTrue(commands[1][-1].endswith("/audit-harness/run_checkpoint_validation.py"))
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            first = ("from pathlib import Path; import time; time.sleep(0.2); "
                     "Path('receipt').write_text('complete')")
            second = ("from pathlib import Path; assert Path('receipt').read_text() == 'complete'; "
                      "Path('validated').touch()")
            self.assertEqual(module["run_sequence"]([
                [sys.executable, "-c", first], [sys.executable, "-c", second],
            ], directory), 0)
            self.assertTrue((directory / "validated").is_file())

    def test_bookkeeping_sequence_never_validates_after_inventory_recorder_failure(self) -> None:
        module = runpy.run_path(str(
            ROOT / "docs/checkpoints/GATE-5-CP-0001/audit-harness/validate_serial_bookkeeping.py"))
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            self.assertEqual(module["run_sequence"]([
                [sys.executable, "-c", "raise SystemExit(7)"],
                [sys.executable, "-c", "from pathlib import Path; Path('must-not-run').touch()"],
            ], directory), 7)
            self.assertFalse((directory / "must-not-run").exists())

    @staticmethod
    def publisher():
        return runpy.run_path(str(
            ROOT / "docs/checkpoints/GATE-5-CP-0001/audit-harness/run_full_verification.py"))

    @staticmethod
    def producer():
        from verify import build_stages

        return {"result": "PASS", "stages": [
            {"name": stage.name, "result": "PASS", "status": "FAIL"}
            for stage in build_stages(False)
        ]}

    def test_current_summary_derives_exact_vocabulary_and_ignores_noncanonical_alias(self) -> None:
        from types import SimpleNamespace

        module = self.publisher()
        summarize = module["summarize_stages"]
        producer = self.producer()
        count = len(producer["stages"])
        self.assertEqual(summarize(producer), (count, count, 0))
        producer["stages"].append({"name": "future-fixture", "result": "PASS", "status": "FAIL"})
        stages = [SimpleNamespace(name=row["name"]) for row in producer["stages"]]
        with mock.patch.dict(summarize.__globals__, {"build_stages": lambda fast: stages}):
            self.assertEqual(summarize(producer), (count + 1, count + 1, 0))

    def test_current_summary_refuses_missing_duplicate_reordered_or_unknown_results(self) -> None:
        from copy import deepcopy

        summarize = self.publisher()["summarize_stages"]
        original = self.producer()
        mutations = []
        missing = deepcopy(original)
        missing["stages"].pop()
        mutations.append(missing)
        duplicate = deepcopy(original)
        duplicate["stages"].append(deepcopy(duplicate["stages"][0]))
        mutations.append(duplicate)
        reordered = deepcopy(original)
        reordered["stages"][0], reordered["stages"][1] = reordered["stages"][1], reordered["stages"][0]
        mutations.append(reordered)
        for field, value in (("name", "unknown-fixture"), ("result", "UNKNOWN"), ("result", None)):
            adverse = deepcopy(original)
            adverse["stages"][0][field] = value
            mutations.append(adverse)
        contradiction = deepcopy(original)
        contradiction["stages"][0]["result"] = "FAIL"
        mutations.append(contradiction)
        for index, adverse in enumerate(mutations):
            with self.subTest(mutation=index), self.assertRaises(RuntimeError):
                summarize(adverse)
        valid_failure = deepcopy(original)
        valid_failure["result"] = "FAIL"
        valid_failure["stages"][0]["result"] = "FAIL"
        self.assertEqual(summarize(valid_failure),
                         (len(original["stages"]), len(original["stages"]) - 1, 1))

    def test_raw_reports_survive_real_postprocessing_exception_and_owned_cleanup(self) -> None:
        import hashlib

        module = self.publisher()
        collect = module["collect_producer_observations"]
        with tempfile.TemporaryDirectory() as outer:
            archive = Path(outer) / "archives"
            producer = self.producer()
            producer["stages"].pop()
            raw = (json.dumps(producer, indent=2) + "\n").replace("\n", "\r\n").encode()
            component = b'{\r\n  "observation": "example"\r\n}\r\n'
            with self.assertRaisesRegex(RuntimeError, "stage"):
                with module["verification_directory"]() as owner:
                    owned = owner["path"]
                    clone = owned / "repository"
                    (clone / "var").mkdir(parents=True)
                    report = clone / "full.json"
                    report.write_bytes(raw)
                    (clone / "var/desktop-e2e.json").write_bytes(component)
                    collect(clone, report, archive, "fixture-subject")
            self.assertFalse(owned.exists())
            manifests = list(archive.glob("*-MANIFEST.json"))
            self.assertEqual(len(manifests), 1)
            manifest = manifests[0]
            document = json.loads(manifest.read_text(encoding="utf-8"))
            self.assertFalse(document["gateVerdictIssued"])
            self.assertEqual(len(document["reports"]), 2)
            expected = {"full.json": raw, "desktop-e2e.json": component}
            for row in document["reports"]:
                preserved = (archive / row["archive"]).read_bytes()
                self.assertEqual(preserved, expected[row["producerName"]])
                self.assertEqual(hashlib.sha256(preserved).hexdigest(), row["sha256"])
                self.assertEqual(len(preserved), row["bytes"])

    def test_raw_capture_refuses_secret_material_but_retains_neutral_failure_inventory(self) -> None:
        capture = self.publisher()["capture_producer_reports"]
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            clone, archive = root / "repository", root / "archives"
            clone.mkdir()
            report = clone / "full.json"
            report.write_text('{"observation":"API_' + 'KEY=' + "a" * 64 + '"}', encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "unsafe"):
                capture(clone, report, archive, "fixture-subject")
            manifests = list(archive.glob("*-MANIFEST.json"))
            self.assertEqual(len(manifests), 1)
            document = json.loads(manifests[0].read_text(encoding="utf-8"))
            self.assertFalse(document["gateVerdictIssued"])
            self.assertEqual(document["reports"], [])
            self.assertEqual(document["refusedReports"][0]["reason"], "SECRET_MATERIAL")
            self.assertEqual(list(archive.iterdir()), manifests)


class Gate5NativeInstallationTests(unittest.TestCase):
    def test_verification_clone_cleanup_handles_real_readonly_git_objects(self) -> None:
        import importlib.util
        import stat

        script = ROOT / "docs/checkpoints/GATE-5-CP-0001/audit-harness/run_full_verification.py"
        specification = importlib.util.spec_from_file_location("gate5_owned_clone_probe", script)
        module = importlib.util.module_from_spec(specification)
        specification.loader.exec_module(module)
        # An outer standard-library temporary owner removes any causal-red residue.
        with tempfile.TemporaryDirectory(prefix="iacode-readonly-regression-") as temporary:
            with mock.patch("tempfile.gettempdir", return_value=temporary):
                with module.verification_directory() as owner:
                    directory = owner["path"]
                    pack = directory / "repository/.git/objects/pack/observed.idx"
                    pack.parent.mkdir(parents=True)
                    pack.write_bytes(b"owned read-only Git object fixture")
                    pack.chmod(stat.S_IREAD)
                self.assertTrue(owner["removed"])
                self.assertFalse(directory.exists())
                with self.assertRaises(TypeError):
                    module.verification_directory(Path(temporary))

    def test_cleanup_membership_derives_every_canonical_active_state_including_running(self) -> None:
        import desktop_test_support as probe

        source = ROOT / "packages/contracts/src/iacode_contracts/sandbox.py"
        tree = ast.parse(source.read_text(encoding="utf-8"))
        declaration = next(row for row in tree.body if isinstance(row, ast.AnnAssign)
                           and row.target.id == "SANDBOX_ACTIVE_SESSION_STATES")
        states = ast.literal_eval(declaration.value)
        predicate = probe.active_session_predicate()
        self.assertEqual(predicate, "state IN (" + ",".join(repr(value) for value in states) + ")")
        self.assertIn("'RUNNING'", predicate)
        self.assertNotIn("BUSY", states)
        self.assertNotEqual(set(states), {"CREATING", "READY", "BUSY", "RECOVERING"})
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = root / "packages/contracts/src/iacode_contracts/sandbox.py"
            target.parent.mkdir(parents=True)
            target.write_text("SANDBOX_ACTIVE_SESSION_STATES: tuple = " + repr((*states, "NEW_ACTIVE")), encoding="utf-8")
            with mock.patch.object(probe, "REPOSITORY_ROOT", root):
                self.assertIn("'NEW_ACTIVE'", probe.active_session_predicate())

    def test_forgery_premise_joins_public_request_ids_to_actual_successful_sandbox_executions(self) -> None:
        module = runpy.run_path(str(ROOT / "scripts/iacode/scenarios/desktop_e2e.py"))
        tree = ast.parse((ROOT / "packages/contracts/src/iacode_contracts/agent_runtime.py").read_text(encoding="utf-8"))
        public = next(row for row in tree.body if isinstance(row, ast.ClassDef) and row.name == "ToolRequestView")
        fields = {row.target.id for row in public.body if isinstance(row, ast.AnnAssign)}
        self.assertNotIn("executor", fields)
        requests = [{"toolRequestId": identity, "name": "shell.exec", "status": "RESOLVED",
                     "createdAt": "2026-10-16T00:00:00Z"} for identity in ("external", "executed")]
        self.assertTrue(all(set(row) <= fields for row in requests))
        detail = {"toolRequests": requests, "toolExecutions": [
            {"toolRequestId": "executed", "status": "SUCCEEDED", "sandboxSession": "owned-session"}]}
        self.assertEqual(module["executed_sandbox_request"](detail)["toolRequestId"], "executed")
        with self.assertRaises(KeyError):
            next(row for row in requests if row["executor"] == "SANDBOX")
        detail["toolExecutions"] = []
        with self.assertRaisesRegex(module["StackError"], "actual successful"):
            module["executed_sandbox_request"](detail)

    def test_fresh_catalog_requires_sync_and_the_exact_authorized_model_without_substitution(self) -> None:
        import desktop_test_support as probe

        success = (200, {"outcomes": [{"provider": "fixture", "added": 1, "updated": 0,
                                      "unchanged": 0, "errors": []}]})
        listed = (200, {"models": [{"provider": "fixture", "model": "authorized", "active": True}]})
        with mock.patch.object(probe, "request", side_effect=[success, listed]) as sent:
            result = probe.synchronize_authorized_model("http://127.0.0.1:12345", "fixture credential", "fixture:authorized")
            self.assertEqual(result["authorizedModel"], "fixture:authorized")
            self.assertEqual(sent.call_count, 2)
            self.assertEqual(sent.call_args_list[0].args[2:], ("POST", "/api/v1/gateway/models/sync", {"provider": "fixture"}))
        with mock.patch.object(probe, "request", side_effect=[success, (200, {"models": []})]) as sent:
            with self.assertRaisesRegex(probe.StackError, "exact authorized model is absent"):
                probe.synchronize_authorized_model("http://127.0.0.1:12345", "fixture credential", "fixture:authorized")
            self.assertEqual(sent.call_count, 2)
        with mock.patch.object(probe, "request", return_value=(503, {})) as sent:
            with self.assertRaisesRegex(probe.StackError, "synchronization failed"):
                probe.synchronize_authorized_model("http://127.0.0.1:12345", "fixture credential", "fixture:authorized")
            self.assertEqual(sent.call_count, 1)

    def test_native_installer_and_host_both_pin_their_owned_shared_storage(self) -> None:
        import native_editor

        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            package = directory / "extensions/iacode.iacode-0.1.0/package.json"
            package.parent.mkdir(parents=True)
            package.write_text(json.dumps({"name": "iacode", "publisher": "iacode", "version": "0.1.0"}), encoding="utf-8")
            with (mock.patch.object(native_editor, "executable", return_value=Path("Code.exe")),
                  mock.patch.object(native_editor, "cli_command", return_value=["Code.exe", "cli.js"]),
                  mock.patch.object(native_editor, "run_owned", return_value=subprocess.CompletedProcess([], 0, "", "")) as launched):
                actor = native_editor.NativeEditor(directory, directory / "workspace", directory / "package.vsix", "a" * 64)
                for arguments in (actor.common, launched.call_args.args[0]):
                    self.assertEqual(arguments[arguments.index("--shared-data-dir") + 1], str(directory / "shared"))
                self.assertEqual(actor.run("package")["result"], "FAIL")
                self.assertFalse(actor.run("package")["sharedStorageObservedOwned"])

    def test_failed_desktop_cleanup_cannot_remove_another_sandbox_owner(self) -> None:
        module = runpy.run_path(str(ROOT / "scripts/iacode/scenarios/desktop_e2e.py"))
        cleanup = module["cleanup_owned_sandboxes"]
        with self.assertRaisesRegex(ValueError, "unowned"):
            cleanup("iacode")
        identifier = "a" * 64

        def observe(*arguments):
            if arguments[:2] == ("container", "ls"):
                self.assertIn("-aq", arguments)  # Exited owned children also count.
                return identifier
            if arguments[:2] == ("container", "inspect"):
                return json.dumps([{"Config": {"Labels": {
                    "org.iacode.sandbox": "1", "org.iacode.sandbox.owner": "another-owner"}}}])
            self.fail("no destructive operation is allowed after ownership mismatch")

        with mock.patch.dict(cleanup.__globals__, {"docker": observe}):
            with self.assertRaisesRegex(module["StackError"], "ownership changed"):
                cleanup("iacode-desktop-" + "b" * 12)

    def test_owned_profile_cleanup_refuses_broad_targets_and_retries_only_sharing_locks(self) -> None:
        import native_process

        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            with self.assertRaisesRegex(ValueError, "unowned"):
                native_process.remove_owned_directory(base, base)
            directory = base / "iacode-owned-fixture"
            directory.mkdir()
            locked = PermissionError("deliberate sharing-lock control")
            locked.winerror = 32
            actual = native_process.shutil.rmtree
            attempts = []

            def remove(target):
                attempts.append(target)
                if len(attempts) == 1:
                    raise locked
                actual(target)

            with mock.patch.object(native_process.shutil, "rmtree", side_effect=remove):
                self.assertEqual(native_process.remove_owned_directory(directory, base), 1)
            self.assertFalse(directory.exists())
            directory.mkdir()
            with mock.patch.object(native_process.shutil, "rmtree", side_effect=PermissionError("not a sharing lock")) as remove:
                with self.assertRaises(PermissionError):
                    native_process.remove_owned_directory(directory, base)
                self.assertEqual(remove.call_count, 1)

    def test_native_process_tree_is_drained_even_after_parent_exits(self) -> None:
        import native_editor

        child = "import time; time.sleep(60)"
        parent = (
            "import subprocess,sys; p=subprocess.Popen([sys.executable,'-c',"
            + repr(child)
            + "],stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); print(p.pid)"
        )
        result = native_editor.run_owned([sys.executable, "-c", parent],
                                         environment=dict(os.environ), timeout=15)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertGreater(int(result.stdout.strip()), 0)
        if os.name == "nt":
            self.assertTrue(result.owned_tree_cleanup["jobOwned"])
            self.assertGreaterEqual(result.owned_tree_cleanup["remainingBeforeCleanup"], 1)
            self.assertEqual(result.owned_tree_cleanup["remainingAfterCleanup"], 0)
        else:
            self.assertIsNone(result.owned_tree_cleanup)

    def test_native_recovery_proof_uses_persistent_storage_context(self) -> None:
        import native_editor

        native_editor.require_persistent_host(["Code.exe", "--extensionDevelopmentPath=/owned-driver"])
        with self.assertRaisesRegex(RuntimeError, "in-memory"):
            native_editor.require_persistent_host(["Code.exe", "--extensionTestsPath=/tests"])
        with tempfile.TemporaryDirectory() as temporary:
            actor = native_editor.NativeEditor.__new__(native_editor.NativeEditor)
            actor.directory = Path(temporary)
            actor.extensions = actor.directory / "extensions"
            actor.driver = actor.directory / "driver"
            actor.workspace = actor.directory / "workspace"
            actor.protocol_digest = "a" * 64
            actor.common = ["Code.exe", "--user-data-dir", str(actor.directory / "profile")]
            with mock.patch.object(native_editor, "run_owned", return_value=subprocess.CompletedProcess([], 0, "", "")) as launched:
                result = actor.run("package")
            self.assertEqual(result["result"], "FAIL")  # No invented native report means no PASS.
            arguments = launched.call_args.args[0]
            self.assertTrue(any(value.startswith("--extensionDevelopmentPath=") for value in arguments))
            self.assertFalse(any(value.startswith("--extensionTestsPath") for value in arguments))

    def test_restarted_api_rediscovers_its_port_and_checks_actual_authenticated_forwarding(self) -> None:
        import desktop_test_support as probe

        with (mock.patch.object(probe, "published_port", return_value=22222) as published,
              mock.patch.object(probe, "operation", side_effect=[ConnectionRefusedError(), (200, {})]) as hello):
            self.assertEqual(probe.restarted_api_endpoint("fixture"), "http://127.0.0.1:22222")
            published.assert_called_once_with("api", 8000)
            self.assertEqual(hello.call_count, 2)
            self.assertEqual(hello.call_args.args[0], "http://127.0.0.1:22222")
        with (mock.patch.object(probe, "published_port", return_value=22222),
              mock.patch.object(probe, "operation", return_value=(401, {"code": "AUTHENTICATION_INVALID"})) as hello):
            with self.assertRaisesRegex(probe.StackError, "AUTHENTICATION_INVALID"):
                probe.restarted_api_endpoint("fixture")
            self.assertEqual(hello.call_count, 1)

    def test_standalone_live_proof_retires_old_pass_before_dependency_import_failure(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for relative in ("scripts/iacode/scenarios/desktop_e2e.py", "scripts/iacode/build_clients.py",
                             "scripts/iacode/compose.py", "scripts/iacode/desktop_test_support.py"):
                target = root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / relative, target)
            shutil.copytree(ROOT / "packages/common/src", root / "packages/common/src",
                            ignore=shutil.ignore_patterns("__pycache__"))
            contract = root / "packages/contracts/src/iacode_contracts/desktop_protocol.json"
            contract.parent.mkdir(parents=True)
            contract.write_bytes(b"\xff")  # Deliberate startup-data corruption, not a domain fake.
            report = root / "var/stale.json"
            report.parent.mkdir()
            report.write_text('{"result":"PASS"}\n', encoding="utf-8")
            result = subprocess.run([sys.executable, "-I", "-S", str(root / "scripts/iacode/scenarios/desktop_e2e.py"),
                                     "--report", str(report)], cwd=root, text=True, encoding="utf-8",
                                    capture_output=True, timeout=30, check=False)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("UnicodeDecodeError", result.stderr)
            self.assertFalse(report.exists(), "an actual cold import failure must not retain the prior PASS")

    def test_live_desktop_harness_cold_start_needs_only_the_standard_library(self) -> None:
        script = ROOT / "scripts/iacode/scenarios/desktop_e2e.py"
        clean = subprocess.run([sys.executable, "-I", "-S", str(script), "--help"], cwd=ROOT,
                               text=True, encoding="utf-8", capture_output=True, timeout=30, check=False)
        self.assertEqual(clean.returncode, 0, clean.stderr)
        self.assertIn("--report", clean.stdout)
        adverse = subprocess.run([sys.executable, "-I", "-S", "-c",
            "import sys; sys.path.insert(0, " + repr(str(ROOT / "packages/contracts/src"))
            + "); import iacode_contracts"], cwd=ROOT, text=True, encoding="utf-8",
            capture_output=True, timeout=30, check=False)
        self.assertNotEqual(adverse.returncode, 0)
        self.assertIn("pydantic", adverse.stderr)

    def test_installed_cli_adapter_resolves_versioned_layout_and_refuses_escape(self) -> None:
        from native_editor import cli_command

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "installation"
            (root / "bin").mkdir(parents=True)
            script = root / "versioned/resources/app/out/cli.js"
            script.parent.mkdir(parents=True)
            script.write_text("// owned CLI layout fixture", encoding="utf-8")
            code = root / "Code.exe"
            adapter = root / "bin/code.cmd"
            adapter.write_text('"%~dp0..\\Code.exe" "%~dp0..\\versioned\\resources\\app\\out\\cli.js" %*', encoding="utf-8")
            self.assertEqual(cli_command(code), [str(code), str(script.resolve())])
            adapter.write_text('"%~dp0..\\Code.exe" "%~dp0..\\..\\cli.js" %*', encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "outside"):
                cli_command(code)
            adapter.write_text("unsupported launcher", encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "unsupported"):
                cli_command(code)


if __name__ == "__main__":
    unittest.main()
