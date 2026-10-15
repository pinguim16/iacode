"""Credential containment before sandbox artifacts or durable activity responses."""

from __future__ import annotations

import base64
import json
from typing import Any

from iacode_common.secret_scanning import find_secret_kinds


class OutputSecurityError(ValueError):
    def __init__(self, code: str) -> None:
        super().__init__("sandbox output was rejected before durable delivery")
        self.code = code


def require_safe_bytes(content: bytes) -> None:
    try:
        findings = find_secret_kinds(content.decode("utf-8", errors="replace"))
    except Exception:
        raise OutputSecurityError("SANDBOX_OUTPUT_SECRET_SCAN_FAILED") from None
    if findings:
        raise OutputSecurityError("SANDBOX_OUTPUT_SECRET_DETECTED")


def require_safe_output(response: dict[str, Any]) -> None:
    """Check all channels before writing even the first full stream.

    Full streams are base64 in the helper response; scanning their envelope is not scanning
    their decoded bytes. Error responses and non-stream structured output are scanned too.
    """
    try:
        serialized = json.dumps(response, ensure_ascii=False, sort_keys=True).encode("utf-8")
        result = response.get("result") or {}
        streams = [base64.b64decode(result[f"{name}Full"], validate=True)
                   for name in ("stdout", "stderr") if result.get(f"{name}Full")]
    except Exception:
        raise OutputSecurityError("SANDBOX_OUTPUT_SECRET_SCAN_FAILED") from None
    require_safe_bytes(serialized)
    for content in streams:
        require_safe_bytes(content)
