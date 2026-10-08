#!/usr/bin/env python3
"""Declare every changed path of GATE-3-CP-0005 with an explicit reason."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
BASE = "1fad2bec08a797d9641ad2b9c3092f6078af2d61"

REASONS = {
    ".iacode/anchors/checkpoint-chain.json": "Anchors sealed predecessor GATE-3-CP-0004.",
    ".iacode/memory/LESSONS.md": "Canonical index rendered from the updated engineering memory.",
    ".iacode/memory/guardrails/registry.json": "Registers GRD-0058 and strengthens GRD-0042 after its recorded recurrence.",
    ".iacode/memory/lessons.jsonl": "Records LSN-0057 and the resolved GRD-0042 guardrail failure.",
    ".iacode/policies/audit-registry.json": "Registers M1-CP-0004 against this corrective checkpoint.",
    "apps/web/package.json": "M1-F-004: coordinated direct Angular 22 security updates.",
    "apps/web/package-lock.json": "M1-F-004: clean npm 12 resolution of the corrected frontend graph.",
    "docs/checkpoints/LATEST.md": "Points to GATE-3-CP-0005.",
    "scripts/development-ledger/policies.py": "Parses both singular and plural sealed finding sections.",
    "tests/test_development_ledger.py": "Holds the sealed singular finding rendering fixed.",
    "tests/test_gate3_sandbox.py": "Guards the advisory denominator and correct preserved-reference subject selection.",
}

CHECKPOINT_REASONS = {
    "COMPLETENESS-REPORT.json": "Machine-readable delivery completeness audit.",
    "COMPLETENESS-REPORT.md": "Readable delivery completeness audit.",
    "COUNTS.json": "Counts derived from canonical test, requirement, finding and attack sources.",
    "CLOSURE-REQUIREMENTS.json": "Derived closure requirement set with evidence and final status.",
    "CLOSURE-REQUIREMENTS.md": "Readable rendering of the closure requirements.",
    "COMMANDS.jsonl": "Append-only command ledger of this run.",
    "DECISIONS.md": "Decisions taken by this corrective delivery.",
    "DEPENDENCY-SCAN-BASELINE.json": "Reproducible two-Critical/four-High baseline for M1-F-004.",
    "DEPENDENCY-SCAN-REPORT.json": "Clean scan of both npm and PyPI after the correction.",
    "DIFF-SUMMARY.md": "Summary of the corrective change set.",
    "FINAL-REPORT.md": "Closing report of this corrective delivery.",
    "FILES.json": "The declared change inventory itself.",
    "HANDOFF.md": "Handoff for the later independent M1 audit.",
    "LESSON-PREFLIGHT.json": "Machine-readable lesson preflight after memory stabilization.",
    "LESSON-PREFLIGHT.md": "Readable rendering of the lesson preflight.",
    "M1-CP-0004-FINDINGS-CLOSURE.json": "Machine-readable closure of M1-F-004.",
    "M1-CP-0004-FINDINGS-CLOSURE.md": "Readable closure of M1-F-004.",
    "M1-INTERNAL-MIRROR.json": "Machine-readable internal milestone closure audit.",
    "M1-INTERNAL-MIRROR.md": "Readable internal milestone closure audit.",
    "M1-INTERNAL-RED-TEAM.json": "Machine-readable internal Gate 3 adversarial battery.",
    "NEXT.md": "The next allowed action; Gate 4 remains prohibited.",
    "PLAN.md": "Frozen plan written before the dependency update.",
    "PRESERVED-REFERENCE-PROBE.json": "Diagnostic proof for the GRD-0042 subject-selection recurrence.",
    "PROVENANCE.json": "Provenance and rights record for this checkpoint.",
    "QUALITY.json": "Quality dimensions and their evidence.",
    "REQUIREMENTS-MATRIX.json": "Canonical 198-row requirement matrix.",
    "REQUIREMENTS-MATRIX.md": "Readable requirement matrix.",
    "REWORK-LOG.jsonl": "Green Keeper cycles for this delivery.",
    "RED-TEAM-REPORT.md": "Readable internal Red Team report.",
    "RISKS.md": "Residual risks of the correction.",
    "RUN-METADATA.json": "Tool, provider, model and environment metadata.",
    "STATE.json": "Machine-readable checkpoint state.",
    "STATUS.md": "Canonical checkpoint status.",
    "TESTS.json": "Test execution summary for this checkpoint.",
    "VERIFICATION-REPORT.json": "Latest complete-verification report.",
}

HARNESS_REASONS = {
    "declare_inventory.py": "Declares every changed path and refuses an unclassified path.",
    "prepare_closure.py": "Builds the finding closure, requirement evidence and derived checkpoint state.",
    "preserved_reference_probe.py": "Diagnoses preserved-reference ownership and published reachability.",
    "refresh_inventory.py": "Rebinds hashes only for paths already declared in FILES.json.",
    "record_dependency_lesson.py": "Records and guards LSN-0057 from M1-F-004.",
    "record_port_forwarding_lesson.py": (
        "Records the confirmed Docker Desktop host-port failure and its live-test guardrail."
    ),
    "record_preflight_scope_lesson.py": (
        "Records the confirmed implicit lesson-exclusion failure and its preflight guardrail."
    ),
    "regenerate_web_lock.ps1": "Regenerates the npm lock from a clean temporary directory without peer overrides.",
    "repair_preserved_guardrail.py": "Records and resolves the GRD-0042 subject-selection failure.",
    "sync_assurance.py": "Synchronizes audited assurance results into STATE, QUALITY and TESTS.",
}


def changed() -> list[tuple[str, str]]:
    entries: dict[str, str] = {}
    committed = subprocess.run(["git", "diff", "--name-status", BASE, "HEAD"], cwd=ROOT,
                               capture_output=True, text=True, encoding="utf-8", check=True).stdout
    for line in committed.splitlines():
        status, _, path = line.partition("\t")
        if path.strip():
            entries[path.strip().replace("\\", "/")] = {
                "A": "created", "D": "deleted"}.get(status[:1], "modified")
    status = subprocess.run(["git", "status", "--porcelain=v1", "--untracked-files=all"],
                            cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
                            check=True).stdout
    for line in status.splitlines():
        code, path = line[:2], line[3:].strip().replace("\\", "/")
        if path.startswith('"'):
            path = json.loads(path)
        if path in entries:
            continue
        exists_at_base = subprocess.run(["git", "cat-file", "-e", f"{BASE}:{path}"], cwd=ROOT,
                                        capture_output=True, check=False).returncode == 0
        entries[path] = "deleted" if "D" in code else ("modified" if exists_at_base else "created")
    return sorted((kind, path) for path, kind in entries.items())


def reason_for(path: str) -> str | None:
    if path in REASONS:
        return REASONS[path]
    prefix = f"docs/checkpoints/{CHECKPOINT.name}/"
    if path.startswith(prefix + "delivery-harness/"):
        return HARNESS_REASONS.get(path[len(prefix + "delivery-harness/"):])
    if path.startswith(prefix):
        return CHECKPOINT_REASONS.get(path[len(prefix):])
    return None


def main() -> int:
    groups = {"created": [], "modified": [], "deleted": []}
    undeclared: list[str] = []
    for kind, path in changed():
        reason = reason_for(path)
        if reason is None:
            undeclared.append(path)
        else:
            groups[kind].append({"path": path, "reason": reason})
    sys.path.insert(0, str(ROOT / "scripts" / "development-ledger"))
    from ledger_common import write_json
    write_json(CHECKPOINT / "FILES.json", {
        "filesRead": [], "filesCreated": groups["created"],
        "filesModified": groups["modified"], "filesDeleted": groups["deleted"],
    })
    print(f"declared created={len(groups['created'])} modified={len(groups['modified'])} "
          f"deleted={len(groups['deleted'])}")
    for path in undeclared:
        print(f"UNDECLARED {path}")
    return 0 if not undeclared else 1


if __name__ == "__main__":
    raise SystemExit(main())
