"""Preserve a specifically named local causal invocation; never substitute for a complete gate."""

from __future__ import annotations

import argparse
import re

from execute_gate import preserve_execution
from ledger_common import use_utf8_stdout


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--label", required=True)
    parser.add_argument("argv", nargs=argparse.REMAINDER)
    options = parser.parse_args()
    command = list(options.argv)
    if command and command[0] == "--":
        command.pop(0)
    if not re.fullmatch(r"[A-Z][A-Z0-9-]{0,63}", options.label):
        raise ValueError("a bounded explicit targeted evidence label is required")
    if not command or command[0] not in {"python", "docker"}:
        raise ValueError("targeted local evidence requires an explicit repository runtime")
    return preserve_execution(command, options.label, "TARGETED_CAUSAL_NOT_WHOLE_GATE", options.label)


if __name__ == "__main__":
    use_utf8_stdout()
    raise SystemExit(main())
