"""Read the canonical delivery policy from the operational tooling.

The mandatory gate set belongs to `.iacode/policies/quality-gates.json`, and the development-ledger
tooling under `scripts/development-ledger/` is what reads it. The verification command needs the
same answer, and there are only two ways to get it: import that reader, or keep a second copy.

A second copy is how the verification stops covering a gate the registry grew — the exact failure
class `.iacode/memory/lessons.jsonl` records for the Green Keeper's own gate set. So this module
imports the real reader and adapts it, and the adaptation is one function wide.

It is a separate module rather than an import inside `verify.py` because the import needs a
``sys.path`` entry that nothing else in this package wants.
"""

from __future__ import annotations

import sys
from pathlib import Path

LEDGER_TOOLING = Path(__file__).resolve().parents[1] / "development-ledger"


def _policies_module():
    if str(LEDGER_TOOLING) not in sys.path:
        sys.path.insert(0, str(LEDGER_TOOLING))
    import policies

    return policies


def mandatory_gate_commands(root: Path) -> list[tuple[str, list[str]]]:
    """Every mandatory gate, as ``(identifier, command)``, in the order policy declares them."""
    policies = _policies_module()
    definitions = policies.gate_definitions(root)
    return [
        (identifier, [str(item) for item in definitions[identifier]["command"]])
        for identifier in policies.mandatory_gates(root)
    ]
