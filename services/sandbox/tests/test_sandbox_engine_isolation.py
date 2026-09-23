"""Isolation, measured inside real sandboxes on the real engine.

Every case here creates containers through the service exactly as a run would, and asks the sandbox
itself what it can see: who it runs as, which capabilities it holds, what is mounted, which network
interfaces exist, which environment variables it has, and whether a neighbouring sandbox is visible.
Nothing is inferred from configuration; the configuration is what is under test.
"""

from __future__ import annotations

import json
import os
import uuid

import pytest
from sandbox_fixtures import engine_harness

#: Mount points Docker manages inside every container, network or not. They come from the engine's
#: own VM, never from the host's user filesystem, and they are read-only files, not directories.
ENGINE_MANAGED_MOUNTS = {"/etc/hosts", "/etc/hostname", "/etc/resolv.conf"}

#: Filesystem types a bind mount of the Windows host or of the engine VM's disk would show.
HOST_FILESYSTEMS = ("ext4", "9p", "fuse", "grpcfuse", "fakeowner", "virtiofs", "drvfs", "ntfs",
                    "xfs", "btrfs")


@pytest.fixture
def harness():
    created = engine_harness()
    yield created
    created.close()


def output(result) -> str:
    return str(result.output.get("stdout", ""))


class ContainerIsolationTests:
    def test_the_sandbox_runs_unprivileged_with_no_capability(self, harness) -> None:
        run_id = harness.run_id()
        result = harness.shell("id -u; id -g; grep -E '^(Cap(Eff|Prm|Bnd|Amb)|NoNewPrivs)' "
                               "/proc/self/status", run_id=run_id)
        assert result.status == "SUCCEEDED", result
        lines = output(result).splitlines()
        assert lines[0] == "10001" and lines[1] == "10001"
        status = dict(line.split(":\t", 1) for line in lines[2:])
        for key in ("CapEff", "CapPrm", "CapBnd", "CapAmb"):
            assert int(status[key], 16) == 0, key
        assert status["NoNewPrivs"].strip() == "1"

    def test_the_root_filesystem_is_read_only(self, harness) -> None:
        run_id = harness.run_id()
        result = harness.shell("touch /etc/iacode-probe 2>&1; touch /usr/bin/probe 2>&1; "
                               "touch /workspace/allowed && echo workspace-writable", run_id=run_id)
        text = output(result)
        assert "Read-only file system" in text
        assert "workspace-writable" in text

    def test_no_docker_socket_or_engine_endpoint_is_reachable(self, harness) -> None:
        run_id = harness.run_id()
        result = harness.shell(
            "for p in /var/run/docker.sock /run/docker.sock /var/run/docker /run/containerd; do "
            "test -e $p && echo PRESENT:$p; done; env | grep -c DOCKER_ || true; "
            "grep -c docker.sock /proc/self/mountinfo || true", run_id=run_id)
        assert result.status == "SUCCEEDED", result
        text = output(result)
        assert "PRESENT" not in text
        assert text.split() == ["0", "0"]

    def test_no_host_path_is_mounted(self, harness) -> None:
        run_id = harness.run_id()
        result = harness.shell("cat /proc/self/mountinfo", run_id=run_id)
        offenders = []
        for line in output(result).splitlines():
            left, _, right = line.partition(" - ")
            mount_point = left.split()[4]
            filesystem = right.split()[0]
            if mount_point in ENGINE_MANAGED_MOUNTS:
                continue
            if any(filesystem.startswith(kind) for kind in HOST_FILESYSTEMS):
                offenders.append(f"{mount_point} ({filesystem})")
        assert offenders == [], offenders
        mounted = {line.split()[4] for line in output(result).splitlines()}
        assert "/workspace" in mounted
        for forbidden in ("/host", "/mnt/c", "/c", "/Users", "/home/cesar", "/root/.ssh"):
            assert forbidden not in mounted

    def test_the_workspace_is_bounded(self, harness) -> None:
        run_id = harness.run_id()
        result = harness.shell("df -k /workspace | tail -1", run_id=run_id)
        size_kb = int(output(result).split()[1])
        limit_mb = harness.service.policies.get("developer").resources.workspace_mb
        assert size_kb <= limit_mb * 1024


