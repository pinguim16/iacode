"""Retain exact safe owned-live producer bytes before fallible report interpretation/rerun."""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))


def retire_previous(source: Path, directory: Path) -> None:
    """Archive an available prior safe observation before removing a stale producer location."""
    from ledger_common import find_secrets, write_json

    if source.is_symlink() or source.parent.is_symlink() or source.parent.is_junction():
        raise ValueError("redirected prior producer refused")
    if not source.is_file():
        return
    raw = source.read_bytes()
    if find_secrets(raw.decode("utf-8", errors="strict")):
        raise ValueError("unsafe prior producer cannot be archived")
    number = len(list(directory.glob("KNOWLEDGE-PREVIOUS-PRODUCER-*.json"))) + 1
    target = directory / f"KNOWLEDGE-PREVIOUS-PRODUCER-{number:04d}.json"
    with target.open("xb") as stream:
        stream.write(raw)
    if target.read_bytes() != raw:
        raise ValueError("prior producer archival byte equality failed")
    write_json(
        directory / f"KNOWLEDGE-PREVIOUS-RAW-RECEIPT-{number:04d}.json",
        {
            "kind": "PRIOR_PRODUCER_NOT_CURRENT_ACCEPTANCE",
            "sizeBytes": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest(),
            "artifact": target.name,
            "acceptanceGranted": False,
        },
    )
    source.unlink()


def main() -> int:
    from execute_gate import preserve_execution
    from ledger_common import find_secrets, utc_now, write_json

    source = ROOT / "var/knowledge-engine-e2e.json"
    directory = CHECKPOINT / "attempts"
    number = len(list(directory.glob("KNOWLEDGE-LIVE-PRODUCER-*.json"))) + 1
    target = directory / f"KNOWLEDGE-LIVE-PRODUCER-{number:04d}.json"
    manifest = directory / f"KNOWLEDGE-LIVE-RAW-RECEIPT-{number:04d}.json"
    if target.exists() or manifest.exists():
        raise ValueError("never overwrite an original producer observation")
    retire_previous(source, directory)
    try:
        result = preserve_execution(
            [
                "python",
                "scripts/iacode/scenarios/knowledge_engine_e2e.py",
                "--report",
                "var/knowledge-engine-e2e.json",
            ],
            "KNOWLEDGE-LIVE",
            "TARGETED_OWNED_LIVE_NOT_WHOLE_VERIFIER",
            "knowledge-engine-e2e",
        )
    finally:
        if source.is_file():
            raw = source.read_bytes()
            decoded = raw.decode("utf-8", errors="strict")
            if find_secrets(decoded):
                raise ValueError("unsafe producer report cannot be archived")
            with target.open("xb") as stream:
                stream.write(raw)
            write_json(
                manifest,
                {
                    "schemaVersion": "1.0.0",
                    "kind": "UNINTERPRETED_EXACT_PRODUCER_BYTES",
                    "observedAt": utc_now(),
                    "source": source.relative_to(ROOT).as_posix(),
                    "artifact": target.relative_to(CHECKPOINT).as_posix(),
                    "sizeBytes": len(raw),
                    "sha256": hashlib.sha256(raw).hexdigest(),
                    "safeOutputOccurrences": 0,
                    "acceptanceGranted": False,
                },
            )
    return result


if __name__ == "__main__":
    raise SystemExit(main())
