"""The catalog: what normalization records, what it refuses to invent, and what a sync may not do."""

from __future__ import annotations

import pytest
from fixtures.doubles import (
    EPOCH,
    FakeClock,
    InMemoryCatalogStore,
    ScriptedProvider,
    build_gateway,
    descriptor,
    provider_config,
)
from iacode_model_gateway.catalog.normalize import normalise_model, normalise_models
from iacode_model_gateway.catalog.sync import CatalogSynchroniser, DiscoveredCatalog
from iacode_model_gateway.contracts import (
    Capability,
    CapabilityProvenance,
    CapabilityState,
    Endpoint,
    ReasoningEffort,
)
from iacode_model_gateway.errors import GatewayError, GatewayErrorType


def _model(model_id: str = "model-one", **payload):
    return normalise_model("alpha", model_id, dict(payload), synced_at=EPOCH)


def test_normalised_model_carries_the_declared_fields() -> None:
    """Everything the provider stated reaches the descriptor."""
    model = _model(
        "model-one",
        id="model-one",
        display_name="Model One",
        owned_by="acme",
        context_length=128000,
        max_output_tokens=8192,
        supported_endpoints=["chat_completions", "responses"],
        supported_parameters=["tools", "reasoning", "structured_outputs", "stream"],
        supported_reasoning_efforts=["low", "high"],
    )

    assert model.display_name == "Model One"
    assert model.family == "acme"
    assert model.context_window == 128000
    assert model.max_output_tokens == 8192
    assert model.supported_endpoints == (Endpoint.OPENAI_CHAT_COMPLETIONS,
                                         Endpoint.OPENAI_RESPONSES)
    assert model.capability(Capability.TOOLS) is CapabilityState.SUPPORTED
    assert model.reasoning_levels == (ReasoningEffort.LOW, ReasoningEffort.HIGH)
    assert model.active
    assert model.synced_at == EPOCH


def test_unknown_capability_is_not_turned_into_false() -> None:
    """A provider that listed an identifier and nothing else has told us nothing."""
    model = _model("terse", id="terse")

    for capability in Capability:
        assert model.capability(capability) is CapabilityState.UNKNOWN
        assert model.provenance(capability) is CapabilityProvenance.UNKNOWN


def test_a_declared_feature_list_is_a_complete_statement() -> None:
    """Listing features says what is supported *and*, by omission, what is not."""
    model = _model("listed", id="listed", supported_parameters=["tools"])

    assert model.capability(Capability.TOOLS) is CapabilityState.SUPPORTED
    assert model.capability(Capability.VISION) is CapabilityState.UNSUPPORTED
    assert model.provenance(Capability.VISION) is CapabilityProvenance.PROVIDER_METADATA


def test_a_boolean_states_only_what_it_names() -> None:
    model = _model("flagged", id="flagged", supports_tools=False)

    assert model.capability(Capability.TOOLS) is CapabilityState.UNSUPPORTED
    assert model.capability(Capability.VISION) is CapabilityState.UNKNOWN


def test_capability_provenance_is_recorded() -> None:
    """An administrator's statement and the provider's are distinguishable in the catalog."""
    stated = normalise_model(
        "alpha", "terse", {"id": "terse"}, synced_at=EPOCH,
        provider_capabilities={Capability.STREAMING: CapabilityState.SUPPORTED})

    assert stated.capability(Capability.STREAMING) is CapabilityState.SUPPORTED
    assert stated.provenance(Capability.STREAMING) is CapabilityProvenance.MANUAL_CONFIGURATION

    declared = normalise_model(
        "alpha", "rich", {"id": "rich", "supports_streaming": True}, synced_at=EPOCH,
        provider_capabilities={Capability.STREAMING: CapabilityState.UNSUPPORTED})

    # The provider's own metadata is not overruled by a provider-wide statement.
    assert declared.capability(Capability.STREAMING) is CapabilityState.SUPPORTED
    assert declared.provenance(Capability.STREAMING) is CapabilityProvenance.PROVIDER_METADATA


def test_capability_is_never_inferred_from_a_name() -> None:
    """'vision' in an identifier is a naming convention, not metadata."""
    model = _model("gpt-4-vision-preview", id="gpt-4-vision-preview")

    assert model.capability(Capability.VISION) is CapabilityState.UNKNOWN
    assert "INFERRED" not in {str(item) for item in CapabilityProvenance}


def test_nested_metadata_is_read_without_naming_each_provider_shape() -> None:
    model = _model(
        "nested", id="nested",
        architecture={"input_modalities": ["text", "image"]},
        top_provider={"context_length": 64000})

    assert model.context_window == 64000
    assert model.capability(Capability.VISION) is CapabilityState.SUPPORTED


def test_an_explicitly_inactive_model_is_recorded_as_inactive() -> None:
    assert not _model("gone", id="gone", status="retired").active
    assert _model("here", id="here").active


def test_a_duplicate_identifier_is_refused() -> None:
    """Applying it would make the surviving record depend on iteration order."""
    with pytest.raises(ValueError):
        normalise_models("alpha", [("dup", {"id": "dup"}), ("dup", {"id": "dup"})],
                         synced_at=EPOCH)


def test_invalid_metadata_does_not_become_a_confident_value() -> None:
    model = _model("odd", id="odd", context_length="a lot", max_output_tokens=-5)

    assert model.context_window is None
    assert model.max_output_tokens is None


