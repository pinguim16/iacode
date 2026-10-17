"""Authenticated, project-bound factual capture; no arbitrary document/reuse ingestion."""

from __future__ import annotations

import re
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, FastAPI, Request
from fastapi.responses import JSONResponse
from iacode_experience.domain import ExperienceError, parse_capture, require_safe
from iacode_telemetry.logging import get_logger

from iacode_api.dependencies import get_resources

logger = get_logger(__name__)
router = APIRouter(prefix="/api/v1/experiences", tags=["experiences"])
UUID_PATTERN = re.compile(r"[0-9a-f]{8}-(?:[0-9a-f]{4}-){3}[0-9a-f]{12}")


def _identifier(value: str) -> str:
    if not UUID_PATTERN.fullmatch(value):
        raise ExperienceError("IDENTITY_INVALID")
    return value


def _runtime(request: Request, allowed: set[str]) -> Any:
    resources = get_resources(request)
    if not resources.settings.desktop_token.get_secret_value():
        raise ExperienceError("AUTHENTICATED_RUNTIME_REQUIRED")
    pairs = list(request.query_params.multi_items())
    if len(pairs) != len(dict(pairs)) or any(key not in allowed for key, _ in pairs):
        raise ExperienceError("QUERY_CONTRACT_INVALID")
    return resources.experience


async def _call(action: Callable[[], Awaitable[Any]]) -> Any:
    try:
        return await action()
    except ExperienceError:
        raise
    except Exception as error:
        logger.error(
            "experience dependency failed",
            extra={"code": "EXPERIENCE_DEPENDENCY_UNAVAILABLE", "errorType": type(error).__name__},
        )
        raise ExperienceError("EXPERIENCE_DEPENDENCY_UNAVAILABLE") from error


def _summary(stored: Any) -> dict:
    return {
        "experienceId": stored.experience_id,
        "projectId": stored.project_id,
        "sourceRunId": stored.source_run_id,
        "contentDigest": stored.content_digest,
        "createdAt": stored.created_at.isoformat(),
        "expiresAt": stored.expires_at.isoformat(),
        "state": stored.state,
    }


def register_experience_errors(app: FastAPI) -> None:
    @app.exception_handler(ExperienceError)
    async def handle(request: Request, error: ExperienceError) -> JSONResponse:
        if error.code.endswith("NOT_FOUND"):
            status = 404
        elif error.code.endswith("CONFLICT"):
            status = 409
        elif error.code in ("EXPERIENCE_UNAVAILABLE", "LEGACY_QUARANTINED"):
            status = 410
        elif error.code in (
            "AUTHENTICATED_RUNTIME_REQUIRED",
            "EXPERIENCE_DEPENDENCY_UNAVAILABLE",
            "SOURCE_OBJECT_UNAVAILABLE",
            "SECRET_SCAN_UNAVAILABLE",
        ):
            status = 503
        elif error.code == "REUSE_PERMISSION_DENIED":
            status = 403
        elif error.code == "CONTENT_TOO_LARGE":
            status = 413
        else:
            status = 400
        return JSONResponse(
            status_code=status,
            headers={"Cache-Control": "no-store"},
            content={
                "code": error.code,
                "message": "experience operation refused",
                "correlationId": getattr(request.state, "correlation_id", None),
            },
        )


@router.get("/sources/{run_id}")
async def candidate(request: Request, run_id: str) -> JSONResponse:
    runtime = _runtime(request, set())
    value = await _call(lambda: runtime.sources.candidates(_identifier(run_id)))
    return JSONResponse(value, headers={"Cache-Control": "no-store"})


@router.post("/projects/{project_id}")
async def capture(request: Request, project_id: str) -> JSONResponse:
    runtime = _runtime(request, set())
    _identifier(project_id)
    raw = bytearray()
    async for part in request.stream():
        if len(raw) + len(part) > runtime.service.policy.maxRequestBytes:
            raise ExperienceError("CONTENT_TOO_LARGE")
        raw.extend(part)
    payload = parse_capture(bytes(raw), runtime.service.policy, runtime.service.known_credentials)
    row = await _call(lambda: runtime.service.capture(project_id, payload))
    return JSONResponse(
        {**_summary(row), "idempotentReplay": row.replay, "document": row.body},
        status_code=200 if row.replay else 201,
        headers={"Cache-Control": "no-store"},
    )


@router.get("/projects/{project_id}")
async def listing(request: Request, project_id: str) -> JSONResponse:
    runtime = _runtime(request, {"cursor", "limit", "use"})
    _identifier(project_id)
    if request.query_params.get("use", "storage") != "storage":
        raise ExperienceError("REUSE_PERMISSION_DENIED")
    limit_text = request.query_params.get("limit", "25")
    if not re.fullmatch(r"[1-9][0-9]?", limit_text):
        raise ExperienceError("PAGE_LIMIT_INVALID")
    limit = int(limit_text)
    after = None
    if "cursor" in request.query_params:
        scope, separator, cursor = request.query_params["cursor"].partition(":")
        if separator != ":" or scope != project_id:
            raise ExperienceError("CURSOR_SCOPE_INVALID")
        after = _identifier(cursor)
    rows = await _call(lambda: runtime.store.page(project_id, after, limit, datetime.now(UTC)))
    # No full bodies in a page; verify each eligible record before even its digest is disclosed.
    for row in rows:
        await _call(lambda row=row: runtime.service.deliver(row))
    return JSONResponse(
        {
            "experiences": [_summary(row) for row in rows],
            "nextCursor": f"{project_id}:{rows[-1].experience_id}" if len(rows) == limit else None,
        },
        headers={"Cache-Control": "no-store"},
    )


async def _read(request: Request, project_id: str, experience_id: str) -> JSONResponse:
    runtime = _runtime(request, {"use"})
    _identifier(project_id)
    _identifier(experience_id)
    if request.query_params.get("use", "storage") != "storage":
        raise ExperienceError("REUSE_PERMISSION_DENIED")
    row = await _call(lambda: runtime.store.get(project_id, experience_id))
    document = await _call(lambda: runtime.service.deliver(row))
    # Normalized exact body was re-scanned by deliver; envelope contains only validated IDs/hashes.
    result = {**_summary(row), "document": document.model_dump(mode="json")}
    from iacode_experience.domain import canonical

    require_safe(canonical(result), runtime.service.known_credentials)
    return JSONResponse(result, headers={"Cache-Control": "no-store"})


@router.get("/projects/{project_id}/{experience_id}")
async def inspect(request: Request, project_id: str, experience_id: str) -> JSONResponse:
    return await _read(request, project_id, experience_id)


@router.get("/projects/{project_id}/{experience_id}/export")
async def export(request: Request, project_id: str, experience_id: str) -> JSONResponse:
    response = await _read(request, project_id, experience_id)
    response.headers["Content-Disposition"] = 'attachment; filename="experience.json"'
    return response


@router.delete("/projects/{project_id}/{experience_id}")
async def withdraw(request: Request, project_id: str, experience_id: str) -> JSONResponse:
    runtime = _runtime(request, set())
    _identifier(project_id)
    _identifier(experience_id)
    row = await _call(lambda: runtime.store.withdraw(project_id, experience_id))
    return JSONResponse(_summary(row), headers={"Cache-Control": "no-store"})
