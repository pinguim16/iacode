"""The Model Gateway HTTP API.

Six endpoints, versioned under ``/api/v1/gateway``. They are a thin translation: the wire shapes in
``iacode_contracts.gateway`` in, the gateway's own contracts out, and back. Every decision that
matters — routing, retrying, falling back, normalising — happens in the gateway, so the streaming
endpoint and the inference endpoint cannot disagree about any of it.

Three properties this module is responsible for.

**No secret leaves.** The provider listing reports whether a credential is configured and the *name*
of the variable that would carry it, never a value, and there is no field in the response models
that could hold one. The error handler returns the gateway's classified message and never a
provider's body.

**No stack trace leaves.** A ``GatewayError`` becomes the Foundation's error contract with a stable
code and a correlation identifier; the detail stays in the log, exactly as Gate 0 established.

**A disconnected client stops costing money.** The streaming endpoint iterates the gateway's
generator inside Starlette's response, so a client that goes away closes the generator, which closes
the upstream connection.
"""

from __future__ import annotations

import json
import os
from collections.abc import AsyncIterator
from typing import Any

from fastapi import APIRouter, FastAPI, Query, Request, status
from fastapi.responses import JSONResponse, StreamingResponse
from iacode_common.identifiers import uuid7
from iacode_contracts.foundation import ErrorResponse
from iacode_contracts.gateway import (
    CapabilityPayload,
    GatewayHealthResponse,
    InferenceRequest,
    InferenceResponse,
    ModelListResponse,
    ModelSummary,
    ProviderListResponse,
    ProviderSummary,
    RouteAttemptPayload,
    RouteDecisionPayload,
    SyncOutcomePayload,
    SyncRequest,
    SyncResponse,
    ToolCallDeltaPayload,
    ToolCallPayload,
    UsagePayload,
)
from iacode_model_gateway.config import resolve_secret
from iacode_model_gateway.contracts import (
    CONTRACT_VERSION,
    Capability,
    GatewayMessage,
    GatewayRequest,
    GatewayResponse,
    MessageRole,
    ModelDescriptor,
    ReasoningEffort,
    ResponseFormat,
    RouteDecision,
    StreamEvent,
    ToolDefinition,
    Usage,
)
from iacode_model_gateway.errors import GatewayError, GatewayErrorType
from iacode_telemetry.context import get_correlation_id
from iacode_telemetry.logging import get_logger
from pydantic import ValidationError

from iacode_api.dependencies import get_resources
from iacode_api.errors import ApiError

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/gateway", tags=["model-gateway"])

#: How a classified failure becomes an HTTP status. Written once, here, so two endpoints cannot
#: answer differently for the same failure.
HTTP_STATUS: dict[GatewayErrorType, int] = {
    GatewayErrorType.AUTHENTICATION_ERROR: status.HTTP_502_BAD_GATEWAY,
    GatewayErrorType.AUTHORIZATION_ERROR: status.HTTP_502_BAD_GATEWAY,
    GatewayErrorType.RATE_LIMITED: status.HTTP_429_TOO_MANY_REQUESTS,
    GatewayErrorType.MODEL_NOT_FOUND: status.HTTP_404_NOT_FOUND,
    GatewayErrorType.INVALID_REQUEST: status.HTTP_400_BAD_REQUEST,
    # 413, written out. Starlette renamed its constant and deprecated the old spelling, and a
    # module that imports the deprecated name emits a warning on every import of the application.
    # The number is the contract; the constant is one library's spelling of it.
    GatewayErrorType.CONTEXT_LIMIT: 413,
    GatewayErrorType.PROVIDER_UNAVAILABLE: status.HTTP_503_SERVICE_UNAVAILABLE,
    GatewayErrorType.PROVIDER_TIMEOUT: status.HTTP_504_GATEWAY_TIMEOUT,
    GatewayErrorType.TRANSIENT_PROVIDER_ERROR: status.HTTP_502_BAD_GATEWAY,
    GatewayErrorType.PERMANENT_PROVIDER_ERROR: status.HTTP_502_BAD_GATEWAY,
    GatewayErrorType.CIRCUIT_OPEN: status.HTTP_503_SERVICE_UNAVAILABLE,
    # 499 is nginx's "client closed request". It is not in the HTTP registry and Starlette has no
    # constant for it, which is why it is written out; every alternative in the 4xx range would say
    # the caller sent something wrong, and the caller sent something fine and then went away.
    GatewayErrorType.CANCELLED: 499,
    GatewayErrorType.NO_CANDIDATE: status.HTTP_409_CONFLICT,
    GatewayErrorType.RESPONSE_TOO_LARGE: status.HTTP_502_BAD_GATEWAY,
    GatewayErrorType.INTERNAL_GATEWAY_ERROR: status.HTTP_500_INTERNAL_SERVER_ERROR,
}

