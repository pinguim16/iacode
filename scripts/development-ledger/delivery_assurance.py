#!/usr/bin/env python3
"""Shared delivery-assurance logic for the requirements matrix and the completeness audit.

The Delivery Completeness Validator must not accept "the implementer says it is done". Every
requirement that claims completion has to point at evidence that this module can resolve:

- ``file:<repository-relative path>``      an existing, non-empty file in the repository
- ``checkpoint:<name>``                    an existing, non-empty file inside the checkpoint
- ``command:<id>``                         a successful record in the checkpoint's COMMANDS.jsonl
- ``test:<TestClass.test_name>``           a test case that actually exists in the suite

The same function is used by ``check_completeness.py`` to produce the report and by
``validate_checkpoint.py`` to recompute it, so a stored report cannot disagree with the matrix.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Any

from ledger_common import LedgerError, load_json
from policies import (
    compare_requirement_sets,
    counted_test_suites,
    declared_requirement_refs,
    expected_requirement_refs,
    source_ref,
)

EVIDENCE_KINDS = ("file", "checkpoint", "command", "test")

def completeness_scope(root: Path, checkpoint: Path) -> list[str]:
    """Extra paths the completeness fingerprint covers beyond the assurance scope.

    The requirements matrix and the lesson preflight live inside the checkpoint, so they are not in
    the assurance scope, yet changing either of them invalidates a completeness audit. A checkpoint
    outside the repository, which only a test fixture ever is, contributes no extra path.
    """
    names = ("REQUIREMENTS-MATRIX.json", "LESSON-PREFLIGHT.json")
    resolved: list[str] = []
    for name in names:
        try:
            resolved.append(str((checkpoint / name).relative_to(root)).replace("\\", "/"))
        except ValueError:
            continue
    return resolved


EXPECTED_SET_DESCRIPTION = (
    "derived by policies.expected_requirement_refs from the canonical Gate specification, the "
    "lesson preflight and the open independent audit findings and attacks"
)


def load_command_results(checkpoint: Path) -> dict[str, dict[str, Any]]:
    """Map command id to record for the checkpoint ledger, ignoring unparsable lines."""
    results: dict[str, dict[str, Any]] = {}
    commands_path = checkpoint / "COMMANDS.jsonl"
    if not commands_path.is_file():
        return results
    for line in commands_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        identifier = record.get("id")
        if isinstance(identifier, str) and identifier:
            results[identifier] = record
    return results


def command_succeeded(record: dict[str, Any]) -> bool:
    if record.get("result") not in (None, "COMPLETED"):
        return False
    exit_code = record.get("exitCode")
    return exit_code == 0


_TEST_ID_CACHE: dict[str, set[str]] = {}


def collect_test_ids(root: Path) -> set[str]:
    """Every test case id in the suite, as ``TestClass.test_name`` and as the bare method name.

    The suite is read with ``ast`` rather than imported. Importing it would execute it, would make
    the answer depend on the interpreter's module cache, and fails outright when a checkout is
    inspected from another checkout -- which is exactly the situation of a validator resolving the
    references of a repository it is auditing. Inheritance inside a test module is resolved, so a
    subclass carries the cases it inherits.

    Every Python suite the canonical registry declares as counted is read, not only ``tests/``. A
    Gate that adds a suite and leaves it out of this function would make its own test references
    unresolvable, and the honest reference would have to be downgraded to a command.
    """
    cache_key = str(root.resolve())
    if cache_key in _TEST_ID_CACHE:
        return _TEST_ID_CACHE[cache_key]
    identifiers: set[str] = set()
    directories = [
        root / str(suite["root"]) for suite in counted_test_suites(root)
        if str(suite.get("framework", "")).startswith("python-")
    ]
    if not any(directory.is_dir() for directory in directories):
        _TEST_ID_CACHE[cache_key] = identifiers
        return identifiers

    files = sorted(
        {path for directory in directories if directory.is_dir()
         for path in directory.rglob("*.py")}
    )
    for path in files:
        if "__pycache__" in path.parts:
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except (OSError, SyntaxError):
            continue
        own: dict[str, set[str]] = {}
        bases: dict[str, list[str]] = {}
        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue
            own[node.name] = {
                item.name for item in node.body
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
                and item.name.startswith("test")
            }
            bases[node.name] = [
                base.id for base in node.bases if isinstance(base, ast.Name)
            ] + [
                base.attr for base in node.bases if isinstance(base, ast.Attribute)
            ]

        def resolve(name: str, seen: set[str]) -> set[str]:
            if name in seen:
                return set()
            seen.add(name)
            methods = set(own.get(name, set()))
            for base in bases.get(name, []):
                methods |= resolve(base, seen)
            return methods

        for name in own:
            methods = resolve(name, set())
            if methods:
                # A class name is a usable reference: it names a group of cases that must exist.
                identifiers.add(name)
            for method in methods:
                identifiers.add(f"{name}.{method}")
                identifiers.add(method)

        # A pytest suite writes its cases as module-level functions, which no class owns. They are
        # real cases and a reference to one has to resolve, so the module is a usable qualifier in
        # the same way a class is.
        for node in tree.body:
            if (isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                    and node.name.startswith("test")):
                identifiers.add(node.name)
                identifiers.add(f"{path.stem}.{node.name}")

    _TEST_ID_CACHE[cache_key] = identifiers
    return identifiers


def resolve_evidence(
    root: Path,
    checkpoint: Path,
    reference: Any,
    command_results: dict[str, dict[str, Any]],
    test_ids: set[str],
) -> str | None:
    """Return an error string when the reference cannot be resolved, otherwise None."""
    if not isinstance(reference, str) or ":" not in reference:
        return f"malformed evidence reference {reference!r}"
    kind, _, value = reference.partition(":")
    if kind not in EVIDENCE_KINDS:
        return f"unsupported evidence kind {kind!r}"
    if not value:
        return f"empty evidence target in {reference!r}"

    if kind in ("file", "checkpoint"):
        base = root if kind == "file" else checkpoint
        candidate = (base / value).resolve()
        if base.resolve() != candidate and base.resolve() not in candidate.parents:
            return f"evidence path escapes its root: {reference}"
        if not candidate.is_file():
            return f"evidence file does not exist: {reference}"
        try:
            if not candidate.read_text(encoding="utf-8").strip():
                return f"evidence file is empty: {reference}"
        except UnicodeDecodeError:
            if candidate.stat().st_size == 0:
                return f"evidence file is empty: {reference}"
        return None

    if kind == "command":
        record = command_results.get(value)
        if record is None:
            return f"evidence references an unknown command id: {reference}"
        if not command_succeeded(record):
            return (
                f"evidence references command {value!r}, which did not complete successfully "
                f"(result={record.get('result')!r}, exitCode={record.get('exitCode')!r})"
            )
        return None

    if value not in test_ids:
        return f"evidence references a test that does not exist in the suite: {reference}"
    return None


def evaluate_matrix(
    root: Path,
    checkpoint: Path,
    matrix: Any,
    command_results: dict[str, dict[str, Any]] | None = None,
    test_ids: set[str] | None = None,
) -> dict[str, Any]:
    """Audit a requirements matrix and return the completeness report body."""
    if command_results is None:
        command_results = load_command_results(checkpoint)
    if test_ids is None:
        test_ids = collect_test_ids(root)

    findings: list[dict[str, str]] = []
    counters = {status: 0 for status in (
        "NOT_STARTED", "IN_PROGRESS", "COMPLETE", "PARTIAL", "MISSING", "NOT_APPLICABLE")}

    requirements = matrix.get("requirements") if isinstance(matrix, dict) else None
    if not isinstance(requirements, list) or not requirements:
        return {
            "totalRequirements": 0,
            "anchoredRequirements": 0,
            "expectedRequirements": 0,
            "expectedSetSource": "not derived",
            "mandatoryRequirements": 0,
            "complete": 0,
            "partial": 0,
            "missing": 0,
            "notApplicable": 0,
            "inProgress": 0,
            "notStarted": 0,
            "coveragePercent": 0.0,
            "evidenceCoveragePercent": 0.0,
            "result": "FAIL",
            "findings": [{
                "requirement": "-",
                "severity": "BLOCKING",
                "detail": "the requirements matrix contains no requirement",
            }],
        }

    seen: set[str] = set()
    mandatory = 0
    evidence_required = 0
    evidence_resolved = 0
    declared_ids = {
        item.get("id") for item in requirements if isinstance(item, dict)
    }

    # A lesson that the preflight selected is a requirement of this Gate. Dropping it from the matrix
    # would let the memory be silently ignored, which is the failure the memory exists to prevent.
    preflight_path = checkpoint / "LESSON-PREFLIGHT.json"
    preflight: Any = None
    if preflight_path.is_file():
        try:
            preflight = load_json(preflight_path)
        except LedgerError:
            preflight = None
        if isinstance(preflight, dict):
            for derived in preflight.get("derivedRequirements") or []:
                identifier = derived.get("id") if isinstance(derived, dict) else None
                if identifier and identifier not in declared_ids:
                    findings.append({
                        "requirement": str(identifier),
                        "severity": "BLOCKING",
                        "detail": (
                            f"the lesson preflight derived this requirement from "
                            f"{derived.get('lessonId')} but the matrix does not declare it"),
                    })

    # The denominator is not the matrix's to choose. The expected identifier set is derived from
    # the Gate specification, the preflight and the open audit findings, and compared exactly, so
    # deleting a requirement no longer shrinks the total: it becomes a blocking finding.
    expected_total = 0
    expected_source = "not derived"
    gate = matrix.get("gate") if isinstance(matrix, dict) else None
    # The comparison is bound to matrix schemaVersion 2.0.0, which is the version that carries an
    # anchored sourceRef per requirement. A 3.2.0 checkpoint is required to use it, so downgrading
    # the matrix to escape the comparison fails checkpoint validation instead of succeeding.
    if gate and isinstance(matrix, dict) and matrix.get("schemaVersion") == "2.0.0":
        try:
            expected = expected_requirement_refs(
                root, str(gate), checkpoint.name,
                preflight if isinstance(preflight, dict) else None)
            expected_total = len(expected)
            expected_source = EXPECTED_SET_DESCRIPTION
            findings.extend(compare_requirement_sets(expected, declared_requirement_refs(matrix)))
            for item in requirements:
                if isinstance(item, dict) and source_ref(item.get("sourceRef")) is None:
                    findings.append({
                        "requirement": str(item.get("id")),
                        "severity": "BLOCKING",
                        "detail": (
                            "every requirement must carry an anchored sourceRef of the form "
                            "canonical:, lesson:, finding:, attack: or local:"),
                    })
        except LedgerError as exc:
            findings.append({
                "requirement": "-",
                "severity": "BLOCKING",
                "detail": f"the expected requirement set cannot be derived: {exc}",
            })

    for item in requirements:
        identifier = item.get("id", "?") if isinstance(item, dict) else "?"
        if not isinstance(item, dict):
            findings.append({"requirement": str(identifier), "severity": "BLOCKING",
                             "detail": "requirement entry is not an object"})
            continue
        if identifier in seen:
            findings.append({"requirement": identifier, "severity": "BLOCKING",
                             "detail": "duplicate requirement identifier"})
        seen.add(identifier)

        status = item.get("status")
        if status not in counters:
            findings.append({"requirement": identifier, "severity": "BLOCKING",
                             "detail": f"unsupported requirement status {status!r}"})
            continue
        counters[status] += 1
        if item.get("mandatory"):
            mandatory += 1

        evidence = []
        for key in ("implementationEvidence", "testEvidence", "documentationEvidence", "validationEvidence"):
            values = item.get(key)
            if isinstance(values, list):
                evidence.extend(values)

        if status in ("NOT_STARTED", "IN_PROGRESS", "PARTIAL", "MISSING"):
            findings.append({"requirement": identifier, "severity": "BLOCKING",
                             "detail": f"requirement is {status} and cannot ship"})
        if status == "NOT_APPLICABLE" and not (item.get("justification") or item.get("notes")):
            findings.append({"requirement": identifier, "severity": "BLOCKING",
                             "detail": "NOT_APPLICABLE requires an explicit justification"})
        if status == "COMPLETE":
            evidence_required += 1
            if not evidence:
                findings.append({"requirement": identifier, "severity": "BLOCKING",
                                 "detail": "COMPLETE requires at least one evidence reference"})
            else:
                errors = [
                    message for message in (
                        resolve_evidence(root, checkpoint, reference, command_results, test_ids)
                        for reference in evidence
                    ) if message
                ]
                for message in errors:
                    findings.append({"requirement": identifier, "severity": "BLOCKING", "detail": message})
                if not errors:
                    evidence_resolved += 1

    total = sum(counters.values())
    satisfied = counters["COMPLETE"] + counters["NOT_APPLICABLE"]
    coverage = round(satisfied * 100.0 / total, 2) if total else 0.0
    evidence_coverage = round(evidence_resolved * 100.0 / evidence_required, 2) if evidence_required else 100.0
    blocking = [finding for finding in findings if finding["severity"] == "BLOCKING"]
    result = "PASS" if (
        not blocking
        and total > 0
        and counters["PARTIAL"] == 0
        and counters["MISSING"] == 0
        and coverage == 100.0
        and evidence_coverage == 100.0
    ) else "FAIL"

    # How many of the declared rows carry an anchored reference, which is the set the derivation
    # governs. A delivery may add its own local requirements -- the schema defines a ``local:``
    # kind for exactly that -- and those are audited like the rest without belonging to the derived
    # set. Reporting the two counts separately is what lets a control compare the anchored set with
    # the expected one instead of forbidding a delivery to declare a requirement of its own.
    anchored = sum(
        1 for item in requirements
        if isinstance(item, dict)
        and (parsed := source_ref(item.get("sourceRef"))) is not None
        and parsed[0] != "local"
    )

    return {
        "totalRequirements": total,
        "anchoredRequirements": anchored,
        "expectedRequirements": expected_total,
        "expectedSetSource": expected_source,
        "mandatoryRequirements": mandatory,
        "complete": counters["COMPLETE"],
        "partial": counters["PARTIAL"],
        "missing": counters["MISSING"],
        "notApplicable": counters["NOT_APPLICABLE"],
        "inProgress": counters["IN_PROGRESS"],
        "notStarted": counters["NOT_STARTED"],
        "coveragePercent": coverage,
        "evidenceCoveragePercent": evidence_coverage,
        "result": result,
        "findings": findings,
    }


def load_matrix(checkpoint: Path) -> Any:
    path = checkpoint / "REQUIREMENTS-MATRIX.json"
    if not path.is_file():
        raise LedgerError(f"requirements matrix is missing: {path}")
    return load_json(path)
