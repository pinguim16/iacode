#!/usr/bin/env python3
"""Start, stop, rebuild and reset the Foundation stack.

One entry point for the stack's lifecycle, so the runbook documents commands rather than
incantations and every path stamps the images with the same build identity.

    python scripts/iacode/stack.py up          start, building what is missing, and wait for health
    python scripts/iacode/stack.py up --build  rebuild the images first
    python scripts/iacode/stack.py down        stop, keeping every volume
    python scripts/iacode/stack.py restart     restart the running services and wait for health
    python scripts/iacode/stack.py reset       stop and DELETE every volume
    python scripts/iacode/stack.py status      what is running and what its health is

``reset`` destroys data and therefore refuses to run without ``--yes``. That is the one guard in
this file: every other command is reversible, and this one deletes the database.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from compose import (
    HEALTHY_SERVICES,
    REPOSITORY_ROOT,
    StackError,
    compose,
    log,
    main_guard,
    read_env_file,
    wait_for_health,
)


def build_identity() -> dict[str, str]:
    """The version, commit and build instant stamped into every image.

    Without this the API reports ``commit: unknown``, which makes ``/version`` useless for the one
    question it exists to answer. The commit is read from Git and falls back rather than failing:
    the stack must still start from a source archive with no repository.
    """
    values = read_env_file()
    commit = "unknown"
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=str(REPOSITORY_ROOT), text=True,
            encoding="utf-8", errors="replace",
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=False)
        if completed.returncode == 0 and completed.stdout.strip():
            commit = completed.stdout.strip()
            dirty = subprocess.run(
                ["git", "status", "--porcelain"], cwd=str(REPOSITORY_ROOT), text=True,
                encoding="utf-8", errors="replace",
                stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=False)
            if dirty.returncode == 0 and dirty.stdout.strip():
                # An image built from a dirty tree is not the commit it names, and saying so beats
                # a version endpoint that confidently reports a commit nobody can check out.
                commit = f"{commit}-dirty"
    except OSError:
        pass
    return {
        "IACODE_VERSION": values.get("IACODE_VERSION", "0.1.0"),
        "IACODE_COMMIT": commit,
        "IACODE_BUILD_TIMESTAMP": datetime.now(UTC).isoformat(timespec="seconds").replace(
            "+00:00", "Z"),
    }


def up(build: bool, wait: bool) -> int:
    identity = build_identity()
    log(f"version={identity['IACODE_VERSION']} commit={identity['IACODE_COMMIT']}")
    arguments = ["up", "--detach", "--remove-orphans"]
    if build:
        arguments.append("--build")
    result = compose(*arguments, capture=False, extra_env=identity)
    if not result.ok:
        # Compose prints the failing container; repeating its output would bury the reason.
        raise StackError(f"the stack did not start (exit {result.exit_code}); see the output above")
    if wait:
        states = wait_for_health()
        log("every service is healthy: " + ", ".join(sorted(states)))
    return 0


def down(remove_volumes: bool) -> int:
    arguments = ["down", "--remove-orphans"]
    if remove_volumes:
        arguments.append("--volumes")
    compose(*arguments, capture=False, check=True)
    log("volumes deleted" if remove_volumes else "volumes kept")
    return 0


def restart(wait: bool) -> int:
    compose("restart", capture=False, check=True)
    if wait:
        states = wait_for_health()
        log("every service recovered: " + ", ".join(sorted(states)))
    return 0


def status() -> int:
    compose("ps", capture=False)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    subparsers = parser.add_subparsers(dest="command", required=True)

    up_parser = subparsers.add_parser("up", help="start the stack and wait for health")
    up_parser.add_argument("--build", action="store_true", help="rebuild the images first")
    up_parser.add_argument("--no-wait", action="store_true", help="do not wait for health")

    subparsers.add_parser("down", help="stop the stack, keeping the volumes")

    restart_parser = subparsers.add_parser("restart", help="restart the running services")
    restart_parser.add_argument("--no-wait", action="store_true")

    reset_parser = subparsers.add_parser("reset", help="stop the stack and DELETE every volume")
    reset_parser.add_argument("--yes", action="store_true",
                              help="required: this deletes the database and the object storage")

    subparsers.add_parser("status", help="show what is running")

    arguments = parser.parse_args()

    if arguments.command == "up":
        return up(build=arguments.build, wait=not arguments.no_wait)
    if arguments.command == "down":
        return down(remove_volumes=False)
    if arguments.command == "restart":
        return restart(wait=not arguments.no_wait)
    if arguments.command == "reset":
        if not arguments.yes:
            raise StackError(
                "reset deletes every volume, including the database and the object storage. "
                "Re-run with --yes if that is what you want.")
        return down(remove_volumes=True)
    if arguments.command == "status":
        return status()
    raise StackError(f"unknown command {arguments.command!r}")


if __name__ == "__main__":
    main_guard(main)


__all__ = ["HEALTHY_SERVICES", "build_identity", "down", "restart", "up"]
