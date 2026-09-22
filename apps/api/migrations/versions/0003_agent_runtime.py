"""Agent runtime schema.

What Gate 2 needs the persistence contract to carry: a run that knows which team it executes, what
it may spend and what it answered; an agent run that knows which stage it is and which prompt
version produced it; an append-only event log; and the two halves of a tool interaction.

Four decisions, rather than four additions.

**The run's state lives in the column it already had.** ``task_runs.status`` becomes the agent
runtime's state, with three values added — ``CREATED``, ``QUEUED`` and ``WAITING_FOR_TOOL``. A
second state column would be a second answer to "what is this run doing", and the two would
eventually disagree. The vocabulary is derived from ``iacode_contracts.agent_runtime`` rather than
written here a second time; the literal in this file is the snapshot that revision applies, which
is what a migration is.

**``agents`` grows into the configuration the runtime reads.** Gate 0 recorded that roles exist.
The runtime needs the role, the version, the prompt template and the hash of that template, because
a run that behaved oddly cannot be reproduced without knowing which definition it ran under.

**``tool_requests`` and ``tool_results`` are new, and ``tool_calls`` is not touched.** A request is
not an execution. Gate 2 persists what an agent asked for and what somebody authorised answered;
``tool_calls`` records an execution with a latency and a success, and Gate 2 executes nothing, so
it writes no row there. Gate 3 will.

**``run_events`` is append-only by shape.** No ``updated_at``, no ``version``, a unique sequence per
run and a unique dedupe key per run. The sequence is what lets a consumer resume from a cursor; the
dedupe key is what stops a retried Temporal activity from growing the history a second copy of the
same moment.

The downgrade is real and restores the Gate 1 shape. It drops what Gate 2 added, including the
runs' results: a downgrade of a populated database loses the agent runtime's own records, which is
stated here rather than discovered.

Revision ID: 0003_agent_runtime
Revises: 0002_model_gateway
Created: 2026-09-22

"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from iacode_contracts.agent_runtime import (
    AGENT_RUN_STATES,
    RUN_EVENT_TYPES,
    TOOL_REQUEST_STATUSES,
    TOOL_RESULT_STATUSES,
)
from sqlalchemy.dialects import postgresql

revision: str = "0003_agent_runtime"
down_revision: str | None = "0002_model_gateway"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# The vocabularies this revision applies. They are read from the shared contract rather than typed
# again, so the constraint the database carries and the states the runtime can produce cannot
# disagree. What is frozen in this file is the *revision* — which is what a migration is for.
_LEGACY_RUN_STATUSES = ("PENDING", "TIMED_OUT")
RUN_STATUSES = AGENT_RUN_STATES + _LEGACY_RUN_STATUSES
GATE1_RUN_STATUSES = ("PENDING", "RUNNING", "SUCCEEDED", "FAILED", "CANCELLED", "TIMED_OUT")


def _vocabulary(values: tuple[str, ...]) -> str:
    return "(" + ", ".join(f"'{value}'" for value in values) + ")"


# A note on constraint names, because the asymmetry below is deliberate rather than sloppy. The
# naming convention in `iacode_persistence.base` rewrites a constraint's name only when the
# template for that kind contains ``%(constraint_name)s`` — which the CHECK template does and the
# UNIQUE template does not. So a check constraint is created and dropped by its *bare* name and
# lands as ``ck_<table>_<name>``, while a unique constraint keeps exactly the name it was given.
# Getting this backwards produces ``ck_task_runs_ck_task_runs_status_is_known``, which is how the
# mismatch was found.


def upgrade() -> None:
    # --- task_runs: what the run is, what it may spend, what it answered ------------------------
    op.add_column("task_runs", sa.Column("team_slug", sa.String(length=128), nullable=True))
    op.add_column("task_runs", sa.Column("team_version", sa.String(length=32), nullable=True))
    op.add_column("task_runs", sa.Column("route", sa.String(length=64), nullable=True))
    op.add_column("task_runs", sa.Column("model_override", sa.String(length=384), nullable=True))
    op.add_column("task_runs", sa.Column("idempotency_key", sa.String(length=128), nullable=True))
    op.add_column("task_runs", sa.Column("current_stage", sa.String(length=128), nullable=True))
    op.add_column("task_runs", sa.Column(
        "budget", postgresql.JSONB(astext_type=sa.Text()), server_default="{}", nullable=False))
    op.add_column("task_runs", sa.Column(
        "budget_used", postgresql.JSONB(astext_type=sa.Text()),
        server_default="{}", nullable=False))
    op.add_column("task_runs", sa.Column("result", sa.Text(), nullable=True))
    op.add_column("task_runs", sa.Column("result_summary", sa.String(length=1024), nullable=True))
    op.add_column("task_runs", sa.Column("error_type", sa.String(length=128), nullable=True))
    op.add_column("task_runs", sa.Column("error_summary", sa.String(length=2048), nullable=True))
    op.add_column("task_runs", sa.Column("failed_stage", sa.String(length=128), nullable=True))
    op.add_column("task_runs", sa.Column("correlation_id", sa.String(length=128), nullable=True))
    op.add_column("task_runs", sa.Column(
        "cancel_requested", sa.Boolean(), server_default="false", nullable=False))
    op.add_column("task_runs", sa.Column(
        "training_allowed", sa.Boolean(), server_default="false", nullable=False))
    op.create_unique_constraint("idempotency_key", "task_runs", ["idempotency_key"])

    op.drop_constraint(op.f("ck_task_runs_status_is_known"), "task_runs", type_="check")
    op.create_check_constraint(
        "status_is_known", "task_runs", "status IN " + _vocabulary(RUN_STATUSES))

    # --- agents: the configuration the runtime reads --------------------------------------------
    op.add_column("agents", sa.Column("role", sa.String(length=128), nullable=True))
    op.add_column("agents", sa.Column("description", sa.Text(), nullable=True))
    op.add_column("agents",
              sa.Column("profile_version", sa.String(length=32), nullable=True))
    op.add_column("agents", sa.Column("default_route", sa.String(length=64), nullable=True))
    op.add_column("agents", sa.Column("max_turns", sa.Integer(), nullable=True))
    op.add_column("agents", sa.Column(
        "allowed_actions", postgresql.JSONB(astext_type=sa.Text()),
        server_default="[]", nullable=False))
    op.add_column("agents", sa.Column("prompt_template", sa.String(length=256), nullable=True))
    op.add_column("agents",
                  sa.Column("prompt_template_version", sa.String(length=32), nullable=True))
    op.add_column("agents", sa.Column("prompt_template_hash", sa.String(length=64), nullable=True))
    op.add_column("agents", sa.Column("definition_hash", sa.String(length=64), nullable=True))
    op.add_column("agents", sa.Column(
        "customised", sa.Boolean(), server_default="false", nullable=False))

    # --- agent_teams: composition as configuration ----------------------------------------------
    op.create_table(
        "agent_teams",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True),
                  server_default=sa.text("now()"), nullable=False),
        sa.Column("version", sa.BigInteger(), server_default="1", nullable=False),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()),
                  server_default="{}", nullable=False),
        sa.Column("slug", sa.String(length=128), nullable=False),
        sa.Column("name", sa.String(length=256), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("profile_version", sa.String(length=32), server_default="1.0.0",
                  nullable=False),
        sa.Column("stages", postgresql.JSONB(astext_type=sa.Text()),
                  server_default="[]", nullable=False),
        sa.Column("enabled", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("definition_hash", sa.String(length=64), nullable=True),
        sa.Column("customised", sa.Boolean(), server_default="false", nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_agent_teams")),
        sa.UniqueConstraint("slug", name=op.f("uq_agent_teams_slug")),
    )

    # --- agent_runs: which stage, which definition, what it produced -----------------------------
    op.add_column("agent_runs", sa.Column(
        "stage_index", sa.Integer(), server_default="0", nullable=False))
    op.add_column("agent_runs", sa.Column("stage_name", sa.String(length=128), nullable=True))
    op.add_column("agent_runs", sa.Column("agent_slug", sa.String(length=128), nullable=True))
    op.add_column("agent_runs", sa.Column("profile_version", sa.String(length=32), nullable=True))
    op.add_column("agent_runs",
                  sa.Column("prompt_template_version", sa.String(length=32), nullable=True))
    op.add_column("agent_runs",
                  sa.Column("prompt_template_hash", sa.String(length=64), nullable=True))
    op.add_column("agent_runs", sa.Column(
        "turns", sa.Integer(), server_default="0", nullable=False))
    op.add_column("agent_runs", sa.Column(
        "model_calls", sa.Integer(), server_default="0", nullable=False))
    op.add_column("agent_runs", sa.Column("output_name", sa.String(length=128), nullable=True))
    op.add_column("agent_runs", sa.Column("output", sa.Text(), nullable=True))
    op.add_column("agent_runs", sa.Column("output_summary", sa.String(length=1024), nullable=True))
    op.add_column("agent_runs", sa.Column("error_type", sa.String(length=128), nullable=True))
    op.add_column("agent_runs", sa.Column("error_summary", sa.String(length=2048), nullable=True))

    # Any row that predates this revision has stage_index 0, and two of them inside one run would
    # violate the constraint added next. Numbering them by creation order makes the upgrade correct
    # for a populated database instead of correct only for an empty one.
    op.execute(
        "UPDATE agent_runs SET stage_index = ordered.position - 1 FROM ("
        "  SELECT id, ROW_NUMBER() OVER (PARTITION BY task_run_id ORDER BY created_at, id)"
        "         AS position"
        "  FROM agent_runs) AS ordered"
        " WHERE agent_runs.id = ordered.id")
    op.create_unique_constraint(
        "task_run_id_stage_index", "agent_runs", ["task_run_id", "stage_index"])

    op.drop_constraint(op.f("ck_agent_runs_status_is_known"), "agent_runs", type_="check")
    op.create_check_constraint(
        "status_is_known", "agent_runs", "status IN " + _vocabulary(RUN_STATUSES))

    # --- run_events: the append-only history ------------------------------------------------------
    op.create_table(
        "run_events",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.text("now()"), nullable=False),
        sa.Column("task_run_id", sa.UUID(), nullable=False),
        sa.Column("agent_run_id", sa.UUID(), nullable=True),
        sa.Column("sequence", sa.Integer(), nullable=False),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("stage", sa.String(length=128), nullable=True),
        sa.Column("dedupe_key", sa.String(length=128), nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()),
                  server_default="{}", nullable=False),
        sa.ForeignKeyConstraint(
            ["task_run_id"], ["task_runs.id"],
            name=op.f("fk_run_events_task_run_id_task_runs"), ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["agent_run_id"], ["agent_runs.id"],
            name=op.f("fk_run_events_agent_run_id_agent_runs"), ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_run_events")),
        sa.UniqueConstraint("task_run_id", "sequence", name="task_run_id_sequence"),
        sa.UniqueConstraint("task_run_id", "dedupe_key", name="task_run_id_dedupe_key"),
        sa.CheckConstraint("event_type IN " + _vocabulary(RUN_EVENT_TYPES),
                           name="event_type_is_known"),
    )
    op.create_index("ix_run_events_task_run_id_sequence", "run_events",
                    ["task_run_id", "sequence"], unique=False)

    # --- tool_requests and tool_results: asked for, and answered ----------------------------------
    op.create_table(
        "tool_requests",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True),
                  server_default=sa.text("now()"), nullable=False),
        sa.Column("version", sa.BigInteger(), server_default="1", nullable=False),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()),
                  server_default="{}", nullable=False),
        sa.Column("task_run_id", sa.UUID(), nullable=False),
        sa.Column("agent_run_id", sa.UUID(), nullable=True),
        sa.Column("tool_name", sa.String(length=128), nullable=False),
        sa.Column("arguments", postgresql.JSONB(astext_type=sa.Text()),
                  server_default="{}", nullable=False),
        sa.Column("status", sa.String(length=32), server_default="PENDING", nullable=False),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["task_run_id"], ["task_runs.id"],
            name=op.f("fk_tool_requests_task_run_id_task_runs"), ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["agent_run_id"], ["agent_runs.id"],
            name=op.f("fk_tool_requests_agent_run_id_agent_runs"), ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_tool_requests")),
        sa.CheckConstraint("status IN " + _vocabulary(TOOL_REQUEST_STATUSES),
                           name="status_is_known"),
    )
    op.create_index("ix_tool_requests_agent_run_id", "tool_requests", ["agent_run_id"],
                    unique=False)
    op.create_index("ix_tool_requests_task_run_id_created_at", "tool_requests",
                    ["task_run_id", "created_at"], unique=False)

    op.create_table(
        "tool_results",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.text("now()"), nullable=False),
        sa.Column("tool_request_id", sa.UUID(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("output", postgresql.JSONB(astext_type=sa.Text()),
                  server_default="{}", nullable=False),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("result_metadata", postgresql.JSONB(astext_type=sa.Text()),
                  server_default="{}", nullable=False),
        sa.ForeignKeyConstraint(
            ["tool_request_id"], ["tool_requests.id"],
            name=op.f("fk_tool_results_tool_request_id_tool_requests"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_tool_results")),
        sa.UniqueConstraint("tool_request_id", name="tool_request_id"),
        sa.CheckConstraint("status IN " + _vocabulary(TOOL_RESULT_STATUSES),
                           name="status_is_known"),
    )


def downgrade() -> None:
    op.drop_table("tool_results")
    op.drop_index("ix_tool_requests_task_run_id_created_at", table_name="tool_requests")
    op.drop_index("ix_tool_requests_agent_run_id", table_name="tool_requests")
    op.drop_table("tool_requests")
    op.drop_index("ix_run_events_task_run_id_sequence", table_name="run_events")
    op.drop_table("run_events")

    # A run that reached a Gate 2 state has no Gate 1 equivalent. It becomes FAILED rather than
    # being deleted: losing the row would lose the model calls that point at its agent runs, and a
    # downgrade that destroys recorded history is worse than one that marks it unfinished.
    op.execute(
        "UPDATE agent_runs SET status = 'FAILED' WHERE status IN "
        "('CREATED', 'QUEUED', 'WAITING_FOR_TOOL')")
    op.drop_constraint(op.f("ck_agent_runs_status_is_known"), "agent_runs", type_="check")
    op.create_check_constraint(
        "status_is_known", "agent_runs", "status IN " + _vocabulary(GATE1_RUN_STATUSES))
    op.drop_constraint("task_run_id_stage_index", "agent_runs", type_="unique")
    for column in ("error_summary", "error_type", "output_summary", "output", "output_name",
                   "model_calls", "turns", "prompt_template_hash", "prompt_template_version",
                   "profile_version", "agent_slug", "stage_name", "stage_index"):
        op.drop_column("agent_runs", column)

    op.drop_table("agent_teams")

    for column in ("customised", "definition_hash", "prompt_template_hash",
                   "prompt_template_version", "prompt_template", "allowed_actions", "max_turns",
                   "default_route", "profile_version", "description", "role"):
        op.drop_column("agents", column)

    op.execute(
        "UPDATE task_runs SET status = 'FAILED' WHERE status IN "
        "('CREATED', 'QUEUED', 'WAITING_FOR_TOOL')")
    op.drop_constraint(op.f("ck_task_runs_status_is_known"), "task_runs", type_="check")
    op.create_check_constraint(
        "status_is_known", "task_runs", "status IN " + _vocabulary(GATE1_RUN_STATUSES))
    op.drop_constraint("idempotency_key", "task_runs", type_="unique")
    for column in ("training_allowed", "cancel_requested", "correlation_id", "failed_stage",
                   "error_summary", "error_type", "result_summary", "result", "budget_used",
                   "budget", "current_stage", "idempotency_key", "model_override", "route",
                   "team_version", "team_slug"):
        op.drop_column("task_runs", column)
