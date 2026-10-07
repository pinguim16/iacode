#!/usr/bin/env python3
"""The in-image half of the M1 audit's own Red Team: cross-gate attacks on real sandboxes.

Run inside the sandbox service's image with the container engine's socket mounted exactly as the
stack mounts it. It drives the real SandboxService over the real DockerBackend, with an owner label
of its own, so nothing it creates is the stack's and every run it opens is released at the end.

The service scaffolding (`Battery`, `out`, `verdict`) is imported from the GATE 3 module mounted
beside this one: it is the construction of a real service, not an attack. Every attack below is this
audit's own, written against the M1 criteria rather than against the Gate that built the sandbox.

Each attack returns ``(defended, observed)``. The baseline runs the unmutated requests through the
identical service first and must be accepted, or nothing below proves anything.
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
import uuid

sys.path.insert(0, "/tmp")

from gate3_sandbox_attacks import Battery, out, verdict  # noqa: E402
from iacode_sandbox.backend import DockerBackend  # noqa: E402

#: Named like a provider credential on purpose: if a sandbox can see it, a real one would leak too.
SECRET_NAME = "IACODE_DEVWORLD_API_KEY"
SECRET_VALUE = f"m1-audit-{uuid.uuid4().hex}"
os.environ[SECRET_NAME] = SECRET_VALUE
os.environ["IACODE_M1_AUDIT_SENTINEL_TOKEN"] = SECRET_VALUE


def inspect(battery: Battery, run_id: str) -> dict:
    session = battery.session(run_id)
    if session is None:
        return {}
    return DockerBackend().inspect(session.container_name) or {}


def baseline(battery: Battery) -> tuple[bool, str]:
    run_id = battery.run_id()
    wrote = battery.execute("filesystem.write", {"path": "m1.txt", "content": "m1\n"},
                            run_id=run_id)
    read = battery.execute("filesystem.read", {"path": "m1.txt"}, run_id=run_id)
    shell = battery.shell("echo m1-baseline && git status --short", run_id=run_id)
    reviewer = battery.execute("filesystem.read", {"path": "m1.txt"}, run_id=run_id,
                               policy="reviewer")
    accepted = (wrote.status == read.status == shell.status == reviewer.status == "SUCCEEDED"
                and read.output.get("content") == "m1\n" and "m1-baseline" in out(shell))
    return accepted, (f"write {verdict(wrote)}, read {verdict(read)}, shell {verdict(shell)}, "
                      f"reviewer read {verdict(reviewer)}")


def host_execution(battery: Battery) -> tuple[bool, str]:
    """A shell command runs in the run's container, never in the controller or on the host."""
    run_id = battery.run_id()
    probe = battery.shell("cat /etc/hostname; id -u; ls -d /mnt/host /run/desktop /host /e "
                          "2>&1 | head -5; touch /mnt/e-iacode-m1 2>&1 | tail -1", run_id=run_id)
    facts = inspect(battery, run_id)
    lines = out(probe).splitlines()
    hostname = lines[0].strip() if lines else ""
    container_hostname = ((facts.get("Config") or {}).get("Hostname") or "")
    controller_hostname = os.uname().nodename
    uid = lines[1].strip() if len(lines) > 1 else ""
    present = [line.strip() for line in lines[2:]
               if line.strip() in ("/mnt/host", "/run/desktop", "/host", "/e")]
    defended = (probe.status == "SUCCEEDED" and bool(hostname)
                and hostname == container_hostname and hostname != controller_hostname
                and uid == "10001" and not present)
    return defended, (f"the command ran as uid {uid} on host name {hostname!r}, which is the "
                      f"sandbox container's ({container_hostname!r}) and not the controller's "
                      f"({controller_hostname!r}); host mount points absent")


def secret_isolation(battery: Battery) -> tuple[bool, str]:
    run_id = battery.run_id()
    probe = battery.shell(
        "env; tr '\\0' '\\n' < /proc/1/environ; echo; echo ---files; "
        "find / -xdev \\( -name '.env' -o -name '*.env' -o -name 'id_rsa*' -o -name 'id_ed25519*' "
        "-o -name '*.key' -o -name '.git-credentials' -o -name 'credentials' -o -name "
        "'docker.sock' \\) 2>/dev/null | head -5; echo ---keys; "
        "grep -rlsI --exclude-dir=proc --exclude-dir=sys -e 'PRIVATE KEY-----' / 2>/dev/null "
        "| head -5", run_id=run_id)
    text = out(probe)
    environment = text.split("---files")[0]
    files = [line.strip() for line in text.split("---files")[-1].split("---keys")[0].splitlines()
             if line.strip()]
    keys = [line.strip() for line in text.split("---keys")[-1].splitlines()
            if line.strip().startswith("/")]
    leaked = [name for name in (SECRET_NAME, "IACODE_M1_AUDIT_SENTINEL_TOKEN", "IACODE_DATABASE",
                                "IACODE_MINIO", "IACODE_TEMPORAL")
              if name in environment]
    value_leaked = SECRET_VALUE in text
    defended = (probe.status == "SUCCEEDED" and not leaked and not value_leaked and not files
                and not keys)
    return defended, (f"controller variables visible: {leaked or 'none'}; secret value visible: "
                      f"{value_leaked}; credential files: {files or 'none'}; files holding "
                      f"private key material: {keys or 'none'}")


