#!/usr/bin/env python3
"""Negative scenarios the CP-0009 audit runs against the delivery's own controls.

These exercise the product's public validation entry points over a disposable copy
of the sealed delivery. Each scenario is written by the auditor, not copied from the
delivery's test suite, and each one records what the control actually said.

Nothing here writes to the real repository.
"""
from __future__ import annotations

import json
import re
import shutil
import sys
import tempfile
from pathlib import Path
import os as _os
from pathlib import Path as _Path
_DEFAULT_ROOT = _Path(__file__).resolve().parents[4]

ROOT = Path(_os.environ.get("IACODE_ROOT") or _DEFAULT_ROOT)
sys.path.insert(0, str(ROOT / "scripts" / "development-ledger"))

from anchors import load_anchors  # noqa: E402
from delivery_assurance import completeness_scope, evaluate_matrix  # noqa: E402
from derive_counts import derive_counts  # noqa: E402
from lessons import guardrail_effectiveness, validate_lessons  # noqa: E402
from policies import (  # noqa: E402
    audit_attacks, audit_findings, mandatory_gates, open_audits,
)
from validate_checkpoint import (  # noqa: E402
    _normalize_quality, _validate_delivery_assurance, _validate_internal_assurance,
    _validate_memory_policy, _validate_quality_evidence,
)
from ledger_common import scope_fingerprint  # noqa: E402

NOW = "2026-09-20T23:00:00Z"
SUBJECT = ROOT / "docs" / "checkpoints" / "SETUP-00-CP-0008"

RESULTS: list[dict] = []


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, document) -> None:
    path.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8", newline="\n")


