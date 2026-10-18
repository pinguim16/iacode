"""Compare exact staged raw observation bytes, not canonicalized JSON projections."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))
from ledger_common import use_utf8_stdout, write_json


def main() -> int:
    paths = sorted((CHECKPOINT / "attempts").glob("*.json"))
    paths += sorted((CHECKPOINT / "suite-attempts").glob("*.json"))
    paths += sorted((CHECKPOINT / "suite-attempts").glob("*.log"))
    archive = CHECKPOINT / "attempts/RUNTIME-V6-FINALIZATION-ARCHIVE.json"
    if archive.is_file():
        for row in json.loads(archive.read_text(encoding="utf-8"))["records"]:
            candidate = ROOT / row["archive"]
            raw = candidate.read_bytes()
            if len(raw) != row["bytes"] or hashlib.sha256(raw).hexdigest() != row["sha256"]:
                raise ValueError("original archive changed: " + row["archive"])
            paths.append(candidate)
    paths = sorted(set(paths))
    if not paths:
        raise ValueError("actual observation files required")
    observations = []
    for path in paths:
        if path.is_symlink() or not path.is_file():
            raise ValueError("missing or redirected observation")
        name = path.relative_to(ROOT).as_posix()
        raw = path.read_bytes()
        staged = subprocess.check_output(["git", "show", ":" + name], cwd=ROOT)
        if staged != raw:
            raise ValueError("staged raw observation bytes differ: " + name)
        observations.append({"path": name, "sizeBytes": len(raw),
                             "sha256": hashlib.sha256(raw).hexdigest()})
    write_json(CHECKPOINT / "EVIDENCE-TRANSPORT.json", {
        "kind": "ACTUAL_INDEX_BYTE_COMPARISON_NOT_GATE_ACCEPTANCE",
        "result": "PASS", "observations": observations,
    })
    print(f"EVIDENCE_INDEX_BYTES=PASS observations={len(observations)}")
    return 0


if __name__ == "__main__":
    use_utf8_stdout()
    raise SystemExit(main())
