"""Local edge-case preflight, not final Red Team or independent acceptance."""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(
    0, str(Path(__file__).resolve().parents[1].parents[2] / "scripts/development-ledger")
)
from audit_runner_bridge import regular
from ledger_common import utc_now, write_json

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]


def main():
    with tempfile.TemporaryDirectory(prefix="iacode-m2cp3-path-bounds-") as temporary:
        owner = Path(temporary).absolute()
        root = owner / "frozen"
        root.mkdir()
        inside = root / "inside.bin"
        outside = owner / "neighbor.bin"
        inside.write_bytes(b"OWNED_NULL_CONTROL")
        outside.write_bytes(b"OWNED_ADVERSE_CONTROL")
        controls = []
        for name, path, expected in (
            ("inside-null", inside, True),
            ("outside-absolute", outside, False),
            ("parent-relative", root / ".." / outside.name, False),
        ):
            accepted = True
            try:
                regular(path, root)
            except ValueError:
                accepted = False
            controls.append(
                {
                    "name": name,
                    "expectedAccepted": expected,
                    "actualAccepted": accepted,
                    "result": "PASS" if accepted == expected else "FAIL",
                }
            )
    report = {
        "observedAt": utc_now(),
        "kind": "LOCAL_PATH_EDGE_PREFLIGHT_NOT_FINAL_RED_TEAM",
        "controls": controls,
        "temporaryRootRemoved": not owner.exists(),
        "result": "PASS" if all(row["result"] == "PASS" for row in controls) else "FAIL",
    }
    directory = CHECKPOINT / "causal-attempts/bridge-path-bounds"
    directory.mkdir(parents=True, exist_ok=True)
    index = len(list(directory.glob("run-*.json"))) + 1
    write_json(directory / f"run-{index:04d}.json", report)
    print(json.dumps(report))
    return int(report["result"] != "PASS")


if __name__ == "__main__":
    from ledger_common import use_utf8_stdout

    use_utf8_stdout()
    raise SystemExit(main())