class Delivery:
    """A consistent copy of the sealed delivery, ready to be attacked one field at a time."""

    def __init__(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.path = Path(self.temporary.name) / SUBJECT.name
        shutil.copytree(SUBJECT, self.path)
        self.fingerprint = scope_fingerprint(ROOT)
        self.completeness_fingerprint = scope_fingerprint(
            ROOT, completeness_scope(ROOT, self.path))
        self._make_consistent()

    def close(self) -> None:
        self.temporary.cleanup()

    # -- construction -------------------------------------------------------
    def _make_consistent(self) -> None:
        matrix = read_json(self.path / "REQUIREMENTS-MATRIX.json")
        for row in matrix["requirements"]:
            row["status"] = "COMPLETE"
            row["implementationEvidence"] = ["checkpoint:PLAN.md"]
        write_json(self.path / "REQUIREMENTS-MATRIX.json", matrix)
        closure = read_json(self.path / "CLOSURE-REQUIREMENTS.json")
        for row in closure["requirements"]:
            row["implementationStatus"] = "COMPLETE"
            row["finalStatus"] = "COMPLETE"
            row["implementationEvidence"] = ["checkpoint:PLAN.md"]
        write_json(self.path / "CLOSURE-REQUIREMENTS.json", closure)
        self.matrix = matrix
        self.total = len(matrix["requirements"])
        self.mandatory = sum(1 for row in matrix["requirements"] if row["mandatory"])
        self._write_rework_log()
        self._write_report()
        self._write_internal_assurance()
        self._write_findings_closure()
        self._neutralize_counts()
        self._write_counts()

    def _write_rework_log(self, **overrides) -> None:
        entry = {
            "cycle": 1, "timestamp": NOW, "trigger": "audit scenario", "failedGate": None,
            "failureEvidence": [], "rootCauseSummary": None, "filesChanged": [],
            "commandsExecuted": ["cmd-0001"],
            "requiredGates": list(mandatory_gates(ROOT)),
            "gateResults": [{"gate": gate, "commandId": "cmd-0001", "exitCode": 0,
                             "mandatory": True} for gate in mandatory_gates(ROOT)],
            "scopeFingerprint": self.fingerprint,
            "result": "GREEN", "remainingFailures": 0,
        }
        entry.update(overrides)
        (self.path / "REWORK-LOG.jsonl").write_text(
            json.dumps(entry) + "\n", encoding="utf-8", newline="\n")

    def _write_report(self, **overrides) -> None:
        computed = evaluate_matrix(ROOT, self.path, read_json(self.path / "REQUIREMENTS-MATRIX.json"))
        report = {"schemaVersion": "2.0.0", "checkpoint": self.path.name, "generatedAt": NOW,
                  "matrix": "REQUIREMENTS-MATRIX.json", "auditor": "audit scenario",
                  "scopeFingerprint": self.completeness_fingerprint, **computed}
        report.update(overrides)
        write_json(self.path / "COMPLETENESS-REPORT.json", report)
        self.report = report

    def _write_internal_assurance(self) -> None:
        for name in ("M0-INTERNAL-RED-TEAM.md", "M0-INTERNAL-MIRROR.md"):
            stale = self.path / name
            if stale.is_file():
                stale.unlink()
        attacks = []
        for audit in open_audits(ROOT, "SETUP-00", self.path.name):
            for attack in audit_attacks(ROOT, audit):
                attacks.append({
                    "attackId": attack["id"], "description": attack["mutation"],
                    "target": attack["target"], "mutation": attack["mutation"],
                    "expectedDefense": attack["expectedDefense"], "observed": "rejected",
                    "result": "DEFENDED", "evidence": ["attack:" + attack["id"]],
                    "mandatory": attack["mandatory"] == "true"})
        mandatory = [item for item in attacks if item["mandatory"]]
        write_json(self.path / "M0-INTERNAL-RED-TEAM.json", {
            "schemaVersion": "1.0.0", "checkpoint": self.path.name, "generatedAt": NOW,
            "targetFingerprint": self.fingerprint, "source": "audit scenario",
            "attacks": attacks, "total": len(attacks), "defended": len(attacks), "escaped": 0,
            "mandatoryTotal": len(mandatory), "mandatoryDefended": len(mandatory),
            "result": "RED_TEAM_PASS"})
        write_json(self.path / "M0-INTERNAL-MIRROR.json", {
            "schemaVersion": "1.0.0", "checkpoint": self.path.name, "milestone": "M0",
            "generatedAt": NOW, "targetFingerprint": self.fingerprint,
            "auditorRole": "M0 Closure Auditor",
            "independence": "Internal quality assurance, not independent external validation.",
            "checks": [{"id": "MIR-001", "dimension": "scenario", "expectation": "scenario",
                        "observed": "scenario", "result": "PASS",
                        "evidence": ["checkpoint:PLAN.md"]}],
            "total": 1, "passed": 1, "failed": 0, "notApplicable": 0, "result": "PASS"})

    def _write_findings_closure(self) -> None:
        findings = []
        for audit in open_audits(ROOT, "SETUP-00", self.path.name):
            for finding in audit_findings(ROOT, audit):
                findings.append({
                    "findingId": finding["id"], "severity": finding["severity"] or "HIGH",
                    "title": finding["title"], "originalExpected": "scenario",
                    "originalObserved": "scenario", "rootCause": "scenario",
                    "implementation": ["scenario"], "regressionTest": ["scenario"],
                    "verificationCommand": "python -m unittest discover -s tests",
                    "evidence": ["checkpoint:PLAN.md"], "status": "CLOSED"})
        write_json(self.path / "CP7-FINDINGS-CLOSURE.json", {
            "schemaVersion": "1.0.0", "checkpoint": self.path.name, "auditId": "M0-CP-0007",
            "source": "audit scenario", "findings": findings, "total": len(findings),
            "closed": len(findings), "result": "CLOSED"})

    def _neutralize_counts(self) -> None:
        claim = re.compile(r"(?<![0-9])(\d+)\s*/\s*(\d+)\s+"
                           r"(TESTS|REQUIREMENTS|FINDINGS|ATTACKS|LESSONS|GUARDRAILS)\b")
        for document in sorted(self.path.glob("*.md")):
            text = document.read_text(encoding="utf-8")
            rewritten = claim.sub(lambda m: m.group(1) + " of " + m.group(2) + " " + m.group(3), text)
            if rewritten != text:
                document.write_text(rewritten, encoding="utf-8", newline="\n")

    def _write_counts(self) -> None:
        write_json(self.path / "COUNTS.json", {
            "schemaVersion": "1.0.0", "checkpoint": self.path.name, "generatedAt": NOW,
            "counts": derive_counts(ROOT, self.path)})

    # -- probes -------------------------------------------------------------
    def state(self, **overrides):
        effectiveness = guardrail_effectiveness(ROOT)
        state = {
            "schemaVersion": "3.2.0", "gate": "SETUP-00", "status": "READY_FOR_REVIEW",
            "blockedBy": [], "secondToolValidation": {"status": "PENDING_MANUAL"},
            "requirementsMatrix": {"path": "REQUIREMENTS-MATRIX.json", "total": self.total,
                                   "mandatory": self.mandatory, "complete": self.total,
                                   "partial": 0, "missing": 0, "notApplicable": 0,
                                   "coveragePercent": 100.0},
            "greenKeeper": {"status": "PASS", "cycles": 1, "remainingFailures": 0,
                            "unresolvedReworkItems": 0, "log": "REWORK-LOG.jsonl",
                            "externalBlockers": [], "evidence": [],
                            "requiredGates": list(mandatory_gates(ROOT)),
                            "scopeFingerprint": self.fingerprint},
            "deliveryCompleteness": {"status": "PASS", "report": "COMPLETENESS-REPORT.json",
                                     "coveragePercent": 100.0, "evidenceCoveragePercent": 100.0,
                                     "auditor": "scenario", "evidence": [],
                                     "scopeFingerprint": self.completeness_fingerprint},
            "reworkCycles": 1,
            "independentReview": {"status": "PENDING"}, "redTeam": {"status": "PENDING"},
            "milestone": {"id": "M0", "title": "Development control plane",
                          "gates": ["SETUP-00"], "status": "PENDING"},
            "externalAuditRequired": False, "externalAuditReason": None,
            "guardrailEffectiveness": {key: effectiveness[key] for key in (
                "guardrailsTotal", "guardrailsResolved", "guardrailsTested",
                "guardrailsEffective", "guardrailFailures")},
            "integrity": {"status": "PASS", "anchors": len(load_anchors(ROOT)),
                          "chainFile": ".iacode/anchors/checkpoint-chain.json", "evidence": []},
            "externalAttestation": {"status": "NONE", "path": None, "auditId": None,
                                    "evidence": []},
            "lessonPreflight": self._preflight_state(),
        }
        state.update(overrides)
        return state

    def _preflight_state(self):
        preflight = read_json(self.path / "LESSON-PREFLIGHT.json")
        return {"path": "LESSON-PREFLIGHT.json", "gate": "SETUP-00",
                "scope": preflight.get("scope"),
                "lessonsConsidered": preflight.get("lessonsConsidered"),
                "lessonsApplicable": preflight.get("lessonsApplicable"),
                "derivedRequirements": len(preflight.get("derivedRequirements") or []),
                "fingerprint": preflight.get("inputsFingerprint"), "evidence": []}

    def quality_evidence(self, quality=None) -> list[str]:
        errors: list[str] = []
        quality = quality or {"schemaVersion": "3.2.0", "checks": self.quality()}
        commands = {}
        for line in (self.path / "COMMANDS.jsonl").read_text(encoding="utf-8").splitlines():
            if line.strip():
                record_ = json.loads(line)
                commands[record_["id"]] = record_.get("exitCode")
        _validate_quality_evidence(self.path, quality, _normalize_quality(quality),
                                   commands, "3.2.0", errors)
        return errors

    def internal_assurance(self, state=None) -> list[str]:
        errors: list[str] = []
        _validate_internal_assurance(ROOT, self.path, state or self.state(), errors)
        return errors

    def quality(self, **overrides):
        names = ("build", "unitTests", "integrationTests", "e2e", "lint", "staticAnalysis",
                 "security", "documentation", "checkpointValidation", "greenKeeper",
                 "deliveryCompleteness")
        checks = {name: {"status": "PASS", "evidence": ["file:PLAN.md"],
                         "justification": None} for name in names}
        checks["redTeam"] = {"status": "NOT_EXECUTED", "evidence": [], "justification": None}
        for name, status in overrides.items():
            checks[name] = {"status": status, "evidence": [], "justification": None}
        return checks

    def tests(self, failed: int = 0):
        result = {"executed": True, "passed": 5, "failed": failed,
                  "command": "python -m unittest discover -s tests", "evidence": "scenario"}
        return {"schemaVersion": "3.2.0", "unit": result, "integration": result,
                "e2e": {"executed": False, "passed": 0, "failed": 0, "command": None,
                        "evidence": None}}

    def assurance(self, state=None, quality=None, tests=None) -> list[str]:
        errors: list[str] = []
        _validate_delivery_assurance(ROOT, self.path, state or self.state(),
                                     quality or self.quality(), tests or self.tests(),
                                     errors, closure=True)
        return errors

    def memory(self, state=None) -> list[str]:
        errors: list[str] = []
        _validate_memory_policy(ROOT, self.path, state or self.state(), errors, closure=True)
        return errors

    def edit(self, name: str, mutate) -> None:
        document = read_json(self.path / name)
        mutate(document)
        write_json(self.path / name, document)


def record(scenario_id: str, description: str, expected: str, errors, marker) -> None:
    matched = [error for error in errors if marker.lower() in error.lower()]
    RESULTS.append({
        "id": scenario_id, "description": description, "expected": expected,
        "marker": marker, "rejected": bool(matched),
        "observed": (matched[:3] if matched else (list(errors)[:3] or ["no error was reported"])),
        "result": "DEFENDED" if matched else "ESCAPED",
    })
    print("[" + scenario_id + "] " + RESULTS[-1]["result"] + " :: " + description)
    for line in RESULTS[-1]["observed"]:
        print("      " + str(line)[:200])


def positive(scenario_id: str, description: str, errors) -> None:
    RESULTS.append({
        "id": scenario_id, "description": description, "expected": "accept",
        "marker": None, "rejected": bool(errors),
        "observed": list(errors)[:5] or ["no error"],
        "result": "ACCEPTED" if not errors else "REFUSED",
    })
    print("[" + scenario_id + "] " + RESULTS[-1]["result"] + " :: " + description)
    for line in RESULTS[-1]["observed"]:
        print("      " + str(line)[:200])
