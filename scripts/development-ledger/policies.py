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
TEST_SUITE_REGISTRY = Path(".iacode") / "policies" / "test-suites.json"

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

# One section heading of a report: ## Findings, ### M0-F-001 - ...
SECTION_HEADING = re.compile(r"^#{2,}\s+(?P<title>.+?)\s*$")

# One finding heading in an independent review report: ### M0-F-001 — CRITICAL — ...
# The backticks around the identifier are optional: CP-0007 and CP-0009 wrote the identifier bare
# and CP-0011 wrote it quoted. A report whose findings cannot be parsed is refused by
# ``audit_findings`` rather than read as a report without findings.
FINDING_HEADING = re.compile(r"^###\s+`?(?P<id>[A-Z0-9]+-F-[0-9]{3})`?\s*[-—]\s*(?P<rest>.+?)\s*$")

# The section whose findings belong to the report that writes them. An audit report also discusses
# the findings of the audit it follows, under its own heading, and those are that audit's findings
# and not this one's: reading them as new work would make a corrective delivery re-close findings a
# previous delivery already closed.
FINDINGS_SECTION = "findings"

# One attack row in a Red Team report:
#     | C | target | mutation | expected | observed | result | evidence |
# The evidence column and the backticks around the identifier and the verdict are optional,
# because sealed reports differ in how they render the same table: CP-0007 wrote seven columns
# with a bare verdict and CP-0009 wrote six with a quoted one. A parser that recognised only one
# rendering would silently read a sealed report as containing no attack at all.
ATTACK_ROW = re.compile(
    r"^\|\s*`?(?P<id>[A-Z]{1,2})`?\s*\|\s*(?P<target>.+?)\s*\|\s*(?P<mutation>.+?)\s*\|"
    r"\s*(?P<expected>.+?)\s*\|\s*(?P<observed>.+?)\s*\|\s*`?(?P<result>DEFENDED|ESCAPED)`?"
    r"\s*\|(?:\s*(?P<evidence>.+?)\s*\|)?\s*$"
)

# One additional-attack row, which omits the target column.
ADDITIONAL_ATTACK_ROW = re.compile(
    r"^\|\s*`?(?P<id>[A-Z]{1,2})`?\s*\|\s*(?P<mutation>.+?)\s*\|\s*(?P<expected>.+?)\s*\|"
    r"\s*(?P<observed>.+?)\s*\|\s*`?(?P<result>DEFENDED|ESCAPED)`?\s*\|\s*$"
)

# The separator under a Markdown table header: |---|---|
TABLE_SEPARATOR = re.compile(r"^\|(?:\s*:?-{3,}:?\s*\|)+\s*$")

# An attack identifier, in either rendering a sealed report has used: a single letter or a pair of
# letters (CP-0007, CP-0009) or a prefixed, numbered identifier (CP-0011).
ATTACK_IDENTIFIER = re.compile(r"^(?:[A-Z]{1,2}|[A-Z]{2,4}-[0-9]{1,3})$")

# The header cells that introduce a table of attacks. A table whose first column is anything else
# is a table of something else -- a positive control, a guardrail probe, a scenario log -- and its
# rows are not attacks.
ATTACK_ID_HEADERS = ("attack", "id")


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
# The canonical test suites
# --------------------------------------------------------------------------------------------


