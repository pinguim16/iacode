"""Ingress and owned lifecycle decisions, not mock integration acceptance."""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from iacode_api.config import settings_for_tests
from iacode_api.experience.runtime import ExperienceRuntime, build_experience_runtime
from iacode_experience.domain import ExperienceError, require_safe
from iacode_persistence.models import Experience
from iacode_telemetry.logging import JsonLogFormatter
from sqlalchemy import CheckConstraint, UniqueConstraint


def test_legacy_unauthenticated_mode_never_reaches_experience_data(client):
    root = "/api/v1/experiences"
    for method, path in (
        ("POST", "/projects/invalid"),
        ("GET", "/projects/invalid"),
        ("GET", "/sources/invalid"),
        ("GET", "/projects/invalid/invalid/export"),
        ("DELETE", "/projects/invalid/invalid"),
    ):
        response = client.request(method, root + path)
        assert response.status_code == 503
        assert response.json()["code"] == "AUTHENTICATED_RUNTIME_REQUIRED"
        assert "invalid" not in response.text


def test_experience_access_log_masks_target_not_observability():
    marker = "opaque-" + "ab42" * 8
    record = logging.LogRecord(
        "uvicorn.access",
        logging.INFO,
        "fixture",
        1,
        "%s %s %s %s %s",
        ("127.0.0.1", "GET", "/api/v1/experiences/" + marker + "?q=" + marker, "1.1", 400),
        None,
    )
    body = json.loads(JsonLogFormatter("api").format(record))
    assert marker not in json.dumps(body)
    assert body["message"] == "GET /api/v1/experiences/<scoped> 400"
    assert body["logger"] == "uvicorn.access"
    for prefix in ("/API/v1/EXPERIENCES/", "/%61pi/v1/experiences/"):
        alternate = logging.LogRecord(
            "uvicorn.access",
            logging.INFO,
            "fixture",
            1,
            "%s %s %s %s %s",
            ("127.0.0.1", "GET", prefix + marker + "?q=" + marker, "1.1", 404),
            None,
        )
        masked = json.loads(JsonLogFormatter("api").format(alternate))
        assert marker not in json.dumps(masked)
        assert masked["message"] == "GET /api/v1/experiences/<scoped> 404"
    control = logging.LogRecord(
        "other", logging.INFO, "fixture", 1, "ordinary observable event", (), None
    )
    assert (
        json.loads(JsonLogFormatter("api").format(control))["message"]
        == "ordinary observable event"
    )


def test_experience_correlation_is_generated_not_untrusted_header_material(client):
    marker = "opaque-" + "ab42" * 8
    for prefix in ("/api/v1/experiences", "/API/v1/EXPERIENCES"):
        response = client.get(prefix + "/projects/invalid", headers={"X-Correlation-ID": marker})
        assert response.status_code in (404, 503)
        assert response.headers["X-Correlation-ID"] != marker
        assert marker not in response.text


async def test_retention_owned_task_has_explicit_start_and_awaited_shutdown():
    runtime = ExperienceRuntime(
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


async def test_retention_unexpected_task_failure_is_not_silently_consumed():
    async def fail():
        raise RuntimeError("owned task failed")

    task = asyncio.create_task(fail())
    await asyncio.sleep(0)
    runtime = ExperienceRuntime(None, None, None, task)
    with pytest.raises(RuntimeError, match="owned task failed"):
        await runtime.close()


def test_experience_constraint_names_respect_their_actual_kind():
    uniques = {
        item.name for item in Experience.__table__.constraints if isinstance(item, UniqueConstraint)
    }
    checks = {
        item.name for item in Experience.__table__.constraints if isinstance(item, CheckConstraint)
    }
    assert uniques == {"uq_experiences_project_request", "uq_experiences_project_source"}
    assert checks == {"ck_experiences_schema_version_known", "ck_experiences_current_shape"}


def test_public_minio_identity_is_not_a_bearer_secret_but_storage_password_stays_protected(
    monkeypatch,
):
    root = next(
        parent
        for parent in Path(__file__).resolve().parents
        if (parent / "agents").is_dir() and (parent / ".iacode/policies").is_dir()
    )
    # This tests the actual runtime credential projection, not an operational credential. Every
    # provider environment name is explicitly empty so a failed assertion cannot print a real key.
    providers = json.loads((root / ".iacode/policies/providers.json").read_bytes())["providers"]
    for provider in providers:
        monkeypatch.setenv(provider["credential_env"], "")
    material = hashlib.sha256(
        b"explicit nonoperational database and Redis guard fixture"
    ).hexdigest()
    settings = settings_for_tests(
        repository_root=str(root),
        gateway_policy_dir=str(root / ".iacode/policies"),
        minio_access_key="iacode",
        database_url="postgresql+asyncpg://fixture:" + material + "@localhost:5432/fixture",
        redis_url="redis://fixture:" + material + "@localhost:6379/1",
    )
    runtime = build_experience_runtime(settings, None, None, None)
    # The committed public account identity also occurs in legitimate package/report names.
    require_safe(b"iacode-quality-python-pass", runtime.service.known_credentials)
    with pytest.raises(ExperienceError) as caught:
        require_safe(
            settings.minio_secret_key.get_secret_value().encode(), runtime.service.known_credentials
        )
    assert caught.value.code == "AUTHORIZATION_MATERIAL_REFUSED"
    with pytest.raises(ExperienceError) as caught:
        require_safe(material.encode(), runtime.service.known_credentials)
    assert caught.value.code == "AUTHORIZATION_MATERIAL_REFUSED"
