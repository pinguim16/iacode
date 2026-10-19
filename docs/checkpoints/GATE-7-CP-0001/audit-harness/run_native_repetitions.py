"""Two fresh uninstrumented native runs, fail-stop, retaining originals before interpretation."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import uuid
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))


def main() -> int:
    from ledger_common import find_secrets, scope_fingerprint, use_utf8_stdout, write_json

    use_utf8_stdout()
    before = scope_fingerprint(ROOT)
    nonce = uuid.uuid4().hex[:12]
    rows = []
    code = 1
    for ordinal in (1, 2):
        report = ROOT / "var" / f"native-local-{nonce}-{ordinal}.json"
        if report.exists() or report.is_symlink() or report.parent.is_junction():
            raise ValueError("fresh owned regular report destination required")
        command = [sys.executable, "scripts/iacode/native_editor.py", "--report", str(report)]
        process = subprocess.run(
            command, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False
        )
        raw = report.read_bytes() if report.is_file() else None
        originals = {}
        for suffix, data in (("log", process.stdout), ("json", raw)):
            if data is None:
                continue
            if find_secrets(data.decode("utf-8", errors="strict")):
                raise ValueError("unsafe original refused before export")
            target = CHECKPOINT / "attempts" / f"NATIVE-LOCAL-{nonce}-{ordinal}.{suffix}"
            with target.open("xb") as stream:
                stream.write(data)
            if target.read_bytes() != data:
                raise ValueError("original native byte equality failed")
            originals[suffix] = {
                "path": target.relative_to(CHECKPOINT).as_posix(),
                "bytes": len(data),
                "sha256": hashlib.sha256(data).hexdigest(),
            }
        # Only interpret the now durable original; a missing or failed producer remains red.
        document = json.loads(raw) if raw is not None else {}
        passed = (
            process.returncode == 0
            and document.get("result") == "PASS"
            and document.get("ownedTemporaryDirectoryRemoved") is True
            and len(document.get("runs", [])) == 2
        )
        rows.append(
            {
                "ordinal": ordinal,
                "exitCode": process.returncode,
                "result": "PASS" if passed else "FAIL",
                "originals": originals,
            }
        )
        if not passed:
            code = process.returncode or 1
            break
        code = 0
    unchanged = scope_fingerprint(ROOT) == before
    if not unchanged:
        code = 1
    write_json(
        CHECKPOINT / "attempts" / f"NATIVE-LOCAL-{nonce}-MANIFEST.json",
        {
            "kind": "LOCAL_NATIVE_PROOF_NOT_WHOLE_GATE_ACCEPTANCE",
            "sourceFingerprint": before,
            "sourceUnchanged": unchanged,
            "plannedRuns": 2,
            "runs": rows,
            "result": "PASS" if code == 0 and len(rows) == 2 else "FAIL",
            "gateVerdictIssued": False,
            "independentValidation": False,
        },
    )
    print(json.dumps({"runs": rows, "sourceUnchanged": unchanged, "actualExitCode": code}))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
