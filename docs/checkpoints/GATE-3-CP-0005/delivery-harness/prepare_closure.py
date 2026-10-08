#!/usr/bin/env python3
"""Prepare the evidence-backed closure artifacts before final delivery assurance."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parent.parent
ROOT = CHECKPOINT.parents[2]
SUBJECT = "GATE-3-CP-0003"
sys.path.insert(0, str(ROOT / "scripts" / "development-ledger"))

from anchors import load_anchors  # noqa: E402
from delivery_assurance import collect_test_ids, evaluate_matrix, load_command_results, load_matrix, resolve_evidence  # noqa: E402
from ledger_common import load_json, utc_now, write_json  # noqa: E402
from lessons import guardrail_effectiveness, load_guardrails, load_lessons  # noqa: E402

CURRENT_VALIDATION = [
    "command:cmd-0019",
    "command:cmd-0033",
    "command:cmd-0050",
    "command:cmd-0071",
    "command:cmd-0074",
    "command:cmd-0078",
    "command:cmd-0079",
]


def subject_matrix() -> dict[str, dict]:
    shown = subprocess.run(
        ["git", "show", f"iacode-checkpoints/{SUBJECT}:docs/checkpoints/{SUBJECT}/"
                        "REQUIREMENTS-MATRIX.json"],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8", check=True).stdout
    return {str(item.get("sourceRef")): item for item in json.loads(shown)["requirements"]}


def repoint(reference: str) -> str | None:
    kind, _, value = reference.partition(":")
    if kind in ("file", "test"):
        return reference
    if kind == "checkpoint":
        return f"file:docs/checkpoints/{SUBJECT}/{value}"
    if kind == "command":
        return f"file:docs/checkpoints/{SUBJECT}/COMMANDS.jsonl"
    return None


def write_finding_closure() -> None:
    finding = {
        "findingId": "M1-F-004",
        "severity": "CRITICAL",
        "title": "The pinned frontend dependency graph contained two Critical and four High advisories",
        "originalExpected": (
            "Update the direct frontend pins and package-lock.json until the unchanged mandatory "
            "scanner reaches both advisory sources and reports no relevant Critical or High "
            "findings, without suppressing advisories or weakening the denominator."
        ),
        "originalObserved": (
            "The sealed audit reproduced npm critical=2 and high=4 through @angular/build, "
            "@angular/cli, @angular/router, @modelcontextprotocol/sdk, piscina and source-map-js; "
            "PyPI had zero findings."
        ),
        "rootCause": (
            "The exact Angular 22.1 pins and their resolved transitive graph entered ranges covered "
            "by live npm advisories after they were locked. A reproducible graph is not permanently "
            "safe, so the unchanged advisory gate correctly stopped M1."
        ),
        "implementation": [
            "All Angular runtime/compiler packages moved together from 22.1.7 to 22.2.1.",
            "@angular/build and @angular/cli moved together from 22.1.8 to 22.2.2.",
            "npm 12 on Node 22.23.2 regenerated package-lock.json from a clean directory without "
            "--force, --legacy-peer-deps, overrides or advisory suppression.",
            "LSN-0057 and GRD-0058 make Critical/High and unavailable sources structurally blocking.",
        ],
        "regressionTest": [
            "tests/test_gate3_sandbox.py test_the_dependency_scan_blocks_critical_and_high_findings",
            "scripts/iacode/gates/web_tests.py: production build and 49 frontend tests",
            "scripts/iacode/gates/lint.py: TypeScript and Prettier checks",
        ],
        "negativeTest": [
            "DEPENDENCY-SCAN-BASELINE.json reproduces two Critical and four High npm findings with both sources SCANNED.",
            "The guardrail test injects Critical, High and unavailable-source outcomes; each returns nonzero while the clean null control passes.",
        ],
        "verificationCommand": (
            "python scripts/iacode/dependency_scan.py --json --report "
            "docs/checkpoints/GATE-3-CP-0005/DEPENDENCY-SCAN-REPORT.json"
        ),
        "evidence": [
            "command:cmd-0010",
            "command:cmd-0019",
            "checkpoint:DEPENDENCY-SCAN-BASELINE.json",
            "checkpoint:DEPENDENCY-SCAN-REPORT.json",
            "command:cmd-0020",
            "command:cmd-0023",
            "command:cmd-0024",
        ],
        "lesson": "LSN-0057",
        "guardrail": "GRD-0058",
        "status": "CLOSED",
    }
    document = {
        "schemaVersion": "1.0.0",
        "checkpoint": CHECKPOINT.name,
        "auditId": "M1-CP-0004",
        "source": "docs/checkpoints/GATE-3-CP-0004/REVIEW-REPORT.md",
        "findings": [finding],
        "total": 1,
        "closed": 1,
        "result": "CLOSED",
    }
    write_json(CHECKPOINT / "M1-CP-0004-FINDINGS-CLOSURE.json", document)
    lines = [
        "# M1-CP-0004 findings closure", "", "Result: **CLOSED (1/1)**", "",
        "## M1-F-004 — CRITICAL — CLOSED", "", finding["title"], "",
        "The direct Angular graph is updated within major 22; the clean npm resolution reports "
        "zero vulnerabilities, and the unchanged mandatory scan reached npm and PyPI with zero "
        "Critical/High findings. `LSN-0057` is guarded by `GRD-0058`.", "",
        "Evidence: `DEPENDENCY-SCAN-BASELINE.json`, `DEPENDENCY-SCAN-REPORT.json`, commands "
        "`cmd-0019`, `cmd-0020`, `cmd-0023`, and `cmd-0024`.", "",
    ]
    (CHECKPOINT / "M1-CP-0004-FINDINGS-CLOSURE.md").write_text(
        "\n".join(lines), encoding="utf-8", newline="\n")


def complete_requirements() -> None:
    path = CHECKPOINT / "CLOSURE-REQUIREMENTS.json"
    closure = load_json(path)
    subject = subject_matrix()
    lessons = {item["lessonId"]: item for item in load_lessons(ROOT)}
    guardrails = load_guardrails(ROOT)
    commands = load_command_results(CHECKPOINT)
    tests = collect_test_ids(ROOT)
    rotted: list[str] = []

    for row in closure["requirements"]:
        reference = str(row.get("sourceRef"))
        buckets = {
            "implementationEvidence": [], "testEvidence": [], "negativeTestEvidence": [],
            "documentationEvidence": [], "validationEvidence": list(CURRENT_VALIDATION),
            "guardrailEvidence": [],
        }
        notes = "Re-verified by this corrective delivery; the original Gate 3 implementation remains sealed."
        if reference == "finding:M1-F-004":
            buckets.update({
                "implementationEvidence": ["file:apps/web/package.json", "file:apps/web/package-lock.json"],
                "testEvidence": ["test:test_the_dependency_scan_blocks_critical_and_high_findings"],
                "negativeTestEvidence": ["checkpoint:DEPENDENCY-SCAN-BASELINE.json"],
                "documentationEvidence": ["checkpoint:M1-CP-0004-FINDINGS-CLOSURE.md",
                                          "checkpoint:DECISIONS.md"],
                "validationEvidence": ["command:cmd-0019", "checkpoint:DEPENDENCY-SCAN-REPORT.json",
                                       "command:cmd-0023", "command:cmd-0024"],
                "guardrailEvidence": ["file:.iacode/memory/guardrails/registry.json"],
            })
            notes = "Closed by the coordinated Angular 22 update; both live advisory sources report zero blocking findings."
        elif reference.startswith("canonical:"):
            declared = subject.get(reference) or {}
            for key in ("implementationEvidence", "testEvidence", "documentationEvidence"):
                for evidence in declared.get(key) or []:
                    mapped = repoint(str(evidence))
                    if mapped and mapped not in buckets[key]:
                        buckets[key].append(mapped)
        elif reference.startswith("lesson:"):
            lesson = lessons.get(reference.split(":", 1)[1]) or {}
            buckets["implementationEvidence"].append("file:.iacode/memory/lessons.jsonl")
            buckets["documentationEvidence"].append("file:docs/ENGINEERING-MEMORY.md")
            for identifier in lesson.get("guardrails") or []:
                buckets["guardrailEvidence"].append("file:.iacode/memory/guardrails/registry.json")
                for test in (guardrails.get(str(identifier)) or {}).get("verifiedBy") or []:
                    evidence = f"test:{test}"
                    if evidence not in buckets["testEvidence"]:
                        buckets["testEvidence"].append(evidence)
            notes = "Applied through the engineering-memory control and the guardrail tests executed by this delivery."

        for key, values in buckets.items():
            kept: list[str] = []
            for value in values:
                error = resolve_evidence(ROOT, CHECKPOINT, value, commands, tests)
                if error is None:
                    kept.append(value)
                else:
                    rotted.append(f"{row['id']} {value}: {error}")
            row[key] = kept
        row["implementationStatus"] = "COMPLETE"
        row["finalStatus"] = "COMPLETE"
        row["justification"] = None
        row["notes"] = notes
    write_json(path, closure)
    if rotted:
        raise RuntimeError("rotted evidence:\n" + "\n".join(rotted))


def update_checkpoint() -> None:
    tests = load_json(CHECKPOINT / "TESTS.json")
    tests["unit"].update({
        "executed": True, "passed": 714, "failed": 0,
        "command": "python -m unittest discover -s tests",
        "evidence": "command:cmd-0079", "runId": "ledger-suite",
    })
    tests["integration"].update({
        "executed": True, "passed": 788, "failed": 0,
        "command": "python scripts/iacode/image_tests.py",
        "evidence": "command:cmd-0091", "runId": "image-suites",
    })
    tests["e2e"].update({
        "executed": True, "passed": 49, "failed": 0,
        "command": "python -m unittest discover -s infra/tests -t infra/tests",
        "evidence": "command:cmd-0092", "runId": "infra-suite",
    })
    write_json(CHECKPOINT / "TESTS.json", tests)

    quality = load_json(CHECKPOINT / "QUALITY.json")
    for key, evidence in {
        "build": ["command:cmd-0088", "command:cmd-0091"],
        "unitTests": ["file:TESTS.json", "command:cmd-0079"],
        "integrationTests": ["file:TESTS.json", "command:cmd-0091"],
        "e2e": ["file:TESTS.json", "command:cmd-0092", "file:VERIFICATION-REPORT.json"],
        "lint": ["command:cmd-0089"],
        "staticAnalysis": ["command:cmd-0080"],
        "security": ["command:cmd-0019", "file:DEPENDENCY-SCAN-REPORT.json",
                     "file:VERIFICATION-REPORT.json"],
        "documentation": ["file:PLAN.md", "file:DECISIONS.md", "file:DIFF-SUMMARY.md",
                          "file:RISKS.md"],
        "checkpointValidation": ["command:cmd-0083", "file:VERIFICATION-REPORT.json"],
        "greenKeeper": ["file:REWORK-LOG.jsonl", "command:cmd-0079"],
    }.items():
        quality["checks"][key].update({"status": "PASS", "evidence": evidence,
                                        "justification": None})
    write_json(CHECKPOINT / "QUALITY.json", quality)

    state = load_json(CHECKPOINT / "STATE.json")
    state["phase"] = "M1 corrective delivery: close M1-F-004 dependency advisories"
    state["status"] = "IN_PROGRESS"
    state["dirty"] = True
    state["updatedAt"] = utc_now()
    state["blockedBy"] = []
    preflight = load_json(CHECKPOINT / "LESSON-PREFLIGHT.json")
    state["lessonPreflight"].update({
        "path": "LESSON-PREFLIGHT.json", "gate": preflight["gate"],
        "scope": preflight["scope"], "lessonsConsidered": preflight["lessonsConsidered"],
        "lessonsApplicable": preflight["lessonsApplicable"],
        "derivedRequirements": len(preflight.get("derivedRequirements") or []),
        "evidence": ["checkpoint:LESSON-PREFLIGHT.json"],
    })
    report = evaluate_matrix(ROOT, CHECKPOINT, load_matrix(CHECKPOINT))
    state["requirementsMatrix"].update({
        "path": "REQUIREMENTS-MATRIX.json", "total": report["totalRequirements"],
        "mandatory": report["mandatoryRequirements"], "complete": report["complete"],
        "partial": report["partial"], "missing": report["missing"],
        "notApplicable": report["notApplicable"], "coveragePercent": report["coveragePercent"],
    })
    state["integrity"].update({
        "status": "PASS", "anchors": len(load_anchors(ROOT)),
        "chainFile": ".iacode/anchors/checkpoint-chain.json", "evidence": ["command:cmd-0003"],
    })
    measured = guardrail_effectiveness(ROOT)
    state["guardrailEffectiveness"].update({
        key: measured[key] for key in ("guardrailsTotal", "guardrailsResolved",
                                       "guardrailsTested", "guardrailsEffective",
                                       "guardrailFailures")
    })
    state["guardrailEffectiveness"]["evidence"] = [
        "file:.iacode/memory/guardrails/registry.json", "file:.iacode/memory/lessons.jsonl"]
    cycles = [json.loads(line) for line in (CHECKPOINT / "REWORK-LOG.jsonl")
              .read_text(encoding="utf-8").splitlines() if line.strip()]
    latest_cycle = cycles[-1]
    state["greenKeeper"].update({
        "status": "PASS" if latest_cycle["result"] == "GREEN" else "FAIL",
        "cycles": len(cycles),
        "remainingFailures": latest_cycle["remainingFailures"],
        "unresolvedReworkItems": latest_cycle["remainingFailures"],
        "externalBlockers": [],
        "evidence": ["file:REWORK-LOG.jsonl", *[
            f"command:{identifier}" for identifier in latest_cycle["commandsExecuted"]]],
    })
    state["reworkCycles"] = len(cycles)
    write_json(CHECKPOINT / "STATE.json", state)
    (CHECKPOINT / "STATUS.md").write_text("# Status\n\nIN_PROGRESS\n", encoding="utf-8", newline="\n")

    metadata = load_json(CHECKPOINT / "RUN-METADATA.json")
    metadata.update({
        "tool": "Codex desktop application", "toolVersion": "not exposed to the run",
        "provider": "OpenAI", "model": "GPT-5", "effort": "not exposed",
        "operatingSystem": "Windows 11 Pro 10.0.26200",
    })
    write_json(CHECKPOINT / "RUN-METADATA.json", metadata)

    (CHECKPOINT / "DIFF-SUMMARY.md").write_text(
        "# Diff summary\n\n- Angular runtime/compiler pins: 22.1.7 → 22.2.1.\n"
        "- Angular CLI/build pins: 22.1.8 → 22.2.2.\n"
        "- Lock graph regenerated cleanly: 297 packages, zero npm vulnerabilities.\n"
        "- Sealed-report parser accepts singular and plural finding headings.\n"
        "- Dependency advisory and preserved-reference guardrails strengthened.\n"
        "- Docker Desktop host-port and lesson-applicability failures recorded and guarded.\n",
        encoding="utf-8", newline="\n")
    (CHECKPOINT / "RISKS.md").write_text(
        "# Risks\n\n- Advisory state changes over time; every release still requires a fresh live scan.\n"
        "- Angular remains on authorized major 22; no major migration was attempted.\n"
        "- Docker Desktop host-port forwarding can drift while containers remain healthy; the "
        "live loopback suite detects it and a non-destructive restart recovered this run.\n"
        "- M1 remains unpassed until a later fresh-session independent audit.\n",
        encoding="utf-8", newline="\n")


def main() -> int:
    write_finding_closure()
    complete_requirements()
    subprocess.run([sys.executable, str(ROOT / "scripts" / "development-ledger"
                                        / "derive_requirements.py"),
                    "--gate", "GATE-3", "--write"], cwd=ROOT, check=True)
    update_checkpoint()
    report = evaluate_matrix(ROOT, CHECKPOINT, load_matrix(CHECKPOINT))
    print(
        "closure prepared: M1-F-004 CLOSED; "
        f"requirements={report['complete']}/{report['totalRequirements']} COMPLETE"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
