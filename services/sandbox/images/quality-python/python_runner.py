#!/usr/bin/env python3
"""Run the pinned Python quality command with every local ``src`` package importable."""

from __future__ import annotations

import os
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


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: iacode-quality-python COMMAND [ARG ...]", file=sys.stderr)
        return 2
    environment = os.environ.copy()
    inherited = environment.get("PYTHONPATH")
    entries = local_sources(Path("/workspace"))
    if inherited:
        entries.append(inherited)
    environment["PYTHONPATH"] = os.pathsep.join(entries)
    # The argv comes only from the closed evaluator runner registry, never from project content.
    os.execvpe(sys.argv[1], sys.argv[1:], environment)  # noqa: S606
    return 127


if __name__ == "__main__":
    sys.exit(main())
