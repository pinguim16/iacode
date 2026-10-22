"""Run one audit command and preserve bounded, separately captured terminal evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from typing import Any


MAX_CAPTURE_BYTES = 131_072


def _capture(raw: bytes) -> dict[str, Any]:
    bounded = raw if len(raw) <= MAX_CAPTURE_BYTES else raw[-MAX_CAPTURE_BYTES:]
    return {
        "bytes": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "truncatedToTail": len(raw) > MAX_CAPTURE_BYTES,
        "capturedBytes": len(bounded),
        "text": bounded.decode("utf-8", errors="replace"),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--working-directory", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("argv", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    argv = list(args.argv)
    if argv and argv[0] == "--":
        argv = argv[1:]
    if not argv:
        parser.error("a command is required after --")

    working_directory = args.working_directory.resolve(strict=True)
    started_wall = time.time()
    started = time.monotonic()
    completed = subprocess.run(
        argv,
        cwd=working_directory,
        env=os.environ.copy(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    duration_ms = int((time.monotonic() - started) * 1000)
    receipt = {
        "schemaVersion": "1.0.0",
        "artifact": "OBSERVED_COMMAND",
        "workingDirectory": str(working_directory),
        "arguments": argv,
        "startedUnixSeconds": started_wall,
        "durationMs": duration_ms,
        "exitCode": completed.returncode,
        "stdout": _capture(completed.stdout),
        "stderr": _capture(completed.stderr),
    }
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(
        json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(
        "OBSERVED_COMMAND "
        f"exit={completed.returncode} duration_ms={duration_ms} "
        f"stdout_bytes={len(completed.stdout)} stderr_bytes={len(completed.stderr)} "
        f"receipt={args.receipt}"
    )
    if completed.stdout:
        sys.stdout.buffer.write(completed.stdout[-MAX_CAPTURE_BYTES:])
    if completed.stderr:
        print("\n--- child stderr ---", file=sys.stderr)
        sys.stderr.buffer.write(completed.stderr[-MAX_CAPTURE_BYTES:])
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