def docker_socket(battery: Battery) -> tuple[bool, str]:
    run_id = battery.run_id()
    probe = battery.shell(
        "ls -la /var/run/docker.sock /run/docker.sock 2>&1; echo DOCKER_HOST=${DOCKER_HOST:-}; "
        "python3 -c \"import socket;s=socket.socket(socket.AF_UNIX);"
        "s.connect('/var/run/docker.sock')\" 2>&1 | tail -1", run_id=run_id)
    facts = inspect(battery, run_id)
    mounts = facts.get("Mounts") or []
    binds = (facts.get("HostConfig") or {}).get("Binds") or []
    text = out(probe)
    defended = (probe.status == "SUCCEEDED" and "No such file" in text and not mounts
                and not binds and "DOCKER_HOST=\n" in text + "\n")
    return defended, (f"socket paths absent, DOCKER_HOST empty, connecting fails; the container "
                      f"has {len(mounts)} mount(s) and {len(binds)} bind(s)")


def workspace_escape(battery: Battery) -> tuple[bool, str]:
    run_id = battery.run_id()
    seen = []
    for path in ("../../../etc/passwd", "/etc/shadow", "..\\..\\windows", "sub/../../x"):
        seen.append((path, verdict(battery.execute("filesystem.read", {"path": path},
                                                   run_id=run_id))))
    battery.shell("ln -s / root-link && ln -s /etc/passwd pw-link", run_id=run_id)
    for path in ("root-link/etc/passwd", "pw-link"):
        seen.append((path, verdict(battery.execute("filesystem.read", {"path": path},
                                                   run_id=run_id))))
    written = verdict(battery.execute("filesystem.write",
                                      {"path": "root-link/tmp/escaped", "content": "x"},
                                      run_id=run_id))
    seen.append(("write through root-link", written))
    defended = all(code.startswith("DENIED/PATH_") for _path, code in seen)
    return defended, "; ".join(f"{path} -> {code}" for path, code in seen)


def cross_run_isolation(battery: Battery) -> tuple[bool, str]:
    victim = battery.run_id()
    attacker = battery.run_id()
    suffix = uuid.uuid4().hex
    token = f"victim-{suffix}"
    battery.execute("filesystem.write", {"path": "secret.txt", "content": token}, run_id=victim)
    victim_name = battery.session(victim).container_name
    # The token is assembled inside the shell, so the search never finds its own command line.
    search = battery.shell(f"A=victim-; B={suffix}; grep -rsl --exclude-dir=proc "
                           f"--exclude-dir=sys \"$A$B\" / 2>/dev/null | head -3; echo searched",
                           run_id=attacker)
    attacker_name = battery.session(attacker).container_name
    matches = [line.strip() for line in out(search).splitlines()
               if line.strip() and line.strip() != "searched"]
    defended = (not matches and victim_name != attacker_name
                and "searched" in out(search) and search.status == "SUCCEEDED")
    return defended, (f"victim container {victim_name[-12:]}, attacker container "
                      f"{attacker_name[-12:]}; files holding the victim's token seen from the "
                      f"attacker's sandbox: {matches or 'none'}")


def tool_policy_escalation(battery: Battery) -> tuple[bool, str]:
    run_id = battery.run_id()
    reviewer_write = verdict(battery.execute("filesystem.write", {"path": "r.txt", "content": "x"},
                                             run_id=run_id, policy="reviewer"))
    reviewer_shell = verdict(battery.execute("shell.exec", {"command": "id"}, run_id=run_id,
                                             policy="reviewer"))
    unknown = verdict(battery.execute("docker.run", {"image": "alpine"}, run_id=run_id))
    raised = verdict(battery.execute("shell.exec", {"command": "sleep 1", "timeoutSeconds": 86400},
                                     run_id=run_id))
    beside = asyncio.run(battery.service.execute({
        **battery.payload("shell.exec", {"command": "id"}, run_id=run_id),
        "privileged": True, "image": "alpine", "mounts": ["/:/host"]}))
    unknown_policy = verdict(battery.execute("shell.exec", {"command": "id"}, run_id=run_id,
                                             policy="root"))
    codes = {"reviewer write": reviewer_write, "reviewer shell": reviewer_shell,
             "unknown tool": unknown, "raised timeout": raised,
             "fields beside the contract": verdict(beside), "unknown policy": unknown_policy}
    defended = all(code.startswith("DENIED/") for code in codes.values())
    return defended, "; ".join(f"{name} {code}" for name, code in codes.items())


