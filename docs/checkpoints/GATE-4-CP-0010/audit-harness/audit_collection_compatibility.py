#!/usr/bin/env python3
"""Probe current collection rules against every canonically anchored immutable subject."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))

from anchors import load_anchors
from ledger_common import LedgerError, utc_now, write_json
from policies import counted_test_suites, test_suite_source_files


def git(directory: Path, *arguments: str) -> str:
    result = subprocess.run(["git", *arguments], cwd=directory, capture_output=True,
                            text=True, encoding="utf-8", check=False)
    if result.returncode:
        raise RuntimeError(f"git {arguments[0]} failed with exit {result.returncode}")
    return result.stdout.strip()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, required=True)
    arguments = parser.parse_args()
    destination = (ROOT / arguments.report).resolve()
    if destination.parent != CHECKPOINT or destination.exists():
        raise ValueError("preserve prior observations; report must be new and checkpoint-owned")
    anchors = load_anchors(ROOT)
    rows = []
    with tempfile.TemporaryDirectory(prefix="iacode-cp0010-collection-compatibility-") as temporary:
        clone = Path(temporary) / "repository"
        git(Path(temporary), "clone", "--no-local", git(ROOT, "remote", "get-url", "origin"),
            str(clone))
        for anchor in anchors:
            git(clone, "checkout", "--quiet", "--detach", anchor["tag"])
            if git(clone, "rev-parse", "HEAD") != anchor["commit"]:
                raise ValueError("canonical immutable subject changed")
            suites = counted_test_suites(clone)
            failures = []
            files = 0
            for suite in suites:
                try:
                    files += len(test_suite_source_files(clone, suite))
                except LedgerError as error:
                    failures.append({"suite": suite["id"], "reason": str(error)})
            clean = not git(clone, "status", "--porcelain")
            row = {
                "checkpoint": anchor["checkpointId"], "tag": anchor["tag"],
                "commit": anchor["commit"], "expectedCountedSuites": len(suites),
                "derivationSource": "canonical counted suites in this immutable subject's registry",
                "sourceFiles": files, "failures": failures, "gitStateUnchanged": clean,
                "result": "FAIL" if failures or not clean else "PASS" if suites
                          else "NOT_APPLICABLE",
            }
            if not suites:
                row["justification"] = "the subject declares no counted test suites"
            rows.append(row)
    removed = not Path(temporary).exists()
    failed = [row for row in rows if row["result"] == "FAIL"]
    report = {
        "schemaVersion": "1.0.0", "generatedAt": utc_now(),
        "kind": "SAME_SESSION_COLLECTION_COMPONENT_COMPATIBILITY_ONLY",
        "expectedCanonicalAnchors": len(anchors), "inspectedCanonicalAnchors": len(rows),
        "subjects": rows, "incompatibleSubjects": len(failed),
        "temporaryCloneRemoved": removed,
        "result": "PASS" if removed and len(rows) == len(anchors) and not failed else "FAIL",
    }
    write_json(destination, report)
    print(json.dumps({"result": report["result"], "subjects": len(rows),
                      "incompatible": [row["checkpoint"] for row in failed],
                      "temporaryCloneRemoved": removed}))
    return 0 if report["result"] == "PASS" else 1


if __name__ == "__main__":
    sys.path.insert(0, str(ROOT / "scripts/development-ledger"))
    from ledger_common import use_utf8_stdout

    use_utf8_stdout()
    raise SystemExit(main())
