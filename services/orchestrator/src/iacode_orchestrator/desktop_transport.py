"""Infrastructure authentication around the unchanged provider-neutral gateway client."""

from __future__ import annotations

import hmac

import httpx
from iacode_common.desktop_auth import response_signature, signed_headers
from iacode_contracts.desktop import PROTOCOL, gateway_response_limit


class AuthenticatedRuntimeTransport(httpx.AsyncBaseTransport):
    def __init__(self, key: str, *, upstream_response_bytes: int = 8_388_608) -> None:
        self._key = key
        self._response_limit = gateway_response_limit(upstream_response_bytes)

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        body = await request.aread()
        headers = signed_headers(
            self._key,
            request.method,
            request.url.raw_path.decode("ascii"),
            body,
            names=PROTOCOL["headers"],
            version=PROTOCOL["version"],
        )
        request.headers.update(headers)
        async with httpx.AsyncHTTPTransport(trust_env=False) as transport:
            response = await transport.handle_async_request(request)
            parts: list[bytes] = []
            size = 0
            try:
                async for part in response.aiter_raw():
                    size += len(part)
                    if size > self._response_limit:
                        raise httpx.TransportError(
                            "authenticated gateway response exceeds its byte bound"
                        )
                    parts.append(part)
            finally:
                await response.aclose()
        content = b"".join(parts)
        expected = response_signature(
            self._key,
            headers[PROTOCOL["headers"]["requestId"]],
            response.status_code,
            content,
            version=PROTOCOL["version"],
        )
        observed = response.headers.get(PROTOCOL["headers"]["signature"], "")
        if not hmac.compare_digest(expected, observed):
            raise httpx.TransportError("gateway response authentication failed")
        return httpx.Response(
            response.status_code, headers=response.headers, content=content, request=request
        )
