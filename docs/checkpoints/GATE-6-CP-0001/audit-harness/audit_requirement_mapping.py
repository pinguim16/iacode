"""Check authored mapping references now, without issuing any requirement/functional verdict."""

import json
import runpy
import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/development-ledger"))
from check_functional_acceptance import functional_requirement_ids

requirements = runpy.run_path(str(CHECKPOINT / "audit-harness/complete_requirements.py"))
functional = runpy.run_path(str(CHECKPOINT / "audit-harness/complete_functional_acceptance.py"))
closure = json.loads((CHECKPOINT / "CLOSURE-REQUIREMENTS.json").read_text(encoding="utf-8"))
keys = {row["sourceRef"].split("#")[-1] for row in closure["requirements"]
        if row["sourceRef"].startswith("canonical:")}
if keys != set(requirements["CANONICAL"]):
    raise ValueError("authored canonical mapping does not equal the derived complete set")
references = [reference for mapping in requirements["CANONICAL"].values()
              for values in mapping.values() for reference in values if reference.startswith("file:")]
for artifacts, cases in requirements["NEW_LESSONS"].values():
    references.extend("file:" + path for path in artifacts + cases)
for reference in set(references):
    if not (ROOT / reference[5:]).is_file():
        raise ValueError("authored file/test reference is absent: " + reference)
expected = set(functional_requirement_ids(ROOT, "GATE-6"))
actual = {"GATE-6-" + key for group in functional["SCENARIOS"].values() for key in group["requirements"].split()}
if actual != expected:
    raise ValueError("authored functional map differs from canonical derivation: " + str(actual ^ expected))
print(json.dumps({"kind": "AUTHORING_REFERENCE_CHECK_NOT_ACCEPTANCE", "canonicalMappings": len(keys),
                  "uniqueExistingFiles": len(set(references)), "functionalRequirements": len(expected),
                  "functionalScenarios": len(functional["SCENARIOS"]),
                  "requirementsPromoted": 0, "acceptanceIssued": False}))
