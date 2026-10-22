"""Preserve exact unreleased adapter bytes before the queued path-boundary correction."""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))
from ledger_common import find_secrets, scope_fingerprint, utc_now, write_json


def main():
    source = ROOT / "scripts/development-ledger/audit_runner_bridge.py"
    directory = CHECKPOINT / "raw-preimages"
    directory.mkdir(exist_ok=True)
    archive = directory / "BRIDGE-PATH-001.py.raw"
    receipt = directory / "BRIDGE-PATH-001.json"
    if archive.exists() or receipt.exists():
        raise ValueError("Do not replace a preimage")
    raw = source.read_bytes()
    if find_secrets(raw.decode("utf-8", errors="strict")):
        raise ValueError("Unsafe source observation")
    with archive.open("xb") as stream:
        stream.write(raw)
    if source.read_bytes() != raw or archive.read_bytes() != raw:
        raise ValueError("Source changed during preimage capture")
    write_json(receipt, {"observedAt": utc_now(), "kind": "RAW_SOURCE_OBSERVATION_NOT_ACTIVE_IMPLEMENTATION",
                        "origin": source.relative_to(ROOT).as_posix(),
                        "archive": archive.relative_to(CHECKPOINT).as_posix(),
                        "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw),
                        "sourceFingerprint": scope_fingerprint(ROOT), "sourceDirty": True,
                        "originCommit": None,
                        "note": "New uncommitted control asset. Preserve as uninterpreted source evidence; the failing null/adverse boundary observation is causal-attempts/bridge-path-bounds/run-0001.json. No correction or independent acceptance is claimed."})
    print("EXACT_BRIDGE_PREIMAGE_PRESERVED " + hashlib.sha256(raw).hexdigest())
    return 0


if __name__ == "__main__":
    from ledger_common import use_utf8_stdout
    use_utf8_stdout()
    raise SystemExit(main())
