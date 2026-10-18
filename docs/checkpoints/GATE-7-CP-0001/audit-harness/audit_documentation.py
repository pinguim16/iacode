"""Execute the canonical mirror relative-link rule on actual tracked/untracked repository docs."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))


def main() -> int:
    from ledger_common import use_utf8_stdout

    use_utf8_stdout()
    from ledger_common import LedgerError, load_json, scope_fingerprint, utc_now, write_json

    if load_json(CHECKPOINT / "STATE.json")["status"] != "IN_PROGRESS":
        raise LedgerError(
            "this report writer is preseal only; use read-only canonical checks later"
        )
    listing = subprocess.check_output(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"], cwd=ROOT
    ).decode("utf-8")
    missing, links, documents = [], 0, 0
    for relative in sorted(set(listing.splitlines())):
        path = ROOT / relative
        if not relative.endswith(".md") or not path.is_file():
            continue
        documents += 1
        text = path.read_text(encoding="utf-8", errors="ignore")
        for target in re.findall(r"\]\(([^)#:]+)\)", text):
            if target.startswith(("http://", "https://", "mailto:")):
                continue
            links += 1
            if not (path.parent / target).exists():
                missing.append(relative + " -> " + target)
    report = {
        "kind": "ACTUAL_RELATIVE_DOCUMENTATION_LINK_CHECK",
        "generatedAt": utc_now(),
        "scopeFingerprint": scope_fingerprint(ROOT),
        "documents": documents,
        "relativeLinks": links,
        "missing": missing,
        "result": "FAIL" if missing else "PASS",
    }
    write_json(CHECKPOINT / "DOCUMENTATION-LINKS.json", report)
    print(json.dumps(report))
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
