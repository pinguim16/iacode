#!/usr/bin/env python3
"""The in-image half of the GATE 3 internal Red Team: attacks on real sandboxes.

Run by `gate3_red_team.py` inside the sandbox service's image, with the container engine's socket
mounted exactly as the stack mounts it and nothing else of the stack. Every attack drives the real
:class:`~iacode_sandbox.service.SandboxService` over the real :class:`DockerBackend`, so what is
attacked is a real container with its real hardening, never a double.

The service here has an owner label of its own, so nothing it creates or reconciles is the stack's,
and every run it opens is released at the end whatever happened.

Each attack returns ``(defended, observed)``: whether the refusal it aimed at happened, and what was
seen. The baseline runs the unmutated requests through the identical service first; it must be
accepted, or the battery proves nothing. The verdicts are printed as one JSON document on the last
line of standard output.
"""

from __future__ import annotations

import asyncio
import json
import os
import shutil
import sys
import tempfile
import uuid
from pathlib import Path
from typing import Any

from iacode_contracts.sandbox import SANDBOX_CONTRACT_VERSION
from iacode_sandbox.artifacts import MemoryArtifactSink
from iacode_sandbox.backend import DockerBackend
from iacode_sandbox.policy import load_policy_registry
from iacode_sandbox.service import SandboxService
from iacode_sandbox.store import MemorySandboxStore
from iacode_sandbox.telemetry import SandboxMetrics
from prometheus_client import CollectorRegistry

ROOT = Path(os.environ.get("IACODE_REPOSITORY_ROOT", "/app"))

#: A value the controller holds and a sandbox must never see. Named like a credential on purpose.
SENTINEL_NAME = "IACODE_RED_TEAM_SENTINEL_API_KEY"
SENTINEL_VALUE = f"red-team-{uuid.uuid4().hex}"


class Battery:
    def __init__(self, root: Path = ROOT) -> None:
        self.store = MemorySandboxStore()
        self.owner = f"iacode-redteam-{uuid.uuid4().hex[:10]}"
        self.service = SandboxService(
            root=root, policies=load_policy_registry(root), backend=DockerBackend(),
            store=self.store, artifacts=MemoryArtifactSink(self.store),
            metrics=SandboxMetrics(CollectorRegistry()), owner=self.owner)
        self.runs: list[str] = []

    def run_id(self) -> str:
        identifier = str(uuid.uuid4())
        self.runs.append(identifier)
        return identifier

    def payload(self, tool: str, arguments: dict[str, Any] | None = None, *, run_id: str,
                policy: str = "developer", **extra: Any) -> dict[str, Any]:
        body = {
            "contractVersion": SANDBOX_CONTRACT_VERSION, "toolRequestId": str(uuid.uuid4()),
            "runId": run_id, "agentRunId": str(uuid.uuid4()),
            "agent": "developer" if policy == "developer" else "code-reviewer",
            "tool": tool, "arguments": arguments if arguments is not None else {},
            "policy": policy, "workspace": {"kind": "empty"},
        }
        body.update(extra)
        return body

    def execute(self, tool: str, arguments: dict[str, Any] | None = None, *, run_id: str,
                policy: str = "developer", **extra: Any):
        return asyncio.run(self.service.execute(
            self.payload(tool, arguments, run_id=run_id, policy=policy, **extra)))

    def shell(self, command: str, *, run_id: str, **arguments: Any):
        return self.execute("shell.exec", {"command": command, **arguments}, run_id=run_id)

    def session(self, run_id: str):
        return asyncio.run(self.store.active_session_for_run(run_id))

    def containers(self) -> list[dict[str, str]]:
        return DockerBackend().managed(self.owner)

    def close(self) -> None:
        for run_id in self.runs:
            try:
                asyncio.run(self.service.release_run(run_id))
            except Exception:  # noqa: BLE001, S110 - cleanup continues past one failure
                pass


def out(result) -> str:
    return "\n".join(str(result.output.get(key) or "") for key in ("stdout", "stderr"))


def verdict(result) -> str:
    return f"{result.status}/{result.error_code}"


# -- the baseline ------------------------------------------------------------------------------


