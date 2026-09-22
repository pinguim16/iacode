"""The API error contract.

One shape for every failure — :class:`iacode_contracts.foundation.ErrorResponse` — with a stable
``code``, a message safe to show a caller, and the ``correlationId`` that leads to the log record
holding the real detail.

The rule that makes it worth having: **the client gets a summary, the operator gets the truth.** An
unhandled exception is logged with its traceback and returned as ``INTERNAL_ERROR`` with a fixed
sentence. Returning the exception text instead is how a stack trace, a file path, a SQL statement or
a connection string ends up in a caller's log, and a connection string carries a password.

The catalogue is deliberately five codes. `docs/GATE-0-CHECKLIST.md` row 11.3 asks for a contract
that is explicit and extensible, not for an error taxonomy invented before there are errors to
classify. A later Gate adds a code when it has a failure a caller must distinguish.
"""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from iacode_contracts.foundation import ErrorResponse
from iacode_telemetry.context import get_correlation_id
from iacode_telemetry.logging import get_logger
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = get_logger(__name__)

# The sentence a caller sees when something unexpected failed. Fixed, because any detail derived
# from the exception is a detail derived from our internals.
INTERNAL_MESSAGE = "The request could not be completed. Quote the correlation identifier."

ERROR_CODES = {
    status.HTTP_400_BAD_REQUEST: "BAD_REQUEST",
    status.HTTP_404_NOT_FOUND: "NOT_FOUND",
    status.HTTP_422_UNPROCESSABLE_CONTENT: "VALIDATION_ERROR",
    status.HTTP_503_SERVICE_UNAVAILABLE: "DEPENDENCY_UNAVAILABLE",
}
INTERNAL_CODE = "INTERNAL_ERROR"


class ApiError(Exception):
    """A failure the API raises deliberately, with a code a caller may branch on."""

    def __init__(self, code: str, message: str, http_status: int = 400,
                 details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.http_status = http_status
        self.details = details


def _correlation_id(request: Request) -> str | None:
    """The identifier of the request that failed.

    Read from ``request.state`` first and from the ambient context second. The order matters: the
    unhandled-exception handler runs in Starlette's outermost error middleware, outside the task
    the correlation middleware bound its context in, so the context variable is empty there while
    ``request.state`` — which lives on the shared scope — still carries the value.
    """
    return getattr(request.state, "correlation_id", None) or get_correlation_id()


def _response(request: Request, http_status: int, code: str, message: str,
              details: dict[str, Any] | None = None) -> JSONResponse:
    correlation_id = _correlation_id(request)
    body = ErrorResponse(
        code=code,
        message=message,
        correlationId=correlation_id,
        details=details,
    )
    response = JSONResponse(status_code=http_status, content=body.model_dump(mode="json"))
    if correlation_id:
        # The header is set here as well as in the middleware, because an error produced outside
        # the middleware never passes back through it. A caller told to quote a correlation
        # identifier needs it on the response that failed, not only on the ones that worked.
        header = getattr(getattr(request.app.state, "settings", None), "correlation_header",
                         "X-Correlation-ID")
        response.headers[header] = correlation_id
    return response


def register_error_handlers(app: FastAPI) -> None:
    """Install the handlers that make every failure follow the contract."""

    @app.exception_handler(ApiError)
    async def _handle_api_error(request: Request, error: ApiError) -> JSONResponse:
        logger.warning("api error", extra={"errorCode": error.code, "status": error.http_status})
        return _response(request, error.http_status, error.code, error.message, error.details)

    @app.exception_handler(RequestValidationError)
    async def _handle_validation(request: Request,
                                 error: RequestValidationError) -> JSONResponse:
        # Validation detail is about the caller's own input, so returning it helps rather than
        # leaks. ``input`` is dropped: it is the value the caller sent, and echoing it back into a
        # response body is how a mistyped credential ends up in somebody's log.
        details = {
            "errors": [
                {"location": list(item.get("loc", ())), "message": item.get("msg", ""),
                 "type": item.get("type", "")}
                for item in error.errors()
            ]
        }
        logger.info("request validation failed", extra={"errorCount": len(error.errors())})
        return _response(
            request,
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            ERROR_CODES[status.HTTP_422_UNPROCESSABLE_CONTENT],
            "The request payload is not valid.",
            details,
        )

    @app.exception_handler(StarletteHTTPException)
    async def _handle_http(request: Request, error: StarletteHTTPException) -> JSONResponse:
        code = ERROR_CODES.get(error.status_code, f"HTTP_{error.status_code}")
        message = error.detail if isinstance(error.detail, str) else "The request failed."
        if error.status_code >= 500:
            logger.error("http error", extra={"status": error.status_code})
            return _response(request, error.status_code, INTERNAL_CODE, INTERNAL_MESSAGE)
        logger.info("http error", extra={"status": error.status_code, "errorCode": code})
        return _response(request, error.status_code, code, message)

    @app.exception_handler(Exception)
    async def _handle_unexpected(request: Request, error: Exception) -> JSONResponse:
        # ``exc_info`` is what puts the traceback in the log. The response carries none of it.
        logger.error("unhandled exception", exc_info=error)
        return _response(
            request, status.HTTP_500_INTERNAL_SERVER_ERROR, INTERNAL_CODE, INTERNAL_MESSAGE)
