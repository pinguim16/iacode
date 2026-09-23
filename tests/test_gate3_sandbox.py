"""Control-plane and repository-structure properties of GATE 3 — SANDBOX.

What this suite can check is what can be read from the repository, or exercised with the standard
library alone: the Gate's canonical specification and its registries, the ledger controls the Gate
repaired before it started, the boundary between the agent runtime and the sandbox, the sandbox
policy, the documents, and the scope of the Gate.

What it deliberately does not check is sandbox behaviour against a container engine. That suite
runs inside the sandbox service's image, which has the container client, and in the recorded
scenarios; duplicating a behavioural assertion here with a text search would be a second, weaker
control that disagrees with the first.

Every scan and every refusal here carries a **null control**: the identical path over an unmutated
fixture, which must be accepted, so a refusal is attributed to the mutation under test and not to
leftover state.
"""

from __future__ import annotations

import ast
import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = PROJECT_ROOT / "scripts" / "development-ledger"
sys.path.insert(0, str(SCRIPTS))

import ledger_common  # noqa: E402
import policies  # noqa: E402
import record_command  # noqa: E402
import validate_checkpoint  # noqa: E402
from delivery_assurance import collect_test_ids  # noqa: E402


def _git(root: Path, *arguments: str) -> None:
    subprocess.run(["git", *arguments], cwd=root, check=True, capture_output=True)


# ---------------------------------------------------------------------------------------------
# 0. Pre-gate maintenance inherited from GATE 2
# ---------------------------------------------------------------------------------------------


class LedgerCommandReplayabilityTests(unittest.TestCase):
    """`R-G2-010` / `G2-F-011`: the recorder refuses, before running it, a command the validator
    would later refuse, and both ask one rule rather than two copies of it."""

    def setUp(self) -> None:
        self._directory = tempfile.TemporaryDirectory(prefix="iacode-replay-")
        self.root = Path(self._directory.name)
        (self.root / ".iacode").mkdir()
        self.checkpoint = self.root / "docs" / "checkpoints" / "FIXTURE-CP-0001"
        self.checkpoint.mkdir(parents=True)
        (self.root / "probe.py").write_text(
            "from pathlib import Path\nPath('executed.marker').write_text('ran')\n",
            encoding="utf-8")
        _git(self.root, "init", "-q")
        _git(self.root, "config", "user.name", "Fixture")
        _git(self.root, "config", "user.email", "fixture@example.invalid")
        _git(self.root, "add", ".")
        _git(self.root, "commit", "-q", "-m", "fixture")

    def tearDown(self) -> None:
        self._directory.cleanup()

    def record(self, *command: str) -> tuple[int, list[dict]]:
        argv = ["record_command.py", "--root", str(self.root), "--checkpoint",
                str(self.checkpoint), "--quiet", "--purpose", "fixture", "--", *command]
        with mock.patch.object(sys, "argv", argv), contextlib.redirect_stdout(io.StringIO()):
            exit_code = record_command.main()
        commands = self.checkpoint / "COMMANDS.jsonl"
        records = [json.loads(line) for line in commands.read_text(encoding="utf-8").splitlines()
                   if line.strip()] if commands.is_file() else []
        return exit_code, records

    def executed(self) -> bool:
        return (self.root / "executed.marker").is_file()

    def test_valid_command_executes_and_records(self) -> None:
        """The null control: the identical path accepts a replayable command and runs it."""
        exit_code, records = self.record("python", "probe.py")

        self.assertEqual(exit_code, 0)
        self.assertTrue(self.executed())
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["result"], "COMPLETED")
        self.assertEqual(records[0]["exitCode"], 0)
        errors: list[str] = []
        validate_checkpoint._validate_command_reproducibility(self.root, records[0], 1, errors)
        self.assertEqual(errors, [])

    def test_unsupported_runtime_is_rejected_before_execution(self) -> None:
        exit_code, records = self.record(sys.executable, "probe.py")

        self.assertNotEqual(exit_code, 0)
        self.assertFalse(self.executed(), "a refused command was executed anyway")
        self.assertEqual(len(records), 1)
        record = records[0]
        self.assertEqual(record["result"], "PRECONDITION_REJECTED")
        self.assertEqual(record["resultCode"], "E_UNREPLAYABLE_COMMAND")
        self.assertIsNone(record["exitCode"], "a refusal must not fabricate an exit code")
        self.assertIn("explicit runtime", record["failureReason"])

    def test_unresolved_python_script_is_rejected_before_execution(self) -> None:
        exit_code, records = self.record("python", "tools/absent_probe.py")

        self.assertNotEqual(exit_code, 0)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["result"], "PRECONDITION_REJECTED")
        self.assertEqual(records[0]["resultCode"], "E_UNREPLAYABLE_COMMAND")
        self.assertIsNone(records[0]["exitCode"])
        self.assertIn("does not resolve", records[0]["failureReason"])

    def test_rejected_command_is_never_executed(self) -> None:
        """A refusal is a refusal of the process: nothing of the command runs."""
        with mock.patch.object(record_command.subprocess, "run",
                               wraps=subprocess.run) as launched:
            exit_code, records = self.record(sys.executable, "probe.py")

        self.assertNotEqual(exit_code, 0)
        launched_commands = [call.args[0] for call in launched.call_args_list if call.args]
        self.assertFalse(any("probe.py" in list(command) for command in launched_commands),
                         f"the refused command was launched: {launched_commands}")
        self.assertTrue(launched_commands, "the wrapper observed nothing, so it proves nothing")
        self.assertEqual(records[0]["result"], "PRECONDITION_REJECTED")

    def test_the_refusal_record_is_valid_ledger_evidence(self) -> None:
        """The record of a refusal keeps the checkpoint valid, and cannot be evidence of a PASS."""
        _exit_code, records = self.record(sys.executable, "probe.py")
        errors: list[str] = []
        validate_checkpoint._validate_command_reproducibility(self.root, records[0], 1, errors)
        self.assertEqual(errors, [])
        self.assertNotIsInstance(records[0].get("exitCode"), int)

    def test_a_refusal_the_rule_does_not_support_is_refused(self) -> None:
        """A replayable command recorded as refused-for-being-unreplayable is a false record."""
        _exit_code, records = self.record("python", "probe.py")
        forged = dict(records[0], result="PRECONDITION_REJECTED",
                      resultCode="E_UNREPLAYABLE_COMMAND", exitCode=None,
                      failureReason="forged")
        errors: list[str] = []
        validate_checkpoint._validate_command_reproducibility(self.root, forged, 1, errors)
        self.assertTrue(any("does not refuse" in error for error in errors), errors)

    def test_recorder_and_validator_share_one_rule(self) -> None:
        self.assertIs(record_command.command_replay_errors, ledger_common.command_replay_errors)
        self.assertIs(validate_checkpoint.command_replay_errors,
                      ledger_common.command_replay_errors)
        for module in (record_command, validate_checkpoint):
            tree = ast.parse(Path(module.__file__).read_text(encoding="utf-8"))
            assigned = {target.id for node in ast.walk(tree) if isinstance(node, ast.Assign)
                        for target in node.targets if isinstance(target, ast.Name)}
            with self.subTest(module=module.__name__):
                self.assertNotIn("RUNTIME_TOKENS", assigned,
                                 "a second copy of the runtime token set")

    def test_the_guard_is_what_refuses(self) -> None:
        """Mutation control: without the shared rule the same command runs, so the refusal above
        is the rule's and not an accident of the fixture."""
        with mock.patch.object(record_command, "command_replay_errors", return_value=[]):
            exit_code, records = self.record(sys.executable, "probe.py")

        self.assertEqual(exit_code, 0)
        self.assertTrue(self.executed())
        self.assertEqual(records[0]["result"], "COMPLETED")


def memory_fixture(root: Path) -> None:
    """A disposable clone of the repository as it stands, working tree included."""
    if not ledger_common.clone_with_worktree(PROJECT_ROOT, root):
        raise RuntimeError("the repository could not be cloned for a fixture")


