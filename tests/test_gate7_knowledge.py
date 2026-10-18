"""Knowledge delivery controls and causal root-level guards, not substituted live acceptance."""

from __future__ import annotations

import json
import ast
import re
import sys
import unittest
import tempfile
import importlib.util
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))

import ledger_common
import policies


def owned_capability_titles(root: Path) -> tuple[str, ...]:
    gate = ledger_common.delivered_gate(root)
    match = re.fullmatch(r"GATE(\d+)", ledger_common.normalize_gate(gate))
    if match is None:
        raise ValueError("the current delivery has no numbered Gate")
    current = int(match.group(1))
    plan = (root / "docs/MASTER-PLAN.md").read_text(encoding="utf-8")
    rows = re.findall(r"^\| GATE (\d+) — ([^|]+?) \|", plan, flags=re.MULTILINE)
    if not rows:
        raise ValueError("master plan produced no capability corpus")
    return tuple(title.strip() for number, title in rows if int(number) <= current)


def rollup_issues(root: Path, text: str) -> list[str]:
    titles = owned_capability_titles(root)
    normalized = re.sub(r"\s+", " ", text.replace("**", "")).casefold()
    issues = []
    if "checkpoints/latest.md" not in normalized:
        issues.append("live acceptance is not delegated to the canonical checkpoint")
    if re.search(r"current gate\s*:\s*`?gate\s*\d+", normalized):
        issues.append("live current Gate is frozen in a capability rollup")
    for title in titles:
        if title.casefold() not in normalized:
            issues.append("owned capability omitted: " + title)
        for sentence in re.split(r"[.\n]", text):
            folded = re.sub(r"\s+", " ", sentence.replace("**", "")).casefold()
            if title.casefold() in folded and any(
                marker in folded
                for marker in (
                    "what does not",
                    "belongs to later",
                    "belong to later",
                    "not implemented",
                    "no runtime",
                )
            ):
                issues.append("owned capability denied: " + title)
    return issues


class Gate7RollupTests(unittest.TestCase):
    def test_current_rollups_do_not_deny_the_owned_capabilities(self):
        documents = {
            "README.md": ("## Current boundary", "## Running it"),
            "docs/ARCHITECTURE.md": ("## Current state", "## Control plane"),
        }
        for path, (start, end) in documents.items():
            with self.subTest(document=path):
                text = (ROOT / path).read_text(encoding="utf-8").split(start, 1)[1].split(end, 1)[0]
                self.assertEqual(rollup_issues(ROOT, text), [])

    def test_rollup_guard_has_positive_and_each_missing_denied_stale_mutation(self):
        titles = owned_capability_titles(ROOT)
        valid = "Current capabilities: " + "; ".join(titles) + ".\ndocs/checkpoints/LATEST.md\n"
        self.assertEqual(rollup_issues(ROOT, valid), [])
        for title in titles:
            with self.subTest(capability=title):
                self.assertTrue(rollup_issues(ROOT, valid.replace(title, "omitted-capability")))
                self.assertTrue(
                    rollup_issues(
                        ROOT, valid + "\nWhat does not: " + title + " belongs to later Gates."
                    )
                )
        self.assertTrue(rollup_issues(ROOT, valid + "\nCurrent Gate: GATE 0"))
        self.assertTrue(
            rollup_issues(ROOT, valid.replace("docs/checkpoints/LATEST.md", "unbound-status"))
        )

    def test_original_published_readme_is_a_real_causal_negative_not_a_rewritten_fixture(self):
        checkpoint = ROOT / "docs/checkpoints/GATE-7-CP-0001"
        manifest = json.loads((checkpoint / "attempts/README-ROLLUP-0001.json").read_bytes())
        raw = (checkpoint / manifest["artifact"]).read_bytes()
        import hashlib

        self.assertEqual(hashlib.sha256(raw).hexdigest(), manifest["sha256"])
        self.assertEqual(len(raw), manifest["sizeBytes"])
        import subprocess

        published = subprocess.run(
            ["git", "show", manifest["sourceCommit"] + ":" + manifest["sourcePath"]],
            cwd=ROOT,
            capture_output=True,
            check=True,
        )
        self.assertEqual(raw, published.stdout)
        original = (
            raw.decode("utf-8").split("## Current boundary", 1)[1].split("## Running it", 1)[0]
        )
        issues = rollup_issues(ROOT, original)
        self.assertIn("owned capability denied: Experience Store", issues)
        self.assertIn("live current Gate is frozen in a capability rollup", issues)


