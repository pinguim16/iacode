"""Canonical credential-shape detection shared by runtime and delivery controls.

The patterns in this module are intentionally standard-library only.  Evidence is scanned inside
the evaluator image before it reaches durable storage, while the development ledger uses the same
taxonomy before it records or publishes repository evidence.  A second, weaker runtime copy would
allow a value rejected by the repository scanner to cross the product's evidence boundary.

Only finding *kinds* are returned.  Callers must never log or persist a matching value merely to
explain why it was rejected.
"""

from __future__ import annotations

import re

__all__ = ["SECRET_PATTERNS", "find_secret_kinds", "redact_secret_patterns"]


SECRET_PATTERNS: tuple[tuple[str, re.Pattern[str], str], ...] = (
    (
        "authorization header",
        re.compile(
            r"(?i)(authorization[\"']?\s*:\s*[\"']?)(?!\[REDACTED\])"
            r"(?:(?:Bearer|Basic)\s+)?[-A-Za-z0-9._~+/=]{6,}"
        ),
        r"\1[REDACTED]",
    ),
    (
        "bearer credential",
        re.compile(
            r"(?i)\bBearer\s+(?!\[REDACTED\]|credentials?\b|tokens?\b|authentication\b)"
            r"[-A-Za-z0-9._~+/=]{8,}"
        ),
        "Bearer [REDACTED]",
    ),
    (
        "named secret assignment",
        re.compile(
            r"(?i)\b((?:[A-Z0-9]+_)*(?:API_KEY|TOKEN|SECRET|PASSWORD|ACCESS_KEY_ID|"
            r"SECRET_ACCESS_KEY)[\"']?\s*[:=]\s*[\"']?)"
            r"(?!\[REDACTED\]|example\b|placeholder\b|change[_-]?me[_-a-z0-9]*|"
            r"not[_-]?set\b|your[_-])[-A-Za-z0-9._~+/=:@]{6,}"
        ),
        r"\1[REDACTED]",
    ),
    ("DevWorld credential", re.compile(r"\bdw_live_[A-Za-z0-9_-]{8,}\b"), "[REDACTED]"),
    ("OpenAI-style key", re.compile(r"\bsk-[A-Za-z0-9_-]{12,}\b"), "[REDACTED]"),
    ("GitHub credential", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"), "[REDACTED]"),
    (
        "GitHub fine-grained credential",
        re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"),
        "[REDACTED]",
    ),
    (
        "private SSH key block",
        re.compile(
            r"-----BEGIN ((?:OPENSSH|RSA|EC|DSA) PRIVATE KEY)-----[\s\S]*?-----END \1-----",
            re.IGNORECASE,
        ),
        "[REDACTED]",
    ),
    (
        "private SSH key header",
        re.compile(r"-----BEGIN (?:OPENSSH|RSA|EC|DSA) PRIVATE KEY-----", re.IGNORECASE),
        "[REDACTED]",
    ),
)


def find_secret_kinds(text: str) -> list[str]:
    """Return the canonical finding kinds without returning matched values."""
    return [name for name, pattern, _replacement in SECRET_PATTERNS if pattern.search(text)]


def redact_secret_patterns(text: str) -> str:
    """Redact every canonical credential shape from text."""
    result = text
    for _name, pattern, replacement in SECRET_PATTERNS:
        result = pattern.sub(replacement, result)
    return result
