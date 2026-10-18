"""One application-owned knowledge policy, real adapters and bounded observable retention task."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from iacode_knowledge.domain import KnowledgeService, load_policy
from iacode_telemetry.logging import get_logger

from iacode_api.knowledge.sources import CurrentKnowledgeSources
from iacode_api.knowledge.store import SqlKnowledgeStore

logger = get_logger(__name__)


@dataclass
class KnowledgeRuntime:
    service: KnowledgeService
    store: SqlKnowledgeStore
    sources: CurrentKnowledgeSources
    task: asyncio.Task | None = None

    async def sweep_forever(self) -> None:
        while True:
            await asyncio.sleep(self.service.policy.sweepIntervalSeconds)
            try:
                async with asyncio.timeout(self.service.policy.operationTimeoutSeconds):
                    counts = await self.store.sweep(self.sources)
                logger.info("knowledge retention sweep completed", extra=counts)
            except Exception as error:
                logger.error(
                    "knowledge retention sweep failed",
                    extra={
                        "code": "KNOWLEDGE_RETENTION_UNAVAILABLE",
                        "errorType": type(error).__name__,
                    },
                )

    def start(self) -> None:
        if self.task is not None:
            raise RuntimeError("knowledge retention task already owned")
        self.task = asyncio.create_task(self.sweep_forever(), name="knowledge-retention")

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
            await task
            raise RuntimeError("knowledge retention task ended unexpectedly")


def build_knowledge_runtime(settings: Any, sessions: Any, experience: Any) -> KnowledgeRuntime:
    root = Path(settings.repository_root)
    policy = load_policy(root / ".iacode/policies/knowledge-policy.json")
    source_root = Path(settings.knowledge_source_root)
    if not source_root.is_absolute():
        source_root = root / source_root
    credentials = experience.service.known_credentials
    store = SqlKnowledgeStore(sessions, policy, credentials)
    sources = CurrentKnowledgeSources(source_root, policy, experience, credentials)
    return KnowledgeRuntime(KnowledgeService(policy, sources, store, credentials), store, sources)
