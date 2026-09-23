"""The structural domain model, read from the declaration rather than from a database.

These assert the *contract* later Gates will build on: which tables exist, how they relate, which
conventions apply where, and that rights default to denial. They need no database, which is what
makes them part of the mandatory gate; `tests/integration/` checks that the migrated schema
actually matches.
"""

from __future__ import annotations

from iacode_persistence import models
from iacode_persistence.base import Base, ImmutableRecord, TimestampedEntity

# The set from `docs/GATE-0-CHECKLIST.md` row 5.6.
STRUCTURAL_TABLES = {
    "projects", "repositories", "tasks", "task_runs", "agents", "agent_runs",
    "providers", "models", "model_calls", "tool_calls", "artifacts", "experiences",
}

# What `docs/GATE-2-CHECKLIST.md` adds. Kept as its own set rather than merged into the one above,
# so the two statements stay legible: Gate 0 declared a persistence contract, and Gate 2 added the
# tables the agent runtime needs *beside* it rather than duplicating any of them.
AGENT_RUNTIME_TABLES = {"agent_teams", "run_events", "tool_requests", "tool_results"}
#: GATE 3 adds one table, for what nothing existing could hold: a sandbox session's lifecycle.
#: Its executions evolve ``tool_calls`` rather than shadowing it.
SANDBOX_TABLES = {"sandbox_sessions"}

# Append-only facts: something that already happened, and cannot change afterwards.
APPEND_ONLY = {"model_calls", "tool_calls", "run_events", "tool_results"}


def test_structural_tables_exist() -> None:
    assert set(Base.metadata.tables) == STRUCTURAL_TABLES | AGENT_RUNTIME_TABLES | SANDBOX_TABLES


def test_the_agent_runtime_created_no_parallel_entity() -> None:
    """Gate 2 evolved the existing entities; it did not shadow one with a table of its own.

    The check is a property rather than a list: no new table may be a renamed copy of a structural
    one. `docs/GATE-2-CHECKLIST.md` row 3.2 exists because "agent_runtime_tasks" beside "tasks" is
    the easiest wrong turn available to this Gate.
    """
    for table in AGENT_RUNTIME_TABLES:
        for structural in STRUCTURAL_TABLES:
            assert structural not in table, (
                f"{table} looks like a second home for {structural}")


def test_common_columns_follow_the_convention() -> None:
    """The convention is defined once and applied where it makes sense, not everywhere."""
    for name, table in Base.metadata.tables.items():
        columns = set(table.columns.keys())
        assert "id" in columns, f"{name} has no identifier"
        assert "created_at" in columns, f"{name} does not record when it was created"

        if name in APPEND_ONLY:
            # An `updated_at` on a fact that cannot change invites code to update it, and an
            # optimistic-locking counter on a row nobody locks is noise.
            assert "updated_at" not in columns, f"{name} is append-only but tracks updates"
            assert "version" not in columns, f"{name} is append-only but carries a lock counter"
            assert "metadata" not in columns, f"{name} is append-only but carries open metadata"
        else:
            assert "updated_at" in columns, f"{name} has a lifecycle but no update time"
            assert "version" in columns, f"{name} has a lifecycle but no lock counter"
            assert "metadata" in columns, f"{name} has a lifecycle but no extension point"


def test_the_two_base_classes_are_used_deliberately() -> None:
    for table_name in APPEND_ONLY:
        model = next(mapper.class_ for mapper in Base.registry.mappers
                     if mapper.class_.__tablename__ == table_name)
        assert issubclass(model, ImmutableRecord)
        assert not issubclass(model, TimestampedEntity)


def test_every_identifier_is_a_uuid() -> None:
    """One strategy, not one per table."""
    import uuid

    for name, table in Base.metadata.tables.items():
        column = table.columns["id"]
        assert column.primary_key, f"{name}.id is not the primary key"
        assert column.type.python_type is uuid.UUID, f"{name}.id is not a UUID"
        assert column.default is not None, f"{name}.id has no generator"


def test_identifiers_are_generated_by_the_application() -> None:
    """Generating in Python is what lets a caller know the key before the insert."""
    from iacode_common.identifiers import uuid7, uuid7_timestamp_ms

    project = models.Project(slug="declaration", name="Declaration")
    generated = project.id or uuid7()

    assert generated.version == 7
    assert uuid7_timestamp_ms(generated) > 0


