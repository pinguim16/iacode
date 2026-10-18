"""Actual source/filesystem and owned lifecycle controls, not a substitute for real SQL/HTTP."""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import os
import uuid
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from iacode_api.knowledge import sources as source_module
from iacode_api.knowledge.runtime import KnowledgeRuntime
from iacode_api.knowledge.sources import CurrentKnowledgeSources, read_confined
from iacode_api.routes.knowledge import _call
from iacode_common.secret_scanning import find_secret_kinds
from iacode_knowledge.domain import KnowledgeError, canonical, load_policy
from iacode_telemetry.logging import JsonLogFormatter

from tests.knowledge_fixture import deploy_source, mutate_grant


def policy():
    root = next(
        parent
        for parent in Path(__file__).resolve().parents
        if (parent / ".iacode/policies/knowledge-policy.json").is_file()
    )
    return load_policy(root / ".iacode/policies/knowledge-policy.json")


def rig(tmp_path):
    now = datetime.now(UTC)
    project = str(uuid.uuid4())
    fixture = deploy_source(tmp_path, project, now)
    source = CurrentKnowledgeSources(tmp_path, policy(), None, ())
    return source, project, fixture, now


def test_unconfigured_authentication_never_reaches_any_knowledge_operation(client):
    root = "/api/v1/knowledge/projects/invalid"
    for method, suffix in (
        ("POST", "/ingestions"),
        ("POST", "/search"),
        ("GET", "/documents"),
        ("GET", "/documents/invalid"),
        ("GET", "/documents/invalid/export"),
        ("GET", "/documents/invalid/chunks/invalid"),
        ("DELETE", "/documents/invalid"),
    ):
        response = client.request(method, root + suffix)
        assert response.status_code == 503
        assert response.json()["code"] == "AUTHENTICATED_RUNTIME_REQUIRED"
        assert "invalid" not in response.text


async def test_actual_files_roundtrip_exact_content_and_grant(tmp_path):
    sources, project, fixture, now = rig(tmp_path)
    entry = fixture["entry"]
    actual = await sources.load(
        project, "curated", entry["sourceId"], entry["revision"], now, capture=True
    )
    assert actual.artifact.text == fixture["artifact"]["text"]
    assert (
        actual.entry.sourceDigest
        == hashlib.sha256((tmp_path / entry["artifactPath"]).read_bytes()).hexdigest()
    )
    assert (
        actual.entry.grantDigest
        == hashlib.sha256((tmp_path / entry["grantPath"]).read_bytes()).hexdigest()
    )
    assert actual.grant.ragAllowed is True and actual.grant.trainingAllowed is False


async def test_denied_grant_is_checked_before_actual_source_body_read(tmp_path, monkeypatch):
    sources, project, fixture, now = rig(tmp_path)
    entry = fixture["entry"]
    mutate_grant(tmp_path, entry, {"ragAllowed": False})
    observed = []
    actual = source_module.read_confined

    def observe(root, path, maximum):
        observed.append(path)
        return actual(root, path, maximum)

    monkeypatch.setattr(source_module, "read_confined", observe)
    with pytest.raises(KnowledgeError) as caught:
        await sources.load(
            project, "curated", entry["sourceId"], entry["revision"], now, capture=True
        )
    assert caught.value.code == "REUSE_PERMISSION_DENIED"
    assert entry["grantPath"] in observed and entry["artifactPath"] not in observed


async def test_wrong_project_never_opens_another_projects_grant_or_artifact(tmp_path, monkeypatch):
    sources, _project, fixture, now = rig(tmp_path)
    observed = []
    actual = source_module.read_confined

    def observe(root, path, maximum):
        observed.append(path)
        return actual(root, path, maximum)

    monkeypatch.setattr(source_module, "read_confined", observe)
    with pytest.raises(KnowledgeError) as caught:
        await sources.load(
            str(uuid.uuid4()),
            "curated",
            fixture["entry"]["sourceId"],
            "fixture-v1",
            now,
            capture=True,
        )
    assert caught.value.code == "SOURCE_NOT_FOUND" and observed == ["registry.json"]


