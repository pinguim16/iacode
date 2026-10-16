"""Bind authored Gate 5 scenarios only to complete immutable executed observations."""

from __future__ import annotations

import json
import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))
sys.path.insert(0, str(ROOT / "scripts/iacode"))

from check_functional_acceptance import functional_requirement_ids
from ledger_common import LedgerError, load_json, scope_fingerprint, utc_now, write_json
from verify import build_stages

# Explicit semantic mappings; this is not an automatic promotion of all discovered rows.
SCENARIOS = {
    "SECURITY": {
        "requirements": ["1.5", "2.1", "3.3", "8.2"],
        "feature": "Authenticated closed desktop boundary",
        "expected": "Unauthorized, secret-bearing, forged tool-result and verdict/host-command IPC are refused before effects, alongside the real clean task.",
        "steps": ["unauthenticated-domain-refused-before-effects", "closed-ipc-refuses-tool-result",
                  "closed-ipc-refuses-quality-verdict", "closed-ipc-refuses-shell.exec",
                  "secret-upload-refused-before-sql-or-object-persistence",
                  "redis-replay-refusal-survives-api-restart",
                  "authenticated-external-sandbox-result-forgery-refused"],
    },
    "SNAPSHOT": {
        "requirements": ["3.1", "3.4", "4.2"],
        "feature": "Exact informed input consent and immutable persistence",
        "expected": "Default cancellation and wrong consent send no upload; exact native approval stores stable rights-bound bytes; actual object tampering cannot create a task.",
        "steps": ["cli-preview-is-bounded-and-excludes-private-path",
                  "cli-changed-or-wrong-consent-refused-locally",
                  "real-snapshot-persistence-stable-retry-and-rights",
                  "read-only-snapshot-reconciliation",
                  "actual-native-snapshot-and-uncertain-accepted-create",
                  "actual-object-tamper-refused-before-task-persistence"],
    },
    "TASK": {
        "requirements": ["4.1", "4.4", "4.7", "5.2", "8.1"],
        "feature": "Real provider task, sandbox unittest and ordered shared truth",
        "expected": "Fresh installed clients expose the same real task; the provider successfully executes unittest only in the owned sandbox, ordered events and derived quality evidence are observable without host-source changes.",
        "steps": ["fresh-offline-cli-install-and-authenticated-contract",
                  "actual-new-host-secretstorage-recovery-provider-sandbox-quality",
                  "both-clients-observe-identical-server-task-truth",
                  "host-source-and-sentinel-unchanged"],
    },
    "RECOVERY": {
        "requirements": ["2.6", "6.4", "8.3"],
        "feature": "Uncertain outcome reconciliation across actual host restart",
        "expected": "Loss of an already accepted response retains the stable identity, produces one persisted task/quality run and recovers server truth read-only in a second native process without replay.",
        "steps": ["actual-native-snapshot-and-uncertain-accepted-create",
                  "lost-response-has-one-real-persisted-run",
                  "actual-new-host-secretstorage-recovery-provider-sandbox-quality",
                  "actual-quality-response-loss-reconciles-once-without-replay"],
    },
    "QUALITY": {
        "requirements": ["4.6"],
        "feature": "Derived immutable quality and actual reproduction",
        "expected": "Both clients expose the same server-derived verdict/checks/evidence; installed CLI reproduces real inputs and reconciled quality reaches PASS with real evidence, never a client-selected denominator.",
        "steps": ["both-clients-observe-identical-derived-verdict-and-evidence",
                  "installed-cli-reproduces-real-quality-inputs",
                  "reconciled-quality-completes-with-real-pass-evidence"],
    },
    "CANCELLATION": {
        "requirements": ["4.5"],
        "feature": "Requested versus completed cancellation and local-only SIGINT",
        "expected": "RUNNING task/quality cancellation waits for terminal truth and every canonical active sandbox state to clear; repeat remains safe. Local SIGINT returns 130/cursor without remotely cancelling quality.",
        "steps": ["installed-cli-running-task-cancel-request-terminal-and-repeat",
                  "actual-cli-sigint-stops-only-local-observation",
                  "installed-cli-running-quality-cancel-waits-for-cleanup"],
    },
    "INSTALLATION": {
        "requirements": ["3.5", "6.1", "6.2"],
        "feature": "Actual fresh native installation and workspace trust",
        "expected": "The production VSIX activates all nineteen commands in actual fresh persistent owned Code hosts; untrusted workspaces refuse every mutation before connecting, and native consent/status/quality operate through real editor APIs.",
        "steps": ["actual-native-snapshot-and-uncertain-accepted-create",
                  "actual-new-host-secretstorage-recovery-provider-sandbox-quality"],
    },
    "ISOLATION": {
        "requirements": ["8.4", "8.5"],
        "feature": "Immutable measured subject and exact owned cleanup",
        "expected": "The full non-fast execution measures the published unchanged subject. Operational identities and host source/sentinel remain unchanged; every owned profile, container, volume and sandbox network is actually removed.",
        "steps": ["host-source-and-sentinel-unchanged", "operational-container-identities-preserved",
                  "owned-services-volumes-profiles-removed",
                  "owned-sandbox-children-and-networks-removed", "measured-source-inputs-unchanged"],
    },
}


