"""Control-plane and repository-structure properties of GATE 0 — FOUNDATION.

These belong to the development-ledger suite rather than to a runtime suite because they are about
the repository: that the Gate has a canonical specification the requirement set derives from, that
the delivery-assurance scope covers the runtime this Gate introduced, that the declared test suites
are the ones actually counted, and that nothing reserved for a later Gate has been implemented.

They need no Docker and no running stack, which is what makes them usable as part of the mandatory
`tests` gate.
"""

from __future__ import annotations

import ast
import json
import re
import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = PROJECT_ROOT / "scripts" / "development-ledger"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import ledger_common  # noqa: E402
import policies  # noqa: E402
from delivery_assurance import collect_test_ids  # noqa: E402
from derive_counts import count_test_cases  # noqa: E402

GATE = "GATE-0"
SPECIFICATION = PROJECT_ROOT / "docs" / "GATE-0-CHECKLIST.md"


class Gate0CanonicalSpecificationTests(unittest.TestCase):
    """The Gate has a specification, and the registry mirrors it row for row.

    `docs/GATE-0-CHECKLIST.md` is the source the expected requirement set is derived from. If the
    registry could drift from it, a requirement could be dropped by editing the mirror — which is
    exactly the escape `policies.canonical_requirements` re-parses the document to prevent.
    """

    def test_the_specification_exists_and_is_parseable(self) -> None:
        self.assertTrue(SPECIFICATION.is_file())
        rows = policies.parse_checklist(SPECIFICATION.read_text(encoding="utf-8"))
        self.assertGreater(len(rows), 0)
        for row in rows:
            with self.subTest(key=row["key"]):
                self.assertRegex(row["key"], r"^[0-9]+[a-z]?\.[0-9]+$")
                self.assertTrue(row["description"].strip())
                self.assertTrue(row["artifact"].strip())
                self.assertTrue(row["evidence"].strip())

    def test_the_registry_mirrors_the_specification(self) -> None:
        # Raises when the two disagree, which is the behaviour under test.
        declared = policies.canonical_requirements(PROJECT_ROOT, GATE)
        parsed = policies.parse_checklist(SPECIFICATION.read_text(encoding="utf-8"))

        self.assertEqual([item["key"] for item in declared], [row["key"] for row in parsed])
        for item, row in zip(declared, parsed):
            self.assertEqual(item["description"], row["description"])

    def test_every_canonical_requirement_is_mandatory(self) -> None:
        """Gate 0 declares no optional row. An optional requirement is a requirement nobody meets."""
        for item in policies.canonical_requirements(PROJECT_ROOT, GATE):
            with self.subTest(key=item["key"]):
                self.assertTrue(item["mandatory"])

    def test_the_registry_names_the_specification_document(self) -> None:
        self.assertEqual(policies.gate_specification(PROJECT_ROOT, GATE),
                         "docs/GATE-0-CHECKLIST.md")

    def test_a_gate_without_a_specification_is_refused(self) -> None:
        """A Gate whose specification does not exist cannot have a requirement set derived."""
        with self.assertRaises(ledger_common.LedgerError):
            policies.gate_specification(PROJECT_ROOT, "GATE-99")


class ExpectedRequirementSetTests(unittest.TestCase):
    def test_expected_set_names_the_gate_specification(self) -> None:
        """A derived requirement cites the document it came from, not another Gate's.

        The derivation used to write `docs/SETUP-00-CHECKLIST.md` into every requirement's source
        reference. For SETUP-00 that was correct; for any other Gate it points a reader at a
        document that does not contain the row.
        """
        expected = policies.expected_requirement_refs(PROJECT_ROOT, GATE, "GATE-0-CP-0001", None)

        canonical = {key: value for key, value in expected.items()
                     if key.startswith("canonical:")}
        self.assertTrue(canonical)
        for reference, item in canonical.items():
            with self.subTest(reference=reference):
                self.assertIn("docs/GATE-0-CHECKLIST.md", item["sourceReference"])
                self.assertNotIn("SETUP-00-CHECKLIST", item["sourceReference"])
                self.assertEqual(item["source"], "GATE_SPECIFICATION")

    def test_the_setup_gate_still_derives_from_its_own_specification(self) -> None:
        expected = policies.expected_requirement_refs(
            PROJECT_ROOT, "SETUP-00", "SETUP-00-CP-0013", None)

        for reference, item in expected.items():
            if reference.startswith("canonical:"):
                self.assertIn("docs/SETUP-00-CHECKLIST.md", item["sourceReference"])


