"""Retain safe bounded logs from only the builder's already pinned container ID."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(
    0, str(Path(__file__).resolve().parents[1].parents[2] / "scripts/development-ledger")
)
from ledger_common import find_secrets, load_json, utc_now, write_json

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]


def main():
    scope = load_json(CHECKPOINT / "OWNED-DOCKER-SCOPE.json")
    identifier = scope["builderOwnership"]["id"]
    if identifier in {row["id"] for row in scope["before"]["containers"]}:
        raise ValueError("Only the newly owned builder can be diagnosed")
    command = ["docker", "logs", "--since", "2026-10-21T20:39:00Z", "--tail", "80", identifier]
    result = subprocess.run(command, cwd=ROOT, capture_output=True, timeout=60, check=False)
    directory = CHECKPOINT / "environment-attempts/builder-diagnostics"
    directory.mkdir(parents=True, exist_ok=True)
    index = len(list(directory.glob("run-*.json"))) + 1
    stem = directory / f"run-{index:04d}"
    receipt = {
        "observedAt": utc_now(),
        "kind": "OWNED_BUILDER_DIAGNOSTIC_NOT_ACCEPTANCE",
        "arguments": command,
        "exitCode": result.returncode,
        "streams": {},
    }
    for name, raw in (("stdout", result.stdout), ("stderr", result.stderr)):
        fact = {
            "sha256": hashlib.sha256(raw).hexdigest(),
            "bytes": len(raw),
            "refused": True,
            "path": None,
        }
        try:
            text = raw.decode("utf-8", errors="strict")
            if len(raw) <= 262144 and not find_secrets(text):
                path = stem.with_suffix("." + name + ".log")
                with path.open("xb") as stream:
                    stream.write(raw)
                fact.update(refused=False, path=path.relative_to(ROOT).as_posix())
        except Exception as error:
            fact.update(refused=True, errorType=type(error).__name__)
        receipt["streams"][name] = fact
    write_json(stem.with_suffix(".json"), receipt)
    print(json.dumps(receipt))
    return result.returncode or int(any(row["refused"] for row in receipt["streams"].values()))


if __name__ == "__main__":
    from ledger_common import use_utf8_stdout

    use_utf8_stdout()
    raise SystemExit(main())
