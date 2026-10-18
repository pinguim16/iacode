"""Typed nonempty source observations and original-byte proofs; never a Gate verdict."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))


def require_completed_text(observation: dict) -> str:
    if (
        type(observation) is not dict
        or observation.get("session_id") is not None
        or type(observation.get("exit_code")) is not int
        or observation["exit_code"] != 0
        or type(observation.get("output")) is not str
        or not observation["output"].strip()
    ):
        raise ValueError("completed successful nonempty source observation required")
    value = observation["output"]
    value.encode("utf-8", errors="strict")
    if "\x00" in value:
        raise ValueError("source observation contains a forbidden null")
    return value


def validate_observation(raw: bytes, expected_sha256: str, expected_size: int) -> dict:
    if (
        type(raw) is not bytes
        or not raw
        or type(expected_sha256) is not str
        or re.fullmatch(r"[0-9a-f]{64}", expected_sha256) is None
        or type(expected_size) is not int
        or expected_size <= 0
        or len(raw) != expected_size
        or hashlib.sha256(raw).hexdigest() != expected_sha256
    ):
        raise ValueError("actual nonempty bytes, size and digest must agree")
    return {
        "kind": "VERIFIED_NONEMPTY_ORIGINAL_BYTES",
        "bytes": len(raw),
        "sha256": expected_sha256,
        "result": "PASS",
        "gateVerdictGranted": False,
    }


def verify_file_bytes(path: Path, expected_sha256: str, expected_size: int) -> dict:
    if path.is_symlink() or path.is_junction() or not path.is_file():
        raise ValueError("a regular actual original file is required")
    return validate_observation(path.read_bytes(), expected_sha256, expected_size)


def main() -> int:
    from ledger_common import load_json, use_utf8_stdout, write_json

    use_utf8_stdout()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path)
    parser.add_argument("--read-only", action="store_true")
    options = parser.parse_args()
    if options.source is not None:
        path = (ROOT / options.source).resolve(strict=True)
        if not path.is_relative_to(CHECKPOINT / "audit-harness") or path.suffix != ".py":
            raise ValueError("only the declared checkpoint Python preimage family is readable")
        raw = path.read_bytes()
        text = raw.decode("utf-8", errors="strict")
        require_completed_text({"exit_code": 0, "output": text})
        print(
            json.dumps(
                {
                    "kind": "COMPLETE_SOURCE_PREIMAGE_NOT_CODE_ACCEPTANCE",
                    "completed": True,
                    "bytes": len(raw),
                    "sha256": hashlib.sha256(raw).hexdigest(),
                    "text": text,
                }
            )
        )
        return 0
    manifest = load_json(CHECKPOINT / "attempts/HELPER-ORIGINALS.json")
    if not manifest["files"]:
        raise ValueError("original proof denominator cannot be empty")
    rows = []
    for record in manifest["files"]:
        path = (CHECKPOINT / record["path"]).resolve(strict=True)
        if not path.is_relative_to(CHECKPOINT / "attempts"):
            raise ValueError("original observation escaped its declared archive")
        rows.append(
            {
                "path": record["path"],
                **verify_file_bytes(path, record["sha256"], record["bytes"]),
            }
        )
    report = {
        "kind": "ACTUAL_TYPED_ORIGINAL_BYTE_VERIFICATION_NOT_GATE_ACCEPTANCE",
        "result": "PASS",
        "observations": rows,
        "gateVerdictGranted": False,
    }
    if not options.read_only:
        if load_json(CHECKPOINT / "STATE.json")["status"] != "IN_PROGRESS":
            raise ValueError("terminal subjects permit only read-only verification")
        write_json(CHECKPOINT / "RAW-ORIGINALS-VALIDATION.json", report)
    print(json.dumps(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