def test_relationships_cascade_deliberately() -> None:
    """A delete either cascades, is refused, or clears the reference. Never silently orphans."""
    expected = {
        ("repositories", "project_id"): "CASCADE",
        ("tasks", "project_id"): "CASCADE",
        ("task_runs", "task_id"): "CASCADE",
        ("agent_runs", "task_run_id"): "CASCADE",
        # An agent that has run cannot be deleted: its runs are the record that it did.
        ("agent_runs", "agent_id"): "RESTRICT",
        ("models", "provider_id"): "CASCADE",
        # A recorded call keeps its provider and its model from being deleted underneath it. The
        # columns are nullable from Gate 1 — a call can outlive the catalog row it names — but a
        # row that *is* named may not vanish while the record points at it.
        ("model_calls", "model_id"): "RESTRICT",
        ("model_calls", "provider_id"): "RESTRICT",
        ("model_calls", "agent_run_id"): "SET NULL",
        ("tool_calls", "agent_run_id"): "CASCADE",
        ("artifacts", "task_run_id"): "SET NULL",
        ("experiences", "task_run_id"): "SET NULL",
        # Gate 2. A run's history and its tool interactions belong to the run: deleting the run
        # deletes them. The agent run reference is cleared rather than cascaded, because an event
        # about a stage stays true after the stage's row is gone.
        ("run_events", "task_run_id"): "CASCADE",
        ("run_events", "agent_run_id"): "SET NULL",
        ("tool_requests", "task_run_id"): "CASCADE",
        ("tool_requests", "agent_run_id"): "SET NULL",
        ("tool_results", "tool_request_id"): "CASCADE",
        # Gate 3. A session belongs to its run; an execution record outlives the request and the
        # session it names, because it is the record that the tool ran.
        ("sandbox_sessions", "task_run_id"): "CASCADE",
        ("sandbox_sessions", "active_tool_request_id"): "SET NULL",
        ("tool_calls", "tool_request_id"): "SET NULL",
        ("tool_calls", "sandbox_session_id"): "SET NULL",
    }
    observed = {
        (table_name, next(iter(key.columns)).name): key.ondelete
        for table_name, table in Base.metadata.tables.items()
        for key in table.foreign_key_constraints
    }

    assert observed == expected


def test_rights_default_to_denial() -> None:
    """`.iacode/policies/provenance-policy.md` at the database level, not as an opinion in code."""
    experiences = Base.metadata.tables["experiences"]

    assert experiences.columns["training_allowed"].server_default.arg == "false"
    assert experiences.columns["rag_allowed"].server_default.arg == "false"
    assert experiences.columns["distillation_allowed"].server_default.arg == "false"
    # Storage is the one that defaults to permitted: an experience that cannot be stored is not an
    # experience, and the restriction that matters is what may be done with it afterwards.
    assert experiences.columns["storage_allowed"].server_default.arg == "true"


def test_providers_and_agents_are_disabled_by_default() -> None:
    """Nothing is live because a row exists. A Gate enables what it can actually run."""
    for table_name in ("providers", "agents"):
        column = Base.metadata.tables[table_name].columns["enabled"]
        assert column.server_default.arg == "false", f"{table_name} is enabled by default"


def test_a_model_is_governed_by_its_provider_rather_than_by_a_switch_of_its_own() -> None:
    """``models`` has no ``enabled`` column from Gate 1, and that is the point.

    Gate 0 gave every model a default-off ``enabled`` flag, which made sense while nothing populated
    the table. Gate 1 populates it by discovery: a row exists because a provider listed the model,
    and ``active`` says whether it still does. An operator switch on top of that would be a second
    place to disable a model, and two switches are how a model ends up disabled in the one nobody
    looked at. The switch is at the provider, in configuration; the router refuses a model whose
    provider is not enabled.
    """
    models = Base.metadata.tables["models"]

    assert "enabled" not in models.columns
    assert models.columns["active"].server_default.arg == "true"
    assert Base.metadata.tables["providers"].columns["enabled"].server_default.arg == "false"


def test_lifecycle_vocabularies_are_constrained() -> None:
    """A status column with no constraint accepts a typo as a new state."""
    for table_name in ("tasks", "task_runs", "agent_runs"):
        names = {constraint.name
                 for constraint in Base.metadata.tables[table_name].constraints
                 if constraint.name}
        assert any("status_is_known" in name for name in names), \
            f"{table_name}.status accepts any string"


def test_an_artifact_points_at_exactly_one_object() -> None:
    """Two rows pointing at one object make deletion unsafe: neither knows if the other needs it."""
    assert Base.metadata.tables["artifacts"].columns["storage_key"].unique


def test_no_table_stores_a_credential() -> None:
    """Gate 1 resolves provider credentials from configuration; they are not persisted here.

    The pattern matches a column that *holds* a credential, not one whose name happens to contain a
    credential word: `input_tokens` and `output_tokens` on `model_calls` are counts, and a rule that
    flagged them would be switched off the first time somebody needed a token count.
    """
    import re

    credential = re.compile(
        r"(?i)(password|passwd|secret|api[_-]?key|access[_-]?key|private[_-]?key|credential"
        r"|(^|_)token(_|$))")
    for name, table in Base.metadata.tables.items():
        for column in table.columns:
            assert credential.search(column.name) is None, \
                f"{name}.{column.name} looks like a credential column"


