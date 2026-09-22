"""Typed configuration for the IACode API.

Configuration is validated once, at startup, and the process refuses to start when a mandatory
value is missing or malformed. A service that boots with an invalid database URL and only discovers
it on the first request has turned a configuration error into an incident.

Three layers, kept separate rather than conflated:

``defaults``      safe values compiled into the class. They are safe because they point at nothing:
                  ``localhost``, an empty CORS list, ``INFO`` logging. A default never carries a
                  credential and never enables something surprising.
``environment``   the real local configuration, supplied as ``IACODE_*`` environment variables. The
                  compose stack passes them; `infra/compose/.env.example` documents every one.
``test``          :func:`settings_for_tests`, which builds a settings object from explicit arguments
                  without reading the environment at all, so a test run cannot be coloured by the
                  developer's shell.

Every key declared here is read by the implementation. `.iacode/memory/lessons.jsonl` records the
opposite case as a defect: a configuration key that nothing consumes promises behaviour that does
not exist, so it is documentation at best and a lie at worst.
"""

from __future__ import annotations

import sys
from functools import lru_cache
from typing import Annotated, Literal

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

Environment = Literal["local", "test", "ci"]


class Settings(BaseSettings):
    """Every value the API reads, with its type and its validation."""

    model_config = SettingsConfigDict(
        env_prefix="IACODE_",
        env_file=None,
        case_sensitive=False,
        extra="ignore",
    )

    # --- identity -----------------------------------------------------------------------------
    service_name: str = Field(default="iacode-api", min_length=1)
    environment: Environment = "local"
    version: str = Field(default="0.1.0", min_length=1)
    commit: str = Field(
        default="unknown",
        description="Git commit the image was built from; 'unknown' outside a built image.")
    build_timestamp: str | None = Field(
        default=None, description="RFC 3339 instant the image was built.")

    # --- http ---------------------------------------------------------------------------------
    host: str = "0.0.0.0"
    port: Annotated[int, Field(ge=1, le=65535)] = 8000
    root_path: str = Field(
        default="",
        description="Prefix the API is served under when it sits behind a reverse proxy.")
    # ``NoDecode`` is load-bearing. Without it pydantic-settings sees a list-typed field and tries
    # to JSON-decode the environment variable before any validator runs, so the natural value —
    # ``http://a,http://b`` — fails to parse and the process dies at start-up with a message about
    # JSON. The splitting is done by the validator below instead.
    cors_allow_origins: Annotated[list[str], NoDecode] = Field(
        default_factory=list,
        description="Exact origins allowed to call the API. A wildcard is rejected.")
    correlation_header: str = Field(default="X-Correlation-ID", min_length=1)

    # --- logging ------------------------------------------------------------------------------
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"

    # --- postgresql ---------------------------------------------------------------------------
    database_url: str = Field(
        default="postgresql+asyncpg://iacode:iacode@localhost:5432/iacode",
        description="SQLAlchemy async URL of the system of record.")
    database_pool_size: Annotated[int, Field(ge=1, le=100)] = 5
    database_max_overflow: Annotated[int, Field(ge=0, le=100)] = 5
    database_connect_timeout_seconds: Annotated[float, Field(gt=0, le=60)] = 5.0

    # --- redis --------------------------------------------------------------------------------
    redis_url: str = Field(default="redis://localhost:6379/0")

    # --- object storage -----------------------------------------------------------------------
    minio_endpoint: str = Field(
        default="localhost:9000",
        description="Host and port only; the scheme is decided by minio_secure.")
    minio_access_key: SecretStr = SecretStr("")
    minio_secret_key: SecretStr = SecretStr("")
    minio_secure: bool = False
    minio_bucket: str = Field(default="iacode-artifacts", min_length=3)

    # --- temporal -----------------------------------------------------------------------------
    temporal_target: str = Field(default="localhost:7233")
    temporal_namespace: str = Field(default="default", min_length=1)
    # There is deliberately no task queue here. The API is a Temporal *client* in Gate 0: it
    # verifies connectivity and starts nothing, so a task queue name would be a key nothing reads.
    # The worker declares its own in services/orchestrator/config.py, and the Compose file passes
    # IACODE_TEMPORAL_TASK_QUEUE to both; this model ignores extras, so the value reaches the
    # process that uses it and no further.

    # --- readiness ----------------------------------------------------------------------------
    readiness_timeout_seconds: Annotated[float, Field(gt=0, le=30)] = 3.0

    @field_validator("cors_allow_origins", mode="before")
    @classmethod
    def _split_origins(cls, value: object) -> object:
        """Accept a comma-separated list, because that is what an environment variable carries."""
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    @field_validator("cors_allow_origins")
    @classmethod
    def _reject_wildcard(cls, value: list[str]) -> list[str]:
        """A permissive wildcard is refused rather than warned about.

        `docs/GATE-0-CHECKLIST.md` row 3.9 requires explicit CORS. Accepting ``*`` here and
        documenting it as development-only is how a development default reaches an environment
        that is not development.
        """
        if any(origin.strip() == "*" for origin in value):
            raise ValueError(
                "IACODE_CORS_ALLOW_ORIGINS may not contain '*'; list the exact origins")
        for origin in value:
            if not origin.startswith(("http://", "https://")):
                raise ValueError(f"CORS origin must include a scheme: {origin!r}")
        return value

    @field_validator("database_url")
    @classmethod
    def _require_async_driver(cls, value: str) -> str:
        """The persistence layer is asynchronous.

        A synchronous URL would silently block the event loop on every query.
        """
        if not value.startswith("postgresql+asyncpg://"):
            raise ValueError(
                "IACODE_DATABASE_URL must use the postgresql+asyncpg driver, found "
                f"{value.split('://', 1)[0]!r}")
        return value

    @field_validator("redis_url")
    @classmethod
    def _require_redis_scheme(cls, value: str) -> str:
        if not value.startswith(("redis://", "rediss://", "unix://")):
            raise ValueError("IACODE_REDIS_URL must use a redis://, rediss:// or unix:// scheme")
        return value

    @field_validator("minio_endpoint")
    @classmethod
    def _reject_scheme_in_endpoint(cls, value: str) -> str:
        """The MinIO SDK takes host:port and decides the scheme from ``secure``.

        Passing a URL here produces a client that silently builds ``http://http://host`` paths, so
        it is refused at load time instead of failing on the first object operation.
        """
        if "://" in value:
            raise ValueError(
                "IACODE_MINIO_ENDPOINT is host:port without a scheme; use IACODE_MINIO_SECURE")
        return value

    @property
    def python_version(self) -> str:
        return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"

    def safe_dump(self) -> dict[str, object]:
        """Configuration as it may be logged: every secret replaced, nothing else changed."""
        from iacode_common.redaction import redact_mapping

        raw = self.model_dump(mode="json")
        for name, field in type(self).model_fields.items():
            if field.annotation is SecretStr:
                raw[name] = "[REDACTED]" if getattr(self, name).get_secret_value() else ""
        return redact_mapping(raw)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """The process-wide settings, read from the environment exactly once.

    Cached because configuration is immutable for the lifetime of the process. Tests do not call
    this: they call :func:`settings_for_tests`, so no test depends on the ambient environment and
    test has to remember to clear a cache.
    """
    return Settings()


