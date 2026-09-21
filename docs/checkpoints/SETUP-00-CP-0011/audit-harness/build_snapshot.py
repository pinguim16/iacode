#!/usr/bin/env python3
"""Build the sealed snapshot the adversarial battery attacks.

The battery must attack a repository in which this audit checkpoint is sealed, because that is the
state whose defences matter. The snapshot is produced by the same tooling the real seal uses: the
working tree is copied into a fresh clone, committed, and sealed with seal_checkpoint.py. Nothing
here touches the real repository.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]


def run(argv: list[str], cwd: Path) -> tuple[int, str]:
    completed = subprocess.run(argv, cwd=cwd, capture_output=True, text=True, check=False)
    return completed.returncode, (completed.stdout + completed.stderr).strip()


def model_internal_assurance(destination: Path) -> None:
    """Give the snapshot the internal assurance artifacts a sealed checkpoint carries.

    The battery runs before the report it produces exists, so the snapshot models the shape a
    sealed, approved checkpoint has. This is the same technique the product battery uses for its own
    first run. The models always overwrite whatever the working tree holds, because the defences
    around a claimed milestone verdict can only be attacked in a repository that claims one, and
    they never leave the disposable copy: the real checkpoint keeps whatever its own controls
    produced.
    """
    import json
    import sys as _sys
    from datetime import datetime, timezone

    _sys.path.insert(0, str(destination / "scripts" / "development-ledger"))
    from ledger_common import scope_fingerprint

    checkpoint = destination / "docs" / "checkpoints" / "SETUP-00-CP-0011"
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    fingerprint = scope_fingerprint(destination)

    red_team = checkpoint / "M0-INTERNAL-RED-TEAM.json"
    red_team.write_text(json.dumps({
        "schemaVersion": "1.1.0",
        "checkpoint": "SETUP-00-CP-0011",
        "generatedAt": stamp,
        "targetFingerprint": fingerprint,
        "source": "modelled by the audit snapshot before the battery has produced its results",
        "baselineControl": {
            "result": "VALID",
            "detail": "modelled for the snapshot; the real control is executed by the battery "
                      "this snapshot exists to run",
        },
        "attacks": [{
            "attackId": "SNAPSHOT",
            "description": "placeholder shape for the snapshot under attack",
            "target": "snapshot",
            "mutation": "none",
            "expectedDefense": "reject",
            "observed": "modelled by the audit snapshot",
            "result": "DEFENDED",
            "evidence": ["attack:SNAPSHOT"],
            "mandatory": True,
        }],
        "total": 1, "defended": 1, "escaped": 0,
        "mandatoryTotal": 1, "mandatoryDefended": 1,
        "result": "RED_TEAM_PASS",
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")

    mirror = checkpoint / "M0-INTERNAL-MIRROR.json"
    mirror.write_text(json.dumps({
        "schemaVersion": "1.0.0",
        "checkpoint": "SETUP-00-CP-0011",
        "milestone": "M0",
        "generatedAt": stamp,
        "targetFingerprint": fingerprint,
        "auditorRole": "M0 Closure Auditor",
        "independence": "Internal quality assurance, not independent validation.",
        "checks": [{
            "id": "MIR-001",
            "dimension": "snapshot",
            "expectation": "placeholder shape for the snapshot under attack",
            "observed": "modelled by the audit snapshot",
            "result": "PASS",
            "evidence": ["checkpoint:REQUIREMENTS-MATRIX.json"],
        }],
        "total": 1, "passed": 1, "failed": 0,
        "result": "PASS",
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--destination", type=Path, required=True)
    args = parser.parse_args()
    destination = args.destination.resolve()
    if destination.exists():
        shutil.rmtree(destination, ignore_errors=True)

    code, output = run(["git", "clone", "--no-local", "--quiet", str(ROOT), str(destination)], ROOT)
    if code != 0:
        print(f"SNAPSHOT_FAILED clone: {output}")
        return 2

    # Only the paths the working tree actually changed are copied. Copying every tracked file would
    # rewrite identical content through a different end-of-line normalization and make the clone
    # report modifications that do not exist.
    status = subprocess.run(
        ["git", "status", "--porcelain=v1", "--untracked-files=all"],
        cwd=ROOT, capture_output=True, text=True, check=True).stdout
    for line in status.splitlines():
        if not line.strip():
            continue
        code, relative = line[:2], line[3:].strip().replace("\\", "/")
        source = ROOT / relative
        target = destination / relative
        if "D" in code and not source.exists():
            if target.is_file():
                target.unlink()
            continue
        if source.is_dir():
            for item in sorted(source.rglob("*")):
                if item.is_file() and "__pycache__" not in item.parts:
                    inner = destination / item.relative_to(ROOT)
                    inner.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(item, inner)
            continue
        if source.is_file():
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)

    model_internal_assurance(destination)

    for argv in (
        ["git", "config", "user.name", "IACode Audit Snapshot"],
        ["git", "config", "user.email", "iacode-audit@example.invalid"],
        [sys.executable, "scripts/development-ledger/derive_counts.py", "--write",
         "--checkpoint", "docs/checkpoints/SETUP-00-CP-0011"],
        [sys.executable, "docs/checkpoints/SETUP-00-CP-0011/audit-harness/declare_inventory.py"],
        [sys.executable, "scripts/development-ledger/finalize_checkpoint.py",
         "--checkpoint", "docs/checkpoints/SETUP-00-CP-0011",
         "--commit-ref", "refs/tags/iacode-checkpoints/SETUP-00-CP-0011"],
        ["git", "add", "-A"],
        ["git", "commit", "--quiet", "-m", "audit: snapshot of SETUP-00-CP-0011 under attack"],
        [sys.executable, "scripts/development-ledger/seal_checkpoint.py",
         "--checkpoint", "docs/checkpoints/SETUP-00-CP-0011",
         "--message", "seal: snapshot of SETUP-00-CP-0011"],
    ):
        code, output = run(argv, destination)
        if code != 0:
            print(f"SNAPSHOT_FAILED {' '.join(argv[-3:])}: exit={code}\n{output}")
            return 2

    code, output = run([sys.executable, "scripts/development-ledger/validate_checkpoint.py"],
                       destination)
    print(f"snapshot validate exit={code}: {output[:400]}")
    code, output = run([sys.executable, "scripts/development-ledger/milestone_status.py",
                        "--milestone", "M0"], destination)
    print(f"snapshot milestone exit={code}: {output[:400]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
