#!/usr/bin/env python3
"""Declare the change set of this checkpoint, one entry per path, with the reason it changed.

The tooling binds the hashes; it never invents a declaration. Every path is enumerated from Git and
matched against a reason written here, so an undeclared change fails loudly instead of being
absorbed by a catch-all.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
BASE = "90b67a7e0a11179465bc5c92dee22c78da36801f"

REASONS = {
    ".iacode/anchors/checkpoint-chain.json":
        "The tenth integrity anchor, for SETUP-00-CP-0010, which its own checkpoint could not "
        "write and which its successor owes it.",
    ".iacode/attestations/M0-CP-0011.json":
        "The attestation this audit authored about the sealed subject it judged.",
    "docs/checkpoints/LATEST.md":
        "Points at this checkpoint.",
}

CHECKPOINT_REASONS = {
    "AUDIT-EXECUTIONS.json": "Machine-readable record of every execution this audit performed.",
    "AUDIT-EXECUTIONS.md": "Readable rendering of the execution record.",
    "CLOSURE-REQUIREMENTS.json": "Milestone closure requirements of this checkpoint.",
    "CLOSURE-REQUIREMENTS.md": "Readable rendering of the closure requirements.",
    "COMMANDS.jsonl": "Append-only command ledger of this run.",
    "COMPLETENESS-REPORT.json": "Delivery completeness audit of this checkpoint.",
    "COMPLETENESS-REPORT.md": "Readable rendering of the completeness audit.",
    "COUNTS.json": "Every count this checkpoint uses as evidence, derived once.",
    "DECISIONS.md": "Decisions taken by this audit.",
    "DIFF-SUMMARY.md": "Summary of the change set.",
    "FILES.json": "The declared inventory itself.",
    "FINAL-M0-AUDIT-MATRIX.json": "The audit matrix, rebuilt from the execution record.",
    "FINAL-M0-AUDIT-MATRIX.md": "Readable rendering of the audit matrix.",
    "FINAL-REPORT.md": "Closing report of this audit.",
    "HANDOFF.md": "Handoff for the next run.",
    "LESSON-PREFLIGHT.json": "Lesson preflight for the independent-audit scope.",
    "LESSON-PREFLIGHT.md": "Readable rendering of the preflight.",
    "M0-INTERNAL-MIRROR.json": "Internal mirror audit of this checkpoint.",
    "M0-INTERNAL-MIRROR.md": "Readable rendering of the internal mirror audit.",
    "M0-INTERNAL-RED-TEAM.json": "Internal adversarial battery of this checkpoint.",
    "M0-INTERNAL-RED-TEAM.md": "Readable rendering of the internal battery.",
    "MILESTONE-REPORT.md": "The milestone verdict and what supports it.",
    "NEXT.md": "The exact next allowed action.",
    "PLAN.md": "The audit plan, written before execution.",
    "PROVENANCE.json": "Provenance and rights of the artifacts produced here.",
    "QUALITY.json": "Quality dimensions of this checkpoint with their evidence.",
    "RED-TEAM-REPORT.md": "The adversarial battery this audit owns, and its null-mutation control.",
    "REQUIREMENTS-MATRIX.json": "Requirement matrix of this checkpoint.",
    "REQUIREMENTS-MATRIX.md": "Readable rendering of the requirement matrix.",
    "RESUME-VALIDATION.md": "Cold-start and clean-clone validation of this audit.",
    "REVIEW-REPORT.md": "The independent review verdict and its basis.",
    "REWORK-LOG.jsonl": "Green Keeper cycles of this checkpoint.",
    "RISKS.md": "Risks this audit records.",
    "RUN-METADATA.json": "Tool, provider, model, environment and timestamps of this run.",
    "STATE.json": "Machine-readable state of this checkpoint.",
    "STATUS.md": "The canonical status.",
    "TESTS.json": "Test execution recorded for this checkpoint.",
}

HARNESS_REASONS = {
    "RESULTS.jsonl": "Append-only record of audit results, which the matrix is rebuilt from.",
    "attack_battery.py": "The adversarial battery this audit owns.",
    "build_executions.py": "Assembles the machine-readable execution record.",
    "build_matrix.py": "Rebuilds the audit matrix from the derived rows and the result record.",
    "build_snapshot.py": "Builds the sealed snapshot of this checkpoint that the battery attacks.",
    "complete_matrix.py": "Completes the requirement matrix of this checkpoint from audit evidence.",
    "declare_inventory.py": "Declares this change set.",
    "derive_expected.py": "Independent derivation of the expected requirement set.",
    "matrix_rows.py": "Derives the rows of the audit matrix.",
    "record.py": "Appends one audit result record.",
    "render_red_team.py": "Renders the battery results into the checkpoint artifacts.",
    "resolve_evidence.py": "Independent resolution of every declared evidence reference.",
    "run_named.py": "Executes named test identifiers and reports each outcome separately.",
    "run_suite.py": "Executes the whole suite and reports passes, failures, errors and skips.",
}


def changed() -> list[tuple[str, str]]:
    out = subprocess.run(
        ["git", "status", "--porcelain=v1", "--untracked-files=all"],
        cwd=ROOT, capture_output=True, text=True, check=True).stdout
    entries: list[tuple[str, str]] = []
    for line in out.splitlines():
        if not line.strip():
            continue
        code, path = line[:2], line[3:].strip().replace("\\", "/")
        if path.startswith('"') and path.endswith('"'):
            path = json.loads(path)
        if code.strip() in ("??", "A"):
            entries.append(("created", path))
        elif "D" in code:
            entries.append(("deleted", path))
        else:
            entries.append(("modified", path))
    expanded: list[tuple[str, str]] = []
    for kind, path in entries:
        target = ROOT / path
        if target.is_dir():
            for item in sorted(target.rglob("*")):
                if item.is_file() and "__pycache__" not in item.parts:
                    expanded.append((kind, str(item.relative_to(ROOT)).replace("\\", "/")))
        else:
            expanded.append((kind, path))
    return expanded


def reason_for(path: str) -> str | None:
    if path in REASONS:
        return REASONS[path]
    prefix = f"docs/checkpoints/{CHECKPOINT.name}/"
    if path.startswith(prefix + "audit-harness/"):
        return HARNESS_REASONS.get(path[len(prefix + "audit-harness/"):])
    if path.startswith(prefix):
        return CHECKPOINT_REASONS.get(path[len(prefix):])
    return None


def bind_hashes(document: dict) -> None:
    """Bind every declared path to the content it names, the way the tooling does at finalization.

    Hashes are bound here as well as at finalization, because the gates run against an uncommitted
    tree and a checkpoint whose inventory does not describe its own content cannot be validated.
    """
    sys.path.insert(0, str(ROOT / "scripts" / "development-ledger"))
    from ledger_common import blob_hash, canonical_hash_path

    for key, before, after in (("filesCreated", False, True),
                               ("filesModified", True, True),
                               ("filesDeleted", True, False)):
        for entry in document[key]:
            path = entry["path"]
            if path.endswith("/FILES.json"):
                entry.pop("hashBefore", None)
                entry.pop("hashAfter", None)
                continue
            if before:
                digest = blob_hash(ROOT, BASE, path)
                if digest is not None:
                    entry["hashBefore"] = digest
            if after and (ROOT / path).is_file():
                entry["hashAfter"] = canonical_hash_path(ROOT / path)


def main() -> int:
    created: list[dict] = []
    modified: list[dict] = []
    deleted: list[dict] = []
    undeclared: list[str] = []
    for kind, path in changed():
        reason = reason_for(path)
        if reason is None:
            undeclared.append(path)
            continue
        entry = {"path": path, "reason": reason}
        if kind == "created":
            created.append(entry)
        elif kind == "deleted":
            deleted.append(entry)
        else:
            modified.append(entry)

    document = {
        "filesRead": [],
        "filesCreated": sorted(created, key=lambda item: item["path"]),
        "filesModified": sorted(modified, key=lambda item: item["path"]),
        "filesDeleted": sorted(deleted, key=lambda item: item["path"]),
    }
    bind_hashes(document)
    (CHECKPOINT / "FILES.json").write_text(
        json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"INVENTORY created={len(created)} modified={len(modified)} deleted={len(deleted)} "
          f"undeclared={len(undeclared)}")
    for path in undeclared:
        print(f"- undeclared: {path}")
    return 0 if not undeclared else 1


if __name__ == "__main__":
    raise SystemExit(main())
