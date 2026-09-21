#!/usr/bin/env python3
"""Record the auditor's verdict on every canonical SETUP-00 requirement.

This is the audit's own requirements matrix, in the shape SETUP-00-CP-0007 used: the
canonical Gate specification re-stated with the verdict this audit reached for each row,
and the evidence that supports it.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
import os as _os
from pathlib import Path as _Path
_DEFAULT_ROOT = _Path(__file__).resolve().parents[4]

ROOT = Path(_os.environ.get("IACODE_ROOT") or _DEFAULT_ROOT)
CP = ROOT / "docs" / "checkpoints" / "SETUP-00-CP-0009"

AUDIT = "checkpoint:AUDIT-EXECUTIONS.md"
MATRIX = "checkpoint:FINAL-M0-AUDIT-MATRIX.json"

# Rows this audit could not confirm, with the reason.
PARTIAL = {
    "7d.4": (
        "The rejection half of the control is complete and was reproduced fifteen ways, but the "
        "acceptance half is unreachable: a legitimate attestation must live in the tree of the "
        "commit it names as subjectCommit, and once the audit checkpoint commits it the subject "
        "can no longer be validated at all. No repository state satisfies the promotion, and no "
        "test covers acceptance. See finding CP9-F-001."),
    "7d.8": (
        "The anchor chain itself is complete and defended every mutation this audit ran, but its "
        "verifying test binds the exclusion to the literal name SETUP-00-CP-0008, so the "
        "mandatory tests gate turns red for the next delivery the moment this checkpoint is "
        "sealed. A guardrail that must be edited for every successor is not yet a durable "
        "guardrail. See finding CP9-F-002."),
}

# The audit evidence that answers each checklist section, beyond the artifact the row names.
SECTION_EVIDENCE = {
    "1": [MATRIX, AUDIT],
    "2": [MATRIX, AUDIT],
    "3": [MATRIX, AUDIT],
    "4": [MATRIX, AUDIT],
    "5": [MATRIX, AUDIT, "checkpoint:AUDIT-EXECUTIONS.json"],
    "6": [MATRIX, AUDIT, "checkpoint:AUDIT-EXECUTIONS.json"],
    "7": [MATRIX, AUDIT, "checkpoint:AUDIT-EXECUTIONS.json"],
    "7b": [MATRIX, AUDIT, "checkpoint:AUDIT-EXECUTIONS.json"],
    "7c": [MATRIX, AUDIT, "checkpoint:AUDIT-EXECUTIONS.json"],
    "7d": [MATRIX, AUDIT, "checkpoint:AUDIT-EXECUTIONS.json", "checkpoint:RED-TEAM-REPORT.md"],
    "8": [MATRIX, AUDIT, "checkpoint:REVIEW-REPORT.md", "checkpoint:RED-TEAM-REPORT.md"],
    "9": [MATRIX, AUDIT],
}

PATH_IN_BACKTICKS = re.compile(r"`([^`]+)`")


def artifact_paths(artifact: str) -> list[str]:
    """Concrete repository paths for the artifact column of a checklist row."""
    resolved: list[str] = []
    for candidate in PATH_IN_BACKTICKS.findall(artifact):
        candidate = candidate.strip()
        if not candidate or " " in candidate:
            continue
        if "*" in candidate:
            matches = sorted(ROOT.glob(candidate))
            if matches:
                resolved.append(matches[0].relative_to(ROOT).as_posix())
            continue
        target = ROOT / candidate
        if target.is_file():
            resolved.append(candidate)
        elif target.is_dir():
            files = sorted(item for item in target.rglob("*") if item.is_file())
            if files:
                resolved.append(files[0].relative_to(ROOT).as_posix())
    return resolved


def checklist_rows() -> dict[str, dict[str, str]]:
    pattern = re.compile(
        r"^\|\s*(?P<key>[0-9]+[a-z]?\.[0-9]+)\s*\|\s*(?P<description>.+?)\s*\|"
        r"\s*(?P<artifact>.+?)\s*\|\s*(?P<evidence>.+?)\s*\|\s*$")
    rows = {}
    for line in (ROOT / "docs" / "SETUP-00-CHECKLIST.md").read_text(
            encoding="utf-8").splitlines():
        match = pattern.match(line)
        if match and match.group("description") not in ("Requirement", "---"):
            rows[match.group("key")] = match.groupdict()
    return rows


def main() -> int:
    rows = checklist_rows()
    matrix = json.loads((CP / "REQUIREMENTS-MATRIX.json").read_text(encoding="utf-8"))
    closure = json.loads((CP / "CLOSURE-REQUIREMENTS.json").read_text(encoding="utf-8"))

    for entry in matrix["requirements"]:
        key = entry["sourceRef"].split("#", 1)[1]
        section = key.split(".", 1)[0]
        artifacts = artifact_paths(rows[key]["artifact"])
        implementation = ["file:" + path for path in artifacts] or [AUDIT]
        partial = key in PARTIAL
        entry["status"] = "PARTIAL" if partial else "COMPLETE"
        entry["implementationEvidence"] = implementation
        entry["testEvidence"] = ["command:cmd-0004", "command:cmd-0010"]
        entry["documentationEvidence"] = ["file:docs/SETUP-00-CHECKLIST.md"]
        entry["validationEvidence"] = list(SECTION_EVIDENCE.get(section, [MATRIX, AUDIT]))
        entry["justification"] = PARTIAL.get(key)
        entry["notes"] = ("Audited by the CP-0009 fresh-session independent audit; "
                          + ("not confirmed." if partial else "confirmed."))

    for entry in closure["requirements"]:
        key = entry["sourceRef"].split("#", 1)[1]
        source = next(item for item in matrix["requirements"]
                      if item["sourceRef"] == entry["sourceRef"])
        entry["implementationStatus"] = source["status"]
        entry["finalStatus"] = source["status"]
        entry["implementationEvidence"] = source["implementationEvidence"]
        entry["testEvidence"] = source["testEvidence"]
        entry["negativeTestEvidence"] = ["checkpoint:RED-TEAM-REPORT.md"]
        entry["documentationEvidence"] = source["documentationEvidence"]
        entry["validationEvidence"] = source["validationEvidence"]
        entry["guardrailEvidence"] = ["file:.iacode/memory/guardrails/registry.json"]
        entry["justification"] = source["justification"]
        entry["notes"] = source["notes"]

    (CP / "REQUIREMENTS-MATRIX.json").write_text(
        json.dumps(matrix, indent=2) + "\n", encoding="utf-8", newline="\n")
    (CP / "CLOSURE-REQUIREMENTS.json").write_text(
        json.dumps(closure, indent=2) + "\n", encoding="utf-8", newline="\n")

    complete = sum(1 for item in matrix["requirements"] if item["status"] == "COMPLETE")
    partial = sum(1 for item in matrix["requirements"] if item["status"] == "PARTIAL")
    total = len(matrix["requirements"])
    print("total=" + str(total) + " complete=" + str(complete) + " partial=" + str(partial)
          + " coverage=" + format(round(complete * 100.0 / total, 2), ".2f"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
