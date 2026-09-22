#!/usr/bin/env python3
"""Mandatory gate: what the infrastructure declares.

The half of the infrastructure suite that needs nothing running — pinned images, loopback-only
ports, health conditions instead of sleeps, no credential in a committed file. The tests that
exercise the live stack are part of the verification command, not of this gate, for the same reason
the backend integration tests are: a mandatory gate must be runnable.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from compose import REPOSITORY_ROOT, log, main_guard


def main() -> int:
    completed = subprocess.run(
        [sys.executable, "-m", "unittest",
         "test_compose_definition", "-v"],
        cwd=str(REPOSITORY_ROOT / "infra" / "tests"), text=True, check=False)
    log(f"INFRA_DEFINITION={'PASS' if completed.returncode == 0 else 'FAIL'}")
    return completed.returncode


if __name__ == "__main__":
    main_guard(main)
