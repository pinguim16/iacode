#!/usr/bin/env python3
"""Re-derive the sealed subject's requirements, tests, lessons and guardrails in transport."""

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
SUBJECT = "GATE-4-CP-0005"
COMMIT = "c631270e49c095a9777825c0bc18818694c07ffb"
TAG = f"iacode-checkpoints/{SUBJECT}"
sys.path.insert(0, str(ROOT / "scripts" / "development-ledger"))

from ledger_common import use_utf8_stdout  # noqa: E402


def run(arguments: list[str], cwd: Path) -> dict[str, Any]:
    completed = subprocess.run(
        arguments,
        cwd=cwd,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    return {
        "command": arguments,
        "exitCode": completed.returncode,
        "tail": "\n".join(completed.stdout.splitlines()[-30:]),
    }


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    use_utf8_stdout()
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path, required=True)
    arguments = parser.parse_args()

    with tempfile.TemporaryDirectory(prefix="iacode-g4-subject-counts-") as temporary:
        clone = Path(temporary) / "repository"
        steps = [run(["git", "clone", "--quiet", "--no-local", "https://github.com/pinguim16/iacode.git", str(clone)], Path(temporary))]
        if steps[-1]["exitCode"] == 0:
            steps.append(run(["git", "checkout", "--quiet", "--detach", TAG], clone))
        observed = run(["git", "rev-parse", "HEAD"], clone) if clone.is_dir() else {"exitCode": 1, "tail": "clone unavailable", "command": []}
        steps.append(observed)
        tools = [
            [sys.executable, "scripts/development-ledger/validate_checkpoint.py"],
            [sys.executable, "scripts/development-ledger/derive_requirements.py", "--checkpoint", f"docs/checkpoints/{SUBJECT}", "--gate", "GATE-4"],
            [sys.executable, "scripts/development-ledger/check_completeness.py", "--checkpoint", f"docs/checkpoints/{SUBJECT}", "--auditor", "fresh-session independent Gate 4 audit"],
            [sys.executable, "scripts/development-ledger/derive_counts.py", "--checkpoint", f"docs/checkpoints/{SUBJECT}"],
            [sys.executable, "scripts/development-ledger/validate_lessons.py"],
            [sys.executable, "scripts/development-ledger/verify_integrity.py"],
        ]
        for tool in tools:
            steps.append(run(tool, clone))

        subject = clone / "docs" / "checkpoints" / SUBJECT
        counts = load(subject / "COUNTS.json") if subject.is_dir() else {}
        completeness = load(subject / "COMPLETENESS-REPORT.json") if subject.is_dir() else {}
        state = load(subject / "STATE.json") if subject.is_dir() else {}
        red_team = load(subject / "M2-INTERNAL-RED-TEAM.json") if subject.is_dir() else {}
        count_values = counts.get("counts") or {}
        requirements = count_values.get("REQUIREMENTS") or {}
        tests = count_values.get("TESTS") or {}
        guardrails = count_values.get("GUARDRAILS") or {}
        attacks = count_values.get("ATTACKS") or {}
        lessons = count_values.get("LESSONS") or {}
        passed = (
            all(step["exitCode"] == 0 for step in steps)
            and observed.get("tail", "").strip() == COMMIT
            and requirements.get("numerator") == requirements.get("denominator") == 221
            and tests.get("numerator") == tests.get("denominator")
            and int(tests.get("denominator", 0)) >= 1701
            and guardrails.get("numerator") == guardrails.get("denominator")
            and int(guardrails.get("denominator", 0)) >= 97
            and attacks.get("numerator") == attacks.get("denominator") == 20
            and completeness.get("result") == "PASS"
            and completeness.get("totalRequirements") == 221
            and completeness.get("complete") == 221
            and red_team.get("result") == "RED_TEAM_PASS"
            and state.get("guardrailEffectiveness", {}).get("guardrailFailures") == 0
        )
        report = {
            "schemaVersion": "1.0.0",
            "artifact": "GATE-4-SUBJECT-COUNTS-AUDIT",
            "checkpoint": CHECKPOINT.name,
            "subjectCheckpoint": SUBJECT,
            "subjectCommit": COMMIT,
            "generatedAt": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            "steps": steps,
            "counts": count_values,
            "completeness": {
                "result": completeness.get("result"),
                "total": completeness.get("totalRequirements"),
                "complete": completeness.get("complete"),
                "coveragePercent": completeness.get("coveragePercent"),
                "evidenceCoveragePercent": completeness.get("evidenceCoveragePercent"),
            },
            "guardrailFailures": state.get("guardrailEffectiveness", {}).get("guardrailFailures"),
            "redTeamResult": red_team.get("result"),
            "lessons": lessons,
            "result": "PASS" if passed else "FAIL",
        }
        arguments.report.resolve().write_text(
            json.dumps(report, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
            newline="\n",
        )
    print(
        f"SUBJECT_COUNTS_AUDIT={report['result']} "
        f"requirements={requirements.get('numerator')}/{requirements.get('denominator')} "
        f"tests={tests.get('numerator')}/{tests.get('denominator')} "
        f"guardrails={guardrails.get('numerator')}/{guardrails.get('denominator')} "
        f"attacks={attacks.get('numerator')}/{attacks.get('denominator')}"
    )
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