class Gate7LintDenominatorTests(unittest.TestCase):
    def test_inherited_lint_guard_refuses_each_new_python_root_omission(self):
        import test_gate4_quality_engine as inherited

        source = (ROOT / "scripts/iacode/gates/lint.py").read_text(encoding="utf-8")
        assignment = next(
            node
            for node in ast.parse(source).body
            if isinstance(node, ast.Assign)
            and any(
                isinstance(target, ast.Name) and target.id == "PYTHON_ROOTS"
                for target in node.targets
            )
        )
        roots = ast.literal_eval(assignment.value)
        control = inherited.Gate4QualityCoverageTests(
            "test_mandatory_lint_covers_every_python_project_root"
        )
        control.test_mandatory_lint_covers_every_python_project_root()
        knowledge_roots = [value for value in roots if value.startswith("services/knowledge/")]
        self.assertTrue(knowledge_roots)
        # Removing only src or only tests still covers the project under the inherited rule;
        # remove the whole owning project to exercise its actual adverse denominator.
        narrowed = tuple(value for value in roots if value not in knowledge_roots)
        with patch.object(inherited.ast, "literal_eval", return_value=narrowed):
            with self.assertRaises(AssertionError):
                control.test_mandatory_lint_covers_every_python_project_root()


class Gate7ProcessCompletionTests(unittest.TestCase):
    def driver(self):
        path = ROOT / "docs/checkpoints/GATE-7-CP-0001/audit-harness/publish_progress.py"
        spec = importlib.util.spec_from_file_location("gate7_publication_process_control", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_process_owned_sequence_waits_for_real_success_before_consumer(self):
        module = self.driver()
        with tempfile.TemporaryDirectory(prefix="iacode-g7-process-positive-") as directory:
            root = Path(directory)
            producer = [
                sys.executable,
                "-c",
                "from pathlib import Path; "
                "Path('producer.complete').write_text('actual child completion')",
            ]
            consumer = [
                sys.executable,
                "-c",
                "from pathlib import Path; "
                "assert Path('producer.complete').read_text() == 'actual child completion'; "
                "Path('consumer.executed').write_text('after producer exit')",
            ]
            results = module.run_sequence([("producer", producer), ("consumer", consumer)], root)
            self.assertEqual(
                results,
                [{"stage": "producer", "exitCode": 0}, {"stage": "consumer", "exitCode": 0}],
            )
            self.assertTrue((root / "consumer.executed").is_file())

    def test_success_looking_output_then_actual_failure_never_starts_consumer(self):
        module = self.driver()
        with tempfile.TemporaryDirectory(prefix="iacode-g7-process-adverse-") as directory:
            root = Path(directory)
            producer = [
                sys.executable,
                "-c",
                "print('intermediate durable result: success', flush=True); raise SystemExit(7)",
            ]
            consumer = [
                sys.executable,
                "-c",
                "from pathlib import Path; "
                "Path('forbidden-consumer.executed').write_text('must not execute')",
            ]
            with self.assertRaises(module.StageFailedError) as caught:
                module.run_sequence([("producer", producer), ("consumer", consumer)], root)
            self.assertEqual((caught.exception.stage, caught.exception.code), ("producer", 7))
            self.assertFalse((root / "forbidden-consumer.executed").exists())

    def test_actual_publication_entry_consumes_ordered_canonical_sequence(self):
        module = self.driver()
        tree = ast.parse(Path(module.__file__).read_text(encoding="utf-8"))
        main = next(
            node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "main"
        )
        sequence = next(
            node.value
            for node in ast.walk(main)
            if isinstance(node, ast.Assign)
            and any(
                isinstance(target, ast.Name) and target.id == "steps" for target in node.targets
            )
        )
        names = [ast.literal_eval(item.elts[0]) for item in sequence.elts]
        self.assertEqual(
            names,
            [
                "stage-declared-inputs",
                "staged-scan",
                "canonical-finalizer",
                "stage-finalized-content",
                "commit",
                "committed-validation",
                "normal-push",
            ],
        )
        calls = [
            node
            for node in ast.walk(main)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "run_sequence"
        ]
        self.assertEqual(len(calls), 1)
        self.assertEqual(ast.unparse(calls[0].args[0]), "steps")
        self.assertEqual(ast.unparse(calls[0].args[1]), "ROOT")
        text = ast.unparse(sequence)
        self.assertIn("finalize_checkpoint.py", text)
        self.assertIn("validate_checkpoint.py", text)
        self.assertNotIn("--force", text)


class Gate7SpecificationTests(unittest.TestCase):
    def test_no_canonical_entry_requirement_can_disappear_from_the_current_specification(self):
        import subprocess

        published = subprocess.run(
            ["git", "show", "ad240dac4bea356ad283fff961fb629a611dd7a8:docs/GATE-7-CHECKLIST.md"],
            cwd=ROOT,
            capture_output=True,
            check=True,
            text=True,
            encoding="utf-8",
        )
        entry = {
            row["key"]: row["description"] for row in policies.parse_checklist(published.stdout)
        }
        current = {
            row["key"]: row["description"]
            for row in policies.canonical_requirements(ROOT, "GATE-7")
        }
        self.assertTrue(entry)
        self.assertTrue(entry.items() <= current.items())
        for key in entry:
            removed = {name: value for name, value in current.items() if name != key}
            self.assertFalse(entry.items() <= removed.items())

    def test_current_specification_and_registry_mirror_every_row(self):
        rows = policies.parse_checklist(
            (ROOT / "docs/GATE-7-CHECKLIST.md").read_text(encoding="utf-8")
        )
        declared = policies.canonical_requirements(ROOT, "GATE-7")
        self.assertEqual(
            [(row["key"], row["description"], row["artifact"], row["evidence"]) for row in rows],
            [
                (row["key"], row["description"], row["artifact"], row["evidence"])
                for row in declared
            ],
        )
        self.assertEqual(len({row["key"] for row in rows}), len(rows))
        self.assertTrue(all(row["mandatory"] for row in declared))
        self.assertEqual(
            {row["key"].partition(".")[0] for row in rows}, {str(number) for number in range(1, 9)}
        )

    def test_every_behavior_row_demands_actual_functional_acceptance(self):
        rows = policies.canonical_requirements(ROOT, "GATE-7")
        behavior = [
            row for row in rows if row["key"].partition(".")[0] in {"2", "3", "4", "5", "6", "7"}
        ]
        self.assertTrue(behavior)
        for row in behavior:
            with self.subTest(requirement=row["key"]):
                self.assertIn("FUNCTIONAL-ACCEPTANCE.json", row["evidence"])

    def test_versioned_corpus_has_varied_predefined_exact_expectations(self):
        value = json.loads(
            (ROOT / "services/knowledge/tests/fixtures/retrieval-corpus.json").read_bytes()
        )
        self.assertEqual(value["classification"], "synthetic-validation-only")
        documents = {row["name"]: row["text"] for row in value["documents"]}
        self.assertEqual(len(documents), len(value["documents"]))
        self.assertGreaterEqual(len(documents), 8)
        queries = value["queries"]
        self.assertGreaterEqual(len(queries), 10)
        self.assertEqual(len({row["query"] for row in queries}), len(queries))
        self.assertTrue(any(not row["expectedSources"] for row in queries))
        self.assertTrue(any(len(row["expectedSources"]) > 1 for row in queries))
        self.assertTrue(any("\r\n" in text for text in documents.values()))
        for row in queries:
            self.assertEqual(len(row["expectedSources"]), len(row["expectedScores"]))
            self.assertTrue(set(row["expectedSources"]) <= set(documents))
            self.assertTrue(
                all(type(score) is int and score > 0 for score in row["expectedScores"])
            )


class Gate7ArchitectureBoundaryTests(unittest.TestCase):
    def test_every_policy_field_has_a_closed_contract_and_actual_consumer(self):
        policy = json.loads((ROOT / ".iacode/policies/knowledge-policy.json").read_bytes())
        module = ast.parse(
            (ROOT / "packages/contracts/src/iacode_contracts/knowledge.py").read_text(
                encoding="utf-8"
            )
        )
        contract = next(
            node
            for node in module.body
            if isinstance(node, ast.ClassDef) and node.name == "KnowledgePolicy"
        )
        fields = {
            node.target.id
            for node in contract.body
            if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name)
        }
        self.assertEqual(set(policy), fields)
        paths = [
            ROOT / "services/knowledge/src/iacode_knowledge/domain.py",
            ROOT / "apps/api/src/iacode_api/routes/knowledge.py",
            *(ROOT / "apps/api/src/iacode_api/knowledge").glob("*.py"),
        ]
        consumers = {
            node.attr
            for path in paths
            for node in ast.walk(ast.parse(path.read_text(encoding="utf-8")))
            if isinstance(node, ast.Attribute)
        }
        # Schema version is consumed by the literal contract. Behavioral keys also need code.
        self.assertEqual(set(policy) - {"schemaVersion"} - consumers, set())
        altered = set(policy) | {"unconsumedValidationOnlyBound"}
        self.assertEqual(altered - {"schemaVersion"} - consumers, {"unconsumedValidationOnlyBound"})

    def test_knowledge_library_imports_no_provider_database_http_or_execution_authority(self):
        allowed = {
            "__future__",
            "hashlib",
            "re",
            "unicodedata",
            "dataclasses",
            "datetime",
            "pathlib",
            "typing",
            "iacode_contracts",
            "iacode_experience",
            "pydantic",
        }
        directory = ROOT / "services/knowledge/src/iacode_knowledge"

        def forbidden(text):
            modules = set()
            for node in ast.walk(ast.parse(text)):
                if isinstance(node, ast.Import):
                    modules.update(alias.name.partition(".")[0] for alias in node.names)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    modules.add(node.module.partition(".")[0])
            return modules - allowed

        paths = list(directory.glob("*.py"))
        self.assertTrue(paths)
        for path in paths:
            self.assertEqual(forbidden(path.read_text(encoding="utf-8")), set(), path.name)
        for module in (
            "subprocess",
            "socket",
            "httpx",
            "sqlalchemy",
            "iacode_model_gateway",
            "iacode_sandbox",
            "iacode_evaluator",
        ):
            with self.subTest(module=module):
                self.assertEqual(forbidden("import " + module + "\n"), {module})

    def test_actual_schema_closes_definitions_and_denies_source_training(self):
        schema = json.loads((ROOT / ".iacode/schemas/knowledge.schema.json").read_bytes())
        self.assertTrue(schema["anyOf"])
        definitions = schema["$defs"]
        for name, definition in definitions.items():
            with self.subTest(definition=name):
                if definition.get("type") == "object":
                    self.assertIs(definition.get("additionalProperties"), False)
        grant = definitions["SourceGrant"]["properties"]
        self.assertIs(grant["trainingAllowed"]["const"], False)
        self.assertIs(grant["distillationAllowed"]["const"], False)
        provenance = definitions["KnowledgeProvenance"]["properties"]
        self.assertEqual(provenance["grant"]["$ref"], "#/$defs/SourceGrant")
        document = definitions["KnowledgeDocument"]["properties"]
        self.assertEqual(document["provenance"]["$ref"], "#/$defs/KnowledgeProvenance")
        self.assertIs(document["untrustedContent"]["const"], True)

    def test_default_sources_are_empty_and_curated_payloads_are_not_shipped(self):
        registry = json.loads((ROOT / ".iacode/knowledge-sources/registry.json").read_bytes())
        self.assertEqual(registry, {"schemaVersion": "1.0.0", "sources": []})
        import subprocess

        for path in (
            ".iacode/knowledge-sources/artifacts/validation.json",
            ".iacode/knowledge-sources/grants/validation.json",
        ):
            result = subprocess.run(
                ["git", "check-ignore", "--no-index", path],
                cwd=ROOT,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0)
        dockerignore = (ROOT / ".dockerignore").read_text(encoding="utf-8").splitlines()
        allow = dockerignore.index("!.iacode/knowledge-sources/")
        deny = dockerignore.index(".iacode/knowledge-sources/**")
        self.assertLess(allow, deny)
        self.assertIn("!.iacode/knowledge-sources/registry.json", dockerignore[deny + 1 :])

    def test_current_verifier_adds_live_knowledge_without_dropping_inherited_stages(self):
        sys.path.insert(0, str(ROOT / "scripts/iacode"))
        import verify

        stages = verify.build_stages(False)
        names = [stage.name for stage in stages]
        self.assertEqual(len(names), len(set(names)))
        self.assertEqual(names.count("knowledge-engine-e2e"), 1)
        self.assertTrue(
            {
                "experience-store-e2e",
                "desktop-client-e2e",
                "native-client-installation",
                "quality-false-pass",
                "restart",
                "dependency-failure",
                "fresh-install",
            }
            <= set(names)
        )
        stage = next(stage for stage in stages if stage.name == "knowledge-engine-e2e")
        self.assertIn("scripts/iacode/scenarios/knowledge_engine_e2e.py", stage.argv)
        self.assertFalse(stage.destructive)
        mandatory = verify.mandatory_gate_commands(ROOT)
        self.assertEqual(
            {name[5:] for name in names if name.startswith("gate:")},
            {identifier for identifier, _ in mandatory},
        )
        self.assertIn("knowledgeTests", {identifier for identifier, _ in mandatory})


