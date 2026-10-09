"""The Quality Engine's only execution request: a structured call to the Gate 3 sandbox."""

from __future__ import annotations

import shlex
import uuid

from iacode_contracts.quality import QualityCheck, QualityPlan
from iacode_contracts.sandbox import SANDBOX_CONTRACT_VERSION

from iacode_evaluator.runners import get_runner

SANDBOX_POLICY_BY_STACK = {
    "python": "quality-python",
    "node": "quality-node",
    "typescript": "quality-node",
    "angular": "quality-node",
    "maven": "quality-java",
    "gradle": "quality-java",
}


def sandbox_policy(plan: QualityPlan, check: QualityCheck) -> str:
    """Select an image policy from the frozen runner, never from project-authored input."""
    stack = get_runner(check.runner).stack
    if stack == "common":
        stack = next(
            candidate
            for candidate in ("python", "node", "typescript", "angular", "maven", "gradle")
            if candidate in plan.projectProfile.split("+")
        )
    return SANDBOX_POLICY_BY_STACK[stack]


def quality_tool_request_id(run_id: str, check_id: str) -> str:
    """Derive the UUID identity required by the sandbox store from immutable check ownership."""
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"iacode-quality-tool:{run_id}:{check_id}"))


def sandbox_request(
    *, run_id: str, tool_request_id: str, plan: QualityPlan, check: QualityCheck
) -> dict:
    """Build a request that names policy and snapshot but cannot carry infrastructure settings."""
    policy = sandbox_policy(plan, check)
    return {
        "contractVersion": SANDBOX_CONTRACT_VERSION,
        "toolRequestId": tool_request_id,
        "runId": run_id,
        "agentRunId": None,
        "agent": "quality-engine",
        "tool": "shell.exec",
        "arguments": {
            "command": shlex.join(check.command),
            "cwd": check.workingDirectory,
            "environment": {"CI": "true", "NO_COLOR": "1", "TZ": "UTC"},
            "timeoutSeconds": check.timeoutSeconds,
        },
        "policy": policy,
        "workspace": {
            "kind": "snapshot",
            "artifactId": plan.snapshotId,
            "checksum": plan.snapshotDigest,
        },
    }
