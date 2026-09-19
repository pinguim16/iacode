#!/usr/bin/env python3
"""Redact known credential-shaped values from a file or standard input."""

from __future__ import annotations

import argparse
import os
import sys
import tempfile
from pathlib import Path

from ledger_common import redact_text


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", type=Path, help="input file; stdin when omitted")
    parser.add_argument("--in-place", action="store_true", help="atomically replace the input file")
    args = parser.parse_args()

    if args.in_place and args.path is None:
        parser.error("--in-place requires a path")
    source = args.path.read_text(encoding="utf-8") if args.path else sys.stdin.read()
    redacted = redact_text(source)
    if args.in_place:
        temporary_name = ""
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", encoding="utf-8", dir=args.path.parent, delete=False
            ) as temporary:
                temporary.write(redacted)
                temporary_name = temporary.name
            os.chmod(temporary_name, args.path.stat().st_mode)
            os.replace(temporary_name, args.path)
        finally:
            if temporary_name:
                Path(temporary_name).unlink(missing_ok=True)
    else:
        sys.stdout.write(redacted)
    return 0


if __name__ == "__main__":
    sys.exit(main())
