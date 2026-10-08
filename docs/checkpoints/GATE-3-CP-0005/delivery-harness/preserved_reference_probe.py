#!/usr/bin/env python3
"""Reproduce the load-bearing preserved-reference check and keep its Git evidence."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "development-ledger"))

from ledger_common import published_clone, published_reachability, write_json  # noqa: E402


def git(root: Path, *arguments: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *arguments], cwd=root, check=check, capture_output=True,
                          text=True, encoding="utf-8", errors="replace")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    rows: list[dict[str, object]] = []
    with tempfile.TemporaryDirectory(prefix="iacode-preserved-probe-") as directory:
        clone = Path(directory) / "source"
        if not published_clone(ROOT, clone):
            raise RuntimeError("published clone failed")
        output = git(clone, "for-each-ref", "--format=%(refname) %(objectname)",
                     "refs/tags/iacode-preserved").stdout
        anchors = json.loads((clone / ".iacode" / "anchors" / "checkpoint-chain.json")
                             .read_text(encoding="utf-8"))["anchors"]
        for line in output.splitlines():
            reference, commit = line.split()
            checkpoint = next(
                (str(anchor["checkpointId"]) for anchor in anchors
                 if commit in (clone / "docs" / "checkpoints" / str(anchor["checkpointId"])
                               / "COMMANDS.jsonl").read_text(encoding="utf-8")),
                None,
            )
            if checkpoint is None:
                raise RuntimeError(f"no anchored checkpoint names {commit}")
            git(clone, "checkout", "--quiet", "--detach",
                f"refs/tags/iacode-checkpoints/{checkpoint}")
            before = git(clone, "for-each-ref", "--contains", commit,
                         "--format=%(refname)", "refs/heads", "refs/tags",
                         "refs/remotes").stdout.splitlines()
            git(clone, "update-ref", "-d", reference)
            after = git(clone, "for-each-ref", "--contains", commit,
                        "--format=%(refname)", "refs/heads", "refs/tags",
                        "refs/remotes").stdout.splitlines()
            validation = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "development-ledger"
                                     / "validate_checkpoint.py"), "--root", str(clone)],
                capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
            after_validation = git(clone, "for-each-ref", "--contains", commit,
                                   "--format=%(refname)", "refs/heads", "refs/tags",
                                   "refs/remotes").stdout.splitlines()
            rows.append({
                "reference": reference,
                "commit": commit,
                "checkpoint": checkpoint,
                "before": before,
                "after": after,
                "reachabilityAfterDeletion": published_reachability(clone, commit),
                "validationExitCode": validation.returncode,
                "validationOutput": (validation.stdout + validation.stderr)[-1200:],
                "referencesAfterValidation": after_validation,
            })
            git(clone, "update-ref", reference, commit)
            git(clone, "checkout", "--quiet", "main")
    document = {"artifact": "PRESERVED_REFERENCE_PROBE", "checkpoint": CHECKPOINT.name,
                "references": rows}
    target = args.report if args.report.is_absolute() else ROOT / args.report
    write_json(target, document)
    print(json.dumps(document, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
