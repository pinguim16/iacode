"""Shared, standard-library-only support for the IACode Development Ledger."""

from __future__ import annotations

import json
import re
import subprocess
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "1.0.0"
STATUSES = (
    "NOT_STARTED",
    "BASELINING",
    "IN_PROGRESS",
    "BLOCKED",
    "READY_FOR_REVIEW",
    "REWORK_REQUIRED",
    "READY_FOR_RED_TEAM",
    "GATE_PASS",
    "GATE_FAIL",
)

REQUIRED_CHECKPOINT_FILES = (
    "STATUS.md",
    "HANDOFF.md",
    "RUN-METADATA.json",
    "STATE.json",
    "PLAN.md",
    "DECISIONS.md",
    "COMMANDS.jsonl",
    "FILES.json",
    "TESTS.json",
    "QUALITY.json",
    "PROVENANCE.json",
    "DIFF-SUMMARY.md",
    "RISKS.md",
    "NEXT.md",
)

SCHEMA_BINDINGS = {
    "STATE.json": "checkpoint.schema.json",
    "RUN-METADATA.json": "run-metadata.schema.json",
    "TESTS.json": "test-result.schema.json",
    "QUALITY.json": "quality-result.schema.json",
    "PROVENANCE.json": "provenance.schema.json",
}


class LedgerError(RuntimeError):
    """A user-actionable ledger validation or operation error."""


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def find_root(start: Path | None = None) -> Path:
    candidate = (start or Path.cwd()).resolve()
    for path in (candidate, *candidate.parents):
        if (path / ".iacode").is_dir():
            return path
    raise LedgerError(f"repository root not found from {candidate}")


def run_git(root: Path, *args: str) -> tuple[int, str]:
    completed = subprocess.run(
        ["git", *args],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    return completed.returncode, completed.stdout.strip()


def git_snapshot(root: Path) -> dict[str, Any]:
    branch_code, branch = run_git(root, "branch", "--show-current")
    head_code, head = run_git(root, "rev-parse", "HEAD")
    status_code, status = run_git(root, "status", "--porcelain")
    if branch_code != 0 or status_code != 0:
        raise LedgerError("Git repository state is unavailable")
    return {
        "branch": branch or "DETACHED",
        "head": head if head_code == 0 else "UNBORN",
        "dirty": bool(status),
    }


def resolve_latest(root: Path) -> Path:
    latest = root / "docs" / "checkpoints" / "LATEST.md"
    if not latest.is_file():
        raise LedgerError("docs/checkpoints/LATEST.md is missing")
    text = latest.read_text(encoding="utf-8")
    match = re.search(r"^Checkpoint:\s*`?([^`\r\n]+)`?\s*$", text, re.MULTILINE)
    if not match:
        raise LedgerError("LATEST.md does not contain a 'Checkpoint:' entry")
    target = (root / match.group(1).strip()).resolve()
    checkpoints_root = (root / "docs" / "checkpoints").resolve()
    if checkpoints_root not in target.parents:
        raise LedgerError("LATEST.md points outside docs/checkpoints")
    if not target.is_dir():
        raise LedgerError(f"LATEST.md points to a nonexistent checkpoint: {target}")
    return target


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise LedgerError(f"invalid JSON in {path}: {exc}") from exc


def _resolve_local_ref(schema: dict[str, Any], root_schema: dict[str, Any]) -> dict[str, Any]:
    ref = schema.get("$ref")
    if not ref:
        return schema
    if not ref.startswith("#/"):
        raise LedgerError(f"unsupported schema reference: {ref}")
    value: Any = root_schema
    for component in ref[2:].split("/"):
        component = component.replace("~1", "/").replace("~0", "~")
        value = value[component]
    if not isinstance(value, dict):
        raise LedgerError(f"schema reference does not resolve to an object: {ref}")
    return value


def _matches_type(value: Any, expected: str) -> bool:
    checks = {
        "object": lambda item: isinstance(item, dict),
        "array": lambda item: isinstance(item, list),
        "string": lambda item: isinstance(item, str),
        "integer": lambda item: isinstance(item, int) and not isinstance(item, bool),
        "number": lambda item: isinstance(item, (int, float)) and not isinstance(item, bool),
        "boolean": lambda item: isinstance(item, bool),
        "null": lambda item: item is None,
    }
    return checks.get(expected, lambda _item: False)(value)


def validate_schema(value: Any, schema: dict[str, Any], path: str = "$", root_schema: dict[str, Any] | None = None) -> list[str]:
    root_schema = root_schema or schema
    schema = _resolve_local_ref(schema, root_schema)
    errors: list[str] = []

    expected_type = schema.get("type")
    if expected_type is not None:
        allowed = expected_type if isinstance(expected_type, list) else [expected_type]
        if not any(_matches_type(value, item) for item in allowed):
            return [f"{path}: expected type {allowed}, got {type(value).__name__}"]

    if "const" in schema and value != schema["const"]:
        errors.append(f"{path}: expected constant {schema['const']!r}")
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}: value {value!r} is not in the allowed enum")

    if isinstance(value, dict):
        required = schema.get("required", [])
        for key in required:
            if key not in value:
                errors.append(f"{path}: missing required property {key!r}")
        properties = schema.get("properties", {})
        for key, item in value.items():
            if key in properties:
                errors.extend(validate_schema(item, properties[key], f"{path}.{key}", root_schema))
            elif schema.get("additionalProperties") is False:
                errors.append(f"{path}: unexpected property {key!r}")

    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0):
            errors.append(f"{path}: expected at least {schema['minItems']} items")
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, item in enumerate(value):
                errors.extend(validate_schema(item, item_schema, f"{path}[{index}]", root_schema))

    if isinstance(value, str):
        if len(value) < schema.get("minLength", 0):
            errors.append(f"{path}: string is shorter than {schema['minLength']}")
        pattern = schema.get("pattern")
        if pattern and re.search(pattern, value) is None:
            errors.append(f"{path}: value does not match {pattern!r}")
        format_name = schema.get("format")
        try:
            if format_name == "date-time":
                if re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})", value) is None:
                    raise ValueError("not RFC 3339")
                parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
                if parsed.tzinfo is None:
                    raise ValueError("timezone required")
            elif format_name == "date":
                if re.fullmatch(r"\d{4}-\d{2}-\d{2}", value) is None:
                    raise ValueError("not an ISO date")
                date.fromisoformat(value)
        except ValueError:
            errors.append(f"{path}: invalid {format_name} value")

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            errors.append(f"{path}: value is below minimum {schema['minimum']}")

    return errors


