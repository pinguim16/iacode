"""Restore only the measured family-level byte guard; integral assurance remains due."""

import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))
from ledger_common import load_json, scope_fingerprint, utc_now, write_json
from lesson_preflight import render_markdown
from lessons import build_preflight, load_lessons, render_index, save_lessons


def main():
    proof = load_json(CHECKPOINT / "byte-transport-attempts/controls/run-0004.json")
    index = load_json(CHECKPOINT / "byte-transport-attempts/index-0006.json")
    text = (CHECKPOINT / "byte-transport-attempts/controls/run-0004.stderr.log").read_text(encoding="utf-8")
    if (proof["exitCode"] or not proof["sourceUnchanged"]
            or proof["sourceFingerprint"] != scope_fingerprint(ROOT)
            or "Ran 3 tests" not in text or not text.rstrip().endswith("OK")
            or index["result"] != "PASS" or index["mismatches"] or index["compared"] != 206):
        raise ValueError("Actual complete current transport and exact index proof required")
    lessons = load_lessons(ROOT)
    lesson = next(row for row in lessons if row["lessonId"] == "LSN-0131")
    failures = [row for row in lesson["guardrailFailures"]
                if "BYTE-TRANSPORT-002" in row["detail"] and not row.get("resolvedIn")]
    if lesson["status"] != "CONFIRMED" or len(failures) != 1:
        raise ValueError("Expected exactly this open distinct recurrence")
    test = "M2ObservationTransportTests.test_next_checkpoint_and_other_gate_observations_keep_the_same_real_byte_boundaries"
    if not any(row["reference"] == test for row in lesson["prevention"]):
        lesson["prevention"].append({"kind": "test", "reference": test,
            "description": "Real archive and both checkout modes across the next auditor and another Gate's complete original-observation family set, beside actual binary nulls."})
    failures[0]["resolvedIn"] = CHECKPOINT.name
    lesson.update(status="GUARDED", updatedAt=utc_now(),
        resolution="Generic canonical original-observation family attributes now protect current and later auditor checkpoints. Three actual Git controls and206 exact staged original comparisons pass. All recurrences, failed attempts and the canceled incomplete quality run remain; complete immutable assurance is still pending.")
    lesson["notes"] += " The earlier CP0003-only restoration was subsequently insufficient for a new auditor; BYTE-TRANSPORT-002 records that distinct guarded escape. Family-level controls now provide local automated prevention, not independent approval."
    lesson["evidence"] += ["file:docs/checkpoints/GATE-7-CP-0003/byte-transport-attempts/controls/run-0004.json",
                            "file:docs/checkpoints/GATE-7-CP-0003/byte-transport-attempts/index-0006.json"]
    registry_path = ROOT / ".iacode/memory/guardrails/registry.json"
    registry = load_json(registry_path)
    for entry in registry["guardrails"]:
        if entry["guardrailId"] in lesson["guardrails"]:
            entry["verifiedBy"] = list(dict.fromkeys([*entry["verifiedBy"], test]))
    write_json(registry_path, registry)
    save_lessons(ROOT, lessons)
    (ROOT / ".iacode/memory/LESSONS.md").write_text(render_index(lessons), encoding="utf-8", newline="\n")
    rework = load_json(CHECKPOINT / "INTERNAL-ENVIRONMENT-REWORK.json")
    item = next(row for row in rework["items"] if row["id"] == "BYTE-TRANSPORT-002")
    item.update(status="LOCAL_CORRECTION_DEMONSTRATED_WHOLE_ASSURANCE_PENDING",
        currentProof=["byte-transport-attempts/controls/run-0004.json", "byte-transport-attempts/index-0006.json"],
        originalFilesRewritten=False)
    write_json(CHECKPOINT / "INTERNAL-ENVIRONMENT-REWORK.json", rework)
    previous = load_json(CHECKPOINT / "LESSON-PREFLIGHT.json")
    preflight = build_preflight(ROOT, previous["gate"], previous["scope"], previous["technologies"], previous["modules"])
    write_json(CHECKPOINT / "LESSON-PREFLIGHT.json", preflight)
    (CHECKPOINT / "LESSON-PREFLIGHT.md").write_text(render_markdown(preflight), encoding="utf-8", newline="\n")
    print("Family-level original-byte guard restored locally; no whole Green Keeper, runtime or independent result granted")
    return 0


if __name__ == "__main__":
    from ledger_common import use_utf8_stdout
    use_utf8_stdout()
    raise SystemExit(main())
