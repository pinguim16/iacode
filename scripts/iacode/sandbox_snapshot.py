#!/usr/bin/env python3
"""Store a directory as an authorised workspace snapshot, and print its artifact identifier.

A run's sandbox never sees the host's filesystem. What it can start from is a snapshot: the regular
files of a directory the operator names here, archived by `iacode_sandbox.snapshots` (links refused,
`.git` and caches left out), stored in the Foundation's bucket with a row in `artifacts` and its
SHA-256. Pass the printed `artifactId` as `workspaceSnapshot` when creating a run.

The archive is built inside the sandbox service's image, which can reach the database and the
bucket, with the directory mounted read-only for that one command. The stack must be running.

    python scripts/iacode/sandbox_snapshot.py --source path/to/directory --name my-snapshot
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from compose import compose, log, main_guard, require_docker


def create(source: Path, name: str) -> dict[str, object]:
    """Archive ``source`` as the snapshot ``name``; the result names its artifact."""
    if not source.is_dir():
        raise SystemExit(f"{source} is not a directory")
    if not re.fullmatch(r"[a-z0-9][a-z0-9._-]{0,63}", name):
        raise SystemExit("--name is lowercase letters, digits, '.', '_' and '-'")
    result = compose(
        "run", "--rm", "--no-deps", "--entrypoint", "",
        "--volume", f"{source.resolve()}:/input:ro",
        "sandbox", "python", "-m", "iacode_sandbox.snapshots", "create",
        "--source", "/input", "--name", name,
        merge_stderr=False)
    lines = [line for line in result.stdout.splitlines() if line.strip().startswith("{")]
    if not result.ok or not lines:
        raise SystemExit(f"the snapshot could not be stored:\n{result.output[-1500:]}")
    return json.loads(lines[-1])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--name", required=True)
    arguments = parser.parse_args()
    require_docker()
    snapshot = create(arguments.source, arguments.name)
    if "error" in snapshot:
        log(f"SANDBOX_SNAPSHOT=FAIL {snapshot['error']}: {snapshot.get('detail')}")
        return 1
    log(f"SANDBOX_SNAPSHOT=PASS artifactId={snapshot['artifactId']} sha256={snapshot['sha256']}")
    print(json.dumps(snapshot))
    return 0


if __name__ == "__main__":
    main_guard(main)
