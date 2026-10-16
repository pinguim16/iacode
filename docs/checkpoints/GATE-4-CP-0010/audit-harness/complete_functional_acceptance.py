#!/usr/bin/env python3
"""Bind every canonical functional requirement to one complete current published execution."""

from __future__ import annotations

import json
import sys
from copy import deepcopy
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))
sys.path.insert(0, str(ROOT / "scripts/iacode"))

from check_functional_acceptance import functional_requirement_ids
from ledger_common import LedgerError, load_json, scope_fingerprint, utc_now, write_json
from verify import build_stages

STAGES = {
    "SANDBOX": ["sandbox-integration", "sandbox-coding", "sandbox-timeout",
                "sandbox-cancellation", "sandbox-recovery", "sandbox-tool-result-origin"],
    "REPRODUCTION": ["quality-reproduction"],
    "DURABILITY": ["quality-recovery", "quality-cancellation", "quality-timeout"],
    "VERDICTS": ["quality-pass", "quality-fail", "quality-iacode"],
    "FALSE-PASS": ["quality-false-pass"],
    "OUTPUT": ["gate:apiTests", "gate:sandboxTests", "quality-false-pass"],
}


def main() -> int:
    verification = load_json(CHECKPOINT / "VERIFY.json")
    publication = load_json(CHECKPOINT / "PUBLISHED-CLEAN-CLONE-REPORT.json")
    functional = load_json(CHECKPOINT / "FUNCTIONAL-SCENARIOS.json")
    subject = publication["publishedCommit"]
    live_state = load_json(CHECKPOINT / "PROGRAM-STATE-LIVE-VALIDATION.json")
    if (live_state.get("result") != "PASS" or live_state.get("subjectCommit") != subject
            or live_state.get("sourceFingerprint") != scope_fingerprint(ROOT)):
        raise LedgerError("functional closure cannot mix published subjects or later unverified source")
    expected_stages = [stage.name for stage in build_stages(False)]
    observed_stages = [stage["name"] for stage in verification["stages"]]
    if (publication.get("result") != "PASS" or verification.get("result") != "PASS"
            or verification.get("fast") is not False or observed_stages != expected_stages
            or publication.get("invocationCount") != 1 or publication.get("retryCount") != 0
            or functional.get("subjectCommit") != subject
            or not all(stage.get("result") == "PASS" for stage in verification["stages"])
            or subject == "33c3f42c0d5faf112c3e037a55006dd750c4bfe1"):
        raise LedgerError("functional closure requires the complete corrected immutable subject")
    commands = [json.loads(line) for line in (CHECKPOINT / "COMMANDS.jsonl").read_text(
        encoding="utf-8").splitlines() if line.strip()]
    matches = [row for row in commands if row.get("exitCode") == 0
               and row.get("subjectCommit") == subject
               and "audit-harness/run_full_verification.py" in row.get("command", "")]
    if len(matches) != 1:
        raise LedgerError("one successful command must bind the complete published execution")
    command_id = matches[0]["id"]
    proof = functional["scenarios"].get("quality-secret-output.json")
    if not proof or proof.get("result") != "PASS":
        raise LedgerError("the full verifier did not execute passing output containment")
    proof_steps = {step["step"]: step for scenario in proof["scenarios"]
                   for step in scenario["steps"]}
    needed = {"control.accepted", "control.after_refusal_pass"} | {
        f"{fixture}.{check}" for fixture in ("python-secret-output", "python-secret-output-full")
        for check in ("history_clean", "no_sandbox_artifact", "causal_containment_refusal")
    }
    if any(name not in proof_steps or proof_steps[name].get("result") != "PASS" for name in needed):
        raise LedgerError("clean controls and both causal output boundaries must be observed")
    baseline = load_json(ROOT / "docs/checkpoints/GATE-4-CP-0009/FUNCTIONAL-ACCEPTANCE.json")
    rows = deepcopy(baseline["scenarios"])
    output = deepcopy(rows[-1])
    output.update({
        "scenarioId": "G4-FA-CP0010-OUTPUT", "requirementIds": ["GATE-4-19.2"],
        "feature": "Output containment before durable delivery",
        "scenario": "Reject nested JSON in mixed logs and full streams before history or object writes.",
        "expected": ["Both adverse runs derive FAIL with explicit containment refusals, no prohibited "
                     "history bytes or sandbox objects, and clean runs before and after derive PASS."],
    })
    rows.append(output)
    stages = {stage["name"]: stage for stage in verification["stages"]}
    now = utc_now()
    for row in rows:
        row["scenarioId"] = row["scenarioId"].replace("CP0009", "CP0010")
        suffix = row["scenarioId"].removeprefix("G4-FA-CP0010-")
        row["preconditions"] = [f"One complete non-fast execution of published subject {subject}."]
        row["execution"] = [f"Execute canonical stage {name}." for name in STAGES[suffix]]
        row["observed"] = [f"{name}: PASS in {stages[name]['durationSeconds']} seconds."
                           for name in STAGES[suffix]]
        if suffix == "OUTPUT":
            row["observed"] += [f"{name}: {json.dumps(proof_steps[name]['observed'], sort_keys=True)}"
                                for name in sorted(needed)]
        row["result"] = "PASS"
        row["evidence"] = ["checkpoint:VERIFY.json", "checkpoint:FUNCTIONAL-SCENARIOS.json",
                           "checkpoint:PUBLISHED-CLEAN-CLONE-REPORT.json", command_id]
        row["artifactReferences"] = row["evidence"][:-1]
        row["timestamp"] = now
    required = set(functional_requirement_ids(ROOT, "GATE-4"))
    if {item for row in rows for item in row["requirementIds"]} != required:
        raise LedgerError("functional scenarios must cover exactly the current canonical set")
    write_json(CHECKPOINT / "FUNCTIONAL-ACCEPTANCE.json", {
        "schemaVersion": "1.0.0", "gate": "GATE-4", "checkpoint": CHECKPOINT.name,
        "status": "PASS", "generatedAt": now, "scenarios": rows,
    })
    print(f"FUNCTIONAL_EVIDENCE_BOUND requirements={len(required)} scenarios={len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
