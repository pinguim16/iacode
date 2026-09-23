"""Sessions on the real engine: provisioning, lifecycle, release, recovery and expiry."""

from __future__ import annotations

import asyncio
import hashlib
import io
import tarfile
import tempfile
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from iacode_sandbox.backend import DockerBackend
from iacode_sandbox.service import SandboxService
from iacode_sandbox.snapshots import SnapshotError, build_snapshot
from sandbox_fixtures import engine_harness, request


class MemorySnapshots:
    """A snapshot reader over archives held in memory, checked by digest like the real one."""

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


def container_exists(name: str) -> bool:
    return DockerBackend().inspect(name) is not None


class SessionLifecycleTests:
    def test_a_session_is_created_ready_and_removed_with_its_run(self, harness) -> None:
        run_id = harness.run_id()
        harness.shell("true", run_id=run_id)
        session = harness.session(run_id)
        assert session.state == "READY"
        assert container_exists(session.container_name)
        assert asyncio.run(harness.service.release_run(run_id)) == 1
        assert not container_exists(session.container_name)
        stored = asyncio.run(harness.store.session(session.session_id))
        assert stored.state == "STOPPED" and stored.stopped_at is not None

    def test_a_running_tool_holds_the_session_in_running(self, harness) -> None:
        run_id = harness.run_id()
        harness.shell("true", run_id=run_id)
        states: list[str] = []

        async def observe():
            task = asyncio.ensure_future(harness.service.execute(request(
                "shell.exec", {"command": "sleep 3"}, run_id=run_id)))
            await asyncio.sleep(1.5)
            states.append((await harness.store.active_session_for_run(run_id)).state)
            await task
            states.append((await harness.store.active_session_for_run(run_id)).state)

        asyncio.run(observe())
        assert states == ["RUNNING", "READY"]

    def test_inspect_reports_the_store_and_the_engine(self, harness) -> None:
        run_id = harness.run_id()
        harness.shell("true", run_id=run_id)
        session = harness.session(run_id)
        seen = asyncio.run(harness.service.inspect(session.session_id))
        assert seen["state"] == "READY" and seen["containerState"] == "running"


class WorkspaceProvisioningTests:
    def test_a_snapshot_provisions_the_workspace_as_a_repository(self, harness) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory)
            (source / "calc.py").write_text("def add(a, b):\n    return a - b\n",
                                            encoding="utf-8")
            (source / "tests").mkdir()
            (source / "tests" / "test_calc.py").write_text("import calc\n", encoding="utf-8")
            archive = build_snapshot(source)
        checksum = harness.service.snapshot_reader.add("snapshot-1", archive)
        run_id = harness.run_id()
        result = asyncio.run(harness.service.execute(request(
            "git.log", {"maxCount": 3}, run_id=run_id,
            workspace={"kind": "snapshot", "artifactId": "snapshot-1", "checksum": checksum})))
        assert result.status == "SUCCEEDED", result
        assert "Workspace snapshot" in result.output["stdout"]
        listing = harness.execute("filesystem.list", {"path": ".", "depth": 2}, run_id=run_id)
        paths = {entry["path"] for entry in listing.output["entries"]}
        assert {"calc.py", "tests", "tests/test_calc.py"} <= paths

    def test_an_unsafe_snapshot_is_refused_and_no_session_survives(self, harness) -> None:
        buffer = io.BytesIO()
        with tarfile.open(fileobj=buffer, mode="w:gz") as archive:
            link = tarfile.TarInfo("escape")
            link.type = tarfile.SYMTYPE
            link.linkname = "/etc"
            archive.addfile(link)
        checksum = harness.service.snapshot_reader.add("hostile", buffer.getvalue())
        run_id = harness.run_id()
        result = asyncio.run(harness.service.execute(request(
            "git.status", {}, run_id=run_id,
            workspace={"kind": "snapshot", "artifactId": "hostile", "checksum": checksum})))
        assert (result.status, result.error_code) == ("FAILED", "SNAPSHOT_UNSAFE")
        assert harness.session(run_id) is None

    def test_a_snapshot_with_a_different_digest_is_refused(self, harness) -> None:
        with tempfile.TemporaryDirectory() as directory:
            (Path(directory) / "a.txt").write_text("a", encoding="utf-8")
            archive = build_snapshot(Path(directory))
        harness.service.snapshot_reader.add("snapshot-2", archive)
        run_id = harness.run_id()
        result = asyncio.run(harness.service.execute(request(
            "git.status", {}, run_id=run_id,
            workspace={"kind": "snapshot", "artifactId": "snapshot-2", "checksum": "0" * 64})))
        assert (result.status, result.error_code) == ("FAILED", "SNAPSHOT_CHECKSUM_MISMATCH")
        assert harness.session(run_id) is None
        leftover = DockerBackend().managed(harness.service.owner)
        assert leftover == [], "a failed session left a container"

    def test_the_snapshot_builder_refuses_a_link(self) -> None:
        import os

        with tempfile.TemporaryDirectory() as directory:
            os.symlink("/etc/passwd", Path(directory) / "leak")
            with pytest.raises(SnapshotError) as refused:
                build_snapshot(Path(directory))
        assert refused.value.code == "SNAPSHOT_SOURCE_UNSAFE"


class RecoveryTests:
    def test_a_restarted_service_keeps_a_live_session_and_removes_an_orphan(self, harness) -> None:
        run_id = harness.run_id()
        harness.shell("echo kept > kept.txt", run_id=run_id)
        live = harness.session(run_id)

        orphan_store = engine_harness(owner=harness.service.owner)
        orphan_run = orphan_store.run_id()
        orphan_store.shell("true", run_id=orphan_run)
        orphan = orphan_store.session(orphan_run)

        restarted = SandboxService(root=harness.service.root, policies=harness.service.policies,
                                   backend=DockerBackend(), store=harness.store,
                                   artifacts=harness.artifacts, owner=harness.service.owner)
        stranger = engine_harness()
        stranger_run = stranger.run_id()
        stranger.shell("true", run_id=stranger_run)
        report = asyncio.run(restarted.reconcile())

        stranger_name = stranger.session(stranger_run).container_name
        assert container_exists(stranger_name), "a container of another owner was touched"
        stranger.close()
        assert orphan.session_id in report["removed"]
        assert not container_exists(orphan.container_name)
        assert container_exists(live.container_name)
        again = harness.execute("filesystem.read", {"path": "kept.txt"}, run_id=run_id)
        assert again.output["content"] == "kept\n"

    def test_a_session_whose_container_vanished_is_failed_not_trusted(self, harness) -> None:
        run_id = harness.run_id()
        harness.shell("true", run_id=run_id)
        session = harness.session(run_id)
        DockerBackend().remove(session.container_name)
        report = asyncio.run(harness.service.reconcile())
        assert session.session_id in report["lost"]
        assert harness.session(run_id) is None

    def test_an_expired_session_is_swept_and_its_container_removed(self) -> None:
        clock = {"now": datetime.now(UTC)}
        swept = engine_harness(now=lambda: clock["now"])
        try:
            run_id = swept.run_id()
            swept.shell("true", run_id=run_id)
            session = swept.session(run_id)
            clock["now"] = datetime.now(UTC) + timedelta(days=1)
            expired = asyncio.run(swept.service.sweep(limit=5))
            assert session.session_id in expired
            assert not container_exists(session.container_name)
            assert asyncio.run(swept.store.session(session.session_id)).state == "EXPIRED"
        finally:
            swept.close()
