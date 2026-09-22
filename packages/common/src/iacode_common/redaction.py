"""Runtime redaction of credential-shaped values.

`.iacode/policies/secret-policy.md` forbids a credential from reaching a record. The development
ledger enforces that over *text* it is about to store. This module is the runtime counterpart: the
API and the worker handle configuration objects, log event dictionaries, HTTP headers and database
URLs, and a text-only redactor cannot see a secret that is still a value in a mapping.

Three shapes are covered, because a secret escapes through whichever one is left out:

- **by key** — any mapping key whose name marks it as sensitive, at any depth;
- **by URL** — the user information of a connection string, which is a password in a field whose
  key is innocuous (``database_url``);
- **by text** — a credential already interpolated into a message, which no key can protect.

Redaction is not reversible and never logs what it replaced. A value it cannot classify is left
alone: over-redacting a log until it stops being useful pushes engineers to turn redaction off,
which is a worse outcome than a redacted field they can still reason about.
"""

from __future__ import annotations

import re
from typing import Any
from urllib.parse import urlsplit, urlunsplit

__all__ = [
    "REDACTED",
    "is_sensitive_key",
    "redact_mapping",
    "redact_text",
    "redact_url",
    "redact_value",
]

REDACTED = "[REDACTED]"

# A key is sensitive when its *name* says the value is a credential. Matching on a substring is
# deliberate: ``POSTGRES_PASSWORD``, ``password`` and ``db_password_file`` are all the same risk.
_SENSITIVE_KEY = re.compile(
    r"(?i)(password|passwd|secret|token|api[-_]?key|access[-_]?key|private[-_]?key|"
    r"credential|authorization|auth[-_]?header|session[-_]?key|signing[-_]?key)"
)

# A key that merely mentions a sensitive word without holding a value. Redacting these produces
# logs where the redaction markers outnumber the information.
_SENSITIVE_KEY_EXEMPT = re.compile(
    r"(?i)^(password_policy|token_url|secret_policy|api_key_header|authorization_scheme|"
    r"credential_provider|has_password|password_set)$"
)

# Values that are documentation rather than credentials. The example environment file is committed
# on purpose, and redacting its placeholders would hide whether a real value had leaked into it.
_PLACEHOLDER = re.compile(
    r"(?i)^(|\[redacted\]|change[-_]?me[-_a-z0-9]*|example|placeholder|not[-_]?set|none|null|"
    r"your[-_].*|<.*>|\$\{.*\})$"
)

_TEXT_PATTERNS: tuple[re.Pattern[str], ...] = (
    # An authorization header, with or without a Bearer or Basic prefix, in a log line or a
    # serialised mapping. The pattern is written out rather than quoted as an example, because
    # an example of the shape is indistinguishable from the shape.
    re.compile(
        r"(?i)(authorization[\"']?\s*[:=]\s*[\"']?)(?!\[REDACTED\])"
        r"(?:(?:bearer|basic)\s+)?[-A-Za-z0-9._~+/=]{6,}"
    ),
    # NAME_TOKEN=<value>, api_key: "<value>", password = <value>
    re.compile(
        r"(?i)\b((?:[A-Za-z0-9]+[-_])*"
        r"(?:secret[-_]?access[-_]?key|access[-_]?key[-_]?id|secret[-_]?key|api[-_]?key|"
        r"access[-_]?key|private[-_]?key|signing[-_]?key|credential|token|secret|passwd|password)"
        r"[\"']?\s*[:=]\s*[\"']?)"
        r"(?!\[REDACTED\]|example\b|placeholder\b|changeme\b|not[-_]?set\b|your[-_])"
        r"[-A-Za-z0-9._~+/=:@]{6,}"
    ),
)

_SCHEME_WITH_USERINFO = re.compile(r"(?i)^[a-z][a-z0-9+.\-]*://[^/\s]*@")

# The same shape found anywhere inside a longer message, so a connection string interpolated into
# a log line is redacted even though no key protects it.
_EMBEDDED_URL = re.compile(r"(?i)\b[a-z][a-z0-9+.\-]*://[^\s\"']*@[^\s\"']*")


def is_sensitive_key(key: str) -> bool:
    """Whether a mapping key marks its value as a credential."""
    name = str(key)
    if _SENSITIVE_KEY_EXEMPT.match(name):
        return False
    return _SENSITIVE_KEY.search(name) is not None


def redact_url(value: str) -> str:
    """Mask the password inside a connection string, keeping the rest readable.

    ``postgresql+asyncpg://iacode:hunter2@db:5432/iacode`` becomes
    ``postgresql+asyncpg://iacode:[REDACTED]@db:5432/iacode``. The host, the port, the database and
    the user survive, because those are what an operator reads a log to find out.
    """
    if not _SCHEME_WITH_USERINFO.match(value):
        return value
    try:
        parts = urlsplit(value)
    except ValueError:
        return REDACTED
    if parts.password is None:
        return value
    host = parts.hostname or ""
    if parts.port:
        host = f"{host}:{parts.port}"
    userinfo = f"{parts.username or ''}:{REDACTED}"
    return urlunsplit((parts.scheme, f"{userinfo}@{host}", parts.path, parts.query, parts.fragment))


def redact_text(value: str) -> str:
    """Replace credential-shaped substrings already interpolated into a message."""
    result = _EMBEDDED_URL.sub(lambda match: redact_url(match.group(0)), value)
    for pattern in _TEXT_PATTERNS:
        result = pattern.sub(lambda match: match.group(1) + REDACTED, result)
    return result


def redact_value(key: str, value: Any) -> Any:
    """Redact one value in the context of the key it was stored under."""
    if isinstance(value, (dict, list, tuple)):
        return redact_mapping(value)
    if value is None or isinstance(value, (bool, int, float)):
        return value
    text = str(value)
    if is_sensitive_key(key):
        return value if _PLACEHOLDER.match(text) else REDACTED
    if _SCHEME_WITH_USERINFO.match(text):
        return redact_url(text)
    return redact_text(text)


def redact_mapping(value: Any) -> Any:
    """Recursively redact a mapping, sequence or scalar taken from configuration or a log event."""
    if isinstance(value, dict):
        return {key: redact_value(str(key), item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        redacted = [redact_mapping(item) for item in value]
        return type(value)(redacted) if isinstance(value, tuple) else redacted
    if isinstance(value, str):
        return redact_value("", value)
    return value
