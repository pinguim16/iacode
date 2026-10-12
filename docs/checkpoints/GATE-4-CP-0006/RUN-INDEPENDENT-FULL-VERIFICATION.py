"""Independently run the canonical verifier once from the sealed published Gate 4 subject.

This audit evidence harness never retries a failed stage or a failed verifier. It preserves the
clone, copies only the workstation's ignored provider configuration (without reading or reporting
its values), proves the shared ``iacode`` Compose project was not touched, and brings the integral
generated report back into this audit checkpoint.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


CHECKPOINT = Path(__file__).resolve().parent
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "development-ledger"))

from ledger_common import use_utf8_stdout  # noqa: E402


def command(arguments: list[str], *, cwd: Path, check: bool = True) -> str:
    completed = subprocess.run(
        arguments,
        cwd=cwd,
        check=check,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return completed.stdout.strip()


def write_json(path: Path, document: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(document, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def summarize_stages(verification: dict[str, Any]) -> tuple[int, int, int]:
    """Count the canonical verifier's ``result`` field, never an invented alias."""
    stages = verification.get("stages")
    if not isinstance(stages, list):
        raise RuntimeError("verification report has no stage list")
    if len(stages) != 42:
        raise RuntimeError(f"verification report has {len(stages)} stages, expected 42")
    invalid = [
        stage
        for stage in stages
        if not isinstance(stage, dict) or stage.get("result") not in {"PASS", "FAIL"}
    ]
    if invalid:
        raise RuntimeError("verification report contains a stage without PASS/FAIL result")
    passed = sum(1 for stage in stages if stage["result"] == "PASS")
    return len(stages), passed, len(stages) - passed


def require_expected_clone_state(status: str) -> None:
    entries = [line for line in status.splitlines() if line]
    if not entries:
        return
    raise RuntimeError(f"transport clone has unexpected Git state: {entries}")


def docker_json(arguments: list[str]) -> Any:
    output = command(["docker", *arguments], cwd=ROOT)
    return json.loads(output) if output else []


def project_resource_ids(kind: str, project: str) -> list[str]:
    if kind == "containers":
        arguments = ["ps", "-a", "-q", "--filter", f"label=com.docker.compose.project={project}"]
    else:
        noun = {"volumes": "volume", "networks": "network"}[kind]
        arguments = [noun, "ls", "-q", "--filter", f"label=com.docker.compose.project={project}"]
    output = command(["docker", *arguments], cwd=ROOT)
    return sorted(item for item in output.splitlines() if item)


def snapshot_project(project: str) -> dict[str, Any]:
    container_ids = project_resource_ids("containers", project)
    volume_ids = project_resource_ids("volumes", project)
    network_ids = project_resource_ids("networks", project)
    containers = []
    for item in docker_json(["inspect", *container_ids]) if container_ids else []:
        state = item.get("State", {})
        containers.append(
            {
                "id": item.get("Id"),
                "name": item.get("Name"),
                "created": item.get("Created"),
                "imageId": item.get("Image"),
                "declaredImage": item.get("Config", {}).get("Image"),
                "status": state.get("Status"),
                "startedAt": state.get("StartedAt"),
                "finishedAt": state.get("FinishedAt"),
                "exitCode": state.get("ExitCode"),
                "restartCount": item.get("RestartCount"),
                "health": state.get("Health", {}).get("Status"),
            }
        )
    volumes = []
    for item in docker_json(["volume", "inspect", *volume_ids]) if volume_ids else []:
        volumes.append(
            {
                "name": item.get("Name"),
                "driver": item.get("Driver"),
                "createdAt": item.get("CreatedAt"),
                "labels": item.get("Labels"),
            }
        )
    networks = []
    for item in docker_json(["network", "inspect", *network_ids]) if network_ids else []:
        networks.append(
            {
                "id": item.get("Id"),
                "name": item.get("Name"),
                "created": item.get("Created"),
                "driver": item.get("Driver"),
                "labels": item.get("Labels"),
            }
        )
    document = {
        "project": project,
        "containers": sorted(containers, key=lambda item: str(item["name"])),
        "volumes": sorted(volumes, key=lambda item: str(item["name"])),
        "networks": sorted(networks, key=lambda item: str(item["name"])),
    }
    canonical = json.dumps(document, sort_keys=True, separators=(",", ":")).encode("utf-8")
    document["sha256"] = hashlib.sha256(canonical).hexdigest()
    return document


