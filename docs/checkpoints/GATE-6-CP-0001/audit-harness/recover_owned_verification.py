"""Remove only the interrupted v3 test project after observed ownership; preserve other apps."""

from __future__ import annotations

import hashlib
import re
import subprocess
import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))
sys.path.insert(0, str(ROOT / "scripts/iacode"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ledger_common import load_json, utc_now, write_json
from verify import verification_environment
from with_local_engine import ENGINE_ENDPOINT, engine_environment


def docker(*arguments: str, environment: dict[str, str]) -> str:
    result = subprocess.run(["docker", *arguments], cwd=ROOT, env=environment,
        capture_output=True, text=True, encoding="utf-8", errors="strict",
        timeout=20, check=False)
    if result.returncode:
        raise RuntimeError("Docker inventory failed; no resource removal authorized")
    return result.stdout.strip()


def containers(environment: dict[str, str], project: str | None = None) -> list[dict]:
    arguments = ["container", "ls", "--all", "--no-trunc", "--format",
                 "{{.ID}}|{{.Names}}|{{.State}}"]
    if project is not None:
        arguments += ["--filter", "label=com.docker.compose.project=" + project]
    rows = []
    for line in docker(*arguments, environment=environment).splitlines():
        identifier, name, state = line.split("|")
        if not re.fullmatch(r"[0-9a-f]{64}", identifier):
            raise ValueError("unexpected container identity")
        rows.append({"id": identifier, "name": name, "state": state})
    return sorted(rows, key=lambda row: row["id"])


def inventory(environment: dict[str, str], project: str) -> dict:
    selector = "label=com.docker.compose.project=" + project
    volumes = docker("volume", "ls", "--filter", selector,
                     "--format", "{{.Name}}", environment=environment).splitlines()
    networks = []
    for line in docker("network", "ls", "--no-trunc", "--filter", selector,
                       "--format", "{{.ID}}|{{.Name}}", environment=environment).splitlines():
        identifier, name = line.split("|")
        networks.append({"id": identifier, "name": name})
    return {"containers": containers(environment, project), "volumes": sorted(volumes),
            "networks": sorted(networks, key=lambda row: row["id"])}


def validate_ownership(resources: dict, project: str) -> None:
    if not re.fullmatch(r"iacode-verify-[0-9a-f]{12}", project):
        raise ValueError("refusing an operational or unknown Compose project")
    for kind in ("containers", "networks"):
        rows = resources[kind]
        if len({row["id"] for row in rows}) != len(rows):
            raise ValueError("duplicate owned resource identity")
        if any(not row["name"].startswith(project + "-") for row in rows):
            raise ValueError("a project-labelled resource has an unexpected owner name")
    if any(not name.startswith(project + "_") for name in resources["volumes"]):
        raise ValueError("a project-labelled volume has an unexpected owner name")


def main() -> int:
    before_path = CHECKPOINT / "attempts/DOCKER-RECOVERY-0001-BEFORE.json"
    after_path = CHECKPOINT / "attempts/DOCKER-RECOVERY-0001-AFTER.json"
    if before_path.exists() or after_path.exists():
        raise ValueError("recovery observations are immutable; do not replay a removal")
    attempt = load_json(CHECKPOINT / "attempts/FULL-VERIFY-INTERRUPTED-0003.json")
    clone = Path(attempt["progress"]["clone"])
    environment = verification_environment(clone, engine_environment())
    project = environment["COMPOSE_PROJECT_NAME"]
    if project != attempt["composeProject"]:
        raise ValueError("the original checkout owner does not match its receipt")
    identity = docker("info", "--format", "{{.ID}}|{{.Name}}|{{.OSType}}",
                      environment=environment).split("|")
    if len(identity) != 3 or identity[1:] != ["docker-desktop", "linux"]:
        raise ValueError("unexpected local Engine identity; no resource removal")
    owned_before = inventory(environment, project)
    validate_ownership(owned_before, project)
    owned_ids = {row["id"] for row in owned_before["containers"]}
    other_before = [{"id": row["id"], "state": row["state"]}
                    for row in containers(environment) if row["id"] not in owned_ids]
    write_json(before_path, {"kind": "OWNED_TEST_RECOVERY_BEFORE_NOT_ACCEPTANCE",
        "observedAt": utc_now(), "engineEndpoint": ENGINE_ENDPOINT,
        "engineId": identity[0], "composeProject": project, "ownedResources": owned_before,
        "otherContainerIdentitiesAndStates": other_before,
        "subjectCommit": attempt["subjectCommit"], "gateVerdictIssued": False})
    compose = ROOT / "infra/compose"
    arguments = ["docker", "compose", "--project-name", project, "--project-directory",
        str(compose), "--file", str(compose / "docker-compose.yml"), "--env-file",
        str(compose / ".env"), "down", "--volumes", "--remove-orphans"]
    # Both CLI project name and the process interpolation namespace are bound to the same owner.
    result = subprocess.run(arguments, cwd=ROOT, env=environment, capture_output=True,
                            timeout=45, check=False)
    owned_after = inventory(environment, project)
    other_after = {row["id"]: row["state"] for row in containers(environment)}
    unchanged = all(other_after.get(row["id"]) == row["state"] for row in other_before)
    removed = not any(owned_after.values())
    passed = result.returncode == 0 and removed and unchanged
    write_json(after_path, {"kind": "OWNED_TEST_RECOVERY_AFTER_NOT_GATE_ACCEPTANCE",
        "observedAt": utc_now(), "engineEndpoint": ENGINE_ENDPOINT,
        "engineId": identity[0], "composeProject": project, "ownedResources": owned_after,
        "otherContainerIdentitiesPreserved": unchanged, "otherContainersObserved": len(other_before),
        "removalExitCode": result.returncode, "ownedRemoved": removed,
        "outputBytes": len(result.stdout + result.stderr),
        "outputSha256": hashlib.sha256(result.stdout + result.stderr).hexdigest(),
        "dockerRestarted": False, "globalContextChanged": False, "gateVerdictIssued": False,
        "result": "PASS" if passed else "FAIL"})
    print("OWNED_RECOVERY=" + ("PASS" if passed else "FAIL") +
          " removed=" + str(removed) + " otherIdentitiesPreserved=" + str(unchanged))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
