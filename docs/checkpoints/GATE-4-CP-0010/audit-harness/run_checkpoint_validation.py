#!/usr/bin/env python3
"""Run checkpoint validation with the mandatory runner preconditions."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "development-ledger"))

from finalize_checkpoint import refresh_declared_hashes  # noqa: E402
from ledger_common import use_utf8_stdout  # noqa: E402
from sync_in_progress_metadata import synchronize  # noqa: E402


def main() -> int:
    use_utf8_stdout()
    synchronize(ROOT, CHECKPOINT)
    refresh_declared_hashes(ROOT, CHECKPOINT)
    completed = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "development-ledger" / "validate_checkpoint.py"),
            "--root",
            str(ROOT),
        ],
        cwd=ROOT,
        check=False,
    )
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
