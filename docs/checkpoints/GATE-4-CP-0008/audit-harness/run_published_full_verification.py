#!/usr/bin/env python3
"""Run the established single-invocation verifier while writing evidence to CP0008."""

from __future__ import annotations

import importlib.util
from pathlib import Path


CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
SOURCE = (
    ROOT
    / "docs"
    / "checkpoints"
    / "GATE-4-CP-0006"
    / "RUN-INDEPENDENT-FULL-VERIFICATION.py"
)


def main() -> int:
    specification = importlib.util.spec_from_file_location(
        "gate4_cp0008_published_verifier", SOURCE
    )
    if specification is None or specification.loader is None:
        raise RuntimeError("the established published verifier could not be loaded")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    module.CHECKPOINT = CHECKPOINT
    module.ROOT = ROOT
    return int(module.main())


if __name__ == "__main__":
    raise SystemExit(main())
