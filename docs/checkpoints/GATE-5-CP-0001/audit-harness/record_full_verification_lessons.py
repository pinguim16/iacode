"""Escalate observed full-v2 recurrences and confirm new causal lessons before repair."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))
from ledger_common import utc_now, use_utf8_stdout
from lessons import load_lessons, register_recurrence, save_lessons


def main() -> int:
    lessons = load_lessons(ROOT)
    updates = {
        "LSN-0011": ("G5-INT-034", "Cmd-0317 repeats the exact unfinished-inventory-recorder class: cmd-0316 still runs when validation starts, and six strict hashes are refused. A tool session ID is not completion. Group both recorded phases in one synchronous sequencer and require actual quiescent validation."),
        "LSN-0105": ("G5-INT-033", "Cmd-0300 refuses the added infrastructure consumer imports under unchanged I001. Preserve the failure, reorder only imports and require the entire mandatory lint gate green; no rule or assertion change."),
        "LSN-0074": ("G5-INT-028", "Cmd-0276 preserves two nested API registry failures. The existing guard proves metadata and projected policy, but not the real domain registry needed by the new API tests. Keep ambient test settings isolation and explicitly bind the repository fixture."),
        "LSN-0102": ("G5-INT-029", "Cmd-0277 completes 45 canonical stages but its publisher invokes a historical helper whose fixed subject has 42. Derive the current exact vocabulary instead of borrowing a sealed denominator."),
        "LSN-0035": ("G5-INT-030", "Cmd-0279 reproduces four text captures with no explicit decoder and six current capture entry points with unconfigured output. Keep the unchanged whole-tree rules and fix all consumers."),
        "LSN-0083": ("G5-INT-030", "Cmd-0279 reproduces six unconfigured captured-output entry points, including two new current-checkpoint diagnostics. Configure each executable itself without weakening the unchanged scan."),
        "LSN-0037": ("G5-INT-031", "Cmd-0281 derives the current Gate but applies a fixed historical pre-owner expectation to the CLI directory after its owner Gate is authorized. Derive ownership/lifecycle expectations and retain every pre-owner and future reservation assertion."),
    }
    new_recurrences = 0
    new_lessons = 0
    for index, lesson in enumerate(lessons):
        if lesson["lessonId"] not in updates:
            continue
        finding, detail = updates[lesson["lessonId"]]
        if not any(finding in row["detail"] for row in lesson["guardrailFailures"]):
            lessons[index] = register_recurrence(lesson, "GATE-5-CP-0001", finding + ": " + detail)
            new_recurrences += 1
    definitions = (
        ("LSN-0134", "G5-INT-027", "MEDIUM", "Configuration classifiers consume decoded values, not dotenv quote syntax",
         "Raw-line consumers and the host reader retain the quote delimiters of the committed empty desktop values; actual Compose decodes them to empty. Infrastructure, backup secrecy and the two-redactor corpus then disagree about serialization rather than credential classification.",
         "The consumers passed a serialized dotenv token into an API whose input is a value, and the host literal parser omitted enclosing-quote decoding.",
         "Align literal reading with observed Compose semantics and share that decoded input across consumers without changing canonical credential-name or placeholder definitions.",
         "implementation/dotenv-encoded-token-mistaken-for-decoded-value",
         "For committed environment consumers, decode the supported literal syntax before classification and prove actual Compose agreement for quoted empty, quoted placeholder and nonempty adverse values.",
         "Causal red observations, actual Compose positive/adverse comparisons, host-reader and all affected consumer regressions plus complete infrastructure reexecution.",
         ["file:docs/checkpoints/GATE-5-CP-0001/ENV-TEMPLATE-DIAGNOSIS-0001.json"]),
        ("LSN-0135", "G5-INT-032", "HIGH", "Capture producer evidence before fallible interpretation or owned cleanup",
         "The current publisher retains the top-level completed verifier report but loses unexported detailed scenario reports when a stale stage denominator raises and the temporary clone owner correctly cleans its directory.",
         "Producer capture was sequenced after interpretation, so a consumer exception destroyed the only available detailed observations with the owned temporary workspace.",
         "Archive every available safe producer report byte-exactly before interpretation; keep a neutral inventory and retain failures without synthesizing missing artifacts or passing verdicts.",
         "quality/producer-report-lost-before-fallible-consumer-finishes",
         "Every temporary verification producer must preserve its available safe reports before interpretation can raise; actual owner cleanup must leave those reports and digests recoverable without manufacturing PASS.",
         "A real exception and actual temporary-owner cleanup regression with recoverable original bytes, plus a fresh complete publication capture and exact transport verification.",
         ["file:docs/checkpoints/GATE-5-CP-0001/attempts/FULL-VERIFY-RED-0002-MANIFEST.json"]),
    )
    for identifier, finding, severity, title, symptom, cause, resolution, key, check, evidence, files in definitions:
        if any(row["lessonId"] == identifier for row in lessons):
            continue
        now = utc_now()
        new_lessons += 1
        lessons.append({
            "lessonId": identifier, "title": title, "category": "implementation" if identifier == "LSN-0134" else "quality",
            "severity": severity, "source": {"gate": "GATE-5", "checkpoint": "GATE-5-CP-0001", "finding": finding},
            "symptom": symptom, "rootCauseSummary": cause, "resolution": resolution,
            "prevention": [], "guardrails": [], "evidence": [
                "file:docs/checkpoints/GATE-5-CP-0001/COMMANDS.jsonl", *files],
            "applicability": {"gates": ["*"], "scopes": [], "technologies": [], "modules": [],
                              "requiredCheck": check, "requiredEvidence": evidence},
            "status": "CONFIRMED", "recurrenceKey": key, "recurrenceCount": 0, "guardrailFailures": [],
            "createdAt": now, "updatedAt": now,
            "provenance": {"sourceType": "repository-generated", "provider": "local-execution", "model": None,
                           "ownership": "project-generated evidence", "license": "not-applicable",
                           "notes": "Derived only from this checkpoint's preserved actual failures and read-only diagnostics."},
            "trainingEligibility": {"trainingAllowed": False, "ragAllowed": False, "distillationAllowed": False, "justification": None},
            "notes": "Confirmed causal failure; no automated prevention or whole-Gate acceptance is claimed before its corrective controls execute.",
        })
    save_lessons(ROOT, lessons)
    print(f"FULL_V2_LESSONS_RECORDED newRecurrences={new_recurrences} "
          f"newConfirmed={new_lessons}; no correction accepted yet")
    return 0


if __name__ == "__main__":
    use_utf8_stdout()
    raise SystemExit(main())
