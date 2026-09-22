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

from iacode_contracts.agent_runtime import (
    AGENT_RUN_STATES,
    RUN_EVENT_TYPES,
    TOOL_REQUEST_STATUSES,
    TOOL_RESULT_STATUSES,
)
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

from iacode_persistence.base import Base, ImmutableRecord, TimestampedEntity

# Lifecycle vocabularies. They are CHECK constraints rather than PostgreSQL ENUM types: adding a
# value to an ENUM needs a migration that cannot run inside a transaction on older servers, and
# every one of these vocabularies will grow as the Gates land.
TASK_STATUSES = ("PENDING", "RUNNING", "SUCCEEDED", "FAILED", "CANCELLED")

#: The states a run may hold, **derived** from the shared vocabulary rather than written again.
#: Gate 0 declared six of its own; Gate 2 needs `CREATED`, `QUEUED` and `WAITING_FOR_TOOL` as well,
#: and the honest way to add them is to take the runtime's canonical tuple and keep the historical
#: values a sealed row may still carry. A second literal list here is exactly the duplicated
#: classification `.iacode/memory/lessons.jsonl` records as a failure class: one copy grows a value
#: the other does not have, and the disagreement surfaces as a constraint violation.
_LEGACY_RUN_STATUSES = ("PENDING", "TIMED_OUT")
RUN_STATUSES = AGENT_RUN_STATES + _LEGACY_RUN_STATUSES


def _vocabulary(values: tuple[str, ...]) -> str:
    """A CHECK expression over a vocabulary, rendered the same way everywhere."""
    return "(" + ", ".join(f"'{value}'" for value in values) + ")"


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
            "status IN " + _vocabulary(TASK_STATUSES), name="status_is_known"),
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
    """One attempt at a task. A task can be attempted more than once; each attempt is a row.

    Gate 2 gives the row its behaviour. ``status`` becomes the run's state in the agent runtime's
    state machine — the same column, a wider vocabulary — because a second state column would be a
    second answer to "what is this run doing". ``result`` is the run's own final answer and
    ``budget`` is what it was allowed to spend; neither is a prompt and neither is a provider
    payload, which is the difference between this table and ``model_calls``:

    ``model_calls``   records that a call happened and what it cost. It has no column that could
                      hold what was said, by shape rather than by discipline.
    ``task_runs``     records what IACode was asked to do and what it answered, because the
                      workflow cannot resume without the first and the operator cannot read the
                      run without the second. This is local operational persistence, not a
                      transcript of a provider exchange.
    """

    __tablename__ = "task_runs"
    __table_args__ = (
        CheckConstraint("status IN " + _vocabulary(RUN_STATUSES), name="status_is_known"),
        CheckConstraint(
            "finished_at IS NULL OR started_at IS NULL OR finished_at >= started_at",
            name="finished_after_started"),
        Index("ix_task_runs_task_id_created_at", "task_id", "created_at"),
        UniqueConstraint("idempotency_key", name="idempotency_key"),
    )

    task_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, default="PENDING", server_default="PENDING")
    attempt: Mapped[int] = mapped_column(Integer, nullable=False, default=1, server_default="1")
    workflow_id: Mapped[str | None] = mapped_column(
        String(256), doc="Temporal workflow identifier of the run that executes this attempt.")
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # --- Gate 2: what the run is, what it may spend and what it answered -----------------------
    team_slug: Mapped[str | None] = mapped_column(
        String(128), doc="The team profile this run executes, frozen when the run was created.")
    team_version: Mapped[str | None] = mapped_column(String(32))
    route: Mapped[str | None] = mapped_column(
        String(64), doc="A configured route alias the gateway resolves. Never a provider address.")
    model_override: Mapped[str | None] = mapped_column(
        String(384),
        doc="An explicit 'provider:model' the caller asked for. The gateway decides whether it "
            "can serve the request; nothing here inspects provider metadata.")
    idempotency_key: Mapped[str | None] = mapped_column(
        String(128),
        doc="Unique when present: a repeated creation request returns the run the first one made.")
    current_stage: Mapped[str | None] = mapped_column(String(128))
    budget: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False, default=dict, server_default="{}",
        doc="The limits this run was created with. Frozen; a later configuration change does not "
            "retroactively widen a running run.")
    budget_used: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False, default=dict, server_default="{}")
    result: Mapped[str | None] = mapped_column(
        Text, doc="The run's final answer, kept so the page can render it after a restart.")
    result_summary: Mapped[str | None] = mapped_column(String(1024))
    error_type: Mapped[str | None] = mapped_column(
        String(128), doc="The runtime's classified error type, never a traceback.")
    error_summary: Mapped[str | None] = mapped_column(String(2048))
    failed_stage: Mapped[str | None] = mapped_column(String(128))
    correlation_id: Mapped[str | None] = mapped_column(String(128))
    cancel_requested: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false")
    training_allowed: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false",
        doc="Denied by default. Nothing in this Gate grants it, and no run enters a dataset.")

    task: Mapped[Task] = relationship(back_populates="runs")
    agent_runs: Mapped[list[AgentRun]] = relationship(
        back_populates="task_run", cascade="all, delete-orphan")
    events: Mapped[list[RunEvent]] = relationship(
        back_populates="task_run", cascade="all, delete-orphan")
    tool_requests: Mapped[list[ToolRequest]] = relationship(
        back_populates="task_run", cascade="all, delete-orphan")


