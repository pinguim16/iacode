"""The HTTP provider: the one place in the gateway that opens a socket.

Every protocol adapter describes a call; this class makes it. Concentrating the I/O here is what
lets the adapter suite run without a network and what makes the four properties below true for every
protocol at once instead of three times over.

**Nothing is unbounded.** Connect and read timeouts are separate, because they fail for different
reasons and deserve different budgets: a connect timeout means the provider is unreachable, a read
timeout means it accepted the work and is taking too long. A response is read with a byte budget, so
a provider answering with something enormous is refused rather than read into memory until the
process dies.

**The credential is added last and never stored.** :meth:`_headers` reads the ``SecretStr`` at the
moment of the call and puts it in a dict that lives for the duration of that call. It is not in the
:class:`~iacode_model_gateway.protocols.base.HttpCall`, not in a log line, not in an exception, and
not in anything this class returns.

**A provider's error body is never our error message.** The status code and the body's own
classification vocabulary decide the error class; the message is written by us. A provider that
echoes a request header back inside an error — which happens — would otherwise put an
``Authorization`` value into an exception, and from there into a log.

**Cancellation is propagated, not swallowed.** ``CancelledError`` closes the upstream connection and
is re-raised. Converting it into an ordinary error would leave the caller's ``asyncio.CancelledError``
contract broken and the task tree in a state nothing can reason about.
"""

from __future__ import annotations

import time
from collections.abc import AsyncIterator
from typing import Any

import httpx

from iacode_model_gateway.catalog.sync import DiscoveredCatalog
from iacode_model_gateway.config import GatewaySettings, ResolvedProvider
from iacode_model_gateway.contracts import Endpoint, GatewayRequest, ModelDescriptor
from iacode_model_gateway.errors import GatewayError, GatewayErrorType
from iacode_model_gateway.protocols import ProtocolAdapter
from iacode_model_gateway.protocols.base import HttpCall, ParsedCompletion, StreamChunk
from iacode_model_gateway.providers.base import ProviderHealth

__all__ = ["HttpModelProvider", "parse_retry_after"]

#: The largest single SSE frame the reader will assemble. A provider that never sends a blank line
#: would otherwise grow one string until the process runs out of memory.
MAX_FRAME_BYTES = 1_048_576


def parse_retry_after(value: str | None) -> float | None:
    """Read a ``Retry-After`` header expressed in seconds.

    The HTTP date form is deliberately not supported: honouring it requires trusting the provider's
    clock against ours, and a skewed pair produces either a wait of zero — which defeats the point —
    or one of hours, which no caller can be held for. Without a usable hint the gateway falls back
    to its own backoff, which is bounded by construction.
    """
    if value is None:
        return None
    try:
        seconds = float(value.strip())
    except (TypeError, ValueError):
        return None
    return seconds if seconds >= 0 else None


