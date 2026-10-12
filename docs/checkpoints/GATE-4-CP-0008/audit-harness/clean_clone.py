#!/usr/bin/env python3
"""Run the established transport-clone audit against sealed CP0007."""

from __future__ import annotations

import importlib.util
from pathlib import Path


CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
SOURCE = ROOT / "docs" / "checkpoints" / "GATE-4-CP-0002" / "audit-harness" / "clean_clone.py"


def main() -> int:
    specification = importlib.util.spec_from_file_location("gate4_cp0008_clean_clone", SOURCE)
    if specification is None or specification.loader is None:
        raise RuntimeError("the established clean-clone harness could not be loaded")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    module.CHECKPOINT = CHECKPOINT
    module.ROOT = ROOT
    module.SUBJECT = "GATE-4-CP-0007"
    module.TAG = "iacode-checkpoints/GATE-4-CP-0007"
    module.COMMIT = "e21d30fde473f302d0f8f60b59acf008fa52e250"
    return int(module.main())


if __name__ == "__main__":
    raise SystemExit(main())