class NetworkIsolationTests:
    def test_the_default_network_has_only_loopback(self, harness) -> None:
        run_id = harness.run_id()
        result = harness.shell("ls /sys/class/net", run_id=run_id)
        assert output(result).split() == ["lo"]

    def test_external_egress_fails(self, harness) -> None:
        run_id = harness.run_id()
        probe = ("python3 -c \"import socket\n"
                 "for target in (('1.1.1.1', 53), ('8.8.8.8', 443)):\n"
                 "    try:\n"
                 "        socket.create_connection(target, timeout=3)\n"
                 "        print('CONNECTED', target)\n"
                 "    except OSError as error:\n"
                 "        print('REFUSED', type(error).__name__)\n"
                 "try:\n"
                 "    socket.getaddrinfo('github.com', 443)\n"
                 "    print('RESOLVED')\n"
                 "except OSError:\n"
                 "    print('NO_DNS')\"")
        result = harness.shell(probe, run_id=run_id, timeoutSeconds=30)
        text = output(result)
        assert "CONNECTED" not in text and "RESOLVED" not in text
        assert text.count("REFUSED") == 2 and "NO_DNS" in text

    def test_a_local_services_network_is_internal(self) -> None:
        """The second profile exists and is created internal: no route out, no neighbour."""
        import asyncio
        import dataclasses

        from iacode_sandbox.backend import DockerBackend
        from iacode_sandbox.contracts import WorkspaceSource

        created = engine_harness()
        developer = created.service.policies.get("developer")
        local = dataclasses.replace(developer, name="developer-local",
                                    network_profile="local-services")
        created.service.policies.policies["developer-local"] = local
        run_id = created.run_id()
        try:
            session = asyncio.run(created.service.create_session(run_id, local,
                                                                 WorkspaceSource()))
            network = f"iacode-sbx-net-{session.session_id.replace('-', '')}"
            assert DockerBackend().network_is_internal(network)
        finally:
            created.close()


class SecretIsolationTests:
    def test_no_variable_of_the_controller_reaches_a_sandbox(self, harness) -> None:
        sentinel_name = "IACODE_SANDBOX_TEST_SENTINEL"
        sentinel_value = uuid.uuid4().hex
        os.environ[sentinel_name] = sentinel_value
        try:
            run_id = harness.run_id()
            result = harness.shell("env", run_id=run_id)
        finally:
            del os.environ[sentinel_name]
        text = output(result)
        assert sentinel_name not in text and sentinel_value not in text
        names = {line.split("=", 1)[0] for line in text.splitlines() if "=" in line}
        for forbidden in ("IACODE_DATABASE_URL", "IACODE_MINIO_SECRET_KEY",
                          "IACODE_MINIO_ACCESS_KEY",
                          "DEVWORLD_API_KEY", "IACODE_DEVWORLD_API_KEY", "IACODE_OPENAI_API_KEY",
                          "GITHUB_TOKEN", "GH_TOKEN", "SSH_AUTH_SOCK", "DOCKER_HOST",
                          "AWS_ACCESS_KEY_ID"):
            assert forbidden not in names, forbidden
        assert not any(name.startswith("IACODE_") for name in names)

    def test_no_git_or_ssh_credential_exists(self, harness) -> None:
        run_id = harness.run_id()
        result = harness.shell(
            "git config --get credential.helper; echo helper:$?; "
            "ls -a /tmp/.ssh /home 2>&1 | head -3; test -e /tmp/.git-credentials && echo CREDS; "
            "git config --get protocol.allow", run_id=run_id)
        text = output(result)
        assert "CREDS" not in text
        assert "never" in text


class CrossSessionIsolationTests:
    def test_one_run_cannot_see_another_runs_files(self, harness) -> None:
        first, second = harness.run_id(), harness.run_id()
        marker = uuid.uuid4().hex
        written = harness.execute("filesystem.write", {"path": "secret.txt", "content": marker},
                                  run_id=first)
        assert written.status == "SUCCEEDED"
        listing = harness.execute("filesystem.list", {"path": ".", "depth": 4}, run_id=second)
        assert "secret.txt" not in json.dumps(listing.output)
        search = harness.shell(
            f"grep -rl --exclude-dir=proc --exclude-dir=sys --exclude-dir=dev {marker} / "
            "2>/dev/null | head -5; echo done", run_id=second, timeoutSeconds=120)
        assert output(search).split() == ["done"], output(search)

    def test_two_runs_have_two_containers_and_two_workspaces(self, harness) -> None:
        first, second = harness.run_id(), harness.run_id()
        harness.shell("true", run_id=first)
        harness.shell("true", run_id=second)
        one, two = harness.session(first), harness.session(second)
        assert one.container_name != two.container_name
        assert one.session_id != two.session_id

    def test_one_run_cannot_see_another_runs_processes(self, harness) -> None:
        import asyncio

        from sandbox_fixtures import request

        first, second = harness.run_id(), harness.run_id()
        harness.shell("true", run_id=first)
        harness.shell("true", run_id=second)

        async def both():
            sleeper = asyncio.ensure_future(harness.service.execute(request(
                "shell.exec", {"command": "sleep 4; echo slept-" + first[:8]}, run_id=first)))
            await asyncio.sleep(1.5)
            observer = await harness.service.execute(request(
                "shell.exec", {"command": "cat /proc/[0-9]*/cmdline | tr '\\0' ' '"},
                run_id=second))
            return await sleeper, observer

        slept, observed = asyncio.run(both())
        assert "slept-" + first[:8] in output(slept)
        assert "sleep 4" not in output(observed)
