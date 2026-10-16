#!/usr/bin/env python3
"""Read only the actual installed Code storage-mode switch; never inspect a user storage value."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "scripts/iacode"))

from native_editor import cli_command, executable  # noqa: E402


def main() -> int:
    entry = cli_command(executable())
    if len(entry) != 2:
        raise RuntimeError("this diagnostic expects the observed installed Windows Code CLI adapter")
    main_file = Path(entry[1]).with_name("main.js")
    data = main_file.read_bytes()
    observed = b"useInMemoryStorage:!!this.environmentService.extensionTestsLocationURI" in data
    print(json.dumps({"kind": "INSTALLED_CODE_STORAGE_MODE_DIAGNOSIS_NOT_RECOVERY_ACCEPTANCE",
                      "extensionTestsPathSelectsInMemoryStorage": observed,
                      "installedMainSha256": hashlib.sha256(data).hexdigest(), "result": "PASS" if observed else "FAIL"}))
    return 0 if observed else 1


if __name__ == "__main__":
    raise SystemExit(main())
