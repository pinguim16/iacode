#!/usr/bin/env python3
"""Execute every negative scenario of sections 13, 14, 15, 26-28 and 30 of the audit brief."""
from __future__ import annotations

import json
import sys
from pathlib import Path
import os as _os
from pathlib import Path as _Path
_DEFAULT_ROOT = _Path(__file__).resolve().parents[4]

sys.path.insert(0, str(Path(__file__).parent))
from scenarios import (  # noqa: E402
    Delivery, RESULTS, ROOT, mandatory_gates, positive, read_json, record, write_json,
)


def fail_command(delivery, command_id: str, exit_code: int = 5) -> None:
    path = delivery.path / "COMMANDS.jsonl"
    records = [json.loads(line) for line in
               path.read_text(encoding="utf-8").splitlines() if line.strip()]
    for item in records:
        if item["id"] == command_id:
            item["exitCode"] = exit_code
            item["result"] = "FAILED"
            item["resultCode"] = "E_FAILED"
    body = "\n".join(json.dumps(item, ensure_ascii=False) for item in records) + "\n"
    path.write_text(body, encoding="utf-8", newline="\n")


def quality_document(delivery, **entry):
    checks = delivery.quality()
    checks["staticAnalysis"] = entry
    return {"schemaVersion": "3.2.0", "checks": checks}


