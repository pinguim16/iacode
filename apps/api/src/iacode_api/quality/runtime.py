"""Quality use cases available to the HTTP process without execution capability."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from iacode_evaluator.policy import load_policy
from iacode_evaluator.service import QualityService
from iacode_evaluator.snapshots import SnapshotProjectReader
from iacode_evaluator.store import SqlQualityStore


@dataclass(frozen=True)
class QualityApiRuntime:
    service: QualityService
    store: SqlQualityStore
    snapshots: SnapshotProjectReader
    task_queue: str


def build_quality_runtime(settings: Any, session_factory: Any, minio: Any) -> QualityApiRuntime:
    store = SqlQualityStore(session_factory)
    policy_path = Path(settings.repository_root) / ".iacode" / "policies" / "quality-policy.json"
    return QualityApiRuntime(
        service=QualityService(registry=load_policy(policy_path), store=store),
        store=store,
        snapshots=SnapshotProjectReader(session_factory, minio),
        task_queue=settings.quality_task_queue,
    )


__all__ = ["QualityApiRuntime", "SnapshotProjectReader", "build_quality_runtime"]
