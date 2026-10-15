#!/usr/bin/env python3
"""Prove a canonical text marker stays detectable after its declared JSON transport."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "packages/common/src"))
from iacode_common.secret_scanning import find_secret_kinds


def main() -> int:
    marker = "gh" + "p_" + "k" * 20
    raw = "\n" + marker
    nested = json.dumps({"ordinary": raw})
    nested_detected = []
    for _layer in range(5):
        nested_detected.append(bool(find_secret_kinds(nested)))
        nested = json.dumps({"output": json.dumps(nested)})
    checks = {
        "nestedJsonTransportsDetected": all(nested_detected),
        "mixedLogTransportDetected": bool(find_secret_kinds("pytest passed\n" + nested)),
        "plainControlDetected": bool(find_secret_kinds(raw)),
        "jsonNewlineDetected": bool(find_secret_kinds(json.dumps({"ordinary": raw}))),
        "jsonUnicodeDetected": bool(find_secret_kinds(json.dumps({"ordinary": marker}).replace(
            "g", "\\u0067", 1))),
    }
    print(json.dumps(checks))
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
