#!/usr/bin/env python3
"""Declare every audit-checkpoint delta without inventing product changes."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "development-ledger"))

from ledger_common import blob_hash, canonical_hash_path  # noqa: E402

BASE = "70a22e824705f414e0c295bbdf89187db9b391f7"


def run(*args: str) -> str:
    completed = subprocess.run(["git", *args], cwd=ROOT, text=True, encoding="utf-8",
                               errors="replace", capture_output=True, check=True)
    return completed.stdout


def reason(path: str) -> str:
    if path == ".iacode/policies/audit-registry.json":
        return "Register the blocking independent Gate 4 audit for mandatory corrective delivery."
    if path.startswith(".iacode/attestations/"):
        return "Formal fresh-session attestation recording the failed audit without granting promotion."
    if path == ".iacode/anchors/checkpoint-chain.json":
        return "Anchor the sealed subject predecessor before auditing it."
    if path == "docs/checkpoints/LATEST.md":
        return "Point the Engineering Ledger at the current audit checkpoint."
    if path.startswith("docs/checkpoints/GATE-4-CP-0002/audit-harness/"):
        return "Reproducible audit-only harness; it does not alter product behavior."
    if path.startswith("docs/checkpoints/GATE-4-CP-0002/"):
        return "Gate 4 independent-audit evidence, finding, assurance result, or handoff record."
    return "Declared independent-audit delta."


def main() -> int:
    changed = {}
    for line in run("diff", "--name-status", BASE, "--").splitlines():
        if not line:
            continue
        status, path = line.split("\t", 1)
        changed[path.replace("\\", "/")] = status[0]
    for path in run("ls-files", "--others", "--exclude-standard").splitlines():
        if path:
            changed[path.replace("\\", "/")] = "A"
    own = CHECKPOINT.relative_to(ROOT).as_posix() + "/FILES.json"
    changed[own] = "A"
    document = {"filesRead": [], "filesCreated": [], "filesModified": [], "filesDeleted": []}
    bucket = {"A": "filesCreated", "M": "filesModified", "D": "filesDeleted"}
    for path, status in sorted(changed.items()):
        if status not in bucket:
            raise RuntimeError(f"unsupported git delta {status} for {path}")
        item = {"path": path, "reason": reason(path)}
        candidate = ROOT / path
        if status in {"A", "M"} and candidate.is_file() and path != own:
            item["hashAfter"] = canonical_hash_path(candidate)
        if status in {"M", "D"}:
            before = blob_hash(ROOT, BASE, path)
            if before is None:
                raise RuntimeError(f"missing base blob for {path}")
            item["hashBefore"] = before
        document[bucket[status]].append(item)
    (CHECKPOINT / "FILES.json").write_text(
        json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print("INVENTORY_DECLARED created=%d modified=%d deleted=%d" % (
        len(document["filesCreated"]), len(document["filesModified"]), len(document["filesDeleted"])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