def validate_memory_cli(root: Path, *extra: str) -> tuple[int, str]:
    completed = subprocess.run(
        [sys.executable, str(root / "scripts" / "development-ledger" / "validate_lessons.py"),
         "--root", str(root), *extra],
        cwd=root, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return completed.returncode, completed.stdout + completed.stderr


class GuardrailRegistryResolutionTests(unittest.TestCase):
    """`R-G2-010` / MIR-006: a lesson's guardrail is resolved all the way down — lesson, registry
    entry, kind, reference, the control itself — by the validator and the effectiveness measure
    alike, through one function."""

    @classmethod
    def setUpClass(cls) -> None:
        cls._directory = tempfile.TemporaryDirectory(prefix="iacode-guardrail-")
        cls.root = Path(cls._directory.name) / "clone"
        memory_fixture(cls.root)
        cls.registry = cls.root / ".iacode" / "memory" / "guardrails" / "registry.json"
        cls.original = cls.registry.read_text(encoding="utf-8")

    @classmethod
    def tearDownClass(cls) -> None:
        cls._directory.cleanup()

    def tearDown(self) -> None:
        self.registry.write_text(self.original, encoding="utf-8", newline="\n")

    def mutate(self, change) -> dict:
        document = json.loads(self.original)
        entry = next(item for item in document["guardrails"] if item["kind"] == "test")
        change(entry)
        self.registry.write_text(json.dumps(document, indent=2), encoding="utf-8", newline="\n")
        return entry

    def test_the_unmutated_memory_is_valid(self) -> None:
        """The null control: the identical fixture and path accept the real registry."""
        code, output = validate_memory_cli(self.root)
        self.assertEqual(code, 0, output)
        self.assertIn("LESSONS_VALID", output)

    def test_a_test_guardrail_that_names_a_file_is_refused(self) -> None:
        entry = self.mutate(lambda item: item.update(
            reference="file:tests/test_development_ledger.py"))

        code, output = validate_memory_cli(self.root)

        self.assertNotEqual(code, 0, output)
        self.assertIn("LESSONS_INVALID", output)
        self.assertIn(entry["guardrailId"], output)
        self.assertIn("does not exist in the suite", output)

    def test_a_test_guardrail_that_names_a_path_is_refused(self) -> None:
        self.mutate(lambda item: item.update(reference="tests/test_development_ledger.py"))
        code, output = validate_memory_cli(self.root)
        self.assertNotEqual(code, 0, output)
        self.assertIn("LESSONS_INVALID", output)

    def test_validation_and_effectiveness_agree(self) -> None:
        import lessons

        entry = self.mutate(lambda item: item.update(reference="file:tests/absent.py"))
        lessons._TEST_ID_CACHE.clear()
        measured = lessons.guardrail_effectiveness(self.root)
        detail = next(item for item in measured["guardrails"]
                      if item["guardrailId"] == entry["guardrailId"])
        errors = lessons.validate_lessons(self.root)

        self.assertFalse(detail["resolved"])
        self.assertTrue(any(entry["guardrailId"] in error for error in errors), errors)

    def test_the_repository_memory_declares_the_newest_policy(self) -> None:
        """The new rules are versioned so sealed checkpoints keep validating under theirs; the
        repository itself may not step back to a version that does not apply them."""
        import lessons

        self.assertEqual(lessons.memory_policy_version(PROJECT_ROOT),
                         lessons.RESOLVING_MEMORY_POLICIES[-1])
        self.assertIn(lessons.RESOLVED_GUARDRAIL_MEMORY_POLICY,
                      lessons.RESOLVED_GUARDRAIL_MEMORY_POLICIES)

    def test_one_function_resolves_a_guardrail_entry(self) -> None:
        import lessons

        source = Path(lessons.__file__).read_text(encoding="utf-8")
        tree = ast.parse(source)
        callers = {
            function.name for function in ast.walk(tree) if isinstance(function, ast.FunctionDef)
            for node in ast.walk(function) if isinstance(node, ast.Call)
            and getattr(node.func, "id", None) == "guardrail_entry_errors"
        }
        self.assertEqual(callers, {"validate_lessons", "guardrail_effectiveness"})


class LessonIndexFreshnessTests(unittest.TestCase):
    """`R-G2-010`: `LESSONS.md` is derived from `lessons.jsonl`, and a stale render is refused
    rather than discovered by a reader five lessons later."""

    @classmethod
    def setUpClass(cls) -> None:
        cls._directory = tempfile.TemporaryDirectory(prefix="iacode-index-")
        cls.root = Path(cls._directory.name) / "clone"
        memory_fixture(cls.root)
        cls.memory = cls.root / ".iacode" / "memory"
        cls.original = (cls.memory / "lessons.jsonl").read_text(encoding="utf-8")
        cls.original_index = (cls.memory / "LESSONS.md").read_text(encoding="utf-8")

    @classmethod
    def tearDownClass(cls) -> None:
        cls._directory.cleanup()

    def tearDown(self) -> None:
        (self.memory / "lessons.jsonl").write_text(self.original, encoding="utf-8", newline="\n")
        (self.memory / "LESSONS.md").write_text(self.original_index, encoding="utf-8",
                                                newline="\n")

    def retitle_first_lesson(self) -> str:
        lines = self.original.splitlines()
        first = json.loads(lines[0])
        first["title"] = first["title"] + " (retitled by a freshness test)"
        lines[0] = json.dumps(first, ensure_ascii=False)
        (self.memory / "lessons.jsonl").write_text("\n".join(lines) + "\n", encoding="utf-8",
                                                    newline="\n")
        return first["title"]

    def test_the_committed_index_is_the_render_of_the_memory(self) -> None:
        """The null control, and the repository's own state: the index is current."""
        import lessons

        rendered = lessons.render_index(lessons.load_lessons(PROJECT_ROOT))
        committed = (PROJECT_ROOT / ".iacode" / "memory" / "LESSONS.md").read_text(
            encoding="utf-8")
        self.assertEqual(committed, rendered)
        code, output = validate_memory_cli(self.root)
        self.assertEqual(code, 0, output)

    def test_a_memory_changed_without_rerendering_is_refused(self) -> None:
        self.retitle_first_lesson()
        code, output = validate_memory_cli(self.root)
        self.assertNotEqual(code, 0, output)
        self.assertIn("LESSONS_INVALID", output)
        self.assertIn("LESSONS.md", output)

    def test_rerendering_from_the_canonical_source_repairs_it(self) -> None:
        title = self.retitle_first_lesson()
        render_code, render_output = validate_memory_cli(self.root, "--render-index")
        code, output = validate_memory_cli(self.root)

        self.assertEqual(render_code, 0, render_output)
        self.assertEqual(code, 0, output)
        self.assertIn(title, (self.memory / "LESSONS.md").read_text(encoding="utf-8"))

    def test_a_hand_edited_index_is_refused(self) -> None:
        """The index is a render, not a document: editing it by hand is refused too."""
        (self.memory / "LESSONS.md").write_text(self.original_index + "\nA hand edit.\n",
                                                encoding="utf-8", newline="\n")
        code, output = validate_memory_cli(self.root)
        self.assertNotEqual(code, 0, output)


ADR_DIRECTORY = PROJECT_ROOT / "docs" / "adr"


def adr_records(directory: Path) -> list[tuple[str, str, str, str]]:
    """``(identifier, title, status, file name)`` of every ADR, read from the records."""
    import re

    rows = []
    for path in sorted(directory.glob("ADR-*.md")):
        text = path.read_text(encoding="utf-8")
        heading = re.search(r"(?m)^# (ADR-\d{4})\s*[—:]\s*(.+?)\s*$", text)
        status = re.search(r"(?m)^(?:- )?Status: (\S+)", text)
        if heading is None or status is None:
            rows.append((path.stem[:8], "", "", path.name))
            continue
        rows.append((heading.group(1), heading.group(2).strip(), status.group(1).capitalize(),
                     path.name))
    return rows


def adr_index_rows(index: Path) -> list[tuple[str, str, str, str]]:
    import re

    row = re.compile(r"^\| \[(ADR-\d{4})\]\(([^)]+)\) \| (.+?) \| (\S+) \|$")
    rows = []
    for line in index.read_text(encoding="utf-8").splitlines():
        match = row.match(line)
        if match:
            rows.append((match.group(1), match.group(3), match.group(4), match.group(2)))
    return rows


class AdrIndexTests(unittest.TestCase):
    """`R-G2-012`: the ADR index exists, lists every record exactly, and a missing index fails."""

    def test_the_index_exists(self) -> None:
        self.assertTrue((ADR_DIRECTORY / "README.md").is_file(), "the ADR index is missing")

    def test_the_index_lists_every_record_with_its_title_and_status(self) -> None:
        records = adr_records(ADR_DIRECTORY)
        self.assertGreaterEqual(len(records), 24)
        for identifier, title, status, _name in records:
            with self.subTest(adr=identifier):
                self.assertTrue(title and status, f"{identifier} has no heading or status line")
        self.assertEqual(adr_index_rows(ADR_DIRECTORY / "README.md"), records)

    def test_every_link_of_the_index_resolves(self) -> None:
        for identifier, _title, _status, name in adr_index_rows(ADR_DIRECTORY / "README.md"):
            with self.subTest(adr=identifier):
                self.assertTrue((ADR_DIRECTORY / name).is_file())

    def test_a_record_missing_from_the_index_is_detected(self) -> None:
        """Null and mutation control over a disposable copy of the directory."""
        import shutil

        with tempfile.TemporaryDirectory(prefix="iacode-adr-") as workdir:
            copy = Path(workdir) / "adr"
            shutil.copytree(ADR_DIRECTORY, copy)
            self.assertEqual(adr_index_rows(copy / "README.md"), adr_records(copy))
            (copy / "ADR-9999-planted.md").write_text(
                "# ADR-9999 — A planted decision\n\nStatus: Proposed\n", encoding="utf-8")
            self.assertNotEqual(adr_index_rows(copy / "README.md"), adr_records(copy))



# ---------------------------------------------------------------------------------------------
# 1. The Gate's own specification and registries
# ---------------------------------------------------------------------------------------------

GATE = "GATE-3"
SPECIFICATION = PROJECT_ROOT / "docs" / "GATE-3-CHECKLIST.md"
SANDBOX_ROOT = PROJECT_ROOT / "services" / "sandbox"
SANDBOX_SOURCE = SANDBOX_ROOT / "src" / "iacode_sandbox"
SANDBOX_POLICY = PROJECT_ROOT / ".iacode" / "policies" / "sandbox-policy.json"
WORKFLOW = (PROJECT_ROOT / "services" / "orchestrator" / "src" / "iacode_orchestrator"
            / "workflows" / "agent_run.py")


def python_files(root: Path) -> list[Path]:
    return [path for path in sorted(root.rglob("*.py")) if "__pycache__" not in path.parts]


def imported_names(source: str) -> set[str]:
    names: set[str] = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module)
    return names


def dotted(node: ast.AST) -> str:
    parts: list[str] = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        parts.append(node.id)
    return ".".join(reversed(parts))


def called(node: ast.AST) -> set[str]:
    return {dotted(item.func) for item in ast.walk(node)
            if isinstance(item, ast.Call) and dotted(item.func)}


def function(source: str, name: str) -> ast.AST:
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            return node
    raise AssertionError(f"no function {name!r}")


def arithmetic(node: ast.AST) -> int:
    """The value of an integer literal or a product or sum of them; anything else is refused."""
    if isinstance(node, ast.Constant) and isinstance(node.value, int):
        return node.value
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mult):
        return arithmetic(node.left) * arithmetic(node.right)
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        return arithmetic(node.left) + arithmetic(node.right)
    raise AssertionError(f"not integer arithmetic: {ast.unparse(node)}")


def constant_value(source: str, name: str) -> int:
    """An integer module or class constant, read from the source without importing it."""
    for node in ast.walk(ast.parse(source)):
        target = value = None
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            target, value = node.targets[0], node.value
        elif isinstance(node, ast.AnnAssign) and node.value is not None:
            target, value = node.target, node.value
        if isinstance(target, ast.Name) and target.id == name and value is not None:
            return arithmetic(value)
    raise AssertionError(f"no constant {name!r}")


