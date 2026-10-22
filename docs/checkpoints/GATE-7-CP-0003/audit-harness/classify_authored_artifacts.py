"""Classify actual corrective control assets without inferring reuse rights."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(
    0, str(Path(__file__).resolve().parents[1].parents[2] / "scripts/development-ledger")
)
from ledger_common import load_json, write_json

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]

ASSETS = (
    "tests/test_m2_continuation.py",
    "docs/checkpoints/M2-CONSOLIDATION.md",
    ".gitattributes",
    "scripts/development-ledger/new_checkpoint.py",
    "scripts/development-ledger/audit_runner_bridge.py",
    "scripts/development-ledger/m0_red_team.py",
    "scripts/iacode/client_checks.py",
    "scripts/iacode/gates/client_tests.py",
    "scripts/iacode/native_editor.py",
    "scripts/iacode/native_execution.py",
    "tests/test_m2_audit_corrections.py",
    "tests/test_m2_closed_runner_bridge.py",
    "tests/test_m2_owned_resource_cleanup.py",
    "tests/test_m2_native_observation.py",
    "tests/test_m2_bridge_physical_bounds.py",
    "tests/test_m2_cleanup_operator.py",
    "tests/test_m2_current_stream_bootstrap.py",
    "tests/test_m2_observation_transport.py",
    "tests/test_m2_bootstrap_ownership.py",
    "tests/test_m2_progress_publication.py",
    "docs/adr/ADR-0061-client-verification-preserves-producer-and-cleanup-outcomes.md",
    "docs/adr/ADR-0062-isolated-audit-uses-closed-host-validation-jobs.md",
    "docs/checkpoints/GATE-7-CP-0003/audit-harness/owned_docker_scope.py",
    "docs/checkpoints/GATE-7-CP-0003/audit-harness/current_resources.py",
    "docs/checkpoints/GATE-7-CP-0003/audit-harness/test_resource_phase.py",
    "docs/checkpoints/GATE-7-CP-0003/audit-harness/authored_python_quality.py",
    "docs/checkpoints/GATE-7-CP-0003/audit-harness/publish_progress.py",
    "docs/checkpoints/GATE-7-CP-0003/audit-harness/register_authored_style.py",
    "docs/checkpoints/GATE-7-CP-0003/audit-harness/normalize_authored_layout.py",
    "docs/checkpoints/GATE-7-CP-0003/audit-harness/close_authored_style.py",
    "docs/checkpoints/GATE-7-CP-0003/audit-harness/close_continuation_guard.py",
    "docs/checkpoints/GATE-7-CP-0003/audit-harness/probe_current_continuation.py",
    "docs/checkpoints/GATE-7-CP-0003/audit-harness/register_continuation_recurrence.py",
)


def main():
    path = CHECKPOINT / "PROVENANCE.json"
    value = load_json(path)
    existing = {row["artifact"] for row in value["artifacts"]}
    for asset in ASSETS:
        if not (ROOT / asset).is_file():
            raise ValueError("Classification requires an actual asset")
        if asset not in existing:
            value["artifacts"].append(
                {
                    "artifact": asset,
                    "sourceType": "repository-source correction or AI-assisted control asset",
                    "provider": "OpenAI / project repository",
                    "model": "not-exposed",
                    "ownership": "existing project source and project-generated corrective delta",
                    "license": "project-policy; no additional license grant inferred",
                    "rights": {
                        "storageAllowed": True,
                        "ragAllowed": False,
                        "trainingAllowed": False,
                        "distillationAllowed": False,
                    },
                    "evidence": (
                        "AUTHORIZATION.md, OWNER-DECISIONS.json, COMMANDS.jsonl and FILES.json"
                    ),
                    "notes": (
                        "Storage for authorized engineering delivery only; denied reu"
                        "se remains denied. No private reasoning, credentials or vend"
                        "or runtime binaries are included."
                    ),
                }
            )
    write_json(path, value)
    print("AUTHORED_ASSETS_CLASSIFIED storage-only=" + str(len(ASSETS)))
    return 0


if __name__ == "__main__":
    from ledger_common import use_utf8_stdout

    use_utf8_stdout()
    raise SystemExit(main())
