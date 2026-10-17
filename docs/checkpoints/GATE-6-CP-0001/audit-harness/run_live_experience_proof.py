"""Retire stale output, execute the real actor and retain safe exact producer bytes on every result."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))

from ledger_common import find_secrets, utc_now, use_utf8_stdout, write_json


def main() -> int:
    report_path = ROOT / "var/experience-store-e2e.json"
    if report_path.is_symlink() or (ROOT / "var").is_symlink() or (ROOT / "var").is_junction():
        raise ValueError("redirected live proof output refused")
    report_path.unlink(missing_ok=True)
    result = subprocess.run([sys.executable, "scripts/iacode/scenarios/experience_store_e2e.py",
        "--report", "var/experience-store-e2e.json"], cwd=ROOT, capture_output=True, text=True,
        encoding="utf-8", errors="replace", check=False)
    directory = CHECKPOINT / "attempts"
    directory.mkdir(exist_ok=True)
    sequence = len(list(directory.glob("EXPERIENCE-LIVE-*-RECEIPT.json"))) + 1
    stem = f"EXPERIENCE-LIVE-{sequence:04d}"
    receipt = {"kind": "LOCAL_REAL_RUNTIME_PROOF_NOT_GATE_OR_INDEPENDENT_ACCEPTANCE",
        "observedAt": utc_now(), "exitCode": result.returncode, "producerPresent": report_path.is_file(),
        "result": "FAIL", "sourceDirtyAllowedOnlyForLocalRework": True}
    if report_path.is_file():
        raw = report_path.read_bytes()
        receipt.update({"producerBytes": len(raw), "producerSha256": hashlib.sha256(raw).hexdigest()})
        unsafe = find_secrets(raw.decode("utf-8", "strict"))
        receipt["unsafeOccurrences"] = len(unsafe)
        if not unsafe:
            destination = directory / (stem + ".json")
            with destination.open("xb") as output:
                output.write(raw)
            receipt["producerArchive"] = destination.relative_to(ROOT).as_posix()
            producer = json.loads(raw)
            receipt.update({"subjectCommit": producer.get("subjectCommit"),
                "sourceFingerprint": producer.get("sourceFingerprint"),
                "producerResult": producer.get("result"),
                "controls": len(producer.get("steps", [])),
                "failedControls": [row["name"] for row in producer.get("steps", []) if row.get("result") != "PASS"],
                "cleanup": producer.get("cleanup"), "failure": producer.get("failure")})
            if result.returncode == 0 and producer.get("result") == "PASS" and not receipt["failedControls"]:
                receipt["result"] = "PASS"
    write_json(directory / (stem + "-RECEIPT.json"), receipt)
    print(json.dumps(receipt, ensure_ascii=False))
    return 0 if receipt["result"] == "PASS" else 1


if __name__ == "__main__":
    use_utf8_stdout()
    raise SystemExit(main())
