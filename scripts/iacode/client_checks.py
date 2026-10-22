"""Reusable owned client capsules. Decision tests are never labelled live runtime acceptance."""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path

from build_clients import CORE, ROOT, build

sys.path.insert(0, str(ROOT / "packages/common/src"))
from iacode_common.secret_scanning import find_secret_kinds

NODE_IMAGE = (
    "node:22.23.2-bookworm-slim@sha256:"
    "48e4b67d85f87bd551df43704e24d252f56cc5f8e9718841aace50f19948f0f9"
)

MAX_OBSERVATION_BYTES = 262144


class ClientCheckError(RuntimeError):
    """Safe, bounded producer and cleanup observations; no raw exception or hidden PASS."""

    def __init__(self, producer: dict, cleanup: dict) -> None:
        self.report = {
            "schemaVersion": "1.0.0",
            "result": "FAIL",
            "producer": producer,
            "cleanup": cleanup,
        }
        super().__init__(
            "client verification failed: " + json.dumps(self.report, ensure_ascii=True)
        )


def _safe_stream(value: str | bytes | None) -> dict:
    raw = value.encode("utf-8") if isinstance(value, str) else (value or b"")
    result = {
        "text": None,
        "sha256": hashlib.sha256(raw).hexdigest(),
        "bytes": len(raw),
        "refusal": None,
    }
    if len(raw) > MAX_OBSERVATION_BYTES:
        result["refusal"] = "OUTPUT_LIMIT"
        return result
    try:
        text = raw.decode("utf-8", errors="strict")
        if find_secret_kinds(text) or find_secret_kinds(json.dumps(text, ensure_ascii=True)):
            result["refusal"] = "UNSAFE_OUTPUT"
        else:
            result["text"] = text
    except UnicodeError:
        result["refusal"] = "OUTPUT_ENCODING"
    except Exception:  # Scanner failure is refusal, never permission to publish raw output.
        result["refusal"] = "OUTPUT_SCAN_FAILED"
    return result


def _attempt(argv: list[str], timeout: int) -> tuple[subprocess.CompletedProcess | None, dict]:
    completed = None
    status, exit_code, stdout, stderr = "COMPLETED", None, None, None
    try:
        # Capture bytes: a replacement decoder would destroy the original stream identity.
        completed = subprocess.run(
            argv, cwd=ROOT, capture_output=True, timeout=timeout, check=False
        )
        exit_code, stdout, stderr = completed.returncode, completed.stdout, completed.stderr
    except subprocess.TimeoutExpired as exc:
        status, stdout, stderr = "TIMEOUT", exc.stdout, exc.stderr
    except OSError:
        # OSError messages can contain arbitrary path/content. The typed launch fact is sufficient.
        status = "LAUNCH_ERROR"
    observation = {"status": status, "exitCode": exit_code, "arguments": list(argv)}
    for name, value in (("stdout", stdout), ("stderr", stderr)):
        safe = _safe_stream(value)
        observation[name] = safe["text"]
        observation[name + "Sha256"] = safe["sha256"]
        observation[name + "Bytes"] = safe["bytes"]
        observation[name + "Refusal"] = safe["refusal"]
    # Inspect argv too before it can enter a diagnostic. Never persist an unsafe argument list.
    if _safe_stream(json.dumps(argv, ensure_ascii=True))["refusal"]:
        observation["arguments"] = None
        observation["argumentsRefused"] = True
    return completed, observation


def _safe_observation(observation: dict) -> bool:
    return not any(
        observation.get(name) for name in ("stdoutRefusal", "stderrRefusal", "argumentsRefused")
    )


def _owned_container_absent(observation: dict, name: str) -> bool:
    if observation["status"] != "COMPLETED" or observation["exitCode"] != 1:
        return False
    return (
        re.fullmatch(
            r"(?:Error response from daemon: |Error: )?No such container: " + re.escape(name),
            (observation["stderr"] or "").strip(),
        )
        is not None
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
        completed, producer = _attempt(
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
            180,
        )
        # The producer observation exists BEFORE this independent, fallible cleanup attempt.
        # Only the exact container this invocation named. Never a project/global prune.
        _removed, cleanup = _attempt(["docker", "rm", "-f", name], 30)
        cleanup_ok = (
            cleanup["status"] == "COMPLETED" and cleanup["exitCode"] == 0
        ) or _owned_container_absent(cleanup, name)
        if (
            completed is None
            or not cleanup_ok
            or not _safe_observation(producer)
            or not _safe_observation(cleanup)
        ):
            raise ClientCheckError(producer, cleanup) from None
        completed.stdout, completed.stderr = producer["stdout"], producer["stderr"]
        return completed


def verify_packages() -> dict:
    with tempfile.TemporaryDirectory(prefix="iacode-client-build-") as temporary:
        directory = Path(temporary)
        first = build(directory / "first")
        second = build(directory / "second")
        if first != second:
            raise RuntimeError("client package build is not deterministic")
        return first
