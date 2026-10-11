"""Run the canonical verifier once from a fresh transport clone of a published commit.

This evidence harness never retries a failed stage or a failed verifier.  It preserves the clone,
copies only the workstation's ignored provider configuration (without reading or reporting its
values), and brings the generated report back into this checkpoint.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


CHECKPOINT = Path(__file__).resolve().parent
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "development-ledger"))

from ledger_common import use_utf8_stdout  # noqa: E402


def command(arguments: list[str], *, cwd: Path, check: bool = True) -> str:
    completed = subprocess.run(
        arguments,
        cwd=cwd,
        check=check,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return completed.stdout.strip()


def write_json(path: Path, document: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(document, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def summarize_stages(verification: dict[str, Any]) -> tuple[int, int, int]:
    """Count the canonical verifier's ``result`` field, never an invented alias."""
    stages = verification.get("stages")
    if not isinstance(stages, list):
        raise RuntimeError("verification report has no stage list")
    if len(stages) != 42:
        raise RuntimeError(f"verification report has {len(stages)} stages, expected 42")
    invalid = [
        stage
        for stage in stages
        if not isinstance(stage, dict) or stage.get("result") not in {"PASS", "FAIL"}
    ]
    if invalid:
        raise RuntimeError("verification report contains a stage without PASS/FAIL result")
    passed = sum(1 for stage in stages if stage["result"] == "PASS")
    return len(stages), passed, len(stages) - passed


def require_expected_clone_state(status: str, *, summarize_existing: bool) -> None:
    entries = [line for line in status.splitlines() if line]
    expected_report = "?? docs/checkpoints/GATE-4-CP-0005/PUBLISHED-VERIFY.json"
    if not entries:
        return
    if summarize_existing and entries == [expected_report]:
        return
    raise RuntimeError(f"transport clone has unexpected Git state: {entries}")


def main() -> int:
    use_utf8_stdout()
    parser = argparse.ArgumentParser()
    parser.add_argument("--remote", required=True)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--target", type=Path, required=True)
    parser.add_argument(
        "--summarize-existing",
        action="store_true",
        help="reconcile publication metadata from an already completed preserved clone; never reruns",
    )
    parser.add_argument("--execution-command-id")
    arguments = parser.parse_args()

    target = arguments.target.resolve()
    if arguments.summarize_existing:
        if not target.is_dir():
            raise RuntimeError(f"preserved clean-clone target is unavailable: {target}")
        if not arguments.execution_command_id:
            raise RuntimeError("--execution-command-id is required with --summarize-existing")
    else:
        if target.exists():
            raise RuntimeError(f"clean-clone target already exists: {target}")
        target.parent.mkdir(parents=True, exist_ok=True)
        command(["git", "clone", "--no-local", arguments.remote, str(target)], cwd=target.parent)
    observed = command(["git", "rev-parse", "HEAD"], cwd=target)
    if observed != arguments.commit:
        raise RuntimeError(f"published clone resolved {observed}, expected {arguments.commit}")
    remote_main = command(["git", "rev-parse", "origin/main"], cwd=target)
    if remote_main != arguments.commit:
        raise RuntimeError(f"origin/main resolved {remote_main}, expected {arguments.commit}")
    if command(["git", "branch", "--show-current"], cwd=target) != "main":
        raise RuntimeError("transport clone is not attached to published main")
    require_expected_clone_state(
        command(["git", "status", "--porcelain", "--untracked-files=all"], cwd=target),
        summarize_existing=arguments.summarize_existing,
    )

    if not arguments.summarize_existing:
        local_environment = ROOT / "infra" / "compose" / ".env"
        if not local_environment.is_file():
            raise RuntimeError("workstation provider configuration is unavailable")
        clone_environment = target / "infra" / "compose" / ".env"
        shutil.copy2(local_environment, clone_environment)
        if command(["git", "status", "--porcelain"], cwd=target):
            raise RuntimeError("ignored workstation configuration changed the clone's Git state")

    clone_report = target / "docs" / "checkpoints" / "GATE-4-CP-0005" / "PUBLISHED-VERIFY.json"
    if arguments.summarize_existing:
        exit_code = 0
    else:
        invocation = [
            sys.executable,
            "scripts/iacode/verify.py",
            "--keep-going",
            "--report",
            clone_report.relative_to(target).as_posix(),
        ]
        process = subprocess.Popen(
            invocation,
            cwd=target,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
        )
        assert process.stdout is not None
        for line in process.stdout:
            print(line, end="", flush=True)
        exit_code = process.wait()

    if not clone_report.is_file():
        raise RuntimeError(f"verifier produced no report (exit={exit_code})")
    destination = CHECKPOINT / "VERIFY.json"
    shutil.copy2(clone_report, destination)
    verification = json.loads(destination.read_text(encoding="utf-8"))
    stage_count, passed, failed = summarize_stages(verification)
    verification_passed = verification.get("result") == "PASS"
    isolation = verification.get("isolation")
    cleanup_passed = (
        isinstance(isolation, dict)
        and isolation.get("preRunCleanup") == "PASS"
        and isolation.get("postRunCleanup") == "PASS"
    )
    publication_passed = exit_code == 0 and verification_passed and failed == 0 and cleanup_passed
    report = {
        "schemaVersion": "1.0.0",
        "artifact": "PUBLISHED-CLEAN-CLONE-VERIFICATION",
        "generatedAt": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "remote": arguments.remote,
        "publishedCommit": arguments.commit,
        "observedCommit": observed,
        "remoteMainEqualsCommit": True,
        "checkoutMode": "attached-main",
        "clonePath": str(target),
        "gitStateBeforeVerification": "CLEAN",
        "workstationConfiguration": {
            "source": "ignored infra/compose/.env",
            "valuesRecorded": False,
            "gitStateAfterInjection": "CLEAN",
        },
        "invocationCount": 1,
        "retryCount": 0,
        "stageDenominator": stage_count,
        "stagesPassed": passed,
        "stagesFailed": failed,
        "result": "PASS" if publication_passed else "FAIL",
        "exitCode": exit_code,
        "verificationReport": "VERIFY.json",
        "isolation": isolation,
        "clonePreserved": True,
    }
    if arguments.summarize_existing:
        report["publicationReconciliation"] = {
            "mode": "existing-verifier-report",
            "verificationExecutionCommand": arguments.execution_command_id,
            "verifierRerun": False,
            "preservedCloneState": "ONLY_GENERATED_VERIFICATION_REPORT",
            "reason": "publisher counted a non-existent status alias instead of the canonical result field",
        }
    write_json(CHECKPOINT / "PUBLISHED-CLEAN-CLONE-REPORT.json", report)
    print(
        f"PUBLISHED_FULL_VERIFICATION={report['result']} "
        f"stages={passed}/{stage_count} clone={target}",
        flush=True,
    )
    return 0 if publication_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
