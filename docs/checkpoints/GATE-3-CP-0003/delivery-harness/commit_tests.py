#!/usr/bin/env python3
"""Run targeted tests against exactly the content of one commit, before it is pushed.

A disposable worktree is checked out, detached, at ``--commit``, and the tests run there with the
tooling of that commit. The working tree of this repository may already hold the next correction;
this measures the commit alone, which is what a push publishes.

    python commit_tests.py --commit HEAD --test tests.test_gate3_sandbox
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--commit", required=True)
    parser.add_argument("--test", action="append", required=True)
    arguments = parser.parse_args()
    commit = subprocess.run(["git", "rev-parse", arguments.commit], cwd=ROOT, text=True,
                            encoding="utf-8", capture_output=True, check=True).stdout.strip()
    scratch = Path(tempfile.mkdtemp(prefix="iacode-commit-tests-"))
    worktree = scratch / "commit"
    try:
        subprocess.run(["git", "worktree", "add", "--detach", "--quiet", str(worktree), commit],
                       cwd=ROOT, check=True)
        print(f"testing {commit[:12]} in a worktree of its own", flush=True)
        completed = subprocess.run([sys.executable, "-m", "unittest", *arguments.test],
                                   cwd=worktree, check=False)
        return completed.returncode
    finally:
        subprocess.run(["git", "worktree", "remove", "--force", str(worktree)], cwd=ROOT,
                       check=False)
        subprocess.run(["git", "worktree", "prune"], cwd=ROOT, check=False)
        shutil.rmtree(scratch, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
