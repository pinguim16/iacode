#!/usr/bin/env python3
"""Create the next IACode checkpoint with safe, truthful defaults."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from ledger_common import (
    CURRENT_SCHEMA_VERSION,
    QUALITY_DIMENSIONS_V3,
    canonical_hash_path,
    milestone_for,
    STATUSES,
    find_root,
    git_snapshot,
    runtime_label,
    utc_now,
    write_json,
)


def next_checkpoint_name(root: Path, gate: str) -> str:
    checkpoints = root / "docs" / "checkpoints"
    pattern = re.compile(rf"^{re.escape(gate)}-CP-(\d{{4}})$")
    numbers = [int(match.group(1)) for item in checkpoints.iterdir() if item.is_dir() and (match := pattern.match(item.name))]
    return f"{gate}-CP-{max(numbers, default=0) + 1:04d}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path)
    parser.add_argument("--gate", required=True)
    parser.add_argument("--status", choices=tuple(status for status in STATUSES if status not in ("GATE_PASS", "GATE_FAIL")), default="IN_PROGRESS")
    parser.add_argument("--phase")
    args = parser.parse_args()

    root = find_root(args.root) if args.root else find_root()
    if re.fullmatch(r"[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*", args.gate) is None:
        parser.error("--gate must be an uppercase identifier such as SETUP-00 or GATE-0")
    snapshot = git_snapshot(root)
    name = next_checkpoint_name(root, args.gate)
    checkpoint = root / "docs" / "checkpoints" / name
    checkpoint.mkdir(parents=True, exist_ok=False)
    now = utc_now()
    phase = args.phase or args.gate
    planned = milestone_for(args.gate)

    markdown = {
        "STATUS.md": f"# Status\n\n{args.status}\n",
        "HANDOFF.md": (
            "# Handoff\n\nCurrent Gate: " + args.gate + "\nCurrent Status: " + args.status
            + "\n\nLast valid commit: " + snapshot["head"] + "\nCurrent branch: " + snapshot["branch"]
            + "\n\n## Objective\n\nPopulate verified handoff evidence before transfer."
            + "\n\n## What was completed\n\nCheckpoint creation only."
            + "\n\n## What was NOT completed\n\nGate work and validation."
            + "\n\n## Current repository state\n\nSee STATE.json."
            + "\n\n## Files changed\n\nSee FILES.json."
            + "\n\n## Important decisions\n\nSee DECISIONS.md."
            + "\n\n## Tests executed\n\nNone at checkpoint creation."
            + "\n\n## Known failures\n\nNone recorded at checkpoint creation."
            + "\n\n## Known risks\n\nSee RISKS.md."
            + "\n\n## Do not repeat\n\nDo not bypass checkpoint validation."
            + "\n\n## Required next action\n\nPopulate this checkpoint with observed evidence."
            + "\n\n## Exact continuation sequence\n\nRead, populate, test, and validate."
            + "\n\n## Validation commands\n\n`python scripts/development-ledger/validate_checkpoint.py`"
            + "\n\n## Stop conditions\n\nStop on divergence or failed validation.\n"
        ),
        "PLAN.md": "# Plan\n\nRecord an executable plan before implementation.\n",
        "DECISIONS.md": "# Decisions\n\nNo checkpoint-local decision has been recorded yet.\n",
        "DIFF-SUMMARY.md": "# Diff Summary\n\nNo changes have been summarized yet.\n",
        "RISKS.md": "# Risks\n\nNo checkpoint-local risk has been recorded yet.\n",
        "NEXT.md": "# Next\n\n## Required next action\n\nPopulate the exact next allowed action before finalization.\n",
    }
    for filename, content in markdown.items():
        (checkpoint / filename).write_text(content, encoding="utf-8")

    write_json(checkpoint / "STATE.json", {
        "schemaVersion": CURRENT_SCHEMA_VERSION,
        "phase": phase,
        "gate": args.gate,
        "status": args.status,
        "branch": snapshot["branch"],
        "baseCommit": snapshot["head"],
        "currentCommit": snapshot["head"],
        "dirty": True,
        "startedAt": now,
        "updatedAt": now,
        "nextAllowedAction": "Populate and validate this checkpoint.",
        "blockedBy": [],
        "secondToolValidation": {
            "status": "PENDING_MANUAL",
            "tool": None,
            "provider": None,
            "model": None,
            "validatedAt": None,
            "justification": None,
            "evidence": [],
        },
        "requirementsMatrix": {
            "path": "REQUIREMENTS-MATRIX.json",
            "total": 0, "mandatory": 0, "complete": 0, "partial": 0, "missing": 0,
            "notApplicable": 0, "coveragePercent": 0.0,
        },
        "greenKeeper": {
            "status": "NOT_EXECUTED", "cycles": 0, "remainingFailures": 0,
            "unresolvedReworkItems": 0, "log": "REWORK-LOG.jsonl",
            "externalBlockers": [], "evidence": [],
        },
        "deliveryCompleteness": {
            "status": "NOT_EXECUTED", "report": "COMPLETENESS-REPORT.json",
            "coveragePercent": 0.0, "evidenceCoveragePercent": 0.0,
            "auditor": None, "evidence": [],
        },
        "reworkCycles": 0,
        "independentReview": {"status": "PENDING", "tool": None, "reviewedAt": None,
                              "justification": None, "evidence": []},
        "redTeam": {"status": "PENDING", "tool": None, "executedAt": None,
                    "justification": None, "evidence": []},
        "lessonPreflight": {
            "path": "LESSON-PREFLIGHT.json", "gate": args.gate, "scope": None,
            "lessonsConsidered": 0, "lessonsApplicable": 0, "derivedRequirements": 0,
            "evidence": [],
        },
        "milestone": {
            "id": planned[0] if planned else "M0",
            "title": planned[1] if planned else None,
            "gates": list(planned[2]) if planned else [args.gate],
            "status": "PENDING", "auditor": None, "auditedAt": None, "evidence": [],
        },
        "externalAuditRequired": False,
        "externalAuditReason": None,
        "guardrailEffectiveness": {
            "guardrailsTotal": 0, "guardrailsResolved": 0, "guardrailsTested": 0,
            "guardrailsEffective": 0, "guardrailFailures": 0, "evidence": [],
        },
        "integrity": {
            "status": "NOT_EXECUTED", "anchors": 0,
            "chainFile": ".iacode/anchors/checkpoint-chain.json", "evidence": [],
        },
        "externalAttestation": {"status": "NONE", "path": None, "auditId": None, "evidence": []},
    })
    write_json(checkpoint / "RUN-METADATA.json", {
        "tool": "not-recorded",
        "toolVersion": "not-recorded",
        "provider": "not-recorded",
        "model": "not-recorded",
        "effort": "not-exposed",
        "operatingSystem": "not-recorded",
        "startedAt": now,
        "finishedAt": now,
        "branch": snapshot["branch"],
        "initialCommit": snapshot["head"],
        "finalCommit": snapshot["head"],
    })
    (checkpoint / "COMMANDS.jsonl").write_text(json.dumps({
        "id": "cmd-0001",
        "timestamp": now,
        "runtime": runtime_label("python"),
        "command": (
            "python scripts/development-ledger/new_checkpoint.py "
            f"--gate {args.gate} --status {args.status}"
        ),
        "arguments": ["scripts/development-ledger/new_checkpoint.py", "--gate", args.gate,
                      "--status", args.status],
        "inputs": ["scripts/development-ledger/new_checkpoint.py"],
        # The tool binds its own source by content when the repository ships it. A checkout that
        # does not vendor the tooling records ABSENT rather than inventing a digest.
        "inputsDigest": [{
            "path": "scripts/development-ledger/new_checkpoint.py",
            "hash": canonical_hash_path(root / "scripts/development-ledger/new_checkpoint.py")
            if (root / "scripts/development-ledger/new_checkpoint.py").is_file() else "ABSENT",
        }],
        "workingDirectory": str(root),
        "commit": snapshot["head"],
        "purpose": "Create the checkpoint skeleton with truthful non-PASS defaults.",
        "result": "COMPLETED",
        "resultCode": "OK",
        "exitCode": 0,
        "durationMs": 0,
        "stdoutArtifact": None,
        "stderrArtifact": None,
    }) + "\n", encoding="utf-8")
    write_json(checkpoint / "FILES.json", {"filesRead": [], "filesCreated": [], "filesModified": [], "filesDeleted": []})
    empty_test = {"executed": False, "passed": 0, "failed": 0, "command": None, "evidence": None}
    write_json(checkpoint / "TESTS.json", {"schemaVersion": CURRENT_SCHEMA_VERSION, "unit": empty_test, "integration": empty_test, "e2e": empty_test})
    write_json(checkpoint / "QUALITY.json", {
        "schemaVersion": CURRENT_SCHEMA_VERSION,
        "checks": {
            dimension: {"status": "NOT_EXECUTED", "evidence": [], "justification": None}
            for dimension in QUALITY_DIMENSIONS_V3
        },
    })
    (checkpoint / "REWORK-LOG.jsonl").write_text("", encoding="utf-8")
    write_json(checkpoint / "REQUIREMENTS-MATRIX.json", {
        "schemaVersion": "2.0.0", "gate": args.gate, "checkpoint": name, "requirements": [],
    })
    (checkpoint / "REQUIREMENTS-MATRIX.md").write_text(
        f"# Requirements Matrix - {name}\n\nExtract every requirement before implementation.\n",
        encoding="utf-8")
    write_json(checkpoint / "CLOSURE-REQUIREMENTS.json", {
        "schemaVersion": "1.0.0", "gate": args.gate, "checkpoint": name,
        "sources": ["Derive the expected set with derive_requirements.py before implementing."],
        "requirements": [],
    })
    (checkpoint / "CLOSURE-REQUIREMENTS.md").write_text(
        f"# Closure Requirements - {name}\n\n"
        "Derive the expected requirement set from the canonical sources before implementation:\n"
        "`python scripts/development-ledger/derive_requirements.py --write`.\n",
        encoding="utf-8")
    write_json(checkpoint / "PROVENANCE.json", {
        "schemaVersion": CURRENT_SCHEMA_VERSION,
        "artifacts": [{
            "artifact": str(checkpoint.relative_to(root)), "sourceType": "repository-generated",
            "provider": "local-script", "model": "not-applicable", "ownership": "project",
            "license": "project-policy", "rights": {"storageAllowed": True, "ragAllowed": False, "trainingAllowed": False, "distillationAllowed": False},
            "evidence": "Created by new_checkpoint.py.", "notes": "Review rights before reuse."
        }]
    })
    latest = root / "docs" / "checkpoints" / "LATEST.md"
    latest.write_text(f"# Latest Checkpoint\n\nCheckpoint: `docs/checkpoints/{name}`\n\nValidate before use.\n", encoding="utf-8")
    print(checkpoint)
    return 0


if __name__ == "__main__":
    sys.exit(main())
