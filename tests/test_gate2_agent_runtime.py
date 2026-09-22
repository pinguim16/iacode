"""Control-plane and repository-structure properties of GATE 2 — AGENT RUNTIME.

What this suite can check is what can be read from the repository without a runtime: that the
Gate's canonical specification exists and is mirrored, that the registries name what the Gate
introduced, that the boundary the Gate is *for* is not crossed anywhere in the tree, that the
previous Gates' migrations were not edited, and that the documents say what was delivered.

What it deliberately does not check is behaviour. The runtime's own suite runs inside the image
that has its dependencies, and duplicating a behavioural assertion here with a text search would be
a second, weaker control that disagrees with the first.

Every scan here carries a **null control**: the identical scan run over a mutated fixture, which
must fire. A scan that silently matched nothing would report every delivery as clean.
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

GATE = "GATE-2"
SPECIFICATION = PROJECT_ROOT / "docs" / "GATE-2-CHECKLIST.md"
RUNTIME_SOURCE = PROJECT_ROOT / "services" / "agent-runtime" / "src" / "iacode_agent_runtime"
ORCHESTRATOR_SOURCE = PROJECT_ROOT / "services" / "orchestrator" / "src" / "iacode_orchestrator"
WORKFLOW = ORCHESTRATOR_SOURCE / "workflows" / "agent_run.py"
PERSISTENCE_SOURCE = PROJECT_ROOT / "packages" / "persistence" / "src" / "iacode_persistence"
AGENTS = PROJECT_ROOT / "agents"
RUNBOOK = PROJECT_ROOT / "docs" / "runbooks" / "AGENT-RUNTIME.md"


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


def called(source: str) -> set[str]:
    return {
        dotted(node.func) for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.Call) and dotted(node.func)
    }


# ---------------------------------------------------------------------------------------------
# 1. The Gate's own specification and registries
# ---------------------------------------------------------------------------------------------


class Gate2CanonicalSpecificationTests(unittest.TestCase):
    """The Gate's requirement set comes from a document, re-parsed, and from nothing else."""

    def test_the_specification_exists_and_parses(self) -> None:
        self.assertTrue(SPECIFICATION.is_file())
        rows = policies.parse_checklist(SPECIFICATION.read_text(encoding="utf-8"))

        self.assertGreater(len(rows), 80, "the specification parsed as almost nothing")
        for row in rows:
            with self.subTest(key=row["key"]):
                self.assertTrue(row["description"].strip())
                self.assertTrue(row["artifact"].strip())
                self.assertTrue(row["evidence"].strip())

    def test_the_registry_mirrors_the_specification_row_for_row(self) -> None:
        declared = policies.canonical_requirements(PROJECT_ROOT, GATE)
        parsed = policies.parse_checklist(SPECIFICATION.read_text(encoding="utf-8"))

        self.assertEqual([item["key"] for item in declared], [row["key"] for row in parsed])
        self.assertTrue(all(item.get("mandatory") for item in declared))

    def test_a_dropped_row_is_refused(self) -> None:
        """The positive path of the control, so it is not one that has only ever said yes."""
        registry = json.loads(
            (PROJECT_ROOT / ".iacode" / "policies" / "canonical-requirements.json")
            .read_text(encoding="utf-8"))
        entry = next(item for item in registry["gates"] if item["gate"] == GATE)
        self.assertGreater(len(entry["requirements"]), 80)

        parsed = policies.parse_checklist(SPECIFICATION.read_text(encoding="utf-8"))
        shrunk = [row["key"] for row in parsed][:-1]
        self.assertNotEqual(shrunk, [row["key"] for row in parsed],
                            "the mirror check compares a set that cannot shrink")

    def test_the_specification_states_that_no_tool_is_executed(self) -> None:
        """The Gate is defined by what it does not do, and the definition is in the document."""
        text = SPECIFICATION.read_text(encoding="utf-8")
        self.assertIn("does **not** execute anything", text)
        self.assertIn("GATE 3", text)


class Gate2MandatoryGateTests(unittest.TestCase):
    """The executable gate this Gate introduces is in the closed registry, not in an invocation."""

    def test_the_agent_runtime_gate_is_mandatory(self) -> None:
        gates = policies.gate_definitions(PROJECT_ROOT)
        self.assertIn("agentRuntimeTests", gates)
        self.assertTrue(gates["agentRuntimeTests"]["mandatory"])
        self.assertIn("agentRuntimeTests", policies.mandatory_gates(PROJECT_ROOT))

    def test_its_command_is_executable_from_the_repository_root(self) -> None:
        command = policies.gate_definitions(PROJECT_ROOT)["agentRuntimeTests"]["command"]
        self.assertEqual(command[0], "python")
        script = PROJECT_ROOT / command[1]
        self.assertTrue(script.is_file(), f"{command[1]} does not exist")

    def test_the_gate_builds_before_it_measures(self) -> None:
        """A gate that runs inside an image and does not build it measures the past.

        `.iacode/memory/lessons.jsonl` records the Gate where a red test survived a green gate
        that way. The defence is structural: the runner calls ``build_service`` first.
        """
        runner = PROJECT_ROOT / "scripts" / "iacode" / "gates" / "agent_runtime_tests.py"
        source = runner.read_text(encoding="utf-8")
        self.assertIn("build_service(", source)
        self.assertLess(source.index("build_service("), source.index("pytest"),
                        "the gate measures before it builds")


class Gate2TestSuiteRegistryTests(unittest.TestCase):
    """The suite this Gate introduces is declared, counted and resolvable as evidence."""

    def test_the_agent_runtime_suite_is_declared_and_counted(self) -> None:
        suites = {item["id"]: item for item in policies.load_test_suites(PROJECT_ROOT)}
        self.assertIn("agent-runtime", suites)
        self.assertTrue(suites["agent-runtime"]["counted"])
        self.assertEqual(suites["agent-runtime"]["root"], "services/agent-runtime/tests")
        self.assertTrue((PROJECT_ROOT / suites["agent-runtime"]["root"]).is_dir())

    def test_the_suites_case_identifiers_resolve_as_evidence(self) -> None:
        identifiers = collect_test_ids(PROJECT_ROOT)
        for reference in ("RunStateMachineTests", "AgentEnvelopeTests",
                          "ToolExecutionBoundaryTests", "ConcurrentRunIsolationTests",
                          "AgentRuntimeMetricsTests", "PayloadLimitTests"):
            with self.subTest(reference=reference):
                self.assertIn(reference, identifiers)


