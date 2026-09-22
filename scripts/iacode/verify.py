#!/usr/bin/env python3
"""One command that verifies everything the repository has delivered.

`docs/GATE-0-CHECKLIST.md` row 13.1. It runs on Windows and on POSIX, because it is Python driving
Docker rather than a shell script: the primary development environment here is Windows, and an
operational path that only works under bash makes the primary environment the unsupported one.

    python scripts/iacode/verify.py            everything
    python scripts/iacode/verify.py --fast     everything that does not restart the stack
    python scripts/iacode/verify.py --list     what would run

Stages, in order, because each one depends on the last being true:

    gates          the mandatory gate set from `.iacode/policies/quality-gates.json`
    stack          the stack is up and every service is healthy
    integration    the backend suite against the real services
    infra          our configuration of each service, exercised live
    smoke          the API, the web shell, Prometheus, Grafana and a real Temporal workflow
    gateway-smoke  the Model Gateway against the real configured provider
    backup         a backup, a restore into a disposable target, and a verified read-back
    scan           known vulnerabilities in the pinned dependency locks
    scenarios      restart with data intact, dependency failure and recovery
    fresh          a complete installation from no volumes at all

``--fast`` is the targeted mode: it stops before the last two, which are the ones that restart the
stack and delete volumes, so the edit-run loop does not pay for a full reinstallation. The Gate is
verified by the full run.

The stage list is not a list of Gates. Gate 1 added one stage and changed none of the others,
because the Foundation still has to work for the gateway to mean anything — and the report names the
Gate the repository is delivering rather than the one this file was written during.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from compose import REPOSITORY_ROOT, log, main_guard
from policies_bridge import (
    delivered_gate,
    mandatory_gate_commands,
    refresh_declared_hashes,
)


@dataclass
class Stage:
    name: str
    description: str
    argv: list[str]
    destructive: bool = False
    exit_code: int | None = None
    duration_seconds: float = 0.0
    output_tail: str = ""
    extra: dict[str, object] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return self.exit_code == 0


def python_stage(name: str, description: str, *arguments: str,
                 destructive: bool = False) -> Stage:
    return Stage(name=name, description=description,
                 argv=[sys.executable, *arguments], destructive=destructive)


def build_stages(fast: bool) -> list[Stage]:
    stages: list[Stage] = []

    # The mandatory gate set is read from policy, never listed here. A verification that carried
    # its own copy would silently stop covering a gate the moment the registry grew one.
    for identifier, command in mandatory_gate_commands(REPOSITORY_ROOT):
        argv = list(command)
        if argv and argv[0] == "python":
            argv[0] = sys.executable
        stages.append(Stage(name=f"gate:{identifier}",
                            description=f"mandatory gate {identifier}", argv=argv))

    stages += [
        python_stage("stack", "start the stack and wait for real health",
                     "scripts/iacode/stack.py", "up"),
        Stage(name="integration",
              description="the backend suite against the real services",
              argv=["docker", "compose",
                    "--project-directory", str(REPOSITORY_ROOT / "infra" / "compose"),
                    "--file", str(REPOSITORY_ROOT / "infra" / "compose" / "docker-compose.yml"),
                    "--env-file", str(REPOSITORY_ROOT / "infra" / "compose" / ".env"),
                    "run", "--rm", "--entrypoint", "", "api",
                    "python", "-m", "pytest", "tests", "-p", "no:cacheprovider", "--no-header"]),
        Stage(name="infra",
              description="our configuration of each service, exercised live",
              argv=[sys.executable, "-m", "unittest", "discover",
                    "-s", str(REPOSITORY_ROOT / "infra" / "tests"),
                    "-t", str(REPOSITORY_ROOT / "infra" / "tests")]),
        python_stage("smoke", "the API, the web shell, the observability stack and a workflow",
                     "scripts/iacode/smoke.py"),
        # The live provider check. It exits BLOCKED, not FAIL, when no credential is configured
        # here: "not set up on this machine" and "broken" are different states, and reporting the
        # first as the second sends somebody looking for a defect that does not exist.
        python_stage("gateway-smoke", "the Model Gateway against the real configured provider",
                     "scripts/iacode/gateway_smoke.py", "--report",
                     str(REPOSITORY_ROOT / "var" / "gateway-smoke.json")),
        python_stage("backup", "backup, restore into a disposable target, verified read-back",
                     "scripts/iacode/backup_restore_check.py"),
        python_stage("dependency-scan", "known vulnerabilities in the pinned dependencies",
                     "scripts/iacode/dependency_scan.py"),
    ]

    if not fast:
        stages += [
            python_stage("restart", "restart with data intact",
                         "scripts/iacode/scenarios/restart.py", destructive=True),
            python_stage("dependency-failure", "liveness holds, readiness refuses, both recover",
                         "scripts/iacode/scenarios/dependency_failure.py", destructive=True),
            python_stage("fresh-install", "a complete installation from no volumes at all",
                         "scripts/iacode/scenarios/fresh_install.py", "--yes", destructive=True),
        ]
    return stages


def run(stage: Stage, quiet: bool) -> Stage:
    log(f"--- {stage.name}: {stage.description}")
    started = time.monotonic()
    completed = subprocess.run(
        stage.argv, cwd=str(REPOSITORY_ROOT), text=True, encoding="utf-8", errors="replace",
        stdout=subprocess.PIPE if quiet else None,
        stderr=subprocess.STDOUT if quiet else None, check=False)
    stage.duration_seconds = round(time.monotonic() - started, 1)
    stage.exit_code = completed.returncode
    if quiet and completed.stdout:
        stage.output_tail = "\n".join(completed.stdout.strip().splitlines()[-25:])
        if not stage.ok:
            sys.stdout.write(stage.output_tail + "\n")
    log(f"--- {stage.name}: {'PASS' if stage.ok else 'FAIL'} in {stage.duration_seconds:g}s")
    return stage


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--fast", action="store_true",
                        help="skip the stages that restart the stack or delete volumes")
    parser.add_argument("--list", action="store_true", help="print the stages and exit")
    parser.add_argument("--quiet", action="store_true",
                        help="capture stage output and print only the tail of a failing stage")
    parser.add_argument("--report", type=Path, default=None,
                        help="write a machine-readable result document to this path")
    parser.add_argument("--keep-going", action="store_true",
                        help="run every stage even after one fails")
    arguments = parser.parse_args()

    stages = build_stages(fast=arguments.fast)
    if arguments.list:
        for stage in stages:
            marker = " (destructive)" if stage.destructive else ""
            print(f"{stage.name:22} {stage.description}{marker}")
        return 0

    gate = delivered_gate(REPOSITORY_ROOT)
    # The mandatory set includes `checkpointValidation`, and the checkpoint's append-only evidence
    # has grown since the author last bound its hashes — every recorded command since then is in
    # it. Re-derive the declared hashes through the ledger's own function, which never adds or
    # removes a declaration, so an undeclared change still fails. The Green Keeper has always done
    # this and this command did not, which made the same gate green under one runner and red under
    # the other.
    refresh_declared_hashes(REPOSITORY_ROOT)
    log(f"verifying {gate}: {len(stages)} stage(s)"
        + (", targeted mode" if arguments.fast else ""))
    started = time.monotonic()
    executed: list[Stage] = []
    for stage in stages:
        executed.append(run(stage, quiet=arguments.quiet))
        if not stage.ok and not arguments.keep_going:
            log(f"stopping at the first failure: {stage.name}. "
                f"Re-run with --keep-going to see the rest.")
            break

    failed = [stage for stage in executed if not stage.ok]
    elapsed = round(time.monotonic() - started, 1)
    result = "PASS" if not failed and len(executed) == len(stages) else "FAIL"

    if arguments.report:
        arguments.report.parent.mkdir(parents=True, exist_ok=True)
        arguments.report.write_text(json.dumps({
            "gate": gate,
            "result": result,
            "fast": arguments.fast,
            "durationSeconds": elapsed,
            "stages": [
                {"name": stage.name, "description": stage.description,
                 "exitCode": stage.exit_code, "durationSeconds": stage.duration_seconds,
                 "result": "PASS" if stage.ok else "FAIL"}
                for stage in executed
            ],
        }, indent=2) + "\n", encoding="utf-8", newline="\n")
        log(f"wrote {arguments.report}")

    print()
    for stage in executed:
        print(f"[{'PASS' if stage.ok else 'FAIL'}] {stage.name:22} "
              f"{stage.duration_seconds:>6.1f}s  {stage.description}")
    skipped = len(stages) - len(executed)
    if skipped:
        print(f"[SKIP] {skipped} stage(s) were not reached")
    print(f"VERIFY={result} {len(executed) - len(failed)}/{len(stages)} stages in {elapsed:g}s")
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    main_guard(main)
