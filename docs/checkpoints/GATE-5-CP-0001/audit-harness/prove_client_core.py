#!/usr/bin/env python3
"""Execute current client-core decision tests in a pinned, owned, no-network Node container."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))

from ledger_common import canonical_hash_path, use_utf8_stdout, write_json  # noqa: E402

IMAGE = "node:22.23.2-bookworm-slim@sha256:48e4b67d85f87bd551df43704e24d252f56cc5f8e9718841aace50f19948f0f9"
SOURCES = {
    "apps/cli/src/client.cjs": "client.cjs",
    "apps/cli/src/snapshot.cjs": "snapshot.cjs",
    "apps/cli/tests/core.test.cjs": "core.test.cjs",
    "packages/contracts/src/iacode_contracts/desktop_protocol.json": "desktop_protocol.json",
}


def main() -> int:
    use_utf8_stdout()
    report_path = CHECKPOINT / "CLIENT-CORE-UNIT.json"
    if report_path.is_symlink() or report_path.resolve().parent != CHECKPOINT.resolve():
        raise RuntimeError("refusing a redirected client-core report path")
    report_path.unlink(missing_ok=True)
    preimages = {name: canonical_hash_path(ROOT / name) for name in SOURCES}
    with tempfile.TemporaryDirectory(prefix="iacode-g5-core-") as temporary:
        directory = Path(temporary)
        for source, destination in SOURCES.items():
            shutil.copyfile(ROOT / source, directory / destination)
        completed = subprocess.run([
            "docker", "run", "--rm", "--network", "none", "--read-only", "--user", "1000:1000",
            "--cap-drop", "ALL", "--security-opt", "no-new-privileges:true", "--pids-limit", "64",
            "--memory", "256m", "--cpus", "1", "--tmpfs", "/tmp:rw,noexec,nosuid,nodev,size=32m,mode=1777",
            "--volume", f"{directory.resolve()}:/client:ro", "--env", "IACODE_CLIENT_MODULE=/client/client.cjs",
            IMAGE, "node", "--test", "/client/core.test.cjs",
        ], cwd=ROOT, text=True, encoding="utf-8", errors="replace", stdout=subprocess.PIPE,
           stderr=subprocess.STDOUT, check=False, timeout=120)
    report = {"kind": "CLIENT_CORE_UNIT_DECISIONS_NOT_LIVE_RUNTIME_OR_EDITOR_ACCEPTANCE",
              "checkpoint": CHECKPOINT.name, "result": "PASS" if completed.returncode == 0 else "FAIL",
              "exitCode": completed.returncode, "runtimeImage": IMAGE, "sourceHashes": preimages,
              "sourceUnchanged": all(canonical_hash_path(ROOT / name) == digest for name, digest in preimages.items()),
              "temporaryDirectoryRemoved": not directory.exists(), "output": completed.stdout}
    write_json(report_path, report)
    print(completed.stdout)
    print(json.dumps({key: report[key] for key in ("result", "exitCode", "sourceUnchanged", "temporaryDirectoryRemoved")}))
    return completed.returncode if report["sourceUnchanged"] and report["temporaryDirectoryRemoved"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
