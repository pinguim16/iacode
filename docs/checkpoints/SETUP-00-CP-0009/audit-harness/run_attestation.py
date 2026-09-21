#!/usr/bin/env python3
"""Section 11: the external-PASS attestation mechanism, isolated check by check.

The end-to-end fixture runs in attacks.py show that a forged external PASS is refused,
but there the commit-binding error masks the specific defect under test. This script
calls the verification entry point directly, so each scenario is attributed to the
check it is meant to exercise, and the positive case is evaluated too.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
import os as _os
from pathlib import Path as _Path
_DEFAULT_ROOT = _Path(__file__).resolve().parents[4]

ROOT = Path(_os.environ.get("IACODE_ROOT") or _DEFAULT_ROOT)
sys.path.insert(0, str(ROOT / "scripts" / "development-ledger"))

from attestation import resolve_external_pass, verify_attestation  # noqa: E402

SUBJECT = "SETUP-00-CP-0008"
SUBJECT_COMMIT = subprocess.run(
    ["git", "rev-parse", "iacode-checkpoints/" + SUBJECT + "^{commit}"],
    cwd=ROOT, capture_output=True, text=True).stdout.strip()

RESULTS: list[dict] = []


def attestation(**overrides):
    document = {
        "schemaVersion": "1.0.0", "auditId": "M0-CP-0009-PROBE", "milestone": "M0",
        "auditorRole": "milestone independent auditor", "tool": "a tool",
        "provider": "a provider", "model": "a model",
        "subjectCheckpoint": SUBJECT, "subjectCommit": SUBJECT_COMMIT,
        "auditCheckpoint": "SETUP-00-CP-0007",
        "auditCommit": "502c554575f717c1d57290e4f4aafa575e41170e",
        "reviewResult": "APPROVED", "redTeamResult": "RED_TEAM_PASS",
        "completeness": 100.0, "evidenceCoverage": 100.0, "testResult": "PASS",
        "createdAt": "2026-09-20T23:30:00Z",
    }
    document.update(overrides)
    document["__path"] = "probe-attestation.json"
    return document


def probe(scenario_id, description, marker, subject=SUBJECT, commit=SUBJECT_COMMIT, **overrides):
    errors = verify_attestation(ROOT, attestation(**overrides), subject, commit)
    matched = [error for error in errors if marker.lower() in error.lower()] if marker else errors
    RESULTS.append({"id": scenario_id, "description": description, "expected": "reject",
                    "marker": marker, "observed": errors[:4] or ["no error"],
                    "result": "DEFENDED" if matched else "ESCAPED"})
    print("[" + scenario_id + "] " + RESULTS[-1]["result"] + " :: " + description)
    for line in RESULTS[-1]["observed"]:
        print("      " + str(line)[:220])


def main() -> int:
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)

    # Positive control at the verification level.
    errors = verify_attestation(ROOT, attestation(), SUBJECT, SUBJECT_COMMIT)
    RESULTS.append({"id": "EXT-000", "description": "a structurally valid attestation",
                    "expected": "accept", "observed": errors or ["no error"],
                    "result": "ACCEPTED" if not errors else "REFUSED"})
    print("[EXT-000] " + RESULTS[-1]["result"] + " :: a structurally valid attestation")
    for line in RESULTS[-1]["observed"]:
        print("      " + str(line)[:220])

    probe("EXT-001", "a forged secondToolValidation with no attestation behind it", "")
    # EXT-001 is really about resolve_external_pass, so run it at that level instead.
    RESULTS.pop()
    attestation_found, reasons = resolve_external_pass(ROOT, "M0", SUBJECT, SUBJECT_COMMIT)
    RESULTS.append({"id": "EXT-001",
                    "description": "a forged secondToolValidation with no attestation in the repository",
                    "expected": "reject", "marker": "may not be self-asserted",
                    "observed": reasons or ["no error"],
                    "result": "DEFENDED" if any("may not be self-asserted" in r for r in reasons)
                    else "ESCAPED"})
    print("[EXT-001] " + RESULTS[-1]["result"] + " :: " + RESULTS[-1]["description"])
    for line in RESULTS[-1]["observed"]:
        print("      " + str(line)[:220])

    probe("EXT-002", "a forged MILESTONE_EXTERNAL_PASS backed by an attestation for nothing",
          "attests checkpoint", subjectCheckpoint="SETUP-00-CP-0001")
    probe("EXT-003", "an attestation copied from an audit of another checkpoint",
          "attests checkpoint", subjectCheckpoint="SETUP-00-CP-0006")
    probe("EXT-004", "an attestation whose auditor is the audited checkpoint itself",
          "may not be authored by the delivery it judges", auditCheckpoint=SUBJECT)
    probe("EXT-005", "an attestation naming a subject checkpoint that is not the one promoted",
          "attests checkpoint", subjectCheckpoint="SETUP-00-CP-0005")
    probe("EXT-006", "an attestation naming a different subject commit",
          "attests commit", subjectCommit="0" * 40)
    probe("EXT-007", "review REWORK_REQUIRED with an external PASS claimed",
          "requires APPROVED", reviewResult="REWORK_REQUIRED")
    probe("EXT-008", "Red Team FAIL with an external PASS claimed",
          "requires RED_TEAM_PASS", redTeamResult="RED_TEAM_FAIL")
    probe("EXT-009", "an incomplete audit with an external PASS claimed",
          "requires 100.0", completeness=93.22)
    probe("EXT-009b", "an audit with incomplete evidence coverage",
          "requires 100.0", evidenceCoverage=99.0)
    probe("EXT-009c", "an audit whose test result is FAIL",
          "requires PASS", testResult="FAIL")
    probe("EXT-010", "an attestation whose audit checkpoint does not exist",
          "does not exist", auditCheckpoint="SETUP-00-CP-9999")
    probe("EXT-010b", "an attestation with no auditor role recorded",
          "requires auditorRole", auditorRole=None)
    probe("EXT-010c", "an attestation with no auditing tool recorded",
          "requires tool", tool=None)

    (out / "attestation-results.json").write_text(
        json.dumps(RESULTS, indent=2) + "\n", encoding="utf-8", newline="\n")
    bad = [r for r in RESULTS if r["result"] in ("ESCAPED", "REFUSED")]
    print("TOTAL=" + str(len(RESULTS)) + " PROBLEMS=" + str(len(bad)))
    for item in bad:
        print(" - " + item["id"] + ": " + str(item["observed"])[:300])
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