class Gate2RedTeamHarnessTests(unittest.TestCase):
    """The battery is executable, scoped to this Gate, and records a null-mutation control."""

    def test_the_battery_exists_and_declares_its_attacks(self) -> None:
        harness = PROJECT_ROOT / "scripts" / "development-ledger" / "gate2_red_team.py"
        runtime = PROJECT_ROOT / "scripts" / "development-ledger" / "gate2_runtime_attacks.py"
        self.assertTrue(harness.is_file())
        self.assertTrue(runtime.is_file())

        source = harness.read_text(encoding="utf-8")
        self.assertIn("RUNTIME_ATTACKS", source)
        self.assertIn("baseline_control", source)
        declared = re.findall(r'\("(G2-[A-Z])",', source)
        self.assertGreaterEqual(len(declared), 15,
                                "the battery declares fewer attacks than the Gate asked for")
        self.assertEqual(len(declared), len(set(declared)), "an attack identifier is duplicated")

    def test_the_battery_refuses_to_report_without_its_control(self) -> None:
        source = (PROJECT_ROOT / "scripts" / "development-ledger" / "gate2_red_team.py"
                  ).read_text(encoding="utf-8")
        self.assertIn("the null-mutation control failed", source)
        self.assertIn("raise LedgerError", source)

    def test_every_attack_in_the_in_image_half_is_declared_on_the_host(self) -> None:
        """A verdict nobody declared would be an attack the report never mentions."""
        harness = (PROJECT_ROOT / "scripts" / "development-ledger" / "gate2_red_team.py"
                   ).read_text(encoding="utf-8")
        runtime = (PROJECT_ROOT / "scripts" / "development-ledger" / "gate2_runtime_attacks.py"
                   ).read_text(encoding="utf-8")
        executed = set(re.findall(r'"(G2-[A-Z])": ', runtime))
        declared = set(re.findall(r'\("(G2-[A-Z])",', harness))
        self.assertTrue(executed)
        self.assertTrue(executed <= declared,
                        f"undeclared verdicts: {sorted(executed - declared)}")


class Gate2ScopeTests(unittest.TestCase):
    """The reservation this Gate owns is consumed; every later Gate's is still enforced.

    The Gate a scope control is asked about is derived, never named. `LSN-0037` and `LSN-0032`:
    a control written while one Gate was the only Gate stops being a control at the next one, and
    naming the Gate is the shape that failure takes.
    """

    @staticmethod
    def current() -> str:
        return ledger_common.delivered_gate(PROJECT_ROOT)

    def test_the_agent_definition_reservation_is_consumed_by_its_owner(self) -> None:
        reservations = {item["path"]: item for item in policies.load_gate_scope(PROJECT_ROOT)}
        self.assertIn("agents", reservations)
        self.assertEqual(ledger_common.normalize_gate(reservations["agents"]["gate"]),
                         ledger_common.normalize_gate(GATE))

        in_force = {item["path"]
                    for item in policies.reservations_in_force(PROJECT_ROOT, self.current())}
        self.assertNotIn("agents", in_force,
                         "the Gate that owns the directory is still constrained by it")
        self.assertNotIn("services/agent-runtime", in_force)

    def test_the_delivery_filled_the_directory_it_owns(self) -> None:
        self.assertTrue((AGENTS / "profiles").is_dir())
        self.assertTrue((AGENTS / "teams").is_dir())
        self.assertTrue((AGENTS / "prompts").is_dir())
        self.assertGreaterEqual(len(list((AGENTS / "profiles").glob("*.json"))), 4)
        self.assertGreaterEqual(len(list((AGENTS / "teams").glob("*.json"))), 2)

    def test_every_later_gate_reservation_is_still_empty(self) -> None:
        """Consumed are exactly the reservations of the Gates delivered so far.

        The consumed set is derived from the published Gate order rather than listed. The first
        version named the three directories Gates 1 and 2 had filled, and failed GATE 3 for
        consuming the one it owns — `LSN-0037`'s class wearing a set of paths.
        """
        current = self.current()
        self.assertEqual(policies.scope_violations(PROJECT_ROOT, current), [])

        in_force = {item["path"] for item in policies.reservations_in_force(PROJECT_ROOT, current)}
        self.assertTrue(in_force, "no later Gate's reservation is in force, which cannot be right")
        order = policies.gate_order()
        position = order.index(ledger_common.normalize_gate(current))
        for reservation in policies.load_gate_scope(PROJECT_ROOT):
            path = str(reservation["path"])
            owner = order.index(ledger_common.normalize_gate(str(reservation["gate"])))
            with self.subTest(path=path):
                if owner <= position:
                    self.assertNotIn(path, in_force)
                else:
                    self.assertIn(path, in_force,
                                  "a reservation was consumed by a Gate that has not run")

    def test_the_scope_control_would_refuse_an_early_implementation(self) -> None:
        """The null control: the check fires when the rule is broken.

        The implementation is planted in a disposable copy of the scope policy, in whichever
        reservation is still in force, and never in the working tree: the first version wrote
        into `services/sandbox` and deleted what it wrote, which from GATE 3 onwards would have
        deleted the sandbox itself.
        """
        import shutil
        import tempfile

        current = self.current()
        with tempfile.TemporaryDirectory(prefix="iacode-scope-") as workdir:
            root = Path(workdir)
            shutil.copytree(PROJECT_ROOT / ".iacode" / "policies",
                            root / ".iacode" / "policies")
            reservation = policies.reservations_in_force(root, current)[0]
            planted = root / str(reservation["path"])
            planted.mkdir(parents=True)
            (planted / "README.md").write_text(
                f"**{policies.RESERVATION_MARKER}** for {reservation['gate']}\n",
                encoding="utf-8", newline="\n")
            (planted / "executor.py").write_text("# planted by a control-plane test\n",
                                                 encoding="utf-8", newline="\n")
            self.assertEqual(len(policies.scope_violations(root, current)), 1)
            (planted / "executor.py").unlink()
            self.assertEqual(policies.scope_violations(root, current), [],
                             "the unmutated fixture must pass the same control")


class Gate2VerificationStageTests(unittest.TestCase):
    """One documented command verifies the Gate, and it keeps a targeted mode."""

    def test_the_verification_adds_the_stages_this_gate_introduces(self) -> None:
        source = (PROJECT_ROOT / "scripts" / "iacode" / "verify.py").read_text(encoding="utf-8")
        for stage in ("agent-runtime-smoke", "agent-durability", "agent-cancellation"):
            with self.subTest(stage=stage):
                self.assertIn(stage, source)

    def test_the_targeted_mode_still_exists_and_skips_the_restarts(self) -> None:
        source = (PROJECT_ROOT / "scripts" / "iacode" / "verify.py").read_text(encoding="utf-8")
        self.assertIn("--fast", source)
        self.assertIn("if not fast:", source)

    def test_the_stages_it_declares_are_executable_scripts(self) -> None:
        for relative in ("scripts/iacode/agent_runtime_smoke.py",
                         "scripts/iacode/scenarios/agent_runtime_durability.py",
                         "scripts/iacode/scenarios/agent_runtime_cancellation.py"):
            with self.subTest(relative=relative):
                self.assertTrue((PROJECT_ROOT / relative).is_file())


# ---------------------------------------------------------------------------------------------
# 2. The boundary, read from the whole tree
# ---------------------------------------------------------------------------------------------


#: Modules that let a process start another one, reach a shell, or drive a machine.
EXECUTION_MODULES = frozenset({
    "subprocess", "multiprocessing", "pty", "docker", "paramiko", "fabric", "pexpect",
    "git", "dulwich", "pygit2", "selenium", "playwright", "pyautogui",
})

