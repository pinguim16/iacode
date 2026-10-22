"""Compare actual staged/copied observation bytes without changing index or policy."""

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(
    0, str(Path(__file__).resolve().parents[1].parents[2] / "scripts/development-ledger")
)
from ledger_common import utc_now, write_json
from secret_scan import _read_blobs
from sync_in_progress_metadata import synchronize

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]


def main():
    synchronize(ROOT, CHECKPOINT)
    raw = subprocess.run(
        ["git", "ls-files", "--stage", "-z"], cwd=ROOT, capture_output=True, check=True
    ).stdout
    entries = {}
    for row in raw.split(b"\0"):
        if not row:
            continue
        metadata, path = row.split(b"\t", 1)
        name = path.decode("utf-8")
        if (
            name.startswith("docs/checkpoints/GATE-7-CP-0002/")
            or name.startswith("docs/audits/M2-ENTRY-BLOCKED-2026-10-21/")
            or (
                name.startswith("docs/checkpoints/GATE-7-CP-0003/")
                and name.endswith((".log", ".raw"))
            )
        ):
            entries[name] = metadata.split()[1].decode()
    blobs = _read_blobs(ROOT, sorted(set(entries.values())))
    mismatches, matched = [], []
    for path, oid in sorted(entries.items()):
        actual, staged = (ROOT / path).read_bytes(), blobs[oid]
        observation = {
            "path": path,
            "actualBytes": len(actual),
            "stagedBytes": len(staged),
            "actualSha256": hashlib.sha256(actual).hexdigest(),
            "stagedSha256": hashlib.sha256(staged).hexdigest(),
        }
        (matched if actual == staged else mismatches).append(observation)
    receipt = {
        "observedAt": utc_now(),
        "kind": "ACTUAL_INDEX_BYTE_COMPARISON_NOT_PUBLICATION",
        "result": "FAIL" if mismatches else "PASS",
        "compared": len(entries),
        "matching": len(matched),
        "matchingNullSample": matched[:1],
        "mismatches": mismatches,
        "indexChanged": False,
        "detectorChanged": False,
        "mainHeadUnchanged": True,
    }
    folder = CHECKPOINT / "byte-transport-attempts"
    folder.mkdir(exist_ok=True)
    index = (
        max(
            (
                int(match[1])
                for path in folder.glob("index-*.json")
                if (match := re.fullmatch(r"index-(\d{4})\.json", path.name))
            ),
            default=0,
        )
        + 1
    )
    write_json(folder / f"index-{index:04d}.json", receipt)
    print(
        json.dumps(
            {
                "result": receipt["result"],
                "compared": len(entries),
                "mismatches": len(mismatches),
                "matchingNulls": len(matched),
            }
        )
    )
    return 1 if mismatches else 0


if __name__ == "__main__":
    from ledger_common import use_utf8_stdout

    use_utf8_stdout()
    raise SystemExit(main())
