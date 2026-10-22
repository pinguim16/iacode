"""Bind observed valid draft validation before unsealed immutable-subject publication."""

import sys
from pathlib import Path

sys.path.insert(
    0, str(Path(__file__).resolve().parents[1].parents[2] / "scripts/development-ledger")
)
from ledger_common import load_json, scope_fingerprint, write_json
from sync_in_progress_metadata import synchronize

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]


def main():
    receipt_path = sorted(
        (CHECKPOINT / "quality-attempts/checkpointValidation").glob("run-*.json")
    )[-1]
    receipt = load_json(receipt_path)
    if (
        receipt["exitCode"] != 0
        or not receipt["sourceUnchanged"]
        or receipt["sourceFingerprint"] != scope_fingerprint(ROOT)
        or any(row["refused"] for row in receipt["streams"].values())
    ):
        raise ValueError("Actual current safe valid draft observation required")
    quality = load_json(CHECKPOINT / "QUALITY.json")
    quality["checks"]["checkpointValidation"].update(
        status="PASS",
        evidence=["file:" + receipt_path.relative_to(CHECKPOINT).as_posix()],
        justification=(
            "Actual quiescent valid IN_PROGRESS draft; not terminal readi"
            "ness or independent validation."
        ),
    )
    write_json(CHECKPOINT / "QUALITY.json", quality)
    synchronize(ROOT, CHECKPOINT)
    print(
        "Valid draft observation bound; only IN_PROGRESS immutable runtime publication may follow"
    )
    return 0


if __name__ == "__main__":
    from ledger_common import use_utf8_stdout

    use_utf8_stdout()
    raise SystemExit(main())
