"""Shared, standard-library-only support for the IACode Development Ledger."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "1.0.0"
LEGACY_SCHEMA_VERSION = "1.0.0"
EVIDENCE_SCHEMA_VERSION = "2.0.0"
DELIVERY_SCHEMA_VERSION = "3.0.0"
MEMORY_SCHEMA_VERSION = "3.1.0"
CLOSURE_SCHEMA_VERSION = "3.2.0"
CURRENT_SCHEMA_VERSION = CLOSURE_SCHEMA_VERSION
SUPPORTED_SCHEMA_VERSIONS = (
    LEGACY_SCHEMA_VERSION,
    EVIDENCE_SCHEMA_VERSION,
    DELIVERY_SCHEMA_VERSION,
    MEMORY_SCHEMA_VERSION,
    CLOSURE_SCHEMA_VERSION,
)

# Versions that carry the delivery-assurance gates. 3.1.0 adds the engineering memory preflight and
# the milestone validation policy on top of them; 3.2.0 adds the M0 closure controls: derived
# expected requirement sets, the closed mandatory gate set, preflight freshness, external audit
# attestations, checkpoint integrity anchors and derived counts.
DELIVERY_SCHEMA_VERSIONS = (DELIVERY_SCHEMA_VERSION, MEMORY_SCHEMA_VERSION, CLOSURE_SCHEMA_VERSION)

# Versions that carry the engineering memory and the milestone validation policy.
MEMORY_SCHEMA_VERSIONS = (MEMORY_SCHEMA_VERSION, CLOSURE_SCHEMA_VERSION)

# Versions that carry the M0 closure controls.
CLOSURE_SCHEMA_VERSIONS = (CLOSURE_SCHEMA_VERSION,)

QUALITY_DIMENSIONS = (
    "build",
    "unitTests",
    "integrationTests",
    "e2e",
    "lint",
    "staticAnalysis",
    "security",
    "documentation",
    "checkpointValidation",
    "redTeam",
)

# Delivery-assurance gates introduced with schemaVersion 3.0.0.
DELIVERY_ASSURANCE_DIMENSIONS = ("greenKeeper", "deliveryCompleteness")

QUALITY_DIMENSIONS_V3 = QUALITY_DIMENSIONS + DELIVERY_ASSURANCE_DIMENSIONS

# Dimensions produced by the independent run, after the implementing run hands off. They are the
# only dimensions allowed to be NOT_EXECUTED at READY_FOR_REVIEW.
INDEPENDENT_DIMENSIONS = ("redTeam",)

QUALITY_OUTCOMES = ("PASS", "FAIL", "NOT_APPLICABLE", "NOT_EXECUTED")

GATE_OUTCOMES = ("PASS", "FAIL", "NOT_EXECUTED")

SECOND_TOOL_STATUSES = ("PENDING_MANUAL", "PASSED", "FAILED", "NOT_REQUIRED")

REQUIREMENT_STATUSES = (
    "NOT_STARTED",
    "IN_PROGRESS",
    "COMPLETE",
    "PARTIAL",
    "MISSING",
    "NOT_APPLICABLE",
)

# Statuses that assert the work is ready to leave the implementing run. A non-empty blockedBy is
# incompatible with every one of them, for every schema version.
UNBLOCKED_STATUSES = (
    "READY_FOR_REVIEW",
    "READY_FOR_RED_TEAM",
    "INTERNAL_GATE_PASS",
    "MILESTONE_EXTERNAL_PASS",
    "GATE_PASS",
)

INDEPENDENT_VERDICT_STATUSES = ("PENDING", "APPROVED", "REWORK_REQUIRED", "NOT_REQUIRED")
RED_TEAM_VERDICT_STATUSES = ("PENDING", "RED_TEAM_PASS", "RED_TEAM_FAIL", "NOT_REQUIRED")

# Canonical outcome vocabulary for a recorded operation. PRECONDITION_REJECTED exists so a refusal
# that never launched a process is recorded without fabricating an exit code.
COMMAND_RESULTS = ("COMPLETED", "PRECONDITION_REJECTED", "ABORTED")

RESULT_CODES = {
    "OK": "The operation ran to completion; exitCode carries the process result.",
    "E_NOT_LATEST_CHECKPOINT": "Refused: the requested checkpoint is not the LATEST target.",
    "E_DETACHED_HEAD": "Refused: finalization requires an attached branch.",
    "E_INVALID_COMMIT_REF": "Refused: the commit reference is not a canonical checkpoint tag.",
    "E_VALIDATION_FAILED": "The operation ran and its own validation rejected the result.",
    "E_ABORTED": "The operation was interrupted before producing a result.",
}

# The only checkpoint file excluded from content hashing, because a file cannot
# contain its own hash. Its integrity is bound by the checkpoint commit and tag,
# by its required presence, and by its schema and inventory rules.
# See docs/adr/ADR-0006-checkpoint-inventory-binding.md.
INVENTORY_SELF_REFERENTIAL_FILES = ("FILES.json",)
STATUSES = (
    "NOT_STARTED",
    "BASELINING",
    "IN_PROGRESS",
    "BLOCKED",
    "READY_FOR_REVIEW",
    "REWORK_REQUIRED",
    "READY_FOR_RED_TEAM",
    "INTERNAL_GATE_PASS",
    "MILESTONE_EXTERNAL_PASS",
    "GATE_PASS",
    "GATE_FAIL",
)

# A Gate approved by the project's own controls. It is not, and may not be described as, independent
# external validation. Only MILESTONE_EXTERNAL_PASS carries that meaning.
INTERNAL_PASS_STATUS = "INTERNAL_GATE_PASS"
EXTERNAL_PASS_STATUS = "MILESTONE_EXTERNAL_PASS"

# External independent validation happens per milestone, not per Gate. The auditor evaluates the
# milestone as a whole, including integration between its Gates.
MILESTONES = (
    ("M0", "Development control plane", ("SETUP-00",)),
    ("M1", "IACode V0 foundation", ("GATE 0", "GATE 1", "GATE 2", "GATE 3")),
    ("M2", "IACode V0 completion and experience", ("GATE 4", "GATE 5", "GATE 6", "GATE 7")),
    ("M3", "Code graph, memory and gap detection", ("GATE 8", "GATE 9", "GATE 10", "GATE 11")),
    ("M4", "Skills and dataset production", ("GATE 12", "GATE 13", "GATE 14", "GATE 15")),
    ("M5", "Dataset audit and model adaptation", ("GATE 16", "GATE 17", "GATE 18", "GATE 19")),
    ("M6", "Evaluation, shadow mode and promotion", ("GATE 20", "GATE 21", "GATE 22", "GATE 23")),
)

MILESTONE_STATUSES = ("PENDING", "PASSED", "FAILED", "NOT_REQUIRED")

# An extraordinary audit before the milestone is allowed only for a recorded reason in this set.
EXTERNAL_AUDIT_TRIGGERS = (
    "security-boundary",
    "sandbox-boundary",
    "rights-or-provenance-change",
    "training-data-policy",
    "training-execution",
    "promotion-logic",
    "secret-handling",
    "destructive-persistence",
)


def normalize_gate(name: str) -> str:
    return re.sub(r"[^A-Z0-9]", "", str(name).upper())


def milestone_for(gate: str) -> tuple[str, str, tuple[str, ...]] | None:
    """The milestone a Gate belongs to, or None when the Gate is not in the plan."""
    target = normalize_gate(gate)
    for identifier, title, gates in MILESTONES:
        if target in {normalize_gate(item) for item in gates}:
            return identifier, title, gates
    return None


def requires_external_validation(gate: str, external_audit_required: bool = False) -> bool:
    """External independent validation is due at the end of a milestone, not after every Gate.

    An intermediate Gate closes on the project's own controls. An extraordinary audit may still be
    requested earlier, but only through a recorded reason, which is what ``external_audit_required``
    represents. A Gate outside the plan is treated conservatively as requiring validation.
    """
    if external_audit_required:
        return True
    planned = milestone_for(gate)
    if planned is None:
        return True
    return normalize_gate(gate) == normalize_gate(planned[2][-1])

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


def run_git_bytes(root: Path, *args: str) -> tuple[int, bytes]:
    completed = subprocess.run(
        ["git", *args],
        cwd=root,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return completed.returncode, completed.stdout


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
        "detached": not branch,
    }


def canonical_hash_bytes(content: bytes) -> str:
    """Hash content with line endings normalized so checkouts stay portable."""
    try:
        normalized = content.decode("utf-8").replace("\r\n", "\n").encode("utf-8")
    except UnicodeDecodeError:
        normalized = content
    return hashlib.sha256(normalized).hexdigest()


def canonical_hash_path(path: Path) -> str:
    return canonical_hash_bytes(path.read_bytes())


def blob_hash(root: Path, commit: str, relative_path: str) -> str | None:
    """Canonical hash of a tracked path as it existed at a commit, or None."""
    code, content = run_git_bytes(root, "show", f"{commit}:{relative_path}")
    if code != 0:
        return None
    return canonical_hash_bytes(content)


def _split_nul(payload: bytes) -> list[str]:
    return [item for item in payload.decode("utf-8", "surrogateescape").split("\0") if item]


def git_delta(root: Path, base: str, ref: str | None = None) -> dict[str, str]:
    """Change set from base to ref, or from base to the working tree when ref is None.

    Returns a mapping of repository-relative POSIX path to 'A', 'M', or 'D'.
    Renames are reported as an addition plus a deletion so the inventory stays explicit.
    """
    arguments = ["diff", "--name-status", "--no-renames", "-z", base]
    if ref is not None:
        arguments.append(ref)
    code, payload = run_git_bytes(root, *arguments)
    if code != 0:
        raise LedgerError(f"unable to compute the change set from {base}")
    fields = _split_nul(payload)
    delta: dict[str, str] = {}
    for index in range(0, len(fields) - 1, 2):
        status = fields[index][:1]
        path = fields[index + 1].replace("\\", "/")
        if status in ("A", "M", "D"):
            delta[path] = status
        elif status in ("C", "R", "T"):
            delta[path] = "M"

    if ref is None:
        code, payload = run_git_bytes(root, "status", "--porcelain=1", "-z", "--untracked-files=all")
        if code != 0:
            raise LedgerError("unable to enumerate untracked files")
        for entry in _split_nul(payload):
            if entry.startswith("?? "):
                delta[entry[3:].replace("\\", "/")] = "A"
    return delta


# Directories and files whose content decides whether a delivery gate result is still valid. A
# Green Keeper PASS, a completeness PASS, a Red Team result and a mirror audit are all statements
# about this content: when it changes, the statement is stale and must be re-established.
# The checkpoint ledger itself is deliberately outside the scope, because recording evidence must
# not invalidate the evidence being recorded.
ASSURANCE_SCOPE_PREFIXES = (
    "scripts/",
    "tests/",
    ".iacode/",
    ".claude/",
    "prompts/",
    "docs/",
)

ASSURANCE_SCOPE_EXCLUSIONS = (
    "docs/checkpoints/",
    "__pycache__/",
)

ASSURANCE_SCOPE_FILES = (
    "START-HERE.md",
    "AGENTS.md",
    "CLAUDE.md",
    "README.md",
    ".gitattributes",
)


def in_assurance_scope(path: str) -> bool:
    normalized = path.replace("\\", "/")
    if any(part in normalized for part in ASSURANCE_SCOPE_EXCLUSIONS):
        return False
    if normalized in ASSURANCE_SCOPE_FILES:
        return True
    return any(normalized.startswith(prefix) for prefix in ASSURANCE_SCOPE_PREFIXES)


def assurance_scope_files(root: Path) -> list[str]:
    """Tracked and untracked-but-not-ignored files whose content the delivery gates judge."""
    code, output = run_git(root, "ls-files", "--cached", "--others", "--exclude-standard")
    if code != 0:
        raise LedgerError("unable to enumerate the assurance scope")
    paths = {line.replace("\\", "/") for line in output.splitlines() if line.strip()}
    # A file that Git still has in the index but that no longer exists on disk contributes nothing
    # to the content the gates judged, and including it would make the fingerprint change the
    # moment the deletion is committed rather than the moment the content changed.
    return sorted(
        path for path in paths
        if in_assurance_scope(path) and (root / path).is_file()
    )


def canonical_digest(value: Any) -> str:
    """SHA-256 over canonical JSON, so a fingerprint does not depend on formatting."""
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def scope_fingerprint(root: Path, extra_paths: list[str] | None = None) -> str:
    """Deterministic fingerprint of the delivery-assurance scope.

    Two runs of the same content produce the same value; any edit inside the scope changes it. A
    gate result that carries a fingerprint different from the current one is stale by construction,
    which is what stops a PASS from surviving the change that invalidated it.
    """
    entries: list[list[str]] = []
    for path in assurance_scope_files(root):
        candidate = root / path
        entries.append([path, canonical_hash_path(candidate) if candidate.is_file() else "ABSENT"])
    for path in sorted(set(extra_paths or [])):
        candidate = root / path
        entries.append([path, canonical_hash_path(candidate) if candidate.is_file() else "ABSENT"])
    return canonical_digest(entries)


def clone_with_worktree(root: Path, destination: Path) -> bool:
    """Clone the repository and bring the clone up to the current working tree.

    A delivery is validated before it is committed, so a clone of ``HEAD`` would test the previous
    revision. This produces a fresh repository whose content is exactly what is about to be sealed,
    which is what a clean-clone check is supposed to answer.
    """
    completed = subprocess.run(
        ["git", "clone", "--quiet", "--no-hardlinks", str(root), str(destination)],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
    if completed.returncode != 0:
        return False
    code, output = run_git(root, "ls-files", "--cached", "--others", "--exclude-standard")
    if code != 0:
        return False
    wanted = {line.replace("\\", "/") for line in output.splitlines() if line.strip()}
    code, output = run_git(destination, "ls-files")
    for relative in {line.replace("\\", "/") for line in output.splitlines() if line.strip()}:
        if relative not in wanted and (destination / relative).is_file():
            (destination / relative).unlink()
    for relative in sorted(wanted):
        source = root / relative
        if not source.is_file():
            continue
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(source.read_bytes())
    for argv in (["add", "-A"],
                 ["-c", "user.name=iacode", "-c", "user.email=iacode@local",
                  "commit", "--quiet", "--allow-empty", "-m", "the content under validation"]):
        if run_git(destination, *argv)[0] != 0:
            return False
    return True


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


def head_commit(root: Path) -> str:
    code, head = run_git(root, "rev-parse", "HEAD")
    return head if code == 0 and head else "UNBORN"


def runtime_label(interpreter: str | None = None) -> str:
    """Human-readable runtime identity for a recorded command, without machine-specific paths."""
    if interpreter in (None, "python", "python3"):
        import platform

        return f"python {platform.python_version()}"
    return interpreter


def next_command_id(commands_path: Path) -> str:
    highest = 0
    count = 0
    if commands_path.is_file():
        for line in commands_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            count += 1
            try:
                identifier = json.loads(line).get("id") or ""
            except json.JSONDecodeError:
                continue
            match = re.fullmatch(r"cmd-(\d+)", identifier)
            if match:
                highest = max(highest, int(match.group(1)))
    return f"cmd-{max(highest, count) + 1:04d}"


def build_command_record(
    root: Path,
    *,
    command: str,
    purpose: str,
    working_directory: str | None = None,
    runtime: str | None = None,
    arguments: list[str] | None = None,
    inputs: list[str] | None = None,
    inputs_digest: list[dict[str, Any]] | None = None,
    subject_commit: str | None = None,
    result: str = "COMPLETED",
    result_code: str = "OK",
    exit_code: int | None = None,
    duration_ms: int = 0,
    stdout_artifact: str | None = None,
    stderr_artifact: str | None = None,
    notes: str | None = None,
    operation: str | None = None,
    phase: str | None = None,
    attempt_id: str | None = None,
    preconditions: list[dict[str, Any]] | None = None,
    failure_reason: str | None = None,
    repository_state: dict[str, Any] | None = None,
    commit: str | None = None,
) -> dict[str, Any]:
    """Assemble an auditable command record. Free text is redacted before it is stored."""
    record: dict[str, Any] = {
        "id": "",
        "timestamp": utc_now(),
        "runtime": runtime or runtime_label(),
        "workingDirectory": working_directory or str(root),
        "command": command,
        "commit": commit or head_commit(root),
        "purpose": purpose,
        "result": result,
        "resultCode": result_code,
        "exitCode": exit_code,
        "durationMs": duration_ms,
        "stdoutArtifact": stdout_artifact,
        "stderrArtifact": stderr_artifact,
    }
    if arguments is not None:
        record["arguments"] = [redact_text(item) for item in arguments]
    if inputs is not None:
        record["inputs"] = list(inputs)
        # A record that names an input but not its content cannot be replayed: the audit replayed
        # commands at their declared commits and found inputs that were only ever in a dirty tree.
        # The digest binds what the command actually read, independently of the commit.
        if inputs_digest is None:
            inputs_digest = [
                {
                    "path": reference,
                    "hash": canonical_hash_path(root / reference)
                    if (root / reference).is_file() else "ABSENT",
                }
                for reference in inputs
            ]
        record["inputsDigest"] = list(inputs_digest)
    if subject_commit is not None:
        record["subjectCommit"] = subject_commit
    if operation is not None:
        record["operation"] = operation
    if phase is not None:
        record["phase"] = phase
    if attempt_id is not None:
        record["attemptId"] = attempt_id
    if preconditions is not None:
        record["preconditions"] = preconditions
    if failure_reason is not None:
        record["failureReason"] = redact_text(failure_reason)
    if repository_state is not None:
        record["repositoryState"] = repository_state
    if notes is not None:
        record["notes"] = redact_text(notes)
    return record


def append_command_record(commands_path: Path, record: dict[str, Any]) -> str:
    record = dict(record)
    record["id"] = record.get("id") or next_command_id(commands_path)
    ordered = {"id": record.pop("id")}
    ordered.update(record)
    with commands_path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(ordered, ensure_ascii=False) + "\n")
    return ordered["id"]


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
