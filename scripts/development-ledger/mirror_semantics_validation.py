#!/usr/bin/env python3
"""Execute the mirror audit over every applicability state it can be in, and report what it said.

Finding ``CP11-F-001`` was a quality control that could not tell two states apart:

``EMPTY APPLICABLE SET``
    the canonical sources name nothing of this kind for this delivery to judge. That is a
    legitimate state -- a delivery that corrects no audit, the first delivery of any later Gate --
    and it is ``NOT_APPLICABLE`` with a reason.

``MISSING REQUIRED SET``
    the canonical sources do name something and the delivery does not carry it. That is a failure
    and it is ``FAIL``.

The shipped tooling collapsed the first into the second, so every delivery that had nothing to
correct was refused for having nothing to correct. This validation proves the repair by executing
``m0_mirror_audit.py`` itself over six prepared states, including the three negatives that would
turn the repair into a way of passing without auditing anything. Nothing here writes the artifact
the tool would have produced: writing it by hand is how the defect survived a passing rehearsal.

    python scripts/development-ledger/mirror_semantics_validation.py --write
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path
from typing import Any

from ledger_common import LedgerError, find_root, resolve_latest, utc_now, write_json
from promotion_fixture import run_mirror_scenario

CLOSED_THREE = {"FIX-F-001": "CLOSED", "FIX-F-002": "CLOSED", "FIX-F-003": "CLOSED"}
ONE_OPEN_OF_THREE = {"FIX-F-001": "CLOSED", "FIX-F-002": "CLOSED", "FIX-F-003": "OPEN"}

SCENARIOS: tuple[dict[str, Any], ...] = (
    {
        "id": "MSV-001",
        "name": "no-applicable-audit",
        "title": "a delivery that corrects no audit",
        "arguments": {"findings": None},
        "expect": {
            "overall": "PASS",
            "MIR-002": "NOT_APPLICABLE",
            "MIR-003": "NOT_APPLICABLE",
            "sealed": True,
        },
        "why": "No registered audit names this checkpoint as its corrective delivery, so the "
               "applicable set is empty by derivation. This is the state the finding made "
               "unreachable, and the delivery must reach a handoff-ready status in it.",
    },
    {
        "id": "MSV-002",
        "name": "closed-findings",
        "title": "a delivery whose applicable findings and attacks are all satisfied",
        "arguments": {"findings": CLOSED_THREE,
                      "attacks": [("FIX-01", True), ("FIX-02", True), ("FIX-03", False)]},
        "expect": {"overall": "PASS", "MIR-002": "PASS", "MIR-003": "PASS", "sealed": True},
        "why": "Three findings are applicable and all three are CLOSED; two mandatory attacks are "
               "applicable and both were defended. The repair must not have replaced the check "
               "with an unconditional pass.",
    },
    {
        "id": "MSV-003",
        "name": "open-finding",
        "title": "a delivery with an applicable finding still open",
        "arguments": {"findings": ONE_OPEN_OF_THREE, "attacks": [("FIX-01", True)]},
        "expect": {"overall": "FAIL", "MIR-002": "FAIL", "MIR-003": "PASS", "sealed": False},
        "why": "A non-empty applicable set with an unsatisfied item is a failure, and the delivery "
               "cannot be sealed. This is what stops the repair from becoming a vacuous pass.",
    },
    {
        "id": "MSV-004",
        "name": "missing-closure-record",
        "title": "a delivery that omits the closure record the registry requires",
        "arguments": {"findings": {"FIX-F-001": "CLOSED"}, "attacks": [("FIX-01", True)],
                      "omit_closure": True},
        "expect": {"overall": "FAIL", "MIR-002": "FAIL", "MIR-003": "PASS", "sealed": False},
        "why": "The canonical sources name a finding and the artifact that would close it is "
               "absent. A missing required set is never an empty applicable set.",
    },
    {
        "id": "MSV-005",
        "name": "forged-empty-applicable-set",
        "title": "a delivery declaring that it has nothing to close",
        "arguments": {"findings": {"FIX-F-001": "OPEN"}, "attacks": [("FIX-01", True)],
                      "forge_empty_expected": True},
        "expect": {"overall": "FAIL", "MIR-002": "FAIL", "MIR-003": "PASS", "sealed": False},
        "why": "The checkpoint declares an empty expected set while the registry and the sealed "
               "report name one open finding. The applicable set is derived from the canonical "
               "sources and no artifact inside the delivery can shrink it, so the declaration "
               "changes nothing and the open finding still fails.",
    },
    {
        "id": "MSV-006",
        "name": "undefended-mandatory-attack",
        "title": "a delivery that did not execute an applicable mandatory attack",
        "arguments": {"findings": {"FIX-F-001": "CLOSED"},
                      "attacks": [("FIX-01", True), ("FIX-02", True)],
                      "defended": {"FIX-01"}},
        "expect": {"overall": "FAIL", "MIR-002": "PASS", "MIR-003": "FAIL", "sealed": False},
        "why": "A mandatory attack the sealed report hands the delivery was not executed. The "
               "battery dimension is applicable and unsatisfied, which is a failure.",
    },
)


def _check(scenario: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
    expect = scenario["expect"]
    mirror = result["mirror"]
    checks = {item["id"]: item for item in mirror["checks"]}
    observations: list[str] = [
        f"overall={mirror['result']}",
        f"MIR-002={checks['MIR-002']['result']}",
        f"MIR-003={checks['MIR-003']['result']}",
        f"sealed={result['sealed']}",
    ]
    failures: list[str] = []
    if mirror["result"] != expect["overall"]:
        failures.append(f"overall {mirror['result']} != {expect['overall']}")
    for identifier in ("MIR-002", "MIR-003"):
        if checks[identifier]["result"] != expect[identifier]:
            failures.append(
                f"{identifier} {checks[identifier]['result']} != {expect[identifier]}")
    if result["sealed"] != expect["sealed"]:
        failures.append(f"sealed {result['sealed']} != {expect['sealed']}")
    # An inapplicable dimension is only acceptable when it justifies itself.
    for identifier in ("MIR-002", "MIR-003"):
        check = checks[identifier]
        if check["result"] != "NOT_APPLICABLE":
            continue
        if not (check.get("reason") or "").strip():
            failures.append(f"{identifier} is NOT_APPLICABLE without a reason")
        if not (check.get("derivationSource") or "").strip():
            failures.append(f"{identifier} is NOT_APPLICABLE without a derivation source")
        if check.get("expectedCount") != 0:
            failures.append(
                f"{identifier} is NOT_APPLICABLE with expectedCount={check.get('expectedCount')!r}")
    if mirror["producedBy"] != "execution" or mirror["exitCode"] is None:
        failures.append("the mirror artifact was not produced by executing the tool")
    return {
        "id": scenario["id"],
        "scenario": scenario["name"],
        "title": scenario["title"],
        "why": scenario["why"],
        "expected": expect,
        "observed": "; ".join(observations),
        "mirrorCommand": mirror["command"],
        "mirrorExitCode": mirror["exitCode"],
        "findingsCheck": checks["MIR-002"],
        "attacksCheck": checks["MIR-003"],
        "failures": failures,
        "result": "PASS" if not failures else "FAIL",
    }


def run(workdir: Path) -> dict[str, Any]:
    checks = []
    for scenario in SCENARIOS:
        result = run_mirror_scenario(workdir, name=scenario["name"], **scenario["arguments"])
        checks.append(_check(scenario, result))
    failed = [item for item in checks if item["result"] != "PASS"]
    return {
        "schemaVersion": "1.0.0",
        "generatedAt": utc_now(),
        "validation": "internal mirror audit applicability semantics",
        "finding": "CP11-F-001",
        "statesCovered": {
            "emptyApplicableSet": "MSV-001",
            "satisfiedApplicableSet": "MSV-002",
            "unsatisfiedApplicableSet": "MSV-003",
            "missingRequiredSet": "MSV-004",
            "forgedEmptyApplicableSet": "MSV-005",
            "unexecutedApplicableBattery": "MSV-006",
        },
        "checks": checks,
        "total": len(checks),
        "passed": len(checks) - len(failed),
        "failed": len(failed),
        "result": "PASS" if not failed else "FAIL",
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Mirror Semantics Validation",
        "",
        f"Result: `{report['result']}`",
        "",
        f"- Validation: {report['validation']}",
        f"- Closes: `{report['finding']}`",
        f"- Generated: `{report['generatedAt']}`",
        "",
        "An empty applicable set and a missing required set are different states. Only the first is",
        "benign, and it is recorded as `NOT_APPLICABLE` with a reason, an expected count of zero and",
        "the canonical source the emptiness was derived from. Every row below was produced by",
        "executing `scripts/development-ledger/m0_mirror_audit.py` in a disposable repository;",
        "no row asserts a result and none writes the artifact the tool would have produced.",
        "",
        "| Check | State under test | Expected | Observed | Result |",
        "|---|---|---|---|---|",
    ]
    for check in report["checks"]:
        expected = ", ".join(f"{key}={value}" for key, value in check["expected"].items())
        lines.append("| `%s` | %s | %s | %s | `%s` |" % (
            check["id"], check["title"].replace("|", "/"), expected,
            check["observed"].replace("|", "/"), check["result"]))
    lines += ["", "## Why each state is the outcome it is", ""]
    for check in report["checks"]:
        lines += [f"### `{check['id']}` — {check['title']}", "", check["why"], ""]
        lines += [
            f"- `MIR-002`: `{check['findingsCheck']['result']}` — "
            f"{check['findingsCheck']['observed']}",
            f"- `MIR-003`: `{check['attacksCheck']['result']}` — "
            f"{check['attacksCheck']['observed']}",
            f"- Executed: `{check['mirrorCommand']}`, exit `{check['mirrorExitCode']}`",
            "",
        ]
        for identifier in ("findingsCheck", "attacksCheck"):
            item = check[identifier]
            if item["result"] == "NOT_APPLICABLE":
                lines += [
                    f"- `{item['id']}` justification: {item['reason']}",
                    f"- `{item['id']}` expected items: `{item['expectedCount']}`, derived from "
                    f"{item['derivationSource']}",
                    "",
                ]
        if check["failures"]:
            lines += ["- Divergence: " + "; ".join(check["failures"]), ""]
    lines += [f"Passed: `{report['passed']}` of `{report['total']}` states."]
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path)
    parser.add_argument("--checkpoint", type=Path)
    parser.add_argument("--write", action="store_true",
                        help="write MIRROR-SEMANTICS-VALIDATION.json and .md")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    root = find_root(args.root) if args.root else find_root()
    checkpoint = args.checkpoint or resolve_latest(root)
    if not checkpoint.is_absolute():
        checkpoint = root / checkpoint

    with tempfile.TemporaryDirectory(prefix="iacode-mirror-semantics-") as workdir:
        report = run(Path(workdir))

    if args.write:
        write_json(checkpoint / "MIRROR-SEMANTICS-VALIDATION.json", report)
        (checkpoint / "MIRROR-SEMANTICS-VALIDATION.md").write_text(
            render_markdown(report), encoding="utf-8", newline="\n")
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"MIRROR_SEMANTICS={report['result']} states={report['passed']}/{report['total']}")
        for check in report["checks"]:
            print(f"- {check['result']} {check['id']} {check['scenario']}: {check['observed']}")
    return 0 if report["result"] == "PASS" else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except LedgerError as exc:
        print(f"LEDGER_ERROR: {exc}")
        sys.exit(2)
