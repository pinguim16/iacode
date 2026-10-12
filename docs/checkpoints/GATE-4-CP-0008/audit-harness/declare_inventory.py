#!/usr/bin/env python3
"""Declare every CP0008 repository change with content-bound hashes."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path


CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
BASE = "e21d30fde473f302d0f8f60b59acf008fa52e250"
sys.path.insert(0, str(ROOT / "scripts" / "development-ledger"))

from ledger_common import use_utf8_stdout  # noqa: E402


def git(*arguments: str, binary: bool = False) -> bytes | str:
    return subprocess.run(
        ["git", *arguments],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
        text=not binary,
        encoding=None if binary else "utf-8",
    ).stdout


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def reason(path: str) -> str:
    if path == ".iacode/anchors/checkpoint-chain.json":
        return "Integrity chain rebuilt to anchor sealed CP0007 before auditing it."
    if path == ".iacode/attestations/G4-CP-0008.json":
        return "Fresh-session failed Gate 4 audit attestation naming the immutable subject."
    if path == "docs/checkpoints/LATEST.md":
        return "Canonical pointer advanced to the independent Gate 4 audit checkpoint."
    if path.startswith("docs/checkpoints/GATE-4-CP-0008/audit-harness/"):
        return "Reproducible audit-owned harness; it does not alter product behavior."
    if path.startswith("docs/checkpoints/GATE-4-CP-0008/"):
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
    use_utf8_stdout()
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
    created: list[dict[str, str]] = []
    modified: list[dict[str, str]] = []
    deleted: list[dict[str, str]] = []
    for path in sorted(changed | untracked):
        at_base = subprocess.run(
            ["git", "cat-file", "-e", f"{BASE}:{path}"],
            cwd=ROOT,
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        ).returncode == 0
        exists = (ROOT / path).is_file()
        kind = "M" if at_base and exists else "D" if at_base else "A"
        (modified if kind == "M" else deleted if kind == "D" else created).append(item(path, kind))

    document = {
        "filesRead": [
            {"path": "START-HERE.md", "reason": "Required repository entry point."},
            {"path": "docs/DEVELOPMENT-CONTRACT.md", "reason": "Canonical delivery contract."},
            {"path": "docs/MASTER-PLAN.md", "reason": "Gate and milestone scope."},
            {"path": "docs/GATE-4-CHECKLIST.md", "reason": "Canonical Gate 4 requirements."},
            {"path": "docs/checkpoints/GATE-4-CP-0007/STATE.json", "reason": "Immutable sealed subject state."},
            {"path": "docs/checkpoints/GATE-4-CP-0007/HANDOFF.md", "reason": "Subject handoff and audit target."},
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
    print(f"INVENTORY_DECLARED created={len(created)} modified={len(modified)} deleted={len(deleted)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
