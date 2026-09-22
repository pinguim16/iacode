"""The gateway's log contract.

The Foundation already decides *how* a record is written — one line of JSON, contract fields from
the ambient context, everything passing through the redactor. This module decides *what* the gateway
says, so that one call is readable end to end without the fields differing between the three places
that emit them.

The rule the field list encodes: **operational facts, never content.** A record says which provider,
which model, which endpoint, which route, which attempt, how long and what failed. It does not say
what was asked or what came back. A full prompt in a log is the same disclosure as a prompt in a
database row, with the extra property that log shipping tends to copy it somewhere nobody audited.

A field with no value is absent rather than null, which is the Foundation's contract and the reason
a reader can trust that a present field means something.
"""

from __future__ import annotations

from typing import Any

__all__ = ["CONTRACT_FIELDS", "call_fields"]

#: Every field a gateway record may carry. The suite asserts against this tuple, so a field added at
#: one call site and forgotten at the others is visible.
CONTRACT_FIELDS = (
    "requestId",
    "provider",
    "model",
    "endpoint",
    "route",
    "attempt",
    "fallbackIndex",
    "latencyMs",
    "status",
    "errorType",
)


def call_fields(*, request_id: str | None = None, provider: str | None = None,
                model: str | None = None, endpoint: str | None = None, route: str | None = None,
                attempt: int | None = None, fallback_index: int | None = None,
                latency_ms: float | None = None, status: str | None = None,
                error_type: str | None = None) -> dict[str, Any]:
    """Assemble the structured payload of one gateway log record.

    Only the fields that have a value are returned. ``attempt`` and ``fallbackIndex`` are kept when
    they are zero, because zero is a meaningful position in a chain and dropping it would make the
    first attempt indistinguishable from an unrecorded one.
    """
    candidates: dict[str, Any] = {
        "requestId": request_id,
        "provider": provider,
        "model": model,
        "endpoint": endpoint,
        "route": route,
        "attempt": attempt,
        "fallbackIndex": fallback_index,
        "latencyMs": latency_ms,
        "status": status,
        "errorType": error_type,
    }
    return {key: value for key, value in candidates.items() if value is not None}