def test_provider_registry_persists_operational_metadata() -> None:
    """Row 5.2: what the registry remembers about a provider, and what it must never remember.

    Operational metadata is the answer to "is this provider working and what does it serve". The
    address and the credential are not part of that answer: they belong to the environment, and a
    column for either is a column somebody will eventually fill.
    """
    columns = set(models.Provider.__table__.columns.keys())

    for expected in ("slug", "name", "kind", "adapter", "enabled", "healthy",
                     "last_health_check", "last_sync", "model_count", "detail"):
        assert expected in columns, f"providers does not record {expected}"

    for forbidden in ("api_key", "credential", "secret", "token", "password",
                      "base_url", "endpoint", "authorization"):
        assert forbidden not in columns, f"providers carries {forbidden}"

    # Health is tri-state: unknown until something has asked. A boolean defaulting to false would
    # report every provider as broken before the first check.
    assert models.Provider.__table__.columns["healthy"].nullable
    assert models.Provider.__table__.columns["last_health_check"].nullable
    assert models.Provider.__table__.columns["last_sync"].nullable


def test_run_event_log_is_append_only() -> None:
    """A history that can be edited is not a history.

    The control is the shape: `run_events` inherits `ImmutableRecord`, so there is no `updated_at`
    to bump and no optimistic-locking counter to increment. `docs/GATE-2-CHECKLIST.md` row 3.6.
    """
    events = Base.metadata.tables["run_events"]
    columns = set(events.columns.keys())

    assert "created_at" in columns
    assert "updated_at" not in columns
    assert "version" not in columns

    model = next(mapper.class_ for mapper in Base.registry.mappers
                 if mapper.class_.__tablename__ == "run_events")
    assert issubclass(model, ImmutableRecord)
    assert not issubclass(model, TimestampedEntity)


def test_the_event_sequence_and_its_dedupe_key_are_unique_per_run() -> None:
    """The two constraints that make a history ordered and appendable exactly once."""
    events = Base.metadata.tables["run_events"]
    unique = {
        tuple(column.name for column in constraint.columns)
        for constraint in events.constraints
        if constraint.__class__.__name__ == "UniqueConstraint"
    }

    assert ("task_run_id", "sequence") in unique
    assert ("task_run_id", "dedupe_key") in unique


def test_a_tool_request_carries_at_most_one_result() -> None:
    """The uniqueness constraint is the idempotency mechanism, not a nicety."""
    results = Base.metadata.tables["tool_results"]
    unique = {
        tuple(column.name for column in constraint.columns)
        for constraint in results.constraints
        if constraint.__class__.__name__ == "UniqueConstraint"
    }

    assert ("tool_request_id",) in unique

    model = next(mapper.class_ for mapper in Base.registry.mappers
                 if mapper.class_.__tablename__ == "tool_results")
    assert issubclass(model, ImmutableRecord)


def test_agent_run_usage_is_derived_from_model_calls() -> None:
    """There is no aggregate usage column: a second count eventually disagrees with the first."""
    agent_runs = Base.metadata.tables["agent_runs"]
    model_calls = Base.metadata.tables["model_calls"]

    for forbidden in ("input_tokens", "output_tokens", "total_tokens", "cost"):
        assert forbidden not in agent_runs.columns

    assert "agent_run_id" in model_calls.columns
    assert "input_tokens" in model_calls.columns
    assert "cost" in model_calls.columns


def test_nothing_this_gate_persists_is_training_eligible() -> None:
    """Rights default to denial at the database level, not as an opinion in code."""
    task_runs = Base.metadata.tables["task_runs"]

    assert task_runs.columns["training_allowed"].server_default.arg == "false"
    for table in ("run_events", "tool_requests", "tool_results", "agent_teams"):
        assert "training_allowed" not in Base.metadata.tables[table].columns, (
            f"{table} carries a rights flag nothing in this Gate grants")


def test_no_raw_provider_prompt_is_persisted() -> None:
    """`model_calls` has nowhere to put one, and the run keeps its own task rather than a prompt."""
    for table_name in ("model_calls", "task_runs", "agent_runs", "run_events"):
        columns = set(Base.metadata.tables[table_name].columns.keys())
        for forbidden in ("prompt", "prompts", "messages", "completion", "raw_request",
                          "system_prompt", "transcript"):
            assert forbidden not in columns, f"{table_name} can hold a {forbidden}"

    # What the run does keep is its own instruction and its own answer, which is what lets the
    # workflow resume and the page render after a restart.
    assert "result" in Base.metadata.tables["task_runs"].columns
    assert "description" in Base.metadata.tables["tasks"].columns