def load_sandbox_policy() -> dict:
    return json.loads(SANDBOX_POLICY.read_text(encoding="utf-8"))


class Gate3CanonicalSpecificationTests(unittest.TestCase):
    """The Gate's requirement set comes from a document, re-parsed, and from nothing else."""

    def test_the_specification_exists_and_parses(self) -> None:
        self.assertTrue(SPECIFICATION.is_file())
        rows = policies.parse_checklist(SPECIFICATION.read_text(encoding="utf-8"))

        self.assertGreater(len(rows), 100, "the specification parsed as almost nothing")
        for row in rows:
            with self.subTest(key=row["key"]):
                self.assertTrue(row["description"].strip())
                self.assertTrue(row["artifact"].strip())
                self.assertTrue(row["evidence"].strip())

    def test_the_registry_mirrors_the_specification_row_for_row(self) -> None:
        declared = policies.canonical_requirements(PROJECT_ROOT, GATE)
        parsed = policies.parse_checklist(SPECIFICATION.read_text(encoding="utf-8"))

        self.assertEqual([item["key"] for item in declared], [row["key"] for row in parsed])
        self.assertEqual([item["description"] for item in declared],
                         [row["description"] for row in parsed])
        self.assertTrue(all(item.get("mandatory") for item in declared))

    def test_a_dropped_row_is_refused(self) -> None:
        """The positive path and the refusal of the mirror control, over a disposable copy."""
        import shutil

        with tempfile.TemporaryDirectory(prefix="iacode-spec-") as workdir:
            root = Path(workdir)
            shutil.copytree(PROJECT_ROOT / ".iacode" / "policies", root / ".iacode" / "policies")
            (root / "docs").mkdir()
            shutil.copy2(SPECIFICATION, root / "docs" / SPECIFICATION.name)
            self.assertEqual(len(policies.canonical_requirements(root, GATE)),
                             len(policies.canonical_requirements(PROJECT_ROOT, GATE)))

            registry_path = root / ".iacode" / "policies" / "canonical-requirements.json"
            registry = json.loads(registry_path.read_text(encoding="utf-8"))
            entry = next(item for item in registry["gates"] if item["gate"] == GATE)
            entry["requirements"] = entry["requirements"][:-1]
            registry_path.write_text(json.dumps(registry, indent=2, ensure_ascii=False),
                                     encoding="utf-8")
            with self.assertRaises(ledger_common.LedgerError):
                policies.canonical_requirements(root, GATE)

    def test_the_specification_states_where_a_command_runs(self) -> None:
        """The Gate is defined by where nothing may run, and the definition is in the document."""
        text = SPECIFICATION.read_text(encoding="utf-8")
        self.assertIn("runs **inside a sandbox**", text)
        self.assertIn("Never on the Windows host", text)
        self.assertIn("INTERNAL_GATE_PASS", text)


class Gate3MandatoryGateTests(unittest.TestCase):
    """The executable gate this Gate introduces is in the closed registry, not in an invocation."""

    RUNNER = PROJECT_ROOT / "scripts" / "iacode" / "gates" / "sandbox_tests.py"

    def test_the_sandbox_gate_is_mandatory(self) -> None:
        gates = policies.gate_definitions(PROJECT_ROOT)
        self.assertIn("sandboxTests", gates)
        self.assertTrue(gates["sandboxTests"]["mandatory"])
        self.assertIn("sandboxTests", policies.mandatory_gates(PROJECT_ROOT))

    def test_its_command_is_executable_from_the_repository_root(self) -> None:
        command = policies.gate_definitions(PROJECT_ROOT)["sandboxTests"]["command"]
        self.assertEqual(command, ["python", "scripts/iacode/gates/sandbox_tests.py"])
        self.assertTrue(self.RUNNER.is_file())

    def test_the_gate_builds_both_images_before_it_measures(self) -> None:
        """`LSN-0036`: a gate that runs inside an image it did not build measures the past.

        The sandbox gate depends on two images: the service's, which carries the suite, and the
        sandbox profile the suite creates containers from. Both are built before pytest runs.
        """
        source = self.RUNNER.read_text(encoding="utf-8")
        self.assertIn('build_service("sandbox")', source)
        self.assertIn("sandbox_image.py", source)
        measured = source.index("pytest")
        self.assertLess(source.index('build_service("sandbox")'), measured)
        self.assertLess(source.index("sandbox_image.py"), measured)


class Gate3TestSuiteRegistryTests(unittest.TestCase):
    """The suite this Gate introduces is declared, counted and resolvable as evidence."""

    def test_the_sandbox_suite_is_declared_and_counted(self) -> None:
        suites = {item["id"]: item for item in policies.load_test_suites(PROJECT_ROOT)}
        self.assertIn("sandbox", suites)
        self.assertTrue(suites["sandbox"]["counted"])
        self.assertEqual(suites["sandbox"]["root"], "services/sandbox/tests")
        self.assertEqual(suites["sandbox"]["framework"], "python-pytest")
        self.assertTrue((PROJECT_ROOT / suites["sandbox"]["root"]).is_dir())

    def test_the_suites_case_identifiers_resolve_as_evidence(self) -> None:
        identifiers = collect_test_ids(PROJECT_ROOT)
        for reference in ("ContainerIsolationTests", "PathResolverTests", "ResourceLimitTests",
                          "SessionRecoveryTests", "AgentResultBoundTests", "ToolRegistryTests",
                          "test_a_timeout_kills_the_whole_process_tree"):
            with self.subTest(reference=reference):
                self.assertIn(reference, identifiers)


class Gate3RedTeamHarnessTests(unittest.TestCase):
    """The battery is executable, scoped to the sandbox, and records a null-mutation control."""

    HARNESS = SCRIPTS / "gate3_red_team.py"
    SANDBOX_HALF = SCRIPTS / "gate3_sandbox_attacks.py"

    def test_the_battery_exists_and_declares_its_attacks(self) -> None:
        self.assertTrue(self.HARNESS.is_file())
        self.assertTrue(self.SANDBOX_HALF.is_file())
        import re

        source = self.HARNESS.read_text(encoding="utf-8")
        declared = re.findall(r'\("(G3-[A-Z])",', source)
        host = re.findall(r'"(G3-[A-Z])", "', source)
        self.assertGreaterEqual(len(set(declared) | set(host)), 20,
                                "the battery declares fewer attacks than the Gate asked for")
        self.assertEqual(len(declared), len(set(declared)), "an attack identifier is duplicated")
        self.assertIn("baseline_control", source)

    def test_the_battery_refuses_to_report_without_its_control(self) -> None:
        source = self.HARNESS.read_text(encoding="utf-8")
        self.assertIn("the null-mutation control failed", source)
        self.assertIn("raise LedgerError", source)
        self.assertIn("the battery leaves no sandbox behind", source)

    def test_every_attack_in_the_sandbox_half_is_declared_on_the_host(self) -> None:
        import re

        harness = self.HARNESS.read_text(encoding="utf-8")
        sandbox = self.SANDBOX_HALF.read_text(encoding="utf-8")
        executed = set(re.findall(r'"(G3-[A-Z])": ', sandbox))
        declared = set(re.findall(r'\("(G3-[A-Z])",', harness))
        self.assertGreaterEqual(len(executed), 20)
        self.assertEqual(executed, declared, "a verdict nobody declared, or a declaration nobody "
                                             "executes")

    def test_the_battery_carries_no_credential_of_its_own(self) -> None:
        """It plants a credential-shaped value, built at run time, never written in its source."""
        for path in (self.HARNESS, self.SANDBOX_HALF):
            with self.subTest(module=path.name):
                self.assertEqual(ledger_common.find_secrets(path.read_text(encoding="utf-8")), [])

    def test_the_sandbox_half_attacks_through_the_real_engine(self) -> None:
        source = self.SANDBOX_HALF.read_text(encoding="utf-8")
        self.assertIn("backend=DockerBackend()", source)
        self.assertNotIn("FakeBackend", source)
        harness = ast.unparse(function(self.HARNESS.read_text(encoding="utf-8"),
                                       "run_sandbox_attacks"))
        self.assertLess(harness.index("'build', 'sandbox'"), harness.index("'run', '--rm'"))
        self.assertLess(harness.index("sandbox_image.py"), harness.index("'run', '--rm'"))


class Gate3ScopeTests(unittest.TestCase):
    """The reservation this Gate owns is consumed; every later Gate's is still enforced.

    The Gate a scope control is asked about is derived, never named (`LSN-0037`).
    """

    @staticmethod
    def current() -> str:
        return ledger_common.delivered_gate(PROJECT_ROOT)

    def test_the_sandbox_reservation_belongs_to_this_gate_and_is_consumed(self) -> None:
        reservations = {item["path"]: item for item in policies.load_gate_scope(PROJECT_ROOT)}
        self.assertIn("services/sandbox", reservations)
        self.assertEqual(ledger_common.normalize_gate(reservations["services/sandbox"]["gate"]),
                         ledger_common.normalize_gate(GATE))
        in_force = {item["path"]
                    for item in policies.reservations_in_force(PROJECT_ROOT, self.current())}
        self.assertNotIn("services/sandbox", in_force,
                         "the Gate that owns the directory is still constrained by it")

    def test_the_delivery_filled_the_directory_it_owns(self) -> None:
        for name in ("contracts.py", "policy.py", "tools.py", "paths.py", "backend.py",
                     "service.py", "helper.py", "worker.py"):
            with self.subTest(module=name):
                self.assertTrue((SANDBOX_SOURCE / name).is_file())
        readme = (SANDBOX_ROOT / "README.md").read_text(encoding="utf-8")
        self.assertNotIn(policies.RESERVATION_MARKER, readme)

    def test_the_command_line_stays_reserved_for_its_own_gate(self) -> None:
        in_force = {item["path"]: item
                    for item in policies.reservations_in_force(PROJECT_ROOT, self.current())}
        self.assertIn("apps/cli", in_force)
        self.assertEqual(sorted(path.name for path in (PROJECT_ROOT / "apps" / "cli").iterdir()),
                         ["README.md"])
        self.assertEqual(policies.scope_violations(PROJECT_ROOT, self.current()), [])

    def test_the_gate_after_this_one_has_not_started(self) -> None:
        """No directory the next Gate owns carries anything but its reservation notice."""
        order = policies.gate_order()
        position = order.index(ledger_common.normalize_gate(GATE))
        following = order[position + 1]
        owned = [item for item in policies.load_gate_scope(PROJECT_ROOT)
                 if ledger_common.normalize_gate(str(item["gate"])) == following]
        self.assertTrue(owned, "the next Gate owns no reservation, which cannot be right")
        for reservation in owned:
            directory = PROJECT_ROOT / str(reservation["path"])
            with self.subTest(path=str(reservation["path"])):
                present = sorted(path.name for path in directory.iterdir()) \
                    if directory.is_dir() else []
                self.assertTrue(set(present) <= set(policies.RESERVATION_ALLOWED_FILES), present)


