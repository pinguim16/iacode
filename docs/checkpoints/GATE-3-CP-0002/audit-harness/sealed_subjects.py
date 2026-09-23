#!/usr/bin/env python3
"""M1 criteria 1 and 2: every sealed checkpoint of the milestone validates from its own tag.

Each checkpoint is checked out, detached, at its canonical tag in a disposable worktree, and the
repository's current validator judges it with `--root` pointing at that checkout. That is the
project's own rule (`test_every_sealed_checkpoint_validates_from_its_own_tag`): validation applies
the rules of the schema version a checkpoint declares, so the current tooling must still accept
every sealed checkpoint, and a defect found after a seal is repaired in the tooling, never in the
sealed content.

The validator the checkpoint shipped with is run too and its result recorded, as an observation:
two sealed checkpoints are known not to pass their own revision's validator (`G1-F-007`,
`G2-F-013`), and the audit states which rather than hiding the difference. The tag must resolve to
the commit the integrity chain anchors, and the checkpoint must close at the status the milestone
relies on.

    python sealed_subjects.py --report ../SEALED-SUBJECTS.json
"""

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

from anchors import load_anchors  # noqa: E402
from ledger_common import utc_now  # noqa: E402

#: The sealed checkpoints of M1, in delivery order. The last of each Gate is the one the milestone
#: relies on; GATE-2-CP-0001 is the Gate 2 checkpoint that closed BLOCKED and was superseded.
SUBJECTS = (
    ("GATE 0", "GATE-0-CP-0001", "INTERNAL_GATE_PASS", True),
    ("GATE 1", "GATE-1-CP-0001", "INTERNAL_GATE_PASS", True),
    ("GATE 2", "GATE-2-CP-0001", "BLOCKED", False),
    ("GATE 2", "GATE-2-CP-0002", "INTERNAL_GATE_PASS", True),
    ("GATE 3", "GATE-3-CP-0001", "INTERNAL_GATE_PASS", True),
)


def git(cwd: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *arguments], cwd=cwd, text=True, encoding="utf-8",
                          errors="replace", capture_output=True, check=False)


REMOTE = "https://github.com/pinguim16/iacode.git"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--remote", action="store_true",
                        help="validate from a clone of the published remote instead of from "
                             "worktrees of this repository, whose object store may hold objects "
                             "no published reference reaches")
    arguments = parser.parse_args()
    anchors = {item["checkpointId"]: item for item in load_anchors(ROOT)}
    results = []
    with tempfile.TemporaryDirectory(prefix="iacode-m1-sealed-") as scratch:
        source = ROOT
        if arguments.remote:
            # A clone over a transport carries only what published references reach, which is
            # exactly what a reviewer or a second tool receives. A clone of the local path, or a
            # worktree of it, would also carry this machine's unreachable objects.
            source = Path(scratch) / "published"
            cloned = git(Path(scratch), "clone", "--quiet", REMOTE, str(source))
            if cloned.returncode != 0:
                raise SystemExit(f"the remote could not be cloned: {cloned.stderr[-300:]}")
        for gate, checkpoint, expected_status, final in SUBJECTS:
            tag = f"iacode-checkpoints/{checkpoint}"
            commit = git(source, "rev-parse", f"{tag}^{{commit}}").stdout.strip()
            anchored = anchors.get(checkpoint) or {}
            worktree = Path(scratch) / checkpoint
            added = git(source, "worktree", "add", "--detach", "--quiet", str(worktree), tag)
            validation = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "development-ledger" /
                                     "validate_checkpoint.py"), "--root", str(worktree)],
                cwd=ROOT, text=True, encoding="utf-8", errors="replace",
                capture_output=True, check=False, timeout=900)
            own = subprocess.run(
                [sys.executable, "scripts/development-ledger/validate_checkpoint.py"],
                cwd=worktree, text=True, encoding="utf-8", errors="replace",
                capture_output=True, check=False, timeout=900)
            state = json.loads((worktree / "docs" / "checkpoints" / checkpoint / "STATE.json")
                               .read_text(encoding="utf-8"))
            latest = (worktree / "docs" / "checkpoints" / "LATEST.md").read_text(encoding="utf-8")
            clean = git(worktree, "status", "--porcelain").stdout.strip() == ""
            git(source, "worktree", "remove", "--force", str(worktree))
            checks = {
                "worktreeCreated": added.returncode == 0,
                "validatesDetachedAtTag": validation.returncode == 0,
                "latestNamesTheCheckpoint": f"docs/checkpoints/{checkpoint}" in latest,
                "statusAsExpected": state.get("status") == expected_status,
                # ADR-0023: a sealed state that kept the symbolic HEAD is bound to its own tag.
                "currentCommitNamesOwnTag": state.get("currentCommit") in (
                    f"refs/tags/{tag}", "HEAD"),
                "anchoredAtTheTagCommit": anchored.get("commit") == commit,
                "worktreeCleanAfterValidation": clean,
            }
            results.append({
                "gate": gate, "checkpoint": checkpoint, "finalOfGate": final, "tag": tag,
                "commit": commit, "status": state.get("status"),
                "requirements": (state.get("requirementsMatrix") or {}).get("total"),
                "coveragePercent": (state.get("requirementsMatrix") or {}).get("coveragePercent"),
                "greenKeeper": (state.get("greenKeeper") or {}).get("status"),
                "completeness": (state.get("deliveryCompleteness") or {}).get("status"),
                "validatorOutput": (validation.stdout.strip().splitlines() or [""])[0][:200],
                "ownRevisionValidator": {
                    "exitCode": own.returncode,
                    "output": " ".join(own.stdout.strip().splitlines()[:3])[:300]},
                "checks": checks, "ok": all(checks.values()),
            })
            print(f"[{'PASS' if results[-1]['ok'] else 'FAIL'}] {checkpoint} {state.get('status')} "
                  f"{results[-1]['validatorOutput']}", flush=True)
        git(source, "worktree", "prune")
    report = {
        "schemaVersion": "1.0.0", "artifact": "SEALED-SUBJECTS", "checkpoint": CHECKPOINT.name,
        "generatedAt": utc_now(), "anchors": len(anchors),
        "source": REMOTE if arguments.remote else "worktrees of this repository",
        "subjects": results,
        "result": "PASS" if all(item["ok"] for item in results) else "FAIL",
    }
    arguments.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n",
                                encoding="utf-8", newline="\n")
    print(f"SEALED_SUBJECTS={report['result']} {sum(item['ok'] for item in results)}/{len(results)}")
    return 0 if report["result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
