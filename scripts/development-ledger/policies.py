#!/usr/bin/env python3
"""Canonical, machine-readable delivery policy for the IACode Development Control Plane.

The M0 audit of ``SETUP-00-CP-0006`` proved that a control which trusts its own input is not a
control. Two escapes came from exactly that shape:

- the Green Keeper asked the caller which gates were mandatory, so ``--gates ""`` produced a
  vacuous ``PASS``;
- the completeness audit asked the submitted matrix how many requirements existed, so deleting a
  requirement produced a smaller denominator and a forged ``100%``.

This module is the answer to both. The mandatory gate set and the expected requirement set are
derived here, from sources the delivery does not own:

- ``.iacode/policies/quality-gates.json``          the closed mandatory gate registry;
- ``docs/SETUP-00-CHECKLIST.md``                   the canonical Gate specification, re-parsed;
- ``.iacode/policies/canonical-requirements.json`` the machine-readable mirror of that checklist;
- ``.iacode/policies/audit-registry.json``         the independent audits whose findings are open;
- the sealed audit reports themselves, re-parsed for their finding and attack identifiers;
- the Gate's own lesson preflight, for the lessons the engineering memory imposes.

Every expected identifier carries an anchored ``sourceRef``. A requirements matrix must declare
exactly the anchored set: no omission, no substitution, and no unexpected anchored reference.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from ledger_common import LedgerError, load_json

QUALITY_GATE_POLICY = Path(".iacode") / "policies" / "quality-gates.json"
CANONICAL_REQUIREMENTS = Path(".iacode") / "policies" / "canonical-requirements.json"
AUDIT_REGISTRY = Path(".iacode") / "policies" / "audit-registry.json"

# The anchored reference kinds. A matrix row that carries one of these is compared against the
# expected set; ``local`` rows are delivery-specific additions that may never replace an anchor.
ANCHORED_KINDS = ("canonical", "lesson", "finding", "attack")
SOURCE_REF_KINDS = ANCHORED_KINDS + ("local",)

SOURCE_REF = re.compile(r"^(?P<kind>[a-z]+):(?P<value>\S.*)$")

# One checklist row: | 7b.4 | requirement | artifact | evidence |
CHECKLIST_ROW = re.compile(
    r"^\|\s*(?P<key>[0-9]+[a-z]?\.[0-9]+)\s*\|\s*(?P<description>.+?)\s*\|"
    r"\s*(?P<artifact>.+?)\s*\|\s*(?P<evidence>.+?)\s*\|\s*$"
)

# One finding heading in an independent review report: ### M0-F-001 — CRITICAL — ...
FINDING_HEADING = re.compile(r"^###\s+(?P<id>[A-Z0-9]+-F-[0-9]{3})\s*[-—]\s*(?P<rest>.+?)\s*$")

# One attack row in a Red Team report: | C | target | mutation | expected | observed | result | ev |
ATTACK_ROW = re.compile(
    r"^\|\s*(?P<id>[A-Z]{1,2})\s*\|\s*(?P<target>.+?)\s*\|\s*(?P<mutation>.+?)\s*\|"
    r"\s*(?P<expected>.+?)\s*\|\s*(?P<observed>.+?)\s*\|\s*(?P<result>DEFENDED|ESCAPED)\s*\|"
    r"\s*(?P<evidence>.+?)\s*\|\s*$"
)

# One additional-attack row, which omits the target column.
ADDITIONAL_ATTACK_ROW = re.compile(
    r"^\|\s*(?P<id>[A-Z]{1,2})\s*\|\s*(?P<mutation>.+?)\s*\|\s*(?P<expected>.+?)\s*\|"
    r"\s*(?P<observed>.+?)\s*\|\s*(?P<result>DEFENDED|ESCAPED)\s*\|\s*$"
)


def _read(root: Path, relative: str | Path) -> str:
    path = root / relative
    if not path.is_file():
        raise LedgerError(f"canonical policy source is missing: {relative}")
    return path.read_text(encoding="utf-8")


# --------------------------------------------------------------------------------------------
# Mandatory quality gates
# --------------------------------------------------------------------------------------------


def load_gate_policy(root: Path) -> dict[str, Any]:
    policy = load_json(root / QUALITY_GATE_POLICY)
    if not isinstance(policy, dict) or not isinstance(policy.get("gates"), list) or not policy["gates"]:
        raise LedgerError("quality-gates.json must declare a non-empty gates array")
    return policy


def gate_definitions(root: Path) -> dict[str, dict[str, Any]]:
    return {
        str(gate["id"]): gate
        for gate in load_gate_policy(root)["gates"]
        if isinstance(gate, dict) and gate.get("id")
    }


def mandatory_gates(root: Path) -> tuple[str, ...]:
    """The closed mandatory gate set. A caller may extend a run; it may never shrink this."""
    return tuple(
        str(gate["id"])
        for gate in load_gate_policy(root)["gates"]
        if isinstance(gate, dict) and gate.get("mandatory") and gate.get("id")
    )


# --------------------------------------------------------------------------------------------
# Canonical Gate requirements
# --------------------------------------------------------------------------------------------


def parse_checklist(text: str) -> list[dict[str, str]]:
    """Every requirement row of a Gate checklist, in document order.

    The parse lives in code rather than in a configuration value, so the expected requirement set
    cannot be reduced by weakening a stored regular expression.
    """
    rows: list[dict[str, str]] = []
    section = ""
    for line in text.splitlines():
        heading = re.match(r"^##\s+(.+?)\s*$", line)
        if heading:
            section = heading.group(1)
            continue
        match = CHECKLIST_ROW.match(line)
        if match and match.group("description") not in ("Requirement", "---"):
            rows.append({
                "key": match.group("key"),
                "section": section,
                "description": match.group("description"),
                "artifact": match.group("artifact"),
                "evidence": match.group("evidence"),
            })
    return rows


def canonical_requirements(root: Path, gate: str) -> list[dict[str, Any]]:
    """The canonical requirements of a Gate, cross-checked against the specification document."""
    registry = load_json(root / CANONICAL_REQUIREMENTS)
    entries = registry.get("gates") if isinstance(registry, dict) else None
    if not isinstance(entries, list):
        raise LedgerError("canonical-requirements.json must declare a gates array")
    for entry in entries:
        if not isinstance(entry, dict) or entry.get("gate") != gate:
            continue
        specification = entry.get("specification")
        if not specification:
            raise LedgerError(f"canonical requirements for {gate} name no specification document")
        parsed = parse_checklist(_read(root, specification))
        declared = entry.get("requirements") or []
        parsed_keys = [row["key"] for row in parsed]
        declared_keys = [str(item.get("key")) for item in declared if isinstance(item, dict)]
        if parsed_keys != declared_keys:
            raise LedgerError(
                f"canonical-requirements.json for {gate} does not mirror {specification}: "
                f"{len(declared_keys)} declared rows against {len(parsed_keys)} specified rows"
            )
        for row, item in zip(parsed, declared):
            if row["description"] != item.get("description"):
                raise LedgerError(
                    f"canonical requirement {gate}#{row['key']} does not mirror {specification}")
        return [dict(item) for item in declared]
    raise LedgerError(f"canonical-requirements.json declares no requirements for gate {gate}")


# --------------------------------------------------------------------------------------------
# Independent audits, their findings and their attacks
# --------------------------------------------------------------------------------------------


def parse_findings(text: str) -> list[dict[str, str]]:
    """Every finding identifier and headline of an independent review report."""
    findings: list[dict[str, str]] = []
    for line in text.splitlines():
        match = FINDING_HEADING.match(line)
        if match:
            rest = match.group("rest")
            parts = [part.strip() for part in re.split(r"\s*[-—]\s*", rest, maxsplit=1)]
            findings.append({
                "id": match.group("id"),
                "severity": parts[0] if parts else "",
                "title": parts[1] if len(parts) > 1 else rest,
            })
    return findings


def parse_attacks(text: str) -> list[dict[str, str]]:
    """Every attack row of a Red Team report, mandatory table first, additional table after."""
    attacks: list[dict[str, str]] = []
    seen: set[str] = set()
    for line in text.splitlines():
        match = ATTACK_ROW.match(line)
        if match:
            identifier = match.group("id")
            if identifier in seen:
                continue
            seen.add(identifier)
            attacks.append({
                "id": identifier,
                "target": match.group("target"),
                "mutation": match.group("mutation"),
                "expectedDefense": match.group("expected"),
                "observed": match.group("observed"),
                "result": match.group("result"),
                "mandatory": "true",
            })
            continue
        match = ADDITIONAL_ATTACK_ROW.match(line)
        if match:
            identifier = match.group("id")
            if identifier in seen:
                continue
            seen.add(identifier)
            attacks.append({
                "id": identifier,
                "target": "additional attack surface",
                "mutation": match.group("mutation"),
                "expectedDefense": match.group("expected"),
                "observed": match.group("observed"),
                "result": match.group("result"),
                "mandatory": "false",
            })
    return attacks


def load_audit_registry(root: Path) -> list[dict[str, Any]]:
    registry = load_json(root / AUDIT_REGISTRY)
    audits = registry.get("audits") if isinstance(registry, dict) else None
    if not isinstance(audits, list):
        raise LedgerError("audit-registry.json must declare an audits array")
    return [audit for audit in audits if isinstance(audit, dict)]


def open_audits(root: Path, gate: str, checkpoint: str) -> list[dict[str, Any]]:
    """Audits whose corrective work belongs to this checkpoint."""
    return [
        audit for audit in load_audit_registry(root)
        if audit.get("gate") == gate and audit.get("correctiveCheckpoint") == checkpoint
    ]


def audit_findings(root: Path, audit: dict[str, Any]) -> list[dict[str, str]]:
    report = audit.get("reviewReport")
    if not report:
        raise LedgerError(f"audit {audit.get('auditId')!r} names no review report")
    findings = parse_findings(_read(root, report))
    if not findings:
        raise LedgerError(f"no finding could be parsed from {report}")
    return findings


def audit_attacks(root: Path, audit: dict[str, Any]) -> list[dict[str, str]]:
    report = audit.get("redTeamReport")
    if not report:
        return []
    attacks = parse_attacks(_read(root, report))
    if not attacks:
        raise LedgerError(f"no attack could be parsed from {report}")
    return attacks


# --------------------------------------------------------------------------------------------
# The expected requirement set
# --------------------------------------------------------------------------------------------


def source_ref(value: Any) -> tuple[str, str] | None:
    if not isinstance(value, str):
        return None
    match = SOURCE_REF.match(value.strip())
    if not match or match.group("kind") not in SOURCE_REF_KINDS:
        return None
    return match.group("kind"), match.group("value").strip()


def expected_requirement_refs(
    root: Path,
    gate: str,
    checkpoint: str,
    preflight: dict[str, Any] | None,
) -> dict[str, dict[str, Any]]:
    """The anchored references a delivery for this Gate must declare, derived independently.

    EXPECTED = canonical Gate requirements
             + lesson-derived requirements the preflight selected
             + findings of every audit whose corrective work is this checkpoint
             + mandatory attacks of those audits.
    """
    expected: dict[str, dict[str, Any]] = {}

    for item in canonical_requirements(root, gate):
        reference = f"canonical:{gate}#{item['key']}"
        expected[reference] = {
            "sourceRef": reference,
            "source": "SETUP",
            "sourceReference": f"docs/SETUP-00-CHECKLIST.md row {item['key']}",
            "description": item.get("description", ""),
            "mandatory": bool(item.get("mandatory", True)),
        }

    if isinstance(preflight, dict):
        for derived in preflight.get("derivedRequirements") or []:
            if not isinstance(derived, dict) or not derived.get("lessonId"):
                continue
            reference = f"lesson:{derived['lessonId']}"
            expected[reference] = {
                "sourceRef": reference,
                "source": "LESSON",
                "sourceReference": f"LESSON-PREFLIGHT.json {derived.get('id')}",
                "description": derived.get("description", ""),
                "mandatory": bool(derived.get("mandatory", True)),
            }

    for audit in open_audits(root, gate, checkpoint):
        identifier = audit.get("auditId")
        for finding in audit_findings(root, audit):
            reference = f"finding:{finding['id']}"
            expected[reference] = {
                "sourceRef": reference,
                "source": "AUDIT_FINDING",
                "sourceReference": f"{identifier} {audit.get('reviewReport')} {finding['id']}",
                "description": finding["title"],
                "mandatory": True,
            }
        for attack in audit_attacks(root, audit):
            if attack.get("mandatory") != "true":
                continue
            reference = f"attack:{attack['id']}"
            expected[reference] = {
                "sourceRef": reference,
                "source": "AUDIT_ATTACK",
                "sourceReference": f"{identifier} {audit.get('redTeamReport')} attack {attack['id']}",
                "description": f"Defend attack {attack['id']}: {attack['mutation']}",
                "mandatory": True,
            }

    return expected


def declared_requirement_refs(matrix: Any) -> dict[str, list[str]]:
    """Anchored references declared by a requirements matrix, mapped to the declaring row ids."""
    declared: dict[str, list[str]] = {}
    requirements = matrix.get("requirements") if isinstance(matrix, dict) else None
    for item in requirements or []:
        if not isinstance(item, dict):
            continue
        parsed = source_ref(item.get("sourceRef"))
        if parsed is None or parsed[0] not in ANCHORED_KINDS:
            continue
        reference = f"{parsed[0]}:{parsed[1]}"
        declared.setdefault(reference, []).append(str(item.get("id")))
    return declared


def compare_requirement_sets(
    expected: dict[str, dict[str, Any]],
    declared: dict[str, list[str]],
) -> list[dict[str, str]]:
    """Exact set comparison. Omission, duplication and unexpected anchors are all blocking."""
    findings: list[dict[str, str]] = []
    for reference in sorted(set(expected) - set(declared)):
        findings.append({
            "requirement": reference,
            "severity": "BLOCKING",
            "detail": (
                f"the canonical expected set requires {reference} "
                f"({expected[reference]['sourceReference']}) but the matrix does not declare it"),
        })
    for reference in sorted(set(declared) - set(expected)):
        findings.append({
            "requirement": reference,
            "severity": "BLOCKING",
            "detail": (
                f"the matrix declares the anchored reference {reference}, which the canonical "
                f"expected set does not contain"),
        })
    for reference in sorted(set(declared) & set(expected)):
        if len(declared[reference]) > 1:
            findings.append({
                "requirement": reference,
                "severity": "BLOCKING",
                "detail": (
                    f"{reference} is declared by more than one requirement: "
                    + ", ".join(declared[reference])),
            })
    return findings
