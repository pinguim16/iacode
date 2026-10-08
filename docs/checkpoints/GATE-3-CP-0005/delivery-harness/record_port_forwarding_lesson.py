#!/usr/bin/env python3
"""Record the confirmed host-port failure and its already-exercised guardrail."""

from __future__ import annotations

import json
import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "development-ledger"))

from ledger_common import utc_now, write_json  # noqa: E402
from lessons import guardrail_registry_path, load_lessons, save_lessons  # noqa: E402

LESSON_ID = "LSN-0058"
GUARDRAIL_ID = "GRD-0059"
TEST_IDS = [
    "test_grafana_is_healthy",
    "test_grafana_refuses_anonymous_access",
    "test_minio_is_pinned_and_persistent",
    "test_redis_answers_on_the_published_port",
]


def lesson(now: str) -> dict:
    return {
        "lessonId": LESSON_ID,
        "title": "Container health does not prove Docker Desktop host-port forwarding",
        "category": "environment",
        "severity": "MEDIUM",
        "source": {
            "gate": "GATE-3",
            "checkpoint": CHECKPOINT.name,
            "finding": "cmd-0046-infra",
        },
        "symptom": (
            "The complete verifier and two targeted reruns found Grafana, MinIO and Redis "
            "accepting host connections and immediately closing them, while Compose reported "
            "every affected container healthy."
        ),
        "rootCauseSummary": (
            "Docker Desktop's host-side published-port forwarding had entered a stale state. "
            "Container-local health checks remained green, so health alone could not observe it."
        ),
        "resolution": (
            "Restart the full stack without deleting volumes, wait for every service to recover, "
            "and repeat the live host-facing infrastructure suite. The unchanged 49-test suite "
            "then passed."
        ),
        "prevention": [
            {
                "kind": "test",
                "reference": TEST_IDS[0],
                "description": (
                    "Live tests connect through the actual loopback-published Grafana, MinIO and "
                    "Redis ports instead of trusting container health metadata."
                ),
            }
        ],
        "guardrails": [GUARDRAIL_ID],
        "evidence": [
            f"file:docs/checkpoints/{CHECKPOINT.name}/COMMANDS.jsonl",
            "file:infra/tests/test_running_stack.py",
        ],
        "applicability": {
            "gates": ["*"],
            "scopes": [],
            "technologies": [],
            "modules": [],
            "requiredCheck": (
                "Exercise every required host-published service through its actual loopback port; "
                "do not substitute container health for host reachability."
            ),
            "requiredEvidence": (
                "A live host-facing infrastructure suite after stack health, with the original "
                "failure retained if a non-destructive restart is required for recovery."
            ),
        },
        "status": "GUARDED",
        "recurrenceKey": "infrastructure/container-health-with-broken-host-port-forwarding",
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
            "notes": "Derived only from this checkpoint's recorded verifier and recovery runs.",
        },
        "trainingEligibility": {
            "trainingAllowed": False,
            "ragAllowed": False,
            "distillationAllowed": False,
            "justification": None,
        },
        "notes": (
            "The guardrail detects the host-path failure; recovery remains an environment action "
            "and never converts the original failed run into a pass."
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
            "title": "Host-published services are exercised through their real loopback ports",
            "kind": "test",
            "reference": TEST_IDS[0],
            "verifiedBy": TEST_IDS,
            "lessons": [LESSON_ID],
            "removingItWouldAllow": (
                "A stack whose containers are healthy but whose host-published ports close every "
                "connection to be reported as operational."
            ),
        })
        write_json(path, registry)
    print(f"{LESSON_ID} status=GUARDED guardrails=['{GUARDRAIL_ID}']")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
