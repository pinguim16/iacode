"""Declare the complete GATE-4-CP-0005 delta before hash binding.

The checkpoint contract requires the implementing run to declare every path; the finalizer may
bind hashes but may not invent this inventory.  This script derives the path set from the sealed
base commit and assigns a review-facing reason by artifact class.  It is itself part of the
declared checkpoint evidence.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


CHECKPOINT = Path(__file__).resolve().parent
ROOT = CHECKPOINT.parents[2]
STATE = json.loads((CHECKPOINT / "STATE.json").read_text(encoding="utf-8"))
BASE = str(STATE["baseCommit"])
sys.path.insert(0, str(ROOT / "scripts" / "development-ledger"))

from ledger_common import use_utf8_stdout  # noqa: E402


def git(*arguments: str, check: bool = True) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["git", *arguments],
        cwd=ROOT,
        check=check,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def paths(output: bytes) -> set[str]:
    return {
        item.decode("utf-8").replace("\\", "/")
        for item in output.split(b"\0")
        if item
    }


def existed_at_base(path: str) -> bool:
    return git("cat-file", "-e", f"{BASE}:{path}", check=False).returncode == 0


def reason(path: str) -> str:
    if path.startswith("docs/checkpoints/GATE-4-CP-0005/"):
        return "Gate 4 G4-F-002 corrective checkpoint state, evidence, or reproducible declaration."
    if path.startswith(".iacode/memory/"):
        return "Engineering lesson, retrospective, or automated guardrail for G4-F-002 and the LSN-0049 recurrence."
    if path == ".iacode/anchors/checkpoint-chain.json":
        return "Integrity chain rebuilt to anchor the sealed GATE-4-CP-0004 predecessor."
    if path == ".iacode/policies/audit-registry.json":
        return "Register the sealed GATE-4-CP-0004 independent audit as the source of corrective work."
    if path.startswith("docs/adr/"):
        return "Architecture decision and index for checkout-owned verification runtime state."
    if path.startswith("docs/") or path == "README.md":
        return "Developer, architecture, and operations documentation for deterministic verification ownership."
    if path.startswith("infra/tests/"):
        return "Infrastructure verification now observes Prometheus through the bounded policy-derived scrape cycle."
    if path.startswith("scripts/development-ledger/"):
        return "Canonical structured-audit finding intake required to derive G4-F-002 without altering sealed history."
    if path.startswith("scripts/iacode/"):
        return "Checkout-owned verifier runtime, shared observability policy, diagnostics, or live order-isolation proof."
    if path.startswith("tests/"):
        return "Regression and guardrail coverage for structured finding intake and deterministic full verification."
    return "Gate 4 G4-F-002 corrective delivery artifact."


def main() -> None:
    use_utf8_stdout()
    changed = paths(git("diff", "--name-only", "-z", BASE, "--").stdout)
    changed.update(paths(git("ls-files", "--others", "--exclude-standard", "-z").stdout))

    created: list[dict[str, str]] = []
    modified: list[dict[str, str]] = []
    deleted: list[dict[str, str]] = []
    for path in sorted(changed):
        exists = (ROOT / path).is_file()
        at_base = existed_at_base(path)
        record = {"path": path, "reason": reason(path)}
        if exists and not at_base:
            created.append(record)
        elif exists and at_base:
            modified.append(record)
        elif at_base:
            deleted.append(record)
        else:
            raise RuntimeError(f"cannot classify changed path: {path}")

    document = {
        "filesRead": [
            {"path": "START-HERE.md", "reason": "Required repository entry point."},
            {"path": "docs/DEVELOPMENT-CONTRACT.md", "reason": "Canonical delivery contract."},
            {"path": "docs/MASTER-PLAN.md", "reason": "Authorized Gate and milestone scope."},
            {"path": "docs/GATE-4-CHECKLIST.md", "reason": "Canonical Gate 4 requirement source."},
            {"path": "docs/checkpoints/GATE-4-CP-0004/STATE.json", "reason": "Sealed predecessor state."},
            {"path": "docs/checkpoints/GATE-4-CP-0004/FINDINGS.json", "reason": "Independent G4-F-002 source."},
            {"path": "docs/checkpoints/GATE-4-CP-0004/GATE-4-INDEPENDENT-RED-TEAM.json", "reason": "Preserved independent 20/20 attack battery."},
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
        "FILES_DECLARED "
        f"created={len(created)} modified={len(modified)} deleted={len(deleted)}"
    )


if __name__ == "__main__":
    main()