class HttpModelProvider:
    """A provider reached over HTTP, speaking whichever protocols its configuration declares."""

    def __init__(self, resolved: ResolvedProvider, adapters: dict[Endpoint, ProtocolAdapter],
                 settings: GatewaySettings, *, transport: httpx.AsyncBaseTransport | None = None
                 ) -> None:
        self._resolved = resolved
        self._adapters = adapters
        self._settings = settings
        self._transport = transport

    @property
    def provider_id(self) -> str:
        return self._resolved.provider_id

    # -- plumbing -------------------------------------------------------------------------------

    def _client(self) -> httpx.AsyncClient:
        """A client for one call.

        Per call rather than per provider: a long-lived client would have to be owned, closed and
        shared across event loops, and the gateway is composed by an application whose lifespan
        already owns everything it opens. The connection cost is real and is the price of not
        inventing a second ownership model here.
        """
        timeout = httpx.Timeout(
            connect=self._settings.connect_timeout_seconds,
            read=self._settings.read_timeout_seconds,
            write=self._settings.connect_timeout_seconds,
            pool=self._settings.connect_timeout_seconds,
        )
        return httpx.AsyncClient(
            base_url=self._resolved.base_url, timeout=timeout, transport=self._transport,
            follow_redirects=False)

    def _adapter(self, endpoint: Endpoint) -> ProtocolAdapter:
        adapter = self._adapters.get(endpoint)
        if adapter is None:
            raise GatewayError(
                GatewayErrorType.INTERNAL_GATEWAY_ERROR,
                f"provider {self.provider_id!r} has no adapter for {endpoint!s}",
                provider=self.provider_id)
        return adapter

    def _path(self, endpoint: Endpoint, adapter: ProtocolAdapter) -> str:
        return self._resolved.config.protocol_paths.get(endpoint, adapter.default_path)

    def _headers(self, call: HttpCall, adapter: ProtocolAdapter) -> dict[str, str]:
        """The call's headers plus the credential, assembled at the last possible moment."""
        headers = dict(call.headers)
        headers.update(adapter.auth_headers(self._resolved.credential.get_secret_value()))
        return headers

    def _translate(self, error: Exception) -> GatewayError:
        """Turn a transport failure into a classified one."""
        if isinstance(error, httpx.ConnectTimeout):
            return GatewayError(
                GatewayErrorType.PROVIDER_TIMEOUT,
                f"the provider did not accept a connection within "
                f"{self._settings.connect_timeout_seconds:g}s",
                provider=self.provider_id)
        if isinstance(error, httpx.ReadTimeout | httpx.WriteTimeout | httpx.PoolTimeout):
            return GatewayError(
                GatewayErrorType.PROVIDER_TIMEOUT,
                f"the provider did not answer within {self._settings.read_timeout_seconds:g}s",
                provider=self.provider_id)
        if isinstance(error, httpx.TransportError):
            return GatewayError(
                GatewayErrorType.PROVIDER_UNAVAILABLE,
                f"the provider could not be reached ({type(error).__name__})",
                provider=self.provider_id)
        return GatewayError(
            GatewayErrorType.INTERNAL_GATEWAY_ERROR,
            f"the gateway failed while calling the provider ({type(error).__name__})",
            provider=self.provider_id)

    def _failure(self, response: httpx.Response, payload: Any,
                 adapter: ProtocolAdapter, model_id: str | None) -> GatewayError:
        error_type, message = adapter.classify_error(response.status_code, payload)
        return GatewayError(
            error_type, message, provider=self.provider_id, model=model_id,
            status_code=response.status_code,
            retry_after_seconds=parse_retry_after(response.headers.get("retry-after")),
            details=_rate_limit_hints(response.headers))

    async def _read_bounded(self, response: httpx.Response) -> bytes:
        """Read a response body under a byte budget."""
        budget = self._settings.max_response_bytes
        chunks: list[bytes] = []
        size = 0
        async for chunk in response.aiter_bytes():
            size += len(chunk)
            if size > budget:
                raise GatewayError(
                    GatewayErrorType.RESPONSE_TOO_LARGE,
                    f"the provider answered with more than {budget} bytes",
                    provider=self.provider_id)
            chunks.append(chunk)
        return b"".join(chunks)

    @staticmethod
    def _json(body: bytes) -> Any:
        import json

        if not body.strip():
            return None
        try:
            return json.loads(body)
        except json.JSONDecodeError:
            return None

    # -- operations -----------------------------------------------------------------------------

    async def health(self) -> ProviderHealth:
        """Ask the provider for its model list and report whether it answered.

        Discovery is the health probe because it is the only operation every provider is guaranteed
        to expose and because it costs no tokens. A reachable provider that refuses our credential
        is reported as unreachable *with the reason*, which is the state an operator needs to see.
        """
        adapter = self._adapter(self._discovery_endpoint())
        call = adapter.build_discovery(self._resolved.config.models_path)
        started = time.perf_counter()
        try:
            async with self._client() as client:
                response = await client.request(
                    call.method, call.path, headers=self._headers(call, adapter))
                body = await self._read_bounded(response)
        except GatewayError as error:
            return ProviderHealth(self.provider_id, False, error.message,
                                  round((time.perf_counter() - started) * 1000, 2))
        except Exception as error:  # noqa: BLE001 - every transport failure is a health answer
            classified = self._translate(error)
            return ProviderHealth(self.provider_id, False, classified.message,
                                  round((time.perf_counter() - started) * 1000, 2))
        latency = round((time.perf_counter() - started) * 1000, 2)
        if response.status_code >= 400:
            failure = self._failure(response, self._json(body), adapter, None)
            return ProviderHealth(self.provider_id, False, failure.message, latency)
        return ProviderHealth(self.provider_id, True, None, latency)

    async def list_models(self) -> DiscoveredCatalog:
        """Fetch and parse the provider's catalog, without normalizing it."""
        adapter = self._adapter(self._discovery_endpoint())
        call = adapter.build_discovery(self._resolved.config.models_path)
        try:
            async with self._client() as client:
                response = await client.request(
                    call.method, call.path, headers=self._headers(call, adapter))
                body = await self._read_bounded(response)
        except GatewayError:
            raise
        except Exception as error:
            raise self._translate(error) from error

        payload = self._json(body)
        if response.status_code >= 400:
            raise self._failure(response, payload, adapter, None)
        if payload is None:
            raise GatewayError(
                GatewayErrorType.PROVIDER_UNAVAILABLE,
                "the provider's catalog answer was not JSON",
                provider=self.provider_id)
        try:
            raw = adapter.parse_models(payload)
        except ValueError as error:
            raise GatewayError(
                GatewayErrorType.PROVIDER_UNAVAILABLE,
                f"the provider's catalog answer could not be read: {error}",
                provider=self.provider_id) from error
        return DiscoveredCatalog(
            provider_id=self.provider_id,
            entries=tuple((item.model_id, item.payload) for item in raw))

    async def generate(self, request: GatewayRequest, model: ModelDescriptor,
                       endpoint: Endpoint, *, output_tokens: int) -> ParsedCompletion:
        """Make one non-streaming call and parse the answer."""
        adapter = self._adapter(endpoint)
        call = adapter.build_generate(
            request, model, stream=False, path=self._path(endpoint, adapter),
            max_output_tokens=output_tokens)
        try:
            async with self._client() as client:
                response = await client.request(
                    call.method, call.path, headers=self._headers(call, adapter),
                    json=call.json_body)
                body = await self._read_bounded(response)
        except GatewayError:
            raise
        except Exception as error:
            raise self._translate(error) from error

        payload = self._json(body)
        if response.status_code >= 400:
            raise self._failure(response, payload, adapter, model.ref.model_id)
        if not isinstance(payload, dict):
            raise GatewayError(
                GatewayErrorType.PROVIDER_UNAVAILABLE,
                "the provider's answer was not a JSON object",
                provider=self.provider_id, model=model.ref.model_id)
        try:
            return adapter.parse_completion(payload)
        except ValueError as error:
            raise GatewayError(
                GatewayErrorType.PROVIDER_UNAVAILABLE,
                f"the provider's answer could not be read: {error}",
                provider=self.provider_id, model=model.ref.model_id) from error

    async def stream(self, request: GatewayRequest, model: ModelDescriptor,
                     endpoint: Endpoint, *, output_tokens: int) -> AsyncIterator[StreamChunk]:
        """Make one streaming call and yield normalized chunks as they arrive."""
        adapter = self._adapter(endpoint)
        call = adapter.build_generate(
            request, model, stream=True, path=self._path(endpoint, adapter),
            max_output_tokens=output_tokens)
        decoder = adapter.decoder()

        try:
            async with self._client() as client:
                async with client.stream(
                        call.method, call.path, headers=self._headers(call, adapter),
                        json=call.json_body) as response:
                    if response.status_code >= 400:
                        body = await self._read_bounded(response)
                        raise self._failure(response, self._json(body), adapter,
                                            model.ref.model_id)
                    async for chunk in self._decode(response, decoder, model):
                        yield chunk
        except GatewayError:
            raise
        except GeneratorExit:
            # The consumer stopped reading. The ``async with`` blocks above close the connection on
            # the way out, which is what stops the provider generating tokens nobody will read.
            raise
        except Exception as error:
            raise self._translate(error) from error

        for chunk in decoder.finish():
            yield chunk
        if not decoder.completed:
            raise GatewayError(
                GatewayErrorType.TRANSIENT_PROVIDER_ERROR,
                "the provider closed the stream before sending a terminal frame",
                provider=self.provider_id, model=model.ref.model_id)

    async def _decode(self, response: httpx.Response, decoder: Any,
                      model: ModelDescriptor) -> AsyncIterator[StreamChunk]:
        """Read Server-Sent Events off the response and hand each frame to the decoder."""
        event: str | None = None
        data: list[str] = []
        size = 0
        async for line in response.aiter_lines():
            stripped = line.rstrip("\r")
            if not stripped:
                if data:
                    for chunk in self._feed(decoder, event, "\n".join(data), model):
                        yield chunk
                event, data, size = None, [], 0
                continue
            if stripped.startswith(":"):
                continue  # A comment frame; providers use it as a keep-alive.
            field, _, value = stripped.partition(":")
            value = value[1:] if value.startswith(" ") else value
            if field == "event":
                event = value
            elif field == "data":
                size += len(value)
                if size > MAX_FRAME_BYTES:
                    raise GatewayError(
                        GatewayErrorType.RESPONSE_TOO_LARGE,
                        f"a single stream frame exceeded {MAX_FRAME_BYTES} bytes",
                        provider=self.provider_id, model=model.ref.model_id)
                data.append(value)
        if data:
            for chunk in self._feed(decoder, event, "\n".join(data), model):
                yield chunk

    def _feed(self, decoder: Any, event: str | None, data: str,
              model: ModelDescriptor) -> list[StreamChunk]:
        try:
            return decoder.feed(event, data)
        except ValueError as error:
            raise GatewayError(
                GatewayErrorType.TRANSIENT_PROVIDER_ERROR,
                f"a stream frame could not be read: {error}",
                provider=self.provider_id, model=model.ref.model_id) from error

    def _discovery_endpoint(self) -> Endpoint:
        config = self._resolved.config
        return config.default_protocol or config.protocols[0]


def _rate_limit_hints(headers: httpx.Headers) -> dict[str, Any]:
    """The rate-limit metadata a provider volunteers, when it is simple and safe to read.

    Captured because it is free and useful, and deliberately not built into a quota system: this
    Gate has no accounting and inventing one from headers nobody standardised would be a feature
    resting on a guess.
    """
    hints: dict[str, Any] = {}
    for header, key in (
        ("x-ratelimit-remaining-requests", "rateLimitRemainingRequests"),
        ("x-ratelimit-remaining-tokens", "rateLimitRemainingTokens"),
        ("x-ratelimit-limit-requests", "rateLimitRequests"),
        ("x-ratelimit-limit-tokens", "rateLimitTokens"),
        ("anthropic-ratelimit-requests-remaining", "rateLimitRemainingRequests"),
        ("anthropic-ratelimit-tokens-remaining", "rateLimitRemainingTokens"),
    ):
        value = headers.get(header)
        if value is None:
            continue
        try:
            hints[key] = int(value)
        except (TypeError, ValueError):
            continue
    return hints
