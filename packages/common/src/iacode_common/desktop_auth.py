"""Byte-exact HMAC authentication. Secrets never travel in the protocol or diagnostics."""

from __future__ import annotations

import hashlib
import hmac
import time
import uuid
from collections.abc import Mapping


def request_signature(
    secret: str,
    request_id: str,
    timestamp: str,
    method: str,
    path: str,
    body: bytes,
    *,
    version: str,
) -> str:
    material = "\n".join(
        (version, request_id, timestamp, method.upper(), path, hashlib.sha256(body).hexdigest())
    )
    return hmac.new(secret.encode("utf-8"), material.encode("utf-8"), hashlib.sha256).hexdigest()


def response_signature(
    secret: str, request_id: str, status: int, body: bytes, *, version: str
) -> str:
    material = "\n".join((version, request_id, str(status), hashlib.sha256(body).hexdigest()))
    return hmac.new(secret.encode("utf-8"), material.encode("utf-8"), hashlib.sha256).hexdigest()


def signed_headers(
    secret: str,
    method: str,
    path: str,
    body: bytes = b"",
    *,
    request_id: str | None = None,
    timestamp: int | None = None,
    names: Mapping[str, str],
    version: str,
) -> dict[str, str]:
    identifier = request_id or str(uuid.uuid4())
    instant = str(int(time.time()) if timestamp is None else timestamp)
    return {
        names["requestId"]: identifier,
        names["timestamp"]: instant,
        names["signature"]: request_signature(
            secret, identifier, instant, method, path, body, version=version
        ),
    }
