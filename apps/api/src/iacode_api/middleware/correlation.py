"""Request correlation.

Every request gets an identifier. It is taken from the configured header when the caller supplies
one and generated when they do not, it is bound to the ambient logging context so every record the
request produces carries it without being passed anything, and it is returned on the response so the
caller can quote it.

Two identifiers, not one, because they answer different questions:

``correlationId``  travels across services. A caller that already has one keeps it, which is what
                   lets one identifier tie the frontend, the API and — from Gate 2 — a workflow
                   together.
``requestId``      is this hop only. It is always generated here, so a caller cannot make two
                   different requests indistinguishable in our logs by sending the same
                   correlation identifier for both.

A supplied value is validated before it is used. It is echoed into a response header and written
into log records, so accepting arbitrary caller input would let someone inject a newline and forge
a log line, or smuggle a payload into a header a downstream service parses.
"""

from __future__ import annotations

import re

from iacode_common.identifiers import uuid7
from iacode_telemetry.context import set_context
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

# Printable ASCII, no whitespace, bounded. Wide enough for a UUID, a ULID or a trace identifier
# from another system; narrow enough that nothing can be smuggled through it.
VALID_CORRELATION_ID = re.compile(r"^[A-Za-z0-9._:-]{8,128}$")

REQUEST_ID_HEADER = "X-Request-ID"


class CorrelationMiddleware(BaseHTTPMiddleware):
    """Bind a correlation identifier to the request, the logs and the response."""

    def __init__(self, app, header_name: str) -> None:
        super().__init__(app)
        self.header_name = header_name

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        supplied = request.headers.get(self.header_name, "")
        correlation_id = supplied if VALID_CORRELATION_ID.match(supplied) else str(uuid7())
        request_id = str(uuid7())

        # Bound for the whole request, including the exception handlers: the error contract reads
        # the correlation identifier from this context to put it in the response body.
        set_context(correlationId=correlation_id, requestId=request_id)
        request.state.correlation_id = correlation_id
        request.state.request_id = request_id

        response = await call_next(request)
        response.headers[self.header_name] = correlation_id
        response.headers[REQUEST_ID_HEADER] = request_id
        return response