def load_test_suites(root: Path) -> list[dict[str, Any]]:
    """Every declared test suite, or the historical single suite when no registry exists.

    Gate 0 adds runtime suites next to the control-plane one, and the denominator of the TESTS
    count has to include them. Which suites exist is a policy statement, exactly like the mandatory
    gate set: a suite cannot be added by an invocation and cannot be dropped to shrink a count.

    A repository sealed before the registry existed has one suite, ``tests/``. Returning it keeps
    every sealed checkpoint deriving the number it was sealed with instead of becoming invalid
    because the tooling grew.
    """
    path = root / TEST_SUITE_REGISTRY
    if not path.is_file():
        return [{
            "id": "ledger",
            "title": "Development control plane suite",
            "root": "tests",
            "framework": "python-unittest",
            "counted": True,
            "purpose": "The only suite this repository revision declares.",
        }]
    registry = load_json(path)
    suites = registry.get("suites") if isinstance(registry, dict) else None
    if not isinstance(suites, list) or not suites:
        raise LedgerError("test-suites.json must declare a non-empty suites array")
    for suite in suites:
        if not isinstance(suite, dict) or not suite.get("id") or not suite.get("root"):
            raise LedgerError("every declared test suite needs an id and a root")
        if not suite.get("counted") and not str(suite.get("notCountedReason") or "").strip():
            raise LedgerError(
                f"test suite {suite['id']!r} is not counted and records no reason; an omission "
                f"from the denominator is declared, never implied")
    return [dict(suite) for suite in suites]


def counted_test_suites(root: Path) -> list[dict[str, Any]]:
    """The declared suites whose cases the count derivation and evidence resolution may use."""
    return [suite for suite in load_test_suites(root) if suite.get("counted")]


# --------------------------------------------------------------------------------------------
# Gate scope
# --------------------------------------------------------------------------------------------

GATE_SCOPE = Path(".iacode") / "policies" / "gate-scope.json"

# A reserved directory holds its declaration and nothing else. The marker is a phrase the README
# states about itself, so a reservation cannot be lifted by editing prose alone: dropping the
# marker while the directory holds an implementation still fails, because the implementation is
# what the control counts.
RESERVATION_MARKER = "Status: RESERVED"
RESERVATION_ALLOWED_FILES = ("README.md",)


def load_gate_scope(root: Path) -> list[dict[str, Any]]:
    """Every reservation the canonical scope policy declares, or none when it does not exist."""
    path = root / GATE_SCOPE
    if not path.is_file():
        return []
    document = load_json(path)
    reservations = document.get("reservations") if isinstance(document, dict) else None
    if not isinstance(reservations, list):
        raise LedgerError("gate-scope.json must declare a reservations array")
    return [item for item in reservations if isinstance(item, dict)]


def gate_order() -> tuple[str, ...]:
    """Every planned Gate in delivery order, normalised, derived from the published milestones."""
    from ledger_common import MILESTONES, normalize_gate

    return tuple(normalize_gate(gate) for _identifier, _title, gates in MILESTONES
                 for gate in gates)


def reservations_in_force(root: Path, gate: str) -> list[dict[str, Any]]:
    """The reservations that still constrain a delivery for ``gate``.

    A reservation belongs to a Gate that has not run yet, so it constrains every delivery before its
    owner and stops constraining anything from its owner onwards — otherwise the control would fail
    the Gate for the directory it had just legitimately filled.

    This is derived here, once, rather than re-implemented by each caller. The scope check and the
    test that reads the reservation READMEs both need exactly this set, and a second copy of the
    ordering rule is a second copy that can disagree with the first.
    """
    from ledger_common import normalize_gate

    order = gate_order()
    current = normalize_gate(gate)
    position = order.index(current) if current in order else -1
    in_force: list[dict[str, Any]] = []
    for reservation in load_gate_scope(root):
        owner = normalize_gate(str(reservation.get("gate")))
        if owner not in order or (position >= 0 and order.index(owner) <= position):
            continue
        in_force.append(reservation)
    return in_force


def scope_violations(root: Path, gate: str) -> list[str]:
    """Reserved paths a delivery for ``gate`` has implemented, which it may not have.

    A path that does not exist is not a violation: creating the directory is part of the monorepo
    layout and is verified by the suite, while this control is about what a delivery *put inside*
    one.
    """
    violations: list[str] = []
    for reservation in reservations_in_force(root, gate):
        directory = root / str(reservation["path"])
        if not directory.is_dir():
            continue
        contents = sorted(
            str(item.relative_to(directory)).replace("\\", "/")
            for item in directory.rglob("*")
            if item.is_file() and "__pycache__" not in item.parts
        )
        extra = [name for name in contents if name not in RESERVATION_ALLOWED_FILES]
        if extra:
            violations.append(
                f"{reservation['path']} is reserved for {reservation['gate']} but carries "
                + ", ".join(extra[:5]))
            continue
        readme = directory / "README.md"
        if not readme.is_file() or RESERVATION_MARKER not in readme.read_text(encoding="utf-8"):
            violations.append(
                f"{reservation['path']} is reserved for {reservation['gate']} and does not "
                f"declare the reservation")
    return violations


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