class Agent(TimestampedEntity, Base):
    """A declared agent role.

    Gate 0 recorded that roles exist; Gate 2 loads and executes them, so the row now carries the
    configuration the runtime actually reads. The definition lives in ``agents/profiles/`` and this
    table is its operational mirror: ``definition_hash`` is what makes the bootstrap idempotent,
    and ``customised`` is what stops it from silently overwriting an operator's edit.
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

    # --- Gate 2: the configuration the runtime reads -------------------------------------------
    role: Mapped[str | None] = mapped_column(String(128))
    description: Mapped[str | None] = mapped_column(Text)
    profile_version: Mapped[str | None] = mapped_column(
        String(32),
        doc="The version the definition declares. Distinct from the inherited optimistic-locking "
            "``version``, which counts writes to this row: one number is about the profile and "
            "the other is about the row, and sharing a name would make both unreadable.")
    default_route: Mapped[str | None] = mapped_column(String(64))
    max_turns: Mapped[int | None] = mapped_column(Integer)
    allowed_actions: Mapped[list[str]] = mapped_column(
        JSONB, nullable=False, default=list, server_default="[]",
        doc="The tool names this role may request. A request outside the set is refused before "
            "anything is persisted; nothing here executes one.")
    prompt_template: Mapped[str | None] = mapped_column(
        String(256), doc="Repository path of the versioned prompt template.")
    prompt_template_version: Mapped[str | None] = mapped_column(String(32))
    prompt_template_hash: Mapped[str | None] = mapped_column(String(64))
    definition_hash: Mapped[str | None] = mapped_column(
        String(64), doc="Digest of the repository definition this row was loaded from.")
    customised: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false",
        doc="Set by an operator who edited the row. Bootstrap leaves a customised row alone.")

    runs: Mapped[list[AgentRun]] = relationship(back_populates="agent")


class AgentTeam(TimestampedEntity, Base):
    """A declared team: an ordered list of stages, each naming an agent.

    Composition is configuration. Nothing in this Gate invents a team and no model decides which
    agents run — dynamic composition is a later Gate's problem and pretending to have it now would
    be a feature that cannot be evidenced.
    """

    __tablename__ = "agent_teams"

    slug: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    profile_version: Mapped[str] = mapped_column(
        String(32), nullable=False, default="1.0.0", server_default="1.0.0")
    stages: Mapped[list[dict[str, Any]]] = mapped_column(
        JSONB, nullable=False, default=list, server_default="[]")
    enabled: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default="true")
    definition_hash: Mapped[str | None] = mapped_column(String(64))
    customised: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false")


class AgentRun(TimestampedEntity, Base):
    """One execution of one agent inside one task run.

    It carries the provenance of what produced its output: which profile version, which prompt
    template and which hash of that template. Without those three, a run that behaved oddly cannot
    be reproduced, because the definition it ran under may have changed since.

    There is no aggregate token column and no aggregate cost column. ``model_calls`` already holds
    the authoritative usage of every call this run made, and a second count maintained by hand is a
    second number that will eventually disagree with the first.
    """

    __tablename__ = "agent_runs"
    __table_args__ = (
        CheckConstraint("status IN " + _vocabulary(RUN_STATUSES), name="status_is_known"),
        Index("ix_agent_runs_task_run_id_created_at", "task_run_id", "created_at"),
        UniqueConstraint("task_run_id", "stage_index", name="task_run_id_stage_index"),
    )

    task_run_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("task_runs.id", ondelete="CASCADE"), nullable=False)
    agent_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("agents.id", ondelete="RESTRICT"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, default="PENDING", server_default="PENDING")
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # --- Gate 2: which stage this is, what produced it and what it answered ---------------------
    stage_index: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0")
    stage_name: Mapped[str | None] = mapped_column(String(128))
    agent_slug: Mapped[str | None] = mapped_column(String(128))
    profile_version: Mapped[str | None] = mapped_column(String(32))
    prompt_template_version: Mapped[str | None] = mapped_column(String(32))
    prompt_template_hash: Mapped[str | None] = mapped_column(String(64))
    turns: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    model_calls: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0")
    output_name: Mapped[str | None] = mapped_column(String(128))
    output: Mapped[str | None] = mapped_column(
        Text, doc="What this agent produced, as the next stage will receive it.")
    output_summary: Mapped[str | None] = mapped_column(
        String(1024),
        doc="A short verifiable summary of the outcome. Never a model's private reasoning.")
    error_type: Mapped[str | None] = mapped_column(String(128))
    error_summary: Mapped[str | None] = mapped_column(String(2048))

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
    """One tool invocation that **was executed**, append-only, like every other recorded fact.

    Gate 2 writes no row here, and that is not an omission. This table records an execution — a
    latency, a success, an error code — and Gate 2 executes nothing. What Gate 2 records is a
    *request* and its *result*, in ``tool_requests`` and ``tool_results``; the sandbox that
    executes one is Gate 3's, and it is what will fill this table.
    """

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


class RunEvent(ImmutableRecord, Base):
    """One recorded moment of a run. Append-only by shape as well as by intention.

    It inherits :class:`ImmutableRecord`, so there is no ``updated_at`` and no ``version``: an
    event describes something that already happened, and a column that invites an update is how a
    history quietly stops being one. A correction is a later event, never an edit.

    ``sequence`` is unique per run and assigned by the store, so the order two consumers see is the
    same order and a reconnecting consumer can resume from a cursor. ``dedupe_key`` is what makes
    an append idempotent: a Temporal activity can execute more than once, and an event log that
    grew a duplicate every time an activity was retried would make the run's history a function of
    infrastructure luck.
    """

    __tablename__ = "run_events"
    __table_args__ = (
        CheckConstraint("event_type IN " + _vocabulary(RUN_EVENT_TYPES),
                        name="event_type_is_known"),
        UniqueConstraint("task_run_id", "sequence", name="task_run_id_sequence"),
        UniqueConstraint("task_run_id", "dedupe_key", name="task_run_id_dedupe_key"),
        Index("ix_run_events_task_run_id_sequence", "task_run_id", "sequence"),
    )

    task_run_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("task_runs.id", ondelete="CASCADE"), nullable=False)
    agent_run_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("agent_runs.id", ondelete="SET NULL"))
    sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    stage: Mapped[str | None] = mapped_column(String(128))
    dedupe_key: Mapped[str] = mapped_column(
        String(128), nullable=False,
        doc="Identifies the occurrence, not the row: the same occurrence appended twice is one "
            "event.")
    payload: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False, default=dict, server_default="{}",
        doc="Short, verifiable facts about the moment. Never a prompt, a completion or a model's "
            "private reasoning.")

    task_run: Mapped[TaskRun] = relationship(back_populates="events")


class ToolRequest(TimestampedEntity, Base):
    """A tool an agent asked for. **Nothing here executes it.**

    The row is the whole of Gate 2's answer to a tool call: persist it, record the event, and put
    the run to sleep until something authorised answers. ``tool_name`` is data — it is never
    resolved to a command, a path or an executable — and ``arguments`` is an opaque object this
    Gate stores and hands back without reading.
    """

    __tablename__ = "tool_requests"
    __table_args__ = (
        CheckConstraint("status IN " + _vocabulary(TOOL_REQUEST_STATUSES),
                        name="status_is_known"),
        Index("ix_tool_requests_task_run_id_created_at", "task_run_id", "created_at"),
    )

    task_run_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("task_runs.id", ondelete="CASCADE"), nullable=False)
    agent_run_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("agent_runs.id", ondelete="SET NULL"), index=True)
    tool_name: Mapped[str] = mapped_column(String(128), nullable=False)
    arguments: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False, default=dict, server_default="{}")
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, default="PENDING", server_default="PENDING")
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    task_run: Mapped[TaskRun] = relationship(back_populates="tool_requests")
    result: Mapped[ToolResult | None] = relationship(
        back_populates="request", cascade="all, delete-orphan", uselist=False)


class ToolResult(ImmutableRecord, Base):
    """The answer to one tool request, append-only and at most one per request.

    The uniqueness constraint is the idempotency mechanism rather than a nicety: the same result
    delivered twice — a retried HTTP call, a redelivered signal — must resolve the request once and
    resume the run once. A rule enforced by the database cannot be forgotten by a code path.
    """

    __tablename__ = "tool_results"
    __table_args__ = (
        CheckConstraint("status IN " + _vocabulary(TOOL_RESULT_STATUSES), name="status_is_known"),
        UniqueConstraint("tool_request_id", name="tool_request_id"),
    )

    tool_request_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tool_requests.id", ondelete="CASCADE"), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    output: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False, default=dict, server_default="{}")
    error: Mapped[str | None] = mapped_column(Text)
    result_metadata: Mapped[dict[str, Any]] = mapped_column(
        "result_metadata", JSONB, nullable=False, default=dict, server_default="{}",
        doc="Whatever the executor wants to record about the execution. Opaque to this Gate.")

    request: Mapped[ToolRequest] = relationship(back_populates="result")


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
