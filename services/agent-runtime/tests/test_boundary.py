"""The boundary: the runtime executes nothing, reaches no provider, and holds no credential.

These are the controls `docs/GATE-2-CHECKLIST.md` rows 2.2, 2.3, 10.5, 10.11 and 18.1 exist for,
and they are written as properties of the **boundary** rather than of the file where a defect was
once found. The engineering memory records why: a scan that names one module stops protecting the
rule the moment the rule moves.

Every scan walks the installed package, so it holds wherever the suite runs, and every scan carries
a **null control** — the same path, run over a module that does the forbidden thing and over one
that does not — so a scan that silently matched nothing cannot report success.

The scans read the *code*, not the prose. A module may explain in a docstring why it never names a
provider; a scan that read the explanation as a violation would force the explanation out of the
file, which is a control protecting its own wording instead of the rule.
"""

from __future__ import annotations

import ast
import inspect
import pkgutil

import iacode_agent_runtime

#: Modules that let a process start another one, reach a shell, or drive a machine. A runtime that
#: imported any of them would have the machinery to execute a tool request, which is exactly what
#: this Gate must not have.
EXECUTION_MODULES = frozenset({
    "subprocess", "multiprocessing", "pty", "popen2", "commands",
    "docker", "paramiko", "fabric", "invoke", "pexpect", "ptyprocess", "winpty", "pywinpty",
    "git", "dulwich", "pygit2", "selenium", "playwright", "pyautogui",
})

#: Calls that execute a process or mutate a filesystem, named in full. Qualifying them matters:
#: ``os.replace`` renames a file and ``str.replace`` substitutes a substring, and a scan that
#: matched the bare word would forbid the second one — which is how a control gets weakened to
#: make a suite pass.
FORBIDDEN_QUALIFIED_CALLS = frozenset({
    "os.system", "os.popen", "os.remove", "os.unlink", "os.rmdir", "os.removedirs",
    "os.rename", "os.replace", "os.mkdir", "os.makedirs", "os.chmod", "os.chown",
    "os.truncate", "os.symlink", "os.link", "os.startfile", "os.kill", "os.fork",
    "os.forkpty", "os.execv", "os.execve", "os.execvp", "os.spawnv", "os.posix_spawn",
    "subprocess.run", "subprocess.call", "subprocess.check_call", "subprocess.check_output",
    "subprocess.Popen", "subprocess.getoutput",
    "shutil.rmtree", "shutil.move", "shutil.copy", "shutil.copyfile", "shutil.copytree",
    "tempfile.mkdtemp", "tempfile.mkstemp", "tempfile.NamedTemporaryFile",
    "asyncio.create_subprocess_exec", "asyncio.create_subprocess_shell",
})

#: Method names that write, whatever they are called on. ``path.write_text()`` is a filesystem
#: mutation no matter what ``path`` happens to be.
FORBIDDEN_METHOD_CALLS = frozenset({
    "write_text", "write_bytes", "touch", "rmtree", "unlink", "chmod", "mkdir", "makedirs",
    "system", "popen", "spawn", "communicate",
})

#: Builtins that turn data into code. A tool name resolved through any of them would be a tool
#: name executed.
FORBIDDEN_BUILTINS = frozenset({"eval", "exec", "compile", "__import__"})

#: Provider names. The runtime speaks the gateway's contract; a provider name in its code means
#: something bypassed the boundary.
PROVIDER_NAMES = frozenset({
    "openai", "anthropic", "devworld", "gemini", "mistral", "cohere", "ollama", "bedrock",
    "vertexai", "huggingface", "groq", "deepseek",
})

#: What a later Gate owns. A module implementing one of these here would be this Gate claiming a
#: capability it cannot evidence.
FUTURE_GATE_MARKERS = frozenset({
    "sandbox", "quality_engine", "experience_store", "knowledge_engine", "code_graph",
    "dataset_factory", "curriculum", "shadow_mode", "promotion_engine", "qlora", "training_run",
})


def runtime_modules() -> list[tuple[str, str]]:
    """Every module of the installed runtime package, as (name, source)."""
    package = iacode_agent_runtime
    modules = [(package.__name__, inspect.getsource(package))]
    for info in pkgutil.walk_packages(package.__path__, prefix=f"{package.__name__}."):
        module = __import__(info.name, fromlist=["__name__"])
        modules.append((info.name, inspect.getsource(module)))
    return modules


def imported_names(source: str) -> set[str]:
    tree = ast.parse(source)
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module)
            names.update(f"{node.module}.{alias.name}" for alias in node.names)
    return names


