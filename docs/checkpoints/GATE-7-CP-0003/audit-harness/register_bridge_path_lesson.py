"""Register the observed unreleased adapter defect, without claiming a working guard."""

import sys
from pathlib import Path

sys.path.insert(
    0, str(Path(__file__).resolve().parents[1].parents[2] / "scripts/development-ledger")
)
from ledger_common import load_json, utc_now, validate_schema
from lessons import load_lessons, next_lesson_id, render_index, save_lessons

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]


def main():
    rows = load_lessons(ROOT)
    if any(row["source"].get("finding") == "BRIDGE-PATH-001" for row in rows):
        raise ValueError("Do not silently repeat the observed registration")
    proof = load_json(CHECKPOINT / "causal-attempts/bridge-path-bounds/run-0001.json")
    if proof.get("result") != "FAIL":
        raise ValueError("The actual pre-fix refusal failure must be retained")
    now = utc_now()
    row = {
        "lessonId": next_lesson_id(rows),
        "title": "Private runner inputs require physical containment, not lexical ancestry",
        "category": "security",
        "severity": "MEDIUM",
        "source": {"gate": "GATE-7", "checkpoint": CHECKPOINT.name, "finding": "BRIDGE-PATH-001"},
        "symptom": (
            "The unreleased adapter rejects an absolute outside file but "
            "accepts an existing parent-relative outside file under a lex"
            "ically owned prefix."
        ),
        "rootCauseSummary": (
            "Path.is_relative_to compares lexical components and does not"
            " establish actual filesystem containment through parent comp"
            "onents."
        ),
        "resolution": (
            "Pending: refuse parent traversal and compare strict physical"
            " containment while retaining reparse and hardlink refusals. "
            "No auditor or privileged HTTP path-input surface was offered"
            "."
        ),
        "prevention": [],
        "evidence": [
            "file:docs/checkpoints/GATE-7-CP-0003/causal-attempts/bridge-path-bounds/run-0001.json",
            "file:docs/checkpoints/GATE-7-CP-0003/INTERNAL-ENVIRONMENT-REWORK.json",
        ],
        "applicability": {
            "gates": ["*"],
            "scopes": [],
            "technologies": ["Python"],
            "modules": ["scripts/development-ledger"],
            "requiredCheck": (
                "Reject physical escapes, parent aliases, redirected ancestor"
                "s and hardlinks before reading a frozen input or publishing "
                "a report; retain an actual valid inside-file control."
            ),
            "requiredEvidence": (
                "Actual pre-fix red beside a valid null; executed current ins"
                "ide/absolute/parent/reparse/hardlink controls and full uncha"
                "nged current assurance."
            ),
        },
        "status": "CONFIRMED",
        "recurrenceKey": "security/private-runner-lexical-ancestry-accepts-physical-escape",
        "recurrenceCount": 0,
        "guardrailFailures": [],
        "createdAt": now,
        "updatedAt": now,
        "provenance": {
            "sourceType": "repository-generated",
            "provider": "local-execution",
            "model": None,
            "ownership": "project-generated engineering evidence",
            "license": "not-applicable",
            "notes": (
                "Actual exclusively owned filesystem fixture; no unrelated da"
                "ta or independent verdict."
            ),
        },
        "trainingEligibility": {
            "trainingAllowed": False,
            "ragAllowed": False,
            "distillationAllowed": False,
            "justification": "No explicit rights evidence for reuse.",
        },
        "notes": (
            "Operator-only defensive boundary in a new adapter; closed HT"
            "TP clients cannot submit source/report paths. No disclosure "
            "was observed. Working automated prevention and final deliver"
            "y remain pending."
        ),
    }
    errors = validate_schema(row, load_json(ROOT / ".iacode/schemas/lesson.schema.json"))
    if errors:
        raise ValueError(errors)
    rows.append(row)
    save_lessons(ROOT, rows)
    (ROOT / ".iacode/memory/LESSONS.md").write_text(
        render_index(rows), encoding="utf-8", newline="\n"
    )
    print(row["lessonId"] + " CONFIRMED; no guard effectiveness or acceptance claimed")
    return 0


if __name__ == "__main__":
    from ledger_common import use_utf8_stdout

    use_utf8_stdout()
    raise SystemExit(main())
