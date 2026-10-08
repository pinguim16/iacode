#!/usr/bin/env python3
"""Record and, after its control is tested, guard the lesson from M1-F-004.

The first phase runs before lesson preflight so the audit failure constrains this corrective
delivery.  The second phase is used only after the guardrail test exists and passes.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "development-ledger"))

from ledger_common import utc_now, write_json  # noqa: E402
from lessons import guardrail_registry_path, load_lessons, save_lessons  # noqa: E402

LESSON_ID = "LSN-0057"
GUARDRAIL_ID = "GRD-0058"
TEST_ID = "test_the_dependency_scan_blocks_critical_and_high_findings"


def lesson(now: str) -> dict:
    return {
        "lessonId": LESSON_ID,
        "title": "A pinned lock can become unsafe without changing, so advisory state is live evidence",
        "category": "security",
        "severity": "CRITICAL",
        "source": {
            "gate": "GATE-3",
            "checkpoint": "GATE-3-CP-0004",
            "finding": "M1-F-004",
        },
        "symptom": (
            "A sealed delivery whose implementation checks passed later failed the unchanged "
            "dependency gate with two Critical and four High npm advisories in its pinned graph."
        ),
        "rootCauseSummary": (
            "The lockfile was reproducible but advisory state changed after it was pinned. "
            "Reproducibility fixes the graph; it does not make the graph permanently safe."
        ),
        "resolution": (
            "Update the direct frontend pins and resolved lock graph to non-vulnerable versions, "
            "then require a live scan of both npm and PyPI advisory sources before handoff."
        ),
        "prevention": [
            {
                "kind": "automated-check",
                "reference": "scripts/iacode/dependency_scan.py",
                "description": (
                    "The mandatory scan fails closed when either advisory source is unavailable "
                    "and blocks every relevant Critical or High finding."
                ),
            }
        ],
        "evidence": [
            "file:docs/checkpoints/GATE-3-CP-0004/FINDINGS.json",
            "file:docs/checkpoints/GATE-3-CP-0004/DEPENDENCY-SCAN-REPORT.json",
            "file:scripts/iacode/dependency_scan.py",
        ],
        "applicability": {
            "gates": ["*"],
            "scopes": [],
            "technologies": [],
            "modules": [],
            "requiredCheck": (
                "For every pinned dependency graph delivered by a Gate, run the current advisory "
                "scan against every required source and refuse Critical or High findings without "
                "suppressing advisories or narrowing the denominator."
            ),
            "requiredEvidence": (
                "A report from every required advisory source showing zero relevant Critical or "
                "High findings, plus a test that proves those severities remain blocking."
            ),
        },
        "status": "CONFIRMED",
        "recurrenceKey": "security/pinned-lock-advisory-state-changed",
        "recurrenceCount": 0,
        "guardrailFailures": [],
        "createdAt": now,
        "updatedAt": now,
        "provenance": {
            "sourceType": "repository-generated",
            "provider": "local-analysis",
            "model": None,
            "ownership": "project-generated evidence",
            "license": "not-applicable",
            "notes": (
                "Derived from the sealed M1 fresh-session audit; no content outside this "
                "repository was used."
            ),
        },
        "trainingEligibility": {
            "trainingAllowed": False,
            "ragAllowed": False,
            "distillationAllowed": False,
            "justification": None,
        },
        "notes": (
            "The residual limit is time: a green scan is evidence about the advisory databases "
            "at execution time, so every later release still needs a fresh scan."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=("record", "guard"), required=True)
    args = parser.parse_args()
    now = utc_now()
    lessons = load_lessons(ROOT)
    indexes = {item.get("lessonId"): index for index, item in enumerate(lessons)}
    if LESSON_ID not in indexes:
        lessons.append(lesson(now))
        indexes[LESSON_ID] = len(lessons) - 1

    if args.phase == "guard":
        item = lessons[indexes[LESSON_ID]]
        item["status"] = "GUARDED"
        item["updatedAt"] = now
        item["guardrails"] = [GUARDRAIL_ID]
        if not any(control.get("reference") == TEST_ID for control in item["prevention"]):
            item["prevention"].append({
                "kind": "test",
                "reference": TEST_ID,
                "description": (
                    "The dependency scanner's blocking severities and fail-closed source policy "
                    "are structural assertions, so weakening either turns the suite red."
                ),
            })

        path = guardrail_registry_path(ROOT)
        registry = json.loads(path.read_text(encoding="utf-8"))
        present = {entry["guardrailId"] for entry in registry["guardrails"]}
        if GUARDRAIL_ID not in present:
            registry["guardrails"].append({
                "guardrailId": GUARDRAIL_ID,
                "title": "Critical and High dependency advisories remain release-blocking",
                "kind": "automated-check",
                "reference": "scripts/iacode/dependency_scan.py",
                "verifiedBy": [TEST_ID],
                "lessons": [LESSON_ID],
                "removingItWouldAllow": (
                    "A pinned graph with a current Critical or High advisory, or an unavailable "
                    "advisory source, to be handed off as green."
                ),
            })
        write_json(path, registry)

    save_lessons(ROOT, lessons)
    current = lessons[indexes[LESSON_ID]]
    print(f"{LESSON_ID} status={current['status']} guardrails={current.get('guardrails', [])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
