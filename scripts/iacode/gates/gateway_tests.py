#!/usr/bin/env python3
"""Mandatory gate: the Model Gateway suite.

Runs inside the API image, where the gateway package is installed, and with no dependency on a
running stack: every provider in this suite is a deterministic double, so the gate is executable
whenever Docker is. The live provider checks are a separate stage of the verification command,
because they need a credential and they spend tokens — a mandatory gate that needed either would be
a gate that gets skipped.
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
        "python", "-m", "pytest", "/app/gateway_tests", "-p", "no:cacheprovider", "--no-header",
        capture=False)
    log(f"GATEWAY_TESTS={'PASS' if result.ok else 'FAIL'}")
    return result.exit_code


if __name__ == "__main__":
    main_guard(main)
