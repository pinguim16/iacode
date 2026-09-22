"""Validation of a provider's base address.

The gateway makes outbound HTTP calls on behalf of callers. That is the shape of a server-side
request forgery, and the only thing that stops it being one is where the address comes from: an
administrator's configuration file, read at start-up, never a field of an inference request. The
contract enforces the second half by having no such field; this module enforces the first.

Four rules, each closing a way an address becomes dangerous:

**Scheme.** A remote provider is reached over HTTPS. Plain HTTP is accepted only for a loopback
address, which is what a locally-hosted runtime — vLLM, llama.cpp, an OpenAI-compatible server on
``127.0.0.1`` — actually uses. Allowing ``http://`` to a remote host would send an API key across
the network in clear text.

**User information.** ``https://user:password@provider.example`` is refused outright. It is a
credential in a field nothing redacts, it would be copied into every log line that records the base
URL, and a provider that needed it would be configured through the key variable instead.

**Shape.** A query string or a fragment on a base URL is refused: the adapter appends a path to it,
and ``https://host/?x=1`` plus ``/models`` is not a URL anyone intended.

**Determinism.** Nothing here resolves DNS. A check that resolved a hostname and approved the
address would be approving one answer to a question the HTTP client asks again later, and the two
answers need not agree. The defence against a hostile address is that the address is administrative
configuration, not that we out-guess the resolver.
"""

from __future__ import annotations

import ipaddress
from urllib.parse import urlsplit

__all__ = ["BaseUrlError", "normalise_base_url", "is_loopback_host"]

_LOOPBACK_NAMES = frozenset({"localhost", "localhost.localdomain", "ip6-localhost"})


class BaseUrlError(ValueError):
    """A configured provider address that may not be used."""


def is_loopback_host(host: str) -> bool:
    """Whether a host names this machine, by name or by address."""
    if not host:
        return False
    name = host.strip("[]").lower()
    if name in _LOOPBACK_NAMES:
        return True
    try:
        return ipaddress.ip_address(name).is_loopback
    except ValueError:
        return False


def normalise_base_url(value: str, *, allow_plain_http_loopback: bool = True) -> str:
    """Validate a configured base URL and return it without a trailing slash.

    Returning the normalised form rather than a boolean is deliberate: every caller needs the
    trailing slash removed before it appends a path, and a separate "clean it up" step is a step
    that gets skipped in the one place that matters.
    """
    if not isinstance(value, str) or not value.strip():
        raise BaseUrlError("a provider base URL is required and must not be empty")
    candidate = value.strip()

    try:
        parts = urlsplit(candidate)
    except ValueError as error:
        raise BaseUrlError(f"the provider base URL cannot be parsed: {error}") from error

    if parts.scheme not in ("http", "https"):
        raise BaseUrlError(
            f"a provider base URL must use http or https, found {parts.scheme or 'no scheme'!r}")
    if parts.username or parts.password:
        raise BaseUrlError(
            "a provider base URL must not embed user information; configure the credential "
            "through its environment variable instead")
    if not parts.hostname:
        raise BaseUrlError("a provider base URL must name a host")
    if parts.query or parts.fragment:
        raise BaseUrlError(
            "a provider base URL carries no query string and no fragment; the adapter appends a "
            "path to it")

    if parts.scheme == "http":
        if not allow_plain_http_loopback or not is_loopback_host(parts.hostname):
            raise BaseUrlError(
                "plain HTTP is allowed only for a loopback provider; a remote provider must be "
                "reached over HTTPS so the credential is not sent in clear text")

    path = parts.path.rstrip("/")
    authority = parts.netloc
    return f"{parts.scheme}://{authority}{path}"
