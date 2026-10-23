"""Register observed recurrences and measured local guards without whole/independent verdicts."""

from __future__ import annotations

import argparse
import ast
import hashlib
import sys
from pathlib import Path

sys.path.insert(
    0, str(Path(__file__).resolve().parents[1].parents[2] / "scripts/development-ledger")
)

from ledger_common import find_secrets, load_json, scope_fingerprint, utc_now, write_json
from lessons import load_lessons, register_recurrence, render_index, save_lessons

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]


def test_names(path, class_name):
    tree = ast.parse((ROOT / path).read_text(encoding="utf-8"))
    owner = next(
        node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == class_name
    )
    names = [
        class_name + "." + node.name
        for node in owner.body
        if isinstance(node, ast.FunctionDef) and node.name.startswith("test_")
    ]
    if not names or len(names) != len(set(names)):
        raise ValueError("COMPLETE_ACTUAL_TEST_CLASS_REQUIRED")
    return names


def save(rows):
    save_lessons(ROOT, rows)
    (ROOT / ".iacode/memory/LESSONS.md").write_text(
        render_index(rows), encoding="utf-8", newline="\n"
    )


def prepare():
    destination = CHECKPOINT / "FULL-REWORK-MEMORY-PREPARATION.json"
    if destination.exists():
        raise ValueError("ONE_SHOT_MEMORY_PREPARATION")
    original = load_json(CHECKPOINT / "causal-attempts/all-m2/run-0010.json")
    stderr = ROOT / original["streams"]["stderr"]["path"]
    raw = stderr.read_bytes()
    if (
        original["exitCode"] != 1
        or not original["sourceUnchanged"]
        or hashlib.sha256(raw).hexdigest() != original["streams"]["stderr"]["sha256"]
        or b"Ran 107 tests" not in raw
        or b"FAILED (failures=2)" not in raw
        or b"'LSN-0154' not found" not in raw
    ):
        raise ValueError("ACTUAL_NEW_LESSON_DOCUMENTATION_REJECTION_REQUIRED")
    rows = load_lessons(ROOT)
    old = next(row for row in rows if row["lessonId"] == "LSN-0140")
    if old["status"] != "GUARDED" or old["recurrenceCount"] != 4:
        raise ValueError("EXACT_ORIGINAL_CONTINUATION_STATUS_REQUIRED")
    revised = register_recurrence(
        old,
        CHECKPOINT.name,
        "CONTINUATION-002: actual all-M2 run0010 rejects the newly registered LSN-0154 "
        "missing from the current retrospective. The unchanged automatic guard fired before "
        "publication; preserve this repeated authoring-order failure, not an implementation "
        "guard escape or a failed independent audit.",
    )
    revised["resolution"] = "New-lesson retrospective completion and current controls remain due."
    rows[rows.index(old)] = revised
    rework = load_json(CHECKPOINT / "INTERNAL-ENVIRONMENT-REWORK.json")
    rework["items"].append(
        {
            "id": "CONTINUATION-002",
            "status": "OPEN",
            "classification": "GUARDRAIL_FAILURE LSN-0140 AUTHORING_ORDER_CONTROL_FIRED",
            "observed": revised["guardrailFailures"][-1]["detail"],
            "evidence": "causal-attempts/all-m2/run-0010.json",
            "requiredCorrection": (
                "Keep the canonical template and every actual lesson/guard identity; "
                "repeat unchanged current controls and whole assurance."
            ),
        }
    )
    registry = load_json(ROOT / ".iacode/memory/guardrails/registry.json")
    for identifier, guard_id, path, owner in (
        ("LSN-0151", "GRD-0154", "tests/test_m2_host_transport.py", "M2HostTransportTests"),
        ("LSN-0154", "GRD-0157", "tests/test_m2_self_snapshot.py", "M2SelfSnapshotTests"),
    ):
        lesson = next(row for row in rows if row["lessonId"] == identifier)
        if lesson["status"] != "CONFIRMED":
            raise ValueError("OPEN_CONFIRMED_LOCAL_FAILURE_REQUIRED")
        names = test_names(path, owner)
        for name in names:
            if not any(row["reference"] == name for row in lesson["prevention"]):
                lesson["prevention"].append(
                    {
                        "kind": "test",
                        "reference": name,
                        "description": (
                            "Actual Git positive/null/adverse control; local proof still due."
                        ),
                    }
                )
        if guard_id not in lesson["guardrails"]:
            lesson["guardrails"].append(guard_id)
        guards = [row for row in registry["guardrails"] if row["guardrailId"] == guard_id]
        if not guards:
            if identifier != "LSN-0154":
                raise ValueError("EXISTING_HOST_GIT_GUARD_REQUIRED")
            guards = [
                {
                    "guardrailId": guard_id,
                    "title": "Immutable bounded product inputs preserve every non-checkpoint blob",
                    "kind": "test",
                    "reference": names[0],
                    "verifiedBy": [],
                    "lessons": [identifier],
                    "removingItWouldAllow": (
                        "Accumulated audit outputs to consume the self-snapshot ceiling, "
                        "or product inputs to be silently omitted or replaced."
                    ),
                }
            ]
            registry["guardrails"].extend(guards)
        if len(guards) != 1:
            raise ValueError("UNAMBIGUOUS_LOCAL_GUARD_REQUIRED")
        guards[0]["verifiedBy"] = list(dict.fromkeys([*guards[0]["verifiedBy"], *names]))
        lesson["updatedAt"] = utc_now()
    save(rows)
    write_json(ROOT / ".iacode/memory/guardrails/registry.json", registry)
    write_json(CHECKPOINT / "INTERNAL-ENVIRONMENT-REWORK.json", rework)
    write_json(
        destination,
        {
            "observedAt": utc_now(),
            "result": "PREPARED_NOT_GUARDED_OR_WHOLE_ACCEPTANCE",
            "continuationRecurrenceCount": revised["recurrenceCount"],
            "newGuard": "GRD-0157",
            "newTestsMustRun": True,
            "historicalFailuresOrCountersRewritten": False,
        },
    )
    print("CONTINUATION_RECURRENCE_REGISTERED_GUARDS_PREPARED_NOT_ACCEPTED")
    return 0


