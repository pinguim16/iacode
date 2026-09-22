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
from decimal import Decimal
from typing import Any

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
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
    """A model provider and its operational state.

    Credentials are never stored here. Gate 1 resolves them from the environment at call time, and
    the absence of a column is the mechanism: a nullable secret column is a place a secret
    eventually lands, whatever the intention was when it was added.
    """

    __tablename__ = "providers"

    slug: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    kind: Mapped[str] = mapped_column(
        String(64), nullable=False,
        doc="Transport family, for example 'http-api' or 'local-runtime'.")
    enabled: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false")
    adapter: Mapped[str | None] = mapped_column(
        String(64),
        doc="The adapter family that serves this provider, mirrored from the provider policy.")
    healthy: Mapped[bool | None] = mapped_column(
        Boolean,
        doc="Result of the last health probe. NULL means never probed, which is not the same as "
            "unhealthy and is not rendered as one.")
    last_health_check: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_sync: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    model_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0")
    detail: Mapped[str | None] = mapped_column(
        Text,
        doc="Why the last probe or synchronisation failed, already classified. Never a provider's "
            "raw error body, which can echo a request header back at us.")

    models: Mapped[list[Model]] = relationship(
        back_populates="provider", cascade="all, delete-orphan")


class Model(TimestampedEntity, Base):
    """A model a provider exposes, as the catalog discovered it.

    Identity is the pair ``(provider_id, slug)``: two providers may expose the same identifier, and
    they are different models with different availability and different prices.

    **Capabilities are a tri-state, stored as JSONB rather than as booleans.** Gate 0 gave this
    table ``supports_tools`` and ``enabled`` as non-null booleans, and Gate 1 removes both, because
    a boolean cannot express the state most discovery answers actually produce: the provider said
    nothing. Recording that silence as ``false`` would make the catalog assert a fact it was never
    told, and the router would quietly exclude every model a terse provider lists.
    ``capability_provenance`` records where each statement came from, so an administrator's claim is
    never mistaken for the provider's.
    """

    __tablename__ = "models"
    __table_args__ = (
        UniqueConstraint("provider_id", "slug", name="provider_id_slug"),
    )

    provider_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("providers.id", ondelete="CASCADE"), nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String(256), nullable=False)
    display_name: Mapped[str] = mapped_column(String(256), nullable=False)
    family: Mapped[str | None] = mapped_column(String(128))
    context_window: Mapped[int | None] = mapped_column(Integer)
    max_output_tokens: Mapped[int | None] = mapped_column(Integer)
    supported_endpoints: Mapped[list[str]] = mapped_column(
        JSONB, nullable=False, default=list, server_default="[]",
        doc="Protocol families the model accepts. Empty means the provider did not say, which the "
            "endpoint selection treats differently from 'accepts none'.")
    capabilities: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False, default=dict, server_default="{}",
        doc="Capability to SUPPORTED, UNSUPPORTED or UNKNOWN. An absent key is UNKNOWN.")
    capability_provenance: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False, default=dict, server_default="{}",
        doc="Capability to PROVIDER_METADATA, MANUAL_CONFIGURATION or OBSERVED.")
    reasoning_levels: Mapped[list[str]] = mapped_column(
        JSONB, nullable=False, default=list, server_default="[]")
    active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default="true",
        doc="Whether the provider still lists the model. A model that disappears is deactivated "
            "rather than deleted, because model_calls rows point at it.")
    raw_metadata: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False, default=dict, server_default="{}",
        doc="The provider's own record, kept for diagnosis. Routing reads the normalised columns; "
            "nothing decides behaviour from this.")
    synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    provider: Mapped[Provider] = relationship(back_populates="models")
    calls: Mapped[list[ModelCall]] = relationship(back_populates="model")


class ModelCall(ImmutableRecord, Base):
    """One attempt against one model. An append-only fact, so it has no update time and no version.

    **Prompts and completions are absent, and this is the mechanism rather than the intention.**
    There is no column for a message, a prompt or a completion, so no code path can put one here by
    accident, and `docs/GATE-1-CHECKLIST.md` row 10.4 is satisfied by the shape of the table. What
    is recorded is operational: who was called, over which protocol, by which routing decision, how
    it went, how long it took, what it consumed and what it cost when that is knowable.

    ``request_fingerprint`` is a digest of what was asked, for correlating two identical calls
    without storing either. It is not anonymisation: anyone holding a candidate prompt can hash it
    and compare. The runbook says so in the same words.

    ``model_id`` is nullable from Gate 1. A call can legitimately outlive the catalog row it names —
    a model withdrawn between the call and the record — and losing the record of a call that cost
    money would be worse than losing the link to a row that no longer describes anything.
    """

    __tablename__ = "model_calls"
    __table_args__ = (
        Index("ix_model_calls_model_id_created_at", "model_id", "created_at"),
        Index("ix_model_calls_provider_id_created_at", "provider_id", "created_at"),
        CheckConstraint(
            "finished_at IS NULL OR started_at IS NULL OR finished_at >= started_at",
            name="finished_after_started"),
    )

    model_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("models.id", ondelete="RESTRICT"))
    provider_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("providers.id", ondelete="RESTRICT"))
    agent_run_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("agent_runs.id", ondelete="SET NULL"), index=True)
    request_id: Mapped[str] = mapped_column(String(128), nullable=False)
    correlation_id: Mapped[str | None] = mapped_column(String(128))
    request_fingerprint: Mapped[str | None] = mapped_column(String(64))
    endpoint: Mapped[str | None] = mapped_column(String(64))
    route: Mapped[str | None] = mapped_column(String(64))
    purpose: Mapped[str] = mapped_column(String(128), nullable=False)
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, default="UNKNOWN", server_default="UNKNOWN")
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    input_tokens: Mapped[int | None] = mapped_column(Integer)
    output_tokens: Mapped[int | None] = mapped_column(Integer)
    cached_input_tokens: Mapped[int | None] = mapped_column(Integer)
    reasoning_tokens: Mapped[int | None] = mapped_column(
        Integer,
        doc="How many reasoning tokens the provider reported. The reasoning itself is never "
            "stored: a model's private deliberation is not ours to keep.")
    cost: Mapped[Decimal | None] = mapped_column(
        Numeric(18, 8),
        doc="NULL unless pricing is configured. Zero would state that the call was free.")
    latency_ms: Mapped[int | None] = mapped_column(Integer)
    retry_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0")
    fallback_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0")
    succeeded: Mapped[bool] = mapped_column(Boolean, nullable=False)
    error_code: Mapped[str | None] = mapped_column(
        String(128), doc="The gateway's classified error type, never a provider's raw message.")

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
