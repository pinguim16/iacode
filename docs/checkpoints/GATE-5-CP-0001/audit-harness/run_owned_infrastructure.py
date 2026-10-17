"""Reexecute every infrastructure case against a fresh owned dynamic-port stack."""

from __future__ import annotations

import json
import re
import runpy
import subprocess
import sys
import tempfile
import time
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))
sys.path.insert(0, str(ROOT / "scripts/iacode"))
from derive_counts import count_unittest_cases
from ledger_common import scope_fingerprint, use_utf8_stdout, utc_now
from verify import clean_verification_project, verification_environment


def main() -> int:
    destination = CHECKPOINT / "INFRASTRUCTURE-REWORK.json"
    if destination.exists():
        raise ValueError("preserve the prior infrastructure observation before a rerun")
    probe = runpy.run_path(str(
        ROOT / "docs/checkpoints/GATE-4-CP-0006/RUN-INDEPENDENT-FULL-VERIFICATION.py"))
    snapshot = probe["snapshot_project"]
    before = snapshot("iacode")
    fingerprint = scope_fingerprint(ROOT)
    report = {"kind": "SAME_SESSION_OWNED_INFRASTRUCTURE_REWORK", "result": "FAIL",
              "generatedAt": utc_now(), "sourceFingerprint": fingerprint, "commands": []}
    with tempfile.TemporaryDirectory(prefix="iacode-gate5-infra-") as temporary:
        lease = Path(temporary)
        if (lease.resolve().parent != Path(tempfile.gettempdir()).resolve()
                or not lease.name.startswith("iacode-gate5-infra-")
                or lease.is_symlink() or lease.is_junction()):
            raise ValueError("unexpected freshly created infrastructure owner")
        environment = verification_environment(lease, None)
        project = environment["COMPOSE_PROJECT_NAME"]
        report["composeProject"] = project
        existing = snapshot(project)
        if any(existing[kind] for kind in ("containers", "volumes", "networks")):
            raise ValueError("new namespace collides with existing resources; none removed")
        try:
            for name, arguments in (
                ("stack", [sys.executable, "scripts/iacode/stack.py", "up", "--build"]),
                ("tests", [sys.executable, "-m", "unittest", "discover", "-s", "infra/tests", "-v"]),
            ):
                started = time.monotonic()
                completed = subprocess.run(
                    arguments, cwd=ROOT, env=environment, capture_output=True, text=True,
                    encoding="utf-8", errors="replace", check=False,
                )
                row = {"name": name, "arguments": ["python", *arguments[1:]],
                       "exitCode": completed.returncode,
                       "durationSeconds": round(time.monotonic() - started, 3)}
                if name == "tests":
                    match = re.search(r"Ran (\d+) tests?", completed.stderr + completed.stdout)
                    row["casesExecuted"] = int(match[1]) if match else None
                    row["casesDerived"] = count_unittest_cases(ROOT, "infra/tests")
                    row["skipped"] = "skipped=" in completed.stderr + completed.stdout
                    row["complete"] = (
                        row["casesExecuted"] == row["casesDerived"] and not row["skipped"]
                    )
                if completed.returncode:
                    row["failureTail"] = (completed.stdout + completed.stderr)[-4000:]
                report["commands"].append(row)
                print(f"OWNED_INFRA_{name.upper()} exit={completed.returncode}", flush=True)
                if completed.returncode:
                    break
        finally:
            cleanup = clean_verification_project(environment)
            owned_after = snapshot(project)
            report["cleanupExitCode"] = cleanup.returncode
            report["ownedAfter"] = owned_after
            report["ownedRemoved"] = cleanup.returncode == 0 and not any(
                owned_after[kind] for kind in ("containers", "volumes", "networks"))
    report["temporaryDirectoryRemoved"] = not lease.exists()
    report["sharedBefore"], report["sharedAfter"] = before, snapshot("iacode")
    report["sharedUnchanged"] = report["sharedBefore"] == report["sharedAfter"]
    report["sourceInputsUnchanged"] = scope_fingerprint(ROOT) == fingerprint
    if (len(report["commands"]) == 2 and all(row["exitCode"] == 0 for row in report["commands"])
            and report["commands"][-1]["complete"] and report["ownedRemoved"]
            and report["temporaryDirectoryRemoved"] and report["sharedUnchanged"]
            and report["sourceInputsUnchanged"]):
        report["result"] = "PASS"
    destination.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(report, indent=2))
    return 0 if report["result"] == "PASS" else 1


if __name__ == "__main__":
    use_utf8_stdout()
    raise SystemExit(main())
