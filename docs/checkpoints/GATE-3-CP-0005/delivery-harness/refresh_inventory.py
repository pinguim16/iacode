#!/usr/bin/env python3
"""Refresh content hashes for the checkpoint's already-declared inventory."""

from __future__ import annotations

import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]

sys.path.insert(0, str(ROOT / "scripts" / "development-ledger"))

from finalize_checkpoint import refresh_declared_hashes  # noqa: E402


def main() -> int:
    refresh_declared_hashes(ROOT, CHECKPOINT)
    print("inventory hashes refreshed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
