"""Bind observed local component facts; never complete findings or whole assurance."""

import sys
from pathlib import Path

sys.path.insert(
    0, str(Path(__file__).resolve().parents[1].parents[2] / "scripts/development-ledger")
)
from current_resources import current_scope_path
from delivery_assurance import evaluate_matrix
from derive_requirements import render_closure
from ledger_common import load_json, scope_fingerprint, utc_now, write_json
from lessons import load_lessons
from sync_in_progress_metadata import synchronize

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]


def main():
    fingerprint = scope_fingerprint(ROOT)
    phase = current_scope_path()
    proofs = tuple(
        sorted((CHECKPOINT / folder).glob("run-*.json"))[-1].relative_to(CHECKPOINT).as_posix()
        for folder in (
            "causal-attempts/bootstrap-ownership",
            "causal-attempts/resource-phase",
            "quality-attempts/staticAnalysis",
        )
    )
    for name in proofs:
        value = load_json(CHECKPOINT / name)
        if (
            value["exitCode"] != 0
            or not value["sourceUnchanged"]
            or value["sourceFingerprint"] != fingerprint
            or any(item["refused"] for item in value["streams"].values())
        ):
            raise ValueError("Actual safe current component proof required")
    closure = load_json(CHECKPOINT / "CLOSURE-REQUIREMENTS.json")
    row = next(
        value for value in closure["requirements"] if value["sourceRef"] == "lesson:LSN-0125"
    )
    row.update(
        implementationStatus="PARTIAL",
        finalStatus="PARTIAL",
        justification=(
            "Bootstrap recurrence is locally repaired and guarded; comple"
            "te current native/full immutable assurance remains pending."
        ),
    )
    evidence = {
        "implementationEvidence": [
            "file:docs/checkpoints/GATE-7-CP-0003/audit-harness/current_resources.py",
            "file:scripts/development-ledger/audit_runner_bridge.py",
        ],
        "testEvidence": ["file:docs/checkpoints/GATE-7-CP-0003/" + name for name in proofs[:2]],
        "negativeTestEvidence": [
            (
                "file:docs/checkpoints/GATE-7-CP-0003/causal-attempts/bootstr"
                "ap-ownership/run-0001.json"
            ),
            (
                "file:docs/checkpoints/GATE-7-CP-0003/resource-phases/phase-0"
                "002/BUILDER-BOOTSTRAP.json"
            ),
        ],
        "documentationEvidence": [
            "checkpoint:DECISIONS.md",
            "checkpoint:INTERNAL-ENVIRONMENT-REWORK.json",
        ],
        "guardrailEvidence": [
            (
                "test:BootstrapOwnershipTests.test_actual_bootstrap_caller_re"
                "quires_owned_native_process_boundary"
            ),
            (
                "test:BootstrapOwnershipTests.test_real_parent_exit_with_inhe"
                "rited_output_writer_is_observed_then_exactly_drained"
            ),
        ],
    }
    for key, values in evidence.items():
        row[key] = list(dict.fromkeys([*row[key], *values]))
    write_json(CHECKPOINT / "CLOSURE-REQUIREMENTS.json", closure)
    (CHECKPOINT / "CLOSURE-REQUIREMENTS.md").write_text(
        render_closure(closure), encoding="utf-8", newline="\n"
    )
    quality = load_json(CHECKPOINT / "QUALITY.json")
    quality["checks"]["staticAnalysis"].update(
        status="PASS",
        evidence=["file:" + proofs[2]],
        justification=(
            "Actual current canonical static-analysis component, not complete quality acceptance."
        ),
    )
    lint_path = sorted((CHECKPOINT / "quality-attempts/lint").glob("run-*.json"))[-1]
    lint = load_json(lint_path)
    if lint["sourceFingerprint"] == fingerprint:
        if (
            type(lint["exitCode"]) is int
            and lint["exitCode"] == 0
            and lint["sourceUnchanged"] is True
            and not any(row["refused"] for row in lint["streams"].values())
        ):
            from publish_progress import require_current_lint

            bound = require_current_lint()
            quality["checks"]["lint"].update(
                status="PASS",
                evidence=["file:" + bound["receipt"]],
                justification="Actual complete current canonical lint and publication binding.",
            )
        else:
            quality["checks"]["lint"].update(
                status="FAIL",
                evidence=["file:" + lint_path.relative_to(CHECKPOINT).as_posix()],
                justification="Latest actual current lint observation did not pass safely.",
            )
    else:
        quality["checks"]["lint"].update(
            status="NOT_EXECUTED",
            evidence=[],
            justification="Prior complete lint is preserved at an older assurance source epoch.",
        )
    write_json(CHECKPOINT / "QUALITY.json", quality)
    state = load_json(CHECKPOINT / "STATE.json")
    if state["status"] != "IN_PROGRESS" or state["blockedBy"]:
        raise ValueError("Only authorized unblocked corrective progress may be collected")
    report = evaluate_matrix(ROOT, CHECKPOINT, load_json(CHECKPOINT / "REQUIREMENTS-MATRIX.json"))
    state["requirementsMatrix"].update(
        total=report["totalRequirements"],
        mandatory=report["mandatoryRequirements"],
        complete=report["complete"],
        partial=report["partial"],
        missing=report["missing"],
        notApplicable=report["notApplicable"],
        coveragePercent=report["coveragePercent"],
    )
    rework = load_json(CHECKPOINT / "INTERNAL-ENVIRONMENT-REWORK.json")
    state["greenKeeper"]["unresolvedReworkItems"] = sum(
        value["status"] in {"OPEN", "LOCAL_CORRECTION_DEMONSTRATED_WHOLE_ASSURANCE_PENDING"}
        for value in rework["items"]
    )
    state["nextAllowedAction"] = (
        "Publish an exact current immutable IN_PROGRESS runtime subje"
        "ct; execute all16 canonical quality gates, full non-fast ver"
        "ifier, DCV, fresh internal Red Team/mirror and exact phase-0"
        "002 disposal; seal READY_FOR_REVIEW before a fresh independe"
        "nt M2 auditor. No Gate8, Engine/application restart or globa"
        "l/other-chat changes."
    )
    pending_guards = [
        row["lessonId"]
        for row in load_lessons(ROOT)
        if any(
            failure["checkpoint"] == CHECKPOINT.name and not failure.get("resolvedIn")
            for failure in row.get("guardrailFailures", [])
        )
    ]
    if pending_guards:
        state["nextAllowedAction"] = (
            "Finish current lint, whole authored quality, corrective controls and quiescent "
            "canonical validation before local restoration of "
            + ", ".join(pending_guards)
            + "; then refresh the source epoch and proofs before runtime-v3 publication and "
            "complete16-gate/full49-stage/DCV/Red Team/mirror/disposal/seal. No Gate8, "
            "restarts or global/other-chat changes; independent M2 remains later."
        )
    write_json(CHECKPOINT / "STATE.json", state)
    write_json(
        CHECKPOINT / "ACTIVE-VALIDATION.json",
        {
            "recordedAt": utc_now(),
            "kind": "TRANSIENT_OPERATOR_RESUME_MARKER_NOT_ACCEPTANCE",
            "sourceFingerprint": fingerprint,
            "nativeToolSessions": [],
            "pausedByOwner": False,
            "cleanup": "ORIGINAL_DISPOSED_PHASE_0002_ACTIVE_FINAL_DISPOSAL_PENDING",
            "ownedBuilderReceipt": phase.relative_to(CHECKPOINT).as_posix(),
            "independentAuditorStarted": False,
            "gate8Authorized": False,
            "warning": (
                "Never rerun any historical PID controller or disposed receip"
                "t. Preserve original failed comparisons and every failed pro"
                "ducer."
            ),
        },
    )
    synchronize(ROOT, CHECKPOINT)
    print("CURRENT_COMPONENTS_BOUND full_assurance_pending independent_M2_pending no_Gate8")
    return 0


if __name__ == "__main__":
    from ledger_common import use_utf8_stdout

    use_utf8_stdout()
    raise SystemExit(main())
