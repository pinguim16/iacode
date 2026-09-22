"""Control-plane and repository-structure properties of GATE 1 — MODEL GATEWAY.

What this suite can check is what can be read from the repository without a runtime: that the Gate's
canonical specification exists and is mirrored, that the registries name what the Gate introduced,
that the boundary the Gate is *for* is not crossed anywhere in the tree, and that the previous
Gate's migrations were not edited.

What it deliberately does not check is behaviour. The gateway's own suite runs inside the image that
has its dependencies, and duplicating a behavioural assertion here with a text search would be a
second, weaker control that disagrees with the first.
"""

from __future__ import annotations

import ast
import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "development-ledger"))

import ledger_common  # noqa: E402
import policies  # noqa: E402
from delivery_assurance import collect_test_ids  # noqa: E402
from derive_counts import count_pytest_cases  # noqa: E402

GATE = "GATE-1"
SPECIFICATION = PROJECT_ROOT / "docs" / "GATE-1-CHECKLIST.md"
GATEWAY_ROOT = PROJECT_ROOT / "services" / "model-gateway"
GATEWAY_SOURCE = GATEWAY_ROOT / "src" / "iacode_model_gateway"


class Gate1CanonicalSpecificationTests(unittest.TestCase):
    """The Gate's requirement set comes from a document, re-parsed, and from nothing else."""

    def test_the_specification_exists_and_parses(self) -> None:
        self.assertTrue(SPECIFICATION.is_file())
        rows = policies.parse_checklist(SPECIFICATION.read_text(encoding="utf-8"))

        self.assertGreater(len(rows), 50, "the specification parsed as almost nothing")
        for row in rows:
            with self.subTest(key=row["key"]):
                self.assertTrue(row["description"].strip())
                self.assertTrue(row["artifact"].strip())
                self.assertTrue(row["evidence"].strip())

    def test_the_registry_mirrors_the_specification_row_for_row(self) -> None:
        """`canonical_requirements` re-parses the document and refuses a mirror that drifted."""
        declared = policies.canonical_requirements(PROJECT_ROOT, GATE)
        parsed = policies.parse_checklist(SPECIFICATION.read_text(encoding="utf-8"))

        self.assertEqual([item["key"] for item in declared], [row["key"] for row in parsed])
        self.assertTrue(all(item.get("mandatory") for item in declared))

    def test_a_dropped_row_is_refused(self) -> None:
        """The positive path of the control, so it is not one that has only ever said yes."""
        import shutil
        import tempfile

        with tempfile.TemporaryDirectory(prefix="iacode-gate1-spec-") as workdir:
            root = Path(workdir)
            (root / "docs").mkdir(parents=True)
            (root / ".iacode" / "policies").mkdir(parents=True)
            shutil.copy(SPECIFICATION, root / "docs" / "GATE-1-CHECKLIST.md")
            registry = json.loads(
                (PROJECT_ROOT / ".iacode" / "policies"
                 / "canonical-requirements.json").read_text(encoding="utf-8"))
            for entry in registry["gates"]:
                if entry["gate"] == GATE:
                    entry["requirements"] = entry["requirements"][:-1]
            (root / ".iacode" / "policies" / "canonical-requirements.json").write_text(
                json.dumps(registry), encoding="utf-8")

            with self.assertRaises(ledger_common.LedgerError):
                policies.canonical_requirements(root, GATE)

    def test_the_derived_set_names_this_gates_specification(self) -> None:
        expected = policies.expected_requirement_refs(
            PROJECT_ROOT, GATE, "GATE-1-CP-0001", None)

        self.assertTrue(expected)
        canonical = [item for reference, item in expected.items()
                     if reference.startswith("canonical:")]
        self.assertTrue(canonical)
        for item in canonical:
            with self.subTest(reference=item["sourceRef"]):
                self.assertIn("docs/GATE-1-CHECKLIST.md", item["sourceReference"])

    def test_the_gate_specification_is_read_from_the_registry(self) -> None:
        self.assertEqual(policies.gate_specification(PROJECT_ROOT, GATE),
                         "docs/GATE-1-CHECKLIST.md")


class Gate1RegistryTests(unittest.TestCase):
    """Every registry the Gate grows says so, because nothing else makes a new control mandatory."""

    def test_the_gateway_gate_is_in_the_mandatory_set(self) -> None:
        mandatory = policies.mandatory_gates(PROJECT_ROOT)

        self.assertIn("gatewayTests", mandatory)
        definition = policies.gate_definitions(PROJECT_ROOT)["gatewayTests"]
        script = PROJECT_ROOT / definition["command"][-1]
        self.assertTrue(script.is_file(), f"{script} does not exist")

    def test_gateway_suite_is_declared_and_discovered(self) -> None:
        """A suite that is not declared contributes nothing to the denominator."""
        suites = {suite["id"]: suite for suite in policies.counted_test_suites(PROJECT_ROOT)}

        self.assertIn("gateway", suites)
        self.assertEqual(suites["gateway"]["root"], "services/model-gateway/tests")
        discovered = count_pytest_cases(PROJECT_ROOT, suites["gateway"]["root"])
        self.assertGreater(discovered, 100, "the gateway suite discovered almost nothing")

    def test_every_declared_suite_still_discovers_cases(self) -> None:
        for suite in policies.counted_test_suites(PROJECT_ROOT):
            with self.subTest(suite=suite["id"]):
                root = PROJECT_ROOT / str(suite["root"])
                self.assertTrue(root.is_dir(), f"{suite['root']} does not exist")


class Gate1ScopeTests(unittest.TestCase):
    """The directory the Foundation reserved is the one this Gate filled."""

    def test_every_reservation_is_out_of_force_for_the_gate_that_owns_it(self) -> None:
        """The general property. The Gate 0 formulation named one Gate and expired with it."""
        reservations = policies.load_gate_scope(PROJECT_ROOT)
        self.assertTrue(reservations, "the scope registry declares nothing")

        for reservation in reservations:
            path, owner = str(reservation["path"]), str(reservation["gate"])
            in_force = {str(item["path"]) for item
                        in policies.reservations_in_force(PROJECT_ROOT, owner)}
            with self.subTest(path=path):
                self.assertNotIn(path, in_force)

    def test_model_gateway_reservation_is_consumed_by_its_owner(self) -> None:
        """Owned by the Gate being delivered, so it no longer constrains it.

        The Gate is derived rather than named: a control that names one stops being a control at
        the next Gate, which is the failure `LSN-0037` records.
        """
        current = ledger_common.delivered_gate(PROJECT_ROOT)
        owners = {str(item["path"]): str(item["gate"])
                  for item in policies.load_gate_scope(PROJECT_ROOT)}

        # Normalised on both sides, because the registry writes "GATE 1" and the checkpoint
        # writes "GATE-1"; `reservations_in_force` compares them the same way.
        self.assertEqual(ledger_common.normalize_gate(owners["services/model-gateway"]),
                         ledger_common.normalize_gate(current))
        reserved = {str(item["path"]) for item
                    in policies.reservations_in_force(PROJECT_ROOT, current)}
        self.assertNotIn("services/model-gateway", reserved)
        # A later Gate's reservation still constrains this one, which is what the registry is for.
        self.assertIn("services/sandbox", reserved)

    def test_gateway_readme_describes_the_delivery(self) -> None:
        readme = (GATEWAY_ROOT / "README.md").read_text(encoding="utf-8")

        self.assertNotIn(policies.RESERVATION_MARKER, readme)
        self.assertIn("Model Gateway", readme)
        for topic in ("provider", "protocol", "route", "stream"):
            with self.subTest(topic=topic):
                self.assertIn(topic, readme.lower())

    def test_no_future_gate_capability_is_implemented(self) -> None:
        self.assertEqual(
            policies.scope_violations(PROJECT_ROOT,
                                      ledger_common.delivered_gate(PROJECT_ROOT)), [])


