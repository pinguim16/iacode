"""Evolve the Foundation experience envelope; quarantine rather than promote legacy bodies.

Revision ID: 0007_experience_store
Revises: 0006_quality_engine
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0007_experience_store"
down_revision: str | None = "0006_quality_engine"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    for name in ("project_id", "source_run_id", "request_key"):
        op.add_column("experiences", sa.Column(name, sa.UUID(), nullable=True))
    op.add_column(
        "experiences", sa.Column("schema_version", sa.Integer(), nullable=False, server_default="0")
    )
    op.add_column(
        "experiences", sa.Column("state", sa.String(16), nullable=False, server_default="LEGACY")
    )
    for name in ("request_digest", "content_digest"):
        op.add_column("experiences", sa.Column(name, sa.String(64), nullable=True))
    for name in ("source_finished_at", "expires_at", "purged_at"):
        op.add_column("experiences", sa.Column(name, sa.DateTime(timezone=True), nullable=True))
    op.create_unique_constraint(
        "uq_experiences_project_request", "experiences", ["project_id", "request_key"]
    )
    op.create_unique_constraint(
        "uq_experiences_project_source", "experiences", ["project_id", "source_run_id"]
    )
    op.create_index("ix_experiences_project_id_id", "experiences", ["project_id", "id"])
    op.create_index("ix_experiences_state_expires_at", "experiences", ["state", "expires_at"])
    op.create_check_constraint("schema_version_known", "experiences", "schema_version IN (0, 1)")
    op.create_check_constraint(
        "current_shape",
        "experiences",
        "(schema_version = 0 AND state = 'LEGACY') OR (schema_version = 1 AND "
        "state IN ('ACTIVE', 'EXPIRED', 'DELETED') AND project_id IS NOT NULL AND "
        "source_run_id IS NOT NULL AND source_finished_at IS NOT NULL AND "
        "request_key IS NOT NULL AND request_digest IS NOT NULL AND "
        "content_digest IS NOT NULL AND expires_at IS NOT NULL AND "
        "request_digest ~ '^[0-9a-f]{64}$' AND content_digest ~ '^[0-9a-f]{64}$' AND "
        "expires_at > created_at AND "
        "NOT rag_allowed AND NOT training_allowed AND NOT distillation_allowed AND "
        "metadata = '{}'::jsonb AND ownership = 'UNVERIFIED' AND license = 'UNKNOWN' AND "
        "((state = 'ACTIVE' AND storage_allowed AND purged_at IS NULL AND "
        "body ? 'schemaVersion' AND body->>'schemaVersion' = '1.0.0') OR "
        "(state <> 'ACTIVE' AND NOT storage_allowed "
        "AND purged_at IS NOT NULL AND body = '{}'::jsonb AND summary = '')))",
    )
    op.create_table(
        "experience_events",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("experience_id", sa.UUID(), nullable=False),
        sa.Column("kind", sa.String(16), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["experience_id"], ["experiences.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("experience_id", "kind", name="experience_kind"),
        sa.CheckConstraint("kind IN ('CAPTURED', 'EXPIRED', 'DELETED')", name="kind_known"),
    )
    op.execute("""
    CREATE FUNCTION guard_experience_fact() RETURNS trigger LANGUAGE plpgsql AS $$
    BEGIN
      IF OLD.schema_version <> NEW.schema_version THEN
        RAISE EXCEPTION 'experience schema is immutable';
      END IF;
      IF OLD.schema_version = 0 THEN RETURN NEW; END IF;
      IF (to_jsonb(NEW) - ARRAY['task_run_id','body','summary','state','storage_allowed',
                               'purged_at','updated_at','version']) IS DISTINCT FROM
         (to_jsonb(OLD) - ARRAY['task_run_id','body','summary','state','storage_allowed',
                               'purged_at','updated_at','version']) THEN
        RAISE EXCEPTION 'experience fact is immutable';
      END IF;
      IF NEW.task_run_id IS DISTINCT FROM OLD.task_run_id AND NEW.task_run_id IS NOT NULL THEN
        RAISE EXCEPTION 'experience source is immutable';
      END IF;
      IF OLD.state <> 'ACTIVE' AND ROW(NEW.body,NEW.summary,NEW.state,NEW.storage_allowed,NEW.purged_at)
          IS DISTINCT FROM ROW(OLD.body,OLD.summary,OLD.state,OLD.storage_allowed,OLD.purged_at) THEN
        RAISE EXCEPTION 'experience terminal state is immutable';
      END IF;
      IF NEW.state = 'ACTIVE' AND ROW(NEW.body,NEW.summary,NEW.storage_allowed,NEW.purged_at)
          IS DISTINCT FROM ROW(OLD.body,OLD.summary,OLD.storage_allowed,OLD.purged_at) THEN
        RAISE EXCEPTION 'experience payload is immutable';
      END IF;
      RETURN NEW;
    END $$;
    CREATE TRIGGER experience_fact_immutable BEFORE UPDATE ON experiences
      FOR EACH ROW EXECUTE FUNCTION guard_experience_fact();
    CREATE FUNCTION guard_experience_event() RETURNS trigger LANGUAGE plpgsql AS $$
    BEGIN RAISE EXCEPTION 'experience audit fact is immutable'; END $$;
    CREATE TRIGGER experience_event_immutable BEFORE UPDATE ON experience_events
      FOR EACH ROW EXECUTE FUNCTION guard_experience_event();
    """)


def downgrade() -> None:
    op.execute(
        "DROP TRIGGER experience_event_immutable ON experience_events; DROP FUNCTION guard_experience_event();"
    )
    op.execute(
        "DROP TRIGGER experience_fact_immutable ON experiences; DROP FUNCTION guard_experience_fact();"
    )
    op.drop_table("experience_events")
    op.drop_constraint(op.f("ck_experiences_current_shape"), "experiences", type_="check")
    op.drop_constraint(op.f("ck_experiences_schema_version_known"), "experiences", type_="check")
    op.drop_index("ix_experiences_state_expires_at", "experiences")
    op.drop_index("ix_experiences_project_id_id", "experiences")
    op.drop_constraint("uq_experiences_project_source", "experiences", type_="unique")
    op.drop_constraint("uq_experiences_project_request", "experiences", type_="unique")
    for name in (
        "purged_at",
        "expires_at",
        "source_finished_at",
        "content_digest",
        "request_digest",
        "state",
        "schema_version",
        "request_key",
        "source_run_id",
        "project_id",
    ):
        op.drop_column("experiences", name)
