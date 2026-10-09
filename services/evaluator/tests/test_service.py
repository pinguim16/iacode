"""The stable internal Quality Engine use-case boundary."""

from __future__ import annotations

import asyncio
import os
from pathlib import Path

import pytest
from iacode_evaluator.errors import QualityError
from iacode_evaluator.policy import load_policy
from iacode_evaluator.service import QualityService
from iacode_evaluator.store import MemoryQualityStore

ROOT = (
    Path(os.environ["IACODE_REPOSITORY_ROOT"]).resolve()
    if os.environ.get("IACODE_REPOSITORY_ROOT")
    else next(
        parent
        for parent in Path(__file__).resolve().parents
        if (parent / ".iacode" / "policies").is_dir()
    )
)
POLICY = ROOT / ".iacode" / "policies" / "quality-policy.json"
SHA = "a" * 64


def run(coroutine):
    return asyncio.run(coroutine)


@pytest.fixture
def service() -> QualityService:
    return QualityService(registry=load_policy(POLICY), store=MemoryQualityStore())


class QualityServiceTests:
    def test_profile_plan_start_read_cancel_and_reproduce_use_one_boundary(self, service) -> None:
        planned = run(
            service.create_profile_and_plan(
                snapshot_id="snapshot-1",
                snapshot_digest=SHA,
                project_files={"pyproject.toml": "[project]\nname='fixture'\n"},
                configuration=None,
                owner_run_id="owner-1",
            )
        )
        assert planned.profile.stacks == ("python",)
        started = run(
            service.start_run(
                plan_id=planned.plan.planId,
                owner_run_id="owner-1",
                idempotency_key="start-1",
            )
        )
        assert run(service.get_run(started.run_id)).plan == planned.plan
        cancelled = run(service.request_cancel(started.run_id, request_id="cancel-1"))
        assert cancelled.state == "CANCELLED"
        assert run(service.request_cancel(started.run_id, request_id="cancel-1")) == cancelled
        reproduced = run(
            service.request_reproduction(started.run_id, idempotency_key="reproduce-1")
        )
        assert reproduced.run_id != started.run_id
        assert reproduced.reproduction_of_run_id == started.run_id
        original_events = run(service.store.events(started.run_id))
        assert original_events[-1].event_type == "REPRODUCTION_REQUESTED"

    def test_active_run_cannot_be_reproduced(self, service) -> None:
        planned = run(
            service.create_profile_and_plan(
                snapshot_id="snapshot-1",
                snapshot_digest=SHA,
                project_files={"package.json": "{}"},
                configuration=None,
                owner_run_id=None,
            )
        )
        started = run(
            service.start_run(
                plan_id=planned.plan.planId,
                owner_run_id=None,
                idempotency_key="start-1",
            )
        )
        with pytest.raises(QualityError, match="terminal"):
            run(service.request_reproduction(started.run_id, idempotency_key="reproduce-1"))

    def test_unknown_run_is_an_explicit_error(self, service) -> None:
        with pytest.raises(QualityError, match="does not exist"):
            run(service.get_run("missing"))
