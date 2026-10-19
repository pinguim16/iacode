"""Preserve exact refused continuation documents before their structured correction."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))


def main() -> int:
    from ledger_common import find_secrets, load_json, use_utf8_stdout, utc_now, write_json

    use_utf8_stdout()
    destination = CHECKPOINT / "attempts/CONTINUATION-REFUSAL-0001-MANIFEST.json"
    if destination.exists() or load_json(CHECKPOINT / "STATE.json")["status"] != "IN_PROGRESS":
        raise ValueError("never replay original archival or rewrite a sealed checkpoint")
    records = [
        json.loads(line)
        for line in (CHECKPOINT / "COMMANDS.jsonl").read_text(encoding="utf-8").splitlines()
        if line
    ]
    if not any(row["id"] == "cmd-0223" and row["exitCode"] == 1 for row in records):
        raise ValueError("the actual original structural refusal must resolve")
    paths = [
        CHECKPOINT / "HANDOFF.md",
        CHECKPOINT / "NEXT.md",
        ROOT / ".iacode/memory/retrospectives/GATE-7-CP-0001.md",
    ]
    rows = []
    for ordinal, path in enumerate(paths, 1):
        if path.is_symlink() or path.is_junction() or not path.is_file():
            raise ValueError("regular original required")
        raw = path.read_bytes()
        if not raw or find_secrets(raw.decode("utf-8", errors="strict")):
            raise ValueError("unsafe or empty original refused")
        target = CHECKPOINT / "attempts" / f"CONTINUATION-REFUSAL-0001-{ordinal}.raw"
        with target.open("xb") as stream:
            stream.write(raw)
        if target.read_bytes() != raw:
            raise ValueError("original byte equality failed")
        rows.append(
            {
                "original": path.relative_to(ROOT).as_posix(),
                "archive": target.relative_to(CHECKPOINT).as_posix(),
                "bytes": len(raw),
                "sha256": hashlib.sha256(raw).hexdigest(),
            }
        )
    write_json(
        destination,
        {
            "kind": "EXACT_FAILED_CONTINUATION_NOT_CURRENT_ACCEPTANCE",
            "observedAt": utc_now(),
            "commandId": "cmd-0223",
            "files": rows,
            "originalConsoleBytesRetained": False,
            "gateVerdictIssued": False,
            "trainingAllowed": False,
            "independentValidation": False,
        },
    )
    print("REFUSED_CONTINUATION_ORIGINALS_PRESERVED; no console-byte or acceptance claim")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
