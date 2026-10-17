"""Run a child against the already available local Linux pipe, without global Docker changes."""

from __future__ import annotations

import os
import subprocess
import sys
from collections.abc import Mapping

ENGINE_ENDPOINT = "npipe:////./pipe/docker_engine_linux"


def engine_environment(base: Mapping[str, str] | None = None) -> dict[str, str]:
    environment = dict(os.environ if base is None else base)
    environment.pop("DOCKER_CONTEXT", None)
    environment["DOCKER_HOST"] = ENGINE_ENDPOINT
    return environment


def run_child(arguments: list[str]) -> int:
    if not arguments:
        raise ValueError("an explicit child command is required")
    executable = list(arguments)
    if executable[0] in {"python", "python3"}:
        executable[0] = sys.executable
    return subprocess.run(executable, env=engine_environment(), check=False).returncode


if __name__ == "__main__":
    arguments = sys.argv[1:]
    if arguments[:1] != ["--"]:
        raise ValueError("use -- followed by the exact child command")
    raise SystemExit(run_child(arguments[1:]))
