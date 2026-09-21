#!/usr/bin/env python3
"""Section 17: the four guardrails CP-0007 reported as ineffective, plus a variation each.

CP-0007 recorded: "Ineffective/bypassed on that path: LSN-0005, LSN-0007, LSN-0008, LSN-0009."
For each one this reproduces the original bypass and then a reasonable variation of it, so a
correction that only closes the literal reported path is visible.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
import os as _os
from pathlib import Path as _Path
_DEFAULT_ROOT = _Path(__file__).resolve().parents[4]

sys.path.insert(0, str(Path(__file__).parent))
from scenarios import (  # noqa: E402
    Delivery, RESULTS, ROOT, mandatory_gates, read_json, record, write_json,
)

sys.path.insert(0, str(ROOT / "scripts" / "development-ledger"))
from validate_checkpoint import POSITIVE_TERMINAL_STATUSES  # noqa: E402


def main() -> int:
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)

    # ---- LSN-0005 / M0-F-001: a terminal status that skipped the assurance gates -------
    delivery = Delivery()
    state = delivery.state(status="MILESTONE_EXTERNAL_PASS")
    state["greenKeeper"] = {**state["greenKeeper"], "status": "FAIL"}
    state["milestone"] = {**state["milestone"], "status": "PASSED"}
    record("GRD-LSN-0005-original",
           "original bypass: MILESTONE_EXTERNAL_PASS carrying a red Green Keeper",
           "reject", delivery.assurance(state), "GREEN_KEEPER_GATE=PASS")
    delivery.close()

    missed = []
    for status in POSITIVE_TERMINAL_STATUSES:
        delivery = Delivery()
        state = delivery.state(status=status)
        state["deliveryCompleteness"] = {**state["deliveryCompleteness"], "status": "FAIL"}
        errors = delivery.assurance(state)
        if not any("DELIVERY_COMPLETENESS_GATE=PASS" in error for error in errors):
            missed.append(status)
        delivery.close()
    record("GRD-LSN-0005-variation",
           "variation: a red completeness gate under every positive terminal status",
           "reject", ["statuses that escaped: " + (", ".join(missed) or "none")],
           "escaped: none")

    # ---- LSN-0007 / M0-F-002: an internally authored external verdict ------------------
    delivery = Delivery()
    state = delivery.state(status="MILESTONE_EXTERNAL_PASS")
    state["milestone"] = {**state["milestone"], "status": "PASSED"}
    state["secondToolValidation"] = {"status": "PASSED", "tool": "self", "provider": "self",
                                     "model": "self", "validatedAt": "2026-09-20T23:00:00Z",
                                     "justification": None, "evidence": []}
    record("GRD-LSN-0007-original",
           "original bypass: complete second-tool attribution written by the delivery itself",
           "reject", delivery.memory(state), "may not be self-asserted")
    delivery.close()

    delivery = Delivery()
    state = delivery.state()
    state["externalAttestation"] = {"status": "VERIFIED",
                                    "path": ".iacode/attestations/does-not-exist.json",
                                    "auditId": "FORGED", "evidence": []}
    state["secondToolValidation"] = {"status": "PASSED", "tool": "t", "provider": "p",
                                     "model": "m", "validatedAt": "2026-09-20T23:00:00Z",
                                     "justification": None, "evidence": []}
    record("GRD-LSN-0007-variation",
           "variation: externalAttestation declared VERIFIED against a file that does not exist",
           "reject", delivery.memory(state), "external validation")
    delivery.close()

    # ---- LSN-0008 / M0-F-006: the completeness denominator ------------------------------
    delivery = Delivery()
    delivery.edit("REQUIREMENTS-MATRIX.json",
                  lambda d: d.update({"requirements": [
                      r for r in d["requirements"]
                      if r.get("sourceRef") != "canonical:SETUP-00#1.1"]}))
    delivery._write_report()
    state = delivery.state()
    state["requirementsMatrix"] = {**state["requirementsMatrix"], "total": delivery.total - 1,
                                   "complete": delivery.total - 1,
                                   "mandatory": delivery.mandatory - 1}
    record("GRD-LSN-0008-original",
           "original bypass: delete a mandatory requirement and recompute every stored count",
           "reject", delivery.assurance(state), "canonical expected set requires")
    delivery.close()

    delivery = Delivery()

    def substitute(document):
        for row in document["requirements"]:
            if row.get("sourceRef") == "canonical:SETUP-00#1.1":
                row["sourceRef"] = "local:an invented delivery requirement"
                break

    delivery.edit("REQUIREMENTS-MATRIX.json", substitute)
    delivery._write_report()
    record("GRD-LSN-0008-variation",
           "variation: keep the row count but substitute a canonical anchor with a local one",
           "reject", delivery.assurance(), "canonical expected set requires")
    delivery.close()

    # ---- LSN-0009 / M0-F-005: the vacuous Green Keeper PASS -----------------------------
    delivery = Delivery()
    delivery._write_rework_log(requiredGates=[], gateResults=[], commandsExecuted=[])
    record("GRD-LSN-0009-original",
           "original bypass: a GREEN cycle measured against no gate at all",
           "reject", delivery.assurance(), "canonical mandatory set")
    delivery.close()

    delivery = Delivery()
    delivery._write_rework_log(
        requiredGates=["tests"],
        gateResults=[{"gate": "tests", "commandId": "cmd-0001", "exitCode": 0,
                      "mandatory": True}])
    record("GRD-LSN-0009-variation",
           "variation: a GREEN cycle measured against a single mandatory gate",
           "reject", delivery.assurance(), "canonical mandatory set")
    delivery.close()

    # The invocation-level half of LSN-0009: the caller cannot narrow the set.
    proc = subprocess.run(
        [sys.executable, "scripts/development-ledger/green_keeper.py", "--help"],
        cwd=ROOT, capture_output=True, text=True)
    canonical = list(mandatory_gates(ROOT))
    record("GRD-LSN-0009-policy",
           "the mandatory gate set is read from policy, and --gates only adds to a run",
           "policy-derived",
           ["canonical mandatory set = " + ", ".join(canonical),
            "green_keeper --gates help: " + " ".join(
                line.strip() for line in proc.stdout.splitlines()
                if "--gates" in line or "add" in line)[:300]],
           "canonical mandatory set =")

    (out / "guardrail-results.json").write_text(
        json.dumps(RESULTS, indent=2) + "\n", encoding="utf-8", newline="\n")
    escaped = [r for r in RESULTS if r["result"] in ("ESCAPED", "REFUSED")]
    print("TOTAL=" + str(len(RESULTS)) + " ESCAPED=" + str(len(escaped)))
    return 0 if not escaped else 1


if __name__ == "__main__":
    sys.exit(main())
