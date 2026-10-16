"""Require staged byte identity for every copied observation before publication."""

import hashlib
import json
import subprocess
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
paths = sorted((CHECKPOINT / "attempts").glob("*.json"))
paths += [CHECKPOINT / name for name in ("DESKTOP-LIVE.json", "HARDENED-GATEWAY.json")]
observed = []
for path in paths:
    if path.is_symlink() or not path.is_file():
        raise ValueError("missing or redirected actual observation")
    relative = path.relative_to(ROOT).as_posix()
    raw = path.read_bytes()
    exported = subprocess.check_output(["git", "show", ":" + relative], cwd=ROOT)
    if exported != raw:
        raise ValueError("staged evidence bytes differ: " + relative)
    observed.append({"path": relative, "sizeBytes": len(raw),
                     "sha256": hashlib.sha256(raw).hexdigest()})
print(json.dumps({"result": "PASS", "observations": observed}))
