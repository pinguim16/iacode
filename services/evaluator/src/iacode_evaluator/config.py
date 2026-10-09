"""Validated process configuration for the Quality Engine worker."""

from __future__ import annotations

import socket
from functools import lru_cache
from pathlib import Path
from typing import Annotated, Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class EvaluatorSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="IACODE_", env_file=None, case_sensitive=False, extra="ignore"
    )

    service_name: str = Field(default="iacode-evaluator", min_length=1)
    version: str = Field(default="0.1.0", min_length=1)
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"

    temporal_target: str = "localhost:7233"
    temporal_namespace: str = Field(default="default", min_length=1)
    quality_task_queue: str = Field(default="iacode-quality", min_length=1)
    worker_connect_timeout_seconds: Annotated[float, Field(gt=0, le=600)] = 120.0

    database_url: str = "postgresql+asyncpg://iacode:iacode@localhost:5432/iacode"
    database_pool_size: Annotated[int, Field(ge=1, le=100)] = 5
    database_max_overflow: Annotated[int, Field(ge=0, le=100)] = 5
    database_connect_timeout_seconds: Annotated[float, Field(gt=0, le=120)] = 10.0

    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = ""
    minio_secret_key: str = ""
    minio_secure: bool = False
    minio_bucket: str = Field(default="iacode-artifacts", min_length=3)

    repository_root: str = "/app"
    quality_metrics_port: Annotated[int, Field(ge=1, le=65535)] = 9103

    @field_validator("temporal_target", "minio_endpoint")
    @classmethod
    def endpoint_has_no_scheme(cls, value: str) -> str:
        if "://" in value:
            raise ValueError("service endpoints are host:port without a scheme")
        return value

    @field_validator("database_url")
    @classmethod
    def asynchronous_database(cls, value: str) -> str:
        if not value.startswith("postgresql+asyncpg://"):
            raise ValueError("IACODE_DATABASE_URL must use postgresql+asyncpg")
        return value

    @property
    def identity(self) -> str:
        return f"{self.service_name}@{socket.gethostname()}"

    @property
    def policy_path(self) -> Path:
        return Path(self.repository_root) / ".iacode" / "policies" / "quality-policy.json"


@lru_cache(maxsize=1)
def get_evaluator_settings() -> EvaluatorSettings:
    return EvaluatorSettings()


def minio_client(settings: EvaluatorSettings):
    from minio import Minio

    return Minio(
        settings.minio_endpoint,
        access_key=settings.minio_access_key,
        secret_key=settings.minio_secret_key,
        secure=settings.minio_secure,
    )


__all__ = ["EvaluatorSettings", "get_evaluator_settings", "minio_client"]