# ---------------------------------------------------------------------------------------------
# 2. The boundary between the runtime and the sandbox, read from the whole tree
# ---------------------------------------------------------------------------------------------


#: What only the sandbox service may import: its own package and a container client.
SANDBOX_ONLY_MODULES = frozenset({"iacode_sandbox", "docker"})


def sandbox_imports(source: str) -> set[str]:
    return {name for name in imported_names(source)
            if name.split(".")[0] in SANDBOX_ONLY_MODULES}


class SandboxBoundaryTests(unittest.TestCase):
    """Sandbox logic lives in the sandbox service and nowhere else.

    The API routes, the Agent Runtime, the Model Gateway and the orchestrator worker reach the
    sandbox only through the contract constants and the activity names in `iacode_contracts`; none
    of them imports the sandbox package or a container client.
    """

    OUTSIDE = (
        PROJECT_ROOT / "apps" / "api" / "src",
        PROJECT_ROOT / "services" / "agent-runtime" / "src",
        PROJECT_ROOT / "services" / "model-gateway" / "src",
        PROJECT_ROOT / "services" / "orchestrator" / "src",
        PROJECT_ROOT / "packages",
    )

    def outside(self) -> list[Path]:
        return [path for root in self.OUTSIDE for path in python_files(root)]

    def test_the_boundary_has_something_to_scan(self) -> None:
        self.assertGreaterEqual(len(self.outside()), 60)
        self.assertGreaterEqual(len(python_files(SANDBOX_SOURCE)), 10)

    def test_the_sandbox_is_its_own_service_with_its_own_contracts(self) -> None:
        self.assertTrue((SANDBOX_ROOT / "pyproject.toml").is_file())
        self.assertTrue((SANDBOX_ROOT / "Dockerfile").is_file())
        self.assertTrue((SANDBOX_SOURCE / "contracts.py").is_file())
        self.assertTrue((PROJECT_ROOT / "docs" / "adr" /
                         "ADR-0025-sandbox-isolation-boundary.md").is_file())

    def test_no_module_outside_the_sandbox_imports_it_or_a_container_client(self) -> None:
        offenders = [f"{path.relative_to(PROJECT_ROOT).as_posix()}: {sorted(found)}"
                     for path in self.outside()
                     if (found := sandbox_imports(path.read_text(encoding="utf-8")))]
        self.assertEqual(offenders, [], f"sandbox logic escaped its service: {offenders}")

    def test_the_scan_detects_a_module_that_does_it(self) -> None:
        """The null control over a mutated module, and the unmutated one it must pass."""
        mutated = "from iacode_sandbox.service import SandboxService\nimport docker\n"
        self.assertEqual(sandbox_imports(mutated), {"iacode_sandbox.service", "docker"})
        self.assertEqual(sandbox_imports("from iacode_contracts.sandbox import X\n"), set())

    def test_the_health_is_a_poller_and_an_engine_not_a_process(self) -> None:
        source = (SANDBOX_SOURCE / "healthcheck.py").read_text(encoding="utf-8")
        self.assertIn("describe_task_queue", source)
        self.assertIn("DockerBackend", source)

    def test_the_observability_stack_scrapes_the_service(self) -> None:
        text = (PROJECT_ROOT / "infra" / "prometheus" / "prometheus.yml").read_text(
            encoding="utf-8")
        self.assertIn("job_name: iacode-sandbox", text)
        self.assertIn('"sandbox:9102"', text)


def payload_keys_and_policy(source: str) -> tuple[set[str], str]:
    """The keys of the payload the workflow sends the sandbox, and where its policy comes from."""
    dispatch = function(source, "_execute_in_sandbox")
    for node in ast.walk(dispatch):
        if (isinstance(node, ast.Assign) and len(node.targets) == 1
                and isinstance(node.targets[0], ast.Name) and node.targets[0].id == "payload"
                and isinstance(node.value, ast.Dict)):
            keys = {key.value for key in node.value.keys if isinstance(key, ast.Constant)}
            policy = next(ast.unparse(value) for key, value in
                          zip(node.value.keys, node.value.values, strict=True)
                          if isinstance(key, ast.Constant) and key.value == "policy")
            return keys, policy
    raise AssertionError("the dispatch builds no payload")


def result_key_literals(source: str) -> list[str]:
    """String literals that spell a key of the execute activity's answer instead of naming it."""
    return [node.value for node in ast.walk(ast.parse(source))
            if isinstance(node, ast.Constant) and node.value in ("agentResult", "execution")]


class WorkflowSandboxDispatchTests(unittest.TestCase):
    """What the workflow sends the sandbox, when, and what it does with the answer."""

    EXPECTED_PAYLOAD = {"contractVersion", "toolRequestId", "runId", "agentRunId", "agent",
                        "tool", "arguments", "policy", "workspace"}

    @classmethod
    def setUpClass(cls) -> None:
        cls.source = WORKFLOW.read_text(encoding="utf-8")

    def test_only_a_stage_with_a_sandbox_policy_dispatches(self) -> None:
        wait = function(self.source, "wait_for_tool")
        text = ast.unparse(wait)
        self.assertIn("stage.sandbox_policy", text)
        self.assertIn("self._execute_in_sandbox", text)
        # The previous Gate's path is still there for every other stage.
        self.assertIn("iacode_agent_runtime_read_tool_result", text)
        self.assertIn("workflow.wait_condition", text)

    def test_the_policy_is_the_stages_and_the_request_carries_no_setting(self) -> None:
        keys, policy = payload_keys_and_policy(self.source)
        self.assertEqual(keys, self.EXPECTED_PAYLOAD)
        self.assertEqual(policy, "stage.sandbox_policy")

    def test_the_scan_detects_a_policy_taken_from_the_request(self) -> None:
        """The null control: the identical scan over a mutated dispatch."""
        mutated = self.source.replace('"policy": stage.sandbox_policy',
                                      '"policy": request["arguments"].get("policy")', 1)
        self.assertNotEqual(mutated, self.source)
        self.assertNotEqual(payload_keys_and_policy(mutated)[1], "stage.sandbox_policy")

    def test_the_execution_is_an_activity_on_the_sandbox_queue_and_bounded(self) -> None:
        dispatch = ast.unparse(function(self.source, "_execute_in_sandbox"))
        self.assertIn("workflow.start_activity(SANDBOX_EXECUTE_ACTIVITY", dispatch)
        self.assertIn("task_queue=SANDBOX_TASK_QUEUE", dispatch)
        self.assertIn("schedule_to_close_timeout=timedelta(seconds=timeout_seconds)", dispatch)
        self.assertIn("heartbeat_timeout=SANDBOX_HEARTBEAT_TIMEOUT", dispatch)

    def test_a_sandbox_that_cannot_answer_is_a_failed_result_not_a_wait(self) -> None:
        dispatch = ast.unparse(function(self.source, "_execute_in_sandbox"))
        self.assertIn("except ActivityError", dispatch)
        self.assertIn("SANDBOX_UNAVAILABLE", dispatch)
        self.assertIn("'status': 'FAILED'", dispatch)

    def test_the_result_is_persisted_through_the_store_before_the_run_resumes(self) -> None:
        dispatch = ast.unparse(function(self.source, "_execute_in_sandbox"))
        self.assertIn("iacode_agent_runtime_resolve_tool_request", dispatch)
        self.assertIn("ToolResult.from_dict(stored)", dispatch)
        activities = (PROJECT_ROOT / "services" / "orchestrator" / "src" / "iacode_orchestrator"
                      / "agent_runtime" / "activities.py").read_text(encoding="utf-8")
        self.assertIn('@activity.defn(name="iacode_agent_runtime_resolve_tool_request")',
                      activities)

    def test_a_cancellation_cancels_the_execution_and_waits_for_it(self) -> None:
        dispatch = ast.unparse(function(self.source, "_execute_in_sandbox"))
        self.assertIn("handle.cancel()", dispatch)
        self.assertIn("ActivityCancellationType.WAIT_CANCELLATION_COMPLETED", dispatch)

    def test_the_sandbox_is_released_when_the_run_ends(self) -> None:
        run = ast.unparse(function(self.source, "run"))
        self.assertIn("await effects.release_sandboxes()", run)
        self.assertLess(run.index("release_sandboxes"), run.index("self.state = outcome.state"))
        release = ast.unparse(function(self.source, "release_sandboxes"))
        self.assertIn("SANDBOX_RELEASE_ACTIVITY", release)

    def test_both_sides_name_the_result_by_the_shared_key(self) -> None:
        """The producer and the consumer of the answer spell its keys once, in the contract.

        They live in two processes that share nothing but a queue. The first version had the
        workflow read ``"agentResult"`` from an answer that did not carry it, and every suite that
        drove one side against a double passed.
        """
        self.assertEqual(result_key_literals(self.source), [])
        worker = (SANDBOX_SOURCE / "worker.py").read_text(encoding="utf-8")
        self.assertEqual(result_key_literals(worker), [])
        dispatch = ast.unparse(function(self.source, "_execute_in_sandbox"))
        self.assertIn("body[SANDBOX_AGENT_RESULT_KEY]", dispatch)
        answer = ast.unparse(function(worker, "execute_tool"))
        self.assertIn("SANDBOX_AGENT_RESULT_KEY: result.agent_result()", answer)

    def test_the_key_scan_detects_a_literal(self) -> None:
        """The null control: the identical scan over a workflow that spells the key itself."""
        mutated = self.source.replace("body[SANDBOX_AGENT_RESULT_KEY]", "body['agentResult']", 1)
        self.assertNotEqual(mutated, self.source)
        self.assertEqual(result_key_literals(mutated), ["agentResult"])

    def test_the_sandbox_registers_both_activities_on_its_queue(self) -> None:
        worker = (SANDBOX_SOURCE / "worker.py").read_text(encoding="utf-8")
        self.assertIn("@activity.defn(name=SANDBOX_EXECUTE_ACTIVITY)", worker)
        self.assertIn("@activity.defn(name=SANDBOX_RELEASE_ACTIVITY)", worker)
        self.assertIn("task_queue=SANDBOX_TASK_QUEUE", worker)


