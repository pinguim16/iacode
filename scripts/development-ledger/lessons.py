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

from ledger_common import (
    LedgerError,
    canonical_digest,
    canonical_hash_path,
    find_secrets,
    load_json,
    utc_now,
    validate_schema,
)

MEMORY_DIRECTORY = Path(".iacode") / "memory"
LESSONS_FILE = "lessons.jsonl"
INDEX_FILE = "LESSONS.md"
GUARDRAIL_REGISTRY_FILE = "guardrails/registry.json"
POLICY_FILE = "POLICY.json"

# Memory policy versions. 1.0.0 is the original memory: a GUARDED lesson had to name a
# preventive control, but nothing resolved the reference. 2.0.0 resolves every claim and
# requires a registered guardrail. Sealed checkpoints carry a 1.0.0 memory and are read
# under those rules, which is how a new control avoids invalidating history.
LEGACY_MEMORY_POLICY = "1.0.0"
RESOLVING_MEMORY_POLICY = "2.0.0"

# The applicability and derivation rules the preflight implements. It is part of the preflight
# fingerprint, so changing how lessons are selected makes every existing preflight stale.
LESSON_POLICY_VERSION = "2.0.0"

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


def guardrail_registry_path(root: Path) -> Path:
    return memory_root(root) / GUARDRAIL_REGISTRY_FILE


def memory_policy_version(root: Path) -> str:
    """The memory policy this repository declares, defaulting to the original rules."""
    path = memory_root(root) / POLICY_FILE
    if not path.is_file():
        return LEGACY_MEMORY_POLICY
    document = load_json(path)
    version = document.get('schemaVersion') if isinstance(document, dict) else None
    return str(version) if version else LEGACY_MEMORY_POLICY


def load_guardrails(root: Path) -> dict[str, dict[str, Any]]:
    """The guardrail registry, keyed by identifier. An empty registry is an empty mapping."""
    path = guardrail_registry_path(root)
    if not path.is_file():
        return {}
    document = load_json(path)
    entries = document.get("guardrails") if isinstance(document, dict) else None
    if not isinstance(entries, list):
        raise LedgerError("guardrails/registry.json must declare a guardrails array")
    return {
        str(entry["guardrailId"]): entry
        for entry in entries
        if isinstance(entry, dict) and entry.get("guardrailId")
    }


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


# --------------------------------------------------------------------------------------------
# Resolving what a lesson claims
# --------------------------------------------------------------------------------------------

# Kinds whose reference is a repository path that must exist.
PATH_CONTROL_KINDS = ("validator", "policy", "schema", "lint", "automated-check", "documentation")

_TEST_ID_CACHE: dict[str, set[str]] = {}


def suite_test_ids(root: Path) -> set[str]:
    """Every test case id in the suite, as ``TestClass.test_name`` and as the bare method name.

    The audit found that a ``GUARDED`` lesson could name a test that does not exist. A claim about
    a control is only worth as much as the resolution of its reference, so the memory validator
    resolves the reference against the real suite instead of accepting the string.
    """
    key = str(root.resolve())
    if key in _TEST_ID_CACHE:
        return _TEST_ID_CACHE[key]
    from delivery_assurance import collect_test_ids

    identifiers = collect_test_ids(root)
    _TEST_ID_CACHE[key] = identifiers
    return identifiers


def _invariant_exists(root: Path, reference: str) -> bool:
    """An invariant reference names a function that must exist in the tooling."""
    module, _, symbol = reference.rpartition(".")
    definition = re.compile(rf"^\s*(?:def|class)\s+{re.escape(symbol)}\b", re.MULTILINE)
    scripts = root / "scripts"
    if module:
        candidate = scripts / "development-ledger" / f"{module}.py"
        if candidate.is_file():
            return definition.search(candidate.read_text(encoding="utf-8")) is not None
    if not scripts.is_dir():
        return False
    for path in scripts.rglob("*.py"):
        if "__pycache__" in path.parts:
            continue
        if definition.search(path.read_text(encoding="utf-8")):
            return True
    return False