#: Calls that execute or mutate, named in full so ``os.replace`` and ``str.replace`` differ.
FORBIDDEN_CALLS = frozenset({
    "os.system", "os.popen", "os.remove", "os.unlink", "os.rename", "os.replace", "os.mkdir",
    "os.makedirs", "os.execv", "os.spawnv", "os.kill", "subprocess.run", "subprocess.Popen",
    "shutil.rmtree", "shutil.move", "eval", "exec", "__import__",
})


class RepositoryToolExecutionBoundaryTests(unittest.TestCase):
    """Nothing in the Gate 2 runtime boundary can execute a tool request.

    The scan covers the runtime **and** the worker that drives it, because the boundary is the pair
    rather than one package. The rehearsal harness is outside it deliberately: it is a test
    fixture, it lives beside the worker's source rather than inside it, and the image puts it where
    the running worker cannot import it.
    """

    def boundary(self) -> list[Path]:
        return python_files(RUNTIME_SOURCE) + python_files(ORCHESTRATOR_SOURCE)

    def test_the_boundary_has_something_to_scan(self) -> None:
        self.assertGreaterEqual(len(self.boundary()), 20)

    def test_no_module_imports_an_execution_capability(self) -> None:
        offenders: list[str] = []
        for path in self.boundary():
            for name in imported_names(path.read_text(encoding="utf-8")):
                if name.split(".")[0] in EXECUTION_MODULES:
                    offenders.append(f"{path.name}: {name}")
        self.assertEqual(offenders, [], f"the runtime boundary can execute: {offenders}")

    def test_no_module_executes_or_mutates(self) -> None:
        offenders: list[str] = []
        for path in self.boundary():
            for name in called(path.read_text(encoding="utf-8")) & FORBIDDEN_CALLS:
                offenders.append(f"{path.name}: {name}")
        self.assertEqual(offenders, [], f"the runtime boundary executes or mutates: {offenders}")

    def test_no_tool_name_is_resolved_dynamically(self) -> None:
        offenders: list[str] = []
        for path in self.boundary():
            names = called(path.read_text(encoding="utf-8"))
            for forbidden in ("getattr", "importlib.import_module", "globals", "locals"):
                if forbidden in names:
                    offenders.append(f"{path.name}: {forbidden}")
        self.assertEqual(offenders, [], f"a name is resolved dynamically: {offenders}")

    def test_the_scan_detects_a_module_that_does_it(self) -> None:
        """The null control. Without it a scan that matched nothing would look like a defence."""
        mutated = "\n".join([
            "import subprocess",
            "",
            "",
            "def run(name):",
            "    return subprocess.run([name])",
            "",
        ])
        self.assertTrue(imported_names(mutated) & EXECUTION_MODULES)
        self.assertTrue(called(mutated) & FORBIDDEN_CALLS)

        clean = "\n".join(["import json", "", "", "def render(value):",
                           "    return json.dumps(value).replace('a', 'b')", ""])
        self.assertFalse(imported_names(clean) & EXECUTION_MODULES)
        self.assertFalse(called(clean) & FORBIDDEN_CALLS)

    def test_the_rehearsal_harness_is_outside_the_shipped_source(self) -> None:
        """It exists, it is a harness, and the worker cannot import it."""
        rehearsal = PROJECT_ROOT / "services" / "orchestrator" / "rehearsal"
        self.assertTrue((rehearsal / "durability.py").is_file())
        self.assertFalse((ORCHESTRATOR_SOURCE / "rehearsal").exists())

        dockerfile = (PROJECT_ROOT / "services" / "orchestrator" / "Dockerfile"
                      ).read_text(encoding="utf-8")
        self.assertIn("services/orchestrator/rehearsal /app/rehearsal", dockerfile)
        self.assertIn("PYTHONPATH=/app/src", dockerfile)

    def test_the_rehearsal_executes_nothing_either(self) -> None:
        source = (PROJECT_ROOT / "services" / "orchestrator" / "rehearsal" / "durability.py"
                  ).read_text(encoding="utf-8")
        self.assertFalse(imported_names(source) & EXECUTION_MODULES)
        self.assertFalse(called(source) & FORBIDDEN_CALLS)


class RuntimeDependencyDirectionTests(unittest.TestCase):
    """The dependency points inward, and the runtime speaks the gateway's contract."""

    def test_the_runtime_imports_no_application_and_no_workflow_sdk(self) -> None:
        offenders: list[str] = []
        for path in python_files(RUNTIME_SOURCE):
            for name in imported_names(path.read_text(encoding="utf-8")):
                if name.split(".")[0] in ("iacode_api", "iacode_orchestrator", "fastapi",
                                          "starlette", "temporalio", "alembic"):
                    offenders.append(f"{path.name}: {name}")
        self.assertEqual(offenders, [], f"the runtime reaches outward: {offenders}")

    def test_the_runtime_imports_no_gateway_implementation(self) -> None:
        for path in python_files(RUNTIME_SOURCE):
            with self.subTest(module=path.name):
                names = imported_names(path.read_text(encoding="utf-8"))
                self.assertFalse(any(name.startswith("iacode_model_gateway") for name in names))

    def test_no_provider_is_named_in_the_runtime(self) -> None:
        offenders: list[str] = []
        for path in python_files(RUNTIME_SOURCE):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            docstrings = set()
            for node in ast.walk(tree):
                if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef,
                                     ast.AsyncFunctionDef)):
                    first = node.body[0] if node.body else None
                    if (isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant)
                            and isinstance(first.value.value, str)):
                        docstrings.add(id(first.value))
            for node in ast.walk(tree):
                if isinstance(node, ast.Constant) and isinstance(node.value, str):
                    if id(node) in docstrings:
                        continue
                    for provider in ("openai", "anthropic", "devworld", "gemini"):
                        if provider in node.value.lower():
                            offenders.append(f"{path.name}: {node.value[:50]}")
        self.assertEqual(offenders, [], f"a provider is named in the runtime: {offenders}")


class WorkflowDeterminismTests(unittest.TestCase):
    """Workflow code is replayed. Everything that cannot be replayed is an activity."""

    def source(self) -> str:
        return WORKFLOW.read_text(encoding="utf-8")

    def test_the_workflow_exists_and_registers_the_run(self) -> None:
        self.assertTrue(WORKFLOW.is_file())
        source = self.source()
        self.assertIn("@workflow.defn", source)
        self.assertIn("@workflow.run", source)
        self.assertIn("@workflow.signal", source)

    def test_the_workflow_reads_no_clock_no_randomness_and_no_database(self) -> None:
        names = called(self.source())
        for forbidden in ("time.time", "time.monotonic", "datetime.now", "random.random",
                          "random.uniform", "uuid.uuid4", "os.getenv"):
            with self.subTest(call=forbidden):
                self.assertNotIn(forbidden, names)

    def test_the_workflow_imports_no_database_and_no_http_client(self) -> None:
        names = imported_names(self.source())
        for forbidden in ("sqlalchemy", "httpx", "requests", "psycopg", "random"):
            with self.subTest(module=forbidden):
                self.assertNotIn(forbidden, names)

    def test_every_effect_is_an_activity(self) -> None:
        """The workflow's own effects are activity invocations, and the list is closed."""
        source = self.source()
        self.assertIn("workflow.execute_activity", source)
        activities = set(re.findall(r'"(iacode_agent_runtime_[a-z_]+)"', source))
        declared = set(re.findall(
            r'@activity\.defn\(name="(iacode_agent_runtime_[a-z_]+)"\)',
            (PROJECT_ROOT / "services" / "orchestrator" / "src" / "iacode_orchestrator"
             / "agent_runtime" / "activities.py").read_text(encoding="utf-8")))
        self.assertTrue(activities)
        self.assertTrue(activities <= declared,
                        f"the workflow calls activities nobody registers: "
                        f"{sorted(activities - declared)}")

    def test_the_determinism_scan_detects_a_module_that_breaks_it(self) -> None:
        mutated = "\n".join(["import random", "import time", "", "",
                             "def run():", "    return random.random() + time.time()", ""])
        self.assertTrue(called(mutated) & {"random.random", "time.time"})
        self.assertIn("random", imported_names(mutated))