def baseline(battery: Battery) -> tuple[bool, str]:
    run_id = battery.run_id()
    wrote = battery.execute("filesystem.write", {"path": "notes.txt", "content": "ok\n"},
                            run_id=run_id)
    read = battery.execute("filesystem.read", {"path": "notes.txt"}, run_id=run_id)
    echoed = battery.shell("echo baseline", run_id=run_id)
    status = battery.execute("git.status", run_id=run_id)
    accepted = (wrote.status == read.status == echoed.status == status.status == "SUCCEEDED"
                and read.output.get("content") == "ok\n"
                and out(echoed).strip() == "baseline")
    return accepted, (f"write {verdict(wrote)}, read {verdict(read)}, shell {verdict(echoed)}, "
                      f"git.status {verdict(status)}")


# -- the attacks -------------------------------------------------------------------------------


def path_traversal(battery: Battery) -> tuple[bool, str]:
    run_id = battery.run_id()
    seen = []
    for path in ("../../etc/passwd", "a/../../etc/shadow", "/etc/passwd", "C:/Windows/win.ini",
                 "//server/share/x", "notes.txt\x00.png"):
        result = battery.execute("filesystem.read", {"path": path}, run_id=run_id)
        seen.append((path.replace("\x00", "\\0"), verdict(result)))
    defended = all(item[1].startswith("DENIED/PATH_") for item in seen)
    return defended, "; ".join(f"{path} -> {code}" for path, code in seen)


def symlink_escape(battery: Battery) -> tuple[bool, str]:
    run_id = battery.run_id()
    made = battery.shell("ln -s /etc/passwd file-link && ln -s /etc dir-link && ln -s / root-link",
                         run_id=run_id)
    read = battery.execute("filesystem.read", {"path": "file-link"}, run_id=run_id)
    write = battery.execute("filesystem.write", {"path": "dir-link/owned", "content": "x"},
                            run_id=run_id)
    listed = battery.execute("filesystem.list", {"path": "root-link"}, run_id=run_id)
    codes = [verdict(read), verdict(write), verdict(listed)]
    defended = made.exit_code == 0 and all(
        code == "DENIED/PATH_SYMLINK_ESCAPE" for code in codes)
    return defended, f"links made (exit {made.exit_code}); read, write, list: {codes}"


def workspace_cross_read(battery: Battery) -> tuple[bool, str]:
    owner, intruder = battery.run_id(), battery.run_id()
    marker = uuid.uuid4().hex
    battery.execute("filesystem.write", {"path": "secret.txt", "content": marker}, run_id=owner)
    victim = battery.session(owner)
    looked = battery.shell(
        "grep -rl --exclude-dir=proc --exclude-dir=sys --exclude-dir=dev "
        f"{marker} / 2>/dev/null | head -5",
        run_id=intruder, timeoutSeconds=60)
    found = marker in out(looked) or "secret.txt" in out(looked)
    named = battery.execute("filesystem.read",
                            {"path": f"../{victim.container_name}/secret.txt"}, run_id=intruder)
    defended = not found and named.status == "DENIED"
    return defended, (f"search for the other run's token found "
                      f"{'it' if found else 'nothing'}; naming its container: {verdict(named)}")


def host_path(battery: Battery) -> tuple[bool, str]:
    run_id = battery.run_id()
    probe = battery.shell(
        "for p in /host /mnt/c /c /run/desktop/mnt/host /Users /home/cesar /var/lib/docker; do "
        "if [ -e \"$p\" ]; then echo PRESENT:$p; fi; done; "
        "awk '{print $4, $5}' /proc/self/mountinfo", run_id=run_id)
    text = out(probe)
    present = [line for line in text.splitlines() if line.startswith("PRESENT:")]
    mounts = [line for line in text.splitlines()
              if line.strip() and not line.startswith("PRESENT:")]
    workspace = [line for line in mounts if line.split(" ")[-1] == "/workspace"]
    host_backed = [line for line in mounts
                   if line.split(" ")[-1] not in ("/etc/resolv.conf", "/etc/hostname",
                                                  "/etc/hosts")
                   and line.split(" ")[0] not in ("/",)
                   and line.split(" ")[-1] not in ("/", "/workspace", "/tmp", "/proc", "/dev",
                                                   "/sys", "/dev/pts", "/dev/mqueue",
                                                   "/dev/shm", "/sys/fs/cgroup")
                   and not line.split(" ")[-1].startswith(("/proc/", "/sys/", "/dev/"))]
    defended = probe.exit_code == 0 and not present and bool(workspace) and not host_backed
    return defended, (f"host paths present: {present or 'none'}; unexpected mounts: "
                      f"{host_backed or 'none'}")


