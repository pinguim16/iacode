"""Escalate observed unowned CLI descendant drain before repairing the new helper."""

import hashlib
import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))
from ledger_common import load_json, write_json
from lessons import load_lessons, register_recurrence, render_index, save_lessons, build_preflight
from lesson_preflight import render_markdown


def main():
    original = load_json(CHECKPOINT / "resource-phases/phase-0002/BUILDER-BOOTSTRAP.json")
    preimage = CHECKPOINT / "raw-preimages/BOOTSTRAP-DRAIN-001-current-resources.py"
    if (original["status"] != "TIMEOUT" or original["result"] != "FAIL"
            or original["exitCode"] is not None
            or hashlib.sha256(preimage.read_bytes()).hexdigest() != "11cbfe4d8a2b88351d5f20559c7eda0d6ba66206f9c08940ffc350990939473f"):
        raise ValueError("Exact failed original and archived helper preimage required")
    rework = load_json(CHECKPOINT / "INTERNAL-ENVIRONMENT-REWORK.json")
    if any(item["id"] == "BOOTSTRAP-DRAIN-001" for item in rework["items"]):
        raise ValueError("Do not duplicate an observed recurrence")
    rework["items"].append({"id": "BOOTSTRAP-DRAIN-001", "status": "OPEN",
        "classification": "GUARDRAIL_FAILURE LSN-0125",
        "observed": "A new task-owned buildx bootstrap used direct piped subprocess.run with a60-second timeout. The parent Docker CLI was killed, but its exact buildx plugin retained inherited output handles and prevented the timeout observation from returning until pinned helper-only recovery. Actual parent recorder duration was240210ms.",
        "evidence": "resource-phases/phase-0002/BUILDER-BOOTSTRAP.json",
        "commands": ["cmd-0234", "cmd-0235"],
        "preimage": "raw-preimages/BOOTSTRAP-DRAIN-001-current-resources.py",
        "requiredCorrection": "Use the existing exact owned Windows Job runner, retain safe producer and cleanup observations, preserve the unchanged60-second producer budget, add actual surviving-writer and actual caller-boundary controls. Never signal the Engine or other applications.",
        "exposure": "Internal new checkpoint helper only; no product verdict or independent auditor. Image pull availability is a separate unresolved operational dependency, not a proved Engine outage."})
    write_json(CHECKPOINT / "INTERNAL-ENVIRONMENT-REWORK.json", rework)
    lessons = load_lessons(ROOT)
    index = next(i for i, row in enumerate(lessons) if row["lessonId"] == "LSN-0125")
    lesson = lessons[index]
    if lesson["status"] != "GUARDED":
        raise ValueError("Expected the existing guarded native-descendant boundary")
    revised = register_recurrence(lesson, CHECKPOINT.name,
        "BOOTSTRAP-DRAIN-001: newly authored buildx helper used unowned piped capture; killed parent left exact plugin35632 with inherited handles beyond its60-second timeout. Pinned creation/executable/argv-only recovery drained the CLI without signaling Engine or applications. Extend the existing guard to the real checkpoint caller; image pull availability remains separate.")
    revised["resolution"] = "CP0003 BOOTSTRAP-DRAIN-001 remains open; no local guarded claim. " + revised["resolution"]
    revised["evidence"] += ["file:" + (CHECKPOINT / name).relative_to(ROOT).as_posix()
        for name in ("INTERNAL-ENVIRONMENT-REWORK.json", "resource-phases/phase-0002/BUILDER-BOOTSTRAP.json",
                     "raw-preimages/BOOTSTRAP-DRAIN-001-current-resources.py")]
    lessons[index] = revised
    save_lessons(ROOT, lessons)
    (ROOT / ".iacode/memory/LESSONS.md").write_text(render_index(lessons), encoding="utf-8", newline="\n")
    prior = load_json(CHECKPOINT / "LESSON-PREFLIGHT.json")
    preflight = build_preflight(ROOT, prior["gate"], prior["scope"], prior["technologies"], prior["modules"])
    write_json(CHECKPOINT / "LESSON-PREFLIGHT.json", preflight)
    (CHECKPOINT / "LESSON-PREFLIGHT.md").write_text(render_markdown(preflight), encoding="utf-8", newline="\n")
    quality = load_json(CHECKPOINT / "QUALITY.json")
    for key in ("lint", "staticAnalysis", "checkpointValidation"):
        quality["checks"][key].update(status="NOT_EXECUTED", evidence=[],
            justification="New guarded native-descendant recurrence changes assurance-scoped memory; prior actual source epochs remain preserved, not current acceptance.")
    write_json(CHECKPOINT / "QUALITY.json", quality)
    print("BOOTSTRAP-DRAIN-001 escalated; LSN-0125 CONFIRMED, no deadline extension or independent verdict")
    return 0


if __name__ == "__main__":
    from ledger_common import use_utf8_stdout
    use_utf8_stdout()
    raise SystemExit(main())
