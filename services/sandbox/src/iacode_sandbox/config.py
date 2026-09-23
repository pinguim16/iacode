"""Typed configuration for the sandbox service.

Deliberately small. What a sandbox may *do* is not configuration of this process: it is the
canonical policy under ``.iacode/policies/sandbox-policy.json``, which the image carries. What is
here is where the service finds the rest of the stack — the database, the bucket, Temporal — and how
it runs: its metrics port, how often it sweeps and how many sessions one sweep may end.

Nothing here is ever passed to a sandbox. The service's own environment, credentials included,
stays in the service; a sandbox's environment is built by the helper from a fixed base and the
policy's allowlist.
"""

from __future__ import annotations

import socket
from functools import lru_cache
from typing import Annotated, Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

__all__ = ["SandboxSettings", "get_sandbox_settings", "minio_client"]


class SandboxSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="IACODE_", env_file=None, case_sensitive=False,
                                      extra="ignore")

    service_name: str = Field(default="iacode-sandbox", min_length=1)
    version: str = Field(default="0.1.0", min_length=1)
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"

    temporal_target: str = Field(default="localhost:7233")
    temporal_namespace: str = Field(default="default", min_length=1)
    worker_connect_timeout_seconds: Annotated[float, Field(gt=0, le=600)] = 120.0

    database_url: str = Field(
        default="postgresql+asyncpg://iacode:iacode@localhost:5432/iacode")
    database_pool_size: Annotated[int, Field(ge=1, le=100)] = 5
    database_max_overflow: Annotated[int, Field(ge=0, le=100)] = 5
    database_connect_timeout_seconds: Annotated[float, Field(gt=0, le=120)] = 10.0

    minio_endpoint: str = Field(default="localhost:9000")
    minio_access_key: str = Field(default="")
    minio_secret_key: str = Field(default="")
    minio_secure: bool = False
    minio_bucket: str = Field(default="iacode-artifacts", min_length=3)

    repository_root: str = Field(
        default="/app",
        description="Where the canonical policy and the sandbox image inputs live in this image.")
    sandbox_owner: str = Field(
        default="iacode", pattern=r"^[a-z0-9][a-z0-9_.-]{0,63}$",
        description="The owner label on every container this service creates. It lists and "
                    "removes only containers carrying it, so a second stack or a test suite on "
                    "the same engine is never touched.")
    sandbox_metrics_port: Annotated[int, Field(ge=1, le=65535)] = 9102
    sandbox_sweep_interval_seconds: Annotated[float, Field(ge=5, le=3600)] = 60.0
    sandbox_sweep_batch: Annotated[int, Field(ge=1, le=100)] = 10

    @field_validator("temporal_target")
    @classmethod
    def _reject_scheme(cls, value: str) -> str:
        if "://" in value:
            raise ValueError("IACODE_TEMPORAL_TARGET is host:port without a scheme")
        return value

    @property
    def identity(self) -> str:
        return f"{self.service_name}@{socket.gethostname()}"


@lru_cache(maxsize=1)
def get_sandbox_settings() -> SandboxSettings:
    return SandboxSettings()


def minio_client(settings: SandboxSettings):
    from minio import Minio

    return Minio(settings.minio_endpoint, access_key=settings.minio_access_key,
                 secret_key=settings.minio_secret_key, secure=settings.minio_secure)
