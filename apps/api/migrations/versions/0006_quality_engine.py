"""Quality Engine persistence.

Plans, checks, results, evidence metadata, findings, verdicts and events are immutable facts.
Only ``quality_runs`` has a mutable lifecycle envelope. Object bytes remain in the existing
artifact store and are referenced from ``quality_evidence``.

Revision ID: 0006_quality_engine
Revises: 0005_tool_request_executor
Created: 2026-10-09
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from iacode_contracts.quality import (
    QUALITY_CHECK_KINDS,
    QUALITY_EVIDENCE_KINDS,
    QUALITY_FINDING_SEVERITIES,
    QUALITY_RESULT_ORIGIN,
    QUALITY_RESULT_STATUSES,
    QUALITY_RUN_EVENT_TYPES,
    QUALITY_RUN_STATES,
    QUALITY_VERDICTS,
)
from iacode_contracts.sandbox import SANDBOX_ACTIVE_SESSION_STATES
from sqlalchemy.dialects import postgresql

revision: str = "0006_quality_engine"
down_revision: str | None = "0005_tool_request_executor"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _vocabulary(values: tuple[str, ...]) -> str:
    return "(" + ", ".join(f"'{value}'" for value in values) + ")"


def _immutable_columns() -> list[sa.Column]:
    return [
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    ]


def upgrade() -> None:
    op.create_table(
        "quality_plans",
        *_immutable_columns(),
        sa.Column("owner_task_run_id", sa.UUID(), nullable=True),
        sa.Column("snapshot_artifact_id", sa.UUID(), nullable=False),
        sa.Column("plan_digest", sa.String(length=64), nullable=False),
        sa.Column("snapshot_digest", sa.String(length=64), nullable=False),
        sa.Column("project_profile", sa.String(length=128), nullable=False),
        sa.Column("project_profile_digest", sa.String(length=64), nullable=False),
        sa.Column("policy_id", sa.String(length=64), nullable=False),
        sa.Column("policy_version", sa.String(length=32), nullable=False),
        sa.Column("policy_digest", sa.String(length=64), nullable=False),
        sa.Column("content", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.ForeignKeyConstraint(["owner_task_run_id"], ["task_runs.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["snapshot_artifact_id"], ["artifacts.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("plan_digest", name="quality_plans_plan_digest"),
    )
    op.create_index("ix_quality_plans_owner_task_run_id", "quality_plans", ["owner_task_run_id"])
    op.create_index("ix_quality_plans_snapshot_digest", "quality_plans", ["snapshot_digest"])

    op.create_table(
        "quality_checks",
        *_immutable_columns(),
        sa.Column("quality_plan_id", sa.UUID(), nullable=False),
        sa.Column("check_id", sa.String(length=128), nullable=False),
        sa.Column("ordinal", sa.Integer(), nullable=False),
        sa.Column("kind", sa.String(length=32), nullable=False),
        sa.Column("runner", sa.String(length=128), nullable=False),
        sa.Column("content", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.CheckConstraint("kind IN " + _vocabulary(QUALITY_CHECK_KINDS), name="kind_is_known"),
        sa.ForeignKeyConstraint(["quality_plan_id"], ["quality_plans.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "quality_plan_id", "check_id", name="quality_checks_quality_plan_id_check_id"
        ),
        sa.UniqueConstraint(
            "quality_plan_id", "ordinal", name="quality_checks_quality_plan_id_ordinal"
        ),
    )
    op.create_index("ix_quality_checks_quality_plan_id", "quality_checks", ["quality_plan_id"])

    op.create_table(
        "quality_runs",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("version", sa.BigInteger(), server_default="1", nullable=False),
        sa.Column(
            "metadata", postgresql.JSONB(astext_type=sa.Text()), server_default="{}", nullable=False
        ),
        sa.Column("quality_plan_id", sa.UUID(), nullable=False),
        sa.Column("owner_task_run_id", sa.UUID(), nullable=True),
        sa.Column("reproduction_of_run_id", sa.UUID(), nullable=True),
        sa.Column("state", sa.String(length=32), server_default="CREATED", nullable=False),
        sa.Column("idempotency_key", sa.String(length=128), nullable=False),
        sa.Column("workflow_id", sa.String(length=256), nullable=True),
        sa.Column("deadline_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("terminal_reason", sa.String(length=2048), nullable=True),
        sa.Column("cancel_requested", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("training_allowed", sa.Boolean(), server_default="false", nullable=False),
        sa.CheckConstraint("state IN " + _vocabulary(QUALITY_RUN_STATES), name="state_is_known"),
        sa.CheckConstraint(
            "finished_at IS NULL OR started_at IS NULL OR finished_at >= started_at",
            name="finished_after_started",
        ),
        sa.ForeignKeyConstraint(["quality_plan_id"], ["quality_plans.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["owner_task_run_id"], ["task_runs.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(
            ["reproduction_of_run_id"], ["quality_runs.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("idempotency_key", name="quality_runs_idempotency_key"),
        sa.UniqueConstraint("workflow_id", name="quality_runs_workflow_id"),
    )
    op.create_index("ix_quality_runs_quality_plan_id", "quality_runs", ["quality_plan_id"])
    op.create_index("ix_quality_runs_owner_task_run_id", "quality_runs", ["owner_task_run_id"])
    op.create_index(
        "ix_quality_runs_reproduction_of_run_id", "quality_runs", ["reproduction_of_run_id"]
    )
    op.create_index("ix_quality_runs_state_created_at", "quality_runs", ["state", "created_at"])

    # A sandbox session is owned by an agent task run or by a quality run, never both. Gate 3's
    # schema could name only task runs; retaining that foreign key as the sole owner would force
    # the Quality Engine to create a fake task merely to execute a check.
    op.drop_index("uq_sandbox_sessions_one_active_per_run", table_name="sandbox_sessions")
    op.alter_column("sandbox_sessions", "task_run_id", nullable=True)
    op.add_column("sandbox_sessions", sa.Column("quality_run_id", sa.UUID(), nullable=True))
    op.create_foreign_key(
        op.f("fk_sandbox_sessions_quality_run_id_quality_runs"),
        "sandbox_sessions",
        "quality_runs",
        ["quality_run_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_check_constraint(
        "exactly_one_run_owner",
        "sandbox_sessions",
        "num_nonnulls(task_run_id, quality_run_id) = 1",
    )
    op.create_index(
        "ix_sandbox_sessions_quality_run_id",
        "sandbox_sessions",
        ["quality_run_id"],
    )
    active_states = _vocabulary(SANDBOX_ACTIVE_SESSION_STATES)
    op.create_index(
        "uq_sandbox_sessions_one_active_per_run",
        "sandbox_sessions",
        ["task_run_id"],
        unique=True,
        postgresql_where=sa.text(f"task_run_id IS NOT NULL AND state IN {active_states}"),
    )
    op.create_index(
        "uq_sandbox_sessions_one_active_per_quality_run",
        "sandbox_sessions",
        ["quality_run_id"],
        unique=True,
        postgresql_where=sa.text(f"quality_run_id IS NOT NULL AND state IN {active_states}"),
    )

    op.create_table(
        "quality_results",
        *_immutable_columns(),
        sa.Column("quality_run_id", sa.UUID(), nullable=False),
        sa.Column("quality_check_id", sa.UUID(), nullable=False),
        sa.Column("result_id", sa.String(length=128), nullable=False),
        sa.Column("result_digest", sa.String(length=64), nullable=False),
        sa.Column("callback_key", sa.String(length=128), nullable=False),
        sa.Column(
            "origin", sa.String(length=32), server_default=QUALITY_RESULT_ORIGIN, nullable=False
        ),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("sandbox_session_id", sa.UUID(), nullable=True),
        sa.Column("exit_code", sa.Integer(), nullable=True),
        sa.Column("duration_ms", sa.Integer(), nullable=False),
        sa.Column("timed_out", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("truncated", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("summary", sa.String(length=2048), nullable=False),
        sa.Column("content", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.CheckConstraint(
            "status IN " + _vocabulary(QUALITY_RESULT_STATUSES), name="status_is_known"
        ),
        sa.CheckConstraint(f"origin = '{QUALITY_RESULT_ORIGIN}'", name="origin_is_evaluator"),
        sa.CheckConstraint(
            "exit_code IS NULL OR status <> 'DENIED'", name="denied_has_no_exit_code"
        ),
        sa.ForeignKeyConstraint(["quality_run_id"], ["quality_runs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["quality_check_id"], ["quality_checks.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(
            ["sandbox_session_id"], ["sandbox_sessions.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "quality_run_id", "quality_check_id", name="quality_results_quality_run_id_check_id"
        ),
        sa.UniqueConstraint("result_id", name="quality_results_result_id"),
        sa.UniqueConstraint("callback_key", name="quality_results_callback_key"),
    )
    op.create_index("ix_quality_results_quality_run_id", "quality_results", ["quality_run_id"])
    op.create_index(
        "ix_quality_results_sandbox_session_id", "quality_results", ["sandbox_session_id"]
    )

    op.create_table(
        "quality_evidence",
        *_immutable_columns(),
        sa.Column("quality_run_id", sa.UUID(), nullable=False),
        sa.Column("quality_result_id", sa.UUID(), nullable=True),
        sa.Column("artifact_id", sa.UUID(), nullable=False),
        sa.Column("evidence_id", sa.String(length=128), nullable=False),
        sa.Column("kind", sa.String(length=32), nullable=False),
        sa.Column("digest", sa.String(length=64), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("media_type", sa.String(length=128), nullable=False),
        sa.Column("producer", sa.String(length=128), nullable=False),
        sa.Column(
            "source_digests",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default="[]",
            nullable=False,
        ),
        sa.Column("retention_class", sa.String(length=64), nullable=False),
        sa.Column("storage_allowed", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("rag_allowed", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("training_allowed", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("distillation_allowed", sa.Boolean(), server_default="false", nullable=False),
        sa.CheckConstraint("kind IN " + _vocabulary(QUALITY_EVIDENCE_KINDS), name="kind_is_known"),
        sa.ForeignKeyConstraint(["quality_run_id"], ["quality_runs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["quality_result_id"], ["quality_results.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["artifact_id"], ["artifacts.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("evidence_id", name="quality_evidence_evidence_id"),
        sa.UniqueConstraint(
            "quality_run_id", "digest", name="quality_evidence_quality_run_id_digest"
        ),
    )
    op.create_index("ix_quality_evidence_artifact_id", "quality_evidence", ["artifact_id"])
    op.create_index("ix_quality_evidence_digest", "quality_evidence", ["digest"])
    op.create_index("ix_quality_evidence_quality_run_id", "quality_evidence", ["quality_run_id"])
    op.create_index(
        "ix_quality_evidence_quality_result_id", "quality_evidence", ["quality_result_id"]
    )

    op.create_table(
        "quality_findings",
        *_immutable_columns(),
        sa.Column("quality_run_id", sa.UUID(), nullable=False),
        sa.Column("quality_result_id", sa.UUID(), nullable=False),
        sa.Column("finding_id", sa.String(length=128), nullable=False),
        sa.Column("check_id", sa.String(length=128), nullable=False),
        sa.Column("severity", sa.String(length=16), nullable=False),
        sa.Column("category", sa.String(length=64), nullable=False),
        sa.Column("fingerprint", sa.String(length=64), nullable=False),
        sa.Column("message", sa.String(length=2048), nullable=False),
        sa.Column("location", sa.String(length=512), nullable=True),
        sa.Column("recurrence_count", sa.Integer(), server_default="1", nullable=False),
        sa.Column(
            "evidence_ids",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default="[]",
            nullable=False,
        ),
        sa.CheckConstraint(
            "severity IN " + _vocabulary(QUALITY_FINDING_SEVERITIES), name="severity_is_known"
        ),
        sa.ForeignKeyConstraint(["quality_run_id"], ["quality_runs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["quality_result_id"], ["quality_results.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("finding_id", name="quality_findings_finding_id"),
        sa.UniqueConstraint(
            "quality_run_id", "fingerprint", name="quality_findings_quality_run_id_fingerprint"
        ),
    )
    op.create_index("ix_quality_findings_quality_run_id", "quality_findings", ["quality_run_id"])
    op.create_index(
        "ix_quality_findings_quality_result_id", "quality_findings", ["quality_result_id"]
    )

    op.create_table(
        "quality_verdicts",
        *_immutable_columns(),
        sa.Column("quality_run_id", sa.UUID(), nullable=False),
        sa.Column("verdict", sa.String(length=8), nullable=False),
        sa.Column("digest", sa.String(length=64), nullable=False),
        sa.Column("content", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.CheckConstraint("verdict IN " + _vocabulary(QUALITY_VERDICTS), name="verdict_is_known"),
        sa.ForeignKeyConstraint(["quality_run_id"], ["quality_runs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("quality_run_id", name="quality_verdicts_quality_run_id"),
        sa.UniqueConstraint("digest", name="quality_verdicts_digest"),
    )

    op.create_table(
        "quality_run_events",
        *_immutable_columns(),
        sa.Column("quality_run_id", sa.UUID(), nullable=False),
        sa.Column("sequence", sa.Integer(), nullable=False),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("dedupe_key", sa.String(length=128), nullable=False),
        sa.Column(
            "payload", postgresql.JSONB(astext_type=sa.Text()), server_default="{}", nullable=False
        ),
        sa.CheckConstraint(
            "event_type IN " + _vocabulary(QUALITY_RUN_EVENT_TYPES), name="event_type_is_known"
        ),
        sa.ForeignKeyConstraint(["quality_run_id"], ["quality_runs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "quality_run_id", "sequence", name="quality_run_events_quality_run_id_sequence"
        ),
        sa.UniqueConstraint(
            "quality_run_id", "dedupe_key", name="quality_run_events_quality_run_id_dedupe_key"
        ),
    )
    op.create_index(
        "ix_quality_run_events_run_sequence", "quality_run_events", ["quality_run_id", "sequence"]
    )


def downgrade() -> None:
    op.drop_index("ix_quality_run_events_run_sequence", table_name="quality_run_events")
    op.drop_table("quality_run_events")
    op.drop_table("quality_verdicts")
    op.drop_index("ix_quality_findings_quality_result_id", table_name="quality_findings")
    op.drop_index("ix_quality_findings_quality_run_id", table_name="quality_findings")
    op.drop_table("quality_findings")
    op.drop_index("ix_quality_evidence_quality_result_id", table_name="quality_evidence")
    op.drop_index("ix_quality_evidence_quality_run_id", table_name="quality_evidence")
    op.drop_index("ix_quality_evidence_digest", table_name="quality_evidence")
    op.drop_index("ix_quality_evidence_artifact_id", table_name="quality_evidence")
    op.drop_table("quality_evidence")
    op.drop_index("ix_quality_results_sandbox_session_id", table_name="quality_results")
    op.drop_index("ix_quality_results_quality_run_id", table_name="quality_results")
    op.drop_table("quality_results")
    op.drop_index(
        "uq_sandbox_sessions_one_active_per_quality_run", table_name="sandbox_sessions"
    )
    op.drop_index("uq_sandbox_sessions_one_active_per_run", table_name="sandbox_sessions")
    op.drop_index("ix_sandbox_sessions_quality_run_id", table_name="sandbox_sessions")
    op.drop_constraint(
        op.f("ck_sandbox_sessions_exactly_one_run_owner"),
        "sandbox_sessions",
        type_="check",
    )
    op.drop_constraint(
        op.f("fk_sandbox_sessions_quality_run_id_quality_runs"),
        "sandbox_sessions",
        type_="foreignkey",
    )
    op.execute(sa.text("DELETE FROM sandbox_sessions WHERE quality_run_id IS NOT NULL"))
    op.drop_column("sandbox_sessions", "quality_run_id")
    op.alter_column("sandbox_sessions", "task_run_id", nullable=False)
    active_states = _vocabulary(SANDBOX_ACTIVE_SESSION_STATES)
    op.create_index(
        "uq_sandbox_sessions_one_active_per_run",
        "sandbox_sessions",
        ["task_run_id"],
        unique=True,
        postgresql_where=sa.text(f"state IN {active_states}"),
    )
    op.drop_index("ix_quality_runs_state_created_at", table_name="quality_runs")
    op.drop_index("ix_quality_runs_reproduction_of_run_id", table_name="quality_runs")
    op.drop_index("ix_quality_runs_owner_task_run_id", table_name="quality_runs")
    op.drop_index("ix_quality_runs_quality_plan_id", table_name="quality_runs")
    op.drop_table("quality_runs")
    op.drop_index("ix_quality_checks_quality_plan_id", table_name="quality_checks")
    op.drop_table("quality_checks")
    op.drop_index("ix_quality_plans_snapshot_digest", table_name="quality_plans")
    op.drop_index("ix_quality_plans_owner_task_run_id", table_name="quality_plans")
    op.drop_table("quality_plans")