def gate_specification(root: Path, gate: str) -> str:
    """The canonical specification document of a Gate, as the registry declares it.

    Every Gate has its own specification, and a derived requirement must cite the document it was
    actually derived from. Naming one Gate's checklist in the derivation of another's requirements
    would make a Gate 0 requirement point at the SETUP-00 checklist, where the row does not exist:
    an evidence reference that resolves to the wrong document is not evidence.
    """
    registry = load_json(root / CANONICAL_REQUIREMENTS)
    entries = registry.get("gates") if isinstance(registry, dict) else None
    if not isinstance(entries, list):
        raise LedgerError("canonical-requirements.json must declare a gates array")
    for entry in entries:
        if isinstance(entry, dict) and entry.get("gate") == gate and entry.get("specification"):
            return str(entry["specification"])
    raise LedgerError(f"canonical-requirements.json declares no specification for gate {gate}")


# --------------------------------------------------------------------------------------------
# Independent audits, their findings and their attacks
# --------------------------------------------------------------------------------------------


def parse_findings(text: str) -> list[dict[str, str]]:
    """Every finding identifier and headline the report raises *as its own*.

    Scoped to the report's ``## Findings`` section. An audit report also verifies the findings of
    the audit before it, under a heading of its own and in the same ``###`` shape; those belong to
    the earlier audit and were closed by an earlier delivery. Reading them here would require the
    corrective delivery to close findings it did not receive, and would inflate the expected
    requirement set with work that is already done.
    """
    findings: list[dict[str, str]] = []
    section = ""
    for line in text.splitlines():
        heading = SECTION_HEADING.match(line)
        if heading and not line.startswith("###"):
            section = heading.group("title").strip().strip("`").lower()
            continue
        if section != FINDINGS_SECTION:
            continue
        match = FINDING_HEADING.match(line)
        if match:
            rest = match.group("rest")
            parts = [part.strip() for part in re.split(r"\s*[-—]\s*", rest, maxsplit=1)]
            findings.append({
                "id": match.group("id"),
                "severity": parts[0].strip("`") if parts else "",
                "title": parts[1] if len(parts) > 1 else rest,
            })
    return findings


def _table_cells(line: str) -> list[str]:
    body = line.strip()
    if not body.startswith("|"):
        return []
    body = body[1:]
    if body.endswith("|"):
        body = body[:-1]
    return [cell.strip() for cell in body.split("|")]


def _attack_columns(header: str) -> list[str] | None:
    """The column map of a table of attacks, or ``None`` when the table is not one."""
    cells = [cell.strip().strip("`").lower() for cell in _table_cells(header)]
    if not cells or cells[0] not in ATTACK_ID_HEADERS or "result" not in cells:
        return None
    return cells


def _attack_from_row(cells: list[str], columns: list[str],
                     additional_section: bool) -> dict[str, str] | None:
    def column(name: str, default: str = "") -> str:
        return cells[columns.index(name)].strip() if name in columns else default

    identifier = cells[0].strip().strip("`")
    if ATTACK_IDENTIFIER.match(identifier) is None:
        return None
    result = column("result").strip("`")
    if result not in ("DEFENDED", "ESCAPED"):
        return None
    # The battery a row belongs to is stated by the row when the table says so, and by the section
    # otherwise. CP-0011 rendered one table with a category column; the earlier reports rendered one
    # table per battery.
    if "category" in columns:
        mandatory = column("category").strip("`").lower() == "mandatory"
    else:
        mandatory = not additional_section
    return {
        "id": identifier,
        "target": column("target", "additional attack surface"),
        "mutation": column("mutation") or column("scenario") or column("expectation"),
        "expectedDefense": column("expected", "reject"),
        "observed": column("observed", "not recorded as a column in the sealed report"),
        "result": result,
        "mandatory": "true" if mandatory else "false",
    }


