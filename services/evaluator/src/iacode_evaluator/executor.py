"""The Quality Engine's only execution request: a structured call to the Gate 3 sandbox."""

from __future__ import annotations

import shlex

from iacode_contracts.quality import QualityCheck, QualityPlan
from iacode_contracts.sandbox import SANDBOX_CONTRACT_VERSION

SANDBOX_POLICY_BY_STACK = {
    "python": "quality-python",
    "node": "quality-node",
    "node+typescript": "quality-node",
    "node+typescript+angular": "quality-node",
    "maven": "quality-java",
    "gradle": "quality-java",
}


def sandbox_request(
    *, run_id: str, tool_request_id: str, plan: QualityPlan, check: QualityCheck
) -> dict:
    """Build a request that names policy and snapshot but cannot carry infrastructure settings."""
    policy = SANDBOX_POLICY_BY_STACK[plan.projectProfile]
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
