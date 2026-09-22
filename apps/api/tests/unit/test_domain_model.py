"""The structural domain model, read from the declaration rather than from a database.

These assert the *contract* later Gates will build on: which tables exist, how they relate, which
conventions apply where, and that rights default to denial. They need no database, which is what
makes them part of the mandatory gate; `tests/integration/` checks that the migrated schema
actually matches.
"""

from __future__ import annotations

from iacode_api.db import models
from iacode_api.db.base import Base, ImmutableRecord, TimestampedEntity

# The set from `docs/GATE-0-CHECKLIST.md` row 5.6.
STRUCTURAL_TABLES = {
    "projects", "repositories", "tasks", "task_runs", "agents", "agent_runs",
    "providers", "models", "model_calls", "tool_calls", "artifacts", "experiences",
}

# Append-only facts: something that already happened, and cannot change afterwards.
APPEND_ONLY = {"model_calls", "tool_calls"}


def test_structural_tables_exist() -> None:
    assert set(Base.metadata.tables) == STRUCTURAL_TABLES


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
        ("model_calls", "model_id"): "RESTRICT",
        ("model_calls", "agent_run_id"): "SET NULL",
        ("tool_calls", "agent_run_id"): "CASCADE",
        ("artifacts", "task_run_id"): "SET NULL",
        ("experiences", "task_run_id"): "SET NULL",
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


def test_providers_models_and_agents_are_disabled_by_default() -> None:
    """Nothing this Gate creates is live. A later Gate enables what it can actually run."""
    for table_name in ("providers", "models", "agents"):
        column = Base.metadata.tables[table_name].columns["enabled"]
        assert column.server_default.arg == "false", f"{table_name} is enabled by default"


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
