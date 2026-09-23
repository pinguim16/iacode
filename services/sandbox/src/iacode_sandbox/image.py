"""The sandbox image an agent runs in, addressed by the content that built it.

`LSN-0036` records the failure this module exists to prevent: a test that ran inside an image built
from older sources measured the image, not the source. A sandbox image is worse — a stale one would
run agents with yesterday's helper, yesterday's path resolver and yesterday's toolchain while every
check reported today's code.

So the image is never referred to by a mutable name. Its inputs — the profile's Dockerfile and
files, and the helper modules the image copies — are hashed, and the tag **is** the hash:
``iacode/sandbox-iacode-dev:<first sixteen hex digits>``. Changing any input changes the tag, and a
tag that does not exist is refused rather than substituted, so the only way to run a sandbox is from
an image built from exactly the inputs in front of the controller. The digest is also stamped on the
image as a label, and the controller checks the label, not only the name.

Standard library only: the verification script on the host computes the same fingerprint.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

__all__ = [
    "FINGERPRINT_LABEL",
    "HELPER_MODULES",
    "image_inputs",
    "image_reference",
    "input_fingerprint",
]

#: The label every sandbox image carries with the full fingerprint of its inputs.
FINGERPRINT_LABEL = "org.iacode.sandbox.fingerprint"

#: The modules the image copies to /opt/iacode, relative to the repository root. The path resolver
#: and the patch applier run inside the sandbox from these copies, so they are image inputs.
HELPER_MODULES = (
    "services/sandbox/src/iacode_sandbox/helper.py",
    "services/sandbox/src/iacode_sandbox/paths.py",
    "services/sandbox/src/iacode_sandbox/patching.py",
)


def image_inputs(root: Path, context: str) -> list[str]:
    """Every repository-relative file that decides what the image contains, sorted."""
    directory = root / context
    if not directory.is_dir():
        raise FileNotFoundError(f"the image context {context!r} does not exist under {root}")
    files = sorted(str(path.relative_to(root)).replace("\\", "/")
                   for path in directory.rglob("*")
                   if path.is_file() and "__pycache__" not in path.parts)
    return sorted(set(files) | set(HELPER_MODULES))


def input_fingerprint(root: Path, context: str) -> str:
    """SHA-256 over every input's path and LF-normalised content."""
    digest = hashlib.sha256()
    for relative in image_inputs(root, context):
        content = (root / relative).read_bytes().replace(b"\r\n", b"\n")
        digest.update(relative.encode("utf-8") + b"\0")
        digest.update(hashlib.sha256(content).hexdigest().encode("ascii") + b"\n")
    return digest.hexdigest()


def image_reference(repository: str, fingerprint: str) -> str:
    """The content-addressed tag of the image built from inputs with this fingerprint."""
    return f"{repository}:{fingerprint[:16]}"
