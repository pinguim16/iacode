#!/usr/bin/env python3
"""Audit Gate 4 documentation, lessons, guardrails and reproduced behavior."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "development-ledger"))

from ledger_common import utc_now  # noqa: E402
from lessons import guardrail_effectiveness, preflight_staleness  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--verification-report", type=Path, required=True)
    arguments = parser.parse_args()
    verification = json.loads(arguments.verification_report.read_text(encoding="utf-8"))
    stages = {item.get("name"): item for item in verification.get("stages") or []}
    checks: list[dict[str, object]] = []

    def record(name: str, ok: bool, observed: object, evidence: list[str]) -> None:
        checks.append({
            "check": name,
            "result": "PASS" if ok else "FAIL",
            "observed": observed,
            "evidence": evidence,
        })
        print(f"[{'PASS' if ok else 'FAIL'}] {name}")

    documents = {
        "entry": ROOT / "START-HERE.md",
        "architecture": ROOT / "docs" / "ARCHITECTURE.md",
        "development": ROOT / "docs" / "DEVELOPMENT.md",
        "versions": ROOT / "docs" / "VERSIONS.md",
        "model usage": ROOT / "docs" / "MODEL-USAGE-POLICY.md",
        "quality runbook": ROOT / "docs" / "runbooks" / "QUALITY-ENGINE.md",
        "Gate checklist": ROOT / "docs" / "GATE-4-CHECKLIST.md",
        "execution ADR": ROOT / "docs" / "adr" / "ADR-0029-quality-execution-boundary.md",
        "evidence ADR": ROOT / "docs" / "adr" / "ADR-0030-quality-evidence-and-verdict-immutability.md",
        "profiles ADR": ROOT / "docs" / "adr" / "ADR-0031-project-profiles-select-closed-quality-runners.md",
    }
    doc_observed = {}
    for name, path in documents.items():
        value = path.read_text(encoding="utf-8") if path.is_file() else ""
        doc_observed[name] = {
            "path": path.relative_to(ROOT).as_posix(),
            "nonEmpty": bool(value),
            "namesQuality": "quality" in value.lower(),
        }
    record(
        "Gate 4 entry, architecture, operational and decision documents exist",
        all(item["nonEmpty"] and item["namesQuality"] for item in doc_observed.values()),
        doc_observed,
        [f"file:{path.relative_to(ROOT).as_posix()}" for path in documents.values()],
    )

    required_stages = {
        "quality-integration",
        "quality-pass",
        "quality-fail",
        "quality-iacode",
        "quality-reproduction",
        "quality-recovery",
        "quality-cancellation",
        "quality-timeout",
        "quality-false-pass",
        "sandbox-coding",
        "sandbox-tool-result-origin",
        "backup",
        "dependency-scan",
        "restart",
        "dependency-failure",
        "fresh-install",
    }
    reproduced = {
        name: {
            "result": stages.get(name, {}).get("result"),
            "exitCode": stages.get(name, {}).get("exitCode"),
        }
        for name in sorted(required_stages)
    }
    record(
        "documented Quality Engine behavior was reproduced",
        verification.get("result") == "PASS"
        and len(stages) == 42
        and all(item["result"] == "PASS" and item["exitCode"] == 0
                for item in reproduced.values()),
        {"verification": verification.get("result"), "stages": reproduced},
        ["checkpoint:VERIFICATION-REPORT.json", "checkpoint:CLEAN-CLONE-REPORT.json"],
    )

    lesson_run = subprocess.run(
        [sys.executable, "scripts/development-ledger/validate_lessons.py"],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
        timeout=1200,
    )
    record(
        "Engineering Memory validates",
        lesson_run.returncode == 0,
        {
            "exitCode": lesson_run.returncode,
            "tail": (lesson_run.stdout + lesson_run.stderr).strip()[-800:],
        },
        ["file:.iacode/memory/lessons.jsonl", "file:.iacode/memory/guardrails/registry.json"],
    )

    preflight = json.loads((CHECKPOINT / "LESSON-PREFLIGHT.json").read_text(encoding="utf-8"))
    stale = preflight_staleness(ROOT, preflight, "GATE-4")
    considered = int(preflight.get("lessonsConsidered") or 0)
    applicable = int(preflight.get("lessonsApplicable") or 0)
    derived = len(preflight.get("derivedRequirements") or [])
    record(
        "independent-audit lesson preflight is fresh and complete",
        considered == 90 and applicable == derived == 90 and not stale,
        {
            "scope": preflight.get("scope"),
            "considered": considered,
            "applicable": applicable,
            "derived": derived,
            "staleness": stale,
        },
        ["checkpoint:LESSON-PREFLIGHT.json", "checkpoint:LESSON-PREFLIGHT.md"],
    )

    measured = guardrail_effectiveness(ROOT)
    record(
        "all registered guardrails are resolved, tested and effective",
        measured["guardrailFailures"] == 0
        and measured["guardrailsResolved"] == measured["guardrailsTotal"]
        and measured["guardrailsTested"] == measured["guardrailsTotal"]
        and measured["guardrailsEffective"] == measured["guardrailsTotal"],
        measured,
        ["file:.iacode/memory/guardrails/registry.json", "file:.iacode/memory/lessons.jsonl"],
    )

    retrospective = ROOT / ".iacode" / "memory" / "retrospectives" / "GATE-4-CP-0001.md"
    retrospective_text = retrospective.read_text(encoding="utf-8").lower() if retrospective.is_file() else ""
    record(
        "sealed Gate 4 retrospective exists and names evidence and limits",
        retrospective.is_file()
        and "evidence" in retrospective_text
        and "## what failed" in retrospective_text
        and "## what was learned" in retrospective_text,
        {"path": retrospective.relative_to(ROOT).as_posix(), "size": retrospective.stat().st_size
         if retrospective.is_file() else 0},
        ["file:.iacode/memory/retrospectives/GATE-4-CP-0001.md"],
    )

    failed = [item for item in checks if item["result"] != "PASS"]
    report = {
        "schemaVersion": "1.0.0",
        "artifact": "GATE-4-DOCUMENTATION-AND-MEMORY-REVIEW",
        "checkpoint": CHECKPOINT.name,
        "generatedAt": utc_now(),
        "checks": checks,
        "guardrailEffectiveness": measured,
        "passed": len(checks) - len(failed),
        "total": len(checks),
        "result": "PASS" if not failed else "FAIL",
    }
    output = arguments.report.resolve()
    output.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(f"DOCUMENTATION_MEMORY={report['result']} {report['passed']}/{report['total']}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
