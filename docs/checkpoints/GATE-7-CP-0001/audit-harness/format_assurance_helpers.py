"""Check the explicit current assurance-helper/regression scope with the pinned toolchain."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))
PREFIX = "docs/checkpoints/GATE-7-CP-0001/audit-harness/"
PATHS = (
    *(
        PREFIX + name + ".py"
        for name in (
            "complete_functional_acceptance",
            "complete_requirements",
            "run_internal_red_team",
            "assemble_verified_progress",
            "audit_documentation",
            "run_checkpoint_validation",
            "assemble_final_handoff",
            "archive_failed_runtime_v1",
            "archive_failed_runtime_v2",
            "archive_failed_runtime_v3",
            "import_rework_contexts",
            "import_native_contexts",
            "import_native_followup",
            "run_native_repetitions",
            "write_progress_handoff",
            "archive_continuation_refusal",
            "run_full_verification",
            "format_assurance_helpers",
            "diagnose_promotion_producer",
            "publish_progress",
            "run_knowledge_integration",
            "verify_original_bytes",
        )
    ),
    "tests/test_gate7_assurance.py",
    "tests/test_gate7_quality_observation.py",
    "tests/test_gate7_git_transport.py",
    "tests/test_gate7_native_cleanup.py",
    "tests/test_gate7_publication_paths.py",
    "tests/test_gate7_continuation.py",
    "scripts/iacode/native_process.py",
    "scripts/iacode/native_editor.py",
    "scripts/iacode/scenarios/quality_engine_e2e.py",
)


def main() -> int:
    from ledger_common import use_utf8_stdout

    use_utf8_stdout()
    from format_current_python import run
    from ledger_common import load_json

    if load_json(CHECKPOINT / "STATE.json")["status"] != "IN_PROGRESS":
        raise ValueError("never format a terminal or sealed subject")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-only", action="store_true")
    options = parser.parse_args()
    for path in PATHS:
        resolved = (ROOT / path).resolve(strict=True)
        if not resolved.is_relative_to(ROOT.resolve()):
            raise ValueError("assurance formatting escaped the declared workspace")
    if options.check_only:
        return run("check", *PATHS)
    code = run("format", *PATHS, "tests/test_gate7_knowledge.py", "tests/test_gate7_assurance.py")
    if code:
        return code
    code = run("check", "--fix", *PATHS)
    if code:
        return code
    return run("check", *PATHS)


if __name__ == "__main__":
    raise SystemExit(main())
