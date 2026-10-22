"""Restore measured local native prevention; complete immutable assurance stays pending."""

import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))
from ledger_common import load_json, scope_fingerprint, utc_now, write_json
from lessons import load_lessons, render_index, save_lessons, build_preflight
from lesson_preflight import render_markdown


def main():
    original = load_json(CHECKPOINT / "causal-attempts/bootstrap-ownership/run-0001.json")
    proof = load_json(CHECKPOINT / "causal-attempts/bootstrap-ownership/run-0002.json")
    phase_proof = load_json(CHECKPOINT / "causal-attempts/resource-phase/run-0004.json")
    live = load_json(CHECKPOINT / "resource-phases/phase-0002/BUILDER-BOOTSTRAP-RETRY-0001.json")
    if (original["exitCode"] != 1 or proof["exitCode"] != 0 or not proof["sourceUnchanged"]
            or proof["sourceFingerprint"] != scope_fingerprint(ROOT) or phase_proof["exitCode"] != 0
            or not phase_proof["sourceUnchanged"] or phase_proof["sourceFingerprint"] != scope_fingerprint(ROOT)
            or live["result"] != "PASS" or live["producerBudgetSeconds"] != 60
            or live["execution"]["producer"]["exitCode"] != 0
            or live["execution"]["cleanup"]["result"] != "PASS"):
        raise ValueError("Actual causal guard, phase controls and live bounded owned bootstrap required")
    lessons = load_lessons(ROOT)
    lesson = next(row for row in lessons if row["lessonId"] == "LSN-0125")
    failures = [row for row in lesson["guardrailFailures"]
                if "BOOTSTRAP-DRAIN-001" in row["detail"] and not row.get("resolvedIn")]
    if lesson["status"] != "CONFIRMED" or len(failures) != 1:
        raise ValueError("Only this unresolved native-descendant recurrence may be restored")
    tests = ["BootstrapOwnershipTests." + name for name in (
        "test_actual_bootstrap_caller_requires_owned_native_process_boundary",
        "test_archived_actual_preimage_is_rejected_by_identical_caller_guard",
        "test_real_parent_exit_with_inherited_output_writer_is_observed_then_exactly_drained")]
    for name in tests:
        if not any(row["reference"] == name for row in lesson["prevention"]):
            lesson["prevention"].append({"kind": "test", "reference": name,
                "description": "Guard the actual bootstrap caller and archived adverse preimage; real Windows surviving-writer null proves exact owned cleanup without Engine operations."})
    failures[0]["resolvedIn"] = CHECKPOINT.name
    lesson.update(status="GUARDED", updatedAt=utc_now(),
        resolution="The new checkpoint bootstrap now invokes the existing exact owned Job runner. Actual caller/preimage/surviving-writer controls pass, and live same60-second bootstrap exits0 with independent cleanup PASS. Preserve the original240210ms timeout and pinned helper-only recovery. Current complete immutable assurance and independent M2 remain due.")
    lesson["notes"] += " BOOTSTRAP-DRAIN-001 was separately escalated before correction; local caller and real descendant controls plus live unchanged-budget bootstrap now restore automated prevention. No broader process termination, Engine restart or whole-delivery verdict is inferred."
    evidence = ["causal-attempts/bootstrap-ownership/run-0001.json", "causal-attempts/bootstrap-ownership/run-0002.json",
                "causal-attempts/resource-phase/run-0004.json", "resource-phases/phase-0002/BUILDER-BOOTSTRAP-RETRY-0001.json"]
    lesson["evidence"] += ["file:" + (CHECKPOINT / name).relative_to(ROOT).as_posix() for name in evidence]
    registry_path = ROOT / ".iacode/memory/guardrails/registry.json"
    registry = load_json(registry_path)
    for guard in registry["guardrails"]:
        if guard["guardrailId"] in lesson["guardrails"]:
            guard["verifiedBy"] = list(dict.fromkeys([*guard["verifiedBy"], *tests]))
    write_json(registry_path, registry)
    save_lessons(ROOT, lessons)
    (ROOT / ".iacode/memory/LESSONS.md").write_text(render_index(lessons), encoding="utf-8", newline="\n")
    rework = load_json(CHECKPOINT / "INTERNAL-ENVIRONMENT-REWORK.json")
    item = next(row for row in rework["items"] if row["id"] == "BOOTSTRAP-DRAIN-001")
    item.update(status="LOCAL_CORRECTION_DEMONSTRATED_WHOLE_ASSURANCE_PENDING", currentProof=evidence,
        fixtureAdjustment="Resource-phase run-0003 retained an AttributeError after the removed subprocess API was still named by its mock. The test now targets the actual run_owned entry with the same no-call/refusal assertions; run-0004 passes. No assertion or production guard was weakened.")
    write_json(CHECKPOINT / "INTERNAL-ENVIRONMENT-REWORK.json", rework)
    prior = load_json(CHECKPOINT / "LESSON-PREFLIGHT.json")
    preflight = build_preflight(ROOT, prior["gate"], prior["scope"], prior["technologies"], prior["modules"])
    write_json(CHECKPOINT / "LESSON-PREFLIGHT.json", preflight)
    (CHECKPOINT / "LESSON-PREFLIGHT.md").write_text(render_markdown(preflight), encoding="utf-8", newline="\n")
    print("BOOTSTRAP-DRAIN-001 local guard restored from observed controls; no whole quality, seal or independent verdict")
    return 0


if __name__ == "__main__":
    from ledger_common import use_utf8_stdout
    use_utf8_stdout()
    raise SystemExit(main())
