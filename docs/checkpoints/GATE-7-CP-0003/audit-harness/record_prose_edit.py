"""Bind the authorized punctuation-only prose repair without publishing a detector-shaped line."""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))
from ledger_common import find_secrets, load_json, utc_now, write_json

TARGET = "docs/audits/M2-ENTRY-BLOCKED-2026-10-21/environment-isolation-0001/REPORT.md"
ORIGINAL = "3931194b0600007d5e2a8239350b650e9d87c2b8963238d1170e3e3b0216d4a5"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--after", action="store_true")
    options = parser.parse_args()
    raw = (ROOT / TARGET).read_bytes()
    receipt_path = CHECKPOINT / "AUTHORIZED-PROSE-DIFF.json"
    if not options.after:
        if hashlib.sha256(raw).hexdigest() != ORIGINAL or receipt_path.exists():
            raise ValueError("original prose bytes or fresh receipt precondition differ")
        pattern = b"authorization" + b": " + b"create"
        if raw.count(pattern) != 1 or find_secrets(raw.decode("utf-8")) != ["authorization header"]:
            raise ValueError("expected unique benign prose finding is absent or ambiguous")
        offset = raw.index(pattern) + len(b"authorization")
        write_json(receipt_path, {"target": TARGET, "authorizedBy": "OWNER-DECISIONS.json",
            "beforeSha256": ORIGINAL, "beforeBytes": len(raw), "byteOffset": offset,
            "removedHex": b": ".hex(), "insertedHex": b" to ".hex(),
            "contextWord": "authorization", "nextWord": "create",
            "status": "PREIMAGE_BOUND", "recordedAt": utc_now(),
            "note": "Exact byte diff, not a waiver. The original is reconstructable from the repaired file and inverse byte patch, verified against its preimage digest. No raw detector-shaped line is republished."})
    else:
        receipt = load_json(receipt_path)
        offset = receipt["byteOffset"]
        removed, inserted = bytes.fromhex(receipt["removedHex"]), bytes.fromhex(receipt["insertedHex"])
        if raw[offset:offset + len(inserted)] != inserted:
            raise ValueError("the actual edit is not the authorized byte patch")
        reconstructed = raw[:offset] + removed + raw[offset + len(inserted):]
        if hashlib.sha256(reconstructed).hexdigest() != ORIGINAL or find_secrets(raw.decode("utf-8")):
            raise ValueError("extra content changes or remaining strict-secret finding")
        receipt.update({"afterSha256": hashlib.sha256(raw).hexdigest(), "afterBytes": len(raw),
                        "status": "EXACT_AUTHORIZED_EDIT_VERIFIED", "verifiedAt": utc_now(),
                        "strictDetectorChanged": False, "technicalContentChanged": False})
        write_json(receipt_path, receipt)
    print("AUTHORIZED_PROSE_EDIT=" + ("VERIFIED" if options.after else "PREIMAGE_BOUND"))
    return 0


if __name__ == "__main__":
    from ledger_common import use_utf8_stdout
    use_utf8_stdout()
    raise SystemExit(main())