#: Detail keys that are safe to return to a caller. An allow-list rather than a deny-list: a key
#: added to a failure somewhere in the gateway must be considered before it reaches a response, and
#: a deny-list gets that wrong by default.
PUBLIC_DETAIL_KEYS = frozenset({
    "route", "routeReason", "fallbackCount", "fallbackStopped", "chain", "reason", "requested",
    "considered", "rejected", "inputTokenEstimate", "estimateIsExact", "limit", "value",
    "maximum", "setting", "provider", "scope",
})


def register_gateway_errors(app: FastAPI) -> None:
    """Install the handler that turns a classified gateway failure into the error contract.

    Registered from :func:`iacode_api.main.create_app` rather than from the Foundation's
    ``register_error_handlers``, so the Foundation error module keeps knowing nothing about the
    gateway. The direction of that dependency is the point: Gate 0 does not import Gate 1.
    """

    @app.exception_handler(GatewayError)
    async def _handle(request: Request, error: GatewayError) -> JSONResponse:
        http_status = HTTP_STATUS.get(error.error_type, status.HTTP_502_BAD_GATEWAY)
        correlation_id = getattr(request.state, "correlation_id", None) or get_correlation_id()
        logger.warning("gateway failure", extra={
            "errorType": str(error.error_type), "provider": error.provider,
            "model": error.model, "status": http_status})
        body = ErrorResponse(
            code=str(error.error_type),
            message=error.message,
            correlationId=correlation_id,
            details=_public_details(error),
        )
        response = JSONResponse(status_code=http_status,
                                content=body.model_dump(mode="json"))
        if correlation_id:
            header = getattr(getattr(request.app.state, "settings", None), "correlation_header",
                             "X-Correlation-ID")
            response.headers[header] = correlation_id
        return response


def _public_details(error: GatewayError) -> dict[str, Any] | None:
    details = {key: value for key, value in error.details.items() if key in PUBLIC_DETAIL_KEYS}
    if error.retry_after_seconds is not None:
        details["retryAfterSeconds"] = error.retry_after_seconds
    return details or None


# ---------------------------------------------------------------------------------------------
# Translation
# ---------------------------------------------------------------------------------------------


def _to_gateway_request(payload: InferenceRequest, request_id: str, *,
                        stream: bool) -> GatewayRequest:
    """Turn the wire shape into the gateway's contract, refusing anything it will not accept.

    A validation failure here is the caller's mistake and is answered as one. Letting it reach the
    gateway would surface as an internal error, which is a worse answer to the same question.
    """
    try:
        messages = tuple(
            GatewayMessage(
                role=MessageRole(item.role),
                content=item.content,
                name=item.name,
                tool_call_id=item.toolCallId,
            )
            for item in payload.messages
        )
        capabilities = tuple(Capability(item) for item in payload.requiredCapabilities)
        tools = tuple(
            ToolDefinition(name=item.name, description=item.description,
                           parameters=item.parameters)
            for item in payload.tools
        )
        response_format = (
            ResponseFormat(name=payload.responseFormat.name,
                           json_schema=payload.responseFormat.jsonSchema,
                           strict=payload.responseFormat.strict)
            if payload.responseFormat is not None else None
        )
        return GatewayRequest(
            request_id=request_id,
            messages=messages,
            route=payload.route,
            model=payload.model,
            required_capabilities=capabilities,
            temperature=payload.temperature,
            top_p=payload.topP,
            max_output_tokens=payload.maxOutputTokens,
            reasoning_effort=(ReasoningEffort(payload.reasoningEffort)
                              if payload.reasoningEffort else None),
            stream=stream,
            tools=tools,
            response_format=response_format,
            metadata=payload.metadata,
        )
    except (ValidationError, ValueError) as error:
        raise ApiError("VALIDATION_ERROR", _first_message(error),
                       status.HTTP_422_UNPROCESSABLE_CONTENT) from error


