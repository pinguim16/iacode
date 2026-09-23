#!/usr/bin/env python3
"""Copy the verification's generated reports into the checkpoint, bound to their source.

`var/` is ignored by Git, so a report a stage wrote there is not evidence anyone else can read. The
two this delivery relies on are copied into the checkpoint with the path they came from and the
digest of the bytes read, so the copy can be compared with a later run rather than trusted:

- `var/verify-report.json` -> `VERIFICATION-REPORT.json`, the full verification;
- `var/sandbox-tool-result-origin.json` -> `TOOL-RESULT-ORIGIN.json`, the `M1-F-002` stage.

    python collect_reports.py
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "development-ledger"))

from ledger_common import utc_now, write_json  # noqa: E402

REPORTS = (("var/verify-report.json", "VERIFICATION-REPORT.json", "VERIFICATION-REPORT"),
           ("var/sandbox-tool-result-origin.json", "TOOL-RESULT-ORIGIN.json",
            "TOOL-RESULT-ORIGIN"))


def main() -> int:
    for source, target, artifact in REPORTS:
        raw = (ROOT / source).read_bytes()
        document = {"schemaVersion": "1.0.0", "artifact": artifact,
                    "checkpoint": CHECKPOINT.name, "collectedAt": utc_now(), "source": source,
                    "sourceSha256": hashlib.sha256(raw).hexdigest(),
                    "report": json.loads(raw.decode("utf-8"))}
        write_json(CHECKPOINT / target, document)
        result = document["report"].get("result")
        print(f"{target}: {result} from {source}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