def settings_for_tests(**overrides: object) -> Settings:
    """Settings built from explicit values, ignoring the environment completely.

    Every field is supplied explicitly. Initialisation arguments outrank the environment in
    pydantic-settings, so listing all of them is what makes the result independent of the shell:
    the API test suite runs inside a container whose environment is full of real ``IACODE_*``
    values, and a field left out here would silently inherit one of them.
    """
    values: dict[str, object] = {
        "service_name": "iacode-api",
        "environment": "test",
        "version": "0.0.0-test",
        "commit": "test",
        "build_timestamp": None,
        "host": "127.0.0.1",
        "port": 8000,
        "root_path": "",
        "cors_allow_origins": ["http://localhost:4200"],
        "correlation_header": "X-Correlation-ID",
        "log_level": "WARNING",
        "database_url": "postgresql+asyncpg://iacode:iacode@localhost:5432/iacode_test",
        "database_pool_size": 1,
        "database_max_overflow": 0,
        "database_connect_timeout_seconds": 2.0,
        "redis_url": "redis://localhost:6379/1",
        "minio_endpoint": "localhost:9000",
        "minio_access_key": "test-access",
        "minio_secret_key": "test-secret",
        "minio_secure": False,
        "minio_bucket": "iacode-artifacts-test",
        "temporal_target": "localhost:7233",
        "temporal_namespace": "default",
        "readiness_timeout_seconds": 2.0,
    }
    values.update(overrides)
    missing = set(Settings.model_fields) - set(values)
    if missing:
        raise AssertionError(
            "settings_for_tests must supply every field so no test reads the ambient environment; "
            f"missing: {', '.join(sorted(missing))}")
    return Settings(_env_file=None, **values)  # type: ignore[arg-type]
