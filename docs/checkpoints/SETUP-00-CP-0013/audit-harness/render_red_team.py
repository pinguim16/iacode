#!/usr/bin/env python3
"""Merge this audit's two batteries into the checkpoint's Red Team artifacts.

``attack_battery.py`` attacks the controls directly. ``attack_battery_refreshed.py`` re-runs the
three scenarios that the file-inventory binding refused before they reached their target, this time
re-deriving the declared hashes first, so the refusal is attributable to the control under test.
Both carry a null-mutation control, and both controls must be ``VALID`` or nothing here is written.

    python render_red_team.py --battery <a.json> --refreshed <b.json>
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

HARNESS = Path(__file__).resolve().parent
CHECKPOINT = HARNESS.parent
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "development-ledger"))

from ledger_common import scope_fingerprint  # noqa: E402

SOURCE = (
    "The adversarial battery of the SETUP-00-CP-0013 fresh-session independent audit, authored by "
    "this audit and executed against disposable clones of the sealed SETUP-00-CP-0012 checkout, "
    "one clone per scenario. It is independent of m0_red_team.py, which this audit also executed "
    "separately and which reported 73 of 73 defended."
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--battery", type=Path, required=True)
    parser.add_argument("--refreshed", type=Path, required=True)
    args = parser.parse_args()

    direct = json.loads(args.battery.read_text(encoding="utf-8"))
    refreshed = json.loads(args.refreshed.read_text(encoding="utf-8"))
    for name, document in (("battery", direct), ("refreshed", refreshed)):
        if (document.get("baselineControl") or {}).get("result") != "VALID":
            print(f"REFUSED: the {name} null-mutation control is not VALID")
            return 3

    attacks: list[dict[str, Any]] = list(direct["attacks"]) + list(refreshed["attacks"])
    escaped = [item for item in attacks if item["result"] == "ESCAPED"]
    mandatory = [item for item in attacks if item["mandatory"]]
    control = dict(direct["baselineControl"])
    control["detail"] = (
        control["detail"]
        + " A second null-mutation control, with the declared inventory hashes re-derived by the "
          "project's own helper, was also accepted before the three attributable variants ran: "
        + refreshed["baselineControl"]["detail"])

    report = {
        "schemaVersion": "1.1.0",
        "checkpoint": CHECKPOINT.name,
        "generatedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "targetFingerprint": scope_fingerprint(ROOT),
        "source": SOURCE,
        "baselineControl": control,
        "attacks": attacks,
        "total": len(attacks),
        "defended": len(attacks) - len(escaped),
        "escaped": len(escaped),
        "mandatoryTotal": len(mandatory),
        "mandatoryDefended": len([i for i in mandatory if i["result"] == "DEFENDED"]),
        "result": "RED_TEAM_FAIL" if escaped else "RED_TEAM_PASS",
    }

    schema = json.loads(
        (ROOT / ".iacode" / "schemas" / "red-team-report.schema.json").read_text(encoding="utf-8"))
    from ledger_common import validate_schema

    errors = validate_schema(report, schema)
    if errors:
        print("RED_TEAM_REPORT_INVALID")
        for error in errors:
            print(f"- {error}")
        return 2

    (CHECKPOINT / "M0-INTERNAL-RED-TEAM.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    (CHECKPOINT / "RED-TEAM-REPORT.md").write_text(render(report), encoding="utf-8", newline="\n")
    print(f"RED_TEAM={report['result']} defended={report['defended']}/{report['total']} "
          f"mandatory={report['mandatoryDefended']}/{report['mandatoryTotal']}")
    return 0 if not escaped else 1


def render(report: dict[str, Any]) -> str:
    lines = [
        "# Red Team Report — the adversarial battery of this audit",
        "",
        f"Result: `{report['result']}`  ",
        f"Defended: {report['defended']} of {report['total']}  ",
        f"Checkpoint: `{report['checkpoint']}`  ",
        f"Target fingerprint: `{report['targetFingerprint']}`",
        "",
        "## What this battery is",
        "",
        report["source"],
        "",
        "## Null-mutation control",
        "",
        f"Result: `{report['baselineControl']['result']}`",
        "",
        report["baselineControl"]["detail"],
        "",
        "A battery without this control proves nothing: the second `M0` audit's first harness "
        "reported every attack as defended while the refusals came from leftover state rather than "
        "from the mutation under test.",
        "",
        "## Scenarios",
        "",
        "| Attack | Category | Target | Mutation | Expected | Result |",
        "|---|---|---|---|---|---|",
    ]
    for attack in report["attacks"]:
        category, _, target = str(attack["target"]).partition(": ")
        lines.append(
            f"| `{attack['attackId']}` | {'mandatory' if attack['mandatory'] else 'additional'} | "
            f"{category}: {target} | {str(attack['mutation']).replace('|', '/')} | "
            f"{attack['expectedDefense']} | `{attack['result']}` |")
    lines += ["", "## Observed refusals", ""]
    for attack in report["attacks"]:
        lines.append(f"- `{attack['attackId']}`: {str(attack['observed']).replace('|', '/')}")
    lines += [
        "",
        "## What this battery is not",
        "",
        "It is not the independent Red Team of a later audit, and it is not `m0_red_team.py`. It is "
        "this audit's own adversarial work against the sealed subject and against the state the "
        "`CP11-F-001` repair opened. Mutating a sealed checkout necessarily makes the worktree "
        "dirty and the validator says so, so a scenario is judged by whether the refusal it was "
        "aimed at appears, never by a non-zero exit code alone.",
        "",
        "Three scenarios were first refused by the file-inventory binding before reaching their "
        "target. They were re-run as variants that re-derive the declared hashes with the "
        "project's own helper, and each was then refused by the control it was aimed at. Both "
        "forms are kept, because removing the weaker one would hide why the stronger one exists.",
        "",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