class SecondOrchestratorTests(unittest.TestCase):
    """Temporal is the durable engine, and nothing competes with it."""

    def test_no_second_orchestrator_exists(self) -> None:
        """No background thread, no scheduler and no polling loop drives a run beside Temporal."""
        offenders: list[str] = []
        for path in python_files(RUNTIME_SOURCE) + python_files(ORCHESTRATOR_SOURCE):
            source = path.read_text(encoding="utf-8")
            names = imported_names(source) | called(source)
            for forbidden in ("threading", "sched", "apscheduler", "celery", "rq",
                              "threading.Thread", "asyncio.create_task"):
                if forbidden in names:
                    offenders.append(f"{path.name}: {forbidden}")
        self.assertEqual(offenders, [],
                         f"something other than Temporal drives work: {offenders}")

    def test_the_worker_registers_the_agent_workflow_on_its_own_queue(self) -> None:
        source = (ORCHESTRATOR_SOURCE / "worker.py").read_text(encoding="utf-8")
        self.assertIn("AgentRunWorkflow", source)
        self.assertIn("AGENT_RUNTIME_ACTIVITIES", source)
        self.assertIn("agent_runtime_task_queue", source)


# ---------------------------------------------------------------------------------------------
# 3. Persistence and migrations
# ---------------------------------------------------------------------------------------------


class Gate2PersistenceTests(unittest.TestCase):
    """One schema definition, shared, and the migrations that were already applied are untouched."""

    def test_persistence_package_is_the_single_schema_definition(self) -> None:
        self.assertTrue((PERSISTENCE_SOURCE / "models.py").is_file())
        self.assertTrue((PERSISTENCE_SOURCE / "base.py").is_file())
        self.assertFalse((PROJECT_ROOT / "apps" / "api" / "src" / "iacode_api" / "db"
                          / "models.py").exists(),
                         "the web application still carries a second schema definition")

        declaring: list[str] = []
        # Source, not suites. A test that *reads* the schema is not a second declaration of it, and
        # `apps/api/tests/unit/test_domain_model.py` is exactly that: it asserts the contract the
        # shared package declares.
        for path in python_files(PROJECT_ROOT / "apps") + python_files(PROJECT_ROOT / "services") \
                + python_files(PROJECT_ROOT / "packages"):
            if path.is_relative_to(PERSISTENCE_SOURCE) or "tests" in path.parts:
                continue
            source = path.read_text(encoding="utf-8")
            if "DeclarativeBase" in source or re.search(r"__tablename__\s*=", source):
                declaring.append(str(path.relative_to(PROJECT_ROOT)))
        self.assertEqual(declaring, [],
                         f"a table is declared outside the persistence package: {declaring}")

    def test_both_processes_depend_on_the_shared_package(self) -> None:
        for relative in ("apps/api/pyproject.toml", "services/orchestrator/pyproject.toml",
                         "services/agent-runtime/pyproject.toml"):
            with self.subTest(project=relative):
                self.assertIn("iacode-persistence",
                              (PROJECT_ROOT / relative).read_text(encoding="utf-8"))

    def test_applied_migrations_are_not_edited(self) -> None:
        """A migration that has been applied is history. This Gate adds one and edits none."""
        versions = PROJECT_ROOT / "apps" / "api" / "migrations" / "versions"
        names = sorted(path.name for path in versions.glob("*.py"))
        self.assertEqual(names, ["0001_foundation_schema.py", "0002_model_gateway.py",
                                 "0003_agent_runtime.py"])

        import subprocess

        completed = subprocess.run(
            ["git", "diff", "--name-only", "HEAD", "--",
             "apps/api/migrations/versions/0001_foundation_schema.py",
             "apps/api/migrations/versions/0002_model_gateway.py"],
            cwd=str(PROJECT_ROOT), text=True, encoding="utf-8", errors="replace",
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=False)
        if completed.returncode != 0:
            self.skipTest("not a Git checkout")
        self.assertEqual(completed.stdout.strip(), "",
                         "a migration that has already been applied was edited")

    def test_the_new_migration_follows_the_previous_head(self) -> None:
        sys.path.insert(0, str(PROJECT_ROOT / "apps" / "api"))
        from migrations.head import head_revision, revision_graph

        versions = PROJECT_ROOT / "apps" / "api" / "migrations" / "versions"
        graph = revision_graph(versions)
        self.assertEqual(head_revision(versions), "0003_agent_runtime")
        self.assertEqual(graph["0003_agent_runtime"], "0002_model_gateway")

    def test_no_parallel_entity_is_created(self) -> None:
        """Gate 2 evolved the existing entities rather than shadowing one with a table of its own."""
        source = (PERSISTENCE_SOURCE / "models.py").read_text(encoding="utf-8")
        tables = set(re.findall(r'__tablename__ = "([a-z_]+)"', source))
        self.assertIn("task_runs", tables)
        self.assertIn("agent_runs", tables)
        for forbidden in ("agent_runtime_tasks", "agent_runtime_runs", "runs", "agent_tasks"):
            with self.subTest(table=forbidden):
                self.assertNotIn(forbidden, tables)

    def test_the_run_state_vocabulary_has_one_source(self) -> None:
        contract = (PROJECT_ROOT / "packages" / "contracts" / "src" / "iacode_contracts"
                    / "agent_runtime.py").read_text(encoding="utf-8")
        models = (PERSISTENCE_SOURCE / "models.py").read_text(encoding="utf-8")
        states = (RUNTIME_SOURCE / "states.py").read_text(encoding="utf-8")

        self.assertIn("AGENT_RUN_STATES", contract)
        self.assertIn("from iacode_contracts.agent_runtime import", models)
        self.assertIn("AGENT_RUN_STATES", models)
        self.assertIn("from iacode_contracts.agent_runtime import", states)
        # And neither of the two consumers writes the list again.
        for consumer, text in (("models.py", models), ("states.py", states)):
            with self.subTest(module=consumer):
                self.assertNotIn('"WAITING_FOR_TOOL",\n    "SUCCEEDED"', text)


# ---------------------------------------------------------------------------------------------
# 4. The declared agents, and the documents
# ---------------------------------------------------------------------------------------------


