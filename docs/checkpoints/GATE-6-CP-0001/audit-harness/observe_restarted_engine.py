"""Observe the supported Desktop management path after restart; never issue a Gate verdict."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))
from ledger_common import load_json, use_utf8_stdout, utc_now, write_json


def query(*arguments: str) -> str:
    result = subprocess.run(["docker", "--context", "desktop-linux", *arguments], cwd=ROOT,
        capture_output=True, text=True, encoding="utf-8", errors="strict", timeout=20, check=False)
    if result.returncode:
        raise RuntimeError("supported Desktop management query failed; no recovery acceptance")
    return result.stdout.strip()


def main() -> int:
    destination = CHECKPOINT / "attempts/DOCKER-RESTART-0001-AFTER.json"
    if destination.exists():
        raise ValueError("the post-restart observation already exists; never overwrite it")
    before = load_json(CHECKPOINT / "attempts/DOCKER-RECOVERY-0001-BEFORE.json")
    project = before["composeProject"]
    if not re.fullmatch(r"iacode-verify-[0-9a-f]{12}", project):
        raise ValueError("unexpected historical test owner")
    identity = query("info", "--format", "{{.ID}}|{{.Name}}|{{.OSType}}").split("|")
    if len(identity) != 3 or identity[1:] != ["docker-desktop", "linux"]:
        raise ValueError("unexpected Desktop Engine identity")
    version = query("version", "--format", "{{.Server.Version}}")
    if not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", version):
        raise ValueError("unexpected Server version")
    current = {}
    for line in query("container", "ls", "--all", "--no-trunc", "--format",
                      "{{.ID}}|{{.State}}").splitlines():
        identifier, state = line.split("|")
        if not re.fullmatch(r"[0-9a-f]{64}", identifier) or state not in {
                "created", "running", "paused", "restarting", "removing", "exited", "dead"}:
            raise ValueError("unexpected container identity/state")
        current[identifier] = state
    previous = before["otherContainerIdentitiesAndStates"]
    selector = "label=com.docker.compose.project=" + project
    owned = {kind: query(kind, "ls", *( ["--all"] if kind == "container" else []),
        "--filter", selector, "--format", "{{.Name}}" if kind == "volume" else "{{.ID}}")
        .splitlines() for kind in ("container", "volume", "network")}
    unchanged_ids = all(row["id"] in current for row in previous)
    states = [{"id": row["id"], "before": row["state"], "after": current.get(row["id"])}
              for row in previous]
    removed = not any(owned.values())
    write_json(destination, {
        "kind": "POST_RESTART_MANAGEMENT_OBSERVATION_NOT_GATE_ACCEPTANCE",
        "observedAt": utc_now(), "context": "desktop-linux", "engineId": identity[0],
        "serverVersion": version, "historicalTestProject": project,
        "oldOwnedResources": owned, "oldOwnedResourcesRemainAbsent": removed,
        "previousOtherContainersObserved": len(previous),
        "previousOtherContainerIdentitiesStillPresent": unchanged_ids,
        "previousOtherContainerStates": states,
        "containerStatesMayChangeDuringAuthorizedRestart": True,
        "managementResult": "PASS", "generalRuntimeReadiness": "REQUIRES_FULL_VERIFICATION",
        "gateVerdictIssued": False, "resourceMutationPerformedByThisProbe": False,
        "limits": "Management response and identities only. Complete unchanged lint is separate "
                  "cmd-0192 evidence; this observation does not replace any canonical stage.",
    })
    print(f"DESKTOP_MANAGEMENT=PASS oldOwnedAbsent={removed} "
          f"previousOtherIdentitiesPresent={unchanged_ids} observed={len(previous)}")
    return 0 if removed else 1


if __name__ == "__main__":
    use_utf8_stdout()
    raise SystemExit(main())