class GatewayBoundaryTests(unittest.TestCase):
    """The boundary this Gate exists to draw, checked by reading the tree."""

    #: Provider-specific vocabulary. A consumer that knows one of these words is a consumer coupled
    #: to one vendor's API, which is the coupling the Gate is for.
    PROVIDER_WORDS = (
        "chat/completions", "chat_completions", "anthropic-version", "x-api-key",
        "stream_options", "prompt_tokens", "completion_tokens", "input_json_delta",
        "content_block_delta", "response.output_text", "tool_use", "max_completion_tokens",
    )

    #: Where that vocabulary is allowed to appear: the adapter layer and the suites that test it.
    ADAPTER_PREFIXES = (
        "services/model-gateway/src/iacode_model_gateway/protocols/",
        "services/model-gateway/src/iacode_model_gateway/catalog/normalize.py",
        "services/model-gateway/tests/",
        "docs/",
    )

    def _tracked(self, *prefixes: str) -> list[Path]:
        code, listing = ledger_common.run_git(
            PROJECT_ROOT, "ls-files", "--cached", "--others", "--exclude-standard")
        self.assertEqual(code, 0)
        paths = []
        for line in listing.splitlines():
            relative = line.strip().replace("\\", "/")
            if not relative or not relative.startswith(prefixes):
                continue
            path = PROJECT_ROOT / relative
            if path.is_file() and path.suffix in (".py", ".ts", ".html", ".json", ".md"):
                paths.append(path)
        return paths

    def test_no_provider_specific_name_escapes_the_adapter_layer(self) -> None:
        offenders: list[str] = []
        for path in self._tracked("apps/", "packages/", "services/"):
            relative = str(path.relative_to(PROJECT_ROOT)).replace("\\", "/")
            if relative.startswith(self.ADAPTER_PREFIXES):
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            for word in self.PROVIDER_WORDS:
                if word in text:
                    offenders.append(f"{relative}: {word}")

        self.assertEqual(offenders, [], f"provider vocabulary outside the adapters: {offenders}")

    def test_the_adapter_layer_is_where_that_vocabulary_lives(self) -> None:
        """The negative control: the words exist, so the search above is not vacuous."""
        protocols = GATEWAY_SOURCE / "protocols"
        corpus = "\n".join(path.read_text(encoding="utf-8")
                           for path in sorted(protocols.glob("*.py")))

        for word in ("chat/completions", "anthropic-version", "x-api-key", "stream_options"):
            with self.subTest(word=word):
                self.assertIn(word, corpus)

    def test_gateway_imports_no_application_module(self) -> None:
        """The dependency points inward: the application composes the gateway, never the reverse."""
        offenders: list[str] = []
        for path in sorted(GATEWAY_SOURCE.rglob("*.py")):
            if "__pycache__" in path.parts:
                continue
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                names: list[str] = []
                if isinstance(node, ast.Import):
                    names = [alias.name for alias in node.names]
                elif isinstance(node, ast.ImportFrom) and node.module:
                    names = [node.module]
                for name in names:
                    if name.split(".")[0] in ("iacode_api", "iacode_orchestrator", "fastapi",
                                              "sqlalchemy", "starlette", "alembic"):
                        offenders.append(f"{path.name}: {name}")

        self.assertEqual(offenders, [], f"the gateway reaches into the application: {offenders}")

    def test_the_provider_policy_declares_names_and_no_values(self) -> None:
        document = json.loads(
            (PROJECT_ROOT / ".iacode" / "policies" / "providers.json").read_text(encoding="utf-8"))

        self.assertTrue(document["providers"])
        for provider in document["providers"]:
            with self.subTest(provider=provider["provider_id"]):
                for field in ("base_url_env", "credential_env"):
                    value = provider[field]
                    self.assertEqual(value, value.upper())
                    self.assertTrue(value.startswith("IACODE_"))
                self.assertNotIn("api_key", provider)
                self.assertNotIn("credential", provider)
                self.assertTrue(provider["protocols"])

    def test_the_route_policy_asserts_no_measured_preference(self) -> None:
        """An alias with candidates would be a claim this project has not earned."""
        document = json.loads(
            (PROJECT_ROOT / ".iacode" / "policies"
             / "model-routes.json").read_text(encoding="utf-8"))

        self.assertTrue(document["routes"])
        for route in document["routes"]:
            with self.subTest(alias=route["alias"]):
                self.assertEqual(route["candidates"], [],
                                 "a configured candidate is a preference nobody measured")
        self.assertEqual(document["allowUnknownCapability"], [])


class Gate1MigrationTests(unittest.TestCase):
    """A schema change is a new migration; a previous Gate's is not edited."""

    VERSIONS = PROJECT_ROOT / "apps" / "api" / "migrations" / "versions"

    def test_previous_migrations_are_unmodified(self) -> None:
        code, listing = ledger_common.run_git(PROJECT_ROOT, "rev-parse", "HEAD")
        if code != 0:
            self.skipTest("not a Git checkout")

        for path in sorted(self.VERSIONS.glob("*.py")):
            relative = str(path.relative_to(PROJECT_ROOT)).replace("\\", "/")
            committed = subprocess.run(
                ["git", "show", f"HEAD:{relative}"], cwd=str(PROJECT_ROOT), text=True,
                encoding="utf-8", errors="replace",
                stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=False)
            if committed.returncode != 0:
                continue  # A migration this delivery adds has no committed version yet.
            with self.subTest(migration=path.name):
                self.assertEqual(
                    committed.stdout.replace("\r\n", "\n"),
                    path.read_text(encoding="utf-8"),
                    f"{path.name} was edited; a schema change is a new migration")

    def test_the_new_migration_declares_its_parent(self) -> None:
        heads = []
        parents = set()
        for path in sorted(self.VERSIONS.glob("*.py")):
            text = path.read_text(encoding="utf-8")
            identifier = re.search(r'^revision: str = "([^"]+)"', text, re.MULTILINE)
            parent = re.search(r'^down_revision: str \| None = "([^"]+)"', text, re.MULTILINE)
            self.assertIsNotNone(identifier, f"{path.name} declares no revision")
            if parent:
                parents.add(parent.group(1))
            heads.append(identifier.group(1))

        remaining = [item for item in heads if item not in parents]
        self.assertEqual(len(remaining), 1, f"the migration chain has {len(remaining)} heads")

    def test_the_migration_stores_no_content_column(self) -> None:
        text = (self.VERSIONS / "0002_model_gateway.py").read_text(encoding="utf-8")

        for forbidden in ('"prompt"', '"messages"', '"completion"', '"response"',
                          '"api_key"', '"credential"'):
            with self.subTest(column=forbidden):
                self.assertNotIn(forbidden, text)


