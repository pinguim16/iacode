#!/usr/bin/env python3
"""Mandatory gate: the Sandbox suite, against the real container engine.

Runs inside the sandbox service's image, which carries the container client and the package, with
the engine's socket mounted exactly as the stack mounts it — and with nothing else of the stack: no
database, no bucket, no Temporal. The suite's store and artifact sink are in memory; its containers
are real, because isolation, limits and process control cannot be asserted against a double.

Two builds come first, in order. The service image, because a gate that runs inside an image it did
not build measures the past (`LSN-0036`). Then the sandbox image profiles, addressed by the content
of their inputs, because the suite creates sandboxes from exactly the image the current inputs
describe and refuses any other.

The cases marked ``integration`` need the stack's database and bucket; they are deselected here and
run in the verification's ``sandbox-integration`` stage, against the running stack.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from compose import REPOSITORY_ROOT, build_service, compose, log, main_guard


def main() -> int:
    build_service("sandbox")
    images = subprocess.run([sys.executable, str(REPOSITORY_ROOT / "scripts" / "iacode" /
                                                 "sandbox_image.py")], check=False)
    if images.returncode != 0:
        log("SANDBOX_TESTS=FAIL (the sandbox image could not be built)")
        return images.returncode
    result = compose(
        "run", "--rm", "--no-deps", "--entrypoint", "", "sandbox",
        "python", "-m", "pytest", "/app/sandbox_tests", "-m", "not integration",
        "-p", "no:cacheprovider", "--no-header",
        capture=False)
    log(f"SANDBOX_TESTS={'PASS' if result.ok else 'FAIL'}")
    return result.exit_code


if __name__ == "__main__":
    main_guard(main)