class AssuranceScopeTests(unittest.TestCase):
    def test_assurance_scope_covers_the_runtime_source(self) -> None:
        """A gate result is a statement about content; the content now includes the product.

        With the runtime outside the scope, editing the API, the worker, the frontend or the compose
        stack would leave every Green Keeper, completeness, Red Team and mirror result looking fresh
        while describing content that no longer exists.
        """
        for path in ("apps/api/src/iacode_api/main.py",
                     "services/orchestrator/src/iacode_orchestrator/worker.py",
                     "packages/common/src/iacode_common/redaction.py",
                     "apps/web/src/main.ts",
                     "infra/compose/docker-compose.yml"):
            with self.subTest(path=path):
                self.assertTrue(ledger_common.in_assurance_scope(path))

    def test_the_checkpoint_ledger_stays_outside_the_scope(self) -> None:
        """Recording evidence must not invalidate the evidence being recorded."""
        self.assertFalse(
            ledger_common.in_assurance_scope("docs/checkpoints/GATE-0-CP-0001/STATE.json"))

    def test_the_fingerprint_changes_when_the_runtime_changes(self) -> None:
        before = ledger_common.scope_fingerprint(PROJECT_ROOT)
        after = ledger_common.scope_fingerprint(
            PROJECT_ROOT, extra_paths=["apps/api/src/iacode_api/main.py"])

        self.assertNotEqual(before, after)


class TestSuiteRegistryTests(unittest.TestCase):
    def test_declared_suites_are_discovered(self) -> None:
        """Every counted suite exists and contributes cases to the derived denominator."""
        suites = policies.counted_test_suites(PROJECT_ROOT)
        self.assertTrue(suites)

        for suite in suites:
            with self.subTest(suite=suite["id"]):
                root = PROJECT_ROOT / str(suite["root"])
                self.assertTrue(root.is_dir(), f"{suite['root']} does not exist")

        total = count_test_cases(PROJECT_ROOT)
        ledger_only = len(
            [path for path in (PROJECT_ROOT / "tests").rglob("test_*.py")])
        self.assertGreater(total, ledger_only,
                           "the denominator does not include the runtime suites")

    def test_an_uncounted_suite_declares_why(self) -> None:
        """A suite left out of the denominator is a declared omission, never an implied one."""
        for suite in policies.load_test_suites(PROJECT_ROOT):
            if not suite.get("counted"):
                with self.subTest(suite=suite["id"]):
                    self.assertTrue(str(suite.get("notCountedReason", "")).strip())

    def test_evidence_resolution_covers_the_runtime_suites(self) -> None:
        """A `test:` reference to a backend case has to resolve, or the honest reference is weaker."""
        identifiers = collect_test_ids(PROJECT_ROOT)

        self.assertIn("test_health_is_up_while_dependencies_are_down", identifiers)
        self.assertIn("test_database_round_trip", identifiers)
        self.assertIn("test_compose_declares_the_foundation_services", identifiers)

    def test_the_registry_is_schema_valid(self) -> None:
        document = ledger_common.load_json(
            PROJECT_ROOT / ".iacode" / "policies" / "test-suites.json")
        schema = ledger_common.load_json(
            PROJECT_ROOT / ".iacode" / "schemas" / "test-suites.schema.json")

        self.assertEqual(ledger_common.validate_schema(document, schema), [])