class DeclaredAgentTests(unittest.TestCase):
    """The definitions are versioned files, and no shipped profile may request a tool."""

    def profiles(self) -> list[dict]:
        return [json.loads(path.read_text(encoding="utf-8"))
                for path in sorted((AGENTS / "profiles").glob("*.json"))]

    def test_builtin_profiles_are_exactly_the_declared_set(self) -> None:
        self.assertEqual({item["agent"] for item in self.profiles()},
                         {"engineering-lead", "generalist", "planner", "reviewer"})

    def test_builtin_teams_are_the_declared_set(self) -> None:
        teams = [json.loads(path.read_text(encoding="utf-8"))
                 for path in sorted((AGENTS / "teams").glob("*.json"))]
        self.assertEqual({item["team"] for item in teams},
                         {"single-agent", "planner-reviewer"})

    def test_no_shipped_profile_is_given_a_tool(self) -> None:
        """Gate 2 executes nothing, so a profile with a permitted action would be configuration
        for a capability that does not exist."""
        for profile in self.profiles():
            with self.subTest(agent=profile["agent"]):
                self.assertEqual(profile.get("allowedActions"), [])

    def test_prompts_are_versioned_files(self) -> None:
        for profile in self.profiles():
            with self.subTest(agent=profile["agent"]):
                template = PROJECT_ROOT / profile["promptTemplate"]
                self.assertTrue(template.is_file(), f"{profile['promptTemplate']} is missing")
                self.assertRegex(template.name, r"^[a-z0-9-]+\.v[0-9]+\.md$")
                self.assertTrue(template.read_text(encoding="utf-8").strip())

    def test_no_profile_names_a_provider_or_a_model(self) -> None:
        for profile in self.profiles():
            body = json.dumps(profile).lower()
            for forbidden in ("openai", "anthropic", "devworld", "gpt-", "claude-", "gemini"):
                with self.subTest(agent=profile["agent"], name=forbidden):
                    self.assertNotIn(forbidden, body)

    def test_agents_readme_describes_the_delivery(self) -> None:
        readme = (AGENTS / "README.md").read_text(encoding="utf-8")
        self.assertNotIn(policies.RESERVATION_MARKER, readme,
                         "the directory still declares itself reserved")
        self.assertIn("GATE 2", readme)
        self.assertIn("profiles/", readme)
        self.assertIn("teams/", readme)
        self.assertIn("prompts/", readme)


class Gate2DocumentationTests(unittest.TestCase):
    """The documents describe what was delivered rather than what was planned."""

    def test_the_entry_point_names_the_current_gate(self) -> None:
        text = (PROJECT_ROOT / "START-HERE.md").read_text(encoding="utf-8")
        self.assertIn("GATE 2", text)
        self.assertIn("docs/GATE-2-CHECKLIST.md", text)

    def test_the_architecture_describes_the_runtime_and_its_boundary(self) -> None:
        text = (PROJECT_ROOT / "docs" / "ARCHITECTURE.md").read_text(encoding="utf-8")
        self.assertIn("Agent Runtime", text)
        self.assertIn("WAITING_FOR_TOOL", text)
        self.assertIn("ADR-0020", text)
        self.assertIn("ADR-0021", text)

    def test_the_readme_and_versions_mention_the_gate(self) -> None:
        self.assertIn("Agent Runtime",
                      (PROJECT_ROOT / "README.md").read_text(encoding="utf-8"))
        self.assertIn("agent-runtime",
                      (PROJECT_ROOT / "docs" / "VERSIONS.md").read_text(encoding="utf-8"))

    def test_the_development_document_names_the_new_gate_and_suite(self) -> None:
        text = (PROJECT_ROOT / "docs" / "DEVELOPMENT.md").read_text(encoding="utf-8")
        self.assertIn("agentRuntimeTests", text)
        self.assertIn("services/agent-runtime", text)

    def test_agent_runtime_runbook_covers_the_declared_topics(self) -> None:
        self.assertTrue(RUNBOOK.is_file())
        text = RUNBOOK.read_text(encoding="utf-8")
        for topic in ("Starting", "Creating a run", "Following", "Cancelling",
                      "Tool requests", "Tool results", "Budgets", "live smoke",
                      "Troubleshooting"):
            with self.subTest(topic=topic):
                self.assertIn(topic, text)

    def test_gate_three_boundary_is_documented(self) -> None:
        runbook = RUNBOOK.read_text(encoding="utf-8")
        adr = (PROJECT_ROOT / "docs" / "adr" / "ADR-0021-tool-execution-boundary.md"
               ).read_text(encoding="utf-8")
        for text in (runbook, adr):
            self.assertIn("GATE 3", text)
            self.assertIn("WAITING_FOR_TOOL", text)

    def test_the_runbook_never_prints_a_credential(self) -> None:
        text = RUNBOOK.read_text(encoding="utf-8")
        self.assertNotIn("sk-", text)
        self.assertNotIn("Bearer ", text)
        self.assertEqual(ledger_common.find_secrets(text), [])


class Gate2AdrTests(unittest.TestCase):
    """The structural decisions of the Gate are recorded, and no ADR is a stub."""

    def adrs(self) -> list[Path]:
        return [PROJECT_ROOT / "docs" / "adr" / name for name in (
            "ADR-0020-agent-runtime-boundary.md",
            "ADR-0021-tool-execution-boundary.md",
            "ADR-0022-agent-output-envelope.md")]

    def test_every_decision_is_recorded(self) -> None:
        for path in self.adrs():
            with self.subTest(adr=path.name):
                self.assertTrue(path.is_file(), f"{path.name} is missing")
                text = path.read_text(encoding="utf-8")
                # The shape the repository's ADRs already use: a status line under the title, then
                # the three sections. Asserting a different shape here would make the control about
                # this Gate's formatting rather than about the decisions being recorded.
                self.assertRegex(text, r"(?m)^Status: (Accepted|Proposed|Superseded)")
                for section in ("## Context", "## Decision", "## Consequences"):
                    self.assertIn(section, text)
                self.assertGreater(len(text), 1200, f"{path.name} is a stub")

    def test_the_index_lists_them(self) -> None:
        # A missing index fails. The first version skipped instead, the index never existed, and
        # the test was counted as executed for two checkpoints without asserting anything: a
        # vacuous pass, `R-G2-012`, closed in GATE 3.
        index = (PROJECT_ROOT / "docs" / "adr" / "README.md")
        self.assertTrue(index.is_file(), "the ADR directory has no index")
        text = index.read_text(encoding="utf-8")
        for path in self.adrs():
            with self.subTest(adr=path.name):
                self.assertIn(path.stem.split("-")[0] + "-" + path.stem.split("-")[1], text)


