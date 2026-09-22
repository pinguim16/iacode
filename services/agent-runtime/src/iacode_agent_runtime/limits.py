"""The size limits the runtime enforces, and the one function that enforces them.

A limit that each call site re-implements is a limit that one call site will get wrong. Everything
here goes through :func:`enforce_size`, which measures the same way — the UTF-8 byte length of the
canonical JSON rendering, or of the text — and refuses with the same classified error.

The defaults are deliberately small enough to be felt. A task input of 64 KiB is a very long
instruction; a tool argument object of 32 KiB is a very large argument. The point of a limit is
that an unbounded payload cannot reach the database or the model, not that the number is exactly
right, and every one of them is configurable.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from iacode_agent_runtime.errors import AgentRuntimeError, AgentRuntimeErrorType

__all__ = ["RuntimeLimits", "enforce_size", "payload_size"]


@dataclass(frozen=True)
class RuntimeLimits:
    """How large each thing may be, in bytes."""

    max_task_bytes: int = 64 * 1024
    max_agent_output_bytes: int = 256 * 1024
    max_tool_arguments_bytes: int = 32 * 1024
    max_tool_result_bytes: int = 256 * 1024
    max_event_payload_bytes: int = 32 * 1024
    max_context_bytes: int = 512 * 1024

    def __post_init__(self) -> None:
        # Named pairs rather than a dynamic attribute lookup. The runtime resolves no name at
        # runtime — a tool name least of all — and a boundary scan enforces that over the whole
        # package, so this module does not get an exception for convenience.
        declared = (
            ("max_task_bytes", self.max_task_bytes),
            ("max_agent_output_bytes", self.max_agent_output_bytes),
            ("max_tool_arguments_bytes", self.max_tool_arguments_bytes),
            ("max_tool_result_bytes", self.max_tool_result_bytes),
            ("max_event_payload_bytes", self.max_event_payload_bytes),
            ("max_context_bytes", self.max_context_bytes),
        )
        for name, value in declared:
            if not isinstance(value, int) or isinstance(value, bool) or value < 1:
                raise AgentRuntimeError(
                    AgentRuntimeErrorType.INVALID_REQUEST,
                    f"{name} must be a positive number of bytes",
                    details={"setting": name, "value": value})


def payload_size(value: Any) -> int:
    """How large a value is, measured the way every limit measures it."""
    if isinstance(value, str):
        return len(value.encode("utf-8"))
    if isinstance(value, (bytes, bytearray)):
        return len(value)
    return len(json.dumps(value, ensure_ascii=False, sort_keys=True,
                          default=str).encode("utf-8"))


def enforce_size(value: Any, limit: int, *, what: str) -> None:
    """Refuse a payload larger than ``limit``.

    The error names the limit and the measured size and nothing else: echoing the payload back
    into the failure would defeat the purpose of refusing to carry it.
    """
    size = payload_size(value)
    if size > limit:
        raise AgentRuntimeError(
            AgentRuntimeErrorType.PAYLOAD_TOO_LARGE,
            f"{what} is {size} bytes, above the configured limit of {limit}",
            details={"what": what, "limit": limit, "size": size})
