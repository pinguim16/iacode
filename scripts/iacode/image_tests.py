#!/usr/bin/env python3
"""Run every counted Python suite that lives inside the API image, in one execution.

Two of the four suites the canonical registry counts — `apps/api/tests` and
`services/model-gateway/tests` — need the image's dependencies, and the mandatory gates run them
separately because a gate measures one thing. The delivery evidence needs the other shape: the
number of cases that actually executed, compared with the denominator the registry derives. Two
recorded runs cannot be added up without double counting the categories they are filed under, so
this entry point makes them one physical execution with one number.

It builds the image first, for the reason `scripts/iacode/gates/api_tests.py` does: a run inside an
image nobody rebuilt measures whatever that image happens to contain.

    python scripts/iacode/image_tests.py             # unit and integration
    python scripts/iacode/image_tests.py --no-deps   # only what needs no running stack
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from compose import build_service, compose, log, main_guard

#: Where each counted suite lives inside the image. The gateway suite is copied to its own path
#: rather than installed under `tests`, so that a gate can address one without the other.
SUITE_PATHS = ("tests", "/app/gateway_tests")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--no-deps", action="store_true",
                        help="do not start the stack; the integration tests then skip themselves")
    args = parser.parse_args()

    build_service("api")
    prefix = ["run", "--rm", "--entrypoint", ""]
    if args.no_deps:
        prefix.insert(2, "--no-deps")
    result = compose(*prefix, "api", "python", "-m", "pytest", *SUITE_PATHS,
                     "-p", "no:cacheprovider", "--no-header", capture=False)
    log(f"IMAGE_TESTS={'PASS' if result.ok else 'FAIL'}")
    return result.exit_code


if __name__ == "__main__":
    main_guard(main)
