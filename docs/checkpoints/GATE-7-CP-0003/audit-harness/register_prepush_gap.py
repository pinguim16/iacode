"""Record a real pre-publication evidence gap without rewriting its public subject."""

import json
import subprocess
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
    output = CHECKPOINT / "PRE-PUSH-LINT-0001.json"
    if output.exists():
        raise ValueError("Do not duplicate this recorded publication gap")
    commit = "477ec86f09c5e03ad328cf40a3725855b3526bad"
    raw = subprocess.run(
        ["git", "show", commit + ":docs/checkpoints/GATE-7-CP-0003/QUALITY.json"],
        cwd=ROOT,
        capture_output=True,
        check=True,
    ).stdout
    quality = json.loads(raw)
    prior = load_json(CHECKPOINT / "quality-attempts/lint/run-0008.json")
    canceled = load_json(CHECKPOINT / "published-green-keeper/run-0002/RECEIPT.json")
    if (
        quality["checks"]["lint"]["status"] != "NOT_EXECUTED"
        or prior["sourceFingerprint"] == canceled["sourceFingerprint"]
        or canceled["execution"]["producer"]["exitCode"] != 20
        or canceled["execution"]["cleanup"]["result"] != "PASS"
        or not canceled["temporaryCloneRemoved"]
    ):
        raise ValueError(
            "Actual published missing-current-lint and completed owned cancellation required"
        )
    observation = {
        "recordedAt": utc_now(),
        "id": "PRE-PUSH-LINT-001",
        "kind": "INTERNAL_PROTOCOL_FAILURE_NOT_INDEPENDENT_FINDING",
        "publicSubject": commit,
        "publicTag": "iacode-subjects/GATE-7-CP-0003-runtime-v2",
        "publishedLintStatus": quality["checks"]["lint"]["status"],
        "publishedSourceFingerprint": canceled["sourceFingerprint"],
        "nearestCompletedLintSourceFingerprint": prior["sourceFingerprint"],
        "requiredCheck": (
            "LSN-0054 requires current whole lint and repository-wide sca"
            "ns before each push, not only later closure assurance."
        ),
        "rootCause": (
            "The trusted progress publisher enforced declared scope, stag"
            "ed secret scan and canonical validation but omitted the exis"
            "ting pre-push lint precondition. Targeted component green di"
            "d not satisfy the broader requirement."
        ),
        "historyRewritten": False,
        "oldSubjectOrTagChanged": False,
        "canceledCycleIsWholeAcceptance": False,
        "canceledCycleCleanup": "PASS",
        "canonicalCorrection": (
            "Require successful canonical lint bound to current source an"
            "d current pre-publication HEAD before any publication effect"
            "s. Run actual lint and new guard controls, then publish a ne"
            "w immutable subject and execute fresh full assurance."
        ),
    }
    write_json(output, observation)
    rework = load_json(CHECKPOINT / "INTERNAL-ENVIRONMENT-REWORK.json")
    rework["items"].append(
        {
            "id": "PRE-PUSH-LINT-001",
            "status": "OPEN",
            "classification": "RECURRENCE_OF_CONFIRMED_LSN-0054_NOT_A_GUARDED_FAILURE",
            "observed": observation["rootCause"],
            "evidence": output.name,
            "requiredCorrection": observation["canonicalCorrection"],
        }
    )
    write_json(CHECKPOINT / "INTERNAL-ENVIRONMENT-REWORK.json", rework)
    lessons = load_lessons(ROOT)
    index = next(i for i, row in enumerate(lessons) if row["lessonId"] == "LSN-0054")
    revised = register_recurrence(
        lessons[index],
        CHECKPOINT.name,
        (
            "PRE-PUSH-LINT-001: runtime-v2 commit477ec86 was published wi"
            "th current lint NOT_EXECUTED; older completed lint described"
            " another fingerprint. Preserve immutable history and cancel "
            "only its exact owned incomplete quality cycle before repairi"
            "ng the publisher precondition."
        ),
    )
    revised["evidence"] += [
        "file:" + output.relative_to(ROOT).as_posix(),
        "file:" + (CHECKPOINT / "INTERNAL-ENVIRONMENT-REWORK.json").relative_to(ROOT).as_posix(),
    ]
    revised["notes"] += (
        " PRE-PUSH-LINT-001 is an actual recurrence in the corrective"
        " checkpoint, not a retroactive lint PASS or an independent f"
        "inding. The trusted current publisher must acquire a checked"
        " current proof before another push; broad manual Git actions"
        " remain subject to the contract."
    )
    lessons[index] = revised
    save_lessons(ROOT, lessons)
    (ROOT / ".iacode/memory/LESSONS.md").write_text(
        render_index(lessons), encoding="utf-8", newline="\n"
    )
    previous = load_json(CHECKPOINT / "LESSON-PREFLIGHT.json")
    preflight = build_preflight(
        ROOT, previous["gate"], previous["scope"], previous["technologies"], previous["modules"]
    )
    write_json(CHECKPOINT / "LESSON-PREFLIGHT.json", preflight)
    (CHECKPOINT / "LESSON-PREFLIGHT.md").write_text(
        render_markdown(preflight), encoding="utf-8", newline="\n"
    )
    quality = load_json(CHECKPOINT / "QUALITY.json")
    for key in ("lint", "staticAnalysis", "checkpointValidation"):
        quality["checks"][key].update(
            status="NOT_EXECUTED",
            evidence=[],
            justification=(
                "Publication-gap recurrence changes assurance-scoped memory; "
                "old successful epochs are retained, not current proof."
            ),
        )
    write_json(CHECKPOINT / "QUALITY.json", quality)
    active = load_json(CHECKPOINT / "ACTIVE-VALIDATION.json")
    active.update(
        recordedAt=utc_now(),
        nativeToolSessions=[],
        publicQualityStatus="CONTROLLED_CANCELLATION_NOT_COMPLETE",
        privateCloneRemoved=True,
        nextAction=(
            "Repair publication preconditions, run actual current lint be"
            "fore a new immutable runtime publication, then fresh complet"
            "e assurance."
        ),
    )
    write_json(CHECKPOINT / "ACTIVE-VALIDATION.json", active)
    print(
        "PRE-PUSH-LINT-001 recorded; LSN-0054 recurrence incremented,"
        " public history unchanged, no complete quality or audit verd"
        "ict"
    )
    return 0


if __name__ == "__main__":
    from ledger_common import use_utf8_stdout

    use_utf8_stdout()
    raise SystemExit(main())
