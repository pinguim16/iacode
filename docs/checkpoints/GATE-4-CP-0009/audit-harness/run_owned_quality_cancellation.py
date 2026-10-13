#!/usr/bin/env python3
"""Run the cancellation scenario in one disposable checkout-owned Compose project."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "iacode"))

from verify import clean_verification_project, verification_environment  # noqa: E402


def load_isolation_probe() -> Any:
    source = (
        ROOT
        / "docs"
        / "checkpoints"
        / "GATE-4-CP-0006"
        / "RUN-INDEPENDENT-FULL-VERIFICATION.py"
    )
    specification = importlib.util.spec_from_file_location("cp0009_isolation_probe", source)
    if specification is None or specification.loader is None:
        raise RuntimeError("the established Compose isolation probe could not be loaded")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


def run(arguments: list[str], environment: dict[str, str]) -> int:
    return subprocess.run(
        arguments,
        cwd=ROOT,
        env=environment,
        check=False,
    ).returncode


def write_json(path: Path, document: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(document, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def main() -> int:
    probe = load_isolation_probe()
    environment = verification_environment(ROOT)
    project = environment["COMPOSE_PROJECT_NAME"]
    report_path = CHECKPOINT / "QUALITY-CANCELLATION-GUARDRAIL.json"
    audit_path = CHECKPOINT / "QUALITY-CANCELLATION-ISOLATION.json"
    if report_path.exists():
        report_path.unlink()

    shared_before = probe.snapshot_project("iacode")
    pre_cleanup = clean_verification_project(environment)
    stack_exit: int | None = None
    scenario_exit: int | None = None
    post_cleanup: subprocess.CompletedProcess[str] | None = None
    try:
        if pre_cleanup.returncode == 0:
            stack_exit = run(
                [sys.executable, "scripts/iacode/stack.py", "up", "--build"], environment
            )
        if stack_exit == 0:
            scenario_exit = run(
                [
                    sys.executable,
                    "scripts/iacode/scenarios/quality_engine_e2e.py",
                    "--scenario",
                    "cancel",
                    "--skip-build",
                    "--report",
                    str(report_path),
                ],
                environment,
            )
    finally:
        post_cleanup = clean_verification_project(environment)

    shared_after = probe.snapshot_project("iacode")
    owned_after = probe.snapshot_project(project)
    shared_unchanged = shared_before == shared_after
    owned_removed = not any(
        owned_after[kind] for kind in ("containers", "volumes", "networks")
    )
    scenario_result = None
    if report_path.is_file():
        scenario_result = json.loads(report_path.read_text(encoding="utf-8")).get("result")
    passed = bool(
        pre_cleanup.returncode == 0
        and stack_exit == 0
        and scenario_exit == 0
        and scenario_result == "PASS"
        and post_cleanup is not None
        and post_cleanup.returncode == 0
        and shared_unchanged
        and owned_removed
    )
    write_json(
        audit_path,
        {
            "schemaVersion": "1.0.0",
            "generatedAt": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            "composeProject": project,
            "preRunCleanup": "PASS" if pre_cleanup.returncode == 0 else "FAIL",
            "stackExitCode": stack_exit,
            "scenarioExitCode": scenario_exit,
            "scenarioResult": scenario_result,
            "postRunCleanup": (
                "PASS" if post_cleanup is not None and post_cleanup.returncode == 0 else "FAIL"
            ),
            "sharedProjectUnchanged": shared_unchanged,
            "ownedProjectRemoved": owned_removed,
            "result": "PASS" if passed else "FAIL",
        },
    )
    print(
        f"QUALITY_CANCELLATION_GUARDRAIL={'PASS' if passed else 'FAIL'} "
        f"project={project} shared_unchanged={shared_unchanged} owned_removed={owned_removed}"
    )
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
