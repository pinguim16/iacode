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
import record_command  # noqa: E402
import validate_checkpoint  # noqa: E402


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


if __name__ == "__main__":
    unittest.main()