async def test_actual_source_change_and_missing_bytes_fail_closed(tmp_path):
    sources, project, fixture, now = rig(tmp_path)
    entry = fixture["entry"]
    path = tmp_path / entry["artifactPath"]
    original = path.read_bytes()
    path.write_bytes(original + b" ")
    with pytest.raises(KnowledgeError) as caught:
        await sources.load(
            project, "curated", entry["sourceId"], entry["revision"], now, capture=False
        )
    assert caught.value.code == "SOURCE_CHANGED"
    path.unlink()
    with pytest.raises(KnowledgeError) as caught:
        await sources.load(
            project, "curated", entry["sourceId"], entry["revision"], now, capture=False
        )
    assert caught.value.code == "SOURCE_OBJECT_UNAVAILABLE"


async def test_actual_revocation_and_grant_tamper_are_not_cached(tmp_path):
    sources, project, fixture, now = rig(tmp_path)
    entry = fixture["entry"]
    await sources.load(project, "curated", entry["sourceId"], entry["revision"], now, capture=False)
    mutate_grant(tmp_path, entry, {"status": "REVOKED"})
    with pytest.raises(KnowledgeError) as caught:
        await sources.load(
            project, "curated", entry["sourceId"], entry["revision"], now, capture=False
        )
    assert caught.value.code == "SOURCE_REVOKED"
    (tmp_path / entry["grantPath"]).write_bytes(b"{}")
    with pytest.raises(KnowledgeError) as caught:
        await sources.load(
            project, "curated", entry["sourceId"], entry["revision"], now, capture=False
        )
    assert caught.value.code == "SOURCE_CHANGED"


def test_actual_path_confinement_refuses_traversal_absolute_alias_and_symlink(tmp_path):
    (tmp_path / "allowed.json").write_bytes(b"{}")
    assert read_confined(tmp_path, "allowed.json", 20) == b"{}"
    for path in (
        "../outside.json",
        "/outside.json",
        "C:/outside.json",
        "./allowed.json",
        "folder/../allowed.json",
        "folder\\allowed.json",
        "folder//allowed.json",
    ):
        with pytest.raises(KnowledgeError) as caught:
            read_confined(tmp_path, path, 20)
        assert caught.value.code == "SOURCE_PATH_REFUSED"
    link = tmp_path / "redirect.json"
    link.symlink_to(tmp_path / "allowed.json")
    with pytest.raises(KnowledgeError) as caught:
        read_confined(tmp_path, "redirect.json", 20)
    assert caught.value.code == "SOURCE_PATH_REFUSED"


def test_actual_nonregular_hardlinked_and_oversized_files_refused(tmp_path):
    (tmp_path / "ordinary.json").write_bytes(b"{}")
    os.link(tmp_path / "ordinary.json", tmp_path / "hardlink.json")
    (tmp_path / "directory").mkdir()
    for path in ("hardlink.json", "directory"):
        with pytest.raises(KnowledgeError) as caught:
            read_confined(tmp_path, path, 20)
        assert caught.value.code == "SOURCE_PATH_REFUSED"
    os.mkfifo(tmp_path / "fifo")
    with pytest.raises(KnowledgeError) as caught:
        read_confined(tmp_path, "fifo", 20)
    assert caught.value.code == "SOURCE_PATH_REFUSED"
    (tmp_path / "large.json").write_bytes(b" " * 21)
    with pytest.raises(KnowledgeError) as caught:
        read_confined(tmp_path, "large.json", 20)
    assert caught.value.code == "SOURCE_LIMIT_EXCEEDED"


async def test_actual_secret_and_private_source_fields_refused(tmp_path):
    sources, project, _fixture, now = rig(tmp_path)
    marker = "gh" + "p_" + "q" * 24
    assert find_secret_kinds(marker)
    for text in (marker,):
        changed = deploy_source(tmp_path, project, now, text=text)
        with pytest.raises(KnowledgeError) as caught:
            await sources.load(
                project, "curated", changed["entry"]["sourceId"], "fixture-v1", now, capture=True
            )
        assert caught.value.code == "SECRET_MATERIAL_REFUSED"
    changed = deploy_source(tmp_path, project, now)
    artifact = {**changed["artifact"], "privateReasoning": "untrusted transcript"}
    raw = canonical(artifact)
    (tmp_path / changed["entry"]["artifactPath"]).write_bytes(raw)
    registry = json.loads((tmp_path / "registry.json").read_bytes())
    registry["sources"][0]["sourceDigest"] = hashlib.sha256(raw).hexdigest()
    (tmp_path / "registry.json").write_bytes(canonical(registry))
    mutate_grant(tmp_path, changed["entry"], {"sourceDigest": hashlib.sha256(raw).hexdigest()})
    with pytest.raises(KnowledgeError) as caught:
        await sources.load(
            project, "curated", changed["entry"]["sourceId"], "fixture-v1", now, capture=True
        )
    assert caught.value.code == "KNOWLEDGE_CONTRACT_INVALID"


