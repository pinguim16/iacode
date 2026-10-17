"""One application-owned policy, real adapters and retention task. Startup performs no I/O."""

from __future__ import annotations

import asyncio
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlsplit

from iacode_experience.domain import ExperienceService, load_policy
from iacode_telemetry.logging import get_logger
from sqlalchemy.engine import make_url

from iacode_api.experience.sources import SqlExperienceSources
from iacode_api.experience.store import SqlExperienceStore

logger = get_logger(__name__)


@dataclass
class ExperienceRuntime:
    service: ExperienceService
    store: SqlExperienceStore
    sources: SqlExperienceSources
    task: asyncio.Task | None = None

    async def sweep_forever(self) -> None:
        while True:
            # Delay the first probe too: Foundation startup remains dependency-I/O-free.
            await asyncio.sleep(self.service.policy.sweepIntervalSeconds)
            try:
                counts = await self.store.sweep()
                logger.info("experience retention sweep completed", extra=counts)
            except Exception as error:
                # The failure is observable; no SQL, input, credentials or exception text travels.
                logger.error(
                    "experience retention sweep failed",
                    extra={
                        "code": "RETENTION_STORE_UNAVAILABLE",
                        "errorType": type(error).__name__,
                    },
                )

    def start(self) -> None:
        if self.task is not None:
            raise RuntimeError("experience retention task already owned")
        self.task = asyncio.create_task(self.sweep_forever(), name="experience-retention")

    async def close(self) -> None:
        task, self.task = self.task, None
        if task is None:
            return
        if not task.done():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                if not task.cancelled():
                    raise
        else:
            # A task that ended unexpectedly must not be disguised as successful disposal.
            await task
            raise RuntimeError("experience retention task ended unexpectedly")


def build_experience_runtime(
    settings: Any, sessions: Any, minio: Any, quality_store: Any
) -> ExperienceRuntime:
    root = Path(settings.repository_root)
    policy = load_policy(root / ".iacode/policies/experience-policy.json")
    providers = json.loads((Path(settings.gateway_policy_dir) / "providers.json").read_bytes())
    credentials = tuple(
        filter(
            None,
            (
                settings.desktop_token.get_secret_value(),
                # The committed MinIO account identity is public, not its password component.
                # No value is globally exempt: identical text remains refused if it is an
                # actual configured bearer/password below. Canonical shape detection is intact.
                settings.minio_secret_key.get_secret_value(),
                make_url(settings.database_url).password,
                unquote(urlsplit(settings.redis_url).password or ""),
                *(os.environ.get(row["credential_env"], "") for row in providers["providers"]),
            ),
        )
    )
    store = SqlExperienceStore(sessions, policy)
    sources = SqlExperienceSources(sessions, minio, quality_store, policy, credentials)
    return ExperienceRuntime(ExperienceService(policy, sources, store, credentials), store, sources)