def _first_message(error: Exception) -> str:
    """The first validation message, without the exception's own formatting noise."""
    if isinstance(error, ValidationError):
        problems = error.errors()
        if problems:
            location = ".".join(str(part) for part in problems[0].get("loc", ()))
            return f"{location}: {problems[0].get('msg', 'is not valid')}".strip(": ")
    return str(error)


def _usage(usage: Usage) -> UsagePayload:
    return UsagePayload(
        inputTokens=usage.input_tokens,
        outputTokens=usage.output_tokens,
        totalTokens=usage.total_tokens,
        cachedInputTokens=usage.cached_input_tokens,
        reasoningTokens=usage.reasoning_tokens,
    )


def _route(decision: RouteDecision) -> RouteDecisionPayload:
    return RouteDecisionPayload(
        reason=str(decision.reason),
        route=decision.route,
        considered=decision.considered,
        rejected=list(decision.rejected),
        fallbackCount=decision.fallback_count,
        chain=[
            RouteAttemptPayload(
                provider=attempt.ref.provider_id,
                model=attempt.ref.model_id,
                endpoint=str(attempt.endpoint) if attempt.endpoint else None,
                attempt=attempt.attempt,
                outcome=attempt.outcome,
                errorType=attempt.error_type,
                retries=attempt.retries,
                latencyMs=attempt.latency_ms,
            )
            for attempt in decision.chain
        ],
    )


def _response(answer: GatewayResponse) -> InferenceResponse:
    return InferenceResponse(
        contractVersion=answer.contract_version,
        requestId=answer.request_id,
        provider=answer.ref.provider_id,
        model=answer.ref.model_id,
        endpoint=str(answer.endpoint),
        content=answer.content,
        toolCalls=[
            ToolCallPayload(id=call.id, name=call.name, arguments=call.arguments,
                            argumentsValid=call.arguments_valid,
                            invalidReason=call.invalid_reason)
            for call in answer.tool_calls
        ],
        finishReason=str(answer.finish_reason),
        usage=_usage(answer.usage),
        latencyMs=answer.latency_ms,
        route=_route(answer.route),
        cost=answer.cost,
    )


def _model_summary(descriptor: ModelDescriptor) -> ModelSummary:
    return ModelSummary(
        provider=descriptor.ref.provider_id,
        model=descriptor.ref.model_id,
        displayName=descriptor.display_name,
        family=descriptor.family,
        contextWindow=descriptor.context_window,
        maxOutputTokens=descriptor.max_output_tokens,
        supportedEndpoints=[str(item) for item in descriptor.supported_endpoints],
        capabilities={
            str(capability): CapabilityPayload(
                state=str(descriptor.capability(capability)),
                provenance=str(descriptor.provenance(capability)))
            for capability in Capability
        },
        reasoningLevels=[str(item) for item in descriptor.reasoning_levels],
        active=descriptor.active,
        syncedAt=descriptor.synced_at.isoformat() if descriptor.synced_at else None,
    )