# ---------------------------------------------------------------------------------------------
# 3. One path resolver
# ---------------------------------------------------------------------------------------------


#: The helper operations that take a path or a working directory from the request.
PATH_TAKING_OPERATIONS = ("op_list", "op_read", "op_write", "op_search", "op_exec")


def unresolved_operations(source: str) -> list[str]:
    """Helper operations that read a path from the request without the one resolver."""
    offenders = []
    for name in PATH_TAKING_OPERATIONS:
        node = function(source, name)
        reads_a_path = any(
            isinstance(item, ast.Constant) and item.value in ("path", "cwd")
            for item in ast.walk(node))
        if reads_a_path and "_resolve" not in called(node):
            offenders.append(name)
    return offenders


def refusals_outside_the_resolver(paths: list[Path]) -> list[str]:
    return [path.name for path in paths if path.name != "paths.py"
            and "PathRejectedError" in called(ast.parse(path.read_text(encoding="utf-8")))]


class SinglePathResolverTests(unittest.TestCase):
    """One canonical resolver decides every path; no module re-implements path safety.

    The property is "no resolved path leaves the workspace", and the one place that decides it is
    `iacode_sandbox.paths`. What is asserted here is that every path a tool touches reaches it: the
    request normaliser on the controller, the helper's operations and the patch applier inside the
    sandbox — and that no other module raises the resolver's refusal on its own account.
    """

    HELPER = SANDBOX_SOURCE / "helper.py"

    def test_every_path_taking_operation_goes_through_the_resolver(self) -> None:
        source = self.HELPER.read_text(encoding="utf-8")
        self.assertEqual(unresolved_operations(source), [])
        self.assertIn("resolve_workspace_path", called(function(source, "_resolve")))

    def test_the_patch_and_the_request_normaliser_use_the_same_resolver(self) -> None:
        patching = (SANDBOX_SOURCE / "patching.py").read_text(encoding="utf-8")
        self.assertIn("resolve_workspace_path", called(ast.parse(patching)))
        tools = (SANDBOX_SOURCE / "tools.py").read_text(encoding="utf-8")
        self.assertIn("normalize_request_path", called(ast.parse(tools)))

    def test_no_other_module_decides_a_path_refusal(self) -> None:
        self.assertEqual(refusals_outside_the_resolver(python_files(SANDBOX_SOURCE)), [])

    def test_the_sandbox_runs_the_resolver_the_repository_tests(self) -> None:
        dockerfile = (SANDBOX_ROOT / "images" / "iacode-dev" / "Dockerfile").read_text(
            encoding="utf-8")
        self.assertIn("COPY services/sandbox/src/iacode_sandbox/paths.py /opt/iacode/paths.py",
                      dockerfile)

    def test_the_scans_detect_a_bypass(self) -> None:
        """The null control: an operation that opens the requested path directly is caught."""
        source = self.HELPER.read_text(encoding="utf-8")
        mutated = source.replace(
            'path = _resolve(request.get("path"), allow_root=False)',
            'path = Path(WORKSPACE) / str(request.get("path"))', 1)
        self.assertNotEqual(mutated, source)
        self.assertEqual(unresolved_operations(mutated), ["op_read"])

        with tempfile.TemporaryDirectory(prefix="iacode-resolver-") as workdir:
            planted = Path(workdir) / "shortcut.py"
            planted.write_text("def check(p):\n    raise PathRejectedError('PATH_ESCAPE', p)\n",
                               encoding="utf-8")
            self.assertEqual(refusals_outside_the_resolver([planted]), ["shortcut.py"])


# ---------------------------------------------------------------------------------------------
# 4. Agents, policies and the sandbox image
# ---------------------------------------------------------------------------------------------


def profile_policy_violations(profiles: dict[str, dict], policy: dict) -> list[str]:
    """Profiles whose permitted actions are not inside their sandbox policy's tools."""
    tools = {item["name"]: set(item["tools"]) for item in policy["sandboxPolicies"]}
    violations = []
    for name, profile in sorted(profiles.items()):
        actions = set(profile.get("allowedActions") or [])
        governing = profile.get("sandboxPolicy")
        if actions and governing not in tools:
            violations.append(f"{name}: tools with no sandbox policy")
        elif actions - tools.get(governing, set()):
            violations.append(f"{name}: {sorted(actions - tools[governing])} outside {governing}")
    return violations


def load_profiles() -> dict[str, dict]:
    return {path.stem: json.loads(path.read_text(encoding="utf-8"))
            for path in sorted((PROJECT_ROOT / "agents" / "profiles").glob("*.json"))}


WRITING_TOOLS = {"filesystem.write", "filesystem.apply_patch", "shell.exec", "git.add",
                 "git.commit"}


class Gate3AgentToolPolicyTests(unittest.TestCase):
    """No agent is given a tool its sandbox policy does not allow, and no agent gets everything."""

    def test_every_profiles_actions_are_inside_its_policy(self) -> None:
        self.assertEqual(profile_policy_violations(load_profiles(), load_sandbox_policy()), [])

    def test_the_scan_detects_a_profile_that_exceeds_its_policy(self) -> None:
        """The null control: one planted action over the unmutated profiles."""
        profiles = load_profiles()
        self.assertEqual(profile_policy_violations(profiles, load_sandbox_policy()), [])
        profiles["code-reviewer"] = dict(profiles["code-reviewer"])
        profiles["code-reviewer"]["allowedActions"] = [
            *profiles["code-reviewer"]["allowedActions"], "filesystem.write"]
        self.assertEqual(len(profile_policy_violations(profiles, load_sandbox_policy())), 1)

    def test_no_agent_is_given_every_tool_by_default(self) -> None:
        profiles = load_profiles()
        with_tools = {name for name, item in profiles.items() if item.get("allowedActions")}
        self.assertEqual(with_tools, {"developer", "code-reviewer"})
        self.assertFalse(set(profiles["code-reviewer"]["allowedActions"]) & WRITING_TOOLS)

    def test_the_planner_has_no_tool_and_no_policy(self) -> None:
        planner = load_profiles()["planner"]
        self.assertEqual(planner.get("allowedActions"), [])
        self.assertIsNone(planner.get("sandboxPolicy"))

    def test_a_read_only_policy_offers_no_writing_tool(self) -> None:
        for item in load_sandbox_policy()["sandboxPolicies"]:
            if item["workspaceAccess"] == "read-only":
                with self.subTest(policy=item["name"]):
                    self.assertFalse(set(item["tools"]) & WRITING_TOOLS)

    def test_the_runtime_accepts_every_result_the_sandbox_hands_over(self) -> None:
        """Two limits in two services that must agree are read from their sources and compared.

        The sandbox shortens what it hands an agent to its bound; the runtime refuses a tool
        result larger than its own. A runtime bound below the sandbox's would fail a run for a
        result the sandbox considered deliverable.
        """
        sandbox = constant_value(
            (PROJECT_ROOT / "packages" / "contracts" / "src" / "iacode_contracts" / "sandbox.py")
            .read_text(encoding="utf-8"), "SANDBOX_AGENT_RESULT_MAX_BYTES")
        runtime = constant_value(
            (PROJECT_ROOT / "services" / "agent-runtime" / "src" / "iacode_agent_runtime"
             / "limits.py").read_text(encoding="utf-8"), "max_tool_result_bytes")
        self.assertGreater(sandbox, 0)
        self.assertLessEqual(sandbox, runtime)
        contracts = (SANDBOX_SOURCE / "contracts.py").read_text(encoding="utf-8")
        self.assertIn("fit_agent_output", called(function(contracts, "agent_result")))


class SandboxImageProfileTests(unittest.TestCase):
    """The image a sandbox runs is declared, pinned, built from known inputs and unprivileged."""

    @staticmethod
    def dockerfile(profile: dict) -> str:
        return (PROJECT_ROOT / profile["context"] / "Dockerfile").read_text(encoding="utf-8")

    def test_the_registry_declares_a_functional_profile(self) -> None:
        profiles = {item["name"]: item for item in load_sandbox_policy()["imageProfiles"]}
        self.assertIn("iacode-dev", profiles)
        used = {item["imageProfile"] for item in load_sandbox_policy()["sandboxPolicies"]}
        self.assertTrue(used <= set(profiles), "a policy names an image profile nobody declares")

    def test_every_profile_is_pinned_and_unprivileged(self) -> None:
        import re

        for profile in load_sandbox_policy()["imageProfiles"]:
            text = self.dockerfile(profile)
            with self.subTest(profile=profile["name"]):
                bases = re.findall(r"(?m)^FROM\s+(\S+)", text)
                self.assertTrue(bases)
                for base in bases:
                    self.assertRegex(base, r"@sha256:[0-9a-f]{64}$")
                    self.assertNotIn(":latest", base)
                installs = re.findall(r"apt-get install[^&]*", text)
                for install in installs:
                    for package in install.split()[2:]:
                        if not package.startswith("-") and package != chr(92):
                            self.assertIn("=", package, f"{package} is not pinned")
                users = re.findall(r"(?m)^USER\s+(\S+)", text)
                self.assertTrue(users)
                self.assertNotIn(users[-1], ("root", "0"))

    def test_the_project_profile_carries_git_and_python(self) -> None:
        text = self.dockerfile({"context": "services/sandbox/images/iacode-dev"})
        self.assertIn("git=", text)
        self.assertIn("FROM python:3.13", text)

    def test_the_image_is_addressed_by_its_inputs(self) -> None:
        builder = (PROJECT_ROOT / "scripts" / "iacode" / "sandbox_image.py").read_text(
            encoding="utf-8")
        image = (SANDBOX_SOURCE / "image.py").read_text(encoding="utf-8")
        self.assertIn('FINGERPRINT_LABEL = "org.iacode.sandbox.fingerprint"', image)
        self.assertIn("input_fingerprint", builder)
        self.assertIn("FINGERPRINT_LABEL", builder)

    def test_the_service_installs_the_scanned_lock_and_a_pinned_client(self) -> None:
        service = (SANDBOX_ROOT / "Dockerfile").read_text(encoding="utf-8")
        scan = (PROJECT_ROOT / "scripts" / "iacode" / "dependency_scan.py").read_text(
            encoding="utf-8")
        self.assertIn("COPY apps/api/requirements.lock.txt", service)
        self.assertIn('"apps" / "api" / "requirements.lock.txt"', scan)
        self.assertRegex(service, r"ARG DOCKER_SHA256=[0-9a-f]{64}")
        self.assertIn("if digest != expected", service)


