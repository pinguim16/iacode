"""Typed configuration for the worker.

Separate from the API's settings because the two processes need different things: the worker has no
HTTP surface, no CORS and no object storage, and inheriting the API's model would force it to carry
— and validate — configuration it never reads. `.iacode/memory/lessons.jsonl` records a declared key
with no consumer as a defect, and a shared settings class is the most common way to acquire one.

The two share a prefix (``IACODE_``) and the Temporal keys, so one ``.env`` configures both.
"""

from __future__ import annotations

import socket
from functools import lru_cache
from typing import Annotated, Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class WorkerSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="IACODE_",
        env_file=None,
        case_sensitive=False,
        extra="ignore",
    )

    service_name: str = Field(default="iacode-worker", min_length=1)
    version: str = Field(default="0.1.0", min_length=1)
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"

    temporal_target: str = Field(default="localhost:7233")
    temporal_namespace: str = Field(default="default", min_length=1)
    temporal_task_queue: str = Field(default="iacode-foundation", min_length=1)
    worker_connect_timeout_seconds: Annotated[float, Field(gt=0, le=600)] = 120.0
    worker_identity: str = Field(
        default="",
        description="Worker identity in Temporal; the container hostname when left empty.")

    @field_validator("temporal_target")
    @classmethod
    def _reject_scheme(cls, value: str) -> str:
        """``Client.connect`` takes host:port. A URL here fails at connect time with a DNS error."""
        if "://" in value:
            raise ValueError("IACODE_TEMPORAL_TARGET is host:port without a scheme")
        return value

    @property
    def namespace(self) -> str:
        return self.temporal_namespace

    @property
    def task_queue(self) -> str:
        return self.temporal_task_queue

    @property
    def connect_timeout_seconds(self) -> float:
        return self.worker_connect_timeout_seconds

    @property
    def identity(self) -> str:
        """A stable, meaningful identity so Temporal's UI names the worker rather than a number."""
        return self.worker_identity or f"{self.service_name}@{socket.gethostname()}"


@lru_cache(maxsize=1)
def get_worker_settings() -> WorkerSettings:
    return WorkerSettings()
