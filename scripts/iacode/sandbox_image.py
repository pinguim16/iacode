#!/usr/bin/env python3
"""Build the sandbox image profiles, addressed by the content of their inputs.

`LSN-0036`: a check that ran inside an image built from older sources measured the image. The
sandbox image is named by the digest of its inputs (`iacode_sandbox.image`), so this script's job is
small and exact: for every image profile in the canonical policy, compute the fingerprint of the
inputs in front of it, and build the image under that tag unless an image with that tag and that
fingerprint label already exists. A changed input is a new tag, and a new tag is a new build.

    python scripts/iacode/sandbox_image.py            build what is missing, report every profile
    python scripts/iacode/sandbox_image.py --check    build nothing; fail when an image is missing

Exit ``0`` means every profile's image exists for the current inputs.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPOSITORY_ROOT / "services" / "sandbox" / "src"))

from compose import log, main_guard, require_docker
from iacode_sandbox.image import (
    FINGERPRINT_LABEL,
    image_reference,
    input_fingerprint,
)

POLICY = REPOSITORY_ROOT / ".iacode" / "policies" / "sandbox-policy.json"


def profiles() -> list[dict[str, str]]:
    document = json.loads(POLICY.read_text(encoding="utf-8"))
    return list(document.get("imageProfiles") or [])


def label_of(reference: str) -> str | None:
    completed = subprocess.run(
        ["docker", "image", "inspect", "--format",
         "{{index .Config.Labels \"" + FINGERPRINT_LABEL + "\"}}", reference],
        text=True, encoding="utf-8", errors="replace", capture_output=True, check=False)
    return completed.stdout.strip() if completed.returncode == 0 else None


def ensure(profile: dict[str, str], *, build: bool) -> tuple[str, str]:
    """``(reference, outcome)`` for one profile, building it when allowed and needed."""
    fingerprint = input_fingerprint(REPOSITORY_ROOT, profile["context"])
    reference = image_reference(profile["repository"], fingerprint)
    if label_of(reference) == fingerprint:
        return reference, "PRESENT"
    if not build:
        return reference, "MISSING"
    dockerfile = REPOSITORY_ROOT / profile["context"] / "Dockerfile"
    completed = subprocess.run(
        ["docker", "build", "--file", str(dockerfile), "--label",
         f"{FINGERPRINT_LABEL}={fingerprint}", "--tag", reference, str(REPOSITORY_ROOT)],
        cwd=str(REPOSITORY_ROOT), text=True, encoding="utf-8", errors="replace",
        capture_output=True, check=False)
    if completed.returncode != 0:
        log(completed.stdout[-2000:] + completed.stderr[-2000:])
        return reference, "BUILD_FAILED"
    return reference, ("BUILT" if label_of(reference) == fingerprint else "BUILD_FAILED")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true", help="build nothing; report and fail")
    arguments = parser.parse_args()
    require_docker()
    failures = 0
    for profile in profiles():
        reference, outcome = ensure(profile, build=not arguments.check)
        log(f"SANDBOX_IMAGE {profile['name']} {reference} {outcome}")
        failures += outcome not in ("PRESENT", "BUILT")
    log(f"SANDBOX_IMAGES={'PASS' if not failures else 'FAIL'}")
    return 1 if failures else 0


if __name__ == "__main__":
    main_guard(main)
