from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Bind FILES.json to the current Git delta.")
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--base", required=True)
    args = parser.parse_args()

    root = args.root.resolve()
    checkpoint = (root / args.checkpoint).resolve()
    sys.path.insert(0, str(root / "scripts" / "development-ledger"))
    from ledger_common import blob_hash, canonical_hash_path, git_delta  # noqa: PLC0415

    delta = git_delta(root, args.base, None)
    files_created: list[dict[str, str]] = []
    files_modified: list[dict[str, str]] = []
    files_deleted: list[dict[str, str]] = []
    own_path = str((checkpoint / "FILES.json").relative_to(root)).replace("\\", "/")
    reason = "Audit-only evidence or metadata for the fresh independent M2 review."
    prior_reason = (
        "Pre-existing authorized entry-blocked evidence preserved distinctly; not adopted as this "
        "auditor's verdict."
    )

    for path, letter in sorted(delta.items()):
        item: dict[str, str] = {
            "path": path,
            "reason": prior_reason
            if path.startswith("docs/audits/M2-ENTRY-BLOCKED-2026-10-21/")
            else reason,
        }
        if path != own_path and letter in {"A", "M"}:
            item["hashAfter"] = canonical_hash_path(root / path)
        if letter in {"M", "D"}:
            before = blob_hash(root, args.base, path)
            if before is None:
                raise RuntimeError(f"base blob is unavailable for {path}")
            item["hashBefore"] = before
        if letter == "A":
            files_created.append(item)
        elif letter == "M":
            files_modified.append(item)
        elif letter == "D":
            files_deleted.append(item)
        else:
            raise RuntimeError(f"unexpected delta letter {letter!r} for {path}")

    files_read = [
        {"path": "AGENTS.md", "reason": "Repository adapter and mandatory entry/closure order."},
        {"path": "START-HERE.md", "reason": "Canonical entry protocol."},
        {"path": "docs/DEVELOPMENT-CONTRACT.md", "reason": "Delivery and audit obligations."},
        {"path": "docs/MASTER-PLAN.md", "reason": "M2 scope and Gate boundary."},
        {"path": "docs/CHECKPOINT-PROTOCOL.md", "reason": "Checkpoint integrity and evidence rules."},
        {"path": "docs/MILESTONE-VALIDATION.md", "reason": "Independent milestone audit contract."},
        {"path": "docs/adr/ADR-0037-intermediate-gates-use-internal-closure.md", "reason": "Independent status semantics."},
        {"path": "docs/checkpoints/GATE-7-CP-0001/STATE.json", "reason": "Sealed subject state."},
        {"path": "docs/checkpoints/GATE-7-CP-0001/RISKS.md", "reason": "Mandatory risk review before Docker or cleanup."},
    ]
    inventory = {
        "filesRead": files_read,
        "filesCreated": files_created,
        "filesModified": files_modified,
        "filesDeleted": files_deleted,
    }
    (checkpoint / "FILES.json").write_text(
        json.dumps(inventory, indent=2) + "\n", encoding="utf-8"
    )
    print(
        "INVENTORY_WRITTEN "
        f"created={len(files_created)} modified={len(files_modified)} deleted={len(files_deleted)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
