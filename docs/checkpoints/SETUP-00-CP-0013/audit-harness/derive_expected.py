#!/usr/bin/env python3
"""Derive the expected requirement set of a checkpoint without the product tooling.

Nothing here imports ``policies.py``. The canonical Gate checklist, the audit registry, the sealed
audit reports and the checkpoint's own preflight are parsed again with this module's own readers,
so agreeing with the delivery means two independent derivations agreed rather than that one
function was called twice.

The two document rules this module implements are the ones the reports themselves declare, not the
ones a function asserts:

``## Findings``
    An audit report re-confirms the findings of the audit before it, under a heading of its own and
    in the same ``###`` shape. Only the report's own ``## Findings`` section raises findings the
    corrective delivery receives. A first draft of this module ignored that boundary and derived
    six findings for ``SETUP-00-CP-0012`` where the sealed report raises one; the boundary is the
    document's, and reading it is part of reading the document correctly.

``Category``
    A battery table that carries a ``Category`` column states mandatory or additional per row.
    Older reports have no such column and mark the distinction with an ``additional`` section
    heading instead, so both are read.

    python derive_expected.py --checkpoint SETUP-00-CP-0012
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

HARNESS = Path(__file__).resolve().parent
ROOT = HARNESS.parents[3]

CHECKLIST_ROW = re.compile(
    r"^\|\s*(?P<key>[0-9]+[a-z]?\.[0-9]+)\s*\|\s*(?P<description>.+?)\s*\|"
    r"\s*(?P<artifact>.+?)\s*\|\s*(?P<evidence>.+?)\s*\|\s*$")
SECTION = re.compile(r"^(?P<hashes>#{1,6})\s+(?P<title>.+?)\s*$")
FINDING_HEADING = re.compile(
    r"^###\s+`?(?P<id>[A-Z0-9]+-F-[0-9]{3})`?\s*[-—]\s*(?P<rest>.+?)\s*$")
ATTACK_ID = re.compile(r"^[A-Z]{2,4}-[0-9]{2}$|^[A-Z]{1,2}$")
ADDITIONAL_HEADING = re.compile(r"\badditional\b", re.IGNORECASE)


def _cells(line: str) -> list[str]:
    body = line.strip()
    if not body.startswith("|"):
        return []
    body = body[1:]
    if body.endswith("|"):
        body = body[:-1]
    return [cell.strip() for cell in body.split("|")]


def checklist_keys(path: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        match = CHECKLIST_ROW.match(line)
        if match and match.group("key") != "#":
            rows.append({"key": match.group("key"),
                         "description": match.group("description").strip()})
    return rows


def report_findings(path: Path) -> list[str]:
    """Identifiers raised under the report's own ``## Findings`` section."""
    found: list[str] = []
    in_findings = False
    for line in path.read_text(encoding="utf-8").splitlines():
        heading = SECTION.match(line)
        if heading and len(heading.group("hashes")) <= 2:
            in_findings = heading.group("title").strip().strip("`").lower() == "findings"
            continue
        if not in_findings:
            continue
        match = FINDING_HEADING.match(line)
        if match and match.group("id") not in found:
            found.append(match.group("id"))
    return found


def report_attacks(path: Path) -> dict[str, list[str]]:
    """Mandatory and additional attack identifiers, by the table's own category column.

    When a table has no category column the section heading decides, which is how the two earlier
    sealed reports mark the distinction.
    """
    mandatory: list[str] = []
    additional: list[str] = []
    seen: set[str] = set()
    section_is_additional = False
    columns: list[str] | None = None
    for line in path.read_text(encoding="utf-8").splitlines():
        heading = SECTION.match(line)
        if heading:
            section_is_additional = bool(ADDITIONAL_HEADING.search(heading.group("title")))
            columns = None
            continue
        cells = _cells(line)
        if not cells:
            columns = None
            continue
        lowered = [cell.strip().strip("`").lower() for cell in cells]
        if "result" in lowered and not ATTACK_ID.match(cells[0].strip().strip("`")):
            columns = lowered
            continue
        if set("".join(lowered)) <= set("-: "):
            continue
        identifier = cells[0].strip().strip("`")
        if not ATTACK_ID.match(identifier) or identifier in seen:
            continue
        seen.add(identifier)
        is_additional = section_is_additional
        if columns and "category" in columns:
            index = columns.index("category")
            if index < len(cells):
                is_additional = cells[index].strip().strip("`").lower() != "mandatory"
        (additional if is_additional else mandatory).append(identifier)
    return {"mandatory": mandatory, "additional": additional}


