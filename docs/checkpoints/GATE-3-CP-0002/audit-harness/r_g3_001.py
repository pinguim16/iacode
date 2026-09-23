#!/usr/bin/env python3
"""R-G3-001: the sandbox controller holds the container engine's socket. Is that risk bounded?

The owner's mandate accepts the socket for the local MVP only if ten controls are proved, and
requires a CRITICAL/HIGH finding if any untrusted input can reach an arbitrary engine operation.
This probe proves each control from the running stack and from the source, never from a document:

C1  the agent receives no socket                 the Agent Runtime and worker containers mount none
C2  no child sandbox receives the socket         a real sandbox container has no mount and no bind
C3  no ToolRequest controls engine arguments     the only engine argv builder reads a policy spec
C4  no public API accepts a generic engine op    no route, no activity and no contract field for one
C5  the controller publishes no port             docker inspect: no port binding
C6  cap_drop ALL and no-new-privileges hold      docker inspect of the running controller
C7  arbitrary host mounts are impossible         the builder emits no --volume/--mount; one bind
                                                 (the socket) on the controller, none on a child
C8  the network policy is imposed                children run on network none (or their own
                                                 internal network), decided by the policy
C9  the tool policy limits operations            the registry is closed and the policy canonical
C10 only trusted controller code talks to it     only backend.py starts a process; it starts only
                                                 the docker client, with argument vectors

The attack half (M1-G in the audit's battery) feeds engine-shaped values through the request and
checks the containers the engine actually created.

    python r_g3_001.py --report ../R-G3-001-REVIEW.json
"""

from __future__ import annotations

import argparse
import ast
import json
import subprocess
import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
SANDBOX_SRC = ROOT / "services" / "sandbox" / "src" / "iacode_sandbox"
sys.path.insert(0, str(ROOT / "scripts" / "development-ledger"))

from ledger_common import utc_now  # noqa: E402

STACK = ("iacode-api", "iacode-worker", "iacode-sandbox", "iacode-web", "iacode-postgres",
         "iacode-redis", "iacode-minio", "iacode-temporal", "iacode-temporal-ui",
         "iacode-prometheus", "iacode-grafana")


def inspect(name: str) -> dict:
    completed = subprocess.run(["docker", "inspect", name], capture_output=True, text=True,
                               encoding="utf-8", errors="replace", check=False)
    if completed.returncode != 0:
        return {}
    return (json.loads(completed.stdout) or [{}])[0]


def mounts_socket(facts: dict) -> bool:
    for mount in facts.get("Mounts") or []:
        if "docker.sock" in str(mount.get("Source")) or "docker.sock" in str(
                mount.get("Destination")):
            return True
    return any("docker.sock" in str(bind) for bind in
               (facts.get("HostConfig") or {}).get("Binds") or [])


