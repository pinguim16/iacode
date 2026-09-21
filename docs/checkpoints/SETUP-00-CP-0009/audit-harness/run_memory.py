#!/usr/bin/env python3
"""Section 16 and 18: the engineering memory and guardrail effectiveness, recomputed.

Nothing here reads a count from a report. Every number is derived from
.iacode/memory/ and from the discovered test suite.
"""
from __future__ import annotations

import json
import sys
import unittest
from collections import Counter
from pathlib import Path
import os as _os
from pathlib import Path as _Path
_DEFAULT_ROOT = _Path(__file__).resolve().parents[4]

ROOT = Path(_os.environ.get("IACODE_ROOT") or _DEFAULT_ROOT)
sys.path.insert(0, str(ROOT / "scripts" / "development-ledger"))

from lessons import (  # noqa: E402
    build_preflight, guardrail_effectiveness, register_recurrence, validate_lessons,
)


def suite_ids() -> set[str]:
    import os
    loader = unittest.TestLoader()
    previous = os.getcwd()
    os.chdir(ROOT)
    try:
        suite = loader.discover("tests")
    finally:
        os.chdir(previous)
    names: set[str] = set()
    stack = [suite]
    while stack:
        item = stack.pop()
        if isinstance(item, unittest.TestSuite):
            stack.extend(list(item))
        else:
            names.add(type(item).__name__ + "." + item._testMethodName)
    return names


