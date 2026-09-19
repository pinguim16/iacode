#!/usr/bin/env python3
"""Validate an IACode checkpoint and its relationship to the repository."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from ledger_common import (
    REQUIRED_CHECKPOINT_FILES,
    SCHEMA_BINDINGS,
    LedgerError,
    find_root,
    find_secrets,
    git_snapshot,
    load_json,
    resolve_latest,
    validate_schema,
)


def validate_checkpoint(root: Path, checkpoint: Path | None = None, allow_dirty: bool = False) -> list[str]:
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
    for schema_name in set(SCHEMA_BINDINGS.values()) | {"command.schema.json"}:
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
    if commands_path.is_file():
        for line_number, line in enumerate(commands_path.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            try:
                command = json.loads(line)
                for error in validate_schema(command, schemas.get("command.schema.json", {})):
                    errors.append(f"COMMANDS.jsonl:{line_number}: {error}")
            except json.JSONDecodeError as exc:
                errors.append(f"COMMANDS.jsonl:{line_number}: invalid JSON: {exc}")

    files_path = target / "FILES.json"
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
        except LedgerError as exc:
            errors.append(str(exc))

    for path in target.rglob("*"):
        if path.is_file():
            try:
                findings = find_secrets(path.read_text(encoding="utf-8"))
                for finding in findings:
                    errors.append(f"secret pattern detected in {path.name}: {finding}")
            except UnicodeDecodeError:
                errors.append(f"binary or non-UTF-8 checkpoint file is not allowed: {path.name}")

    state = documents.get("STATE.json")
    if isinstance(state, dict):
        try:
            actual = git_snapshot(root)
            if state.get("branch") != actual["branch"]:
                errors.append(f"branch mismatch: expected {state.get('branch')!r}, observed {actual['branch']!r}")
            expected_commit = state.get("currentCommit")
            if expected_commit == "HEAD":
                if actual["head"] == "UNBORN":
                    errors.append("currentCommit is HEAD but repository has no commit")
            elif expected_commit != actual["head"]:
                errors.append(f"commit mismatch: expected {expected_commit!r}, observed {actual['head']!r}")
            if not allow_dirty and state.get("dirty") != actual["dirty"]:
                errors.append(f"dirty-state mismatch: expected {state.get('dirty')!r}, observed {actual['dirty']!r}")
        except LedgerError as exc:
            errors.append(str(exc))

    handoff = target / "HANDOFF.md"
    next_file = target / "NEXT.md"
    if handoff.is_file() and len(handoff.read_text(encoding="utf-8").strip()) < 80:
        errors.append("HANDOFF.md is not meaningfully populated")
    if next_file.is_file() and len(next_file.read_text(encoding="utf-8").strip()) < 40:
        errors.append("NEXT.md is not meaningfully populated")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, help="repository root; defaults to auto-detection")
    parser.add_argument("--checkpoint", type=Path, help="checkpoint directory; must equal LATEST")
    parser.add_argument("--allow-dirty", action="store_true", help="skip dirty-state equality during pre-commit finalization")
    args = parser.parse_args()

    try:
        root = find_root(args.root) if args.root else find_root()
        checkpoint = args.checkpoint
        if checkpoint and not checkpoint.is_absolute():
            checkpoint = root / checkpoint
        errors = validate_checkpoint(root, checkpoint, args.allow_dirty)
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

