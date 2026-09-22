"""What a provider is, expressed without reference to any particular one.

Four operations, and they are four because each answers a question the layers above genuinely ask:

``health``       can we reach it at all? Asked by the health endpoint and by the frontend, and
                 deliberately separate from the process's own liveness.
``list_models``  what does it offer? Asked by catalog synchronization, never by a request.
``generate``     answer this request.
``stream``       answer this request incrementally.

Nothing here mentions HTTP, and that is not decoration. A future local runtime — a model in this
process, a subprocess, a gRPC service — implements this contract without the HTTP implementation
being in the way, which is the whole reason the contract exists separately from
:class:`~iacode_model_gateway.providers.http_provider.HttpModelProvider`.

The contract is also deliberately **stateless between calls**. Retries, circuits and fallbacks are
decided above, once, for every provider. A provider that retried internally would make the gateway's
own attempt count a lie, and the operator reading a metric would have no way to know.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Protocol, runtime_checkable

from iacode_model_gateway.catalog.sync import DiscoveredCatalog
from iacode_model_gateway.contracts import Endpoint, GatewayRequest, ModelDescriptor
from iacode_model_gateway.protocols.base import ParsedCompletion, StreamChunk

__all__ = ["ModelProvider", "ProviderHealth"]


class ProviderHealth:
    """The outcome of asking a provider whether it is reachable.

    A class rather than a boolean because "unreachable" and "reachable but refusing our credential"
    are different operational states and the health page has to be able to say which.
    """

    def __init__(self, provider_id: str, reachable: bool, detail: str | None = None,
                 latency_ms: float | None = None) -> None:
        self.provider_id = provider_id
        self.reachable = reachable
        self.detail = detail
        self.latency_ms = latency_ms

    def as_dict(self) -> dict[str, object]:
        return {
            "provider": self.provider_id,
            "reachable": self.reachable,
            "detail": self.detail,
            "latencyMs": self.latency_ms,
        }


@runtime_checkable
class ModelProvider(Protocol):
    """One source of models, however it is reached."""

    @property
    def provider_id(self) -> str: ...

    async def health(self) -> ProviderHealth:
        """Whether the provider answers, and how quickly."""

    async def list_models(self) -> DiscoveredCatalog:
        """Everything the provider says it offers, unnormalized."""

    async def generate(self, request: GatewayRequest, model: ModelDescriptor,
                       endpoint: Endpoint, *, output_tokens: int) -> ParsedCompletion:
        """Answer a request in one response."""

    def stream(self, request: GatewayRequest, model: ModelDescriptor,
               endpoint: Endpoint, *, output_tokens: int) -> AsyncIterator[StreamChunk]:
        """Answer a request incrementally.

        Not an ``async def``: the caller needs the iterator itself, so that opening the connection
        and consuming it are the same operation and cancelling the consumer closes the connection.
        """