if __name__ == "__main__":  # pragma: no cover - convenience
    unittest.main()


class ProviderConfigurationTests(unittest.TestCase):
    """Row 5.1: what the versioned provider policy may and may not carry."""

    def test_provider_configuration_carries_no_credential(self) -> None:
        document = json.loads(
            (PROJECT_ROOT / ".iacode" / "policies" / "providers.json").read_text(encoding="utf-8"))
        providers = document["providers"]
        self.assertTrue(providers, "the provider policy declares nothing")

        for entry in providers:
            with self.subTest(provider=entry.get("provider_id")):
                for field in ("provider_id", "adapter", "enabled", "base_url_env",
                              "credential_env", "models_path", "protocols"):
                    self.assertIn(field, entry, f"{field} is not declared")
                self.assertIsInstance(entry["enabled"], bool)
                self.assertTrue(entry["protocols"], "a provider that speaks no protocol")

                # The two address-and-credential fields hold the NAME of a variable. A value here
                # would be a published value: this file is committed.
                for field in ("base_url_env", "credential_env"):
                    value = str(entry[field])
                    self.assertTrue(_VARIABLE_NAME.match(value),
                                    f"{field} is {value!r}, which is not a variable name")

                # No field may *hold* a credential. The rule is about shapes rather than about
                # words: `credential_env` legitimately carries the string
                # `IACODE_DEVWORLD_API_KEY`, which is a name, while a key is an opaque run of
                # characters nobody would type twice.
                for field, value in entry.items():
                    if field.endswith("_env") or not isinstance(value, str):
                        continue
                    with self.subTest(field=field):
                        self.assertIsNone(
                            _CREDENTIAL_SHAPE.search(value),
                            f"{field} holds something shaped like a credential")

                # And no field may be a credential slot at all: a name without the `_env` suffix
                # is a place for a value, and a place for a value eventually holds one.
                for field in entry:
                    with self.subTest(field=field):
                        self.assertFalse(
                            _CREDENTIAL_SLOT.match(field),
                            f"{field} is a credential slot; only a `*_env` name belongs here")


class TrainingRightsTests(unittest.TestCase):
    """Row 10.7: nothing this Gate persists becomes training data."""

    def test_gate_one_records_no_training_eligible_data(self) -> None:
        checkpoint = PROJECT_ROOT / "docs" / "checkpoints" / _delivering_checkpoint()
        provenance = json.loads((checkpoint / "PROVENANCE.json").read_text(encoding="utf-8"))
        artifacts = provenance["artifacts"]
        self.assertTrue(artifacts, "the checkpoint claims no artifact at all")

        for artifact in artifacts:
            with self.subTest(artifact=artifact.get("artifact")):
                rights = artifact["rights"]
                self.assertFalse(rights["trainingAllowed"])
                self.assertFalse(rights["distillationAllowed"])
                self.assertFalse(rights["ragAllowed"])

        # Every lesson this Gate wrote carries the same default, because a lesson is an artifact.
        for line in (PROJECT_ROOT / ".iacode" / "memory"
                     / "lessons.jsonl").read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            lesson = json.loads(line)
            with self.subTest(lesson=lesson["lessonId"]):
                eligibility = lesson["trainingEligibility"]
                self.assertFalse(eligibility["trainingAllowed"])
                self.assertFalse(eligibility["distillationAllowed"])

        # And the gateway persists no content that could become training data in the first place.
        models = (PROJECT_ROOT / "apps" / "api" / "src" / "iacode_api" / "db"
                  / "models.py").read_text(encoding="utf-8")
        call_table = models.partition("class ModelCall")[2].partition("\nclass ")[0]
        for column in ("prompt", "messages", "completion", "content", "response"):
            with self.subTest(column=column):
                self.assertNotIn(f'"{column}"', call_table)
                self.assertNotIn(f"    {column}:", call_table)


class LiveSmokeContractTests(unittest.TestCase):
    """Rows 14.4, 14.5 and 14.8: what the live check does, proved without calling a provider."""

    def test_absent_smoke_model_fails_rather_than_substitutes(self) -> None:
        smoke = _gateway_smoke()
        answers = {
            "/api/v1/gateway/models/sync": {"outcomes": [
                {"provider": "devworld", "added": 2, "updated": 0, "deactivated": 0,
                 "unchanged": 0, "errors": []}]},
            "/api/v1/gateway/models": {"total": 2, "models": [
                {"model": "a-model-that-is-not-the-smoke-model", "displayName": "A",
                 "capabilities": {}},
                {"model": "another-one", "displayName": "B", "capabilities": {}}]},
        }

        def answer(url, payload=None, *, timeout, accept_status=(200,)):
            for path, body in answers.items():
                if path in url:
                    return 200, body
            raise AssertionError(f"the check reached an unexpected address: {url}")

        original = smoke.request_json
        smoke.request_json = answer
        try:
            with self.assertRaises(smoke.StackError) as raised:
                smoke.check_catalog("http://127.0.0.1:1", "devworld:the-configured-one")
        finally:
            smoke.request_json = original

        message = str(raised.exception)
        self.assertIn("the-configured-one", message)
        self.assertIn("no other model is used in its place", message)
        # And nothing was spent: the failure happened before any inference address was reached.
        self.assertNotIn("a-model-that-is-not-the-smoke-model", message)

    def test_live_smoke_is_bounded_and_minimal(self) -> None:
        smoke = _gateway_smoke()
        source = (PROJECT_ROOT / "scripts" / "iacode"
                  / "gateway_smoke.py").read_text(encoding="utf-8")

        self.assertLessEqual(smoke.MAX_OUTPUT_TOKENS, 64, "the output cap is not small")
        self.assertLess(len(smoke.PROMPT), 120, "the prompt is not short")
        for timeout in (smoke.READ_TIMEOUT_SECONDS, smoke.INFERENCE_TIMEOUT_SECONDS):
            self.assertGreater(timeout, 0)
            self.assertLessEqual(timeout, 300, "a live check may not wait without a bound")

        # One inference and one stream. A loop over either would be repetition against a real
        # account, which is what row 14.5 forbids.
        self.assertEqual(source.count("/api/v1/gateway/infer"), 1)
        self.assertEqual(source.count("/api/v1/gateway/stream"), 1)
        for repetition in ("for attempt in", "while True", "while attempt"):
            with self.subTest(repetition=repetition):
                self.assertNotIn(repetition, source)

        # It never touches the credential. The variable is named in the module's documentation,
        # where an operator reads it; it is never read, never sent and never printed, so this
        # check cannot fail authentication against a real account even once.
        for reading in ('setting("IACODE_DEVWORLD_API_KEY")',
                        "environ['IACODE_DEVWORLD_API_KEY']",
                        'environ.get("IACODE_DEVWORLD_API_KEY")'):
            with self.subTest(reading=reading):
                self.assertNotIn(reading, source)
        for header in ("Bear" + "er", "auth" + "orization"):
            with self.subTest(header=header):
                self.assertNotIn(header.lower(), source.lower())

    def test_missing_credential_blocks_rather_than_passes(self) -> None:
        smoke = _gateway_smoke()
        health = {"providers": [{
            "provider": "devworld", "addressConfigured": True, "addressVariable": "AN_ADDRESS",
            "credentialConfigured": False, "credentialVariable": "A_VARIABLE_NAME",
            "enabled": True}]}

        original_request, original_setting = smoke.request_json, smoke.setting
        smoke.request_json = lambda url, payload=None, **_kwargs: (200, health)
        smoke.setting = lambda name: (
            "devworld:model-one" if name == "IACODE_GATEWAY_SMOKE_MODEL" else "")
        try:
            with self.assertRaises(smoke.BlockedError) as raised:
                smoke.require_configuration("http://127.0.0.1:1")
        finally:
            smoke.request_json, smoke.setting = original_request, original_setting

        message = str(raised.exception)
        self.assertIn("A_VARIABLE_NAME", message, "the block does not name the missing variable")
        self.assertIn("never printed", message)
        # BLOCKED is its own exit code. Mapping it onto success is the failure row 14.8 forbids.
        self.assertEqual(smoke.BLOCKED_EXIT, 2)
        self.assertNotEqual(smoke.BLOCKED_EXIT, 0)


