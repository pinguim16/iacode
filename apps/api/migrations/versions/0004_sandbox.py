"""Sandbox schema.

What Gate 3 needs the persistence contract to carry: a durable record of every sandbox session, and
an execution record for every tool the sandbox ran.

Two decisions.

**``tool_calls`` is evolved, not shadowed.** Gate 0 created it for exactly this — "one tool
invocation that was executed" — and Gate 2 deliberately wrote no row there. Gate 3 adds what an
execution needs to be traceable and honest: the tool request it answers (unique, so a retried
execution is recorded once), the session it ran in, a status from the shared vocabulary, the exit
code only when a process was started, the timeout and truncation flags, a short summary and the
artifacts holding what did not fit inline. A ``tool_executions`` table beside it would be a second
answer to "what ran", and the two would eventually disagree. Existing rows, if a database has any,
keep their meaning: ``status`` is derived from the ``succeeded`` they already carry.

**``sandbox_sessions`` is new, because nothing existing can hold it.** A session is a lifecycle —
created, ready, running, stopped, expired — with a container, a policy, an image fingerprint, a
workspace source and an expiry, and the service's memory cannot be its only record: a restarted
service reconciles these rows with the containers the engine reports. At most one session per run is
active, stated by a partial unique index rather than by a code path.

**``task_runs.workspace`` says where a run's workspace comes from** — nothing, or an authorised
snapshot artifact and its digest — because the plan a workflow receives is rebuilt from the row, and
a snapshot named only in process memory would be lost to an idempotent replay.

The downgrade is real and restores the Gate 2 shape, dropping the sessions, the execution columns
and the run's workspace source.

Revision ID: 0004_sandbox
Revises: 0003_agent_runtime
Created: 2026-09-22

"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from iacode_contracts.sandbox import (
    SANDBOX_ACTIVE_SESSION_STATES,
    SANDBOX_SESSION_STATES,
    TOOL_EXECUTION_STATUSES,
)
from sqlalchemy.dialects import postgresql

revision: str = "0004_sandbox"
down_revision: str | None = "0003_agent_runtime"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _vocabulary(values: tuple[str, ...]) -> str:
    return "(" + ", ".join(f"'{value}'" for value in values) + ")"


def upgrade() -> None:
    # --- task_runs: where the run's workspace comes from ----------------------------------------
    op.add_column("task_runs", sa.Column(
        "workspace", postgresql.JSONB(astext_type=sa.Text()), server_default="{}",
        nullable=False))

    # --- sandbox_sessions: the durable half of a session ------------------------------------------
    op.create_table(
        "sandbox_sessions",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True),
                  server_default=sa.text("now()"), nullable=False),
        sa.Column("version", sa.BigInteger(), server_default="1", nullable=False),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()),
                  server_default="{}", nullable=False),
        sa.Column("task_run_id", sa.UUID(), nullable=False),
        sa.Column("state", sa.String(length=32), nullable=False),
        sa.Column("policy", sa.String(length=64), nullable=False),
        sa.Column("image", sa.String(length=256), nullable=False),
        sa.Column("image_fingerprint", sa.String(length=64), nullable=False),
        sa.Column("container_name", sa.String(length=128), nullable=False),
        sa.Column("network_profile", sa.String(length=32), nullable=False),
        sa.Column("workspace_source", postgresql.JSONB(astext_type=sa.Text()),
                  server_default="{}", nullable=False),
        sa.Column("resource_limits", postgresql.JSONB(astext_type=sa.Text()),
                  server_default="{}", nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("stopped_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("failure_reason", sa.Text(), nullable=True),
        sa.Column("active_tool_request_id", sa.UUID(), nullable=True),
        sa.ForeignKeyConstraint(
            ["task_run_id"], ["task_runs.id"],
            name=op.f("fk_sandbox_sessions_task_run_id_task_runs"), ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["active_tool_request_id"], ["tool_requests.id"],
            name=op.f("fk_sandbox_sessions_active_tool_request_id_tool_requests"),
            ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_sandbox_sessions")),
        sa.CheckConstraint("state IN " + _vocabulary(SANDBOX_SESSION_STATES),
                           name="state_is_known"),
        sa.UniqueConstraint("container_name", name="sandbox_sessions_container_name"),
    )
    op.create_index("ix_sandbox_sessions_task_run_id", "sandbox_sessions", ["task_run_id"],
                    unique=False)
    op.create_index("uq_sandbox_sessions_one_active_per_run", "sandbox_sessions",
                    ["task_run_id"], unique=True,
                    postgresql_where=sa.text(
                        "state IN " + _vocabulary(SANDBOX_ACTIVE_SESSION_STATES)))

    # --- tool_calls: an execution, traceable and honest --------------------------------------------
    op.add_column("tool_calls", sa.Column("tool_request_id", sa.UUID(), nullable=True))
    op.add_column("tool_calls", sa.Column("sandbox_session_id", sa.UUID(), nullable=True))
    op.add_column("tool_calls", sa.Column("status", sa.String(length=32), nullable=True))
    op.add_column("tool_calls", sa.Column("exit_code", sa.Integer(), nullable=True))
    op.add_column("tool_calls", sa.Column("timed_out", sa.Boolean(), server_default="false",
                                          nullable=False))
    op.add_column("tool_calls", sa.Column("truncated", sa.Boolean(), server_default="false",
                                          nullable=False))
    op.add_column("tool_calls", sa.Column("summary", sa.String(length=240), nullable=True))
    op.add_column("tool_calls", sa.Column(
        "artifact_ids", postgresql.JSONB(astext_type=sa.Text()), server_default="[]",
        nullable=False))
    op.create_foreign_key(
        op.f("fk_tool_calls_tool_request_id_tool_requests"), "tool_calls", "tool_requests",
        ["tool_request_id"], ["id"], ondelete="SET NULL")
    op.create_foreign_key(
        op.f("fk_tool_calls_sandbox_session_id_sandbox_sessions"), "tool_calls",
        "sandbox_sessions", ["sandbox_session_id"], ["id"], ondelete="SET NULL")
    # A row written before this revision keeps the meaning it had: its status is what its
    # ``succeeded`` flag said.
    op.execute("UPDATE tool_calls SET status = CASE WHEN succeeded THEN 'SUCCEEDED' "
               "ELSE 'FAILED' END WHERE status IS NULL")
    op.alter_column("tool_calls", "status", nullable=False)
    op.create_check_constraint(
        "status_is_known", "tool_calls", "status IN " + _vocabulary(TOOL_EXECUTION_STATUSES))
    op.create_check_constraint(
        "denied_has_no_exit_code", "tool_calls", "exit_code IS NULL OR status <> 'DENIED'")
    op.create_unique_constraint("tool_calls_tool_request_id", "tool_calls", ["tool_request_id"])
    op.create_index("ix_tool_calls_sandbox_session_id", "tool_calls", ["sandbox_session_id"],
                    unique=False)


def downgrade() -> None:
    op.drop_index("ix_tool_calls_sandbox_session_id", table_name="tool_calls")
    op.drop_constraint("tool_calls_tool_request_id", "tool_calls", type_="unique")
    op.drop_constraint(op.f("ck_tool_calls_denied_has_no_exit_code"), "tool_calls", type_="check")
    op.drop_constraint(op.f("ck_tool_calls_status_is_known"), "tool_calls", type_="check")
    op.drop_constraint(op.f("fk_tool_calls_sandbox_session_id_sandbox_sessions"), "tool_calls",
                       type_="foreignkey")
    op.drop_constraint(op.f("fk_tool_calls_tool_request_id_tool_requests"), "tool_calls",
                       type_="foreignkey")
    for column in ("artifact_ids", "summary", "truncated", "timed_out", "exit_code", "status",
                   "sandbox_session_id", "tool_request_id"):
        op.drop_column("tool_calls", column)
    op.drop_index("uq_sandbox_sessions_one_active_per_run", table_name="sandbox_sessions")
    op.drop_index("ix_sandbox_sessions_task_run_id", table_name="sandbox_sessions")
    op.drop_table("sandbox_sessions")
    op.drop_column("task_runs", "workspace")