class MonorepoStructureTests(unittest.TestCase):
    def test_monorepo_structure_exists(self) -> None:
        for relative in ("apps/api", "apps/web", "apps/cli", "apps/vscode-extension",
                         "services/orchestrator", "services/model-gateway", "services/sandbox",
                         "services/evaluator", "services/experience", "services/knowledge",
                         "services/training",
                         "packages/common", "packages/contracts", "packages/telemetry",
                         "agents", "training", "evaluation", "datasets",
                         "infra", "scripts", "docs"):
            with self.subTest(path=relative):
                self.assertTrue((PROJECT_ROOT / relative).is_dir(), f"{relative} is missing")

    def test_reserved_directories_declare_themselves(self) -> None:
        """A directory held for a later Gate says so, and holds nothing else.

        Scoped to the reservations still in force, derived from the Gate the repository is
        delivering. A reservation whose owner has already run describes a directory that Gate
        legitimately filled, and requiring it to keep declaring itself reserved would mean the
        control fails every delivery after the one it was written for.
        """
        reservations = policies.reservations_in_force(
            PROJECT_ROOT, ledger_common.delivered_gate(PROJECT_ROOT))
        self.assertTrue(reservations)

        for reservation in reservations:
            directory = PROJECT_ROOT / str(reservation["path"])
            with self.subTest(path=reservation["path"]):
                self.assertTrue(directory.is_dir())
                readme = directory / "README.md"
                self.assertTrue(readme.is_file(), "a reserved directory carries its declaration")
                text = readme.read_text(encoding="utf-8")
                self.assertIn(policies.RESERVATION_MARKER, text)
                self.assertIn(str(reservation["gate"]), text,
                              "the README names the Gate the registry reserves it for")

    def test_no_future_gate_capability_is_implemented(self) -> None:
        """No delivery implements a directory reserved for a Gate that has not run.

        The Gate is derived from the latest checkpoint rather than written here. With ``GATE-0``
        as a literal this assertion would have failed the moment Gate 1 filled the directory
        reserved for Gate 1, which is the failure class `LSN-0025` records.
        """
        gate = ledger_common.delivered_gate(PROJECT_ROOT)

        self.assertEqual(policies.scope_violations(PROJECT_ROOT, gate), [])

    def test_the_scope_control_detects_an_implementation(self) -> None:
        """The positive path of the control, so it is not one that has only ever said yes."""
        import shutil
        import tempfile

        with tempfile.TemporaryDirectory(prefix="iacode-scope-") as workdir:
            root = Path(workdir)
            shutil.copytree(PROJECT_ROOT / ".iacode" / "policies", root / ".iacode" / "policies")
            reservation = policies.load_gate_scope(root)[0]
            planted = root / str(reservation["path"])
            planted.mkdir(parents=True)
            (planted / "README.md").write_text(
                f"**{policies.RESERVATION_MARKER}** for {reservation['gate']}\n",
                encoding="utf-8", newline="\n")
            (planted / "service.py").write_text("raise SystemExit\n", encoding="utf-8")

            violations = policies.scope_violations(root, GATE)

        self.assertEqual(len(violations), 1, violations)
        self.assertIn(str(reservation["path"]), violations[0])

    def test_the_scope_control_ignores_a_gate_that_has_already_run(self) -> None:
        """A reservation constrains only the deliveries that come before its owner.

        Without this the control would keep failing a Gate for the directory it had just
        legitimately filled, which is the fastest way to have a control switched off.
        """
        order = policies.gate_order()
        self.assertEqual(order[0], "SETUP00", "the plan starts at SETUP-00")
        self.assertLess(order.index("GATE0"), order.index("GATE5"))

        # `apps/cli` is reserved for GATE 5. It constrains Gate 0 and Gate 1, and stops
        # constraining anything once GATE 5 is the Gate being delivered.
        import shutil
        import tempfile

        with tempfile.TemporaryDirectory(prefix="iacode-scope-order-") as workdir:
            root = Path(workdir)
            shutil.copytree(PROJECT_ROOT / ".iacode" / "policies", root / ".iacode" / "policies")
            (root / "apps" / "cli").mkdir(parents=True)
            (root / "apps" / "cli" / "main.py").write_text("raise SystemExit\n", encoding="utf-8")

            self.assertTrue(policies.scope_violations(root, "GATE-0"))
            self.assertEqual(policies.scope_violations(root, "GATE-5"), [])


