#!/usr/bin/env python3
"""Internal Gate 4 false-PASS battery with an unmutated PASS control.

Every mandatory mutation named by the canonical checklist executes against the shipped contracts,
immutable store or verdict function inside the rebuilt evaluator image. A rejection for the wrong
reason is an escape. The host wrapper records the report as ``M2-INTERNAL-RED-TEAM.json``.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import subprocess
import sys
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

if "--in-image" not in sys.argv:
    from ledger_common import (
        LedgerError,
        find_root,
        resolve_latest,
        scope_fingerprint,
        use_utf8_stdout,
        utc_now,
        write_json,
    )

SOURCE = "scripts/development-ledger/gate4_red_team.py — Gate 4 internal false-PASS battery"


def _in_image_battery() -> dict[str, Any]:
    from iacode_contracts.quality import (
        QualityCheck,
        QualityEvidence,
        QualityPlan,
        QualityPolicy,
        QualityResult,
    )
    from iacode_evaluator.errors import QualityError
    from iacode_evaluator.store import MemoryQualityStore
    from iacode_evaluator.verdict import derive_verdict
    from pydantic import ValidationError

    now = datetime(2026, 10, 9, 20, tzinfo=UTC)
    run_id = "red-team-run"
    plan_sha = "a" * 64
    snapshot_sha = "b" * 64
    evidence_sha = "c" * 64

    def plan() -> QualityPlan:
        return QualityPlan(
            planId=plan_sha,
            snapshotId="snapshot-red-team",
            snapshotDigest=snapshot_sha,
            projectProfile="python",
            projectProfileDigest="d" * 64,
            policy=QualityPolicy(
                policyId="default",
                version="1.0.0",
                digest="e" * 64,
                profile="python",
                mandatoryCheckKinds=("unit",),
                maxRunSeconds=60,
                maxCheckSeconds=30,
                maxOutputBytes=4096,
            ),
            checks=(
                QualityCheck(
                    checkId="q001-unit",
                    kind="unit",
                    runner="python.unit",
                    command=("python", "-m", "unittest"),
                    applicabilityReason="mandatory red-team control",
                    timeoutSeconds=30,
                    requiredEvidenceKinds=("report",),
                ),
            ),
            createdAt=now,
        )

    def evidence() -> QualityEvidence:
        return QualityEvidence(
            evidenceId="evidence-red-team",
            kind="report",
            artifactId="artifact-red-team",
            digest=evidence_sha,
            sizeBytes=24,
            mediaType="application/json",
            producer="iacode-evaluator",
            sourceDigests=(snapshot_sha,),
            createdAt=now,
            retentionClass="quality-evidence",
        )

    def result(status: str = "PASSED", **updates: Any) -> QualityResult:
        body: dict[str, Any] = {
            "resultId": "result-red-team",
            "runId": run_id,
            "checkId": "q001-unit",
            "status": status,
            "exitCode": 0 if status == "PASSED" else None,
            "durationMs": 1,
            "timedOut": status == "TIMED_OUT",
            "truncated": False,
            "summary": f"red-team {status}",
            "evidence": (evidence(),),
            "findings": (),
            "finishedAt": now,
        }
        body.update(updates)
        return QualityResult(**body)

    canonical_plan = plan()
    canonical_result = result()
    control = derive_verdict(
        run_id=run_id,
        plan=canonical_plan,
        results=(canonical_result,),
        resolved_evidence_digests={evidence_sha},
        derived_at=now,
    )
    attacks: list[dict[str, Any]] = []

    def attack(
        identifier: str,
        target: str,
        mutation: str,
        expected: str,
        operation: Callable[[], tuple[bool, str]],
    ) -> None:
        try:
            defended, observed = operation()
        except Exception as error:
            defended, observed = False, f"attack crashed: {type(error).__name__}"
        attacks.append(
            {
                "attackId": identifier,
                "description": target,
                "target": target,
                "mutation": mutation,
                "expectedDefense": expected,
                "observed": observed,
                "result": "DEFENDED" if defended else "ESCAPED",
                "evidence": [
                    "file:services/evaluator/src/iacode_evaluator/verdict.py",
                    "file:packages/contracts/src/iacode_contracts/quality.py",
                ],
                "mandatory": True,
                "origin": "Gate 4 internal Red Team in the rebuilt evaluator image",
            }
        )

    def verdict_mutation(mutated: QualityResult | None) -> tuple[bool, str]:
        verdict = derive_verdict(
            run_id=run_id,
            plan=canonical_plan,
            results=() if mutated is None else (mutated,),
            resolved_evidence_digests={evidence_sha},
            derived_at=now,
        )
        return verdict.verdict == "FAIL", f"verdict={verdict.verdict}; reasons={verdict.reasons}"

    attack(
        "G4-A",
        "missing result",
        "remove the only mandatory result",
        "derived verdict FAIL names the missing check",
        lambda: verdict_mutation(None),
    )

    def flip_exit() -> tuple[bool, str]:
        try:
            result(exitCode=1)
        except ValidationError as error:
            return (
                "a passed check requires exit code zero" in str(error),
                "contract refused non-zero PASS",
            )
        return False, "contract accepted a non-zero PASS"

    attack(
        "G4-B",
        "exit-code forgery",
        "keep PASSED and flip exitCode to 1",
        "the result contract refuses the contradictory shape",
        flip_exit,
    )

    def forged_evidence() -> tuple[bool, str]:
        verdict = derive_verdict(
            run_id=run_id,
            plan=canonical_plan,
            results=(canonical_result,),
            resolved_evidence_digests={"f" * 64},
            derived_at=now,
        )
        return verdict.verdict == "FAIL", f"verdict={verdict.verdict}; reasons={verdict.reasons}"

    attack(
        "G4-C",
        "forged evidence",
        "replace the resolved digest set",
        "the evidence reference is unresolved and verdict is FAIL",
        forged_evidence,
    )

    async def plan_conflict(field: str) -> tuple[bool, str]:
        store = MemoryQualityStore(now=lambda: now)
        await store.create_plan(canonical_plan)
        if field == "policy":
            changed_policy = canonical_plan.policy.model_copy(update={"maxCheckSeconds": 1})
            changed = canonical_plan.model_copy(update={"policy": changed_policy})
        else:
            changed = canonical_plan.model_copy(update={"snapshotDigest": "f" * 64})
        try:
            await store.create_plan(changed)
        except QualityError as error:
            return error.code == "PLAN_ID_CONFLICT", f"store refused {error.code}"
        return False, "store accepted changed material under the frozen plan identity"

    attack(
        "G4-D",
        "policy mutation",
        "change maxCheckSeconds under the same planId",
        "the immutable store refuses PLAN_ID_CONFLICT",
        lambda: asyncio.run(plan_conflict("policy")),
    )
    attack(
        "G4-E",
        "snapshot mutation",
        "change snapshotDigest under the same planId",
        "the immutable store refuses PLAN_ID_CONFLICT",
        lambda: asyncio.run(plan_conflict("snapshot")),
    )

    def invalid_contract(field: str, value: Any, expected_text: str) -> tuple[bool, str]:
        body = canonical_result.model_dump(mode="python")
        body[field] = value
        try:
            QualityResult.model_validate(body)
        except ValidationError as error:
            return expected_text in str(error), f"contract refused {field}"
        return False, f"contract accepted {field}={value}"

    attack(
        "G4-F",
        "wrong origin",
        "post a result with origin CALLER",
        "the closed origin contract refuses it",
        lambda: invalid_contract("origin", "CALLER", "EVALUATOR"),
    )
    for identifier, status, updates in (
        ("G4-G", "TIMED_OUT", {"timedOut": True, "exitCode": 124}),
        ("G4-H", "DENIED", {"exitCode": None}),
        ("G4-I", "CANCELLED", {"exitCode": None}),
    ):
        attack(
            identifier,
            f"{status.lower()} result",
            f"replace PASSED with {status}",
            "the derived verdict is FAIL",
            lambda status=status, updates=updates: verdict_mutation(result(status, **updates)),
        )
    attack(
        "G4-J",
        "unknown status",
        "submit status ASSERTED_GOOD",
        "the closed result-status contract refuses it",
        lambda: invalid_contract("status", "ASSERTED_GOOD", "unknown quality result status"),
    )

    escaped = [item for item in attacks if item["result"] == "ESCAPED"]
    return {
        "baselineControl": {
            "result": "VALID" if control.verdict == "PASS" else "INVALID",
            "detail": f"unmutated complete result derived {control.verdict}",
            "evidence": ["file:services/evaluator/src/iacode_evaluator/verdict.py"],
        },
        "attacks": attacks,
        "escaped": len(escaped),
        "defended": len(attacks) - len(escaped),
        "total": len(attacks),
    }


def _compose(root: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    directory = root / "infra" / "compose"
    return subprocess.run(
        [
            "docker",
            "compose",
            "--project-directory",
            str(directory),
            "--file",
            str(directory / "docker-compose.yml"),
            "--env-file",
            str(directory / ".env"),
            *arguments,
        ],
        cwd=root,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
        timeout=1800,
    )


def run_in_image(root: Path, rebuild: bool) -> dict[str, Any]:
    if rebuild:
        built = _compose(root, "build", "evaluator")
        if built.returncode != 0:
            raise LedgerError("evaluator rebuild failed: " + built.stdout[-1200:])
    script = Path(__file__).resolve()
    completed = _compose(
        root,
        "run",
        "--rm",
        "--no-deps",
        "--entrypoint",
        "",
        "--volume",
        f"{script.as_posix()}:/app/gate4-red-team.py:ro",
        "evaluator",
        "python",
        "/app/gate4-red-team.py",
        "--in-image",
    )
    if completed.returncode != 0:
        raise LedgerError("Gate 4 Red Team image harness failed: " + completed.stdout[-1600:])
    for line in reversed(completed.stdout.splitlines()):
        if line.strip().startswith("{"):
            return json.loads(line)
    raise LedgerError("Gate 4 Red Team image harness returned no report")


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Internal Red Team — GATE 4 — QUALITY ENGINE",
        "",
        f"Result: `{report['result']}`",
        "",
        f"- Baseline control: `{report['baselineControl']['result']}`",
        f"- Attacks defended: {report['defended']}/{report['total']}",
        "",
        "| Attack | Target | Mutation | Expected | Observed | Result |",
        "|---|---|---|---|---|---|",
    ]
    for attack in report["attacks"]:
        observed = attack["observed"].replace("|", "\\|").replace("\n", " ")
        lines.append(
            f"| `{attack['attackId']}` | {attack['target']} | {attack['mutation']} | "
            f"{attack['expectedDefense']} | {observed} | `{attack['result']}` |"
        )
    return "\n".join(lines) + "\n"


def main() -> int:
    if "--in-image" not in sys.argv:
        use_utf8_stdout()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path)
    parser.add_argument("--checkpoint", type=Path)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--skip-gate-rebuild", action="store_true")
    parser.add_argument("--in-image", action="store_true", help=argparse.SUPPRESS)
    arguments = parser.parse_args()
    if arguments.in_image:
        report = _in_image_battery()
        print(json.dumps(report, separators=(",", ":")))
        return 0 if report["baselineControl"]["result"] == "VALID" and not report["escaped"] else 1

    root = find_root(arguments.root) if arguments.root else find_root()
    checkpoint = arguments.checkpoint or resolve_latest(root)
    if not checkpoint.is_absolute():
        checkpoint = root / checkpoint
    observed = run_in_image(root, rebuild=not arguments.skip_gate_rebuild)
    report = {
        "schemaVersion": "1.1.0",
        "checkpoint": checkpoint.name,
        "generatedAt": utc_now(),
        "targetFingerprint": scope_fingerprint(root),
        "source": SOURCE,
        **observed,
        "mandatoryTotal": observed["total"],
        "mandatoryDefended": observed["defended"],
        "result": (
            "RED_TEAM_PASS"
            if observed["baselineControl"]["result"] == "VALID" and not observed["escaped"]
            else "RED_TEAM_FAIL"
        ),
    }
    if arguments.write:
        write_json(checkpoint / "M2-INTERNAL-RED-TEAM.json", report)
        (checkpoint / "RED-TEAM-REPORT.md").write_text(
            render_markdown(report), encoding="utf-8", newline="\n"
        )
    for attack in report["attacks"]:
        print(f"[{attack['result']}] {attack['attackId']} {attack['target']}: {attack['observed']}")
    print(
        f"RED_TEAM={report['result']} {report['defended']}/{report['total']} "
        f"control={report['baselineControl']['result']}"
    )
    return 0 if report["result"] == "RED_TEAM_PASS" else 1


if __name__ == "__main__":
    if "--in-image" in sys.argv:
        sys.exit(main())
    try:
        sys.exit(main())
    except LedgerError as error:
        print(f"LEDGER_ERROR: {error}")
        sys.exit(2)
