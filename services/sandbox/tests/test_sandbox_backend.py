"""Every sandbox container is created by one function, with every hardening flag, from a policy."""

from __future__ import annotations

import ast
from pathlib import Path

import iacode_sandbox
from iacode_sandbox.backend import (
    DOCKER,
    LABEL_MANAGED,
    BackendError,
    ContainerSpec,
    DockerBackend,
    container_arguments,
)

SPEC = ContainerSpec(name="iacode-sbx-test", image="iacode/sandbox-iacode-dev:abc",
                     session_id="s-1", run_id="r-1", policy="developer",
                     expires_at_epoch=2_000_000_000, cpus=1.0, memory_mb=1024, pids=256,
                     workspace_mb=256, tmp_mb=64)

PACKAGE = Path(iacode_sandbox.__file__).resolve().parent


def pairs(arguments: list[str]) -> dict[str, list[str]]:
    found: dict[str, list[str]] = {}
    for index, token in enumerate(arguments[:-1]):
        if token.startswith("--"):
            found.setdefault(token, []).append(arguments[index + 1])
    return found


class ContainerSpecTests:
    def test_every_isolation_flag_is_emitted(self) -> None:
        arguments = container_arguments(SPEC)
        flags = pairs(arguments)
        assert arguments[:3] == [DOCKER, "run", "--detach"]
        assert "--read-only" in arguments
        assert flags["--cap-drop"] == ["ALL"]
        assert flags["--security-opt"] == ["no-new-privileges"]
        assert flags["--user"] == ["10001:10001"]
        assert flags["--network"] == ["none"]
        assert flags["--memory"] == ["1024m"] and flags["--memory-swap"] == ["1024m"]
        assert flags["--pids-limit"] == ["256"]
        assert flags["--cpus"] == ["1"]

    def test_no_privilege_and_no_host_resource_can_be_granted(self) -> None:
        arguments = container_arguments(SPEC)
        joined = " ".join(arguments)
        for forbidden in ("--privileged", "--volume", "-v", "--mount", "--env", "-e",
                          "--env-file", "--cap-add", "--device", "--pid", "--ipc",
                          "--userns", "--network=host", "--volumes-from", "--group-add"):
            assert forbidden not in arguments, forbidden
        for forbidden in ("docker.sock", "/var/run", "C:\\", "/home", "/root", ".ssh",
                          "unconfined"):
            assert forbidden not in joined, forbidden

    def test_the_writable_places_are_bounded_in_memory_filesystems(self) -> None:
        mounts = pairs(container_arguments(SPEC))["--tmpfs"]
        assert len(mounts) == 2
        workspace, temporary = mounts
        assert workspace.startswith("/workspace:") and "size=256m" in workspace
        assert "nosuid" in workspace and "nodev" in workspace
        assert temporary.startswith("/tmp:") and "size=64m" in temporary
        assert "noexec" in temporary

    def test_every_container_carries_the_ownership_labels(self) -> None:
        labels = pairs(container_arguments(SPEC))["--label"]
        assert f"{LABEL_MANAGED}=1" in labels
        assert "org.iacode.sandbox.session=s-1" in labels
        assert "org.iacode.sandbox.run=r-1" in labels

    def test_the_image_decides_the_command_not_the_request(self) -> None:
        assert container_arguments(SPEC)[-1] == SPEC.image

    def test_the_backend_starts_only_the_container_client(self) -> None:
        backend = DockerBackend()
        try:
            backend._run(["sh", "-c", "id"])
        except BackendError as refused:
            assert refused.code == "BACKEND_INVALID"
        else:
            raise AssertionError("the backend started something that is not the Docker client")
        try:
            DockerBackend(executable="/bin/sh")
        except BackendError as refused:
            assert refused.code == "BACKEND_INVALID"
        else:
            raise AssertionError("the backend accepted another executable")

    def test_no_module_of_the_controller_uses_a_shell(self) -> None:
        """Only the helper runs a shell, inside a sandbox, for shell.exec; the controller never."""
        offenders = []
        for path in sorted(PACKAGE.glob("*.py")):
            if path.name == "helper.py":
                continue
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.keyword) and node.arg == "shell":
                    offenders.append(f"{path.name}: shell=")
                if isinstance(node, ast.Attribute) and node.attr in ("system", "popen") \
                        and isinstance(node.value, ast.Name) and node.value.id == "os":
                    offenders.append(f"{path.name}: os.{node.attr}")
        assert offenders == []

    def test_only_the_backend_and_the_helper_start_processes(self) -> None:
        launchers = set()
        for path in sorted(PACKAGE.glob("*.py")):
            source = path.read_text(encoding="utf-8")
            if "subprocess." in source:
                launchers.add(path.name)
        assert launchers == {"backend.py", "helper.py"}
