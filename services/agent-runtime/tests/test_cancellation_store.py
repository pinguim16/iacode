"""Actual SQL-store method with explicit row/transaction doubles, not live persistence proof."""

from types import SimpleNamespace
from unittest import mock

import pytest
from iacode_agent_runtime.errors import AgentRuntimeError
from iacode_agent_runtime.persistence import SqlAgentRunStore


class Transaction:
    def begin(self):
        return self

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_arguments):
        return False


def fixture(state):
    row = SimpleNamespace(status=state, cancel_requested=False, result="preserved")
    store = SqlAgentRunStore(lambda: Transaction())
    store._run_row = mock.AsyncMock(return_value=row)
    record = SimpleNamespace(state=state)
    store.load_run = mock.AsyncMock(return_value=record)
    return store, row, record


@pytest.mark.asyncio
async def test_repeated_cancel_of_cancelled_run_returns_unchanged_terminal_truth():
    store, row, record = fixture("CANCELLED")
    before = vars(row).copy()
    assert await store.request_cancellation("run-decision") is record
    assert vars(row) == before
    store.load_run.assert_awaited_once_with("run-decision")


@pytest.mark.asyncio
async def test_cancel_of_success_or_failure_still_refuses_without_mutation():
    for state in ("SUCCEEDED", "FAILED"):
        store, row, _ = fixture(state)
        before = vars(row).copy()
        with pytest.raises(AgentRuntimeError) as raised:
            await store.request_cancellation("run-decision")
        assert str(raised.value.error_type) == "INVALID_STATE_TRANSITION"
        assert vars(row) == before
        store.load_run.assert_not_awaited()


@pytest.mark.asyncio
async def test_running_cancel_sets_only_request_flag_not_terminal_state():
    store, row, record = fixture("RUNNING")
    assert await store.request_cancellation("run-decision") is record
    assert row.cancel_requested is True
    assert row.status == "RUNNING"
    assert row.result == "preserved"
