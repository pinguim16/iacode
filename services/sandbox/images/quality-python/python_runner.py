#!/usr/bin/env python3
"""Run the pinned Python quality command with every local ``src`` package importable."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

IGNORED = frozenset({".git", ".venv", "build", "dist", "node_modules", "target", "vendor"})


def local_sources(root: Path) -> list[str]:
    sources: list[str] = []
    for current, directories, _filenames in os.walk(root, followlinks=False):
        directories[:] = sorted(name for name in directories if name not in IGNORED)
        path = Path(current)
        if path.name == "src":
            sources.append(str(path))
            directories[:] = []
    return sorted(sources)


def prepare_test_project(project: Path, repository: Path, environment: dict[str, str]) -> None:
    """Install local metadata and expose repository configuration inside the sandbox."""
    repository_config = repository / ".iacode"
    project_config = project / ".iacode"
    if project != repository and repository_config.is_dir() and not project_config.exists():
        project_config.symlink_to(repository_config, target_is_directory=True)
    if not (project / "pyproject.toml").is_file():
        return
    # /tmp is this sandbox's private, size-limited tmpfs and is never a host directory.
    target = Path("/tmp/iacode-quality-site")  # noqa: S108
    target.mkdir(parents=True, exist_ok=True)
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--disable-pip-version-check",
            "--no-deps",
            "--no-build-isolation",
            "--target",
            str(target),
            ".",
        ],
        cwd=project,
        env=environment,
        check=False,
    )
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)
    environment["PYTHONPATH"] = os.pathsep.join(
        [str(target), environment.get("PYTHONPATH", "")]
    ).rstrip(os.pathsep)


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: iacode-quality-python COMMAND [ARG ...]", file=sys.stderr)
        return 2
    environment = os.environ.copy()
    environment["IACODE_REPOSITORY_ROOT"] = "/workspace"
    inherited = environment.get("PYTHONPATH")
    entries = local_sources(Path("/workspace"))
    if inherited:
        entries.append(inherited)
    environment["PYTHONPATH"] = os.pathsep.join(entries)
    if "pytest" in sys.argv:
        prepare_test_project(Path.cwd(), Path("/workspace"), environment)
    # The argv comes only from the closed evaluator runner registry, never from project content.
    os.execvpe(sys.argv[1], sys.argv[1:], environment)  # noqa: S606
    return 127


if __name__ == "__main__":
    sys.exit(main())
