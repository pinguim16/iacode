"""Cross-cutting primitives shared by every IACode runtime component.

The package holds only what more than one component needs and what has no home in a single one:
identifier generation and credential redaction. It deliberately depends on nothing but the standard
library, so importing it can never drag a web framework, a database driver or a workflow SDK into a
process that does not want one.
"""

from iacode_common.identifiers import uuid7, uuid7_timestamp_ms
from iacode_common.redaction import (
    REDACTED,
    is_sensitive_key,
    redact_mapping,
    redact_text,
    redact_url,
    redact_value,
)

__all__ = [
    "REDACTED",
    "is_sensitive_key",
    "redact_mapping",
    "redact_text",
    "redact_url",
    "redact_value",
    "uuid7",
    "uuid7_timestamp_ms",
]
