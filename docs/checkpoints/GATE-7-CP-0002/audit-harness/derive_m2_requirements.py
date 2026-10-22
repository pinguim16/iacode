"""Derive the accumulated M2 requirement denominator from canonical policy and lesson preflight."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


GATES = ("GATE-4", "GATE-5", "GATE-6", "GATE-7")


def _load_policies(root: Path) -> Any:
    module_root = root / "scripts" / "development-ledger"
    path = module_root / "policies.py"
    sys.path.insert(0, str(module_root))
    spec = importlib.util.spec_from_file_location("m2_audit_policies", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--checkpoint", type=Path, required=True)
    args = parser.parse_args()

    root = args.root.resolve()
    checkpoint = args.checkpoint.resolve()
    policies = _load_policies(root)
    rows: list[dict[str, Any]] = []
    sources: list[dict[str, Any]] = []

    for gate in GATES:
        requirements = policies.canonical_requirements(root, gate)
        specification = policies.gate_specification(root, gate)
        sources.append({
            "gate": gate,
            "path": specification,
            "sha256": _sha256(root / specification),
            "requirements": len(requirements),
        })
        for item in requirements:
            rows.append({
                "id": f"{gate}-{item['key']}",
                "kind": "GATE_SPECIFICATION",
                "gate": gate,
                "key": item["key"],
                "section": item["section"],
                "description": item["description"],
                "artifact": item["artifact"],
                "requiredEvidence": item["evidence"],
                "mandatory": bool(item.get("mandatory", True)),
                "source": f"{specification}#{item['key']}",
                "status": "NOT_AUDITED",
                "evidence": [],
            })

    preflight_path = checkpoint / "LESSON-PREFLIGHT.json"
    preflight = json.loads(preflight_path.read_text(encoding="utf-8"))
    lessons = preflight.get("derivedRequirements")
    if not isinstance(lessons, list):
        raise RuntimeError("lesson preflight has no derivedRequirements array")
    for item in lessons:
        rows.append({
            "id": item["id"],
            "kind": "LESSON",
            "lessonId": item["lessonId"],
            "description": item["description"],
            "requiredEvidence": item["requiredEvidence"],
            "mandatory": bool(item.get("mandatory", True)),
            "source": f".iacode/memory/lessons.jsonl#{item['lessonId']}",
            "status": "NOT_AUDITED",
            "evidence": [],
        })

    identifiers = [row["id"] for row in rows]
    if len(identifiers) != len(set(identifiers)):
        raise RuntimeError("derived M2 requirement identifiers are not unique")
    expected_gate = {"GATE-4": 105, "GATE-5": 50, "GATE-6": 51, "GATE-7": 48}
    actual_gate = {gate: sum(row.get("gate") == gate for row in rows) for gate in GATES}
    if actual_gate != expected_gate:
        raise RuntimeError(f"unexpected Gate denominator: {actual_gate!r}")
    if len(lessons) != 150 or len(rows) != 404:
        raise RuntimeError(f"unexpected M2 denominator: lessons={len(lessons)} total={len(rows)}")

    document = {
        "schemaVersion": "1.0.0",
        "artifact": "M2_AUDIT_REQUIREMENTS",
        "checkpoint": checkpoint.name,
        "milestone": "M2",
        "gates": list(GATES),
        "sources": sources + [{
            "path": str(preflight_path.relative_to(root)).replace("\\", "/"),
            "sha256": _sha256(preflight_path),
            "requirements": len(lessons),
        }],
        "counts": {
            "gateRequirements": sum(actual_gate.values()),
            "lessonRequirements": len(lessons),
            "total": len(rows),
            "mandatory": sum(bool(row["mandatory"]) for row in rows),
        },
        "requirements": rows,
    }
    output = checkpoint / "M2-AUDIT-REQUIREMENTS.json"
    output.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(
        "M2_AUDIT_REQUIREMENTS_DERIVED "
        f"gate=254 lessons={len(lessons)} total={len(rows)} output={output}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
