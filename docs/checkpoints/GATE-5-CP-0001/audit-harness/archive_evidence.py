#!/usr/bin/env python3
"""Archive a checkpoint-owned JSON observation once, without changing its bytes."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parent.parent


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True)
    parser.add_argument("--name", required=True)
    args = parser.parse_args()
    if not re.fullmatch(r"[A-Z0-9][A-Z0-9-]*\.json", args.source) or not re.fullmatch(
            r"[A-Z0-9][A-Z0-9-]*\.json", args.name):
        raise RuntimeError("archive names must be checkpoint-owned JSON basenames")
    source = CHECKPOINT / args.source
    target = CHECKPOINT / "attempts" / args.name
    if (source.is_symlink() or target.exists()
            or not target.resolve().is_relative_to(CHECKPOINT.resolve())):
        raise RuntimeError("refusing an existing or redirected archive target")
    payload = source.read_bytes()
    json.loads(payload)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)
    if target.read_bytes() != payload:
        raise RuntimeError("archive differs from the observed bytes")
    print(json.dumps({"result": "ARCHIVED", "sha256": hashlib.sha256(payload).hexdigest(),
                      "sizeBytes": len(payload), "target": target.relative_to(CHECKPOINT).as_posix()}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
