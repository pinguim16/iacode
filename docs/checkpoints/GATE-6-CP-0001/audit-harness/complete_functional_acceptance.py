"""Bind all canonical runtime criteria to a single complete immutable actual execution."""

from __future__ import annotations

import json
import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))
sys.path.insert(0, str(ROOT / "scripts/iacode"))

from check_functional_acceptance import functional_requirement_ids
from ledger_common import LedgerError, load_json, scope_fingerprint, utc_now, write_json
from verify import build_stages

# Reviewed semantic groups, not a discovered-list promotion. Whole API integration and domain
# suites in the same full verifier additionally prove strict JSON, migrations, rollback,
# immutability, legacy quarantine, limits and lifecycle; live controls cannot replace those tests.
SCENARIOS = {
    "CONTRACT": {
        "requirements": "2.1 2.2 2.3 2.4 3.5 3.6",
        "feature": "Closed bounded observations and pre-effect privacy",
        "expected": "Strict contracts and actual signed HTTP refuse ambiguous JSON, forged/private facts and complete declared credential forms before durable effects; actual public source identities remain usable.",
        "steps": ["actual-source-bound-experience-captured", "consumer-recomputed-returned-document-digest",
                  "observed-provider-tool-quality-and-denied-reuse-lineage",
                  "private-transcript-refused-before-persistence", "secret-ingress-refused-before-persistence",
                  *[f"known-capability-form-{i}-refused-before-persistence" for i in range(6)]],
    },
    "SOURCES": {
        "requirements": "2.5 2.6",
        "feature": "Actual governed task and verified immutable quality lineage",
        "expected": "A real completed task and derived quality evidence supply facts; source mismatch, caller verdicts and corrupt/unavailable objects cannot become valid experiences.",
        "steps": ["actual-provider-sandbox-task-completed", "actual-derived-quality-pass-with-evidence",
                  "cross-project-source-capture-refused", "forged-verdict-refused-before-persistence",
                  "actual-source-object-corrupt-fails-closed", "actual-source-object-remove-fails-closed"],
    },
    "RIGHTS": {
        "requirements": "3.1 3.2 3.3 3.4 3.7",
        "feature": "Exact storage consent and restrictive source-bound rights",
        "expected": "Missing/false/nonboolean consent and forged rights cause no capture. Persisted/exported provenance is content-bound and all unproven reuse requests disclose no document.",
        "steps": ["consent-missing-refused-before-persistence", "consent-denied-refused-before-persistence",
                  "consent-type-refused-before-persistence", "forged-rights-refused-before-persistence",
                  "observed-provider-tool-quality-and-denied-reuse-lineage", "actual-verified-export",
                  *[f"denied-{use}-use-no-data" for use in ("rag", "training", "distillation", "unknown")]],
    },
    "PERSISTENCE": {
        "requirements": "4.1 4.2 4.3 4.4 5.3",
        "feature": "Real existing-table migration, immutable atomic persisted capture",
        "expected": "The complete actual migration/autogenerate and integration suites preserve legacy identity/rights, enforce immutable facts and atomic audit rollback. Live API read/list/export returns exact durable content/digests.",
        "steps": ["actual-source-bound-experience-captured", "actual-verified-read", "actual-verified-export",
                  "consumer-recomputed-returned-document-digest", "actual-concurrent-retry-one-row-one-capture-audit"],
    },
    "RETRY-RECOVERY": {
        "requirements": "4.5 4.6 6.5",
        "feature": "Accepted-response loss, concurrent retry, restart and source recovery",
        "expected": "A real accepted but lost response and concurrent retries create exactly one fact/audit, preserve original expiry across restart and refuse conflicts/resurrection. Corrupt/missing actual objects fail closed and restored originals recover.",
        "steps": ["actual-accepted-experience-response-loss-one-durable-effect",
                  "actual-concurrent-retry-one-row-one-capture-audit", "conflicting-stable-request-refused",
                  "restart-preserves-content-rights-original-expiry-and-retry",
                  "actual-source-object-corrupt-fails-closed", "actual-source-object-remove-fails-closed",
                  "restored-source-clean-control-after-corrupt", "restored-source-clean-control-after-remove",
                  "new-key-cannot-resurrect-withdrawn-source", "expired-source-new-key-cannot-resurrect"],
    },
    "ACCESS": {
        "requirements": "5.1 5.2 5.4 5.5 5.6",
        "feature": "Actual finite authenticated scoped transport and bounded diagnostics",
        "expected": "Actual absent/invalid/stale/expired/replayed authorization and project/cursor mismatch fail closed. Bounded pagination and production logging preserve observability without rejected content. Every inherited client/native/runtime regression remains mandatory.",
        "steps": ["unauthenticated-capture-refused-before-effects", "invalid-signature-refused",
                  "stale-authentication-refused", "authentication-null-control",
                  "actual-redis-authentication-replay-refused", "authentication-replay-survives-real-restart",
                  "actual-expired-capability-refuses-experience-access", "cross-project-get-refused",
                  "cross-project-delete-refused", "cross-project-cursor-refused",
                  "actual-bounded-summary-pagination", "actual-project-cursor-resumption",
                  "actual-production-logs-retain-observability-not-ingress"],
    },
    "RETENTION": {
        "requirements": "6.1 6.2 6.3 6.4 6.6",
        "feature": "Finite consumed policy, immediate denial and owned automatic physical purge",
        "expected": "Actual domain/SQL/lifecycle tests prove limits, batches, finite tombstones and owned shutdown. Live withdrawal/expiry deny immediately; the automatic sweeper physically clears primary content, stable retries cannot renew and original sources remain unchanged.",
        "steps": ["actual-project-bound-withdrawal", "repeated-withdrawal-is-terminal-observation",
                  "withdrawn-read-denied-immediately", "withdrawal-physically-purges-primary-and-preserves-sources",
                  "actual-short-retention-capture-honest-observed-outcome", "expired-read-denied-without-manual-sweep",
                  "actual-owned-background-sweeper-physically-purged", "expired-request-retry-cannot-renew"],
    },
    "LIVE-ISOLATION": {
        "requirements": "7.1 7.2 7.3 7.4 7.5 7.6",
        "feature": "Full immutable functional/adverse proof with safe producer retention",
        "expected": "One complete non-fast exact published detached-subject execution retains every inherited stage and safe original producer bytes. Real provider/task/quality, lifecycle/adverse controls and causal stale-report/consumer-failure tests pass, with owned cleanup and unchanged operational/source identities.",
        "steps": ["actual-provider-sandbox-task-completed", "actual-derived-quality-pass-with-evidence",
                  "actual-source-bound-experience-captured", "actual-verified-export",
                  "actual-accepted-experience-response-loss-one-durable-effect",
                  "actual-owned-background-sweeper-physically-purged", "owned-resources-removed",
                  "operational-container-identities-preserved", "measured-source-inputs-unchanged"],
    },
}


