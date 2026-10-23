"""Register the observed full-verifier failures before changing the measured implementation."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(
    0, str(Path(__file__).resolve().parents[1].parents[2] / "scripts/development-ledger")
)

from ledger_common import load_json, utc_now, write_json
from lessons import load_lessons, recurrence_key, register_recurrence, render_index, save_lessons

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]


def main():
    destination = CHECKPOINT / "FULL-REWORK-REGISTRATION-0001.json"
    if destination.exists():
        raise ValueError("ONE_SHOT_FULL_FAILURE_REGISTRATION")
    proof = load_json(CHECKPOINT / "causal-attempts/full-host-transport/run-0001/RECEIPT.json")
    output = (CHECKPOINT / "causal-attempts/full-host-transport/run-0001/stdout.log").read_text(
        encoding="utf-8"
    )
    failure = load_json(CHECKPOINT / "FULL-VERIFICATION-FAILURE-0001.json")
    if (
        proof["execution"]["producer"]["exitCode"] != 0
        or proof["execution"]["cleanup"]["result"] != "PASS"
        or not proof["temporaryOwnerRemoved"]
        or not proof["sourceUnchanged"]
        or '"exitCode": 128' not in output
        or "Filename too long" not in output
        or failure["passed"] != 43
        or len(failure["failed"]) != 6
    ):
        raise ValueError("ACTUAL_ORIGINAL_COMPLETE_FAILURE_AND_CAUSAL_CLONE_PROOF_REQUIRED")
    rows = load_lessons(ROOT)
    old = next(row for row in rows if row["lessonId"] == "LSN-0151")
    if old["status"] != "GUARDED" or old["recurrenceCount"] != 1:
        raise ValueError("EXPECTED_UNMODIFIED_GUARDED_TRANSPORT_LESSON")
    revised = register_recurrence(
        old,
        CHECKPOINT.name,
        "HISTORY-TRANSPORT-002: unchanged host Red Team T uses a separate raw Git clone; "
        "the actual nested clone exits128 with Filename too long before either producer. "
        "The original current-reader/historical-producer guards do not cover this caller.",
    )
    revised["resolution"] = (
        "Confirmed missing host Red Team transport caller; repair and actual long-depth "
        "null/adverse controls remain pending. Preserve all historical results and counters."
    )
    evidence = (
        "file:docs/checkpoints/GATE-7-CP-0003/causal-attempts/"
        "full-host-transport/run-0001/RECEIPT.json"
    )
    revised["evidence"] += [
        evidence,
        "file:docs/checkpoints/GATE-7-CP-0003/FULL-VERIFICATION-FAILURE-0001.json",
    ]
    rows[rows.index(old)] = revised
    now = utc_now()
    if any(row["lessonId"] == "LSN-0154" for row in rows):
        raise ValueError("NEW_LESSON_ID_ALREADY_PRESENT")
    lesson = {
        "lessonId": "LSN-0154",
        "title": (
            "Self-qualification must separate bounded product inputs from accumulated "
            "audit evidence"
        ),
        "category": "quality",
        "severity": "HIGH",
        "source": {
            "gate": "GATE-7",
            "checkpoint": CHECKPOINT.name,
            "finding": "SELF-SNAPSHOT-GROWTH-001",
        },
        "symptom": (
            "The committed repository exceeds the unchanged64MiB snapshot ceiling after audit "
            "evidence accumulates; the whole canonical functional verifier rejects its "
            "self-qualification snapshot."
        ),
        "rootCauseSummary": (
            "The live self-qualification command archives the entire Git tree, including "
            "accumulated checkpoint outputs, rather than distinguishing the product-input "
            "boundary from separately validated ledger evidence."
        ),
        "resolution": (
            "Confirmed original rejection. A policy-bound immutable input view, complete "
            "project/check preservation and separate complete evidence validation must be "
            "proven before correction can be accepted. No size limit is raised and no "
            "original evidence is removed."
        ),
        "prevention": [],
        "evidence": [
            "file:docs/checkpoints/GATE-7-CP-0003/FULL-VERIFICATION-FAILURE-0001.json",
            "file:docs/checkpoints/GATE-7-CP-0003/VERIFY.json",
        ],
        "applicability": {
            "gates": ["*"],
            "scopes": [],
            "technologies": [],
            "modules": [],
            "requiredCheck": (
                "Bound self-qualification to canonical immutable product inputs without dropping "
                "any required project, runner, test or check; separately retain and validate all "
                "ledger evidence and preserve snapshot security ceilings."
            ),
            "requiredEvidence": (
                "Actual oversized whole-tree rejection, valid immutable input-view controls, "
                "exact project/check equivalence, unchanged capacity refusal and whole current "
                "verifier/assurance."
            ),
        },
        "status": "CONFIRMED",
        "recurrenceKey": recurrence_key(
            "quality",
            "self qualification snapshot conflates product inputs and accumulated audit outputs",
        ),
        "recurrenceCount": 0,
        "guardrailFailures": [],
        "createdAt": now,
        "updatedAt": now,
        "provenance": {
            "sourceType": "repository-generated",
            "provider": "local-execution",
            "model": None,
            "ownership": "project-generated engineering evidence",
            "license": "not-applicable",
            "notes": "Original complete runtime-v5 verifier rejection; not independent approval.",
        },
        "trainingEligibility": {
            "trainingAllowed": False,
            "ragAllowed": False,
            "distillationAllowed": False,
            "justification": "No explicit rights evidence.",
        },
        "guardrails": [],
    }
    rows.append(lesson)
    rework = load_json(CHECKPOINT / "INTERNAL-ENVIRONMENT-REWORK.json")
    for identifier, classification, detail in (
        (
            "HISTORY-TRANSPORT-002",
            "GUARDRAIL_FAILURE LSN-0151",
            revised["guardrailFailures"][-1]["detail"],
        ),
        (
            "SELF-SNAPSHOT-GROWTH-001",
            "NEW_CONFIRMED_FAILURE_CLASS LSN-0154",
            lesson["rootCauseSummary"],
        ),
        (
            "DEPENDENCY-ADVISORY-001",
            "ACTIVE_SECURITY_CONTROL_DETECTED_VULNERABLE_PINS",
            "Live scan blocks certifi and vite; LSN-0057 control fired rather than allowing "
            "false security acceptance.",
        ),
        (
            "FULL-LIVE-OBSERVATIONS-001",
            "OPEN_DIAGNOSIS_NOT_YET_CONFIRMED_CAUSE",
            "Desktop export cancellation, experience catalog-prefix failure and all-container "
            "comparison require actual bounded diagnosis, not guessed fixes or waived checks.",
        ),
    ):
        if any(row["id"] == identifier for row in rework["items"]):
            raise ValueError("REWORK_ID_ALREADY_PRESENT")
        rework["items"].append(
            {
                "id": identifier,
                "status": "OPEN",
                "classification": classification,
                "observed": detail,
                "evidence": "FULL-VERIFICATION-FAILURE-0001.json",
                "requiredCorrection": (
                    "Repair the proven cause, retain original red/null/green evidence, and "
                    "repeat the unchanged complete current assurance before sealing."
                ),
            }
        )
    save_lessons(ROOT, rows)
    (ROOT / ".iacode/memory/LESSONS.md").write_text(
        render_index(rows), encoding="utf-8", newline="\n"
    )
    write_json(CHECKPOINT / "INTERNAL-ENVIRONMENT-REWORK.json", rework)
    write_json(
        destination,
        {
            "recordedAt": now,
            "result": "OPEN_REWORK_NOT_ACCEPTANCE",
            "guardedRecurrence": "LSN-0151",
            "recurrenceCount": revised["recurrenceCount"],
            "newLesson": "LSN-0154",
            "sourceChanged": True,
            "wholeAssuranceMustBeRepeated": True,
            "snapshotLimitChanged": False,
            "historicalEvidenceChanged": False,
        },
    )
    print(
        "LSN-0151 recurrence2 escalated; LSN-0154 confirmed; complete requirement derivation "
        "is required before repair"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
