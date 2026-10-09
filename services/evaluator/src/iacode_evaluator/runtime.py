"""Composition root shared by the evaluator worker and its activities."""

from __future__ import annotations

from dataclasses import dataclass

from prometheus_client import CollectorRegistry

from iacode_evaluator.config import EvaluatorSettings, minio_client
from iacode_evaluator.evidence import QualityEvidenceStore, SqlEvidenceRepository
from iacode_evaluator.policy import PolicyRegistry, load_policy
from iacode_evaluator.store import SqlQualityStore
from iacode_evaluator.telemetry import QualityMetrics


@dataclass
class EvaluatorRuntime:
    settings: EvaluatorSettings
    engine: object
    session_factory: object
    object_store: object
    policy: PolicyRegistry
    store: SqlQualityStore
    evidence: QualityEvidenceStore
    registry: CollectorRegistry
    metrics: QualityMetrics

    async def close(self) -> None:
        await self.engine.dispose()  # type: ignore[attr-defined]


def build_runtime(settings: EvaluatorSettings) -> EvaluatorRuntime:
    from iacode_persistence.engine import create_engine, create_session_factory

    engine = create_engine(
        settings.database_url,
        pool_size=settings.database_pool_size,
        max_overflow=settings.database_max_overflow,
        connect_timeout_seconds=settings.database_connect_timeout_seconds,
    )
    factory = create_session_factory(engine)
    objects = minio_client(settings)
    registry = CollectorRegistry()
    return EvaluatorRuntime(
        settings=settings,
        engine=engine,
        session_factory=factory,
        object_store=objects,
        policy=load_policy(settings.policy_path),
        store=SqlQualityStore(factory),
        evidence=QualityEvidenceStore(
            client=objects,
            bucket=settings.minio_bucket,
            repository=SqlEvidenceRepository(factory),
        ),
        registry=registry,
        metrics=QualityMetrics(registry, service=settings.service_name),
    )


__all__ = ["EvaluatorRuntime", "build_runtime"]
