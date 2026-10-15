"""Canonical credential-shape detection shared by runtime and delivery controls.

The patterns in this module are intentionally standard-library only.  Evidence is scanned inside
the evaluator image before it reaches durable storage, while the development ledger uses the same
taxonomy before it records or publishes repository evidence.  A second, weaker runtime copy would
allow a value rejected by the repository scanner to cross the product's evidence boundary.

Only finding *kinds* are returned.  Callers must never log or persist a matching value merely to
explain why it was rejected.
"""

from __future__ import annotations

import json
import re
from collections.abc import Iterator

__all__ = [
    "SECRET_PATTERNS", "find_secret_kinds", "iter_secret_scan_views", "redact_secret_patterns",
]


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
    found = {name for view, _line in iter_secret_scan_views(text)
             for name, pattern, _replacement in SECRET_PATTERNS if pattern.search(view)}
    return [name for name, _pattern, _replacement in SECRET_PATTERNS if name in found]


def iter_secret_scan_views(text: str) -> Iterator[tuple[str, int | None]]:
    """Sensitive in-memory transport views, shared with the publication scanner.

    Never log or persist a view. Finding consumers return only kinds, digests and locations.
    None locates exact matches in the original text; decoded views name their carrier's line,
    since decoded newlines are not additional source-file lines.
    """
    seen: set[tuple[str, int | None]] = set()
    pending: list[tuple[object, int | None]] = [(text, None)]
    while pending:
        value, carrier_line = pending.pop()
        if isinstance(value, str):
            if (value, carrier_line) in seen:
                continue
            seen.add((value, carrier_line))
            yield value, carrier_line
            # Without an escape, JSON decoding cannot introduce a new credential shape.
            # Keep exact lexical detection and avoid reparsing ordinary source/history blobs.
            if "\\" not in value:
                continue
            try:
                document = json.loads(value)
            except json.JSONDecodeError:
                # A stream may interleave ordinary tool logs with JSON records or strings.
                # Parse every potential value, not only a whole-document or line envelope.
                for document, start in _json_fragments(value):
                    origin = carrier_line or value.count("\n", 0, start) + 1
                    if isinstance(document, (dict, list)):
                        yield json.dumps(document, ensure_ascii=False), origin
                    pending.append((document, origin))
                continue
            origin = carrier_line or 1
            if isinstance(document, (dict, list)):
                yield json.dumps(document, ensure_ascii=False), origin
            pending.append((document, origin))
        elif isinstance(value, dict):
            pending.extend((item, carrier_line) for item in value)
            pending.extend((item, carrier_line) for item in value.values())
        elif isinstance(value, list):
            pending.extend((item, carrier_line) for item in value)


def _json_fragments(text: str):
    """Decode stream fragments with a content-derived work ceiling; exhaustion fails closed."""
    decoder = json.JSONDecoder()
    work = 0
    budget = max(1_000_000, len(text) * 20)
    for match in re.finditer(r'[\{\["]', text):
        start = match.start()
        try:
            document, end = decoder.raw_decode(text, start)
        except json.JSONDecodeError as error:
            # For an unterminated string the decoder reports its opening position, not the
            # end it actually searched. Charge that whole suffix, including overlapping starts.
            work += (len(text) - start if error.msg.startswith("Unterminated string")
                     else max(1, error.pos - start + 1))
            if work > budget:
                raise ValueError("JSON fragment scan work limit exceeded") from None
            continue
        work += end - start
        if work > budget:
            raise ValueError("JSON fragment scan work limit exceeded")
        yield document, start


def redact_secret_patterns(text: str) -> str:
    """Redact every canonical credential shape from text."""
    result = text
    for _name, pattern, replacement in SECRET_PATTERNS:
        result = pattern.sub(replacement, result)
    return result