def _stream_payload(event: StreamEvent) -> str:
    """Render one normalised event as a Server-Sent Event frame in the wire vocabulary."""
    payload = {
        "type": str(event.type),
        "requestId": event.request_id,
        "sequence": event.sequence,
        "text": event.text,
        "toolCallDelta": (
            ToolCallDeltaPayload(
                index=event.tool_call_delta.index,
                id=event.tool_call_delta.id,
                name=event.tool_call_delta.name,
                argumentsFragment=event.tool_call_delta.arguments_fragment,
            ).model_dump(mode="json")
            if event.tool_call_delta is not None else None
        ),
        "usage": _usage(event.usage).model_dump(mode="json") if event.usage else None,
        "finishReason": str(event.finish_reason) if event.finish_reason else None,
        "provider": event.ref.provider_id if event.ref else None,
        "model": event.ref.model_id if event.ref else None,
        "endpoint": str(event.endpoint) if event.endpoint else None,
        "route": _route(event.route).model_dump(mode="json") if event.route else None,
        "error": event.error,
        "latencyMs": event.latency_ms,
    }
    body = json.dumps({key: value for key, value in payload.items() if value is not None},
                      ensure_ascii=False)
    return f"event: {event.type}\ndata: {body}\n\n"


async def _provider_summaries(request: Request) -> list[ProviderSummary]:
    runtime = get_resources(request).gateway
    records = {record.provider_id: record for record in
               await runtime.catalog_store.list_providers()}
    summaries: list[ProviderSummary] = []
    for config in sorted(runtime.providers.values(), key=lambda item: item.provider_id):
        record = records.get(config.provider_id)
        summaries.append(ProviderSummary(
            provider=config.provider_id,
            displayName=config.display_name,
            adapter=config.adapter,
            enabled=config.enabled,
            protocols=[str(item) for item in config.protocols],
            credentialConfigured=resolve_secret(config.credential_env) is not None,
            credentialVariable=config.credential_env,
            addressConfigured=bool((os.environ.get(config.base_url_env) or "").strip()),
            addressVariable=config.base_url_env,
            healthy=record.healthy if record else None,
            lastHealthCheck=(record.last_health_check.isoformat()
                             if record and record.last_health_check else None),
            lastSync=record.last_sync.isoformat() if record and record.last_sync else None,
            modelCount=record.model_count if record else 0,
            detail=record.detail if record else None,
        ))
    return summaries


# ---------------------------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------------------------


@router.get("/providers", response_model=ProviderListResponse,
            summary="The configured providers and their operational state")
async def list_providers(request: Request) -> ProviderListResponse:
    """Safe metadata only.

    The response says whether a credential is configured and which variable would carry it. It never
    says what the value is, and no field in the model could hold one.
    """
    summaries = await _provider_summaries(request)
    return ProviderListResponse(total=len(summaries), providers=summaries)


@router.get("/models", response_model=ModelListResponse,
            summary="The discovered model catalog")
async def list_models(
    request: Request,
    provider: str | None = Query(default=None, description="Restrict to one provider."),
    active: bool | None = Query(default=None, description="Restrict by catalog activity."),
    capability: list[str] | None = Query(
        default=None,
        description="Keep only models that support every named capability. A model whose support "
                    "is unknown is not returned, because unknown is not support."),
) -> ModelListResponse:
    runtime = get_resources(request).gateway
    descriptors = await runtime.catalog_store.list_models(provider_id=provider, active=active)
    if capability:
        try:
            required = [Capability(item) for item in capability]
        except ValueError as error:
            raise ApiError("BAD_REQUEST", str(error), status.HTTP_400_BAD_REQUEST) from error
        descriptors = [
            descriptor for descriptor in descriptors
            if all(str(descriptor.capability(item)) == "SUPPORTED" for item in required)
        ]
    summaries = [_model_summary(descriptor) for descriptor in descriptors]
    return ModelListResponse(total=len(summaries), models=summaries)


@router.post("/models/sync", response_model=SyncResponse,
             summary="Refresh the catalog from the providers' discovery endpoints")