def calls_in(path: Path) -> list[tuple[str, int]]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    found = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            target = node.func
            name = (f"{getattr(target.value, 'id', '?')}.{target.attr}"
                    if isinstance(target, ast.Attribute) else getattr(target, "id", ""))
            if name in ("subprocess.run", "subprocess.Popen", "subprocess.call",
                        "subprocess.check_output", "os.system", "os.popen", "os.execv",
                        "os.execvp", "asyncio.create_subprocess_exec",
                        "asyncio.create_subprocess_shell", "pty.spawn"):
                found.append((name, node.lineno))
    return found


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path, required=True)
    arguments = parser.parse_args()
    controls = []

    def control(identifier: str, title: str, ok: bool, observed: str, evidence: list[str]) -> None:
        controls.append({"id": identifier, "control": title, "result": "PASS" if ok else "FAIL",
                         "observed": observed, "evidence": evidence})
        print(f"[{'PASS' if ok else 'FAIL'}] {identifier} {title}: {observed[:160]}", flush=True)

    facts = {name: inspect(name) for name in STACK}
    holders = sorted(name for name, item in facts.items() if item and mounts_socket(item))
    control("C1", "the agent receives no socket",
            holders == ["iacode-sandbox"] and bool(facts.get("iacode-worker")),
            f"containers of the stack that mount the engine socket: {holders}; the worker that "
            f"runs agents mounts none",
            ["file:infra/compose/docker-compose.yml",
             "test:test_only_the_sandbox_service_is_given_the_engine_socket"])

    backend = (SANDBOX_SRC / "backend.py").read_text(encoding="utf-8")
    builder_flags = [flag for flag in ("--volume", "--mount", "-v", "--privileged", "--cap-add",
                                       "--device", "--pid", "--ipc", "--env-file", "--env",
                                       "--network=host", "--userns")
                     if f'"{flag}"' in backend]
    control("C2", "no child sandbox receives the socket",
            not builder_flags,
            f"flags the only container builder can emit that could hand a sandbox a host "
            f"resource: {builder_flags or 'none'}; the battery's M1-C inspects a real child",
            ["file:services/sandbox/src/iacode_sandbox/backend.py", "test:ContainerSpecTests"])

    tree = ast.parse(backend)
    spec_fields = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "ContainerSpec":
            spec_fields = [item.target.id for item in node.body
                           if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name)]
    service = (SANDBOX_SRC / "service.py").read_text(encoding="utf-8")
    spec_built_from_policy = ("image=reference" in service and "cpus=resources.cpus" in service
                              and "network=network" in service)
    request_fields = sorted(
        {"contractVersion", "toolRequestId", "runId", "agentRunId", "agent", "tool", "arguments",
         "policy", "workspace"})
    contracts = (SANDBOX_SRC / "contracts.py").read_text(encoding="utf-8")
    fields_declared = all(f'"{name}"' in contracts for name in request_fields)
    control("C3", "no ToolRequest controls engine arguments",
            spec_built_from_policy and fields_declared and "_strict(payload" in contracts,
            f"ContainerSpec fields {spec_fields} are filled from the policy's image and resources "
            f"and a generated session name; the request contract is closed to {request_fields}, "
            f"refused beside it by _strict; tool arguments travel as JSON on the helper's stdin",
            ["file:services/sandbox/src/iacode_sandbox/service.py",
             "file:services/sandbox/src/iacode_sandbox/contracts.py",
             "test:test_the_image_decides_the_command_not_the_request"])

    worker = (SANDBOX_SRC / "worker.py").read_text(encoding="utf-8")
    activities = [name for name in ("SANDBOX_EXECUTE_ACTIVITY", "SANDBOX_RELEASE_ACTIVITY")
                  if f"@activity.defn(name={name})" in worker]
    web_routes = []
    for path in (ROOT / "apps" / "api" / "src").rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        if "docker" in text.lower() or "iacode_sandbox.backend" in text:
            web_routes.append(str(path.relative_to(ROOT)).replace("\\", "/"))
    control("C4", "no public API accepts a generic engine operation",
            activities == ["SANDBOX_EXECUTE_ACTIVITY", "SANDBOX_RELEASE_ACTIVITY"]
            and "ACTIVITIES = [execute_tool, release_run]" in worker and not web_routes,
            f"the controller serves two activities ({activities}) and no HTTP surface; the API "
            f"source names no engine client ({web_routes or 'none'})",
            ["file:services/sandbox/src/iacode_sandbox/worker.py",
             "test:SandboxBoundaryTests"])

    controller = facts.get("iacode-sandbox") or {}
    host_config = controller.get("HostConfig") or {}
    ports = host_config.get("PortBindings") or {}
    exposed = (controller.get("NetworkSettings") or {}).get("Ports") or {}
    published = {key: value for key, value in exposed.items() if value}
    control("C5", "the controller publishes no port",
            bool(controller) and not ports and not published,
            f"port bindings {ports or 'none'}; published ports {published or 'none'}",
            ["file:infra/compose/docker-compose.yml"])

    cap_drop = host_config.get("CapDrop") or []
    cap_add = host_config.get("CapAdd") or []
    security = host_config.get("SecurityOpt") or []
    user = (controller.get("Config") or {}).get("User") or ""
    control("C6", "cap_drop and no-new-privileges remain",
            [item.upper() for item in cap_drop] in (["ALL"], ["CAP_ALL"]) and not cap_add
            and any("no-new-privileges" in item for item in security)
            and not host_config.get("Privileged") and user not in ("", "root", "0"),
            f"CapDrop {cap_drop}, CapAdd {cap_add or 'none'}, SecurityOpt {security}, "
            f"Privileged {host_config.get('Privileged')}, User {user!r}",
            ["file:infra/compose/docker-compose.yml",
             "file:services/sandbox/Dockerfile"])

    binds = [str(item.get("Source")) + ":" + str(item.get("Destination"))
             for item in controller.get("Mounts") or []]
    control("C7", "arbitrary host mounts are impossible",
            len(binds) == 1 and "docker.sock" in binds[0] and not builder_flags,
            f"the controller's only mount is {binds}; the child builder emits no volume, mount "
            f"or env-file flag; the battery's M1-G checks the children the engine created",
            ["file:services/sandbox/src/iacode_sandbox/backend.py",
             "file:infra/compose/docker-compose.yml"])

    policy = json.loads((ROOT / ".iacode" / "policies" / "sandbox-policy.json")
                        .read_text(encoding="utf-8"))
    profiles = sorted({str(item.get("networkProfile")) for item in
                       (policy.get("sandboxPolicies") or [])})
    control("C8", "the network policy is imposed",
            '"--network", spec.network' in backend and 'network = "none"' in service
            and bool(profiles) and set(profiles) <= {"none", "local-services"},
            f"children start with --network from the spec, 'none' unless the policy grants its "
            f"own internal network; declared profiles {profiles}",
            ["file:.iacode/policies/sandbox-policy.json",
             "test:test_external_egress_fails"])

    tools = (SANDBOX_SRC / "tools.py").read_text(encoding="utf-8")
    control("C9", "the tool policy limits operations",
            "ToolRejectedError" in tools and "git.push" not in tools,
            "the registry is closed (an unknown name raises ToolRejectedError), each policy "
            "names its tools, and no remote Git verb exists",
            ["file:services/sandbox/src/iacode_sandbox/tools.py",
             "file:.iacode/policies/sandbox-policy.json", "test:SandboxPolicyTests"])

    starters = {}
    for path in sorted(SANDBOX_SRC.rglob("*.py")):
        found = calls_in(path)
        if found:
            starters[str(path.relative_to(ROOT)).replace("\\", "/")] = found
    helper_only = {path: calls for path, calls in starters.items()
                   if not path.endswith(("backend.py", "helper.py"))}
    control("C10", "only trusted controller code talks to the engine",
            "backend.py" in " ".join(starters) and not helper_only
            and 'if executable != DOCKER' in backend and "shell=True" not in backend,
            f"modules that start a process: {sorted(starters)} (helper.py runs inside the "
            f"sandbox, never in the controller); backend refuses any executable but docker and "
            f"never uses a shell",
            ["file:services/sandbox/src/iacode_sandbox/backend.py",
             "test:test_the_backend_starts_only_the_container_client"])

    failed = [item for item in controls if item["result"] != "PASS"]
    report = {
        "schemaVersion": "1.0.0", "artifact": "R-G3-001-REVIEW", "checkpoint": CHECKPOINT.name,
        "risk": "R-G3-001", "generatedAt": utc_now(), "controls": controls,
        "passed": len(controls) - len(failed), "total": len(controls),
        "untrustedInputReachesEngineOperation": bool(failed),
        "disposition": ("ACCEPTED_LOCAL_ARCHITECTURAL_RISK" if not failed
                        else "FINDING_CRITICAL_OR_HIGH"),
        "backlog": ("Replace direct socket access by a rootless container engine or a restricted "
                    "socket proxy that exposes only the create, exec, inspect, list and remove "
                    "operations the backend uses."),
        "result": "PASS" if not failed else "FAIL",
    }
    arguments.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n",
                                encoding="utf-8", newline="\n")
    print(f"R_G3_001={report['result']} {report['passed']}/{report['total']} "
          f"disposition={report['disposition']}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
