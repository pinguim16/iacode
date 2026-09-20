#!/usr/bin/env python3
"""Shared library for the IACode engineering memory.

The memory belongs to the engineering organization, not to any person. It holds what the project
learned from confirmed failures, and its purpose is to stop the same class of failure from happening
twice. A lesson that is merely written down is weak; a lesson that is enforced by a test, a
validator, a schema, or an invariant is a guardrail. Only the second kind may be marked ``GUARDED``.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from ledger_common import LedgerError, find_secrets, load_json, utc_now, validate_schema

MEMORY_DIRECTORY = Path(".iacode") / "memory"
LESSONS_FILE = "lessons.jsonl"
INDEX_FILE = "LESSONS.md"

LESSON_STATUSES = ("OBSERVED", "CONFIRMED", "GUARDED", "SUPERSEDED", "RETIRED")

# A lesson that no longer applies must not generate work for a Gate.
INACTIVE_STATUSES = ("SUPERSEDED", "RETIRED")

LESSON_CATEGORIES = (
    "architecture",
    "implementation",
    "testing",
    "quality",
    "security",
    "documentation",
    "tooling",
    "git",
    "checkpoint",
    "process",
    "provider",
    "model-behavior",
    "training",
    "data",
    "performance",
    "environment",
)

LESSON_SEVERITIES = ("LOW", "MEDIUM", "HIGH", "CRITICAL")

# Controls that actually prevent recurrence. Documentation explains a lesson; it does not guard it.
PREVENTIVE_KINDS = ("test", "validator", "lint", "policy", "schema", "invariant", "automated-check")
CONTROL_KINDS = PREVENTIVE_KINDS + ("documentation",)

SEVERITY_ORDER = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "CRITICAL": 3}


def memory_root(root: Path) -> Path:
    return root / MEMORY_DIRECTORY


def lessons_path(root: Path) -> Path:
    return memory_root(root) / LESSONS_FILE


def load_lessons(root: Path) -> list[dict[str, Any]]:
    path = lessons_path(root)
    if not path.is_file():
        return []
    lessons: list[dict[str, Any]] = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            lessons.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise LedgerError(f"{LESSONS_FILE}:{number}: invalid JSON: {exc}") from exc
    return lessons


def save_lessons(root: Path, lessons: list[dict[str, Any]]) -> None:
    path = lessons_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(lesson, ensure_ascii=False, sort_keys=False) + "\n" for lesson in lessons),
        encoding="utf-8",
        newline="\n",
    )


def next_lesson_id(lessons: list[dict[str, Any]]) -> str:
    highest = 0
    for lesson in lessons:
        match = re.fullmatch(r"LSN-(\d{4})", str(lesson.get("lessonId", "")))
        if match:
            highest = max(highest, int(match.group(1)))
    return f"LSN-{highest + 1:04d}"


def recurrence_key(category: str, symptom: str) -> str:
    """Stable fingerprint for a class of failure, not for one occurrence of it."""
    words = re.findall(r"[a-z0-9]+", symptom.lower())
    stop = {"the", "a", "an", "of", "to", "in", "on", "and", "or", "is", "was", "were", "be",
            "that", "this", "it", "its", "for", "with", "as", "at", "by", "from", "not"}
    keep = [word for word in words if word not in stop][:6]
    slug = "-".join(keep) or "unclassified"
    category_slug = re.sub(r"[^a-z0-9]+", "-", category.lower()).strip("-") or "process"
    return f"{category_slug}/{slug}"


def preventive_controls(lesson: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        control for control in lesson.get("prevention") or []
        if isinstance(control, dict) and control.get("kind") in PREVENTIVE_KINDS
    ]


def escalate(severity: str) -> str:
    index = SEVERITY_ORDER.get(severity, 1)
    return LESSON_SEVERITIES[min(index + 1, len(LESSON_SEVERITIES) - 1)]


def register_recurrence(lesson: dict[str, Any], checkpoint: str, detail: str) -> dict[str, Any]:
    """A repeat increments the counter; a repeat against a guardrail is itself a finding."""
    lesson = json.loads(json.dumps(lesson))
    lesson["recurrenceCount"] = int(lesson.get("recurrenceCount", 0)) + 1
    lesson["updatedAt"] = utc_now()
    if lesson.get("status") == "GUARDED":
        failures = list(lesson.get("guardrailFailures") or [])
        failures.append({
            "observedAt": lesson["updatedAt"],
            "checkpoint": checkpoint,
            "detail": f"GUARDRAIL_FAILURE: {detail}",
        })
        lesson["guardrailFailures"] = failures
        lesson["severity"] = escalate(lesson.get("severity", "MEDIUM"))
        lesson["status"] = "CONFIRMED"
    return lesson


def _matches(selectors: Any, requested: list[str]) -> bool:
    """An empty selector list means the lesson does not constrain on that dimension."""
    values = [str(item) for item in selectors or []]
    if not values or "*" in values:
        return True
    lowered = {item.lower() for item in requested}
    return any(value.lower() in lowered for value in values)


def is_applicable(lesson: dict[str, Any], gate: str, scope: str,
                  technologies: list[str], modules: list[str]) -> tuple[bool, str]:
    """Decide whether a lesson constrains a Gate, and say why in reviewable words."""
    if lesson.get("status") in INACTIVE_STATUSES:
        return False, f"status {lesson.get('status')} is inactive"
    applicability = lesson.get("applicability") or {}
    gates = [str(item) for item in applicability.get("gates") or []]
    if gates and "*" not in gates and gate.lower() not in {item.lower() for item in gates}:
        return False, f"declared for {', '.join(gates)} and not for {gate}"
    if not _matches(applicability.get("scopes"), [scope]):
        return False, f"scope {scope} is outside its declared scopes"
    if not _matches(applicability.get("technologies"), technologies):
        return False, "no declared technology is in play"
    if not _matches(applicability.get("modules"), modules):
        return False, "no declared module is in play"

    reasons = []
    if "*" in gates or not gates:
        reasons.append("applies to every Gate")
    else:
        reasons.append(f"declared for {gate}")
    reasons.append(f"category {lesson.get('category')}")
    reasons.append(f"severity {lesson.get('severity')}")
    if lesson.get("status") == "GUARDED":
        reasons.append("already guarded, so the control must keep holding")
    else:
        reasons.append(f"status {lesson.get('status')}, so it is not yet prevented automatically")
    return True, "; ".join(reasons)


def required_check(lesson: dict[str, Any]) -> str:
    applicability = lesson.get("applicability") or {}
    declared = applicability.get("requiredCheck")
    if declared:
        return str(declared)
    controls = preventive_controls(lesson)
    if controls:
        return "Confirm the control still holds: " + "; ".join(
            f"{control['kind']} {control['reference']}" for control in controls)
    return "Confirm the failure class cannot occur in this Gate and record how it was checked."


def required_evidence(lesson: dict[str, Any]) -> str:
    applicability = lesson.get("applicability") or {}
    declared = applicability.get("requiredEvidence")
    if declared:
        return str(declared)
    controls = preventive_controls(lesson)
    if controls:
        return "A passing reference to " + ", ".join(control["reference"] for control in controls)
    return "An executed check with a resolvable evidence reference."


def derived_requirement(lesson: dict[str, Any], identifier: str) -> dict[str, Any]:
    return {
        "id": identifier,
        "lessonId": lesson["lessonId"],
        "description": f"Verify {lesson['title'][0].lower() + lesson['title'][1:]}",
        "mandatory": lesson.get("severity") in ("HIGH", "CRITICAL") or lesson.get("status") == "GUARDED",
        "requiredEvidence": required_evidence(lesson),
    }


def build_preflight(root: Path, gate: str, scope: str, technologies: list[str],
                    modules: list[str]) -> dict[str, Any]:
    lessons = load_lessons(root)
    applicable: list[dict[str, Any]] = []
    derived: list[dict[str, Any]] = []
    for lesson in lessons:
        ok, reason = is_applicable(lesson, gate, scope, technologies, modules)
        if not ok:
            continue
        identifier = "LESSON-REQ-%04d" % (len(derived) + 1)
        applicable.append({
            "lessonId": lesson["lessonId"],
            "title": lesson["title"],
            "status": lesson["status"],
            "severity": lesson["severity"],
            "reasonApplicable": reason,
            "requiredCheck": required_check(lesson),
            "requiredEvidence": required_evidence(lesson),
            "derivedRequirementId": identifier,
        })
        derived.append(derived_requirement(lesson, identifier))
    return {
        "schemaVersion": "1.0.0",
        "gate": gate,
        "scope": scope,
        "technologies": list(technologies),
        "modules": list(modules),
        "generatedAt": utc_now(),
        "lessonsConsidered": len(lessons),
        "lessonsApplicable": len(applicable),
        "applicable": applicable,
        "derivedRequirements": derived,
    }


def validate_lessons(root: Path, lessons: list[dict[str, Any]] | None = None) -> list[str]:
    """Every rule the memory must satisfy, in one place, used by the CLI and by the tests."""
    errors: list[str] = []
    try:
        lessons = load_lessons(root) if lessons is None else lessons
    except LedgerError as exc:
        return [str(exc)]

    schema_path = root / ".iacode" / "schemas" / "lesson.schema.json"
    schema = load_json(schema_path) if schema_path.is_file() else None
    if schema is None:
        errors.append("lesson.schema.json is missing")

    seen_ids: set[str] = set()
    seen_keys: dict[str, str] = {}
    for index, lesson in enumerate(lessons, 1):
        label = lesson.get("lessonId") or f"line {index}"
        if schema is not None:
            for error in validate_schema(lesson, schema):
                errors.append(f"{label}: {error}")

        identifier = lesson.get("lessonId")
        if identifier in seen_ids:
            errors.append(f"{label}: duplicate lessonId")
        if isinstance(identifier, str):
            seen_ids.add(identifier)

        key = lesson.get("recurrenceKey")
        if isinstance(key, str) and key in seen_keys and seen_keys[key] != identifier:
            errors.append(
                f"{label}: recurrenceKey {key!r} is already used by {seen_keys[key]}; a repeat must "
                f"increment that lesson instead of creating a new one")
        elif isinstance(key, str):
            seen_keys.setdefault(key, str(identifier))

        status = lesson.get("status")
        if status == "GUARDED" and not preventive_controls(lesson):
            errors.append(
                f"{label}: GUARDED requires at least one preventive control of kind "
                f"{', '.join(PREVENTIVE_KINDS)}; documentation alone is not a guardrail")
        if status == "SUPERSEDED" and not lesson.get("supersededBy"):
            errors.append(f"{label}: SUPERSEDED requires supersededBy")

        eligibility = lesson.get("trainingEligibility") or {}
        if eligibility.get("trainingAllowed") and not eligibility.get("justification"):
            errors.append(f"{label}: trainingAllowed requires explicit rights justification")
        if eligibility.get("distillationAllowed") and not eligibility.get("justification"):
            errors.append(f"{label}: distillationAllowed requires explicit rights justification")

        count = lesson.get("recurrenceCount")
        failures = lesson.get("guardrailFailures") or []
        if isinstance(count, int) and len(failures) > count:
            errors.append(
                f"{label}: {len(failures)} guardrail failures recorded but recurrenceCount is {count}")
        if failures and status == "GUARDED":
            errors.append(
                f"{label}: a guardrail failure must reopen the lesson; GUARDED is not a valid status "
                f"while a GUARDRAIL_FAILURE is unresolved")

        for field in ("symptom", "rootCauseSummary", "resolution", "title", "notes"):
            value = lesson.get(field)
            if isinstance(value, str):
                for finding in find_secrets(value):
                    errors.append(f"{label}: secret pattern detected in {field}: {finding}")
        for reference in lesson.get("evidence") or []:
            if isinstance(reference, str):
                for finding in find_secrets(reference):
                    errors.append(f"{label}: secret pattern detected in evidence: {finding}")

    return errors


def render_index(lessons: list[dict[str, Any]]) -> str:
    lines = [
        "# Engineering Lessons",
        "",
        "Rendered index of `lessons.jsonl`, which is the authoritative machine-readable memory.",
        "Regenerate with `python scripts/development-ledger/validate_lessons.py --render-index`.",
        "",
        "A lesson is `GUARDED` only when an automated control prevents its recurrence. Reading this",
        "file is never the control. See [docs/ENGINEERING-MEMORY.md](../../docs/ENGINEERING-MEMORY.md).",
        "",
        "| ID | Status | Severity | Category | Lesson | Guarded by |",
        "|---|---|---|---|---|---|",
    ]
    for lesson in lessons:
        controls = preventive_controls(lesson)
        guard = ", ".join(f"`{control['reference']}`" for control in controls) if controls else "_not yet guarded_"
        lines.append("| `%s` | `%s` | %s | %s | %s | %s |" % (
            lesson.get("lessonId"), lesson.get("status"), lesson.get("severity"),
            lesson.get("category"), lesson.get("title"), guard))
    lines += ["", "## Detail", ""]
    for lesson in lessons:
        lines += [
            "### %s — %s" % (lesson.get("lessonId"), lesson.get("title")),
            "",
            "- Status: `%s`, severity %s, category %s, recurrences %s." % (
                lesson.get("status"), lesson.get("severity"), lesson.get("category"),
                lesson.get("recurrenceCount", 0)),
            "- Source: %s, %s%s." % (
                lesson.get("source", {}).get("gate"),
                lesson.get("source", {}).get("checkpoint"),
                ", finding %s" % lesson["source"]["finding"] if lesson.get("source", {}).get("finding") else ""),
            "- Symptom: %s" % lesson.get("symptom"),
            "- Root cause: %s" % lesson.get("rootCauseSummary"),
            "- Resolution: %s" % lesson.get("resolution"),
        ]
        controls = lesson.get("prevention") or []
        if controls:
            lines.append("- Prevention:")
            for control in controls:
                lines.append("  - `%s` %s — %s" % (control["kind"], control["reference"], control["description"]))
        else:
            lines.append("- Prevention: _none recorded_")
        lines.append("- Evidence: %s" % ", ".join("`%s`" % item for item in lesson.get("evidence") or []))
        lines.append("")
    while lines and not lines[-1]:
        lines.pop()
    return "\n".join(lines) + "\n"
