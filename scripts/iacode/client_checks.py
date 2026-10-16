"""Reusable owned client capsules. Decision tests are never labelled live runtime acceptance."""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import uuid
from pathlib import Path

from build_clients import CORE, ROOT, build

NODE_IMAGE = (
    "node:22.23.2-bookworm-slim@sha256:"
    "48e4b67d85f87bd551df43704e24d252f56cc5f8e9718841aace50f19948f0f9"
)


def capsule(directory: Path) -> None:
    for project in ("cli", "vscode-extension"):
        shutil.copytree(
            ROOT / "apps" / project,
            directory / project,
            ignore=shutil.ignore_patterns("node_modules", "out", "*.vsix"),
        )
    for name, source in CORE.items():
        for destination in (directory / "cli/src", directory / "vscode-extension/src/core"):
            destination.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / source, destination / name)


def run_node(*, guard: bool | str = False, node: Path | None = None) -> subprocess.CompletedProcess:
    if guard not in (False, True, "native-root"):
        raise ValueError("unknown closed client guard")
    with tempfile.TemporaryDirectory(prefix="iacode-client-cases-") as temporary:
        directory = Path(temporary)
        capsule(directory)
        tests = (
            [
                "vscode-extension/tests/extension.test.cjs"
                if guard == "native-root"
                else "cli/tests/core.test.cjs"
            ]
            if guard
            else [
                *[
                    f"cli/tests/{path.name}"
                    for path in sorted((directory / "cli/tests").glob("*.test.cjs"))
                ],
                *[
                    f"vscode-extension/tests/{path.name}"
                    for path in sorted((directory / "vscode-extension/tests").glob("*.test.cjs"))
                ],
            ]
        )
        arguments = ["--test", "--test-concurrency=1"]
        if guard:
            pattern = (
                "canonical filesystem spelling"
                if guard == "native-root"
                else "signed malformed mutation result"
            )
            arguments += ["--test-name-pattern=" + pattern]
        if node:
            environment = {
                **os.environ,
                "IACODE_CLIENT_MODULE": str(directory / "cli/src/client.cjs"),
                "IACODE_CLI_ENTRY": str(directory / "cli/bin/iacode.cjs"),
                "IACODE_EXTENSION_MODULE": str(directory / "vscode-extension/src/extension.cjs"),
            }
            return subprocess.run(
                [str(node), *arguments, *tests],
                cwd=directory,
                env=environment,
                text=True,
                encoding="utf-8",
                errors="replace",
                capture_output=True,
                timeout=180,
                check=False,
            )
        name = "iacode-client-unit-" + uuid.uuid4().hex
        try:
            return subprocess.run(
                [
                    "docker",
                    "run",
                    "--name",
                    name,
                    "--rm",
                    "--network",
                    "none",
                    "--read-only",
                    "--user",
                    "1000:1000",
                    "--cap-drop",
                    "ALL",
                    "--security-opt",
                    "no-new-privileges:true",
                    "--pids-limit",
                    "96",
                    "--memory",
                    "384m",
                    "--cpus",
                    "1",
                    "--tmpfs",
                    "/tmp:rw,noexec,nosuid,nodev,size=48m,mode=1777",
                    "--volume",
                    f"{directory.resolve()}:/client:ro",
                    "--workdir",
                    "/client",
                    "--env",
                    "IACODE_CLIENT_MODULE=/client/cli/src/client.cjs",
                    "--env",
                    "IACODE_CLI_ENTRY=/client/cli/bin/iacode.cjs",
                    "--env",
                    "IACODE_EXTENSION_MODULE=/client/vscode-extension/src/extension.cjs",
                    NODE_IMAGE,
                    "node",
                    *arguments,
                    *tests,
                ],
                cwd=ROOT,
                text=True,
                encoding="utf-8",
                errors="replace",
                capture_output=True,
                timeout=180,
                check=False,
            )
        finally:
            # Only the exact container this invocation named. Never a project/global prune.
            removed = subprocess.run(
                ["docker", "rm", "-f", name],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
                timeout=30,
            )
            if removed.returncode and "No such container" not in removed.stderr:
                raise RuntimeError("owned client-test container cleanup failed")


def verify_packages() -> dict:
    with tempfile.TemporaryDirectory(prefix="iacode-client-build-") as temporary:
        directory = Path(temporary)
        first = build(directory / "first")
        second = build(directory / "second")
        if first != second:
            raise RuntimeError("client package build is not deterministic")
        return first
