"""Execute the owning exact structural assertions with clean and adverse ORM metadata."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from tests.unit import test_domain_model as contract


def test_exact_table_inventory_refuses_each_missing_and_extra_table(monkeypatch):
    contract.test_structural_tables_exist()
    actual = dict(contract.Base.metadata.tables)
    for name in contract.KNOWLEDGE_TABLES:
        with monkeypatch.context() as mutation:
            mutation.setattr(
                contract,
                "Base",
                SimpleNamespace(
                    metadata=SimpleNamespace(
                        tables={key: value for key, value in actual.items() if key != name}
                    )
                ),
            )
            with pytest.raises(AssertionError):
                contract.test_structural_tables_exist()
    with monkeypatch.context() as mutation:
        mutation.setattr(
            contract,
            "Base",
            SimpleNamespace(
                metadata=SimpleNamespace(tables={**actual, "unauthorized_shadow": object()})
            ),
        )
        with pytest.raises(AssertionError):
            contract.test_structural_tables_exist()


def test_fact_lifecycle_classification_refuses_each_wrong_knowledge_role(monkeypatch):
    contract.test_common_columns_follow_the_convention()
    contract.test_the_two_base_classes_are_used_deliberately()
    for name in contract.KNOWLEDGE_TABLES:
        with monkeypatch.context() as mutation:
            changed = contract.APPEND_ONLY ^ {name}
            mutation.setattr(contract, "APPEND_ONLY", changed)
            with pytest.raises(AssertionError):
                contract.test_common_columns_follow_the_convention()
            if name == "knowledge_documents":
                with pytest.raises(AssertionError):
                    contract.test_the_two_base_classes_are_used_deliberately()


def test_actual_foreign_key_contract_refuses_each_changed_knowledge_cascade(monkeypatch):
    contract.test_relationships_cascade_deliberately()
    for name in contract.KNOWLEDGE_TABLES:
        keys = contract.Base.metadata.tables[name].foreign_key_constraints
        assert len(keys) == 1
        key = next(iter(keys))
        with monkeypatch.context() as mutation:
            mutation.setattr(key, "ondelete", "SET NULL")
            with pytest.raises(AssertionError):
                contract.test_relationships_cascade_deliberately()
