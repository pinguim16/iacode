#!/usr/bin/env python3
"""Does any real credential of this machine appear anywhere in the repository's history?

Asked by the owner after GitGuardian reported a "Generic Password" in commit 7d57721 (the M1 audit
checkpoint). A pattern scanner answers "does something look like a credential"; this answers the
question that matters: is a credential this machine actually uses present in what was, or could
be, published. It reads the secret values of infra/compose/.env — the only place the machine's
credentials live, never committed — and searches every blob reachable from every local ref (a
superset of what is published), every commit message and every annotated tag message for each
value. It prints and records only variable names and locations, never a value.

An access key ID is an identifier, not a secret — it names an account as a user name does — so it
is not searched for; the MinIO one is the project's name and would match everywhere.

    python real_secret_exposure.py --report ../SECRET-EXPOSURE-CHECK.json
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

SENSITIVE = re.compile(r"(?i)(pass|pwd|secret|token|key|credential|auth)")
IDENTIFIERS = re.compile(r"(?i)ACCESS_KEY(_ID)?$")


def git(root: Path, *args: str, data: bytes | None = None) -> bytes:
    return subprocess.run(["git", *args], cwd=root, input=data, capture_output=True,
                          check=True).stdout


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path, required=True)
    arguments = parser.parse_args()
    environment = ROOT / "infra" / "compose" / ".env"
    values: dict[str, bytes] = {}
    for line in environment.read_text(encoding="utf-8").splitlines():
        if "=" not in line or line.lstrip().startswith("#"):
            continue
        name, _, value = line.partition("=")
        name, value = name.strip(), value.strip().strip('"').strip("'")
        if SENSITIVE.search(name) and not IDENTIFIERS.search(name) and len(value) >= 6:
            values[name] = value.encode("utf-8")

    listing = git(ROOT, "rev-list", "--objects", "--all").decode("utf-8", "replace")
    objects: dict[str, str] = {}
    for line in listing.splitlines():
        oid, _, path = line.partition(" ")
        objects.setdefault(oid, path)
    kinds = git(ROOT, "cat-file", "--batch-check=%(objectname) %(objecttype)",
                data=("\n".join(objects) + "\n").encode()).decode().splitlines()
    blobs = [line.split()[0] for line in kinds if line.endswith(" blob")]
    batch = git(ROOT, "cat-file", "--batch", data=("\n".join(blobs) + "\n").encode())
    hits: list[str] = []
    position = scanned = 0
    while position < len(batch):
        newline = batch.index(b"\n", position)
        header = batch[position:newline].split()
        oid, size = header[0].decode(), int(header[2])
        content = batch[newline + 1:newline + 1 + size]
        position = newline + 1 + size + 1
        scanned += 1
        hits += [f"{name} in blob {oid[:12]} ({objects.get(oid)})"
                 for name, value in values.items() if value in content]
    commits = 0
    for record in git(ROOT, "log", "--all", "--format=%H%x00%B%x1e").split(b"\x1e"):
        commit, _, body = record.strip().partition(b"\x00")
        if not commit:
            continue
        commits += 1
        hits += [f"{name} in the message of commit {commit[:12].decode()}"
                 for name, value in values.items() if value in body]
    tags = 0
    for reference in git(ROOT, "for-each-ref", "--format=%(objecttype) %(refname)",
                         "refs/tags").decode().splitlines():
        kind, _, ref = reference.partition(" ")
        if kind == "tag":
            tags += 1
            body = git(ROOT, "cat-file", "tag", ref)
            hits += [f"{name} in the message of tag {ref}"
                     for name, value in values.items() if value in body]
    report = {
        "schemaVersion": "1.0.0", "artifact": "SECRET-EXPOSURE-CHECK",
        "checkpoint": CHECKPOINT.name, "generatedAt": utc_now(),
        "trigger": "GitGuardian 'Generic Password' incident on commit 7d57721 (GATE-3-CP-0002)",
        "variablesChecked": sorted(values), "valuesRecorded": False,
        "blobsScanned": scanned, "commitMessagesScanned": commits,
        "annotatedTagsScanned": tags, "exposures": hits,
        "result": "NONE" if not hits else "FOUND",
    }
    arguments.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n",
                                encoding="utf-8", newline="\n")
    for hit in hits:
        print(f"EXPOSED {hit}")
    print(f"checked {len(values)} secret variable(s): {', '.join(sorted(values))}")
    print(f"REAL_SECRET_EXPOSURE={report['result']} blobs={scanned} commits={commits} "
          f"tags={tags} hits={len(hits)}")
    return 1 if hits else 0


if __name__ == "__main__":
    raise SystemExit(main())
