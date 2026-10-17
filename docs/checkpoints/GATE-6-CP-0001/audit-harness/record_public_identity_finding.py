"""Confirm actual privacy-classification false positive without publishing credentials."""

import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parents[1]
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))

from ledger_common import load_json, utc_now, use_utf8_stdout, write_json
from lessons import load_lessons, save_lessons


def main() -> int:
    actual = load_json(CHECKPOINT / "suite-attempts/API-UNIT-0004.json")
    if actual["exitCode"] != 1 or actual["unsafeOutputOccurrences"] != 0:
        raise ValueError("the actual safe classifier diagnostic red is required")
    cause = ("The runtime put the MinIO public account/access identity in the same exact-value set "
             "as bearer keys and passwords. The committed public identity occurs in legitimate "
             "quality package/report names, so the actual owning-image classifier refuses those "
             "bytes with AUTHORIZATION_MATERIAL_REFUSED. Field masking/type alone is not a "
             "definition of a secret. No value is globally allowlisted and actual secret scanning "
             "or password protection may not be weakened.")
    findings = load_json(CHECKPOINT / "FINDINGS.json")
    if not any(row["findingId"] == "G6-INT-006" for row in findings["findings"]):
        findings["findings"].append({"findingId": "G6-INT-006", "severity": "HIGH",
            "title": "Public storage identity misclassified as bearer secret", "status": "OPEN",
            "expected": "Public source package names remain valid while actual HMAC/provider/storage/database secrets and their declared forms remain refused.",
            "observed": "Cmd-0040: new explicit credential-free runtime classifier case fails AUTHORIZATION_MATERIAL_REFUSED; 172 other API cases pass. Cmd-0038 also retains the first live clean-capture control failure after real provider/sandbox task and quality PASS; its original upstream code was not recorded, so that live causal link requires retest.",
            "rootCause": cause, "evidence": ["command:cmd-0038", "command:cmd-0040",
                "file:docs/checkpoints/GATE-6-CP-0001/suite-attempts/API-UNIT-0004.log",
                "file:docs/checkpoints/GATE-6-CP-0001/attempts/EXPERIENCE-LIVE-0001.json"]})
    write_json(CHECKPOINT / "FINDINGS.json", findings)
    lessons = load_lessons(ROOT)
    if not any(row["lessonId"] == "LSN-0138" for row in lessons):
        now = utc_now()
        lessons.append({"lessonId": "LSN-0138",
            "title": "Secret projection distinguishes public identities from authorization secrets",
            "category": "security", "severity": "HIGH",
            "source": {"gate": "GATE-6", "checkpoint": CHECKPOINT.name, "finding": "G6-INT-006"},
            "symptom": "A configured public MinIO identity collides with legitimate quality package/report text and a real runtime classifier returns AUTHORIZATION_MATERIAL_REFUSED.",
            "rootCauseSummary": cause,
            "resolution": "Project actual secret components by their contract: retain HMAC/provider/storage/database/Redis passwords and all declared encoded-form detection; do not add a public account identity as a bearer secret or globally exempt a word.",
            "prevention": [], "guardrails": [], "evidence": [
                "file:docs/checkpoints/GATE-6-CP-0001/suite-attempts/API-UNIT-0004.log",
                "file:docs/checkpoints/GATE-6-CP-0001/COMMANDS.jsonl"],
            "applicability": {"gates": ["*"], "scopes": [], "technologies": [], "modules": [],
                "requiredCheck": "Known-secret projection must distinguish public identities from actual passwords/bearer values; use the real configured field semantics, preserve unknown-secret detection and exact raw/encoded refusal of actual secrets.",
                "requiredEvidence": "Actual owning-runtime public-identity clean control plus opaque password/bearer adverse controls, and complete real source capture without any detector weakening."},
            "status": "CONFIRMED", "recurrenceKey": "security/public-account-identity-treated-as-bearer-secret",
            "recurrenceCount": 0, "guardrailFailures": [], "createdAt": now, "updatedAt": now,
            "provenance": {"sourceType": "repository-generated", "provider": "local-execution",
                "model": None, "ownership": "project-generated evidence", "license": "not-applicable",
                "notes": "Actual credential-free diagnostic; no operational value or private reasoning retained."},
            "trainingEligibility": {"trainingAllowed": False, "ragAllowed": False,
                "distillationAllowed": False, "justification": None},
            "notes": "Confirmed before repair; no live capture, guard restoration or Gate acceptance is claimed."})
    save_lessons(ROOT, lessons)
    print("G6-INT-006/LSN-0138 CONFIRMED; no detector exception or positive rights grant introduced")
    return 0


if __name__ == "__main__":
    use_utf8_stdout()
    raise SystemExit(main())