def main() -> int:
    destination = CHECKPOINT / "FUNCTIONAL-ACCEPTANCE.json"
    if destination.exists():
        raise LedgerError("preserve earlier functional assembly before another attempt")
    verification = load_json(CHECKPOINT / "VERIFY.json")
    publication = load_json(CHECKPOINT / "PUBLISHED-CLEAN-CLONE-REPORT.json")
    functional = load_json(CHECKPOINT / "FUNCTIONAL-SCENARIOS.json")
    subject = publication["publishedCommit"]
    experience = functional["scenarios"]["experience-store-e2e.json"]
    expected = [stage.name for stage in build_stages(False)]
    if (verification.get("result") != "PASS" or verification.get("fast") is not False
            or [row["name"] for row in verification["stages"]] != expected
            or any(row["result"] != "PASS" for row in verification["stages"])
            or publication.get("result") != "PASS" or publication.get("invocationCount") != 1
            or publication.get("retryCount") != 0 or functional.get("subjectCommit") != subject
            or experience.get("subjectCommit") != subject or experience.get("sourceDirty") is not False
            or experience.get("sourceFingerprint") != scope_fingerprint(ROOT)
            or experience.get("result") != "PASS"):
        raise LedgerError("the complete current immutable subject must pass every mandatory stage")
    required = set(functional_requirement_ids(ROOT, "GATE-6"))
    mapped = {"GATE-6-" + key for group in SCENARIOS.values() for key in group["requirements"].split()}
    if required != mapped:
        raise LedgerError("authored mapping differs from canonical functional membership: " + str(required ^ mapped))
    commands = [json.loads(line) for line in (CHECKPOINT / "COMMANDS.jsonl").read_text(
        encoding="utf-8").splitlines() if line.strip()]
    runs = [row for row in commands if row.get("exitCode") == 0
            and row.get("subjectCommit") == subject
            and "audit-harness/run_full_verification.py" in row.get("command", "")]
    if len(runs) != 1:
        raise LedgerError("one completed recorded immutable full execution must resolve")
    steps = {row["name"]: row for row in experience["steps"]}
    manifest = load_json(CHECKPOINT / load_json(CHECKPOINT / "PRODUCER-REPORTS.json")["manifest"])
    if manifest.get("refusedReports") or not any(
            row["producerName"] == "experience-store-e2e.json" for row in manifest["reports"]):
        raise LedgerError("actual safe experience producer bytes were not retained")
    now, rows = utc_now(), []
    for identifier, group in SCENARIOS.items():
        if any(steps.get(name, {}).get("result") != "PASS" for name in group["steps"]):
            raise LedgerError("an actual functional premise did not pass: " + identifier)
        rows.append({"scenarioId": "G6-FA-" + identifier,
            "requirementIds": ["GATE-6-" + key for key in group["requirements"].split()],
            "feature": group["feature"], "scenario": group["expected"],
            "environment": experience["environment"],
            "preconditions": ["Exact published detached subject " + subject,
                              "Complete mandatory suites/stages and fresh separately owned real stack."],
            "execution": [runs[0]["command"], "Actual domain, API unit and complete PostgreSQL/migration suites in this invocation."],
            "expected": [group["expected"]],
            "observed": [name + ": PASS" for name in group["steps"]], "result": "PASS",
            "evidence": [runs[0]["id"], "checkpoint:VERIFY.json", "checkpoint:FUNCTIONAL-SCENARIOS.json",
                         "checkpoint:PUBLISHED-CLEAN-CLONE-REPORT.json", "checkpoint:PRODUCER-REPORTS.json"],
            "timestamp": now, "artifactReferences": ["file:apps/api/tests/integration/test_experience_store.py",
                                                       "file:services/experience/tests/test_contract.py"]})
    write_json(destination, {"schemaVersion": "1.0.0", "gate": "GATE-6", "checkpoint": CHECKPOINT.name,
                             "status": "PASS", "generatedAt": now, "scenarios": rows})
    print(f"FUNCTIONAL_ASSEMBLY=PASS scenarios={len(rows)} requirements={len(required)} subject={subject}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