def main() -> int:
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    names = suite_ids()
    lessons = [json.loads(line) for line in
               (ROOT / ".iacode" / "memory" / "lessons.jsonl").read_text(
                   encoding="utf-8").splitlines() if line.strip()]
    registry = json.loads((ROOT / ".iacode" / "memory" / "guardrails" / "registry.json")
                          .read_text(encoding="utf-8"))["guardrails"]
    guards = {item["guardrailId"]: item for item in registry}

    chain = []
    problems = []
    for lesson in lessons:
        if lesson["status"] != "GUARDED":
            continue
        for identifier in lesson.get("guardrails") or []:
            entry = guards.get(identifier)
            if entry is None:
                problems.append({"lesson": lesson["lessonId"], "issue": "missing guardrail",
                                 "guardrail": identifier})
                continue
            verified = list(entry.get("verifiedBy") or [])
            chain.append({
                "lesson": lesson["lessonId"], "guardrail": identifier,
                "kind": entry.get("kind"), "control": entry.get("reference"),
                "controlResolves": (entry.get("reference") in names
                                    if entry.get("kind") == "test"
                                    else (ROOT / str(entry.get("reference"))).exists()
                                    if "/" in str(entry.get("reference")) else True),
                "verifiedBy": verified,
                "verifyingTestsExist": all(item in names for item in verified) and bool(verified),
                "namesTheLessonBack": lesson["lessonId"] in (entry.get("lessons") or []),
            })
    for item in chain:
        if not (item["controlResolves"] and item["verifyingTestsExist"]
                and item["namesTheLessonBack"]):
            problems.append(item)

    effectiveness = guardrail_effectiveness(ROOT)
    state = json.loads((ROOT / "docs" / "checkpoints" / "SETUP-00-CP-0008" / "STATE.json")
                       .read_text(encoding="utf-8"))["guardrailEffectiveness"]
    recomputed = {
        "guardrailsTotal": len(registry),
        "guardrailsResolved": sum(1 for item in chain if item["controlResolves"]),
        "guardrailsTested": sum(1 for item in chain if item["verifyingTestsExist"]),
        "guardrailsEffective": sum(1 for item in chain
                                   if item["controlResolves"] and item["verifyingTestsExist"]
                                   and item["namesTheLessonBack"]),
        "guardrailFailures": sum(1 for lesson in lessons
                                 for failure in (lesson.get("guardrailFailures") or [])
                                 if not failure.get("resolvedIn")),
    }

    # recurrence and lifecycle
    copy = json.loads(json.dumps(lessons))
    index = next(i for i, item in enumerate(copy)
                 if item["status"] == "GUARDED" and not item.get("guardrailFailures"))
    identifier = copy[index]["lessonId"]
    copy[index] = register_recurrence(copy[index], "SETUP-00-CP-0009",
                                      "the audit reproduced this failure class")
    escalated = {"lesson": identifier, "status": copy[index]["status"],
                 "severity": copy[index]["severity"],
                 "recurrenceCount": copy[index]["recurrenceCount"],
                 "failures": len(copy[index]["guardrailFailures"])}
    copy[index]["status"] = "GUARDED"
    forced = [error for error in validate_lessons(ROOT, copy) if identifier in error]
    copy[index]["guardrailFailures"][0]["resolvedIn"] = "SETUP-00-CP-0010"
    repaired = [error for error in validate_lessons(ROOT, copy) if identifier in error]

    retired = json.loads(json.dumps(lessons))
    retired[0]["status"] = "RETIRED"
    import lessons as module
    original = module.load_lessons
    module.load_lessons = lambda _root: retired
    try:
        preflight = build_preflight(ROOT, "SETUP-00", "audit probe", [], [])
    finally:
        module.load_lessons = original

    stored_preflight = json.loads(
        (ROOT / "docs" / "checkpoints" / "SETUP-00-CP-0008" / "LESSON-PREFLIGHT.json")
        .read_text(encoding="utf-8"))
    derived_ids = {item["lessonId"] for item in stored_preflight["derivedRequirements"]}
    matrix = json.loads(
        (ROOT / "docs" / "checkpoints" / "SETUP-00-CP-0008" / "REQUIREMENTS-MATRIX.json")
        .read_text(encoding="utf-8"))["requirements"]
    matrix_lessons = {row["sourceRef"].split("lesson:", 1)[1] for row in matrix
                      if str(row.get("sourceRef", "")).startswith("lesson:")}
    active = {item["lessonId"] for item in lessons
              if item["status"] not in ("SUPERSEDED", "RETIRED")}

    report = {
        "lessonsTotal": len(lessons),
        "statuses": dict(Counter(item["status"] for item in lessons)),
        "trainingAllowed": dict(Counter(
            str(item["trainingEligibility"]["trainingAllowed"]) for item in lessons)),
        "recurrenceCounts": dict(Counter(str(item.get("recurrenceCount")) for item in lessons)),
        "lessonsWithRecurrence": [item["lessonId"] for item in lessons
                                  if item.get("recurrenceCount")],
        "guardrailFailures": [{"lesson": item["lessonId"],
                               "resolvedIn": [f.get("resolvedIn")
                                              for f in item["guardrailFailures"]]}
                              for item in lessons if item.get("guardrailFailures")],
        "resolutionChain": chain,
        "resolutionProblems": problems,
        "effectivenessRecomputed": recomputed,
        "effectivenessProduct": {key: effectiveness[key] for key in recomputed},
        "effectivenessCheckpointState": {key: state[key] for key in recomputed},
        "effectivenessAgrees": (recomputed == {key: effectiveness[key] for key in recomputed}
                                == {key: state[key] for key in recomputed}),
        "recurrenceEscalation": escalated,
        "guardedWhileUnresolvedRefused": forced,
        "guardedAfterRepairAccepted": not repaired,
        "derivedRequirementsAfterRetiring": len(preflight["derivedRequirements"]),
        "retiredLessonStillDerived": any(item["lessonId"] == retired[0]["lessonId"]
                                         for item in preflight["derivedRequirements"]),
        "activeLessons": len(active),
        "derivedRequirements": len(derived_ids),
        "lessonRowsInMatrix": len(matrix_lessons),
        "activeWithoutRequirement": sorted(active - derived_ids),
        "requirementWithoutActiveLesson": sorted(derived_ids - active),
        "requirementWithoutMatrixRow": sorted(derived_ids - matrix_lessons),
    }
    (out / "memory-results.json").write_text(json.dumps(report, indent=2) + "\n",
                                             encoding="utf-8", newline="\n")
    print(json.dumps({key: report[key] for key in (
        "lessonsTotal", "statuses", "effectivenessAgrees", "effectivenessRecomputed",
        "recurrenceEscalation", "guardedAfterRepairAccepted",
        "derivedRequirementsAfterRetiring", "activeLessons", "derivedRequirements",
        "lessonRowsInMatrix")}, indent=1))
    print("resolution problems: " + str(len(problems)))
    print("guarded-while-unresolved refusal: " + str(forced))
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
