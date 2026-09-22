"""Foundation schema.

The structural tables Gate 0 establishes so that later Gates have somewhere to record what they do.
No behaviour depends on them yet and no endpoint exposes them; they are a persistence contract.

Two things in here are decisions rather than generated output:

**The pgvector extension is created, and nothing uses it.** The image ships it, creating it costs
nothing, and doing it now means Gate 7 adds a column rather than migrating the database engine. No
vector column is defined, because the embedding dimension is a retrieval decision and choosing one
before there is a retriever would be a guess frozen into a schema. `docs/adr/ADR-0013` records this.

**The downgrade is real.** It is not expected to be run against anything that matters, but a
migration that cannot be reversed cannot be rehearsed either, and the first delivery is exactly when
that rehearsal is cheap.

Revision ID: 0001_foundation
Revises:
Created: 2026-09-21

"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001_foundation"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Prepared, not used. See the module docstring and ADR-0013.
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table('agents',
    sa.Column('slug', sa.String(length=128), nullable=False),
    sa.Column('name', sa.String(length=256), nullable=False),
    sa.Column('role_contract', sa.Text(), nullable=False),
    sa.Column('enabled', sa.Boolean(), server_default='false', nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('version', sa.BigInteger(), server_default='1', nullable=False),
    sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_agents')),
    sa.UniqueConstraint('slug', name=op.f('uq_agents_slug'))
    )
    op.create_table('projects',
    sa.Column('slug', sa.String(length=128), nullable=False),
    sa.Column('name', sa.String(length=256), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('version', sa.BigInteger(), server_default='1', nullable=False),
    sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_projects')),
    sa.UniqueConstraint('slug', name=op.f('uq_projects_slug'))
    )
    op.create_table('providers',
    sa.Column('slug', sa.String(length=128), nullable=False),
    sa.Column('name', sa.String(length=256), nullable=False),
    sa.Column('kind', sa.String(length=64), nullable=False),
    sa.Column('enabled', sa.Boolean(), server_default='false', nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('version', sa.BigInteger(), server_default='1', nullable=False),
    sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_providers')),
    sa.UniqueConstraint('slug', name=op.f('uq_providers_slug'))
    )
    op.create_table('models',
    sa.Column('provider_id', sa.UUID(), nullable=False),
    sa.Column('slug', sa.String(length=256), nullable=False),
    sa.Column('display_name', sa.String(length=256), nullable=False),
    sa.Column('context_window', sa.Integer(), nullable=True),
    sa.Column('supports_tools', sa.Boolean(), server_default='false', nullable=False),
    sa.Column('enabled', sa.Boolean(), server_default='false', nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('version', sa.BigInteger(), server_default='1', nullable=False),
    sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['provider_id'], ['providers.id'], name=op.f('fk_models_provider_id_providers'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_models')),
    sa.UniqueConstraint('provider_id', 'slug', name='provider_id_slug')
    )
    op.create_index(op.f('ix_models_provider_id'), 'models', ['provider_id'], unique=False)
    op.create_table('repositories',
    sa.Column('project_id', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(length=256), nullable=False),
    sa.Column('url', sa.Text(), nullable=False),
    sa.Column('default_branch', sa.String(length=256), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('version', sa.BigInteger(), server_default='1', nullable=False),
    sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['project_id'], ['projects.id'], name=op.f('fk_repositories_project_id_projects'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_repositories')),
    sa.UniqueConstraint('project_id', 'name', name='project_id_name')
    )
    op.create_index(op.f('ix_repositories_project_id'), 'repositories', ['project_id'], unique=False)
    op.create_table('tasks',
    sa.Column('project_id', sa.UUID(), nullable=False),
    sa.Column('title', sa.String(length=512), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('status', sa.String(length=32), server_default='PENDING', nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('version', sa.BigInteger(), server_default='1', nullable=False),
    sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.CheckConstraint("status IN ('PENDING', 'RUNNING', 'SUCCEEDED', 'FAILED', 'CANCELLED')", name=op.f('ck_tasks_status_is_known')),
    sa.ForeignKeyConstraint(['project_id'], ['projects.id'], name=op.f('fk_tasks_project_id_projects'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_tasks'))
    )
    op.create_index(op.f('ix_tasks_project_id'), 'tasks', ['project_id'], unique=False)
    op.create_table('task_runs',
    sa.Column('task_id', sa.UUID(), nullable=False),
    sa.Column('status', sa.String(length=32), server_default='PENDING', nullable=False),
    sa.Column('attempt', sa.Integer(), server_default='1', nullable=False),
    sa.Column('workflow_id', sa.String(length=256), nullable=True),
    sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('finished_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('version', sa.BigInteger(), server_default='1', nullable=False),
    sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.CheckConstraint("status IN ('PENDING', 'RUNNING', 'SUCCEEDED', 'FAILED', 'CANCELLED', 'TIMED_OUT')", name=op.f('ck_task_runs_status_is_known')),
    sa.CheckConstraint('finished_at IS NULL OR started_at IS NULL OR finished_at >= started_at', name=op.f('ck_task_runs_finished_after_started')),
    sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], name=op.f('fk_task_runs_task_id_tasks'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_task_runs'))
    )
    op.create_index('ix_task_runs_task_id_created_at', 'task_runs', ['task_id', 'created_at'], unique=False)
    op.create_table('agent_runs',
    sa.Column('task_run_id', sa.UUID(), nullable=False),
    sa.Column('agent_id', sa.UUID(), nullable=False),
    sa.Column('status', sa.String(length=32), server_default='PENDING', nullable=False),
    sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('finished_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('version', sa.BigInteger(), server_default='1', nullable=False),
    sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.CheckConstraint("status IN ('PENDING', 'RUNNING', 'SUCCEEDED', 'FAILED', 'CANCELLED', 'TIMED_OUT')", name=op.f('ck_agent_runs_status_is_known')),
    sa.ForeignKeyConstraint(['agent_id'], ['agents.id'], name=op.f('fk_agent_runs_agent_id_agents'), ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['task_run_id'], ['task_runs.id'], name=op.f('fk_agent_runs_task_run_id_task_runs'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_agent_runs'))
    )
    op.create_index(op.f('ix_agent_runs_agent_id'), 'agent_runs', ['agent_id'], unique=False)
    op.create_index('ix_agent_runs_task_run_id_created_at', 'agent_runs', ['task_run_id', 'created_at'], unique=False)
    op.create_table('artifacts',
    sa.Column('task_run_id', sa.UUID(), nullable=True),
    sa.Column('kind', sa.String(length=128), nullable=False),
    sa.Column('storage_bucket', sa.String(length=128), nullable=False),
    sa.Column('storage_key', sa.Text(), nullable=False),
    sa.Column('content_type', sa.String(length=256), nullable=False),
    sa.Column('size_bytes', sa.Integer(), nullable=False),
    sa.Column('checksum_sha256', sa.String(length=64), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('version', sa.BigInteger(), server_default='1', nullable=False),
    sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['task_run_id'], ['task_runs.id'], name=op.f('fk_artifacts_task_run_id_task_runs'), ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_artifacts')),
    sa.UniqueConstraint('storage_key', name=op.f('uq_artifacts_storage_key'))
    )
    op.create_index(op.f('ix_artifacts_task_run_id'), 'artifacts', ['task_run_id'], unique=False)
    op.create_table('experiences',
    sa.Column('task_run_id', sa.UUID(), nullable=True),
    sa.Column('kind', sa.String(length=128), nullable=False),
    sa.Column('summary', sa.Text(), nullable=False),
    sa.Column('body', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False),
    sa.Column('source_type', sa.String(length=64), nullable=False),
    sa.Column('ownership', sa.String(length=64), nullable=False),
    sa.Column('license', sa.String(length=128), nullable=False),
    sa.Column('storage_allowed', sa.Boolean(), server_default='true', nullable=False),
    sa.Column('rag_allowed', sa.Boolean(), server_default='false', nullable=False),
    sa.Column('training_allowed', sa.Boolean(), server_default='false', nullable=False),
    sa.Column('distillation_allowed', sa.Boolean(), server_default='false', nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('version', sa.BigInteger(), server_default='1', nullable=False),
    sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['task_run_id'], ['task_runs.id'], name=op.f('fk_experiences_task_run_id_task_runs'), ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_experiences'))
    )
    op.create_index('ix_experiences_kind_created_at', 'experiences', ['kind', 'created_at'], unique=False)
    op.create_index(op.f('ix_experiences_task_run_id'), 'experiences', ['task_run_id'], unique=False)
    op.create_table('model_calls',
    sa.Column('model_id', sa.UUID(), nullable=False),
    sa.Column('agent_run_id', sa.UUID(), nullable=True),
    sa.Column('purpose', sa.String(length=128), nullable=False),
    sa.Column('input_tokens', sa.Integer(), nullable=True),
    sa.Column('output_tokens', sa.Integer(), nullable=True),
    sa.Column('latency_ms', sa.Integer(), nullable=True),
    sa.Column('succeeded', sa.Boolean(), nullable=False),
    sa.Column('error_code', sa.String(length=128), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['agent_run_id'], ['agent_runs.id'], name=op.f('fk_model_calls_agent_run_id_agent_runs'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['model_id'], ['models.id'], name=op.f('fk_model_calls_model_id_models'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_model_calls'))
    )
    op.create_index(op.f('ix_model_calls_agent_run_id'), 'model_calls', ['agent_run_id'], unique=False)
    op.create_index('ix_model_calls_model_id_created_at', 'model_calls', ['model_id', 'created_at'], unique=False)
    op.create_table('tool_calls',
    sa.Column('agent_run_id', sa.UUID(), nullable=False),
    sa.Column('tool_name', sa.String(length=128), nullable=False),
    sa.Column('succeeded', sa.Boolean(), nullable=False),
    sa.Column('latency_ms', sa.Integer(), nullable=True),
    sa.Column('error_code', sa.String(length=128), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['agent_run_id'], ['agent_runs.id'], name=op.f('fk_tool_calls_agent_run_id_agent_runs'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_tool_calls'))
    )
    op.create_index('ix_tool_calls_agent_run_id_created_at', 'tool_calls', ['agent_run_id', 'created_at'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_tool_calls_agent_run_id_created_at', table_name='tool_calls')
    op.drop_table('tool_calls')
    op.drop_index('ix_model_calls_model_id_created_at', table_name='model_calls')
    op.drop_index(op.f('ix_model_calls_agent_run_id'), table_name='model_calls')
    op.drop_table('model_calls')
    op.drop_index(op.f('ix_experiences_task_run_id'), table_name='experiences')
    op.drop_index('ix_experiences_kind_created_at', table_name='experiences')
    op.drop_table('experiences')
    op.drop_index(op.f('ix_artifacts_task_run_id'), table_name='artifacts')
    op.drop_table('artifacts')
    op.drop_index('ix_agent_runs_task_run_id_created_at', table_name='agent_runs')
    op.drop_index(op.f('ix_agent_runs_agent_id'), table_name='agent_runs')
    op.drop_table('agent_runs')
    op.drop_index('ix_task_runs_task_id_created_at', table_name='task_runs')
    op.drop_table('task_runs')
    op.drop_index(op.f('ix_tasks_project_id'), table_name='tasks')
    op.drop_table('tasks')
    op.drop_index(op.f('ix_repositories_project_id'), table_name='repositories')
    op.drop_table('repositories')
    op.drop_index(op.f('ix_models_provider_id'), table_name='models')
    op.drop_table('models')
    op.drop_table('providers')
    op.drop_table('projects')
    op.drop_table('agents')
    op.execute("DROP EXTENSION IF EXISTS vector")