def test_same_model_id_in_two_providers_does_not_collide() -> None:
    first = normalise_model("alpha", "shared", {"id": "shared"}, synced_at=EPOCH)
    second = normalise_model("beta", "shared", {"id": "shared"}, synced_at=EPOCH)

    assert first.ref.qualified != second.ref.qualified


async def test_catalog_comes_from_the_provider_api() -> None:
    """Nothing is written by hand: the entries in the store are the provider's own answer."""
    store = InMemoryCatalogStore()
    provider = ScriptedProvider("alpha", catalog=[("model-one", {"id": "model-one"}),
                                                  ("model-two", {"id": "model-two"})])
    gateway = build_gateway(catalog=store, factory=lambda config: provider)

    outcomes = await gateway.synchronise_catalog()

    assert outcomes[0].added == 2
    assert {item.ref.model_id for item in await store.list_models()} == {"model-one",
                                                                        "model-two"}


async def test_sync_is_idempotent() -> None:
    store = InMemoryCatalogStore()
    entries = [("model-one", {"id": "model-one"})]
    provider = ScriptedProvider("alpha", catalog=entries)
    gateway = build_gateway(catalog=store, factory=lambda config: provider)

    first = await gateway.synchronise_catalog()
    provider.catalog = entries
    second = await gateway.synchronise_catalog()

    assert first[0].added == 1
    assert second[0].added == 0
    assert second[0].unchanged == 1
    assert second[0].updated == 0


async def test_changed_metadata_is_reported_as_an_update() -> None:
    store = InMemoryCatalogStore()
    provider = ScriptedProvider("alpha", catalog=[("model-one", {"id": "model-one"})])
    gateway = build_gateway(catalog=store, factory=lambda config: provider)
    await gateway.synchronise_catalog()

    provider.catalog = [("model-one", {"id": "model-one", "context_length": 32000})]
    outcome = (await gateway.synchronise_catalog())[0]

    assert outcome.updated == 1
    assert (await store.list_models())[0].context_window == 32000


async def test_missing_model_is_deactivated_not_deleted() -> None:
    """Rows in model_calls point at it; deleting it would strand recorded history."""
    store = InMemoryCatalogStore()
    provider = ScriptedProvider("alpha", catalog=[("keep", {"id": "keep"}),
                                                  ("drop", {"id": "drop"})])
    gateway = build_gateway(catalog=store, factory=lambda config: provider)
    await gateway.synchronise_catalog()

    provider.catalog = [("keep", {"id": "keep"})]
    outcome = (await gateway.synchronise_catalog())[0]

    assert outcome.deactivated == 1
    everything = {item.ref.model_id: item for item in await store.list_models()}
    assert set(everything) == {"keep", "drop"}
    assert not everything["drop"].active


async def test_failed_sync_preserves_the_previous_catalog() -> None:
    """A provider having a bad day must not take the catalog offline."""
    store = InMemoryCatalogStore()
    provider = ScriptedProvider("alpha", catalog=[("model-one", {"id": "model-one"})])
    gateway = build_gateway(catalog=store, factory=lambda config: provider)
    await gateway.synchronise_catalog()

    provider.catalog = GatewayError(GatewayErrorType.PROVIDER_UNAVAILABLE, "down")
    outcome = (await gateway.synchronise_catalog())[0]

    assert outcome.errors
    survivors = await store.list_models()
    assert [item.ref.model_id for item in survivors] == ["model-one"]
    assert survivors[0].active
    assert store.providers["alpha"].healthy is False


async def test_an_empty_answer_is_refused_rather_than_applied() -> None:
    """Applying it would deactivate every model and take the gateway offline."""
    store = InMemoryCatalogStore()
    store.seed(descriptor())
    synchroniser = CatalogSynchroniser(store, FakeClock())

    with pytest.raises(GatewayError) as error:
        await synchroniser.apply(DiscoveredCatalog(provider_id="alpha", entries=()),
                                 display_name="Alpha", adapter="openai-compatible", enabled=True)

    assert error.value.error_type is GatewayErrorType.PROVIDER_UNAVAILABLE
    assert (await store.list_models())[0].active


async def test_a_failed_transaction_leaves_nothing_half_applied() -> None:
    """Normalisation happens before the store is touched, so a bad record commits nothing."""
    store = InMemoryCatalogStore()
    store.seed(descriptor())
    synchroniser = CatalogSynchroniser(store, FakeClock())

    with pytest.raises(GatewayError):
        await synchroniser.apply(
            DiscoveredCatalog(provider_id="alpha",
                              entries=(("dup", {"id": "dup"}), ("dup", {"id": "dup"}))),
            display_name="Alpha", adapter="openai-compatible", enabled=True)

    assert [item.ref.model_id for item in await store.list_models()] == ["model-one"]


async def test_the_provider_record_carries_the_sync_outcome() -> None:
    store = InMemoryCatalogStore()
    provider = ScriptedProvider("alpha", catalog=[("model-one", {"id": "model-one"})])
    gateway = build_gateway(
        providers={"alpha": provider_config()}, catalog=store,
        factory=lambda config: provider)

    await gateway.synchronise_catalog()

    record = store.providers["alpha"]
    assert record.model_count == 1
    assert record.healthy is True
    assert record.last_sync is not None
    assert not hasattr(record, "credential")
