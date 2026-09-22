"""Configuration: what it accepts, what it refuses, and what it never reveals."""

from __future__ import annotations

import pytest
from iacode_api.config import Settings, get_settings, settings_for_tests
from pydantic import ValidationError


def test_configuration_rejects_invalid_values() -> None:
    """Every validator refuses at load time rather than at first use."""
    with pytest.raises(ValidationError):
        settings_for_tests(database_url="postgresql://iacode:iacode@localhost:5432/iacode")

    with pytest.raises(ValidationError):
        settings_for_tests(redis_url="http://localhost:6379")

    with pytest.raises(ValidationError):
        settings_for_tests(minio_endpoint="http://localhost:9000")

    with pytest.raises(ValidationError):
        settings_for_tests(port=0)

    with pytest.raises(ValidationError):
        settings_for_tests(log_level="CHATTY")


def test_cors_refuses_a_wildcard() -> None:
    with pytest.raises(ValidationError) as error:
        settings_for_tests(cors_allow_origins=["*"])
    assert "may not contain" in str(error.value)


def test_cors_requires_a_scheme() -> None:
    with pytest.raises(ValidationError):
        settings_for_tests(cors_allow_origins=["localhost:4200"])


def test_cors_accepts_a_comma_separated_environment_value() -> None:
    """An environment variable carries one string; the application needs a list."""
    settings = settings_for_tests(
        cors_allow_origins="http://localhost:4200, http://127.0.0.1:4200")

    assert settings.cors_allow_origins == ["http://localhost:4200", "http://127.0.0.1:4200"]


def test_configuration_layers_are_separate() -> None:
    """The defaults point at nothing, and the test profile is not the default profile."""
    defaults = Settings(_env_file=None, _env_prefix="IACODE_UNUSED_PREFIX_")

    assert defaults.environment == "local"
    assert defaults.cors_allow_origins == []
    assert defaults.minio_access_key.get_secret_value() == ""
    assert "localhost" in defaults.database_url

    profile = settings_for_tests()
    assert profile.environment == "test"
    assert profile.cors_allow_origins == ["http://localhost:4200"]


def test_test_settings_ignore_the_ambient_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    """A test must not change behaviour because of the shell it runs in."""
    monkeypatch.setenv("IACODE_LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("IACODE_MINIO_BUCKET", "somebody-elses-bucket")

    settings = settings_for_tests()

    assert settings.log_level == "WARNING"
    assert settings.minio_bucket == "iacode-artifacts-test"


def test_safe_dump_redacts_every_secret() -> None:
    settings = settings_for_tests(
        database_url="postgresql+asyncpg://iacode:hunter2@db:5432/iacode",
        minio_secret_key="a-real-looking-secret",
    )

    dumped = settings.safe_dump()

    assert dumped["minio_secret_key"] == "[REDACTED]"
    assert dumped["database_url"] == "postgresql+asyncpg://iacode:[REDACTED]@db:5432/iacode"
    assert "hunter2" not in str(dumped)
    assert "a-real-looking-secret" not in str(dumped)
    # Redaction that hid the host would make the dump useless for diagnosing a connection problem.
    assert "db:5432/iacode" in dumped["database_url"]


def test_every_declared_key_is_read_somewhere() -> None:
    """A configuration key nothing consumes promises behaviour that does not exist.

    The check reads the application source rather than trusting a list, so adding a field without
    using it fails here instead of surviving as documentation of a feature nobody built.
    """
    from pathlib import Path

    source_root = Path(__file__).resolve().parents[2] / "src"
    corpus = "\n".join(
        path.read_text(encoding="utf-8")
        for path in source_root.rglob("*.py")
        if path.name != "config.py"
    )
    # Read through a property rather than by name.
    read_indirectly = {"version", "commit", "build_timestamp", "service_name", "environment",
                       "host", "port"}
    unused = [
        name for name in Settings.model_fields
        if name not in read_indirectly and f"settings.{name}" not in corpus
        and f".{name}" not in corpus
    ]

    assert unused == [], f"declared but never read: {', '.join(unused)}"


def test_get_settings_is_cached() -> None:
    assert get_settings() is get_settings()
