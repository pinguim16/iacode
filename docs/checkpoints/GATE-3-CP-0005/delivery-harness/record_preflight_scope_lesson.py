#!/usr/bin/env python3
"""Record the lesson that every preflight exclusion must declare its scope."""

from __future__ import annotations

import json
import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "development-ledger"))

from ledger_common import utc_now, write_json  # noqa: E402
from lessons import guardrail_registry_path, load_lessons, save_lessons  # noqa: E402

LESSON_ID = "LSN-0059"
GUARDRAIL_ID = "GRD-0060"
TEST_ID = "test_the_repository_preflight_covers_every_applicable_lesson"


def lesson(now: str) -> dict:
    return {
        "lessonId": LESSON_ID,
        "title": "A lesson exclusion must declare the scope it excludes",
        "category": "process",
        "severity": "MEDIUM",
        "source": {
            "gate": "GATE-3",
            "checkpoint": CHECKPOINT.name,
            "finding": "cmd-0064",
        },
        "symptom": (
            "The full suite rejected LSN-0058 because technology and module selectors excluded "
            "it from a generic preflight while its scopes list was empty."
        ),
        "rootCauseSummary": (
            "Applicability dimensions were used as incidental metadata. In this model they are "
            "selectors, so they silently narrowed where the lesson constrained delivery."
        ),
        "resolution": (
            "Remove selectors that were not intended to narrow LSN-0058. Reserve non-empty "
            "selectors for deliberate exclusions, with scopes naming the boundary explicitly."
        ),
        "prevention": [
            {
                "kind": "test",
                "reference": TEST_ID,
                "description": (
                    "Every active lesson excluded from a canonical preflight must carry a "
                    "non-empty scopes declaration that makes the exclusion reviewable."
                ),
            }
        ],
        "guardrails": [GUARDRAIL_ID],
        "evidence": [
            f"file:docs/checkpoints/{CHECKPOINT.name}/COMMANDS.jsonl",
            "file:tests/test_development_ledger.py",
        ],
        "applicability": {
            "gates": ["*"],
            "scopes": [],
            "technologies": [],
            "modules": [],
            "requiredCheck": (
                "Confirm every active lesson excluded from a preflight declares a non-empty "
                "scope selector, and that incidental metadata does not narrow applicability."
            ),
            "requiredEvidence": (
                "A passing repository-preflight coverage test over the complete active lesson set."
            ),
        },
        "status": "GUARDED",
        "recurrenceKey": "process/lesson-excluded-without-declared-scope",
        "recurrenceCount": 0,
        "guardrailFailures": [],
        "createdAt": now,
        "updatedAt": now,
        "provenance": {
            "sourceType": "repository-generated",
            "provider": "local-execution",
            "model": None,
            "ownership": "project-generated evidence",
            "license": "not-applicable",
            "notes": "Derived from cmd-0064 and its targeted repair proof in cmd-0069.",
        },
        "trainingEligibility": {
            "trainingAllowed": False,
            "ragAllowed": False,
            "distillationAllowed": False,
            "justification": None,
        },
        "notes": (
            "The control checks explicit exclusions; it cannot decide whether a deliberately "
            "declared scope is semantically the best boundary."
        ),
    }


def main() -> int:
    now = utc_now()
    lessons = load_lessons(ROOT)
    indexes = {item.get("lessonId"): index for index, item in enumerate(lessons)}
    if LESSON_ID in indexes:
        previous = lessons[indexes[LESSON_ID]]
        updated = lesson(now)
        updated["createdAt"] = previous.get("createdAt", now)
        lessons[indexes[LESSON_ID]] = updated
    else:
        lessons.append(lesson(now))
    save_lessons(ROOT, lessons)

    path = guardrail_registry_path(ROOT)
    registry = json.loads(path.read_text(encoding="utf-8"))
    present = {entry["guardrailId"] for entry in registry["guardrails"]}
    if GUARDRAIL_ID not in present:
        registry["guardrails"].append({
            "guardrailId": GUARDRAIL_ID,
            "title": "Lesson preflight exclusions declare their scope",
            "kind": "test",
            "reference": TEST_ID,
            "verifiedBy": [TEST_ID],
            "lessons": [LESSON_ID],
            "removingItWouldAllow": (
                "A technology or module selector to silently exclude an active lesson without "
                "declaring the scope boundary reviewers must evaluate."
            ),
        })
        write_json(path, registry)
    print(f"{LESSON_ID} status=GUARDED guardrails=['{GUARDRAIL_ID}']")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
