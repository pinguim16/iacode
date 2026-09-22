"""The trust boundary: where an address may come from and what it may look like."""

from __future__ import annotations

import pytest
from fixtures.doubles import provider_config, request as build_request
from iacode_model_gateway.config import resolve_provider
from iacode_model_gateway.contracts import GatewayRequest
from iacode_model_gateway.errors import GatewayError, GatewayErrorType
from iacode_model_gateway.security.base_url import (
    BaseUrlError,
    is_loopback_host,
    normalise_base_url,
)


class BaseUrlSafetyTests:
    """A gateway makes outbound calls; where the address comes from is what stops it being SSRF."""

    def test_https_is_accepted_and_normalised(self) -> None:
        assert normalise_base_url("https://provider.example/v1/") == "https://provider.example/v1"
        assert normalise_base_url(" https://provider.example ") == "https://provider.example"

    def test_plain_http_to_a_remote_host_is_refused(self) -> None:
        """It would put the credential on the wire in clear text."""
        with pytest.raises(BaseUrlError) as error:
            normalise_base_url("http://provider.example")

        assert "clear text" in str(error.value)

    def test_plain_http_to_loopback_is_allowed(self) -> None:
        """A locally hosted runtime is the case this exists for."""
        assert normalise_base_url("http://127.0.0.1:8000/v1") == "http://127.0.0.1:8000/v1"
        assert normalise_base_url("http://localhost:11434") == "http://localhost:11434"
        assert normalise_base_url("http://[::1]:8000") == "http://[::1]:8000"

    def test_loopback_can_be_refused_by_policy(self) -> None:
        with pytest.raises(BaseUrlError):
            normalise_base_url("http://127.0.0.1:8000", allow_plain_http_loopback=False)

    def test_user_information_is_refused(self) -> None:
        """A credential in a field nothing redacts, copied into every log line."""
        with pytest.raises(BaseUrlError) as error:
            normalise_base_url("https://user:pass@provider.example")

        assert "user information" in str(error.value)

    def test_another_scheme_is_refused(self) -> None:
        for candidate in ("file:///etc/passwd", "ftp://provider.example",
                          "gopher://provider.example", "provider.example"):
            with pytest.raises(BaseUrlError):
                normalise_base_url(candidate)

    def test_a_query_or_fragment_is_refused(self) -> None:
        with pytest.raises(BaseUrlError):
            normalise_base_url("https://provider.example/v1?key=value")
        with pytest.raises(BaseUrlError):
            normalise_base_url("https://provider.example/v1#fragment")

    def test_an_empty_address_is_refused(self) -> None:
        with pytest.raises(BaseUrlError):
            normalise_base_url("   ")

    def test_loopback_detection_reads_the_address_not_the_spelling(self) -> None:
        assert is_loopback_host("127.0.0.1")
        assert is_loopback_host("127.9.9.9")
        assert is_loopback_host("::1")
        assert is_loopback_host("LOCALHOST")
        assert not is_loopback_host("10.0.0.1")
        assert not is_loopback_host("localhost.attacker.example")

    def test_nothing_here_resolves_dns(self) -> None:
        """A check that approved one DNS answer would approve a question asked again later."""
        import inspect

        from iacode_model_gateway.security import base_url

        source = inspect.getsource(base_url)
        assert "getaddrinfo" not in source
        assert "gethostbyname" not in source
        assert "socket" not in source


def test_request_cannot_supply_a_provider_address() -> None:
    """There is no field for it, which is stronger than validating one."""
    fields = set(GatewayRequest.model_fields)

    assert not fields & {"base_url", "baseUrl", "endpoint_url", "url", "host", "headers",
                         "api_key", "credential", "authorization"}
    request = build_request(metadata={"base_url": "https://attacker.example"})
    # Metadata is opaque annotation, never read as configuration.
    assert request.metadata["base_url"] == "https://attacker.example"


def test_a_configured_address_that_is_unusable_fails_loudly() -> None:
    with pytest.raises(GatewayError) as error:
        resolve_provider(provider_config(), {
            "IACODE_ALPHA_BASE_URL": "http://provider.example",
            "IACODE_ALPHA_CREDENTIAL": "value",
        })

    assert error.value.error_type is GatewayErrorType.INVALID_REQUEST
    assert "unusable address" in error.value.message


def test_a_missing_address_names_the_variable() -> None:
    with pytest.raises(GatewayError) as error:
        resolve_provider(provider_config(), {"IACODE_ALPHA_CREDENTIAL": "value"})

    assert "IACODE_ALPHA_BASE_URL" in error.value.message


def test_the_gateway_never_reads_an_address_from_request_metadata() -> None:
    """The only consumer of metadata is the caller's own annotation of its request."""
    import inspect

    from iacode_model_gateway import gateway as gateway_module
    from iacode_model_gateway.providers import http_provider

    for module in (gateway_module, http_provider):
        source = inspect.getsource(module)
        assert "request.metadata" not in source
