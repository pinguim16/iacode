#!/usr/bin/env python3
"""Which commits does sealed evidence name, and does a published reference reach each one?

Finding `M1-F-003` is one instance of a property: every object that sealed evidence references must
be reachable from the published history, because a reviewer receives the published history and
nothing else. This harness measures the property over the whole ledger, independently of the
validator the delivery changes, so the baseline and the result are observations and not the
tool's own opinion of itself.

For every checkpoint it reads every 40-hex value in the command records and the commit fields of
`STATE.json`, `FILES.json` and `RUN-METADATA.json`, and asks Git two separate questions:

- does the object exist in this repository's object store (`LOCAL OBJECT EXISTS`);
- does a published reference -- a branch, a tag or a remote-tracking branch -- reach it
  (`PUBLISHED OBJECT EXISTS`).

A commit that answers yes and no is exactly the defect: valid here, invalid in any clone of the
remote.

    python sealed_evidence_commits.py --report ../SEALED-EVIDENCE-COMMITS-BASELINE.json
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "development-ledger"))

from ledger_common import utc_now  # noqa: E402

SHA = re.compile(r"[0-9a-f]{40}")
PUBLISHED = ("refs/heads", "refs/tags", "refs/remotes")


def git(root: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *arguments], cwd=root, text=True, encoding="utf-8",
                          errors="replace", capture_output=True, check=False)


def named_commits(root: Path) -> dict[str, list[str]]:
    found: dict[str, list[str]] = {}

    def walk(value: object, where: str) -> None:
        if isinstance(value, dict):
            for key, item in value.items():
                walk(item, f"{where}.{key}")
        elif isinstance(value, list):
            for item in value:
                walk(item, where)
        elif isinstance(value, str) and SHA.fullmatch(value):
            found.setdefault(value, []).append(where)

    for checkpoint in sorted((root / "docs" / "checkpoints").iterdir()):
        if not checkpoint.is_dir():
            continue
        ledger = checkpoint / "COMMANDS.jsonl"
        if ledger.is_file():
            for number, line in enumerate(ledger.read_text(encoding="utf-8").splitlines(), 1):
                if line.strip():
                    walk(json.loads(line), f"{checkpoint.name}/COMMANDS.jsonl:{number}")
        for name in ("STATE.json", "FILES.json", "RUN-METADATA.json"):
            path = checkpoint / name
            if path.is_file():
                document = json.loads(path.read_text(encoding="utf-8"))
                for key in ("baseCommit", "currentCommit", "initialCommit", "finalCommit"):
                    value = document.get(key) if isinstance(document, dict) else None
                    if isinstance(value, str) and SHA.fullmatch(value):
                        found.setdefault(value, []).append(f"{checkpoint.name}/{name}.{key}")
    return found


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--root", type=Path, default=ROOT)
    arguments = parser.parse_args()
    root = arguments.root.resolve()
    commits = named_commits(root)
    rows = []
    for commit, where in sorted(commits.items()):
        local = git(root, "cat-file", "-e", f"{commit}^{{commit}}").returncode == 0
        reaching = git(root, "for-each-ref", "--contains", commit, "--count=3",
                       "--format=%(refname)", *PUBLISHED).stdout.split() if local else []
        rows.append({"commit": commit, "localObjectExists": local,
                     "publishedObjectExists": bool(reaching), "reachedBy": reaching,
                     "namedBy": sorted(set(where))[:6], "references": len(where)})
    unpublished = [row for row in rows if not row["publishedObjectExists"]]
    report = {
        "schemaVersion": "1.0.0", "artifact": "SEALED-EVIDENCE-COMMITS",
        "checkpoint": CHECKPOINT.name, "generatedAt": utc_now(),
        "repository": "this working repository" if root == ROOT else str(root),
        "publishedReferences": list(PUBLISHED),
        "commitsNamed": len(rows), "unpublished": len(unpublished),
        "localButUnpublished": [row["commit"] for row in unpublished
                                if row["localObjectExists"]],
        "absent": [row["commit"] for row in rows if not row["localObjectExists"]],
        "commits": rows,
        "result": "PASS" if not unpublished else "FAIL",
    }
    arguments.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n",
                                encoding="utf-8", newline="\n")
    for row in unpublished:
        print(f"UNPUBLISHED {row['commit'][:12]} local={row['localObjectExists']} "
              f"named by {', '.join(row['namedBy'][:3])}")
    print(f"SEALED_EVIDENCE_COMMITS={report['result']} named={len(rows)} "
          f"unpublished={len(unpublished)}")
    return 0 if not unpublished else 1


if __name__ == "__main__":
    raise SystemExit(main())
