"""Actual complete local quality/client/API controls followed by real owned live acceptance."""

from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))

from ledger_common import find_secrets, scope_fingerprint, utc_now, use_utf8_stdout, write_json


def main() -> int:
    if len(sys.argv) != 1:
        raise ValueError("the complete pre-live sequence has no phase-selection arguments")
    harness = CHECKPOINT.relative_to(ROOT).as_posix() + "/audit-harness/"
    phases = (
        ("mechanical-format", [harness + "format_new_python.py"]),
        ("whole-mandatory-lint", ["scripts/iacode/gates/lint.py"]),
        ("complete-domain-and-api-unit", [harness + "run_experience_checks.py", "--suite", "both"]),
        ("whole-mandatory-client-tests", ["scripts/iacode/gates/client_tests.py"]),
        ("complete-gate6-root", ["-m", "unittest", "discover", "-s", "tests", "-p", "test_gate6_*", "-v"]),
        ("actual-owned-provider-sandbox-experience", [harness + "run_live_experience_proof.py"]),
    )
    report = {"kind": "LOCAL_PRE_LIVE_SEQUENCE_NOT_FULL_GATE_ACCEPTANCE", "status": "RUNNING",
              "startedAt": utc_now(), "phases": []}
    destination = CHECKPOINT / "PRE-LIVE-PROGRESS.json"
    if destination.is_file():
        raw = destination.read_bytes()
        if find_secrets(raw.decode("utf-8", "strict")):
            raise ValueError("unsafe previous progress cannot be exported")
        archive = CHECKPOINT / "attempts"
        sequence = len(list(archive.glob("PRE-LIVE-SEQUENCE-*.json"))) + 1
        archived = archive / f"PRE-LIVE-SEQUENCE-{sequence:04d}.json"
        with archived.open("xb") as output:
            output.write(raw)
        report["previousProgressArchive"] = archived.relative_to(CHECKPOINT).as_posix()
        report["previousProgressBytes"] = len(raw)
        report["previousProgressSha256"] = hashlib.sha256(raw).hexdigest()
    for name, arguments in phases:
        report["currentPhase"] = name
        write_json(destination, report)
        print("PRE_LIVE_PHASE_STARTED " + name, flush=True)
        result = subprocess.run([sys.executable, *arguments], cwd=ROOT, text=True,
                                encoding="utf-8", errors="replace", check=False)
        report["phases"].append({"name": name, "exitCode": result.returncode,
                                 "finishedAt": utc_now()})
        write_json(destination, report)
        print(f"PRE_LIVE_PHASE_FINISHED {name} exit={result.returncode}", flush=True)
        if result.returncode:
            report["status"] = "FAIL"
            write_json(destination, report)
            return result.returncode
    report.update({"status": "PASS", "finishedAt": utc_now(),
                   "sourceFingerprintAfter": scope_fingerprint(ROOT)})
    write_json(destination, report)
    print("PRE_LIVE_SEQUENCE=PASS; immutable full verification and ordered closure remain pending")
    return 0


if __name__ == "__main__":
    use_utf8_stdout()
    raise SystemExit(main())