def main() -> int:
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)

    # ---------------------------------------------------------------- baseline control
    delivery = Delivery()
    positive("BASE-001", "the consistent delivery copy is accepted by both validators",
             delivery.assurance() + delivery.memory() + delivery.internal_assurance()
             + delivery.quality_evidence())
    delivery.close()

    # ---------------------------------------------------------------- 13. Green Keeper
    cases = [
        ("GK-001", "requiredGates empty in the recorded cycle",
         lambda d: d._write_rework_log(requiredGates=[], gateResults=[]),
         "canonical mandatory set"),
        ("GK-002", "one mandatory gate omitted from the cycle",
         lambda d: d._write_rework_log(
             requiredGates=[g for g in mandatory_gates(ROOT) if g != "lessons"],
             gateResults=[{"gate": g, "commandId": "cmd-0001", "exitCode": 0, "mandatory": True}
                          for g in mandatory_gates(ROOT) if g != "lessons"]),
         "canonical mandatory set"),
        ("GK-003", "a mandatory gate recorded as not executed",
         lambda d: d._write_rework_log(
             gateResults=[{"gate": g, "commandId": "cmd-0001",
                           "exitCode": 0 if g != "tests" else None, "mandatory": True}
                          for g in mandatory_gates(ROOT)]),
         "exiting None"),
        ("GK-004", "a mandatory gate that exited nonzero",
         lambda d: d._write_rework_log(
             gateResults=[{"gate": g, "commandId": "cmd-0001",
                           "exitCode": 0 if g != "tests" else 1, "mandatory": True}
                          for g in mandatory_gates(ROOT)]),
         "exiting 1"),
        ("GK-005", "a mandatory gate with no command evidence",
         lambda d: d._write_rework_log(
             commandsExecuted=[],
             gateResults=[{"gate": g, "commandId": None, "exitCode": 0, "mandatory": True}
                          for g in mandatory_gates(ROOT)]),
         "no command evidence"),
    ]
    for scenario_id, description, mutate, marker in cases:
        delivery = Delivery()
        mutate(delivery)
        record(scenario_id, description, "reject", delivery.assurance(), marker)
        delivery.close()

    delivery = Delivery()
    state = delivery.state()
    state["greenKeeper"] = {**state["greenKeeper"], "remainingFailures": 2}
    record("GK-006", "a PASS carrying remaining failures", "reject",
           delivery.assurance(state), "remainingFailures")
    delivery.close()

    delivery = Delivery()
    state = delivery.state()
    state["greenKeeper"] = {**state["greenKeeper"], "unresolvedReworkItems": 1}
    record("GK-007", "a PASS carrying unresolved rework items", "reject",
           delivery.assurance(state), "unresolved")
    delivery.close()

    delivery = Delivery()
    delivery._write_rework_log(result="RED", remainingFailures=1)
    record("GK-008", "a fabricated PASS over a red cycle in the log", "reject",
           delivery.assurance(), "contradicts the last rework cycle")
    delivery.close()

    delivery = Delivery()
    stale = "0" * 64
    delivery._write_rework_log(scopeFingerprint=stale)
    state = delivery.state()
    state["greenKeeper"] = {**state["greenKeeper"], "scopeFingerprint": stale}
    record("GK-009", "a PASS whose fingerprint no longer describes the scope", "reject",
           delivery.assurance(state), "STALE")
    delivery.close()

    canonical = list(mandatory_gates(ROOT))
    record("GK-010", "the mandatory set is the policy registry, not the caller's argument",
           "policy-derived", ["mandatory_gates(ROOT) = " + ",".join(canonical)],
           "mandatory_gates(ROOT)")

    # ---------------------------------------------------------------- 14. completeness
    def drop(prefix):
        def mutate(document):
            victim = next(r for r in document["requirements"]
                          if str(r.get("sourceRef", "")).startswith(prefix))
            document["requirements"] = [r for r in document["requirements"]
                                        if r["id"] != victim["id"]]
        return mutate

    for scenario_id, description, prefix in (
            ("DC-001", "a canonical requirement removed", "canonical:"),
            ("DC-002", "a lesson-derived requirement removed", "lesson:"),
            ("DC-003", "an audit-finding requirement removed", "finding:"),
            ("DC-004", "an audit-attack requirement removed", "attack:")):
        delivery = Delivery()
        delivery.edit("REQUIREMENTS-MATRIX.json", drop(prefix))
        delivery._write_report()
        state = delivery.state()
        state["requirementsMatrix"] = {**state["requirementsMatrix"],
                                       "total": delivery.total - 1,
                                       "complete": delivery.total - 1,
                                       "mandatory": delivery.mandatory - 1}
        record(scenario_id, description, "reject", delivery.assurance(state),
               "canonical expected set requires")
        delivery.close()

    delivery = Delivery()
    delivery.edit("REQUIREMENTS-MATRIX.json",
                  lambda d: d.update({"requirements": d["requirements"][1:]}))
    delivery._write_report()
    state = delivery.state()
    state["requirementsMatrix"] = {**state["requirementsMatrix"], "total": delivery.total - 1,
                                   "complete": delivery.total - 1}
    record("DC-005", "the denominator decreased with every stored count recomputed", "reject",
           delivery.assurance(state), "canonical expected set requires")
    delivery.close()

    delivery = Delivery()
    state = delivery.state()
    state["requirementsMatrix"] = {**state["requirementsMatrix"], "total": delivery.total + 40}
    record("DC-006", "the declared total falsified upward", "reject",
           delivery.assurance(state), "does not match the matrix")
    delivery.close()

    delivery = Delivery()
    delivery.edit("REQUIREMENTS-MATRIX.json",
                  lambda d: d["requirements"][0].update({"status": "PARTIAL"}))
    delivery._write_report(coveragePercent=100.0, complete=delivery.total, partial=0,
                           result="PASS")
    record("DC-007", "coverage forged to 100 over an incomplete matrix", "reject",
           delivery.assurance(), "contradicts the recomputed value")
    delivery.close()

    delivery = Delivery()
    delivery.edit("REQUIREMENTS-MATRIX.json",
                  lambda d: d["requirements"][0].update({"status": "MISSING"}))
    delivery._write_report(result="PASS", missing=0, complete=delivery.total,
                           coveragePercent=100.0)
    record("DC-008", "a report claiming PASS over a MISSING requirement", "reject",
           delivery.assurance(), "contradicts the recomputed value")
    delivery.close()

    delivery = Delivery()

    def strip_evidence(document):
        row = document["requirements"][0]
        for key in ("implementationEvidence", "testEvidence", "documentationEvidence",
                    "validationEvidence"):
            row[key] = []

    delivery.edit("REQUIREMENTS-MATRIX.json", strip_evidence)
    delivery._write_report()
    record("DC-009", "a COMPLETE requirement with no evidence at all", "reject",
           delivery.assurance(), "at least one evidence reference")
    delivery.close()

    delivery = Delivery()
    delivery.edit("REQUIREMENTS-MATRIX.json",
                  lambda d: d["requirements"][0].update(
                      {"implementationEvidence": ["file:docs/does-not-exist.md"],
                       "testEvidence": [], "documentationEvidence": [],
                       "validationEvidence": []}))
    delivery._write_report()
    record("DC-010", "evidence pointing at a path that does not exist", "reject",
           delivery.assurance(), "does not exist")
    delivery.close()

    delivery = Delivery()
    delivery.edit("REQUIREMENTS-MATRIX.json",
                  lambda d: d["requirements"][0].update(
                      {"implementationEvidence": ["command:cmd-0002"],
                       "testEvidence": [], "documentationEvidence": [],
                       "validationEvidence": []}))
    fail_command(delivery, "cmd-0002", 3)
    delivery._write_report()
    record("DC-011", "evidence referencing a command whose record failed", "reject",
           delivery.assurance(), "cmd-0002")
    delivery.close()

    # ---------------------------------------------------------------- 30. evidence integrity
    delivery = Delivery()
    record("EVD-001", "a quality PASS with no evidence reference", "reject",
           delivery.quality_evidence(quality_document(
               delivery, status="PASS", evidence=[], justification=None)),
           "at least one evidence reference")
    delivery.close()

    delivery = Delivery()
    record("EVD-002", "quality evidence naming a file that does not exist", "reject",
           delivery.quality_evidence(quality_document(
               delivery, status="PASS", evidence=["file:NO-SUCH-FILE.md"], justification=None)),
           "NO-SUCH-FILE")
    delivery.close()

    delivery = Delivery()
    record("EVD-003", "quality evidence naming a command that does not exist", "reject",
           delivery.quality_evidence(quality_document(
               delivery, status="PASS", evidence=["command:cmd-9999"], justification=None)),
           "cmd-9999")
    delivery.close()

    delivery = Delivery()
    fail_command(delivery, "cmd-0002", 5)
    record("EVD-004", "quality evidence naming a command that failed", "reject",
           delivery.quality_evidence(quality_document(
               delivery, status="PASS", evidence=["command:cmd-0002"], justification=None)),
           "cmd-0002")
    delivery.close()

    delivery = Delivery()
    (delivery.path / "EMPTY-EVIDENCE.md").write_text("", encoding="utf-8", newline="\n")
    record("EVD-005", "quality evidence naming an existing but empty file", "reject",
           delivery.quality_evidence(quality_document(
               delivery, status="PASS", evidence=["file:EMPTY-EVIDENCE.md"], justification=None)),
           "EMPTY-EVIDENCE")
    delivery.close()

    delivery = Delivery()
    state = delivery.state()
    state["deliveryCompleteness"] = {**state["deliveryCompleteness"],
                                     "scopeFingerprint": "0" * 64}
    delivery._write_report(scopeFingerprint="0" * 64)
    record("EVD-006", "a completeness verdict describing content that has since changed",
           "reject", delivery.assurance(state), "STALE")
    delivery.close()

    # ---------------------------------------------------------------- 26-28 staleness
    delivery = Delivery()
    stale = "1" * 64
    delivery._write_rework_log(scopeFingerprint=stale)
    state = delivery.state()
    state["greenKeeper"] = {**state["greenKeeper"], "scopeFingerprint": stale}
    record("STL-001", "a Green Keeper PASS whose recorded scope is no longer the current one",
           "reject", delivery.assurance(state), "STALE")
    delivery.close()

    delivery = Delivery()
    delivery._write_report(scopeFingerprint="2" * 64)
    record("STL-002", "a completeness PASS that predates a relevant scope change", "reject",
           delivery.assurance(), "STALE")
    delivery.close()

    delivery = Delivery()
    report = read_json(delivery.path / "M0-INTERNAL-RED-TEAM.json")
    report["targetFingerprint"] = "3" * 64
    write_json(delivery.path / "M0-INTERNAL-RED-TEAM.json", report)
    record("STL-003a", "an internal Red Team result that predates a change to an attacked control",
           "reject", delivery.internal_assurance(), "STALE")
    delivery.close()

    delivery = Delivery()
    report = read_json(delivery.path / "M0-INTERNAL-MIRROR.json")
    report["targetFingerprint"] = "4" * 64
    write_json(delivery.path / "M0-INTERNAL-MIRROR.json", report)
    record("STL-003b", "an internal mirror result that predates a change to the audited content",
           "reject", delivery.internal_assurance(), "STALE")
    delivery.close()

    delivery = Delivery()
    report = read_json(delivery.path / "M0-INTERNAL-RED-TEAM.json")
    report["attacks"][0]["result"] = "ESCAPED"
    write_json(delivery.path / "M0-INTERNAL-RED-TEAM.json", report)
    record("STL-004", "an internal Red Team PASS while one attack escaped", "reject",
           delivery.internal_assurance(), "escap")
    delivery.close()

    delivery = Delivery()
    report = read_json(delivery.path / "M0-INTERNAL-MIRROR.json")
    report["checks"][0]["result"] = "FAIL"
    write_json(delivery.path / "M0-INTERNAL-MIRROR.json", report)
    record("STL-005", "an internal mirror PASS while one mirrored check failed", "reject",
           delivery.internal_assurance(), "fail")
    delivery.close()

    (out / "scenario-results.json").write_text(
        json.dumps(RESULTS, indent=2) + "\n", encoding="utf-8", newline="\n")
    escaped = [r for r in RESULTS if r["result"] in ("ESCAPED", "REFUSED")]
    print("TOTAL=" + str(len(RESULTS)) + " ESCAPED_OR_REFUSED=" + str(len(escaped)))
    for item in escaped:
        print(" - " + item["id"] + ": " + str(item["observed"])[:300])
    return 0 if not escaped else 1


if __name__ == "__main__":
    sys.exit(main())
