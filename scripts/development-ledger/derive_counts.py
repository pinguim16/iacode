#!/usr/bin/env python3
"""Derive every count a delivery uses as evidence, from one machine-readable source each.

The M0 audit found a sealed checkpoint whose state declared 47 mandatory requirements while its
matrix and its completeness report both computed 45, and a report that said 180 tests where the
suite had 181. The cause was the same in both cases: an authoritative number maintained by hand in
more than one place.

A count is now derived once, here, from the artifact that owns it:

    TESTS        the discovered test suite and TESTS.json
    REQUIREMENTS the requirements matrix, after the expected-set comparison
    FINDINGS     the closure record of every open audit
    ATTACKS      the internal Red Team report
    LESSONS      the engineering memory
    GUARDRAILS   the guardrail registry

``validate_checkpoint.py`` recomputes these values and rejects both a ``COUNTS.json`` that
disagrees and any Markdown in the checkpoint that states ``N/M LABEL`` with different numbers.
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
import unittest
from pathlib import Path
from typing import Any

from ledger_common import (
    LedgerError,
    find_root,
    load_json,
    resolve_latest,
    utc_now,
    validate_schema,
)
from policies import counted_test_suites

COUNT_LABELS = ("TESTS", "REQUIREMENTS", "FINDINGS", "ATTACKS", "LESSONS", "GUARDRAILS")


def count_unittest_cases(root: Path, relative: str) -> int:
    """Distinct cases a ``unittest`` suite discovers under ``relative``."""
    directory = root / relative
    if not directory.is_dir():
        return 0
    identifiers: set[str] = set()

    def walk(suite: Any) -> None:
        for item in suite:
            if isinstance(item, unittest.TestSuite):
                walk(item)
            elif isinstance(item, unittest.TestCase):
                identifiers.add(item.id())

    walk(unittest.defaultTestLoader.discover(str(directory), top_level_dir=str(directory)))
    return len(identifiers)


def count_pytest_cases(root: Path, relative: str) -> int:
    """Distinct cases a ``pytest`` suite declares under ``relative``, read rather than executed.

    The suite is parsed with ``ast`` for the same reason the evidence resolver parses it: deriving
    a count by importing test modules would execute them and would make the denominator depend on
    an installed environment the validator does not have.

    ``pytest.mark.parametrize`` is refused rather than approximated. A parametrised function is one
    source definition and several collected cases, so a static reading and the runner would report
    different numbers for the same suite, and a denominator that cannot be re-derived exactly is a
    claim rather than a measurement.
    """
    directory = root / relative
    if not directory.is_dir():
        return 0
    total = 0
    for path in sorted(directory.rglob("test_*.py")):
        if "__pycache__" in path.parts:
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except (OSError, SyntaxError) as exc:
            raise LedgerError(f"declared pytest suite file cannot be parsed: {path.name}: {exc}")
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if not node.name.startswith("test"):
                continue
            for decorator in node.decorator_list:
                if "parametrize" in ast.dump(decorator):
                    raise LedgerError(
                        f"{path.name}::{node.name} is parametrised; the TESTS denominator is "
                        f"derived statically and cannot reproduce a runtime expansion")
            total += 1
    return total


def count_test_cases(root: Path) -> int:
    """Distinct test cases across every counted suite the canonical registry declares."""
    total = 0
    for suite in counted_test_suites(root):
        framework = str(suite.get("framework"))
        relative = str(suite["root"])
        if framework == "python-unittest":
            total += count_unittest_cases(root, relative)
        elif framework == "python-pytest":
            total += count_pytest_cases(root, relative)
    return total


def executed_test_runs(tests: dict[str, Any]) -> dict[str, int]:
    """Passing cases per *physical* execution, not per category.

    One discovery run over ``tests/`` covers unit and integration cases at once. Recording it in
    both categories and adding the two produced ``610/306`` in the audit checkpoint: twice the
    suite, from one execution. Categories that name the same run -- explicitly through ``runId``,
    or implicitly by recording the same command with the same result -- are one measurement, and
    the largest recorded value for that run is the one that counts.
    """
    runs: dict[str, int] = {}
    for category in ("unit", "integration", "e2e"):
        entry = tests.get(category)
        if not isinstance(entry, dict) or not entry.get("executed"):
            continue
        passed = int(entry.get("passed") or 0)
        failed = int(entry.get("failed") or 0)
        identifier = entry.get("runId") or "command:%s|%d/%d" % (
            entry.get("command"), passed, failed)
        runs[str(identifier)] = max(runs.get(str(identifier), 0), passed)
    return runs


def derive_counts(root: Path, checkpoint: Path) -> dict[str, dict[str, Any]]:
    from delivery_assurance import evaluate_matrix
    from lessons import load_guardrails, load_lessons
    from policies import audit_findings, open_audits

    counts: dict[str, dict[str, Any]] = {}

    discovered = count_test_cases(root)
    passed = discovered
    tests_path = checkpoint / "TESTS.json"
    if tests_path.is_file():
        tests = load_json(tests_path)
        if isinstance(tests, dict):
            passed = sum(executed_test_runs(tests).values())
    counts["TESTS"] = {
        "numerator": passed,
        "denominator": discovered,
        "source": (
            "discovery over every counted suite of .iacode/policies/test-suites.json, "
            "cross-checked with TESTS.json and deduplicated by physical execution"),
    }

    matrix_path = checkpoint / "REQUIREMENTS-MATRIX.json"
    if matrix_path.is_file():
        matrix = load_json(matrix_path)
        report = evaluate_matrix(root, checkpoint, matrix)
        counts["REQUIREMENTS"] = {
            "numerator": report["complete"] + report["notApplicable"],
            "denominator": report["totalRequirements"],
            "source": "REQUIREMENTS-MATRIX.json evaluated against the derived expected set",
        }

    state_path = checkpoint / "STATE.json"
    gate = ""
    milestone = "M0"
    if state_path.is_file():
        state = load_json(state_path)
        if isinstance(state, dict):
            gate = str(state.get("gate") or "")
            milestone = str((state.get("milestone") or {}).get("id") or "M0")

    total_findings = 0
    closed_findings = 0
    for audit in open_audits(root, gate, checkpoint.name):
        total_findings += len(audit_findings(root, audit))
        name = audit.get("findingsClosureFile") or "FINDINGS-CLOSURE.json"
        path = checkpoint / str(name)
        if path.is_file():
            document = load_json(path)
            rows = document.get("findings") if isinstance(document, dict) else None
            closed_findings += sum(
                1 for item in rows or []
                if isinstance(item, dict) and item.get("status") == "CLOSED")
    if total_findings:
        counts["FINDINGS"] = {
            "numerator": closed_findings,
            "denominator": total_findings,
            "source": "the sealed audit review reports and the closure record",
        }

    red_team_path = checkpoint / f"{milestone}-INTERNAL-RED-TEAM.json"
    if red_team_path.is_file():
        report = load_json(red_team_path)
        if isinstance(report, dict):
            attacks = [item for item in report.get("attacks") or [] if isinstance(item, dict)]
            counts["ATTACKS"] = {
                "numerator": sum(1 for item in attacks if item.get("result") == "DEFENDED"),
                "denominator": len(attacks),
                "source": red_team_path.name,
            }

    lessons = load_lessons(root)
    counts["LESSONS"] = {
        "numerator": sum(1 for lesson in lessons if lesson.get("status") == "GUARDED"),
        "denominator": len(lessons),
        "source": ".iacode/memory/lessons.jsonl",
    }

    guardrails = load_guardrails(root)
    from lessons import guardrail_effectiveness

    effectiveness = guardrail_effectiveness(root, lessons)
    counts["GUARDRAILS"] = {
        "numerator": effectiveness["guardrailsEffective"],
        "denominator": len(guardrails),
        "source": ".iacode/memory/guardrails/registry.json measured for effectiveness",
    }

    return counts


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path)
    parser.add_argument("--checkpoint", type=Path)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    root = find_root(args.root) if args.root else find_root()
    checkpoint = args.checkpoint or resolve_latest(root)
    if not checkpoint.is_absolute():
        checkpoint = root / checkpoint

    document = {
        "schemaVersion": "1.0.0",
        "checkpoint": checkpoint.name,
        "generatedAt": utc_now(),
        "counts": derive_counts(root, checkpoint),
    }
    schema_path = root / ".iacode" / "schemas" / "counts.schema.json"
    if schema_path.is_file():
        errors = validate_schema(document, load_json(schema_path))
        if errors:
            print("COUNTS_INVALID")
            for error in errors:
                print(f"- {error}")
            return 2

    if args.write:
        (checkpoint / "COUNTS.json").write_text(
            json.dumps(document, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8", newline="\n")

    print("COUNTS_DERIVED " + " ".join(
        f"{label}={value['numerator']}/{value['denominator']}"
        for label, value in document["counts"].items()))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except LedgerError as exc:
        print(f"LEDGER_ERROR: {exc}")
        sys.exit(2)