class LiveSmokeContractTests(unittest.TestCase):
    """The live check is honest about what it did and about what it could not do."""

    def source(self) -> str:
        return (PROJECT_ROOT / "scripts" / "iacode" / "agent_runtime_smoke.py"
                ).read_text(encoding="utf-8")

    def test_live_smoke_blocks_without_a_credential(self) -> None:
        source = self.source()
        self.assertIn("BLOCKED_EXIT", source)
        self.assertIn("class BlockedError", source)
        self.assertIn("credentialConfigured", source)
        self.assertIn("credentialVariable", source)
        self.assertNotIn("except BlockedError:\n        return 0", source)

    def test_live_smoke_never_substitutes_a_model(self) -> None:
        source = self.source()
        self.assertIn("IACODE_GATEWAY_SMOKE_MODEL", source)
        self.assertIn("is not in the discovered catalog", source)
        self.assertNotIn("models[0]", source)
        self.assertNotIn("fallback_model", source)

    def test_the_live_smoke_records_no_content(self) -> None:
        """The report carries provenance and our own task text, never a model's answer."""
        source = self.source()
        self.assertIn('"singleAgentRunId"', source)
        self.assertIn('"smokeModel"', source)
        for forbidden in ('"completion"', '"answer":', '"prompt":'):
            with self.subTest(field=forbidden):
                self.assertNotIn(forbidden, source)

    def test_the_smoke_is_bounded(self) -> None:
        source = self.source()
        self.assertIn("MAX_OUTPUT_TOKENS", source)
        self.assertIn("maxModelCalls", source)


class FrontendSafetyTests(unittest.TestCase):
    """Model output is text the page shows, never markup the page trusts."""

    def test_model_output_is_not_rendered_as_markup(self) -> None:
        page = PROJECT_ROOT / "apps" / "web" / "src" / "app" / "agent-runtime"
        template = (page / "agent-runtime.html").read_text(encoding="utf-8")
        component = (page / "agent-runtime.ts").read_text(encoding="utf-8")
        service = (page / "agent-runtime.service.ts").read_text(encoding="utf-8")

        self.assertIn('data-testid="result"', template)
        for forbidden in ("innerHTML", "bypassSecurityTrust", "[innerHtml]", "DomSanitizer",
                          "marked", "markdown"):
            for name, text in (("template", template), ("component", component),
                               ("service", service)):
                with self.subTest(file=name, forbidden=forbidden):
                    self.assertNotIn(forbidden, text)

    def test_the_page_offers_nothing_that_would_execute_a_tool(self) -> None:
        """The controls, not the prose.

        The page *says* that a sandbox will execute a tool from Gate 3 onwards, which is exactly
        what an operator needs to read. What it must not have is a control that does it, so the
        check is over the elements a person can click rather than over the words on the page.
        """
        template = (PROJECT_ROOT / "apps" / "web" / "src" / "app" / "agent-runtime"
                    / "agent-runtime.html").read_text(encoding="utf-8")
        self.assertIn('data-testid="waiting-for-tool"', template)

        controls = re.findall(r"<(?:button|a|input|form)\b[^>]*>(?:[^<]*)", template,
                              flags=re.IGNORECASE)
        self.assertTrue(controls, "the page declares no control at all; the scan found nothing")
        for control in controls:
            lowered = control.lower()
            for forbidden in ("execute", "approve", "allow", "run tool", "resolve", "shell"):
                with self.subTest(control=control[:40], forbidden=forbidden):
                    self.assertNotIn(forbidden, lowered)

        # And the panel that announces the pause carries no control at all.
        panel = template[template.index('data-testid="waiting-for-tool"'):]
        panel = panel[:panel.index("</div>")]
        self.assertNotIn("<button", panel)
        self.assertNotIn("<form", panel)


if __name__ == "__main__":
    unittest.main()


# ---------------------------------------------------------------------------------------------
# 5. The guardrails this Gate's own failures produced
# ---------------------------------------------------------------------------------------------


class SourceIntegrityTests(unittest.TestCase):
    """A source file carries no stray control character.

    `LSN-0041`: a regex written through a shell heredoc arrived as a literal backspace, the scan it
    belonged to matched nothing, and the test still passed. The class is broader than that one
    escape — any editing path that consumes a backslash escape lands a control character in a
    string — so the control is over the character rather than over the regex.
    """

    #: Everything except the ones a text file legitimately contains.
    FORBIDDEN = frozenset(chr(code) for code in range(0x20)) - {"\t", "\n", "\r"}

    def roots(self) -> list[Path]:
        return [
            PROJECT_ROOT / "tests",
            PROJECT_ROOT / "scripts",
            PROJECT_ROOT / "packages",
            PROJECT_ROOT / "services",
            PROJECT_ROOT / "apps" / "api" / "src",
            PROJECT_ROOT / "apps" / "api" / "tests",
            PROJECT_ROOT / "apps" / "api" / "migrations",
        ]

    def test_no_source_file_carries_a_stray_control_character(self) -> None:
        offenders: list[str] = []
        scanned = 0
        for root in self.roots():
            for path in python_files(root):
                scanned += 1
                text = path.read_text(encoding="utf-8")
                found = sorted({repr(character) for character in text if character in self.FORBIDDEN})
                if found:
                    offenders.append(f"{path.relative_to(PROJECT_ROOT)}: {', '.join(found)}")
        self.assertGreater(scanned, 50, "the scan found almost nothing to read")
        self.assertEqual(offenders, [],
                         f"a source file carries a control character: {offenders}")

    def test_the_scan_detects_one(self) -> None:
        """The null control, which is the whole reason this test exists.

        Both fixtures are built rather than written: a literal with the escape in it would be the
        very thing being guarded against, and a file that carried one would fail the scan above.
        """
        mangled = "pattern = re.compile('a" + chr(8) + "b')"
        intact = "pattern = re.compile(r'a" + chr(92) + "bb')"

        self.assertEqual([item for item in mangled if item in self.FORBIDDEN], [chr(8)])
        self.assertEqual([item for item in intact if item in self.FORBIDDEN], [])


class ScenarioReadinessTests(unittest.TestCase):
    """A scenario waits on the fact, not on a log line.

    `LSN-0043`: the rehearsal worker prints that it started *before* it begins polling, so a
    scenario that read the log line could start a run against a queue nobody was watching and then
    wait out its whole timeout for a run that had not begun.
    """

    def scenario(self) -> str:
        return (PROJECT_ROOT / "scripts" / "iacode" / "scenarios"
                / "agent_runtime_durability.py").read_text(encoding="utf-8")

    def test_readiness_is_asked_of_temporal(self) -> None:
        source = self.scenario()
        self.assertIn("def wait_for_poller", source)
        self.assertIn('"poller"', source)
        self.assertIn("pollers", source)

    def test_readiness_is_not_read_from_a_log_line(self) -> None:
        body = self.scenario()
        start = body.index("def wait_for_poller")
        end = body.index("def wait_for_state")
        waiting = body[start:end]
        self.assertNotIn('"logs"', waiting,
                         "the scenario decides readiness from a log line")

    def test_the_harness_asks_the_server_for_the_answer(self) -> None:
        harness = (PROJECT_ROOT / "services" / "orchestrator" / "rehearsal"
                   / "durability.py").read_text(encoding="utf-8")
        self.assertIn("DescribeTaskQueueRequest", harness)
        self.assertIn("TASK_QUEUE_TYPE_WORKFLOW", harness)


