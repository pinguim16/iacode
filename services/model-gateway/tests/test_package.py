"""The package itself: that it is installed, that it is whole, and what it does not reach for."""

from __future__ import annotations

import importlib
import pkgutil

import iacode_model_gateway


def test_gateway_package_is_importable() -> None:
    """The boundary is a real, installed package rather than a directory on somebody's path.

    Every module imports, so a circular import or a missing dependency is a failure here rather than
    on the first request that happens to reach the module nobody imported at start-up.
    """
    assert iacode_model_gateway.CONTRACT_VERSION
    assert iacode_model_gateway.ModelGateway is not None

    failures: list[str] = []
    for module in pkgutil.walk_packages(iacode_model_gateway.__path__,
                                        prefix="iacode_model_gateway."):
        try:
            importlib.import_module(module.name)
        except Exception as error:  # noqa: BLE001 - the failure is the finding
            failures.append(f"{module.name}: {type(error).__name__}: {error}")

    assert failures == [], failures


def test_the_public_surface_is_the_contract() -> None:
    """What a consumer is offered at the top level is the contract and the gateway, not internals."""
    exported = set(iacode_model_gateway.__all__)

    assert {"GatewayRequest", "GatewayResponse", "StreamEvent", "ModelGateway", "GatewayError",
            "Capability", "CapabilityState", "Endpoint"} <= exported
    # Nothing provider-shaped, and nothing from the transport, is part of the offer.
    assert not exported & {"HttpModelProvider", "OpenAiChatAdapter", "AnthropicMessagesAdapter",
                           "SqlCatalogStore"}


def test_the_distribution_declares_what_it_needs() -> None:
    """Including the two IACode packages it genuinely uses, and not the application."""
    from importlib.metadata import requires

    declared = " ".join(requires("iacode-model-gateway") or [])

    assert "httpx" in declared
    assert "pydantic" in declared
    assert "iacode-api" not in declared
