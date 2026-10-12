#!/usr/bin/env python3
"""Declare the complete CP0007 delta with authored reasons and canonical hashes."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
BASE = "dfa2871c4fcecf9eedd7df9f135a5cfcdebce9d5"
sys.path.insert(0, str(ROOT / "scripts" / "development-ledger"))

from ledger_common import canonical_hash_bytes, canonical_hash_path, use_utf8_stdout  # noqa: E402


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


def reason(path: str) -> str:
    if path == ".iacode/anchors/checkpoint-chain.json":
        return "Integrity chain extended to anchor immutable published predecessor CP0006."
    if path.startswith(".iacode/memory/"):
        return "LSN-0040 guardrail failure recorded, repaired, tested and re-guarded."
    if path == ".iacode/policies/audit-registry.json":
        return "Published-transport finding G4-F-003 registered as mandatory corrective work."
    if path.startswith(".iacode/schemas/"):
        return "Checkpoint schema 3.3.0 accepts the forward-only transport-bound evidence contract."
    if path == "DIVERGENCE.md":
        return "Truthful CP0006 remote publication divergence and finding retained."
    if path == "docs/CHECKPOINT-PROTOCOL.md":
        return "Checkpoint protocol documents the schema 3.3.0 command-input transport rule."
    if path == "docs/adr/ADR-0034-command-inputs-must-cross-git-transport.md":
        return "Structural decision for forward-only transport-bound command evidence."
    if path.startswith("scripts/development-ledger/"):
        return "Shared recorder and validator enforce one Git transport classification."
    if path.startswith("tests/"):
        return "Automated regressions prevent generated or Git-metadata inputs from escaping."
    if path == "docs/checkpoints/LATEST.md":
        return "Canonical pointer advanced to the Gate 4 corrective successor."
    if path.startswith("docs/checkpoints/GATE-4-CP-0007/audit-harness/"):
        return "Reproducible corrective-run evidence harness."
    if path.startswith("docs/checkpoints/GATE-4-CP-0007/"):
        return "Gate 4 corrective evidence, assurance record or review handoff artifact."
    return "Declared Gate 4 corrective change required to close G4-F-003."


def item(path: str, kind: str) -> dict[str, str]:
    result = {"path": path, "reason": reason(path)}
    if path.endswith("/FILES.json"):
        return result
    if kind in {"M", "D"}:
        result["hashBefore"] = canonical_hash_bytes(git("show", f"{BASE}:{path}", binary=True))
    if kind in {"A", "M"}:
        result["hashAfter"] = canonical_hash_path(ROOT / path)
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
        exists_at_base = subprocess.run(
            ["git", "cat-file", "-e", f"{BASE}:{path}"],
            cwd=ROOT,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
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
            {"path": "docs/checkpoints/GATE-4-CP-0006/STATE.json", "reason": "Immutable predecessor state."},
            {"path": "docs/checkpoints/GATE-4-CP-0006/HANDOFF.md", "reason": "Predecessor handoff and publication claim."},
            {"path": "DIVERGENCE.md", "reason": "Observed remote transport failure and required reconciliation."}
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
