#!/usr/bin/env python3
"""Execute one full internal verifier from an exact published subject in a fresh clone."""

from __future__ import annotations

import argparse
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
from datetime import UTC, datetime
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
REMOTE = "https://github.com/pinguim16/iacode.git"


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8", newline="\n")


def command(arguments: list[str], cwd: Path) -> str:
    result = subprocess.run(arguments, cwd=cwd, capture_output=True, text=True,
                            encoding="utf-8", errors="replace", check=False)
    if result.returncode:
        raise RuntimeError(f"verification setup failed: {arguments[0]} exit={result.returncode}")
    return result.stdout.strip()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--tag", required=True)
    args = parser.parse_args()
    destination = CHECKPOINT / "VERIFY.json"
    if destination.exists():
        raise RuntimeError("preserve the previous complete verification before another attempt")
    source = ROOT / "docs/checkpoints/GATE-4-CP-0006/RUN-INDEPENDENT-FULL-VERIFICATION.py"
    spec = importlib.util.spec_from_file_location("cp0010_isolation", source)
    if spec is None or spec.loader is None:
        raise RuntimeError("the canonical isolation probe cannot be loaded")
    probe = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(probe)
    before = probe.snapshot_project("iacode")
    progress: list[str] = []
    with tempfile.TemporaryDirectory(prefix="iacode-cp0010-full-verification-") as directory:
        clone = Path(directory) / "repository"
        command(["git", "clone", "--no-local", REMOTE, str(clone)], Path(directory))
        command(["git", "checkout", "--detach", args.tag], clone)
        observed = command(["git", "rev-parse", "HEAD"], clone)
        if observed != args.commit or command(["git", "rev-parse", "origin/main"], clone) != args.commit:
            raise RuntimeError("the published subject is not the requested remote main/tag commit")
        if command(["git", "status", "--porcelain"], clone):
            raise RuntimeError("the fresh transported subject is not clean")
        shutil.copy2(ROOT / "infra/compose/.env", clone / "infra/compose/.env")
        if command(["git", "status", "--porcelain"], clone):
            raise RuntimeError("ignored workstation configuration changed the transported tree")
        report_path = clone / "artifacts/review/INTERNAL-FULL-VERIFY.json"
        process = subprocess.Popen(
            [sys.executable, "scripts/iacode/verify.py", "--keep-going", "--quiet",
             "--report", report_path.relative_to(clone).as_posix()],
            cwd=clone, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, encoding="utf-8", errors="replace", bufsize=1,
        )
        assert process.stdout is not None
        for line in process.stdout:
            print(line, end="", flush=True)
            if line.startswith("[iacode] ---"):
                progress.append(line.strip())
                write_json(CHECKPOINT / "FULL-VERIFY-PROGRESS.json", {
                    "subjectCommit": observed, "clone": str(clone), "transitions": progress,
                    "updatedAt": datetime.now(UTC).isoformat(),
                })
        exit_code = process.wait()
        if not report_path.is_file():
            raise RuntimeError(f"the complete verifier produced no report (exit={exit_code})")
        verification = json.loads(report_path.read_text(encoding="utf-8"))
        write_json(destination, verification)
        stage_count, passed, failed = probe.summarize_stages(verification)
        scenarios = {}
        for path in sorted((clone / "var").glob("*.json")):
            if path.name.startswith("quality-") or path.name == "sandbox-tool-result-origin.json":
                document = json.loads(path.read_text(encoding="utf-8"))
                scenarios[path.name] = document
                write_json(ROOT / "var" / path.name, document)
        write_json(CHECKPOINT / "FUNCTIONAL-SCENARIOS.json", {
            "subjectCommit": observed, "source": "single full verifier invocation",
            "scenarios": scenarios,
        })
        isolation = verification.get("isolation") or {}
        after = probe.snapshot_project("iacode")
        project = isolation.get("composeProject")
        owned = probe.snapshot_project(str(project)) if project else None
        removed = bool(owned and not any(owned[kind] for kind in ("containers", "volumes", "networks")))
        clean = not command(["git", "status", "--porcelain"], clone)
        write_json(CHECKPOINT / "COMPOSE-ISOLATION-AUDIT.json", {
            "sharedBefore": before, "sharedAfter": after, "sharedUnchanged": before == after,
            "ownedAfter": owned, "ownedRemoved": removed,
            "result": "PASS" if before == after and removed else "FAIL",
        })
        report = {
            "schemaVersion": "1.0.0", "reviewKind": "SAME_SESSION_INTERNAL_REVIEW",
            "publishedCommit": observed, "subjectTag": args.tag,
            "remoteMainEqualsCommit": True, "checkoutMode": "detached-subject-tag",
            "configuration": "ignored workstation environment copied without recording values",
            "invocationCount": 1, "retryCount": 0, "verifierRerun": False,
            "stageDenominator": stage_count, "stagesPassed": passed, "stagesFailed": failed,
            "exitCode": exit_code, "sharedProjectUnchanged": before == after,
            "ownedComposeProjectRemoved": removed, "gitStateAfterVerificationClean": clean,
            "result": "PASS" if (
                exit_code == 0 and verification.get("result") == "PASS" and not failed
                and isolation.get("postRunCleanup") == "PASS" and before == after and removed and clean
            ) else "FAIL",
        }
    report["temporaryCloneRemoved"] = not Path(directory).exists()
    if not report["temporaryCloneRemoved"]:
        report["result"] = "FAIL"
    write_json(CHECKPOINT / "PUBLISHED-CLEAN-CLONE-REPORT.json", report)
    print(f"INTERNAL_PUBLISHED_FULL_VERIFICATION={report['result']} stages={passed}/{stage_count}")
    return 0 if report["result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
