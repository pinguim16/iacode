"""Restore guards only after the specific later executable acceptance exists in the ledger."""

import json
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
CHECKPOINT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))
from lessons import load_lessons, save_lessons  # noqa: E402
from ledger_common import utc_now  # noqa: E402

records = {row["id"]: row for row in (json.loads(line) for line in
           (CHECKPOINT / "COMMANDS.jsonl").read_text(encoding="utf-8").splitlines() if line.strip())}
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--round", choices=("initial", "strict-delta", "public-vocabulary"), default="initial")
selected_round = parser.parse_args().round
strict_delta = selected_round == "strict-delta"
public_vocabulary = selected_round == "public-vocabulary"
required = (("cmd-0193", "cmd-0199") if public_vocabulary else
            ("cmd-0169", "cmd-0177") if strict_delta else
            ("cmd-0123", "cmd-0126", "cmd-0128", "cmd-0141"))
for identifier in required:
    if records.get(identifier, {}).get("exitCode") != 0:
        raise ValueError("missing actual corrective acceptance: " + identifier)
lessons = load_lessons(ROOT)
if public_vocabulary:
    report = json.loads((CHECKPOINT / "DESKTOP-LIVE.json").read_text(encoding="utf-8"))
    steps = {row["name"]: row["result"] for row in report["steps"]}
    if report.get("result") != "PASS" or any(steps.get(name) != "PASS" for name in (
            "actual-cli-sigint-stops-only-local-observation",
            "installed-cli-running-task-cancel-request-terminal-and-repeat",
            "installed-cli-running-quality-cancel-waits-for-cleanup",
            "owned-sandbox-children-and-networks-removed")):
        raise ValueError("complete actual canonical-vocabulary cancellation proof required")
for lesson in lessons:
    selected = (("LSN-0128",) if public_vocabulary else
                ("LSN-0119",) if strict_delta else ("LSN-0119", "LSN-0125"))
    if lesson["lessonId"] not in selected:
        continue
    if lesson["recurrenceCount"] != (2 if strict_delta else 1) or not lesson["guardrailFailures"]:
        raise ValueError("recurrence history must remain intact")
    lesson["status"] = "GUARDED"
    for failure in lesson["guardrailFailures"]:
        if failure["checkpoint"] == "GATE-5-CP-0001":
            failure["resolvedIn"] = "GATE-5-CP-0001"
    lesson["updatedAt"] = utc_now()
    lesson["notes"] = (
        "The escalated recurrence remains in guardrailFailures. The strengthened template guard "
        "passed cmd-0123 and actual checkpoint validation cmd-0141; actual owned shared storage "
        "and full native removal passed cmd-0128 with launch controls cmd-0126. Whole-Gate and "
        "persistent provider recovery acceptance remain separate and are not inferred."
    )
    if strict_delta:
        lesson["notes"] = (
            "Both escalated recurrences and their severity remain recorded. Cmd-0169 executes the "
            "strict scanner over every actual changed path, including new checkpoint harnesses; "
            "cmd-0177 is actual serialized checkpoint acceptance after the source-reference correction. "
            "No scanner rule, publication allowance or correct assertion changed. Full Gate assurance remains separate."
        )
    if public_vocabulary:
        lesson["notes"] = (
            "The public-contract recurrence, severity escalation and failure history remain intact. "
            "Cmd-0193 executes the guard against every canonical active sandbox state and an added-state fixture; "
            "cmd-0199 executes the complete real native/provider/sandbox/quality workflow, local SIGINT, "
            "task/quality cancellation and repeat, tamper refusal and complete exact-owner cleanup. "
            "The unchanged byte-exact DESKTOP-LIVE.json preserves that dirty-source observation; "
            "immutable full Gate assurance remains separately required."
        )
save_lessons(ROOT, lessons)
print(json.dumps({row["lessonId"]: {"status": row["status"], "recurrences": row["recurrenceCount"]}
                  for row in lessons if row["lessonId"] in selected}))
