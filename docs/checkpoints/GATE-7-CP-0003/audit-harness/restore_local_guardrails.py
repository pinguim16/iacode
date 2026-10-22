"""Restore demonstrated local automated prevention, never whole-delivery acceptance."""

import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))
from ledger_common import load_json, utc_now, write_json
from lessons import load_lessons, render_index, save_lessons


def main():
    proof_names = ["causal-attempts/run-0011.json", "causal-attempts/native-observation/run-0003.json",
                   "causal-attempts/bridge-physical-bounds/run-0002.json", "causal-attempts/bridge/run-0005.json",
                   "causal-attempts/owned-cleanup/run-0004.json", "causal-attempts/operator-cleanup/run-0002.json",
                   "causal-attempts/current-streams/run-0001.json", "causal-attempts/inherited-streams/run-0001.json"]
    for name in proof_names:
        proof = load_json(CHECKPOINT / name)
        if (proof["exitCode"] != 0 or not proof["sourceUnchanged"]
                or any(stream["refused"] for stream in proof["streams"].values())):
            raise ValueError("No local restoration on incomplete/unsafe/red proof: " + name)
    now = utc_now()
    additions = {
        "LSN-0010": ("GRD-0011", [
            "CheckpointInvocationProducerTests.test_registered_m2_attack_runs_actual_null_and_phase_human_replay",
            "CheckpointInvocationProducerTests.test_registered_m2_attack_reproduces_old_phase_escape_with_valid_null"]),
        "LSN-0135": ("GRD-0137", [
            "NativeProducerObservationTests.test_failed_callback_cannot_replace_real_nonzero_producer",
            "NativeProducerObservationTests.test_timeout_and_callback_failure_keep_both_observations",
            "NativeProducerObservationTests.test_capture_handle_release_failure_cannot_replace_primary_observation",
            "NativeProducerObservationTests.test_native_actor_forwards_producer_facts_without_approving_cleanup_failure",
            "BridgePhysicalBoundsTests.test_output_prefix_is_fixed_before_a_controlled_actual_append"]),
        "LSN-0035": ("GRD-0037", ["M2CurrentStreamBootstrapTests.test_actual_capture_entry_blocks_reject_cold_bootstrap_removal"]),
        "LSN-0083": ("GRD-0084", ["M2CurrentStreamBootstrapTests.test_actual_capture_entry_blocks_reject_cold_bootstrap_removal"]),
        "LSN-0152": ("GRD-0155", [
            "BridgePhysicalBoundsTests.test_actual_inside_null_and_absolute_escape_refusal",
            "BridgePhysicalBoundsTests.test_parent_relative_existing_escape_is_refused",
            "BridgePhysicalBoundsTests.test_parent_alias_in_the_source_root_is_refused",
            "BridgePhysicalBoundsTests.test_redirected_owned_ancestor_and_hardlink_are_refused",
            "BridgePhysicalBoundsTests.test_report_escape_keeps_producer_but_never_archives_outside_content"])}
    registry_path = ROOT / ".iacode/memory/guardrails/registry.json"
    registry = load_json(registry_path)
    if any(row["guardrailId"] == "GRD-0155" for row in registry["guardrails"]):
        raise ValueError("Guard already registered; do not overwrite another registration")
    registry["guardrails"].append({
        "guardrailId": "GRD-0155", "title": "Private runner source/report physical containment",
        "kind": "test", "reference": additions["LSN-0152"][1][1],
        "verifiedBy": additions["LSN-0152"][1], "lessons": ["LSN-0152"],
        "removingItWouldAllow": "A lexically owned parent-relative input or report to expose an outside physical file."})
    lessons = load_lessons(ROOT)
    for lesson in lessons:
        if lesson["lessonId"] not in additions:
            continue
        guard, controls = additions[lesson["lessonId"]]
        if lesson["status"] != "CONFIRMED":
            raise ValueError("Only the observed reopened lessons may be locally restored")
        for control in controls:
            if not any(row["reference"] == control for row in lesson["prevention"]):
                lesson["prevention"].append({"kind": "test", "reference": control,
                    "description": "Executed actual current positive/adverse control; no production fake or independent verdict."})
        for failure in lesson.get("guardrailFailures", []):
            if failure["checkpoint"] == CHECKPOINT.name and not failure.get("resolvedIn"):
                failure["resolvedIn"] = CHECKPOINT.name
        lesson["status"] = "GUARDED"
        lesson["updatedAt"] = now
        lesson["guardrails"] = list(dict.fromkeys([*lesson.get("guardrails", []), guard]))
        lesson["resolution"] = ("CP0003 local prevention restored by actual current producer/null/adverse controls "
                                "and unchanged inherited controls. Whole current immutable verification, ordered "
                                "internal assurance and fresh independent M2 validation remain separate obligations.")
        lesson["notes"] = (lesson.get("notes", "") + " CP0003 local controls now execute the repaired boundary; "
                           "all original failures, counters, maximum severities and historical evidence remain. "
                           "No whole-delivery readiness or independent verdict is inferred from this local restoration.")
        if lesson["lessonId"] == "LSN-0152":
            lesson["notes"] = ("Operator-only boundary, not an HTTP path-submission capability. Actual parent, "
                               "root alias, reparse/hardlink and report-escape controls pass beside valid inside files. "
                               "Whole current immutable assurance and independent M2 validation remain required.")
        for name in proof_names:
            reference = "file:" + (CHECKPOINT / name).relative_to(ROOT).as_posix()
            if reference not in lesson["evidence"]:
                lesson["evidence"].append(reference)
        entry = next(row for row in registry["guardrails"] if row["guardrailId"] == guard)
        entry["verifiedBy"] = list(dict.fromkeys([*entry["verifiedBy"], *controls]))
    write_json(registry_path, registry)
    save_lessons(ROOT, lessons)
    (ROOT / ".iacode/memory/LESSONS.md").write_text(render_index(lessons), encoding="utf-8", newline="\n")
    rework = load_json(CHECKPOINT / "INTERNAL-ENVIRONMENT-REWORK.json")
    for item in rework["items"]:
        if item["id"] in {"BRIDGE-PATH-001", "M2-F-002-NATIVE-EXTENSION", "ROOT-UTF8-001"}:
            item.update(status="LOCAL_CORRECTION_DEMONSTRATED_WHOLE_ASSURANCE_PENDING",
                        currentProof=proof_names, currentCanonicalImplementation=True)
    write_json(CHECKPOINT / "INTERNAL-ENVIRONMENT-REWORK.json", rework)
    print("Local automated prevention restored for five lessons; whole acceptance and findings closure NOT granted")
    return 0


if __name__ == "__main__":
    from ledger_common import use_utf8_stdout
    use_utf8_stdout()
    raise SystemExit(main())
