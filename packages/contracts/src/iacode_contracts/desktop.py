"""The closed, shared desktop operation boundary. No caller selects execution policy."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

PROTOCOL_BYTES = Path(__file__).with_name("desktop_protocol.json").read_bytes()
PROTOCOL = json.loads(PROTOCOL_BYTES)
PROTOCOL_DIGEST = hashlib.sha256(PROTOCOL_BYTES).hexdigest()


def gateway_response_limit(upstream_bytes: int) -> int:
    """One bounded JSON envelope budget shared by the API and its worker transport."""
    return max(PROTOCOL["maxResponseBytes"], upstream_bytes * 6 + 65_536)


class DesktopError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(message)


def validate(value: Any, schema: dict[str, Any], location: str = "arguments") -> None:
    kind = schema["type"]
    expected = {"object": dict, "array": list, "string": str, "integer": int}
    if type(value) is not expected[kind]:
        raise DesktopError("FIELD_TYPE_INVALID", f"{location} has the wrong type")
    if kind == "object":
        for name in schema["required"]:
            if name not in value:
                raise DesktopError("FIELD_MISSING", f"{location}.{name} is required")
        if set(value) - set(schema["properties"]):
            raise DesktopError("FIELD_UNKNOWN", f"{location} has an undeclared field")
        for name, item in value.items():
            validate(item, schema["properties"][name], f"{location}.{name}")
    elif kind == "array":
        if not schema["minItems"] <= len(value) <= schema["maxItems"]:
            raise DesktopError("FIELD_VALUE_INVALID", f"{location} has an invalid item count")
        for item in value:
            validate(item, schema["items"], f"{location}[]")
    elif kind == "string":
        try:
            value.encode("utf-8")
        except UnicodeEncodeError:
            raise DesktopError("FIELD_VALUE_INVALID", f"{location} is not valid Unicode") from None
        if not schema.get("minLength", 0) <= len(value) <= schema["maxLength"] or (
            schema.get("pattern") and not re.fullmatch(schema["pattern"], value)
        ):
            raise DesktopError("FIELD_VALUE_INVALID", f"{location} has an invalid value")
    elif not schema["minimum"] <= value <= schema["maximum"]:
        raise DesktopError("FIELD_VALUE_INVALID", f"{location} is outside its bound")


def _unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DesktopError("FIELD_DUPLICATE", "JSON object has a repeated field")
        result[key] = value
    return result


def _non_finite(_: str) -> Any:
    raise DesktopError("JSON_INVALID", "non-finite numbers are not JSON")


def parse_request(data: bytes) -> dict[str, Any]:
    if len(data) > PROTOCOL["maxRequestBytes"]:
        raise DesktopError("REQUEST_TOO_LARGE", "request exceeds the protocol byte bound")
    try:
        value = json.loads(
            data.decode("utf-8"), object_pairs_hook=_unique, parse_constant=_non_finite
        )
    except (UnicodeError, ValueError, RecursionError) as error:
        if isinstance(error, DesktopError):
            raise
        raise DesktopError("JSON_INVALID", "request must be bounded valid UTF-8 JSON") from None
    if type(value) is not dict:
        raise DesktopError("FIELD_TYPE_INVALID", "request must be an object")
    if set(value) != {"version", "operation", "arguments", "requestId"}:
        code = (
            "FIELD_MISSING"
            if {"version", "operation", "arguments", "requestId"} - set(value)
            else "FIELD_UNKNOWN"
        )
        raise DesktopError(code, "request envelope fields do not match the contract")
    if type(value["version"]) is not str or type(value["operation"]) is not str:
        raise DesktopError("FIELD_TYPE_INVALID", "version and operation must be strings")
    if value["version"] != PROTOCOL["version"]:
        raise DesktopError("VERSION_UNSUPPORTED", "desktop protocol version is unsupported")
    if value["operation"] not in PROTOCOL["operations"]:
        raise DesktopError("OPERATION_UNKNOWN", "desktop operation is not declared")
    validate(
        value["requestId"],
        PROTOCOL["operations"]["start"]["properties"]["idempotencyKey"],
        "requestId",
    )
    validate(value["arguments"], PROTOCOL["operations"][value["operation"]])
    return value
