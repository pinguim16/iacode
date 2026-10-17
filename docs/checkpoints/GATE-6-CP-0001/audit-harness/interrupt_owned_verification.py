"""Stop only the exact re-observed owned verifier, preserving incomplete-attempt evidence."""

import argparse
import json
import subprocess
import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))
from ledger_common import scope_fingerprint, utc_now, write_json, use_utf8_stdout

use_utf8_stdout()

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--pid", type=int, required=True)
parser.add_argument("--parent", type=int, required=True)
parser.add_argument("--created", required=True)
parser.add_argument("--recorder", type=int, required=True)
args = parser.parse_args()
progress = json.loads((CHECKPOINT / "FULL-VERIFY-PROGRESS.json").read_text(encoding="utf-8"))
target = CHECKPOINT / "attempts/FULL-VERIFY-INTERRUPTED-0001.json"
if target.exists() or args.pid <= 0 or args.parent <= 0:
    raise ValueError("existing interruption evidence or invalid exact process identity")
query = (f"Get-CimInstance Win32_Process | Where-Object {{ $_.ProcessId -in @({args.pid},{args.parent},{args.recorder}) }} | "
         "ForEach-Object { [pscustomobject]@{ processId=$_.ProcessId; parentProcessId=$_.ParentProcessId; "
         "createdUtc=$_.CreationDate.ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ'); commandLine=$_.CommandLine } } | ConvertTo-Json")
observed = json.loads(subprocess.check_output(["powershell.exe", "-NoProfile", "-Command", query]).decode("utf-8"))
rows = {row["processId"]: row for row in observed}
child, parent = rows.get(args.pid, {}), rows.get(args.parent, {})
recorder = rows.get(args.recorder, {})
if (parent.get("parentProcessId") != args.recorder
        or "scripts/development-ledger/record_command.py --subject-commit " + progress["subjectCommit"] not in recorder.get("commandLine", "")
        or child.get("parentProcessId") != args.parent or child.get("createdUtc") != args.created
        or "scripts/iacode/verify.py --keep-going --quiet" not in child.get("commandLine", "")
        or "audit-harness/run_full_verification.py --commit " + progress["subjectCommit"] not in parent.get("commandLine", "")):
    raise ValueError("owned process identity diverged; no process was terminated")
stopped = subprocess.run(["taskkill", "/PID", str(args.pid), "/T", "/F"],
                         capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
print(stopped.stdout)
if stopped.returncode:
    raise RuntimeError("owned verifier termination did not succeed: " + stopped.stderr[-500:])
write_json(target, {"kind": "INTENTIONALLY_INTERRUPTED_INCOMPLETE_VERIFICATION_NOT_PASS",
    "generatedAt": utc_now(), "subjectCommit": progress["subjectCommit"],
    "sourceFingerprint": scope_fingerprint(ROOT), "progress": progress,
    "ownedProcessObservation": observed, "terminationExitCode": stopped.returncode,
    "reason": "Add the mandatory Gate6 in-scope retrospective before final immutable assurance so the later closure needs no unverified assurance-source edit. No completed stage or PASS is inferred.",
    "verificationResult": "NOT_COMPLETED", "gateVerdictIssued": False})
# The outer interrupted recorder must finish appending its own outcome before this recorder
# may append. A process session ID is not completion; no inventory/validator is running.
import time
deadline = time.monotonic() + 180
while time.monotonic() < deadline:
    alive = subprocess.check_output(["powershell.exe", "-NoProfile", "-Command",
        f"if (Get-CimInstance Win32_Process -Filter 'ProcessId={args.recorder}') {{ 'ACTIVE' }}"]).decode("utf-8").strip()
    if not alive:
        break
    time.sleep(.5)
else:
    raise RuntimeError("the original recorder has not finished; no later metadata writer may start")
print("OWNED_VERIFIER_INTERRUPTED original_recorder_finished=true incomplete_attempt_preserved=true test_pass_claimed=false")
