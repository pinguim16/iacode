#!/usr/bin/env python3
"""Preserve the observed first client red report byte-for-byte before another execution."""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parent.parent


def main() -> int:
    source = CHECKPOINT / "CLIENT-CORE-UNIT.json"
    target = CHECKPOINT / "attempts/CLIENT-CORE-RED-0001.json"
    if source.is_symlink() or not target.resolve().is_relative_to(CHECKPOINT.resolve()):
        raise RuntimeError("refusing a redirected evidence path")
    if target.exists():
        raise RuntimeError("the immutable red attempt already exists; do not overwrite it")
    payload = source.read_bytes()
    report = json.loads(payload)
    if report.get("result") != "FAIL" or report.get("exitCode") != 1:
        raise RuntimeError("the source is not the actually observed red attempt")
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)
    if target.read_bytes() != payload:
        raise RuntimeError("red evidence copy is not byte-identical")
    print(json.dumps({"result": "ARCHIVED", "sha256": hashlib.sha256(payload).hexdigest(),
                      "sizeBytes": len(payload), "target": target.relative_to(CHECKPOINT).as_posix()}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
