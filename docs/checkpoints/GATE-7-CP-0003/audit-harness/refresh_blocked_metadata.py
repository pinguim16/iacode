"""Repair only observed bookkeeping defects while preserving BLOCKED and actual red receipts."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(
    0, str(Path(__file__).resolve().parents[1].parents[2] / "scripts/development-ledger")
)
from anchors import load_anchors
from ledger_common import load_json, utc_now, write_json
from validate_checkpoint import _validate_quality_evidence

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]


def main() -> int:
    quality = load_json(CHECKPOINT / "QUALITY.json")
    for name in ("lint", "staticAnalysis"):
        quality["checks"][name]["evidence"] = [f"file:quality-attempts/{name}/run-0001.json"]
    validation = sorted((CHECKPOINT / "quality-attempts/checkpointValidation").glob("run-*.json"))[
        -1
    ]
    for name, evidence in (
        ("checkpointValidation", validation.relative_to(CHECKPOINT).as_posix()),
        ("deliveryCompleteness", "COMPLETENESS-REPORT.json"),
    ):
        quality["checks"][name].update(
            {
                "status": "FAIL",
                "evidence": ["file:" + evidence],
                "justification": "Actual red progress validation; no readiness claim.",
            }
        )
    errors = []
    records = [
        json.loads(line)
        for line in (CHECKPOINT / "COMMANDS.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    _validate_quality_evidence(
        CHECKPOINT,
        quality,
        quality["checks"],
        {row["id"]: row.get("exitCode") for row in records},
        quality["schemaVersion"],
        errors,
    )
    if errors:
        raise ValueError(
            "quality evidence must resolve at its owning checkpoint: " + "; ".join(errors)
        )
    write_json(CHECKPOINT / "QUALITY.json", quality)
    state = load_json(CHECKPOINT / "STATE.json")
    if state["status"] != "BLOCKED":
        raise ValueError("only the actual blocked progress snapshot may be updated")
    state["integrity"]["anchors"] = len(load_anchors(ROOT))
    state["updatedAt"] = utc_now()
    write_json(CHECKPOINT / "STATE.json", state)
    metadata = load_json(CHECKPOINT / "RUN-METADATA.json")
    metadata["finishedAt"] = state["updatedAt"]
    write_json(CHECKPOINT / "RUN-METADATA.json", metadata)
    print(
        "BLOCKED_BOOKKEEPING_BOUND status_unchanged quality_reference"
        "s_resolved anchor_count_derived"
    )
    return 0


if __name__ == "__main__":
    from ledger_common import use_utf8_stdout

    use_utf8_stdout()
    raise SystemExit(main())
