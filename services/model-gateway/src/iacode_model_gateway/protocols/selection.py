"""Choosing which protocol to speak to a model.

`docs/GATE-1-CHECKLIST.md` row 4.5 forbids the assumption that every model answers on
``/chat/completions``. Three inputs decide instead, and the order between them is the whole content
of this module:

1. **what the model declares** — the endpoints the catalog normalized from the provider's own
   discovery answer;
2. **what the provider serves** — the protocols its configuration says it exposes;
3. **what the provider prefers** — its configured default, used only to break a tie or to answer
   the case where the model declared nothing.

The third case is the interesting one. Most ``/models`` answers in the wild carry an identifier and
little else, so "the model declares no endpoint" is the normal state rather than an error, and
refusing it would leave the gateway unable to call anything. The selection therefore falls back to
the provider's configured protocol and **records that it did**: ``EndpointSource.PROVIDER_DEFAULT``
is in the route explanation, so an operator reading a failure can tell the difference between a
model that said it speaks this protocol and a model that said nothing at all.

What is never allowed is the opposite: a model that *does* declare its endpoints and does not
include the one we need. That is refused here, before a socket is opened, because the provider's
answer to such a request is a confusing 404 that costs a round trip to learn nothing.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from iacode_model_gateway.config import ProviderConfig
from iacode_model_gateway.contracts import Endpoint, ModelDescriptor
from iacode_model_gateway.errors import GatewayError, GatewayErrorType

__all__ = ["EndpointSelection", "EndpointSource", "select_endpoint"]


class EndpointSource(StrEnum):
    """Where the endpoint choice came from."""

    MODEL_METADATA = "MODEL_METADATA"
    PROVIDER_DEFAULT = "PROVIDER_DEFAULT"


@dataclass(frozen=True)
class EndpointSelection:
    """The protocol to use, and on what authority."""

    endpoint: Endpoint
    source: EndpointSource


def select_endpoint(model: ModelDescriptor, provider: ProviderConfig,
                    requested: Endpoint | None = None) -> EndpointSelection:
    """Decide which protocol to speak, or refuse with a classified error."""
    served = tuple(provider.protocols)
    if not served:
        raise GatewayError(
            GatewayErrorType.INTERNAL_GATEWAY_ERROR,
            f"provider {provider.provider_id!r} declares no protocol",
            provider=provider.provider_id, model=model.ref.model_id)

    declared = tuple(model.supported_endpoints)

    if requested is not None:
        if requested not in served:
            raise GatewayError(
                GatewayErrorType.INVALID_REQUEST,
                f"provider {provider.provider_id!r} does not serve the {requested!s} protocol",
                provider=provider.provider_id, model=model.ref.model_id)
        if declared and requested not in declared:
            raise GatewayError(
                GatewayErrorType.INVALID_REQUEST,
                f"model {model.ref.model_id!r} does not declare the {requested!s} protocol",
                provider=provider.provider_id, model=model.ref.model_id)
        return EndpointSelection(
            endpoint=requested,
            source=EndpointSource.MODEL_METADATA if declared else EndpointSource.PROVIDER_DEFAULT)

    if declared:
        usable = [endpoint for endpoint in served if endpoint in declared]
        if not usable:
            raise GatewayError(
                GatewayErrorType.INVALID_REQUEST,
                f"model {model.ref.model_id!r} declares "
                f"{', '.join(str(item) for item in declared)}, which provider "
                f"{provider.provider_id!r} does not serve",
                provider=provider.provider_id, model=model.ref.model_id)
        preferred = provider.default_protocol
        chosen = preferred if preferred in usable else usable[0]
        return EndpointSelection(endpoint=chosen, source=EndpointSource.MODEL_METADATA)

    chosen = provider.default_protocol or served[0]
    return EndpointSelection(endpoint=chosen, source=EndpointSource.PROVIDER_DEFAULT)