def host_secret(battery: Battery) -> tuple[bool, str]:
    run_id = battery.run_id()
    os.environ[SENTINEL_NAME] = SENTINEL_VALUE
    try:
        seen = battery.shell("env; cat /proc/1/environ | tr '\\000' '\\n'", run_id=run_id)
    finally:
        os.environ.pop(SENTINEL_NAME, None)
    text = out(seen)
    leaked = [name for name in (SENTINEL_NAME, "DEVWORLD", "GITHUB_TOKEN", "SSH_AUTH_SOCK",
                                "DOCKER_HOST", "IACODE_DATABASE_URL", "IACODE_MINIO_SECRET_KEY",
                                "AWS_", "AZURE_", "GOOGLE_APPLICATION")
              if name in text]
    defended = seen.status == "SUCCEEDED" and SENTINEL_VALUE not in text and not leaked
    return defended, f"variables of the controller visible in the sandbox: {leaked or 'none'}"


def docker_socket(battery: Battery) -> tuple[bool, str]:
    run_id = battery.run_id()
    probe = battery.shell(
        "for s in /var/run/docker.sock /run/docker.sock /var/run/containerd/containerd.sock; do "
        "if [ -e $s ]; then echo PRESENT:$s; fi; done; "
        "python3 -c \"import socket; s=socket.socket(); s.settimeout(2); "
        "print('TCP2375', s.connect_ex(('host.docker.internal', 2375)))\" 2>&1 | tail -1",
        run_id=run_id)
    text = out(probe)
    defended = "PRESENT:" not in text and "TCP2375 0" not in text
    return defended, text.strip().replace("\n", " | ")[:200]


def unknown_tool(battery: Battery) -> tuple[bool, str]:
    run_id = battery.run_id()
    before = len(battery.containers())
    seen = [verdict(battery.execute(name, {"command": "id"}, run_id=run_id))
            for name in ("shell", "bash", "rm -rf /", "os.system", "git.push")]
    started = len(battery.containers()) - before
    defended = all(item == "DENIED/UNKNOWN_TOOL" for item in seen) and started == 0
    return defended, f"{seen}; containers started: {started}"


def policy_escalation(battery: Battery) -> tuple[bool, str]:
    run_id = battery.run_id()
    beside = [verdict(battery.execute("shell.exec", {"command": "true"}, run_id=run_id,
                                      **{key: value}))
              for key, value in (("network", "full"), ("memory", "unlimited"),
                                 ("mount", "C:\\"), ("privileged", True),
                                 ("image", "alpine:latest"))]
    inside = [verdict(battery.execute("shell.exec", {"command": "true", key: value},
                                      run_id=run_id))
              for key, value in (("network", "full"), ("timeoutSeconds", 100000),
                                 ("environment", {"LD_PRELOAD": "/tmp/x.so"}))]
    reviewer = verdict(battery.execute("filesystem.write", {"path": "x", "content": "y"},
                                       run_id=run_id, policy="reviewer"))
    unknown_policy = verdict(battery.execute("shell.exec", {"command": "true"}, run_id=run_id,
                                             policy="root"))
    defended = (all(item == "DENIED/CONTRACT_UNKNOWN_FIELD" for item in beside)
                and inside == ["DENIED/ARGUMENT_UNKNOWN", "DENIED/ARGUMENT_OUT_OF_RANGE",
                               "DENIED/ENVIRONMENT_NOT_ALLOWED"]
                and reviewer in ("DENIED/TOOL_NOT_IN_POLICY", "DENIED/WORKSPACE_READ_ONLY")
                and unknown_policy == "DENIED/POLICY_UNKNOWN")
    return defended, (f"beside the contract {beside}; inside the arguments {inside}; reviewer "
                      f"write {reviewer}; unknown policy {unknown_policy}")


def timeout(battery: Battery) -> tuple[bool, str]:
    run_id = battery.run_id()
    result = battery.shell("sleep 60", run_id=run_id, timeoutSeconds=2)
    after = battery.execute("shell.exec", {"command": "ps -eo args | grep -c '[s]leep 60'"},
                            run_id=run_id)
    left = out(after).strip().splitlines()[0] if out(after).strip() else "?"
    defended = (result.status == "TIMED_OUT" and result.timed_out
                and result.duration_ms < 15000 and left == "0")
    return defended, (f"{verdict(result)} after {result.duration_ms} ms; sleeps left "
                      f"running: {left}")


