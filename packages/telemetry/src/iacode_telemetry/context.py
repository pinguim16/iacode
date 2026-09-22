"""The ambient identifiers a log record inherits from the work in progress.

A log line is only useful if it can be tied back to the request, task or run that produced it, and
threading those identifiers through every function signature is how projects end up with none of
them. They live in :mod:`contextvars` instead: set once at the boundary that knows them, read by
the log processor, and isolated per task so two concurrent requests never see each other's values.

Gate 0 knows only the correlation and request identifiers. ``taskId``, ``runId`` and ``agentId``
belong to Gates that do not exist yet, so the fields are declared here and left unset: the logging
contract omits an unset field rather than inventing a value for it.
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar, Token
from typing import Any

__all__ = [
    "CONTEXT_FIELDS",
    "bind_context",
    "current_context",
    "get_correlation_id",
    "set_context",
]

# Every field the logging contract may carry from the ambient context, in the order the contract
# documents them. A field that has no value in this Gate is simply absent from the record.
CONTEXT_FIELDS = ("traceId", "correlationId", "requestId", "taskId", "runId", "agentId")

# The default is ``None``, not ``{}``. A mutable default is one object shared by every context
# that never set a value, so a single in-place mutation anywhere would leak identifiers from
# one request into all the others. Every read below turns ``None`` into a fresh mapping.
_context: ContextVar[dict[str, str] | None] = ContextVar("iacode_log_context", default=None)


def current_context() -> dict[str, str]:
    """A copy of the ambient identifiers, so a caller cannot mutate the live mapping."""
    return dict(_context.get() or {})


def get_correlation_id() -> str | None:
    return (_context.get() or {}).get("correlationId")


def set_context(**values: Any) -> Token:
    """Merge identifiers into the ambient context and return the token that restores it.

    A value of ``None`` removes the field. That is how an identifier stays absent instead of being
    recorded as the string ``"None"``, which is the shape the logging contract forbids.
    """
    merged = dict(_context.get() or {})
    for key, value in values.items():
        if key not in CONTEXT_FIELDS:
            raise ValueError(f"unknown log context field: {key}")
        if value is None:
            merged.pop(key, None)
        else:
            merged[key] = str(value)
    return _context.set(merged)


@contextmanager
def bind_context(**values: Any) -> Iterator[dict[str, str]]:
    """Bind identifiers for the duration of a block and restore the previous context after it."""
    reset_handle = set_context(**values)
    try:
        yield current_context()
    finally:
        _context.reset(reset_handle)
