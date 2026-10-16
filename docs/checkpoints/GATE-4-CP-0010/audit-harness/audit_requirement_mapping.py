#!/usr/bin/env python3
"""Check all proposed source evidence before final reports exist; never complete a requirement."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))

import complete_requirements as mapping
from delivery_assurance import collect_test_ids, load_command_results, resolve_evidence
from derive_requirements import EVIDENCE_FIELDS
from ledger_common import LedgerError, load_json, utc_now, use_utf8_stdout, write_json

PENDING_FINAL_REPORTS = {"checkpoint:VERIFY.json", "checkpoint:FUNCTIONAL-SCENARIOS.json"}


def main() -> int:
    destination = CHECKPOINT / "REQUIREMENT-MAPPING-PREVIEW.json"
    if destination.exists():
        raise LedgerError("preserve the prior mapping observation")
    baseline = subprocess.run(
        ["git", "show", f"iacode-checkpoints/{mapping.SUBJECT}:"
         f"docs/checkpoints/{mapping.SUBJECT}/CLOSURE-REQUIREMENTS.json"],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8", check=True,
    )
    previous = {row["sourceRef"]: row for row in json.loads(baseline.stdout)["requirements"]}
    requirements = load_json(CHECKPOINT / "CLOSURE-REQUIREMENTS.json")["requirements"]
    tests, commands = collect_test_ids(ROOT), load_command_results(CHECKPOINT)
    rows = []
    for requirement in requirements:
        reference = requirement["sourceRef"]
        evidence = mapping.corrective(reference)
        failures = []
        if evidence is None:
            prior = previous.get(reference)
            if prior is None or prior.get("finalStatus") != "COMPLETE":
                failures.append("no complete baseline or corrective mapping")
                evidence = {}
            else:
                evidence = {field: [mapping.historical(value) for value in prior.get(field, [])]
                            for field in EVIDENCE_FIELDS}
                evidence["validationEvidence"].append("checkpoint:VERIFY.json")
        pending = []
        for field in EVIDENCE_FIELDS:
            references = evidence.get(field, [])
            if not references:
                failures.append(f"empty evidence field: {field}")
            for value in references:
                if field == "validationEvidence" and value in PENDING_FINAL_REPORTS:
                    pending.append(value)
                    continue
                error = resolve_evidence(ROOT, CHECKPOINT, value, commands, tests)
                if error:
                    failures.append(f"{field}: {value}: {error}")
        rows.append({"sourceRef": reference, "sourceEvidenceErrors": failures,
                     "pendingFinalEvidence": sorted(set(pending)),
                     "result": "SOURCE_MAPPING_ERROR" if failures else "PENDING_FINAL_VERIFICATION"})
    errors = sum(bool(row["sourceEvidenceErrors"]) for row in rows)
    write_json(destination, {
        "schemaVersion": "1.0.0", "generatedAt": utc_now(),
        "scope": "read-only source mapping preview; no requirement status or verdict is changed",
        "expectedRequirements": len(requirements), "inspectedRequirements": len(rows),
        "sourceMappingErrors": errors, "requirements": rows,
        "result": "SOURCE_MAPPING_ERROR" if errors else "PENDING_FINAL_VERIFICATION",
        "promotionEvidence": False,
    })
    print(f"MAPPING_PREVIEW inspected={len(rows)} source_mapping_errors={errors} "
          "final_verification=PENDING promotion=false")
    for row in rows:
        for error in row["sourceEvidenceErrors"]:
            print(f"- {row['sourceRef']}: {error}")
    return 1 if errors else 0


if __name__ == "__main__":
    use_utf8_stdout()
    raise SystemExit(main())
