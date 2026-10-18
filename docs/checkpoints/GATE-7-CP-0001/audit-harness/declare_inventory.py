"""Declare the current delta using authored Gate-specific scope reasons; never grant a verdict."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))

from ledger_common import (
    canonical_hash_bytes, canonical_hash_path, load_json, use_utf8_stdout, write_json,
)


def git(*arguments: str, binary: bool = False) -> bytes | str:
    result = subprocess.run(["git", *arguments], cwd=ROOT, check=True, capture_output=True,
                            text=not binary, encoding=None if binary else "utf-8")
    return result.stdout


def reason(path: str) -> str:
    exact = {
        ".iacode/anchors/checkpoint-chain.json": "Anchor sealed Gate6; preserve every predecessor.",
        "docs/checkpoints/LATEST.md": "Point to the separately authorized Gate7 checkpoint.",
        "docs/GATE-7-CHECKLIST.md": "Define the complete canonical Knowledge Engine specification.",
        ".iacode/policies/canonical-requirements.json": "Register Gate7 without altering prior rows.",
        "START-HERE.md": "Align live entry with authorized Gate7 and pending M2 independent audit.",
        ".gitattributes": "Preserve new checkpoint producer bytes across actual Git transport.",
        "docs/adr/README.md": "Keep the canonical ADR index aligned with structural decisions.",
    }
    if path in exact:
        return exact[path]
    if path.startswith(CHECKPOINT.relative_to(ROOT).as_posix() + "/"):
        return "Record Gate7 authority, requirements, work and actual evidence with resumable M2 handoff."
    if path in {
        "docs/adr/ADR-0053-knowledge-requires-content-bound-source-permission.md",
        "docs/adr/ADR-0054-knowledge-indexes-are-rebuildable-cited-projections.md",
    }:
        return "Define the governed source, rights, index, citation and invalidation architecture."
    raise ValueError("a changed path has no authored Gate7 declaration: " + path)


def main() -> int:
    use_utf8_stdout()
    state = load_json(CHECKPOINT / "STATE.json")
    if subprocess.run(["git", "rev-parse", "--verify",
        f"refs/tags/iacode-checkpoints/{CHECKPOINT.name}"], cwd=ROOT,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False).returncode == 0:
        raise ValueError("never rewrite a sealed checkpoint")
    base = state["baseCommit"]
    changed = set(str(git("diff", "--name-only", base)).splitlines())
    changed.update(str(git("ls-files", "--others", "--exclude-standard")).splitlines())
    document = {"filesRead": [{"path": path, "reason": why} for path, why in (
        ("AGENTS.md", "Project adapter and mandatory repository contract."),
        ("START-HERE.md", "Canonical entry protocol."),
        ("docs/DEVELOPMENT-CONTRACT.md", "Scope and ordered delivery obligations."),
        ("docs/MASTER-PLAN.md", "Gate7 purpose and M2 boundary."),
        ("docs/MILESTONE-VALIDATION.md", "Separate independent milestone handoff/verdict."),
        ("docs/checkpoints/GATE-6-CP-0001/STATE.json", "Immutable predecessor Git/status binding."),
        ("docs/checkpoints/GATE-6-CP-0001/HANDOFF.md", "Predecessor evidence and safe continuation."),
        ("docs/checkpoints/GATE-6-CP-0001/RISKS.md", "Historical exclusions and residual limits."),
    )], "filesCreated": [], "filesModified": [], "filesDeleted": []}
    for path in sorted(changed):
        existed = subprocess.run(["git", "cat-file", "-e", f"{base}:{path}"], cwd=ROOT,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False).returncode == 0
        exists = (ROOT / path).is_file()
        category = "filesModified" if existed and exists else "filesDeleted" if existed else "filesCreated"
        row = {"path": path, "reason": reason(path)}
        if path != CHECKPOINT.relative_to(ROOT).as_posix() + "/FILES.json":
            if existed:
                row["hashBefore"] = canonical_hash_bytes(git("show", f"{base}:{path}", binary=True))
            if exists:
                row["hashAfter"] = canonical_hash_path(ROOT / path)
        document[category].append(row)
    write_json(CHECKPOINT / "FILES.json", document)
    print("INVENTORY_DECLARED " + " ".join(f"{key}={len(document[key])}" for key in
          ("filesCreated", "filesModified", "filesDeleted")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
