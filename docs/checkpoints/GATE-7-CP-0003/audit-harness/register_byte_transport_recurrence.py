"""Escalate actual staged byte loss before correcting copied-evidence attributes."""

import hashlib
import sys
from pathlib import Path

sys.path.insert(
    0, str(Path(__file__).resolve().parents[1].parents[2] / "scripts/development-ledger")
)
from ledger_common import load_json, utc_now, write_json
from lesson_preflight import render_markdown
from lessons import build_preflight, load_lessons, register_recurrence, render_index, save_lessons

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]


def main():
    proof = load_json(CHECKPOINT / "byte-transport-attempts/index-0001.json")
    if proof["result"] != "FAIL" or not proof["mismatches"] or not proof["matching"]:
        raise ValueError("Actual adverse and matching staged-byte observations required")
    rows = load_lessons(ROOT)
    for index, lesson in enumerate(rows):
        if lesson["lessonId"] != "LSN-0131":
            continue
        if any(row["checkpoint"] == CHECKPOINT.name for row in lesson.get("guardrailFailures", [])):
            raise ValueError("Do not duplicate current guarded recurrence")
        revised = register_recurrence(
            lesson,
            CHECKPOINT.name,
            (
                "BYTE-TRANSPORT-001: actual Git staging changes62 of182 origi"
                "nal copied observations/preimages, beside120 unchanged nulls"
                ". New current observation families and inherited unsealed au"
                "dit bytes lack explicit Git byte boundaries; publication sto"
                "pped before commit/tag/push."
            ),
        )
        revised["resolution"] = (
            "CP0003 byte transport recurrence remains open; protect actua"
            "l raw evidence and prove real Git store/archive/checkout byt"
            "es without rewriting originals."
        )
        revised["evidence"].append(
            "file:docs/checkpoints/GATE-7-CP-0003/byte-transport-attempts/index-0001.json"
        )
        revised["evidence"].append(
            "file:docs/checkpoints/GATE-7-CP-0003/PUBLICATION-INTERRUPTION-0001.json"
        )
        rows[index] = revised
    save_lessons(ROOT, rows)
    (ROOT / ".iacode/memory/LESSONS.md").write_text(
        render_index(rows), encoding="utf-8", newline="\n"
    )
    raw = (ROOT / ".gitattributes").read_bytes()
    archive = CHECKPOINT / "raw-preimages/ATTRIBUTES-BEFORE-BYTE-BOUNDARY.raw"
    with archive.open("xb") as stream:
        stream.write(raw)
    write_json(
        archive.with_suffix(".json"),
        {
            "observedAt": utc_now(),
            "bytes": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest(),
            "source": ".gitattributes",
            "archive": archive.name,
        },
    )
    rework = load_json(CHECKPOINT / "INTERNAL-ENVIRONMENT-REWORK.json")
    rework["items"].append(
        {
            "id": "BYTE-TRANSPORT-001",
            "status": "OPEN",
            "classification": "GUARDRAIL_FAILURE LSN-0131",
            "observed": (
                "Actual staged copied bytes differ in62 of182 files;120 match"
                ". No originals were rewritten and no commit/tag/push occurre"
                "d."
            ),
            "evidence": "byte-transport-attempts/index-0001.json",
            "requiredCorrection": (
                "Explicit copied-observation Git attributes, actual default/C"
                "RLF checkout and archive controls, index recheck, and new co"
                "mplete current assurance."
            ),
        }
    )
    write_json(CHECKPOINT / "INTERNAL-ENVIRONMENT-REWORK.json", rework)
    previous = load_json(CHECKPOINT / "LESSON-PREFLIGHT.json")
    preflight = build_preflight(
        ROOT, previous["gate"], previous["scope"], previous["technologies"], previous["modules"]
    )
    write_json(CHECKPOINT / "LESSON-PREFLIGHT.json", preflight)
    (CHECKPOINT / "LESSON-PREFLIGHT.md").write_text(
        render_markdown(preflight), encoding="utf-8", newline="\n"
    )
    print(
        "LSN-0131 recurrence escalated and complete preflight refresh"
        "ed; no guard or transport acceptance claimed"
    )
    return 0


if __name__ == "__main__":
    from ledger_common import use_utf8_stdout

    use_utf8_stdout()
    raise SystemExit(main())
