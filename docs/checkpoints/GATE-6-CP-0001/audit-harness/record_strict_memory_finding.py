"""Preserve a strict memory refusal neutrally and escalate its already-guarded class."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))
from ledger_common import find_secrets, load_json, utc_now, use_utf8_stdout, write_json
from lessons import load_lessons, register_recurrence, save_lessons


def main() -> int:
    commands = [json.loads(line) for line in (CHECKPOINT / "COMMANDS.jsonl").read_text(
        encoding="utf-8").splitlines() if line.strip()]
    if next(row for row in commands if row["id"] == "cmd-0056")["exitCode"] != 1:
        raise ValueError("actual strict memory refusal required")
    lessons = load_lessons(ROOT)
    subject = next(row for row in lessons if row["lessonId"] == "LSN-0138")
    original = subject["title"]
    if not find_secrets(original):
        raise ValueError("the original title must actually reproduce the strict classifier refusal")
    neutral = {"kind": "STRICT_MEMORY_REFUSAL_NEUTRAL_RECEIPT", "observedAt": utc_now(),
        "command": "cmd-0056", "lesson": "LSN-0138", "field": "title",
        "originalUtf8Bytes": len(original.encode()),
        "originalSha256": hashlib.sha256(original.encode()).hexdigest(),
        "strictClassifierRefused": True, "matchedTextExported": False,
        "limit": "A descriptive label matched a strict credential shape; no actual credential disclosure was observed."}
    write_json(CHECKPOINT / "STRICT-MEMORY-FINDING.json", neutral)
    detail = ("G6-INT-008: Cmd-0056 rejects a new memory title under unchanged strict detection. "
              "The guarded actual-delta principle also applies to memory text, not only source. "
              "Retain the failure and neutral original digest, reword only the label, keep both "
              "scanners unchanged and require actual memory/delta/checkpoint acceptance.")
    for index, lesson in enumerate(lessons):
        if lesson["lessonId"] == "LSN-0119" and not any("G6-INT-008" in row["detail"] for row in lesson["guardrailFailures"]):
            lessons[index] = register_recurrence(lesson, CHECKPOINT.name, detail)
    subject["title"] = "Secret projection distinguishes public identities from authorization secrets"
    subject["updatedAt"] = utc_now()
    subject["evidence"].append("file:docs/checkpoints/GATE-6-CP-0001/STRICT-MEMORY-FINDING.json")
    save_lessons(ROOT, lessons)
    findings = load_json(CHECKPOINT / "FINDINGS.json")
    if not any(row["findingId"] == "G6-INT-008" for row in findings["findings"]):
        findings["findings"].append({"findingId": "G6-INT-008", "severity": "CRITICAL",
            "title": "GUARDRAIL_FAILURE: strict engineering-memory text scan", "status": "OPEN",
            "classification": "GUARDRAIL_FAILURE", "lessonId": "LSN-0119", "guardrailId": "GRD-0120",
            "observed": "Cmd-0056 actually returns LESSONS_INVALID on the new LSN-0138 title. The neutral receipt preserves its identity, bytes/digest and actual classifier refusal without exporting rejected text.",
            "requiredCorrection": detail, "evidence": ["command:cmd-0056", "checkpoint:STRICT-MEMORY-FINDING.json"]})
    write_json(CHECKPOINT / "FINDINGS.json", findings)
    print("G6-INT-008 GUARDRAIL_FAILURE escalated; label corrected; no scanner change or acceptance")
    return 0


if __name__ == "__main__":
    use_utf8_stdout()
    raise SystemExit(main())