class Gate7ProducerBoundaryTests(unittest.TestCase):
    def helper(self, name):
        path = ROOT / "docs/checkpoints/GATE-7-CP-0001/audit-harness" / (name + ".py")
        sys.path.insert(0, str(path.parent))
        sys.path.insert(0, str(ROOT / "scripts/iacode"))
        spec = importlib.util.spec_from_file_location("gate7_boundary_" + name, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_full_summary_derives_current_exact_stage_vocabulary_and_refuses_mutations(self):
        publisher = self.helper("run_full_verification")
        names = [stage.name for stage in publisher.build_stages(False)]
        value = {"result": "PASS", "stages": [{"name": name, "result": "PASS"} for name in names]}
        self.assertEqual(publisher.summarize_stages(value), (len(names), len(names), 0))
        mutations = [
            value["stages"][:-1],
            value["stages"] + [value["stages"][0]],
            list(reversed(value["stages"])),
            [{"name": name, "status": "PASS"} for name in names],
        ]
        for stages in mutations:
            with self.subTest(stage_count=len(stages)):
                with self.assertRaises(RuntimeError):
                    publisher.summarize_stages({"result": "PASS", "stages": stages})
        for invalid in ("SKIP", "UNKNOWN", None):
            changed = [{**row} for row in value["stages"]]
            changed[0]["result"] = invalid
            with self.assertRaises(RuntimeError):
                publisher.summarize_stages({"result": "PASS", "stages": changed})
        changed = [{**row} for row in value["stages"]]
        changed[0]["result"] = "FAIL"
        with self.assertRaises(RuntimeError):
            publisher.summarize_stages({"result": "PASS", "stages": changed})
        self.assertEqual(
            publisher.summarize_stages({"result": "FAIL", "stages": changed}),
            (len(names), len(names) - 1, 1),
        )

    def test_knowledge_raw_producer_survives_actual_consumer_refusal_before_clone_cleanup(self):
        publisher = self.helper("run_full_verification")
        with tempfile.TemporaryDirectory(prefix="iacode-g7-raw-capture-") as outer:
            archive = Path(outer) / "archive"
            with tempfile.TemporaryDirectory(prefix="iacode-g7-clone-") as inner:
                clone = Path(inner)
                (clone / "var").mkdir()
                report = clone / "full.json"
                report.write_bytes(b'{"result":"FAIL","stages":[]}\r\n')
                raw = b'{\r\n  "result": "PASS", "kind": "unit-raw-fixture-not-runtime-proof"\r\n}\r\n'
                (clone / "var/knowledge-engine-e2e.json").write_bytes(raw)
                with patch.object(
                    publisher,
                    "summarize_stages",
                    side_effect=RuntimeError("deliberate consumer refusal"),
                ):
                    with self.assertRaises(RuntimeError):
                        publisher.collect_producer_observations(clone, report, archive, "fixture")
            manifests = list(archive.glob("*-MANIFEST.json"))
            self.assertEqual(len(manifests), 1)
            manifest = json.loads(manifests[0].read_bytes())
            row = next(
                row
                for row in manifest["reports"]
                if row["producerName"] == "knowledge-engine-e2e.json"
            )
            self.assertEqual((archive / row["archive"]).read_bytes(), raw)
            import hashlib

            self.assertEqual(row["sha256"], hashlib.sha256(raw).hexdigest())
            self.assertFalse(manifest["gateVerdictIssued"])

    def test_prior_live_pass_is_preserved_and_retired_before_any_new_producer(self):
        publisher = self.helper("execute_live_knowledge")
        with tempfile.TemporaryDirectory(prefix="iacode-g7-prior-producer-") as directory:
            root = Path(directory)
            source = root / "prior.json"
            archive = root / "archive"
            archive.mkdir()
            raw = b'{\r\n "result":"PASS", "kind":"prior-unit-fixture-not-current-proof"\r\n}\r\n'
            source.write_bytes(raw)
            publisher.retire_previous(source, archive)
            self.assertFalse(source.exists())
            backups = list(archive.glob("KNOWLEDGE-PREVIOUS-PRODUCER-*.json"))
            self.assertEqual(len(backups), 1)
            self.assertEqual(backups[0].read_bytes(), raw)
            receipt = json.loads(
                next(archive.glob("KNOWLEDGE-PREVIOUS-RAW-RECEIPT-*.json")).read_bytes()
            )
            self.assertEqual(receipt["kind"], "PRIOR_PRODUCER_NOT_CURRENT_ACCEPTANCE")
            self.assertFalse(receipt["acceptanceGranted"])


class Gate7InterruptionBoundaryTests(unittest.TestCase):
    def support(self):
        sys.path.insert(0, str(ROOT / "scripts/iacode"))
        import desktop_test_support

        return desktop_test_support

    def test_knowledge_interruption_requires_only_its_exact_canonical_project(self):
        import uuid

        support = self.support()
        project = str(uuid.uuid4())
        for operation, options in (
            ("knowledge-ingest", {}),
            ("knowledge-ingest", {"knowledge_project": "not-canonical"}),
            ("knowledge-ingest", {"knowledge_project": project.upper()}),
            ("knowledge-ingest", {"knowledge_project": project, "experience_project": project}),
            ("experience-capture", {"experience_project": project, "knowledge_project": project}),
            ("start", {"knowledge_project": project}),
            ("unknown", {"knowledge_project": project}),
        ):
            with self.subTest(operation=operation, fields=sorted(options)):
                with self.assertRaises(ValueError):
                    support.InterruptedResponseProxy(
                        "http://127.0.0.1:9", drop_operation=operation, **options
                    )
        proxy = support.InterruptedResponseProxy(
            "http://127.0.0.1:9", drop_operation="knowledge-ingest", knowledge_project=project
        )
        try:
            self.assertTrue(proxy.thread.is_alive())
            self.assertIsNone(proxy.accepted_document)
            self.assertFalse(proxy.dropped)
        finally:
            proxy.close()
        self.assertFalse(proxy.thread.is_alive())

    def test_knowledge_interruption_refuses_coerced_or_widened_policy_bounds(self):
        import uuid

        support = self.support()
        for maximum in (True, 0, 16385):
            with self.subTest(maximum=maximum):
                with patch.object(support.json, "loads", return_value={"maxRequestBytes": maximum}):
                    with self.assertRaises(ValueError):
                        support.InterruptedResponseProxy(
                            "http://127.0.0.1:9",
                            drop_operation="knowledge-ingest",
                            knowledge_project=str(uuid.uuid4()),
                        )
