"""Preserve the actual successful hardened transport/provider diagnostic byte-exactly."""

import hashlib
import json
import shutil
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
source = ROOT / "var/hardened-gateway-diagnosis.json"
target = CHECKPOINT / "HARDENED-GATEWAY.json"
if source.is_symlink() or target.is_symlink():
    raise ValueError("redirected diagnostic evidence")
data = source.read_bytes()
report = json.loads(data)
if report.get("result") != "PASS" or report.get("cleanupExitCode") != 0:
    raise ValueError("actual successful diagnostic and cleanup required")
if target.exists() and target.read_bytes() != data:
    raise ValueError("existing diagnostic evidence is immutable")
if not target.exists():
    shutil.copyfile(source, target)
if target.read_bytes() != data:
    raise ValueError("diagnostic archival differs")
print(json.dumps({"result": "PASS", "sizeBytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}))
