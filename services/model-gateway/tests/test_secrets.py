"""Where a credential is allowed to be, which is nowhere but the call it authenticates."""

from __future__ import annotations

import json
import logging

import pytest
from fixtures.doubles import (
    InMemoryCatalogStore,
    InMemoryModelCallStore,
    ScriptedProvider,
    build_gateway,
    completion,
    descriptor,
    gateway_source_root,
    policy_dir,
    provider_config,
    request as build_request,
)
from iacode_model_gateway.config import (
    ProviderConfig,
    load_provider_configs,
    resolve_provider,
    resolve_secret,
)
from iacode_model_gateway.errors import GatewayError, GatewayErrorType
from iacode_model_gateway.ports import ModelCallRecord, ProviderRecord
from iacode_model_gateway.protocols.anthropic_messages import AnthropicMessagesAdapter
from iacode_model_gateway.protocols.openai_chat import OpenAiChatAdapter
from iacode_telemetry.logging import JsonLogFormatter

#: Built rather than written. A literal of this shape in a test file is indistinguishable from a
#: leak to the repository secret scan, and suppressing the scan for one file is how a real one gets
#: through — a defect this project already has a lesson about.
CREDENTIAL = "dw" + "-live-" + "z" * 32

ENVIRONMENT = {
    "IACODE_ALPHA_BASE_URL": "https://provider.example/v1",
    "IACODE_ALPHA_CREDENTIAL": CREDENTIAL,
}


class SecretContainmentTests:
    """The credential reaches the authorization header and nothing else."""

    def test_the_resolved_provider_hides_it_from_every_rendering(self) -> None:
        resolved = resolve_provider(provider_config(), ENVIRONMENT)

        assert CREDENTIAL not in repr(resolved)
        assert CREDENTIAL not in str(resolved)
        assert CREDENTIAL not in json.dumps(resolved.model_dump(mode="json"))
        assert resolved.credential.get_secret_value() == CREDENTIAL

    def test_only_the_adapter_reads_the_value(self) -> None:
        headers = OpenAiChatAdapter().auth_headers(CREDENTIAL)
        anthropic = AnthropicMessagesAdapter().auth_headers(CREDENTIAL)

        assert headers["Authorization"].endswith(CREDENTIAL)
        assert anthropic["x-api-key"] == CREDENTIAL

    def test_the_call_description_carries_no_credential(self) -> None:
        """An adapter builds a call without the header, so a fixture of one is safe to keep."""
        call = OpenAiChatAdapter().build_generate(
            build_request(), descriptor(), stream=False, path="/chat/completions",
            max_output_tokens=16)

        assert CREDENTIAL not in json.dumps({"headers": call.headers, "body": call.json_body})
        assert "Authorization" not in call.headers

    def test_a_provider_configuration_has_nowhere_to_put_one(self) -> None:
        fields = set(ProviderConfig.model_fields)

        assert "credential" not in fields
        assert "api_key" not in fields
        assert "token" not in fields
        assert "credential_env" in fields

    def test_a_store_record_has_nowhere_to_put_one(self) -> None:
        provider_fields = set(ProviderRecord.__dataclass_fields__)
        call_fields = set(ModelCallRecord.__dataclass_fields__)

        assert not provider_fields & {"credential", "api_key", "token", "secret"}
        assert not call_fields & {"credential", "api_key", "token", "secret", "prompt",
                                  "messages", "completion", "response"}

    def test_the_log_formatter_redacts_a_credential_that_reached_a_record(self) -> None:
        """Belt and braces: the call sites keep it out, and one day one of them will not."""
        formatter = JsonLogFormatter(service="test")
        record = logging.LogRecord(
            "iacode", logging.INFO, __file__, 1,
            "calling provider", (), None)
        record.__dict__["providerCredential"] = CREDENTIAL

        rendered = formatter.format(record)

        assert CREDENTIAL not in rendered

    def test_an_absent_credential_is_a_state_not_an_empty_string(self) -> None:
        """Treating absent as empty sends an unauthenticated request nobody can explain."""
        assert resolve_secret("IACODE_ALPHA_CREDENTIAL", {}) is None
        assert resolve_secret("IACODE_ALPHA_CREDENTIAL", {"IACODE_ALPHA_CREDENTIAL": "  "}) is None

        with pytest.raises(GatewayError) as error:
            resolve_provider(provider_config(),
                             {"IACODE_ALPHA_BASE_URL": "https://provider.example"})

        assert error.value.error_type is GatewayErrorType.AUTHENTICATION_ERROR
        assert "IACODE_ALPHA_CREDENTIAL" in error.value.message

    async def test_a_recorded_call_carries_no_content_and_no_credential(self) -> None:
        store = InMemoryCatalogStore()
        store.seed(descriptor())
        calls = InMemoryModelCallStore()
        provider = ScriptedProvider("alpha", completions=[completion()])
        gateway = build_gateway(catalog=store, calls=calls, factory=lambda config: provider)

        await gateway.infer(build_request())

        rendered = json.dumps([record.__dict__ for record in calls.calls], default=str)
        assert CREDENTIAL not in rendered
        assert "Say hello." not in rendered
        assert "hello" not in rendered

    async def test_a_failure_message_never_quotes_the_provider_body(self) -> None:
        store = InMemoryCatalogStore()
        store.seed(descriptor())
        echoed = GatewayError(
            GatewayErrorType.INVALID_REQUEST,
            "the provider refused the request", provider="alpha")
        provider = ScriptedProvider("alpha", completions=[echoed])
        gateway = build_gateway(catalog=store, factory=lambda config: provider)

        with pytest.raises(GatewayError) as error:
            await gateway.infer(build_request())

        assert CREDENTIAL not in json.dumps(error.value.to_dict(), default=str)


def test_no_fake_provider_is_registered_at_runtime() -> None:
    """The deterministic double lives under the fixtures and is reachable from nowhere else."""
    configs = load_provider_configs(policy_dir())
    identifiers = {config.provider_id for config in configs}

    assert identifiers
    assert not identifiers & {"fake", "scripted", "double", "mock", "stub", "test"}
    for config in configs:
        assert config.adapter != "scripted"

    for path in sorted(gateway_source_root().rglob("*.py")):
        text = path.read_text(encoding="utf-8")
        assert "ScriptedProvider" not in text, f"{path.name} reaches the test double"
        assert "fixtures.doubles" not in text, f"{path.name} imports the test doubles"


def test_the_provider_policy_carries_no_credential_value() -> None:
    policy = policy_dir()

    for config in load_provider_configs(policy):
        assert config.credential_env == config.credential_env.upper()
        assert config.base_url_env == config.base_url_env.upper()

    raw = (policy / "providers.json").read_text(encoding="utf-8")
    assert "sk-" not in raw
    assert "Bearer " not in raw


def test_a_configuration_that_put_a_value_where_a_name_belongs_is_refused() -> None:
    """The crude shape check is what catches a credential pasted into the wrong field."""
    with pytest.raises(ValueError):
        provider_config(credential_env=CREDENTIAL)
