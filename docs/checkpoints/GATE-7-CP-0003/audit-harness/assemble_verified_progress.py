"""Project actual complete current assurance; preserve the original failed rework evidence."""

from __future__ import annotations

from acceptance_evidence import CHECKPOINT, current_execution, current_greenkeeper, sealed_module


def main():
    from ledger_common import LedgerError, load_json, utc_now, write_json

    current_execution()
    _receipt, _cycle, folder = current_greenkeeper()
    path = CHECKPOINT / "INTERNAL-ENVIRONMENT-REWORK.json"
    rework = load_json(path)
    for item in rework["items"]:
        if item.get("status") == "RESOLVED_BY_COMPLETED_UNCHANGED_RETRY":
            proof = load_json(CHECKPOINT / item["successEvidence"])
            if proof.get("exitCode") != 0 or proof.get("sourceUnchanged") is not True:
                raise LedgerError("original completed retry does not resolve")
            continue
        if item.get("status") not in {
            "LOCAL_CORRECTION_DEMONSTRATED_WHOLE_ASSURANCE_PENDING",
            "RESOLVED_CURRENT_WHOLE_ASSURANCE",
        } or not item.get("currentProof"):
            raise LedgerError("unresolved or unproved internal rework: " + item["id"])
        for reference in item["currentProof"]:
            if not (CHECKPOINT / reference).is_file():
                raise LedgerError("missing original local rework proof: " + reference)
    # The sealed assembler checks DCV/Red Team/mirror when present and refuses stale/red ones.
    # It records physical canonical test counts without summing overlapping invocations.
    result = sealed_module("assemble_verified_progress").main()
    if result != 0:
        return result
    for item in rework["items"]:
        if item.get("status") == "RESOLVED_BY_COMPLETED_UNCHANGED_RETRY":
            continue
        item.setdefault("statusBeforeWholeAssurance", item["status"])
        item["status"] = "RESOLVED_CURRENT_WHOLE_ASSURANCE"
        item["wholeAssuranceEvidence"] = [folder + "/RECEIPT.json", "VERIFY.json"]
        item["wholeAssuranceObservedAt"] = utc_now()
    rework["currentResolution"] = (
        "Actual current whole mandatory quality and immutable functional execution passed. "
        "Original failures, observations, classifications and local controls are preserved. "
        "This is internal corrective closure, not independent M2 validation."
    )
    write_json(path, rework)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