def resolve_control(root: Path, control: dict[str, Any]) -> str | None:
    """Return why a preventive control cannot be resolved, or None when it resolves."""
    kind = control.get("kind")
    reference = control.get("reference")
    if not isinstance(reference, str) or not reference.strip():
        return f"control of kind {kind!r} has no reference"
    if kind == "test":
        if reference not in suite_test_ids(root):
            return f"control names the test {reference!r}, which does not exist in the suite"
        return None
    if kind == "invariant":
        if not _invariant_exists(root, reference):
            return f"control names the invariant {reference!r}, which is defined nowhere in scripts/"
        return None
    if kind in PATH_CONTROL_KINDS:
        candidate = (root / reference).resolve()
        if root.resolve() not in candidate.parents:
            return f"control path escapes the repository: {reference}"
        if not candidate.is_file():
            return f"control names the path {reference!r}, which does not exist"
        try:
            if not candidate.read_text(encoding="utf-8").strip():
                return f"control names the empty file {reference!r}"
        except UnicodeDecodeError:
            pass
        return None
    return f"unsupported control kind {kind!r}"


def resolve_lesson_evidence(root: Path, reference: Any) -> str | None:
    """Return why a lesson evidence reference cannot be resolved, or None when it resolves."""
    if not isinstance(reference, str) or ":" not in reference:
        return f"malformed evidence reference {reference!r}"
    kind, _, value = reference.partition(":")
    if kind != "file":
        return f"unsupported lesson evidence kind {kind!r}; lessons cite repository files"
    if not value.strip():
        return f"empty evidence target in {reference!r}"
    candidate = (root / value).resolve()
    if root.resolve() not in candidate.parents:
        return f"evidence path escapes the repository: {reference}"
    if not candidate.is_file():
        return f"evidence file does not exist: {reference}"
    try:
        if not candidate.read_text(encoding="utf-8").strip():
            return f"evidence file is empty: {reference}"
    except UnicodeDecodeError:
        if candidate.stat().st_size == 0:
            return f"evidence file is empty: {reference}"
    return None


def _resolve_source_locator(root: Path, lesson: dict[str, Any]) -> str | None:
    """A lesson's provenance must point at a checkpoint that records the finding it cites.

    ``finding`` is free text because a finding identifier looks different in every audit. The rule
    is therefore narrow and checkable: every checkpoint named in the locator must exist, and every
    identifier-shaped token in the locator must appear somewhere in the evidence of one of the
    checkpoints the locator names.
    """
    source = lesson.get("source") or {}
    checkpoints_root = root / "docs" / "checkpoints"
    named = [str(source.get("checkpoint") or "")]
    finding = str(source.get("finding") or "")
    named += re.findall(r"\b[A-Z][A-Z0-9]*-[0-9]{2}-CP-[0-9]{4}\b", finding)
    named = [item for item in dict.fromkeys(named) if item]
    if not named:
        return "source names no checkpoint"

    corpus: list[str] = []
    for identifier in named:
        directory = checkpoints_root / identifier
        if not directory.is_dir():
            return f"source cites {identifier}, which is not a checkpoint in this repository"
        for path in sorted(directory.iterdir()):
            if path.is_file() and path.suffix.lower() in (".md", ".json", ".jsonl"):
                try:
                    corpus.append(path.read_text(encoding="utf-8"))
                except UnicodeDecodeError:
                    continue
    haystack = "\n".join(corpus)

    tokens = re.findall(r"\b(?:[A-Z]+[0-9]*-)?[A-Z]{1,3}[0-9]+(?:\.[0-9]+)?\b", finding)
    tokens = [token for token in tokens if not re.fullmatch(r"CP[0-9]+", token)]
    for token in tokens:
        if token in {item for identifier in named for item in (identifier,)}:
            continue
        if token not in haystack:
            return (
                f"source cites finding {token!r}, which appears in none of the checkpoints it "
                f"names ({', '.join(named)})")
    return None


