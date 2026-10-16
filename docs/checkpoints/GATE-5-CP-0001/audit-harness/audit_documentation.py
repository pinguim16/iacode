"""Execute the canonical mirror's relative-link rule against the actual repository documents."""

import json
import re
import subprocess
import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))
from ledger_common import scope_fingerprint, utc_now, write_json

listing = subprocess.check_output(["git", "ls-files", "--cached", "--others", "--exclude-standard"],
                                  cwd=ROOT).decode("utf-8")
missing = []
links = 0
documents = 0
for relative in sorted(set(listing.splitlines())):
    path = ROOT / relative
    if not relative.endswith(".md") or not path.is_file():
        continue
    documents += 1
    for target in re.findall(r"\]\(([^)#:]+)\)", path.read_text(encoding="utf-8", errors="ignore")):
        if target.startswith(("http://", "https://", "mailto:")):
            continue
        links += 1
        if not (path.parent / target).exists():
            missing.append(relative + " -> " + target)
report = {"kind": "ACTUAL_RELATIVE_DOCUMENTATION_LINK_CHECK", "generatedAt": utc_now(),
          "scopeFingerprint": scope_fingerprint(ROOT), "documents": documents, "relativeLinks": links,
          "missing": missing, "result": "FAIL" if missing else "PASS"}
write_json(CHECKPOINT / "DOCUMENTATION-LINKS.json", report)
print(json.dumps(report))
raise SystemExit(1 if missing else 0)
