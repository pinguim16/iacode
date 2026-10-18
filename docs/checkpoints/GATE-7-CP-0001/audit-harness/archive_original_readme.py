"""Capture original published README bytes once, before correction, with original interpretation."""

from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))

from ledger_common import find_secrets, load_json, utc_now, use_utf8_stdout, write_json


def main() -> int:
    base = load_json(CHECKPOINT / "STATE.json")["baseCommit"]
    result = subprocess.run(["git", "show", base + ":README.md"], cwd=ROOT, capture_output=True,
                            check=True)
    raw = result.stdout
    if find_secrets(raw.decode("utf-8", errors="strict")):
        raise ValueError("original README is not safe to archive")
    directory = CHECKPOINT / "attempts"
    directory.mkdir(exist_ok=True)
    target = directory / "README-ROLLUP-0001.md.raw"
    manifest = directory / "README-ROLLUP-0001.json"
    if target.exists() or manifest.exists():
        raise ValueError("never replay original observation archival")
    with target.open("xb") as stream:
        stream.write(raw)
    if target.read_bytes() != raw:
        raise ValueError("raw archival did not retain original bytes")
    write_json(manifest, {
        "kind": "ORIGINAL_PUBLISHED_README_NOT_ACTIVE_RELOCATED_DOCUMENTATION",
        "sourceCommit": base, "sourcePath": "README.md", "observedAt": utc_now(),
        "artifact": target.relative_to(CHECKPOINT).as_posix(),
        "sha256": hashlib.sha256(raw).hexdigest(), "sizeBytes": len(raw),
        "interpretation": "Original repository root at the named immutable published commit.",
        "trainingAllowed": False, "ragAllowed": False, "distillationAllowed": False,
    })
    print("ORIGINAL_README_ARCHIVED bytes=" + str(len(raw)) + " sha256=" + hashlib.sha256(raw).hexdigest())
    return 0


if __name__ == "__main__":
    use_utf8_stdout()
    raise SystemExit(main())
