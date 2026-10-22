"""Bind measured bridge progress, without granting completeness or audit acceptance."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(
    0, str(Path(__file__).resolve().parents[1].parents[2] / "scripts/development-ledger")
)
from ledger_common import load_json, write_json
from sync_in_progress_metadata import synchronize

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]


def main():
    proof = "environment-attempts/canonical-bridge/run-0001/RECEIPT.json"
    observed = load_json(CHECKPOINT / proof)
    if observed["result"] != "PASS" or not observed["privateSourceRemoved"]:
        raise ValueError("Actual complete canonical capability proof required")
    closure = load_json(CHECKPOINT / "CLOSURE-REQUIREMENTS.json")
    references = {
        "canonical:GATE-7#7.3",
        "canonical:GATE-7#7.5",
        "canonical:GATE-7#8.6",
        "lesson:LSN-0142",
        "lesson:LSN-0143",
    }
    found = set()
    for row in closure["requirements"]:
        if row["sourceRef"] in references:
            found.add(row["sourceRef"])
            row.update(
                implementationStatus="PARTIAL",
                finalStatus="PARTIAL",
                implementationEvidence=[
                    "file:scripts/development-ledger/audit_runner_bridge.py",
                    "file:docs/checkpoints/GATE-7-CP-0003/audit-harness/owned_docker_scope.py",
                ],
                testEvidence=[
                    "file:docs/checkpoints/GATE-7-CP-0003/" + proof,
                    "file:docs/checkpoints/GATE-7-CP-0003/causal-attempts/bridge/run-0002.json",
                ],
                negativeTestEvidence=[
                    (
                        "file:docs/checkpoints/GATE-7-CP-0003/causal-attempts/owned-c"
                        "leanup/run-0001.json"
                    )
                ],
                documentationEvidence=[
                    "file:docs/adr/ADR-0062-isolated-audit-uses-closed-host-validation-jobs.md"
                ],
                justification=(
                    "Actual restricted canonical build/run/bind succeeds; current"
                    " lint, full assurance and final owned-resource absence remai"
                    "n pending."
                ),
            )
    if found != references:
        raise ValueError("Do not omit a canonical obligation")
    write_json(CHECKPOINT / "CLOSURE-REQUIREMENTS.json", closure)
    quality = load_json(CHECKPOINT / "QUALITY.json")
    quality["checks"]["lint"].update(
        status="NOT_EXECUTED",
        evidence=[],
        justification=(
            "Earlier complete lint was before the bridge/harness changes;"
            " rerun current complete gate."
        ),
    )
    quality["checks"]["staticAnalysis"].update(
        status="PASS",
        evidence=["file:quality-attempts/staticAnalysis/run-0002.json"],
        justification="Current complete canonical compile gate; not integral readiness.",
    )
    write_json(CHECKPOINT / "QUALITY.json", quality)
    state = load_json(CHECKPOINT / "STATE.json")
    state["nextAllowedAction"] = (
        "Finish full internal assurance and exact owned-resource clea"
        "nup; seal only on truthful readiness, then start a fresh iso"
        "lated M2 auditor. No Gate8."
    )
    write_json(CHECKPOINT / "STATE.json", state)
    synchronize(ROOT, CHECKPOINT)
    print("BRIDGE_PROGRESS_RECORDED_WITHOUT_CLOSURE")
    return 0


if __name__ == "__main__":
    from ledger_common import use_utf8_stdout

    use_utf8_stdout()
    raise SystemExit(main())
