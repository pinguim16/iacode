"""Mechanically register the authored Gate 6 checklist without changing earlier rows."""

from __future__ import annotations

import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))

from ledger_common import load_json, write_json
from policies import parse_checklist


def main() -> int:
    registry_path = ROOT / ".iacode/policies/canonical-requirements.json"
    registry = load_json(registry_path)
    gate = "GATE-6"
    specification = "docs/GATE-6-CHECKLIST.md"
    if any(row["gate"] == gate for row in registry["gates"]):
        raise ValueError("the new Gate specification is already registered; do not overwrite it")
    rows = parse_checklist((ROOT / specification).read_text(encoding="utf-8"))
    if not rows:
        raise ValueError("the canonical checklist must contain actual requirement rows")
    registry["gates"].append({"gate": gate, "specification": specification,
                              "requirements": [{**row, "mandatory": True} for row in rows]})
    write_json(registry_path, registry)
    print(f"GATE_SPECIFICATION_REGISTERED gate={gate} requirements={len(rows)} predecessors=unchanged")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
