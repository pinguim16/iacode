"""Preserve the actual complete desktop acceptance without changing its bytes."""

import hashlib
import json
import shutil
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
source = ROOT / "var/desktop-e2e.json"
target = CHECKPOINT / "DESKTOP-LIVE.json"
if source.is_symlink() or target.is_symlink():
    raise ValueError("redirected acceptance evidence")
data = source.read_bytes()
report = json.loads(data)
if (report.get("result") != "PASS" or not report.get("ownedTemporaryDirectoryRemoved")
        or report.get("taskCancellation", {}).get("phase") != "COMPLETE"
        or not report.get("steps") or any(row["result"] != "PASS" for row in report["steps"])
        or report.get("cleanup", {}).get("remainingContainers") != 0
        or report.get("cleanup", {}).get("remainingVolumes") != 0
        or report.get("sandboxCleanup", {}).get("remainingContainers") != 0
        or report.get("sandboxCleanup", {}).get("remainingNetworks") != 0):
    raise ValueError("actual complete positive acceptance and cleanup required")
if target.exists() and target.read_bytes() != data:
    raise ValueError("existing acceptance evidence is immutable")
if not target.exists():
    shutil.copyfile(source, target)
if target.read_bytes() != data:
    raise ValueError("acceptance archival differs")
print(json.dumps({"result": "PASS", "sizeBytes": len(data),
                  "steps": len(report["steps"]), "sha256": hashlib.sha256(data).hexdigest()}))