def orphan_child(battery: Battery) -> tuple[bool, str]:
    run_id = battery.run_id()
    result = battery.shell("setsid sh -c 'sleep 300' & nohup sleep 301 & sleep 60",
                           run_id=run_id, timeoutSeconds=2)
    after = battery.shell("ps -eo args | grep -c '[s]leep 30'", run_id=run_id)
    left = out(after).strip().splitlines()[0] if out(after).strip() else "?"
    defended = result.status == "TIMED_OUT" and left == "0"
    return defended, f"{verdict(result)}; escaped sleeps left running: {left}"


def output_bomb(battery: Battery) -> tuple[bool, str]:
    run_id = battery.run_id()
    result = battery.shell("head -c 40000000 /dev/zero | tr '\\000' 'x'", run_id=run_id,
                           timeoutSeconds=120)
    inline = len(str(result.output.get("stdout") or ""))
    limit = battery.service.policies.get("developer").resources.output_bytes
    defended = result.truncated and inline <= limit and bool(result.artifacts)
    return defended, (f"{verdict(result)}, truncated={result.truncated}, inline {inline} "
                      f"bytes against {limit}, artifacts {len(result.artifacts)}")


def pid_pressure(battery: Battery) -> tuple[bool, str]:
    run_id = battery.run_id()
    bomb = battery.shell("bomb() { bomb | bomb & }; bomb", run_id=run_id, timeoutSeconds=5)
    swept = int(bomb.output.get("orphansKilled") or 0)
    alive = battery.shell("echo alive; ls -d /proc/[0-9]* | wc -l", run_id=run_id)
    lines = out(alive).strip().splitlines()
    left = int(lines[1]) if len(lines) > 1 and lines[1].strip().isdigit() else -1
    # The detached bomb's own command returns at once; what matters is that the sweep after it
    # killed its descendants and the sandbox still starts the next command with an empty table:
    # the init process, the helper, the shell, ls and wc.
    defended = swept > 0 and lines[:1] == ["alive"] and 0 < left <= 6
    return defended, (f"bomb {verdict(bomb)}, {swept} descendants killed by the sweep; afterwards "
                      f"{verdict(alive)} {lines[:1]}, {left} processes in the sandbox")


def memory_cap(battery: Battery) -> tuple[bool, str]:
    run_id = battery.run_id()
    hog = battery.shell("python3 -c \"b = bytearray(3 * 1024 ** 3); print(len(b))\"",
                        run_id=run_id, timeoutSeconds=60)
    alive = battery.shell("echo alive", run_id=run_id)
    defended = hog.status == "FAILED" and hog.exit_code not in (None, 0) \
        and out(alive).strip() == "alive"
    return defended, (f"3 GiB allocation {verdict(hog)} exit {hog.exit_code}; afterwards "
                      f"{out(alive).strip()}")


def remote_git(battery: Battery) -> tuple[bool, str]:
    run_id = battery.run_id()
    push = battery.shell("git remote add origin https://github.com/pinguim16/iacode.git && "
                         "GIT_TERMINAL_PROMPT=0 git push origin HEAD", run_id=run_id,
                         timeoutSeconds=60)
    helpers = battery.shell("git config --get-all credential.helper; echo END-HELPERS; "
                            "for f in ~/.ssh ~/.git-credentials ~/.netrc; do "
                            "if [ -e $f ]; then echo PRESENT:$f; fi; done", run_id=run_id)
    configured = out(helpers).split("END-HELPERS")[0].strip()
    tools = [verdict(battery.execute(name, {}, run_id=run_id))
             for name in ("git.push", "git.fetch", "git.clone", "git.remote")]
    defended = (push.exit_code not in (None, 0)
                and not configured and "PRESENT:" not in out(helpers)
                and all(item == "DENIED/UNKNOWN_TOOL" for item in tools))
    return defended, (f"a push from the shell exited {push.exit_code}; remote tools {tools}; "
                      f"credential helper: {configured or 'none'}")


def destructive_git(battery: Battery) -> tuple[bool, str]:
    run_id = battery.run_id()
    tools = [verdict(battery.execute(name, {"revision": "HEAD"}, run_id=run_id))
             for name in ("git.reset", "git.clean", "git.rebase", "git.filter-repo")]
    option = verdict(battery.execute("git.show", {"revision": "--output=/workspace/x"},
                                     run_id=run_id))
    injected = verdict(battery.execute("git.show", {"revision": "HEAD; rm -rf ."},
                                       run_id=run_id))
    defended = (all(item == "DENIED/UNKNOWN_TOOL" for item in tools)
                and option == injected == "DENIED/GIT_REVISION_INVALID")
    return defended, f"tools {tools}; option-like revision {option}; injected revision {injected}"