def main() -> int:
    use_utf8_stdout()
    parser = argparse.ArgumentParser()
    parser.add_argument("--remote", required=True)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--tag", required=True)
    parser.add_argument("--target", type=Path, required=True)
    arguments = parser.parse_args()

    target = arguments.target.resolve()
    if target.exists():
        raise RuntimeError(f"clean-clone target already exists: {target}")
    target.parent.mkdir(parents=True, exist_ok=True)
    shared_before = snapshot_project("iacode")
    if not shared_before["containers"]:
        raise RuntimeError("the shared iacode Compose project is unavailable for preservation proof")
    command(["git", "clone", "--no-local", arguments.remote, str(target)], cwd=target.parent)
    tag_commit = command(["git", "rev-parse", arguments.tag], cwd=target)
    if tag_commit != arguments.commit:
        raise RuntimeError(f"published tag resolved {tag_commit}, expected {arguments.commit}")
    command(["git", "checkout", "--detach", arguments.tag], cwd=target)
    observed = command(["git", "rev-parse", "HEAD"], cwd=target)
    if observed != arguments.commit:
        raise RuntimeError(f"published clone resolved {observed}, expected {arguments.commit}")
    remote_main = command(["git", "rev-parse", "origin/main"], cwd=target)
    if remote_main != arguments.commit:
        raise RuntimeError(f"origin/main resolved {remote_main}, expected {arguments.commit}")
    if command(["git", "branch", "--show-current"], cwd=target):
        raise RuntimeError("transport clone is not detached at the sealed subject tag")
    require_expected_clone_state(
        command(["git", "status", "--porcelain", "--untracked-files=all"], cwd=target)
    )

    local_environment = ROOT / "infra" / "compose" / ".env"
    if not local_environment.is_file():
        raise RuntimeError("workstation provider configuration is unavailable")
    clone_environment = target / "infra" / "compose" / ".env"
    shutil.copy2(local_environment, clone_environment)
    if command(["git", "status", "--porcelain"], cwd=target):
        raise RuntimeError("ignored workstation configuration changed the clone's Git state")

    clone_report = target / "INDEPENDENT-GATE-4-VERIFY.json"
    invocation = [
        sys.executable,
        "scripts/iacode/verify.py",
        "--keep-going",
        "--report",
        clone_report.relative_to(target).as_posix(),
    ]
    process = subprocess.Popen(
        invocation,
        cwd=target,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        bufsize=1,
    )
    assert process.stdout is not None
    for line in process.stdout:
        print(line, end="", flush=True)
    exit_code = process.wait()

    if not clone_report.is_file():
        raise RuntimeError(f"verifier produced no report (exit={exit_code})")
    destination = CHECKPOINT / "VERIFICATION-REPORT.json"
    shutil.copy2(clone_report, destination)
    verification = json.loads(destination.read_text(encoding="utf-8"))
    stage_count, passed, failed = summarize_stages(verification)
    verification_passed = verification.get("result") == "PASS"
    isolation = verification.get("isolation")
    cleanup_passed = (
        isinstance(isolation, dict)
        and isolation.get("preRunCleanup") == "PASS"
        and isolation.get("postRunCleanup") == "PASS"
    )
    shared_after = snapshot_project("iacode")
    shared_unchanged = shared_before == shared_after
    owned_project = isolation.get("composeProject") if isinstance(isolation, dict) else None
    owned_after = snapshot_project(str(owned_project)) if owned_project else None
    owned_removed = bool(
        owned_after
        and not owned_after["containers"]
        and not owned_after["volumes"]
        and not owned_after["networks"]
    )
    write_json(
        CHECKPOINT / "COMPOSE-ISOLATION-AUDIT.json",
        {
            "schemaVersion": "1.0.0",
            "sharedProject": "iacode",
            "sharedBefore": shared_before,
            "sharedAfter": shared_after,
            "sharedUnchanged": shared_unchanged,
            "ownedProject": owned_project,
            "ownedAfter": owned_after,
            "ownedRemoved": owned_removed,
            "result": "PASS" if shared_unchanged and owned_removed else "FAIL",
        },
    )
    publication_passed = (
        exit_code == 0
        and verification_passed
        and failed == 0
        and cleanup_passed
        and shared_unchanged
        and owned_removed
    )
    report = {
        "schemaVersion": "1.0.0",
        "artifact": "PUBLISHED-CLEAN-CLONE-VERIFICATION",
        "generatedAt": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "remote": arguments.remote,
        "publishedCommit": arguments.commit,
        "observedCommit": observed,
        "remoteMainEqualsCommit": True,
        "subjectTag": arguments.tag,
        "subjectTagEqualsCommit": True,
        "checkoutMode": "detached-subject-tag",
        "clonePath": str(target),
        "gitStateBeforeVerification": "CLEAN",
        "workstationConfiguration": {
            "source": "ignored infra/compose/.env",
            "valuesRecorded": False,
            "gitStateAfterInjection": "CLEAN",
        },
        "invocationCount": 1,
        "retryCount": 0,
        "verifierRerun": False,
        "stageDenominator": stage_count,
        "stagesPassed": passed,
        "stagesFailed": failed,
        "result": "PASS" if publication_passed else "FAIL",
        "exitCode": exit_code,
        "verificationReport": "VERIFICATION-REPORT.json",
        "isolation": isolation,
        "sharedComposeProject": {
            "name": "iacode",
            "beforeSha256": shared_before["sha256"],
            "afterSha256": shared_after["sha256"],
            "unchanged": shared_unchanged,
        },
        "ownedComposeProjectRemoved": owned_removed,
        "clonePreserved": True,
    }
    write_json(CHECKPOINT / "PUBLISHED-CLEAN-CLONE-REPORT.json", report)
    print(
        f"PUBLISHED_FULL_VERIFICATION={report['result']} "
        f"stages={passed}/{stage_count} clone={target}",
        flush=True,
    )
    return 0 if publication_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