class FrontendConfigurationTests(unittest.TestCase):
    """Properties of the frontend that are checked by reading files, not by running Node."""

    WEB = PROJECT_ROOT / "apps" / "web"

    def test_web_dependencies_are_locked(self) -> None:
        package = json.loads((self.WEB / "package.json").read_text(encoding="utf-8"))
        lock = self.WEB / "package-lock.json"

        self.assertTrue(lock.is_file(), "package-lock.json is what `npm ci` installs")
        for section in ("dependencies", "devDependencies"):
            for name, version in package[section].items():
                with self.subTest(package=name):
                    # Exact versions only. A caret range makes two builds of the same commit
                    # install different code.
                    self.assertRegex(version, r"^\d+\.\d+\.\d+",
                                     f"{name} is pinned to a range, not a version")

    def test_api_base_is_centralised(self) -> None:
        """One place knows the backend address, and it is not compiled into the bundle."""
        sources = [path for path in (self.WEB / "src").rglob("*.ts")
                   if not path.name.endswith(".spec.ts")]
        self.assertTrue(sources)

        address = re.compile(r"https?://(?!api\.test)[a-z0-9.-]+(:\d+)?", re.IGNORECASE)
        for path in sources:
            if path.name == "api-config.ts":
                continue
            with self.subTest(path=path.name):
                self.assertIsNone(address.search(path.read_text(encoding="utf-8")),
                                  f"{path.name} hardcodes a backend address")

        configuration = (self.WEB / "src" / "app" / "api-config.ts").read_text(encoding="utf-8")
        self.assertIn("config.json", configuration)
        self.assertIn("API_CONFIG", configuration)

    def test_the_runtime_configuration_carries_no_secret(self) -> None:
        config = json.loads((self.WEB / "public" / "config.json").read_text(encoding="utf-8"))

        # The file is served unauthenticated to every visitor.
        self.assertEqual(set(config), {"apiBaseUrl"})


