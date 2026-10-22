"""Read only the private builder history; preserve safe metadata before interpretation."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

from owned_docker_scope import child_environment

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))
from ledger_common import find_secrets, load_json, utc_now, write_json


def main():
    environment = child_environment()
    scope = load_json(CHECKPOINT / "OWNED-DOCKER-SCOPE.json")
    folder = CHECKPOINT / "resource-observations/build-history"
    folder.mkdir(parents=True, exist_ok=True)
    index = len(list(folder.glob("run-*"))) + 1
    output = folder / f"run-{index:04d}"
    output.mkdir()
    observations = []

    def capture(arguments, name):
        result = subprocess.run(["docker", "buildx", *arguments], cwd=ROOT, env=environment,
                                capture_output=True, timeout=60, check=False)
        row = {"arguments": ["docker", "buildx", *arguments], "exitCode": result.returncode, "streams": {}}
        safe_stdout = None
        for label, raw in (("stdout", result.stdout), ("stderr", result.stderr)):
            fact = {"sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw), "refused": True, "path": None}
            try:
                text = raw.decode("utf-8", errors="strict")
                if len(raw) <= 8 * 1024 * 1024 and not find_secrets(text):
                    path = output / (name + "." + label + ".json")
                    with path.open("xb") as stream:
                        stream.write(raw)
                    fact.update(refused=False, path=path.relative_to(CHECKPOINT).as_posix())
                    if label == "stdout":
                        safe_stdout = raw
            except Exception:
                pass  # Neutral refusal remains observable; no raw unsafe publication.
            row["streams"][label] = fact
        observations.append(row)
        if result.returncode or safe_stdout is None:
            raise ValueError("HISTORY_OBSERVATION_REFUSED")
        try:
            return json.loads(safe_stdout)
        except json.JSONDecodeError as error:
            if error.msg != "Extra data":
                raise
            # This installed Buildx emits complete JSON records, one per line. Require
            # every nonempty line to decode; never salvage a prefix or omit a bad row.
            return [json.loads(line) for line in safe_stdout.splitlines() if line.strip()]

    result = "FAIL"
    summary = []
    try:
        rows = capture(["history", "ls", "--no-trunc", "--format", "json"], "list")
        if type(rows) is dict:
            rows = [rows]
        if type(rows) is not list or any(type(row) is not dict for row in rows):
            raise ValueError("EXPECTED_HISTORY_ARRAY")
        # Capture every record, including failed attempts. A top-two diagnostic is
        # insufficient to account for all owned outputs before exact final cleanup.
        if len(rows) > 10000:
            raise ValueError("HISTORY_RECORD_LIMIT")
        for row in rows:
            reference = row.get("ref", row.get("ID"))
            prefix = scope["builder"] + "/" + scope["builder"] + "0/"
            if type(reference) is not str:
                raise ValueError("HISTORY_ID_SHAPE")
            identifier = reference.removeprefix(prefix)
            if re.fullmatch(r"[a-z0-9]{20,64}", identifier) is None:
                raise ValueError("HISTORY_ID_SHAPE")
            document = capture(["history", "inspect", "--format", "json", identifier], "inspect-" + identifier)
            if type(document) is not dict:
                raise ValueError("EXPECTED_TYPED_HISTORY_INSPECT")
            summary.append({"id": identifier, "keys": sorted(document), "status": document.get("Status", document.get("status"))})
        result = "CAPTURED_NOT_OWNERSHIP_CLAIM_OR_ACCEPTANCE"
    finally:
        write_json(output / "RECEIPT.json", {"observedAt": utc_now(), "result": result,
                                            "builder": scope["builder"], "observations": observations,
                                            "inspectSummary": summary})
    print(json.dumps({"result": result, "output": output.relative_to(ROOT).as_posix(), "inspectSummary": summary}))
    return 0 if result != "FAIL" else 1


if __name__ == "__main__":
    from ledger_common import use_utf8_stdout
    use_utf8_stdout()
    raise SystemExit(main())
