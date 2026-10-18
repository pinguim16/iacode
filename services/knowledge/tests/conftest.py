"""Explicit deterministic domain fixtures; SQL and functional proof use the real adapters."""

from __future__ import annotations

import hashlib
import uuid
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from iacode_contracts.knowledge import CuratedArtifact, SourceEntry, SourceGrant
from iacode_knowledge.domain import AdmittedSource, canonical, load_policy

PROJECT = "11473b5e-8081-46bb-a61a-90bd3a1ddc25"
SOURCE = "66f77c37-83c8-4828-8677-c4a1d4beb067"


@pytest.fixture
def now():
    return datetime(2026, 1, 1, tzinfo=UTC)


@pytest.fixture
def policy():
    root = next(
        parent
        for parent in Path(__file__).resolve().parents
        if (parent / ".iacode/policies/knowledge-policy.json").is_file()
    )
    return load_policy(root / ".iacode/policies/knowledge-policy.json")


def make_source(now, text="PostgreSQL migrations preserve source records and exact citations."):
    artifact = CuratedArtifact(
        schemaVersion="1.0.0",
        classification="curated-project-knowledge",
        createdAt=now - timedelta(seconds=1),
        title="Synthetic validation-only knowledge",
        text=text,
    )
    source_digest = hashlib.sha256(canonical(artifact.model_dump(mode="json"))).hexdigest()
    grant = SourceGrant(
        schemaVersion="1.0.0",
        kind="operator-reviewed-source-grant",
        grantId=str(uuid.uuid4()),
        projectId=PROJECT,
        sourceId=SOURCE,
        revision="fixture-v1",
        sourceDigest=source_digest,
        ownership="synthetic-validation-corpus",
        license="validation-only",
        authority="explicit fixture author for isolated automated validation",
        evidence=(
            "Permits storage and retrieval of this synthetic fixture only; no actual user data."
        ),
        reviewed=True,
        status="ACTIVE",
        storageAllowed=True,
        ragAllowed=True,
        trainingAllowed=False,
        distillationAllowed=False,
        validFrom=now - timedelta(hours=1),
        validUntil=now + timedelta(hours=1),
    )
    entry = SourceEntry(
        projectId=PROJECT,
        sourceId=SOURCE,
        revision="fixture-v1",
        artifactPath="artifacts/source.json",
        sourceDigest=source_digest,
        grantPath="grants/source.json",
        grantDigest=hashlib.sha256(canonical(grant.model_dump(mode="json"))).hexdigest(),
    )
    return AdmittedSource(entry, artifact, grant)


@pytest.fixture
def source(now):
    return make_source(now)