class SpecificationEvidenceTests(unittest.TestCase):
    """Every test a canonical checklist names by hand must exist in the suite.

    Two rows of this Gate's own specification cited frontend tests that nobody had written, and
    five more cited backend ones. Nothing noticed, because each of those rows also named an
    artifact that did exist, so the row looked covered. A reference to a case that does not exist
    is a requirement with no control behind it.
    """

    def test_every_test_the_specifications_name_exists(self) -> None:
        identifiers = collect_test_ids(PROJECT_ROOT)
        self.assertTrue(identifiers, "no test was discovered at all")

        for checklist in sorted((PROJECT_ROOT / "docs").glob("*-CHECKLIST.md")):
            for row in policies.parse_checklist(checklist.read_text(encoding="utf-8")):
                for column in ("artifact", "evidence"):
                    for token in _BACKTICKED.findall(row[column]):
                        name = token.strip()
                        if not _TEST_NAME.match(name):
                            continue
                        with self.subTest(specification=checklist.name, row=row["key"]):
                            self.assertIn(
                                name, identifiers,
                                f"{checklist.name} row {row['key']} names {name}, "
                                f"which no suite defines")

    def test_the_rule_detects_a_name_no_suite_defines(self) -> None:
        identifiers = collect_test_ids(PROJECT_ROOT)

        self.assertNotIn("test_a_case_this_repository_does_not_have", identifiers)



def _revisions_compared_against(source: str, revisions: set[str]) -> list[str]:
    """Revisions this source treats as the answer rather than as a starting point.

    An equality against a revision says "this is the one it must be", which is the claim that goes
    stale when the next migration lands. Passing one to ``alembic upgrade`` names a point in the
    history on purpose, and an upgrade-path test would be meaningless without it.
    """
    found: list[str] = []
    for revision in sorted(revisions):
        quoted = "[\"']" + re.escape(revision) + "[\"']"
        if re.search(r"[!=]=\s*" + quoted, source) or re.search(quoted + r"\s*[!=]=", source):
            found.append(revision)
    return found


def _declared_migration_revisions() -> set[str]:
    """Every revision identifier the migration directory declares."""
    versions = PROJECT_ROOT / "apps" / "api" / "migrations" / "versions"
    found: set[str] = set()
    for path in sorted(versions.glob("*.py")):
        match = re.search(r'^revision: str = "([^"]+)"', path.read_text(encoding="utf-8"),
                          re.MULTILINE)
        if match:
            found.add(match.group(1))
    return found


def _controls_that_must_derive() -> list[Path]:
    """Controls and tooling, excluding the migrations themselves and the one derivation.

    A migration names its own revision and the one it follows; that is what a migration is. The
    derivation in `migrations/head.py` reads them. Everything else must ask rather than name.
    """
    excluded = {
        (PROJECT_ROOT / "apps" / "api" / "migrations" / "head.py").resolve(),
    }
    versions = (PROJECT_ROOT / "apps" / "api" / "migrations" / "versions").resolve()
    modules: list[Path] = []
    for directory in ("scripts/iacode", "scripts/development-ledger", "tests",
                      "apps/api/tests", "infra/tests"):
        root = PROJECT_ROOT / directory
        if not root.is_dir():
            continue
        for path in sorted(root.rglob("*.py")):
            if "__pycache__" in path.parts or path.resolve() in excluded:
                continue
            if versions in path.resolve().parents:
                continue
            modules.append(path)
    return modules


#: A plausible environment variable name, which is what a ``*_env`` field must hold.
_VARIABLE_NAME = re.compile(r"^[A-Z][A-Z0-9_]*$")

#: An opaque run of characters with no word in it: what a key looks like and a name does not.
_CREDENTIAL_SHAPE = re.compile(r"(?<![A-Za-z0-9])[A-Za-z0-9+/_-]{24,}(?![A-Za-z0-9])")

#: A field that would hold a credential rather than name the variable carrying one.
_CREDENTIAL_SLOT = re.compile(
    r"(?i)^(api[-_]?key|key|token|secret|password|credential|authorization)$")

#: Anything the checklist wrote in backticks.
_BACKTICKED = re.compile(r"`([^`]+)`")

#: A Python test case name, as the checklists write them.
_TEST_NAME = re.compile(r"^test_[a-z0-9_]+$")


def _delivering_checkpoint() -> str:
    """The checkpoint this Gate is writing, from the ledger rather than from a literal."""
    return ledger_common.resolve_latest(PROJECT_ROOT).name


def _gateway_smoke():
    """Import the live check as a module, without running it."""
    operational = PROJECT_ROOT / "scripts" / "iacode"
    if str(operational) not in sys.path:
        sys.path.insert(0, str(operational))
    import gateway_smoke

    return gateway_smoke


