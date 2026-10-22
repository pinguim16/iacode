"""Document the checked publication boundary without pretending real lint already ran."""

import sys
from pathlib import Path

sys.path.insert(
    0, str(Path(__file__).resolve().parents[1].parents[2] / "scripts/development-ledger")
)
from derive_requirements import render_closure
from ledger_common import load_json, utc_now, write_json
from lesson_preflight import render_markdown
from lessons import build_preflight, load_lessons, render_index, save_lessons

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]


def main():
    proof = load_json(CHECKPOINT / "causal-attempts/publication-policy/run-0003.json")
    if proof["exitCode"] or not proof["sourceUnchanged"]:
        raise ValueError("Actual publication decision/owner controls required; not live lint")
    tests = [
        (
            "PublicationCallerTests.test_actual_publisher_checks_current_"
            "lint_before_publication_effects"
        ),
        "PublicationCallerTests.test_archived_actual_publisher_without_precondition_is_rejected",
        (
            "PublicationProofDecisionTests.test_modeled_valid_proof_is_ac"
            "cepted_without_git_state_effects"
        ),
        "PublicationProofDecisionTests.test_missing_stale_failed_and_bool_exit_proofs_are_refused",
        (
            "PublicationProofDecisionTests.test_other_head_or_unbound_art"
            "ifact_cannot_serve_as_current_prepublication_proof"
        ),
        (
            "PublicationProofDecisionTests.test_actual_stream_tamper_and_"
            "wrapper_identity_change_are_refused"
        ),
        (
            "PublicationProofDecisionTests.test_latest_failed_attempt_can"
            "not_fall_back_to_older_success"
        ),
    ]
    lessons = load_lessons(ROOT)
    lesson = next(row for row in lessons if row["lessonId"] == "LSN-0054")
    if lesson["status"] != "CONFIRMED":
        raise ValueError("Do not overstate coverage of broader manual Git actions")
    for name in tests:
        if not any(item["reference"] == name for item in lesson["prevention"]):
            lesson["prevention"].append(
                {
                    "kind": "test",
                    "reference": name,
                    "description": (
                        "Actual trusted publisher caller and modeled receipt/input/by"
                        "te decisions; does not report real repository lint or execut"
                        "e a push."
                    ),
                }
            )
    lesson.update(
        updatedAt=utc_now(),
        resolution=(
            "Current trusted progress publisher requires latest successfu"
            "l canonical lint bound to current source and pre-publication"
            " HEAD, original scanned stream bytes and an actual command/i"
            "nput binding before publication effects. Real current lint/n"
            "ew publication and fresh whole assurance were still due at t"
            "his local-control epoch; checkpoint evidence owns their even"
            "tual outcome. Broad manual Git actions remain procedural, so"
            " status stays CONFIRMED."
        ),
    )
    lesson["evidence"] += [
        "file:tests/test_m2_progress_publication.py",
        "file:docs/checkpoints/GATE-7-CP-0003/causal-attempts/publication-policy/run-0001.json",
        "file:docs/checkpoints/GATE-7-CP-0003/causal-attempts/publication-policy/run-0003.json",
    ]
    save_lessons(ROOT, lessons)
    (ROOT / ".iacode/memory/LESSONS.md").write_text(
        render_index(lessons), encoding="utf-8", newline="\n"
    )
    rework = load_json(CHECKPOINT / "INTERNAL-ENVIRONMENT-REWORK.json")
    item = next(row for row in rework["items"] if row["id"] == "PRE-PUSH-LINT-001")
    item.update(
        status="LOCAL_CORRECTION_DEMONSTRATED_WHOLE_ASSURANCE_PENDING",
        currentProof=["causal-attempts/publication-policy/run-0003.json"],
        actualCurrentLint="NOT_EXECUTED",
        limit=(
            "Modeled verifier decisions are not execution of canonical re"
            "pository lint; actual current proof and a fresh complete imm"
            "utable cycle remain due."
        ),
    )
    write_json(CHECKPOINT / "INTERNAL-ENVIRONMENT-REWORK.json", rework)
    closure = load_json(CHECKPOINT / "CLOSURE-REQUIREMENTS.json")
    row = next(item for item in closure["requirements"] if item["sourceRef"] == "lesson:LSN-0054")
    row.update(
        implementationStatus="PARTIAL",
        finalStatus="PARTIAL",
        justification=(
            "Publisher boundary repaired with actual caller and modeled m"
            "etadata controls; real current lint and new properly precede"
            "d publication remain due."
        ),
    )
    for key, values in {
        "implementationEvidence": [
            "file:docs/checkpoints/GATE-7-CP-0003/audit-harness/publish_progress.py"
        ],
        "testEvidence": [
            "file:docs/checkpoints/GATE-7-CP-0003/causal-attempts/publication-policy/run-0003.json"
        ],
        "negativeTestEvidence": [
            "file:docs/checkpoints/GATE-7-CP-0003/PRE-PUSH-LINT-0001.json",
            "file:docs/checkpoints/GATE-7-CP-0003/causal-attempts/publication-policy/run-0001.json",
        ],
        "documentationEvidence": [
            "checkpoint:PRE-PUSH-LINT-0001.json",
            "file:docs/DEVELOPMENT-CONTRACT.md",
        ],
        "guardrailEvidence": ["test:" + name for name in tests[:2]],
    }.items():
        row[key] = list(dict.fromkeys([*row[key], *values]))
    write_json(CHECKPOINT / "CLOSURE-REQUIREMENTS.json", closure)
    (CHECKPOINT / "CLOSURE-REQUIREMENTS.md").write_text(
        render_closure(closure), encoding="utf-8", newline="\n"
    )
    previous = load_json(CHECKPOINT / "LESSON-PREFLIGHT.json")
    preflight = build_preflight(
        ROOT, previous["gate"], previous["scope"], previous["technologies"], previous["modules"]
    )
    write_json(CHECKPOINT / "LESSON-PREFLIGHT.json", preflight)
    (CHECKPOINT / "LESSON-PREFLIGHT.md").write_text(
        render_markdown(preflight), encoding="utf-8", newline="\n"
    )
    print(
        "Publication local controls recorded; actual current lint/ful"
        "l assurance still required, no guarded/independent overclaim"
    )
    return 0


if __name__ == "__main__":
    from ledger_common import use_utf8_stdout

    use_utf8_stdout()
    raise SystemExit(main())
