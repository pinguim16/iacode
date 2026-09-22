#!/usr/bin/env python3
"""Mandatory gate: the Agent Runtime suite.

Runs inside the API image, where the runtime package and the shared schema are installed, and with
no dependency on a running stack: every model in this suite is a deterministic double, there is no
Temporal in it and there is no provider credential. The live agent smokes and the durability
scenario are separate stages of the verification command, because they need a credential, a running
stack and a container restart — and a mandatory gate that needed any of those would be a gate that
gets skipped.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from compose import build_service, compose, log, main_guard


def main() -> int:
    # Build first: a gate that runs inside an image and does not build it measures whatever the
    # image happens to contain, which is a measurement of the past.
    build_service("api")
    result = compose(
        "run", "--rm", "--no-deps", "--entrypoint", "", "api",
        "python", "-m", "pytest", "/app/agent_runtime_tests", "-p", "no:cacheprovider",
        "--no-header",
        capture=False)
    log(f"AGENT_RUNTIME_TESTS={'PASS' if result.ok else 'FAIL'}")
    return result.exit_code


if __name__ == "__main__":
    main_guard(main)
