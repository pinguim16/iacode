"""Execute the targeted causal rollup controls; never represent a subset as a complete gate."""

from __future__ import annotations

import argparse

from execute_gate import preserve_execution
from ledger_common import use_utf8_stdout


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only-current", action="store_true")
    parser.add_argument("--include-inherited", action="store_true")
    options = parser.parse_args()
    if options.only_current and options.include_inherited:
        raise ValueError("the causal-only and complete affected-class modes are distinct")
    pattern = "test_gate[57]_*" if options.include_inherited else "test_gate7_*"
    command = ["python", "-m", "unittest", "discover", "-s", "tests", "-p", pattern,
               "-k", "test_current_rollups" if options.only_current else "Gate7RollupTests"]
    if options.include_inherited:
        command.extend(["-k", "Gate5DocumentationTests"])
    return preserve_execution(command, "ROLLUP", "TARGETED_CAUSAL_NOT_WHOLE_GATE", "rollup-control")


if __name__ == "__main__":
    use_utf8_stdout()
    raise SystemExit(main())
