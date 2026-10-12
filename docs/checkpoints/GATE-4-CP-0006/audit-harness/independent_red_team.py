#!/usr/bin/env python3
"""Consolidate the fresh Gate 4 independent Red Team from executed evidence."""

from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
SUBJECT = ROOT / "docs" / "checkpoints" / "GATE-4-CP-0005"
sys.path.insert(0, str(ROOT / "scripts" / "development-ledger"))

from ledger_common import use_utf8_stdout  # noqa: E402


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
        "The complete A–T battery was executed by this fresh auditing session over valid controls. "
        "A–J and Q–S ran in the rebuilt evaluator image; K–O attacked the real bundle validator; "
        "P is bound to the single integral verifier; T is bound to detached deterministic rebuilds. "
        "Synthetic credential material was assembled only in memory and is absent from this report.",
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


def run_image_battery(image: str) -> dict[str, Any]:
    source = ROOT / "scripts" / "development-ledger" / "gate4_red_team.py"
    completed = subprocess.run(
        [
            "docker", "run", "--rm", "--entrypoint", "",
            "--volume", f"{source.as_posix()}:/app/gate4-red-team.py:ro",
            image, "python", "/app/gate4-red-team.py", "--in-image",
        ],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
        timeout=1800,
    )
    if completed.returncode != 0:
        raise RuntimeError("independent evaluator Red Team failed: " + completed.stdout[-1600:])
    for line in reversed(completed.stdout.splitlines()):
        if line.strip().startswith("{"):
            return json.loads(line)
    raise RuntimeError("independent evaluator Red Team returned no report")


def run_bundle_mutations() -> list[dict[str, Any]]:
    source = ROOT / "scripts" / "development-ledger" / "gate4_red_team.py"
    specification = importlib.util.spec_from_file_location("gate4_red_team_audit_source", source)
    if specification is None or specification.loader is None:
        raise RuntimeError("cannot load canonical Gate 4 Red Team")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    attacks = module._host_attacks(ROOT, SUBJECT)  # noqa: SLF001 - intentional audit reuse
    selected = [item for item in attacks if str(item.get("attackId")) in "KLMNO"]
    if [item.get("attackId") for item in selected] != list("KLMNO"):
        raise RuntimeError("canonical host bundle mutation set did not yield K-O")
    for item in selected:
        item["origin"] = "fresh execution by the independent Gate 4 audit"
    return selected


def main() -> int:
    use_utf8_stdout()
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--markdown", type=Path, required=True)
    parser.add_argument("--image", required=True)
    arguments = parser.parse_args()

    canonical = run_image_battery(arguments.image)
    probe = load("G4-X7-INDEPENDENT-PROBE.json")
    bundle = load("SUBJECT-BUNDLE-AUDIT.json")
    verification = load("VERIFICATION-REPORT.json")
    stages = {str(item.get("name")): item for item in verification.get("stages") or []}

    attacks: list[dict[str, Any]] = []
    for original in canonical.get("attacks") or []:
        attack = dict(original)
        attack["origin"] = "fresh execution by the independent Gate 4 audit"
        attack["evidence"] = [
            "file:scripts/development-ledger/gate4_red_team.py",
            "checkpoint:G4-X7-INDEPENDENT-PROBE.json",
        ]
        identifier = str(attack.get("attackId"))
        if identifier == "Q":
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

    attacks.extend(run_bundle_mutations())
    names = [
        "quality-recovery", "quality-cancellation", "quality-timeout",
        "sandbox-tool-result-origin",
    ]
    lifecycle = {name: (stages.get(name) or {}).get("result") for name in names}
    attacks.append({
        "attackId": "P",
        "target": "live adverse lifecycle",
        "mutation": "execute restart, cancellation, timeout and forged-origin scenarios",
        "expectedDefense": "every fail-closed invariant survives in the current verifier run",
        "observed": "; ".join(f"{key}={value}" for key, value in lifecycle.items()),
        "result": "DEFENDED" if all(value == "PASS" for value in lifecycle.values()) else "ESCAPED",
        "mandatory": True,
        "evidence": ["checkpoint:VERIFICATION-REPORT.json"],
        "origin": "single integral published verifier run",
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

    order = {identifier: index for index, identifier in enumerate("ABCDEFGHIJKLMNOPQRST")}
    attacks.sort(key=lambda item: order[str(item["attackId"])])
    identifiers = [str(item.get("attackId")) for item in attacks]
    if identifiers != list("ABCDEFGHIJKLMNOPQRST"):
        raise RuntimeError(f"independent Red Team denominator changed: {identifiers}")

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
        "subjectCheckpoint": "GATE-4-CP-0005",
        "subjectCommit": "c631270e49c095a9777825c0bc18818694c07ffb",
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
        "mandatoryTotal": 20,
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
