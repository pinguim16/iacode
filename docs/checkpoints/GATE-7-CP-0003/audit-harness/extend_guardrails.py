"""Add demonstrated producer-boundary controls without dropping historical prevention."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))
from ledger_common import load_json, utc_now, write_json
from lessons import load_lessons, save_lessons


def main() -> int:
    additions = {
        "LSN-0010": ("GRD-0011", [
            "CheckpointInvocationProducerTests.test_custom_phase_and_quoted_unicode_replay_are_literal",
            "CheckpointInvocationProducerTests.test_omitted_default_status_is_not_invented",
            "CheckpointInvocationProducerTests.test_nested_working_directory_and_explicit_root_replay",
            "CheckpointInvocationProducerTests.test_default_null_control_preserves_supplied_invocation",
        ]),
        "LSN-0135": ("GRD-0137", [
            "ClientProducerCleanupEvidenceTests.test_both_failures_retain_distinct_actual_exit_and_streams",
            "ClientProducerCleanupEvidenceTests.test_timeout_and_failed_cleanup_preserve_partial_real_output",
            "ClientProducerCleanupEvidenceTests.test_successful_producer_with_failed_cleanup_cannot_pass",
            "ClientProducerCleanupEvidenceTests.test_secret_and_oversized_output_are_not_disclosed",
            "ClientProducerCleanupEvidenceTests.test_clean_null_control_returns_actual_producer",
        ]),
    }
    registry_path = ROOT / ".iacode/memory/guardrails/registry.json"
    registry = load_json(registry_path)
    rows = load_lessons(ROOT)
    for lesson in rows:
        if lesson["lessonId"] not in additions:
            continue
        guardrail_id, tests = additions[lesson["lessonId"]]
        for test in tests:
            if not any(item["reference"] == test for item in lesson["prevention"]):
                lesson["prevention"].append({"kind": "test", "reference": test,
                    "description": "Actual producer/replay causal boundary with null and adverse controls."})
        for path in ("docs/checkpoints/GATE-7-CP-0002/FINDINGS.json",
                     "tests/test_m2_audit_corrections.py",
                     "docs/checkpoints/GATE-7-CP-0003/causal-attempts/run-0005.json",
                     "docs/checkpoints/GATE-7-CP-0003/causal-attempts/run-0006.json"):
            reference = "file:" + path
            if reference not in lesson["evidence"]:
                lesson["evidence"].append(reference)
        lesson["updatedAt"] = utc_now()
        note = " M2 CP0003 adds actual child-producer and literal replay regressions; " \
               "the independent guarded recurrence remains unresolved until complete corrective acceptance."
        if note not in lesson.get("notes", ""):
            lesson["notes"] = lesson.get("notes", "") + note
        for guardrail in registry["guardrails"]:
            if guardrail["guardrailId"] == guardrail_id:
                guardrail["verifiedBy"] = list(dict.fromkeys([*guardrail["verifiedBy"], *tests]))
    write_json(registry_path, registry)
    save_lessons(ROOT, rows)
    print("Extended two guardrails; both recurrences remain CONFIRMED and unresolved.")
    return 0


if __name__ == "__main__":
    from ledger_common import use_utf8_stdout
    use_utf8_stdout()
    raise SystemExit(main())
