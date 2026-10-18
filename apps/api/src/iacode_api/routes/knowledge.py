"""Authenticated project-bound knowledge, current exact citations and explicit withdrawal."""

from __future__ import annotations

import asyncio
import re
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, FastAPI, Request
from fastapi.responses import JSONResponse
from iacode_knowledge.domain import (
    INVALID_SOURCE_CODES,
    KnowledgeError,
    parse_ingest,
    parse_search,
)
from iacode_telemetry.logging import get_logger

from iacode_api.dependencies import get_resources

logger = get_logger(__name__)
router = APIRouter(prefix="/api/v1/knowledge", tags=["knowledge"])
UUID_PATTERN = re.compile(r"[0-9a-f]{8}-(?:[0-9a-f]{4}-){3}[0-9a-f]{12}")


def _identifier(value: str) -> str:
    if not UUID_PATTERN.fullmatch(value):
        raise KnowledgeError("IDENTITY_INVALID")
    return value


def _runtime(request: Request, allowed: set[str]) -> Any:
    resources = get_resources(request)
    if not resources.settings.desktop_token.get_secret_value():
        raise KnowledgeError("AUTHENTICATED_RUNTIME_REQUIRED")
    pairs = list(request.query_params.multi_items())
    if len(pairs) != len(dict(pairs)) or any(key not in allowed for key, _ in pairs):
        raise KnowledgeError("QUERY_CONTRACT_INVALID")
    return resources.knowledge


async def _call(runtime: Any, action: Callable[[], Awaitable[Any]]) -> Any:
    try:
        async with asyncio.timeout(runtime.service.policy.operationTimeoutSeconds):
            return await action()
    except KnowledgeError:
        raise
    except TimeoutError as error:
        logger.error("knowledge operation timed out", extra={"code": "KNOWLEDGE_TIMEOUT"})
        raise KnowledgeError("KNOWLEDGE_TIMEOUT") from error
    except Exception as error:
        logger.error(
            "knowledge dependency failed",
            extra={
                "code": "KNOWLEDGE_DEPENDENCY_UNAVAILABLE",
                "errorType": type(error).__name__,
            },
        )
        raise KnowledgeError("KNOWLEDGE_DEPENDENCY_UNAVAILABLE") from error


async def _body(request: Request, runtime: Any) -> bytes:
    raw = bytearray()
    async for part in request.stream():
        if len(raw) + len(part) > runtime.service.policy.maxRequestBytes:
            raise KnowledgeError("CONTENT_TOO_LARGE")
        raw.extend(part)
    return bytes(raw)


def _summary(row: Any) -> dict:
    return {
        "documentId": row.document_id,
        "projectId": row.project_id,
        "sourceKind": row.source_kind,
        "sourceId": row.source_id,
        "revision": row.revision,
        "sourceDigest": row.source_digest,
        "grantDigest": row.grant_digest,
        "contentDigest": row.content_digest,
        "policyDigest": row.policy_digest,
        "createdAt": row.created_at.isoformat(),
        "expiresAt": row.expires_at.isoformat(),
        "state": row.state,
    }


def _response(runtime: Any, value: dict, status: int = 200) -> JSONResponse:
    runtime.service.safe_response(value)
    return JSONResponse(value, status_code=status, headers={"Cache-Control": "no-store"})


def register_knowledge_errors(app: FastAPI) -> None:
    @app.exception_handler(KnowledgeError)
    async def handle(request: Request, error: KnowledgeError) -> JSONResponse:
        code = error.code
        if code in {
            "PROJECT_NOT_FOUND",
            "SOURCE_NOT_FOUND",
            "KNOWLEDGE_NOT_FOUND",
            "CHUNK_NOT_FOUND",
        }:
            status = 404
        elif code in {"REQUEST_CONFLICT", "SOURCE_REVISION_CONFLICT", "INDEX_STALE"}:
            status = 409
        elif code in {
            "KNOWLEDGE_UNAVAILABLE",
            "SOURCE_CHANGED",
            "SOURCE_REVOKED",
            "SOURCE_GRANT_EXPIRED",
            "EXPERIENCE_SOURCE_UNAVAILABLE",
        }:
            status = 410
        elif code in {
            "REUSE_PERMISSION_DENIED",
            "RIGHTS_EVIDENCE_UNVERIFIED",
            "SOURCE_SCOPE_MISMATCH",
        }:
            status = 403
        elif code in {
            "CONTENT_TOO_LARGE",
            "SOURCE_LIMIT_EXCEEDED",
            "RESPONSE_LIMIT_EXCEEDED",
            "INDEX_CAPACITY_EXCEEDED",
            "CHUNK_LIMIT_EXCEEDED",
        }:
            status = 413
        elif code in {
            "AUTHENTICATED_RUNTIME_REQUIRED",
            "KNOWLEDGE_DEPENDENCY_UNAVAILABLE",
            "KNOWLEDGE_TIMEOUT",
            "SOURCE_STORE_UNAVAILABLE",
            "SOURCE_OBJECT_UNAVAILABLE",
            "SECRET_SCAN_UNAVAILABLE",
            "INDEX_CORRUPT",
            "STORED_LIMIT_EXCEEDED",
            "STORED_DIGEST_INVALID",
            "STORED_IDENTITY_INVALID",
            "STORED_RETENTION_INVALID",
        }:
            status = 503
        else:
            status = 400
        return JSONResponse(
            {
                "code": code,
                "message": "knowledge operation refused",
                "correlationId": getattr(request.state, "correlation_id", None),
            },
            status_code=status,
            headers={"Cache-Control": "no-store"},
        )