def close_local():
    destination = CHECKPOINT / "FULL-REWORK-LOCAL-PREVENTION.json"
    if destination.exists():
        raise ValueError("ONE_SHOT_LOCAL_PREVENTION_OBSERVATION")
    path = sorted((CHECKPOINT / "causal-attempts/all-m2").glob("run-*.json"))[-1]
    proof = load_json(path)
    if (
        proof["exitCode"] != 0
        or not proof["sourceUnchanged"]
        or proof["sourceFingerprint"] != scope_fingerprint(ROOT)
        or any(fact["refused"] for fact in proof["streams"].values())
    ):
        raise ValueError("COMPLETE_SAFE_CURRENT_M2_CONTROLS_REQUIRED")
    output = ""
    for fact in proof["streams"].values():
        raw = (ROOT / fact["path"]).read_bytes()
        if len(raw) != fact["bytes"] or hashlib.sha256(raw).hexdigest() != fact["sha256"]:
            raise ValueError("ORIGINAL_CURRENT_M2_BYTES_REQUIRED")
        text = raw.decode("utf-8", errors="strict")
        if find_secrets(text):
            raise ValueError("SAFE_CURRENT_M2_STREAM_REQUIRED")
        output += text
    rows = load_lessons(ROOT)
    rework = load_json(CHECKPOINT / "INTERNAL-ENVIRONMENT-REWORK.json")
    targets = {
        "LSN-0140": "CONTINUATION-002",
        "LSN-0151": "HISTORY-TRANSPORT-002",
        "LSN-0154": "SELF-SNAPSHOT-GROWTH-001",
    }
    for identifier, finding in targets.items():
        lesson = next(row for row in rows if row["lessonId"] == identifier)
        if lesson["status"] != "CONFIRMED":
            raise ValueError("OPEN_CONFIRMED_LESSON_REQUIRED")
        for control in lesson["prevention"]:
            name = control["reference"]
            if (
                name.startswith(
                    (
                        "M2HostTransportTests.",
                        "M2SelfSnapshotTests.",
                        "CorrectiveContinuationTests.",
                    )
                )
                and name not in output
            ):
                raise ValueError("EVERY_NEW_LOCAL_CONTROL_MUST_ACTUALLY_RUN")
        lesson.update(
            status="GUARDED",
            updatedAt=utc_now(),
            resolution="Actual complete current M2 positive/null/adverse controls demonstrate "
            "local automated prevention only. Full current public quality, live "
            "functional verification and ordered independent M2 remain mandatory. "
            "Original failures, severity and recurrence counters remain unchanged.",
        )
        for failure in lesson["guardrailFailures"]:
            if finding in failure["detail"] and not failure.get("resolvedIn"):
                failure["resolvedIn"] = CHECKPOINT.name
        lesson["evidence"] = list(
            dict.fromkeys(
                [
                    *lesson["evidence"],
                    "file:" + path.relative_to(ROOT).as_posix(),
                ]
            )
        )
        item = next(row for row in rework["items"] if row["id"] == finding)
        item.update(
            status="LOCAL_CORRECTION_DEMONSTRATED_WHOLE_ASSURANCE_PENDING",
            currentProof=[path.relative_to(CHECKPOINT).as_posix()],
        )
    retrospective = ROOT / ".iacode/memory/retrospectives/GATE-7-CP-0003.md"
    text = retrospective.read_text(encoding="utf-8")
    for identifier, guard_id in (
        ("LSN-0140", "GRD-0142"),
        ("LSN-0151", "GRD-0154"),
        ("LSN-0154", "GRD-0157"),
    ):
        lesson = next(row for row in rows if row["lessonId"] == identifier)
        label = "New" if identifier == "LSN-0154" else "Recurrence" + str(lesson["recurrenceCount"])
        old = identifier + " / " + guard_id + " | " + label + ", CONFIRMED"
        if text.count(old) != 1:
            raise ValueError("EXACT_CURRENT_RETROSPECTIVE_STATUS_REQUIRED")
        text = text.replace(old, old.replace("CONFIRMED", "local GUARDED"), 1)
    text = text.replace(
        "GRD-0157 is prepared; current complete controls must run before local\nGUARDED status.",
        "GRD-0157 now has actual complete current positive/null/adverse controls; local\n"
        "GUARDED status does not grant whole immutable or independent acceptance.",
    )
    save(rows)
    retrospective.write_text(text, encoding="utf-8", newline="\n")
    write_json(CHECKPOINT / "INTERNAL-ENVIRONMENT-REWORK.json", rework)
    write_json(
        destination,
        {
            "observedAt": utc_now(),
            "result": "LOCAL_AUTOMATED_PREVENTION_NOT_WHOLE_ACCEPTANCE",
            "proofSourceFingerprint": proof["sourceFingerprint"],
            "nextSourceFingerprint": scope_fingerprint(ROOT),
            "evidence": [path.relative_to(CHECKPOINT).as_posix()],
            "lessons": list(targets),
            "wholeAssuranceMustBeRepeated": True,
            "independentVerdictGranted": False,
        },
    )
    print("ACTUAL_LOCAL_GUARDS_RESTORED_FRESH_WHOLE_ASSURANCE_STILL_REQUIRED")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("prepare", "close-local"))
    options = parser.parse_args()
    raise SystemExit(prepare() if options.action == "prepare" else close_local())
