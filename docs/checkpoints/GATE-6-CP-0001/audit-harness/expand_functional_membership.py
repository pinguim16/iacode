"""Mechanically expose every already-mandatory runtime row to functional acceptance.

This widens evidence membership only. It never changes a criterion, mandatory flag, historical
Gate, lesson or acceptance result. The complete verifier, not this transformer, must prove it.
"""

from __future__ import annotations

import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))

from check_functional_acceptance import functional_requirement_ids
from ledger_common import load_json, write_json
from policies import parse_checklist


def main() -> int:
    path = ROOT / "docs/GATE-6-CHECKLIST.md"
    registry_path = ROOT / ".iacode/policies/canonical-requirements.json"
    original = path.read_text(encoding="utf-8")
    before_rows = parse_checklist(original)
    old_members = set(functional_requirement_ids(ROOT, "GATE-6"))
    expected = {row["key"] for row in before_rows if 2 <= int(row["key"].split(".")[0]) <= 7}
    if len(before_rows) != 51 or len(expected) != 37:
        raise ValueError("canonical specification changed; review rather than selecting a subset")
    lines = []
    for line in original.splitlines():
        parts = line.split("|")
        if len(parts) == 6 and parts[1].strip() in expected:
            if "FUNCTIONAL-ACCEPTANCE.json" not in parts[4]:
                parts[4] = " FUNCTIONAL-ACCEPTANCE.json; " + parts[4].strip() + " "
            line = "|".join(parts)
        lines.append(line)
    changed = "\n".join(lines) + "\n"
    after_rows = parse_checklist(changed)
    registry = load_json(registry_path)
    current = next(row for row in registry["gates"] if row["gate"] == "GATE-6")
    for old, new, registered in zip(before_rows, after_rows, current["requirements"], strict=True):
        for key in ("key", "description", "artifact"):
            if old[key] != new[key] or registered[key] != old[key]:
                raise ValueError("the transformation may not change any requirement or artifact")
        if not registered["mandatory"]:
            raise ValueError("every original mandatory criterion must remain mandatory")
        registered["evidence"] = new["evidence"]
    path.write_text(changed, encoding="utf-8", newline="\n")
    write_json(registry_path, registry)
    new_members = set(functional_requirement_ids(ROOT, "GATE-6"))
    if not old_members <= new_members or new_members != {"GATE-6-" + key for key in expected}:
        raise ValueError("functional membership must widen to the complete runtime criterion set")
    print(f"FUNCTIONAL_MEMBERSHIP_WIDENED previous={len(old_members)} current={len(new_members)} "
          "criteria=51 predecessors=unchanged acceptance=NOT_ISSUED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
