"""Cross-cutting primitives shared by every IACode runtime component.

The package holds only what more than one component needs and what has no home in a single one:
identifier generation, credential redaction, and canonical credential-shape detection. It
deliberately depends on nothing but the standard library, so importing it can never drag a web
framework, a database driver or a workflow SDK into a process that does not want one.
"""

from iacode_common.identifiers import uuid7, uuid7_timestamp_ms
from iacode_common.redaction import (
    REDACTED,
    carries_a_secret_value,
    is_placeholder,
    is_sensitive_key,
    redact_mapping,
    redact_text,
    redact_url,
    redact_value,
)
from iacode_common.secret_scanning import (
    SECRET_PATTERNS,
    find_secret_kinds,
    redact_secret_patterns,
)

__all__ = [
    "REDACTED",
    "SECRET_PATTERNS",
    "carries_a_secret_value",
    "find_secret_kinds",
    "is_placeholder",
    "is_sensitive_key",
    "redact_mapping",
    "redact_secret_patterns",
    "redact_text",
    "redact_url",
    "redact_value",
    "uuid7",
    "uuid7_timestamp_ms",
]
