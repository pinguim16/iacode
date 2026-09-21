#!/usr/bin/env python3
"""Consolidate every audit execution into the checkpoint's machine-readable evidence."""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path
import os as _os
from pathlib import Path as _Path
_DEFAULT_ROOT = _Path(__file__).resolve().parents[4]

AUDIT = Path(_os.environ.get("IACODE_AUDIT_OUT") or (_DEFAULT_ROOT / "audit-out"))
HARNESS = AUDIT / "harness"
CP = _DEFAULT_ROOT / "docs" / "checkpoints" / "SETUP-00-CP-0009"


def load(relative: str):
    path = AUDIT / relative
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else None


def tail(relative: str, lines: int = 12) -> list[str]:
    path = AUDIT / relative
    if not path.is_file():
        return []
    content = path.read_text(encoding="utf-8", errors="replace").splitlines()
    return [line[:400] for line in content[-lines:] if line.strip()]


def main() -> int:
    document = {
        "schemaVersion": "1.0.0",
        "checkpoint": "SETUP-00-CP-0009",
        "milestone": "M0",
        "subjectCheckpoint": "SETUP-00-CP-0008",
        "auditMechanism": "FRESH_SESSION_INDEPENDENT_AUDIT",
        "note": ("Every negative scenario ran inside a disposable clone or an in-memory copy "
                 "under the session scratchpad. No tag, commit or artifact of the real "
                 "repository was written to by any attack."),
        "coldStart": {
            "documentsRead": [
                "START-HERE.md", "AGENTS.md", "CLAUDE.md",
                "docs/DEVELOPMENT-CONTRACT.md", "docs/MASTER-PLAN.md", "docs/ROADMAP.md",
                "docs/DEFINITION-OF-DONE.md", "docs/QUALITY-GATES.md",
                "docs/HANDOFF-PROTOCOL.md", "docs/CHECKPOINT-PROTOCOL.md",
                "docs/SETUP-00-CHECKLIST.md", "docs/ENGINEERING-MEMORY.md",
                "docs/MILESTONE-VALIDATION.md", "docs/checkpoints/LATEST.md",
                "docs/adr/ADR-0010-milestone-closure-controls.md",
                ".iacode/attestations/README.md", ".iacode/policies/secret-policy.md",
                ".iacode/policies/quality-gates.json",
                ".iacode/policies/canonical-requirements.json",
                ".iacode/policies/audit-registry.json",
                ".iacode/memory/POLICY.json", ".iacode/memory/lessons.jsonl",
                ".iacode/memory/guardrails/registry.json",
                ".iacode/anchors/checkpoint-chain.json",
            ],
            "checkpointsRead": {
                "SETUP-00-CP-0007": ["REVIEW-REPORT.md", "RED-TEAM-REPORT.md",
                                     "MILESTONE-REPORT.md", "FINAL-REPORT.md", "HANDOFF.md",
                                     "STATE.json", "REQUIREMENTS-MATRIX.json"],
                "SETUP-00-CP-0008": ["STATUS.md", "STATE.json", "RUN-METADATA.json",
                                     "COUNTS.json", "CLOSURE-REQUIREMENTS.json",
                                     "CP7-FINDINGS-CLOSURE.json", "M0-INTERNAL-RED-TEAM.json",
                                     "M0-INTERNAL-MIRROR.json", "COMPLETENESS-REPORT.json",
                                     "LESSON-PREFLIGHT.json", "REQUIREMENTS-MATRIX.json",
                                     "REWORK-LOG.jsonl", "COMMANDS.jsonl", "FILES.json",
                                     "QUALITY.json", "HANDOFF.md", "NEXT.md", "FINAL-REPORT.md"],
            },
            "externalSummariesUsedAsEvidence": 0,
        },
        "expectedRequirementSet": load("expected-set.json"),
        "findingClosure": load("finding-tests.json"),
        "attackBattery": load("battery/attack-results.json"),
        "assuranceScenarios": load("scenarios/scenario-results.json"),
        "attestationProbes": load("attestation/attestation-results.json"),
        "externalPassReachability": load("work4/ext-reachability.json"),
        "preflightFreshness": load("preflight/preflight-results.json"),
        "previouslyBypassedGuardrails": load("guardrails/guardrail-results.json"),
        "engineeringMemory": load("memory/memory-results.json"),
        "historyIntegrity": load("history/history-results.json"),
        "semanticCounts": load("counts/counts-docs.json"),
        "commandAuditability": load("commands/command-audit.json"),
        "successorSuiteSimulation": load("successor-sim.json"),
        "executionTails": {
            "cleanCloneSuite": tail("clean-clone-tests.txt", 6),
            "findingRegressionTests": tail("finding-tests-run.txt", 6),
            "handoffCommands": tail("handoff-commands.txt", 8),
            "attackBatteryRun": tail("battery-run.txt", 3),
        },
    }
    (CP / "AUDIT-EXECUTIONS.json").write_text(json.dumps(document, indent=2) + "\n",
                                              encoding="utf-8", newline="\n")

    target = CP / "audit-harness"
    target.mkdir(parents=True, exist_ok=True)
    header = ('import os as _os\nfrom pathlib import Path as _Path\n'
              '_DEFAULT_ROOT = _Path(__file__).resolve().parents[4]\n')
    for name in sorted(HARNESS.glob("*.py")):
        text = name.read_text(encoding="utf-8")
        # The copies kept in the checkpoint resolve the repository from their own location, so the
        # audit reproduces from a clean clone without the session's absolute paths.
        text = text.replace(
            'ROOT = Path(_os.environ.get("IACODE_ROOT") or _DEFAULT_ROOT)',
            'ROOT = Path(_os.environ.get("IACODE_ROOT") or _DEFAULT_ROOT)')
        text = text.replace(
            'AUDIT = Path("C:/Users/cesar/AppData/Local/Temp/claude/E--iacode/"\n'
            '             "b305dd77-f117-4885-9aeb-0239c66d22e6/scratchpad/audit")',
            'AUDIT = Path(_os.environ.get("IACODE_AUDIT_OUT") or (_DEFAULT_ROOT / "audit-out"))')
        text = text.replace(
            'AUDIT = Path("C:/Users/cesar/AppData/Local/Temp/claude/E--iacode/"\n'
            '             "b305dd77-f117-4885-9aeb-0239c66d22e6/scratchpad/audit")\n'
            'CP = _DEFAULT_ROOT / "docs" / "checkpoints" / "SETUP-00-CP-0009"',
            'AUDIT = Path(_os.environ.get("IACODE_AUDIT_OUT") or (_DEFAULT_ROOT / "audit-out"))\n'
            'CP = _DEFAULT_ROOT / "docs" / "checkpoints" / "SETUP-00-CP-0009"')
        text = text.replace('CP = _DEFAULT_ROOT / "docs" / "checkpoints" / "SETUP-00-CP-0009"',
                            'CP = _DEFAULT_ROOT / "docs" / "checkpoints" / "SETUP-00-CP-0009"')
        lines = text.splitlines(keepends=True)
        for index, line in enumerate(lines):
            if line.startswith("from pathlib import Path"):
                lines.insert(index + 1, header)
                break
        (target / name.name).write_text("".join(lines), encoding="utf-8", newline="\n")
    print("AUDIT-EXECUTIONS.json written; harness files copied: "
          + str(len(list(target.glob('*.py')))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