SECRET_PATTERNS: tuple[tuple[str, re.Pattern[str], str], ...] = (
    (
        "authorization header",
        re.compile(r"(?i)(authorization[\"']?\s*:\s*[\"']?)(?!\[REDACTED\])(?:(?:Bearer|Basic)\s+)?[-A-Za-z0-9._~+/=]{6,}"),
        r"\1[REDACTED]",
    ),
    (
        "bearer credential",
        re.compile(r"(?i)\bBearer\s+(?!\[REDACTED\]|credentials?\b|tokens?\b|authentication\b)[-A-Za-z0-9._~+/=]{8,}"),
        "Bearer [REDACTED]",
    ),
    (
        "named secret assignment",
        re.compile(r"(?i)\b((?:[A-Z0-9]+_)*(?:API_KEY|TOKEN|SECRET|PASSWORD|ACCESS_KEY_ID|SECRET_ACCESS_KEY)[\"']?\s*[:=]\s*[\"']?)(?!\[REDACTED\]|example\b|placeholder\b|changeme\b|not[_-]?set\b|your[_-])[-A-Za-z0-9._~+/=:@]{6,}"),
        r"\1[REDACTED]",
    ),
    ("DevWorld credential", re.compile(r"\bdw_live_[A-Za-z0-9_-]{8,}\b"), "[REDACTED]"),
    ("OpenAI-style key", re.compile(r"\bsk-[A-Za-z0-9_-]{12,}\b"), "[REDACTED]"),
    ("GitHub credential", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"), "[REDACTED]"),
    ("GitHub fine-grained credential", re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"), "[REDACTED]"),
    (
        "private SSH key block",
        re.compile(r"-----BEGIN ((?:OPENSSH|RSA|EC|DSA) PRIVATE KEY)-----[\s\S]*?-----END \1-----", re.IGNORECASE),
        "[REDACTED]",
    ),
    (
        "private SSH key header",
        re.compile(r"-----BEGIN (?:OPENSSH|RSA|EC|DSA) PRIVATE KEY-----", re.IGNORECASE),
        "[REDACTED]",
    ),
)


def find_secrets(text: str) -> list[str]:
    return [name for name, pattern, _replacement in SECRET_PATTERNS if pattern.search(text)]


def redact_text(text: str) -> str:
    result = text
    for _name, pattern, replacement in SECRET_PATTERNS:
        result = pattern.sub(replacement, result)
    return result
