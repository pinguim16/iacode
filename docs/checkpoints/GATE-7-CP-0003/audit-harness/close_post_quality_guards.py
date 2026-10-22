"""Restore measured local prevention only; complete immutable assurance stays mandatory."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "scripts/development-ledger"))
from audit_runner_bridge import regular
from derive_requirements import render_closure
from ledger_common import load_json, scope_fingerprint, utc_now, write_json
from lesson_preflight import render_markdown
from lessons import build_preflight, load_lessons, render_index, save_lessons
from publish_progress import require_current_authored_quality, require_current_lint

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]
TARGETS = {
    "LSN-0035": (
        "ROOT-CODEPAGE-001",
        "GRD-0037",
        [
            "PublicationCallerTests."
            "test_unchanged_whole_tree_codepage_guard_covers_current_m2_sources",
            "PublicationProofDecisionTests."
            "test_actual_git_capture_states_decoder_and_preserves_unicode",
        ],
    ),
    "LSN-0151": (
        "HISTORY-TRANSPORT-001",
        "GRD-0154",
        [
            "M2HistoryTransportTests."
            "test_real_short_null_and_long_materialization_preserve_config_and_refusal",
            "M2HistoryTransportTests."
            "test_genuine_bad_subject_remains_refused_without_configuration_effects",
            "M2HistoryTransportTests."
            "test_legacy_git_read_gets_exact_bytes_only_with_child_runtime_override",
            "M2HistoryTransportTests."
            "test_child_runtime_configuration_preserves_existing_pairs_and_refuses_malformed_input",
        ],
    ),
}


def current_proof(folder, fingerprint):
    path = sorted((CHECKPOINT / folder).glob("run-*.json"))[-1]
    regular(path, CHECKPOINT)
    value = load_json(path)
    if (
        value["sourceFingerprint"] != fingerprint
        or value["sourceUnchanged"] is not True
        or type(value["exitCode"]) is not int
        or value["exitCode"] != 0
        or any(row["refused"] for row in value["streams"].values())
    ):
        raise ValueError("Actual safe current local proof required: " + folder)
    for fact in value["streams"].values():
        stream = ROOT / fact["path"]
        regular(stream, ROOT)
        raw = stream.read_bytes()
        if len(raw) != fact["bytes"] or hashlib.sha256(raw).hexdigest() != fact["sha256"]:
            raise ValueError("Original local proof stream identity differs: " + folder)
    if folder in {"causal-attempts/inherited-git", "causal-attempts/review-reconstruction"}:
        execution = value.get("execution")
        if (
            type(execution) is not dict
            or execution["producer"]["status"] != "COMPLETED"
            or type(execution["producer"]["exitCode"]) is not int
            or execution["producer"]["exitCode"] != 0
            or execution["cleanup"]["result"] != "PASS"
        ):
            raise ValueError("Primary success never replaces owned native cleanup: " + folder)
    return path.relative_to(CHECKPOINT).as_posix()


def historical_proofs(fingerprint):
    latest = {}
    for path in sorted((CHECKPOINT / "history-diagnostics").glob("run-*/RECEIPT.json")):
        receipt = load_json(path)
        latest[receipt["checkpoint"]] = (path, receipt)
    expected = {"GATE-5-CP-0001", "GATE-6-CP-0001", "GATE-7-CP-0001"}
    if set(latest) != expected:
        raise ValueError("Every actual historical declaration is required")
    evidence = []
    for identifier, (path, receipt) in latest.items():
        regular(path, CHECKPOINT)
        stdout = path.with_name("stdout.log")
        regular(stdout, CHECKPOINT)
        raw = stdout.read_bytes()
        execution = receipt["execution"]
        producer = execution["producer"]
        if (
            producer["status"] != "COMPLETED"
            or type(producer["exitCode"]) is not int
            or producer["exitCode"] != 0
            or execution["cleanup"]["result"] != "PASS"
            or any(producer[name]["refusal"] for name in ("stdout", "stderr"))
            or receipt["sourceFingerprint"] != fingerprint
            or receipt["sourceUnchanged"] is not True
            or receipt["temporaryOwnerRemoved"] is not True
            or len(raw) != producer["stdout"]["bytes"]
            or hashlib.sha256(raw).hexdigest() != producer["stdout"]["sha256"]
        ):
            raise ValueError("Actual unchanged historical execution required: " + identifier)
        observed = json.loads(raw)
        rebuilt = observed["reconstruction"]
        declaration = load_json(
            ROOT / "docs/checkpoints" / identifier / "REVIEW-BUNDLE-VALIDATION.json"
        )
        if (
            rebuilt["result"] != "PASS"
            or rebuilt["byteIdentical"] is not True
            or rebuilt["subjectCommit"] != declaration["subject"]["commit"]
            or rebuilt["subjectTree"] != declaration["subject"]["tree"]
            or any(
                type(rebuilt[key]) is not int or rebuilt[key] != 0
                for key in ("cloneExitCode", "checkoutExitCode")
            )
            or len(rebuilt["producerExitCodes"]) != 2
            or any(type(code) is not int or code != 0 for code in rebuilt["producerExitCodes"])
            or rebuilt["sha256"] != [declaration["sha256"]] * 2
            or rebuilt["sizeBytes"] != [declaration["sizeBytes"]] * 2
            or rebuilt["entries"] != [declaration["entries"]] * 2
            or rebuilt["validationResults"] != ["PASS", "PASS"]
            or observed["declarationComparison"]["result"] != "PASS"
            or observed["declarationComparison"]["findings"]
        ):
            raise ValueError("Original historical declaration not reproduced: " + identifier)
        evidence.extend(
            (path.relative_to(CHECKPOINT).as_posix(), stdout.relative_to(CHECKPOINT).as_posix())
        )
    return evidence


def main():
    state = load_json(CHECKPOINT / "STATE.json")
    if state["status"] != "IN_PROGRESS" or state["blockedBy"]:
        raise ValueError("Authorized unblocked unsealed progress required")
    destination = CHECKPOINT / "POST-QUALITY-LOCAL-RESTORATION.json"
    if destination.exists():
        raise ValueError("Do not rewrite a local restoration observation")
    fingerprint = scope_fingerprint(ROOT)
    lint, authored = require_current_lint(), require_current_authored_quality()
    proofs = [
        current_proof(folder, fingerprint)
        for folder in (
            "causal-attempts/all-m2",
            "causal-attempts/inherited-streams",
            "causal-attempts/history-transport",
            "causal-attempts/inherited-git",
            "causal-attempts/review-reconstruction",
            "quality-attempts/checkpointValidation",
        )
    ]
    evidence = [lint["receipt"], authored["receipt"], *proofs, *historical_proofs(fingerprint)]
    lessons = load_lessons(ROOT)
    registry_path = ROOT / ".iacode/memory/guardrails/registry.json"
    registry = load_json(registry_path)
    rework = load_json(CHECKPOINT / "INTERNAL-ENVIRONMENT-REWORK.json")
    closure = load_json(CHECKPOINT / "CLOSURE-REQUIREMENTS.json")
    retrospective = ROOT / ".iacode/memory/retrospectives/GATE-7-CP-0003.md"
    text = retrospective.read_text(encoding="utf-8")
    changes = []
    for identifier, (finding, guard_id, tests) in TARGETS.items():
        lesson = next(row for row in lessons if row["lessonId"] == identifier)
        failures = [
            row
            for row in lesson["guardrailFailures"]
            if row["checkpoint"] == CHECKPOINT.name
            and finding in row["detail"]
            and not row.get("resolvedIn")
        ]
        item = next(row for row in rework["items"] if row["id"] == finding)
        guard = next(row for row in registry["guardrails"] if row["guardrailId"] == guard_id)
        row = next(
            row for row in closure["requirements"] if row["sourceRef"] == "lesson:" + identifier
        )
        old = f"{identifier} / {guard_id} | Recurrence{lesson['recurrenceCount']}, CONFIRMED"
        if (
            lesson["status"] != "CONFIRMED"
            or len(failures) != 1
            or item["status"] != "OPEN"
            or text.count(old) != 1
        ):
            raise ValueError("Exact open recurrence required: " + identifier)
        changes.append((lesson, failures[0], item, guard, row, old, tests))
    # Every premise is checked before changing any file. Internal status is not independence.
    for lesson, failure, item, guard, row, old, tests in changes:
        failure["resolvedIn"] = CHECKPOINT.name
        lesson.update(
            status="GUARDED",
            updatedAt=utc_now(),
            resolution=(
                "Post-quality local prevention is restored only after actual current "
                "positive/adverse "
                "controls, original historical declarations, full lint, authored read-only quality "
                "and quiescent checkpoint validation. Original failures, counters and "
                "severity remain. "
                "Fresh source-epoch whole quality/functional/internal assurance and independent M2 "
                "validation remain mandatory."
            ),
        )
        for reference in tests:
            if not any(entry["reference"] == reference for entry in lesson["prevention"]):
                lesson["prevention"].append(
                    {
                        "kind": "test",
                        "reference": reference,
                        "description": (
                            "Actual current boundary/null/refusal control; "
                            "not independent acceptance."
                        ),
                    }
                )
        references = [
            "file:" + (CHECKPOINT / name).relative_to(ROOT).as_posix() for name in evidence
        ]
        lesson["evidence"] = list(dict.fromkeys([*lesson["evidence"], *references]))
        guard["verifiedBy"] = list(dict.fromkeys([*guard["verifiedBy"], *tests]))
        item.update(
            status="LOCAL_CORRECTION_DEMONSTRATED_WHOLE_ASSURANCE_PENDING", currentProof=evidence
        )
        row.update(
            implementationStatus="PARTIAL",
            finalStatus="PARTIAL",
            justification=(
                "Local prevention demonstrated; complete current immutable assurance pending."
            ),
        )
        for field in ("testEvidence", "validationEvidence"):
            row[field] = list(dict.fromkeys([*row[field], *references]))
        row["guardrailEvidence"] = list(
            dict.fromkeys(
                [
                    *row["guardrailEvidence"],
                    *("test:" + reference for reference in tests),
                ]
            )
        )
        row["documentationEvidence"] = list(
            dict.fromkeys(
                [
                    *row["documentationEvidence"],
                    "file:.iacode/memory/retrospectives/GATE-7-CP-0003.md",
                ]
            )
        )
        text = text.replace(old, old.replace("CONFIRMED", "local GUARDED"), 1)
    text = text.replace(
        "its new local restoration is\nnot yet granted.",
        "its new local restoration is\nmeasured, while whole assurance remains due.",
    )
    write_json(registry_path, registry)
    save_lessons(ROOT, lessons)
    (ROOT / ".iacode/memory/LESSONS.md").write_text(
        render_index(lessons), encoding="utf-8", newline="\n"
    )
    retrospective.write_text(text, encoding="utf-8", newline="\n")
    write_json(CHECKPOINT / "INTERNAL-ENVIRONMENT-REWORK.json", rework)
    write_json(CHECKPOINT / "CLOSURE-REQUIREMENTS.json", closure)
    (CHECKPOINT / "CLOSURE-REQUIREMENTS.md").write_text(
        render_closure(closure), encoding="utf-8", newline="\n"
    )
    prior = load_json(CHECKPOINT / "LESSON-PREFLIGHT.json")
    preflight = build_preflight(
        ROOT, prior["gate"], prior["scope"], prior["technologies"], prior["modules"]
    )
    write_json(CHECKPOINT / "LESSON-PREFLIGHT.json", preflight)
    (CHECKPOINT / "LESSON-PREFLIGHT.md").write_text(
        render_markdown(preflight), encoding="utf-8", newline="\n"
    )
    write_json(
        destination,
        {
            "observedAt": utc_now(),
            "result": "LOCAL_GUARDS_RESTORED_NOT_WHOLE_DELIVERY",
            "proofSourceFingerprint": fingerprint,
            "nextSourceFingerprint": scope_fingerprint(ROOT),
            "lessons": list(TARGETS),
            "evidence": evidence,
            "independent": False,
        },
    )
    print("Post-quality local guards restored; fresh whole-current assurance remains required")
    return 0


if __name__ == "__main__":
    from ledger_common import use_utf8_stdout

    use_utf8_stdout()
    raise SystemExit(main())
