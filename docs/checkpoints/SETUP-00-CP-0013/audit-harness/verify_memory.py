#!/usr/bin/env python3
"""Re-measure the engineering memory and the guardrails without the product tooling.

``lessons.py`` already measures guardrail effectiveness, and ``validate_lessons.py`` already
validates the memory. This module asks the same questions with its own readers, so agreeing means
two independent measurements agreed.

It additionally checks the treatment the project prescribes for a *recurrence*: a repeat of a
guarded failure class is a ``GUARDRAIL_FAILURE`` recorded against the lesson whose class recurred,
with the checkpoint that resolved it, rather than a brand-new lesson that hides the repeat.

    python verify_memory.py --json <out.json>
"""

from __future__ import annotations

import argparse
import json
import unittest
from pathlib import Path
from typing import Any

HARNESS = Path(__file__).resolve().parent
ROOT = HARNESS.parents[3]
MEMORY = ROOT / ".iacode" / "memory"


def suite_identifiers() -> set[str]:
    identifiers: set[str] = set()

    def walk(suite: Any) -> None:
        for item in suite:
            if isinstance(item, unittest.TestSuite):
                walk(item)
            elif isinstance(item, unittest.TestCase):
                full = item.id()
                parts = full.split(".")
                identifiers.add(full)
                if len(parts) >= 2:
                    identifiers.add(".".join(parts[-2:]))
                    identifiers.add(parts[-2])
                    identifiers.add(parts[-1])

    tests = ROOT / "tests"
    walk(unittest.defaultTestLoader.discover(str(tests), top_level_dir=str(tests)))
    return identifiers


def _symbol_exists(reference: str) -> bool:
    """Import the tooling module an invariant names and look the symbol up at run time."""
    import importlib
    import sys as _sys

    module_name, _, symbol = reference.rpartition(".")
    if not module_name or not symbol:
        return False
    ledger = str(ROOT / "scripts" / "development-ledger")
    if ledger not in _sys.path:
        _sys.path.insert(0, ledger)
    try:
        module = importlib.import_module(module_name)
    except Exception:
        return False
    return hasattr(module, symbol)


def load_lessons() -> list[dict[str, Any]]:
    return [json.loads(line)
            for line in (MEMORY / "lessons.jsonl").read_text(encoding="utf-8").splitlines()
            if line.strip()]


def measure(recurrence_finding: str) -> dict[str, Any]:
    tests = suite_identifiers()
    lessons = load_lessons()
    registry = json.loads(
        (MEMORY / "guardrails" / "registry.json").read_text(encoding="utf-8"))["guardrails"]

    unresolved_failures: list[str] = []
    resolved_failures: list[dict[str, str]] = []
    for lesson in lessons:
        for failure in lesson.get("guardrailFailures") or []:
            entry = {
                "lessonId": str(lesson.get("lessonId")),
                "detail": str(failure.get("detail")),
                "resolvedIn": str(failure.get("resolvedIn") or ""),
            }
            if failure.get("resolvedIn"):
                resolved_failures.append(entry)
            else:
                unresolved_failures.append(
                    f"{lesson.get('lessonId')}: {failure.get('detail')}")

    named = {str(item["guardrailId"]) for item in registry}
    guarded_without_guardrail = [
        str(lesson["lessonId"]) for lesson in lessons
        if lesson.get("status") == "GUARDED"
        and not (set(lesson.get("guardrails") or []) & named)]

    unresolvable_controls: list[str] = []
    missing_tests: list[str] = []
    untested: list[str] = []
    for item in registry:
        reference = str(item.get("reference") or "")
        kind = str(item.get("kind") or "")
        if kind == "test":
            if reference not in tests:
                unresolvable_controls.append(f"{item['guardrailId']}:{reference}")
        elif kind == "invariant":
            # An invariant names a symbol of the tooling. This audit imports the module and looks
            # the symbol up at run time rather than searching the source for a definition, so a
            # reference that only looks right in the text does not resolve here.
            if not _symbol_exists(reference):
                unresolvable_controls.append(f"{item['guardrailId']}:{reference}")
        else:
            candidate = ROOT / reference
            if not (candidate.is_file() and candidate.read_text(
                    encoding="utf-8", errors="ignore").strip()):
                unresolvable_controls.append(f"{item['guardrailId']}:{reference}")
        verified_by = [str(value) for value in item.get("verifiedBy") or []]
        if not verified_by:
            untested.append(str(item["guardrailId"]))
        missing_tests += [f"{item['guardrailId']}:{value}"
                          for value in verified_by if value not in tests]

    recurrence = [entry for entry in resolved_failures
                  if recurrence_finding in entry["detail"]]
    new_lessons_for_recurrence = [
        str(lesson["lessonId"]) for lesson in lessons
        if recurrence_finding in json.dumps(lesson.get("source") or {})]

    return {
        "lessons": len(lessons),
        "statuses": {
            status: sum(1 for lesson in lessons if lesson.get("status") == status)
            for status in sorted({str(lesson.get("status")) for lesson in lessons})},
        "guardrails": len(registry),
        "guardrailFailuresUnresolved": unresolved_failures,
        "guardrailFailuresResolved": len(resolved_failures),
        "guardedWithoutRegisteredGuardrail": guarded_without_guardrail,
        "unresolvableControls": unresolvable_controls,
        "guardrailsWithoutVerifyingTest": untested,
        "verifyingTestsThatDoNotExist": missing_tests,
        "recurrenceFinding": recurrence_finding,
        "recurrenceRecordedAsGuardrailFailure": recurrence,
        "lessonsRaisedByTheRecurrence": new_lessons_for_recurrence,
        "clean": not (unresolved_failures or guarded_without_guardrail
                      or unresolvable_controls or untested or missing_tests),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--finding", default="CP11-F-001")
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    result = measure(args.finding)
    if args.json:
        args.json.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n",
                             encoding="utf-8", newline="\n")
    print(
        f"MEMORY lessons={result['lessons']} guardrails={result['guardrails']} "
        f"unresolvedFailures={len(result['guardrailFailuresUnresolved'])} "
        f"resolvedFailures={result['guardrailFailuresResolved']} "
        f"unresolvableControls={len(result['unresolvableControls'])} "
        f"withoutTest={len(result['guardrailsWithoutVerifyingTest'])} "
        f"missingTests={len(result['verifyingTestsThatDoNotExist'])} clean={result['clean']}")
    print("  statuses: " + ", ".join(f"{k}={v}" for k, v in result["statuses"].items()))
    for entry in result["recurrenceRecordedAsGuardrailFailure"]:
        print(f"  RECURRENCE {entry['lessonId']} resolvedIn={entry['resolvedIn']}")
    for item in result["guardrailFailuresUnresolved"][:5]:
        print(f"  UNRESOLVED {item}")
    for item in result["unresolvableControls"][:5]:
        print(f"  UNRESOLVABLE {item}")
    return 0 if result["clean"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
