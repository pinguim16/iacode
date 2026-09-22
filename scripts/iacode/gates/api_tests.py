#!/usr/bin/env python3
"""Mandatory gate: the Foundation backend unit suite.

Runs inside the API image, with no dependency on a running stack, so the gate is executable
whenever Docker is. The integration tests are deliberately excluded here and run as part of the
verification command instead: they need the whole stack up, and a mandatory gate that cannot run
without nine healthy containers is a gate that gets skipped.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from compose import build_service, compose, log, main_guard


def main() -> int:
    # Build first: a gate that runs inside an image and does not build it measures whatever
    # the image happens to contain, which is a measurement of the past.
    build_service("api")
    result = compose(
        "run", "--rm", "--no-deps", "--entrypoint", "", "api",
        "python", "-m", "pytest", "tests/unit", "-p", "no:cacheprovider", "--no-header",
        capture=False)
    log(f"API_UNIT_TESTS={'PASS' if result.ok else 'FAIL'}")
    return result.exit_code


if __name__ == "__main__":
    main_guard(main)
