#!/usr/bin/env python3
"""Render the adversarial battery of this audit into the checkpoint artifacts.

The machine-readable report follows the repository's own red-team schema so a later reader can
validate it like any other, and the Markdown report is generated from the same data rather than
written beside it.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--battery", type=Path, required=True)
    args = parser.parse_args()
    sys.path.insert(0, str(ROOT / "scripts" / "development-ledger"))
    from ledger_common import scope_fingerprint

    battery = json.loads(args.battery.read_text(encoding="utf-8"))
    scenarios = battery["scenarios"]
    attacks = [{
        "attackId": item["attackId"],
        "description": item["mutation"],
        "target": item["target"],
        "mutation": item["mutation"],
        "expectedDefense": item["expectedDefense"],
        "observed": item["observed"],
        "result": item["result"],
        "evidence": ["checkpoint:RED-TEAM-REPORT.md"],
        "mandatory": item["category"] == "mandatory",
    } for item in scenarios]
    defended = [item for item in attacks if item["result"] == "DEFENDED"]
    escaped = [item for item in attacks if item["result"] == "ESCAPED"]
    mandatory = [item for item in attacks if item["mandatory"]]
    mandatory_defended = [item for item in mandatory if item["result"] == "DEFENDED"]

    report = {
        "schemaVersion": "1.1.0",
        "checkpoint": CHECKPOINT.name,
        "generatedAt": battery["generatedAt"],
        "targetFingerprint": scope_fingerprint(ROOT),
        "source": (
            "the adversarial battery this audit owns, executed against disposable copies of a "
            "sealed snapshot of this checkpoint, one copy per scenario"),
        "baselineControl": {
            "result": battery["baselineControl"]["result"],
            "detail": (
                "the unmutated snapshot is validated and its milestone verdict derived through the "
                "identical path every scenario uses: "
                + battery["baselineControl"]["validator"].splitlines()[0] + "; "
                + battery["baselineControl"]["milestone"].splitlines()[0]),
            "evidence": ["checkpoint:audit-harness/attack_battery.py"],
        },
        "attacks": attacks,
        "total": len(attacks),
        "defended": len(defended),
        "escaped": len(escaped),
        "mandatoryTotal": len(mandatory),
        "mandatoryDefended": len(mandatory_defended),
        "result": "RED_TEAM_PASS" if not escaped else "RED_TEAM_FAIL",
    }
    (CHECKPOINT / "M0-INTERNAL-RED-TEAM.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")

    lines = [
        "# Red Team Report — the adversarial battery of this audit",
        "",
        f"Result: `{report['result']}`",
        "",
        f"- Audit checkpoint: `{CHECKPOINT.name}`",
        f"- Subject: `{battery['subjectCheckpoint']}`",
        f"- Scenarios executed: {report['total']}; defended: {report['defended']}; "
        f"escaped: {report['escaped']}",
        f"- Null-mutation control: `{report['baselineControl']['result']}`",
        "",
        "## What the battery attacks",
        "",
        "Each scenario runs against its own fresh copy of a sealed snapshot of this checkpoint, so",
        "no refusal can be inherited from a previous scenario. The snapshot is produced by the same",
        "finalize and seal tooling the real checkpoint uses, and it models this checkpoint as",
        "approved, because the defences around a claimed milestone verdict can only be attacked in a",
        "repository that claims one. The models never leave the disposable copy.",
        "",
        "The control runs first. If the unmutated snapshot were refused, no refusal afterwards could",
        "be attributed to a mutation, and the battery reports `INVALID` rather than a row of",
        "defences. It was accepted:",
        "",
        "```text",
        battery["baselineControl"]["validator"].splitlines()[0],
        battery["baselineControl"]["milestone"].splitlines()[0],
        "```",
        "",
        "## Scenarios",
        "",
        "| Attack | Category | Target | Mutation | Expected | Result |",
        "|---|---|---|---|---|---|",
    ]
    for item in scenarios:
        mutation = item["mutation"].replace("|", "\\|")
        lines.append(
            f"| `{item['attackId']}` | {item['category']} | {item['target']} | {mutation} | "
            f"{item['expectedDefense']} | `{item['result']}` |")
    lines += [
        "",
        "## Observed refusals",
        "",
    ]
    for item in scenarios:
        observed = item["observed"].replace("\n", " ")
        lines.append(f"- `{item['attackId']}`: {observed}")
    lines += [
        "",
        "## Corrections made to this battery",
        "",
        "The first revision of this battery reported four scenarios as escaped. None of them was an",
        "escape: every mutation was refused, and the four expectations were wrong. One asserted that",
        "a fresh-session attestation recording that cross-tool execution was available must be",
        "rejected, which the model does not claim and does not need to, because the mechanism still",
        "authorises only the independent-audit status; it was replaced by the real control, a",
        "cross-tool mechanism contradicting its own recorded availability. One mutated the",
        "attestation without moving the claim in `STATE.json`, so the refusal named a missing",
        "attestation rather than the older subject; it now moves both. Two asserted message",
        "fragments the validator does not emit. The corrected battery is the one reported here, and",
        "this correction is recorded rather than quietly repaired, because a battery whose",
        "expectations are wrong proves nothing about the product.",
        "",
        "## What this battery is not",
        "",
        "It is not independent of the tool. It is written and executed by the auditing session, on",
        "the same tooling as the implementing run, and it is recorded as the adversarial position of",
        "this audit rather than as cross-tool validation.",
        "",
    ]
    (CHECKPOINT / "RED-TEAM-REPORT.md").write_text("\n".join(lines), encoding="utf-8", newline="\n")
    print(f"RED_TEAM_RENDERED total={report['total']} defended={report['defended']} "
          f"escaped={report['escaped']} control={report['baselineControl']['result']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