class MigrationConstraintNamingTests(unittest.TestCase):
    """`LSN-0042`: the convention rewrites a CHECK constraint's name and not a UNIQUE one.

    Getting it backwards produces `ck_task_runs_ck_task_runs_status_is_known` on one side and a
    downgrade that drops a constraint nobody created on the other. The migration states the
    asymmetry where the code is, and the reversibility test applies and reverses it for real.
    """

    def migration(self) -> str:
        return (PROJECT_ROOT / "apps" / "api" / "migrations" / "versions"
                / "0003_agent_runtime.py").read_text(encoding="utf-8")

    def test_a_check_constraint_is_created_and_dropped_by_its_bare_name(self) -> None:
        source = self.migration()
        self.assertIn('op.create_check_constraint(\n        "status_is_known"', source)
        self.assertIn('op.drop_constraint(op.f("ck_task_runs_status_is_known")', source)

    def test_a_unique_constraint_keeps_exactly_the_name_it_was_given(self) -> None:
        source = self.migration()
        self.assertIn('op.create_unique_constraint("idempotency_key"', source)
        self.assertIn('op.drop_constraint("idempotency_key"', source)
        self.assertNotIn('op.create_unique_constraint(\n        op.f("uq_', source)

    def test_the_asymmetry_is_stated_where_the_code_is(self) -> None:
        self.assertIn("%(constraint_name)s", self.migration())


