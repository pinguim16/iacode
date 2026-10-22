"""Record an actual completed full lint retry without closing unrelated rework."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(
    0, str(Path(__file__).resolve().parents[1].parents[2] / "scripts/development-ledger")
)
from ledger_common import load_json, scope_fingerprint, utc_now, write_json

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]


def main():
    path = "quality-attempts/lint/run-0003.json"
    receipt = load_json(CHECKPOINT / path)
    if (
        receipt["exitCode"] != 0
        or not receipt["sourceUnchanged"]
        or receipt["sourceFingerprint"] != scope_fingerprint(ROOT)
        or any(row["refused"] for row in receipt["streams"].values())
    ):
        raise ValueError("Actual current complete safe lint success is required")
    quality = load_json(CHECKPOINT / "QUALITY.json")
    quality["checks"]["lint"].update(
        status="PASS",
        evidence=["file:" + path],
        justification=(
            "Actual full canonical retry completed at unchanged source; o"
            "riginal export failure preserved."
        ),
    )
    write_json(CHECKPOINT / "QUALITY.json", quality)
    rework = load_json(CHECKPOINT / "INTERNAL-ENVIRONMENT-REWORK.json")
    item = next(row for row in rework["items"] if row["id"] == "PRIVATE-BUILDER-EXPORT-001")
    item.update(status="RESOLVED_BY_COMPLETED_UNCHANGED_RETRY", successEvidence=path)
    write_json(CHECKPOINT / "INTERNAL-ENVIRONMENT-REWORK.json", rework)
    active = load_json(CHECKPOINT / "ACTIVE-VALIDATION.json")
    active["recordedAt"] = utc_now()
    item = next(row for row in active["nativeToolSessions"] if row["id"] == 61756)
    item.update(lastObservedStatus="COMPLETED", exitCode=0, evidence=path)
    write_json(CHECKPOINT / "ACTIVE-VALIDATION.json", active)
    print("LINT_COMPLETION_RECORDED_ADAPTER_REWORK_AND_ROOT_BASELINE_STILL_PENDING")
    return 0


if __name__ == "__main__":
    from ledger_common import use_utf8_stdout

    use_utf8_stdout()
    raise SystemExit(main())