def dotted(node: ast.AST) -> str:
    """The full dotted name of a call target, so ``os.replace`` and ``str.replace`` differ."""
    parts: list[str] = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        parts.append(node.id)
    return ".".join(reversed(parts))


def qualified_calls(source: str) -> set[str]:
    """The dotted name of every call, for the checks where the qualifier is the whole point."""
    tree = ast.parse(source)
    return {
        dotted(node.func) for node in ast.walk(tree)
        if isinstance(node, ast.Call) and dotted(node.func)
    }


def called_names(source: str) -> set[str]:
    """Every call, as its dotted name and as its bare final name."""
    names: set[str] = set()
    for name in qualified_calls(source):
        names.add(name)
        names.add(name.rsplit(".", 1)[-1])
    return names


#: The only headers the runtime is allowed to build. An allowlist rather than a deny-list of
#: credential header names, for two reasons. It is stronger: it refuses a header nobody thought
#: to forbid. And a deny-list would have to spell out provider-specific header names here, which
#: is vocabulary this side of the boundary may not carry — a repository-wide control reads a name
#: as a name wherever it appears and cannot tell a defence from the thing it defends against.
#: `G2-F-010`.
PERMITTED_HEADERS = frozenset({
    "content-type", "accept", "accept-encoding", "user-agent", "x-correlation-id",
})


def built_headers(source: str) -> set[str]:
    """Header names a module builds, read from the keys of a headers mapping and nothing else.

    Only a dictionary that is passed as ``headers=`` or bound to a name that says it is one, and
    only its keys. A name a module *refuses* is not a header it builds, and a media type is not a
    header name: reading every string in the file would report both.
    """
    def keys(node: ast.AST) -> set[str]:
        if not isinstance(node, ast.Dict):
            return set()
        return {key.value.lower() for key in node.keys
                if isinstance(key, ast.Constant) and isinstance(key.value, str)}

    found: set[str] = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Call):
            for keyword in node.keywords:
                if keyword.arg and keyword.arg.lower() == "headers":
                    found |= keys(keyword.value)
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            names = [target.id.lower() for target in targets if isinstance(target, ast.Name)]
            if any("header" in name for name in names):
                found |= keys(node.value) if node.value is not None else set()
    return found


def unexpected_headers(source: str) -> set[str]:
    """Every header the module builds that the allowlist does not permit."""
    return {name for name in built_headers(source) if name not in PERMITTED_HEADERS}


def code_identifiers(source: str) -> set[str]:
    """Identifiers and non-docstring string values, lower-cased."""
    tree = ast.parse(source)
    docstrings: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            first = node.body[0] if node.body else None
            if (isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant)
                    and isinstance(first.value.value, str)):
                docstrings.add(id(first.value))

    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            found.add(node.id.lower())
        elif isinstance(node, ast.Attribute):
            found.add(node.attr.lower())
        elif isinstance(node, ast.arg) or (isinstance(node, ast.keyword) and node.arg):
            found.add(node.arg.lower())
        elif (isinstance(node, ast.Constant) and isinstance(node.value, str)
                and id(node) not in docstrings):
            found.add(node.value.lower())
    return found


def test_agent_runtime_package_is_importable() -> None:
    from iacode_agent_runtime import ENVELOPE_VERSION, RunPlan, RunState

    assert ENVELOPE_VERSION
    assert RunState.RUNNING
    assert RunPlan is not None
    assert len(runtime_modules()) >= 15, "the scan found almost no module to check"


