"""Refresh only declared mismatched index entries, never normalize or edit originals."""

import hashlib
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(
    0, str(Path(__file__).resolve().parents[1].parents[2] / "scripts/development-ledger")
)
sys.path.insert(0, str(Path(__file__).resolve().parents[1].parents[2] / "scripts/iacode"))
from client_checks import _safe_stream
from ledger_common import load_json, utc_now, write_json

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]


def main():
    output = CHECKPOINT / "byte-transport-attempts/index-refresh-0001.json"
    if output.exists():
        raise ValueError("Preserve prior index refresh observation")
    proof = load_json(CHECKPOINT / "byte-transport-attempts/index-0003.json")
    files = load_json(CHECKPOINT / "FILES.json")
    declared = {row["path"] for group in ("filesCreated", "filesModified") for row in files[group]}
    targets = []
    for row in proof["mismatches"]:
        name = row["path"]
        path = ROOT / name
        if (
            name not in declared
            or not path.resolve().is_relative_to(ROOT.resolve())
            or path.is_symlink()
            or path.is_junction()
        ):
            raise ValueError("Unowned or redirected index refresh target")
        original = path.read_bytes()
        if (
            len(original) != row["actualBytes"]
            or hashlib.sha256(original).hexdigest() != row["actualSha256"]
        ):
            raise ValueError("Original observation changed; do not restage blindly")
        targets.append(name)
    if not targets:
        raise ValueError("No actual mismatched owned entries")
    payload = b"".join(name.encode("utf-8") + b"\0" for name in sorted(targets))
    arguments = [
        "git",
        "--literal-pathspecs",
        "add",
        "--renormalize",
        "--pathspec-from-file=-",
        "--pathspec-file-nul",
    ]
    result = subprocess.run(
        arguments, cwd=ROOT, input=payload, capture_output=True, timeout=60, check=False
    )
    report = {
        "observedAt": utc_now(),
        "arguments": arguments,
        "targetPaths": sorted(targets),
        "inputSha256": hashlib.sha256(payload).hexdigest(),
        "exitCode": result.returncode,
        "streams": {
            label: _safe_stream(raw)
            for label, raw in (("stdout", result.stdout), ("stderr", result.stderr))
        },
        "originalFilesEdited": False,
        "newCommitTagPush": False,
        "result": "FAIL",
    }
    write_json(output, report)
    unchanged = all(
        hashlib.sha256((ROOT / row["path"]).read_bytes()).hexdigest() == row["actualSha256"]
        for row in proof["mismatches"]
    )
    report["originalsUnchanged"] = unchanged
    if (
        result.returncode == 0
        and unchanged
        and not any(row["refusal"] for row in report["streams"].values())
    ):
        report["result"] = "PASS"
    write_json(output, report)
    print(
        json.dumps(
            {
                "result": report["result"],
                "exactIndexTargets": len(targets),
                "originalsUnchanged": unchanged,
                "newCommitTagPush": False,
            }
        )
    )
    return 0 if report["result"] == "PASS" else 1


if __name__ == "__main__":
    from ledger_common import use_utf8_stdout

    use_utf8_stdout()
    raise SystemExit(main())