async def synchronise(request: Request, payload: SyncRequest | None = None) -> SyncResponse:
    """Discover, normalise and apply each provider's catalog.

    Explicit rather than automatic: a synchronisation costs a provider round trip and changes what
    the router can choose, so it happens when somebody asks for it.
    """
    runtime = get_resources(request).gateway
    gateway = runtime.gateway(get_correlation_id())
    outcomes = await gateway.synchronise_catalog(payload.provider if payload else None)
    return SyncResponse(outcomes=[
        SyncOutcomePayload(
            provider=outcome.provider_id, added=outcome.added, updated=outcome.updated,
            deactivated=outcome.deactivated, unchanged=outcome.unchanged,
            errors=list(outcome.errors))
        for outcome in outcomes
    ])


@router.get("/health", response_model=GatewayHealthResponse,
            summary="Whether the gateway can work, and whether each provider is reachable")
async def gateway_health(request: Request) -> GatewayHealthResponse:
    """Two answers, kept apart.

    An unreachable provider is reported as unreachable and the gateway is reported as degraded. It
    does not make this endpoint fail and it certainly does not touch ``/health``, which answers a
    question about this process and contacts nothing.
    """
    resources = get_resources(request)
    runtime = resources.gateway
    gateway = runtime.gateway(get_correlation_id())
    await gateway.provider_health()
    summaries = await _provider_summaries(request)
    catalog = await runtime.catalog_store.list_models(active=True)
    usable = any(item.enabled and item.healthy for item in summaries)
    return GatewayHealthResponse(
        status="READY" if usable else "DEGRADED",
        contractVersion=CONTRACT_VERSION,
        providers=summaries,
        circuits=gateway.circuit_snapshot(),
        catalogSize=len(catalog),
        defaultModel=runtime.settings.default_model,
        routes=[alias.alias for alias in runtime.route_policy.aliases],
    )


@router.post("/infer", response_model=InferenceResponse,
             summary="Run one inference request through the router")
async def infer(request: Request, payload: InferenceRequest) -> InferenceResponse:
    runtime = get_resources(request).gateway
    request_id = str(uuid7())
    gateway_request = _to_gateway_request(payload, request_id, stream=False)
    gateway = runtime.gateway(get_correlation_id())
    answer = await gateway.infer(gateway_request)
    return _response(answer)


@router.post("/stream", summary="Run one inference request and stream the answer")
async def stream(request: Request) -> StreamingResponse:
    """Stream over Server-Sent Events, through the same router and the same adapters.

    The body is read and validated here rather than through a parameter, because a failure that
    happened after the response started streaming could not be answered with a status code. By the
    time the generator runs, the request is known to be valid and the only failures left are the
    provider's.
    """
    runtime = get_resources(request).gateway
    try:
        payload = InferenceRequest.model_validate(await request.json())
    except ValidationError as error:
        raise ApiError("VALIDATION_ERROR", _first_message(error),
                       status.HTTP_422_UNPROCESSABLE_CONTENT) from error
    except ValueError as error:
        raise ApiError("BAD_REQUEST", "the request body is not valid JSON",
                       status.HTTP_400_BAD_REQUEST) from error

    request_id = str(uuid7())
    gateway_request = _to_gateway_request(payload, request_id, stream=True)
    gateway = runtime.gateway(get_correlation_id())

    async def events() -> AsyncIterator[str]:
        try:
            async for event in gateway.stream(gateway_request):
                yield _stream_payload(event)
        except GatewayError as error:
            # The stream has already started, so there is no status code left to send. The failure
            # is delivered as a terminal error event, which is what a consumer can act on.
            body = json.dumps({
                "type": "error", "requestId": request_id, "sequence": -1,
                "error": {**error.to_dict(),
                          "details": _public_details(error) or {}},
            }, ensure_ascii=False)
            yield f"event: error\ndata: {body}\n\n"

    return StreamingResponse(
        events(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-store",
            # Without this an nginx or a proxy in front of the API buffers the whole response and
            # the stream arrives as one block, which looks exactly like streaming being broken.
            "X-Accel-Buffering": "no",
        },
    )