def network_egress(battery: Battery) -> tuple[bool, str]:
    run_id = battery.run_id()
    probe = battery.shell(
        "python3 - <<'PY'\n"
        "import socket\n"
        "for host, port in (('1.1.1.1', 53), ('8.8.8.8', 443), ('github.com', 443)):\n"
        "    s = socket.socket(); s.settimeout(3)\n"
        "    try:\n"
        "        s.connect((host, port)); print('CONNECTED', host)\n"
        "    except Exception as error:\n"
        "        print('REFUSED', host, type(error).__name__)\n"
        "PY\n"
        "ls /sys/class/net", run_id=run_id, timeoutSeconds=60)
    text = out(probe)
    interfaces = text.strip().splitlines()[-1:] if text.strip() else []
    defended = "CONNECTED" not in text and text.count("REFUSED") == 3 and interfaces == ["lo"]
    return defended, text.strip().replace("\n", " | ")[:220]


def result_forgery(battery: Battery) -> tuple[bool, str]:
    """A retried request with the same identifier carrying a different command."""
    run_id = battery.run_id()
    first = battery.payload("shell.exec", {"command": "echo first"}, run_id=run_id)
    forged = dict(first, arguments={"command": "touch /workspace/forged && echo forged"})
    one = asyncio.run(battery.service.execute(first))
    two = asyncio.run(battery.service.execute(forged))
    check = battery.execute("filesystem.list", {"path": "."}, run_id=run_id)
    names = {entry["path"] for entry in check.output.get("entries") or []}
    defended = (out(one).strip() == "first" and two.replayed and not one.replayed
                and (two.status, two.exit_code) == (one.status, one.exit_code)
                and "forged" not in names)
    return defended, (f"the second delivery was answered from the record (replayed="
                      f"{two.replayed}, {verdict(two)}, exit {two.exit_code}) and the forged "
                      f"command {'ran' if 'forged' in names else 'never ran'}")


def cross_run_session(battery: Battery) -> tuple[bool, str]:
    victim, attacker = battery.run_id(), battery.run_id()
    battery.shell("true", run_id=victim)
    session = battery.session(victim)
    named = verdict(battery.execute("shell.exec", {"command": "true"}, run_id=attacker,
                                    sessionId=session.session_id))
    container = verdict(battery.execute("shell.exec", {"command": "true"}, run_id=attacker,
                                        containerName=session.container_name))
    battery.shell("true", run_id=attacker)
    theirs = battery.session(attacker)
    defended = (named == container == "DENIED/CONTRACT_UNKNOWN_FIELD"
                and theirs.session_id != session.session_id
                and theirs.container_name != session.container_name)
    return defended, (f"naming the victim's session {named}, its container {container}; the "
                      "attacker got a sandbox of its own")


def container_privileges(battery: Battery) -> tuple[bool, str]:
    run_id = battery.run_id()
    battery.shell("true", run_id=run_id)
    inspected = DockerBackend().inspect(battery.session(run_id).container_name) or {}
    host = inspected.get("HostConfig") or {}
    config = inspected.get("Config") or {}
    facts = {
        "privileged": host.get("Privileged"),
        "capAdd": host.get("CapAdd"),
        "capDrop": host.get("CapDrop"),
        "readOnlyRoot": host.get("ReadonlyRootfs"),
        "noNewPrivileges": "no-new-privileges" in " ".join(host.get("SecurityOpt") or []),
        "user": config.get("User"),
        "network": host.get("NetworkMode"),
        "binds": host.get("Binds"),
        "mounts": [item.get("Type") for item in inspected.get("Mounts") or []],
        "pidsLimit": host.get("PidsLimit"),
        "memory": host.get("Memory"),
    }
    readonly = battery.shell("touch /usr/bin/owned 2>&1; echo x > /etc/passwd 2>&1; id -u",
                             run_id=run_id)
    defended = (facts["privileged"] is False and not facts["capAdd"]
                and [item.upper() for item in facts["capDrop"] or []] == ["ALL"]
                and facts["readOnlyRoot"] is True and facts["noNewPrivileges"]
                and facts["user"] not in ("", "0", "root") and facts["network"] == "none"
                and not facts["binds"] and not facts["mounts"]
                and (facts["pidsLimit"] or 0) > 0 and (facts["memory"] or 0) > 0
                and "Read-only file system" in out(readonly)
                and out(readonly).strip().splitlines()[-1] != "0")
    return defended, json.dumps(facts)[:300]


