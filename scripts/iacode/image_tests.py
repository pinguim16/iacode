#!/usr/bin/env python3
"""Run every counted Python suite that lives inside an image, in one execution.

Four of the suites the canonical registry counts need an image's dependencies: `apps/api/tests`,
`services/model-gateway/tests` and `services/agent-runtime/tests` run in the API image, and
`services/sandbox/tests` runs in the sandbox service's image, with the container engine's socket.
The mandatory gates run them separately because a gate measures one thing. The delivery evidence
needs the other shape: the number of cases that actually executed, compared with the denominator
the registry derives. Two recorded runs cannot be added up without double counting the categories
they are filed under, so this entry point makes them one recorded execution with one number: it
runs both images' suites and reports each count and their sum.

It builds what it runs first, for the reason `scripts/iacode/gates/api_tests.py` does: a run inside
an image nobody rebuilt measures whatever that image happens to contain. For the sandbox suite
that is two images — the service's, and the sandbox image profile its cases create containers from.

    python scripts/iacode/image_tests.py             # unit and integration
    python scripts/iacode/image_tests.py --no-deps   # only what needs no running stack
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from compose import REPOSITORY_ROOT, build_service, compose, log, main_guard

#: Where each counted suite lives inside the API image. The gateway and agent runtime suites are
#: copied to paths of their own rather than under `tests`, so a gate can address one without
#: the others.
SUITE_PATHS = ("tests", "/app/gateway_tests", "/app/agent_runtime_tests")

#: Where the sandbox suite lives inside the sandbox service's image.
SANDBOX_SUITE_PATH = "/app/sandbox_tests"


def passed(output: str) -> int:
    """The number of passing cases pytest reported on its summary line, or 0."""
    found = re.findall(r"(\d+) passed", output)
    return int(found[-1]) if found else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--no-deps", action="store_true",
                        help="do not start the stack; the integration tests then skip themselves")
    args = parser.parse_args()
    build_service("api")
    build_service("sandbox")
    images = subprocess.run([sys.executable,
                             str(REPOSITORY_ROOT / "scripts" / "iacode" / "sandbox_image.py")],
                            check=False)
    if images.returncode != 0:
        log("IMAGE_TESTS=FAIL (the sandbox image could not be built)")
        return images.returncode

    prefix = ["run", "--rm", "--entrypoint", ""]
    if args.no_deps:
        prefix.insert(2, "--no-deps")
    api = compose(*prefix, "api", "python", "-m", "pytest", *SUITE_PATHS,
                  "-p", "no:cacheprovider", "--no-header", capture=True)
    sys.stdout.write(api.output)
    marker = ["-m", "not integration"] if args.no_deps else []
    sandbox = compose(*prefix, "sandbox", "python", "-m", "pytest", SANDBOX_SUITE_PATH, *marker,
                      "-p", "no:cacheprovider", "--no-header", capture=True)
    sys.stdout.write(sandbox.output)

    ok = api.ok and sandbox.ok
    log(f"IMAGE_TESTS_API passed={passed(api.output)} "
        f"{'PASS' if api.ok else 'FAIL'}")
    log(f"IMAGE_TESTS_SANDBOX passed={passed(sandbox.output)} "
        f"{'PASS' if sandbox.ok else 'FAIL'}")
    log(f"IMAGE_TESTS={'PASS' if ok else 'FAIL'} "
        f"passed={passed(api.output) + passed(sandbox.output)}")
    return 0 if ok else (api.exit_code or sandbox.exit_code or 1)


if __name__ == "__main__":
    main_guard(main)
