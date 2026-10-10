#!/usr/bin/env python3
"""Validate and fully verify the immutable Gate 4 subject from a transport clone."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
REMOTE = "https://github.com/pinguim16/iacode.git"
SUBJECT = "GATE-4-CP-0001"
TAG = f"iacode-checkpoints/{SUBJECT}"
COMMIT = "70a22e824705f414e0c295bbdf89187db9b391f7"
sys.path.insert(0, str(ROOT / "scripts" / "development-ledger"))

from ledger_common import utc_now  # noqa: E402


def run(argv: list[str], cwd: Path, timeout: float) -> tuple[int, str, float]:
    started = time.monotonic()
    try:
        completed = subprocess.run(
            argv,
            cwd=cwd,
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
            timeout=timeout,
        )
        return completed.returncode, completed.stdout, round(time.monotonic() - started, 1)
    except subprocess.TimeoutExpired as error:
        output = error.stdout or ""
        if isinstance(output, bytes):
            output = output.decode("utf-8", errors="replace")
        return 124, output + "\nTIMEOUT", round(time.monotonic() - started, 1)


def record(steps: list[dict[str, object]], title: str, argv: list[str], cwd: Path,
           timeout: float) -> tuple[int, str]:
    code, output, seconds = run(argv, cwd, timeout)
    steps.append({
        "step": title,
        "command": argv,
        "exitCode": code,
        "durationSeconds": seconds,
        "tail": output.strip()[-1200:],
    })
    print(f"[{'PASS' if code == 0 else 'FAIL'}] {title} ({seconds}s)", flush=True)
    if output.strip():
        print(output.strip()[-500:], flush=True)
    return code, output


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--verification-report", type=Path, required=True)
    parser.add_argument("--skip-full-verification", action="store_true")
    arguments = parser.parse_args()
    report_path = arguments.report.resolve()
    verification_path = arguments.verification_report.resolve()
    steps: list[dict[str, object]] = []
    scratch = Path(tempfile.mkdtemp(prefix="iacode-g4-audit-clone-"))
    clone = scratch / "iacode"
    observed_head = None
    observed_tree = None
    verification: dict[str, object] = {}
    local_configuration = "not copied"
    try:
        code, _ = record(
            steps,
            "clone authorised remote over transport",
            ["git", "clone", "--quiet", REMOTE, str(clone)],
            scratch,
            900,
        )
        if code != 0:
            raise RuntimeError("authorised remote clone failed")
        code, _ = record(
            steps,
            "checkout immutable subject tag detached",
            ["git", "checkout", "--detach", "--quiet", TAG],
            clone,
            300,
        )
        if code != 0:
            raise RuntimeError("subject tag checkout failed")
        observed_head = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=clone, text=True, encoding="utf-8",
            capture_output=True, check=False,
        ).stdout.strip()
        observed_tree = subprocess.run(
            ["git", "rev-parse", "HEAD^{tree}"], cwd=clone, text=True, encoding="utf-8",
            capture_output=True, check=False,
        ).stdout.strip()
        identity_ok = observed_head == COMMIT
        steps.append({
            "step": "subject identity",
            "exitCode": 0 if identity_ok else 1,
            "expectedCommit": COMMIT,
            "observedCommit": observed_head,
            "observedTree": observed_tree,
        })
        print(f"[{'PASS' if identity_ok else 'FAIL'}] subject identity {observed_head}", flush=True)

        commands = (
            (
                "validate sealed subject detached",
                [sys.executable, "scripts/development-ledger/validate_checkpoint.py"],
                1200,
            ),
            (
                "verify checkpoint integrity chain",
                [sys.executable, "scripts/development-ledger/verify_integrity.py"],
                1200,
            ),
            (
                "validate engineering memory",
                [sys.executable, "scripts/development-ledger/validate_lessons.py"],
                1200,
            ),
            (
                "confirm subject tag and branch are published",
                [sys.executable, "scripts/development-ledger/remote_sync.py", "--tag", TAG],
                1200,
            ),
        )
        for title, argv, timeout in commands:
            record(steps, title, argv, clone, timeout)

        if not arguments.skip_full_verification:
            source_env = ROOT / "infra" / "compose" / ".env"
            target_env = clone / "infra" / "compose" / ".env"
            if source_env.is_file():
                shutil.copyfile(source_env, target_env)
                local_configuration = (
                    "ignored infra/compose/.env copied as machine configuration only; "
                    "all versioned content came from the remote subject tag"
                )
            clone_report = clone / "var" / "gate4-audit-verification.json"
            code, output = record(
                steps,
                "complete non-fast 42-stage verification",
                [
                    sys.executable,
                    "scripts/iacode/verify.py",
                    "--keep-going",
                    "--report",
                    str(clone_report),
                ],
                clone,
                10800,
            )
            if clone_report.is_file():
                verification = json.loads(clone_report.read_text(encoding="utf-8"))
                verification_path.parent.mkdir(parents=True, exist_ok=True)
                verification_path.write_text(
                    json.dumps(verification, indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8",
                    newline="\n",
                )
            else:
                verification = {
                    "result": "FAIL",
                    "reason": "verification report was not produced",
                    "commandExitCode": code,
                    "commandTail": output.strip()[-1200:],
                }
        clean = subprocess.run(
            ["git", "status", "--porcelain"], cwd=clone, text=True, encoding="utf-8",
            capture_output=True, check=False,
        ).stdout.strip()
        allowed_dirty = {"?? var/"}
        dirty_lines = {line for line in clean.splitlines() if line}
        steps.append({
            "step": "published checkout has no unexpected repository mutation",
            "exitCode": 0 if dirty_lines.issubset(allowed_dirty) else 1,
            "observed": sorted(dirty_lines),
            "allowed": sorted(allowed_dirty),
        })
    except Exception as error:  # the report must survive a failed audit operation
        steps.append({"step": "harness", "exitCode": 1, "error": str(error)})
    finally:
        env_copy = clone / "infra" / "compose" / ".env"
        if env_copy.is_file():
            env_copy.unlink()
        shutil.rmtree(scratch, ignore_errors=True)

    failed = [item for item in steps if item.get("exitCode") != 0]
    document = {
        "schemaVersion": "1.0.0",
        "artifact": "GATE-4-CLEAN-CLONE-AUDIT",
        "checkpoint": CHECKPOINT.name,
        "subjectCheckpoint": SUBJECT,
        "subjectTag": f"refs/tags/{TAG}",
        "expectedCommit": COMMIT,
        "observedCommit": observed_head,
        "observedTree": observed_tree,
        "remote": REMOTE,
        "generatedAt": utc_now(),
        "localConfiguration": local_configuration,
        "verificationResult": verification.get("result"),
        "verificationStages": len(verification.get("stages") or []),
        "steps": steps,
        "result": "PASS" if not failed else "FAIL",
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        json.dumps(document, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(
        f"CLEAN_CLONE_AUDIT={document['result']} steps={len(steps) - len(failed)}/{len(steps)} "
        f"verification={document['verificationResult']} stages={document['verificationStages']}"
    )
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
