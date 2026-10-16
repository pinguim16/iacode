"""Authenticated desktop operations delegate to the existing governed domain boundaries."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from iacode_contracts.agent_runtime import (
    AGENT_RUN_STATES,
    TERMINAL_RUN_STATES,
    CreateAgentRunRequest,
)
from iacode_contracts.desktop import PROTOCOL, PROTOCOL_DIGEST, DesktopError, parse_request
from iacode_contracts.quality import (
    QUALITY_RUN_STATES,
    QUALITY_TERMINAL_RUN_STATES,
    CreateQualityRunRequest,
    ReproduceQualityRunRequest,
)
from iacode_persistence.models import Artifact, QualityRun, TaskRun
from sqlalchemy import select

from iacode_api.dependencies import get_resources
from iacode_api.desktop_snapshots import authorize_snapshot, store_snapshot
from iacode_api.routes import agent_runs, quality

router = APIRouter(tags=["desktop"])


async def dispatch(request: Request, operation: str, arguments: dict) -> Any:
    settings = request.app.state.settings
    if operation == "hello":
        return {
            "authenticated": True,
            "protocolDigest": PROTOCOL_DIGEST,
            "expiresAt": settings.desktop_token_expires_at,
            "operations": list(PROTOCOL["operations"]),
            "runStates": AGENT_RUN_STATES,
            "terminalRunStates": TERMINAL_RUN_STATES,
            "qualityStates": QUALITY_RUN_STATES,
            "terminalQualityStates": QUALITY_TERMINAL_RUN_STATES,
        }
    resources = get_resources(request)
    if operation in {"lookup", "quality-lookup"}:
        model = TaskRun if operation == "lookup" else QualityRun
        async with resources.session_factory() as session:
            row = (
                (
                    await session.execute(
                        select(model).where(model.idempotency_key == arguments["idempotencyKey"])
                    )
                )
                .scalars()
                .first()
            )
        return {
            "idempotencyKey": arguments["idempotencyKey"],
            "found": row is not None,
            "runId": str(row.id) if row is not None else None,
            "state": (row.status if operation == "lookup" else row.state)
            if row is not None
            else None,
        }
    if operation == "snapshot-lookup":
        async with resources.session_factory() as session:
            rows = (
                (
                    await session.execute(
                        select(Artifact)
                        .where(
                            Artifact.metadata_["source"].astext == "desktop",
                            Artifact.metadata_["manifestDigest"].astext
                            == arguments["manifestDigest"],
                        )
                        .order_by(Artifact.id)
                        .limit(2)
                    )
                )
                .scalars()
                .all()
            )
        if len(rows) > 1:
            raise DesktopError(
                "SNAPSHOT_IDENTITY_CONFLICT", "inventory has ambiguous stored identities"
            )
        row = rows[0] if rows else None
        if row is not None:
            await authorize_snapshot(resources, str(row.id), row.checksum_sha256)
        return {
            "manifestDigest": arguments["manifestDigest"],
            "found": row is not None,
            "snapshotId": str(row.id) if row is not None else None,
            "snapshotDigest": row.checksum_sha256 if row is not None else None,
        }
    if operation == "snapshot":
        return await store_snapshot(resources, arguments)
    if operation == "agents":
        return await agent_runs.list_agents(request)
    if operation == "teams":
        return await agent_runs.list_agent_teams(request)
    if operation == "list":
        return await agent_runs.list_agent_runs(request, limit=arguments.get("limit", 25))
    if operation == "start":
        await authorize_snapshot(resources, arguments["snapshotId"])
        return await agent_runs.create_agent_run(
            request,
            CreateAgentRunRequest(
                task=arguments["task"],
                team=arguments["team"],
                model=arguments.get("model"),
                workspaceSnapshot=arguments["snapshotId"],
                idempotencyKey=arguments["idempotencyKey"],
            ),
        )
    if operation == "read":
        return await agent_runs.read_agent_run(request, arguments["runId"])
    if operation == "events":
        return await agent_runs.read_agent_run_events(
            request, arguments["runId"], after=arguments["after"], limit=arguments.get("limit", 200)
        )
    if operation == "cancel":
        return await agent_runs.cancel_agent_run(request, arguments["runId"])
    if operation == "quality-start":
        await authorize_snapshot(resources, arguments["snapshotId"], arguments["snapshotDigest"])
        return await quality.create_quality_run(
            request,
            CreateQualityRunRequest(
                snapshotId=arguments["snapshotId"],
                snapshotDigest=arguments["snapshotDigest"],
                policyId="default",
                idempotencyKey=arguments["idempotencyKey"],
            ),
        )
    if operation == "quality-read":
        return await quality.read_quality_run(request, arguments["runId"])
    if operation == "quality-events":
        return await quality.read_quality_events(
            request, arguments["runId"], after=arguments["after"], limit=arguments.get("limit", 200)
        )
    if operation == "quality-cancel":
        return await quality.cancel_quality_run(request, arguments["runId"])
    if operation == "quality-reproduce":
        return await quality.reproduce_quality_run(
            request,
            arguments["runId"],
            ReproduceQualityRunRequest(idempotencyKey=arguments["idempotencyKey"]),
        )
    raise DesktopError("OPERATION_NOT_IMPLEMENTED", "the declared desktop operation has no handler")


@router.post(PROTOCOL["path"])
async def desktop_operation(request: Request) -> JSONResponse:
    if not request.app.state.settings.desktop_token.get_secret_value():
        return JSONResponse(
            status_code=503,
            content={
                "code": "DESKTOP_MODE_NOT_CONFIGURED",
                "message": "legacy development mode is not a desktop connection",
            },
        )
    try:
        payload = parse_request(await request.body())
        if payload["requestId"] != request.headers.get(PROTOCOL["headers"]["requestId"]):
            raise DesktopError(
                "REQUEST_ID_MISMATCH", "authenticated request and envelope identities differ"
            )
        result = await dispatch(request, payload["operation"], payload["arguments"])
    except DesktopError as error:
        status = (
            503
            if error.code.endswith("UNAVAILABLE")
            else 403
            if error.code == "SNAPSHOT_NOT_AUTHORISED"
            else 400
        )
        return JSONResponse(status_code=status, content={"code": error.code, "message": str(error)})
    return JSONResponse(
        content=jsonable_encoder(
            {
                "version": PROTOCOL["version"],
                "requestId": payload["requestId"],
                "operation": payload["operation"],
                "data": result,
            }
        )
    )