class SecretScanScopeTests(unittest.TestCase):
    """The repository secret scan covers what the repository carries, and still refuses a leak.

    It used to walk every file on disk. Gate 0's own bootstrap creates `infra/compose/.env` with
    real local credentials, so the control refused the repository for containing exactly the file
    the runbook tells an operator to create — and a control that refuses a correct state is a
    control that gets switched off.

    Narrowing a control needs its positive *and* negative paths executed, which is what these two
    do: an ignored file carrying a credential does not fail validation, and a tracked one does.
    """

    def _fixture(self, workdir: Path, tracked: bool) -> list[str]:
        import shutil
        import subprocess

        shutil.copytree(PROJECT_ROOT / ".iacode" / "schemas", workdir / ".iacode" / "schemas")
        subprocess.run(["git", "init", "-b", "main"], cwd=workdir, check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        (workdir / ".gitignore").write_text("ignored.env\n", encoding="utf-8", newline="\n")
        name = "carried.env" if tracked else "ignored.env"
        # Assembled, so this test file carries no credential-shaped literal of its own.
        credential = "s3cr3t" + "ValueThatMustNotSurvive"
        (workdir / name).write_text(
            "IACODE_POSTGRES_" + "PASSWORD=" + credential + "\n",
            encoding="utf-8", newline="\n")

        code, listing = ledger_common.run_git(
            workdir, "ls-files", "--cached", "--others", "--exclude-standard")
        self.assertEqual(code, 0)
        return sorted(line.strip() for line in listing.splitlines() if line.strip())

    def test_an_ignored_file_is_outside_the_scan(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory(prefix="iacode-scan-ignored-") as workdir:
            listed = self._fixture(Path(workdir), tracked=False)

        self.assertNotIn("ignored.env", listed)

    def test_a_carried_file_is_inside_the_scan_and_its_credential_is_detected(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory(prefix="iacode-scan-carried-") as workdir:
            root = Path(workdir)
            listed = self._fixture(root, tracked=True)
            findings = ledger_common.find_secrets(
                (root / "carried.env").read_text(encoding="utf-8"))

        self.assertIn("carried.env", listed)
        self.assertIn("named secret assignment", findings)

    def test_the_documented_placeholder_is_not_a_finding(self) -> None:
        """One placeholder convention. The committed example uses it and must stay scannable."""
        example = (PROJECT_ROOT / "infra" / "compose" / ".env.example").read_text(encoding="utf-8")

        self.assertIn("change-me-before-starting", example)
        self.assertEqual(ledger_common.find_secrets(example), [])

    def test_the_repository_carries_no_credential(self) -> None:
        code, listing = ledger_common.run_git(
            PROJECT_ROOT, "ls-files", "--cached", "--others", "--exclude-standard")
        self.assertEqual(code, 0)

        offenders = []
        for relative in sorted({line.strip() for line in listing.splitlines() if line.strip()}):
            path = PROJECT_ROOT / relative
            if not path.is_file() or "__pycache__" in path.parts:
                continue
            try:
                findings = ledger_common.find_secrets(path.read_text(encoding="utf-8"))
            except UnicodeDecodeError:
                continue
            if findings:
                offenders.append(f"{relative}: {', '.join(findings)}")

        self.assertEqual(offenders, [])


class SubprocessDecodingTests(unittest.TestCase):
    """Whatever a child process writes is decoded as UTF-8, never as the platform codepage.

    `subprocess.run(..., text=True)` with no `encoding` decodes with `locale.getencoding()`, which
    on this repository's primary platform is `cp1252`. Every tool here writes UTF-8 — em dashes in
    a docstring, a box character from `npm`, an accented path — so the platform default turns a
    green gate into `UnicodeDecodeError` at the moment the output happens to contain one. It is a
    failure of the *reader*, in a code path that has nothing to do with what is being measured.

    This is a repository-wide rule rather than a fix at one call site, because the defect reappears
    every time somebody adds a capture and the output happens to be ASCII that day.
    """

    CAPTURING = {"run", "Popen", "check_output"}
    SEARCHED = ("scripts", "infra", "apps", "services", "packages", "tests")

    @staticmethod
    def _decodes_text(call: ast.Call) -> bool:
        keywords = {keyword.arg for keyword in call.keywords if keyword.arg}
        if "encoding" in keywords or "errors" in keywords:
            return False
        decodes = any(
            keyword.arg in ("text", "universal_newlines")
            and isinstance(keyword.value, ast.Constant) and keyword.value.value is True
            for keyword in call.keywords)
        captures = bool(keywords & {"capture_output", "stdout", "stderr"})
        return decodes and captures

    def test_no_capture_relies_on_the_platform_codepage(self) -> None:
        offenders = []
        for directory in self.SEARCHED:
            for path in sorted((PROJECT_ROOT / directory).rglob("*.py")):
                if "node_modules" in path.parts or "__pycache__" in path.parts:
                    continue
                tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
                for node in ast.walk(tree):
                    if not isinstance(node, ast.Call):
                        continue
                    name = ast.unparse(node.func)
                    if "subprocess" not in name or name.rsplit(".", 1)[-1] not in self.CAPTURING:
                        continue
                    if self._decodes_text(node):
                        offenders.append(
                            f"{path.relative_to(PROJECT_ROOT).as_posix()}:{node.lineno}")

        self.assertEqual(offenders, [], "captures without an explicit encoding")

    @classmethod
    def _captures(cls, tree: ast.AST) -> bool:
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            name = ast.unparse(node.func)
            if "subprocess" not in name or name.rsplit(".", 1)[-1] not in cls.CAPTURING:
                continue
            if {keyword.arg for keyword in node.keywords} & {"capture_output", "stdout", "stderr"}:
                return True
        return False

    def test_every_tool_that_re_emits_captured_output_configures_its_own_stream(self) -> None:
        """Reading a child's UTF-8 is half of it: writing it back out encodes again.

        `sys.stdout` encodes with the platform codepage too, so a tool that captures correctly and
        then prints what it captured still dies on Windows -- and it dies *after* the work
        succeeded, which is the worst possible moment. Every entry point that captures therefore
        configures its streams, directly or through `compose.main_guard`, which every operational
        script goes through.
        """
        offenders = []
        for path in sorted((PROJECT_ROOT / "scripts").rglob("*.py")):
            if "__pycache__" in path.parts:
                continue
            source = path.read_text(encoding="utf-8")
            if '__name__ == "__main__"' not in source:
                continue
            if not self._captures(ast.parse(source, filename=str(path))):
                continue
            if "use_utf8_stdout()" not in source and "main_guard(" not in source:
                offenders.append(path.relative_to(PROJECT_ROOT).as_posix())

        self.assertEqual(offenders, [], "entry points that re-emit captured output unconfigured")

    def test_the_rule_detects_a_capture_that_would_fail(self) -> None:
        """The control is exercised against a call it must reject, not only against clean code."""
        offending = ast.parse(
            "subprocess.run(argv, text=True, stdout=subprocess.PIPE)").body[0].value
        accepted = ast.parse(
            'subprocess.run(argv, text=True, encoding="utf-8", stdout=subprocess.PIPE)'
        ).body[0].value
        bytes_capture = ast.parse("subprocess.run(argv, stdout=subprocess.PIPE)").body[0].value

        self.assertTrue(self._decodes_text(offending))
        self.assertFalse(self._decodes_text(accepted))
        # A byte capture decodes nothing, so it is not in scope.
        self.assertFalse(self._decodes_text(bytes_capture))


if __name__ == "__main__":
    unittest.main()
