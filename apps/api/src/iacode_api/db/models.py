"""The structural tables the later Gates build on.

This is a **persistence contract**, not a feature. Gate 0 creates the tables, their relationships
and their constraints so that Gate 1 has somewhere to record a model call and Gate 2 has somewhere
to record an agent run. It implements none of the behaviour those Gates own: there is no routing,
no orchestration, no retrieval and no scoring here, and no endpoint exposes these tables.

The set comes from `docs/GATE-0-CHECKLIST.md` row 5.6. Two tables named in the Gate 0 prompt are
present with a narrower shape than a later Gate will need, and that is deliberate:

``models``        carries identity and capability flags, not pricing or routing policy. Routing is
                  Gate 1's decision and encoding it now would be guesswork frozen into a schema.
``experiences``   carries the envelope — what happened, which run produced it, and the rights that
                  govern reuse — and stores the body as JSONB. Gate 6 owns the body's schema, and
                  `.iacode/policies/training-data-policy.md` already fixes the rights fields, so
                  the envelope is knowable now and the body is not.

Rights default to denial. `.iacode/policies/provenance-policy.md` makes that a project-wide rule
rather than a table-level opinion, so ``training_allowed`` is ``false`` at the database level and
becomes true only with recorded evidence.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from iacode_api.db.base import Base, ImmutableRecord, TimestampedEntity

# Lifecycle vocabularies. They are CHECK constraints rather than PostgreSQL ENUM types: adding a
# value to an ENUM needs a migration that cannot run inside a transaction on older servers, and
# every one of these vocabularies will grow as the Gates land.
TASK_STATUSES = ("PENDING", "RUNNING", "SUCCEEDED", "FAILED", "CANCELLED")
RUN_STATUSES = ("PENDING", "RUNNING", "SUCCEEDED", "FAILED", "CANCELLED", "TIMED_OUT")


class Project(TimestampedEntity, Base):
    """A unit of work IACode is responsible for."""

    __tablename__ = "projects"

    slug: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)

    repositories: Mapped[list[Repository]] = relationship(
        back_populates="project", cascade="all, delete-orphan")
    tasks: Mapped[list[Task]] = relationship(
        back_populates="project", cascade="all, delete-orphan")


class Repository(TimestampedEntity, Base):
    """A source repository attached to a project."""

    __tablename__ = "repositories"
    __table_args__ = (
        UniqueConstraint("project_id", "name", name="project_id_name"),
    )

    project_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    default_branch: Mapped[str] = mapped_column(String(256), nullable=False, default="main")

    project: Mapped[Project] = relationship(back_populates="repositories")


class Task(TimestampedEntity, Base):
    """Something IACode has been asked to do. Gate 2 gives it behaviour; Gate 0 gives it a home."""

    __tablename__ = "tasks"
    __table_args__ = (
        CheckConstraint(
            "status IN " + str(TASK_STATUSES), name="status_is_known"),
    )

    project_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, default="PENDING", server_default="PENDING")

    project: Mapped[Project] = relationship(back_populates="tasks")
    runs: Mapped[list[TaskRun]] = relationship(
        back_populates="task", cascade="all, delete-orphan")


class TaskRun(TimestampedEntity, Base):
    """One attempt at a task. A task can be attempted more than once; each attempt is a row."""

    __tablename__ = "task_runs"
    __table_args__ = (
        CheckConstraint("status IN " + str(RUN_STATUSES), name="status_is_known"),
        CheckConstraint(
            "finished_at IS NULL OR started_at IS NULL OR finished_at >= started_at",
            name="finished_after_started"),
        Index("ix_task_runs_task_id_created_at", "task_id", "created_at"),
    )

    task_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, default="PENDING", server_default="PENDING")
    attempt: Mapped[int] = mapped_column(Integer, nullable=False, default=1, server_default="1")
    workflow_id: Mapped[str | None] = mapped_column(
        String(256), doc="Temporal workflow identifier, once Gate 2 runs tasks as workflows.")
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    task: Mapped[Task] = relationship(back_populates="runs")
    agent_runs: Mapped[list[AgentRun]] = relationship(
        back_populates="task_run", cascade="all, delete-orphan")


class Agent(TimestampedEntity, Base):
    """A declared agent role.

    Gate 2 loads and executes these; Gate 0 only records that they exist.
    """

    __tablename__ = "agents"

    slug: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    role_contract: Mapped[str] = mapped_column(
        Text, nullable=False,
        doc="Repository path of the canonical role contract in .iacode/agents/.")
    enabled: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false",
        doc="Disabled by default: an agent runs only when a Gate that can run it enables it.")

    runs: Mapped[list[AgentRun]] = relationship(back_populates="agent")


class AgentRun(TimestampedEntity, Base):
    """One execution of one agent inside one task run."""

    __tablename__ = "agent_runs"
    __table_args__ = (
        CheckConstraint("status IN " + str(RUN_STATUSES), name="status_is_known"),
        Index("ix_agent_runs_task_run_id_created_at", "task_run_id", "created_at"),
    )

    task_run_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("task_runs.id", ondelete="CASCADE"), nullable=False)
    agent_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("agents.id", ondelete="RESTRICT"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, default="PENDING", server_default="PENDING")
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    task_run: Mapped[TaskRun] = relationship(back_populates="agent_runs")
    agent: Mapped[Agent] = relationship(back_populates="runs")


class Provider(TimestampedEntity, Base):
    """A model provider.

    Credentials are never stored here: Gate 1 resolves them from configuration.
    """

    __tablename__ = "providers"

    slug: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    kind: Mapped[str] = mapped_column(
        String(64), nullable=False,
        doc="Transport family, for example 'http-api' or 'local-runtime'.")
    enabled: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false")

    models: Mapped[list[Model]] = relationship(
        back_populates="provider", cascade="all, delete-orphan")


class Model(TimestampedEntity, Base):
    """A model a provider exposes. Capability flags only; Gate 1 owns routing and pricing."""

    __tablename__ = "models"
    __table_args__ = (
        UniqueConstraint("provider_id", "slug", name="provider_id_slug"),
    )

    provider_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("providers.id", ondelete="CASCADE"), nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String(256), nullable=False)
    display_name: Mapped[str] = mapped_column(String(256), nullable=False)
    context_window: Mapped[int | None] = mapped_column(Integer)
    supports_tools: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false")
    enabled: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false")

    provider: Mapped[Provider] = relationship(back_populates="models")
    calls: Mapped[list[ModelCall]] = relationship(back_populates="model")


class ModelCall(ImmutableRecord, Base):
    """One invocation of one model. An append-only fact, so it has no update time and no version.

    Prompts and completions are deliberately absent. Storing them is a rights and secret-handling
    decision that `.iacode/policies/training-data-policy.md` governs, and Gate 1 makes it with the
    provenance record in hand. Gate 0 records that a call happened and what it cost.
    """

    __tablename__ = "model_calls"
    __table_args__ = (
        Index("ix_model_calls_model_id_created_at", "model_id", "created_at"),
    )

    model_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("models.id", ondelete="RESTRICT"), nullable=False)
    agent_run_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("agent_runs.id", ondelete="SET NULL"), index=True)
    purpose: Mapped[str] = mapped_column(String(128), nullable=False)
    input_tokens: Mapped[int | None] = mapped_column(Integer)
    output_tokens: Mapped[int | None] = mapped_column(Integer)
    latency_ms: Mapped[int | None] = mapped_column(Integer)
    succeeded: Mapped[bool] = mapped_column(Boolean, nullable=False)
    error_code: Mapped[str | None] = mapped_column(String(128))

    model: Mapped[Model] = relationship(back_populates="calls")


class ToolCall(ImmutableRecord, Base):
    """One tool invocation made during an agent run. Append-only, like every other recorded fact."""

    __tablename__ = "tool_calls"
    __table_args__ = (
        Index("ix_tool_calls_agent_run_id_created_at", "agent_run_id", "created_at"),
    )

    agent_run_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("agent_runs.id", ondelete="CASCADE"), nullable=False)
    tool_name: Mapped[str] = mapped_column(String(128), nullable=False)
    succeeded: Mapped[bool] = mapped_column(Boolean, nullable=False)
    latency_ms: Mapped[int | None] = mapped_column(Integer)
    error_code: Mapped[str | None] = mapped_column(String(128))


class Artifact(TimestampedEntity, Base):
    """A stored object. The bytes live in object storage; this row is the pointer and the metadata.

    ``storage_key`` is unique because two rows pointing at one object make deletion unsafe: neither
    row knows whether the other still needs the bytes.
    """

    __tablename__ = "artifacts"

    task_run_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("task_runs.id", ondelete="SET NULL"), index=True)
    kind: Mapped[str] = mapped_column(String(128), nullable=False)
    storage_bucket: Mapped[str] = mapped_column(String(128), nullable=False)
    storage_key: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    content_type: Mapped[str] = mapped_column(String(256), nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    checksum_sha256: Mapped[str] = mapped_column(String(64), nullable=False)


class Experience(TimestampedEntity, Base):
    """An observable engineering experience, with the rights that govern its reuse.

    Gate 6 owns the body, which is why it is JSONB here. The envelope is knowable now because
    `.iacode/policies/provenance-policy.md` already fixes it, and the rights columns default to
    denial so an experience cannot become training data by omission.
    """

    __tablename__ = "experiences"
    __table_args__ = (
        Index("ix_experiences_kind_created_at", "kind", "created_at"),
    )

    task_run_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("task_runs.id", ondelete="SET NULL"), index=True)
    kind: Mapped[str] = mapped_column(String(128), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    body: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False, default=dict, server_default="{}")
    source_type: Mapped[str] = mapped_column(String(64), nullable=False)
    ownership: Mapped[str] = mapped_column(String(64), nullable=False)
    license: Mapped[str] = mapped_column(String(128), nullable=False)
    storage_allowed: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default="true")
    rag_allowed: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false")
    training_allowed: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false",
        doc="Denied by default; granted only with recorded rights evidence.")
    distillation_allowed: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false")
