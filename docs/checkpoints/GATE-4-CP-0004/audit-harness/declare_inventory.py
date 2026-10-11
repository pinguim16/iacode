#!/usr/bin/env python3
"""Declare the complete audit-checkpoint delta with content-bound hashes."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path


CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
BASE = "5d47200fde08c47b7a6410be2204b4c1b9fbadc1"


def git(*arguments: str, binary: bool = False) -> bytes | str:
    completed = subprocess.run(
        ["git", *arguments],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
        text=not binary,
        encoding=None if binary else "utf-8",
    )
    return completed.stdout


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def reason(path: str) -> str:
    if path == ".iacode/anchors/checkpoint-chain.json":
        return "Integrity chain rebuilt to anchor the sealed Gate 4 subject before auditing it."
    if path == ".iacode/attestations/G4-CP-0004.json":
        return "Fresh-session Gate 4 audit attestation naming the immutable sealed subject."
    if path == "docs/checkpoints/LATEST.md":
        return "Canonical checkpoint pointer advanced to the independent Gate 4 audit checkpoint."
    if path.startswith("docs/checkpoints/GATE-4-CP-0004/audit-harness/"):
        return "Reproducible audit-owned harness; it does not modify or replace product behavior."
    if path.startswith("docs/checkpoints/GATE-4-CP-0004/"):
        return "Gate 4 independent audit evidence, assurance record, or handoff artifact."
    return "Declared repository change required by the Gate 4 independent audit."


def item(path: str, kind: str) -> dict[str, str]:
    result = {"path": path, "reason": reason(path)}
    if path.endswith("/FILES.json"):
        return result
    if kind in {"M", "D"}:
        result["hashBefore"] = digest(git("show", f"{BASE}:{path}", binary=True))
    if kind in {"A", "M"}:
        result["hashAfter"] = digest((ROOT / path).read_bytes())
    return result


def main() -> int:
    changed = {
        line.strip().replace("\\", "/")
        for line in str(git("diff", "--name-only", BASE)).splitlines()
        if line.strip()
    }
    untracked = {
        line.strip().replace("\\", "/")
        for line in str(git("ls-files", "--others", "--exclude-standard")).splitlines()
        if line.strip()
    }
    paths = sorted(changed | untracked)
    created: list[dict[str, str]] = []
    modified: list[dict[str, str]] = []
    deleted: list[dict[str, str]] = []
    for path in paths:
        exists_at_base = subprocess.run(
            ["git", "cat-file", "-e", f"{BASE}:{path}"], cwd=ROOT, check=False,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        ).returncode == 0
        exists_now = (ROOT / path).is_file()
        kind = "M" if exists_at_base and exists_now else "D" if exists_at_base else "A"
        target = modified if kind == "M" else deleted if kind == "D" else created
        target.append(item(path, kind))

    document = {
        "filesRead": [
            {"path": "START-HERE.md", "reason": "Required repository entry point."},
            {"path": "docs/DEVELOPMENT-CONTRACT.md", "reason": "Canonical delivery contract."},
            {"path": "docs/MASTER-PLAN.md", "reason": "Gate and milestone scope."},
            {"path": "docs/GATE-4-CHECKLIST.md", "reason": "Canonical Gate 4 requirements."},
            {"path": "docs/checkpoints/GATE-4-CP-0003/STATE.json", "reason": "Sealed subject state."},
            {"path": "docs/checkpoints/GATE-4-CP-0003/HANDOFF.md", "reason": "Subject handoff and audit target."},
        ],
        "filesCreated": created,
        "filesModified": modified,
        "filesDeleted": deleted,
    }
    (CHECKPOINT / "FILES.json").write_text(
        json.dumps(document, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(
        f"INVENTORY_DECLARED created={len(created)} modified={len(modified)} "
        f"deleted={len(deleted)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
