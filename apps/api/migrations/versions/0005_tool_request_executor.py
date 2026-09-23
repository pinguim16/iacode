"""Tool request executor.

`M1-F-002`: the API's tool-result endpoint accepted a result for a request the sandbox was
executing, and the agent received it instead of the sandbox's, because nothing recorded who was
supposed to answer. ``tool_requests.executor`` records it when the request is created: ``SANDBOX``
for a stage with a sandbox policy, ``EXTERNAL`` otherwise. The store refuses a result whose origin
is not the request's executor.

**The backfill keeps every existing row's meaning.** A request the sandbox executed has an
execution record in ``tool_calls`` (unique on ``tool_request_id`` since ``0004``), so exactly those
rows become ``SANDBOX``; every other row was answered from outside and stays ``EXTERNAL``, the
server default. The constraint then closes the vocabulary.

The downgrade is real and restores the ``0004`` shape.

Revision ID: 0005_tool_request_executor
Revises: 0004_sandbox
Created: 2026-09-23

"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from iacode_contracts.agent_runtime import (
    TOOL_EXECUTOR_EXTERNAL,
    TOOL_EXECUTOR_SANDBOX,
    TOOL_REQUEST_EXECUTORS,
)

revision: str = "0005_tool_request_executor"
down_revision: str | None = "0004_sandbox"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _vocabulary(values: tuple[str, ...]) -> str:
    return "(" + ", ".join(f"'{value}'" for value in values) + ")"


def upgrade() -> None:
    op.add_column("tool_requests", sa.Column(
        "executor", sa.String(length=16), server_default=TOOL_EXECUTOR_EXTERNAL, nullable=False))
    op.execute(
        f"UPDATE tool_requests SET executor = '{TOOL_EXECUTOR_SANDBOX}' WHERE id IN "
        "(SELECT tool_request_id FROM tool_calls WHERE tool_request_id IS NOT NULL)")
    op.create_check_constraint(
        "executor_is_known", "tool_requests",
        "executor IN " + _vocabulary(TOOL_REQUEST_EXECUTORS))


def downgrade() -> None:
    op.drop_constraint(op.f("ck_tool_requests_executor_is_known"), "tool_requests", type_="check")
    op.drop_column("tool_requests", "executor")
