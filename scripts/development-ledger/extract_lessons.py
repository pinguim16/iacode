#!/usr/bin/env python3
"""Derive lesson candidates from the evidence a delivery already produced.

Reads rework logs, review findings, Red Team findings, recorded failures and retrospectives, and
emits candidates. A candidate is never stronger than ``OBSERVED``: promotion to ``CONFIRMED`` and
then to ``GUARDED`` is a human judgement backed by evidence, and ``GUARDED`` additionally requires a
control that this tool cannot invent. When a candidate matches the recurrence key of an existing
lesson, the existing lesson is incremented instead, and a repeat against a ``GUARDED`` lesson is
recorded as a ``GUARDRAIL_FAILURE``.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

from ledger_common import LedgerError, find_root, redact_text, resolve_latest, utc_now
from lessons import (
    load_lessons,
    next_lesson_id,
    recurrence_key,
    register_recurrence,
    save_lessons,
)

DEFAULT_CATEGORY = "process"

# Words that reliably indicate which part of the system failed, used only to pick a category.
CATEGORY_HINTS = (
    ("checkpoint", "checkpoint"),
    ("inventory", "checkpoint"),
    ("finaliz", "checkpoint"),
    ("tag", "git"),
    ("commit", "git"),
    ("test", "testing"),
    ("suite", "testing"),
    ("lint", "quality"),
    ("static analysis", "quality"),
    ("coverage", "quality"),
    ("secret", "security"),
    ("credential", "security"),
    ("permission", "security"),
    ("schema", "tooling"),
    ("validator", "tooling"),
    ("script", "tooling"),
    ("document", "documentation"),
    ("readme", "documentation"),
    ("provenance", "data"),
    ("training", "training"),
    ("model", "model-behavior"),
    ("provider", "provider"),
    ("timeout", "performance"),
    ("environment", "environment"),
    ("path", "environment"),
)


def classify(text: str) -> str:
    lowered = text.lower()
    for hint, category in CATEGORY_HINTS:
        if hint in lowered:
            return category
    return DEFAULT_CATEGORY


def candidates_from_rework_log(path: Path, checkpoint: str, gate: str) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    if not path.is_file():
        return found
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            cycle = json.loads(line)
        except json.JSONDecodeError:
            continue
        if cycle.get("result") == "GREEN":
            continue
        symptom = "Gate %s failed during cycle %s" % (cycle.get("failedGate") or "unknown",
                                                      cycle.get("cycle"))
        found.append({
            "symptom": symptom,
            "rootCauseSummary": cycle.get("rootCauseSummary") or "root cause not recorded in the cycle",
            "source": {"gate": gate, "checkpoint": checkpoint,
                       "finding": "REWORK-LOG cycle %s" % cycle.get("cycle")},
            "evidence": ["checkpoint:REWORK-LOG.jsonl"] + list(cycle.get("failureEvidence") or []),
        })
    return found


def candidates_from_findings(path: Path, checkpoint: str, gate: str) -> list[dict[str, Any]]:
    """Pick out findings from a review, Red Team or retrospective document."""
    found: list[dict[str, Any]] = []
    if not path.is_file():
        return found
    text = path.read_text(encoding="utf-8")
    pattern = re.compile(r"^##+\s+((?:R|RT)-?\d+[^\n]*)$", re.MULTILINE)
    for match in pattern.finditer(text):
        heading = match.group(1).strip()
        body = text[match.end():].strip().split("\n\n", 1)
        detail = body[0].replace("\n", " ").strip() if body else heading
        found.append({
            "symptom": heading,
            "rootCauseSummary": detail[:400],
            "source": {"gate": gate, "checkpoint": checkpoint, "finding": heading.split()[0]},
            "evidence": [f"checkpoint:{path.name}"],
        })
    return found


def to_lesson(candidate: dict[str, Any], identifier: str) -> dict[str, Any]:
    symptom = redact_text(candidate["symptom"])
    category = classify(symptom + " " + candidate["rootCauseSummary"])
    now = utc_now()
    return {
        "lessonId": identifier,
        "title": symptom[:120],
        "category": category,
        "severity": "MEDIUM",
        "source": candidate["source"],
        "symptom": symptom,
        "rootCauseSummary": redact_text(candidate["rootCauseSummary"]),
        "resolution": "Not yet recorded. Describe what actually corrected the cause before promoting this lesson.",
        "prevention": [],
        "evidence": candidate["evidence"],
        "applicability": {"gates": ["*"], "scopes": [], "technologies": [], "modules": []},
        "status": "OBSERVED",
        "recurrenceKey": recurrence_key(category, symptom),
        "recurrenceCount": 0,
        "guardrailFailures": [],
        "createdAt": now,
        "updatedAt": now,
        "provenance": {
            "sourceType": "repository-generated",
            "provider": "local-script",
            "model": None,
            "ownership": "project-generated evidence",
            "license": "not-applicable",
            "notes": "Extracted from recorded delivery evidence by extract_lessons.py.",
        },
        "trainingEligibility": {
            "trainingAllowed": False,
            "ragAllowed": False,
            "distillationAllowed": False,
            "justification": None,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path)
    parser.add_argument("--checkpoint", type=Path)
    parser.add_argument("--gate", default="SETUP-00")
    parser.add_argument("--source", action="append", default=[],
                        help="extra finding document inside the checkpoint, such as RED-TEAM-REPORT.md")
    parser.add_argument("--write", action="store_true",
                        help="append new candidates and increment recurrences in lessons.jsonl")
    args = parser.parse_args()

    root = find_root(args.root) if args.root else find_root()
    checkpoint = args.checkpoint or resolve_latest(root)
    if not checkpoint.is_absolute():
        checkpoint = root / checkpoint

    candidates = candidates_from_rework_log(checkpoint / "REWORK-LOG.jsonl", checkpoint.name, args.gate)
    for name in args.source or ["REVIEW-REPORT.md", "RED-TEAM-REPORT.md", "RETROSPECTIVE.md"]:
        candidates += candidates_from_findings(checkpoint / name, checkpoint.name, args.gate)

    lessons = load_lessons(root)
    by_key = {lesson.get("recurrenceKey"): index for index, lesson in enumerate(lessons)}
    created: list[str] = []
    repeated: list[str] = []

    for candidate in candidates:
        category = classify(candidate["symptom"] + " " + candidate["rootCauseSummary"])
        key = recurrence_key(category, candidate["symptom"])
        if key in by_key:
            index = by_key[key]
            before = lessons[index].get("status")
            lessons[index] = register_recurrence(
                lessons[index], checkpoint.name, candidate["symptom"])
            repeated.append("%s (%s)" % (lessons[index]["lessonId"],
                                         "GUARDRAIL_FAILURE" if before == "GUARDED" else "recurrence"))
            continue
        identifier = next_lesson_id(lessons)
        lesson = to_lesson(candidate, identifier)
        lessons.append(lesson)
        by_key[lesson["recurrenceKey"]] = len(lessons) - 1
        created.append(identifier)

    if args.write:
        save_lessons(root, lessons)

    print("LESSON_CANDIDATES considered=%d created=%d repeated=%d written=%s" % (
        len(candidates), len(created), len(repeated), "yes" if args.write else "no"))
    for identifier in created:
        print(f"- OBSERVED {identifier}")
    for entry in repeated:
        print(f"- REPEAT {entry}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except LedgerError as exc:
        print(f"LEDGER_ERROR: {exc}")
        sys.exit(2)
