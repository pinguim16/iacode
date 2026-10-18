"""Delegate current in-progress metadata/hash/validation boundaries without stale snapshots."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))


def synchronize(root: Path, checkpoint: Path) -> None:
    from sync_in_progress_metadata import synchronize as canonical_synchronize

    canonical_synchronize(root, checkpoint)


def refresh_declared_hashes(root: Path, checkpoint: Path) -> None:
    from finalize_checkpoint import refresh_declared_hashes as canonical_refresh

    canonical_refresh(root, checkpoint)


def main() -> int:
    from ledger_common import use_utf8_stdout

    use_utf8_stdout()
    synchronize(ROOT, CHECKPOINT)
    refresh_declared_hashes(ROOT, CHECKPOINT)
    return subprocess.run(
        [sys.executable, "scripts/development-ledger/validate_checkpoint.py"],
        cwd=ROOT,
        check=False,
    ).returncode


if __name__ == "__main__":
    raise SystemExit(main())
