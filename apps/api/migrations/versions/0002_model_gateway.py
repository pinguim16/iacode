"""Model gateway schema.

What Gate 1 needs the persistence contract to carry: a provider's operational state, a model as the
catalog actually discovered it, and the operational record of every attempt.

Three changes are decisions rather than additions, and each removes something Gate 0 created.

**``models.supports_tools`` and ``models.enabled`` are dropped.** Both are non-null booleans, and a
boolean cannot express the state most discovery answers produce: the provider said nothing. Keeping
them would mean the catalog asserting ``false`` about a model it was told nothing about, and the
router excluding every model a terse provider lists. Capability is stored as JSONB with a
provenance map beside it, so ``UNKNOWN`` survives to the routing policy that has a rule for it.
``active`` replaces ``enabled`` and means what the provider said, not what an operator switched.

**``model_calls.model_id`` becomes nullable.** A call can outlive the catalog row it names — a model
withdrawn between the call and the record — and losing the record of a call that cost money is worse
than losing the link to a row that no longer describes anything.

**Nothing here stores content.** There is no column for a prompt, a message or a completion, and
that absence is the control. `docs/GATE-1-CHECKLIST.md` row 10.4 asks for prompts not to be
persisted by default; a schema with nowhere to put one cannot be made to put one there by a later
edit that forgets.

The downgrade is real and restores the Gate 0 shape, including the two boolean columns. It cannot
restore what those columns never contained, so it fills them from the capability map where the map
says ``SUPPORTED`` — which is exactly the information loss that motivated the change, stated rather
than hidden.

Revision ID: 0002_model_gateway
Revises: 0001_foundation
Created: 2026-09-22

"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0002_model_gateway"
down_revision: str | None = "0001_foundation"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # --- providers: operational state -----------------------------------------------------------
    op.add_column("providers", sa.Column("adapter", sa.String(length=64), nullable=True))
    op.add_column("providers", sa.Column("healthy", sa.Boolean(), nullable=True))
    op.add_column("providers",
                  sa.Column("last_health_check", sa.DateTime(timezone=True), nullable=True))
    op.add_column("providers", sa.Column("last_sync", sa.DateTime(timezone=True), nullable=True))
    op.add_column("providers",
                  sa.Column("model_count", sa.Integer(), server_default="0", nullable=False))
    op.add_column("providers", sa.Column("detail", sa.Text(), nullable=True))

    # --- models: the catalog as it was discovered ------------------------------------------------
    op.add_column("models", sa.Column("family", sa.String(length=128), nullable=True))
    op.add_column("models", sa.Column("max_output_tokens", sa.Integer(), nullable=True))
    op.add_column("models", sa.Column(
        "supported_endpoints", postgresql.JSONB(astext_type=sa.Text()),
        server_default="[]", nullable=False))
    op.add_column("models", sa.Column(
        "capabilities", postgresql.JSONB(astext_type=sa.Text()),
        server_default="{}", nullable=False))
    op.add_column("models", sa.Column(
        "capability_provenance", postgresql.JSONB(astext_type=sa.Text()),
        server_default="{}", nullable=False))
    op.add_column("models", sa.Column(
        "reasoning_levels", postgresql.JSONB(astext_type=sa.Text()),
        server_default="[]", nullable=False))
    op.add_column("models",
                  sa.Column("active", sa.Boolean(), server_default="true", nullable=False))
    op.add_column("models", sa.Column(
        "raw_metadata", postgresql.JSONB(astext_type=sa.Text()),
        server_default="{}", nullable=False))
    op.add_column("models", sa.Column("synced_at", sa.DateTime(timezone=True), nullable=True))

    # Carry forward what the booleans did say before they are dropped, so an upgrade of a populated
    # database keeps the statements an operator had made rather than resetting them to unknown.
    op.execute(
        "UPDATE models SET capabilities = jsonb_build_object('tools', 'SUPPORTED'), "
        "capability_provenance = jsonb_build_object('tools', 'MANUAL_CONFIGURATION') "
        "WHERE supports_tools IS TRUE")
    op.execute("UPDATE models SET active = enabled")

    op.drop_column("models", "supports_tools")
    op.drop_column("models", "enabled")

    # --- model_calls: the operational record ------------------------------------------------------
    op.alter_column("model_calls", "model_id", existing_type=sa.UUID(), nullable=True)
    op.add_column("model_calls", sa.Column("provider_id", sa.UUID(), nullable=True))
    op.add_column("model_calls", sa.Column(
        "request_id", sa.String(length=128), server_default="", nullable=False))
    op.alter_column("model_calls", "request_id", server_default=None)
    op.add_column("model_calls", sa.Column("correlation_id", sa.String(length=128), nullable=True))
    op.add_column("model_calls",
                  sa.Column("request_fingerprint", sa.String(length=64), nullable=True))
    op.add_column("model_calls", sa.Column("endpoint", sa.String(length=64), nullable=True))
    op.add_column("model_calls", sa.Column("route", sa.String(length=64), nullable=True))
    op.add_column("model_calls", sa.Column(
        "status", sa.String(length=32), server_default="UNKNOWN", nullable=False))
    op.add_column("model_calls", sa.Column("started_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("model_calls",
                  sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("model_calls", sa.Column("cached_input_tokens", sa.Integer(), nullable=True))
    op.add_column("model_calls", sa.Column("reasoning_tokens", sa.Integer(), nullable=True))
    op.add_column("model_calls", sa.Column("cost", sa.Numeric(precision=18, scale=8),
                                           nullable=True))
    op.add_column("model_calls",
                  sa.Column("retry_count", sa.Integer(), server_default="0", nullable=False))
    op.add_column("model_calls",
                  sa.Column("fallback_count", sa.Integer(), server_default="0", nullable=False))

    op.create_foreign_key(
        op.f("fk_model_calls_provider_id_providers"), "model_calls", "providers",
        ["provider_id"], ["id"], ondelete="RESTRICT")
    op.create_index("ix_model_calls_provider_id_created_at", "model_calls",
                    ["provider_id", "created_at"], unique=False)
    op.create_check_constraint(
        "finished_after_started", "model_calls",
        "finished_at IS NULL OR started_at IS NULL OR finished_at >= started_at")


def downgrade() -> None:
    op.drop_constraint(op.f("ck_model_calls_finished_after_started"), "model_calls",
                       type_="check")
    op.drop_index("ix_model_calls_provider_id_created_at", table_name="model_calls")
    op.drop_constraint(op.f("fk_model_calls_provider_id_providers"), "model_calls",
                       type_="foreignkey")
    for column in ("fallback_count", "retry_count", "cost", "reasoning_tokens",
                   "cached_input_tokens", "finished_at", "started_at", "status", "route",
                   "endpoint", "request_fingerprint", "correlation_id", "request_id",
                   "provider_id"):
        op.drop_column("model_calls", column)
    # A row whose model has since been withdrawn cannot satisfy the restored NOT NULL, and inventing
    # a model for it would be worse than refusing: the rows are deleted, and the downgrade says so.
    op.execute("DELETE FROM model_calls WHERE model_id IS NULL")
    op.alter_column("model_calls", "model_id", existing_type=sa.UUID(), nullable=False)

    op.add_column("models",
                  sa.Column("enabled", sa.Boolean(), server_default="false", nullable=False))
    op.add_column("models",
                  sa.Column("supports_tools", sa.Boolean(), server_default="false",
                            nullable=False))
    op.execute("UPDATE models SET enabled = active")
    op.execute("UPDATE models SET supports_tools = TRUE "
               "WHERE capabilities ->> 'tools' = 'SUPPORTED'")
    for column in ("synced_at", "raw_metadata", "active", "reasoning_levels",
                   "capability_provenance", "capabilities", "supported_endpoints",
                   "max_output_tokens", "family"):
        op.drop_column("models", column)

    for column in ("detail", "model_count", "last_sync", "last_health_check", "healthy",
                   "adapter"):
        op.drop_column("providers", column)