def stale_image(battery: Battery) -> tuple[bool, str]:
    """A service whose image inputs changed refuses rather than running the old image."""
    with tempfile.TemporaryDirectory(prefix="iacode-stale-") as directory:
        copy = Path(directory)
        shutil.copytree(ROOT / ".iacode" / "policies", copy / ".iacode" / "policies")
        shutil.copytree(ROOT / "services" / "sandbox" / "images",
                        copy / "services" / "sandbox" / "images")
        source = copy / "services" / "sandbox" / "src" / "iacode_sandbox"
        source.mkdir(parents=True)
        for name in ("helper.py", "paths.py", "patching.py"):
            shutil.copy2(ROOT / "services" / "sandbox" / "src" / "iacode_sandbox" / name,
                         source / name)
        dockerfile = copy / "services" / "sandbox" / "images" / "iacode-dev" / "Dockerfile"
        dockerfile.write_text(dockerfile.read_text(encoding="utf-8")
                              + "\n# changed by the red team\n", encoding="utf-8")
        mutated = Battery(root=copy)
        try:
            run_id = mutated.run_id()
            result = mutated.execute("shell.exec", {"command": "true"}, run_id=run_id)
            started = len(mutated.containers())
        finally:
            mutated.close()
    defended = (result.status in ("FAILED", "DENIED")
                and result.error_code in ("SANDBOX_IMAGE_MISSING", "SANDBOX_IMAGE_STALE")
                and started == 0)
    return defended, f"{verdict(result)}; containers started: {started}"


def command_injection(battery: Battery) -> tuple[bool, str]:
    run_id = battery.run_id()
    read = verdict(battery.execute("filesystem.read", {"path": "a.txt; touch /workspace/pwn"},
                                   run_id=run_id))
    search = battery.execute("filesystem.search",
                             {"pattern": "$(touch /workspace/pwn2)", "regex": False},
                             run_id=run_id)
    shell = battery.shell("echo injected; touch /tmp/inside-only && ls /tmp/inside-only",
                          run_id=run_id)
    listing = battery.execute("filesystem.list", {"path": "."}, run_id=run_id)
    names = {entry["path"] for entry in listing.output.get("entries") or []}
    defended = ("pwn" not in names and "pwn2" not in names
                and shell.status == "SUCCEEDED" and "/tmp/inside-only" in out(shell))
    return defended, (f"path with a command {read}; pattern with a command "
                      f"{verdict(search)}; neither ran; the shell's own command stayed inside "
                      f"its sandbox")


ATTACKS = {
    "G3-A": path_traversal,
    "G3-B": symlink_escape,
    "G3-C": workspace_cross_read,
    "G3-D": host_path,
    "G3-E": host_secret,
    "G3-F": docker_socket,
    "G3-G": unknown_tool,
    "G3-H": policy_escalation,
    "G3-I": timeout,
    "G3-J": orphan_child,
    "G3-K": output_bomb,
    "G3-L": pid_pressure,
    "G3-M": memory_cap,
    "G3-N": remote_git,
    "G3-O": destructive_git,
    "G3-P": network_egress,
    "G3-Q": result_forgery,
    "G3-R": cross_run_session,
    "G3-S": container_privileges,
    "G3-T": stale_image,
    "G3-U": command_injection,
}


def main() -> int:
    battery = Battery()
    verdicts: dict[str, dict[str, Any]] = {}
    try:
        accepted, observed = baseline(battery)
        verdicts["baseline"] = {"defended": accepted, "observed": observed}
        for identifier, attack in ATTACKS.items():
            try:
                defended, observed = attack(battery)
            except Exception as error:  # noqa: BLE001 - a crashed attack has found something
                defended, observed = False, f"the attack failed: {type(error).__name__}: {error}"
            verdicts[identifier] = {"defended": defended, "observed": observed[:500]}
            print(f"[{'DEFENDED' if defended else 'ESCAPED'}] {identifier}: {observed[:140]}",
                  file=sys.stderr, flush=True)
        verdicts["residue"] = {"containers": len(battery.containers())}
    finally:
        battery.close()
    verdicts["residueAfterRelease"] = {"containers": len(battery.containers())}
    print(json.dumps(verdicts), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
