"""Harden every domain route when desktop mode is configured; never leak its key."""

from __future__ import annotations

import asyncio
import base64
import hashlib
import hmac
import json
import re
import time
from datetime import UTC, datetime
from typing import Any

from iacode_common.desktop_auth import request_signature, response_signature
from iacode_common.secret_scanning import iter_secret_scan_views
from iacode_contracts.desktop import PROTOCOL, gateway_response_limit

from iacode_api.config import Settings


class DesktopAuthMiddleware:
    def __init__(self, app: Any, settings: Settings) -> None:
        self.app = app
        self.settings = settings

    async def __call__(self, scope: dict, receive: Any, send: Any) -> None:
        path = scope.get("path", "")
        key = self.settings.desktop_token.get_secret_value()
        if (
            scope["type"] != "http"
            or not key
            or not (path == "/api/v1" or path.startswith("/api/v1/"))
        ):
            await self.app(scope, receive, send)
            return
        names = {key: value.lower().encode("ascii") for key, value in PROTOCOL["headers"].items()}
        raw_headers = scope.get("headers", [])
        values = {
            key: [v.decode("latin-1") for k, v in raw_headers if k.lower() == name]
            for key, name in names.items()
        }
        identifier = values["requestId"][0] if len(values["requestId"]) == 1 else ""

        async def answer(code: str, status: int) -> None:
            body = json.dumps(
                {"code": code, "message": "desktop request refused", "requestId": identifier},
                separators=(",", ":"),
            ).encode("utf-8")
            headers = [(b"content-type", b"application/json"), (b"cache-control", b"no-store")]
            # Only a syntactically bounded identifier is reflected, even in authentication errors.
            headers.append(
                (
                    names["signature"],
                    response_signature(
                        key, identifier, status, body, version=PROTOCOL["version"]
                    ).encode("ascii"),
                )
            )
            await send({"type": "http.response.start", "status": status, "headers": headers})
            await send({"type": "http.response.body", "body": body})

        if not all(len(value) == 1 for value in values.values()) or not re.fullmatch(
            r"[0-9a-f-]{36}", identifier
        ):
            identifier = ""
            await answer("AUTHENTICATION_REQUIRED", 401)
            return
        instant = values["timestamp"][0]
        signature = values["signature"][0]
        if not re.fullmatch(r"[0-9]{10,11}", instant) or not re.fullmatch(
            r"[0-9a-f]{64}", signature
        ):
            await answer("AUTHENTICATION_INVALID", 401)
            return
        expires = self.settings.desktop_token_expires_at
        if expires is None or expires <= datetime.now(UTC):
            await answer("AUTHENTICATION_EXPIRED", 401)
            return
        if abs(time.time() - int(instant)) > PROTOCOL["clockWindowSeconds"]:
            await answer("AUTHENTICATION_STALE", 401)
            return
        limit = (
            PROTOCOL["maxRequestBytes"]
            if path == PROTOCOL["path"]
            else max(PROTOCOL["maxRequestBytes"], self.settings.gateway_max_request_bytes)
        )
        chunks: list[bytes] = []
        size = 0
        try:
            async with asyncio.timeout(PROTOCOL["requestTimeoutSeconds"]):
                while True:
                    message = await receive()
                    if message["type"] == "http.disconnect":
                        return
                    part = message.get("body", b"")
                    size += len(part)
                    if size > limit:
                        await answer("REQUEST_TOO_LARGE", 413)
                        return
                    chunks.append(part)
                    if not message.get("more_body", False):
                        break
        except TimeoutError:
            await answer("REQUEST_TIMEOUT", 408)
            return
        body = b"".join(chunks)
        raw_path = scope.get("raw_path", path.encode("ascii"))
        target = raw_path.decode("ascii")
        if scope.get("query_string"):
            target += "?" + scope["query_string"].decode("ascii")
        expected = request_signature(
            key, identifier, instant, scope["method"], target, body, version=PROTOCOL["version"]
        )
        if not hmac.compare_digest(expected, signature):
            await answer("AUTHENTICATION_INVALID", 401)
            return

        def reflects_capability(data: bytes) -> bool:
            forms = {key.casefold()}
            for text in (key, key.upper()):
                raw = text.encode("ascii")
                forms.update(
                    (
                        base64.b64encode(raw).decode().casefold(),
                        base64.urlsafe_b64encode(raw).decode().rstrip("=").casefold(),
                        raw.hex(),
                        "".join(f"%{value:02x}" for value in raw),
                        "".join(f"\\u{value:04x}" for value in raw),
                    )
                )
            return any(
                any(form in view.casefold() for form in forms)
                for view, _ in iter_secret_scan_views(data.decode("utf-8", errors="replace"))
            )

        if reflects_capability(body):
            await answer("AUTHENTICATION_MATERIAL_REFUSED", 400)
            return
        if path == PROTOCOL["path"] and any(k.lower() == b"origin" for k, _ in raw_headers):
            await answer("BROWSER_ORIGIN_REFUSED", 403)
            return
        try:
            redis = scope["app"].state.resources.redis
            accepted = await redis.set(
                "iacode:desktop:nonce:"
                + hashlib.sha256(f"{key}:{identifier}".encode("ascii")).hexdigest(),
                "1",
                nx=True,
                ex=PROTOCOL["replaySeconds"],
            )
        except Exception:
            await answer("AUTHENTICATION_STATE_UNAVAILABLE", 503)
            return
        if not accepted:
            await answer("AUTHENTICATION_REPLAY", 409)
            return
        supplied = False

        async def replay() -> dict:
            nonlocal supplied
            if not supplied:
                supplied = True
                return {"type": "http.request", "body": body, "more_body": False}
            return await receive()

        # Event streams are authenticated on ingress, not buffered indefinitely. Desktop clients
        # use the closed paginated operation instead, and never accept an unsigned response.
        if path.endswith("/stream"):
            await self.app(scope, replay, send)
            return
        start: dict | None = None
        output: list[bytes] = []
        output_size = 0
        output_limit = (
            PROTOCOL["maxResponseBytes"]
            if path == PROTOCOL["path"]
            else gateway_response_limit(self.settings.gateway_max_response_bytes)
        )

        async def signed_send(message: dict) -> None:
            nonlocal start, output_size
            if message["type"] == "http.response.start":
                start = message
                return
            if message["type"] != "http.response.body" or start is None:
                raise RuntimeError("unsupported authenticated response shape")
            part = message.get("body", b"")
            output_size += len(part)
            if output_size <= output_limit:
                output.append(part)
            if message.get("more_body", False):
                return
            if output_size > output_limit:
                await answer("RESPONSE_TOO_LARGE_OUTCOME_UNCERTAIN", 502)
                return
            response_body = b"".join(output)
            if reflects_capability(response_body):
                await answer("CREDENTIAL_REFLECTION_OUTCOME_UNCERTAIN", 502)
                return
            headers = [
                (k, v)
                for k, v in start.get("headers", [])
                if k.lower() not in {names["signature"], b"cache-control"}
            ]
            headers.extend(
                [
                    (b"cache-control", b"no-store"),
                    (
                        names["signature"],
                        response_signature(
                            key,
                            identifier,
                            start["status"],
                            response_body,
                            version=PROTOCOL["version"],
                        ).encode("ascii"),
                    ),
                ]
            )
            await send({**start, "headers": headers})
            await send({"type": "http.response.body", "body": response_body})

        await self.app(scope, replay, signed_send)