def engine_operation_from_input(battery: Battery) -> tuple[bool, str]:
    """R-G3-001: nothing a request carries becomes an argument of the engine."""
    facts_seen = []
    for run_id in ("--privileged", "x --volume /:/host --cap-add ALL"):
        battery.runs.append(run_id)
        result = battery.execute("shell.exec", {"command": "--privileged -v /:/host"},
                                 run_id=run_id)
        facts = inspect(battery, run_id)
        host = facts.get("HostConfig") or {}
        facts_seen.append({
            "runId": run_id, "result": verdict(result),
            "privileged": host.get("Privileged"), "binds": host.get("Binds") or [],
            "mounts": len(facts.get("Mounts") or []), "capAdd": host.get("CapAdd") or [],
            "capDrop": host.get("CapDrop") or [], "network": host.get("NetworkMode"),
            "label": ((facts.get("Config") or {}).get("Labels") or {}).get(
                "org.iacode.sandbox.run")})
    workspace = asyncio.run(battery.service.execute({
        **battery.payload("shell.exec", {"command": "id"}, run_id=battery.run_id()),
        "workspace": {"kind": "path", "path": "/var/run"}}))
    defended = workspace.status == "DENIED" and all(
        item["privileged"] in (False, None) and not item["binds"] and item["mounts"] == 0
        and not item["capAdd"] and item["network"] in ("none", None)
        for item in facts_seen)
    for item in facts_seen:
        if item["label"] not in (None, item["runId"]):
            defended = False
    return defended, (json.dumps(facts_seen)[:380] + f"; workspace naming a host path "
                      f"{verdict(workspace)}")


def git_remote_exposure(battery: Battery) -> tuple[bool, str]:
    run_id = battery.run_id()
    probe = battery.shell(
        "git init -q . 2>/dev/null; git remote -v; echo remotes-listed; "
        "git config --list --show-origin | grep -i -E 'credential|url\\.|token' ; echo cfg; "
        "ls -la ~/.ssh ~/.git-credentials 2>&1 | tail -2; "
        "timeout 20 git push https://github.com/pinguim16/iacode.git HEAD:refs/heads/m1 2>&1 "
        "| tail -1; echo push-exit=$?", run_id=run_id)
    tools = [verdict(battery.execute(name, {"remote": "origin"}, run_id=run_id))
             for name in ("git.push", "git.fetch", "git.clone")]
    text = out(probe)
    remote_lines = text.split("remotes-listed")[0].strip()
    configuration = [line.strip() for line in
                     text.split("remotes-listed")[-1].split("cfg")[0].splitlines() if line.strip()]
    # The sandbox's gitconfig sets credential.helper to the empty value, which disables every
    # helper; that line is the control, and only a helper with a value would be an exposure.
    exposures = [line for line in configuration
                 if not line.endswith("credential.helper=")]
    push_failed = ("Could not resolve host" in text or "unable to access" in text
                   or "not allowed" in text or "fatal" in text)
    defended = (not remote_lines and not exposures and push_failed
                and all(code.startswith("DENIED/") for code in tools))
    return defended, (f"remotes: {remote_lines or 'none'}; credential configuration: "
                      f"{configuration or 'none'} (an empty helper disables helpers); exposures: "
                      f"{exposures or 'none'}; push over the network "
                      f"{'failed' if push_failed else 'SUCCEEDED'}; remote tools {tools}")


def network_egress(battery: Battery) -> tuple[bool, str]:
    run_id = battery.run_id()
    script = (
        "import socket\n"
        "for host, port in (('1.1.1.1', 443), ('api', 8000), ('temporal', 7233), "
        "('host.docker.internal', 18080), ('iacode-postgres', 5432)):\n"
        "    s = socket.socket(); s.settimeout(3)\n"
        "    try:\n"
        "        s.connect((host, port)); print('CONNECTED', host, port)\n"
        "    except Exception as error:\n"
        "        print('refused', host, port, type(error).__name__)\n")
    probe = battery.shell(f"python3 -c \"{script}\"", run_id=run_id)
    text = out(probe)
    defended = probe.status == "SUCCEEDED" and "CONNECTED" not in text and "refused" in text
    return defended, text.strip().replace("\n", " | ")[:300]


ATTACKS = {
    "M1-A": host_execution,
    "M1-B": secret_isolation,
    "M1-C": docker_socket,
    "M1-D": workspace_escape,
    "M1-E": cross_run_isolation,
    "M1-F": tool_policy_escalation,
    "M1-G": engine_operation_from_input,
    "M1-H": git_remote_exposure,
    "M1-I": network_egress,
}


def main() -> int:
    battery = Battery()
    verdicts: dict[str, dict] = {}
    try:
        accepted, observed = baseline(battery)
        verdicts["baseline"] = {"defended": accepted, "observed": observed}
        for identifier, attack in ATTACKS.items():
            try:
                defended, observed = attack(battery)
            except Exception as error:  # noqa: BLE001 - a crashed attack has found something
                defended, observed = False, f"the attack failed: {type(error).__name__}: {error}"
            verdicts[identifier] = {"defended": bool(defended), "observed": observed[:500]}
            print(f"[{'DEFENDED' if defended else 'ESCAPED'}] {identifier}: {observed[:160]}",
                  file=sys.stderr, flush=True)
        verdicts["residue"] = {"containers": len(battery.containers())}
    finally:
        battery.close()
    verdicts["residueAfterRelease"] = {"containers": len(battery.containers())}
    print(json.dumps(verdicts), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
