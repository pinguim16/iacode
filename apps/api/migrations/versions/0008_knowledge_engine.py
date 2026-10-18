"""Persist governed cited projections and a bounded real inverted index.

Revision ID: 0008_knowledge_engine
Revises: 0007_experience_store
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0008_knowledge_engine"
down_revision: str | None = "0007_experience_store"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "knowledge_documents",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("version", sa.BigInteger(), nullable=False, server_default="1"),
        sa.Column("metadata", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("project_id", sa.UUID(), nullable=False),
        sa.Column("source_kind", sa.String(16), nullable=False),
        sa.Column("source_id", sa.UUID(), nullable=False),
        sa.Column("revision", sa.String(128), nullable=False),
        sa.Column("source_digest", sa.String(64), nullable=False),
        sa.Column("grant_digest", sa.String(64), nullable=False),
        sa.Column("policy_digest", sa.String(64), nullable=False),
        sa.Column("material_digest", sa.String(64), nullable=False),
        sa.Column("request_key", sa.UUID(), nullable=False),
        sa.Column("request_digest", sa.String(64), nullable=False),
        sa.Column("content_digest", sa.String(64), nullable=False),
        sa.Column("state", sa.String(16), nullable=False, server_default="ACTIVE"),
        sa.Column("body", postgresql.JSONB(), nullable=False),
        sa.Column("source_created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("retention_ceiling", sa.DateTime(timezone=True), nullable=False),
        sa.Column("purged_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "checked_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("project_id", "request_key", name="uq_knowledge_documents_request"),
        sa.UniqueConstraint(
            "project_id", "material_digest", name="uq_knowledge_documents_material"
        ),
        sa.CheckConstraint("source_kind = 'curated'", name="source_kind_known"),
        sa.CheckConstraint(
            "state IN ('ACTIVE','INVALIDATED','EXPIRED','DELETED')", name="state_known"
        ),
        sa.CheckConstraint(
            "request_digest ~ '^[0-9a-f]{64}$' AND material_digest ~ '^[0-9a-f]{64}$' AND "
            "content_digest ~ '^[0-9a-f]{64}$' AND source_digest ~ '^[0-9a-f]{64}$' AND "
            "grant_digest ~ '^[0-9a-f]{64}$' AND policy_digest ~ '^[0-9a-f]{64}$'",
            name="digests_valid",
        ),
        sa.CheckConstraint(
            "expires_at > created_at AND expires_at <= retention_ceiling AND "
            "source_created_at <= created_at AND metadata = '{}'::jsonb AND "
            "octet_length(body::text) <= 1048576 AND "
            "((state = 'ACTIVE' AND purged_at IS NULL AND body ? 'schemaVersion' AND "
            "body->>'schemaVersion' = '1.0.0') "
            "OR (state <> 'ACTIVE' AND purged_at IS NOT NULL AND body = '{}'::jsonb))",
            name="lifecycle_shape",
        ),
    )
    op.create_index(
        "ix_knowledge_documents_project_id_id", "knowledge_documents", ["project_id", "id"]
    )
    op.create_index(
        "ix_knowledge_documents_project_source",
        "knowledge_documents",
        ["project_id", "source_kind", "source_id"],
    )
    op.create_index(
        "ix_knowledge_documents_state_expires_at", "knowledge_documents", ["state", "expires_at"]
    )
    op.create_table(
        "knowledge_index_entries",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("document_id", sa.UUID(), nullable=False),
        sa.Column("ordinal", sa.Integer(), nullable=False),
        sa.Column("digest", sa.String(64), nullable=False),
        sa.Column("tokens", postgresql.JSONB(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["document_id"], ["knowledge_documents.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("document_id", "ordinal", name="uq_knowledge_index_entries_ordinal"),
        sa.CheckConstraint("ordinal >= 0 AND ordinal < 128", name="ordinal_valid"),
        sa.CheckConstraint("digest ~ '^[0-9a-f]{64}$'", name="digest_valid"),
        sa.CheckConstraint(
            "jsonb_typeof(tokens) = 'array' AND jsonb_array_length(tokens) <= 512 AND "
            "octet_length(tokens::text) <= 300000",
            name="tokens_bounded",
        ),
    )
    op.create_index(
        "ix_knowledge_index_entries_tokens",
        "knowledge_index_entries",
        ["tokens"],
        postgresql_using="gin",
    )
    op.create_table(
        "knowledge_events",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("document_id", sa.UUID(), nullable=False),
        sa.Column("kind", sa.String(16), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["document_id"], ["knowledge_documents.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("document_id", "kind", name="uq_knowledge_events_kind"),
        sa.CheckConstraint(
            "kind IN ('INDEXED','INVALIDATED','EXPIRED','DELETED')", name="kind_known"
        ),
    )
    op.execute("""
    CREATE FUNCTION guard_knowledge_document() RETURNS trigger LANGUAGE plpgsql AS $$
    BEGIN
      IF (to_jsonb(NEW) - ARRAY['body','state','purged_at','checked_at','updated_at','version'])
         IS DISTINCT FROM
         (to_jsonb(OLD) - ARRAY['body','state','purged_at','checked_at','updated_at','version']) THEN
        RAISE EXCEPTION 'knowledge material is immutable';
      END IF;
      IF OLD.state <> 'ACTIVE' AND ROW(NEW.body,NEW.state,NEW.purged_at)
         IS DISTINCT FROM ROW(OLD.body,OLD.state,OLD.purged_at) THEN
        RAISE EXCEPTION 'knowledge terminal state is immutable';
      END IF;
      IF NEW.state = 'ACTIVE' AND ROW(NEW.body,NEW.purged_at)
         IS DISTINCT FROM ROW(OLD.body,OLD.purged_at) THEN
        RAISE EXCEPTION 'knowledge payload is immutable';
      END IF;
      RETURN NEW;
    END $$;
    CREATE TRIGGER knowledge_document_immutable BEFORE UPDATE ON knowledge_documents
      FOR EACH ROW EXECUTE FUNCTION guard_knowledge_document();
    CREATE FUNCTION guard_knowledge_index_fact() RETURNS trigger LANGUAGE plpgsql AS $$
    BEGIN RAISE EXCEPTION 'knowledge index and audit facts are immutable'; END $$;
    CREATE TRIGGER knowledge_index_immutable BEFORE UPDATE ON knowledge_index_entries
      FOR EACH ROW EXECUTE FUNCTION guard_knowledge_index_fact();
    CREATE TRIGGER knowledge_event_immutable BEFORE UPDATE ON knowledge_events
      FOR EACH ROW EXECUTE FUNCTION guard_knowledge_index_fact();
    """)


def downgrade() -> None:
    op.execute("DROP TRIGGER knowledge_event_immutable ON knowledge_events")
    op.execute("DROP TRIGGER knowledge_index_immutable ON knowledge_index_entries")
    op.execute("DROP TRIGGER knowledge_document_immutable ON knowledge_documents")
    op.execute("DROP FUNCTION guard_knowledge_index_fact()")
    op.execute("DROP FUNCTION guard_knowledge_document()")
    op.drop_table("knowledge_events")
    op.drop_index("ix_knowledge_index_entries_tokens", table_name="knowledge_index_entries")
    op.drop_table("knowledge_index_entries")
    op.drop_index("ix_knowledge_documents_state_expires_at", table_name="knowledge_documents")
    op.drop_index("ix_knowledge_documents_project_source", table_name="knowledge_documents")
    op.drop_index("ix_knowledge_documents_project_id_id", table_name="knowledge_documents")
    op.drop_table("knowledge_documents")
