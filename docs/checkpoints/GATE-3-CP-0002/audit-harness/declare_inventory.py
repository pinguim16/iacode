#!/usr/bin/env python3
"""Declare the change set of this audit checkpoint, one entry per path, with its reason.

The tooling binds the hashes; it never invents a declaration. Every path is enumerated from Git and
matched against a reason written here, so an undeclared change fails loudly instead of being
absorbed by a catch-all. The audit changes no product code, so every path outside this checkpoint
is named individually.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
BASE = "3bc8e9d8a94d44163d1af9325ad5b2272f71f8ed"

REASONS = {
    ".iacode/anchors/checkpoint-chain.json":
        "The eighteenth integrity anchor, for the sealed subject GATE-3-CP-0001, which its own "
        "checkpoint could not write and which its successor owes it.",
    ".iacode/attestations/M1-CP-0002.json":
        "The attestation this fresh-session audit authored about the sealed subject it judged.",
    "docs/checkpoints/LATEST.md":
        "Points at this audit checkpoint.",
}

CHECKPOINT_REASONS = {
    "AUDIT-EXECUTIONS.json": "Machine-readable record of every execution this audit performed.",
    "CLOSURE-REQUIREMENTS.json": "Milestone closure requirements of this checkpoint.",
    "CLOSURE-REQUIREMENTS.md": "Readable rendering of the closure requirements.",
    "COMMANDS.jsonl": "Append-only command ledger of this run.",
    "COMPLETENESS-REPORT.json": "Delivery completeness audit of this checkpoint.",
    "COMPLETENESS-REPORT.md": "Readable rendering of the completeness audit.",
    "COUNTS.json": "Every count this checkpoint uses as evidence, derived once.",
    "CROSS-GATE-LIVE.json":
        "The fourth live attempt (cmd-0016), an explicitly chosen model: task, Agent Runtime, "
        "Model Gateway, tool requests, sandbox, tool results and back, read from what the stack "
        "recorded.",
    "CROSS-GATE-LIVE-ATTEMPT-2.json":
        "The second live attempt (cmd-0014), the operator's configured model: the developer "
        "stage never produced a valid tool request.",
    "CROSS-GATE-LIVE-ATTEMPT-3.json":
        "The third live attempt (cmd-0015), the configured model again: the same failure.",
    "DECISIONS.md": "Decisions taken by this audit.",
    "DIFF-SUMMARY.md": "Summary of the change set.",
    "FILES.json": "The declared inventory itself.",
    "FINAL-M1-AUDIT-MATRIX.json": "The eighteen frozen M1 criteria with their observed results.",
    "FINAL-M1-AUDIT-MATRIX.md": "Readable rendering of the M1 audit matrix.",
    "FINAL-REPORT.md": "Closing report of this audit.",
    "HANDOFF.md": "Handoff for the next run.",
    "LESSON-PREFLIGHT.json": "Lesson preflight for the independent-audit scope.",
    "LESSON-PREFLIGHT.md": "Readable rendering of the preflight.",
    "M1-INTERNAL-MIRROR.json": "Internal mirror audit of this checkpoint.",
    "M1-INTERNAL-MIRROR.md": "Readable rendering of the internal mirror audit.",
    "M1-INTERNAL-RED-TEAM.json": "The focused cross-gate adversarial battery this audit owns.",
    "MILESTONE-REPORT.md": "The consolidated M1 milestone report and the verdict it supports.",
    "NEXT.md": "The exact next allowed action.",
    "PLAN.md": "The audit plan, written before execution.",
    "PROVENANCE.json": "Provenance and rights of the artifacts produced here.",
    "QUALITY.json": "Quality dimensions of this checkpoint with their evidence.",
    "R-G3-001-REVIEW.json":
        "The explicit review of the container engine socket held by the sandbox controller.",
    "R-G3-001-REVIEW.md": "Readable rendering of the R-G3-001 review and its disposition.",
    "RED-TEAM-REPORT.md": "The cross-gate adversarial battery and its null-mutation control.",
    "REQUIREMENTS-MATRIX.json": "Requirement matrix of this checkpoint.",
    "REQUIREMENTS-MATRIX.md": "Readable rendering of the requirement matrix.",
    "RESUME-VALIDATION.md": "Cold-start, sealed-subject and clean-clone validation of this audit.",
    "REVIEW-REPORT.md": "The independent review verdict and its basis.",
    "REWORK-LOG.jsonl": "Green Keeper cycles of this checkpoint.",
    "RISKS.md": "Risks this audit records.",
    "RUN-METADATA.json": "Tool, provider, model, environment and timestamps of this run.",
    "SEALED-SUBJECTS.json":
        "Validation of every sealed checkpoint of M1 from its own canonical tag, detached.",
    "SEALED-SUBJECTS-PUBLISHED.json":
        "Validation of every sealed M1 checkpoint from a clone of the published remote, which "
        "carries only what published references reach.",
    "STATE.json": "Machine-readable state of this checkpoint.",
    "STATUS.md": "The canonical status.",
    "TESTS.json": "Test execution recorded for this checkpoint.",
    "VERIFICATION-REPORT.json": "The full verification run by this audit over the audited tree.",
    "CLEAN-CLONE-REPORT.json": "The full verification run by this audit in a fresh clone.",
    "FINDINGS.json": "The findings of this review, with severity, status and disposition.",
    "FORGED-RESULT-PROBE.json":
        "The reproduction of finding M1-F-001 on the stack, with its null control.",
}

HARNESS_REASONS = {
    "EXECUTIONS.jsonl":
        "Append-only record of executions, which AUDIT-EXECUTIONS.json is built from.",
    "declare_inventory.py": "Declares this change set.",
    "executions.py": "Appends one execution record and assembles the execution artifact.",
    "sealed_subjects.py": "Validates every sealed M1 checkpoint from its own tag, detached.",
    "cross_gate_live.py":
        "Drives one live coding run through the deployed stack and reads back what it recorded.",
    "r_g3_001.py": "Probes the controls that bound the engine socket the sandbox service holds.",
    "red_team.py": "The focused cross-gate adversarial battery this audit owns.",
    "m1_sandbox_attacks.py": "The in-image half of the battery, against the real engine.",
    "probe_forged_result.py": "Reproduces finding M1-F-001 on the stack with a null control.",
    "clean_clone.py": "Re-runs the mandatory validations and the full verification in a fresh clone.",
    "build_matrix.py": "Builds the M1 audit matrix from the frozen criteria and the executions.",
    "sync_state.py": "Copies the derived counts into STATE.json from the artifacts that own them.",
    "complete_requirements.py":
        "Completes the requirement matrix from evidence this audit resolved itself.",
}


def changed() -> list[tuple[str, str]]:
    out = subprocess.run(
        ["git", "status", "--porcelain=v1", "--untracked-files=all"],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8", check=True).stdout
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
    # Committed changes since the base belong to the change set as well.
    committed = subprocess.run(
        ["git", "diff", "--name-status", BASE, "HEAD"],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8", check=True).stdout
    seen = {path for _kind, path in entries}
    for line in committed.splitlines():
        if not line.strip():
            continue
        status, _, path = line.partition("\t")
        path = path.strip().replace("\\", "/")
        if path in seen:
            continue
        seen.add(path)
        kind = {"A": "created", "D": "deleted"}.get(status[:1], "modified")
        entries.append((kind, path))
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
        {"created": created, "deleted": deleted}.get(kind, modified).append(entry)

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