def expected(checkpoint: str) -> dict:
    gate = checkpoint.rsplit("-CP-", 1)[0]
    directory = ROOT / "docs" / "checkpoints" / checkpoint
    refs: dict[str, str] = {}

    for row in checklist_keys(ROOT / "docs" / "SETUP-00-CHECKLIST.md"):
        refs[f"canonical:{gate}#{row['key']}"] = "SETUP"

    preflight_path = directory / "LESSON-PREFLIGHT.json"
    lessons: list[str] = []
    if preflight_path.is_file():
        preflight = json.loads(preflight_path.read_text(encoding="utf-8"))
        for derived in preflight.get("derivedRequirements") or []:
            identifier = derived.get("lessonId")
            if identifier:
                refs[f"lesson:{identifier}"] = "LESSON"
                lessons.append(identifier)

    registry = json.loads(
        (ROOT / ".iacode" / "policies" / "audit-registry.json").read_text(encoding="utf-8"))
    audits = [item for item in registry["audits"]
              if item.get("gate") == gate and item.get("correctiveCheckpoint") == checkpoint]
    findings: list[str] = []
    attacks: list[str] = []
    for audit in audits:
        for identifier in report_findings(ROOT / audit["reviewReport"]):
            refs[f"finding:{identifier}"] = "AUDIT_FINDING"
            findings.append(identifier)
        if audit.get("redTeamReport"):
            for identifier in report_attacks(ROOT / audit["redTeamReport"])["mandatory"]:
                refs[f"attack:{identifier}"] = "AUDIT_ATTACK"
                attacks.append(identifier)

    return {
        "checkpoint": checkpoint,
        "gate": gate,
        "expectedRefs": sorted(refs),
        "bySource": {
            "SETUP": sum(1 for value in refs.values() if value == "SETUP"),
            "LESSON": sum(1 for value in refs.values() if value == "LESSON"),
            "AUDIT_FINDING": sum(1 for value in refs.values() if value == "AUDIT_FINDING"),
            "AUDIT_ATTACK": sum(1 for value in refs.values() if value == "AUDIT_ATTACK"),
        },
        "total": len(refs),
        "applicableAudits": [item["auditId"] for item in audits],
        "findings": findings,
        "mandatoryAttacks": attacks,
        "lessons": lessons,
    }


def compare(checkpoint: str) -> dict:
    derived = expected(checkpoint)
    matrix_path = ROOT / "docs" / "checkpoints" / checkpoint / "REQUIREMENTS-MATRIX.json"
    matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
    declared = [str(row.get("sourceRef")) for row in matrix.get("requirements") or []]
    anchored = [item for item in declared if not item.startswith("local:")]
    local = [item for item in declared if item.startswith("local:")]
    missing = sorted(set(derived["expectedRefs"]) - set(anchored))
    unexpected = sorted(set(anchored) - set(derived["expectedRefs"]))
    duplicates = sorted({item for item in declared if declared.count(item) > 1})
    return {
        **derived,
        "declaredTotal": len(declared),
        "declaredAnchored": len(anchored),
        "declaredLocal": len(local),
        "missingFromDelivery": missing,
        "declaredButNotExpected": unexpected,
        "duplicateRefs": duplicates,
        "setsAgree": not missing and not unexpected and not duplicates,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    result = compare(args.checkpoint)
    if args.json:
        args.json.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n",
                             encoding="utf-8", newline="\n")
    print(
        f"EXPECTED_SET checkpoint={result['checkpoint']} derived={result['total']} "
        f"declaredAnchored={result['declaredAnchored']} declaredLocal={result['declaredLocal']} "
        f"missing={len(result['missingFromDelivery'])} "
        f"unexpected={len(result['declaredButNotExpected'])} "
        f"duplicates={len(result['duplicateRefs'])} agree={result['setsAgree']}")
    print("  by source: " + ", ".join(f"{key}={value}"
                                      for key, value in sorted(result["bySource"].items())))
    for item in result["missingFromDelivery"][:10]:
        print(f"  MISSING {item}")
    for item in result["declaredButNotExpected"][:10]:
        print(f"  UNEXPECTED {item}")
    return 0 if result["setsAgree"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