SANDBOX_RUNBOOK = PROJECT_ROOT / "docs" / "runbooks" / "SANDBOX.md"


class Gate3DocumentationTests(unittest.TestCase):
    """The documents describe what this Gate delivered rather than what was planned."""

    @staticmethod
    def read(*parts: str) -> str:
        return PROJECT_ROOT.joinpath(*parts).read_text(encoding="utf-8")

    def test_the_entry_point_names_the_current_gate(self) -> None:
        text = self.read("START-HERE.md")
        for expected in ("GATE 3", "docs/GATE-3-CHECKLIST.md", "docs/runbooks/SANDBOX.md",
                         "READY_FOR_MILESTONE_AUDIT"):
            with self.subTest(expected=expected):
                self.assertIn(expected, text)

    def test_the_architecture_describes_the_sandbox_and_its_boundary(self) -> None:
        text = self.read("docs", "ARCHITECTURE.md")
        for expected in ("## The sandbox", "ADR-0024", "ADR-0025", "ADR-0026", "ADR-0027",
                         "iacode-sandbox", "runbooks/SANDBOX.md"):
            with self.subTest(expected=expected):
                self.assertIn(expected, text)

    def test_the_readme_and_versions_mention_the_gate(self) -> None:
        self.assertIn("GATE 3 — SANDBOX", self.read("README.md"))
        versions = self.read("docs", "VERSIONS.md")
        for expected in ("sandbox-iacode-dev", "services/sandbox", "29.6.1"):
            with self.subTest(expected=expected):
                self.assertIn(expected, versions)

    def test_the_development_document_names_the_gate_and_its_suite(self) -> None:
        text = self.read("docs", "DEVELOPMENT.md")
        for expected in ("sandboxTests", "services/sandbox", "sandbox_coding_e2e.py"):
            with self.subTest(expected=expected):
                self.assertIn(expected, text)

    def test_the_runbook_covers_the_declared_topics(self) -> None:
        text = SANDBOX_RUNBOOK.read_text(encoding="utf-8")
        for topic in ("The security boundary", "## Lifecycle", "## The tool policy",
                      "## Filesystem", "## Shell", "## Git", "## Network", "## Resources",
                      "## Artifacts", "## Cleanup and recovery", "## Scenarios",
                      "## Dependency scanning", "## Observability", "## Debugging"):
            with self.subTest(topic=topic):
                self.assertIn(topic, text)

    def test_the_agents_git_identity_is_documented_apart_from_the_owners(self) -> None:
        text = SANDBOX_RUNBOOK.read_text(encoding="utf-8")
        self.assertIn("IACode Agent", text)
        self.assertIn("ADR-0024", text)
        policy = load_sandbox_policy()["gitIdentity"]
        self.assertIn(policy["name"], text)
        self.assertIn(policy["email"], text)

    def test_the_runbook_never_prints_a_credential(self) -> None:
        text = SANDBOX_RUNBOOK.read_text(encoding="utf-8")
        self.assertEqual(ledger_common.find_secrets(text), [])


class Gate3AdrTests(unittest.TestCase):
    """The structural decisions of this Gate are recorded and indexed."""

    DECISIONS = ("ADR-0024", "ADR-0025", "ADR-0026", "ADR-0027")

    def test_every_decision_is_recorded(self) -> None:
        records = {identifier: (title, status)
                   for identifier, title, status, _name in adr_records(ADR_DIRECTORY)}
        for identifier in self.DECISIONS:
            with self.subTest(adr=identifier):
                self.assertIn(identifier, records)
                self.assertEqual(records[identifier][1], "Accepted")

    def test_the_index_lists_them(self) -> None:
        listed = {identifier for identifier, *_rest in
                  adr_index_rows(ADR_DIRECTORY / "README.md")}
        self.assertTrue(set(self.DECISIONS) <= listed)


# ---------------------------------------------------------------------------------------------
# 5. Verification stages and the deterministic scenarios
# ---------------------------------------------------------------------------------------------


SCENARIO = PROJECT_ROOT / "scripts" / "iacode" / "scenarios" / "sandbox_coding_e2e.py"
REHEARSAL = PROJECT_ROOT / "services" / "orchestrator" / "rehearsal" / "coding.py"
VERIFY = PROJECT_ROOT / "scripts" / "iacode" / "verify.py"

#: Modules that let a process start another one or reach a shell.
EXECUTION_MODULES = frozenset({"subprocess", "multiprocessing", "pty", "docker", "paramiko",
                               "pexpect", "git", "dulwich", "pygit2"})

#: Calls that execute a process or rewrite the filesystem outside the process's own scratch.
EXECUTING_CALLS = frozenset({"os.system", "os.popen", "os.execv", "os.spawnv", "os.kill",
                             "subprocess.run", "subprocess.Popen", "shutil.rmtree", "eval",
                             "exec", "__import__"})


def executes(source: str) -> set[str]:
    tree = ast.parse(source)
    found = {name for name in imported_names(source) if name.split(".")[0] in EXECUTION_MODULES}
    return found | (called(tree) & EXECUTING_CALLS)


class Gate3VerificationStageTests(unittest.TestCase):
    """The verification command covers this Gate, in its targeted and its full mode."""

    STAGES = {"sandbox-integration": '"-m", "integration"',
              "sandbox-coding": "coding", "sandbox-timeout": "timeout",
              "sandbox-cancellation": "cancel", "sandbox-recovery": "recovery",
              "sandbox-tool-result-origin": "forged-result"}

    @classmethod
    def setUpClass(cls) -> None:
        cls.source = VERIFY.read_text(encoding="utf-8")

    def test_the_verification_adds_the_stages_this_gate_introduces(self) -> None:
        for stage, argument in self.STAGES.items():
            with self.subTest(stage=stage):
                self.assertIn(f'"{stage}"', self.source)
                self.assertIn(argument, self.source)

    def test_the_scenario_stages_run_in_the_targeted_mode_too(self) -> None:
        """They restart no service of the stack but the sandbox, so they are not destructive."""
        fast_only = self.source.index("if not fast:")
        for stage in self.STAGES:
            with self.subTest(stage=stage):
                self.assertLess(self.source.index(f'"{stage}"'), fast_only)

    def test_the_mandatory_gate_deselects_what_needs_the_stack(self) -> None:
        runner = (PROJECT_ROOT / "scripts" / "iacode" / "gates" / "sandbox_tests.py").read_text(
            encoding="utf-8")
        self.assertIn('"not integration"', runner)
        project = (SANDBOX_ROOT / "pyproject.toml").read_text(encoding="utf-8")
        self.assertIn('"integration:', project)


class SandboxScenarioTests(unittest.TestCase):
    """What the deterministic scenarios exercise, and what they are allowed to substitute."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.scenario = SCENARIO.read_text(encoding="utf-8")
        cls.rehearsal = REHEARSAL.read_text(encoding="utf-8")

    def test_the_four_scenarios_exist(self) -> None:
        for name in ("scenario_coding", "scenario_timeout", "scenario_cancel",
                     "scenario_recovery", "scenario_forged_result"):
            with self.subTest(scenario=name):
                function(self.scenario, name)

    def test_the_scenario_builds_what_it_measures_first(self) -> None:
        """`LSN-0036`: the worker image, the service image and the sandbox image are all rebuilt."""
        prepare = ast.unparse(function(self.scenario, "prepare_images"))
        for built in ("build_service('worker')", "build_service('sandbox')", "sandbox_image.py"):
            with self.subTest(built=built):
                self.assertIn(built, prepare)
        main = ast.unparse(function(self.scenario, "main"))
        self.assertLess(main.index("prepare_images()"), main.index("start_rehearsal()"))

    def test_only_the_model_is_substituted(self) -> None:
        """The run is created by the runtime's own service and executed by the real workflow."""
        self.assertIn("AgentRuntimeService(", self.rehearsal)
        self.assertIn("service.create_run(", self.rehearsal)
        self.assertIn("workflows=[AgentRunWorkflow]", self.rehearsal)
        self.assertIn('@activity.defn(name="iacode_agent_runtime_call_model")', self.rehearsal)
        activities = {node.id for node in ast.walk(function(self.rehearsal, "run_worker"))
                      if isinstance(node, ast.Name)}
        self.assertIn("resolve_tool_request", activities)
        self.assertNotIn("execute_tool", self.rehearsal,
                         "the rehearsal answers its own tool requests instead of the sandbox")

    def test_the_rehearsal_executes_nothing(self) -> None:
        """It asks for tools; the sandbox executes them. The scan over it must find nothing."""
        self.assertEqual(executes(self.rehearsal), set())
        self.assertFalse((PROJECT_ROOT / "services" / "orchestrator" / "src" /
                          "iacode_orchestrator" / "rehearsal").exists())

    def test_the_execution_scan_detects_a_harness_that_executes(self) -> None:
        """The null control over a mutated harness."""
        mutated = self.rehearsal + "\nimport subprocess\nsubprocess.run(['sh', '-c', 'id'])\n"
        self.assertEqual(executes(mutated), {"subprocess", "subprocess.run"})

    def test_the_workspace_is_a_synthetic_snapshot_never_the_working_tree(self) -> None:
        snapshot = ast.unparse(function(self.scenario, "synthetic_snapshot"))
        self.assertIn("create_snapshot(source", snapshot)
        self.assertNotIn("REPOSITORY_ROOT", snapshot)
        self.assertIn("tempfile.TemporaryDirectory", self.scenario)

    def test_the_host_sentinel_is_compared_by_content(self) -> None:
        coding = ast.unparse(function(self.scenario, "scenario_coding"))
        self.assertIn("digest(sentinel) == before", coding)
        self.assertIn("host.no_file_appeared", coding)
        self.assertIn("WRITE-{index}=REFUSED", coding)

    def test_the_assertions_read_what_the_run_recorded(self) -> None:
        """Every verdict is read from the harness's report of the database, not from a request."""
        for name in ("scenario_coding", "scenario_timeout", "scenario_cancel",
                     "scenario_recovery", "scenario_forged_result"):
            with self.subTest(scenario=name):
                self.assertIn("harness('report'", ast.unparse(function(self.scenario, name)))
        report = ast.unparse(function(self.rehearsal, "report"))
        for table in ("ToolCall", "ToolResult", "SandboxSession", "RunEvent"):
            self.assertIn(table, report)


