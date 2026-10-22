#!/usr/bin/env python3
"""Mandatory build, deterministic packaging and complete client decision suite."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from client_checks import ClientCheckError, run_node, verify_packages


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--node", type=Path, help="explicit supported runtime for a second compatibility execution"
    )
    arguments = parser.parse_args()
    packages = verify_packages()
    try:
        result = run_node(node=arguments.node)
    except ClientCheckError as exc:
        print(json.dumps({"gate": "clientTests", "result": "FAIL", "execution": exc.report,
                          "liveAcceptance": False}))
        return 1
    print(result.stdout)
    print(result.stderr)
    print(
        json.dumps(
            {
                "gate": "clientTests",
                "result": "PASS" if result.returncode == 0 else "FAIL",
                "packages": packages["artifacts"],
                "liveAcceptance": False,
            }
        )
    )
    return result.returncode


if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    raise SystemExit(main())
