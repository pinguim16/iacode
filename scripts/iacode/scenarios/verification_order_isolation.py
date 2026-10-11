#!/usr/bin/env python3
"""Prove the historical infra/smoke order on two independent clean runtime cycles.

This is a targeted regression, not a replacement for the complete verifier.  Each cycle starts
from no containers or volumes in the checkout-owned Compose project and executes the exact
contiguous live prefix that exposed G4-F-002: stack, integration, infra, smoke.  A second cycle is
attempted only after the first passed; a red result is never rerun to turn it green.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from compose import REPOSITORY_ROOT, StackError, log, main_guard
from verify import (
    build_stages,
    clean_verification_project,
    run,
    verification_environment,
)

ORDER = ("stack", "integration", "infra", "smoke")


def ordered_stages():
    by_name = {stage.name: stage for stage in build_stages(fast=True)}
    return [by_name[name] for name in ORDER]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cycles", type=int, default=2)
    parser.add_argument("--report", type=Path, required=True)
    arguments = parser.parse_args()
    if arguments.cycles != 2:
        raise StackError("the determinism probe requires exactly two predeclared clean cycles")

    environment = verification_environment()
    cycles: list[dict[str, object]] = []
    result = "PASS"
    started = time.monotonic()
    for number in range(1, arguments.cycles + 1):
        before = clean_verification_project(environment)
        if before.returncode != 0:
            raise StackError(f"cycle {number} pre-clean failed")
        stages = ordered_stages()
        for stage in stages:
            run(stage, quiet=True, environment=environment)
            if not stage.ok:
                result = "FAIL"
                break
        after = clean_verification_project(environment)
        cleanup = "PASS" if after.returncode == 0 else "FAIL"
        if cleanup == "FAIL":
            result = "FAIL"
        cycles.append({
            "cycle": number,
            "precondition": "no verification containers or volumes",
            "stages": [
                {
                    "name": stage.name,
                    "result": "PASS" if stage.ok else "FAIL",
                    "exitCode": stage.exit_code,
                    "durationSeconds": stage.duration_seconds,
                    **({"outputTail": stage.output_tail} if not stage.ok else {}),
                }
                for stage in stages
                if stage.exit_code is not None
            ],
            "cleanup": cleanup,
            "result": (
                "PASS"
                if cleanup == "PASS" and all(stage.ok for stage in stages)
                else "FAIL"
            ),
        })
        if result == "FAIL":
            break

    report = {
        "schemaVersion": "1.0.0",
        "artifact": "G4-F-002-ORDER-ISOLATION-PROBE",
        "composeProject": environment["COMPOSE_PROJECT_NAME"],
        "publishedPorts": "docker-allocated",
        "order": list(ORDER),
        "cycles": cycles,
        "durationSeconds": round(time.monotonic() - started, 1),
        "result": result,
    }
    target = arguments.report
    if not target.is_absolute():
        target = REPOSITORY_ROOT / target
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    log(
        f"ORDER_ISOLATION={result} "
        f"{sum(1 for item in cycles if item['result'] == 'PASS')}/{arguments.cycles} cycles"
    )
    return 0 if result == "PASS" and len(cycles) == arguments.cycles else 1


if __name__ == "__main__":
    main_guard(main)
