"""Validate the corrected consumer on actual preserved FAIL evidence, without a verifier rerun."""

import hashlib
import json
import runpy
import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))
from ledger_common import use_utf8_stdout


def main() -> int:
    manifest = json.loads((CHECKPOINT / "attempts/FULL-VERIFY-RED-0002-MANIFEST.json").read_text(
        encoding="utf-8"))
    observation = next(row for row in manifest["observations"] if row["original"] == "VERIFY.json")
    content = (CHECKPOINT / observation["archive"]).read_bytes()
    if (len(content) != observation["bytes"]
            or hashlib.sha256(content).hexdigest() != observation["sha256"]):
        raise ValueError("preserved producer bytes differ from their actual archive")
    producer = json.loads(content)
    if producer["result"] != "FAIL":
        raise ValueError("this diagnostic must not relabel the actual failed invocation")
    publisher = runpy.run_path(str(CHECKPOINT / "audit-harness/run_full_verification.py"))
    denominator, passed, failed = publisher["summarize_stages"](producer)
    report = {
        "kind": "FAILED_VERIFIER_REINTERPRETATION_NOT_RERUN",
        "subjectCommit": manifest["subjectCommit"], "verifierRerun": False,
        "sourceArchive": observation["archive"], "sha256": observation["sha256"],
        "originalVerifierResult": producer["result"], "stageDenominator": denominator,
        "stagesPassed": passed, "stagesFailed": failed,
        "unavailableCollectorArtifacts": manifest["unavailableCollectorArtifacts"],
        "gateVerdictIssued": False,
    }
    destination = CHECKPOINT / "FAILED-VERIFIER-REINTERPRETATION.json"
    if destination.exists():
        raise ValueError("the original diagnostic must be preserved")
    destination.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    use_utf8_stdout()
    raise SystemExit(main())
