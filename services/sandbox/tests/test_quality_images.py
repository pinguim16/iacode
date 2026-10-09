"""The real quality toolchain images run only through hardened sandbox policies."""

from __future__ import annotations

import asyncio
import hashlib
import tempfile
from pathlib import Path

import pytest
from iacode_sandbox.snapshots import SnapshotError, build_snapshot
from sandbox_fixtures import engine_harness

pytestmark = pytest.mark.engine

TOOLCHAINS = (
    (
        "quality-python",
        "python --version && pytest --version && ruff --version && coverage --version",
        ("Python 3.13.15", "pytest 9.1.1", "ruff 0.16.8", "Coverage.py"),
    ),
    (
        "quality-node",
        "node --version && npm --version && python3 --version",
        ("v22.23.2", "10.9.8", "Python 3.11.2"),
    ),
    (
        "quality-java",
        "java -version 2>&1 && mvn --version && gradle --version && python3 --version",
        ("21.0.10", "Apache Maven 3.9.12", "Gradle 8.14.3", "Python 3.12.3"),
    ),
)


class MemorySnapshots:
    def __init__(self) -> None:
        self.archives: dict[str, bytes] = {}

    def add(self, identifier: str, data: bytes) -> str:
        self.archives[identifier] = data
        return hashlib.sha256(data).hexdigest()

    async def read(self, artifact_id: str, checksum: str | None = None) -> bytes:
        data = self.archives[artifact_id]
        if checksum and hashlib.sha256(data).hexdigest() != checksum:
            raise SnapshotError("SNAPSHOT_CHECKSUM_MISMATCH", "digest mismatch")
        return data


@pytest.fixture
def harness():
    created = engine_harness()
    created.service.snapshot_reader = MemorySnapshots()
    yield created
    created.close()


class QualityImageExecutionTests:
    @pytest.mark.parametrize("policy", [item[0] for item in TOOLCHAINS])
    def test_every_quality_helper_provisions_a_real_snapshot(self, harness, policy: str) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory)
            (source / "quality.txt").write_text("snapshot=true\n", encoding="utf-8")
            archive = build_snapshot(source)
        checksum = harness.service.snapshot_reader.add(f"snapshot-{policy}", archive)
        run_id = harness.run_id()
        result = asyncio.run(
            harness.service.execute(
                {
                    "contractVersion": "1.0.0",
                    "toolRequestId": harness.run_id(),
                    "runId": run_id,
                    "agentRunId": None,
                    "agent": "quality-engine",
                    "tool": "shell.exec",
                    "arguments": {"command": "test -f quality.txt"},
                    "policy": policy,
                    "workspace": {
                        "kind": "snapshot",
                        "artifactId": f"snapshot-{policy}",
                        "checksum": checksum,
                    },
                }
            )
        )
        assert result.status == "SUCCEEDED", result

    @pytest.mark.parametrize(("policy", "command", "expected"), TOOLCHAINS)
    def test_pinned_toolchain_runs_in_its_real_sandbox(
        self, harness, policy: str, command: str, expected: tuple[str, ...]
    ) -> None:
        run_id = harness.run_id()
        result = harness.shell(command, run_id=run_id, policy=policy)
        assert result.status == "SUCCEEDED", result
        output = str(result.output.get("stdout", "")) + str(result.output.get("stderr", ""))
        assert all(item in output for item in expected), output
        session = harness.session(run_id)
        assert session.policy == policy
        assert session.network_profile == "none"
        assert f"sandbox-{policy}" in session.image

    @pytest.mark.parametrize("policy", [item[0] for item in TOOLCHAINS])
    def test_quality_sandbox_cannot_open_an_internet_socket(self, harness, policy: str) -> None:
        run_id = harness.run_id()
        result = harness.shell(
            "python3 -c \"import socket; socket.create_connection(('1.1.1.1', 53), 0.2)\"",
            run_id=run_id,
            policy=policy,
        )
        assert result.status == "FAILED"
        assert result.exit_code not in (None, 0)

    @pytest.mark.parametrize("policy", [item[0] for item in TOOLCHAINS])
    def test_secret_and_diff_controls_are_available_offline(self, harness, policy: str) -> None:
        run_id = harness.run_id()
        command = (
            "printf 'safe=true\\n' > quality.txt && iacode-quality-secret-scan && "
            "git init -q && git add -A && git diff --cached --check"
        )
        result = harness.shell(command, run_id=run_id, policy=policy)
        assert result.status == "SUCCEEDED", result
        assert "QUALITY_SECRET_SCAN=PASS" in str(result.output.get("stdout", ""))

    @pytest.mark.parametrize("policy", [item[0] for item in TOOLCHAINS])
    def test_a_non_allowlisted_credential_shape_fails_the_secret_check(
        self, harness, policy: str
    ) -> None:
        run_id = harness.run_id()
        command = (
            "printf 'API_' > leaked.env; "
            "printf 'KEY=realistic-unreviewed-value-928471\\n' >> leaked.env; "
            "iacode-quality-secret-scan; test $? -eq 1"
        )
        result = harness.shell(command, run_id=run_id, policy=policy)
        assert result.status == "SUCCEEDED", result
        assert "QUALITY_SECRET_SCAN=FAIL" in str(result.output.get("stdout", ""))
