"""Restore only observed local continuation prevention; whole delivery remains due."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "scripts/development-ledger"))
from ledger_common import load_json, scope_fingerprint, utc_now, write_json
from lesson_preflight import render_markdown
from lessons import build_preflight, load_lessons, render_index, save_lessons
from publish_progress import require_current_authored_quality, require_current_lint

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]


def main():
    if load_json(CHECKPOINT / "STATE.json")["status"] != "IN_PROGRESS":
        raise ValueError("Never rewrite a terminal or sealed delivery")
    fingerprint = scope_fingerprint(ROOT)
    lint = require_current_lint()
    authored = require_current_authored_quality()
    proofs = []
    for folder in ("causal-attempts/all-m2", "quality-attempts/checkpointValidation"):
        path = sorted((CHECKPOINT / folder).glob("run-*.json"))[-1]
        value = load_json(path)
        if (
            value["sourceFingerprint"] != fingerprint
            or value["sourceUnchanged"] is not True
            or type(value["exitCode"]) is not int
            or value["exitCode"] != 0
            or any(item["refused"] for item in value["streams"].values())
        ):
            raise ValueError("Actual current corrective controls and canonical validation required")
        proofs.append(path.relative_to(CHECKPOINT).as_posix())
    retrospective = ROOT / ".iacode/memory/retrospectives/GATE-7-CP-0003.md"
    text = retrospective.read_text(encoding="utf-8")
    old = "LSN-0140 / GRD-0142 | Recurrence4, CONFIRMED"
    old_note = (
        "The current table below distinguishes local guards from the "
        "still-open continuation recurrence."
    )
    if text.count(old) != 1 or text.count(old_note) != 1:
        raise ValueError("Require the exact open retrospective status before restoration")
    lessons = load_lessons(ROOT)
    lesson = next(row for row in lessons if row["lessonId"] == "LSN-0140")
    failures = [
        row
        for row in lesson["guardrailFailures"]
        if "CONTINUATION-001" in row["detail"] and not row.get("resolvedIn")
    ]
    if lesson["status"] != "CONFIRMED" or len(failures) != 1:
        raise ValueError("Only the exact unresolved continuation recurrence may be restored")
    rework = load_json(CHECKPOINT / "INTERNAL-ENVIRONMENT-REWORK.json")
    item = next(row for row in rework["items"] if row["id"] == "CONTINUATION-001")
    if item["status"] != "OPEN":
        raise ValueError("The exact internal finding must still be open")
    tests = [
        "CorrectiveContinuationTests." + name
        for name in (
            "test_actual_corrective_and_current_handoff_next_preserve_existing_contract",
            "test_actual_retrospectives_keep_exact_sections_and_every_recorded_lesson_guard",
            "test_actual_failed_original_is_exact_inert_and_rejected_by_identical_contract",
            "test_current_positive_and_omission_empty_extra_order_and_lesson_growth_controls",
        )
    ]
    history_tests = [
        "BootstrapOwnershipTests." + name
        for name in (
            "test_actual_history_query_requires_the_same_owned_native_boundary",
            "test_exact_published_history_preimage_is_rejected_by_the_same_guard",
        )
    ]
    native = next(row for row in lessons if row["lessonId"] == "LSN-0125")
    if native["status"] != "GUARDED":
        raise ValueError("Keep the already demonstrated native guard and historical counter")
    for row, references in ((lesson, tests), (native, history_tests)):
        for reference in references:
            if not any(entry["reference"] == reference for entry in row["prevention"]):
                row["prevention"].append(
                    {
                        "kind": "test",
                        "reference": reference,
                        "description": (
                            "Actual current caller/document and exact original adverse co"
                            "ntrols; no template or budget reduction."
                        ),
                    }
                )
    evidence = [
        lint["receipt"],
        authored["receipt"],
        *proofs,
        "continuation-attempts/run-0001/RECEIPT.json",
        "causal-attempts/all-m2/run-0003.json",
    ]
    failures[0]["resolvedIn"] = CHECKPOINT.name
    lesson.update(
        status="GUARDED",
        updatedAt=utc_now(),
        resolution=(
            "CONTINUATION-001 is locally corrected with unchanged canonic"
            "al sections and inherited assertions. The actual corrective/"
            "current documents and every recorded lesson/guard are covere"
            "d, including original rejection, missing/empty/extra/order a"
            "nd growth controls. Current complete lint, whole authored qu"
            "ality and quiescent canonical validation passed. Original fa"
            "ilure/counter remain; fresh source-epoch whole assurance and"
            " independent M2 are due."
        ),
    )
    lesson["evidence"].extend(
        "file:" + (CHECKPOINT / name).relative_to(ROOT).as_posix() for name in evidence
    )
    native["notes"] += (
        " CP0003 proactively applies the same60-second owned Job to private build-history queries. "
        "Actual query cmd0308 passes with retained primary/cleanup facts; current caller and exact "
        "published preimage controls pass. This is defensive scope extension, not another observed "
        "native timeout or a counter reset."
    )
    registry_path = ROOT / ".iacode/memory/guardrails/registry.json"
    registry = load_json(registry_path)
    for guard in registry["guardrails"]:
        additions = (
            tests
            if guard["guardrailId"] in lesson["guardrails"]
            else (history_tests if guard["guardrailId"] in native["guardrails"] else [])
        )
        if additions:
            guard["verifiedBy"] = list(dict.fromkeys([*guard["verifiedBy"], *additions]))
    write_json(registry_path, registry)
    save_lessons(ROOT, lessons)
    (ROOT / ".iacode/memory/LESSONS.md").write_text(
        render_index(lessons), encoding="utf-8", newline="\n"
    )
    text = text.replace(old, "LSN-0140 / GRD-0142 | Recurrence4, local GUARDED", 1)
    text = text.replace(
        old_note,
        ("The table below records local guard restoration, not whole delivery acceptance."),
    )
    retrospective.write_text(text, encoding="utf-8", newline="\n")
    item.update(
        status="LOCAL_CORRECTION_DEMONSTRATED_WHOLE_ASSURANCE_PENDING", currentProof=evidence
    )
    write_json(CHECKPOINT / "INTERNAL-ENVIRONMENT-REWORK.json", rework)
    prior = load_json(CHECKPOINT / "LESSON-PREFLIGHT.json")
    preflight = build_preflight(
        ROOT, prior["gate"], prior["scope"], prior["technologies"], prior["modules"]
    )
    write_json(CHECKPOINT / "LESSON-PREFLIGHT.json", preflight)
    (CHECKPOINT / "LESSON-PREFLIGHT.md").write_text(
        render_markdown(preflight), encoding="utf-8", newline="\n"
    )
    write_json(
        CHECKPOINT / "CONTINUATION-LOCAL-RESTORATION.json",
        {
            "observedAt": utc_now(),
            "result": "LOCAL_GUARD_RESTORED_NOT_WHOLE_DELIVERY",
            "proofSourceFingerprint": fingerprint,
            "nextSourceFingerprint": scope_fingerprint(ROOT),
            "evidence": evidence,
            "independent": False,
        },
    )
    print("LSN-0140 local guard restored; fresh whole-current assurance remains required")
    return 0


if __name__ == "__main__":
    from ledger_common import use_utf8_stdout

    use_utf8_stdout()
    raise SystemExit(main())