def _walk_strings(value: Any, path: str = "$"):
    """Every string inside a lesson, with the place it was found, at any nesting depth."""
    if isinstance(value, str):
        yield path, value
    elif isinstance(value, dict):
        for key, item in value.items():
            yield from _walk_strings(item, f"{path}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from _walk_strings(item, f"{path}[{index}]")


def unresolved_guardrail_failures(lesson: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        failure for failure in lesson.get("guardrailFailures") or []
        if isinstance(failure, dict) and not failure.get("resolvedIn")
    ]


def memory_fingerprint(root: Path) -> str:
    """Content identity of everything a preflight result depends on.

    Not a timestamp: a timestamp says when the preflight ran, which is exactly what let a stale
    preflight survive a retired lesson. This is a digest of the canonical memory, the lesson schema,
    the guardrail registry and the selection policy version, so any change to any of them makes an
    existing preflight detectably stale.
    """
    lessons = load_lessons(root)
    lesson_identity = [
        [
            lesson.get("lessonId"),
            lesson.get("status"),
            lesson.get("severity"),
            lesson.get("category"),
            lesson.get("title"),
            lesson.get("applicability"),
            [[control.get("kind"), control.get("reference")] for control in lesson.get("prevention") or []],
            lesson.get("guardrails"),
            lesson.get("recurrenceCount"),
        ]
        for lesson in lessons
    ]
    schema_path = root / ".iacode" / "schemas" / "lesson.schema.json"
    registry_path = guardrail_registry_path(root)
    return canonical_digest({
        "policyVersion": LESSON_POLICY_VERSION,
        "memoryPolicy": memory_policy_version(root),
        "lessons": lesson_identity,
        "lessonSchema": canonical_hash_path(schema_path) if schema_path.is_file() else None,
        "guardrailRegistry": canonical_hash_path(registry_path) if registry_path.is_file() else None,
    })


def preflight_fingerprint(root: Path, gate: str, scope: str,
                          technologies: list[str], modules: list[str]) -> str:
    """The fingerprint stored in a preflight, over memory identity plus selection inputs."""
    return canonical_digest({
        "memory": memory_fingerprint(root),
        "gate": gate,
        "scope": scope,
        "technologies": sorted(str(item) for item in technologies),
        "modules": sorted(str(item) for item in modules),
    })


def guardrail_effectiveness(root: Path, lessons: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    """Measure the guardrails rather than trusting the word ``GUARDED``."""
    lessons = load_lessons(root) if lessons is None else lessons
    registry = load_guardrails(root)
    test_ids = suite_test_ids(root)

    failures = 0
    failing_lessons: list[str] = []
    for lesson in lessons:
        unresolved = unresolved_guardrail_failures(lesson)
        if unresolved:
            failures += len(unresolved)
            failing_lessons.append(str(lesson.get("lessonId")))

    resolved = 0
    tested = 0
    effective = 0
    details: list[dict[str, Any]] = []
    guarded_by: dict[str, list[str]] = {}
    for lesson in lessons:
        for identifier in lesson.get("guardrails") or []:
            guarded_by.setdefault(str(identifier), []).append(str(lesson.get("lessonId")))

    for identifier, entry in sorted(registry.items()):
        control = {"kind": entry.get("kind"), "reference": entry.get("reference")}
        control_error = resolve_control(root, control)
        verified_by = [str(item) for item in entry.get("verifiedBy") or []]
        missing_tests = [item for item in verified_by if item not in test_ids]
        is_resolved = control_error is None
        is_tested = bool(verified_by) and not missing_tests
        lesson_ids = guarded_by.get(identifier, [])
        is_effective = is_resolved and is_tested and not any(
            lesson_id in failing_lessons for lesson_id in lesson_ids)
        resolved += int(is_resolved)
        tested += int(is_tested)
        effective += int(is_effective)
        details.append({
            "guardrailId": identifier,
            "kind": entry.get("kind"),
            "reference": entry.get("reference"),
            "lessons": lesson_ids,
            "resolved": is_resolved,
            "tested": is_tested,
            "effective": is_effective,
            "detail": control_error or (
                "verifiedBy names tests that do not exist: " + ", ".join(missing_tests)
                if missing_tests else
                "the guardrail declares no verifying test" if not verified_by else None),
        })

    return {
        "guardrailsTotal": len(registry),
        "guardrailsResolved": resolved,
        "guardrailsTested": tested,
        "guardrailsEffective": effective,
        "guardrailFailures": failures,
        "lessonsWithUnresolvedFailures": sorted(set(failing_lessons)),
        "guardrails": details,
    }


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
        "schemaVersion": "2.0.0",
        "gate": gate,
        "scope": scope,
        "technologies": list(technologies),
        "modules": list(modules),
        "generatedAt": utc_now(),
        "policyVersion": LESSON_POLICY_VERSION,
        "inputsFingerprint": preflight_fingerprint(root, gate, scope, technologies, modules),
        "lessonsConsidered": len(lessons),
        "lessonsApplicable": len(applicable),
        "applicable": applicable,
        "derivedRequirements": derived,
    }


def preflight_staleness(root: Path, preflight: Any, gate: str | None = None) -> list[str]:
    """Why a stored preflight no longer describes the memory, or an empty list when it is fresh.

    Freshness is decided by recomputation, not by a date. The recorded fingerprint is compared with
    a fresh one, and the selected lessons and derived requirement identifiers are compared with a
    fresh selection, so adding, retiring or re-scoping a lesson invalidates the preflight.
    """
    if not isinstance(preflight, dict):
        return ["LESSON-PREFLIGHT.json is not an object"]
    errors: list[str] = []
    declared_gate = str(preflight.get("gate") or "")
    scope = str(preflight.get("scope") or "")
    technologies = [str(item) for item in preflight.get("technologies") or []]
    modules = [str(item) for item in preflight.get("modules") or []]

    if gate is not None and declared_gate.upper().replace(" ", "") != str(gate).upper().replace(" ", ""):
        errors.append(
            f"the preflight was generated for gate {declared_gate!r} but the checkpoint declares "
            f"{gate!r}; a preflight may not be reused across Gates")
        return errors

    expected = preflight_fingerprint(root, declared_gate, scope, technologies, modules)
    if preflight.get("inputsFingerprint") != expected:
        errors.append(
            "the lesson preflight is STALE: its recorded inputsFingerprint does not match the "
            "current engineering memory, guardrail registry, lesson schema and selection policy")
    if preflight.get("policyVersion") not in (None, LESSON_POLICY_VERSION):
        errors.append(
            f"the lesson preflight was produced by selection policy "
            f"{preflight.get('policyVersion')!r}, not {LESSON_POLICY_VERSION!r}")

    fresh = build_preflight(root, declared_gate, scope, technologies, modules)
    recorded_lessons = [item.get("lessonId") for item in preflight.get("applicable") or []]
    fresh_lessons = [item["lessonId"] for item in fresh["applicable"]]
    if recorded_lessons != fresh_lessons:
        errors.append(
            "the lesson preflight is STALE: a fresh selection yields "
            f"{', '.join(fresh_lessons) or 'no lesson'} rather than "
            f"{', '.join(str(item) for item in recorded_lessons) or 'no lesson'}")
    recorded_derived = [item.get("id") for item in preflight.get("derivedRequirements") or []]
    fresh_derived = [item["id"] for item in fresh["derivedRequirements"]]
    if recorded_derived != fresh_derived:
        errors.append(
            "the lesson preflight is STALE: its derived requirement identifiers do not match a "
            "fresh derivation")
    return errors


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

    try:
        guardrails = load_guardrails(root)
    except LedgerError as exc:
        errors.append(str(exc))
        guardrails = {}
    registry_backlinks = {
        identifier: [str(item) for item in entry.get("lessons") or []]
        for identifier, entry in guardrails.items()
    }
    test_ids = suite_test_ids(root)

    known_ids = {str(lesson.get("lessonId")) for lesson in lessons}
    for identifier, entry in sorted(guardrails.items()) if guardrails else []:
        for lesson_id in entry.get("lessons") or []:
            if str(lesson_id) not in known_ids:
                errors.append(
                    f"guardrail {identifier}: names lesson {lesson_id!r}, which is not in the memory")

    resolving = memory_policy_version(root) == RESOLVING_MEMORY_POLICY
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
        controls = preventive_controls(lesson)
        if status == "GUARDED" and not controls:
            errors.append(
                f"{label}: GUARDED requires at least one preventive control of kind "
                f"{', '.join(PREVENTIVE_KINDS)}; documentation alone is not a guardrail")
        if status == "SUPERSEDED" and not lesson.get("supersededBy"):
            errors.append(f"{label}: SUPERSEDED requires supersededBy")

        # Every declared control is resolved against the repository. A reference that names a test,
        # an invariant or a file that does not exist is a claim, not a guardrail.
        for control in (lesson.get("prevention") or []) if resolving else []:
            if not isinstance(control, dict):
                continue
            message = resolve_control(root, control)
            if message is not None:
                errors.append(f"{label}: {message}")

        # A GUARDED lesson must point at the guardrail registry, and the registry entry must exist,
        # name this lesson back, and be verified by a test that exists.
        declared_guardrails = [str(item) for item in lesson.get("guardrails") or []]
        if resolving and status == "GUARDED" and not declared_guardrails:
            errors.append(
                f"{label}: GUARDED requires at least one guardrailId from "
                f"{GUARDRAIL_REGISTRY_FILE}")
        for identifier in declared_guardrails if resolving else []:
            entry = guardrails.get(identifier)
            if entry is None:
                errors.append(f"{label}: guardrail {identifier!r} is not in the guardrail registry")
                continue
            if identifier not in registry_backlinks or str(lesson.get("lessonId")) not in [
                    str(item) for item in entry.get("lessons") or []]:
                errors.append(
                    f"{label}: guardrail {identifier!r} does not list this lesson, so the link is "
                    f"one-directional and cannot be audited")
            verified_by = [str(item) for item in entry.get("verifiedBy") or []]
            if not verified_by:
                errors.append(
                    f"{label}: guardrail {identifier!r} declares no verifying test, so nothing "
                    f"fails when the control is removed")
            for test_id in verified_by:
                if test_id not in test_ids:
                    errors.append(
                        f"{label}: guardrail {identifier!r} is verified by {test_id!r}, which does "
                        f"not exist in the suite")

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
        if unresolved_guardrail_failures(lesson) and status == "GUARDED":
            errors.append(
                f"{label}: a guardrail failure must reopen the lesson; GUARDED is not a valid status "
                f"while a GUARDRAIL_FAILURE is unresolved")

        # A lesson may only cite a checkpoint that records the finding it names. The audit found a
        # locator that pointed at the wrong checkpoint while the lesson itself was sound.
        message = _resolve_source_locator(root, lesson) if resolving else None
        if message is not None:
            errors.append(f"{label}: {message}")

        # The whole lesson object is scanned, at any depth. The audit planted a secret-shaped value
        # in prevention.description and the old field list never looked there.
        for location, value in _walk_strings(lesson):
            for finding in find_secrets(value):
                errors.append(f"{label}: secret pattern detected in {location}: {finding}")

        for reference in (lesson.get("evidence") or []) if resolving else []:
            message = resolve_lesson_evidence(root, reference)
            if message is not None:
                errors.append(f"{label}: {message}")

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
