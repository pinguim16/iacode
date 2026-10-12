#!/usr/bin/env python3
"""Re-derive the CP0007 denominators from published transport."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
SUBJECT = "GATE-4-CP-0007"
COMMIT = "e21d30fde473f302d0f8f60b59acf008fa52e250"
TAG = f"iacode-checkpoints/{SUBJECT}"
sys.path.insert(0, str(ROOT / "scripts" / "development-ledger"))

from ledger_common import use_utf8_stdout  # noqa: E402


def run(arguments: list[str], cwd: Path) -> dict[str, Any]:
    completed = subprocess.run(
        arguments, cwd=cwd, text=True, encoding="utf-8", errors="replace",
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False,
    )
    return {
        "command": arguments,
        "exitCode": completed.returncode,
        "tail": "\n".join(completed.stdout.splitlines()[-40:]),
    }


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    use_utf8_stdout()
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path, required=True)
    arguments = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="iacode-g4-cp0008-counts-") as temporary:
        parent = Path(temporary)
        clone = parent / "repository"
        steps = [run([
            "git", "clone", "--quiet", "--no-local",
            "https://github.com/pinguim16/iacode.git", str(clone),
        ], parent)]
        if steps[-1]["exitCode"] == 0:
            steps.append(run(["git", "checkout", "--quiet", "--detach", TAG], clone))
        observed = run(["git", "rev-parse", "HEAD"], clone)
        steps.append(observed)
        for tool in (
            [sys.executable, "scripts/development-ledger/validate_checkpoint.py"],
            [sys.executable, "scripts/development-ledger/derive_requirements.py", "--checkpoint", f"docs/checkpoints/{SUBJECT}", "--gate", "GATE-4"],
            [sys.executable, "scripts/development-ledger/check_completeness.py", "--checkpoint", f"docs/checkpoints/{SUBJECT}", "--auditor", "fresh-session independent Gate 4 audit"],
            [sys.executable, "scripts/development-ledger/derive_counts.py", "--checkpoint", f"docs/checkpoints/{SUBJECT}"],
            [sys.executable, "scripts/development-ledger/validate_lessons.py"],
            [sys.executable, "scripts/development-ledger/verify_integrity.py"],
        ):
            steps.append(run(tool, clone))

        subject = clone / "docs" / "checkpoints" / SUBJECT
        counts = load(subject / "COUNTS.json")
        completeness = load(subject / "COMPLETENESS-REPORT.json")
        state = load(subject / "STATE.json")
        red_team = load(subject / "M2-INTERNAL-RED-TEAM.json")
        closure_paths = [
            clone / "docs" / "checkpoints" / "GATE-4-CP-0003" / "G4-CP-0002-FINDINGS-CLOSURE.json",
            clone / "docs" / "checkpoints" / "GATE-4-CP-0005" / "G4-CP-0004-FINDINGS-CLOSURE.json",
            subject / "G4-CP-0006-PUBLICATION-FINDINGS-CLOSURE.json",
        ]
        closures = [load(path) for path in closure_paths]
        values = counts["counts"]
        requirements = values["REQUIREMENTS"]
        tests = values["TESTS"]
        guardrails = values["GUARDRAILS"]
        attacks = values["ATTACKS"]
        green = state["greenKeeper"]
        finding_ids = sorted(
            str(item.get("findingId"))
            for closure in closures
            for item in closure.get("findings", [])
            if item.get("status") == "CLOSED"
        )
        checks = {
            "publishedCloneCommands": all(step["exitCode"] == 0 for step in steps),
            "subjectIdentity": observed["tail"].strip() == COMMIT,
            "requirements": requirements.get("numerator") == requirements.get("denominator") == 201,
            "tests": tests.get("numerator") == tests.get("denominator") == 1709,
            "guardrails": guardrails.get("numerator") == guardrails.get("denominator") == 97,
            "attacks": attacks.get("numerator") == attacks.get("denominator") == 20,
            "completeness": (
                completeness.get("result") == "PASS"
                and completeness.get("totalRequirements") == 201
                and completeness.get("complete") == 201
                and completeness.get("coveragePercent") == 100.0
                and completeness.get("evidenceCoveragePercent") == 100.0
            ),
            "greenKeeper": (
                green.get("status") == "PASS"
                and len(green.get("requiredGates") or []) == 13
                and green.get("remainingFailures") == 0
                and green.get("unresolvedReworkItems") == 0
            ),
            "internalRedTeam": red_team.get("result") == "RED_TEAM_PASS",
            "findingClosure": (
                all(closure.get("result") in {"PASS", "CLOSED"} for closure in closures)
                and finding_ids == ["G4-F-001", "G4-F-002", "G4-F-003"]
            ),
            "guardrailFailures": state.get("guardrailEffectiveness", {}).get("guardrailFailures") == 0,
        }
        report = {
            "schemaVersion": "1.0.0",
            "artifact": "GATE-4-SUBJECT-COUNTS-AUDIT",
            "checkpoint": CHECKPOINT.name,
            "subjectCheckpoint": SUBJECT,
            "subjectCommit": COMMIT,
            "generatedAt": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            "steps": steps,
            "counts": values,
            "greenKeeper": {
                "status": green.get("status"),
                "requiredGates": green.get("requiredGates"),
                "requiredGateCount": len(green.get("requiredGates") or []),
                "remainingFailures": green.get("remainingFailures"),
            },
            "completeness": {
                "result": completeness.get("result"),
                "total": completeness.get("totalRequirements"),
                "complete": completeness.get("complete"),
                "coveragePercent": completeness.get("coveragePercent"),
                "evidenceCoveragePercent": completeness.get("evidenceCoveragePercent"),
            },
            "closedFindings": finding_ids,
            "checks": checks,
            "result": "PASS" if all(checks.values()) else "FAIL",
        }
        arguments.report.resolve().write_text(
            json.dumps(report, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8", newline="\n",
        )
    print(
        f"SUBJECT_COUNTS_AUDIT={report['result']} "
        f"requirements={requirements['numerator']}/{requirements['denominator']} "
        f"tests={tests['numerator']}/{tests['denominator']} "
        f"guardrails={guardrails['numerator']}/{guardrails['denominator']} "
        f"green={len(green.get('requiredGates') or [])}/13 findings={','.join(finding_ids)}"
    )
    return 0 if report["result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
