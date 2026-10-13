#!/usr/bin/env python3
"""Declare the complete CP0009 delta with authored reasons and canonical hashes."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
BASE = "e7879006d516898d441217f253e8282f69fa0b80"
sys.path.insert(0, str(ROOT / "scripts" / "development-ledger"))

from ledger_common import canonical_hash_bytes, canonical_hash_path, use_utf8_stdout  # noqa: E402


def git(*arguments: str, binary: bool = False) -> bytes | str:
    completed = subprocess.run(
        ["git", *arguments], cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        check=True, text=not binary, encoding=None if binary else "utf-8",
    )
    return completed.stdout


def reason(path: str) -> str:
    if path == ".iacode/anchors/checkpoint-chain.json":
        return "Integrity chain extended to anchor immutable published predecessor CP0008."
    if path.startswith(".iacode/memory/"):
        return "Corrective lessons and guardrails record review reconstruction, provenance and cancellation recurrence evidence."
    if path == ".iacode/policies/audit-registry.json":
        return "Sealed G4-F-004 audit registered as mandatory corrective work."
    if path == ".iacode/policies/canonical-requirements.json" or path == "docs/GATE-4-CHECKLIST.md":
        return "Canonical row 20.5 now requires immutable transported reconstruction."
    if path.startswith(".iacode/schemas/"):
        return "Schema 3.4.0 accepts the immutable review-transport evidence contract."
    if path == "docs/CHECKPOINT-PROTOCOL.md":
        return "Checkpoint protocol documents schema 3.4 reconstruction and seal chronology."
    if path == "docs/adr/ADR-0035-review-bundles-bind-immutable-content.md":
        return "Structural decision for immutable review-bundle reconstruction."
    if path == "docs/adr/ADR-0036-pre-seal-validation-binds-an-explicit-subject.md":
        return "Structural decision for exact detached pre-seal subject validation."
    if path.startswith("services/evaluator/"):
        return "Durable cancellation enforcement and regressions close the repeated non-terminal cancellation class."
    if path.startswith("scripts/development-ledger/"):
        return "Ledger production, sealing, validation or adversarial controls for G4-F-004."
    if path.startswith("tests/"):
        return "Automated regressions prevent stale review declarations and invalid detached subject binding."
    if path == "docs/checkpoints/LATEST.md":
        return "Canonical pointer advanced to the Gate 4 corrective successor."
    if path.startswith("docs/checkpoints/GATE-4-CP-0009/audit-harness/"):
        return "Reproducible corrective-run evidence harness."
    if path.startswith("docs/checkpoints/GATE-4-CP-0009/"):
        return "Gate 4 corrective evidence, assurance record or review handoff artifact."
    return "Declared Gate 4 corrective change required to close G4-F-004."


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
        for line in str(git("diff", "--name-only", BASE)).splitlines() if line.strip()
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
            ["git", "cat-file", "-e", f"{BASE}:{path}"], cwd=ROOT,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False,
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
            {"path": "docs/checkpoints/GATE-4-CP-0008/STATE.json", "reason": "Immutable audit state."},
            {"path": "docs/checkpoints/GATE-4-CP-0008/HANDOFF.md", "reason": "Finding and corrective handoff."},
            {"path": "docs/checkpoints/GATE-4-CP-0008/FINDINGS.json", "reason": "Canonical G4-F-004 source."}
        ],
        "filesCreated": created,
        "filesModified": modified,
        "filesDeleted": deleted,
    }
    (CHECKPOINT / "FILES.json").write_text(
        json.dumps(document, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(
        f"INVENTORY_DECLARED created={len(created)} modified={len(modified)} "
        f"deleted={len(deleted)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