@router.post("/projects/{project_id}/ingestions")
async def ingest(request: Request, project_id: str) -> JSONResponse:
    runtime = _runtime(request, set())
    _identifier(project_id)
    payload = parse_ingest(
        await _body(request, runtime), runtime.service.policy, runtime.service.known_credentials
    )
    row = await _call(runtime, lambda: runtime.service.ingest(project_id, payload))
    return _response(
        runtime, {**_summary(row), "idempotentReplay": row.replay}, 200 if row.replay else 201
    )


@router.post("/projects/{project_id}/search")
async def search(request: Request, project_id: str) -> JSONResponse:
    runtime = _runtime(request, set())
    _identifier(project_id)
    payload, query_tokens = parse_search(
        await _body(request, runtime), runtime.service.policy, runtime.service.known_credentials
    )
    hits = await _call(runtime, lambda: runtime.service.search(project_id, payload, query_tokens))
    return _response(
        runtime,
        {
            "results": [hit.model_dump(mode="json") for hit in hits],
            "outcome": "MATCHES" if hits else "NO_PERMITTED_MATCH",
            "ranking": "distinct-lexical-overlap; shorter-span; source-id; ordinal; document-id",
            "untrustedContent": True,
        },
    )


@router.get("/projects/{project_id}/documents")
async def listing(request: Request, project_id: str) -> JSONResponse:
    runtime = _runtime(request, {"cursor", "limit"})
    _identifier(project_id)
    limit_text = request.query_params.get("limit", "25")
    if not re.fullmatch(r"[1-9][0-9]?", limit_text):
        raise KnowledgeError("PAGE_LIMIT_INVALID")
    after = None
    if "cursor" in request.query_params:
        scope, separator, after = request.query_params["cursor"].partition(":")
        if separator != ":" or scope != project_id:
            raise KnowledgeError("CURSOR_SCOPE_INVALID")
        _identifier(after)
    rows = await _call(
        runtime, lambda: runtime.store.page(project_id, after, int(limit_text), datetime.now(UTC))
    )
    permitted = []
    for row in rows:
        try:
            await _call(runtime, lambda row=row: runtime.service.deliver(row))
        except KnowledgeError as error:
            if error.code not in INVALID_SOURCE_CODES | {"KNOWLEDGE_UNAVAILABLE"}:
                raise
            continue
        permitted.append(_summary(row))
    return _response(
        runtime,
        {
            "documents": permitted,
            "nextCursor": f"{project_id}:{rows[-1].document_id}"
            if len(rows) == int(limit_text)
            else None,
        },
    )


async def _read(request: Request, project_id: str, document_id: str) -> JSONResponse:
    runtime = _runtime(request, set())
    _identifier(project_id)
    _identifier(document_id)
    row = await _call(runtime, lambda: runtime.store.get(project_id, document_id))
    document = await _call(runtime, lambda: runtime.service.deliver(row))
    return _response(runtime, {**_summary(row), "document": document.model_dump(mode="json")})


@router.get("/projects/{project_id}/documents/{document_id}")
async def inspect(request: Request, project_id: str, document_id: str) -> JSONResponse:
    return await _read(request, project_id, document_id)


@router.get("/projects/{project_id}/documents/{document_id}/export")
async def export(request: Request, project_id: str, document_id: str) -> JSONResponse:
    response = await _read(request, project_id, document_id)
    response.headers["Content-Disposition"] = 'attachment; filename="knowledge.json"'
    return response


@router.get("/projects/{project_id}/documents/{document_id}/chunks/{chunk_id}")
async def citation(
    request: Request, project_id: str, document_id: str, chunk_id: str
) -> JSONResponse:
    runtime = _runtime(request, set())
    _identifier(project_id)
    _identifier(document_id)
    if not re.fullmatch(r"[0-9a-f]{64}", chunk_id):
        raise KnowledgeError("IDENTITY_INVALID")
    row = await _call(runtime, lambda: runtime.store.get(project_id, document_id))
    document = await _call(runtime, lambda: runtime.service.deliver(row))
    chunks = [chunk for chunk in document.chunks if chunk.chunkId == chunk_id]
    if len(chunks) != 1:
        raise KnowledgeError("CHUNK_NOT_FOUND")
    chunk = chunks[0]
    return _response(
        runtime,
        {
            "citation": runtime.service.citation(row, document, chunk).model_dump(mode="json"),
            "excerpt": chunk.text,
            "untrustedContent": True,
        },
    )


@router.delete("/projects/{project_id}/documents/{document_id}")
async def withdraw(request: Request, project_id: str, document_id: str) -> JSONResponse:
    runtime = _runtime(request, set())
    _identifier(project_id)
    _identifier(document_id)
    row = await _call(runtime, lambda: runtime.store.withdraw(project_id, document_id))
    return _response(runtime, _summary(row))
