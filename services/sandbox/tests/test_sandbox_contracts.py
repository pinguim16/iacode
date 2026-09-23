"""The versioned contracts: strict, round-trippable, and honest about exit codes."""

from __future__ import annotations

import pytest
from iacode_contracts.sandbox import SANDBOX_CONTRACT_VERSION, TOOL_EXECUTION_STATUSES
from iacode_sandbox.contracts import (
    ArtifactReference,
    CommandExecution,
    ContractError,
    FileOperation,
    GitOperation,
    SandboxSession,
    ToolExecutionRequest,
    ToolExecutionResult,
    Workspace,
    WorkspaceSource,
)
from sandbox_fixtures import request


class SandboxContractTests:
    def test_the_contract_is_versioned(self) -> None:
        payload = request("filesystem.read", {"path": "a.txt"}, run_id="run-1")
        parsed = ToolExecutionRequest.from_dict(payload)
        assert parsed.contract_version == SANDBOX_CONTRACT_VERSION
        assert ToolExecutionRequest.from_dict(parsed.to_dict()) == parsed

    def test_another_version_is_refused_rather_than_interpreted(self) -> None:
        payload = request("filesystem.read", {"path": "a.txt"}, run_id="run-1")
        payload["contractVersion"] = "9.9.9"
        with pytest.raises(ContractError) as refused:
            ToolExecutionRequest.from_dict(payload)
        assert refused.value.code == "CONTRACT_VERSION_UNSUPPORTED"

    def test_a_request_cannot_carry_a_field_the_contract_does_not_declare(self) -> None:
        """A model that adds a limit, a mount or a network to its request meets a refusal."""
        for field in ("memory", "network", "mount", "image", "privileged", "user", "volumes"):
            payload = request("shell.exec", {"command": "true"}, run_id="run-1")
            payload[field] = "unlimited"
            with pytest.raises(ContractError) as refused:
                ToolExecutionRequest.from_dict(payload)
            assert refused.value.code == "CONTRACT_UNKNOWN_FIELD", field

    def test_a_missing_required_field_is_refused(self) -> None:
        payload = request("filesystem.read", {"path": "a.txt"}, run_id="run-1")
        del payload["policy"]
        with pytest.raises(ContractError) as refused:
            ToolExecutionRequest.from_dict(payload)
        assert refused.value.code == "CONTRACT_MISSING_FIELD"

    def test_no_exit_code_is_invented_for_a_command_that_never_started(self) -> None:
        with pytest.raises(ContractError) as refused:
            CommandExecution(started=False, exit_code=0, stdout="", stderr="", duration_ms=0)
        assert refused.value.code == "EXIT_CODE_FABRICATED"
        honest = CommandExecution(started=False, exit_code=None, stdout="", stderr="",
                                  duration_ms=0)
        assert honest.to_dict()["exitCode"] is None

    def test_the_result_round_trips_with_its_artifacts(self) -> None:
        artifact = ArtifactReference(artifact_id="a1", kind="sandbox.stdout", bucket="b",
                                     key="k", size_bytes=3, sha256="0" * 64)
        result = ToolExecutionResult(tool_request_id="t1", tool="shell.exec", status="SUCCEEDED",
                                     output={"exitCode": 0}, exit_code=0, duration_ms=5,
                                     truncated=True, artifacts=(artifact,))
        assert ToolExecutionResult.from_dict(result.to_dict()) == result

    def test_the_status_vocabulary_is_closed(self) -> None:
        for status in TOOL_EXECUTION_STATUSES:
            ToolExecutionResult(tool_request_id="t", tool="x", status=status)
        with pytest.raises(ContractError):
            ToolExecutionResult(tool_request_id="t", tool="x", status="MAYBE")

    def test_the_agent_sees_a_cancellation_as_a_failure_it_cannot_misread(self) -> None:
        for status in ("CANCELLED", "INTERRUPTED"):
            result = ToolExecutionResult(tool_request_id="t", tool="shell.exec", status=status)
            assert result.agent_result()["status"] == "FAILED"
        agent = ToolExecutionResult(tool_request_id="t", tool="shell.exec", status="SUCCEEDED",
                                    exit_code=0, session_id="s").agent_result()
        assert agent["metadata"] == {"executor": "sandbox", "tool": "shell.exec",
                                     "sandboxSession": "s"}

    def test_the_session_workspace_and_operations_have_closed_vocabularies(self) -> None:
        workspace = Workspace(workspace_id="w", source=WorkspaceSource())
        assert Workspace.from_dict(workspace.to_dict()) == workspace
        with pytest.raises(ContractError):
            SandboxSession(session_id="s", run_id="r", policy="developer", state="HALF_ALIVE",
                           workspace=workspace, container_name="c", image="i",
                           network_profile="none")
        with pytest.raises(ContractError):
            FileOperation(operation="chmod", path="a")
        with pytest.raises(ContractError):
            GitOperation(verb="push")
        with pytest.raises(ContractError):
            WorkspaceSource(kind="host-directory")
        with pytest.raises(ContractError):
            WorkspaceSource(kind="snapshot")