def parse_attacks(text: str) -> list[dict[str, str]]:
    """Every attack row of a Red Team report, mandatory battery first, additional battery after.

    Which battery a row belongs to is decided by the table's own category column when it has one and
    by the section it is written under otherwise, never by how many columns its table happens to
    have. The CP-0007 report wrote its additional attacks in a narrower table, the CP-0009 report
    wrote them in the same table shape as the mandatory ones, and the CP-0011 report wrote one table
    with a category column and prefixed identifiers; a parser that inferred the battery from the
    shape would have promoted twenty-six additional attacks to mandatory the moment the second
    report was registered, and a parser that recognised only the first two renderings read the third
    sealed report as containing no attack at all.

    A table is read by its header whenever it has one, so the column meanings come from the document
    instead of from a guess, and a table whose first column is not an attack identifier is not a
    table of attacks. The header-less shapes stay supported because a report may quote a battery
    fragment without its header.
    """
    attacks: list[dict[str, str]] = []
    seen: set[str] = set()
    additional_section = False
    columns: list[str] | None = None
    lines = text.splitlines()
    for index, line in enumerate(lines):
        heading = SECTION_HEADING.match(line)
        if heading:
            additional_section = "additional" in heading.group("title").lower()
            columns = None
            continue
        if TABLE_SEPARATOR.match(line):
            columns = _attack_columns(lines[index - 1]) if index else None
            continue
        if not line.lstrip().startswith("|"):
            columns = None
            continue
        if columns is not None:
            cells = _table_cells(line)
            if len(cells) != len(columns):
                columns = None
                continue
            parsed = _attack_from_row(cells, columns, additional_section)
            if parsed is None or parsed["id"] in seen:
                continue
            seen.add(parsed["id"])
            attacks.append(parsed)
            continue
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
                "mandatory": "false" if additional_section else "true",
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


def audit_applicability(root: Path, gate: str, checkpoint: str) -> dict[str, Any]:
    """What the canonical sources say this checkpoint must close, and where that came from.

    The applicable set is derived here and nowhere else. No invocation supplies it and no artifact
    inside the checkpoint can shrink it: the audits come from the registry, matched on the Gate and
    on the checkpoint the registry itself names as their corrective delivery, and their findings and
    attacks are re-parsed from the sealed reports at every call.

    An empty result and a missing result are different states, and only the first one is benign. A
    checkpoint that no registered audit names as its corrective delivery has nothing to close, which
    is legitimate and is what the empty set means here. An audit whose sealed report cannot be read
    raises instead of reducing to an empty set, so a report that becomes unparseable can never be
    mistaken for an audit without findings.
    """
    audits = open_audits(root, gate, checkpoint)
    findings: list[dict[str, str]] = []
    attacks: list[dict[str, str]] = []
    for audit in audits:
        findings.extend(audit_findings(root, audit))
        attacks.extend(item for item in audit_attacks(root, audit) if item["mandatory"] == "true")
    return {
        "audits": audits,
        "auditIds": [str(audit.get("auditId")) for audit in audits],
        "findings": findings,
        "mandatoryAttacks": attacks,
        "derivationSource": (
            f"{AUDIT_REGISTRY.as_posix()} matched on gate={gate!r} and "
            f"correctiveCheckpoint={checkpoint!r}, with every finding and mandatory attack "
            f"re-parsed from the sealed reports the matching entries name"),
    }


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

    specification = gate_specification(root, gate)
    for item in canonical_requirements(root, gate):
        reference = f"canonical:{gate}#{item['key']}"
        expected[reference] = {
            "sourceRef": reference,
            "source": "GATE_SPECIFICATION",
            "sourceReference": f"{specification} row {item['key']}",
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
