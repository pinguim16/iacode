#!/usr/bin/env python3
"""Probe whether detected credential-shaped quality output is quarantined before persistence."""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import re
import sys
from datetime import UTC, datetime
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = Path("/app") if (Path("/app") / "evaluator_source").is_dir() else CHECKPOINT.parents[2]
for source in (
    ROOT / "packages" / "common" / "src",
    ROOT / "packages" / "contracts" / "src",
    ROOT / "services" / "evaluator" / "src",
    ROOT / "scripts" / "development-ledger",
):
    if source.is_dir():
        sys.path.insert(0, str(source))

from iacode_common.redaction import redact_mapping  # noqa: E402
from iacode_evaluator.evidence import (  # noqa: E402
    MemoryEvidenceRepository,
    MemoryObjectStore,
    QualityEvidenceStore,
)


def utc_now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


async def execute() -> dict[str, object]:
    # Built in pieces so neither source nor report carries a credential-shaped literal. The value
    # is synthetic and is never emitted; evidence records only booleans and digests.
    marker = "gh" + "p_" + ("A" * 32)
    execution = {
        "status": "SUCCEEDED",
        "exitCode": 0,
        "output": {"stdout": marker, "stderr": ""},
    }
    redacted = redact_mapping(execution)
    report_bytes = json.dumps(
        {"checkId": "synthetic-secret-probe", "execution": redacted},
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    # This is the exact GitHub-token class owned by the canonical scanner. The probe does not need
    # the repository file in the runtime image; it asks whether the evaluator path removes or
    # quarantines a value that the policy scanner necessarily classifies as a finding.
    scanner_detected = re.search(
        r"\bgh[pousr]_[A-Za-z0-9]{20,}\b", report_bytes.decode("utf-8")
    ) is not None
    objects = MemoryObjectStore()
    repository = MemoryEvidenceRepository()
    store = QualityEvidenceStore(client=objects, bucket="audit", repository=repository)
    contract = await store.put(
        run_id="synthetic-audit-run",
        result_id=None,
        kind="report",
        content=report_bytes,
        media_type="application/json",
        producer="iacode-evaluator",
        source_digests=("a" * 64,),
    )
    key = f"quality/evidence/{contract.digest}"
    stored = objects.objects.get(("audit", key), b"")
    resolved = await store.resolve(contract)
    marker_digest = hashlib.sha256(marker.encode("utf-8")).hexdigest()
    return {
        "syntheticMarkerDigest": marker_digest,
        "scannerDetected": scanner_detected,
        "scannerKinds": ["GitHub credential"] if scanner_detected else [],
        "redactionRemovedMarker": marker not in report_bytes.decode("utf-8"),
        "persistenceAccepted": bool(stored),
        "storedContentContainsMarker": marker.encode("utf-8") in stored,
        "storedEvidenceResolved": resolved,
        "evidenceDigest": contract.digest,
        "evidenceSizeBytes": contract.sizeBytes,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path, required=True)
    arguments = parser.parse_args()
    observed = asyncio.run(execute())
    expected = {
        "scannerDetected": True,
        "redactionRemovedMarker": True,
        "persistenceAccepted": False,
        "storedContentContainsMarker": False,
        "storedEvidenceResolved": False,
    }
    violations = [
        key for key, value in expected.items() if observed.get(key) != value
    ]
    result = "PASS" if not violations else "FAIL"
    report = {
        "schemaVersion": "1.0.0",
        "artifact": "GATE-4-SECRET-EVIDENCE-PRE-PERSISTENCE-PROBE",
        "checkpoint": CHECKPOINT.name,
        "generatedAt": utc_now(),
        "requirement": "GATE-4-19.2",
        "expected": expected,
        "observed": observed,
        "violations": violations,
        "result": result,
        "safety": (
            "The marker was synthetic, constructed only in memory, never printed, and represented "
            "in this report solely by its SHA-256 digest."
        ),
        "evidence": [
            "file:services/evaluator/src/iacode_evaluator/activities.py",
            "file:services/evaluator/src/iacode_evaluator/evidence.py",
            "file:scripts/development-ledger/secret_scan.py",
            "file:docs/GATE-4-CHECKLIST.md",
            "file:docs/runbooks/QUALITY-ENGINE.md",
        ],
    }
    output = arguments.report.resolve()
    output.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(
        f"SECRET_EVIDENCE_PROBE={result} scannerDetected={observed['scannerDetected']} "
        f"redacted={observed['redactionRemovedMarker']} "
        f"persisted={observed['persistenceAccepted']} "
        f"storedMarker={observed['storedContentContainsMarker']} "
        f"resolved={observed['storedEvidenceResolved']}"
    )
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