def main() -> int:
    destination = CHECKPOINT / "FUNCTIONAL-ACCEPTANCE.json"
    if destination.exists():
        raise LedgerError("preserve the earlier functional assembly before another attempt")
    verification = load_json(CHECKPOINT / "VERIFY.json")
    publication = load_json(CHECKPOINT / "PUBLISHED-CLEAN-CLONE-REPORT.json")
    functional = load_json(CHECKPOINT / "FUNCTIONAL-SCENARIOS.json")
    subject = publication["publishedCommit"]
    desktop = functional["scenarios"]["desktop-e2e.json"]
    native = functional["scenarios"]["native-editor-package.json"]
    expected_stages = [stage.name for stage in build_stages(False)]
    if (verification.get("result") != "PASS" or verification.get("fast") is not False
            or publication.get("result") != "PASS" or publication.get("invocationCount") != 1
            or publication.get("retryCount") != 0
            or [row["name"] for row in verification["stages"]] != expected_stages
            or any(row["result"] != "PASS" for row in verification["stages"])
            or functional.get("subjectCommit") != subject or desktop.get("subjectCommit") != subject
            or desktop.get("sourceDirty") is not False
            or desktop.get("sourceFingerprint") != scope_fingerprint(ROOT)
            or desktop.get("result") != "PASS" or native.get("result") != "PASS"):
        raise LedgerError("the complete immutable current source must pass every real stage")
    if (not desktop.get("ownedTemporaryDirectoryRemoved") or not native.get("ownedTemporaryDirectoryRemoved")
            or desktop.get("taskCancellation", {}).get("phase") != "COMPLETE"
            or desktop.get("proxyOperationCounts", {}).get("start") != 1):
        raise LedgerError("real recovery, terminal cancellation and cleanup facts are incomplete")
    resume = desktop["nativeResume"]
    executed = next((row for row in resume["steps"]
                     if row["name"] == "actual-provider-task-sandbox-result-and-ordered-events"), {})
    if (not executed.get("successfulUnittestExecution") or executed.get("modelCalls", 0) < 1
            or executed.get("sandboxExecutions", 0) < 1):
        raise LedgerError("real successful sandbox unittest execution is required")
    untrusted = [row for run in native["runs"] for row in run["steps"]
                 if row["name"] == "actual-untrusted-workspace-refuses-every-mutation-before-connection"]
    if len(untrusted) != 1 or untrusted[0]["result"] != "PASS":
        raise LedgerError("actual untrusted host mutation refusal is required")
    steps = {row["name"]: row for row in desktop["steps"]}
    required = set(functional_requirement_ids(ROOT, "GATE-5"))
    mapped = {"GATE-5-" + key for group in SCENARIOS.values() for key in group["requirements"]}
    if mapped != required:
        raise LedgerError(f"authored functional mapping differs from canonical set: {mapped ^ required}")
    commands = [json.loads(line) for line in (CHECKPOINT / "COMMANDS.jsonl").read_text(
        encoding="utf-8").splitlines() if line.strip()]
    matches = [row for row in commands if row.get("exitCode") == 0
               and row.get("subjectCommit") == subject
               and "audit-harness/run_full_verification.py" in row.get("command", "")]
    if len(matches) != 1:
        raise LedgerError("one successful ledger command must bind the complete published execution")
    now = utc_now()
    rows = []
    for name, group in SCENARIOS.items():
        if any(steps.get(step, {}).get("result") != "PASS" for step in group["steps"]):
            raise LedgerError("missing actual accepted premise for scenario " + name)
        rows.append({
            "scenarioId": "G5-FA-" + name,
            "requirementIds": ["GATE-5-" + key for key in group["requirements"]],
            "feature": group["feature"], "scenario": group["expected"],
            "environment": desktop["environment"],
            "preconditions": ["Exact published detached subject " + subject,
                              "Fresh isolated real runtime/clients; configured authorized model unchanged."],
            "execution": [matches[0]["command"], "Actual observations: " + ", ".join(group["steps"])],
            "expected": [group["expected"]],
            "observed": [step + ": " + steps[step]["result"] for step in group["steps"]],
            "result": "PASS", "evidence": [matches[0]["id"], "checkpoint:VERIFY.json",
                "checkpoint:FUNCTIONAL-SCENARIOS.json", "checkpoint:PUBLISHED-CLEAN-CLONE-REPORT.json"],
            "timestamp": now, "artifactReferences": ["quality-run:" + resume["qualityRunId"]],
        })
    write_json(destination, {"schemaVersion": "1.0.0", "gate": "GATE-5",
        "checkpoint": CHECKPOINT.name, "status": "PASS", "generatedAt": now, "scenarios": rows})
    print(f"FUNCTIONAL_ASSEMBLY=PASS scenarios={len(rows)} requirements={len(required)} subject={subject}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
