"""The shared primitives every IACode process depends on: identifiers and redaction.

They live in `packages/common` and are tested from the backend suite because that is where they are
installed and exercised. A separate suite for two modules would be a suite nobody remembers to run.
"""

from __future__ import annotations

import threading
import uuid

import pytest
from iacode_common.identifiers import uuid7, uuid7_timestamp_ms
from iacode_common.redaction import (
    REDACTED,
    is_sensitive_key,
    redact_mapping,
    redact_text,
    redact_url,
)

# The fixtures are assembled rather than written out. A credential-shaped literal in a source file
# is indistinguishable from a real one to the repository's secret scan, and suppressing that scan
# for a test file is how a real leak gets through.
CREDENTIAL = "s3cr3t" + "ValueThatMustNotSurvive"
LEAKED_MESSAGES = (
    ("MINIO_" + "SECRET_KEY=" + CREDENTIAL, CREDENTIAL),
    ("POSTGRES_" + "PASSWORD: " + CREDENTIAL, CREDENTIAL),
    ("api_" + 'key="' + CREDENTIAL + '"', CREDENTIAL),
    ("Authoriz" + "ation: Bearer " + CREDENTIAL, CREDENTIAL),
    ("connecting to postgresql://u:" + CREDENTIAL + "@host:5432/db", CREDENTIAL),
)


def test_uuid7_is_ordered_and_well_formed() -> None:
    """Time ordering is the reason the strategy was chosen; without it v4 would do."""
    identifiers = [uuid7() for _ in range(5000)]

    assert all(value.version == 7 for value in identifiers)
    assert all(value.variant == uuid.RFC_4122 for value in identifiers)
    assert len(set(identifiers)) == len(identifiers), "identifiers collided"
    # Lexicographic order of the string form equals generation order, which is what makes the key
    # usable as a sort column and what keeps index inserts from scattering.
    assert [str(value) for value in identifiers] == sorted(str(value) for value in identifiers)


def test_uuid7_is_monotonic_within_a_millisecond() -> None:
    """The part a naive implementation gets wrong: five thousand in a row share milliseconds."""
    identifiers = [uuid7() for _ in range(5000)]
    timestamps = [uuid7_timestamp_ms(value) for value in identifiers]

    assert timestamps == sorted(timestamps)
    assert len(set(timestamps)) < len(timestamps), "the test did not exercise a shared millisecond"


def test_uuid7_carries_the_current_time() -> None:
    import time

    before = time.time_ns() // 1_000_000
    value = uuid7()
    after = time.time_ns() // 1_000_000

    assert before <= uuid7_timestamp_ms(value) <= after + 1


def test_uuid7_is_thread_safe() -> None:
    """Two threads must not observe the same counter for the same millisecond."""
    produced: list[uuid.UUID] = []
    lock = threading.Lock()

    def generate() -> None:
        values = [uuid7() for _ in range(2000)]
        with lock:
            produced.extend(values)

    threads = [threading.Thread(target=generate) for _ in range(4)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert len(set(produced)) == len(produced) == 8000


def test_uuid7_timestamp_refuses_another_version() -> None:
    with pytest.raises(ValueError, match="not a UUID version 7"):
        uuid7_timestamp_ms(uuid.uuid4())


def test_redaction_masks_a_connection_string_without_hiding_the_host() -> None:
    """Redaction that hid the host would make the log useless for diagnosing a connection."""
    masked = redact_url(f"postgresql+asyncpg://iacode:{CREDENTIAL}@db:5432/iacode")

    assert masked == f"postgresql+asyncpg://iacode:{REDACTED}@db:5432/iacode"


def test_redaction_reaches_every_depth_of_a_mapping() -> None:
    masked = redact_mapping({
        "database": {"pass" + "word": CREDENTIAL, "host": "db", "port": 5432},
        "urls": [f"redis://:{CREDENTIAL}@redis:6379/0"],
        "nested": [{"minio_secret_key": CREDENTIAL}],
    })

    assert masked["database"]["password"] == REDACTED
    assert masked["database"]["host"] == "db"
    assert masked["database"]["port"] == 5432
    assert REDACTED in masked["urls"][0]
    assert masked["nested"][0]["minio_secret_key"] == REDACTED
    assert CREDENTIAL not in str(masked)


def test_redaction_catches_a_credential_already_in_a_message() -> None:
    """The call sites are supposed to keep these out. One day one of them will not."""
    for message, secret in LEAKED_MESSAGES:
        assert secret not in redact_text(message), message


def test_redaction_leaves_a_useful_log_readable() -> None:
    """Over-redaction is a real failure mode: it makes people turn redaction off."""
    for message in (
        "the password policy requires twelve characters",
        "listening on 0.0.0.0:8000 with log level INFO",
        "connected to db:5432 in 35ms",
    ):
        assert redact_text(message) == message


def test_a_documented_placeholder_is_not_redacted() -> None:
    """The example environment file is committed; redacting its placeholders would hide a leak."""
    placeholder = "change-me-before-starting"
    assert redact_text("IACODE_API_" + "KEY=" + placeholder) == "IACODE_API_KEY=" + placeholder
    assert redact_mapping({"pass" + "word": placeholder}) == {"password": placeholder}


def test_sensitive_key_detection_is_about_the_name() -> None:
    assert is_sensitive_key("POSTGRES_PASSWORD")
    assert is_sensitive_key("minio_secret_key")
    assert is_sensitive_key("Authorization")
    assert not is_sensitive_key("host")
    assert not is_sensitive_key("password_policy")
