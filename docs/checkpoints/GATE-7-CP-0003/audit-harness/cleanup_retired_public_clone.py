"""Remove only the assessed clean reconstructible runtime copy; preserve actual removal result."""

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
    output = CHECKPOINT / "RETIRED-PUBLIC-CLONE-CLEANUP.json"
    if output.exists():
        raise ValueError("Prior cleanup observation exists; do not repeat effects")
    original = load_json(CHECKPOINT / "retired-clone-observations/run-0001.json")
    if not original["eligibleForExactOwnerCleanup"]:
        raise ValueError("No verified eligible exact retired target")
    arguments = [
        "powershell",
        "-NoProfile",
        "-File",
        str(Path(__file__).with_name("remove_retired_public_clone.ps1")),
    ]
    code, status, stdout, stderr = None, "COMPLETED", None, None
    try:
        result = subprocess.run(arguments, cwd=ROOT, capture_output=True, timeout=120, check=False)
        code, stdout, stderr = result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired as error:
        status, stdout, stderr = "TIMEOUT", error.stdout, error.stderr
    except OSError:
        status = "LAUNCH_ERROR"
    # Bind actual removal result before later interpretation or another cleanup can fail.
    receipt = {
        "observedAt": utc_now(),
        "arguments": arguments,
        "status": status,
        "exitCode": code,
        "streams": {
            name: _safe_stream(raw) for name, raw in (("stdout", stdout), ("stderr", stderr))
        },
        "target": original["target"],
        "ownershipEvidence": "retired-clone-observations/run-0001.json",
        "reconstruction": (
            "Fresh public clone detached at refs/tags/iacode-checkpoints/"
            "GATE-7-CP-0001 (823cf164c6931dab7f957c92721ded7a916655bd)"
        ),
        "mainRepositoryHistoryChanged": False,
        "dockerResourcesRemoved": False,
        "result": "FAIL",
    }
    write_json(output, receipt)
    receipt["targetAbsent"] = not Path(original["target"]).exists()
    if (
        status == "COMPLETED"
        and code == 0
        and receipt["targetAbsent"]
        and not any(row["refusal"] for row in receipt["streams"].values())
    ):
        receipt["result"] = "PASS"
    write_json(output, receipt)
    print(
        json.dumps(
            {
                "result": receipt["result"],
                "targetAbsent": receipt["targetAbsent"],
                "reconstructibleFromPublicImmutableSubject": True,
                "dockerResourcesRemoved": False,
            }
        )
    )
    return 0 if receipt["result"] == "PASS" else 1


if __name__ == "__main__":
    from ledger_common import use_utf8_stdout

    use_utf8_stdout()
    raise SystemExit(main())
