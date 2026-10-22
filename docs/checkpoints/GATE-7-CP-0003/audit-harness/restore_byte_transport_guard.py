"""Restore measured byte-transport prevention only, with full acceptance still pending."""

import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))
from ledger_common import load_json, utc_now, write_json
from lesson_preflight import render_markdown
from lessons import build_preflight, load_lessons, render_index, save_lessons


def main():
    current = load_json(CHECKPOINT / "byte-transport-attempts/controls/run-0002.json")
    index = load_json(CHECKPOINT / "byte-transport-attempts/index-0005.json")
    if (current["exitCode"] != 0 or not current["sourceUnchanged"]
            or index["result"] != "PASS" or index["mismatches"] or not index["compared"]):
        raise ValueError("Actual complete Git transport and index proof required")
    tests = ["M2ObservationTransportTests.test_every_declared_copied_observation_survives_actual_archive_and_both_checkout_modes",
             "M2ObservationTransportTests.test_removing_byte_boundaries_is_detected_beside_actual_binary_null"]
    lessons = load_lessons(ROOT)
    lesson = next(row for row in lessons if row["lessonId"] == "LSN-0131")
    if lesson["status"] != "CONFIRMED":
        raise ValueError("Expected reopened byte-transport lesson")
    for test in tests:
        if not any(row["reference"] == test for row in lesson["prevention"]):
            lesson["prevention"].append({"kind": "test", "reference": test,
                "description": "Actual Git store/archive and both checkout byte modes for the entire declared observation set, with a real binary null and removed-boundary adverse control."})
    for failure in lesson["guardrailFailures"]:
        if failure["checkpoint"] == CHECKPOINT.name and not failure.get("resolvedIn"):
            failure["resolvedIn"] = CHECKPOINT.name
    lesson.update(status="GUARDED", updatedAt=utc_now(),
        resolution="Explicit copied-evidence Git attributes and exact index refresh preserve originals. Actual two-case transport controls and187-file index comparison pass. No original was normalized, no detector changed and no publication occurred. Whole current immutable assurance remains required.")
    lesson["notes"] += " CP0003 local byte guard is restored by actual Git archive/checkout modes and index equality; retain all original failed comparisons, counters and stopped publication evidence. This is not actual cross-OS/cross-tool or independent milestone validation."
    for name in ("byte-transport-attempts/controls/run-0002.json", "byte-transport-attempts/index-0005.json"):
        lesson["evidence"].append("file:" + (CHECKPOINT / name).relative_to(ROOT).as_posix())
    registry_path = ROOT / ".iacode/memory/guardrails/registry.json"
    registry = load_json(registry_path)
    for entry in registry["guardrails"]:
        if entry["guardrailId"] in lesson["guardrails"]:
            entry["verifiedBy"] = list(dict.fromkeys([*entry["verifiedBy"], *tests]))
    write_json(registry_path, registry)
    save_lessons(ROOT, lessons)
    (ROOT / ".iacode/memory/LESSONS.md").write_text(render_index(lessons), encoding="utf-8", newline="\n")
    rework = load_json(CHECKPOINT / "INTERNAL-ENVIRONMENT-REWORK.json")
    item = next(row for row in rework["items"] if row["id"] == "BYTE-TRANSPORT-001")
    item.update(status="LOCAL_CORRECTION_DEMONSTRATED_WHOLE_ASSURANCE_PENDING",
                currentProof=["byte-transport-attempts/controls/run-0002.json", "byte-transport-attempts/index-0005.json"],
                originalFilesRewritten=False)
    write_json(CHECKPOINT / "INTERNAL-ENVIRONMENT-REWORK.json", rework)
    previous = load_json(CHECKPOINT / "LESSON-PREFLIGHT.json")
    preflight = build_preflight(ROOT, previous["gate"], previous["scope"], previous["technologies"], previous["modules"])
    write_json(CHECKPOINT / "LESSON-PREFLIGHT.json", preflight)
    (CHECKPOINT / "LESSON-PREFLIGHT.md").write_text(render_markdown(preflight), encoding="utf-8", newline="\n")
    print("Local original-byte prevention restored; stopped publication and all original failures retained")
    return 0


if __name__ == "__main__":
    from ledger_common import use_utf8_stdout
    use_utf8_stdout()
    raise SystemExit(main())
