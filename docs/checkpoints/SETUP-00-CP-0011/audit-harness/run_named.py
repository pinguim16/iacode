#!/usr/bin/env python3
"""Execute named test identifiers and report the outcome of each one separately.

The closure record names the tests that close each finding. This audit executes those identifiers
itself rather than reading a claim, and reports pass, failure, error or skip per identifier so a
conditional skip can never be read as a pass.
"""

from __future__ import annotations

import argparse
import json
import sys
import unittest
from pathlib import Path


class Recorder(unittest.TestResult):
    def __init__(self) -> None:
        super().__init__()
        self.outcomes: dict[str, str] = {}
        self.details: dict[str, str] = {}

    def addSuccess(self, test):  # noqa: N802
        super().addSuccess(test)
        self.outcomes[test.id()] = "PASS"

    def addFailure(self, test, err):  # noqa: N802
        super().addFailure(test, err)
        self.outcomes[test.id()] = "FAIL"
        self.details[test.id()] = self._exc_info_to_string(err, test)[-600:]

    def addError(self, test, err):  # noqa: N802
        super().addError(test, err)
        self.outcomes[test.id()] = "ERROR"
        self.details[test.id()] = self._exc_info_to_string(err, test)[-600:]

    def addSkip(self, test, reason):  # noqa: N802
        super().addSkip(test, reason)
        self.outcomes[test.id()] = "SKIPPED"
        self.details[test.id()] = reason


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--identifiers", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    root = args.root.resolve()
    sys.path.insert(0, str(root / "tests"))
    sys.path.insert(0, str(root / "scripts" / "development-ledger"))

    identifiers = [line.strip() for line
                   in args.identifiers.read_text(encoding="utf-8").splitlines() if line.strip()]
    loader = unittest.defaultTestLoader
    suite = unittest.TestSuite()
    missing: list[str] = []
    for identifier in identifiers:
        try:
            suite.addTests(loader.loadTestsFromName(identifier))
        except Exception as exc:  # noqa: BLE001 - a name that cannot be loaded is a result
            missing.append(f"{identifier}: {exc}")

    recorder = Recorder()
    suite.run(recorder)

    outcomes = {identifier: recorder.outcomes.get(identifier, "NOT_RUN")
                for identifier in identifiers}
    report = {
        "root": str(root),
        "requested": len(identifiers),
        "loadFailures": missing,
        "outcomes": outcomes,
        "details": recorder.details,
        "passed": sum(1 for value in outcomes.values() if value == "PASS"),
        "skipped": sum(1 for value in outcomes.values() if value == "SKIPPED"),
        "failed": sum(1 for value in outcomes.values() if value in ("FAIL", "ERROR")),
        "notRun": sum(1 for value in outcomes.values() if value == "NOT_RUN"),
    }
    args.out.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({key: report[key] for key in
                      ("requested", "passed", "skipped", "failed", "notRun", "loadFailures")},
                     indent=2))
    for identifier, outcome in outcomes.items():
        if outcome != "PASS":
            print(f"- {outcome} {identifier}: {recorder.details.get(identifier, '')[:200]}")
    return 0 if report["failed"] == 0 and not missing and report["notRun"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
