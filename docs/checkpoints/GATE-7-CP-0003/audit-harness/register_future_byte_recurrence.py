"""Reopen the confirmed future-checkpoint transport escape before its family-level repair."""

import hashlib
import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))
from ledger_common import load_json, utc_now, write_json
from lesson_preflight import render_markdown
from lessons import build_preflight, load_lessons, register_recurrence, render_index, save_lessons
from sync_in_progress_metadata import synchronize


def main():
    proof = load_json(CHECKPOINT / "byte-transport-attempts/controls/run-0003.json")
    text = (CHECKPOINT / "byte-transport-attempts/controls/run-0003.stderr.log").read_text(encoding="utf-8")
    if (proof["exitCode"] != 1 or not proof["sourceUnchanged"]
            or "test_next_checkpoint_and_other_gate_observations" not in text
            or "FAILED (failures=1)" not in text or "Ran 3 tests" not in text):
        raise ValueError("Actual complete three-case adverse run with only the future-boundary failure required")
    rows = load_lessons(ROOT)
    lesson = next(row for row in rows if row["lessonId"] == "LSN-0131")
    if (lesson["status"] != "GUARDED"
            or any("BYTE-TRANSPORT-002" in row["detail"] for row in lesson["guardrailFailures"])):
        raise ValueError("Expected locally restored lesson without this distinct recurrence")
    revised = register_recurrence(lesson, CHECKPOINT.name,
        "BYTE-TRANSPORT-002: actual next-checkpoint and other-Gate archive/checkout controls escape current-only attributes beside valid binary nulls and both existing current controls. The public quality attempt was stopped with native exit20 and exact Job/clone cleanup, never counted as an integral test result.")
    revised["resolution"] = "Current-only observation protection is insufficient for the later fresh audit. Family-level byte boundaries and actual future-checkpoint positive/adverse controls remain required; no original or historical failed evidence may be normalized."
    revised["evidence"] += ["file:docs/checkpoints/GATE-7-CP-0003/byte-transport-attempts/controls/run-0003.json",
                            "file:docs/checkpoints/GATE-7-CP-0003/published-green-keeper/run-0001/CONTROLLED-CANCELLATION.json"]
    rows[rows.index(lesson)] = revised
    raw = (ROOT / ".gitattributes").read_bytes()
    archive = CHECKPOINT / "raw-preimages/ATTRIBUTES-BEFORE-FAMILY-BOUNDARY.raw"
    if archive.exists():
        raise ValueError("Never overwrite the pre-repair original")
    with archive.open("xb") as stream:
        stream.write(raw)
    write_json(archive.with_suffix(".json"), {"observedAt": utc_now(), "source": ".gitattributes",
        "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(), "archive": archive.name})
    save_lessons(ROOT, rows)
    (ROOT / ".iacode/memory/LESSONS.md").write_text(render_index(rows), encoding="utf-8", newline="\n")
    rework = load_json(CHECKPOINT / "INTERNAL-ENVIRONMENT-REWORK.json")
    rework["items"].append({"id": "BYTE-TRANSPORT-002", "status": "OPEN",
        "classification": "GUARDRAIL_FAILURE LSN-0131",
        "observed": "A real permanent next-checkpoint/other-Gate transport regression fails while current observation and binary-null controls remain valid.",
        "evidence": "byte-transport-attempts/controls/run-0003.json",
        "requiredCorrection": "Protect canonical original-observation families across checkpoint IDs; rerun real archive/both checkouts, exact index comparison and the unchanged complete mandatory set."})
    write_json(CHECKPOINT / "INTERNAL-ENVIRONMENT-REWORK.json", rework)
    previous = load_json(CHECKPOINT / "LESSON-PREFLIGHT.json")
    preflight = build_preflight(ROOT, previous["gate"], previous["scope"], previous["technologies"], previous["modules"])
    write_json(CHECKPOINT / "LESSON-PREFLIGHT.json", preflight)
    (CHECKPOINT / "LESSON-PREFLIGHT.md").write_text(render_markdown(preflight), encoding="utf-8", newline="\n")
    quality = load_json(CHECKPOINT / "QUALITY.json")
    for key in ("lint", "staticAnalysis", "checkpointValidation"):
        quality["checks"][key].update(status="NOT_EXECUTED", evidence=[],
            justification="The family-boundary guard recurrence requires new current-source evidence; earlier actual observations remain preserved.")
    write_json(CHECKPOINT / "QUALITY.json", quality)
    state = load_json(CHECKPOINT / "STATE.json")
    state["greenKeeper"]["unresolvedReworkItems"] = 4
    state["nextAllowedAction"] = "Derive the complete unchanged obligation set, repair original-observation family transport and finish pre-execution exact cleanup orchestration; then run all current mandatory controls and immutable functional proof. No independent auditor before seal and no Gate8."
    write_json(CHECKPOINT / "STATE.json", state)
    synchronize(ROOT, CHECKPOINT)
    print("LSN-0131 distinct future-boundary recurrence reopened before repair; no mandatory set or historical result changed")
    return 0


if __name__ == "__main__":
    from ledger_common import use_utf8_stdout
    use_utf8_stdout()
    raise SystemExit(main())
