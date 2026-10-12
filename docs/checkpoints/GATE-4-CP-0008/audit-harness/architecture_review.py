#!/usr/bin/env python3
"""Run the established independent architecture review over CP0007 content."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path


CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
SUBJECT_COMMIT = "e21d30fde473f302d0f8f60b59acf008fa52e250"
SOURCE = ROOT / "docs" / "checkpoints" / "GATE-4-CP-0006" / "audit-harness" / "architecture_review.py"


def main() -> int:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--report", type=Path, required=True)
    arguments, _ = parser.parse_known_args()
    specification = importlib.util.spec_from_file_location("gate4_cp0008_architecture", SOURCE)
    if specification is None or specification.loader is None:
        raise RuntimeError("the established architecture review could not be loaded")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    module.CHECKPOINT = CHECKPOINT
    module.ROOT = ROOT
    module.SUBJECT = SUBJECT_COMMIT
    result = int(module.main())
    report = json.loads(arguments.report.resolve().read_text(encoding="utf-8"))
    report.update({
        "checkpoint": CHECKPOINT.name,
        "subjectCheckpoint": "GATE-4-CP-0007",
        "subjectCommit": SUBJECT_COMMIT,
    })
    arguments.report.resolve().write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8", newline="\n",
    )
    return result


if __name__ == "__main__":
    raise SystemExit(main())
