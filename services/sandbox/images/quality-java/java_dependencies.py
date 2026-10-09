#!/usr/bin/env python3
"""Refuse dynamic or insecure Java dependency declarations, then resolve offline."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

DYNAMIC = re.compile(r"(?i)(?:latest|release|snapshot|\[[^]]|\([^)]|\+)")
INSECURE_REPOSITORY = re.compile(r"http://(?!localhost|127\.0\.0\.1)")


def main() -> int:
    manifests = [
        path
        for path in (Path("pom.xml"), Path("build.gradle"), Path("build.gradle.kts"))
        if path.is_file()
    ]
    if len(manifests) != 1:
        print("QUALITY_JAVA_DEPENDENCIES=FAIL expected exactly one Java build manifest")
        return 1
    text = manifests[0].read_text(encoding="utf-8")
    if DYNAMIC.search(text) or INSECURE_REPOSITORY.search(text):
        print("QUALITY_JAVA_DEPENDENCIES=FAIL dynamic version or insecure repository")
        return 1
    if manifests[0].name == "pom.xml":
        command = [
            "mvn",
            "--batch-mode",
            "--offline",
            "-Dmaven.repo.local=/opt/iacode/m2",
            "-Djansi.tmpdir=/workspace",
            "dependency:tree",
        ]
    else:
        command = ["gradle", "--offline", "dependencies"]
    result = subprocess.run(command, check=False)
    print(f"QUALITY_JAVA_DEPENDENCIES={'PASS' if result.returncode == 0 else 'FAIL'}")
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
