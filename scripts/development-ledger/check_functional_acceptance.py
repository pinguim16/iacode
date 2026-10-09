#!/usr/bin/env python3
"""Validate executed functional acceptance against the canonical Gate requirement set.

The mandatory functional denominator is derived from canonical requirement evidence text. A caller
may select a checkpoint, but cannot provide or narrow requirement identifiers. PASS is granted only
to executed scenarios whose evidence resolves and whose result is PASS; FAIL, BLOCKED and justified
NOT_APPLICABLE remain visible and never count as passing.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from ledger_common import (
    LedgerError,
    find_root,
    load_json,
    resolve_latest,
    utc_now,
    validate_schema,
)
from policies import canonical_requirements

FUNCTIONAL_MARKERS = (
    "FUNCTIONAL-ACCEPTANCE.json",
    "Recorded functional acceptance",
    "live sandbox proof",
    "live restart scenario",
    "Recorded recovery scenario",
    "live cancellation scenario",
    "live timeout scenario",
    "live reproduction report",
    "passing report",
    "failing report",
    "IACode report",
    "Reproduction report",
    "M2-INTERNAL-RED-TEAM.json",
)


def functional_requirement_ids(root: Path, gate: str) -> tuple[str, ...]:
    """Return the closed functional subset from canonical rows, never caller input."""
    selected: list[str] = []
    for row in canonical_requirements(root, gate):
        evidence = str(row.get("evidence") or "")
        if any(marker in evidence for marker in FUNCTIONAL_MARKERS):
            selected.append(f"{gate}-{row['key']}")
    if not selected:
        raise LedgerError(f"{gate} derives no mandatory functional requirements")
    return tuple(selected)


def _command_ids(checkpoint: Path) -> set[str]:
    commands: set[str] = set()
    path = checkpoint / "COMMANDS.jsonl"
    if not path.is_file():
        return commands
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError as error:
            raise LedgerError(f"{path.name}:{number} is not JSON: {error}") from error
        identifier = item.get("commandId") or item.get("id")
        if identifier:
            commands.add(str(identifier))
    return commands


def _reference_resolves(root: Path, checkpoint: Path, reference: str, commands: set[str]) -> bool:
    if reference.startswith("cmd-"):
        return reference in commands
    if reference.startswith("file:"):
        candidate = Path(reference.removeprefix("file:"))
        return (candidate if candidate.is_absolute() else root / candidate).is_file()
    if reference.startswith("checkpoint:"):
        candidate = Path(reference.removeprefix("checkpoint:"))
        return not candidate.is_absolute() and (checkpoint / candidate).is_file()
    if reference.startswith("quality-run:"):
        return len(reference.removeprefix("quality-run:")) >= 16
    return False


def evaluate(root: Path, checkpoint: Path, document: dict[str, Any]) -> dict[str, Any]:
    state = load_json(checkpoint / "STATE.json")
    gate = str(state["gate"])
    required = functional_requirement_ids(root, gate)
    commands = _command_ids(checkpoint)
    findings: list[dict[str, str]] = []
    covered: set[str] = set()
    seen_scenarios: set[str] = set()

    if document.get("gate") != gate or document.get("checkpoint") != checkpoint.name:
        findings.append(
            {"code": "SCOPE_MISMATCH", "detail": "artifact gate/checkpoint differs from STATE.json"}
        )
    for scenario in document.get("scenarios", []):
        scenario_id = str(scenario.get("scenarioId") or "<missing>")
        if scenario_id in seen_scenarios:
            findings.append({"code": "DUPLICATE_SCENARIO", "detail": scenario_id})
        seen_scenarios.add(scenario_id)
        unknown = sorted(set(scenario.get("requirementIds") or ()) - set(required))
        if unknown:
            findings.append(
                {"code": "NON_FUNCTIONAL_REQUIREMENT", "detail": f"{scenario_id}: {unknown}"}
            )
        evidence = [str(item) for item in scenario.get("evidence") or ()]
        unresolved = [
            item for item in evidence if not _reference_resolves(root, checkpoint, item, commands)
        ]
        if unresolved:
            findings.append(
                {"code": "UNRESOLVED_EVIDENCE", "detail": f"{scenario_id}: {unresolved}"}
            )
        if scenario.get("result") == "PASS" and not unresolved:
            covered.update(set(scenario.get("requirementIds") or ()) & set(required))

    missing = sorted(set(required) - covered)
    for requirement in missing:
        findings.append({"code": "FUNCTIONAL_REQUIREMENT_NOT_PASSED", "detail": requirement})
    result = "PASS" if not findings and document.get("status") == "PASS" else "FAIL"
    return {
        "schemaVersion": "1.0.0",
        "checkpoint": checkpoint.name,
        "gate": gate,
        "generatedAt": utc_now(),
        "result": result,
        "required": list(required),
        "covered": sorted(covered),
        "missing": missing,
        "coveragePercent": round(100.0 * len(covered) / len(required), 2),
        "findings": findings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path)
    parser.add_argument("--checkpoint", type=Path)
    parser.add_argument("--write", action="store_true")
    arguments = parser.parse_args()

    root = find_root(arguments.root) if arguments.root else find_root()
    checkpoint = arguments.checkpoint or resolve_latest(root)
    if not checkpoint.is_absolute():
        checkpoint = root / checkpoint
    artifact_path = checkpoint / "FUNCTIONAL-ACCEPTANCE.json"
    if not artifact_path.is_file():
        raise LedgerError(f"missing {artifact_path.relative_to(root)}")
    document = load_json(artifact_path)
    errors = validate_schema(
        document, load_json(root / ".iacode" / "schemas" / "functional-acceptance.schema.json")
    )
    if errors:
        for error in errors:
            print(f"- FUNCTIONAL_ACCEPTANCE_SCHEMA: {error}")
        return 2
    report = evaluate(root, checkpoint, document)
    if arguments.write:
        (checkpoint / "FUNCTIONAL-ACCEPTANCE-VALIDATION.json").write_text(
            json.dumps(report, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
            newline="\n",
        )
    print(
        "FUNCTIONAL_ACCEPTANCE="
        f"{report['result']} coverage={report['coveragePercent']:.2f} "
        f"covered={len(report['covered'])}/{len(report['required'])}"
    )
    for finding in report["findings"]:
        print(f"- {finding['code']}: {finding['detail']}")
    return 0 if report["result"] == "PASS" else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except LedgerError as error:
        print(f"LEDGER_ERROR: {error}")
        sys.exit(2)