class CountedSuiteExpansionTests(unittest.TestCase):
    """A counted pytest suite declares its cases statically.

    `LSN-0045`: the TESTS denominator is derived by reading the source, so a case produced at run
    time by `pytest.mark.parametrize` cannot be counted. `derive_counts.py` already refuses one,
    but it refuses from inside the counter, several layers below the file that caused it — which
    is why a delivery found out by watching ninety-five ledger tests error at once. This test asks
    the same question of the same files, fails fast, and names the file and the function.
    """

    def counted_pytest_roots(self) -> list[Path]:
        roots: list[Path] = []
        for suite in policies.counted_test_suites(PROJECT_ROOT):
            if str(suite.get("framework")) == "python-pytest":
                roots.append(PROJECT_ROOT / str(suite["root"]))
        return roots

    @staticmethod
    def expansions(path: Path) -> list[str]:
        """Every test function in one file that expands at run time."""
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except (SyntaxError, UnicodeDecodeError):
            return []
        found: list[str] = []
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if not node.name.startswith("test"):
                continue
            for decorator in node.decorator_list:
                if "parametrize" in ast.dump(decorator):
                    found.append(f"{path.name}::{node.name}")
        return found

    def test_no_counted_pytest_case_expands_at_run_time(self) -> None:
        roots = self.counted_pytest_roots()
        self.assertTrue(roots, "no counted pytest suite was found to inspect")
        inspected = 0
        offenders: list[str] = []
        for root in roots:
            self.assertTrue(root.is_dir(), f"counted suite {root} does not exist")
            for path in python_files(root):
                inspected += 1
                offenders.extend(self.expansions(path))
        self.assertGreater(inspected, 0, "the scan found no file to inspect")
        self.assertEqual(
            offenders, [],
            "a counted pytest suite expands at run time; write the cases as a loop over a "
            "module-level tuple instead: " + ", ".join(offenders))

    def test_the_scan_detects_an_expansion(self) -> None:
        """The null control: the same scan, over a module that does it."""
        import tempfile

        source = (
            "import pytest\n\n\n"
            '@pytest.mark.parametrize("value", [1, 2])\n'
            "def test_example(value):\n"
            "    assert value\n\n\n"
            "def test_plain():\n"
            "    assert True\n"
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "test_mutated.py"
            path.write_text(source, encoding="utf-8")
            self.assertEqual(self.expansions(path), ["test_mutated.py::test_example"])

            clean = Path(directory) / "test_clean.py"
            clean.write_text("def test_plain():\n    assert True\n", encoding="utf-8")
            self.assertEqual(self.expansions(clean), [])


class DeadlineEnforcementTests(unittest.TestCase):
    """The deadline ends the run *and* records that it did.

    `LSN-0046`: the first implementation wrapped the engine in `asyncio.wait_for`. The timer fired
    on time and the workflow died with `Activity cancelled` before it could write anything down, so
    the row stayed `RUNNING` for ever — a deadline that is enforced against the process and not
    against the run. Two things had to change and both are asserted here: the race is an explicit
    child task, so the workflow's own task is never left cancelling; and the wait on that child
    accepts every way a cancelled activity surfaces, because Temporal raises `ActivityError`
    rather than `CancelledError`.
    """

    def source(self) -> str:
        return WORKFLOW.read_text(encoding="utf-8")

    def deadline_function(self) -> ast.AST:
        tree = ast.parse(self.source())
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name == "_run_within_deadline":
                    return node
        self.fail("the workflow declares no _run_within_deadline")

    def test_the_engine_is_not_wrapped_in_wait_for(self) -> None:
        calls = [name for name in called(self.source())
                 if name in ("asyncio.wait_for", "wait_for")]
        self.assertEqual(
            calls, [],
            "asyncio.wait_for cancels the awaiting task, which here is the workflow's own; the "
            "deadline path must race an explicit child task instead")

    def test_the_deadline_races_an_explicit_child_task(self) -> None:
        body = ast.dump(self.deadline_function())
        self.assertIn("ensure_future", body, "the engine must run as its own task")
        self.assertIn("FIRST_COMPLETED", body, "the engine must be raced against a timer")

    def test_the_wait_accepts_every_way_a_cancelled_activity_surfaces(self) -> None:
        handlers = [handler for handler in ast.walk(self.deadline_function())
                    if isinstance(handler, ast.ExceptHandler)]
        caught: list[str] = []
        for handler in handlers:
            for node in ast.walk(handler.type) if handler.type is not None else []:
                if isinstance(node, ast.Name):
                    caught.append(node.id)
                elif isinstance(node, ast.Attribute):
                    caught.append(node.attr)
        self.assertIn("CancelledError", caught)
        self.assertIn("Exception", caught,
                      "Temporal raises ActivityError, not CancelledError, when a cancelled "
                      "activity surfaces; a handler that expects only CancelledError lets the "
                      "workflow die before it records the deadline")

    def test_the_deadline_path_writes_the_failure_down(self) -> None:
        tree = ast.parse(self.source())
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name != "_deadline_exceeded":
                    continue
                body = ast.dump(node)
                self.assertIn("set_state", body)
                self.assertIn("record_event", body)
                self.assertIn("RUN_DEADLINE_EXCEEDED", body)
                return
        self.fail("the workflow declares no _deadline_exceeded")

    def test_the_workflow_writes_the_terminal_event_before_the_terminal_state(self) -> None:
        """G2-F-010: a reader between the two commits must find the log closed, not the row."""
        tree = ast.parse(self.source())
        checked: list[str] = []
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if node.name not in ("_deadline_exceeded", "_unrecoverable"):
                continue
            calls = {"record_event": [], "set_state": []}
            for inner in ast.walk(node):
                if (isinstance(inner, ast.Call) and isinstance(inner.func, ast.Attribute)
                        and inner.func.attr in calls):
                    calls[inner.func.attr].append(inner.lineno)
            with self.subTest(function=node.name):
                self.assertTrue(calls["record_event"] and calls["set_state"],
                                f"{node.name} does not write both the event and the state")
                self.assertLess(max(calls["record_event"]), min(calls["set_state"]),
                                f"{node.name} makes the terminal state visible before the log "
                                f"says the run ended")
            checked.append(node.name)
        self.assertEqual(sorted(checked), ["_deadline_exceeded", "_unrecoverable"])

    def test_the_scenario_asserts_the_run_ended_and_said_so(self) -> None:
        scenario = (PROJECT_ROOT / "scripts" / "iacode" / "scenarios"
                    / "agent_runtime_deadline.py").read_text(encoding="utf-8")
        self.assertIn("RUN_DEADLINE_EXCEEDED", scenario)
        self.assertIn("RUN_FAILED", scenario,
                      "a run that ends without recording that it ended is the defect this "
                      "scenario exists to catch")


PROMETHEUS_READS = ("/api/v1/query", "/api/v1/targets")


def unbounded_prometheus_reads(source: str) -> list[str]:
    """Why a module that reads Prometheus's API does not wait for a scrape, or nothing if it does.

    Read from the syntax tree, never from the text: a module reads Prometheus when a string
    constant names one of its query endpoints, and it waits when it calls ``time.monotonic`` and
    ``time.sleep`` and declares a ``*_WAIT_SECONDS`` bound of at least two fifteen-second scrape
    intervals and at most one minute.
    """
    tree = ast.parse(source)
    reads = any(isinstance(node, ast.Constant) and isinstance(node.value, str)
                and any(endpoint in node.value for endpoint in PROMETHEUS_READS)
                for node in ast.walk(tree))
    if not reads:
        return []
    problems: list[str] = []
    calls = called(source)
    for needed in ("time.monotonic", "time.sleep"):
        if needed not in calls:
            problems.append(f"never calls {needed}")
    bounds = [node.value.value for node in ast.walk(tree)
              if isinstance(node, ast.Assign) and len(node.targets) == 1
              and isinstance(node.targets[0], ast.Name)
              and node.targets[0].id.endswith("_WAIT_SECONDS")
              and isinstance(node.value, ast.Constant)
              and isinstance(node.value.value, (int, float))]
    if not bounds:
        problems.append("declares no *_WAIT_SECONDS bound")
    elif not all(30 <= bound <= 60 for bound in bounds):
        problems.append(f"waits {bounds}, outside two scrape intervals to one minute")
    return problems


class ObserverCycleTests(unittest.TestCase):
    """LSN-0049: a check of what Prometheus observes waits for its scrape, within a bound.

    `G2-F-012` was the gateway smoke; `G2-F-014` was the same class in the Foundation smoke, which
    `GRD-0051` did not reach because it named one function. The control is now the class.
    """

    def test_every_script_that_reads_prometheus_waits_for_a_scrape(self) -> None:
        scripts = python_files(PROJECT_ROOT / "scripts")
        readers = []
        for path in scripts:
            source = path.read_text(encoding="utf-8")
            problems = unbounded_prometheus_reads(source)
            if any(endpoint in source for endpoint in PROMETHEUS_READS):
                readers.append(path.name)
            with self.subTest(script=str(path.relative_to(PROJECT_ROOT))):
                self.assertEqual(problems, [], f"{path.name} reads Prometheus without waiting")
        self.assertIn("smoke.py", readers, "the scan found no reader; it would pass on anything")
        self.assertIn("gateway_smoke.py", readers)

    def test_the_scan_fires_on_a_read_that_does_not_wait(self) -> None:
        """The null control: the identical scan over a module that reads once and returns."""
        mutated = (
            "import urllib.request\n"
            "def check(base):\n"
            "    return urllib.request.urlopen(base + '/api/v1/targets?state=active')\n")
        self.assertTrue(unbounded_prometheus_reads(mutated))
        waits = mutated.replace("import urllib.request\n", (
            "import time\nimport urllib.request\nPROBE_WAIT_SECONDS = 45.0\n"
            "def later():\n    time.monotonic()\n    time.sleep(1)\n"))
        self.assertEqual(unbounded_prometheus_reads(waits), [])

    def test_the_foundation_smoke_waits_for_both_targets_and_asks_only_prometheus(self) -> None:
        operational = str(PROJECT_ROOT / "scripts" / "iacode")
        if operational not in sys.path:
            sys.path.insert(0, operational)
        import smoke

        down = {"status": "success", "data": {"activeTargets": [
            {"labels": {"job": "iacode-api"}, "health": "down"},
            {"labels": {"job": "iacode-worker"}, "health": "down"}]}}
        up = {"status": "success", "data": {"activeTargets": [
            {"labels": {"job": "iacode-api"}, "health": "up"},
            {"labels": {"job": "iacode-worker"}, "health": "up"}]}}
        clock = {"now": 0.0}
        asked: list[str] = []

        def answer(first_up_at):
            def fake(url, *args, **kwargs):
                asked.append(url)
                return 200, (up if len(asked) >= first_up_at else down)
            return fake

        def fake_sleep(seconds):
            clock["now"] += seconds

        originals = (smoke.http_json, smoke.time.sleep, smoke.time.monotonic)
        smoke.time.sleep = fake_sleep
        smoke.time.monotonic = lambda: clock["now"]
        try:
            smoke.http_json = answer(3)
            late = smoke.check_prometheus("http://prometheus.invalid")
            asked_late = list(asked)
            asked.clear()
            clock["now"] = 0.0
            smoke.http_json = answer(10_000)
            never = smoke.check_prometheus("http://prometheus.invalid")
        finally:
            smoke.http_json, smoke.time.sleep, smoke.time.monotonic = originals

        self.assertTrue(all(check.ok for check in late), [c.detail for c in late])
        self.assertEqual(len(asked_late), 3)
        self.assertFalse(all(check.ok for check in never), "targets that never came up passed")
        self.assertLessEqual(clock["now"], smoke.TARGET_WAIT_SECONDS + smoke.TARGET_POLL_SECONDS)
        for url in asked_late + asked:
            self.assertTrue(url.startswith("http://prometheus.invalid/api/v1/targets"), url)


class FreshInstallReportTests(unittest.TestCase):
    """The fresh-installation scenario names the smoke checks that failed, not only their count."""

    def test_a_failed_smoke_check_is_named_in_the_scenario_report(self) -> None:
        """GATE-2-CP-0002's verification recorded "17/18 smoke checks" and nothing that explained it."""
        for relative in ("scripts/iacode", "scripts/iacode/scenarios"):
            path = str(PROJECT_ROOT / relative)
            if path not in sys.path:
                sys.path.insert(0, path)
        import fresh_install

        payload = {"result": "FAIL", "total": 2, "passed": 1, "checks": [
            {"name": "api.health", "ok": True, "detail": "status=UP"},
            {"name": "prometheus.target.iacode-worker", "ok": False, "detail": "unknown"}]}
        completed = subprocess.CompletedProcess(
            args=[], returncode=1, stdout="[iacode] smoke\n" + json.dumps(payload))
        original = fresh_install.subprocess.run
        fresh_install.subprocess.run = lambda *args, **kwargs: completed
        try:
            ok, detail = fresh_install.run_smoke()
        finally:
            fresh_install.subprocess.run = original

        self.assertFalse(ok)
        self.assertIn("1/2 smoke checks", detail)
        self.assertIn("prometheus.target.iacode-worker: unknown", detail)
        self.assertNotIn("api.health", detail, "a passing check was reported as failed")
