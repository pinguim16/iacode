"""Confirm the actual archived-link failure and stop only the freshly revalidated owned v7 tree."""

from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))
from ledger_common import find_secrets, load_json, use_utf8_stdout, utc_now, write_json


def main() -> int:
    target = CHECKPOINT / "attempts/FULL-VERIFY-INTERRUPTED-0004.json"
    if target.exists():
        raise ValueError("this interruption must never be replayed")
    progress = load_json(CHECKPOINT / "FULL-VERIFY-PROGRESS.json")
    subject = "cf125cb03deff658df2922c7b74aed4b530e1b17"
    clone = Path(progress["clone"])
    if progress["subjectCommit"] != subject or subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=clone).decode().strip() != subject:
        raise ValueError("the actual exact v7 subject is required")
    diagnostic = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests",
        "-p", "test_development_ledger.py", "-k", "test_documentation_links_resolve", "-v"],
        cwd=clone, text=True, encoding="utf-8", errors="replace", capture_output=True, check=False)
    output = diagnostic.stdout + diagnostic.stderr
    if diagnostic.returncode != 1 or "RUNTIME-V6-FINALIZATION-FINAL-REPORT.md" not in output or find_secrets(output):
        raise ValueError("actual safe diagnostic must reproduce the archived relative-link failure")
    query = ("Get-CimInstance Win32_Process -Filter \"Name = 'python.exe'\" | "
        "Where-Object { $_.ProcessId -in @(8680,22996,5708) } | ForEach-Object { "
        "[pscustomobject]@{ processId=$_.ProcessId; parentProcessId=$_.ParentProcessId; "
        "createdUtc=$_.CreationDate.ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ'); commandLine=$_.CommandLine } } | ConvertTo-Json")
    observed = json.loads(subprocess.check_output(["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", query]).decode("utf-8"))
    rows = {row["processId"]: row for row in observed}
    child, parent, recorder = rows.get(8680, {}), rows.get(22996, {}), rows.get(5708, {})
    if (child.get("parentProcessId") != 22996 or child.get("createdUtc") != "2026-10-18T07:17:30Z"
            or "scripts/iacode/verify.py --keep-going --quiet" not in child.get("commandLine", "")
            or parent.get("parentProcessId") != 5708 or subject not in parent.get("commandLine", "")
            or "audit-harness/run_full_verification.py" not in parent.get("commandLine", "")
            or subject not in recorder.get("commandLine", "") or "record_command.py" not in recorder.get("commandLine", "")):
        raise ValueError("exact fresh process identity changed; no termination performed")
    stopped = subprocess.run(["taskkill", "/PID", "8680", "/T", "/F"], text=True,
        encoding="utf-8", errors="replace", capture_output=True, check=False)
    if stopped.returncode:
        raise ValueError("exact owned interruption failed")
    report = {"kind": "INTENTIONALLY_INTERRUPTED_INCOMPLETE_VERIFICATION_NOT_PASS", "generatedAt": utc_now(),
        "subjectCommit": subject, "progress": progress, "ownedProcessObservation": observed,
        "terminationExitCode": stopped.returncode, "diagnosticCommand": "python -m unittest discover -s tests -p test_development_ledger.py -k test_documentation_links_resolve -v",
        "diagnosticWorkingDirectory": str(clone), "diagnosticExitCode": diagnostic.returncode,
        "diagnosticOutput": output, "reason": "Actual archived raw Markdown is misclassified as active relative-link documentation; preserve bytes in an explicitly raw archive before complete fresh acceptance.",
        "verificationResult": "NOT_COMPLETED", "gateVerdictIssued": False}
    write_json(target, report)
    deadline = time.monotonic() + 180
    while time.monotonic() < deadline:
        alive = subprocess.check_output(["powershell.exe", "-NoProfile", "-NonInteractive", "-Command",
            "if (Get-CimInstance Win32_Process -Filter 'ProcessId=5708') { 'ACTIVE' }"]).decode().strip()
        if not alive:
            print("V7_OWNED_TREE_INTERRUPTED original_recorder_finished=true diagnostic=FAIL incomplete_attempt_preserved=true")
            return 0
        time.sleep(.5)
    raise ValueError("original recorder still active; no later writer may start")


if __name__ == "__main__":
    use_utf8_stdout()
    raise SystemExit(main())
