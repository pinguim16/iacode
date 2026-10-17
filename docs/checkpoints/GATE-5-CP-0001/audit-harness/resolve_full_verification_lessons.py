"""Restore causal guards only after their actual corrective executions; full delivery stays pending."""

import json
import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))
from ledger_common import utc_now, use_utf8_stdout, write_json
from lessons import load_lessons, save_lessons

REQUIRED = ("cmd-0290", "cmd-0291", "cmd-0293", "cmd-0295", "cmd-0296",
            "cmd-0297", "cmd-0298", "cmd-0299", "cmd-0301", "cmd-0305", "cmd-0306")


def main() -> int:
    records = {row["id"]: row for row in (json.loads(line) for line in
               (CHECKPOINT / "COMMANDS.jsonl").read_text(encoding="utf-8").splitlines()
               if line.strip())}
    for identifier in REQUIRED:
        if records.get(identifier, {}).get("exitCode") != 0:
            raise ValueError("missing actual causal acceptance: " + identifier)
    infrastructure = json.loads((CHECKPOINT / "INFRASTRUCTURE-REWORK.json").read_text(encoding="utf-8"))
    if (infrastructure.get("result") != "PASS" or not infrastructure.get("ownedRemoved")
            or not infrastructure.get("sharedUnchanged") or not infrastructure.get("sourceInputsUnchanged")
            or infrastructure["commands"][-1].get("skipped")
            or not infrastructure["commands"][-1].get("complete")):
        raise ValueError("complete actual infrastructure/cleanup proof required")
    registry = json.loads((ROOT / ".iacode/memory/guardrails/registry.json").read_text(encoding="utf-8"))
    additions = {
        "GRD-0039": ["test_cli_reservation_membership_follows_every_policy_lifecycle_position"],
        "GRD-0075": ["test_real_registry_is_bound_explicitly_when_working_directory_is_nested"],
        "GRD-0103": ["test_current_summary_derives_exact_vocabulary_and_ignores_noncanonical_alias",
                     "test_current_summary_refuses_missing_duplicate_reordered_or_unknown_results"],
    }
    for guard in registry["guardrails"]:
        for control in additions.get(guard["guardrailId"], []):
            if control not in guard["verifiedBy"]:
                guard["verifiedBy"].append(control)
    fresh = (
        ("GRD-0136", "LSN-0134", "Configuration classifiers receive canonical decoded literal values",
         ["test_host_literal_reader_matches_actual_compose_and_placeholder_semantics",
          "test_malformed_quoted_env_literals_fail_closed_without_exposing_content",
          "test_process_environment_overlays_are_values_not_dotenv_tokens"],
         "Serialization quote syntax or ambient undeclared values to be mistaken for the actual configured value."),
        ("GRD-0137", "LSN-0135", "Safe producer reports survive interpretation failure and owned cleanup",
         ["test_raw_reports_survive_real_postprocessing_exception_and_owned_cleanup",
          "test_raw_capture_refuses_secret_material_but_retains_neutral_failure_inventory"],
         "A fallible report consumer to destroy the only producer observations, or unsafe content to be exported before scanning."),
    )
    for identifier, lesson_id, title, controls, consequence in fresh:
        if not any(row["guardrailId"] == identifier for row in registry["guardrails"]):
            registry["guardrails"].append({
                "guardrailId": identifier, "title": title, "kind": "test",
                "reference": controls[0], "verifiedBy": controls, "lessons": [lesson_id],
                "removingItWouldAllow": consequence,
            })
    write_json(ROOT / ".iacode/memory/guardrails/registry.json", registry)
    selected = {"LSN-0035", "LSN-0037", "LSN-0074", "LSN-0083", "LSN-0102", "LSN-0105"}
    controls = {lesson: (identifier, names) for identifier, lesson, _, names, _ in fresh}
    lessons = load_lessons(ROOT)
    for lesson in lessons:
        identifier = lesson["lessonId"]
        if identifier in selected:
            for failure in lesson["guardrailFailures"]:
                if failure["checkpoint"] == CHECKPOINT.name:
                    failure["resolvedIn"] = CHECKPOINT.name
            for control in additions.get(lesson["guardrails"][0], []):
                if not any(row["reference"] == control for row in lesson["prevention"]):
                    lesson["prevention"].append({"kind": "test", "reference": control,
                                                "description": "Execute the strengthened current causal boundary without weakening inherited controls."})
        elif identifier in controls:
            guard, names = controls[identifier]
            lesson["guardrails"] = [guard]
            lesson["prevention"] = [{"kind": "test", "reference": name,
                                     "description": "Actual positive/adverse causal regression, not a prose-only claim."}
                                    for name in names]
        else:
            continue
        lesson["status"] = "GUARDED"
        lesson["updatedAt"] = utc_now()
        lesson["evidence"] = list(dict.fromkeys(lesson["evidence"] + [
            "file:tests/test_gate5_clients.py", "file:docs/checkpoints/GATE-5-CP-0001/FINDINGS.json",
            "file:docs/checkpoints/GATE-5-CP-0001/COMMANDS.jsonl",
        ]))
        lesson["notes"] = (
            "All original failures, recurrence counters and escalated severity remain intact. "
            "Actual causal controls: literal/Compose3 cmd-0290; scope5 cmd-0291; API166 including "
            "nested cwd cmd-0293; collector4 cmd-0295; original redactor assertion cmd-0296; "
            "actual FAIL reinterpretation cmd-0297; Gate5 root40 cmd-0298; owned infrastructure49 "
            "with zero skips and complete cleanup cmd-0299; client35/packages cmd-0301; mandatory "
            "lint cmd-0305; whole unchanged encoding class cmd-0306. These restore causal prevention, "
            "not whole-Gate readiness: immutable complete v3 verification and ordered assurance remain required."
        )
    save_lessons(ROOT, lessons)
    print("CAUSAL_GUARDS_RESTORED currentFullVerification=PENDING independentM2=PENDING")
    return 0


if __name__ == "__main__":
    use_utf8_stdout()
    raise SystemExit(main())
