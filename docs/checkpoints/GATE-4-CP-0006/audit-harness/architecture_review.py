#!/usr/bin/env python3
"""Independent structural review of the complete sealed Gate 4 implementation."""

from __future__ import annotations

import argparse
import ast
import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
SUBJECT = "c631270e49c095a9777825c0bc18818694c07ffb"
GATE3 = "iacode-checkpoints/GATE-3-CP-0006"
sys.path.insert(0, str(ROOT / "scripts" / "development-ledger"))

from ledger_common import use_utf8_stdout  # noqa: E402


def text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def main() -> int:
    use_utf8_stdout()
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path, required=True)
    arguments = parser.parse_args()
    checks: list[dict[str, Any]] = []

    def add(identifier: str, area: str, expectation: str, observed: Any, ok: bool,
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
    parsed = 0
    for path in sorted(evaluator.glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        parsed += 1
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in {"subprocess", "docker"}:
                        forbidden_imports.append(f"{path.name}:{node.lineno}:{alias.name}")
            elif isinstance(node, ast.ImportFrom) and node.module in {"subprocess", "docker"}:
                forbidden_imports.append(f"{path.name}:{node.lineno}:{node.module}")
    add(
        "AR-01", "host execution boundary",
        "the evaluator imports no host/container execution client",
        {"parsedModules": parsed, "forbiddenImports": forbidden_imports},
        parsed >= 20 and not forbidden_imports,
        ["file:services/evaluator/src/iacode_evaluator"],
    )

    contracts = text("packages/contracts/src/iacode_contracts/quality.py")
    contract_markers = {
        "closedFrozen": 'ConfigDict(extra="forbid", frozen=True)' in contracts,
        "originOwned": 'origin: Literal["EVALUATOR"]' in contracts,
        "trainingDenied": "trainingAllowed: Literal[False]" in contracts,
        "acyclic": "unique_checks_and_acyclic_dependencies" in contracts,
        "noSubmittedVerdict": "verdict:" not in contracts.split(
            "class CreateQualityRunRequest", 1
        )[1].split("class QualityCheckSummary", 1)[0],
    }
    add(
        "AR-02", "quality contracts",
        "quality contracts are closed, frozen, rights-safe and refuse a submitted verdict",
        contract_markers, all(contract_markers.values()),
        ["file:packages/contracts/src/iacode_contracts/quality.py"],
    )

    runners = text("services/evaluator/src/iacode_evaluator/runners.py")
    stacks = ["python", "node", "typescript", "angular", "maven", "gradle"]
    runner_markers = {stack: f'"{stack}"' in runners for stack in stacks}
    runner_markers.update({
        "mavenOffline": '"--offline"' in runners and "maven.repo.local" in runners,
        "gradleOffline": '("gradle", "--offline"' in runners,
        "unknownRefused": "RUNNER_UNKNOWN" in runners,
    })
    add(
        "AR-03", "closed runners",
        "all supported stacks use closed offline-capable runner definitions",
        runner_markers, all(runner_markers.values()),
        ["file:services/evaluator/src/iacode_evaluator/runners.py",
         "file:.iacode/policies/quality-policy.json"],
    )

    executor = text("services/evaluator/src/iacode_evaluator/executor.py")
    executor_markers = {
        "allProfiles": all(f'"{stack}": "quality-' in executor for stack in stacks),
        "structuredTool": '"tool": "shell.exec"' in executor,
        "snapshotBound": '"checksum": plan.snapshotDigest' in executor,
        "policyFromRunner": "get_runner(check.runner).stack" in executor,
        "noCallerNetwork": '"network"' not in executor,
        "noCallerMount": '"mount"' not in executor,
    }
    add(
        "AR-04", "sandbox request construction",
        "execution is a structured Gate 3 request bound to the frozen runner and snapshot",
        executor_markers, all(executor_markers.values()),
        ["file:services/evaluator/src/iacode_evaluator/executor.py",
         "file:.iacode/policies/sandbox-policies.json"],
    )

    policy = text("services/evaluator/src/iacode_evaluator/policy.py")
    policy_markers = {
        "closedConfiguration": "CONFIG_KEYS = frozenset({" in policy,
        "noRunnerExpansion": "RUNNER_NOT_DECLARED_FOR_PROFILE" in policy,
        "noThresholdWeakening": "QUALITY_THRESHOLD_WEAKENED" in policy,
        "noLimitRaise": "QUALITY_LIMIT_RAISED" in policy,
        "unknownRefused": "QUALITY_POLICY_UNKNOWN_KEY" in policy,
    }
    add(
        "AR-05", "policy narrowing",
        "project configuration can only narrow canonical policy",
        policy_markers, all(policy_markers.values()),
        ["file:services/evaluator/src/iacode_evaluator/policy.py"],
    )

    verdict = text("services/evaluator/src/iacode_evaluator/verdict.py")
    verdict_markers = {
        "missing": "missing result for" in verdict,
        "duplicate": "duplicate result for" in verdict,
        "foreign": "belongs to another run" in verdict,
        "unexpected": "unexpected result for" in verdict,
        "nonPass": 'result.status != "PASSED"' in verdict,
        "unresolved": "has unresolved evidence" in verdict,
        "emptyRequiredSet": "the required check set is missing" in verdict,
        "pureVerdict": 'verdict = "FAIL" if reasons else "PASS"' in verdict,
    }
    add(
        "AR-06", "verdict derivation",
        "pure derivation fails closed for every invalid or incomplete input",
        verdict_markers, all(verdict_markers.values()),
        ["file:services/evaluator/src/iacode_evaluator/verdict.py"],
    )

    evidence_path = ROOT / "services/evaluator/src/iacode_evaluator/evidence.py"
    evidence_source = evidence_path.read_text(encoding="utf-8")
    evidence_tree = ast.parse(evidence_source)
    store_class = next(
        node for node in evidence_tree.body
        if isinstance(node, ast.ClassDef) and node.name == "QualityEvidenceStore"
    )
    put_method = next(
        node for node in store_class.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "put"
    )
    first_put_statement = ast.unparse(put_method.body[0])
    evidence_markers = {
        "sharedScannerImport": (
            "from iacode_common.secret_scanning import find_secret_kinds" in evidence_source
        ),
        "scanIsFirstPutStatement": first_put_statement == "_require_secret_free(content)",
        "scannerFailureCode": "EVIDENCE_SECRET_SCAN_FAILED" in evidence_source,
        "scannerDetectionCode": "EVIDENCE_SECRET_DETECTED" in evidence_source,
        "resolveRescans": (
            "content = await self._read(record.key)" in evidence_source
            and "_require_secret_free(content)" in evidence_source.split(
                "async def resolve", 1
            )[1]
        ),
        "immutableObject": (
            'key = f"quality/evidence/{digest}"' in evidence_source
            and "EVIDENCE_DIGEST_COLLISION" in evidence_source
        ),
    }
    add(
        "AR-07", "pre-persistence evidence containment",
        "the shared scanner runs on exact bytes before lookup/write and resolution rescans legacy bytes",
        {**evidence_markers, "firstPutStatement": first_put_statement},
        all(evidence_markers.values()),
        ["file:packages/common/src/iacode_common/secret_scanning.py",
         "file:services/evaluator/src/iacode_evaluator/evidence.py",
         "file:docs/adr/ADR-0032-quality-evidence-is-scanned-before-durable-commit.md"],
    )

    activities = text("services/evaluator/src/iacode_evaluator/activities.py")
    activity_markers = {
        "exactSerialization": 'json.dumps(' in activities and '.encode("utf-8")' in activities,
        "boundedCatch": "error.code not in SECRET_EVIDENCE_ERROR_CODES" in activities,
        "sanitizedError": 'summary = "quality evidence was rejected before persistence"' in activities,
        "noRejectedEvidence": "evidence_items = ()" in activities,
        "noRejectedFindings": "and not containment_reason" in activities,
        "derivedVerdict": "derive_verdict(" in activities,
    }
    add(
        "AR-08", "activity containment semantics",
        "only containment failures become sanitized ERROR results with no evidence/findings",
        activity_markers, all(activity_markers.values()),
        ["file:services/evaluator/src/iacode_evaluator/activities.py"],
    )

    workflow = text("services/evaluator/src/iacode_evaluator/workflow.py")
    workflow_markers = {
        "temporal": "@workflow.defn" in workflow,
        "sandbox": "SANDBOX_EXECUTE_ACTIVITY" in workflow,
        "singleAttempt": "maximum_attempts=1" in workflow,
        "deadline": "QUALITY_RUN_DEADLINE_EXCEEDED" in workflow,
        "verdict": "await self._verdict()" in workflow,
    }
    add(
        "AR-09", "durable lifecycle",
        "Temporal owns sandbox execution, deadlines, cleanup and derived verdict",
        workflow_markers, all(workflow_markers.values()),
        ["file:services/evaluator/src/iacode_evaluator/workflow.py"],
    )

    docs = [
        "START-HERE.md", "README.md", "docs/ARCHITECTURE.md", "docs/DEVELOPMENT.md",
        "docs/VERSIONS.md", "docs/runbooks/QUALITY-ENGINE.md",
        "docs/adr/ADR-0029-quality-execution-boundary.md",
        "docs/adr/ADR-0030-quality-evidence-and-verdict-immutability.md",
        "docs/adr/ADR-0031-project-profiles-select-closed-quality-runners.md",
        "docs/adr/ADR-0032-quality-evidence-is-scanned-before-durable-commit.md",
    ]
    docs_present = {path: (ROOT / path).is_file() and "quality" in text(path).lower() for path in docs}
    add(
        "AR-10", "documentation and ADRs",
        "entry, architecture, operations and ADRs describe current quality behavior",
        docs_present, all(docs_present.values()), [f"file:{path}" for path in docs],
    )

    lessons = text(".iacode/memory/lessons.jsonl")
    guardrails = json.loads(text(".iacode/memory/guardrails/registry.json"))
    guardrail_text = json.dumps(guardrails, sort_keys=True)
    memory_markers = {
        "lesson": '"lessonId":"LSN-0091"' in lessons.replace(" ", ""),
        "guardrail": "GRD-0092" in guardrail_text,
        "persistenceTest": "test_canonical_secret_is_rejected_before_any_durable_operation" in guardrail_text,
        "workflowTest": "test_secret_bearing_execution_is_contained_and_derives_fail" in guardrail_text,
    }
    add(
        "AR-11", "memory and guardrail",
        "the confirmed failure is a lesson guarded by direct persistence and workflow controls",
        memory_markers, all(memory_markers.values()),
        ["file:.iacode/memory/lessons.jsonl", "file:.iacode/memory/guardrails/registry.json"],
    )

    changed = subprocess.run(
        ["git", "diff", "--name-only", GATE3, SUBJECT],
        cwd=ROOT, text=True, encoding="utf-8", capture_output=True, check=True,
    ).stdout.splitlines()
    forbidden_scope = [
        path for path in changed
        if path.startswith(("extensions/", "vscode/", "services/experience", "services/knowledge",
                            "services/evaluation-lab"))
    ]
    add(
        "AR-12", "Gate scope",
        "Gate 4 introduced no Gate 5–7 or Gate 20 implementation surface",
        {"changedPaths": len(changed), "forbiddenScope": forbidden_scope},
        not forbidden_scope,
        ["git:diff-GATE-3-CP-0006..GATE-4-CP-0005"],
    )

    failed = [item for item in checks if item["result"] != "PASS"]
    report = {
        "schemaVersion": "1.0.0",
        "artifact": "GATE-4-INDEPENDENT-ARCHITECTURE-REVIEW",
        "checkpoint": CHECKPOINT.name,
        "subjectCheckpoint": "GATE-4-CP-0005",
        "subjectCommit": SUBJECT,
        "generatedAt": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "checks": checks,
        "passed": len(checks) - len(failed),
        "total": len(checks),
        "result": "PASS" if not failed else "FAIL",
    }
    arguments.report.resolve().write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(f"ARCHITECTURE_REVIEW={report['result']} {report['passed']}/{report['total']}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
