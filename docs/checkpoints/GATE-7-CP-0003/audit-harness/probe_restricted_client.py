"""Observe the actual client producer under a temporarily restricted Windows token.

This is an environment/producer diagnostic, not a model turn, broker or milestone audit.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "scripts/iacode"))
from client_checks import ClientCheckError, run_node

ROOT = Path(__file__).resolve().parents[4]


def main() -> int:
    # Only this diagnostic process and its children see these values. No config, ACL or group
    # changes; do not expose the engine over a new transport or substitute another application.
    os.environ["DOCKER_HOST"] = "npipe:////./pipe/dockerDesktopLinuxEngine"
    os.environ["DOCKER_CONFIG"] = str(ROOT / "var/m2-docker-probe-empty")
    os.environ.pop("DOCKER_CONTEXT", None)
    try:
        completed = run_node(guard=True)
    except ClientCheckError as exc:
        print(json.dumps({"kind": "ACTUAL_RESTRICTED_CLIENT_DIAGNOSTIC", **exc.report}))
        return 1
    print(
        json.dumps(
            {
                "kind": "ACTUAL_RESTRICTED_CLIENT_DIAGNOSTIC",
                "result": "PRODUCER_RETURNED",
                "exitCode": completed.returncode,
                "stdout": completed.stdout,
                "stderr": completed.stderr,
            }
        )
    )
    return completed.returncode


if __name__ == "__main__":
    from ledger_common import use_utf8_stdout

    use_utf8_stdout()
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    raise SystemExit(main())
