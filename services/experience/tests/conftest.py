"""Pure domain fixtures only; these are not evidence of real persistence or HTTP acceptance."""

from __future__ import annotations

import json
from datetime import UTC, datetime

import pytest
from iacode_contracts.experience import ExperienceDocument
from iacode_experience.domain import ExperiencePolicy, digest


@pytest.fixture
def policy() -> ExperiencePolicy:
    return ExperiencePolicy(
        schemaVersion="1.0.0",
        defaultRetentionSeconds=30,
        maxRetentionSeconds=90,
        captureMaxAgeSeconds=90,
        tombstoneRetentionSeconds=90,
        sweepIntervalSeconds=1,
        batchSize=2,
        maxFacts=1000,
        maxBodyBytes=262144,
        maxRequestBytes=4096,
        maxPageSize=50,
    )


@pytest.fixture
def body() -> dict:
    task = {
        "projectId": "00000000-0000-4000-8000-000000000001",
        "taskId": "00000000-0000-4000-8000-000000000002",
        "runId": "00000000-0000-4000-8000-000000000003",
        "status": "SUCCEEDED",
        "attempt": 1,
        "startedAt": "2026-10-17T00:00:00Z",
        "finishedAt": "2026-10-17T00:00:01Z",
    }
    # Bind the normalized task, including Pydantic's exact datetime representation.
    value = {
        "task": task,
        "environment": {},
        "provider": [],
        "model": [],
        "trajectorySummary": "SUCCEEDED; agents=0; modelCalls=0; tools=0; quality=UNKNOWN",
        "actions": [],
        "toolCalls": [],
        "commands": [],
        "files": {"snapshotId": None, "digest": None, "sizeBytes": None, "fileCount": None},
        "attempts": [],
        "failures": [],
        "corrections": [],
        "tests": {"checks": [], "caseCount": None},
        "quality": None,
        "finalResult": {"taskStatus": "SUCCEEDED", "qualityVerdict": None},
        "provenance": [
            {
                "sourceType": "task-run",
                "sourceId": task["runId"],
                "digest": "0" * 64,
                "storageAllowed": True,
            }
        ],
        "trainingEligibility": {},
    }
    normalized = ExperienceDocument.model_validate_json(json.dumps(value)).model_dump(mode="json")
    normalized["provenance"][0]["digest"] = digest(normalized["task"])
    return normalized


@pytest.fixture
def now() -> datetime:
    return datetime(2026, 10, 17, 0, 0, 2, tzinfo=UTC)
