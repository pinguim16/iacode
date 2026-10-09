#!/usr/bin/env python3
"""Audit M1 runbooks and Engineering Memory against this run's executable evidence."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "development-ledger"))

from ledger_common import utc_now, write_json  # noqa: E402
from lessons import guardrail_effectiveness  # noqa: E402


def main() -> int:
    verification = json.loads((CHECKPOINT / "VERIFICATION-REPORT.json").read_text(encoding="utf-8"))
    stages = {item["name"]: item.get("result") for item in verification.get("stages") or []}
    checks: list[dict[str, object]] = []

    def record(name: str, ok: bool, observed: str, evidence: list[str]) -> None:
        checks.append({"check": name, "ok": ok, "observed": observed, "evidence": evidence})

    documents = {
        "Foundation": ROOT / "docs" / "runbooks" / "FOUNDATION.md",
        "Model Gateway": ROOT / "docs" / "runbooks" / "MODEL-GATEWAY.md",
        "Agent Runtime": ROOT / "docs" / "runbooks" / "AGENT-RUNTIME.md",
        "Sandbox": ROOT / "docs" / "runbooks" / "SANDBOX.md",
        "backup and restore": ROOT / "docs" / "runbooks" / "BACKUP-RESTORE.md",
    }
    missing = [name for name, path in documents.items() if not path.is_file() or not path.stat().st_size]
    record("M1 runbooks exist", not missing,
           f"five non-empty runbooks; missing={missing or 'none'}",
           [f"file:{path.relative_to(ROOT).as_posix()}" for path in documents.values()])

    start = (ROOT / "START-HERE.md").read_text(encoding="utf-8")
    development = (ROOT / "docs" / "DEVELOPMENT.md").read_text(encoding="utf-8")
    record("entry points name the canonical workflow",
           "docs/DEVELOPMENT-CONTRACT.md" in start
           and "scripts/iacode/verify.py" in development
           and "scripts/iacode/smoke.py" in development,
           "START-HERE routes to the contract; DEVELOPMENT names smoke and verification",
           ["file:START-HERE.md", "file:docs/DEVELOPMENT.md",
            "file:docs/DEVELOPMENT-CONTRACT.md"])

    reproduced = (verification.get("result") == "PASS" and not verification.get("fast")
                  and all(stages.get(name) == "PASS" for name in (
                      "stack", "integration", "smoke", "gateway-smoke", "agent-runtime-smoke",
                      "sandbox-integration", "backup", "restart", "dependency-failure",
                      "fresh-install")))
    record("runbook behavior reproduced", reproduced,
           f"full verification={verification.get('result')}; selected stages="
           + ", ".join(f"{name}={stages.get(name)}" for name in (
               "stack", "integration", "smoke", "gateway-smoke", "agent-runtime-smoke",
               "sandbox-integration", "backup", "restart", "dependency-failure", "fresh-install")),
           ["checkpoint:VERIFICATION-REPORT.json", "checkpoint:CLEAN-CLONE-REPORT.json"])

    lesson_run = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "development-ledger" / "validate_lessons.py")],
        cwd=ROOT, text=True, encoding="utf-8", errors="replace", capture_output=True, check=False)
    lesson_tail = " ".join((lesson_run.stdout + lesson_run.stderr).strip().splitlines()[-2:])[:400]
    record("Engineering Memory validates", lesson_run.returncode == 0,
           f"exit={lesson_run.returncode}; {lesson_tail}",
           ["file:.iacode/memory/lessons.jsonl", "file:.iacode/memory/guardrails/registry.json"])

    preflight = json.loads((CHECKPOINT / "LESSON-PREFLIGHT.json").read_text(encoding="utf-8"))
    considered = int(preflight.get("lessonsConsidered") or 0)
    applicable = int(preflight.get("lessonsApplicable") or 0)
    derived = len(preflight.get("derivedRequirements") or [])
    record("lesson preflight is complete", considered > 0 and applicable == derived,
           f"considered={considered} applicable={applicable} derived={derived}",
           ["checkpoint:LESSON-PREFLIGHT.json"])

    measured = guardrail_effectiveness(ROOT)
    effective = (measured["guardrailFailures"] == 0
                 and measured["guardrailsEffective"] == measured["guardrailsTotal"])
    record("guardrails are effective", effective,
           ", ".join(f"{key}={measured[key]}" for key in (
               "guardrailsTotal", "guardrailsResolved", "guardrailsTested",
               "guardrailsEffective", "guardrailFailures")),
           ["file:.iacode/memory/guardrails/registry.json",
            "file:.iacode/memory/lessons.jsonl"])

    failed = [item for item in checks if not item["ok"]]
    report = {
        "schemaVersion": "1.0.0",
        "artifact": "DOCUMENTATION-AND-MEMORY-REVIEW",
        "checkpoint": CHECKPOINT.name,
        "generatedAt": utc_now(),
        "checks": checks,
        "guardrailEffectiveness": measured,
        "passed": len(checks) - len(failed),
        "total": len(checks),
        "result": "PASS" if not failed else "FAIL",
    }
    write_json(CHECKPOINT / "DOCUMENTATION-AND-MEMORY-REVIEW.json", report)
    print(f"DOCUMENTATION_MEMORY={report['result']} {report['passed']}/{report['total']}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
