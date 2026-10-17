"""Carry published partial local proofs into the owning closure source before re-derivation."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))
from check_functional_acceptance import functional_requirement_ids
from derive_requirements import build, render_closure, render_matrix
from ledger_common import load_json, write_json


def main() -> int:
    subject = "127926d4922e8e63e51fd64681fbe1cd04f21800"
    reference = CHECKPOINT.relative_to(ROOT).as_posix() + "/REQUIREMENTS-MATRIX.json"
    prior = json.loads(subprocess.check_output(["git", "show", subject + ":" + reference], cwd=ROOT))
    partial = {row["sourceRef"]: row for row in prior["requirements"] if row["status"] == "PARTIAL"}
    expected = {"canonical:GATE-6#" + key.removeprefix("GATE-6-")
                for key in functional_requirement_ids(ROOT, "GATE-6")}
    if set(partial) != expected:
        raise ValueError("published local partial proof set differs from canonical runtime criteria")
    closure = load_json(CHECKPOINT / "CLOSURE-REQUIREMENTS.json")
    before = {row["sourceRef"] for row in closure["requirements"]}
    for row in closure["requirements"]:
        previous = partial.get(row["sourceRef"])
        if previous is None:
            continue
        if row["finalStatus"] not in {"NOT_STARTED", "PARTIAL"}:
            raise ValueError("refusing to overwrite a different requirement verdict")
        if row["description"] != previous["description"] or row["mandatory"] != previous["mandatory"]:
            raise ValueError("canonical criterion changed; manual evidence reconciliation required")
        row["implementationStatus"] = "PARTIAL"
        row["finalStatus"] = "PARTIAL"
        for field in ("implementationEvidence", "testEvidence", "documentationEvidence",
                      "validationEvidence"):
            row[field] = list(previous[field])
        row["notes"] = previous["notes"]
    write_json(CHECKPOINT / "CLOSURE-REQUIREMENTS.json", closure)
    closure, matrix = build(ROOT, CHECKPOINT, "GATE-6")
    if {row["sourceRef"] for row in closure["requirements"]} != before:
        raise ValueError("canonical requirement membership changed unexpectedly")
    write_json(CHECKPOINT / "CLOSURE-REQUIREMENTS.json", closure)
    write_json(CHECKPOINT / "REQUIREMENTS-MATRIX.json", matrix)
    (CHECKPOINT / "CLOSURE-REQUIREMENTS.md").write_text(render_closure(closure), encoding="utf-8", newline="\n")
    (CHECKPOINT / "REQUIREMENTS-MATRIX.md").write_text(render_matrix(matrix), encoding="utf-8", newline="\n")
    print(f"LOCAL_PROOFS_RETAINED partial={len(partial)} total={len(before)} complete=0 no_gate_verdict=true")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
