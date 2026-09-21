#!/usr/bin/env python3
"""Derive the expected requirement set of the subject independently of the product tooling.

Nothing here imports ``policies.py``. The checklist, the audit registry, the sealed audit reports
and the preflight are parsed again with this module's own readers, so agreeing with the delivery
means two independent derivations agreed, not that one function was called twice.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

CHECKLIST_ROW = re.compile(
    r"^\|\s*(?P<key>[0-9]+[a-z]?\.[0-9]+)\s*\|\s*(?P<description>.+?)\s*\|"
    r"\s*(?P<artifact>.+?)\s*\|\s*(?P<evidence>.+?)\s*\|\s*$")
FINDING_HEADING = re.compile(r"^###\s+(?P<id>[A-Z0-9]+-F-[0-9]{3})\s*[-—]\s*(?P<rest>.+?)\s*$")
WIDE_ATTACK = re.compile(
    r"^\|\s*`?(?P<id>[A-Z]{1,2})`?\s*\|\s*(?P<target>.+?)\s*\|\s*(?P<mutation>.+?)\s*\|"
    r"\s*(?P<expected>.+?)\s*\|\s*(?P<observed>.+?)\s*\|\s*`?(?P<result>DEFENDED|ESCAPED)`?"
    r"\s*\|(?:\s*(?P<evidence>.+?)\s*\|)?\s*$")
NARROW_ATTACK = re.compile(
    r"^\|\s*`?(?P<id>[A-Z]{1,2})`?\s*\|\s*(?P<mutation>.+?)\s*\|\s*(?P<expected>.+?)\s*\|"
    r"\s*(?P<observed>.+?)\s*\|\s*`?(?P<result>DEFENDED|ESCAPED)`?\s*\|\s*$")
ADDITIONAL_HEADING = re.compile(r"^#{2,4}\s+.*\badditional\b", re.IGNORECASE)
HEADING = re.compile(r"^#{2,4}\s+")


def checklist_keys(path: Path) -> list[dict[str, str]]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        match = CHECKLIST_ROW.match(line)
        if match and match.group("key") != "#":
            rows.append({
                "key": match.group("key"),
                "description": match.group("description").strip(),
            })
    return rows


def findings(path: Path) -> list[str]:
    return [FINDING_HEADING.match(line).group("id")
            for line in path.read_text(encoding="utf-8").splitlines()
            if FINDING_HEADING.match(line)]


def attacks(path: Path) -> dict[str, list[str]]:
    """Mandatory and additional attack identifiers, decided by the section a row sits under."""
    mandatory: list[str] = []
    additional: list[str] = []
    seen: set[str] = set()
    in_additional = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if HEADING.match(line):
            in_additional = bool(ADDITIONAL_HEADING.match(line))
            continue
        wide = WIDE_ATTACK.match(line)
        narrow = NARROW_ATTACK.match(line)
        match = wide or narrow
        if not match:
            continue
        identifier = match.group("id")
        if identifier in seen:
            continue
        seen.add(identifier)
        if in_additional or (narrow and not wide):
            additional.append(identifier)
        else:
            mandatory.append(identifier)
    return {"mandatory": mandatory, "additional": additional}


def expected(root: Path, checkpoint: Path) -> dict[str, dict]:
    state = json.loads((checkpoint / "STATE.json").read_text(encoding="utf-8"))
    gate = state["gate"]

    registry = json.loads(
        (root / ".iacode" / "policies" / "canonical-requirements.json").read_text(encoding="utf-8"))
    entry = next(item for item in registry["gates"] if item["gate"] == gate)
    specification = root / entry["specification"]
    parsed = checklist_keys(specification)
    declared = [dict(item) for item in entry["requirements"]]

    mirror_errors = []
    if [row["key"] for row in parsed] != [str(item["key"]) for item in declared]:
        mirror_errors.append(
            f"canonical-requirements.json does not mirror {entry['specification']}")
    for row, item in zip(parsed, declared):
        if row["description"] != item.get("description"):
            mirror_errors.append(f"canonical requirement {gate}#{row['key']} does not mirror")

    result: dict[str, dict] = {}
    for row in parsed:
        result[f"canonical:{gate}#{row['key']}"] = {"source": "SETUP"}

    preflight_path = checkpoint / "LESSON-PREFLIGHT.json"
    if preflight_path.is_file():
        preflight = json.loads(preflight_path.read_text(encoding="utf-8"))
        for derived in preflight.get("derivedRequirements") or []:
            if derived.get("lessonId"):
                result[f"lesson:{derived['lessonId']}"] = {"source": "LESSON"}

    audits = json.loads(
        (root / ".iacode" / "policies" / "audit-registry.json").read_text(encoding="utf-8"))
    open_audits = [
        audit for audit in audits["audits"]
        if audit.get("gate") == gate and audit.get("correctiveCheckpoint") == checkpoint.name]
    battery: dict[str, dict[str, list[str]]] = {}
    for audit in open_audits:
        for identifier in findings(root / audit["reviewReport"]):
            result[f"finding:{identifier}"] = {"source": "AUDIT_FINDING"}
        parsed_attacks = attacks(root / audit["redTeamReport"])
        battery[audit["auditId"]] = parsed_attacks
        for identifier in parsed_attacks["mandatory"]:
            result[f"attack:{identifier}"] = {"source": "AUDIT_ATTACK"}

    return {
        "gate": gate,
        "checkpoint": checkpoint.name,
        "checklistRows": len(parsed),
        "mirrorErrors": mirror_errors,
        "openAudits": [audit["auditId"] for audit in open_audits],
        "battery": battery,
        "expected": result,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()
    root = args.root.resolve()
    checkpoint = root / "docs" / "checkpoints" / args.checkpoint
    derivation = expected(root, checkpoint)

    matrix = json.loads((checkpoint / "REQUIREMENTS-MATRIX.json").read_text(encoding="utf-8"))
    declared = {item["sourceRef"] for item in matrix["requirements"]}
    expected_refs = set(derivation["expected"])
    report = {
        "gate": derivation["gate"],
        "checkpoint": derivation["checkpoint"],
        "checklistRows": derivation["checklistRows"],
        "mirrorErrors": derivation["mirrorErrors"],
        "openAudits": derivation["openAudits"],
        "battery": {
            key: {"mandatory": len(value["mandatory"]), "additional": len(value["additional"])}
            for key, value in derivation["battery"].items()},
        "expectedTotal": len(expected_refs),
        "declaredTotal": len(declared),
        "declaredRows": len(matrix["requirements"]),
        "missingFromDelivery": sorted(expected_refs - declared),
        "extraInDelivery": sorted(declared - expected_refs),
        "bySource": {
            source: sum(1 for item in derivation["expected"].values() if item["source"] == source)
            for source in ("SETUP", "LESSON", "AUDIT_FINDING", "AUDIT_ATTACK")},
        "agrees": (expected_refs == declared and not derivation["mirrorErrors"]
                   and len(declared) == len(matrix["requirements"])),
    }
    text = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.out:
        args.out.write_text(text, encoding="utf-8", newline="\n")
    print(text)
    return 0 if report["agrees"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
