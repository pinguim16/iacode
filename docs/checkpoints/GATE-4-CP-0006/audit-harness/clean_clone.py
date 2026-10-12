#!/usr/bin/env python3
"""Bind the established clean-clone verifier to the corrected sealed Gate 4 subject."""

from __future__ import annotations

import importlib.util
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
SOURCE = (
    ROOT
    / "docs"
    / "checkpoints"
    / "GATE-4-CP-0002"
    / "audit-harness"
    / "clean_clone.py"
)


def main() -> int:
    specification = importlib.util.spec_from_file_location("gate4_clean_clone_base", SOURCE)
    if specification is None or specification.loader is None:
        raise RuntimeError("the established Gate 4 clean-clone harness could not be loaded")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    module.CHECKPOINT = CHECKPOINT
    module.ROOT = ROOT
    module.SUBJECT = "GATE-4-CP-0005"
    module.TAG = "iacode-checkpoints/GATE-4-CP-0005"
    module.COMMIT = "c631270e49c095a9777825c0bc18818694c07ffb"
    return int(module.main())


if __name__ == "__main__":
    raise SystemExit(main())
