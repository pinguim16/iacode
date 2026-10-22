"""Restore only observed local source-quality prevention after complete lint proof."""

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
    fingerprint = scope_fingerprint(ROOT)
    lint = require_current_lint()
    authored = require_current_authored_quality()
    proofs = []
    for folder in ("causal-attempts/all-m2", "causal-attempts/lint-denominator"):
        path = sorted((CHECKPOINT / folder).glob("run-*.json"))[-1]
        value = load_json(path)
        if (
            value["sourceFingerprint"] != fingerprint
            or value["sourceUnchanged"] is not True
            or type(value["exitCode"]) is not int
            or value["exitCode"] != 0
            or any(item["refused"] for item in value["streams"].values())
        ):
            raise ValueError("Require current actual M2 and inherited denominator controls")
        proofs.append(path.relative_to(CHECKPOINT).as_posix())
    lessons = load_lessons(ROOT)
    lesson = next(row for row in lessons if row["lessonId"] == "LSN-0105")
    failures = [
        row
        for row in lesson["guardrailFailures"]
        if "AUTHORED-STYLE-001" in row["detail"] and not row.get("resolvedIn")
    ]
    if lesson["status"] != "CONFIRMED" or len(failures) != 1:
        raise ValueError("Only the exact open authored-source recurrence may be restored")
    rework = load_json(CHECKPOINT / "INTERNAL-ENVIRONMENT-REWORK.json")
    item = next(row for row in rework["items"] if row["id"] == "AUTHORED-STYLE-001")
    if item["status"] != "OPEN":
        raise ValueError("Require the exact observed open source-quality finding")
    tests = [
        (
            "PublicationCallerTests.test_actual_publisher_checks_current_"
            "lint_before_publication_effects"
        ),
        "PublicationCallerTests.test_archived_actual_publisher_without_precondition_is_rejected",
        (
            "AuthoredQualityDecisionTests.test_modeled_valid_whole_scope_"
            "acceptance_has_no_source_effects"
        ),
        (
            "AuthoredQualityDecisionTests.test_missing_stale_narrowed_for"
            "mat_and_nonzero_proofs_are_refused"
        ),
        (
            "AuthoredQualityDecisionTests.test_changed_original_bytes_fai"
            "led_cleanup_and_latest_failure_are_refused"
        ),
    ]
    lesson["prevention"].extend(
        {
            "kind": "test",
            "reference": name,
            "description": (
                "Actual caller guard or explicitly modeled proof-decision con"
                "trol; live quality is separate."
            ),
        }
        for name in tests
        if not any(item["reference"] == name for item in lesson["prevention"])
    )
    lesson["prevention"].append(
        {
            "kind": "automated-check",
            "reference": "docs/checkpoints/GATE-7-CP-0003/audit-harness/authored_python_quality.py",
            "description": (
                "Whole Git-derived active helper/test scope; unchanged pinned"
                " Ruff and read-only proof before publication."
            ),
        }
    )
    evidence = [lint["receipt"], authored["receipt"], *proofs]
    lesson["evidence"].extend(
        "file:" + (CHECKPOINT / name).relative_to(ROOT).as_posix() for name in evidence
    )
    failures[0]["resolvedIn"] = CHECKPOINT.name
    lesson.update(
        status="GUARDED",
        updatedAt=utc_now(),
        resolution=(
            "AUTHORED-STYLE-001 local source correction and publication g"
            "uard are demonstrated by complete unchanged canonical lint, "
            "whole authored quality, actual M2 regressions and inherited "
            "lint denominator controls. Historical failures remain. Curre"
            "nt-source revalidation after this memory update, whole immut"
            "able assurance and independent M2 remain due."
        ),
    )
    registry_path = ROOT / ".iacode/memory/guardrails/registry.json"
    registry = load_json(registry_path)
    for guard in registry["guardrails"]:
        if guard["guardrailId"] in lesson["guardrails"]:
            guard["verifiedBy"] = list(dict.fromkeys([*guard["verifiedBy"], *tests]))
    write_json(registry_path, registry)
    save_lessons(ROOT, lessons)
    (ROOT / ".iacode/memory/LESSONS.md").write_text(
        render_index(lessons), encoding="utf-8", newline="\n"
    )
    prior = load_json(CHECKPOINT / "LESSON-PREFLIGHT.json")
    preflight = build_preflight(
        ROOT, prior["gate"], prior["scope"], prior["technologies"], prior["modules"]
    )
    write_json(CHECKPOINT / "LESSON-PREFLIGHT.json", preflight)
    (CHECKPOINT / "LESSON-PREFLIGHT.md").write_text(
        render_markdown(preflight), encoding="utf-8", newline="\n"
    )
    item.update(
        status="LOCAL_CORRECTION_DEMONSTRATED_WHOLE_ASSURANCE_PENDING",
        currentProof=evidence,
        mechanicalFailures=(
            "Attempts0278/0279 refused non-identical literal AST before w"
            "rites to the affected source. Attempt0280 refused a dynamic "
            "import prefix; the next unchanged-rule scan also caught two "
            "reordered dynamic-load test bootstraps. Explicit order repai"
            "r retained every assertion; all observations remain original"
            ". No failed formatter is read-only acceptance."
        ),
    )
    write_json(CHECKPOINT / "INTERNAL-ENVIRONMENT-REWORK.json", rework)
    write_json(
        CHECKPOINT / "AUTHORED-STYLE-LOCAL-RESTORATION.json",
        {
            "observedAt": utc_now(),
            "result": "LOCAL_PREVENTION_RESTORED_NOT_WHOLE_DELIVERY",
            "proofSourceFingerprint": fingerprint,
            "evidence": evidence,
            "nextSourceFingerprint": scope_fingerprint(ROOT),
            "independent": False,
        },
    )
    print("LSN-0105 local guard restored; fresh whole-current assurance still required")
    return 0


if __name__ == "__main__":
    from ledger_common import use_utf8_stdout

    use_utf8_stdout()
    raise SystemExit(main())