# ---------------------------------------------------------------------------------------------
# 6. M1-F-003: sealed evidence is judged from the published history
# ---------------------------------------------------------------------------------------------


def _rev(root: Path, reference: str) -> str:
    return subprocess.run(["git", "rev-parse", reference], cwd=root, check=True,
                          capture_output=True, text=True, encoding="utf-8").stdout.strip()


def _published_fixture(base: Path) -> tuple[Path, str, str]:
    """A repository holding one published commit and one commit nothing references.

    The second is made with ``commit-tree``, which writes a commit object and no reference: the
    state `b59d66f9f3f9` was in, a closure commit replaced before the history was published.
    """
    source = base / "source"
    source.mkdir(parents=True)
    _git(source, "init", "-q", "-b", "main")
    _git(source, "config", "user.name", "IACode Tests")
    _git(source, "config", "user.email", "iacode-tests@example.invalid")
    (source / "a.txt").write_text("published\n", encoding="utf-8")
    _git(source, "add", "a.txt")
    _git(source, "commit", "-q", "-m", "published")
    published = _rev(source, "HEAD")
    orphan = subprocess.run(
        ["git", "commit-tree", _rev(source, "HEAD^{tree}"), "-p", published,
         "-m", "replaced before publication"],
        cwd=source, check=True, capture_output=True, text=True,
        encoding="utf-8").stdout.strip()
    return source, published, orphan


class PublishedHistoryTests(unittest.TestCase):
    """`M1-F-003`: a local object is not a published one, and the controls ask the second question.

    `GATE-1-CP-0001` named a commit that existed in the working repository's object store and in no
    published history. Every control over sealed history cloned the local path, which carries such
    objects, so all of them passed while every clone of the remote failed.
    """

    def setUp(self) -> None:
        self._directory = tempfile.TemporaryDirectory(prefix="iacode-published-")
        self.base = Path(self._directory.name)
        self.source, self.published, self.orphan = _published_fixture(self.base)

    def tearDown(self) -> None:
        self._directory.cleanup()

    def test_a_local_object_is_not_a_published_object(self) -> None:
        self.assertEqual(ledger_common.published_reachability(self.source, self.published),
                         ledger_common.PUBLISHED)
        self.assertEqual(ledger_common.published_reachability(self.source, self.orphan),
                         ledger_common.UNPUBLISHED_LOCAL_OBJECT)
        self.assertEqual(ledger_common.published_reachability(self.source, "0" * 40),
                         ledger_common.ABSENT_OBJECT)

    def test_a_published_clone_carries_only_what_a_published_reference_reaches(self) -> None:
        # The method the first guardrail used, kept here as the demonstration of the defect: a
        # copy of the object store brings the orphan along.
        copied = self.base / "copied"
        subprocess.run(["git", "clone", "--quiet", *LOCAL_OBJECT_STORE_COPY, str(self.source),
                        str(copied)], check=True, capture_output=True)
        self.assertEqual(ledger_common.published_reachability(copied, self.orphan),
                         ledger_common.UNPUBLISHED_LOCAL_OBJECT)

        clone = self.base / "clone"
        self.assertTrue(ledger_common.published_clone(self.source, clone))
        self.assertEqual(ledger_common.published_reachability(clone, self.published),
                         ledger_common.PUBLISHED)
        self.assertEqual(ledger_common.published_reachability(clone, self.orphan),
                         ledger_common.ABSENT_OBJECT)

    def test_a_published_reference_is_what_brings_the_object(self) -> None:
        _git(self.source, "tag", "iacode-preserved/fixture", self.orphan)
        self.assertEqual(ledger_common.published_reachability(self.source, self.orphan),
                         ledger_common.PUBLISHED)
        clone = self.base / "clone"
        self.assertTrue(ledger_common.published_clone(self.source, clone))
        self.assertEqual(ledger_common.published_reachability(clone, self.orphan),
                         ledger_common.PUBLISHED)

    def test_a_private_reference_does_not_publish_an_object(self) -> None:
        """The reference that protected `b59d66f9f3f9` from garbage collection published nothing."""
        _git(self.source, "update-ref", "refs/iacode-preserved/fixture", self.orphan)
        self.assertEqual(ledger_common.published_reachability(self.source, self.orphan),
                         ledger_common.UNPUBLISHED_LOCAL_OBJECT)

    def test_the_validator_refuses_a_record_naming_an_unpublished_commit(self) -> None:
        def errors_for(root: Path, commit: str) -> list[str]:
            found: list[str] = []
            validate_checkpoint._validate_published_history(
                root, [{"id": "cmd-0001", "commit": commit,
                        "repositoryState": {"head": commit}}], {}, found)
            return found

        # The null control: the identical path accepts a record naming the published commit.
        self.assertEqual(errors_for(self.source, self.published), [])

        local = errors_for(self.source, self.orphan)
        self.assertEqual(len(local), 1, local)
        self.assertIn("exists here only as a local object", local[0])
        self.assertIn(self.orphan[:12], local[0])

        clone = self.base / "clone"
        self.assertTrue(ledger_common.published_clone(self.source, clone))
        absent = errors_for(clone, self.orphan)
        self.assertEqual(len(absent), 1, absent)
        self.assertIn("absent from this repository", absent[0])

        _git(self.source, "tag", "iacode-preserved/fixture", self.orphan)
        self.assertEqual(errors_for(self.source, self.orphan), [])
        republished = self.base / "republished"
        self.assertTrue(ledger_common.published_clone(self.source, republished))
        self.assertEqual(errors_for(republished, self.orphan), [])

    def test_the_checkpoint_metadata_is_judged_by_the_same_rule(self) -> None:
        found: list[str] = []
        validate_checkpoint._validate_published_history(
            self.source, [], {"STATE.json": {"baseCommit": self.orphan, "currentCommit": "HEAD"},
                              "RUN-METADATA.json": {"initialCommit": self.published}}, found)
        self.assertEqual(len(found), 1, found)
        self.assertIn("STATE.json baseCommit", found[0])


#: The clone arguments that copy a local object store, unreachable objects included. Only the
#: demonstration of the defect above may use them.
LOCAL_OBJECT_STORE_COPY = ("--no-hardlinks",)


def preserved_references(root: Path) -> dict[str, str]:
    listed = subprocess.run(
        ["git", "for-each-ref", "--format=%(refname) %(objectname)", "refs/tags/iacode-preserved"],
        cwd=root, check=True, capture_output=True, text=True, encoding="utf-8").stdout
    return dict(line.split() for line in listed.splitlines() if line.strip())


def checkpoint_naming(root: Path, commit: str) -> str | None:
    """The anchored checkpoint whose sealed ledger names ``commit``, derived rather than named."""
    anchors = json.loads((root / ".iacode" / "anchors" / "checkpoint-chain.json")
                         .read_text(encoding="utf-8"))
    for anchor in anchors["anchors"]:
        ledger = root / "docs" / "checkpoints" / anchor["checkpointId"] / "COMMANDS.jsonl"
        if ledger.is_file() and commit in ledger.read_text(encoding="utf-8"):
            return str(anchor["checkpointId"])
    return None


