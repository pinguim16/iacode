#!/usr/bin/env python3
"""Consolidate the fresh Gate 4 independent Red Team from executed evidence."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

CHECKPOINT = Path(__file__).resolve().parent.parent


def load(name: str) -> dict[str, Any]:
    return json.loads((CHECKPOINT / name).read_text(encoding="utf-8"))


def render(report: dict[str, Any]) -> str:
    lines = [
        "# Gate 4 independent Red Team",
        "",
        f"Result: `{report['result']}`",
        "",
        f"- Null control: `{report['baselineControl']['result']}`",
        f"- Defended: {report['defended']}/{report['total']}",
        f"- Escaped: {report['escaped']}",
        "",
        "The A–Q canonical battery was executed again by this auditing session after rebuilding "
        "the evaluator image. Attack Q is additionally proved by an audit-owned instrumented "
        "activity-to-store probe. Synthetic credential material was assembled only in memory and "
        "is absent from this report.",
        "",
        "| Attack | Target | Expected | Observed | Result |",
        "|---|---|---|---|---|",
    ]
    for attack in report["attacks"]:
        observed = str(attack["observed"]).replace("|", "\\|").replace("\n", " ")
        lines.append(
            f"| `{attack['attackId']}` | {attack['target']} | {attack['expectedDefense']} | "
            f"{observed} | `{attack['result']}` |"
        )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--markdown", type=Path, required=True)
    arguments = parser.parse_args()

    canonical = load("M2-INTERNAL-RED-TEAM.json")
    probe = load("G4-X7-INDEPENDENT-PROBE.json")
    bundle = load("SUBJECT-BUNDLE-AUDIT.json")
    verification = load("VERIFICATION-REPORT.json")
    stages = {str(item.get("name")): item for item in verification.get("stages") or []}

    attacks: list[dict[str, Any]] = []
    for original in canonical.get("attacks") or []:
        attack = dict(original)
        attack["origin"] = "fresh execution by the independent Gate 4 audit"
        attack["evidence"] = ["checkpoint:M2-INTERNAL-RED-TEAM.json"]
        identifier = str(attack.get("attackId"))
        if identifier == "P":
            names = [
                "quality-recovery", "quality-cancellation", "quality-timeout",
                "sandbox-tool-result-origin",
            ]
            observed = {name: (stages.get(name) or {}).get("result") for name in names}
            defended = all(value == "PASS" for value in observed.values())
            attack["observed"] = "; ".join(f"{key}={value}" for key, value in observed.items())
            attack["result"] = "DEFENDED" if defended else "ESCAPED"
            attack["evidence"] = ["checkpoint:VERIFICATION-REPORT.json"]
        elif identifier == "Q":
            marker = probe["canonicalMarker"]
            defended = probe.get("result") == "PASS"
            attack["observed"] = (
                f"scannerKinds={marker['scannerKinds']}; scan-before-store="
                f"{marker['scanPrecededDurableOperation']}; status={marker['resultStatus']}; "
                f"verdict={marker['verdict']}; objects={marker['objectCount']}; "
                f"records={marker['metadataCount']}; evidence={marker['evidenceCount']}; "
                f"logs-clean={not marker['capturedLogsContainMarker']}"
            )
            attack["result"] = "DEFENDED" if defended else "ESCAPED"
            attack["evidence"] = ["checkpoint:G4-X7-INDEPENDENT-PROBE.json"]
        attacks.append(attack)

    failure = probe["scannerFailure"]
    attacks.append({
        "attackId": "R",
        "target": "scanner availability",
        "mutation": "make the canonical evidence scanner throw before it can classify clean bytes",
        "expectedDefense": "fail closed before any lookup or write and derive FAIL",
        "observed": (
            f"scan-before-store={failure['scanPrecededDurableOperation']}; "
            f"status={failure['resultStatus']}; verdict={failure['verdict']}; "
            f"objects={failure['objectCount']}; records={failure['metadataCount']}"
        ),
        "result": "DEFENDED" if (
            failure["scanPrecededDurableOperation"]
            and failure["resultStatus"] == "ERROR"
            and failure["verdict"] == "FAIL"
            and failure["objectCount"] == 0
            and failure["metadataCount"] == 0
        ) else "ESCAPED",
        "mandatory": True,
        "evidence": ["checkpoint:G4-X7-INDEPENDENT-PROBE.json"],
        "origin": "audit-owned evaluator-image probe",
    })
    legacy = probe["legacyObject"]
    attacks.append({
        "attackId": "S",
        "target": "legacy persisted object",
        "mutation": "replace already persisted clean bytes with a canonical credential shape",
        "expectedDefense": "rescan after read, refuse resolution and derive FAIL",
        "observed": (
            f"resolved={legacy['resolutionAccepted']}; rescanned-after-read="
            f"{legacy['rescannedAfterRead']}; verdict={legacy['verdict']}"
        ),
        "result": "DEFENDED" if (
            legacy["resolutionAccepted"] is False
            and legacy["rescannedAfterRead"] is True
            and legacy["verdict"] == "FAIL"
        ) else "ESCAPED",
        "mandatory": True,
        "evidence": ["checkpoint:G4-X7-INDEPENDENT-PROBE.json"],
        "origin": "audit-owned evaluator-image probe",
    })
    bundle_checks = bundle.get("checks") or {}
    attacks.append({
        "attackId": "T",
        "target": "review bundle portability and determinism",
        "mutation": "rebuild twice from a detached transport clone and validate there",
        "expectedDefense": "byte-identical rebuilds and complete secret-clean portable validation",
        "observed": (
            f"deterministic={bundle_checks.get('deterministicRebuild')}; "
            f"portable={bundle_checks.get('rebuiltPortableValidation')}; "
            f"categories={bundle_checks.get('originalArchiveStructure')}"
        ),
        "result": "DEFENDED" if (
            bundle_checks.get("deterministicRebuild")
            and bundle_checks.get("rebuiltPortableValidation")
            and bundle_checks.get("originalArchiveStructure")
        ) else "ESCAPED",
        "mandatory": True,
        "evidence": ["checkpoint:SUBJECT-BUNDLE-AUDIT.json"],
        "origin": "audit-owned transport-clone bundle probe",
    })

    baseline_valid = (
        (canonical.get("baselineControl") or {}).get("result") == "VALID"
        and (probe.get("nullControl") or {}).get("status") == "VALID"
        and bundle_checks.get("originalPortableValidation") is True
    )
    escaped = [item for item in attacks if item.get("result") != "DEFENDED"]
    report = {
        "schemaVersion": "1.0.0",
        "artifact": "GATE-4-INDEPENDENT-RED-TEAM",
        "checkpoint": CHECKPOINT.name,
        "subjectCheckpoint": "GATE-4-CP-0003",
        "subjectCommit": "5d47200fde08c47b7a6410be2204b4c1b9fbadc1",
        "generatedAt": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "baselineControl": {
            "result": "VALID" if baseline_valid else "INVALID",
            "components": {
                "canonicalVerdictControl": (canonical.get("baselineControl") or {}).get("result"),
                "activityPersistenceControl": (probe.get("nullControl") or {}).get("status"),
                "subjectBundleControl": bundle_checks.get("originalPortableValidation"),
            },
        },
        "attacks": attacks,
        "mandatoryTotal": len(attacks),
        "mandatoryDefended": len(attacks) - len(escaped),
        "defended": len(attacks) - len(escaped),
        "escaped": len(escaped),
        "total": len(attacks),
        "result": "RED_TEAM_PASS" if baseline_valid and not escaped else "RED_TEAM_FAIL",
    }
    arguments.report.resolve().write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    arguments.markdown.resolve().write_text(
        render(report), encoding="utf-8", newline="\n"
    )
    print(
        f"INDEPENDENT_RED_TEAM={report['result']} "
        f"{report['defended']}/{report['total']} control={report['baselineControl']['result']}"
    )
    return 0 if report["result"] == "RED_TEAM_PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
