#!/usr/bin/env python3
"""Preserve one actual failed owned desktop report byte-exactly; never overwrite an attempt."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
CHECKPOINT = Path(__file__).resolve().parent.parent


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--attempt", type=int, required=True)
    parser.add_argument("--kind", choices=("desktop", "native", "gateway"), default="desktop")
    args = parser.parse_args()
    if not 1 <= args.attempt <= 9999:
        raise ValueError("attempt must be a bounded positive identity")
    sources = {"desktop": "desktop-e2e.json", "native": "native-editor-package.json", "gateway": "hardened-gateway-diagnosis.json"}
    source = ROOT / "var" / sources[args.kind]
    if (ROOT / "var").is_symlink() or source.is_symlink() or not source.is_file():
        raise ValueError("refusing missing or redirected desktop report")
    data = source.read_bytes()
    report = json.loads(data)
    expected = (report.get("scenario") == "desktop-e2e" if args.kind == "desktop" else
                report.get("worker", {}).get("kind") == "ACTUAL_HARDENED_WORKER_GATEWAY_DIAGNOSIS_NOT_TASK_ACCEPTANCE" if args.kind == "gateway" else
                report.get("kind") == "NATIVE_INSTALLATION_AND_TRUST_NOT_LIVE_PROVIDER_ACCEPTANCE")
    if report.get("result") != "FAIL" or not expected:
        raise ValueError("only the actual failed desktop scenario can be archived here")
    prefix = {"desktop": "DESKTOP-LIVE", "native": "NATIVE-INSTALLATION", "gateway": "HARDENED-GATEWAY"}[args.kind]
    target = CHECKPOINT / "attempts" / f"{prefix}-RED-{args.attempt:04d}.json"
    target.parent.mkdir(exist_ok=True)
    if target.exists():
        if target.is_symlink() or target.read_bytes() != data:
            raise ValueError("an archived red attempt is immutable")
    else:
        shutil.copyfile(source, target)
    if target.read_bytes() != data or source.read_bytes() != data:
        raise ValueError("desktop attempt changed during archival")
    print(json.dumps({"result": "PASS", "archive": target.name,
                      "sizeBytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
