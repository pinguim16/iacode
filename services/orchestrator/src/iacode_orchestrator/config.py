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

    # --- Gate 2: what the agent runtime needs of the worker ------------------------------------
    # The worker executes agent runs, so it reads the system of record and it calls the Model
    # Gateway. It does **not** compose a gateway of its own: it calls the gateway's published HTTP
    # contract, which is why there is no provider setting, no policy directory and no credential
    # name anywhere in this class.
    database_url: str = Field(
        default="postgresql+asyncpg://iacode:iacode@localhost:5432/iacode")
    database_pool_size: Annotated[int, Field(ge=1, le=100)] = 5
    database_max_overflow: Annotated[int, Field(ge=0, le=100)] = 5
    database_connect_timeout_seconds: Annotated[float, Field(gt=0, le=120)] = 10.0

    repository_root: str = Field(
        default="/app",
        description="Where agents/ lives in this process. The image copies the declared profiles "
                    "there; a checkout runs from the repository root.")

    agent_runtime_gateway_url: str = Field(
        default="http://api:8000",
        description="Base address of the IACode API, which hosts the Model Gateway. Not a "
                    "provider address: the runtime cannot reach a provider and has no credential.")
    agent_runtime_request_timeout_seconds: Annotated[float, Field(gt=0, le=1800)] = 300.0
    agent_runtime_max_output_tokens: Annotated[int, Field(ge=1, le=100_000)] = 2048
    agent_runtime_task_queue: str = Field(
        default="iacode-agent-runtime", min_length=1,
        description="A queue of its own, so a long agent run never starves the Foundation smoke "
                    "workflow and the two can be scaled independently.")
    agent_runtime_metrics_port: Annotated[int, Field(ge=1, le=65535)] = 9101

    @field_validator("agent_runtime_gateway_url")
    @classmethod
    def _requires_a_scheme(cls, value: str) -> str:
        """An HTTP base address, unlike the Temporal target. A bare host:port would be read by
        httpx as a relative path and every call would fail with a confusing URL error."""
        if not value.startswith(("http://", "https://")):
            raise ValueError("IACODE_AGENT_RUNTIME_GATEWAY_URL is an http:// or https:// address")
        return value.rstrip("/")

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
