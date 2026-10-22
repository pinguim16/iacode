"""Explicit separately receipted resource phase; historical cleanup stays one-shot."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import uuid
from pathlib import Path

import owned_docker_scope as operator

sys.path.insert(
    0, str(Path(__file__).resolve().parents[1].parents[2] / "scripts/development-ledger")
)
from audit_runner_bridge import Job, run_owned
from ledger_common import find_secrets, load_json, use_utf8_stdout, utc_now, write_json
from native_process import WindowsJob

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]


def checked_path(path, *, required=False):
    """Only unredirected local checkpoint children, with regular unlinked files."""
    path = Path(path)
    if not path.is_relative_to(CHECKPOINT) or path.resolve() != path:
        raise ValueError("RESOURCE_PHASE_PATH_ESCAPE")
    for candidate in (path, *path.parents):
        if candidate == CHECKPOINT.parent:
            break
        if candidate.is_symlink() or candidate.is_junction():
            raise ValueError("REDIRECTED_RESOURCE_PHASE")
        if candidate.is_file() and candidate.stat().st_nlink != 1:
            raise ValueError("LINKED_RESOURCE_PHASE")
    if required and not path.is_file():
        raise ValueError("MISSING_RESOURCE_PHASE_FILE")
    return path


def current_scope_path():
    marker = checked_path(CHECKPOINT / "ACTIVE-DOCKER-PHASE.json", required=True)
    if marker.stat().st_size > 4096:
        raise ValueError("RESOURCE_PHASE_MARKER_SIZE")
    value = load_json(marker)
    if (
        type(value) is not dict
        or set(value) != {"schemaVersion", "phase", "scopePath"}
        or value["schemaVersion"] != "1.0.0"
        or type(value["phase"]) is not str
        or re.fullmatch(r"phase-[0-9]{4}", value["phase"]) is None
    ):
        raise ValueError("RESOURCE_PHASE_MARKER_SCHEMA")
    relative = "resource-phases/" + value["phase"] + "/OWNED-DOCKER-SCOPE.json"
    if value["scopePath"] != relative:
        raise ValueError("RESOURCE_PHASE_MARKER_PATH")
    return checked_path(CHECKPOINT / relative, required=True)


def child_environment():
    path = current_scope_path()
    scope = load_json(path)
    project = scope["inheritedOwnedProject"]
    if (
        re.fullmatch(r"iacode-m2cp3-[a-f0-9]{32}", project) is None
        or scope.get("phase") != path.parent.name
        or project not in scope["registeredProjects"]
    ):
        raise ValueError("RESOURCE_PHASE_OWNER_MISMATCH")
    return {
        **operator.child_environment(path),
        "COMPOSE_PROJECT_NAME": project,
        "IACODE_VERSION": "0.1.0",
    }


def current_owner_file():
    path = checked_path(current_scope_path().parent / "RUNTIME-OWNER.txt", required=True)
    scope = load_json(current_scope_path())
    expected = (
        "COMPOSE_PROJECT_NAME=" + scope["inheritedOwnedProject"] + "\nIACODE_VERSION=0.1.0\n"
    ).encode()
    if path.read_bytes() != expected:
        raise ValueError("RESOURCE_PHASE_RUNTIME_OWNER_MISMATCH")
    return path


def prepare():
    marker = checked_path(CHECKPOINT / "ACTIVE-DOCKER-PHASE.json")
    if marker.exists():
        raise ValueError("DO_NOT_REPLACE_RESOURCE_PHASE_POINTER")
    predecessor = checked_path(CHECKPOINT / "OWNED-DOCKER-SCOPE.json", required=True)
    disposal = checked_path(CHECKPOINT / "OWNED-RESOURCE-CLEANUP.json", required=True)
    prior = load_json(predecessor)
    if (
        prior["status"] not in {"CLEANED", "CLEANED_EXTERNAL_OBSERVATION_CHANGED"}
        or load_json(disposal)["ownedResourceCleanupResult"] != "PASS"
        or Path(prior["privateBuildxConfig"]).exists()
    ):
        raise ValueError("PREDECESSOR_DISPOSAL_REQUIRED")
    old_bytes = {path: path.read_bytes() for path in (predecessor, disposal)}
    phase = "phase-0002"
    directory = checked_path(CHECKPOINT / "resource-phases" / phase)
    if directory.exists():
        raise ValueError("DO_NOT_REPLACE_RESOURCE_PHASE")
    directory.mkdir(parents=True)
    scope_path = directory / "OWNED-DOCKER-SCOPE.json"
    project = "iacode-m2cp3-" + uuid.uuid4().hex
    # Real constructor, with a fresh namespace and its own baseline/cleanup destination.
    operator.prepare(scope_path, project)
    scope = load_json(scope_path)
    scope.update(
        phase=phase,
        predecessorScope="OWNED-DOCKER-SCOPE.json",
        predecessorScopeSha256=hashlib.sha256(old_bytes[predecessor]).hexdigest(),
        predecessorCleanupSha256=hashlib.sha256(old_bytes[disposal]).hexdigest(),
        phaseCreatedAt=utc_now(),
        originalExternalComparisonRewritten=False,
    )
    write_json(scope_path, scope)
    with (directory / "RUNTIME-OWNER.txt").open("xb") as stream:
        stream.write(("COMPOSE_PROJECT_NAME=" + project + "\nIACODE_VERSION=0.1.0\n").encode())
    if any(path.read_bytes() != raw for path, raw in old_bytes.items()):
        raise ValueError("HISTORICAL_RESOURCE_RECEIPT_CHANGED")
    value = {
        "schemaVersion": "1.0.0",
        "phase": phase,
        "scopePath": scope_path.relative_to(CHECKPOINT).as_posix(),
    }
    with marker.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(value, indent=2) + "\n")
    child_environment()
    current_owner_file()
    print(
        json.dumps(
            {
                "phase": phase,
                "project": project,
                "status": scope["status"],
                "predecessorReceiptsUnchanged": True,
                "acceptanceGranted": False,
            }
        )
    )
    return 0


def bootstrap_builder(*, retry=False):
    path = current_scope_path()
    target = path.parent / (
        "BUILDER-BOOTSTRAP-RETRY-0001.json" if retry else "BUILDER-BOOTSTRAP.json"
    )
    if target.exists():
        raise ValueError("DO_NOT_REPLACE_BUILDER_BOOTSTRAP_OBSERVATION")
    if retry and load_json(path.parent / "BUILDER-BOOTSTRAP.json")["result"] != "FAIL":
        raise ValueError("EXPLICIT_FAILED_ORIGINAL_REQUIRED_FOR_RETRY")
    environment = child_environment()
    scope = load_json(path)
    arguments = ["docker", "buildx", "inspect", scope["builder"], "--bootstrap"]
    fact = {
        "startedAt": utc_now(),
        "arguments": arguments,
        "result": "FAIL",
        "producerBudgetSeconds": 60,
    }
    execution, streams = run_owned(
        Job(tuple(arguments), 60), ROOT, environment, find_secrets, WindowsJob
    )
    # Bind the primary producer and independent native cleanup before fallible publication.
    fact.update(
        execution=execution,
        status=execution["producer"]["status"],
        exitCode=execution["producer"]["exitCode"],
        artifacts={},
    )
    write_json(target, fact)
    directory = (
        path.parent / "controls" / ("bootstrap-retry-0001" if retry else "bootstrap-initial")
    )
    directory.mkdir(parents=True, exist_ok=False)
    for name, raw in streams.items():
        artifact = directory / name
        with artifact.open("xb") as stream:
            stream.write(raw)
        fact["artifacts"][name] = artifact.relative_to(CHECKPOINT).as_posix()
    if (
        fact["status"] == "COMPLETED"
        and fact["exitCode"] == 0
        and execution["cleanup"]["result"] == "PASS"
        and not any(execution["producer"][name]["refusal"] for name in ("stdout", "stderr"))
    ):
        fact["result"] = "PASS"
    fact["finishedAt"] = utc_now()
    write_json(target, fact)
    print(
        json.dumps(
            {
                "result": fact["result"],
                "status": fact["status"],
                "exitCode": fact["exitCode"],
                "observation": target.relative_to(CHECKPOINT).as_posix(),
                "acceptanceGranted": False,
            }
        )
    )
    return int(fact["result"] != "PASS")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "action",
        choices=(
            "prepare",
            "bootstrap-builder",
            "retry-bootstrap-builder",
            "capture-builder",
            "cleanup",
            "snapshot",
        ),
    )
    args = parser.parse_args()
    if args.action == "prepare":
        return prepare()
    if args.action == "bootstrap-builder":
        return bootstrap_builder()
    if args.action == "retry-bootstrap-builder":
        return bootstrap_builder(retry=True)
    path = current_scope_path()
    if args.action == "capture-builder":
        operator.capture_builder_ownership(path)
    elif args.action == "cleanup":
        return operator.cleanup(path)
    else:
        folder = path.parent / "resource-observations"
        folder.mkdir(exist_ok=True)
        target = folder / f"run-{len(list(folder.glob('run-*.json'))) + 1:04d}.json"
        write_json(target, operator.snapshot())
        print(
            json.dumps({"observation": target.relative_to(CHECKPOINT).as_posix(), "effects": False})
        )
    return 0


if __name__ == "__main__":
    use_utf8_stdout()
    raise SystemExit(main())