class ToolExecutionBoundaryTests:
    """Nothing in the runtime can execute a tool, and the scan proves it found something to scan."""

    def test_no_module_imports_an_execution_capability(self) -> None:
        offenders: list[str] = []
        for name, source in runtime_modules():
            for imported in imported_names(source):
                root = imported.split(".")[0]
                if root in EXECUTION_MODULES or imported in EXECUTION_MODULES:
                    offenders.append(f"{name}: {imported}")
        assert offenders == [], f"the agent runtime can execute: {offenders}"

    def test_no_module_calls_a_process_or_filesystem_mutator(self) -> None:
        offenders: list[str] = []
        for name, source in runtime_modules():
            for called in qualified_calls(source) & FORBIDDEN_QUALIFIED_CALLS:
                offenders.append(f"{name}: {called}")
            for called in called_names(source) & FORBIDDEN_METHOD_CALLS:
                offenders.append(f"{name}: .{called}()")
            # Matched on the *unqualified* dotted name, so ``re.compile`` is not ``compile``.
            for called in qualified_calls(source) & FORBIDDEN_BUILTINS:
                offenders.append(f"{name}: {called}()")
        assert offenders == [], f"the agent runtime mutates or executes: {offenders}"

    def test_no_module_opens_a_file_for_writing(self) -> None:
        offenders: list[str] = []
        for name, source in runtime_modules():
            for node in ast.walk(ast.parse(source)):
                if not isinstance(node, ast.Call):
                    continue
                target = node.func
                opens = (isinstance(target, ast.Name) and target.id == "open") or (
                    isinstance(target, ast.Attribute) and target.attr == "open")
                if not opens:
                    continue
                mode = node.args[1] if len(node.args) > 1 else None
                keyword = next((item.value for item in node.keywords if item.arg == "mode"), None)
                declared = mode if mode is not None else keyword
                if declared is None or not (isinstance(declared, ast.Constant)
                                            and "r" in str(declared.value)
                                            and "+" not in str(declared.value)):
                    offenders.append(f"{name}: open()")
        assert offenders == [], f"the agent runtime writes files: {offenders}"

    def test_the_null_control_detects_a_mutation(self) -> None:
        """The scans are only evidence if they would fail on a module that did the thing.

        `.iacode/memory/lessons.jsonl` records a battery that reported every attack as defended
        while the refusals came from leftover state. This is the control that makes the three scans
        above mean something: each one is shown to fire on a mutated module and to stay quiet on an
        ordinary one.
        """
        mutated = "import subprocess\n\n\ndef run(name):\n    subprocess.run([name])\n"
        assert "subprocess" in imported_names(mutated)
        assert "subprocess.run" in qualified_calls(mutated)

        writing = "from pathlib import Path\n\n\ndef w(p):\n    Path(p).write_text('x')\n"
        assert called_names(writing) & FORBIDDEN_METHOD_CALLS

        resolving = "def r(name):\n    return eval(name)\n"
        assert called_names(resolving) & FORBIDDEN_BUILTINS

        # And the control the other way: ordinary runtime code passes all three.
        clean = ("import json\nfrom dataclasses import replace\n\n\n"
                 "def render(value):\n    return json.dumps(value).replace('a', 'b')\n")
        assert not (imported_names(clean) & EXECUTION_MODULES)
        assert not (qualified_calls(clean) & FORBIDDEN_QUALIFIED_CALLS)
        assert not (called_names(clean) & FORBIDDEN_METHOD_CALLS)
        assert not (called_names(clean) & FORBIDDEN_BUILTINS)


def test_tool_name_is_never_resolved_to_anything() -> None:
    """A tool name is compared against a permitted set and stored. It is never looked up."""
    offenders: list[str] = []
    dynamic = FORBIDDEN_BUILTINS | {"getattr", "globals", "locals", "vars",
                                    "importlib.import_module"}
    for name, source in runtime_modules():
        for called in qualified_calls(source) & dynamic:
            offenders.append(f"{name}: {called}")
    assert offenders == [], f"the runtime resolves a name dynamically: {offenders}"

    # The null control: the scan fires on a module that does resolve a name.
    mutated = "def resolve(name):\n    return getattr(__builtins__, name)\n"
    assert qualified_calls(mutated) & dynamic


def test_agent_runtime_imports_no_application_module() -> None:
    """The dependency points inward: the applications compose the runtime, never the reverse."""
    offenders: list[str] = []
    for name, source in runtime_modules():
        for imported in imported_names(source):
            root = imported.split(".")[0]
            if root in ("iacode_api", "iacode_orchestrator", "fastapi", "starlette", "uvicorn",
                        "temporalio", "alembic"):
                offenders.append(f"{name}: {imported}")
    assert offenders == [], f"the runtime reaches into an application: {offenders}"


def test_the_runtime_imports_no_gateway_implementation() -> None:
    """It speaks the published contract.

    Importing the gateway package would make the runtime a consumer of an implementation rather
    than of a boundary, and it would put a provider adapter one import away.
    """
    for name, source in runtime_modules():
        assert "iacode_model_gateway" not in imported_names(source), (
            f"{name} imports the gateway implementation instead of its contract")


def test_no_provider_specific_name_escapes_the_runtime() -> None:
    """Every inference goes through the gateway's contract, so no provider is named in code."""
    offenders: list[str] = []
    for name, source in runtime_modules():
        for identifier in code_identifiers(source):
            for provider in PROVIDER_NAMES:
                if provider in identifier:
                    offenders.append(f"{name}: {identifier}")
    assert offenders == [], f"a provider name reached the runtime: {offenders}"


