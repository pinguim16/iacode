#!/usr/bin/env python3
"""Validate an IACode checkpoint and its relationship to the repository."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from ledger_common import (
    REQUIRED_CHECKPOINT_FILES,
    SCHEMA_BINDINGS,
    STATUSES,
    LedgerError,
    find_root,
    find_secrets,
    git_snapshot,
    load_json,
    resolve_latest,
    run_git,
    validate_schema,
)


HANDOFF_HEADINGS = (
    "## Objective",
    "## What was completed",
    "## What was NOT completed",
    "## Current repository state",
    "## Files changed",
    "## Important decisions",
    "## Tests executed",
    "## Known failures",
    "## Known risks",
    "## Do not repeat",
    "## Required next action",
    "## Exact continuation sequence",
    "## Validation commands",
    "## Stop conditions",
)

FINAL_REPORT_HEADINGS = (
    "## Status",
    "## Environment",
    "## Tool / Model / Effort",
    "## Deliverables",
    "## Files Created",
    "## Files Modified",
    "## Validation",
    "## Tests",
    "## Red Team",
    "## Known Risks",
    "## Remaining Work",
    "## Handoff Readiness",
    "## Next Gate",
    "## Evidence",
)


def _all_strings(value: Any):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for key, item in value.items():
            yield str(key)
            yield from _all_strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from _all_strings(item)


def _parse_datetime(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})", value) is None:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo is not None else None


def _canonical_hash(path: Path) -> str:
    try:
        content = path.read_text(encoding="utf-8").replace("\r\n", "\n").encode("utf-8")
    except UnicodeDecodeError:
        content = path.read_bytes()
    return hashlib.sha256(content).hexdigest()


def _resolve_expected_commit(root: Path, expected: Any, actual_head: str, allow_pending_ref: bool) -> str | None:
    if expected == "HEAD":
        return actual_head if actual_head != "UNBORN" else None
    if expected == "UNBORN":
        return "UNBORN"
    if isinstance(expected, str) and expected.startswith("refs/tags/iacode-checkpoints/"):
        code, resolved = run_git(root, "rev-parse", "--verify", f"{expected}^{{commit}}")
        if code != 0:
            return actual_head if allow_pending_ref else None
        return resolved
    return expected if isinstance(expected, str) else None


def validate_checkpoint(
    root: Path,
    checkpoint: Path | None = None,
    allow_dirty: bool = False,
    allow_pending_ref: bool = False,
) -> list[str]:
    errors: list[str] = []
    try:
        latest_checkpoint = resolve_latest(root)
    except LedgerError as exc:
        return [str(exc)]

    target = (checkpoint or latest_checkpoint).resolve()
    if target != latest_checkpoint:
        errors.append(f"requested checkpoint is not the LATEST target: {target}")
    if not target.is_dir():
        return errors + [f"checkpoint directory does not exist: {target}"]

    for name in REQUIRED_CHECKPOINT_FILES:
        path = target / name
        if not path.is_file():
            errors.append(f"missing required checkpoint file: {name}")
        elif path.stat().st_size == 0:
            errors.append(f"required checkpoint file is empty: {name}")

    schemas_dir = root / ".iacode" / "schemas"
    schemas: dict[str, dict] = {}
    required_schema_names = set(SCHEMA_BINDINGS.values()) | {
        "command.schema.json",
        "decision.schema.json",
        "experience.schema.json",
    }
    for schema_name in required_schema_names:
        schema_path = schemas_dir / schema_name
        try:
            schema = load_json(schema_path)
            if not isinstance(schema, dict) or "$schema" not in schema or "type" not in schema:
                errors.append(f"schema is not a usable JSON Schema document: {schema_name}")
            else:
                schemas[schema_name] = schema
        except LedgerError as exc:
            errors.append(str(exc))

    documents: dict[str, object] = {}
    for filename, schema_name in SCHEMA_BINDINGS.items():
        path = target / filename
        if not path.is_file():
            continue
        try:
            document = load_json(path)
            documents[filename] = document
            if schema_name in schemas:
                for error in validate_schema(document, schemas[schema_name]):
                    errors.append(f"{filename}: {error}")
        except LedgerError as exc:
            errors.append(str(exc))

    commands_path = target / "COMMANDS.jsonl"
    command_count = 0
    if commands_path.is_file():
        for line_number, line in enumerate(commands_path.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            command_count += 1
            try:
                command = json.loads(line)
                for error in validate_schema(command, schemas.get("command.schema.json", {})):
                    errors.append(f"COMMANDS.jsonl:{line_number}: {error}")
                for value in _all_strings(command):
                    for finding in find_secrets(value):
                        errors.append(f"secret pattern detected in COMMANDS.jsonl:{line_number}: {finding}")
            except json.JSONDecodeError as exc:
                errors.append(f"COMMANDS.jsonl:{line_number}: invalid JSON: {exc}")
        if command_count == 0:
            errors.append("COMMANDS.jsonl contains no command records")

    files_path = target / "FILES.json"
    files: dict[str, Any] | None = None
    if files_path.is_file():
        try:
            files = load_json(files_path)
            for key in ("filesRead", "filesCreated", "filesModified", "filesDeleted"):
                if not isinstance(files, dict) or not isinstance(files.get(key), list):
                    errors.append(f"FILES.json: {key} must be an array")
                else:
                    for index, item in enumerate(files[key]):
                        if not isinstance(item, dict) or not item.get("path") or not item.get("reason"):
                            errors.append(f"FILES.json: {key}[{index}] requires path and reason")
                            continue
                        expected_hash = item.get("hashAfter")
                        if expected_hash:
                            candidate = (root / item["path"]).resolve()
                            if root.resolve() not in candidate.parents:
                                errors.append(f"FILES.json: {key}[{index}] path escapes repository")
                            elif not candidate.is_file():
                                errors.append(f"FILES.json: hashed path does not exist: {item['path']}")
                            else:
                                observed_hash = _canonical_hash(candidate)
                                if observed_hash != expected_hash:
                                    errors.append(f"FILES.json: hash mismatch for {item['path']}")
        except LedgerError as exc:
            errors.append(str(exc))

    for path in root.rglob("*"):
        if path.is_file() and ".git" not in path.parts and "__pycache__" not in path.parts:
            try:
                text = path.read_text(encoding="utf-8")
                findings = set(find_secrets(text))
                if path.suffix.lower() == ".json":
                    try:
                        decoded = json.loads(text)
                        for value in _all_strings(decoded):
                            findings.update(find_secrets(value))
                    except json.JSONDecodeError:
                        pass
                for finding in findings:
                    errors.append(f"secret pattern detected in {path.relative_to(root)}: {finding}")
            except UnicodeDecodeError:
                continue

    state = documents.get("STATE.json")
    metadata = documents.get("RUN-METADATA.json")
    tests = documents.get("TESTS.json")
    quality = documents.get("QUALITY.json")
    if isinstance(state, dict):
        try:
            actual = git_snapshot(root)
            if state.get("branch") != actual["branch"]:
                errors.append(f"branch mismatch: expected {state.get('branch')!r}, observed {actual['branch']!r}")
            expected_commit = state.get("currentCommit")
            resolved_commit = _resolve_expected_commit(root, expected_commit, actual["head"], allow_pending_ref)
            if resolved_commit is None:
                errors.append(f"commit reference cannot be resolved: {expected_commit!r}")
            elif resolved_commit != actual["head"]:
                errors.append(f"commit mismatch: expected {expected_commit!r} -> {resolved_commit!r}, observed {actual['head']!r}")
            if not allow_dirty and state.get("dirty") != actual["dirty"]:
                errors.append(f"dirty-state mismatch: expected {state.get('dirty')!r}, observed {actual['dirty']!r}")
        except LedgerError as exc:
            errors.append(str(exc))

        status_text = (target / "STATUS.md").read_text(encoding="utf-8") if (target / "STATUS.md").is_file() else ""
        status_match = re.search(r"\b(" + "|".join(STATUSES) + r")\b", status_text)
        if not status_match:
            errors.append("STATUS.md does not contain a canonical status")
        elif status_match.group(1) != state.get("status"):
            errors.append(f"status mismatch: STATE.json={state.get('status')!r}, STATUS.md={status_match.group(1)!r}")

        started = _parse_datetime(state.get("startedAt"))
        updated = _parse_datetime(state.get("updatedAt"))
        if started is None or updated is None or updated < started:
            errors.append("STATE.json timestamps are not ordered RFC 3339 values")
        if state.get("status") in ("READY_FOR_REVIEW", "READY_FOR_RED_TEAM", "GATE_PASS", "GATE_FAIL") and state.get("currentCommit") in ("HEAD", "UNBORN"):
            errors.append(f"{state.get('status')} must be anchored to an exact commit or checkpoint tag, not HEAD/UNBORN")

    if isinstance(metadata, dict) and isinstance(state, dict):
        if metadata.get("branch") != state.get("branch"):
            errors.append("RUN-METADATA.json branch does not match STATE.json")
        if metadata.get("initialCommit") != state.get("baseCommit"):
            errors.append("RUN-METADATA.json initialCommit does not match STATE.json baseCommit")
        if metadata.get("finalCommit") != state.get("currentCommit"):
            errors.append("RUN-METADATA.json finalCommit does not match STATE.json currentCommit")
        started = _parse_datetime(metadata.get("startedAt"))
        finished = _parse_datetime(metadata.get("finishedAt"))
        if started is None or finished is None or finished < started:
            errors.append("RUN-METADATA.json timestamps are not ordered RFC 3339 values")

    if isinstance(tests, dict) and isinstance(quality, dict):
        for test_key, quality_key in (("unit", "unitTests"), ("integration", "integrationTests"), ("e2e", "e2e")):
            result = tests.get(test_key)
            verdict = quality.get(quality_key)
            if isinstance(result, dict):
                if not result.get("executed") and (result.get("passed", 0) or result.get("failed", 0)):
                    errors.append(f"TESTS.json {test_key} has counts but executed is false")
                if verdict == "PASS" and (
                    not result.get("executed")
                    or result.get("failed") != 0
                    or result.get("passed", 0) < 1
                    or not result.get("command")
                    or not result.get("evidence")
                ):
                    errors.append(f"QUALITY.json {quality_key}=PASS contradicts TESTS.json {test_key}")

    handoff = target / "HANDOFF.md"
    next_file = target / "NEXT.md"
    if handoff.is_file():
        handoff_text = handoff.read_text(encoding="utf-8")
        if len(handoff_text.strip()) < 80:
            errors.append("HANDOFF.md is not meaningfully populated")
        for heading in HANDOFF_HEADINGS:
            if heading not in handoff_text:
                errors.append(f"HANDOFF.md is missing heading: {heading}")
    if next_file.is_file():
        next_text = next_file.read_text(encoding="utf-8")
        if len(next_text.strip()) < 40 or "# Next" not in next_text or not any(
            heading in next_text for heading in ("## Required next action", "## Next Gate")
        ):
            errors.append("NEXT.md is not meaningfully populated")

    if isinstance(state, dict) and state.get("status") == "GATE_PASS":
        if state.get("dirty") is not False:
            errors.append("GATE_PASS requires dirty=false")
        if state.get("blockedBy"):
            errors.append("GATE_PASS requires blockedBy to be empty")
        if isinstance(quality, dict):
            for key, verdict in quality.items():
                if key != "schemaVersion" and verdict in ("FAIL", "NOT_EXECUTED"):
                    errors.append(f"GATE_PASS cannot have QUALITY.json {key}={verdict}")
            for key in ("security", "documentation", "checkpointValidation", "redTeam"):
                if quality.get(key) != "PASS":
                    errors.append(f"GATE_PASS requires QUALITY.json {key}=PASS")
        else:
            errors.append("GATE_PASS requires valid QUALITY.json")

        final_report = target / "FINAL-REPORT.md"
        resume_validation = target / "RESUME-VALIDATION.md"
        for required_final in (final_report, resume_validation):
            if not required_final.is_file() or not required_final.read_text(encoding="utf-8").strip():
                errors.append(f"GATE_PASS requires {required_final.name}")
        if final_report.is_file():
            report_text = final_report.read_text(encoding="utf-8")
            for heading in FINAL_REPORT_HEADINGS:
                if heading not in report_text:
                    errors.append(f"FINAL-REPORT.md is missing heading: {heading}")
            if "GATE_PASS" not in report_text or "RED_TEAM_PASS" not in report_text:
                errors.append("FINAL-REPORT.md lacks GATE_PASS or RED_TEAM_PASS evidence")
        if resume_validation.is_file() and "SECOND_TOOL_VALIDATION = PENDING_MANUAL" not in resume_validation.read_text(encoding="utf-8"):
            errors.append("RESUME-VALIDATION.md lacks the required second-tool status")

        if state.get("baseCommit") == "UNBORN" and isinstance(files, dict):
            code, tracked_output = run_git(root, "ls-files")
            if code != 0:
                errors.append("unable to enumerate tracked files for empty-project completeness")
            else:
                tracked = {line.replace("\\", "/") for line in tracked_output.splitlines() if line}
                created_items = files.get("filesCreated", [])
                created = {item.get("path", "").replace("\\", "/") for item in created_items if isinstance(item, dict)}
                missing = sorted(tracked - created)
                if missing:
                    errors.append("FILES.json omits tracked files created from EMPTY_PROJECT: " + ", ".join(missing))
                for item in created_items:
                    if isinstance(item, dict) and item.get("path") != str(files_path.relative_to(root)).replace("\\", "/") and not item.get("hashAfter"):
                        errors.append(f"FILES.json created entry lacks hashAfter: {item.get('path')}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, help="repository root; defaults to auto-detection")
    parser.add_argument("--checkpoint", type=Path, help="checkpoint directory; must equal LATEST")
    args = parser.parse_args()

    try:
        root = find_root(args.root) if args.root else find_root()
        checkpoint = args.checkpoint
        if checkpoint and not checkpoint.is_absolute():
            checkpoint = root / checkpoint
        errors = validate_checkpoint(root, checkpoint)
    except LedgerError as exc:
        errors = [str(exc)]

    if errors:
        print("CHECKPOINT_INVALID")
        for error in errors:
            print(f"- {error}")
        return 1
    print("CHECKPOINT_VALID")
    return 0


if __name__ == "__main__":
    sys.exit(main())
