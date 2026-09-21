#!/usr/bin/env python3
"""Execute the whole suite and report what actually happened, case by case.

The delivery records a passing count. This audit does not take it: the suite is executed here and
the result object is read directly, so passes, failures, errors, skips and expected failures are
separated instead of collapsed into one number.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import unittest
from pathlib import Path


def run(root: Path, log: Path) -> dict:
    tests_directory = root / "tests"
    loader = unittest.defaultTestLoader
    suite = loader.discover(str(tests_directory), top_level_dir=str(tests_directory))

    identifiers: list[str] = []

    def walk(item) -> None:
        if isinstance(item, unittest.TestSuite):
            for child in item:
                walk(child)
        elif isinstance(item, unittest.TestCase):
            identifiers.append(item.id())

    walk(suite)

    log.parent.mkdir(parents=True, exist_ok=True)
    stream = log.open("w", encoding="utf-8")
    started = time.monotonic()
    runner = unittest.TextTestRunner(stream=stream, verbosity=2)
    result = runner.run(suite)
    duration = round(time.monotonic() - started, 1)
    stream.close()

    skipped = [{"test": case.id(), "reason": reason} for case, reason in result.skipped]
    failures = [case.id() for case, _ in result.failures]
    errors = [case.id() for case, _ in result.errors]
    expected_failures = [case.id() for case, _ in result.expectedFailures]
    unexpected = [case.id() for case in result.unexpectedSuccesses]

    passed = (result.testsRun - len(failures) - len(errors) - len(skipped)
              - len(expected_failures) - len(unexpected))
    return {
        "root": str(root),
        "discovered": len(identifiers),
        "distinctDiscovered": len(set(identifiers)),
        "testsRun": result.testsRun,
        "passed": passed,
        "failures": failures,
        "errors": errors,
        "skipped": skipped,
        "expectedFailures": expected_failures,
        "unexpectedSuccesses": unexpected,
        "wasSuccessful": result.wasSuccessful(),
        "durationSeconds": duration,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--log", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    sys.path.insert(0, str(root / "scripts" / "development-ledger"))
    report = run(root, args.log.resolve())
    text = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.out:
        args.out.write_text(text, encoding="utf-8", newline="\n")
    print(text)
    return 0 if report["wasSuccessful"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
