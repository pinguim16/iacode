#!/usr/bin/env python3
"""Independent structural review of the sealed Gate 4 Quality Engine slice."""

from __future__ import annotations

import argparse
import ast
import json
import subprocess
import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
SUBJECT_COMMIT = "70a22e824705f414e0c295bbdf89187db9b391f7"
BASE_COMMIT = "92020769ffd19adeb78d432141da5b1fd492f969"
sys.path.insert(0, str(ROOT / "scripts" / "development-ledger"))

from ledger_common import utc_now  # noqa: E402


def text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path, required=True)
    arguments = parser.parse_args()
    checks: list[dict[str, object]] = []

    def add(identifier: str, area: str, expectation: str, observed: object, ok: bool,
            evidence: list[str]) -> None:
        checks.append({
            "id": identifier,
            "area": area,
            "expectation": expectation,
            "observed": observed,
            "result": "PASS" if ok else "FAIL",
            "evidence": evidence,
        })
        print(f"[{'PASS' if ok else 'FAIL'}] {identifier} — {area}")

    evaluator = ROOT / "services" / "evaluator" / "src" / "iacode_evaluator"
    forbidden_imports: list[str] = []
    parsed_modules = 0
    for path in sorted(evaluator.glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        parsed_modules += 1
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in {"subprocess", "docker"}:
                        forbidden_imports.append(f"{path.name}:{node.lineno}:{alias.name}")
            elif isinstance(node, ast.ImportFrom) and node.module in {"subprocess", "docker"}:
                forbidden_imports.append(f"{path.name}:{node.lineno}:{node.module}")
    add(
        "AR-01",
        "host execution boundary",
        "evaluator implementation imports no host/container execution client",
        {"parsedModules": parsed_modules, "forbiddenImports": forbidden_imports},
        parsed_modules >= 20 and not forbidden_imports,
        ["file:services/evaluator/src/iacode_evaluator", "file:services/evaluator/src/iacode_evaluator/executor.py"],
    )

    contracts = text("packages/contracts/src/iacode_contracts/quality.py")
    contract_markers = {
        "closedAndFrozen": 'ConfigDict(extra="forbid", frozen=True)' in contracts,
        "passVerdictNotAccepted": "verdict:" not in contracts.split("class CreateQualityRunRequest", 1)[1]
        .split("class QualityCheckSummary", 1)[0],
        "originLiteral": 'origin: Literal["EVALUATOR"]' in contracts,
        "trainingDenied": "trainingAllowed: Literal[False]" in contracts,
        "acyclicPlan": "unique_checks_and_acyclic_dependencies" in contracts,
    }
    add(
        "AR-02",
        "quality contracts",
        "contracts are closed, immutable, versioned and refuse caller-owned verdict/origin/rights",
        contract_markers,
        all(contract_markers.values()),
        ["file:packages/contracts/src/iacode_contracts/quality.py"],
    )

    runners = text("services/evaluator/src/iacode_evaluator/runners.py")
    stacks = ["python", "node", "typescript", "angular", "maven", "gradle"]
    runner_markers = {stack: f'"{stack}"' in runners for stack in stacks}
    runner_markers.update({
        "mavenOffline": '"--offline"' in runners and "maven.repo.local" in runners,
        "gradleOffline": '("gradle", "--offline"' in runners,
        "closedLookup": "RUNNER_UNKNOWN" in runners,
    })
    add(
        "AR-03",
        "closed runner registry",
        "all required stacks resolve through closed offline-capable runner definitions",
        runner_markers,
        all(runner_markers.values()),
        ["file:services/evaluator/src/iacode_evaluator/runners.py", "file:.iacode/policies/quality-policy.json"],
    )

    executor = text("services/evaluator/src/iacode_evaluator/executor.py")
    executor_markers = {
        "allStackPolicies": all(f'"{stack}": "quality-' in executor for stack in stacks),
        "shellOnly": '"tool": "shell.exec"' in executor,
        "snapshotBound": '"checksum": plan.snapshotDigest' in executor,
        "policyFromRunner": "get_runner(check.runner).stack" in executor,
        "noNetworkField": '"network"' not in executor,
        "noMountField": '"mount"' not in executor,
    }
    add(
        "AR-04",
        "sandbox request construction",
        "execution is a structured Gate 3 request bound to frozen runner policy and snapshot",
        executor_markers,
        all(executor_markers.values()),
        ["file:services/evaluator/src/iacode_evaluator/executor.py", "file:.iacode/policies/sandbox-policies.json"],
    )

    policy = text("services/evaluator/src/iacode_evaluator/policy.py")
    policy_markers = {
        "closedConfiguration": 'CONFIG_KEYS = frozenset({' in policy,
        "noRunnerExpansion": "RUNNER_NOT_DECLARED_FOR_PROFILE" in policy,
        "noThresholdWeakening": "QUALITY_THRESHOLD_WEAKENED" in policy,
        "noLimitRaise": "QUALITY_LIMIT_RAISED" in policy,
        "unknownFieldRefused": "QUALITY_POLICY_UNKNOWN_KEY" in policy,
    }
    add(
        "AR-05",
        "policy narrowing",
        "project configuration can only narrow canonical policy and declared optional runners",
        policy_markers,
        all(policy_markers.values()),
        ["file:services/evaluator/src/iacode_evaluator/policy.py", "file:.iacode/policies/quality-policy.json"],
    )

    verdict = text("services/evaluator/src/iacode_evaluator/verdict.py")
    verdict_markers = {
        "missingFails": "missing result for" in verdict,
        "duplicateFails": "duplicate result for" in verdict,
        "foreignFails": "belongs to another run" in verdict,
        "unexpectedFails": "unexpected result for" in verdict,
        "nonPassFails": 'result.status != "PASSED"' in verdict,
        "evidenceFails": "has unresolved evidence" in verdict,
        "emptySetFails": "the required check set is missing" in verdict,
        "pureDerivedVerdict": 'verdict = "FAIL" if reasons else "PASS"' in verdict,
    }
    add(
        "AR-06",
        "fail-closed verdict",
        "pure derivation rejects every missing, foreign, duplicate, failed or unresolved input",
        verdict_markers,
        all(verdict_markers.values()),
        ["file:services/evaluator/src/iacode_evaluator/verdict.py"],
    )

    evidence = text("services/evaluator/src/iacode_evaluator/evidence.py")
    activities = text("services/evaluator/src/iacode_evaluator/activities.py")
    evidence_markers = {
        "rehashBeforeReturn": "hashlib.sha256(content).hexdigest() == evidence.digest" in evidence,
        "secretContainment": "redact_mapping(execution)" in activities
        and "inline_summary(redact_text(raw_summary))" in activities,
        "immutableObject": 'key = f"quality/evidence/{digest}"' in evidence
        and "EVIDENCE_DIGEST_COLLISION" in evidence,
        "rightsBound": "trainingAllowed" in evidence and "distillationAllowed" in evidence,
    }
    add(
        "AR-07",
        "immutable evidence",
        "evidence is re-hashed, secret-contained, write-once and rights-bound",
        evidence_markers,
        all(evidence_markers.values()),
        ["file:services/evaluator/src/iacode_evaluator/evidence.py", "file:services/evaluator/src/iacode_evaluator/activities.py", "file:services/evaluator/src/iacode_evaluator/store.py"],
    )

    workflow = text("services/evaluator/src/iacode_evaluator/workflow.py")
    cancellation_body = workflow.split("async def _finish_cancelled", 1)[1].split(
        "@workflow.run", 1
    )[0]
    workflow_markers = {
        "temporalWorkflow": "@workflow.defn" in workflow,
        "sandboxActivity": "SANDBOX_EXECUTE_ACTIVITY" in workflow,
        "singleAttemptExecution": "maximum_attempts=1" in workflow,
        "cleanupBeforeCancelled": cancellation_body.find('await self._release("cancellation")')
        < cancellation_body.rfind('"CANCELLED"'),
        "deadlineFails": "QUALITY_RUN_DEADLINE_EXCEEDED" in workflow,
        "derivedVerdict": "await self._verdict()" in workflow,
    }
    add(
        "AR-08",
        "durable workflow",
        "Temporal lifecycle binds sandbox execution, cancellation cleanup, deadline and derived verdict",
        workflow_markers,
        all(workflow_markers.values()),
        ["file:services/evaluator/src/iacode_evaluator/workflow.py", "file:services/evaluator/src/iacode_evaluator/activities.py"],
    )

    store = text("services/evaluator/src/iacode_evaluator/store.py")
    store_markers = {
        "ownerMismatch": "RUN_OWNER_MISMATCH" in store,
        "originMismatch": "RESULT_ORIGIN_MISMATCH" in store,
        "earlyResult": "EARLY_RESULT" in store,
        "lateResult": "LATE_RESULT" in store,
        "idempotency": "idempotency_key" in store,
        "appendEvents": "append_event" in store,
    }
    add(
        "AR-09",
        "persistence and origin",
        "store enforces owner, origin, lifecycle ordering, idempotency and append-only events",
        store_markers,
        all(store_markers.values()),
        ["file:services/evaluator/src/iacode_evaluator/store.py", "file:apps/api/migrations/versions/0006_quality_engine.py"],
    )

    telemetry = text("services/evaluator/src/iacode_evaluator/telemetry.py")
    forbidden_labels = [
        value for value in ("projectPath", "command", "output", "findingMessage", "digest", "runId")
        if f'"{value}"' in telemetry.split("def quality_log", 1)[0]
    ]
    add(
        "AR-10",
        "observability",
        "metric labels remain bounded and sensitive/high-cardinality values are not labels",
        {"forbiddenMetricLabels": forbidden_labels, "qualityLogPresent": "def quality_log" in telemetry},
        not forbidden_labels and "def quality_log" in telemetry,
        ["file:services/evaluator/src/iacode_evaluator/telemetry.py", "file:infra/prometheus/prometheus.yml"],
    )

    required_docs = [
        "START-HERE.md",
        "README.md",
        "docs/ARCHITECTURE.md",
        "docs/DEVELOPMENT.md",
        "docs/VERSIONS.md",
        "docs/MODEL-USAGE-POLICY.md",
        "docs/runbooks/QUALITY-ENGINE.md",
        "docs/adr/ADR-0029-quality-execution-boundary.md",
        "docs/adr/ADR-0030-quality-evidence-and-verdict-immutability.md",
        "docs/adr/ADR-0031-project-profiles-select-closed-quality-runners.md",
    ]
    doc_state = {path: (ROOT / path).is_file() and "quality" in text(path).lower()
                 for path in required_docs}
    add(
        "AR-11",
        "documentation and decisions",
        "entry, architecture, operations and structural ADRs describe delivered quality behavior",
        doc_state,
        all(doc_state.values()),
        [f"file:{path}" for path in required_docs],
    )

    changed = subprocess.run(
        ["git", "diff", "--name-only", BASE_COMMIT, SUBJECT_COMMIT],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=False,
    ).stdout.splitlines()
    forbidden_scope = [path for path in changed if path.startswith((
        "extensions/", "vscode/", "services/experience", "services/knowledge", "services/evaluation-lab"
    ))]
    add(
        "AR-12",
        "Gate scope",
        "Gate 4 changed no Gate 5–7 or Gate 20 implementation surface",
        {"changedPaths": len(changed), "forbiddenScope": forbidden_scope},
        not forbidden_scope,
        ["git:diff-GATE-3-CP-0006..GATE-4-CP-0001"],
    )

    failed = [item for item in checks if item["result"] != "PASS"]
    report = {
        "schemaVersion": "1.0.0",
        "artifact": "GATE-4-ARCHITECTURE-REVIEW",
        "checkpoint": CHECKPOINT.name,
        "subjectCommit": SUBJECT_COMMIT,
        "generatedAt": utc_now(),
        "checks": checks,
        "passed": len(checks) - len(failed),
        "total": len(checks),
        "result": "PASS" if not failed else "FAIL",
    }
    output = arguments.report.resolve()
    output.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(f"ARCHITECTURE_REVIEW={report['result']} {report['passed']}/{report['total']}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