async def test_source_grant_mismatch_expiry_unknown_fields_and_invalid_utf8_refused(tmp_path):
    sources, project, fixture, now = rig(tmp_path)
    entry = fixture["entry"]
    for changed, code in (
        ({"projectId": str(uuid.uuid4())}, "SOURCE_SCOPE_MISMATCH"),
        ({"validUntil": now.isoformat()}, "SOURCE_GRANT_EXPIRED"),
        ({"privateReasoning": "untrusted"}, "KNOWLEDGE_CONTRACT_INVALID"),
    ):
        fixture = deploy_source(tmp_path, project, now)
        mutate_grant(tmp_path, fixture["entry"], changed)
        with pytest.raises(KnowledgeError) as caught:
            await sources.load(
                project, "curated", entry["sourceId"], entry["revision"], now, capture=True
            )
        assert caught.value.code == code
    (tmp_path / "registry.json").write_bytes(b'{"sources":"\xff"}')
    with pytest.raises(KnowledgeError) as caught:
        await sources.load(
            project, "curated", entry["sourceId"], entry["revision"], now, capture=True
        )
    assert caught.value.code == "JSON_INVALID"


def test_knowledge_access_logs_mask_query_target_but_keep_route_status():
    marker = "untrusted-search-marker"
    for prefix in ("/api/v1/knowledge/", "/API/v1/KNOWLEDGE/", "/%61pi/v1/knowledge/"):
        record = logging.LogRecord(
            "uvicorn.access",
            logging.INFO,
            "fixture",
            1,
            "%s %s %s %s %s",
            ("127.0.0.1", "POST", prefix + marker + "?query=" + marker, "1.1", 400),
            None,
        )
        body = json.loads(JsonLogFormatter("api").format(record))
        assert marker not in json.dumps(body)
        assert body["message"] == "POST /api/v1/knowledge/<scoped> 400"


def test_knowledge_error_correlation_does_not_echo_caller_material(client):
    marker = "untrusted-search-marker"
    for prefix in ("/api/v1/knowledge", "/API/v1/KNOWLEDGE"):
        response = client.get(prefix + "/projects/invalid", headers={"X-Correlation-ID": marker})
        assert response.status_code in (404, 503)
        assert marker not in response.text
        assert response.headers["X-Correlation-ID"] != marker


async def test_runtime_owns_task_and_awaits_shutdown_without_dependency_io():
    runtime = KnowledgeRuntime(
        SimpleNamespace(policy=SimpleNamespace(sweepIntervalSeconds=3600)), AsyncMock(), None
    )
    runtime.start()
    task = runtime.task
    with pytest.raises(RuntimeError, match="already owned"):
        runtime.start()
    await asyncio.sleep(0)
    await runtime.close()
    assert task.cancelled() and runtime.task is None
    runtime.store.sweep.assert_not_awaited()
    await runtime.close()


async def test_runtime_unexpected_task_failure_is_not_hidden():
    async def fail():
        raise RuntimeError("owned task failed")

    task = asyncio.create_task(fail())
    await asyncio.sleep(0)
    runtime = KnowledgeRuntime(None, None, None, task)
    with pytest.raises(RuntimeError, match="owned task failed"):
        await runtime.close()


async def test_dependency_failure_has_sanitized_observable_code_not_empty_success(caplog):
    async def fail():
        raise ValueError("private-diagnostic-marker")

    runtime = SimpleNamespace(
        service=SimpleNamespace(policy=SimpleNamespace(operationTimeoutSeconds=1))
    )
    with pytest.raises(KnowledgeError) as caught:
        await _call(runtime, fail)
    assert caught.value.code == "KNOWLEDGE_DEPENDENCY_UNAVAILABLE"
    assert "knowledge dependency failed" in caplog.text
    assert "private-diagnostic-marker" not in caplog.text


async def test_operation_timeout_is_a_real_bound_not_empty_success():
    async def slow():
        await asyncio.sleep(10)

    runtime = SimpleNamespace(
        service=SimpleNamespace(policy=SimpleNamespace(operationTimeoutSeconds=1))
    )
    with pytest.raises(KnowledgeError) as caught:
        await _call(runtime, slow)
    assert caught.value.code == "KNOWLEDGE_TIMEOUT"