class PreservedReferenceTests(unittest.TestCase):
    """`M1-F-003` on the real sealed history: every preserved reference is load-bearing.

    For each published ``refs/tags/iacode-preserved/`` reference, derived from the repository: the
    sealed checkpoint whose ledger names its commit validates from its own tag with the reference
    (the null control); without it the object is still in the repository's store and the checkpoint
    is refused as naming a local object, and a published clone of that repository does not carry
    the object and refuses it as absent.
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls._directory = tempfile.TemporaryDirectory(prefix="iacode-preserved-")
        cls.base = Path(cls._directory.name)
        cls.source = cls.base / "source"
        if not ledger_common.published_clone(PROJECT_ROOT, cls.source):
            raise unittest.SkipTest("the repository could not be cloned over Git's transport")
        cls.preserved = preserved_references(cls.source)
        # Derived once, from the branch, before any test checks out a sealed tag whose tree does
        # not contain the later checkpoints.
        cls.subjects = {reference: checkpoint_naming(cls.source, commit)
                        for reference, commit in cls.preserved.items()}

    @classmethod
    def tearDownClass(cls) -> None:
        cls._directory.cleanup()

    def validate(self, root: Path, checkpoint: str) -> tuple[int, str]:
        _git(root, "checkout", "--quiet", "--detach", f"refs/tags/iacode-checkpoints/{checkpoint}")
        completed = subprocess.run(
            [sys.executable, str(SCRIPTS / "validate_checkpoint.py"), "--root", str(root)],
            capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
        return completed.returncode, completed.stdout + completed.stderr

    def test_the_repository_publishes_a_preserved_reference(self) -> None:
        self.assertTrue(self.preserved, "no refs/tags/iacode-preserved/ reference is published")

    def test_every_preserved_reference_is_what_makes_its_checkpoint_valid(self) -> None:
        for number, (reference, commit) in enumerate(sorted(self.preserved.items())):
            with self.subTest(reference=reference):
                checkpoint = self.subjects[reference]
                self.assertIsNotNone(checkpoint, f"no sealed ledger names {commit[:12]}")
                code, output = self.validate(self.source, checkpoint)
                self.assertEqual(code, 0, f"null control: {output[-600:]}")

                _git(self.source, "update-ref", "-d", reference)
                try:
                    code, output = self.validate(self.source, checkpoint)
                    self.assertNotEqual(code, 0, output)
                    self.assertIn("exists here only as a local object", output)
                    clone = self.base / f"without-{number}"
                    self.assertTrue(ledger_common.published_clone(self.source, clone))
                    code, output = self.validate(clone, checkpoint)
                    self.assertNotEqual(code, 0, output)
                    self.assertIn("absent from this repository", output)
                finally:
                    _git(self.source, "update-ref", reference, commit)
                    _git(self.source, "checkout", "--quiet", "main")


class CloneMethodTests(unittest.TestCase):
    """`M1-F-003`: every control that clones this repository clones the published history.

    The rule is structural, so it is read from the syntax tree: a ``git clone`` argument list in the
    tooling or the suite either goes through ``ledger_common.published_clone`` or carries
    ``--no-local`` itself. ``--no-hardlinks`` and a bare local clone copy the object store and are
    what let the sealed-history check stay green over `M1-F-003`.
    """

    SEARCHED = ("scripts", "tests")

    #: The one named exception: the demonstration of the defect in `PublishedHistoryTests` spells
    #: the old method through this constant, and nothing else may.
    DEMONSTRATION = "LOCAL_OBJECT_STORE_COPY"

    @classmethod
    def offenders(cls, source: str) -> list[int]:
        lines = []
        for node in ast.walk(ast.parse(source)):
            if not isinstance(node, (ast.List, ast.Tuple)):
                continue
            constants = [item.value for item in node.elts
                         if isinstance(item, ast.Constant) and isinstance(item.value, str)]
            demonstration = any(
                isinstance(item, ast.Starred) and isinstance(item.value, ast.Name)
                and item.value.id == cls.DEMONSTRATION for item in node.elts)
            if ("git" in constants and "clone" in constants and "--no-local" not in constants
                    and not demonstration):
                lines.append(node.lineno)
        return lines

    def test_the_named_exception_is_used_once(self) -> None:
        uses = []
        for path in sorted((PROJECT_ROOT / "tests").rglob("*.py")):
            if "__pycache__" in path.parts:
                continue
            for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
                if isinstance(node, ast.Starred) and isinstance(node.value, ast.Name) \
                        and node.value.id == self.DEMONSTRATION:
                    uses.append(path.name)
        self.assertEqual(uses, ["test_gate3_sandbox.py"])

    def test_every_clone_in_the_tooling_and_the_suite_is_a_published_clone(self) -> None:
        found: list[str] = []
        scanned = 0
        for directory in self.SEARCHED:
            for path in sorted((PROJECT_ROOT / directory).rglob("*.py")):
                if "__pycache__" in path.parts:
                    continue
                scanned += 1
                for line in self.offenders(path.read_text(encoding="utf-8")):
                    found.append(f"{path.relative_to(PROJECT_ROOT).as_posix()}:{line}")
        self.assertGreater(scanned, 0, "the scan read nothing")
        self.assertEqual(found, [], "a clone that copies the local object store")

    def test_the_scan_detects_a_clone_of_the_local_object_store(self) -> None:
        """The null control over mutated sources."""
        self.assertEqual(self.offenders(
            'subprocess.run(["git", "clone", "--quiet", "--no-hardlinks", a, b])\n'), [1])
        self.assertEqual(self.offenders('run(["git", "clone", a, b])\n'), [1])
        self.assertEqual(self.offenders(
            'run(["git", "clone", "--quiet", "--no-local", a, b])\n'), [])

    def test_the_shared_helper_is_a_transport_clone(self) -> None:
        source = ast.unparse(ast.parse(Path(ledger_common.__file__).read_text(encoding="utf-8")))
        self.assertIn("'--no-local'", source)
        for module in ("m0_mirror_audit.py", "m0_red_team.py"):
            with self.subTest(module=module):
                text = (SCRIPTS / module).read_text(encoding="utf-8")
                self.assertIn("published_clone(", text)
                self.assertNotIn("--no-hardlinks", text)



# ---------------------------------------------------------------------------------------------
# 7. M1-F-002: a tool result is accepted only from the executor that owns the request
# ---------------------------------------------------------------------------------------------


ORIGIN_CONSTANTS = {"TOOL_EXECUTOR_EXTERNAL", "TOOL_EXECUTOR_SANDBOX", "EXTERNAL", "SANDBOX"}


def origin_arguments(source: str) -> list[tuple[int, str]]:
    """Every ``resolve_tool_request`` call and the expression its ``origin`` keyword is given."""
    found = []
    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, ast.Call):
            continue
        name = getattr(node.func, "attr", None) or getattr(node.func, "id", None)
        if name != "resolve_tool_request":
            continue
        keyword = next((item for item in node.keywords if item.arg == "origin"), None)
        found.append((node.lineno, ast.unparse(keyword.value) if keyword else "<missing>"))
    return found


class ToolResultOriginTests(unittest.TestCase):
    """The origin of a result is fixed by the code path that delivers it, never read from it.

    The store refuses a result whose origin is not the request's executor, so the control is only
    as good as the origin it is given. It is given by exactly two paths: the API's service method
    passes ``EXTERNAL`` and the workflow's internal activity passes ``SANDBOX``, each a constant.
    """

    SEARCHED = ("apps/api/src", "services/agent-runtime/src", "services/orchestrator",
                "scripts")

    def test_every_caller_declares_a_constant_origin(self) -> None:
        calls: list[str] = []
        offenders: list[str] = []
        for directory in self.SEARCHED:
            for path in sorted((PROJECT_ROOT / directory).rglob("*.py")):
                if "__pycache__" in path.parts:
                    continue
                for line, origin in origin_arguments(path.read_text(encoding="utf-8")):
                    where = f"{path.relative_to(PROJECT_ROOT).as_posix()}:{line}"
                    calls.append(where)
                    if origin not in ORIGIN_CONSTANTS:
                        offenders.append(f"{where} origin={origin}")
        self.assertGreaterEqual(len(calls), 3, f"the scan found too few callers: {calls}")
        self.assertEqual(offenders, [])

    def test_the_scan_detects_an_origin_taken_from_a_payload(self) -> None:
        """The null control over mutated sources."""
        self.assertEqual(origin_arguments(
            "store.resolve_tool_request(run, result, origin=TOOL_EXECUTOR_SANDBOX)\n"),
            [(1, "TOOL_EXECUTOR_SANDBOX")])
        for mutated in ("store.resolve_tool_request(run, result, origin=payload['origin'])\n",
                        "store.resolve_tool_request(run, result)\n",
                        "store.resolve_tool_request(run, result, origin=submission.executor)\n"):
            with self.subTest(source=mutated):
                (_, origin), = origin_arguments(mutated)
                self.assertNotIn(origin, ORIGIN_CONSTANTS)

    def test_the_api_path_is_external_and_the_activity_path_is_sandbox(self) -> None:
        service = (PROJECT_ROOT / "services/agent-runtime/src/iacode_agent_runtime/service.py")
        activities = (PROJECT_ROOT / "services/orchestrator/src/iacode_orchestrator/agent_runtime/"
                      "activities.py")
        self.assertEqual([origin for _, origin in origin_arguments(
            service.read_text(encoding="utf-8"))], ["TOOL_EXECUTOR_EXTERNAL"])
        self.assertEqual([origin for _, origin in origin_arguments(
            activities.read_text(encoding="utf-8"))], ["TOOL_EXECUTOR_SANDBOX"])

    def test_the_workflow_records_the_executor_from_the_stage_policy(self) -> None:
        workflow_source = (PROJECT_ROOT / "services/orchestrator/src/iacode_orchestrator/"
                           "workflows/agent_run.py").read_text(encoding="utf-8")
        create = next(node for node in ast.walk(ast.parse(workflow_source))
                      if isinstance(node, ast.AsyncFunctionDef)
                      and node.name == "create_tool_request")
        text = ast.unparse(create)
        self.assertIn("stage.sandbox_policy", text)
        self.assertIn("'executor': executor", text)
        self.assertIn("TOOL_EXECUTOR_SANDBOX", text)

    def test_a_submission_cannot_name_an_origin(self) -> None:
        contracts = (PROJECT_ROOT / "packages/contracts/src/iacode_contracts/agent_runtime.py"
                     ).read_text(encoding="utf-8")
        submission = next(node for node in ast.walk(ast.parse(contracts))
                          if isinstance(node, ast.ClassDef)
                          and node.name == "ToolResultSubmission")
        fields = {node.target.id for node in submission.body
                  if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name)}
        self.assertTrue(fields, "the submission declares no field")
        self.assertFalse(fields & {"origin", "executor"}, fields)
        self.assertIn("extra='forbid'", ast.unparse(submission))

    def test_the_executor_vocabulary_is_written_once(self) -> None:
        """The database constraint, the row and the runtime read one tuple (`LSN-0052`)."""
        for relative in ("packages/persistence/src/iacode_persistence/models.py",
                         "apps/api/migrations/versions/0005_tool_request_executor.py",
                         "services/agent-runtime/src/iacode_agent_runtime/contracts.py",
                         "services/agent-runtime/src/iacode_agent_runtime/persistence.py"):
            with self.subTest(module=relative):
                source = (PROJECT_ROOT / relative).read_text(encoding="utf-8")
                self.assertIn("TOOL_REQUEST_EXECUTORS", source)
                self.assertNotIn("('EXTERNAL', 'SANDBOX')", source)
                self.assertNotIn('("EXTERNAL", "SANDBOX")', source)

if __name__ == "__main__":
    unittest.main()
