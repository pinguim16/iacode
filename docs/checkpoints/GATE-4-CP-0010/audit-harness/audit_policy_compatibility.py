#!/usr/bin/env python3
"""Run current tooling against every sealed subject carrying legacy internal verdict fields."""

from __future__ import annotations

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


def git(directory: Path, *arguments: str) -> str:
    return subprocess.run(["git", *arguments], cwd=directory, check=True,
                          capture_output=True, text=True, encoding="utf-8").stdout.strip()


def main() -> int:
    report_path = CHECKPOINT / "POLICY-COMPATIBILITY.json"
    if report_path.exists():
        raise LedgerError("preserve the prior historical compatibility attempt")
    remote = git(ROOT, "remote", "get-url", "origin")
    rows = []
    with tempfile.TemporaryDirectory(prefix="iacode-cp0010-policy-compatibility-") as temporary:
        clone = Path(temporary) / "repository"
        git(Path(temporary), "clone", "--no-local", remote, str(clone))
        anchors = load_anchors(ROOT)
        for anchor in anchors:
            tag, identifier = anchor["tag"], anchor["checkpointId"]
            if git(clone, "rev-parse", tag) != anchor["commit"]:
                raise LedgerError("published canonical anchor changed")
            state = json.loads(git(clone, "show", f"{tag}:docs/checkpoints/{identifier}/STATE.json"))
            if state.get("status") != "INTERNAL_GATE_PASS":
                continue
            if (state.get("redTeam", {}).get("status") != "RED_TEAM_PASS"
                    and state.get("independentReview", {}).get("status") != "APPROVED"):
                continue
            git(clone, "checkout", "--detach", tag)
            policy = json.loads((clone / ".iacode/memory/POLICY.json").read_text())
            if policy["schemaVersion"] == "2.4.0":
                raise LedgerError("a strict-policy subject claims legacy internal verdict semantics")
            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts/development-ledger/validate_checkpoint.py"),
                 "--root", str(clone)], cwd=ROOT, capture_output=True, text=True,
                encoding="utf-8", errors="replace", check=False,
            )
            clean = not git(clone, "status", "--porcelain")
            rows.append({"tag": tag, "commit": git(clone, "rev-parse", "HEAD"),
                         "subjectPolicy": policy["schemaVersion"], "exitCode": result.returncode,
                         "gitStateUnchanged": clean,
                         "result": "PASS" if result.returncode == 0 and clean else "FAIL"})
    removed = not Path(temporary).exists()
    passed = removed and bool(rows) and all(row["result"] == "PASS" for row in rows)
    write_json(report_path, {"schemaVersion": "1.0.0", "generatedAt": utc_now(),
                            "selection": "all sealed internal verdicts carrying legacy review fields",
                            "subjects": rows, "temporaryCloneRemoved": removed,
                            "result": "PASS" if passed else "FAIL"})
    print(f"POLICY_COMPATIBILITY={'PASS' if passed else 'FAIL'} subjects={len(rows)}")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.path.insert(0, str(ROOT / "scripts/development-ledger"))
    from ledger_common import use_utf8_stdout

    use_utf8_stdout()
    raise SystemExit(main())
