"""Current Gate7 assurance regressions; unit fixtures never stand in for live acceptance."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))
sys.path.insert(0, str(ROOT / "scripts/iacode"))


def harness(name):
    path = ROOT / "docs/checkpoints/GATE-7-CP-0001/audit-harness" / (name + ".py")
    spec = importlib.util.spec_from_file_location("gate7_assurance_" + name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def missing_gate_documentation(root, text):
    import policies

    return [
        name
        for name, row in policies.gate_definitions(root).items()
        if row["mandatory"] and ("`" + name + "`") not in text
    ]


class Gate7DocumentationAndStreamsTests(unittest.TestCase):
    def test_development_documents_every_current_gate_and_registered_growth(self):
        import policies

        text = (ROOT / "docs/DEVELOPMENT.md").read_text(encoding="utf-8")
        actual = policies.gate_definitions(ROOT)
        self.assertEqual(missing_gate_documentation(ROOT, text), [])
        for name in actual:
            with self.subTest(omitted=name):
                self.assertIn(
                    name, missing_gate_documentation(ROOT, text.replace("`" + name + "`", ""))
                )
        with patch.object(
            policies,
            "gate_definitions",
            return_value={**actual, "registeredFutureGate": {"mandatory": True}},
        ):
            self.assertEqual(missing_gate_documentation(ROOT, text), ["registeredFutureGate"])
            self.assertEqual(missing_gate_documentation(ROOT, text + " `registeredFutureGate`"), [])

    def test_current_entrypoints_configure_the_shared_stream_before_work(self):
        import ledger_common

        class ReachedStreamBoundaryError(Exception):
            pass

        names = (
            "publish_progress",
            "run_knowledge_integration",
            "archive_failed_runtime_v1",
            "archive_failed_runtime_v2",
            "import_rework_contexts",
            "complete_functional_acceptance",
            "complete_requirements",
            "run_internal_red_team",
            "assemble_verified_progress",
            "audit_documentation",
            "run_checkpoint_validation",
            "assemble_final_handoff",
            "format_assurance_helpers",
            "diagnose_promotion_producer",
            "verify_original_bytes",
        )
        for name in names:
            with self.subTest(entrypoint=name):
                module = harness(name)
                with (
                    patch.object(
                        ledger_common, "use_utf8_stdout", side_effect=ReachedStreamBoundaryError
                    ),
                    self.assertRaises(ReachedStreamBoundaryError),
                ):
                    module.main()


class Gate7FutureBoundaryTests(unittest.TestCase):
    def test_code_graph_is_only_a_future_notice_and_real_scope_rejects_an_added_file(self):
        import policies

        registry = policies.load_gate_scope(ROOT)
        owned = next(row for row in registry if row["path"] == "services/code-graph")
        self.assertEqual(owned["gate"], "GATE 8")
        directory = ROOT / owned["path"]
        self.assertEqual(sorted(path.name for path in directory.iterdir()), ["README.md"])
        self.assertIn(
            policies.RESERVATION_MARKER, (directory / "README.md").read_text(encoding="utf-8")
        )
        self.assertEqual(policies.scope_violations(ROOT, "GATE-7"), [])
        with tempfile.TemporaryDirectory(prefix="iacode-g7-future-scope-") as raw:
            root = Path(raw)
            policy = root / ".iacode/policies/gate-scope.json"
            policy.parent.mkdir(parents=True)
            policy.write_bytes((ROOT / ".iacode/policies/gate-scope.json").read_bytes())
            target = root / owned["path"]
            target.mkdir(parents=True)
            (target / "README.md").write_bytes((directory / "README.md").read_bytes())
            self.assertEqual(policies.scope_violations(root, "GATE-7"), [])
            (target / "graph.py").write_text(
                "# Deliberately forbidden future-path artifact in an owned unit fixture.\n",
                encoding="utf-8",
            )
            self.assertTrue(policies.scope_violations(root, "GATE-7"))


class Gate7FrameworkDiagnosticsTests(unittest.TestCase):
    def test_framework_methods_and_lifecycle_headers_survive_without_private_bodies(self):
        import verify

        expected = [
            "ERROR: setUpClass (fixture_module.FirstCase)",
            "ERROR: tearDownClass (fixture_module.SecondCase)",
            "ERROR: setUpModule (fixture_module)",
            "ERROR: tearDownModule (fixture_module)",
            "FAIL: test_case (fixture_module.Case.test_case)",
            "ERROR: test_other (fixture_module.Case.test_other)",
            "FAILED tests/unit/test_fixture.py::test_case",
        ]
        text = "\n".join(
            [
                *expected,
                "Traceback payload: private-unit-marker-not-a-diagnostic-identity",
                "ERROR: setUpClass (untrusted/path)",
                "ERROR: arbitrary-body-is-not-a-framework-holder",
            ]
        )
        result = verify.failure_diagnostics(text)
        self.assertEqual(result["failureHeaders"], expected)
        self.assertEqual(result["failureHeaderCount"], len(expected))
        self.assertFalse(result["failureHeadersTruncated"])
        self.assertNotIn("private-unit-marker", json.dumps(result))
        self.assertNotIn("untrusted/path", json.dumps(result))

    def test_framework_identity_count_and_length_limits_remain_unchanged(self):
        import verify

        header = "ERROR: setUpClass (fixture_module.Case)"
        result = verify.failure_diagnostics("\n".join([header] * 257))
        self.assertEqual(result["failureHeaderCount"], 257)
        self.assertEqual(len(result["failureHeaders"]), 256)
        self.assertTrue(result["failureHeadersTruncated"])
        result = verify.failure_diagnostics("ERROR: setUpClass (" + "A" * 1100 + ")")
        self.assertEqual(result["failureHeaderCount"], 1)
        self.assertEqual(result["failureHeaders"], [])
        self.assertTrue(result["failureHeadersTruncated"])


class Gate7MinimalProtocolIsolationTests(unittest.TestCase):
    def test_fixture_copies_contracts_and_never_source_data_history_or_unrelated_verdicts(self):
        import promotion_fixture as producer

        with tempfile.TemporaryDirectory(prefix="iacode-g7-fixture-assets-") as raw:
            base = Path(raw)
            seed, destination = base / "seed", base / "fixture"
            producer.build_fixture_repository(seed)
            synthetic = {
                "knowledge-sources/artifacts/private-fixture.txt": "synthetic-owner-payload",
                "knowledge-sources/grants/private-fixture.json": "{}",
                "unknown-operational-root/source.txt": "synthetic-owner-context",
                "memory/private-fixture.txt": "synthetic-owner-history",
                "anchors/checkpoint-chain.json": "{}",
                "attestations/unrelated-verdict.json": "{}",
            }
            for relative, text in synthetic.items():
                path = seed / ".iacode" / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text, encoding="utf-8")
            with patch.object(producer, "PROJECT_ROOT", seed):
                producer.build_fixture_repository(destination)
            for name in producer.FIXTURE_CONTROL_DIRECTORIES:
                self.assertTrue((destination / ".iacode" / name).is_dir())
            self.assertEqual(
                (seed / ".iacode/VERSION").read_bytes(),
                (destination / ".iacode/VERSION").read_bytes(),
            )
            for relative, text in synthetic.items():
                self.assertFalse((destination / ".iacode" / relative).exists(), relative)
                self.assertEqual((seed / ".iacode" / relative).read_text(encoding="utf-8"), text)
            self.assertEqual(
                sorted(path.name for path in (destination / ".iacode/attestations").iterdir()),
                ["README.md"],
            )
            self.assertTrue(
                (destination / "packages/common/src/iacode_common/secret_scanning.py").is_file()
            )

    def test_a_retained_contract_broken_link_still_fails_the_real_mirror(self):
        import promotion_fixture as producer
        from ledger_common import resolve_latest

        with tempfile.TemporaryDirectory(prefix="iacode-g7-retained-link-") as raw:
            base = Path(raw)
            seed, destination = base / "seed", base / "fixture"
            producer.build_fixture_repository(seed)
            marker = seed / ".iacode/agents/unit-retained-contract.md"
            marker.write_text(
                "# Retained contract\n\n[Missing contract](missing-contract.md)\n",
                encoding="utf-8",
            )
            with patch.object(producer, "PROJECT_ROOT", seed):
                producer.build_fixture_repository(destination)
            self.assertTrue((destination / ".iacode/agents/unit-retained-contract.md").is_file())
            with self.assertRaises(producer.FixtureError):
                producer.deliver_checkpoint(
                    destination, scope="control-plane", status="READY_FOR_REVIEW"
                )
            report = json.loads(
                (resolve_latest(destination) / "M0-INTERNAL-MIRROR.json").read_bytes()
            )
            observed = next(row for row in report["checks"] if row["id"] == "MIR-015")
            self.assertEqual(observed["result"], "FAIL")
            self.assertIn("missing-contract.md", observed["observed"])
            self.assertEqual(report["result"], "FAIL")


class Gate7PromotionProducerCaptureTests(unittest.TestCase):
    def test_owner_locator_and_all_originals_survive_real_consumer_error_and_cleanup(self):
        import promotion_fixture as producer

        module = harness("diagnose_promotion_producer")

        class ReachedOwnerBoundaryError(Exception):
            pass

        with tempfile.TemporaryDirectory(prefix="iacode-g7-producer-records-") as archive_raw:
            checkpoint = Path(archive_raw)
            rows = []
            bodies = [
                b'{"kind":"synthetic-unit-producer-not-acceptance","value":1}\r\n',
                b'{"kind":"synthetic-unit-producer-not-acceptance","value":2}\r\n',
            ]
            with (
                self.assertRaises(json.JSONDecodeError),
                tempfile.TemporaryDirectory(prefix="iacode-g7-producer-owner-") as raw,
            ):
                workdir = Path(raw)
                moved = workdir / "owner-selected-location"
                with patch.object(producer, "promotion_repository", return_value=moved):
                    with (
                        patch.object(
                            producer,
                            "build_fixture_repository",
                            side_effect=ReachedOwnerBoundaryError,
                        ) as reached,
                        self.assertRaises(ReachedOwnerBoundaryError),
                    ):
                        producer.run_positive_promotion(workdir)
                    reached.assert_called_once_with(moved)
                    for index, body in enumerate(bodies, 1):
                        path = (
                            moved
                            / "docs/checkpoints"
                            / f"SETUP-00-CP-{index:04d}"
                            / "M0-INTERNAL-MIRROR.json"
                        )
                        path.parent.mkdir(parents=True)
                        path.write_bytes(body)
                    rows = module.capture_protocol_mirrors(
                        workdir, checkpoint, "PROMOTION-UNIT-CAPTURE"
                    )
                    self.assertEqual(len(rows), len(bodies))
                    json.loads("deliberately invalid post-capture consumer input")
            self.assertFalse(workdir.exists())
            self.assertEqual(len({row["archive"] for row in rows}), len(bodies))
            for row, body in zip(rows, bodies, strict=True):
                original = checkpoint / row["archive"]
                self.assertEqual(original.read_bytes(), body)
                self.assertEqual(row["sha256"], hashlib.sha256(body).hexdigest())
                self.assertFalse(row["acceptanceGranted"])


class Gate7TypedObservationTests(unittest.TestCase):
    def test_real_running_and_failed_children_are_not_completed_source_observations(self):
        module = harness("verify_original_bytes")
        child = subprocess.Popen(
            [
                sys.executable,
                "-X",
                "utf8",
                "-c",
                "import sys; print('owned-child-preimage', flush=True); "
                "sys.stdin.readline(); raise SystemExit(7)",
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
        )
        try:
            observed = child.stdout.readline()
            self.assertEqual(observed.strip(), "owned-child-preimage")
            self.assertIsNone(child.poll())
            with self.assertRaises(ValueError):
                module.require_completed_text(
                    {"session_id": "owned-running-child", "output": observed}
                )
            child.communicate("release\n", timeout=10)
            self.assertEqual(child.returncode, 7)
            with self.assertRaises(ValueError):
                module.require_completed_text({"exit_code": child.returncode, "output": observed})
        finally:
            if child.poll() is None:
                child.kill()
                child.communicate(timeout=10)
        completed = subprocess.run(
            [sys.executable, "-X", "utf8", "-c", "print('completed-owned-preimage')"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=10,
            check=False,
        )
        self.assertEqual(completed.returncode, 0)
        self.assertEqual(
            module.require_completed_text(
                {"exit_code": completed.returncode, "output": completed.stdout}
            ).strip(),
            "completed-owned-preimage",
        )
        for observation in (
            None,
            {},
            {"exit_code": False, "output": "not an integer exit"},
            {"exit_code": 0, "output": ""},
            {"exit_code": 0, "output": " \n"},
            {"exit_code": 0, "output": "forbidden\x00source"},
            {"exit_code": 0, "output": "partial", "session_id": "still-running"},
        ):
            with self.subTest(observation=observation), self.assertRaises(ValueError):
                module.require_completed_text(observation)

    def test_only_typed_nonempty_actual_bytes_size_and_digest_are_evidence(self):
        module = harness("verify_original_bytes")
        raw = b"owned-nonempty-original\r\n"
        digest = hashlib.sha256(raw).hexdigest()
        proof = module.validate_observation(raw, digest, len(raw))
        self.assertEqual(proof["result"], "PASS")
        self.assertFalse(proof["gateVerdictGranted"])
        for arguments in (
            (None, None, None),
            (b"", hashlib.sha256(b"").hexdigest(), 0),
            (raw, None, len(raw)),
            (raw, digest, None),
            (raw, digest, True),
            (raw, "0" * 64, len(raw)),
            (raw, digest, len(raw) + 1),
            (raw.decode(), digest, len(raw)),
        ):
            with self.subTest(arguments=arguments), self.assertRaises(ValueError):
                module.validate_observation(*arguments)

    def test_actual_file_mutations_and_atomic_readonly_source_envelope(self):
        module = harness("verify_original_bytes")
        raw = b"owned-file-original\r\n"
        digest = hashlib.sha256(raw).hexdigest()
        with tempfile.TemporaryDirectory(prefix="iacode-g7-typed-original-") as temporary:
            path = Path(temporary) / "original.raw"
            path.write_bytes(raw)
            self.assertEqual(module.verify_file_bytes(path, digest, len(raw))["result"], "PASS")
            path.write_bytes(b"")
            with self.assertRaises(ValueError):
                module.verify_file_bytes(path, digest, len(raw))
            path.write_bytes(raw + b"mutated")
            with self.assertRaises(ValueError):
                module.verify_file_bytes(path, digest, len(raw))
            path.unlink()
            with self.assertRaises(ValueError):
                module.verify_file_bytes(path, digest, len(raw))
        source = ROOT / "docs/checkpoints/GATE-7-CP-0001/audit-harness/publish_progress.py"
        before = source.read_bytes()
        child = subprocess.run(
            [sys.executable, "-X", "utf8", str(Path(module.__file__)), "--source", str(source)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=10,
            check=False,
        )
        self.assertEqual(child.returncode, 0, child.stderr)
        envelope = json.loads(child.stdout)
        self.assertIs(envelope["completed"], True)
        self.assertEqual(envelope["bytes"], len(before))
        self.assertEqual(envelope["sha256"], hashlib.sha256(before).hexdigest())
        self.assertEqual(envelope["text"], before.decode("utf-8"))
        self.assertEqual(source.read_bytes(), before)


class Gate7RootInputFingerprintTests(unittest.TestCase):
    @contextmanager
    def repository(self, document):
        with tempfile.TemporaryDirectory(prefix="iacode-g7-root-input-test-") as raw:
            root = Path(raw)
            if (
                root.resolve().parent != Path(tempfile.gettempdir()).resolve()
                or root.is_symlink()
                or root.is_junction()
            ):
                raise ValueError("unexpected disposable root-input owner")
            subprocess.run(
                ["git", "init", "--quiet", "--initial-branch=main", str(root)],
                capture_output=True,
                check=True,
            )
            seeds = {
                ".dockerignore": "synthetic-private-source/**\n",
                ".gitignore": ".dockerignore\nverify.ps1\n",
                "ruff.toml": "line-length = 100\n",
                "verify.ps1": "exit 0\n",
            }
            current = json.loads((ROOT / ".iacode/policies/assurance-scope.json").read_bytes())
            for name in current["additionalRootFiles"]:
                if name not in seeds:
                    if Path(name).name != name:
                        raise ValueError("only declared root inputs belong to this fixture")
                    seeds[name] = "synthetic registered root input\n"
            for name, text in seeds.items():
                (root / name).write_text(text, encoding="utf-8")
            if document is not None:
                policy = root / ".iacode/policies/assurance-scope.json"
                policy.parent.mkdir(parents=True)
                policy.write_text(json.dumps(document), encoding="utf-8")
            yield root

    def test_build_and_verification_edits_invalidate_actual_assurance_fingerprint(self):
        import ledger_common

        document = json.loads((ROOT / ".iacode/policies/assurance-scope.json").read_bytes())
        observations = []
        with self.repository(document) as root:
            for name, replacement in (
                (".dockerignore", "!synthetic-private-source/**\n"),
                ("verify.ps1", "exit 7\n"),
            ):
                path = root / name
                original = path.read_bytes()
                before = ledger_common.scope_fingerprint(root)
                path.write_text(replacement, encoding="utf-8")
                observations.append(
                    (
                        name,
                        original != path.read_bytes(),
                        before,
                        ledger_common.scope_fingerprint(root),
                    )
                )
                path.write_bytes(original)
        self.assertFalse(root.exists())
        for name, changed, before, after in observations:
            with self.subTest(rootInput=name):
                self.assertTrue(changed)
                self.assertNotEqual(before, after)

    def test_every_current_root_is_bound_even_if_ignored_and_deletion_invalidates(self):
        import ledger_common

        document = json.loads((ROOT / ".iacode/policies/assurance-scope.json").read_bytes())
        declared = tuple(document["additionalRootFiles"])
        self.assertEqual(ledger_common.assurance_root_files(ROOT, required=True), declared)
        self.assertTrue(
            {".dockerignore", ".gitignore", "ruff.toml", "verify.ps1"}.issubset(declared)
        )
        with self.repository(document) as root:
            baseline = ledger_common.scope_fingerprint(root)
            for name in declared:
                with self.subTest(rootInput=name):
                    path = root / name
                    original = path.read_bytes()
                    path.write_bytes(original + b"# changed synthetic root input\n")
                    self.assertNotEqual(ledger_common.scope_fingerprint(root), baseline)
                    path.write_bytes(original)
                    self.assertEqual(ledger_common.scope_fingerprint(root), baseline)
                    path.unlink()
                    self.assertNotEqual(ledger_common.scope_fingerprint(root), baseline)
                    path.write_bytes(original)
                    self.assertEqual(ledger_common.scope_fingerprint(root), baseline)
        self.assertFalse(root.exists())

    def test_absent_and_v1_subjects_keep_their_original_root_fingerprint_identity(self):
        import ledger_common

        legacy = {
            "schemaVersion": "1.0.0",
            "additionalRootFiles": [".gitignore", "ruff.toml"],
        }
        for document in (None, legacy):
            with self.subTest(subjectPolicy=document), self.repository(document) as root:
                expected_names = (
                    [".gitignore", ".iacode/policies/assurance-scope.json", "ruff.toml"]
                    if document is not None
                    else []
                )
                expected = ledger_common.canonical_digest(
                    [
                        [name, ledger_common.canonical_hash_path(root / name)]
                        for name in sorted(expected_names)
                    ]
                )
                self.assertEqual(ledger_common.scope_fingerprint(root), expected)
                self.assertEqual(
                    ledger_common.assurance_root_files(root),
                    (".gitignore", "ruff.toml") if document is not None else (),
                )
                for name in (".dockerignore", "verify.ps1"):
                    (root / name).write_text("changed legacy-unbound input\n", encoding="utf-8")
                    self.assertEqual(ledger_common.scope_fingerprint(root), expected)
            self.assertFalse(root.exists())

    def test_current_policy_refuses_missing_narrowed_reordered_extra_and_malformed_inputs(self):
        import ledger_common

        valid = json.loads((ROOT / ".iacode/policies/assurance-scope.json").read_bytes())
        names = valid["additionalRootFiles"]
        documents = [
            None,
            False,
            [],
            {**valid, "schemaVersion": "unsupported"},
            {**valid, "schemaVersion": []},
            {**valid, "additionalRootFiles": True},
            {**valid, "additionalRootFiles": ",".join(names)},
            {**valid, "additionalRootFiles": []},
            {**valid, "additionalRootFiles": list(reversed(names))},
            {**valid, "additionalRootFiles": [*names, "undeclared-root.txt"]},
            {**valid, "additionalRootFiles": [*names, *names[:1]]},
            *[
                {**valid, "additionalRootFiles": [name for name in names if name != omitted]}
                for omitted in names
            ],
        ]
        for document in documents:
            with (
                self.subTest(policy=document),
                self.repository(document) as root,
                self.assertRaisesRegex(ledger_common.LedgerError, "requires|unsupported|narrowed"),
            ):
                ledger_common.assurance_root_files(root, required=True)
            self.assertFalse(root.exists())


class Gate7CanonicalProducerTests(unittest.TestCase):
    def canonical_names(self):
        import verify

        return {
            Path(stage.argv[index + 1]).name
            for stage in verify.build_stages(False)
            for index, argument in enumerate(stage.argv[:-1])
            if argument == "--report" and Path(stage.argv[index + 1]).parent.name == "var"
        }

    @contextmanager
    def producer(self, extra=()):
        with tempfile.TemporaryDirectory(prefix="iacode-g7-canonical-producer-") as raw:
            root = Path(raw)
            if root.resolve().parent != Path(tempfile.gettempdir()).resolve():
                raise ValueError("unexpected owned producer fixture")
            (root / "var").mkdir()
            names = self.canonical_names() | {"quality-secret-output.json", "quality-unit.json"}
            names.update(extra)
            self.assertTrue({"sandbox-coding.json", "gateway-smoke.json"}.issubset(names))
            expected = {}
            for name in sorted(names):
                content = json.dumps({"result": "FAIL", "unitProducer": name}).encode() + b"\n"
                (root / "var" / name).write_bytes(content)
                expected[name] = content
            verifier = root / "INTERNAL-FULL-VERIFY.json"
            verifier.write_bytes(b'{"result":"FAIL","stages":[]}\n')
            import ledger_common

            private = "gh" + "p_" + "r" * 20
            self.assertTrue(ledger_common.find_secrets(private))
            (root / "var/unselected-private-data.json").write_text(private, encoding="utf-8")
            yield root, verifier, expected
        self.assertFalse(root.exists())

    def test_all_canonical_producers_and_legacy_outputs_are_captured_without_private_extras(self):
        publisher = harness("run_full_verification")
        with (
            self.producer() as (root, verifier, expected),
            tempfile.TemporaryDirectory(prefix="iacode-g7-canonical-archive-") as raw,
        ):
            archive = Path(raw)
            manifest = publisher.capture_producer_reports(root, verifier, archive, "unit-context")
            document = json.loads(manifest.read_bytes())
            rows = {row["producerName"]: row for row in document["reports"]}
            self.assertEqual(set(rows), set(expected) | {verifier.name})
            self.assertFalse(document["gateVerdictIssued"])
            self.assertEqual(document["refusedReports"], [])
            for name, content in expected.items():
                row = rows[name]
                self.assertEqual((archive / row["archive"]).read_bytes(), content)
                self.assertEqual(row["sha256"], hashlib.sha256(content).hexdigest())

    def test_canonical_registry_growth_is_bound_without_a_caller_selected_report_set(self):
        import verify

        publisher = harness("run_full_verification")
        name = "registered-canonical-report.json"
        stages = [
            *verify.build_stages(False),
            SimpleNamespace(
                name="registered-canonical-stage",
                argv=["python", "unit-producer.py", "--report", str(ROOT / "var" / name)],
            ),
        ]
        with (
            self.producer([name]) as (root, verifier, expected),
            tempfile.TemporaryDirectory(prefix="iacode-g7-canonical-growth-") as raw,
            patch.object(publisher, "build_stages", return_value=stages),
        ):
            manifest = publisher.capture_producer_reports(root, verifier, Path(raw), "unit-context")
            rows = json.loads(manifest.read_bytes())["reports"]
            self.assertIn(name, {row["producerName"] for row in rows})
            self.assertTrue(set(expected).issubset({row["producerName"] for row in rows}))

    def test_all_current_originals_survive_real_consumer_refusal_and_actual_owner_cleanup(self):
        publisher = harness("run_full_verification")
        with tempfile.TemporaryDirectory(prefix="iacode-g7-canonical-survival-") as raw:
            archive = Path(raw)
            with self.producer() as (root, verifier, expected):
                owner = root
                with self.assertRaisesRegex(RuntimeError, "vocabulary"):
                    publisher.collect_producer_observations(root, verifier, archive, "unit-context")
            self.assertFalse(owner.exists())
            manifests = list(archive.glob("*-MANIFEST.json"))
            self.assertEqual(len(manifests), 1)
            rows = {
                row["producerName"]: row for row in json.loads(manifests[0].read_bytes())["reports"]
            }
            self.assertTrue(set(expected).issubset(rows))
            for name, content in expected.items():
                self.assertEqual((archive / rows[name]["archive"]).read_bytes(), content)

    def test_claimed_success_cannot_omit_a_canonically_required_producer(self):
        publisher = harness("run_full_verification")
        with (
            self.producer() as (root, verifier, _expected),
            tempfile.TemporaryDirectory(prefix="iacode-g7-canonical-completeness-") as raw,
        ):
            (root / "var/gateway-smoke.json").unlink()
            verifier.write_text(
                json.dumps(
                    {
                        "result": "PASS",
                        "stages": [
                            {"name": stage.name, "result": "PASS"}
                            for stage in publisher.build_stages(False)
                        ],
                    }
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(RuntimeError, "canonical"):
                publisher.collect_producer_observations(root, verifier, Path(raw), "unit-context")

    def test_forwarding_uses_every_archived_original_after_actual_producer_cleanup(self):
        publisher = harness("run_full_verification")
        with tempfile.TemporaryDirectory(prefix="iacode-g7-forward-archive-") as raw:
            archive = Path(raw)
            with self.producer() as (root, verifier, expected):
                owner = root
                manifest = publisher.capture_producer_reports(
                    root, verifier, archive, "unit-context"
                )
            self.assertFalse(owner.exists())
            target = archive / "forwarded"
            target.mkdir()
            (target / "sandbox-coding.json").write_bytes(b'{"result":"PASS","stale":true}\n')
            actual = publisher.forward_functional_producers(manifest, target)
            self.assertEqual(set(actual), set(expected))
            for name, content in expected.items():
                self.assertEqual((target / name).read_bytes(), content)
                self.assertEqual(actual[name]["result"], "FAIL")
            self.assertFalse((target / verifier.name).exists())
            self.assertFalse((target / "unselected-private-data.json").exists())

    def test_bad_archived_input_never_partially_overwrites_any_prior_functional_target(self):
        publisher = harness("run_full_verification")
        for mode in ("corrupt", "refused", "path", "private"):
            with (
                self.subTest(mode=mode),
                self.producer() as (root, verifier, _expected),
                tempfile.TemporaryDirectory(prefix="iacode-g7-forward-refusal-") as raw,
            ):
                archive = Path(raw)
                manifest = publisher.capture_producer_reports(
                    root, verifier, archive, "unit-context"
                )
                document = json.loads(manifest.read_bytes())
                row = next(
                    item
                    for item in document["reports"]
                    if item["producerName"] == "sandbox-tool-result-origin.json"
                )
                if mode == "corrupt":
                    (archive / row["archive"]).write_bytes(b"corrupt")
                elif mode == "refused":
                    document["refusedReports"].append({"reason": "SECRET_MATERIAL"})
                elif mode == "path":
                    row["archive"] = "../outside.json"
                else:
                    private = json.dumps({"unsafe": "gh" + "p_" + "r" * 20}).encode()
                    (archive / row["archive"]).write_bytes(private)
                    row["bytes"], row["sha256"] = len(private), hashlib.sha256(private).hexdigest()
                manifest.write_text(json.dumps(document), encoding="utf-8")
                target = archive / "forwarded"
                target.mkdir()
                sentinel = target / "quality-unit.json"
                original = b'{"result":"PASS","prior":"must-remain"}\n'
                sentinel.write_bytes(original)
                with self.assertRaises(RuntimeError):
                    publisher.forward_functional_producers(manifest, target)
                self.assertEqual(sentinel.read_bytes(), original)
                self.assertEqual({path.name for path in target.iterdir()}, {sentinel.name})

    def test_directory_or_hardlinked_output_is_refused_before_any_forwarding_effect(self):
        publisher = harness("run_full_verification")
        for mode in ("directory", "hardlink"):
            with (
                self.subTest(mode=mode),
                self.producer() as (root, verifier, _expected),
                tempfile.TemporaryDirectory(prefix="iacode-g7-forward-target-") as raw,
            ):
                archive = Path(raw)
                manifest = publisher.capture_producer_reports(
                    root, verifier, archive, "unit-context"
                )
                target = archive / "forwarded"
                target.mkdir()
                sentinel = target / "quality-unit.json"
                original = b'{"prior":"must-remain"}\n'
                sentinel.write_bytes(original)
                bad = target / "sandbox-tool-result-origin.json"
                outside = archive / "other-owned-file.json"
                outside.write_bytes(original)
                if mode == "directory":
                    bad.mkdir()
                else:
                    os.link(outside, bad)
                    self.assertGreater(bad.stat().st_nlink, 1)
                with self.assertRaises(RuntimeError):
                    publisher.forward_functional_producers(manifest, target)
                self.assertEqual(sentinel.read_bytes(), original)
                self.assertEqual(outside.read_bytes(), original)

    def test_verifier_consumer_uses_durable_original_not_a_second_temporary_read(self):
        publisher = harness("run_full_verification")
        with (
            self.producer() as (root, verifier, _expected),
            tempfile.TemporaryDirectory(prefix="iacode-g7-verifier-original-") as raw,
        ):
            original = {
                "result": "FAIL",
                "stages": [
                    {"name": stage.name, "result": "FAIL"}
                    for stage in publisher.build_stages(False)
                ],
            }
            verifier.write_text(json.dumps(original), encoding="utf-8")
            capture = publisher.capture_producer_reports

            def capture_then_remove(*arguments):
                manifest = capture(*arguments)
                verifier.unlink()
                return manifest

            with patch.object(
                publisher, "capture_producer_reports", side_effect=capture_then_remove
            ):
                observed, summary, manifest = publisher.collect_producer_observations(
                    root, verifier, Path(raw), "unit-context"
                )
            self.assertFalse(verifier.exists())
            self.assertEqual(observed, original)
            self.assertEqual(summary, (len(original["stages"]), 0, len(original["stages"])))
            self.assertTrue(manifest.is_file())


class Gate7RawReworkContextTests(unittest.TestCase):
    def test_every_original_context_is_inert_byte_bound_and_protected_by_real_git_attributes(self):
        importer = harness("import_rework_contexts")
        checkpoint = importer.CHECKPOINT
        document = json.loads((checkpoint / "REWORK-CONTEXT-ARCHIVE.json").read_bytes())
        original = checkpoint / document["sourceInventory"]
        raw = original.read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), importer.EXPECTED_INVENTORY_SHA256)
        self.assertEqual(len(raw), importer.EXPECTED_INVENTORY_BYTES)
        inventory = json.loads(raw)
        self.assertFalse(document["activeSourceOrDocumentation"])
        self.assertFalse(document["configurationIncluded"])
        self.assertFalse(document["gateVerdictGranted"])
        self.assertFalse(document["independentValidation"])
        expected = {
            (row["context"], row["source"], row["bytes"], row["sha256"])
            for row in inventory["files"]
        }
        actual = {
            (row["context"], row["originalRelativePath"], row["bytes"], row["sha256"])
            for row in document["files"]
            if row["context"] != "ORIGINAL_TRANSFER_INVENTORY"
        }
        self.assertEqual(actual, expected)
        self.assertEqual(len(document["files"]), len(inventory["files"]) + 1)
        paths = []
        for row in document["files"]:
            path = checkpoint / row["archive"]
            self.assertTrue(path.resolve().is_relative_to((checkpoint / "attempts").resolve()))
            self.assertEqual(path.suffix, ".raw")
            content = path.read_bytes()
            self.assertGreater(len(content), 0)
            self.assertEqual(len(content), row["bytes"])
            self.assertEqual(hashlib.sha256(content).hexdigest(), row["sha256"])
            paths.append(path.relative_to(ROOT).as_posix())
        observed = subprocess.run(
            ["git", "check-attr", "text", "--", *paths],
            cwd=ROOT,
            capture_output=True,
            check=True,
            text=True,
            encoding="utf-8",
        ).stdout.splitlines()
        self.assertEqual(len(observed), len(paths))
        self.assertTrue(all(line.endswith(": text: unset") for line in observed))


if __name__ == "__main__":
    unittest.main()
