#!/usr/bin/env python3
"""Execute one full internal verifier from an exact published subject in a fresh clone."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import uuid
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
REMOTE = "https://github.com/pinguim16/iacode.git"
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))
sys.path.insert(0, str(ROOT / "scripts/iacode"))
from ledger_common import find_secrets
from verify import build_stages


@contextmanager
def verification_directory():
    # Git pack files can be read-only on Windows. TemporaryDirectory's standard cleanup
    # handles that attribute; native profile sharing-lock retries are a different boundary.
    facts = {"path": None, "removed": False, "cleanupRetries": None}
    directory = None
    try:
        with tempfile.TemporaryDirectory(prefix="iacode-gate6-full-verification-") as raw:
            directory = Path(raw)
            if (directory.resolve().parent != Path(tempfile.gettempdir()).resolve()
                    or not directory.name.startswith("iacode-gate6-full-verification-")
                    or directory.is_symlink() or directory.is_junction()):
                raise ValueError("unexpected freshly created Git clone directory")
            facts["path"] = directory
            yield facts
    finally:
        if directory is not None:
            facts["removed"] = not directory.exists()


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8", newline="\n")


def summarize_stages(verification: dict) -> tuple[int, int, int]:
    """Consume the current producer vocabulary and result field, never a sealed denominator."""
    expected = [stage.name for stage in build_stages(False)]
    stages = verification.get("stages", [])
    if [row.get("name") for row in stages] != expected:
        raise RuntimeError("verification stage vocabulary is incomplete, duplicated or out of order")
    if any(row.get("result") not in {"PASS", "FAIL"} for row in stages):
        raise RuntimeError("verification stage result is missing or unknown")
    passed = sum(row["result"] == "PASS" for row in stages)
    failed = len(stages) - passed
    if verification.get("result") not in {"PASS", "FAIL"} or (
            verification["result"] == "PASS" and failed):
        raise RuntimeError("verification top-level result contradicts its stage results")
    return len(expected), passed, failed


def capture_producer_reports(
    clone: Path, verifier_report: Path, archive: Path, subject: str,
) -> Path:
    """Retain safe original bytes before fallible interpretation and temporary-owner cleanup."""
    archive.mkdir(parents=True, exist_ok=True)
    if archive.is_symlink() or archive.is_junction():
        raise RuntimeError("refusing redirected producer archive")
    prefix = "FULL-PRODUCER-" + uuid.uuid4().hex[:12]
    candidates = [verifier_report] + [
        path for path in sorted((clone / "var").glob("*.json"))
        if path.name.startswith("quality-") or path.name in {
            "sandbox-tool-result-origin.json", "desktop-e2e.json", "native-editor-package.json",
            "experience-store-e2e.json"}
    ]
    reports, refused = [], []
    for path in candidates:
        if not path.is_file():
            continue
        if path.is_symlink() or not path.resolve().is_relative_to(clone.resolve()):
            raise RuntimeError("refusing redirected producer report")
        content = path.read_bytes()
        identity = {"producerName": path.name, "bytes": len(content),
                    "sha256": hashlib.sha256(content).hexdigest()}
        try:
            unsafe = bool(find_secrets(content.decode("utf-8")))
        except (UnicodeError, ValueError):
            refused.append({**identity, "reason": "UNSCANNABLE"})
            continue
        if unsafe:
            refused.append({**identity, "reason": "SECRET_MATERIAL"})
            continue
        destination = archive / (prefix + "-" + path.name)
        with destination.open("xb") as output:
            output.write(content)
        if destination.read_bytes() != content:
            raise RuntimeError("producer archive byte equality failed")
        reports.append({**identity, "archive": destination.name})
    manifest = archive / (prefix + "-MANIFEST.json")
    write_json(manifest, {
        "kind": "RAW_PRODUCER_CAPTURE_NOT_ACCEPTANCE", "subjectCommit": subject,
        "gateVerdictIssued": False, "reports": reports, "refusedReports": refused,
    })
    if refused:
        raise RuntimeError("producer capture refused unsafe artifact(s); neutral inventory retained")
    return manifest


def command(arguments: list[str], cwd: Path) -> str:
    result = subprocess.run(arguments, cwd=cwd, capture_output=True, text=True,
                            encoding="utf-8", errors="replace", check=False)
    if result.returncode:
        raise RuntimeError(f"verification setup failed: {arguments[0]} exit={result.returncode}")
    return result.stdout.strip()


def collect_producer_observations(
    clone: Path, verifier_report: Path, archive: Path, subject: str,
) -> tuple[dict, tuple[int, int, int], Path]:
    """The actual publisher boundary preserves originals before any interpretation can fail."""
    manifest = capture_producer_reports(clone, verifier_report, archive, subject)
    if not verifier_report.is_file():
        raise RuntimeError("the complete verifier produced no report; available originals retained")
    verification = json.loads(verifier_report.read_text(encoding="utf-8"))
    summary = summarize_stages(verification)
    return verification, summary, manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--tag", required=True)
    parser.add_argument("--node", type=Path, required=True)
    args = parser.parse_args()
    if not args.node.is_file():
        raise RuntimeError("explicit supported Node executable required")
    destination = CHECKPOINT / "VERIFY.json"
    if destination.exists():
        raise RuntimeError("preserve the previous complete verification before another attempt")
    source = ROOT / "docs/checkpoints/GATE-4-CP-0006/RUN-INDEPENDENT-FULL-VERIFICATION.py"
    spec = importlib.util.spec_from_file_location("gate6_isolation", source)
    if spec is None or spec.loader is None:
        raise RuntimeError("the canonical isolation probe cannot be loaded")
    probe = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(probe)
    before = probe.snapshot_project("iacode")
    progress: list[str] = []
    with verification_directory() as owner:
        directory = owner["path"]
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
             "--node", str(args.node.resolve()),
             "--report", report_path.relative_to(clone).as_posix()],
            cwd=clone, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, encoding="utf-8", errors="replace", bufsize=1,
        )
        try:
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
        finally:
            verification, summary, manifest = collect_producer_observations(
                clone, report_path, CHECKPOINT / "attempts", observed)
            write_json(CHECKPOINT / "PRODUCER-REPORTS.json", {
                "subjectCommit": observed, "manifest": manifest.relative_to(CHECKPOINT).as_posix(),
                "gateVerdictIssued": False,
            })
        write_json(destination, verification)
        scenarios = {}
        for path in sorted((clone / "var").glob("*.json")):
            if (path.name.startswith("quality-") or path.name in {
                    "sandbox-tool-result-origin.json", "desktop-e2e.json", "native-editor-package.json",
            "experience-store-e2e.json"}):
                document = json.loads(path.read_text(encoding="utf-8"))
                scenarios[path.name] = document
                write_json(ROOT / "var" / path.name, document)
        write_json(CHECKPOINT / "FUNCTIONAL-SCENARIOS.json", {
            "subjectCommit": observed, "source": "single full verifier invocation",
            "scenarios": scenarios,
        })
        stage_count, passed, failed = summary
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
    report["temporaryCloneRemoved"] = owner["removed"]
    report["directoryCleanupRetries"] = owner["cleanupRetries"]
    if not report["temporaryCloneRemoved"]:
        report["result"] = "FAIL"
    write_json(CHECKPOINT / "PUBLISHED-CLEAN-CLONE-REPORT.json", report)
    print(f"INTERNAL_PUBLISHED_FULL_VERIFICATION={report['result']} stages={passed}/{stage_count}")
    return 0 if report["result"] == "PASS" else 1


if __name__ == "__main__":
    sys.path.insert(0, str(ROOT / "scripts/development-ledger"))
    sys.path.insert(0, str(ROOT / "scripts/iacode"))
    from ledger_common import use_utf8_stdout

    use_utf8_stdout()
    raise SystemExit(main())