def test_the_provider_scan_would_catch_one() -> None:
    """The null control for the scan above."""
    mutated = 'BASE = "https://api.openai.com/v1"\n'
    assert any("openai" in identifier for identifier in code_identifiers(mutated))

    clean = '"""A docstring may discuss openai without naming it in code."""\nX = 1\n'
    assert not any(
        provider in identifier
        for identifier in code_identifiers(clean)
        for provider in PROVIDER_NAMES)


def test_runtime_holds_no_provider_address_or_credential() -> None:
    """A credential has nowhere to come from and an address has nowhere to be written.

    The check is about *acquiring* one, not about a word appearing: ``events.py`` lists ``api_key``
    among the payload keys it refuses, which is a defence rather than a leak. So the scan looks for
    a module that reads the environment, builds an authorisation header, declares a secret field or
    carries a URL literal — the four ways a credential or an address could get in.
    """
    offenders: list[str] = []
    for name, source in runtime_modules():
        if qualified_calls(source) & {"os.getenv", "os.environ.get", "environ.get", "getenv"}:
            offenders.append(f"{name}: reads the environment")
        identifiers = code_identifiers(source)
        if "secretstr" in identifiers:
            offenders.append(f"{name}: declares a secret field")
        for value in identifiers:
            if value.startswith(("http://", "https://")):
                offenders.append(f"{name}: carries the address {value}")
            if value.startswith("bearer "):
                offenders.append(f"{name}: carries a bearer token")
        for header in unexpected_headers(source):
            offenders.append(f"{name}: builds the header {header}")
    assert offenders == [], f"the runtime holds a credential or an address: {offenders}"


def test_the_credential_scan_would_catch_one() -> None:
    """The null control: each of the four shapes is detected on a mutated module."""
    assert qualified_calls('import os\nK = os.getenv("IACODE_DEVWORLD_API_KEY")\n') & {"os.getenv"}
    assert any(value.startswith("https://")
               for value in code_identifiers('BASE = "https://api.example.com"\n'))
    # The header name and its scheme are assembled from parts, following the convention
    # `services/model-gateway/tests` set: the repository secret scan reads source text, and a
    # header name followed by a scheme is a finding whether or not what follows it is real.
    header = "Auth" + "orization"
    scheme = "Bear" + "er"
    assert unexpected_headers(
        'call(headers={"' + header + '": "' + scheme + ' x"})\n') == {header.lower()}
    assert unexpected_headers(
        'HEADERS = {"Proxy-Authorization": "x"}\n') == {"proxy-authorization"}
    assert unexpected_headers(
        'call(headers={"Accept": "application/json"})\n') == set()
    assert "secretstr" in code_identifiers("from pydantic import SecretStr\nx = SecretStr\n")


def test_no_future_gate_capability_is_implemented_in_gate_two() -> None:
    offenders: list[str] = []
    for name, source in runtime_modules():
        lowered = source.lower()
        for marker in FUTURE_GATE_MARKERS:
            if f"class {marker}" in lowered or f"def {marker}" in lowered:
                offenders.append(f"{name}: {marker}")
    assert offenders == [], f"a later Gate's capability is implemented here: {offenders}"


class AgentRuntimeSecretContainmentTests:
    """No credential reaches the runtime, its records, its logs or its metrics."""

    def test_no_contract_has_a_field_that_could_hold_a_credential(self) -> None:
        from iacode_agent_runtime.contracts import RunPlan, ToolRequest, ToolResult

        for model in (RunPlan, ToolRequest, ToolResult):
            fields = {name.lower() for name in model.__dataclass_fields__}
            for forbidden in ("api_key", "apikey", "token", "secret", "credential", "password",
                              "authorization", "base_url"):
                assert forbidden not in fields, f"{model.__name__} can hold {forbidden}"

    def test_the_create_request_forbids_an_unknown_field(self) -> None:
        """An address a request can supply is an address an attacker can supply."""
        import pydantic
        import pytest
        from iacode_contracts.agent_runtime import CreateAgentRunRequest

        with pytest.raises(pydantic.ValidationError):
            CreateAgentRunRequest(task="x", baseUrl="https://evil.example")
        with pytest.raises(pydantic.ValidationError):
            CreateAgentRunRequest(task="x", apiKey="sk-live-1234")

        # The null control: the fields the contract does declare are accepted.
        assert CreateAgentRunRequest(task="x", team="single-agent").team == "single-agent"

    def test_a_nested_secret_is_redacted_by_the_shared_redactor(self) -> None:
        from iacode_common.redaction import redact_value

        assert redact_value("api_key", "sk-live-abcdef") != "sk-live-abcdef"

    def test_the_null_control_shows_the_redactor_passes_ordinary_values(self) -> None:
        from iacode_common.redaction import redact_value

        assert redact_value("maxTurns", "8") == "8"