class RecordedInputTests(unittest.TestCase):
    """G1-F-007: a recorded input the repository deliberately does not carry.

    `MIR-016` validates every anchored checkpoint from a detached checkout of its own tag, and a
    checkpoint cannot anchor itself, so `GATE-0-CP-0001` was checked there for the first time by
    this Gate. Six of its records name `var/verify-report.json`, `var/` is ignored, and no checkout
    has it. The rule now judges such a reference by the content it binds; every other reference is
    still judged by whether it resolves.
    """

    @staticmethod
    def _record(inputs: list[str], digests: list[dict[str, str]]) -> dict[str, object]:
        return {
            "id": "cmd-0001",
            "runtime": "python 3.13.15",
            "commit": "0" * 40,
            "purpose": "a fixture",
            "command": "python scripts/development-ledger/validate_checkpoint.py",
            "arguments": ["scripts/development-ledger/validate_checkpoint.py"],
            "inputs": inputs,
            "inputsDigest": digests,
            "workingDirectory": str(PROJECT_ROOT),
            "result": "COMPLETED",
            "resultCode": "OK",
            "exitCode": 0,
            "durationMs": 1,
        }

    def _errors(self, inputs: list[str], digests: list[dict[str, str]]) -> list[str]:
        validator = _validator_module()
        errors: list[str] = []
        validator._validate_command_reproducibility(
            PROJECT_ROOT, self._record(inputs, digests), 1, errors, bind_inputs=True)
        return errors

    #: Ignored by `.gitignore`, and absent: `var/` holds generated artifacts, and this particular
    #: name is never produced. Using one that exists locally would make the test pass because the
    #: file was there, not because the rule accepted it.
    IGNORED_AND_ABSENT = "var/a-generated-artifact-no-checkout-carries.json"

    def test_an_ignored_input_is_bound_by_content_rather_than_by_presence(self) -> None:
        validator = _validator_module()
        self.assertFalse((PROJECT_ROOT / self.IGNORED_AND_ABSENT).exists())
        self.assertTrue(validator.path_is_ignored(PROJECT_ROOT, self.IGNORED_AND_ABSENT),
                        "the fixture path is no longer ignored, so this test proves nothing")

        errors = self._errors([self.IGNORED_AND_ABSENT],
                              [{"path": self.IGNORED_AND_ABSENT, "hash": "a" * 64}])

        self.assertEqual(errors, [])

    def test_an_input_the_repository_carries_is_still_required_to_exist(self) -> None:
        """The negative control: the rule still refuses a reference that resolves to nothing."""
        missing = "scripts/development-ledger/a_file_this_repository_does_not_have.py"

        errors = self._errors([missing], [{"path": missing, "hash": "b" * 64}])

        self.assertTrue(any("recorded input does not exist" in message for message in errors),
                        errors)

    def test_an_ignored_input_without_a_bound_digest_is_still_refused(self) -> None:
        ignored = self.IGNORED_AND_ABSENT

        errors = self._errors([ignored], [{"path": ignored, "hash": "ABSENT"}])

        self.assertTrue(any("recorded input does not exist" in message for message in errors),
                        errors)

    def test_the_recorder_never_declares_an_ignored_path_as_an_input(self) -> None:
        """Forward, the situation cannot recur: an ignored path is not an input at all."""
        recorder = _recorder_module()
        artifact = PROJECT_ROOT / "var" / "a-generated-artifact-for-this-test.json"
        artifact.parent.mkdir(parents=True, exist_ok=True)
        artifact.write_text("{}", encoding="utf-8")
        try:
            detected = recorder._detect_inputs(
                PROJECT_ROOT,
                ["scripts/development-ledger/validate_checkpoint.py",
                 "var/a-generated-artifact-for-this-test.json"])
        finally:
            artifact.unlink(missing_ok=True)

        self.assertIn("scripts/development-ledger/validate_checkpoint.py", detected)
        self.assertNotIn("var/a-generated-artifact-for-this-test.json", detected)

    def test_every_sealed_checkpoint_validates_from_its_own_tag(self) -> None:
        """The property `MIR-016` audits, asserted here so a change to the tooling reports it.

        Skipped rather than failed when Git cannot reach the tags, because an unavailable
        repository is not evidence that sealed history is broken.
        """
        import tempfile

        anchors = json.loads((PROJECT_ROOT / ".iacode" / "anchors"
                              / "checkpoint-chain.json").read_text(encoding="utf-8"))
        identifiers = [item["checkpointId"] for item in anchors["anchors"]]
        self.assertTrue(identifiers, "no checkpoint is anchored")

        validator = PROJECT_ROOT / "scripts" / "development-ledger" / "validate_checkpoint.py"
        with tempfile.TemporaryDirectory(prefix="iacode-sealed-") as workdir:
            clone = Path(workdir) / "clone"
            cloned = subprocess.run(
                ["git", "clone", "--quiet", "--no-hardlinks", str(PROJECT_ROOT), str(clone)],
                capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
            if cloned.returncode != 0:
                self.skipTest("the repository could not be cloned for the sealed-history check")

            for identifier in identifiers:
                with self.subTest(checkpoint=identifier):
                    checked = subprocess.run(
                        ["git", "checkout", "--quiet", "--detach",
                         f"refs/tags/iacode-checkpoints/{identifier}"],
                        cwd=clone, capture_output=True, text=True, encoding="utf-8",
                        errors="replace", check=False)
                    self.assertEqual(checked.returncode, 0,
                                     f"{identifier} has no resolvable tag")
                    result = subprocess.run(
                        [sys.executable, str(validator), "--root", str(clone)],
                        capture_output=True, text=True, encoding="utf-8", errors="replace",
                        check=False)
                    self.assertEqual(result.returncode, 0,
                                     f"{identifier}: {(result.stdout or result.stderr)[:400]}")


def _validator_module():
    import validate_checkpoint

    return validate_checkpoint


def _recorder_module():
    import record_command

    return record_command


class CredentialVocabularyTests(unittest.TestCase):
    """One definition of what a credential-carrying name is, and one home for it.

    `LSN-0038` was recorded for two definitions in one module. It recurred against its own
    guardrail: three modules answered this question and they disagreed, and one of them redacted an
    operational limit out of the configuration dump. `GRD-0040` was scoped to the redactors while
    the class was general, which is a `GUARDRAIL_FAILURE` and is recorded as one.
    """

    #: The module that owns both questions: which names carry a credential, and which values are
    #: placeholders. Everything else imports the answer.
    OWNER = "packages/common/src/iacode_common/redaction.py"

    #: Directories where a second opinion would matter. The frontend has no such rule and the
    #: sealed SETUP-00 tooling answers a different question about text it is about to store.
    SEARCHED = ("infra/tests", "scripts/iacode", "apps/api/src", "services/model-gateway/src")

    def test_no_module_writes_its_own_credential_name_rule(self) -> None:
        offenders: list[str] = []
        for directory in self.SEARCHED:
            root = PROJECT_ROOT / directory
            if not root.is_dir():
                continue
            for path in sorted(root.rglob("*.py")):
                if "__pycache__" in path.parts:
                    continue
                source = path.read_text(encoding="utf-8")
                findings = _own_credential_rule(source)
                if findings:
                    offenders.append(
                        f"{path.relative_to(PROJECT_ROOT).as_posix()}: {', '.join(findings)}")

        self.assertEqual(offenders, [], "\n".join(offenders))

    def test_the_rule_detects_a_second_opinion(self) -> None:
        """The negative control, written the way the three offenders actually were."""
        offender = (
            'name = key.upper()\n'
            'credential_shaped = "PASS' 'WORD" in name or "SEC' 'RET" in name\n'
        )

        self.assertTrue(_own_credential_rule(offender))

    def test_the_two_questions_stay_different(self) -> None:
        """Narrower is not the same as wrong: the difference is the decision, so assert it."""
        sys.path.insert(0, str(PROJECT_ROOT / "packages" / "common" / "src"))
        from iacode_common.redaction import carries_a_secret_value, is_sensitive_key

        # An access key identifies; the secret key it pairs with is the secret. A log masks both;
        # a committed example may publish the first.
        self.assertTrue(is_sensitive_key("IACODE_MINIO_ACCESS_KEY"))
        self.assertFalse(carries_a_secret_value("IACODE_MINIO_ACCESS_KEY"))

        for name in ("IACODE_POSTGRES_PASSWORD", "IACODE_MINIO_SECRET_KEY",
                     "IACODE_DEVWORLD_API_KEY"):
            with self.subTest(name=name):
                self.assertTrue(is_sensitive_key(name))
                self.assertTrue(carries_a_secret_value(name))

        # A quantity is neither.
        self.assertFalse(is_sensitive_key("IACODE_GATEWAY_MAX_OUTPUT_TOKENS"))
        self.assertFalse(carries_a_secret_value("IACODE_GATEWAY_MAX_OUTPUT_TOKENS"))


#: A name test written inline rather than imported: ``"PASSWORD" in name``, ``'SECRET' in name``.
#: Matching the shape rather than the word, so a comment or a message mentioning a credential is
#: not mistaken for a rule about one.
_INLINE_NAME_RULE = re.compile(
    r"""["'](PASSWORD|PASSWD|SECRET|TOKEN|TOKENS|API_?KEY|CREDENTIAL|ACCESS_?KEY)["']\s+in\s+""",
    re.IGNORECASE | re.VERBOSE)


def _own_credential_rule(source: str) -> list[str]:
    """Every place a module decides for itself whether a name carries a credential."""
    return sorted({match.group(1) for match in _INLINE_NAME_RULE.finditer(source)})


class GateRunnerTests(unittest.TestCase):
    """`G1-F-009`: the same gate was green under one runner and red under the other.

    `checkpointValidation` is one of the mandatory gates, and running any gate appends to the
    checkpoint's own append-only evidence, so the declared inventory hashes are stale before the
    gate is reached. The Green Keeper re-derived them first. The verification command did not, and
    nothing noticed until the verification was run after a Green Keeper cycle.

    This is a recurrence of `LSN-0011`, whose guardrail named `green_keeper._refresh_declared_hashes`
    by function rather than the property by rule, so it guarded one runner.
    """

    #: The commands that execute the mandatory gate set. A third would have to be listed here, and
    #: the rule below says what listing it costs: it must refresh first.
    RUNNERS = (
        "scripts/development-ledger/green_keeper.py",
        "scripts/iacode/verify.py",
    )

    #: How a module reveals that it runs the gates rather than merely reading which ones exist.
    EXECUTION_MARKERS = ('mandatory_gate_commands(', 'definition["command"]')

    def test_every_runner_of_the_mandatory_gates_refreshes_the_declared_hashes(self) -> None:
        for relative in self.RUNNERS:
            with self.subTest(runner=relative):
                source = (PROJECT_ROOT / relative).read_text(encoding="utf-8")
                self.assertIn("refresh_declared_hashes", source,
                              f"{relative} runs the mandatory gates without re-deriving the "
                              f"checkpoint's declared hashes first")

    def test_the_refresh_has_one_definition(self) -> None:
        """Both runners reach the same function; neither keeps a copy of the rule."""
        keeper = (PROJECT_ROOT / "scripts" / "development-ledger"
                  / "green_keeper.py").read_text(encoding="utf-8")
        verification = (PROJECT_ROOT / "scripts" / "iacode" / "verify.py").read_text(
            encoding="utf-8")

        for source in (keeper, verification):
            self.assertNotIn("_refresh_inventory_hashes(", source,
                             "a runner reaches past the public function into the primitive")
        self.assertIn("from finalize_checkpoint import refresh_declared_hashes", keeper)
        self.assertIn("refresh_declared_hashes", verification)

    def test_no_other_module_executes_the_mandatory_gate_set(self) -> None:
        """Keeps the list above honest: a new runner fails this until it is considered."""
        found: list[str] = []
        for directory in ("scripts/development-ledger", "scripts/iacode"):
            for path in sorted((PROJECT_ROOT / directory).rglob("*.py")):
                if "__pycache__" in path.parts:
                    continue
                source = path.read_text(encoding="utf-8")
                relative = path.relative_to(PROJECT_ROOT).as_posix()
                if relative == "scripts/iacode/policies_bridge.py":
                    # It builds the list for a runner; it starts nothing.
                    continue
                if any(marker in source for marker in self.EXECUTION_MARKERS):
                    found.append(relative)

        self.assertEqual(sorted(found), sorted(self.RUNNERS))


class FrontendBoundaryTests(unittest.TestCase):
    """What the browser may do, checked by reading the frontend rather than by trusting it.

    Row 13.3 and row 13.4 of the specification. Both are properties of the whole source tree rather
    than of one component, which is why they are here and not in the frontend suite: a component
    test proves what that component does, and the claim is about what nothing does.
    """

    def test_frontend_calls_only_the_iacode_backend(self) -> None:
        sources = _frontend_sources()
        self.assertTrue(sources, "no frontend source was read")

        targets: list[str] = []
        for path in sources:
            source = path.read_text(encoding="utf-8")
            name = path.relative_to(PROJECT_ROOT)
            with self.subTest(source=str(name)):
                # No absolute address anywhere: the backend's address is a deployment decision read
                # at start-up, and a second one compiled into the bundle is a second thing to get
                # wrong — or somebody else's backend.
                self.assertNotIn("://", source, f"{name} carries an absolute address")
                for token in ("dw_" + "live", "IACODE_DEVWORLD_API_KEY", "apiKey", "api_key",
                              "Bear" + "er", "auth" + "orization"):
                    self.assertNotIn(token.lower(), source.lower(), f"{name} mentions {token}")
            targets += _FETCH_TARGET.findall(source)

        self.assertTrue(targets, "the frontend issues no request at all, which cannot be right")
        for target in targets:
            with self.subTest(target=target):
                self.assertTrue(
                    target.strip().startswith(_INJECTED_BASE_ADDRESS)
                    or target.strip() == "CONFIG_URL",
                    f"a request is issued to {target.strip()}, which is neither the injected "
                    f"backend address nor the runtime configuration file")

    def test_frontend_adds_no_conversation_capability(self) -> None:
        """Gate 1 is a gateway, not a chat application."""
        for path in _frontend_sources():
            source = path.read_text(encoding="utf-8")
            name = path.relative_to(PROJECT_ROOT)
            for marker in _BROWSER_STORAGE + _CONVERSATION_CAPABILITY:
                with self.subTest(source=str(name), marker=marker):
                    self.assertNotIn(marker, source, f"{name} carries {marker}")

        service = (FRONTEND_ROOT / "app" / "gateway"
                   / "gateway.service.ts").read_text(encoding="utf-8")

        # One prompt, one answer: the payload is built from the prompt alone, and the page has no
        # way to send a system instruction or a previous turn.
        self.assertTrue(_ONE_USER_MESSAGE.search(service),
                        "the playground no longer sends exactly one user message")
        self.assertEqual(len(_ANY_ROLE.findall(service)), 1,
                         "the frontend names more than one message role")

    def test_the_frontend_rules_detect_what_they_forbid(self) -> None:
        """The negative control: the markers are absent because nothing carries them."""
        offender = "const saved = localStorage.getItem('x'); messages.push(reply);"

        found = [marker for marker in _BROWSER_STORAGE + _CONVERSATION_CAPABILITY
                 if marker in offender]

        self.assertEqual(sorted(found), ["localStorage", "messages.push"])


FRONTEND_ROOT = PROJECT_ROOT / "apps" / "web" / "src"

#: The single expression every request in the frontend is built from.
_INJECTED_BASE_ADDRESS = "`${this.config.baseUrl}"

#: Browser-side persistence. A gateway page that remembers is a page that stores a prompt.
_BROWSER_STORAGE = ("localStorage", "sessionStorage", "indexedDB", "document.cookie")

#: The capabilities later Gates own. Names of mechanisms, not words: the sources say "there is no
#: conversation here" in prose, and a scan for the word would fail on the sentence denying it.
_CONVERSATION_CAPABILITY = ("messages.push", "history.push", "executeTool", "runTool",
                            "conversationId", "personaId", "systemPrompt")

#: A request target: the first argument of ``fetch``, or of the ``fetchImpl`` the config reader
#: takes so that it can be driven from a test.
_FETCH_TARGET = re.compile(r"\bfetch(?:Impl)?\(\s*([^,\n]+)")

#: The payload the playground builds: one user message, inline, from the prompt alone.
_ONE_USER_MESSAGE = re.compile(r"messages:\s*\[\{\s*role:\s*'user'")

#: Any message role named anywhere in the frontend. More than one means the page can compose a
#: conversation, which is the capability row 13.4 forbids.
_ANY_ROLE = re.compile(r"role:\s*'")


def _frontend_sources() -> list[Path]:
    """Every frontend source that ships, which excludes the specs that describe it."""
    return [path for pattern in ("*.ts", "*.html")
            for path in sorted(FRONTEND_ROOT.rglob(pattern))
            if not path.name.endswith(".spec.ts")]


class Gate1GuardrailTests(unittest.TestCase):
    """The controls this Gate's own failures turned into rules.

    Each rule is applied to the repository and then applied to a case it must reject, because a
    scan that has quietly stopped scanning passes every time.
    """

    # --- a gate that measures inside an image must build that image ------------------------

    def test_every_image_gate_builds_before_it_measures(self) -> None:
        """LSN-0036: a gate that runs inside an image and does not build it measures the past."""
        for module in sorted((PROJECT_ROOT / "scripts" / "iacode" / "gates").glob("*.py")):
            with self.subTest(gate=module.name):
                findings = _image_gate_findings(module.read_text(encoding="utf-8"))
                self.assertEqual(findings, [], f"{module.name}: {findings}")

    def test_the_image_gate_rule_detects_a_gate_that_would_skip_the_build(self) -> None:
        offender = (
            "from compose import compose, log, main_guard\n"
            "def main():\n"
            "    result = compose('run', '--rm', 'api', 'python', '-m', 'pytest')\n"
            "    return result.exit_code\n"
        )

        self.assertTrue(_image_gate_findings(offender))

    def test_the_image_gate_rule_accepts_a_gate_that_judges_the_working_tree(self) -> None:
        """A container that mounts the tree judges what is on disk, so it needs no build."""
        mounted = (
            "import subprocess\n"
            "from compose import REPOSITORY_ROOT\n"
            "def main():\n"
            "    return subprocess.run(['docker', 'run', '--rm', '--volume',\n"
            "        f'{REPOSITORY_ROOT}:/repo:ro', 'iacode/api:0.1.0', 'ruff', 'check']).returncode\n"
        )

        self.assertEqual(_image_gate_findings(mounted), [])

    # --- a shared control derives the Gate rather than naming one --------------------------

    def test_no_shared_control_is_bound_to_a_gate_literal(self) -> None:
        """LSN-0037: a control that names a Gate refuses the next one."""
        for module in _python_modules_that_carry_controls():
            with self.subTest(module=str(module.relative_to(PROJECT_ROOT))):
                findings = _gate_literal_findings(module.read_text(encoding="utf-8"))
                self.assertEqual(findings, [], f"{module.name}: {findings}")

    def test_the_gate_literal_rule_detects_a_bound_control(self) -> None:
        offender = (
            "GATE = 'GATE-0'\n"
            "def check():\n"
            "    return policies.scope_violations(PROJECT_ROOT, GATE)\n"
        )
        direct = (
            "def check():\n"
            "    return policies.reservations_in_force(REPOSITORY_ROOT, 'GATE-0')\n"
        )

        self.assertTrue(_gate_literal_findings(offender))
        self.assertTrue(_gate_literal_findings(direct))

    def test_the_gate_literal_rule_accepts_a_derived_gate_and_a_fixture_root(self) -> None:
        derived = (
            "def check(root):\n"
            "    return policies.scope_violations(PROJECT_ROOT, delivered_gate(PROJECT_ROOT))\n"
        )
        fixture = (
            "def check(fixture):\n"
            "    return policies.scope_violations(fixture, 'GATE-0')\n"
        )

        self.assertEqual(_gate_literal_findings(derived), [])
        self.assertEqual(_gate_literal_findings(fixture), [])


    # --- a control names no identifier the repository derives ------------------------------

    def test_no_control_names_a_migration_revision_literally(self) -> None:
        """`G1-F-010`: the same class as the Gate literal, with a revision identifier instead.

        The fresh-installation scenario compared the recorded `alembic_version` with
        `"0001_foundation"`, so the Gate that added the second migration failed a scenario about
        something else. The head is derived in one place now, and nothing else may name one.
        """
        revisions = _declared_migration_revisions()
        self.assertTrue(revisions, "the migration directory declares no revision")

        offenders: list[str] = []
        for path in _controls_that_must_derive():
            named = _revisions_compared_against(path.read_text(encoding="utf-8"), revisions)
            if named:
                offenders.append(
                    f"{path.relative_to(PROJECT_ROOT).as_posix()}: {', '.join(named)}")

        self.assertEqual(offenders, [], "\n".join(offenders))

    def test_the_revision_rule_detects_a_named_head(self) -> None:
        """The negative control, written the way the scenario actually was.

        And the positive one: naming a specific historical revision as a *starting point* is what
        an upgrade-path test is for, so the rule must not refuse it.
        """
        revisions = _declared_migration_revisions()
        oldest = sorted(revisions)[0]
        compared = 'record("migration_recorded", observed == "' + oldest + '")'
        argument = 'assert _alembic(url, "upgrade", "' + oldest + '").returncode == 0'

        self.assertEqual(_revisions_compared_against(compared, revisions), [oldest])
        self.assertEqual(_revisions_compared_against(argument, revisions), [])

    def test_the_head_revision_has_one_derivation(self) -> None:
        """Both consumers reach the same module; neither keeps a copy of the walk."""
        import importlib.util

        module_path = PROJECT_ROOT / "apps" / "api" / "migrations" / "head.py"
        spec = importlib.util.spec_from_file_location("iacode_migrations_head_check", module_path)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        head = module.head_revision(module_path.parent / "versions")
        self.assertIn(head, _declared_migration_revisions())
        graph = module.revision_graph(module_path.parent / "versions")
        self.assertNotIn(head, {parent for parent in graph.values() if parent})

        for relative in ("scripts/iacode/scenarios/fresh_install.py",
                         "apps/api/tests/integration/test_migrations.py"):
            with self.subTest(consumer=relative):
                source = (PROJECT_ROOT / relative).read_text(encoding="utf-8")
                self.assertIn("head", source.lower())
                self.assertNotIn("down_revision", source,
                                 f"{relative} walks the revision graph itself")

    # --- one definition of what a placeholder is ------------------------------------------

    def test_both_redactors_agree_on_every_value_the_example_file_carries(self) -> None:
        """LSN-0038: the two paths disagreed, and the committed example was the casualty.

        The corpus is the artefact the disagreement was about: every value in the environment file
        the repository commits. A value must either survive both redactors or survive neither.
        """
        sys.path.insert(0, str(PROJECT_ROOT / "packages" / "common" / "src"))
        from iacode_common.redaction import redact_text, redact_value

        example = (PROJECT_ROOT / "infra" / "compose" / ".env.example").read_text(encoding="utf-8")
        checked = 0
        for line in example.splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or "=" not in stripped:
                continue
            key, _, value = stripped.partition("=")
            key, value = key.strip(), value.strip()
            in_text = value in redact_text(f"{key}={value}")
            as_value = redact_value(key, value) == value
            checked += 1
            with self.subTest(key=key):
                self.assertEqual(
                    in_text, as_value,
                    f"{key} survives redact_text={in_text} but redact_value={as_value}")

        self.assertGreater(checked, 20, "the example file parsed as almost nothing")

    def test_the_documented_placeholder_survives_both_paths(self) -> None:
        sys.path.insert(0, str(PROJECT_ROOT / "packages" / "common" / "src"))
        from iacode_common.redaction import redact_text, redact_value

        placeholder = "change-me-before-starting"
        name = "IACODE_MINIO_" + "SECRET_KEY"

        self.assertEqual(redact_text(f"{name}={placeholder}"), f"{name}={placeholder}")
        self.assertEqual(redact_value(name, placeholder), placeholder)
        self.assertNotIn("hunter2hunter2", redact_text(f"{name}=hunter2hunter2"))


# ------------------------------------------------------------------------------- the rules

#: Gate identifiers written into source, e.g. ``GATE-0``.
_GATE_LITERAL = re.compile(r"^GATE-\d+$")

#: The controls whose answer depends on which Gate is being delivered.
_GATE_SCOPED_CONTROLS = frozenset({"scope_violations", "reservations_in_force"})

#: The names that mean "this repository" rather than "a fixture built for one assertion".
_REPOSITORY_ROOT_NAMES = frozenset({"PROJECT_ROOT", "REPOSITORY_ROOT"})

#: Helpers that rebuild an artefact before a gate measures inside it.
_BUILD_HELPERS = frozenset({"build_service", "build_toolchain"})


def _called_name(node: ast.Call) -> str:
    function = node.func
    if isinstance(function, ast.Attribute):
        return function.attr
    if isinstance(function, ast.Name):
        return function.id
    return ""


def _string_constants(node: ast.AST) -> list[str]:
    """Every string literal inside one expression, including the elements of a list literal."""
    return [child.value for child in ast.walk(node)
            if isinstance(child, ast.Constant) and isinstance(child.value, str)]


def _image_gate_findings(source: str) -> list[str]:
    """Where a gate module runs a command inside an image without rebuilding that image.

    A container that mounts the working tree is exempt: its subject is what is on disk, not what a
    layer captured, which is why the lint gate needs no build.
    """
    tree = ast.parse(source)
    runs_container = False
    builds = False
    mounts_tree = "--volume" in source and ("REPOSITORY_ROOT" in source or "/repo" in source)

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name = _called_name(node)
        if name in _BUILD_HELPERS:
            builds = True
            continue
        literals = _string_constants(node)
        if name == "compose" and literals[:1] in (["run"], ["exec"]):
            runs_container = True
        elif "docker" in literals and "run" in literals:
            runs_container = True
        elif "docker" in literals and "build" in literals:
            builds = True

    if runs_container and not builds and not mounts_tree:
        return ["runs a command inside an image without building that image first"]
    return []


def _gate_literal_findings(source: str) -> list[str]:
    """Where a Gate-scoped control is asked about this repository under a hard-coded Gate.

    The gate argument is resolved through module-level bindings, because the failure this rule
    exists for was ``GATE = "GATE-0"`` at the top of a module and ``GATE`` at the call site — the
    literal was one indirection away, which was enough to make it look derived.
    """
    tree = ast.parse(source)
    bound: dict[str, str] = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant) \
                and isinstance(node.value.value, str) and _GATE_LITERAL.match(node.value.value):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    bound[target.id] = node.value.value

    findings: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or _called_name(node) not in _GATE_SCOPED_CONTROLS:
            continue
        arguments = list(node.args)
        if not arguments or not isinstance(arguments[0], ast.Name) \
                or arguments[0].id not in _REPOSITORY_ROOT_NAMES:
            continue
        gate_argument = arguments[1] if len(arguments) > 1 else next(
            (keyword.value for keyword in node.keywords if keyword.arg == "gate"), None)
        literal = None
        if isinstance(gate_argument, ast.Constant) and isinstance(gate_argument.value, str):
            literal = gate_argument.value
        elif isinstance(gate_argument, ast.Name):
            literal = bound.get(gate_argument.id)
        if literal is not None and _GATE_LITERAL.match(literal):
            findings.append(
                f"line {node.lineno}: {_called_name(node)} is asked about this repository "
                f"under the hard-coded Gate {literal!r}")
    return findings


def _python_modules_that_carry_controls() -> list[Path]:
    """The control-plane tooling and the repository-wide suites, which outlive any one Gate."""
    modules: list[Path] = []
    for directory in (PROJECT_ROOT / "tests",
                      PROJECT_ROOT / "scripts" / "development-ledger",
                      PROJECT_ROOT / "scripts" / "iacode"):
        modules += [path for path in sorted(directory.rglob("*.py"))
                    if "__pycache__" not in path.parts]
    return modules
