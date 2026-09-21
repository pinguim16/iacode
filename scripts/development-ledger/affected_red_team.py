#!/usr/bin/env python3
"""Report the adversarial position of a delivery by explicit, derived category.

``SETUP-00-CP-0009`` disclosed that its own report could be read two ways: "twenty additional
attacks" in one paragraph and "26/26 additional attacks including 6 attestation scenarios" in
another. Overlapping totals maintained by hand always drift, so every number here is derived from a
machine-readable source and each category is named:

    originalRedTeam          the mandatory battery of the registered audits, re-parsed from their
                             sealed reports
    additionalControlAttacks the additional battery, by the same derivation
    attestationScenarios     the attacks that target the audit-attestation model, counted as their
                             own category because they are the surface this delivery changed
    positiveControls         the executed positive paths, which an adversarial battery cannot
                             contain: a control that only refuses is not proven
    totalAdversarialScenarios the executed battery, which is the union of what the registry
                             requires and what this delivery's new surfaces deserve

    python scripts/development-ledger/affected_red_team.py --write
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from ledger_common import LedgerError, find_root, load_json, resolve_latest, utc_now, write_json
from policies import audit_attacks, load_audit_registry

ATTESTATION_TARGETS = ("external attestation", "pass vocabulary")


def build(root: Path, checkpoint: Path) -> dict[str, Any]:
    state = load_json(checkpoint / "STATE.json") if (checkpoint / "STATE.json").is_file() else {}
    milestone = str((state.get("milestone") or {}).get("id") or "M0")

    report_path = checkpoint / f"{milestone}-INTERNAL-RED-TEAM.json"
    if not report_path.is_file():
        raise LedgerError(f"{report_path.name} does not exist; run m0_red_team.py --write first")
    report = load_json(report_path)
    executed = [item for item in report.get("attacks") or [] if isinstance(item, dict)]
    executed_ids = {str(item.get("attackId")) for item in executed}

    registry_mandatory: dict[str, list[str]] = {}
    registry_additional: dict[str, list[str]] = {}
    for audit in load_audit_registry(root):
        identifier = str(audit.get("auditId"))
        attacks = audit_attacks(root, audit)
        registry_mandatory[identifier] = [
            item["id"] for item in attacks if item["mandatory"] == "true"]
        registry_additional[identifier] = [
            item["id"] for item in attacks if item["mandatory"] != "true"]

    required_mandatory = sorted({item for values in registry_mandatory.values() for item in values})
    required_additional = sorted(
        {item for values in registry_additional.values() for item in values})

    attestation = sorted(
        str(item.get("attackId")) for item in executed
        if str(item.get("target", "")).lower() in ATTESTATION_TARGETS)
    mandatory_executed = sorted(
        str(item.get("attackId")) for item in executed if item.get("mandatory"))
    additional_executed = sorted(
        str(item.get("attackId")) for item in executed if not item.get("mandatory"))
    defended = sorted(
        str(item.get("attackId")) for item in executed if item.get("result") == "DEFENDED")
    escaped = sorted(
        str(item.get("attackId")) for item in executed if item.get("result") == "ESCAPED")

    positives: list[dict[str, Any]] = []
    for name, label in (("POSITIVE-PROMOTION-VALIDATION.json", "positive milestone promotion"),
                        ("SUCCESSOR-DURABILITY.json", "successor anchor durability")):
        path = checkpoint / name
        if path.is_file():
            document = load_json(path)
            positives.append({
                "control": label,
                "artifact": name,
                "result": document.get("result"),
                "checks": document.get("total"),
                "passed": document.get("passed"),
            })

    return {
        "schemaVersion": "1.0.0",
        "checkpoint": checkpoint.name,
        "milestone": milestone,
        "generatedAt": utc_now(),
        "source": {
            "executedBattery": report_path.name,
            "registry": ".iacode/policies/audit-registry.json",
            "reports": [audit.get("redTeamReport") for audit in load_audit_registry(root)],
        },
        "categories": {
            "originalRedTeam": {
                "description": "the mandatory battery of every registered audit, re-parsed from "
                               "its sealed report",
                "required": required_mandatory,
                "executed": mandatory_executed,
                "count": len(mandatory_executed),
                "missing": sorted(set(required_mandatory) - executed_ids),
            },
            "additionalControlAttacks": {
                "description": "the additional battery of every registered audit, plus the attacks "
                               "this delivery's new surfaces deserve",
                "required": required_additional,
                "executed": additional_executed,
                "count": len(additional_executed),
                "missing": sorted(set(required_additional) - executed_ids),
            },
            "attestationScenarios": {
                "description": "attacks that target the audit-attestation model and the milestone "
                               "status vocabulary, which is the surface this delivery changed",
                "executed": attestation,
                "count": len(attestation),
            },
            "positiveControls": {
                "description": "executed positive paths; an adversarial battery cannot contain "
                               "them, and a control proven only by refusals is not proven",
                "executed": positives,
                "count": len(positives),
            },
        },
        "totalAdversarialScenarios": len(executed),
        "defended": len(defended),
        "escaped": len(escaped),
        "baselineControl": report.get("baselineControl"),
        "result": "DEFENDED" if not escaped and not (
            set(required_mandatory) - executed_ids) else "FAIL",
    }


def render_markdown(document: dict[str, Any]) -> str:
    categories = document["categories"]
    lines = [
        "# Affected Red Team",
        "",
        f"Result: `{document['result']}`",
        "",
        f"- Checkpoint: `{document['checkpoint']}`",
        f"- Generated: `{document['generatedAt']}`",
        f"- Executed battery: `{document['source']['executedBattery']}`",
        f"- Null-mutation control: `{(document.get('baselineControl') or {}).get('result')}`",
        "",
        "Every number below is derived from the machine-readable battery and the audit registry; no",
        "total here is maintained by hand, and the categories do not overlap.",
        "",
        "| Category | Count | Missing |",
        "|---|---|---|",
    ]
    for key in ("originalRedTeam", "additionalControlAttacks", "attestationScenarios",
                "positiveControls"):
        entry = categories[key]
        lines.append("| `%s` | %d | %s |" % (
            key, entry["count"],
            ", ".join(entry.get("missing") or []) or "none"))
    lines += [
        "",
        f"- Total adversarial scenarios executed: `{document['totalAdversarialScenarios']}`",
        f"- Defended: `{document['defended']}`; escaped: `{document['escaped']}`",
        "",
        "## Categories",
        "",
    ]
    for key in ("originalRedTeam", "additionalControlAttacks", "attestationScenarios"):
        entry = categories[key]
        lines += [
            f"### {key}",
            "",
            entry["description"] + ".",
            "",
            "- Executed: " + (", ".join(f"`{item}`" for item in entry["executed"]) or "_none_"),
            "",
        ]
    lines += ["### positiveControls", "", categories["positiveControls"]["description"] + ".", ""]
    for item in categories["positiveControls"]["executed"]:
        lines.append(f"- `{item['control']}`: `{item['result']}`, {item['passed']} of "
                     f"{item['checks']} checks (`{item['artifact']}`)")
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path)
    parser.add_argument("--checkpoint", type=Path)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    root = find_root(args.root) if args.root else find_root()
    checkpoint = args.checkpoint or resolve_latest(root)
    if not checkpoint.is_absolute():
        checkpoint = root / checkpoint

    document = build(root, checkpoint)
    if args.write:
        write_json(checkpoint / "AFFECTED-RED-TEAM.json", document)
        (checkpoint / "AFFECTED-RED-TEAM.md").write_text(
            render_markdown(document), encoding="utf-8", newline="\n")
    if args.json:
        print(json.dumps(document, indent=2, ensure_ascii=False))
    else:
        categories = document["categories"]
        print("AFFECTED_RED_TEAM=%s total=%d defended=%d escaped=%d mandatory=%d additional=%d "
              "attestation=%d positive=%d" % (
                  document["result"], document["totalAdversarialScenarios"], document["defended"],
                  document["escaped"], categories["originalRedTeam"]["count"],
                  categories["additionalControlAttacks"]["count"],
                  categories["attestationScenarios"]["count"],
                  categories["positiveControls"]["count"]))
        for key in ("originalRedTeam", "additionalControlAttacks"):
            for missing in categories[key].get("missing") or []:
                print(f"- MISSING {key}: {missing}")
    return 0 if document["result"] == "DEFENDED" else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except LedgerError as exc:
        print(f"LEDGER_ERROR: {exc}")
        sys.exit(2)
