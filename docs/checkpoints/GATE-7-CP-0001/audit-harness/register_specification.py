"""Register only the newly authored canonical specification; preserve every predecessor row."""

from __future__ import annotations

import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))

from ledger_common import load_json, write_json
from policies import parse_checklist


def main() -> int:
    state = load_json(CHECKPOINT / "STATE.json")
    gate = state["gate"]
    specification = f"docs/{gate}-CHECKLIST.md"
    path = ROOT / ".iacode/policies/canonical-requirements.json"
    registry = load_json(path)
    if any(entry["gate"] == gate for entry in registry["gates"]):
        raise ValueError("already registered; refuse overwriting canonical rows")
    rows = parse_checklist((ROOT / specification).read_text(encoding="utf-8"))
    if not rows:
        raise ValueError("no canonical requirements parsed")
    registry["gates"].append(
        {"gate": gate, "specification": specification,
         "requirements": [{**row, "mandatory": True} for row in rows]}
    )
    write_json(path, registry)
    print(f"SPECIFICATION_REGISTERED gate={gate} requirements={len(rows)} predecessors=unchanged")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
