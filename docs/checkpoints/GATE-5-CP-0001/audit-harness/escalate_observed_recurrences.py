"""Record two evidenced guardrail recurrences once, using the canonical memory transition."""

import json
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))
from lessons import load_lessons, register_recurrence, save_lessons  # noqa: E402

updates = {
    "LSN-0119": ("G5-INT-013", "Cmd-0120 refuses the new Compose template outside the five-source guard. Extend unchanged strict scanning to this path and require actual checkpoint acceptance."),
    "LSN-0125": ("G5-INT-014", "Cmd-0121 owned main.log observes implicit global shared storage outside user-data-dir. Explicit shared-data-dir and observed actual storage ownership are required; no global user storage is touched for repair."),
}
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--round", choices=("initial", "strict-delta", "public-vocabulary"), default="initial")
round_name = parser.parse_args().round
if round_name == "strict-delta":
    updates = {"LSN-0119": ("G5-INT-018", "Cmd-0167 strict scanning refuses a source-expression reference in the new checkpoint diagnostic. The old five-source/template guard did not cover every new current path. Scan the actual Git delta, including checkpoint harnesses, without allowances and require a serialized checkpoint validation.")}
elif round_name == "public-vocabulary":
    updates = {"LSN-0128": ("G5-INT-020", "Cmd-0190 waits for a guessed BUSY state absent from the public sandbox contract; cleanup queries also omit real active states. Derive all active membership from the canonical tuple without importing application dependencies, use actual RUNNING for execution, preserve all active cleanup checks and repeat the real proof.")}
lessons = load_lessons(ROOT)
for index, lesson in enumerate(lessons):
    if lesson["lessonId"] not in updates:
        continue
    finding, detail = updates[lesson["lessonId"]]
    if not any(finding in row["detail"] for row in lesson["guardrailFailures"]):
        lessons[index] = register_recurrence(lesson, "GATE-5-CP-0001", finding + ": " + detail)
        lesson = lessons[index]
    if lesson["lessonId"] == "LSN-0125":
        control = "test_native_installer_and_host_both_pin_their_owned_shared_storage"
        if not any(row["reference"] == control for row in lesson["prevention"]):
            lesson["prevention"].append({"kind": "test", "reference": control,
                "description": "Require explicit owned shared-data-dir on installation and host launch; absent actual storage observations never establish a native PASS."})
    if lesson["lessonId"] == "LSN-0119" and finding == "G5-INT-018":
        control = "test_every_current_changed_path_uses_the_strict_detector_including_checkpoint_harnesses"
        if not any(row["reference"] == control for row in lesson["prevention"]):
            lesson["prevention"].append({"kind": "test", "reference": control,
                "description": "Scan the actual Git delta against its checkpoint base, including every new checkpoint harness and undeclared untracked text path, with unchanged strict detection and no publication allowances."})
    if lesson["lessonId"] == "LSN-0128":
        control = "test_cleanup_membership_derives_every_canonical_active_state_including_running"
        if not any(row["reference"] == control for row in lesson["prevention"]):
            lesson["prevention"].append({"kind": "test", "reference": control,
                "description": "Read all canonical active states without application initialization; require RUNNING and STOPPING membership, reject the old guessed set and prove membership grows with a new canonical active state."})
    lesson["notes"] = "An observed guardrail recurrence is escalated and CONFIRMED pending explicit corrective acceptance. Retain all original evidence; tests do not waive actual checkpoint/native execution."
save_lessons(ROOT, lessons)
print(json.dumps({row["lessonId"]: {"status": row["status"], "recurrences": row["recurrenceCount"]}
                  for row in lessons if row["lessonId"] in updates}))
