"""Keep an honest resumable marker while long local baseline producers remain active."""

from __future__ import annotations

import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))
from ledger_common import load_json, utc_now, write_json


def main():
    quality = load_json(CHECKPOINT / "QUALITY.json")
    receipt = load_json(CHECKPOINT / "quality-attempts/lint/run-0002.json")
    if receipt["exitCode"] == 0:
        raise ValueError("This marker requires the actual retained failed export")
    quality["checks"]["lint"].update(status="FAIL", evidence=["file:quality-attempts/lint/run-0002.json"],
                                   justification="Actual complete runner failed OCI transfer after compilation; unchanged full retry active, not accepted.")
    quality["checks"]["staticAnalysis"].update(status="NOT_EXECUTED", evidence=[],
                                             justification="Previous compile receipt predates the new assurance-scoped adapter; current canonical rerun remains due.")
    write_json(CHECKPOINT / "QUALITY.json", quality)
    state = load_json(CHECKPOINT / "STATE.json")
    state["status"] = "IN_PROGRESS"
    state["updatedAt"] = utc_now()
    state["nextAllowedAction"] = (
        "Wait for actual active root baseline and lint-retry exits; preserve their safe output. "
        "Repair BRIDGE-PATH-001 with actual causal controls, finish current internal assurance, "
        "observe exact owned cleanup and seal before any fresh independent M2 auditor. No Gate8."
    )
    write_json(CHECKPOINT / "STATE.json", state)
    write_json(CHECKPOINT / "ACTIVE-VALIDATION.json", {
        "recordedAt": utc_now(), "kind": "TRANSIENT_OPERATOR_RESUME_MARKER_NOT_ACCEPTANCE",
        "sourceFingerprint": "55abd94c325193a81fe5a60348a0765498457a80d81732d4ab4dad2efd04ae5e",
        "nativeToolSessions": [
            {"id": 45796, "purpose": "Complete root baseline through run_causal.py --gate tests", "lastObservedStatus": "RUNNING"},
            {"id": 61756, "purpose": "Unchanged complete lint retry through run_causal.py --gate lint", "lastObservedStatus": "RUNNING"}
        ],
        "warning": "Session IDs are transient and are not durable success evidence. Read actual tool completion and canonical receipts before any dependent step.",
        "openInternalItems": "INTERNAL-ENVIRONMENT-REWORK.json",
        "ownedBuilderReceipt": "OWNED-DOCKER-SCOPE.json", "cleanup": "PENDING_WHILE_TESTS_ACTIVE",
        "independentAuditorStarted": False, "gate8Authorized": False
    })
    print("ACTIVE_VALIDATION_RECORDED_WITHOUT_READINESS")
    return 0


if __name__ == "__main__":
    from ledger_common import use_utf8_stdout
    use_utf8_stdout()
    raise SystemExit(main())
