#!/usr/bin/env python3
"""Assemble the machine-readable record of what this audit executed.

Every section is copied from the artifact the execution produced, so the record is a transcript of
observed results rather than a summary written afterwards. The adversarial battery is appended once
it has run, because a report cannot contain its own result; that is the same residual limit the
checkpoint protocol records about sealing.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parent.parent
TARGET = CHECKPOINT / "AUDIT-EXECUTIONS.json"


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scratch", type=Path, required=True)
    parser.add_argument("--battery", type=Path, default=None)
    args = parser.parse_args()
    scratch = args.scratch.resolve()

    document = {
        "schemaVersion": "1.0.0",
        "auditCheckpoint": CHECKPOINT.name,
        "subjectCheckpoint": "SETUP-00-CP-0010",
        "subjectCommit": "90b67a7e0a11179465bc5c92dee22c78da36801f",
        "auditMechanism": "FRESH_SESSION_INDEPENDENT_AUDIT",
        "sameToolAsImplementer": True,
        "sameProviderAsImplementer": True,
        "crossToolValidation": "NOT_AVAILABLE",
        "generatedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }

    if TARGET.is_file():
        document = _load(TARGET)
        document["generatedAt"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    else:
        document["expectedRequirementSet"] = _load(scratch / "derive-expected.json")
        document["evidenceResolution"] = _load(scratch / "resolve-evidence.json")
        document["suiteWorkingRepository"] = _load(scratch / "suite-working.json")
        document["suiteCleanClone"] = _load(scratch / "suite-clone.json")
        document["namedRegressionTestsCleanClone"] = _load(scratch / "named-clone.json")
        document["namedRegressionTestsWorkingRepository"] = _load(scratch / "named-working.json")
        document["observations"] = _load(scratch / "observations.json")
        document["commandResults"] = _load(scratch / "command-results.json")

    if args.battery is not None:
        document["auditorBattery"] = _load(args.battery.resolve())

    TARGET.write_text(
        json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"AUDIT_EXECUTIONS sections={len(document)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
