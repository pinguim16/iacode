#!/usr/bin/env python3
"""Mandatory build, deterministic packaging and complete client decision suite."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from client_checks import run_node, verify_packages


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--node", type=Path, help="explicit supported runtime for a second compatibility execution"
    )
    arguments = parser.parse_args()
    packages = verify_packages()
    result = run_node(node=arguments.node)
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
    raise SystemExit(main())
