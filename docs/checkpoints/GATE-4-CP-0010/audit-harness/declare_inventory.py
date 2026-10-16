#!/usr/bin/env python3
"""Declare the complete CP0010 delta with authored reasons and canonical hashes."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
BASE = "ff2814f7d7bf06fa8a99858b958daf3f22197496"
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
        return "Anchor immutable sealed predecessor CP0009; historical anchors are preserved."
    if path.startswith(".iacode/memory/"):
        return "Record the internal audit findings, cancellation recurrence and executed guardrails."
    if path == ".iacode/schemas/memory-policy.schema.json":
        return "Version strict internal-verdict semantics without retroactively invalidating sealed subject policies."
    if path in {".iacode/policies/program-state.json", ".iacode/schemas/program-state.schema.json", "docs/program/README.md"}:
        return "Version a generated current resumability pointer without self-referential commits or rewriting historical observations."
    if path == ".iacode/policies/secret-scan-allowlist.json":
        return "Review only two exact decoded alphabet-sequence redaction-fixture component digests from immutable public test history."
    if path in {".iacode/policies/test-suites.json", ".iacode/schemas/test-suites.schema.json"}:
        return "Bind test counts and evidence to canonical runner collection; live input scenarios remain mandatory."
    if path in {".iacode/policies/canonical-requirements.json", "docs/GATE-4-CHECKLIST.md"}:
        return "Reconcile authorized Gate 4 closure and truthful resumability evidence without dropping any requirement row."
    if path.startswith("services/evaluator/"):
        return "Close durable cancellation races and prove early output containment with causal fixtures and evidence regressions."
    if path.startswith("services/sandbox/"):
        return "Close the Gate 4 integration defect at the earlier sandbox output and durable artifact boundaries."
    if path.startswith("apps/api/"):
        return "Prove canonical JSON transport detection and report late cancellation conflicts without workflow signals."
    if path.startswith("tests/") or path.startswith("scripts/development-ledger/"):
        return "Prove and enforce honest internal closure without self-asserted independent verdicts."
    if path.startswith("scripts/iacode/") or path.startswith("packages/common/"):
        return "Implement and prove canonical output containment at every Gate 4 durable integration boundary."
    if path.startswith("docs/adr/"):
        return "Atomically record and index cadence, cancellation, output-durability and count-policy decisions."
    if path == "docs/runbooks/QUALITY-ENGINE.md":
        return "Document cancellation acceptance, fail-closed recovery and the first durable output boundary."
    if path == "docs/ARCHITECTURE.md":
        return "Document actual sandbox output containment before evaluator and Temporal durability."
    if path == "docs/checkpoints/LATEST.md":
        return "Advance the live pointer to the internal corrective audit, preserving sealed CP0009."
    if path.startswith("docs/checkpoints/GATE-4-CP-0010/"):
        return "Declare reproducible Gate 4 internal review, correction, assurance and closure evidence."
    if path in {"START-HERE.md", "AGENTS.md", "CLAUDE.md",
                "docs/CHECKPOINT-PROTOCOL.md", "docs/DEFINITION-OF-DONE.md",
                "docs/DEVELOPMENT-CONTRACT.md", "docs/HANDOFF-PROTOCOL.md", "docs/QUALITY-GATES.md",
                "docs/MASTER-PLAN.md", "docs/ROADMAP.md", "docs/ENGINEERING-MEMORY.md"}:
        return "Align live contracts and tool adapters with the owner-authorized intermediate milestone cadence."
    raise RuntimeError(f"no authored Gate 4 inventory reason for {path!r}")


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
            {"path": "docs/checkpoints/GATE-4-CP-0009/STATE.json", "reason": "Immutable sealed subject state."},
            {"path": "docs/checkpoints/GATE-4-CP-0009/HANDOFF.md", "reason": "Sealed subject handoff."},
            {"path": "docs/checkpoints/GATE-4-CP-0009/G4-CP-0008-FINDINGS-CLOSURE.json", "reason": "Sealed G4-F-004 closure source."}
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
